import maya.cmds  as cmds
import os
import os, sys, sys_lib, fnmatch
from subprocess import call
import subprocess
import ui_micro_lib as ui
import characterSet_lib as cs
import maya.mel as mel
import time

reload( cs )
reload( ui )

class CSUI( object ):
    '''
    Build CharacterSet UI
    '''
    def __init__( self, export=False, path=os.path.expanduser( '~' ) + '/maya/characterSets/', filters=['.chr', '.txt', '.mb', '.ma', '*.*'], columnWidth=200 ):
        #external
        self.export = export
        self.path = path
        self.filters = filters
        self.columnWidth = columnWidth
        #internal
        self.windowName = 'CharacterSetManager'
        self.shortcutsFile = '/var/tmp/custom_info.txt'
        self.shortcuts = []
        self.actionLabel = 'import'
        self.dirStr = ' / '
        self.par = ' '
        self.mem = '   '
        #execute
        self.cleanUI()
        self.whichContext()

    def whichContext( self ):
        if self.export:
            self.actionLabel = 'export'
            self.browser()
            self.drawWindow()
            self.populateSets()
        else:
            self.browser()
            self.drawWindow()
            self.populateNamespace()
        self.populateShortcuts()
        self.populateBrowse()

    def message( self, what='', maya=True, ui=True, *args ):
        if what != '':
            if maya == True:
                mel.eval( 'print \"' + '-- ' + what + ' --' + '\";' )
        else:
            print ''
        if ui == True:
            cmds.text( self.messageForm.heading, edit=True, l='   ' + what + '   ' )
            #cmds.form(self.messageForm.form, edit=True, )

    def cleanUI( self, *args ):
        try:
            cmds.deleteUI( self.windowName )
        except:
            pass

    def browser( self ):
        self.win = cmds.window( self.windowName, w=700 )
        #main form
        self.mainForm = cmds.formLayout( 'mainForm' )
        #bottom form
        cmds.setParent( self.mainForm )
        self.mainBottomForm = cmds.formLayout( 'mainBottomForm', h=100 )
        attachForm = [( self.mainBottomForm, 'left', 5 ), ( self.mainBottomForm, 'bottom', 15 ), ( self.mainBottomForm, 'right', 5 )]
        cmds.formLayout( self.mainForm, edit=True, attachForm=attachForm )
        #action
        self.actionForm = ui.Action( 'action', parent=self.mainBottomForm, filters=self.filters, cmdCancel=self.cleanUI, cmdAction=self.cmdAction, cmdOpen=self.cmdOpen, label=self.actionLabel )
        attachForm = [( self.actionForm.form, 'left', 0 ), ( self.actionForm.form, 'bottom', 0 ), ( self.actionForm.form, 'right', 0 )]
        cmds.formLayout( self.mainBottomForm, edit=True, attachForm=attachForm )
        #message
        self.messageForm = ui.Form( label='', name='message', parent=self.mainBottomForm )
        cmds.formLayout( self.messageForm.form, edit=True, h=20 )
        cmds.text( self.messageForm.heading, edit=True, al='right' )
        attachForm = [( self.messageForm.form, 'left', 0 ), ( self.messageForm.form, 'right', 2 ), ( self.messageForm.form, 'bottom', self.actionForm.heightForm )]
        cmds.formLayout( self.mainBottomForm, edit=True, attachForm=attachForm )
        #path
        self.pathForm = ui.Form( text=self.path, label='Path', name='path', parent=self.mainBottomForm, createField=True )
        attachForm = [( self.pathForm.form, 'left', 0 ), ( self.pathForm.form, 'right', 0 ), ( self.pathForm.form, 'bottom', self.actionForm.heightForm + self.messageForm.heightForm )]
        cmds.formLayout( self.mainBottomForm, edit=True, attachForm=attachForm )
        #edit form height
        h = cmds.formLayout( self.actionForm.form, q=True, h=True ) + cmds.formLayout( self.pathForm.form, q=True, h=True ) + cmds.formLayout( self.messageForm.form, q=True, h=True )
        cmds.formLayout( self.mainBottomForm, edit=True, h=h )
        #left form
        cmds.setParent( self.mainForm )
        self.mainTopLeftForm = cmds.formLayout( 'mainTopLeftForm', w=self.columnWidth, h=80 )
        attachForm = [( self.mainTopLeftForm, 'left', 5 ), ( self.mainTopLeftForm, 'top', 5 ), ( self.mainTopLeftForm, 'bottom', 5 )]
        attachControl = [( self.mainTopLeftForm, 'bottom', 5, self.mainBottomForm )]
        cmds.formLayout( self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl )
        #custom paths
        self.shortcutsForm = ui.Form( label='Shortcuts', name='customPaths', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdShortcuts )
        cmds.formLayout( self.shortcutsForm.form, edit=True, h=60 )
        attachForm = [( self.shortcutsForm.form, 'left', 0 ), ( self.shortcutsForm.form, 'top', 0 ), ( self.shortcutsForm.form, 'right', 0 )]
        cmds.formLayout( self.mainTopLeftForm, edit=True, attachForm=attachForm )
        #browse paths
        self.browseForm = ui.Form( label='Browse', name='browse', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdBrowse, h=80 )
        attachForm = [( self.browseForm.form, 'left', 0 ), ( self.browseForm.form, 'bottom', 0 ), ( self.browseForm.form, 'right', 0 )]
        attachControl = [( self.browseForm.form, 'top', 0, self.shortcutsForm.form )]
        cmds.formLayout( self.mainTopLeftForm, edit=True, attachForm=attachForm, attachControl=attachControl )
        #modular form
        cmds.setParent( self.mainForm )
        self.mainModularForm = cmds.formLayout( 'mainTopRightForm', w=150, h=80 )
        attachForm = [( self.mainModularForm, 'top', 5 ), ( self.mainModularForm, 'right', 5 )]
        attachControl = [( self.mainModularForm, 'left', 20, self.mainTopLeftForm ), ( self.mainModularForm, 'bottom', 5, self.mainBottomForm )]
        cmds.formLayout( self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl )

    def drawWindow( self ):
        #fill mainModularForm
        if not self.export:
            self.importCS( self.mainModularForm )
        else:
            self.exportCS( self.mainModularForm )
        #launch window
        cmds.showWindow( self.win )

    def importCS( self, *args ):
        #replace
        self.replaceForm = ui.Form( label="Build Replace String (  ie. search:replace,search:replace  )", name='replace', parent=self.mainModularForm, createField=True )
        attachForm = [( self.replaceForm.form, 'left', 0 ), ( self.replaceForm.form, 'right', 0 ), ( self.replaceForm.form, 'bottom', self.replaceForm.heightForm )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #prefix
        self.prefixForm = ui.Form( label='Add Prefix', name='prefix', parent=self.mainModularForm, createField=True )
        attachForm = [( self.prefixForm.form, 'left', 0 ), ( self.prefixForm.form, 'right', 0 ), ( self.prefixForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #nameSpace, right attach
        self.namespaceForm = ui.Form( label='Use In Scene Namespace', name='nameSpace', parent=self.mainModularForm, createList=True, h=80 )
        cmds.formLayout( self.namespaceForm.form, edit=True, w=150 )
        attachForm = [( self.namespaceForm.form, 'top', 0 ), ( self.namespaceForm.form, 'right', 0 ), ( self.namespaceForm.form, 'bottom', 0 )]
        attachControl = [( self.namespaceForm.form, 'bottom', 0, self.replaceForm.form )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl )
        #preview section, middle attach
        self.previewForm = ui.Form( label='File Preview', name='read', parent=self.mainModularForm, createList=True, h=80 )
        cmds.formLayout( self.previewForm.form, edit=True, w=1 )
        attachForm = [( self.previewForm.form, 'left', 0 ), ( self.previewForm.form, 'top', 0 ), ( self.previewForm.form, 'bottom', 0 )]
        attachControl = [( self.previewForm.form, 'right', 5, self.namespaceForm.form ), ( self.previewForm.form, 'bottom', 0, self.replaceForm.form )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl )

    def exportCS( self, *args ):
        #in scene character sets, middle attach
        self.setsForm = ui.Form( label='Select Character Set to Export', name='characterSets', parent=self.mainModularForm, createList=True, h=80, cmdSingle=self.cmdSets )
        cmds.formLayout( self.setsForm.form, edit=True, w=200 )
        attachForm = [( self.setsForm.form, 'left', 0 ), ( self.setsForm.form, 'top', 0 ), ( self.setsForm.form, 'bottom', 0 )]
        #attachControl = [(self.setsForm.form,'right',5, self.membersForm.form)]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #character set members, right attach
        self.membersForm = ui.Form( label='Set Members', name='characterSetMembers', parent=self.mainModularForm, createList=True, h=80 )
        cmds.formLayout( self.membersForm.form, edit=True, w=1 )
        attachForm = [( self.membersForm.form, 'top', 0 ), ( self.membersForm.form, 'right', 0 ), ( self.membersForm.form, 'bottom', 0 )]
        attachControl = [( self.membersForm.form, 'left', 5, self.setsForm.form )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl )

    def format( self, line='' ):
        if 'ParentInfo' in line:
            return self.par + line
        else:
            return self.mem + line

    def buildDict( self ):
        rp = cmds.textField( self.replaceForm.field, q=True, tx=True )
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

    def populatePath( self ):
        cmds.textField( self.pathForm.field, edit=True, text=self.path )

    def populateShortcuts( self ):
        if not os.path.exists( self.shortcutsFile ):
            self.shortcuts.append( ['Home', os.environ['HOME']] )
            #self.shortcuts.append(['Desktop', os.path.join(os.environ['USERPROFILE'],'Desktop')])
            self.shortcuts.append( ['Character Sets', os.path.join( os.environ['HOME'], cs.defaultPath() )] )
            cs.createDefaultPath()
        else:
            _file = open( self.shortcutsFile, 'r' )
            lines = _file.readlines()
            for l in lines:
                line = eval( l.strip( '\n' ) )
                self.shortcuts.append( [line[0], line[1]] )
        for path in self.shortcuts:
            cmds.textScrollList( self.shortcutsForm.scroll, edit=True, append=path[0] )

    def populateBrowse( self ):
        #Make sure the path exists and access is permitted
        if os.path.isdir( self.path ) and os.access( self.path, os.R_OK ):
            #Clear the textScrollList
            cmds.textScrollList( self.browseForm.scroll, edit=True, ra=True )
            #Append the '..'(move up a director) as the first item
            cmds.textScrollList( self.browseForm.scroll, edit=True, append='..' )
            #Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            #list the files in the path
            files = os.listdir( str( self.path ) )
            if len( files ) > 0:
                #Sort the directory list based on the names in lowercase
                #This will error if 'u' objects are fed into a list
                files.sort( key=str.lower )
                #pick out the directories
                for i in files:
                    if i[0] != '.':
                        if os.path.isdir( os.path.join( self.path, i ) ):
                            dirs.append( i )
                        else:
                            nonDir.append( i )
                #Add the directories first
                for i in dirs:
                    cmds.textScrollList( self.browseForm.scroll, edit=True, append=self.dirStr + i )
                #Add the files next
                for i in nonDir:
                    #print i
                    #show the files based on the current filter
                    if fnmatch.fnmatch( i, '*' + cmds.optionMenuGrp( self.actionForm.opt, query=True, v=True ) ):
                        cmds.textScrollList( self.browseForm.scroll, edit=True, append=i )

    def populatePreview( self ):
        cmds.textScrollList( self.previewForm.scroll, edit=True, ra=True )
        path = os.path.join( self.path, cmds.textScrollList( self.browseForm.scroll, query=True, si=True )[0] )
        for line in open( path ):
            cmds.textScrollList( self.previewForm.scroll, edit=True, append=self.format( line ).strip( '\n' ) )

    def populateMembers( self ):
        stp = '  '
        self.message( '' )
        cmds.textScrollList( self.membersForm.scroll, edit=True, ra=True )
        set = cmds.textScrollList( self.setsForm.scroll, query=True, si=True )
        members = cmds.character( set, query=True )
        if members:
            members.sort()
            for member in members:
                if cmds.nodeType( member ) != 'character':
                    cmds.textScrollList( self.membersForm.scroll, edit=True, append=member )
                else:
                    cmds.textScrollList( self.membersForm.scroll, edit=True, append=stp + member )
        else:
            cmds.textScrollList( self.membersForm.scroll, edit=True, append='None' )

    def populateSets( self, string='', sets=cs.listTop(), *args ):
        for char in sets:
            if char in cs.listTop():
                cmds.textScrollList( self.setsForm.scroll, edit=True, append=char )
            subSets = cmds.listConnections( char, d=False, s=True, t='character' )
            if subSets:
                subSets.sort()
                string = string + '   '
                for sub in subSets:
                    cmds.textScrollList( self.setsForm.scroll, edit=True, append=string + sub )
                    if cmds.listConnections( sub, d=False, s=True, t='character' ):
                        self.populateSets( string, [sub] )

    def populateNamespace( self ):
        namespace = []
        ref = cmds.ls( type='reference' )
        for s in ref:
            f = None
            try:
                f = cmds.referenceQuery( s, filename=True )
            except:
                pass
            if f != None:
                namespace.append( cmds.file( f, q=True, namespace=True ) )
        for ns in namespace:
            cmds.textScrollList( self.namespaceForm.scroll, edit=True, append=ns )

    def cmdShortcuts( self, *args ):
        tsl = cmds.textScrollList
        tmp = tsl( self.shortcutsForm.scroll, query=True, sii=True )
        if tmp != None :
            idx = tmp[0]
            self.path = self.shortcuts[idx - 1][1]
            self.populatePath()
            self.populateBrowse()

    def cmdBrowse( self, *args ):
        tmp = cmds.textScrollList( self.browseForm.scroll, query=True, si=True )
        if tmp != None:
            item = tmp[0]
            #find if the current item is a directory
            if item[:len( self.dirStr )] == self.dirStr:
                item = item[len( self.dirStr ):]
                path = os.path.join( self.path, item )
                if os.path.exists( path ):
                    if os.access( path, os.R_OK ):
                        self.path = str( path )
                        cmds.textField( self.pathForm.field, edit=True, tx=self.path )
                        try:
                            cmds.textScrollList( self.previewForm.scroll, edit=True, ra=True )
                        except:
                            pass
                        self.populateBrowse()
            elif item == '..':
                path = os.path.split( self.path )[0]
                #go up a directory
                if os.path.exists( path ):
                    if os.access( path, os.R_OK ):
                        self.path = path
                        cmds.textField( self.pathForm.field, edit=True, tx=path )
                        try:
                            cmds.textScrollList( self.previewForm.scroll, edit=True, ra=True )
                        except:
                            pass
                        self.populateBrowse()
            else:
                #this is a file
                path = os.path.join( self.path, item )
                if os.path.isfile( path ):
                    cmds.textField( self.pathForm.field, edit=True, tx=path )
                    try:
                        self.populatePreview()
                    except:
                        pass

    def cmdSets( self, *args ):
        self.populateMembers()

    def cmdImport( self, *args ):
        selFile = cmds.textScrollList( self.browseForm.scroll, q=True, si=True )
        if selFile and '.chr' in selFile[0]:
            path = path = os.path.join( self.path, selFile[0] )
            prefix = cmds.textField( self.prefixForm.field, q=True, tx=True )
            try:
                ns = cmds.textScrollList( self.namespaceForm.scroll, q=True, si=True )[0]
            except:
                ns = ''
            dic = self.buildDict()
            if dic:
                cs.importFile( path, prefix=prefix, ns=ns, rp=dic )
        else:
            self.message( 'Click a file with   \'.chr\'   extension' )

    def cmdExport( self, *args ):
        #this needs to account for user fed file name into path field
        set = cmds.textScrollList( self.setsForm.scroll, q=True, si=True )
        #file = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        path = cmds.textField( self.pathForm.field, q=True, tx=True )
        '''
        if file:
            print self.path
            path = os.path.join(self.path, file[0])
        else:
            self.message('Select a character Set in the middle column.')
            '''
        if set:
            if not os.path.isdir( path ):
                set = set[0].replace( ' ', '' )
                cs.exportFile( set, path )
                self.populateBrowse()
                self.message( 'Set   ' + set + '   exported to   ' + path )
            else:
                self.message( 'Add file name to path field. Action aborted.' )
        else:
            self.message( 'Select a character Set in the middle column.' )

    def cmdAction( self, *args ):
        if self.export:
            #print self.path
            self.cmdExport()
        else:
            self.cmdImport()

    def cmdFilter( self, *args ):
        pass

    def cmdOpen( self, *args ):
        if os.name == 'nt':
            path = self.path.replace( '/', '\\' )
            if os.path.isdir( path ):
                subprocess.Popen( r'explorer /open, ' + path )
        else:
            self.message( 'Close file window to regain control over MAYA.' )
            app = "nautilus"
            call( [app, self.path] )


    def cmdUnflush( self, *args ):
        import characterSet_lib as cs
        reload( cs )
        cs.unflush()
        self.message( cs.tell, maya=False )

    def cmdFlush( self, *args ):
        import characterSet_lib as cs
        reload( cs )
        cs.flush()
        self.message( cs.tell, maya=False )
