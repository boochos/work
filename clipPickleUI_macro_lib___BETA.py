import maya.cmds  as cmds
import maya.mel as mel
import anim_lib as al
import os
from subprocess import call
import subprocess
import clipPickleUI_micro_lib___BETA as ui
import clipPickle_lib as cp
import time

reload( al )
reload( ui )
reload( cp )

def message( what='', maya=False ):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print what

class CPUI( object ):
    '''
    Build CharacterSet UI
    '''

    def __init__( self, columnWidth=80 ):
        #external
        self.columnWidth = columnWidth
        #internal
        self.windowName = 'Clip Manager'
        self.path = os.path.expanduser( '~' ) + '/maya/clipLibrary/'
        #store/restore
        self.objects = []
        self.animBucket = []
        self.objX = None
        self.anim = None
        self.rootLayer = '(Root)'
        #execute
        self.cleanUI()
        self.gui()

    def cleanUI( self, *args ):
        try:
            cmds.deleteUI( self.windowName )
        except:
            pass

    def gui( self ):
        #window
        self.win = cmds.window( self.windowName, w=self.columnWidth, rtf=1 )
        #action
        self.control = ui.Action( 'clipAction', cmdAction='', label='', w=self.columnWidth )
        cmds.button( self.control.button1, e=True, c=self.cmdExport, h=40 )
        #cmds.button( self.control.button2, e=True, c=self.cmdImport )
        cmds.button( self.control.button3, e=True, c=self.cmdImport, h=40 )
        cmds.textScrollList( self.control.scroll1, e=True, sc=self.populatePreview, ams=False, dcc=self.cmdSelectObjectsInClip )
        cmds.textScrollList( self.control.scroll3, e=True, sc='print "not setup"', dcc=self.cmdSelectObjectsInLayer )    #edit in future

        cmds.showWindow( self.win )
        self.populateClipList()

    def cmdExport( self, *args ):
        name = cmds.textField( self.control.field1, q=True, tx=True )
        comment = cmds.textField( self.control.field2, q=True, tx=True )
        cp.clipSave( name=name, path=self.path, comment=comment )
        cmds.textScrollList( self.control.scroll1, edit=True, ra=True )
        self.populateClipList()
        path = os.path.join( self.path, name + '.clip' )
        message( 'Set   ' + name + '   exported to   ' + path + name )

    def cmdImport( self, *args ):
        #file
        selFile = cmds.textScrollList( self.control.scroll1, q=True, si=True )
        if selFile and '.clip' in selFile[0]:
            path = os.path.join( self.path, selFile[0] )
            try:
                ns = cmds.textScrollList( self.infoForm.scroll, q=True, si=True )[0]
            except:
                ns = ''
            print path
            #layers
            putLayerList = cmds.textScrollList( self.control.scroll3, q=True, si=True )
            #check if root is selected, replace with proper name = None
            if putLayerList:
                if self.rootLayer in putLayerList:
                    i = putLayerList.index( self.rootLayer )
                    putLayerList.pop( i )
                    putLayerList.insert( i, None )
            #print putLayerList
            #frame offset
            c1 = cmds.checkBox( self.control.c1, q=True, v=True )
            #objects list
            c2 = cmds.checkBox( self.control.c2, q=True, v=True )
            putObjectList = []
            if c2:
                putObjectList = cmds.ls( sl=1 )
                #print putObjectList, '___________fed list'
                if not putObjectList:
                    cmds.warning( '-- Can\'t import "Selected Objects Only". Select some objects to filter against or turn option OFF. --' )
                    return None
            #remap namespace
            c5 = cmds.checkBox( self.control.c5, q=True, v=True )
            #merge with existing layers
            c6 = cmds.checkBox( self.control.c6, q=True, v=True )
            #print c6
            #apply layer settings
            c7 = cmds.checkBox( self.control.c7, q=True, v=True )
            #print c7
            #import
            cp.clipApply( path=path, ns=c5, onCurrentFrame=c1, mergeExistingLayers=c6, applyLayerSettings=c7, putLayerList=putLayerList, putObjectList=putObjectList, poseOnly=False )
        else:
            message( 'Click a file with   \'.clip\'   extension' )

    def cmdSelectObjectsInClip( self ):
        selFile = cmds.textScrollList( self.control.scroll1, q=True, si=True )
        path = os.path.join( self.path, selFile[0] )
        self.clip = cp.clipOpen( path )
        self.populatePreview()
        cp.selectObjectsInClip( self.clip )

    def cmdSelectObjectsInLayer( self ):
        self.cmdClpNS()
        layer = cmds.textScrollList( self.control.scroll3, q=True, si=True )
        if self.rootLayer in layer:
            layer = [None]
        cp.selectObjectsInLayers( self.clip, layer )

    def cmdClpNS( self ):
        if cmds.ls( sl=1 ):
            self.clip = cp.putNS( self.clip )

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
        #print path
        self.clip = cp.clipOpen( path )
        '''
        for obj in self.clip.objects:
            cmds.textScrollList( self.previewForm.scroll, edit=True, append=self.format( obj.name ) )
        '''
        self.populateLayers()
        self.populateInfo()

    def populateLayers( self ):
        cmds.textScrollList( self.control.scroll3, edit=True, ra=True )
        #print self.clip.layers
        for layer in self.clip.layers:
            #print layer.name, '___'
            if layer.name:
                cmds.textScrollList( self.control.scroll3, edit=True, append=layer.name )
            else:
                cmds.textScrollList( self.control.scroll3, edit=True, append=self.rootLayer )

    def populateInfo( self ):
        if self.clip.comment:
            cmds.text( self.control.heading5, edit=True, label='     ' + str( self.clip.comment ) )
        else:
            cmds.text( self.control.heading5, edit=True, label='' )
        if self.clip.source:
            cmds.text( self.control.heading7, edit=True, label='     ' + str( self.clip.source ) )
        else:
            cmds.text( self.control.heading7, edit=True, label='' )
        if self.clip.user:
            cmds.text( self.control.heading9, edit=True, label='     ' + str( self.clip.user ) )
        else:
            cmds.text( self.control.heading9, edit=True, label='' )
        if self.clip.date:
            cmds.text( self.control.heading11, edit=True, label='     ' + str( self.clip.date ) )
        else:
            cmds.text( self.control.heading11, edit=True, label='' )
        if self.clip.length:
            cmds.text( self.control.heading13, edit=True, label='     ' + str( self.clip.length ) )
        else:
            cmds.text( self.control.heading13, edit=True, label='' )
        '''
        if self.clip.start:
            cmds.text( self.control.heading15, edit=True, label='     ' + str( self.clip.start ) )
        else:
            cmds.text( self.control.heading15, edit=True, label='' )
        if self.clip.start:
            cmds.text( self.control.heading17, edit=True, label='     ' + str( self.clip.start ) )
        else:
            cmds.text( self.control.heading17, edit=True, label='' )
        if self.clip.start:
            cmds.text( self.control.heading19, edit=True, label='     ' + str( self.clip.start ) )
        else:
            cmds.text( self.control.heading19, edit=True, label='' )
        if self.clip.start:
            cmds.text( self.control.heading21, edit=True, label='     ' + str( self.clip.start ) )
        else:
            cmds.text( self.control.heading21, edit=True, label='' )
        '''
