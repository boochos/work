import maya.cmds as cmds
import maya.mel as mel
import os
import platform
import subprocess
import copy
from subprocess import call
#
# import clipPickleUI_micro_lib as ui
# import clipPickle_lib as cp
# import anim_lib as al
import webrImport as web
# web
ui = web.mod('clipPickleUI_micro_lib')
cp = web.mod('clipPickle_lib')
al = web.mod('anim_lib')
fr = web.mod('frameRange_lib')
# TODO: add pose percentage import
# TODO: add UI support for multi ref import/exports
# each ref gets its on class, objects with no namespace get their own class


def message(what='', maya=True, warning=False):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace('\\', '/')
    if warning:
        cmds.warning(what)
    else:
        if maya:
            mel.eval('print \"' + what + '\";')
        else:
            print wha


class CPUI(object):

    '''
    Build CharacterSet UI
    '''

    def __init__(self, columnWidth=80):
        # external
        self.columnWidth = columnWidth
        # internal
        self.windowName = 'ClipManager'
        #self.path = os.path.expanduser('~') + '/maya/clipLibrary/'
        self.path = cp.clipDefaultPath()
        # store/restore
        # self.objects = [] not used
        # self.animBucket = [] not used
        self.clip = None
        self.clipOut = None # editable copy for importing
        self.clipFiles = []
        self.objX = None
        self.anim = None
        self.rootLayer = 'BaseAnimation'
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
        cmds.button(self.control.heading3, e=True, c=self.cmdLibrary)
        cmds.button(self.control.heading6, e=True, c=self.cmdOpenFileWIndow)
        # cmds.button( self.control.button2, e=True, c=self.cmdImport )
        cmds.button(self.control.button3, e=True, c=self.cmdImport, h=40)
        cmds.textScrollList(self.control.scroll1, e=True, sc=self.populateVersionList, ams=False, dcc=self.cmdSelectObjectsInClip)
        cmds.textScrollList(self.control.scroll2, e=True, sc=self.populatePreview, ams=False, dcc=self.cmdSelectObjectsInClip)  # edit in future
        cmds.textScrollList(self.control.scroll3, e=True, sc='print "not setup"', dcc=self.cmdSelectObjectsInLayer)  # edit in future

        self.cmdLoadingHintToggle(on=False)
        cmds.showWindow(self.win)
        self.populateClipList()

    def cmdOpenFile(self, *args):
        cmds.file(self.clip.path, open=True, f=True)
        cmds.deleteUI('OpenSourceFile')

    def cmdOpenFileWIndow(self, path=''):
        ofw = 'OpenSourceFile'
        ofwc = 'openSourceFileForm'
        ofb = 'openClipFileButton'
        font = 'obliqueLabelFont'
        if self.clip:
            path = self.clip.path
        if cmds.window(ofw, q=True, ex=True):
            cmds.deleteUI(ofw)
        ofw = cmds.window(ofw)
        ofwc = cmds.columnLayout(ofwc, cal='center', cat=['both', 1], adj=True, w=350)
        print path
        if path:
            cmds.textField(tx=path + '\n', fn=font, ed=False)
            if os.path.isfile(path):
                cmds.button(ofb, label='Open File', al='center', c=self.cmdOpenFile)
            else:
                cmds.button(ofb, label="File doesn't exist", al='center')
        else:
            cmds.text(label=' -- NO PATH --  ', al='center', fn=font)
        cmds.showWindow(ofw)

    def cmdLibrary(self, *args):
        path = cp.clipDefaultPath()
        if os.name == 'nt':
            # print path
            # path = path.replace('\'', '\\')
            # print path
            if os.path.isdir(path):
                subprocess.Popen(r'explorer /open, ' + path)
        elif platform.system() == 'Darwin':
            subprocess.call(["open", "-R", path])
        else:
            # message('Close file window to regain control over MAYA.')
            app = "nautilus"
            call([app, path])

    def cmdTypeEx(self):
        # type of export
        typ = [None, False, True]
        v = cmds.radioButtonGrp(self.control.typGrpEx, q=True, select=True)
        # print typ[v]
        return typ[v]

    def cmdTypeIm(self):
        # type of export
        typ = [None, False, True]
        v = cmds.radioButtonGrp(self.control.typGrpIm, q=True, select=True)
        # print typ[v]
        return typ[v]

    def cmdExport(self, *args):
        # TODO: overwrite or insert option
        # collect selections in UI
        sel = self.cmdCollectSelections()
        # export
        name = cmds.textField(self.control.field1, q=True, tx=True)
        if name:
            if cmds.ls(sl=True):
                comment = cmds.textField(self.control.field2, q=True, tx=True)
                version = '.' + self.cmdCreateVersionNumber()
                #
                poseOnly = self.cmdTypeEx()
                #
                start = cmds.floatField(self.control.float1, q=True, value=True)
                end = cmds.floatField(self.control.float2, q=True, value=True)
                # print start, end, '___ ui'
                bakeRange = [start, end]
                #
                cp.clipSave(name=name + version, comment=comment, poseOnly=poseOnly, bakeRange=bakeRange)
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
                    cmds.textScrollList(self.control.scroll2, e=True, sii=1)
                if sel[2]:
                    cmds.textScrollList(self.control.scroll3, e=True, si=sel[2])
            else:
                message('Select some objects. Export aborted.', maya=True, warning=True)
        else:
            message('Provided a name. Export aborted.', maya=True, warning=True)

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
            # apply layer settings
            c7 = cmds.checkBox(self.control.c7, q=True, v=True)
            c8 = cmds.checkBox(self.control.c8, q=True, v=True)
            # range
            start = cmds.floatField(self.control.int1, q=True, v=True)
            end = cmds.floatField(self.control.int2, q=True, v=True)
            # get import type
            poseOnly = self.cmdTypeIm()
            # import
            self.clipOut = copy.deepcopy(self.clip)
            cp.clipApply(path=path, ns=c5, onCurrentFrame=c1, mergeExistingLayers=c6, applyLayerSettings=c7, applyRootAsOverride=c8, putLayerList=putLayerList, putObjectList=putObjectList,
                         start=start, end=end, poseOnly=poseOnly, clp=self.clipOut)
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

    def cmdLoadingHintToggle(self, on=False, info=True, options=True, range=True):
        '''
        disables some ui elements for clarity
        '''
        if not on:
            if info:
                cmds.textScrollList(self.control.scroll2, e=True, en=False)
                cmds.textScrollList(self.control.scroll3, e=True, en=False)
                cmds.textField(self.control.heading7, e=True, en=False, tx='off')
                cmds.button(self.control.heading6, e=True, en=False)
                cmds.rowLayout(self.control.row5, e=True, en=False)
                cmds.text(self.control.heading9, e=True, l='')
                cmds.rowLayout(self.control.row4, e=True, en=False)
                cmds.text(self.control.heading11, e=True, l='')
                cmds.radioButtonGrp(self.control.typGrpIm, edit=True, en=False)
            if options:
                cmds.checkBox(self.control.c1, e=True, en=False)
                cmds.checkBox(self.control.c2, e=True, en=False)
                cmds.checkBox(self.control.c5, e=True, en=False)
                cmds.checkBox(self.control.c6, e=True, en=False)
                cmds.checkBox(self.control.c7, e=True, en=False)
                cmds.checkBox(self.control.c8, e=True, en=False)
            if range:
                # headings
                cmds.text(self.control.heading12, e=True, en=False)
                cmds.text(self.control.heading13, e=True, en=False, l='')
                cmds.text(self.control.heading24, e=True, en=False)
                cmds.text(self.control.heading26, e=True, en=False)
                # sliders
                cmds.intSlider(self.control.sl1, edit=True, min=0, max=10, value=0, step=1, en=False)
                cmds.intSlider(self.control.sl2, edit=True, min=0, max=10, value=0, step=1, en=False)
                # fields
                cmds.floatField(self.control.int1, edit=True, min=0, max=10, value=0, step=0.1, en=False)
                cmds.floatField(self.control.int2, edit=True, min=0, max=10, value=0, step=0.1, en=False)
        else:
            if info:
                cmds.textScrollList(self.control.scroll2, e=True, en=True)
                cmds.textScrollList(self.control.scroll3, e=True, en=True)
                cmds.textField(self.control.heading7, e=True, en=True)
                cmds.button(self.control.heading6, e=True, en=True)
                cmds.rowLayout(self.control.row5, e=True, en=True)
                cmds.text(self.control.heading9, e=True)
                cmds.rowLayout(self.control.row4, e=True, en=True)
                cmds.text(self.control.heading11, e=True)
                cmds.radioButtonGrp(self.control.typGrpIm, edit=True, en=True)
            if options:
                cmds.checkBox(self.control.c1, e=True, en=True)
                cmds.checkBox(self.control.c2, e=True, en=True)
                cmds.checkBox(self.control.c5, e=True, en=True)
                cmds.checkBox(self.control.c6, e=True, en=True)
                cmds.checkBox(self.control.c7, e=True, en=True)
                cmds.checkBox(self.control.c8, e=True, en=True)
            if range:
                # headings
                cmds.text(self.control.heading12, e=True, en=True)
                cmds.text(self.control.heading13, e=True, en=True)
                cmds.text(self.control.heading24, e=True, en=True)
                cmds.text(self.control.heading26, e=True, en=True)
        # cmds.refresh()

    def cmdRangeUpdateMin(self, *arg):
        # get slider value
        v = cmds.intSlider(self.control.sl1, q=True, v=True)
        # edit int field
        cmds.floatField(self.control.int1, edit=True, value=v)
        # highest value for minimum value of slider2 has to be 1 less than max value
        if v < cmds.intSlider(self.control.sl2, q=True, max=True):
            cmds.intSlider(self.control.sl2, e=True, min=v)
            cmds.intSlider(self.control.sl2, e=True, en=True)
        elif v == cmds.intSlider(self.control.sl2, q=True, max=True):
            #cmds.intSlider(self.control.sl2, e=True, min=v+1)
            cmds.intSlider(self.control.sl2, e=True, en=False)
        else:
            pass
            # cmds.intSlider(self.control.sl2, e=True, min=v-1)
        # print v, 'upper slider -----    ', cmds.intSlider(self.control.sl1, q=True, min=True), cmds.intSlider(self.control.sl1, q=True, max=True), 'upper range   -----', cmds.intSlider(self.control.sl2, q=True, min=True), cmds.intSlider(self.control.sl2, q=True, max=True), '  lower range'
        e = cmds.floatField(self.control.int2, q=True, value=True)
        s = cmds.floatField(self.control.int1, q=True, value=True)
        cmds.text(self.control.heading13, edit=True, label=str((e - s) + 1))

    def cmdRangeUpdateMax(self, *arg):
        # get slider value
        v = cmds.intSlider(self.control.sl2, q=True, v=True)
        # edit int field
        cmds.floatField(self.control.int2, edit=True, value=v)
        # lowest value for maximum value of slider 1 has to be 1 higher than minimum value
        if v > cmds.intSlider(self.control.sl1, q=True, min=True):
            cmds.intSlider(self.control.sl1, e=True, max=v)
            cmds.intSlider(self.control.sl1, e=True, en=True)
        elif v == cmds.intSlider(self.control.sl1, q=True, min=True):
            #cmds.intSlider(self.control.sl1, e=True, max=v-1)
            cmds.intSlider(self.control.sl1, e=True, en=False)
        else:
            pass
            # cmds.intSlider(self.control.sl1, e=True, max=v+1)
        # print v, 'lower slider -----    ', cmds.intSlider(self.control.sl1, q=True, min=True), cmds.intSlider(self.control.sl1, q=True, max=True), 'upper range   -----', cmds.intSlider(self.control.sl2, q=True, min=True), cmds.intSlider(self.control.sl2, q=True, max=True), '  lower range'
        e = cmds.floatField(self.control.int2, q=True, value=True)
        s = cmds.floatField(self.control.int1, q=True, value=True)
        cmds.text(self.control.heading13, edit=True, label=str((e - s) + 1))

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
        self.cmdLoadingHintToggle(on=False)
        cmds.textField(self.control.heading7, e=True, tx='  --  LOADING  --  ')
        cmds.refresh()
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
            self.populateRange()

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
            cmds.textField(self.control.field2, edit=True, tx=str(self.clip.comment))
        else:
            cmds.textField(self.control.field2, edit=True, tx='')
        if self.clip.source:
            cmds.textField(self.control.heading7, edit=True, tx=str(self.clip.source))
        else:
            cmds.textField(self.control.heading7, edit=True, tx='')
        if self.clip.user:
            cmds.text(self.control.heading9, edit=True, label=str(self.clip.user))
        else:
            cmds.text(self.control.heading9, edit=True, label='')
        if self.clip.date:
            cmds.text(self.control.heading11, edit=True, label=str(self.clip.date))
        else:
            cmds.text(self.control.heading11, edit=True, label='')
        if self.clip.length:
            cmds.text(self.control.heading13, edit=True, label=str(self.clip.length))
        else:
            cmds.text(self.control.heading13, edit=True, label='')
        if self.clip.poseOnly:
            self.cmdLoadingHintToggle(on=True, info=True, options=False, range=False)
            cmds.button(self.control.button3, e=True, l='P O S E')
            cmds.textScrollList(self.control.scroll3, edit=True, en=False, ra=True)
            cmds.radioButtonGrp(self.control.typGrpIm, edit=True, select=2, en1=False, en=True)
            cmds.columnLayout(self.control.col2, e=True, en=False)
            cmds.rowLayout(self.control.row3, e=True, en=False)
        else:
            self.cmdLoadingHintToggle(on=True, info=True, options=True, range=True)
            cmds.button(self.control.button3, e=True, l='I M P O R T')
            cmds.textScrollList(self.control.scroll3, edit=True, en=True)
            cmds.radioButtonGrp(self.control.typGrpIm, edit=True, select=1, en1=True)
            cmds.columnLayout(self.control.col2, e=True, en=True)
            cmds.rowLayout(self.control.row3, e=True, en=True)

    def populateRange(self):
        # self.control.heading5
        if self.clip.start:
            if (self.clip.end - self.clip.start) > 0.0:
                # sliders
                cmds.intSlider(self.control.sl1, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.start, step=1, dc=self.cmdRangeUpdateMin, en=True)
                cmds.intSlider(self.control.sl2, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.end, step=1, dc=self.cmdRangeUpdateMax, en=True)
                # fields
                cmds.floatField(self.control.int1, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.start, step=0.1, en=False)
                cmds.floatField(self.control.int2, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.end, step=0.1, en=False)
            else:
                # sliders
                cmds.intSlider(self.control.sl1, edit=True, min=0, max=10, value=0, step=1, en=False)
                cmds.intSlider(self.control.sl2, edit=True, min=0, max=10, value=0, step=1, en=False)
                # fields
                cmds.floatField(self.control.int1, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.start, step=0.1, en=True)
                cmds.floatField(self.control.int2, edit=True, min=self.clip.start, max=self.clip.end, value=self.clip.end, step=0.1, en=True)
        else:
            # sliders
            cmds.intSlider(self.control.sl1, edit=True, min=0, max=10, value=0, step=1, en=False)
            cmds.intSlider(self.control.sl2, edit=True, min=0, max=10, value=0, step=1, en=False)
            # fields
            cmds.floatField(self.control.int1, edit=True, min=0, max=10, value=0, step=0.1, en=False)
            cmds.floatField(self.control.int2, edit=True, min=0, max=10, value=0, step=0.1, en=False)

    def progressBar(self):
        # calculate progress bar....wont work
        barDiv = sum(1 for line in open('/home/sebastianw/maya/clipLibrary/3rdTrakkerIn_LatticePoints.0001.clip'))
