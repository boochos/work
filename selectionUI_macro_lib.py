import maya.cmds  as cmds
import os
import os, sys, sys_lib, fnmatch
from subprocess import call
import subprocess
import ui_micro_lib as ui
import characterSet_lib as cs
import selectionSet_lib as ss
import maya.mel as mel
import time

reload(ui)
reload(ss)

id = None
scroll = None

class CSUI(object):
    '''
    Build CharacterSet UI
    '''
    def __init__(self, path=os.path.expanduser('~') + '/maya/selectionSets', filters=['.sel', '.txt', '.mb', '.ma', '*.*'], columnWidth=200):
        # external
        self.path = path
        self.filters = filters
        self.columnWidth = columnWidth
        # internal
        self.windowName = 'SelectionSetManager'
        self.shortcutsFile = '/var/tmp/custom_info.txt'
        self.shortcuts = []
        self.actionLabel = 'create'
        self.dirStr = ' / '
        self.par = ''
        self.mem = ''
        # execute
        self.populatePathWindows()
        self.cleanUI()
        self.browser()
        self.drawWindow()
        self.populateShortcuts()
        self.populateBrowse()
        self.populateSelection()
        toggleJob()

    def message(self, what='', maya=True, ui=True, *args):
        if what != '':
            if '\\' in what:
                what = what.replace('\\', '/')
            if maya == True:
                mel.eval('print \"' + '-- ' + what + ' --' + '\";')
        else:
            print ''
        if ui == True:
            cmds.text(self.messageForm.heading, edit=True, l='   ' + what + '   ')
            # cmds.form(self.messageForm.form, edit=True, )

    def cleanUI(self, *args):
        try:
            cmds.deleteUI(self.windowName)
            toggleJob()
        except:
            pass

    def browser(self):
        self.win = cmds.window(self.windowName, w=700)
        # main form
        self.mainForm = cmds.formLayout('mainFormSs')
        # bottom form
        cmds.setParent(self.mainForm)
        self.mainBottomForm = cmds.formLayout('mainBottomFormSs', h=100)
        attachForm = [(self.mainBottomForm, 'left', 5), (self.mainBottomForm, 'bottom', 15), (self.mainBottomForm, 'right', 5)]
        cmds.formLayout(self.mainForm, edit=True, attachForm=attachForm)
        # action
        self.actionForm = ui.Action('actionSs', parent=self.mainBottomForm, filters=self.filters, cmdCancel=self.cleanUI, cmdAction=self.cmdAction, cmdOpen=self.cmdOpen, label=self.actionLabel)
        attachForm = [(self.actionForm.form, 'left', 0), (self.actionForm.form, 'bottom', 0), (self.actionForm.form, 'right', 0)]
        cmds.formLayout(self.mainBottomForm, edit=True, attachForm=attachForm)
        # message
        self.messageForm = ui.Form(label='', name='messageSs', parent=self.mainBottomForm)
        cmds.formLayout(self.messageForm.form, edit=True, h=20)
        cmds.text(self.messageForm.heading, edit=True, al='right')
        attachForm = [(self.messageForm.form, 'left', 0), (self.messageForm.form, 'right', 2), (self.messageForm.form, 'bottom', self.actionForm.heightForm)]
        cmds.formLayout(self.mainBottomForm, edit=True, attachForm=attachForm)
        # path
        self.pathForm = ui.Form(text=self.path, label='Path', name='pathSs', parent=self.mainBottomForm, createField=True)
        attachForm = [(self.pathForm.form, 'left', 0), (self.pathForm.form, 'right', 0), (self.pathForm.form, 'bottom', self.actionForm.heightForm + self.messageForm.heightForm)]
        cmds.formLayout(self.mainBottomForm, edit=True, attachForm=attachForm)
        # edit form height
        h = cmds.formLayout(self.actionForm.form, q=True, h=True) + cmds.formLayout(self.pathForm.form, q=True, h=True) + cmds.formLayout(self.messageForm.form, q=True, h=True)
        cmds.formLayout(self.mainBottomForm, edit=True, h=h)
        # left form
        cmds.setParent(self.mainForm)
        self.mainTopLeftForm = cmds.formLayout('mainTopLeftFormSs', w=self.columnWidth, h=80)
        attachForm = [(self.mainTopLeftForm, 'left', 5), (self.mainTopLeftForm, 'top', 5), (self.mainTopLeftForm, 'bottom', 5)]
        attachControl = [(self.mainTopLeftForm, 'bottom', 5, self.mainBottomForm)]
        cmds.formLayout(self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl)
        # custom paths
        self.shortcutsForm = ui.Form(label='Shortcuts', name='customPathsSs', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdShortcuts)
        cmds.formLayout(self.shortcutsForm.form, edit=True, h=60)
        attachForm = [(self.shortcutsForm.form, 'left', 0), (self.shortcutsForm.form, 'top', 0), (self.shortcutsForm.form, 'right', 0)]
        cmds.formLayout(self.mainTopLeftForm, edit=True, attachForm=attachForm)
        # browse paths
        self.browseForm = ui.Form(label='Browse', name='browseSs', parent=self.mainTopLeftForm, createList=True, cmdSingle=self.cmdBrowse, h=80)
        attachForm = [(self.browseForm.form, 'left', 0), (self.browseForm.form, 'bottom', 0), (self.browseForm.form, 'right', 0)]
        attachControl = [(self.browseForm.form, 'top', 0, self.shortcutsForm.form)]
        cmds.formLayout(self.mainTopLeftForm, edit=True, attachForm=attachForm, attachControl=attachControl)
        # modular form
        cmds.setParent(self.mainForm)
        self.mainModularForm = cmds.formLayout('mainTopRightFormSs', w=150, h=80)
        attachForm = [(self.mainModularForm, 'top', 5), (self.mainModularForm, 'right', 5)]
        attachControl = [(self.mainModularForm, 'left', 20, self.mainTopLeftForm), (self.mainModularForm, 'bottom', 5, self.mainBottomForm)]
        cmds.formLayout(self.mainForm, edit=True, attachForm=attachForm, attachControl=attachControl)

    def drawWindow(self):
        # fill mainModularForm
        self.exportCS(self.mainModularForm)
        # launch window
        cmds.showWindow(self.win)

    def exportCS(self, *args):
        moveUp = 23
        # in scene character sets, middle attach
        self.previewForm = ui.Form(label='Selection set members in file', name='selectionSets', parent=self.mainModularForm, createList=True, h=80, allowMultiSelection=True)
        cmds.formLayout(self.previewForm.form, edit=True, w=200)
        attachForm = [(self.previewForm.form, 'left', 0), (self.previewForm.form, 'top', 0), (self.previewForm.form, 'bottom', 0)]
        # attachControl     = [(self.previewForm.form,'right',5, self.selectionForm.form)]
        cmds.formLayout(self.mainModularForm, edit=True, attachForm=attachForm)
        # character set members, right attach
        self.selectionForm = ui.Form(label='In Scene Selection', name='selection', parent=self.mainModularForm, createList=True, h=80, allowMultiSelection=True)
        cmds.formLayout(self.selectionForm.form, edit=True, w=1)
        attachForm = [(self.selectionForm.form, 'top', 0), (self.selectionForm.form, 'right', 0), (self.selectionForm.form, 'bottom', 0)]
        attachControl = [(self.selectionForm.form, 'left', 5, self.previewForm.form)]
        cmds.formLayout(self.mainModularForm, edit=True, attachForm=attachForm, attachControl=attachControl)
        # buttons
        # addMaster          = ui.Button(name='addMaster', label='Create Master -- Create directory', cmd=self.cmdAddMaster, parent=self.selectionForm.form, moveUp=moveUp*0)
        # addLimbMaster      = ui.Button(name='addLimbMaster', label='Create Set -- Create file', cmd=self.cmdAddSet, parent=self.selectionForm.form, moveUp=moveUp*1)
        addLimbMember = ui.Button(name='addMember', label='Add Member -- Edit file', cmd=self.cmdAddMember, parent=self.selectionForm.form, moveUp=moveUp * 0)
        removeMember = ui.Button(name='removeMember', label='Remove Member -- Edit file', cmd=self.cmdRemoveMember, parent=self.previewForm.form, moveUp=moveUp * 0)
        # scrolledit
        attachForm = [(self.previewForm.scroll, 'bottom', moveUp * 1)]
        cmds.formLayout(self.previewForm.form, edit=True, attachForm=attachForm)
        attachForm = [(self.selectionForm.scroll, 'bottom', moveUp * 1)]
        cmds.formLayout(self.selectionForm.form, edit=True, attachForm=attachForm)

        global scroll
        scroll = self.selectionForm.scroll

    def format(self, line=''):
        if 'ParentInfo' in line:
            return self.par + line
        else:
            return self.mem + line

    def buildDict(self):
        rp = cmds.textField(self.replaceForm.field, q=True, tx=True)
        rp = rp.replace(' ', '')
        dic = {}
        if rp:
            try:
                if ',' in rp:
                    rp = rp.split(',')
                    for d in rp:
                        dic[d.split(':')[0]] = d.split(':')[1]
                    return dic
                else:
                    dic[rp.split(':')[0]] = rp.split(':')[1]
                    return dic
            except:
                self.message("  FAIL  --  Replace string failed. --  Use colons,commas  --    ie.    search1:replace1,search2:replace2")
        else:
            return {None:None}

    def populatePathWindows(self):
        if os.name == 'nt':
            self.path = self.path.replace('/', '\\')

    def populatePath(self):
        self.populatePathWindows()
        cmds.textField(self.pathForm.field, edit=True, text=self.path)

    def populateShortcuts(self):
        if not os.path.exists(self.shortcutsFile):
            self.shortcuts.append(['Home', os.environ['HOME']])
            # self.shortcuts.append(['Desktop', os.path.join(os.environ['USERPROFILE'],'Desktop')])
            self.shortcuts.append(['Selection Sets', os.path.join(os.environ['HOME'], ss.defaultPath())])
            cs.createDefaultPath()
        else:
            _file = open(self.shortcutsFile, 'r')
            lines = _file.readlines()
            for l in lines:
                line = eval(l.strip('\n'))
                self.shortcuts.append([line[0], line[1]])
        for path in self.shortcuts:
            cmds.textScrollList(self.shortcutsForm.scroll, edit=True, append=path[0])

    def populateBrowse(self):
        # Make sure the path exists and access is permitted
        if os.path.isdir(self.path) and os.access(self.path, os.R_OK):
            # Clear the textScrollList
            cmds.textScrollList(self.browseForm.scroll, edit=True, ra=True)
            # Append the '..'(move up a director) as the first item
            cmds.textScrollList(self.browseForm.scroll, edit=True, append='..')
            # Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            # list the files in the path
            files = os.listdir(str(self.path))
            if len(files) > 0:
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
                    # show the files based on the current filter
                    if fnmatch.fnmatch(i, '*' + cmds.optionMenuGrp(self.actionForm.opt, query=True, v=True)):
                        cmds.textScrollList(self.browseForm.scroll, edit=True, append=i)

    def populatePreview(self):
        cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
        path = os.path.join(self.path, cmds.textScrollList(self.browseForm.scroll, query=True, si=True)[0])
        for line in open(path):
            cmds.textScrollList(self.previewForm.scroll, edit=True, append=self.format(line).strip('\n'))

    def populateSelection(self):
        cmds.textScrollList(self.selectionForm.scroll, edit=True, ra=True)
        selection = cmds.ls(sl=True, fl=True)
        if len(selection) > 0:
            for sel in selection:
                cmds.textScrollList(self.selectionForm.scroll, edit=True, append=sel)
        else:
            cmds.textScrollList(self.selectionForm.scroll, edit=True, append='Nothing Selected')

    def cmdShortcuts(self, *args):
        tsl = cmds.textScrollList
        tmp = tsl(self.shortcutsForm.scroll, query=True, sii=True)
        if tmp != None :
            idx = tmp[0]
            self.path = self.shortcuts[idx - 1][1]
            self.populatePath()
            self.populateBrowse()

    def cmdBrowse(self, *args):
        tmp = cmds.textScrollList(self.browseForm.scroll, query=True, si=True)
        if tmp != None:
            item = tmp[0]
            # find if the current item is a directory
            if item[:len(self.dirStr)] == self.dirStr:
                item = item[len(self.dirStr):]
                path = os.path.join(self.path, item)
                if os.path.exists(path):
                    self.path = str(path)
                    if os.access(path, os.R_OK):
                        self.populatePath()
                        cmds.textField(self.pathForm.field, edit=True, tx=self.path)
                        try:
                            cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
                        except:
                            pass
                        self.populateBrowse()
                    else:
                        print 'no access'
            elif item == '..':
                path = os.path.split(self.path)[0]
                # go up a directory
                if os.path.exists(path):
                    if os.access(path, os.R_OK):
                        self.path = path
                        self.populatePath()
                        cmds.textField(self.pathForm.field, edit=True, tx=self.path)
                        try:
                            cmds.textScrollList(self.previewForm.scroll, edit=True, ra=True)
                        except:
                            pass
                        self.populateBrowse()
            else:
                # this is a file
                path = os.path.join(self.path, item)
                if os.path.isfile(path):
                    self.populatePath()
                    cmds.textField(self.pathForm.field, edit=True, tx=path)
                    try:
                        self.populatePreview()
                    except:
                        pass
        else:
            print 'here'

    def cmdAddMaster(self, *args):
        masters = cmds.textScrollList(self.selectionForm.scroll, q=True, si=True)
        if masters:
            path = ss.defaultKeyPath()
            for master in masters:
                master = master.split(':')[1]
                path = path + '/' + master
                if not os.path.isdir(path):
                    os.mkdir(path)
                self.path = path
                self.populatePath()
                self.populateBrowse()
                # cmds.textScrollList(self.selectionForm.scroll, si=master)
        else:
            self.message('Nothing highlighted')

    def cmdAddSet(self, *args):
        # this needs to account for user fed file name into path field
        hi = cmds.textScrollList(self.selectionForm.scroll, q=True, si=True)
        if hi:
            if len(hi) == 1:
                hi = hi[0]
                if ':' in hi:
                    hi = hi.split(':')[1] + '.sel'
                path = os.path.join(self.path, hi)
                if not os.path.isdir(path):
                    outFile = open(path, 'w')
                    # writeFile(sel, outFile = outFile)
                    outFile.close()
                    # ss.exportFile(path)
                    self.populateBrowse()
                    cmds.textScrollList(self.browseForm.scroll, si=str(hi))
                    self.message('Selection exported to:   ' + path)
                else:
                    self.message('Add file name to path field. Action aborted.')
                # browse to new set
                # select set in scroll
            else:
                self.message('Highlight one object create a Set Master')
        else:
            self.message('Nothing highlighted')

    def cmdAddMember(self, *args):
        # confirm set is selected
        # collect highlighted in selection
        # collect set list
        # combine and save to file
        path = cmds.textField(self.pathForm.field, q=True, tx=True)
        print path
        if os.path.isfile(path):
            members = cmds.textScrollList(self.previewForm.scroll, q=True, ai=True)
            selection = cmds.textScrollList(self.selectionForm.scroll, q=True, si=True)
            if not members:
                members = []
            if selection:
                for sel in selection:
                    if ':' in sel:
                        sel = sel.split(':')[1]
                    if sel not in members:
                        members.append(sel)
                ss.exportFile(path, sel=members)
                self.populateBrowse()
            else:
                self.message('Nothing highlighted in right column.')
        else:
            self.message('No file selected in left column.')

    def cmdRemoveMember(self, *args):
        members = cmds.textScrollList(self.previewForm.scroll, q=True, ai=True)
        if members:
            selection = cmds.textScrollList(self.previewForm.scroll, q=True, si=True)
            if selection:
                for sel in selection:
                    members.remove(sel)
                fl = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)[0]
                path = os.path.join(self.path, fl)
                print path
                if members:
                    ss.exportFile(path, sel=members)
                else:
                    outFile = open(path, 'w')
                    self.populatePreview()
                self.populateBrowse()
                self.populatePath()
                fl = [str(fl)]
                # cmds.textScrollList(self.browseForm.scroll, si=fl)
            else:
                self.message('Nothing highlighted in middle column.')
        else:
            self.message('No members to remove from middle column.')

    def cmdSets(self, *args):
        print 'pass'
        # self.populateMembers()

    def cmdExport(self, *args):
        # this needs to account for user fed file name into path field
        set = cmds.textScrollList(self.selectionForm.scroll, q=True, ai=True)
        # file = cmds.textScrollList(self.browseForm.scroll, q=True, si=True)
        path = cmds.textField(self.pathForm.field, q=True, tx=True)
        if set:
            if not os.path.isdir(path):
                ss.exportFile(path, set)
                self.populateBrowse()
                self.message('Selection exported to:   ' + path)
            else:
                self.message('Add file name to path field. Action aborted.')
        else:
            self.message('Select a character Set in the middle column.')

    def cmdAction(self, *args):
        # print self.path
        self.cmdExport()

    def cmdFilter(self, *args):
        pass

    def cmdOpen(self, *args):
        if os.name == 'nt':
            print self.path
            subprocess.Popen(r'explorer /open, "C:\Users\Slabster & Vicster\Documents\maya\selectionSets"')
        else:
            self.message('Close file window to regain control over MAYA.')
            app = "nautilus"
            call([app, self.path])

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def job():
    global scroll
    if cmds.control(scroll, ex=True):
        cmds.textScrollList(scroll, edit=True, ra=True)
        selection = cmds.ls(sl=True, fl=True)
        if len(selection) > 0:
            for sel in selection:
                cmds.textScrollList(scroll, edit=True, append=sel)
        else:
            cmds.textScrollList(scroll, edit=True, append='Nothing Selected')
    else:
        pass
        # message('window missing')

def killJob():
    getJobs = cmds.scriptJob(lj=True)
    jobs = []
    for job in getJobs:
        if "selUI.job()" in job:
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)

def toggleJob():
    global id
    if id:
        killJob()
        cmds.scriptJob(kill=id, force=True)
        id = None
        message('SelectSet scriptJob KILLED', maya=True)
    else:
        killJob()
        id = cmds.scriptJob(e=["SelectionChanged", "import selectionUI_macro_lib as selUI\nselUI.job()"])
        message('SelectSet scriptJob STARTED', maya=True)

