import maya.mel as mel
import maya.cmds as cmds
import os
import subprocess


'''
Whats Next
: steamline playblast ranges to be number list driven (as with russian playblasts)
: remove unneeded code
'''

class quick_rv_playblastTool:

    @classmethod
    def drange2(self, start, stop, step):
        numelements = int((stop-start)/float(step))
        for i in range(numelements+1):
                yield start + i*step

    @classmethod
    def playblast(self, *args, **kwargs ):
        #
        playblastSizeMultiplier = 1
        if 'playblastSizeMultiplier' in kwargs:
            playblastSizeMultiplier = kwargs.pop( 'playblastSizeMultiplier' )
        #
        mode = 'asIs' # 'asIs', or 'basic', or 'imagePlaneOnly'
        if 'mode' in kwargs:
            mode = kwargs.pop( 'mode' )
        #
        rvOverlayMode = 'wipe' #'over' or 'wipe'
        if 'rvOverlayMode' in kwargs:
            rvOverlayMode = kwargs.pop( 'rvOverlayMode' )
        #
        compareImagePlane = False
        if 'compareImagePlane' in kwargs:
            compareImagePlane = kwargs.pop( 'compareImagePlane' )
        #
        russianPlayblast = False
        if 'russianPlayblast' in kwargs:
            russianPlayblast = kwargs.pop( 'russianPlayblast' )

        #setup
        seqName = cmds.workspace( q = True, fn = True ).split( '/' )[5]
        shotName = cmds.workspace( q = True, fn = True ).split( '/' )[7]
        sceneName = cmds.file( q = True, sn = True, shn = True ).split( '.' )[0]

        # getting panel
        modelPanel = cmds.getPanel( withFocus = True )
        camera = ''
        try:
            camera = cmds.modelEditor(modelPanel, query=True, camera=True)
            camera = cmds.listRelatives(camera, shapes=True)[0]
        except:
            pass

        #no point playblasting the graph editor
        if camera:
            #bug fixing, set overscan to 1
            if cmds.getAttr(camera+'.overscan')!=1:
                try:
                    cmds.setAttr(camera+'.overscan', 1)
                except:
                    cmds.warning('Please set camera overscan to 1. Check the attribute editor, under display options.')

            # get scene width and height
            height = int( cmds.getAttr( 'defaultResolution.height' ) * playblastSizeMultiplier )
            width = int( cmds.getAttr( 'defaultResolution.width' ) * playblastSizeMultiplier )

            # setup time ranges
            startTime = cmds.playbackOptions( q = True, minTime = True )
            endTime = cmds.playbackOptions( q = True, maxTime = True )

            # override time range if there's a selection
            rangeStart, rangeEnd = str( cmds.timeControl( mel.eval( '$tmpVar=$gPlayBackSlider' ), query = True, range = True ) ).replace( '"', '' ).split( ':' )
            rangeStart = float( rangeStart )
            rangeEnd = float( rangeEnd ) - 1 #seems to add a frame
            if ( rangeEnd - rangeStart ) > 1:
                startTime = rangeStart
                endTime = rangeEnd

            # get audio filename
            audioNode = ''
            audioFile = ''
            audioOffset_attribute = startTime
            audioOffset_inSeconds = 0
            if cmds.ls( type = 'audio' ):
                audioNode = cmds.ls( type = 'audio' )[0]
                audioFile = cmds.getAttr( audioNode + '.filename' )
                audioOffset_attribute = cmds.getAttr( audioNode + '.offset' )
                audioOffset_inSeconds = (audioOffset_attribute - startTime)/24 #assuming 24fps

            # launch playblast
            tempPlayblastFolder = "/usr/tmp/rv_playblasts/"
            tempFolder = "/usr/tmp/"
            filename_raw = tempPlayblastFolder + shotName + '/' + sceneName + "scratch"
            if russianPlayblast:
                filename_raw = filename_raw + '_RUSSIAN'
            filename = self.playblastFromwindow( russianPlayblast = russianPlayblast, startTime=startTime, endTime=endTime, filename=filename_raw, width=width, height=height, camera=camera, modelPanel=modelPanel, mode=mode)

            #to handle escaping
            if filename:
                #format path for RV
                filename = self.formatPathForRV(filename=filename, startTime=startTime, endTime=endTime, russianPlayblast=russianPlayblast)

                #get overlay info
                overlaySequence = ''
                if compareImagePlane:
                    '''
                    if 2D pan/zoom, render a second sequence with just imageplanes
                    if not, use farthest back image plane
                    '''
                    #check 2D pan/zoom
                    panZoomEnabled = cmds.getAttr(camera + '.panZoomEnabled')

                    #get list of image planes
                    imagePlaneInfo = {} #imagePlane:depth
                    farthestAwayImagePlane_path = ''
                    farthestAwayImagePlane_depth = 0

                    #
                    camera_connections = cmds.listConnections(camera, source=True, type='imagePlane') or []
                    if camera_connections:
                        for connection in camera_connections:
                            #use only active image planes, 2=RGB, 3=RGBA
                            if cmds.getAttr(connection+".displayMode") == 2 or cmds.getAttr(connection+".displayMode") == 3:
                                imagePlaneInfo[connection] = {}
                                depth = cmds.getAttr(connection+".depth")
                                path = cmds.getAttr(connection+".imageName")
                                imagePlaneInfo[connection]['depth'] = depth
                                imagePlaneInfo[connection]['imageName'] = path
                                #set farthest image plane
                                if depth>farthestAwayImagePlane_depth:
                                    farthestAwayImagePlane_depth = depth
                                    farthestAwayImagePlane_path = path


                    #continue only if there are actually image planes present
                    if not camera_connections:
                        compareImagePlane = False
                        cmds.warning('No ImagePlanes attached to camera, turning off Compare ImagePlanes feature.')
                    if camera_connections:
                        #prep sequence for RV
                        '''
                        #because of virtual folder linking, not all paths resolve correctly in maya
                        #forcing all backplates to simply be re-rendered fixes the problem
                        if not panZoomEnabled:
                            overlaySequence = farthestAwayImagePlane_path
                        if panZoomEnabled:
                            filename_raw = tempPlayblastFolder + shotName + '/' + sceneName + "scratch_OVERLAY"
                            overlaySequence = self.playblastFromwindow( startTime=startTime, endTime=endTime, filename=filename_raw, width=width, height=height, camera=camera, modelPanel=modelPanel, mode='imagePlaneOnly')
                        '''
                        #render backplates
                        filename_raw = tempPlayblastFolder + shotName + '/' + sceneName + "scratch_OVERLAY"
                        overlaySequence = self.playblastFromwindow( startTime=startTime, endTime=endTime, filename=filename_raw, width=width, height=height, camera=camera, modelPanel=modelPanel, mode='imagePlaneOnly')

                        #handle escaping
                        if overlaySequence:
                            #format path for RV
                            overlaySequence = self.formatPathForRV(filename=overlaySequence, startTime=startTime, endTime=endTime)
                        else:
                            compareImagePlane = False

                # Launch RV with or without audio
                if not compareImagePlane:
                    if cmds.ls( type = 'audio' ):
                        subprocess.Popen( ['rv', '[', filename, audioFile, '-ao', str(audioOffset_inSeconds), '-eval', 'use rvui; rvui.setMatteValue(2.4); rvui.setMatteOpacityValue(.75);', ']', ] )
                    else:
                        subprocess.Popen( ['rv', filename, '-eval', 'use rvui;rvui.setMatteValue(2.4); rvui.setMatteOpacityValue(.75);'] )
                else:
                        subprocess.Popen( ['rv','-'+rvOverlayMode, filename, '[', overlaySequence, '-in', str(startTime), '-out', str(endTime), ']' ,'-eval', 'use rvui;rvui.setMatteValue(2.4); rvui.setMatteOpacityValue(.75);'] )

                # temp folder cleanup
                '''
                tempPlayblastFolder :subfolder for playblasts
                tempFolder :root folder for maya temp
                '''
                folderSizes = {}
                for tmpPath in [tempFolder, tempPlayblastFolder]:
                    folder_size = 0
                    for ( path, dirs, files ) in os.walk( tmpPath ):
                        for file in files:
                            filename = os.path.join( path, file )
                            folder_size += os.path.getsize( filename )
                    folderSizes[tmpPath] = folder_size / ( 1024 * 1024 )

                # send a warning message
                for tmpPath in [tempFolder, tempPlayblastFolder]:
                    if folderSizes[tmpPath] > 1000:
                        cmds.warning( "Your temp folder is getting heaps big:", tmpPath + ' Size = %0.1f MB' % ( folderSizes[tmpPath] ), 'Try cleaning it out mate.' )

    ######################################################################################################
    @classmethod
    def formatPathForRV(self, **kwargs ):
        #
        filename = ''
        if 'filename' in kwargs:
            filename = kwargs.pop( 'filename' )
        #
        startTime = ''
        if 'startTime' in kwargs:
            startTime = kwargs.pop( 'startTime' )
        #
        endTime = ''
        if 'endTime' in kwargs:
            endTime = kwargs.pop( 'endTime' )
        #
        russianPlayblast = False
        if 'russianPlayblast' in kwargs:
            russianPlayblast = kwargs.pop( 'russianPlayblast' )


        #russianPlayblast
        if russianPlayblast:
            russianPlayblast_range = []
            if russianPlayblast:
                russianPlayblast_factor = .25
                russianPlayblast_range = list(self.drange2(startTime, endTime, russianPlayblast_factor))
                startTime = 0
                endTime = len(russianPlayblast_range)

        #format path
        '''
        http://www.tweaksoftware.com/static/documentation/rv/current/html/rv_manual.html
        rv foo.#.tif
        rv foo.2-8#.tif
        rv foo.2-8@@@@.tif #<-----using this format
        rv foo.%04d.tif
        rv foo.%04d.tif 2-8
        rv foo.#.tif 2-8
        '''
        filename_split = filter( None, filename.split( '.'  ) )
        frameRange = str( int( startTime ) ) + '-' + str( int( endTime ) ) + '@'*len(filename_split[-2])
        #to handle the dots in the file paths
        filename = '.'.join(filename_split[0:-2]) + '.' + frameRange + '.' + filename_split[-1]

        return filename

    ######################################################################################################
    @classmethod
    def playblastFromwindow(self, **kwargs ):
        #
        startTime = 1000
        if 'startTime' in kwargs:
            startTime = kwargs.pop( 'startTime' )
        #
        endTime = 1001
        if 'endTime' in kwargs:
            endTime = kwargs.pop( 'endTime' )
        #
        format = 'iff'
        if 'format' in kwargs:
            format = kwargs.pop( 'format' )
        #
        filename = ''
        if 'filename' in kwargs:
            filename = kwargs.pop( 'filename' )
        #
        forceOverwrite = True
        if 'forceOverwrite' in kwargs:
            forceOverwrite = kwargs.pop( 'forceOverwrite' )
        #
        sequenceTime = False
        if 'sequenceTime' in kwargs:
            sequenceTime = kwargs.pop( 'sequenceTime' )
        #
        viewer = False
        if 'viewer' in kwargs:
            viewer = kwargs.pop( 'viewer' )
        #
        offScreen = True
        if 'offScreen' in kwargs:
            offScreen = kwargs.pop( 'offScreen' )
        #
        clearCache = True
        if 'clearCache' in kwargs:
            clearCache = kwargs.pop( 'clearCache' )
        #
        showOrnaments = False
        if 'showOrnaments' in kwargs:
            showOrnaments = kwargs.pop( 'showOrnaments' )
        #
        framePadding = 4
        if 'framePadding' in kwargs:
            framePadding = kwargs.pop( 'framePadding' )
        #
        percent = 100
        if 'percent' in kwargs:
            percent = kwargs.pop( 'percent' )
        #
        quality = 70
        if 'quality' in kwargs:
            quality = kwargs.pop( 'quality' )
        #
        compression = 'png'
        if 'compression' in kwargs:
            compression = kwargs.pop( 'compression' )
        #
        width = 960
        if 'width' in kwargs:
            width = kwargs.pop( 'width' )
        #
        height = 540
        if 'height' in kwargs:
            height = kwargs.pop( 'height' )
        #
        camera = ''
        if 'camera' in kwargs:
            camera = kwargs.pop( 'camera' )
        #
        mode = 'asIs' #or 'basic', or 'imagePlaneOnly'
        if 'mode' in kwargs:
            mode = kwargs.pop( 'mode' )
        #
        modelPanel = ''
        if 'modelPanel' in kwargs:
            modelPanel = kwargs.pop( 'modelPanel' )
        #
        russianPlayblast = False
        if 'russianPlayblast' in kwargs:
            russianPlayblast = kwargs.pop( 'russianPlayblast' )


        #verify nessessary inputs
        if startTime and endTime and filename and width and height and camera and modelPanel:

            #window
            window_name = 'playblastCaptureWindow'
            window_width = 500
            window_height = 500
            if ( cmds.window( window_name, exists = True ) ):
                    cmds.deleteUI( window_name, window = True )
            if( cmds.windowPref( window_name, exists = True ) ):
                    cmds.windowPref( window_name, remove = True )
            window = cmds.window( window_name, widthHeight = ( window_width, window_height ), title = window_name )

            # setup layout
            formLayout = cmds.formLayout()

            # display options

            #asIs
            polymeshes = cmds.modelEditor( modelPanel, query = True, polymeshes = True )
            nurbsSurfaces = cmds.modelEditor( modelPanel, query = True, nurbsSurfaces = True )
            grid = cmds.modelEditor( modelPanel, query = True, grid = True )
            nurbsCurves = cmds.modelEditor( modelPanel, query = True, nurbsCurves = True )
            locators = cmds.modelEditor( modelPanel, query = True, locators = True )
            hud = cmds.modelEditor( modelPanel, query = True, hud = True )
            handles = cmds.modelEditor( modelPanel, query = True, handles = True )
            displayAppearance = cmds.modelEditor( modelPanel, query = True, displayAppearance = True )
            displayTextures = cmds.modelEditor( modelPanel, query = True, displayTextures = True )
            textures = cmds.modelEditor( modelPanel, query = True, textures = True )
            imagePlane = cmds.modelEditor( modelPanel, query = True, imagePlane = True )
            cameras = cmds.modelEditor( modelPanel, query = True, cameras = True )
            joints = cmds.modelEditor( modelPanel, query = True, joints = True )
            dimensions = cmds.modelEditor( modelPanel, query = True, dimensions = True )
            deformers = cmds.modelEditor( modelPanel, query = True, deformers = True )
            xray = cmds.modelEditor( modelPanel, query = True, xray = True )

            #isolate selected stuff
            '''
            come back to this, how to isolate without it being selection based, need to investigate
            '''
            isFiltered = cmds.modelEditor( modelPanel, query = True, isFiltered = True )
            filteredObjectList = cmds.modelEditor( modelPanel, query = True, filteredObjectList = True )

            #modes
            if mode == 'imagePlaneOnly':
                polymeshes = False
                nurbsSurfaces = False
                grid = False
                nurbsCurves = False
                locators = False
                hud = False
                handles = False
                imagePlane = True
                cameras = True
                joints = False
                dimensions=False
                deformers = False

            if mode == 'basic':
                polymeshes = True
                nurbsSurfaces = False
                grid = False
                nurbsCurves = False
                locators = False
                hud = False
                handles = False
                #imagePlane = True
                #cameras = True
                joints = False
                dimensions=False
                deformers = False

            #make new model editor
            modelView = cmds.modelEditor( 'playblastCaptureWindow_modelView', xray = xray, dimensions=dimensions, deformers=deformers, polymeshes = polymeshes, nurbsSurfaces = nurbsSurfaces, grid = grid, nurbsCurves = nurbsCurves, locators = locators, hud = hud, handles = handles, displayAppearance = displayAppearance, displayTextures = displayTextures, textures = textures, imagePlane=imagePlane, cameras=cameras, joints=joints )

            # attach camera to modelView
            cmds.modelEditor( modelView, edit = True, camera = camera )

            # form layout
            cmds.formLayout( formLayout, edit = True, attachForm = [( modelView, 'top', 0 )] )
            cmds.formLayout( formLayout, edit = True, attachForm = [( modelView, 'left', 0 )] )
            cmds.formLayout( formLayout, edit = True, attachForm = [( modelView, 'bottom', 0 )] )
            cmds.formLayout( formLayout, edit = True, attachForm = [( modelView, 'right', 0 )] )
            cmds.showWindow( window )

            #setup russianPlayblast
            russianPlayblast_range = []
            if russianPlayblast:
                russianPlayblast_factor = .25
                russianPlayblast_range = list(self.drange2(startTime, endTime, russianPlayblast_factor))

            # set focus and playblast
            cmds.setFocus(modelView) #this might not be nessessary
            cmds.modelEditor( modelView, edit = True, activeView = True )
            if not russianPlayblast:
                filename = cmds.playblast( startTime = startTime, endTime =  endTime, format = format, filename = filename, sequenceTime = sequenceTime, viewer = viewer, offScreen = offScreen, clearCache = clearCache, showOrnaments = showOrnaments, framePadding = framePadding, percent = percent, quality = quality, compression = compression, width = width, height = height, forceOverwrite=forceOverwrite )
            elif russianPlayblast:
                filename = cmds.playblast( frame=russianPlayblast_range, format = format, filename = filename, sequenceTime = sequenceTime, viewer = viewer, offScreen = offScreen, clearCache = clearCache, showOrnaments = showOrnaments, framePadding = framePadding, percent = percent, quality = quality, compression = compression, width = width, height = height, forceOverwrite=forceOverwrite )

            #remove window
            if ( cmds.window( window_name, exists = True ) ):
                    cmds.deleteUI( window_name, window = True )

            #
            return filename



