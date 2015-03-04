import maya.cmds as cmds
import maya.mel as mel
import os
#
# import clipPickleUI_micro_lib as ui
# import clipPickle_lib as cp
# import anim_lib as al
import webrImport as web
# web
ui = web.mod('clipPickleUI_micro_lib')
cp = web.mod('clipPickle_lib')
al = web.mod('anim_lib')
# TODO: add pose import and pose percentage import
# TODO: add UI support for multi ref import/exports
# each ref gets its on class, objects with no namespace get their own class


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class CPUI(object):

    '''
    Build CharacterSet UI
    '''

    def __init__(self, columnWidth=80):
        # external
        self.columnWidth = columnWidth
        # internal
        self.windowName = 'ClipManager'
        self.path = os.path.expanduser('~') + '/maya/clipLibrary/'
        # store/restore
        # self.objects = [] not used
        # self.animBucket = [] not used
        self.clipFiles = []
        self.objX = None
        self.anim = None
        self.rootLayer = '(Root)'
        # execute
        self.cleanUI()
        self.gui()

    def cleanUI(self, *args):
        try:
            cmds.deleteUI(self.windowName)
        except:
            pass

    def gui(self):
        # window
        self.win = cmds.window(self.windowName, w=self.columnWidth, rtf=1)
        # action
        self.control = ui.Action('clipAction', cmdAction='', label='', w=self.columnWidth)
        cmds.button(self.control.button1, e=True, c=self.cmdExport, h=40)
        # cmds.button( self.control.button2, e=True, c=self.cmdImport )
        cmds.button(self.control.button3, e=True, c=self.cmdImport, h=40)
        cmds.textScrollList(self.control.scroll1, e=True, sc=self.populateVersionList, ams=False, dcc=self.cmdSelectObjectsInClip)
        cmds.textScrollList(self.control.scroll2, e=True, sc=self.populatePreview, ams=False, dcc=self.cmdSelectObjectsInClip)  # edit in future
        cmds.textScrollList(self.control.scroll3, e=True, sc='print "not setup"', dcc=self.cmdSelectObjectsInLayer)  # edit in future

        cmds.showWindow(self.win)
        self.populateClipList()

    def cmdExport(self, *args):
        # TODO: overwrite or insert option
        # collect selections in UI
        sel = self.cmdCollectSelections()
        # export
        name = cmds.textField(self.control.field1, q=True, tx=True)
        comment = cmds.textField(self.control.field2, q=True, tx=True)
        version = '.' + self.cmdCreateVersionNumber()
        #
        cp.clipSave(name=name + version, comment=comment)
        cmds.textScrollList(self.control.scroll1, edit=True, ra=True)
        self.populateClipList()
        path = os.path.join(self.path, name + '.clip')
        message('Set   ' + name + '   exported to   ' + path)
        # apply selections
        # print sel
        if sel[0]:
            cmds.textScrollList(self.control.scroll1, e=True, si=sel[0])
            self.populateVersionList()
        if sel[1]:
            cmds.textScrollList(self.control.scroll2, e=True, si=sel[1])
        if sel[2]:
            cmds.textScrollList(self.control.scroll3, e=True, si=sel[2])

    def cmdImport(self, *args):
        # file
        selFile = cmds.textScrollList(self.control.scroll1, q=True, si=True)
        if selFile:
            path = self.cmdClipPath()
            try:
                ns = cmds.textScrollList(self.infoForm.scroll, q=True, si=True)[0]
            except:
                ns = ''
            # print path
            # layers
            putLayerList = cmds.textScrollList(self.control.scroll3, q=True, si=True)
            # check if root is selected, replace with proper name = None
            if putLayerList:
                if self.rootLayer in putLayerList:
                    i = putLayerList.index(self.rootLayer)
                    putLayerList.pop(i)
                    putLayerList.insert(i, None)
            # print putLayerList
            # frame offset
            c1 = cmds.checkBox(self.control.c1, q=True, v=True)
            # objects list
            c2 = cmds.checkBox(self.control.c2, q=True, v=True)
            putObjectList = []
            if c2:
                putObjectList = cmds.ls(sl=1, fl=1)
                # print putObjectList, '___________fed list'
                if not putObjectList:
                    cmds.warning('-- Can\'t import "Selected Objects Only". Select some objects to filter against or turn option OFF. --')
                    return None
            # remap namespace
            c5 = cmds.checkBox(self.control.c5, q=True, v=True)
            # merge with existing layers
            c6 = cmds.checkBox(self.control.c6, q=True, v=True)
            # print c6
            # apply layer settings
            c7 = cmds.checkBox(self.control.c7, q=True, v=True)
            # print c7
            # import
            cp.clipApply(path=path, ns=c5, onCurrentFrame=c1, mergeExistingLayers=c6, applyLayerSettings=c7, putLayerList=putLayerList, putObjectList=putObjectList,
                         start=None, end=None)
        else:
            message('Select a clip to import.')

    def cmdSelectObjectsInClip(self):
        path = self.cmdClipPath()
        if path:
            self.clip = cp.clipOpen(path)
            # self.populatePreview()
            cp.selectObjectsInClip(self.clip)
        # print path

    def cmdSelectObjectsInLayer(self):
        self.cmdClipNS()
        layer = cmds.textScrollList(self.control.scroll3, q=True, si=True)
        if self.rootLayer in layer:
            layer = [None]
        cp.selectObjectsInLayers(self.clip, layer)

    def cmdClipNS(self):
        if cmds.ls(sl=1):
            self.clip = cp.putNS(self.clip)

    def cmdClipPath(self):
        vr = ''
        selFile = cmds.textScrollList(self.control.scroll1, q=True, si=True)[0]
        if cmds.textScrollList(self.control.scroll2, q=True, ai=True):
            verFile = cmds.textScrollList(self.control.scroll2, q=True, si=True)[0]
            if verFile:
                vr = '.' + verFile
            else:
                pass
                # versionless, leagcy file or manually named
        selFile = selFile + vr + '.clip'
        path = os.path.join(self.path, selFile)
        return path

    def cmdCreateVersionNumber(self):
        name = cmds.textField(self.control.field1, q=True, tx=True)
        existingVersions = []
        num = []
        for vr in self.clipFiles:
            if name == vr.split('.')[0]:
                vr = vr.split('.')[1]
                if vr != 'clip':
                    existingVersions.append(vr)
        if existingVersions:
            for i in existingVersions:
                try:
                    num.append(int(i))
                except:
                    pass
            num = sorted(num)
            vr = num[len(num) - 1] + 1
            return '%04d' % vr
        else:
            return '0001'

    def cmdCollectSelections(self):
        scroll1 = cmds.textScrollList(self.control.scroll1, q=True, si=True)
        if scroll1:
            scroll1 = scroll1[0]
        scroll2 = cmds.textScrollList(self.control.scroll2, q=True, si=True)
        if scroll2:
            scroll2 = scroll2[0]
        scroll3 = cmds.textScrollList(self.control.scroll3, q=True, si=True)
        if scroll3:
            scroll3 = scroll3[0]
        return scroll1, scroll2, scroll3

    def populateClipList(self):
        # Make sure the path exists and access is permitted
        if os.path.isdir(self.path) and os.access(self.path, os.R_OK):
            #
            # Clear the textScrollList
            # cmds.textScrollList( self.control.scroll1, edit=True, ra=True )
            # Populate the directories and non-directories for organization
            #
            dirs = []
            nonDir = []
            # list the files in the path
            files = os.listdir(str(self.path))
            if len(files) > 0:
                # Sort the directory list based on the names in lowercase
                # This will error if 'u' objects are fed into a list
                files.sort(key=str.lower)
                self.clipFiles = []
                # pick out the directories
                for i in files:
                    if i[0] != '.':
                        if os.path.isdir(os.path.join(self.path, i)):
                            dirs.append(i)
                        else:
                            if '.clip' in i:
                                self.clipFiles.append(i)
                                i = i.split('.')[0]
                            nonDir.append(i)
                # Add the files
                # should be sorted by date created, latest at top
                nonDir = sorted(list(set(nonDir)))
                for i in nonDir:
                    cmds.textScrollList(self.control.scroll1, edit=True, append=i)

    def populateVersionList(self):
        cmds.textScrollList(self.control.scroll2, edit=True, ra=True)
        sel = cmds.textScrollList(self.control.scroll1, q=True, si=True)[0]
        version = []
        for f in self.clipFiles:
            if f.split('.')[0] == sel:
                vr = f.split('.')[1]
                if vr != 'clip':
                    # print f, '===========', vr, sel
                    version.append(vr)
                else:
                    version.append('')
            else:
                # print f + ' not in ' + sel + '_______________'
                pass
        if version:
            # print version
            version = sorted(version)
            if len(version) == 1 and version[0] == '':  # dont draw versions if only 1 exists and matches string ''
                pass
            else:  #
                for i in reversed(version):
                    cmds.textScrollList(self.control.scroll2, edit=True, append=i)
                cmds.textScrollList(self.control.scroll2, edit=True, sii=[1])
            self.populatePreview()

    def populateExportName(self):
        selFile = cmds.textScrollList(self.control.scroll1, q=True, si=True)[0]
        cmds.textField(self.control.field1, e=True, tx=selFile)

    def populatePreview(self):
        path = self.cmdClipPath()
        if path:
            # print path
            self.clip = cp.clipOpen(path)
            self.populateLayers()
            self.populateInfo()
            self.populateExportName()

    def populateLayers(self):
        cmds.textScrollList(self.control.scroll3, edit=True, ra=True)
        # print self.clip.layers
        for layer in self.clip.layers:
            # print layer.name, '___'
            if layer.name:
                cmds.textScrollList(self.control.scroll3, edit=True, append=layer.name)
            else:
                cmds.textScrollList(self.control.scroll3, edit=True, append=self.rootLayer)

    def populateInfo(self):
        if self.clip.comment:
            cmds.text(self.control.heading5, edit=True, label='     ' + str(self.clip.comment))
        else:
            cmds.text(self.control.heading5, edit=True, label='')
        if self.clip.source:
            cmds.text(self.control.heading7, edit=True, label='     ' + str(self.clip.source))
        else:
            cmds.text(self.control.heading7, edit=True, label='')
        if self.clip.user:
            cmds.text(self.control.heading9, edit=True, label='     ' + str(self.clip.user))
        else:
            cmds.text(self.control.heading9, edit=True, label='')
        if self.clip.date:
            cmds.text(self.control.heading11, edit=True, label='     ' + str(self.clip.date))
        else:
            cmds.text(self.control.heading11, edit=True, label='')
        if self.clip.length:
            cmds.text(self.control.heading13, edit=True, label='     ' + str(self.clip.length))
        else:
            cmds.text(self.control.heading13, edit=True, label='')
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

    def progressBar(self):
        # calculate progress bar....wont work
        barDiv = sum(1 for line in open('/home/sebastianw/maya/clipLibrary/3rdTrakkerIn_LatticePoints.0001.clip'))
