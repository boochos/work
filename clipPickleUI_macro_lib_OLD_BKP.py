import maya.cmds  as cmds
import os
import os, sys, sys_lib, fnmatch
from subprocess import call
import subprocess
import clipPickleUI_micro_lib_OLD_BKP as ui
import clipPickle_lib as cp
import maya.mel as mel
import time

reload( cp )
reload( ui )

class CPUI( object ):
    '''
    Build CharacterSet UI
    '''
    def __init__( self, export=False, path=os.path.expanduser( '~' ) + '/maya/clipLibrary/', filters=['.clip', '*.*'], columnWidth=200 ):
        #external
        self.export = export
        self.path = path
        self.filters = filters
        self.columnWidth = columnWidth
        #internal
        self.windowName = 'ClipLibrary'
        self.shortcutsFile = '/var/tmp/custom_info.txt'
        self.shortcuts = []
        self.actionLabel = 'export'
        self.dirStr = ' / '
        self.par = ' '
        self.mem = '   '
        #execute
        self.cleanUI()
        #self.whichContext()
        self.buildClipList()
        self.buildWindow()
        self.populateClipList()

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

    def buildClipList( self ):
        self.win = cmds.window( self.windowName, w=700 )
        #main form
        self.mainForm = cmds.formLayout( 'mainForm' )
        #bottom form
        cmds.setParent( self.mainForm )
        self.mainBottomForm = cmds.formLayout( 'mainBottomForm', h=100 )
        attachForm = [( self.mainBottomForm, 'left', 5 ), ( self.mainBottomForm, 'bottom', 15 ), ( self.mainBottomForm, 'right', 5 )]
        cmds.formLayout( self.mainForm, edit=True, attachForm=attachForm )
        #action
        self.actionForm = ui.Action( 'action', parent=self.mainBottomForm, filters=self.filters, cmdCancel=self.cmdImport, cmdAction=self.cmdExport, cmdOpen=self.cmdOpen, label=self.actionLabel )
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
        #browse paths
        self.browseForm = ui.Form( label='Browse', name='browse', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdBrowse, h=80 )
        attachForm = [( self.browseForm.form, 'left', 0 ), ( self.browseForm.form, 'bottom', 0 ), ( self.browseForm.form, 'top', 0 ), ( self.browseForm.form, 'right', 0 )]
        cmds.formLayout( self.mainTopLeftForm, edit=True, attachForm=attachForm )
        #modular form
        cmds.setParent( self.mainForm )
        self.mainModularForm = cmds.formLayout( 'mainTopRightForm', w=150, h=80 )
        attachForm = [( self.mainModularForm, 'top', 5 ), ( self.mainModularForm, 'right', 5 )]
        attachControl = [( self.mainModularForm, 'left', 20, self.mainTopLeftForm ), ( self.mainModularForm, 'bottom', 5, self.mainBottomForm )]
        cmds.formLayout( self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl )

    def buildWindow( self ):
        #fill mainModularForm
        self.buildClipInfo( self.mainModularForm )
        #launch window
        cmds.showWindow( self.win )

    def buildClipInfo( self, *args ):
        w = 200
        #export name
        self.exportNameForm = ui.Form( label="Clip Export Name", name='exportName', parent=self.mainModularForm, createField=True )
        attachForm = [( self.exportNameForm.form, 'left', 0 ), ( self.exportNameForm.form, 'right', 0 ), ( self.exportNameForm.form, 'bottom', self.exportNameForm.heightForm )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #export comments
        self.exportCommentForm = ui.Form( label='Clip Export Comment', name='exportComment', parent=self.mainModularForm, createField=True )
        attachForm = [( self.exportCommentForm.form, 'left', 0 ), ( self.exportCommentForm.form, 'right', 0 ), ( self.exportCommentForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )

        #clipInfo, right attach
        self.infoForm = ui.Form( label='CLip Info', name='info', parent=self.mainModularForm, createList=False, h=20 )
        cmds.formLayout( self.infoForm.form, edit=True, w=w )
        attachForm = [( self.infoForm.form, 'top', 0 ), ( self.infoForm.form, 'right', 0 ), ( self.infoForm.form, 'bottom', 0 )]
        attachControl = [( self.infoForm.form, 'bottom', 0, self.exportNameForm.form )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )

        #start
        self.startForm = ui.Form( label='start:', name='start', parent=self.mainModularForm, h=20, createField=True )
        cmds.textField( self.startForm.field, e=True, tx='-', ed=False )
        cmds.formLayout( self.startForm.form, edit=True, w=w )
        attachForm = [( self.startForm.form, 'top', 20 ), ( self.startForm.form, 'right', 0 ), ( self.startForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #end
        self.endForm = ui.Form( label='end:', name='end', parent=self.mainModularForm, h=20, createField=True )
        cmds.textField( self.endForm.field, e=True, tx='-', ed=False )
        cmds.formLayout( self.endForm.form, edit=True, w=w )
        attachForm = [( self.endForm.form, 'top', 60 ), ( self.endForm.form, 'right', 0 ), ( self.endForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #length
        self.lengthForm = ui.Form( label='length:', name='length', parent=self.mainModularForm, h=20, createField=True )
        cmds.textField( self.lengthForm.field, e=True, tx='-', ed=False )
        cmds.formLayout( self.lengthForm.form, edit=True, w=w )
        attachForm = [( self.lengthForm.form, 'top', 100 ), ( self.lengthForm.form, 'right', 0 ), ( self.lengthForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )
        #comment
        self.commentForm = ui.Form( label='comment:', name='comment', parent=self.mainModularForm, h=20, createField=True )
        cmds.textField( self.commentForm.field, e=True, tx='-', ed=False )
        cmds.formLayout( self.commentForm.form, edit=True, w=w )
        attachForm = [( self.commentForm.form, 'top', 140 ), ( self.commentForm.form, 'right', 0 ), ( self.commentForm.form, 'bottom', 0 )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm )

        #preview section, middle attach
        self.previewForm = ui.Form( label='CLip Objects', name='read', parent=self.mainModularForm, createList=True, h=80 )
        cmds.formLayout( self.previewForm.form, edit=True, w=1 )
        attachForm = [( self.previewForm.form, 'left', 0 ), ( self.previewForm.form, 'top', 0 ), ( self.previewForm.form, 'bottom', 0 )]
        attachControl = [( self.previewForm.form, 'right', 5, self.infoForm.form ), ( self.previewForm.form, 'bottom', 0, self.exportNameForm.form )]
        cmds.formLayout( self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl )

    def format( self, line='' ):
        if 'ParentInfo' in line:
            return self.par + line
        else:
            return self.mem + line

    def populatePath( self ):
        cmds.textField( self.pathForm.field, edit=True, text=self.path )

    def populateClipList( self ):
        #Make sure the path exists and access is permitted
        if os.path.isdir( self.path ) and os.access( self.path, os.R_OK ):
            #Clear the textScrollList
            cmds.textScrollList( self.browseForm.scroll, edit=True, ra=True )
            #Append the '..'(move up a director) as the first item
            #cmds.textScrollList( self.browseForm.scroll, edit=True, append='..' )
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
                '''
                for i in dirs:
                    pass
                    cmds.textScrollList( self.browseForm.scroll, edit=True, append=self.dirStr + i )'''
                #Add the files next
                for i in nonDir:
                    #print i
                    #show the files based on the current filter
                    if fnmatch.fnmatch( i, '*' + cmds.optionMenuGrp( self.actionForm.opt, query=True, v=True ) ):
                        cmds.textScrollList( self.browseForm.scroll, edit=True, append=i )

    def populatePreview( self ):
        cmds.textScrollList( self.previewForm.scroll, edit=True, ra=True )
        path = os.path.join( self.path, cmds.textScrollList( self.browseForm.scroll, query=True, si=True )[0] )
        self.clip = cp.clipOpen( path )
        for obj in self.clip.objects:
            cmds.textScrollList( self.previewForm.scroll, edit=True, append=self.format( obj.name ) )
        self.populateInfo()

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
            cmds.textScrollList( self.infoForm.scroll, edit=True, append=ns )

    def populateInfo( self ):
        self.clip.getStartEndLength()
        cmds.textField( self.startForm.field, edit=True, tx='     ' + str( self.clip.start ) )
        cmds.textField( self.endForm.field, edit=True, tx='     ' + str( self.clip.end ) )
        cmds.textField( self.lengthForm.field, edit=True, tx='     ' + str( self.clip.length ) )
        cmds.textField( self.commentForm.field, edit=True, tx=str( self.clip.comment ) )

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
            else:
                #this is a file
                path = os.path.join( self.path, item )
                if os.path.isfile( path ):
                    cmds.textField( self.pathForm.field, edit=True, tx=path )
                    try:
                        self.populatePreview()
                    except:
                        pass

    def cmdImport( self, *args ):
        selFile = cmds.textScrollList( self.browseForm.scroll, q=True, si=True )
        if selFile and '.clip' in selFile[0]:
            path = path = os.path.join( self.path, selFile[0] )
            prefix = cmds.textField( self.exportCommentForm.field, q=True, tx=True )
            try:
                ns = cmds.textScrollList( self.infoForm.scroll, q=True, si=True )[0]
            except:
                ns = ''
            print path
            cp.clipRemap( path=path )
                #cs.importFile( path, prefix=prefix, ns=ns, rp=dic )
        else:
            self.message( 'Click a file with   \'.chr\'   extension' )

    def cmdExport( self, *args ):
        #this needs to account for user fed file name into path field
        #set = cmds.textScrollList( self.setsForm.scroll, q=True, si=True )
        #file = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        path = cmds.textField( self.pathForm.field, q=True, tx=True )
        print self.path
        if os.path.isdir( self.path ):
            name = cmds.textField( self.exportNameForm.field, q=True, tx=True )
            comment = cmds.textField( self.exportCommentForm.field, q=True, tx=True )
            if '.clip' not in name:
                name = name + '.clip'
            cp.clipSave( name=name, path=self.path, comment=comment )
            self.populateClipList()
            self.message( 'Set   ' + name + '   exported to   ' + path + name )
        else:
            self.message( 'Add file name to path field. Action aborted.' )


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


