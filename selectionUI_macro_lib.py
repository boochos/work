import maya.cmds as cmds
import maya.mel as mel
import os
#
import webrImport as web
# web
ui = web.mod('ui_micro_lib')
cs = web.mod('characterSet_lib')
ss = web.mod('selectionSet_lib')


idJ = None


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
            print what


class CSUI(object):

    '''
    Build Selection Set UI
    '''
    # TODO: filter applicable sets on launch, perform filter in populateBrowse command
    # TODO: add auto select set on click mode, multi select
    # FUTURE: highlight sets that contain current maya selection
    # BUG: if a set is created from 2 objects with same name and dif namespace, only one is saved to file
    # https://tug.org/pracjourn/2007-4/walden/color.pdf

    def __init__(self):
        # external
        self.path = ss.defaultPath()
        self.columnWidth = 200
        # internal
        self.selDir = os.path.split(self.path)[1]
        self.windowName = 'SelectionSetManager'
        self.dirStr = ' / '
        self.ext = '.sel'
        self.scroll = ''
        self.members = {}
        self.popupName = 'RenameSet'
        self.createLabel = 'Create Set'
        self.renameLabel = 'RENAME SET'
        self.overwriteLabel = '-- O V E R W R I T E --'
        self.alternateUI = False
        # color
        self.neutral = [0.38, 0.38, 0.38]
        self.darkbg = [0.17, 0.17, 0.17]
        self.grey = [0.5, 0.5, 0.5]
        self.greyD = [0.2, 0.2, 0.2]
        self.red = [0.5, 0.2, 0.2]
        self.redD = [0.4, 0.2, 0.2]
        self.blue = [0.2, 0.3, 0.5]
        self.green = [0.2, 0.5, 0.0]
        self.teal = [0.0, 0.5, 0.5]
        self.purple = [0.35, 0.35, 0.5]
        self.purple2 = [0.28, 0.28, 0.39]
        self.orange = [0.5, 0.35, 0.0]
        self.pink = [0.8, 0.4, 0.4]
        # execute
        self.populatePathWindows()
        self.cleanUI()
        self.browseUI()
        self.drawWindow()
        self.populateBrowse()
        self.populateSelection()

    def message(self, what='', maya=True, ui=True, *args):
        if what != '':
            if '\\' in what:
                what = what.replace('\\', '/')
            if maya:
                mel.eval('print \"' + '-- ' + what + ' --' + '\";')
        else:
            print ''
        if ui:
            cmds.text(self.messageForm.heading, edit=True, l='   ' + what + '   ')

    def cleanUI(self, *args):
        # IGNORE: script job keeps running if window is closed with X button
        try:
            cmds.deleteUI(self.windowName)
        except:
            pass

    def browseUI(self):
        self.win = cmds.window(self.windowName, w=700)
        # main form
        self.mainForm = cmds.formLayout('mainFormSs')
        # left form
        cmds.setParent(self.mainForm)
        self.mainTopLeftForm = cmds.formLayout('mainTopLeftFormSs', w=self.columnWidth, h=80)
        attachForm = [(self.mainTopLeftForm, 'left', 5), (self.mainTopLeftForm, 'top', 5), (self.mainTopLeftForm, 'bottom', 5)]
        cmds.formLayout(self.mainForm, edit=True, attachForm=attachForm)
        # create set ui
        self.createSetForm = ui.Form(label='Set Name', name='createSs', parent=self.mainTopLeftForm, createField=True)
        cmds.textField(self.createSetForm.field, e=True, ec=self.cmdCreate, aie=True)
        cmds.formLayout(self.createSetForm.form, edit=True, h=60)
        attachForm = [(self.createSetForm.form, 'left', 0), (self.createSetForm.form, 'top', 0), (self.createSetForm.form, 'right', 0)]
        cmds.formLayout(self.mainTopLeftForm, edit=True, attachForm=attachForm)
        # browse ui
        self.browseForm = ui.Form(label='Select Sets', name='browseSs', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdBrowse, cmdDouble=self.renameUI, h=80, allowMultiSelection=True)
        attachForm = [(self.browseForm.form, 'left', 0), (self.browseForm.form, 'bottom', 0), (self.browseForm.form, 'right', 0)]
        attachControl = [(self.browseForm.form, 'top', 0, self.createSetForm.form)]
        cmds.formLayout(self.mainTopLeftForm, edit=True, attachForm=attachForm, attachControl=attachControl)
        # edit sets ui
        cmds.setParent(self.mainForm)
        self.mainModularForm = cmds.formLayout('mainTopRightFormSs', w=200, h=100)
        attachForm = [(self.mainModularForm, 'top', 5), (self.mainModularForm, 'right', 5), (self.mainModularForm, 'bottom', 5)]
        attachControl = [(self.mainModularForm, 'left', 5, self.mainTopLeftForm)]
        cmds.formLayout(self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl)

        # copied from export cs function, deleted
        moveUp = 23
        # preview
        self.previewForm = ui.Form(label='Set Members', name='selectionSets', parent=self.mainModularForm, createList=True, h=80, allowMultiSelection=True)
        cmds.formLayout(self.previewForm.form, edit=True, w=200)
        attachForm = [(self.previewForm.form, 'left', 0), (self.previewForm.form, 'top', 0), (self.previewForm.form, 'bottom', 0)]
        cmds.formLayout(self.mainModularForm, edit=True, attachForm=attachForm)
        # scene selection
        self.selectionForm = ui.Form(label='Maya Selection', name='selection', parent=self.mainModularForm, createList=True, h=80, allowMultiSelection=True)
        cmds.formLayout(self.selectionForm.form, edit=True, w=1)
        attachForm = [(self.selectionForm.form, 'top', 0), (self.selectionForm.form, 'right', 0), (self.selectionForm.form, 'bottom', 0)]
        attachControl = [(self.selectionForm.form, 'left', 5, self.previewForm.form)]
        cmds.formLayout(self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl)
        cmds.textScrollList(self.selectionForm.scroll, e=True, en=False)
        # buttons
        addLimbMember = ui.Button(name='AddMember', label='Add Members', cmd=self.cmdAddMember, parent=self.selectionForm.form, moveUp=moveUp * 0)
        removeMember = ui.Button(name='removeMember', label='Remove Members', cmd=self.cmdRemoveMember, parent=self.previewForm.form, moveUp=moveUp * 0)
        deleteSet = ui.Button(name='deleteSet', label='Delete Set', cmd=self.cmdDelete, parent=self.browseForm.form, moveUp=moveUp * 0)
        self.createSet = ui.Button(name='addSet', label=self.createLabel, cmd=self.cmdCreate, parent=self.createSetForm.form, moveUp=moveUp * 0)
        # accommodate new buttons
        moveUp = moveUp + 2
        attachForm = [(self.previewForm.scroll, 'bottom', moveUp * 1)]
        cmds.formLayout(self.previewForm.form, edit=True, attachForm=attachForm)
        attachForm = [(self.selectionForm.scroll, 'bottom', moveUp * 1)]
        cmds.formLayout(self.selectionForm.form, edit=True, attachForm=attachForm)
        attachForm = [(self.browseForm.scroll, 'bottom', moveUp * 1)]
        cmds.formLayout(self.browseForm.form, edit=True, attachForm=attachForm)

        self.scroll = self.selectionForm.scroll
        toggleJob(scroll=self.scroll)

    def renameUI(self):
        if not self.alternateUI:
            self.alternateUI = True
            name = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)[0]
            cmds.textField(self.createSetForm.field, e=True, text=name, ec=self.cmdRename)
            cmds.button(self.createSet.name, e=True, l=self.renameLabel, c=self.cmdRename, bgc=self.blue)
            cmds.formLayout(self.mainModularForm, e=True, en=False)
            cmds.setFocus(self.createSetForm.field)
        else:
            # reset UI
            self.alternateUI = False
            cmds.textField(self.createSetForm.field, e=True, text='', ec=self.cmdCreate, aie=True)
            cmds.button(self.createSet.name, e=True, l=self.createLabel, c=self.cmdCreate, bgc=self.neutral)
            cmds.formLayout(self.mainModularForm, e=True, en=True)
            cmds.textField(self.createSetForm.field, e=True, bgc=self.darkbg)
            cmds.setFocus(self.browseForm.scroll)

    def overwriteUI(self):
        name = cmds.textField(self.createSetForm.field, q=True, text=True)
        #cmds.textScrollList(self.browseForm.scroll, e=True, da=True)
        #cmds.textScrollList(self.browseForm.scroll, e=True, si=name)
        # self.populatePreview()
        cmds.formLayout(self.mainModularForm, e=True, en=False)
        cmds.textField(self.createSetForm.field, e=True, aie=False)
        cmds.button(self.createSet.name, e=True, l=self.overwriteLabel, c=self.cmdOverwrite, bgc=self.red)
        self.alternateUI = True

    def displayStyleUI(self):
        pass

    def queryApplicableSets(self):
        pass

    def drawWindow(self):
        cmds.showWindow(self.win)

    def populatePathWindows(self):
        if os.name == 'nt':
            self.path = self.path.replace('/', '\\')

    def populateBrowse(self):
        # FUTURE: add a reason for directory browsing or remove the feature
        # Make sure the path exists and access is permitted
        if os.path.isdir(self.path) and os.access(self.path, os.R_OK):
            # Clear the textScrollList
            cmds.textScrollList(self.browseForm.scroll, edit=True, ra=True)
            # Append the '..'(move up a director) as the first item
            # cmds.textScrollList(self.browseForm.scroll, edit=True, append='..')
            # Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            # list the files in the path
            files = os.listdir(str(self.path))
            if files:
                # Sort the directory list based on the names in lowercase
                # This will error if 'u' objects are fed into a list
                files.sort(key=str.lower)
                # pick out the directories
                for i in files:
                    if i[0] != '.':
                        if os.path.isdir(os.path.join(self.path, i)):
                            dirs.append(i)
                        else:
                            nonDir.append(i)
                # Add the directories first
                for i in dirs:
                    cmds.textScrollList(self.browseForm.scroll, edit=True, append=self.dirStr + i)
                # Add the files next
                for i in nonDir:
                    # print i
                    if self.ext in i:
                        i = i.split('.')[0]
                        cmds.textScrollList(self.browseForm.scroll, edit=True, append=i)

    def populatePreview(self):
        cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
        browseSels = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if self.alternateUI:
            self.renameUI()
        if browseSels:
            for browseSel in browseSels:
                path = os.path.join(self.path, browseSel) + self.ext
                self.members = ss.loadFile(path)
                keys = sorted(self.members.keys())
                for key in keys:
                    cmds.textScrollList(self.previewForm.scroll, edit=True, append=key)

    def populateSelection(self):
        cmds.textScrollList(self.selectionForm.scroll, edit=True, ra=True)
        selection = cmds.ls(sl=True, fl=True)
        if selection:
            for sel in selection:
                cmds.textScrollList(self.selectionForm.scroll, edit=True, append=sel)
        else:
            pass
            # cmds.textScrollList(self.selectionForm.scroll, edit=True, append='Nothing Selected')

    def cmdBrowse(self, *args):
        tmp = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if tmp is not None:
            item = tmp[0]
            # find if the current item is a directory
            if item[:len(self.dirStr)] == self.dirStr:
                item = item[len(self.dirStr):]
                path = os.path.join(self.path, item)
                if os.path.exists(path):
                    self.path = str(path)
                    if os.access(path, os.R_OK):
                        try:
                            cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
                        except:
                            pass
                        self.populateBrowse()
                    else:
                        print 'no access'
            elif item == '..':
                # dont allow out of base dir
                if os.path.split(self.path)[1] is not self.selDir:
                    path = os.path.split(self.path)[0]
                    # query existence
                    if os.path.exists(path):
                        if os.access(path, os.R_OK):
                            self.path = path
                            try:
                                cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
                            except:
                                pass
                            self.populateBrowse()
                else:
                    message('Currently at root of Selection Set directory.', warning=True)
            else:
                # this is a file
                path = os.path.join(self.path, item + self.ext)
                # print path
                if os.path.isfile(path):
                    try:
                        self.populatePreview()
                    except:
                        pass
        else:
            print 'here'

    def cmdAddMember(self, *args):
        selSets = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if len(selSets) > 1:
            message('Too many sets selected', warning=True)
        else:
            selSet = selSets[0]
            if selSet:
                selSet = selSet[0]
                path = path = os.path.join(self.path, selSet) + self.ext
                # print path
                if os.path.isfile(path):
                    selection = cmds.textScrollList(self.selectionForm.scroll, q=True, ai=True)
                    selection = ss.outputDict(selection)
                    if selection:
                        for key in selection:
                            if key not in self.members.keys():
                                self.members[key] = selection[key]
                        ss.exportFile(path, sel=self.members)
                        self.populatePreview()
                    else:
                        message('Select an object in your scene.', warning=True)
                else:
                    message('File path does not exist ' + path, warning=True)
            else:
                message('Select a set in the left column.', warning=True)

    def cmdRemoveMember(self, *args):
        #
        if self.members:
            names = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
            if len(names) > 1:
                message('Too many sets selected', warning=True)
            else:
                selection = cmds.textScrollList(self.previewForm.scroll, q=True, si=True)
                selection = ss.outputDict(selection)
                if selection:
                    for key in selection:
                        del self.members[key]
                    f = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)[0]
                    path = os.path.join(self.path, f) + self.ext
                    ss.exportFile(path, sel=self.members)
                    self.populatePreview()
                else:
                    message('Select an object in the middle column.', warning=True)
        else:
            message('Set is empty, nothing to remove.', warning=True)

    def cmdCreate(self, *args):
        #
        name = cmds.textField(self.createSetForm.field, q=True, tx=True)
        if name != '':
            path = os.path.join(self.path, name + self.ext)
            if not os.path.isfile(path):
                selSet = cmds.textScrollList(self.selectionForm.scroll, q=True, ai=True)
                ss.exportFile(path, selSet)
                self.populateBrowse()
                cmds.textScrollList(self.browseForm.scroll, e=True, si=name)
                self.populatePreview()
            else:
                message('File of same name exists.', warning=True)
                self.overwriteUI()
        else:
            message('Name field is empty', warning=True)

    def cmdDelete(self, *args):
        #
        name = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        print name
        if name:
            name = name[0]
            path = os.path.join(self.path, name + self.ext)
            if os.path.isfile(path):
                os.remove(path)
                self.populateBrowse()
                self.populatePreview()
                message('Set Deleted:   ' + name, warning=True)
            else:
                message('File path does not exist ' + path, warning=True)
        else:
            message('No Set is selected in left column.', warning=True)

    def cmdOverwrite(self, args):
        new = cmds.textField(self.createSetForm.field, q=True, tx=True)
        name = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)[0]
        if name:
            # doesnt work, should use export first then delete file with old name
            os.rename(os.path.join(self.path, name + self.ext), os.path.join(self.path, new + self.ext))
            ss.exportFile(path, selSet)
            # works
            self.populateBrowse()
            cmds.textScrollList(self.browseForm.scroll, e=True, si=new)
            self.renameUI()
            self.populatePreview()
            message('Select set has been overwritten:  ' + new, warning=False)
        else:
            message('Name field is empty', warning=True)

    def cmdRename(self, *args):
        names = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        if len(names) > 1:
            message('Too many objects selected', warning=True)
        else:
            name = names[0]
            new = cmds.textField(self.createSetForm.field, q=True, tx=True)
            if new:
                path = os.path.join(self.path, new + self.ext)
                if not os.path.isfile(path):
                    os.rename(os.path.join(self.path, name + self.ext), os.path.join(self.path, new + self.ext))
                    self.populateBrowse()
                    cmds.textScrollList(self.browseForm.scroll, e=True, si=new)
                    self.renameUI()
                else:
                    self.overwriteUI()
            else:
                message('Enter a new name in the field.', maya=True, warning=True)


def job(scroll=''):
    if scroll:
        if cmds.control(scroll, ex=True):
            cmds.textScrollList(scroll, edit=True, ra=True)
            selection = cmds.ls(sl=True, fl=True)  # returns full path if same object with dif namespace exists
            if selection:
                for sel in selection:
                    if '|' in sel:
                        sel = sel.split('|')
                        sel = sel[len(sel) - 1]
                    cmds.textScrollList(scroll, edit=True, append=sel)
            else:
                pass
        else:
            pass
            # message('window missing, job should be killed')


def killJob():
    getJobs = cmds.scriptJob(lj=True)
    jobs = []
    for job in getJobs:
        if "selUI.job" in job:
            jobs.append(job.split(':')[0])
    if jobs:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)


def toggleJob(scroll=''):
    global idJ
    if idJ:
        killJob()
        cmds.scriptJob(kill=idJ, force=True)
        idJ = None
        message('SelectSet scriptJob KILLED', maya=True)
    else:
        killJob()
        idJ = cmds.scriptJob(e=["SelectionChanged", "import webrImport as web\nselUI = web.mod('selectionUI_macro_lib')\nselUI.job('%s')" % scroll])
        message('SelectSet scriptJob STARTED', maya=True)
