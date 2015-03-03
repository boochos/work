import maya.cmds as cmds
import maya.mel as mel
import os
#
import webrImport as web
# web
ui = web.mod('ui_micro_lib')
cs = web.mod('characterSet_lib')
ss = web.mod('selectionSet_lib')
clr = web.mod('colour')

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
    # TODO: add auto select set on click mode, multi select
    # https://tug.org/pracjourn/2007-4/walden/color.pdf
    # filtersOn.png filtersOff.png gotoLine.png

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
        self.keys = True
        self.rename = False
        self.conflictName = ''
        # color
        self.clr = clr.Get()
        # execute
        killJob()
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
        self.mainTopLeftForm = cmds.formLayout('mainTopLeftFormSs', w=self.columnWidth, h=195)
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
        moveUp = 20
        h = 25
        # preview
        self.previewForm = ui.Form(label='Set Members', name='selectionSets', parent=self.mainModularForm, createList=True, h=80, allowMultiSelection=True, cmdSingle=None, cmdDouble=self.cmdDisplayStyle)
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
        self.addMember = ui.Button(name='AddMember', label='Add Members', cmd=self.cmdAddMember, parent=self.selectionForm.form, moveUp=moveUp * 1, h=h)
        self.removeMember = ui.Button(name='removeMember', label='Remove Members', cmd=self.cmdRemoveMember, parent=self.previewForm.form, moveUp=moveUp * 1, h=h)
        self.deleteSet = ui.Button(name='deleteSet', label='Delete Set', cmd=self.cmdDelete, parent=self.browseForm.form, moveUp=moveUp * 1, h=h)
        #
        self.createSet = ui.Button(name='addSet', label=self.createLabel, cmd=self.cmdCreate, parent=self.createSetForm.form, moveUp=moveUp * 0)
        #
        h = 20
        self.querySets = ui.Button(name='querySets', label='Query Sets', cmd=self.cmdQuerySets, parent=self.selectionForm.form, moveUp=moveUp * 0, h=h, bgc=self.clr.greyD)
        self.namespaces = ui.Button(name='namespaces', label='Display Namespace', cmd=self.cmdDisplayStyle, parent=self.previewForm.form, moveUp=moveUp * 0, h=h, bgc=self.clr.greyD)
        self.contextual = ui.Button(name='contextual', label='Contextual Filter', cmd=self.cmdContextualSetList, parent=self.browseForm.form, moveUp=moveUp * 0, h=h, bgc=self.clr.greyD)
        # accommodate new buttons
        moveUp = moveUp + 5
        attachForm = [(self.previewForm.scroll, 'bottom', moveUp * 2)]
        cmds.formLayout(self.previewForm.form, edit=True, attachForm=attachForm)
        attachForm = [(self.selectionForm.scroll, 'bottom', moveUp * 2)]
        cmds.formLayout(self.selectionForm.form, edit=True, attachForm=attachForm)
        attachForm = [(self.browseForm.scroll, 'bottom', moveUp * 2)]
        cmds.formLayout(self.browseForm.form, edit=True, attachForm=attachForm)

        self.scroll = self.selectionForm.scroll
        toggleJob(scroll=self.scroll, k=self.keys)

    def renameUI(self):
        if not self.alternateUI:
            self.alternateUI = True
            name = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)[0]
            cmds.textField(self.createSetForm.field, e=True, text=name, ec=self.cmdRename)
            cmds.button(self.createSet.name, e=True, l=self.renameLabel, c=self.cmdRename, bgc=self.clr.blue)
            cmds.formLayout(self.mainModularForm, e=True, en=False)
            cmds.setFocus(self.createSetForm.field)
        else:
            # reset UI
            self.alternateUI = False
            cmds.textField(self.createSetForm.field, e=True, text='', ec=self.cmdCreate, aie=True)
            cmds.button(self.createSet.name, e=True, l=self.createLabel, c=self.cmdCreate, bgc=self.clr.neutral)
            cmds.formLayout(self.mainModularForm, e=True, en=True)
            cmds.textField(self.createSetForm.field, e=True, bgc=self.clr.darkbg)
            cmds.setFocus(self.browseForm.scroll)

    def overwriteUI(self):
        self.alternateUI = True
        cmds.formLayout(self.mainModularForm, e=True, en=False)
        cmds.textField(self.createSetForm.field, e=True, aie=False)
        cmds.button(self.createSet.name, e=True, l=self.overwriteLabel, c=self.cmdOverwrite, bgc=self.clr.red)

    def drawWindow(self):
        cmds.showWindow(self.win)

    def populatePathWindows(self):
        if os.name == 'nt':
            self.path = self.path.replace('/', '\\')

    def populateBrowse(self):
        # Make sure the path exists and access is permitted
        if os.path.isdir(self.path) and os.access(self.path, os.R_OK):
            # Clear the textScrollList
            cmds.textScrollList(self.browseForm.scroll, edit=True, ra=True)
            sets = self.cmdGetAllSets()
            if sets:
                cmds.textScrollList(self.browseForm.scroll, edit=True, append=sets)

    def populatePreview(self):
        cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
        browseSels = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if self.alternateUI:
            self.renameUI()
        if browseSels:
            for browseSel in browseSels:
                path = os.path.join(self.path, browseSel) + self.ext
                self.members = ss.loadDict(path)
                if self.keys:
                    keys = sorted(self.members.keys())
                else:
                    keys = sorted(self.members.values())
                for key in keys:
                    cmds.textScrollList(self.previewForm.scroll, edit=True, append=key)

    def populateSelection(self):
        cmds.textScrollList(self.selectionForm.scroll, edit=True, ra=True)
        selection = self.cmdSelectionDict()
        if selection:
            if self.keys:
                cmds.textScrollList(self.selectionForm.scroll, edit=True, append=selection.keys())
            else:
                cmds.textScrollList(self.selectionForm.scroll, edit=True, append=selection.values())
        else:
            pass

    def cmdBrowse(self, *args):
        item = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if item:
            path = os.path.join(self.path, item[0] + self.ext)
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
                path = path = os.path.join(self.path, selSet) + self.ext
                # print path
                if os.path.isfile(path):
                    selection = self.cmdSelectionDict()
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
                if selection:
                    delList = []
                    for key in self.members:
                        if key in selection:
                            delList.append(key)
                    for item in delList:
                        del self.members[item]
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
                selSet = self.cmdSelectionDict()
                ss.exportFile(path, selSet)
                self.populateBrowse()
                cmds.textScrollList(self.browseForm.scroll, e=True, si=name)
                self.populatePreview()
            else:
                message('File of same name exists.', warning=True)
                self.conflictName = name
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
                message('Set Deleted:   ' + name, warning=False)
            else:
                message('File path does not exist ' + path, warning=True)
        else:
            message('No Set is selected in left column.', warning=True)

    def cmdOverwrite(self, *args):
        new = cmds.textField(self.createSetForm.field, q=True, tx=True)
        # ensure context hasn't changed
        if new == self.conflictName:
            # delete existing file with 'new' name
            os.remove(os.path.join(self.path, new + self.ext))
            #
            if not self.rename:
                # if overwriting from create set, need new selection, export
                selection = cmds.ls(sl=True, fl=True)
                if selection:
                    selection = ss.outputDict(selection)
                ss.exportFile(filePath=os.path.join(self.path, new + self.ext), sel=selection)
                self.conflictName = ''
            else:
                # if overwriting from rename set, rename (need current name)
                os.rename(os.path.join(self.path, self.rename + self.ext), os.path.join(self.path, new + self.ext))
                self.rename = False
            #
            self.populateBrowse()
            cmds.textScrollList(self.browseForm.scroll, e=True, si=new)
            self.renameUI()
            self.populatePreview()
            message('Select set has been overwritten:  ' + new, warning=False)
        else:
            self.renameUI()  # reset ui
            cmds.textField(self.createSetForm.field, e=True, tx=new)
            self.cmdCreate()

    def cmdRename(self, *args):
        names = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        if len(names) > 1:
            message('Too many sets selected', warning=True)
        else:
            name = names[0]
            new = cmds.textField(self.createSetForm.field, q=True, tx=True)
            if new:
                path = os.path.join(self.path, new + self.ext)
                if name != new:
                    if not os.path.isfile(path):
                        os.rename(os.path.join(self.path, name + self.ext), os.path.join(self.path, new + self.ext))
                        self.populateBrowse()
                        cmds.textScrollList(self.browseForm.scroll, e=True, si=new)
                        self.renameUI()
                    else:
                        self.conflictName = new
                        self.rename = name
                        self.overwriteUI()
                else:
                    self.renameUI()
                    message('Cancelled', maya=True, warning=False)
            else:
                message('Enter a new name in the field.', maya=True, warning=True)

    def cmdDisplayStyle(self, *args):
        if self.keys:
            self.keys = False
            message('No Namespace', warning=False)
            cmds.button(self.removeMember.name, e=True, en=False)
            cmds.button(self.addMember.name, e=True, en=False)
        else:
            self.keys = True
            message('Namespace', warning=False)
            cmds.button(self.removeMember.name, e=True, en=True)
            cmds.button(self.addMember.name, e=True, en=True)
        # killjob
        toggleJob(scroll=self.scroll, k=self.keys)
        # restart job with new self.keys value
        toggleJob(scroll=self.scroll, k=self.keys)
        # refresh views
        self.populatePreview()
        self.populateSelection()

    def cmdSelectionDict(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            return ss.outputDict(sel)
        else:
            return None

    def cmdGetAllSets(self):
        files = []
        contents = os.listdir(str(self.path))
        if contents:
            # Sort the contents list based on the names in lowercase
            # Will error if 'u' objects are fed into a list
            contents.sort(key=str.lower)
            for i in contents:
                if i[0] != '.':
                    if os.path.isfile(os.path.join(self.path, i)):
                        if self.ext in i:
                            i = i.split('.')[0]
                            files.append(i)
        return files

    def cmdQuerySets(self, *args):
        '''
        find sets containing selection
        '''
        applicable = []
        sel = self.cmdSelectionDict()
        sets = self.cmdGetAllSets()
        if sel:
            for s in sel.values():
                for f in sets:
                    dic = ss.loadDict(os.path.join(self.path, f + self.ext))
                    if s in dic.values():
                        applicable.append(f)
            if applicable:
                cmds.textScrollList(self.browseForm.scroll, e=True, da=True)
                cmds.textScrollList(self.browseForm.scroll, e=True, si=applicable)
                self.populatePreview()
                # add line to select objects in middle column
            else:
                message('No sets were found for current selection')
        else:
            message('Select an object to find sets.')
        # return applicable

    def cmdContextualSetList(self, *args):
        '''
        list only sets that apply to current scene
        '''
        pass


def job(scroll='', k=False):
    import webrImport as web
    ss = web.mod('selectionSet_lib')
    # print '\n  run job  \n'
    #
    add = []
    if scroll:
        if cmds.control(scroll, ex=True):
            cmds.textScrollList(scroll, edit=True, ra=True)
            selection = cmds.ls(sl=True, fl=True)  # returns full path if same object with dif namespace existskeys
            if selection:
                for sel in selection:
                    if '|' in sel:
                        sel = sel.split('|')
                        sel = sel[len(sel) - 1]
                        add.append(sel)
                    else:
                        add.append(sel)
                add = ss.outputDict(add)
                # keys or values
                if k:
                    # add to list
                    cmds.textScrollList(scroll, edit=True, append=sorted(add.keys()))
                else:
                    # add to list
                    cmds.textScrollList(scroll, edit=True, append=sorted(add.values()))
            else:
                pass
                # message('no selection', warning=True)
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


def toggleJob(scroll='', k=False):
    global idJ
    if idJ:
        killJob()
        # cmds.scriptJob(kill=idJ, force=True)
        idJ = None
        # message('SelectSet scriptJob KILLED', maya=True)
    else:
        killJob()
        idJ = cmds.scriptJob(e=["SelectionChanged", "import webrImport as web\nselUI = web.mod('selectionUI_macro_lib')\nselUI.job('%s', %s)" % (scroll, k)])
        # message('SelectSet scriptJob STARTED', maya=True)
