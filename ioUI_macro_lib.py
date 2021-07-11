from subprocess import call
import imp
import os
import os, sys, sys_lib, fnmatch
import subprocess
import time

import cacheSC_autoGeo_v01 as cash
import characterSet_lib as cs
import fileMan_lib as fm
import maya.cmds  as cmds
import maya.mel as mel
import selectionSet_lib as ss
import ui_micro_lib as ui

imp.reload( cash )


class IOUI( object ):
    '''
    Build io UI
    C:\VFX\projects\Scarecrow\IO\_AnimDailies
    path=os.path.expanduser('~') + '/maya/IO/OUT/dailies'
    '''

    def __init__( self, filters = ['.mov', '.sel', '.txt', '.mb', '.ma', '*.*'], columnWidth = 200 ):
        # external
        self.shots = ''
        self.path = ''
        self.filters = filters
        self.columnWidth = columnWidth
        self.user = os.path.expanduser( '~' )
        self.mov = []

        # internal
        self.windowName = 'IOManager'
        self.shortcutsFile = ''
        # self.shortcutsFile                = os.path.join(self.user, 'maya/scripts/cacheShortcuts.txt')
        findfile = [os.path.join( self.user, 'maya/scripts' ), os.path.join( self.user, 'maya/2013-x64/scripts' ), os.path.join( self.user, 'maya/2013-x64/prefs/scripts' )]
        for locale in findfile:
            file = os.path.join( locale, 'cacheShortCuts.txt' )
            if os.path.exists( file ):
                self.shortcutsFile = file
                break
        self.projects = 'Maya/scenes'
        self.shortcuts = []
        self.actionLabel = 'cache'
        self.dirStr = ' / '
        self.par = ''
        self.mem = ''
        self.files = []
        # execute
        self.cleanUI()
        self.browser()
        self.drawWindow()
        self.populateShortcuts()
        self.populateBrowse()
        self.populatePreview()
        self.populatePath()
        # self.populateSelection()
        # toggleJob()

    def message( self, what = '', maya = True, ui = True, *args ):
        if what != '':
            if '\\' in what:
                what = what.replace( '\\', '/' )
            if maya == True:
                mel.eval( 'print \"' + '-- ' + what + ' --' + '\";' )
        else:
            print ''
        if ui == True:
            cmds.text( self.messageForm.heading, edit = True, l = '   ' + what + '   ' )
            # cmds.form(self.messageForm.form, edit=True, )

    def cleanUI( self, *args ):
        try:
            cmds.deleteUI( self.windowName )
            toggleJob()
        except:
            pass

    def browser( self ):
        self.win = cmds.window( self.windowName, w = 700 )
        # main form
        self.mainForm = cmds.formLayout( 'mainFormSs' )
        # bottom form
        cmds.setParent( self.mainForm )
        self.mainBottomForm = cmds.formLayout( 'mainBottomFormSs', h = 100 )
        attachForm = [( self.mainBottomForm, 'left', 5 ), ( self.mainBottomForm, 'bottom', 15 ), ( self.mainBottomForm, 'right', 5 )]
        cmds.formLayout( self.mainForm, edit = True, attachForm = attachForm )
        # action
        self.actionForm = ui.Action( 'actionSs', parent = self.mainBottomForm, filters = self.filters, cmdCancel = self.cleanUI, cmdAction = self.cmdAction, cmdOpen = self.cmdOpen, label = self.actionLabel )
        attachForm = [( self.actionForm.form, 'left', 0 ), ( self.actionForm.form, 'bottom', 0 ), ( self.actionForm.form, 'right', 0 )]
        cmds.formLayout( self.mainBottomForm, edit = True, attachForm = attachForm )
        # message
        self.messageForm = ui.Form( label = '', name = 'messageSs', parent = self.mainBottomForm )
        cmds.formLayout( self.messageForm.form, edit = True, h = 20 )
        cmds.text( self.messageForm.heading, edit = True, al = 'right' )
        attachForm = [( self.messageForm.form, 'left', 0 ), ( self.messageForm.form, 'right', 2 ), ( self.messageForm.form, 'bottom', self.actionForm.heightForm )]
        cmds.formLayout( self.mainBottomForm, edit = True, attachForm = attachForm )
        # path
        self.pathForm = ui.Form( text = self.path, label = 'Path', name = 'pathSs', parent = self.mainBottomForm, createField = True )
        attachForm = [( self.pathForm.form, 'left', 0 ), ( self.pathForm.form, 'right', 0 ), ( self.pathForm.form, 'bottom', self.actionForm.heightForm + self.messageForm.heightForm )]
        cmds.formLayout( self.mainBottomForm, edit = True, attachForm = attachForm )
        # edit form height
        h = cmds.formLayout( self.actionForm.form, q = True, h = True ) + cmds.formLayout( self.pathForm.form, q = True, h = True ) + cmds.formLayout( self.messageForm.form, q = True, h = True )
        cmds.formLayout( self.mainBottomForm, edit = True, h = h )
        # left form
        cmds.setParent( self.mainForm )
        self.mainTopLeftForm = cmds.formLayout( 'mainTopLeftFormSs', w = self.columnWidth, h = 80 )
        attachForm = [( self.mainTopLeftForm, 'left', 5 ), ( self.mainTopLeftForm, 'top', 5 ), ( self.mainTopLeftForm, 'bottom', 5 )]
        attachControl = [( self.mainTopLeftForm, 'bottom', 5, self.mainBottomForm )]
        cmds.formLayout( self.mainForm, edit = True, attachForm = attachForm, attachControl = attachControl )
        # custom paths
        self.shortcutsForm = ui.Form( label = 'Shortcuts', name = 'customPathsSs', parent = self.mainTopLeftForm, createList = True, cmdSingle = self.cmdShortcuts )
        cmds.formLayout( self.shortcutsForm.form, edit = True, h = 60 )
        attachForm = [( self.shortcutsForm.form, 'left', 0 ), ( self.shortcutsForm.form, 'top', 0 ), ( self.shortcutsForm.form, 'right', 0 )]
        cmds.formLayout( self.mainTopLeftForm, edit = True, attachForm = attachForm )
        # browse paths
        self.browseForm = ui.Form( label = 'Browse', name = 'browseSs', parent = self.mainTopLeftForm, createList = True, cmdSingle = self.cmdBrowse, h = 80 )
        attachForm = [( self.browseForm.form, 'left', 0 ), ( self.browseForm.form, 'bottom', 0 ), ( self.browseForm.form, 'right', 0 )]
        attachControl = [( self.browseForm.form, 'top', 0, self.shortcutsForm.form )]
        cmds.formLayout( self.mainTopLeftForm, edit = True, attachForm = attachForm, attachControl = attachControl )
        # modular form
        cmds.setParent( self.mainForm )
        self.mainModularForm = cmds.formLayout( 'mainTopRightFormSs', w = 150, h = 80 )
        attachForm = [( self.mainModularForm, 'top', 5 ), ( self.mainModularForm, 'right', 5 )]
        attachControl = [( self.mainModularForm, 'left', 20, self.mainTopLeftForm ), ( self.mainModularForm, 'bottom', 5, self.mainBottomForm )]
        cmds.formLayout( self.mainForm, edit = True, attachForm = attachForm, attachControl = attachControl )

    def drawWindow( self ):
        # fill mainModularForm
        self.exportCS( self.mainModularForm )
        # launch window
        cmds.showWindow( self.win )

    def exportCS( self, *args ):
        # in scene character sets, middle attach
        self.previewForm = ui.Form( label = '.MOV Files in all subdirectories', name = 'selectionSets', parent = self.mainModularForm, createList = True, h = 80, cmdSingle = self.cmdSets )
        cmds.textScrollList( self.previewForm.scroll, e = True, allowMultiSelection = True )
        cmds.formLayout( self.previewForm.form, edit = True )
        attachForm = [( self.previewForm.form, 'left', 0 ), ( self.previewForm.form, 'top', 0 ), ( self.previewForm.form, 'bottom', 0 ), ( self.previewForm.form, 'right', 0 )]
        # attachControl = [(self.previewForm.form,'right',5, self.selectionForm.form)]
        cmds.formLayout( self.mainModularForm, edit = True, attachForm = attachForm )
        '''
        #character set members, right attach
        self.selectionForm = ui.Form(label='Current Selection', name='selection', parent=self.mainModularForm, createList=True, h=80)
        cmds.formLayout(self.selectionForm.form, edit=True, w=1)
        attachForm = [(self.selectionForm.form,'top',0), (self.selectionForm.form,'right',0), (self.selectionForm.form,'bottom',0)]
        attachControl = [(self.selectionForm.form,'left',5, self.previewForm.form)]
        cmds.formLayout(self.mainModularForm, edit=True, attachForm=attachForm, attachControl= attachControl)
        global scroll
        scroll = self.selectionForm.scroll
        '''

    def format( self, line = '' ):
        if 'ParentInfo' in line:
            return self.par + line
        else:
            return self.mem + line

    def buildDict( self ):
        rp = cmds.textField( self.replaceForm.field, q = True, tx = True )
        rp = rp.replace( ' ', '' )
        dic = {}
        if rp:
            try:
                if ',' in rp:
                    rp = rp.split( ',' )
                    for d in rp:
                        dic[d.split( ':' )[0]] = d.split( ':' )[1]
                    return dic
                else:
                    dic[rp.split( ':' )[0]] = rp.split( ':' )[1]
                    return dic
            except:
                self.message( "  FAIL  --  Replace string failed. --  Use colons,commas  --    ie.    search1:replace1,search2:replace2" )
        else:
            return {None:None}

    def populatePathWindows( self ):
        if os.name == 'nt':
            self.path = self.path.replace( '/', '\\' )

    def populatePath( self ):
        self.populatePathWindows()
        cmds.textField( self.pathForm.field, edit = True, text = self.path )

    def populateShortcuts( self ):
        if not os.path.exists( self.shortcutsFile ):
            print self.shortcutsFile
            self.shortcuts.append( ['Scarecrow', os.environ['HOME']] )
            self.shortcuts.append( ['Shots', os.path.join( os.environ['HOME'], 'maya/IO/' )] )
            self.shortcuts.append( ['AnimDailies', os.path.join( os.environ['HOME'], 'maya/IO/OUT/dailies' )] )
        else:
            print self.shortcutsFile
            _file = open( self.shortcutsFile, 'r' )
            lines = _file.readlines()
            for l in lines:
                l = l.strip( '\n' )
                l = l.strip( '\r' )
                line = eval( l )
                self.shortcuts.append( [line[0], line[1]] )
                if 'AnimDailies' in l:
                    self.path = line[1]
                    # self.populatePath()
                else:
                    self.shots = line[1]

        for path in self.shortcuts:
            cmds.textScrollList( self.shortcutsForm.scroll, edit = True, append = path[0] )

    def populateBrowse( self ):
        # Make sure the path exists and access is permitted
        if os.path.isdir( self.path ) and os.access( self.path, os.R_OK ):
            # Clear the textScrollList
            cmds.textScrollList( self.browseForm.scroll, edit = True, ra = True )
            # Append the '..'(move up a director) as the first item
            cmds.textScrollList( self.browseForm.scroll, edit = True, append = '..' )
            # Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            # list the files in the path
            self.files = os.listdir( str( self.path ) )
            movies = []
            for root, dirs, files in os.walk( self.path ):
                for name in files:
                    if name.endswith( ( "mov" ) ):
                        movies.append( name )
            self.mov = sorted( movies )
            if len( self.files ) > 0:
                # Sort the directory list based on the names in lowercase
                # This will error if 'u' objects are fed into a list
                self.files.sort( key = str.lower )
                # pick out the directories
                for i in self.files:
                    if i[0] != '.':
                        if os.path.isdir( os.path.join( self.path, i ) ):
                            dirs.append( i )
                        else:
                            nonDir.append( i )
                    else:
                        # self.message('no . in whatever')
                        pass
                # set files
                self.files = nonDir
                # Add the directories first
                for i in dirs:
                    cmds.textScrollList( self.browseForm.scroll, edit = True, append = self.dirStr + i )
                # Add the files next
                '''
                for i in nonDir:
                    #print i
                    #show the files based on the current filter
                    if fnmatch.fnmatch(i, '*' + cmds.optionMenuGrp(self.actionForm.opt, query=True, v=True)):
                        cmds.textScrollList(self.browseForm.scroll, edit=True, append=i)'''
            else:
                self.message( 'no files' )
                # pass
        else:
            self.message( 'path exists, access granted' )
            # pass

    def populatePreview( self ):
        cmds.textScrollList( self.previewForm.scroll, edit = True, ra = True )
        # path = os.path.join(self.path, cmds.textScrollList(self.browseForm.scroll, query=True, si=True)[0])
        for file in self.mov:
            cmds.textScrollList( self.previewForm.scroll, edit = True, append = self.format( file ) )

    '''
    def populateSelection(self):
        cmds.textScrollList(self.selectionForm.scroll, edit=True, ra=True)
        selection = cmds.ls(sl=True)
        if len(selection) > 0:
            for sel in selection:
                cmds.textScrollList(self.selectionForm.scroll, edit=True, append=sel)
        else:
            cmds.textScrollList(self.selectionForm.scroll, edit=True, append='Nothing Selected')
            '''

    def cmdShortcuts( self, *args ):
        tsl = cmds.textScrollList
        tmp = tsl( self.shortcutsForm.scroll, query = True, sii = True )
        if tmp != None:
            idx = tmp[0]
            self.path = self.shortcuts[idx - 1][1]
            self.populatePath()
            self.populateBrowse()
            self.populatePreview()
        else:
            print 'here'

    def cmdBrowse( self, *args ):
        tmp = cmds.textScrollList( self.browseForm.scroll, query = True, si = True )
        if tmp != None:
            item = tmp[0]
            # find if the current item is a directory
            if item[:len( self.dirStr )] == self.dirStr:
                item = item[len( self.dirStr ):]
                path = os.path.join( self.path, item )
                if os.path.exists( path ):
                    if os.access( path, os.R_OK ):
                        self.path = path
                        self.populatePath()
                        cmds.textField( self.pathForm.field, edit = True, tx = self.path )
                        try:
                            cmds.textScrollList( self.previewForm.scroll, edit = True, ra = True )
                        except:
                            pass
                        self.populateBrowse()
                        self.populatePreview()
            elif item == '..':
                path = os.path.split( self.path )[0]
                # go up a directory
                if os.path.exists( path ):
                    if os.access( path, os.R_OK ):
                        self.path = path
                        self.populatePath()
                        cmds.textField( self.pathForm.field, edit = True, tx = path )
                        try:
                            cmds.textScrollList( self.previewForm.scroll, edit = True, ra = True )
                        except:
                            pass
                        self.populateBrowse()
                        self.populatePreview()
            else:
                # this is a file
                path = os.path.join( self.path, item )
                if os.path.isfile( path ):
                    # self.path = path
                    self.populatePath()
                    cmds.textField( self.pathForm.field, edit = True, tx = path )
                    try:
                        # self.populatePreview()
                        pass
                    except:
                        pass

    def cmdSets( self, *args ):
        # self.populateMembers()
        pass

    def buildShotPath( self, mov = [], *args ):
        files = []
        for file in mov:
            # get scene
            scene = file.replace( 'mov', 'ma' )
            # get shot name
            project = file.rsplit( '_', 2 )[0]
            # build path
            path = os.path.join( self.shots, project )
            path = os.path.join( path, self.projects )
            files.append( os.path.join( path, scene ) )
        return files

    def cmdCache( self, *args ):
        # get selected files
        mov = cmds.textScrollList( self.previewForm.scroll, q = True, si = True )
        # get path
        path = cmds.textField( self.pathForm.field, q = True, tx = True )
        # build paths
        scenes = self.buildShotPath( mov )
        for sc in scenes:
            if os.path.exists( sc ):
                print sc
                cmds.file( sc, o = True, force = True )
                fm.setProjectFromFilename( 'scenes' )
                cash.createGeoCache()
            else:
                self.message( 'Directory not found --' + sc )

    def cmdAction( self, *args ):
        self.cmdCache()

    def cmdFilter( self, *args ):
        pass

    def cmdOpen( self, *args ):
        if os.name == 'nt':
            Popen_arg = r'explorer /open, "' + self.path + '"'
            Popen_arg = str( Popen_arg )
            subprocess.Popen( Popen_arg )
        else:
            self.message( 'Close file window to regain control over MAYA.' )
            app = "nautilus"
            call( [app, self.path] )
