from __future__ import with_statement
from pymel.core import *
from pymel.util import *
import maya.OpenMaya as openMaya
import pickle
import time
import os
import shutil
import maya.cmds as cmds

def message( what='', maya=False ):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print what

class AnimationToolboxPickle( object ):
    def __init__( self, name, date, time, sel, author, start, end, comment, platform ):
        self.name = str( name )
        self.date = str( date )
        self.time = str( time )
        self.sel = sel
        self.author = str( author )
        self.start = str( start )
        self.end = str( end )
        self.comment = str( comment )
        self.platform = str( platform )

class AnimationToolbox( object ):

    def __init__( self, path=None, fRange=None ):
        self.animPlugin()
        self.fRange = fRange
        if path == None:
            self.path = self.animPath()
        else:
            self.path = path

    #load plugin
    def animPlugin( self ):
        state = pluginInfo( 'animImportExport', q=True, loaded=True )
        if state == 0:
            platform = os.name
            print platform
            if platform == 'Linux':
                cmds.pluginInfo( '/software/apps/maya/2012.sp1/cent5.x86_64/bin/plug-ins/' + 'animImportExport', e=True, a=True )
                cmds.loadPlugin( 'animImportExport' )
            elif platform == 'nt':
                path = "C:\Program Files\Autodesk\Maya2013" + "\\" + "bin\plug-ins" + "\\" + "animImportExport.mll"
                print path
                cmds.pluginInfo( 'C:\Program Files\Autodesk\Maya2013\\bin\plug-ins\\' + 'animImportExport.mll', e=True, a=True )
                cmds.loadPlugin( 'animImportExport' )
            else:
                pass
                #cmds.pluginInfo('/Applications/Autodesk/maya2009/Maya.app/Contents/MacOS/plug-ins/' + 'animImportExport.bundle', e=True, a=True)
                #cmds.loadPlugin('animImportExport')

    #get current frame, and last playback frame
    def frameRange( self ):
        start = currentTime( q=True )
        end = playbackOptions( q=True, max=True )
        return start , end

    #export anim to file
    def animExport( self ):
        sel = ls( sl=True )
        if len( sel ) > 0:
            if self.fRange == None:
                self.fRange = self.frameRange()
            ops = "precision=8;intValue=17;nodeNames=0;verboseUnits=0;whichRange=2;range=" + str( self.fRange[0] ) + ":" + str( self.fRange[1] )
            ops += ";options=keys;hierarchy=none;controlPoints=0;shapes=0;useChannelBox=0;copyKeyCmd=-animation objects -time >"
            ops += str( self.fRange[0] ) + ":" + str( self.fRange[1] ) + "> -float >" + str( self.fRange[0] ) + ":" + str( self.fRange[1] ) + "> -option keys -hierarchy none -controlPoints 0 -shape 0 "
            exportSelected( self.path, es=True, typ="animExport", op=ops )
            openMaya.MGlobal.displayInfo( 'Animation exported from  ' + str( self.fRange[0] ) + '  to  ' + str( self.fRange[1] ) )
        else:
            openMaya.MGlobal.displayError( '... Select at least one object with animation...' )

    #import anim from file
    def animImport( self ):
        sel = ls( sl=True )
        if len( sel ) > 0:
            if self.fRange == None:
                self.fRange = self.frameRange()
            ops = "targetTime=1;time=" + str( self.fRange[0] ) + ";copies=1;option=merge;connect=0"
            importFile( self.path, i=True, typ="animImport", ra=True, namespace="animTemp", options=ops )
            #cmds.select(sel)
            openMaya.MGlobal.displayInfo( 'Animation imported at  -' + str( self.fRange[0] ) )
        else:
            openMaya.MGlobal.displayError( '... Select at least one object to apply animation to animation...' )

    #create directory for animation file
    def animPath( self ):
        path = os.path.join( os.getenv( 'HOME' ), 'animExport' )
        if os.path.isdir( path ):
            return os.path.join( path, 'animTemp.anim' )
        else:
            os.mkdir( path, 0777 )
            return os.path.join( path, 'animTemp.anim' )

    #copy anim
    def animCopy( self ):
        sel = ls( sl=True )
        if len( sel ) > 0:
            frame = self.frameRange()
            copyKey( sel, time=( frame[0], frame[1] ), option='keys', hierarchy='none', controlPoints=0, shape=1 )
            # openMaya.MGlobal.displayInfo( 'Animation copied from  -' + str( frame[0] ) + '-  to  -' + str( frame[1] ) + '-\";' )
        else:
            openMaya.MGlobal.displayWarning( '... Select at least one object with animation...' )

    #paste anim
    def animPaste( self ):
        sel = ls( sl=True )
        if len( sel ) > 0:
            frame = self.frameRange()
            pasteKey( sel, time=( frame[0], ), f=( frame[0], ), option='merge', copies=1, connect=0, timeOffset=0, floatOffset=0, valueOffset=0 )
            openMaya.MGlobal.displayInfo( 'Animation pasted at  -' + str( frame[0] ) + '-\";' )
        else:
            openMaya.MGlobal.displayWarning( '... Select at least one object with animation...' )

class AnimationExportManager( object ):
    def __init__( self ):
        self.export_path = None
        self.pickle = None
        self.getExportPath()

    def getKeyInfo( self, start=None, end=None ):
        kInfo = None
        if start != None and end != None:
            kStr = '%s:%s' % ( start, end )
            kInfo = keyframe( query=True, t=kStr )
        else:
            kInfo = keyframe( query=True )
        kInfo.sort()
        keyList = []
        for i in kInfo:
            if i not in keyList:
                keyList.append( i )

        loKey = keyList[0]
        hiKey = keyList[len( keyList ) - 1]
        cFrm = currentTime()
        nKey = findKeyframe()
        fnlRng = [None, None]

        if cFrm in keyList:
            if cFrm <= nKey:
                loKey = cFrm
        elif cFrm < nKey:
            loKey = nKey
        return [loKey, hiKey]

    def getExportPath( self ):
        '''
        Export path is changed depeding on private or public, and which project, the user is currently in.
        /Volumes/VFX/Projects/Treasure_Buddies/Assets/Published_Production_Assets/Department_Libraries/Animation_Library
        '''
        basePath = os.path.expanduser( '~' ) + '/maya/animationLibrary/'
        project = 'animation'
        user = getEnv( 'USER' )
        if os.path.exists( basePath ):
            path = os.path.join( basePath, project )
            if not os.path.exists( path ):
                #self.export_path = 'C:/Users/Slabster & Vicster/Documents/maya'
                os.mkdir( path )
                #wStr= 'User path not found in: %s\n expected, %s' %(basePath, user)
                #openMaya.MGlobal.displayWarning(wStr)
            self.export_path = path
        else:
            os.mkdir( basePath )
            self.export_path = path
            message( "path:   '" + basePath + "'   created" )

    def radioBtnCMD( self, *args ):
        idx = radioButtonGrp( 'ovrExpt_rngBtnGrp_radioButtonGrp', query=True, sl=True )
        if idx == 1:
            text( 'ovrExpt_strtTxt_text', edit=True, en=False )
            intField( 'ovrExpt_strtIntFld_intField', edit=True, en=False )
            text( 'ovrExpt_endTxt_text', edit=True, en=False )
            intField( 'ovrExpt_endIntFld_intField', edit=True, en=False )
        elif idx == 2:
            text( 'ovrExpt_strtTxt_text', edit=True, en=True )
            intField( 'ovrExpt_strtIntFld_intField', edit=True, en=True )
            text( 'ovrExpt_endTxt_text', edit=True, en=True )
            intField( 'ovrExpt_endIntFld_intField', edit=True, en=True )

    def validateText( self, *args ):
        valStr = textField( 'ovrExpt_nameFld_textField', query=True, tx=True )
        valExp = ',./;\'[]=-!@#$%^&*()+<>?:"}{|\\ '
        for i in valStr:
            if i in valExp:
                textField( 'ovrExpt_nameFld_textField', edit=True, tx='None' )
                break

    def getFrameRange( self, *args ):
        if radioButtonGrp( 'ovrExpt_rngBtnGrp_radioButtonGrp', query=True, sl=True ) == 1:
            return self.getKeyInfo()
        else:
            crntTime = currentTime()
            currentTime( intField( 'ovrExpt_strtIntFld_intField', query=True, v=True ) )
        fRange = self.getKeyInfo( start=intField( 'ovrExpt_strtIntFld_intField', query=True, v=True ), end=intField( 'ovrExpt_endIntFld_intField' , query=True, v=True ) )
        currentTime( crntTime )
        return fRange

    def getDate( *args ):
        return time.strftime( '%d/%m/%Y' )

    def getTime( *args ):
        return time.strftime( '%I:%M:%S %p' )

    def createPickle( self, path ):
        #Animation pickle information
        f = open( os.path.join( path, self.pickle.name + '.api' ), 'wb' )
        pickle.dump( self.pickle, f )
        f.close()

    def exportCMD( self, *args ):
        if not os.path.exists( self.export_path ):
            os.mkdir( self.export_path, 0777 )
        exportName = textField( 'ovrExpt_nameFld_textField', query=True, tx=True )
        if exportName != 'None':
            exportPath = os.path.join( self.export_path, exportName )
            print exportPath, '______________'
            if not os.path.exists( exportPath ):
                if len( ls( sl=True ) ) > 0:
                    selList = []
                    #loop to get objects name as a string
                    for i in ls( sl=True ):
                        selList.append( str( i.name() ) )
                    os.mkdir( exportPath )
                    fRange = self.getFrameRange()
                    comments = textField( 'ovrExpt_comment_textField', query=True, tx=True )
                    self.pickle = AnimationToolboxPickle( exportName, self.getDate(), self.getTime(), selList,
                                                      getEnv( 'USER' ), fRange[0], fRange[1], comments, os.name )
                    self.createPickle( exportPath )
                    AnimationToolbox( path=os.path.join( exportPath, exportName + '.anim' ), fRange=fRange ).animExport()
                else:
                    openMaya.MGlobal.displayError( 'Nothing is selected, export aborted...' )
            else:
                openMaya.MGlobal.displayError( 'Directory with that name all ready exists, export aborted' )
        else:
            setFocus( 'ovrExpt_nameFld_textField' )
            openMaya.MGlobal.displayError( 'Invalid name, export aborted...' )

    def window( self ):
        if window( 'Animation_exporter', ex=True ):
            deleteUI( 'Animation_exporter' )

        with window( 'Animation_exporter', t='Animation Exporter' ):
            mainLayout = formLayout( 'ovrExpt_formLayout', numberOfDivisions=100 )
            with mainLayout:
                exPthTxt = text( 'ovrExpt_exPth_text', l='Export Path: ', w=65, align='left', h=15 )
                exPthTxtFld = textField( 'ovrExpt_exPthTxtFld_textField', tx=self.export_path )

                nameTxt = text( 'ovrExpt_name_text', l='Name: ', w=60 )
                nameFld = textField( 'ovrExpt_nameFld_textField', tx='None', cc=self.validateText )

                cmntTxt = text( 'ovrExpt_comment_text', l='Comments:', align='left', w=60 )
                cmntTxtFld = textField( 'ovrExpt_comment_textField' )

                rngTxt = text( 'ovrExpt_rng_text', l='Range Options:', align='left' )
                rngBtnGrp = radioButtonGrp( 'ovrExpt_rngBtnGrp_radioButtonGrp', labelArray2=['Current Frame -> End of Frames', 'Use Custom:'],
                                           adj=1, cw=[1, 200], sl=1, vr=True, numberOfRadioButtons=2, h=40, cc=self.radioBtnCMD )

                strtTxt = text( 'ovrExpt_strtTxt_text', l='Start:', align='left', w=28, en=False )
                strtIntFld = intField( 'ovrExpt_strtIntFld_intField', v=0, w=50, en=False )

                endTxt = text( 'ovrExpt_endTxt_text', l='End:', align='left', en=False )
                endIntFld = intField( 'ovrExpt_endIntFld_intField', w=50, en=False, v=1 )

                exBtn = button( 'ovrExpt_exBtn_button', l='E X P O R T', c=self.exportCMD )
                #by setting the focus the field is updated and the text fills the control
                setFocus( 'ovrExpt_exPthTxtFld_textField' )
                exPthTxtFld = textField( 'ovrExpt_exPthTxtFld_textField', edit=True, ed=False )

                formLayout( mainLayout, edit=True,
                           attachForm=[
                                            ( exPthTxt, 'top', 8 ), ( exPthTxt, 'left', 5 ),
                                            ( exPthTxtFld, 'top', 5 ), ( exPthTxtFld, 'right', 5 ),
                                            ( nameTxt, 'left', 23 ),
                                            ( nameFld, 'right', 5 ),
                                            ( cmntTxt, 'left', 5 ),
                                            ( cmntTxtFld, 'right', 5 ),
                                            ( rngTxt, 'left', 5 ), ( rngTxt, 'right', 5 ),
                                            ( rngBtnGrp, 'left', 5 ), ( rngBtnGrp, 'right', 5 ),
                                            ( strtTxt, 'left', 58 ),
                                            ( exBtn, 'left', 5 ), ( exBtn, 'right', 5 ), ( exBtn, 'bottom', 5 )],
                           attachControl=[
                                            ( exPthTxtFld, 'left', 5, exPthTxt ),
                                            ( nameTxt, 'top', 8, exPthTxt ), ( nameTxt, 'top', 5, exPthTxtFld ),
                                            ( nameFld, 'left', 5, exPthTxt ), ( nameFld, 'top', 5, exPthTxtFld ),
                                            ( cmntTxt, 'top', 8, nameFld ),
                                            ( cmntTxtFld, 'left', 5, exPthTxt ), ( cmntTxtFld, 'top', 5, nameFld ),
                                            ( rngTxt, 'top', 5, cmntTxtFld ),
                                            ( rngBtnGrp, 'top', 0, rngTxt ),
                                            ( strtTxt, 'top', 8, rngBtnGrp ),
                                            ( strtIntFld, 'left', 5, strtTxt ), ( strtIntFld, 'top', 5, rngBtnGrp ),
                                            ( endTxt, 'left', 15, strtIntFld ), ( endTxt, 'top', 8, rngBtnGrp ),
                                            ( endIntFld, 'left', 5 , endTxt ), ( endIntFld, 'top', 5, rngBtnGrp ),
                                            ( exBtn, 'top', 5, endTxt )]
                           )
        setFocus( 'ovrExpt_nameFld_textField' )


class AnimationImportManager( object ):
    def __init__( self ):
        self.mainForm = 'aim_formLayout'
        self.libRdBtnGrp = 'aim_library_radioButtonGrp'
        self.nmSpcOptMn = 'aim_namespace_optionMenu'

        self.anmTxt = 'aim_anim_text'
        self.aim_tsl = 'aim_anim_textScrollList'
        self.dateInfoTxt = 'aim_dateInfo_text'
        self.timeInfoTxt = 'aim_timeInfo_text'
        self.athrInfoTxt = 'aim_athrInfo_text'
        self.strtInfoTxt = 'aim_strtInfo_text'
        self.endInfoTxt = 'aim_endInfo_text'
        self.cmntInfoTxt = 'aim_cmntInfo_text'
        self.pltfInfoTxt = 'aim_pltfInfo_text'
        self.rngRadBtnGrp = 'aim_rng_radioButtonGrp'
        self.rngIntFld = 'aim_rng_intField'

        self.delBtn = 'aim_del_button'
        self.pubBtn = 'aim_pub_button'
        self.impBtn = 'aim_imp_button'

        self.pickle = None
        self.working_path = None
        self.publish_path = None
        self.anim_path = None

    def setImportPath( self ):
        libCheck = radioButtonGrp( self.libRdBtnGrp, query=True, sl=True )
        basePath = os.path.expanduser( '~' ) + '/maya/animationLibrary/'
        project = 'animation'
        user = getEnv( 'USER' )
        pubPath = os.path.expanduser( '~' ) + '/maya/animationPublished'

        if libCheck == 1:
            if os.path.exists( basePath ):
                path = os.path.join( basePath, project )
            else:
                print 'base path does not exist'
            if os.path.exists( path ):
                usrPath = os.path.join( path )
                if os.path.exists( usrPath ):
                    self.working_path = usrPath
                else:
                    os.mkdir( usrPath, 0777 )
                    self.working_path = usrPath

            else:
                os.mkdir( path )
                self.working_path = usrPath
                #wStr= 'User path not found in: %s\nexpected, %s' %(tmpPath, user)
                #openMaya.MGlobal.displayWarning(wStr)

            if os.path.exists( pubPath ):
                self.publish_path = pubPath
            else:
                os.mkdir( pubPath )
                self.publish_path = pubPath
                #wStr= 'Public path not found, was expecting, %s' %(pubPath)
                #openMaya.MGlobal.displayWarning(wStr)

        elif libCheck == 2:
            self.working_path = self.publish_path

    def rangeRBGCMD( self, *args ):
        sel = radioButtonGrp( self.rngRadBtnGrp, query=True, sl=True )
        if sel == 1:
            text( 'aim_frm_text', edit=True, en=False )
            intField( self.rngIntFld, edit=True, en=False )
        elif sel == 2:
            text( 'aim_frm_text', edit=True, en=True )
            intField( self.rngIntFld, edit=True, en=True )


    def populate_aim_tsl( self ):
        #delete the contents first
        textScrollList( self.aim_tsl, edit=True, ra=True )
        if self.working_path != None:
            dirs = os.listdir( self.working_path )
            dirs.sort()
            for i in dirs:
                path = os.path.join( self.working_path, i )
                if os.path.isdir( path ):
                    textScrollList( self.aim_tsl, edit=True, append=i )

    def loadImportUI( self ):
        if textScrollList( self.aim_tsl, query=True, ni=True ) > 0:
            textScrollList( self.aim_tsl, edit=True, sii=1 )
            self.aim_tsl_selectCMD()
        else:
            self.clearAnimInfo()

    def processPickle( self ):
        text( self.dateInfoTxt, edit=True, l=self.pickle.date )
        text( self.timeInfoTxt, edit=True, l=self.pickle.time )
        text( self.strtInfoTxt, edit=True, l=self.pickle.start )
        text( self.endInfoTxt, edit=True, l=self.pickle.end )
        text( self.athrInfoTxt, edit=True, l=self.pickle.author )
        text( self.pltfInfoTxt, edit=True, l=self.pickle.platform )
        text( self.cmntInfoTxt, edit=True, l=self.pickle.comment )

    def publishCMD( self, *args ):
        selItem = textScrollList( self.aim_tsl, query=True, si=True )[0]
        localCopy = os.path.join( self.working_path, selItem )
        if os.path.exists( localCopy ):
            pubCopy = os.path.join( self.publish_path, selItem )
            if not os.path.exists( pubCopy ):
                shutil.copytree( localCopy, pubCopy )
                #os.system('cp -R ' + localCopy + ' ' + self.publish_path)
                fStr = 'Publish Success!: %s' % pubCopy
                openMaya.MGlobal.displayInfo( fStr )
            else:
                fStr = '%s folder all ready exists in the Public folder.Publish aborted' % ( selItem )
                openMaya.MGlobal.displayError( fStr )

    def aim_tsl_selectCMD( self ):
        getItem = textScrollList( self.aim_tsl, query=True, si=True )
        if len( getItem ) > 0:
            selItem = getItem[0]
            path = os.path.join( self.working_path, selItem )
            print path
            print os.listdir( path )
            if os.path.exists( path ):
                for i in os.listdir( path ):
                    if i[0] != '.':
                        split = i.split( '.' )
                        print split
                        if split[1] == 'api':
                            f = open( os.path.join( path, i ), 'rb' )
                            self.pickle = pickle.load( f )
                            f.close()
                            self.processPickle()
                        else:
                            self.anim_path = os.path.join( path, i )
        else:
            self.clearAnimInfo()

    def clearAnimInfo( self ):
        text( self.dateInfoTxt, edit=True, l='None' )
        text( self.timeInfoTxt, edit=True, l='None' )
        text( self.strtInfoTxt, edit=True, l='None' )
        text( self.endInfoTxt, edit=True, l='None' )
        text( self.athrInfoTxt, edit=True, l='None' )
        text( self.pltfInfoTxt, edit=True, l='None' )
        text( self.cmntInfoTxt, edit=True, l='None' )

    def findReferenceNodes( self ):
        refNodes = ls( type='reference' )
        for node in refNodes:
            try:
                ref = FileReference( node )
                nmspace = ref.namespace
                menuItem( nmspace + '_menuItem', l=nmspace, parent=self.nmSpcOptMn )
            except:
                iStr = '%s, is not associated with a reference file, node skipped.' % ( node )
                openMaya.MGlobal.displayInfo( iStr )

    def importAnimCMD( self, *args ):
        if len( textScrollList( self.aim_tsl, query=True, si=True ) ) > 0:
            select( cl=True )
            sel = radioButtonGrp( self.rngRadBtnGrp, query=True, sl=True )
            nmSpace = optionMenu( self.nmSpcOptMn, query=True, v=True )
            if nmSpace != 'None':
                for i in self.pickle.sel:
                    find = i.rfind( ':' )
                    if find != -1:
                        select( nmSpace + ':' + i.split( ':' )[1], tgl=True )
                    else:
                        select( nmSpace + ':' + str( i ), tgl=True )

            else:
                for i in self.pickle.sel:
                    find = i.rfind( ':' )
                    if find != -1:
                        select( i.split( ':' )[1], tgl=True )
                    else:
                        select( self.pickle.sel, tgl=True )
            if sel == 1:
                AnimationToolbox( self.anim_path ).animImport()
            else:
                strt = intField( self.rngIntFld, query=True, v=True )
                AnimationToolbox( self.anim_path, [strt, ''] ).animImport()

    def buildButtonLayout( self, *args ):
        #if it exists delete it so the buttons arn't blocked from clicking
        try:
            deleteUI( self.btnForm )
        except:
            pass
        cmds.setParent( self.mainForm )
        self.btnForm = horizontalLayout()

        with self.btnForm:
            button( self.delBtn, l='D E L E T E', c=self.deleteAnimCMD )
            button( self.pubBtn, l='P U B L I S H', c=self.publishCMD )
            button( self.impBtn, l='I M P O R T', c=self.importAnimCMD )
            cmds.setParent( self.mainForm )

            formLayout( self.mainForm, edit=True,
                       attachForm=[( self.btnForm, 'right', 5 ), ( self.btnForm, 'bottom', 5 )],
                       attachControl=[( self.btnForm, 'left', 5, self.midSep ), ( self.btnForm, 'top', 5, self.btnSep )] )

        self.btnForm.redistribute()

    def deleteAnimCMD( self, *args ):
        selItem = textScrollList( self.aim_tsl, query=True, si=True )[0]
        path = os.path.join( self.working_path, selItem )
        if os.path.exists( path ):
            shutil.rmtree( path )
            self.populate_aim_tsl()
            self.loadImportUI()
            msgStr = '%s, has been deleted.' % ( selItem )
            openMaya.MGlobal.displayInfo( msgStr )

    def libRBGCMD( self, *args ):
        self.setImportPath()
        val = radioButtonGrp( self.libRdBtnGrp, query=True, sl=True )
        #private checkbox has been checked
        if val == 1:
            #set the controls to reflect the current state
            text( self.anmTxt, edit=True, l='Animations (Private):' )
            deleteUI( self.impBtn )
            self.buildButtonLayout()

            self.setImportPath()
            self.populate_aim_tsl()
            self.loadImportUI()

        #public checkbox has been checked
        elif val == 2:
            text( self.anmTxt, edit=True, l='Animations (Public):' )
            deleteUI( self.delBtn )
            deleteUI( self.pubBtn )
            deleteUI( self.impBtn )
            button( self.impBtn, l='I M P O R T ', parent=self.btnForm, c=self.importAnimCMD )

            formLayout( self.btnForm, edit=True,
                       attachForm=[( self.impBtn, 'left', 0 ), ( self.impBtn, 'top', 0 ),
                                   ( self.impBtn, 'right', 0 ), ( self.impBtn, 'bottom', 0 )] )

            setFocus( self.impBtn )
            self.setImportPath()
            self.populate_aim_tsl()
            self.loadImportUI()

    def window( self ):
        win_name = 'animation_import_manager'
        if window( win_name, ex=True ):
            deleteUI( win_name )

        with window( win_name, t='Animation Import Manager' ):
            mainform = formLayout( self.mainForm, numberOfDivisions=100 )
            with mainform:
                libTxt = text( 'aim_lib_text', l='Library Location:', align='left', h=15, fn='boldLabelFont' )
                radioButtonGrp( self.libRdBtnGrp, nrb=2, la2=[' Private', ' Public'], sl=1, onc=self.libRBGCMD )

                libSep = separator()

                nmSpcTxt = text( 'aim_nmSpc_text', l='Namespace:', align='left', h=15, w=78, fn='boldLabelFont' )
                optionMenu( self.nmSpcOptMn )
                menuItem( 'aim_none_menuItem', l='None' )

                rngOptTxt = text( 'aim_rng_text', l='Range Options:', align='left', h=15, fn='boldLabelFont' )
                rngRdBtnGrp = radioButtonGrp( self.rngRadBtnGrp, numberOfRadioButtons=2, sl=1,
                                             vr=True, labelArray2=['Current Frame', 'Use Custom'], cc=self.rangeRBGCMD )
                rngFrmTxt = text( 'aim_frm_text', l='Frame:', align='left', width=36, en=False )
                rngIntFld = intField( self.rngIntFld, w=40, en=False )
                rngSep = separator()

                anmTslSep = separator( width=227 )
                self.midSep = separator( hr=False )

                #place the top controls
                formLayout( self.mainForm, edit=True,
                       attachForm=[( libTxt, 'left', 5 ), ( libTxt, 'top', 5 ),
                                            ( libSep, 'left', 0 ),
                                        ( self.libRdBtnGrp, 'left', 15 ),
                                            ( nmSpcTxt, 'left', 5 ),
                                            ( self.midSep, 'left', 227 ), ( self.midSep, 'top', 0 ), ( self.midSep, 'bottom', 5 ),
                                            ( self.nmSpcOptMn, 'left', 15 ),
                                            ( rngSep, 'left', 0 ),
                                            ( rngOptTxt, 'left', 5 ),
                                            ( rngRdBtnGrp, 'left', 14 ),
                                            ( rngFrmTxt, 'left', 15 ),
                                        ( anmTslSep, 'left', 0 )],
                       attachControl=[
                                            ( libSep, 'top', 5, self.libRdBtnGrp ), ( libSep, 'right', 0, self.midSep ),
                                            ( self.libRdBtnGrp, 'top', 7, libTxt ),
                                            ( nmSpcTxt, 'top', 5, libSep ),
                                            ( self.nmSpcOptMn, 'top', 5, nmSpcTxt ), ( self.nmSpcOptMn, 'right', 5, self.midSep ),
                                            ( rngSep, 'top', 5, self.nmSpcOptMn ), ( rngSep, 'right', 0, self.midSep ),
                                            ( rngOptTxt, 'top', 5, rngSep ),
                                            ( rngRdBtnGrp, 'top', 5, rngOptTxt ),
                                            ( rngFrmTxt, 'top', 7, rngRdBtnGrp ),
                                            ( rngIntFld, 'left', 5, rngFrmTxt ), ( rngIntFld, 'top', 5, rngRdBtnGrp ),
                                        ( anmTslSep, 'top', 5, rngIntFld )]
                       )

                #Place the bottom left controls
                text( self.anmTxt, l='Animations (Private):', h=15, align='left', w=150, fn='boldLabelFont' )
                textScrollList( self.aim_tsl, sc=self.aim_tsl_selectCMD )

                formLayout( self.mainForm, edit=True,
                       attachForm=[( self.anmTxt, 'left', 5 ),
                                   ( self.aim_tsl, 'left', 5 ), ( self.aim_tsl, 'bottom', 5 )],
                       attachControl=[( self.anmTxt, 'top', 5, anmTslSep ),
                                            ( self.aim_tsl, 'top', 5, self.anmTxt ), ( self.aim_tsl, 'right', 5, self.midSep )]
                       )

                #place the right controls
                anmInfTxt = text( 'aim_animInfo_text', l='Animation Information:', w=180, align='left', h=15, fn='boldLabelFont' )
                anmSep = separator()

                dateTxt = text( 'aim_date_text', l='Date     :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.dateInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                timeTxt = text( 'aim_time_text', l='Time     :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.timeInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                strtText = text( 'aim_strt_text', l='Start    :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.strtInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                endText = text( 'aim_end_text', l='End      :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.endInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                athrText = text( 'aim_athr_text', l='Author   :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.athrInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                pltfText = text( 'aim_pltf_text', l='Platform :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.pltfInfoTxt, l='None', align='left', fn="fixedWidthFont", h=15, w=28 )

                cmntText = text( 'aim_cmnt_text', l='Comment  :', align='left', fn="fixedWidthFont", h=15, w=71 )
                text( self.cmntInfoTxt, l='None', align='left', fn="fixedWidthFont", h=48 )

                self.btnSep = separator()
                self.buildButtonLayout()
                formLayout( self.mainForm, edit=True,
                       attachForm=[
                                         ( anmInfTxt, 'top', 5 ),
                                         ( anmSep, 'right', 0 ),
                                         ( self.cmntInfoTxt, 'right', 5 ),
                                         ( self.btnSep, 'right', 0 ), ( self.btnSep, 'bottom', 50 ),
                                         ( self.btnForm, 'bottom', 5 ), ( self.btnForm, 'right', 5 )],

                       attachControl=[( anmInfTxt, 'left', 5, self.midSep ),
                                        ( anmSep, 'left', 0, self.midSep ), ( anmSep, 'top', 5, anmInfTxt ),

                                            ( dateTxt, 'left', 5, self.midSep ), ( dateTxt, 'top', 5, anmSep ),
                                            ( self.dateInfoTxt, 'left', 5, dateTxt ), ( self.dateInfoTxt, 'top', 5, anmSep ),

                                            ( timeTxt, 'left', 5, self.midSep ), ( timeTxt, 'top', 5, dateTxt ),
                                            ( self.timeInfoTxt, 'left', 5, timeTxt ), ( self.timeInfoTxt, 'top', 5, self.dateInfoTxt ),

                                            ( strtText, 'left', 5, self.midSep ), ( strtText, 'top', 5, timeTxt ),
                                            ( self.strtInfoTxt, 'left', 5, strtText ), ( self.strtInfoTxt, 'top', 5, self.timeInfoTxt ),

                                            ( endText, 'left', 5 , self.midSep ), ( endText, 'top', 5, strtText ),
                                            ( self.endInfoTxt, 'left', 5, endText ), ( self.endInfoTxt, 'top', 5, self.strtInfoTxt ),

                                            ( athrText, 'left', 5, self.midSep ), ( athrText, 'top', 5, endText ),
                                            ( self.athrInfoTxt, 'left', 5, athrText ), ( self.athrInfoTxt, 'top', 5, self.endInfoTxt ),

                                            ( pltfText, 'left', 5, self.midSep ), ( pltfText, 'top', 5, athrText ),
                                            ( self.pltfInfoTxt, 'left', 5, pltfText ), ( self.pltfInfoTxt, 'top', 5, self.athrInfoTxt ),

                                            ( cmntText, 'left', 5, self.midSep ), ( cmntText, 'top', 5, pltfText ),
                                            ( self.cmntInfoTxt, 'left', 5, cmntText ), ( self.cmntInfoTxt, 'top', 5, self.pltfInfoTxt ),
                                            ( self.btnSep, 'left', 0, self.midSep ),
                                            ( self.btnForm, 'left', 5, self.midSep ), ( self.btnForm, 'top', 5, self.btnSep )

                                            ]
                       )
        self.setImportPath()
        self.populate_aim_tsl()
        self.loadImportUI()
        self.findReferenceNodes()
