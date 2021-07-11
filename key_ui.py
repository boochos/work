import os

import maya.cmds as cmds
import maya.mel as mm
import webrImport as web

# web
key_sys_lib = web.mod( 'key_sys_lib' )
key_ui_core = web.mod( 'key_ui_core' )


#--------------------------------
# ++  S A V E  S C E N E ++ #
#--------------------------------
class SaveDialogue( key_ui_core.DirDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel, path, parent ):
        super( SaveDialogue, self ).__init__( intWinName, visWinName, buttonLabel, path )
        self.parent = parent

    def buildButton( self ):
        bCmd = self.bCMD( self, self.parent.mode )
        cmds.button( self.button, l = self.buttonLabel, c = bCmd.cmd )

    class bCMD( object ):

        def __init__( self, parent, mode ):
            self.parent = parent
            self.mode = mode

        def cmd( self, *args ):

            fileExt = None
            fileType = cmds.file( query = True, type = True )

            if fileType[0] == 'mayaBinary':
                fileExt = '.mb'
            elif fileType[0] == 'mayaAscii':
                fileExt = '.ma'

            saveName = cmds.text( self.parent.parent.nameTxt, query = True, l = True ) + fileExt
            savePath = cmds.text( self.parent.pathTxt, query = True, l = True )
            finalPath = os.path.join( savePath, saveName )

            if self.mode == 'scene':

                cmds.file( rename = finalPath )
                cmds.file( save = True, type = fileType[0] )
                cmds.deleteUI( self.parent.intWinName, window = True )

            elif self.mode == 'selected':
                sel = cmds.ls( sl = True )
                if len( sel ) > 0:
                    cmds.file( os.path.join( savePath, saveName ), exportSelected = True, type = 'mayaBinary' )
                    cmds.deleteUI( self.parent.intWinName, window = True )
                else:
                    import key_sys_lib
                    key_sys_lib.printMayaWarning( 'Nothing is selected...' )


class SaveWin( key_ui_core.NameDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel, mode ):
        super( SaveWin, self ).__init__( intWinName, visWinName, buttonLabel )
        self.SaveDialogue = 'key_SaveDialogue'
        self.mode = mode

    def buildButton( self ):
        cmds.button( self.button, l = self.cmdButtonLabel, c = self.saveFileDialog )

    def deleteChildren( self, *args ):
        print( self.SaveDialogue )
        if cmds.window( self.SaveDialogue, ex = True ):
            cmds.deleteUI( self.SaveDialogue )

    def findPathFromName( self ):
        path = None
        nameList = cmds.text( self.nameTxt, q = True, l = True ).split( '_' )
        if len( nameList ) > 0:
            seq = nameList[0]
            name = '%s_%s_%s' % ( nameList[0], nameList[1], nameList[2] )

            seqIdx = self.scenepath.rfind( 'SEQ' )
            if seqIdx > -1:
                path = self.scenepath[:seqIdx + 3]
                if os.path.isdir( path ):
                    dirList = os.listdir( path )
                    if seq in dirList:
                        path = os.path.join( path, seq )
                        if os.path.exists( path ):
                            if name in os.listdir( path ):
                                path = os.path.join( path, name, '3D', 'scenes' )
                                if not os.path.exists( path ):
                                    path = None
                            else:
                                path = None
                        else:
                            path = None
                    else:
                        path = None
        return path

    def saveFileDialog( self, *args ):
        self.scenepath = os.path.join( cmds.workspace( q = True, rd = True ), 'scenes' )
        path = self.findPathFromName()

        if path == None:
            if os.path.exists( self.scenepath ):
                print( 'Defaulting to workspace /scenes' )
                path = self.scenepath
            else:
                print( 'Folder does not exist for filename, defaulting to workspace.' )
                path = cmds.workspace( q = True, rd = True )

        SaveWin = SaveDialogue( self.SaveDialogue, 'Browse To Directory', 'S A V E', path, self )
        SaveWin.win()


def saveSceneWin( *args ):
    KeySaveSceneWin = SaveWin( 'key_saveScene', 'Save Scene', 'S E T  S A V E  P A T H', 'scene' )
    KeySaveSceneWin.win()
    cmds.scriptJob( uiDeleted = [KeySaveSceneWin.intWinName, KeySaveSceneWin.deleteChildren] )


def saveSelectedWin( *args ):
    KeySaveSelectedWin = SaveWin( 'key_saveSelected', 'Save Selected', 'S E T  S A V E  P A T H', 'selected' )
    KeySaveSelectedWin.win()
    cmds.scriptJob( uiDeleted = [KeySaveSelectedWin.intWinName, KeySaveSelectedWin.deleteChildren] )

#---------------------#
# ++  R E N D E R  ++ #
#---------------------#


class SetDirectoryDialogue( key_ui_core.DirDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel, path, parent ):
        super( SetDirectoryDialogue, self ).__init__( intWinName, visWinName, buttonLabel, path )
        self.parent = parent
        self.outputname = None
        self.outputpath = None

    def buildButton( self ):
        cmds.button( self.button, l = self.buttonLabel, c = self.bCMD )

    def bCMD( self, *args ):
        self.outputname = cmds.text( self.parent.nameTxt, query = True, l = True )
        if self.outputname != ' ':
            # check if output dir exists
            self.outputpath = os.path.join( self.path, self.outputname )
            self.parent.outputname = self.outputname
            self.parent.outputpath = self.outputpath
            cmds.textField( self.parent.rlPathTxtFld, edit = True, w = 300, tx = cmds.text( self.pathTxt, query = True, l = True ) )

            cmds.setAttr( 'defaultRenderGlobals.imageFilePrefix', self.outputname, type = 'string' )
            cmds.setAttr( 'defaultRenderGlobals.extensionPadding', 4 )

            import maya.mel as mm
            mm.eval( "setMayaSoftwareFrameExt(3, 0);" )

            # set the  workspace image path
            cmds.workspace( rt = ['images', self.outputpath] )
            # enable the render button
            cmds.button( self.parent.rlRenderBut, edit = True, en = True )

        else:
            key_sys_lib.printMayaWarning( 'No file name specified, aborting operation...' )

        cmds.deleteUI( self.intWinName )


class Key_RenderLauncher( key_ui_core.NameDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel ):
        super( Key_RenderLauncher, self ).__init__( intWinName, visWinName, buttonLabel )

        self.renderPathWin = 'key_SetRenderPath'
        self.rlPathTxtFld = self.intWinName + '_rlPathTxtFld'
        self.rlPathForm = self.intWinName + '_rlForm'
        self.rlBrwsPathBut = self.intWinName + '_rlBrwsPathBut'
        self.rlRenderBut = self.intWinName + '_rlRenderBut'
        self.advXfld = self.intWinName + 'rlAdvXFld'
        self.advYfld = self.intWinName + 'rlAdvYFld'
        self.advEndSubDCb = self.intWinName + '_advEndSubDCb'
        self.cpuIntFld = self.intWinName + '_cpuIntFld'
        self.subRndrLyrCB = self.intWinName + '_subRndrLyrCB'
        self.xDivisions = 2
        self.yDivisions = 2
        self.subdivide = False
        self.outputname = None
        self.outputpath = None
        # get the current working images directory
        self.currentWorkspace = os.path.realpath( cmds.workspace( query = True, rd = True ) )
        self.currentImagePath = cmds.workspace( rte = 'images' )
        self.imageFilePrefix = cmds.getAttr( 'defaultRenderGlobals.imageFilePrefix' )
        self.uncompressedTifCb = self.intWinName + '_rl_uncompTifCb'

        self.render_exrCB = None

        version = mm.eval( 'getApplicationVersionAsFloat()' )
        if version == 2011.0:
            self.renderer = 'maya2011'
        elif version == 2012.0:
            self.renderer = 'maya2012'
        else:
            self.renderer = 'maya2009'

        self.renderers = ['maya2009', 'maya2011', 'maya2012']

    def setPathCMD( self ):
        setRenderPathWin = SetDirectoryDialogue( self.renderPathWin, 'Browse To Directory', 'S E T  P A T H', cmds.workspace( query = True, active = True ), self )
        setRenderPathWin.win()

    def cubeRender( self, *args ):
        from render import qube_render
        # make sure the scene has been saved
        sName = cmds.file( query = True, sn = True )
        if len( sName ) != 0:
            # find the TK_pass nodes in the scene
            allObjects = cmds.ls( l = True )
            for obj in allObjects:
                if cmds.nodeType( obj ) == 'p_MegaTK_pass':
                    # set the global tk vars
                    cmds.setAttr( obj + '.render_dir', self.outputpath, type = 'string' )
                    cmds.setAttr( obj + '.fname', self.outputname, type = 'string' )
                    try:
                        # update the UI's if they're open
                        cmds.textFieldGrp( 'AEMegaTKPassFName_textFieldGrp', e = True, tx = self.outputname )
                        cmds.textFieldButtonGrp( 'AEMegaTKPassDir_textFieldButtonGrp', e = True, tx = self.outputpath )
                    except:
                        pass

            render_exr = cmds.checkBox( self.render_exrCB, query = True, v = True )

            # set the image format to .tiff
            if not cmds.checkBox( self.uncompressedTifCb, query = True, v = True ):

                if render_exr:
                    cmds.setAttr( 'defaultRenderGlobals.imageFormat', 51 )
                    cmds.setAttr( 'miDefaultFramebuffer.datatype', 16 )
                    cmds.setAttr( "defaultRenderGlobals.imfPluginKey", 'exr', type = 'string' )
                else:
                    cmds.setAttr( 'defaultRenderGlobals.imageFormat', 3 )
            else:
                pass

            # cmds.setAttr('defaultRenderGlobals.imageFilePrefix','tif',type='string')

            xDivisions = cmds.intField( self.advXfld, q = True, value = True )
            yDivisions = cmds.intField( self.advYfld, q = True, value = True )

            waitfor = cmds.intField( self.waitForField, q = True, value = True )

            if waitfor == 0:
                waitfor = None

            reload( qube_render )
            subRndInt = cmds.checkBox( self.subRndrLyrCB, query = True, v = True )
            subRndVal = False
            if subRndInt:
                subRndVal = True
            jobids = qube_render.Qube_Submit( False, None, cmds.checkBox( self.advEndSubDCb, query = True, value = True ),
                                             self.xDivisions, self.yDivisions,
                                             cmds.intField( self.cpuIntFld, query = True, v = True ), subRndVal,
                                             renderer = self.renderer,
                                             waitfor = waitfor, render_exr = render_exr )

            cmds.confirmDialog( title = 'jobs Launched', message = 'Jobids: ' + str( jobids ), button = 'Ok' )
            # set the image path back to its original setting
            cmds.workspace( rt = ['images', self.currentImagePath] )
            # disable the button
            cmds.button( self.rlRenderBut, edit = True, en = False )

        else:
            key_sys_lib.printMayaWarning( 'Scene Not Saved, operation aborted...' )
        # -- End Def cubeRender

    def set_renderer( self, args ):
        print( args )
        self.renderer = args

    def addControls( self ):
        # create the controls

        if os.uname()[0] == 'Darwin':
            collapsable = True
            collapse = True
        else:
            collapse = False
            collapsable = False

        advFrame = cmds.frameLayout( self.intWinName + '_advFrameLayout', collapsable = collapsable, label = 'Advanced', collapse = collapse, parent = self.intWinName + '_nameConColumnLayout' )
        advColumn = cmds.columnLayout( self.intWinName + '_advColumnLayout', parent = advFrame )
        advForm = cmds.formLayout( self.intWinName + '_advFormLayout', numberOfDivisions = 100, parent = advColumn )

        advSpltTxt = cmds.text( label = 'Split Render:', parent = advForm )
        advSpltCheck = cmds.checkBox( self.advEndSubDCb, l = '', value = 0, parent = advForm, width = 40 )

        advXtxt = cmds.text( label = 'xDivisions:' )
        advXintField = cmds.intField( self.advXfld, value = 2, width = 40 )

        advYtxt = cmds.text( label = 'yDivisions:' )
        advYintField = cmds.intField( self.advYfld, value = 2, width = 40 )

        renderer = cmds.optionMenu( label = 'Render Using:', changeCommand = self.set_renderer )
        for item in self.renderers:
            cmds.menuItem( label = item, parent = renderer )

        waitForLabel = cmds.text( label = 'wait for jobID:' )

        self.waitForField = cmds.intField( value = 0, width = 100 )

        self.render_exrCB = cmds.checkBox( l = 'Render EXR', value = True )

        cmds.optionMenu( renderer, edit = True, value = self.renderer )

        cmds.formLayout( advForm, edit = True,
                        attachForm = [( advSpltTxt, 'top', 8 ), ( advSpltCheck, 'top', 8 ), ( advXtxt, 'top', 8 ), ( advXintField, 'top', 8 ), ( advYtxt, 'top', 8 ), ( advYintField, 'top', 8 ), ( renderer, 'left', 8 ), ( waitForLabel, 'left', 8 )],
                        attachControl = [( advSpltCheck, 'left', 5, advSpltTxt ),
                                       ( advXtxt, 'left', 0, advSpltCheck ),
                                       ( advXintField, 'left', 5, advXtxt ),
                                       ( advYtxt, 'left', 5, advXintField ),
                                       ( advYintField, 'left', 5, advYtxt ),
                                       ( renderer, 'top', 5, advSpltCheck ),
                                       ( waitForLabel, 'top', 5, renderer ),
                                       ( self.waitForField, 'top', 5, renderer ),
                                       ( self.waitForField, 'left', 5, waitForLabel ),
                                       ( self.render_exrCB, 'top', 5, self.waitForField ), ( self.render_exrCB, 'left', 5, waitForLabel )]
                        )

        renderLayerLayout = cmds.frameLayout( 'renderLayout', collapsable = False, label = 'Render Layers', collapse = False, parent = self.intWinName + '_nameConColumnLayout' )
        renderForm = cmds.formLayout( parent = renderLayerLayout )
        render = mm.eval( 'createRenderLayerEditor("%s", "RenderLayerEditor");' % renderForm )
        cmds.formLayout( renderForm, edit = True, h = 150,
                        attachForm = [( "RenderLayerEditor", 'left', 5 ), ( "RenderLayerEditor", 'top', 5 ),
                                    ( "RenderLayerEditor", 'right', 5 ), ( "RenderLayerEditor", 'bottom', 5 )]
                        )

        cmds.formLayout( self.rlPathForm, numberOfDivisions = 100, parent = self.intWinName + '_nameConColumnLayout' )
        cpuTxt = cmds.text( self.intWinName + '_cpuTxt', l = 'CPU`s: ', w = 39 )
        cmds.intField( self.cpuIntFld, v = 5, width = 35 )
        cmds.textField( self.rlPathTxtFld )
        cmds.iconTextButton( self.rlBrwsPathBut, style = 'iconOnly', image = 'fileOpen.xpm', width = 23, height = 23, c = self.setPathCMD )
        cmds.checkBox( self.uncompressedTifCb, l = 'Cancel Image Format override' )
        cmds.checkBox( self.subRndrLyrCB, l = 'Submit Render Layers' )

        cmds.button( self.rlRenderBut, en = False, label = self.cmdButtonLabel, c = self.cubeRender )
        cmds.formLayout( self.rlPathForm, edit = True,
                        attachForm = [( cpuTxt, 'top', 8 ), ( cpuTxt, 'left', 5 ),
                                    ( self.cpuIntFld, 'top', 5 ), ( self.uncompressedTifCb, 'top', 5 ),
                                    ( self.rlPathTxtFld, 'right', 35 ), ( self.rlPathTxtFld, 'left', 5 ),
                                    ( self.rlBrwsPathBut, 'top', 5 ), ( self.rlRenderBut, 'left', 5 ), ( self.rlRenderBut, 'right', 5 ), ( self.rlRenderBut, 'bottom', 5 )],

                        attachControl = [( self.rlPathTxtFld, 'top', 5, self.subRndrLyrCB ), ( self.cpuIntFld, 'left', 5, cpuTxt ), ( self.uncompressedTifCb, 'left', 5, self.cpuIntFld ),
                                       ( self.subRndrLyrCB, 'left', 5, self.cpuIntFld ), ( self.subRndrLyrCB, 'top', 5, self.uncompressedTifCb ),
                                       ( self.rlBrwsPathBut, 'top', 5, self.subRndrLyrCB ), ( self.rlBrwsPathBut, 'left', 5, self.rlPathTxtFld ),
                                       ( self.rlRenderBut, 'top', 5, self.rlPathTxtFld )]
                        )

    def deleteChildren( self, *args ):
        if cmds.window( self.renderPathWin, ex = True ):
            cmds.deleteUI( self.renderPathWin )

    def win( self ):
        if cmds.window( self.intWinName, exists = True ):
            cmds.deleteUI( self.intWinName, window = True )

        cmds.window( self.intWinName, menuBar = True, title = self.visWinName, width = 400, height = 800 )
        self.buildMenuBar()
        cmds.paneLayout( configuration = "horizontal2", ps = [1, 50, 25] )
        self.buildNameContents()
        self.addControls()
        self.parseSceneNameAndPopulate()
        self.buildName()
        cmds.scriptJob( uiDeleted = [self.intWinName, self.deleteChildren] )
        cmds.showWindow( self.intWinName )


def keyLaunchRenderWin( *args ):
    KeyRenderLauncher = Key_RenderLauncher( 'key_renderLauncher', 'Render  Launcher', 'L A U N C H ' )
    KeyRenderLauncher.win()

#------------------ #
#  -- Geo Cache --  #
#-------------------#


class KeyCacheSetDirectoryDialogue( key_ui_core.DirDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel, path, parent ):
        super( KeyCacheSetDirectoryDialogue, self ).__init__( intWinName, visWinName, buttonLabel, path )
        self.parent = parent
        self.outputname = None
        self.outputpath = None

    def buildButton( self ):
        cmds.button( self.button, l = self.buttonLabel, c = self.bCMD )

    def bCMD( self, *args ):
        self.outputname = cmds.text( self.parent.nameTxt, query = True, l = True )
        if self.outputname != ' ':
            # check if output dir exists
            self.outputpath = os.path.join( self.path, self.outputname )
            self.parent.outputname = self.outputname
            self.parent.outputpath = self.outputpath
            cmds.textField( self.parent.pathTextField, edit = True, w = 300, tx = cmds.text( self.pathTxt, query = True, l = True ) )
        else:
            key_sys_lib.printMayaWarning( 'No file name specified, aborting operation...' )

        cmds.deleteUI( self.intWinName )


class Key_GeoCache( key_ui_core.NameDialog_v01 ):

    def __init__( self, intWinName, visWinName, buttonLabel ):
        super( Key_GeoCache, self ).__init__( intWinName, visWinName, buttonLabel )
        self.checkBox = self.intWinName + '_chkBxGrp'
        self.pathTextField = self.intWinName + '_txtFld'
        self.setPathWin = self.intWinName + '_cacheSetPathWin'
        self.cachePath = os.path.join( cmds.workspace( q = True, rd = True ), 'data/geo_cache' )

    def buildButton( self ):
        pass

    def geoCacheCMD( self, *args ):
        # get the selection list
        sel = cmds.ls( selection = True )
        passSel = True
        for each in sel:
            relatives = cmds.listRelatives( each )
            if relatives != None:
                if cmds.nodeType( relatives[0] ) != 'mesh':
                    passSel = False
                    break
            else:
                passSel = False

        if self.pathTextField != None and passSel == True and len( sel ) != 0:
            cacheList = []
            # get the path so write the cache to
            path = cmds.textField( self.pathTextField, query = True, text = True )

            # get the file name
            filename = cmds.text( self.nameTxt, query = True, label = True )
            # check to see if the current folder exists
            finalPath = os.path.join( path, filename )
            isDir = os.path.isdir( finalPath )
            if ( isDir ):
                key_sys_lib.printMayaWarning( 'Conflict!!!' )
                key_sys_lib.printMayaWarning( finalPath + ' all ready exists' )
                key_sys_lib.printMayaWarning( 'Geometry Cache aborted.....' )
            else:
                import maya.mel as mm
                # create the output directory
                os.mkdir( finalPath )
                gPlayBackSlider = mm.eval( '$tmpVar = $gPlayBackSlider' )
                minRange = cmds.playbackOptions( query = True, minTime = True ) - 1
                maxRange = cmds.playbackOptions( query = True, maxTime = True ) + 1
                useAudio = cmds.checkBox( self.checkBox, query = True, v = True )
                if useAudio == 1:
                    soundNode = cmds.timeControl( gPlayBackSlider, query = True, sound = True )
                    if len( soundNode ) > 0:
                        maxRange = str( cmds.sound( soundNode, query = True, length = True ) + 1 ).split( '.' )[0]
                    else:
                        key_sys_lib.printMayaWarning( 'Use Audio Length is selected, but there is no audio in the timeline. Using Animation slider range.' )
                for each in sel:
                    # extract the shape node
                    cacheList.append( cmds.listRelatives( each, shapes = True )[0] )

                mm.eval( 'doCreateGeometryCache 4 { "0", "' + str( minRange ) + '", "' + str( maxRange ) + '", "OneFilePerFrame", "0", "' + finalPath + '","0","' + filename + '","0", "add", "1", "1", "1","0","1"}' )
        else:
            print( 'Select a valid mesh to Geometry Cache.' )

    def setPathCMD( self ):
        setRenderPathWin = KeyCacheSetDirectoryDialogue( self.setPathWin, 'Browse To Directory', 'S E T  P A T H', self.cachePath, self )
        setRenderPathWin.win()

    def getPath( self ):
        return cmds.textField( self.pathTextField, query = True, tx = True )

    def addControls( self ):
        # create a load file window
        if os.path.isdir( self.cachePath ) != True:
            self.cachePath = os.path.join( cmds.workspace( q = True, rd = True ) )

        form = cmds.formLayout( self.intWinName + '_formLayout', numberOfDivisions = 100 )
        cmds.checkBox( self.checkBox, l = ' Use audio Length' )
        sep = cmds.separator()
        cmds.textField( self.pathTextField, tx = self.cachePath, w = 300 )
        icnBtn = cmds.iconTextButton( self.intWinName + '_icnTxtBtn', style = 'iconOnly', image = 'fileOpen.xpm', width = 23, height = 23, c = self.setPathCMD )
        cmds.button( self.button, l = self.cmdButtonLabel, c = self.geoCacheCMD )
        cmds.setParent( '..' )

        cmds.formLayout( form, edit = True,
                        attachForm = [( self.checkBox, 'left', 5 ), ( self.checkBox, 'top', 5 ),
                                    ( sep, 'left', 5 ), ( sep, 'right', 5 ),
                                    ( self.pathTextField, 'left', 5 ), ( self.pathTextField, 'right', 33 ),
                                    ( self.button, 'left', 5 ), ( self.button, 'right', 5 )],
                        attachControl = [( sep, 'top', 5, self.checkBox ),
                                       ( self.pathTextField, 'top', 5, sep ),
                                       ( icnBtn, 'top', 5, sep ), ( icnBtn, 'left', 5, self.pathTextField ),
                                       ( self.button, 'top', 5, self.pathTextField )] )

    def deleteChildren( self, *args ):
        if cmds.window( self.setPathWin, ex = True ):
            cmds.deleteUI( self.setPathWin )

    def win( self ):
        if cmds.window( self.intWinName, exists = True ):
            cmds.deleteUI( self.intWinName, window = True )

        cmds.window( self.intWinName, menuBar = True, title = self.visWinName, width = 400, height = 650 )
        self.buildMenuBar()
        cmds.paneLayout( configuration = "horizontal2", h = 100, ps = [1, 100, 25] )
        self.buildNameContents()
        self.addControls()
        self.parseSceneNameAndPopulate()
        self.buildName()
        cmds.showWindow( self.intWinName )


def geoCacheWin( *args ):
    KeyCache = Key_GeoCache( 'key_geoCache', 'Geometry Cache', 'Cache Geo' )
    KeyCache.win()
    cmds.scriptJob( uiDeleted = [KeyCache.intWinName, KeyCache.deleteChildren] )
