import maya.cmds  as cmds
import constraintUI_micro_lib as ui
import constraint_lib as cn
import maya.mel as mel
import anim_lib as al
import os, sys, sys_lib, fnmatch
from subprocess import call
import subprocess
import clipPickleUI_micro_lib___BETA as ui
import clipPickle_lib as cp
import time

reload(al)
reload(cn)
reload(ui)
reload(cp)

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

class CPUI(object):
    '''
    Build CharacterSet UI
    '''

    def __init__(self, columnWidth=80):
        #external
        self.columnWidth                  = columnWidth
        #internal
        self.windowName                   = 'Clip Manager'
        self.path=os.path.expanduser( '~' ) + '/maya/clipLibrary/'
        #store/restore
        self.objects  = []
        self.animBucket = []
        self.objX = None
        self.anim = None
        #execute
        self.cleanUI()
        self.gui()

    def cleanUI(self, *args):
        try:
            cmds.deleteUI(self.windowName)
        except:
            pass

    def gui(self):
        #window
        self.win = cmds.window(self.windowName, w=self.columnWidth, rtf=1)
        #action
        self.control = ui.Action('clipAction', cmdAction='', label='', w=self.columnWidth)
        cmds.button(self.control.button1, e=True, c=self.cmdExport, h=40)
        cmds.button(self.control.button2, e=True, c=self.cmdImport)
        cmds.button(self.control.button3, e=True, c=self.cmdImport, h=40)
        cmds.textScrollList(self.control.scroll1, e=True, sc=self.populatePreview)

        cmds.showWindow(self.win)
        self.populateClipList()

    def cmdExport( self, *args ):
        name = cmds.textField( self.control.field1, q=True, tx=True )
        path = os.path.join( self.path, name + '.clip' )
        if os.path.isdir( self.path ):
            comment = cmds.textField( self.control.field2, q=True, tx=True )
            if '.clip' not in name:
                name = name + '.clip'
            cp.clipSave( name=name, path=self.path, comment=comment )
            cmds.textScrollList( self.control.scroll1, edit=True, ra=True )
            self.populateClipList()
            message( 'Set   ' + name + '   exported to   ' + path + name )
        else:
            message( 'Add file name to path field. Action aborted.' )

    def cmdImport( self, *args ):
        selFile = cmds.textScrollList( self.control.scroll1, q=True, si=True )
        if selFile and '.clip' in selFile[0]:
            path = path = os.path.join( self.path, selFile[0] )
            #prefix = cmds.textField( self.exportCommentForm.field, q=True, tx=True )
            try:
                ns = cmds.textScrollList( self.infoForm.scroll, q=True, si=True )[0]
            except:
                ns = ''
            print path
            cp.clipRemap( path=path )
                #cs.importFile( path, prefix=prefix, ns=ns, rp=dic )
        else:
            message( 'Click a file with   \'.chr\'   extension' )

    def populateClipList( self ):
        #Make sure the path exists and access is permitted
        if os.path.isdir( self.path ) and os.access( self.path, os.R_OK ):
            #Clear the textScrollList
            #cmds.textScrollList( self.control.scroll1, edit=True, ra=True )
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
                    cmds.textScrollList( self.control.scroll1, edit=True, append=i )

    def populatePreview( self ):
        path = os.path.join( self.path, cmds.textScrollList( self.control.scroll1, query=True, si=True )[0] )
        self.clip = cp.clipOpen( path )
        '''
        for obj in self.clip.objects:
            cmds.textScrollList( self.previewForm.scroll, edit=True, append=self.format( obj.name ) )
        '''
        self.populateInfo()

    def populateInfo( self ):
        #len()
        print self.clip.layers[2].name, '__________________'
        self.clip.layers[2].getStartEndLength()
        cmds.text( self.control.heading5, edit=True, label='     ' + str( self.clip.layers[2].comment ) )
        cmds.text( self.control.heading7, edit=True, label='     ' + str( self.clip.layers[2].end ) )
        cmds.text( self.control.heading9, edit=True, label='     ' + str( self.clip.layers[2].start ) )
        cmds.text( self.control.heading11, edit=True, label=str( self.clip.end ) )
        cmds.text( self.control.heading13, edit=True, label=str( self.clip.length ) )
        cmds.text( self.control.heading15, edit=True, label=str( self.clip.start ) )
        cmds.text( self.control.heading17, edit=True, label=str( self.clip.start ) )
        cmds.text( self.control.heading19, edit=True, label=str( self.clip.start ) )
        cmds.text( self.control.heading21, edit=True, label=str( self.clip.start ) )
