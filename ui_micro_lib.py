from __future__ import with_statement
import maya.cmds as cmds
import maya.mel as mel


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class Form(object):
    # builds text field or list with heading

    def __init__(self, text='', label='', name='', parent=None, h=15, w=15, createField=False, createList=False, allowMultiSelection=False, cmdSingle='print \'single click\'', cmdDouble='print \'double click\''):
        self.parent = parent
        self.text = text
        self.label = label
        self.form = name + '_form'
        self.heading = name + '_heading'
        self.field = name + '_field'
        self.scroll = name + '_scroll'
        self.ams = allowMultiSelection
        self.cmdSingle = cmdSingle
        self.cmdDouble = cmdDouble
        self.ui = [self.form, self.heading, self.field]
        self.m = 0
        self.h = h
        self.w = w
        self.heightHeading = 15
        self.heightField = 20
        self.heightForm = self.heightHeading + self.heightField
        self.cleanUI()
        self.buildForm()
        self.buildHeading()
        if createField:
            self.buildField()
        if createList:
            self.buildList()

    def cleanUI(self):
        cmds.setParent(self.parent)
        for ui in self.ui:
            if cmds.control(ui, q=True, exists=True):
                cmds.deleteUI(ui)

    def buildForm(self):
        cmds.setParent(self.parent)
        f = cmds.formLayout(self.form, h=self.heightForm)

    def buildHeading(self):
        self.heading = cmds.text(self.heading, l=self.label, fn='obliqueLabelFont', al='left', h=15, w=10)
        attachForm = [(self.heading, 'top', 0), (self.heading, 'left', 3), (self.heading, 'right', 0)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm)

    def buildField(self):
        self.field = cmds.textField(self.field, tx=self.text, h=20)
        attachForm = [(self.field, 'left', 0), (self.field, 'right', 0)]
        attachControl = [(self.field, 'top', 0, self.heading)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)

    def buildList(self):
        if self.cmdSingle:
            self.scroll = cmds.textScrollList(self.scroll, sc=self.cmdSingle, allowMultiSelection=self.ams, dcc=self.cmdDouble, fn='plainLabelFont', h=10, w=10)
        else:
            self.scroll = cmds.textScrollList(self.scroll, allowMultiSelection=self.ams, dcc=self.cmdDouble, fn='plainLabelFont', h=10, w=10)
        attachForm = [(self.scroll, 'bottom', 0), (self.scroll, 'left', 0), (self.scroll, 'right', 0)]
        attachControl = [(self.scroll, 'top', 0, self.heading)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)


class Button(object):

    def __init__(self, name='', label='', cmd='', parent='', moveUp=20, h=20, bgc=None):
        self.name = name
        self.label = label
        self.cmd = cmd
        self.parent = parent
        self.moveUp = moveUp
        self.h = h
        self.bgc = bgc
        self.new()

    def new(self):
        cmds.setParent(self.parent)
        self.name = cmds.button(self.name, label=self.label, c=self.cmd, h=self.h)
        if self.bgc:
            cmds.button(self.name, e=True, bgc=self.bgc)
        attachForm = [(self.name, 'bottom', self.moveUp), (self.name, 'right', 0), (self.name, 'left', 0)]
        cmds.formLayout(self.parent, edit=True, attachForm=attachForm)


class Action(object):
    # builds row of buttons for bottom of window
    # removed from variables: cmdFlush='print \'None\'', cmdUnflush='print \'None\'',

    def __init__(self, name, parent=None, h=15, w=80,
                 cmdAction='', cmdCancel='', cmdOpen='', cmdFilter='print \'None\'',
                 filters=['.chr', '.txt', '.mb', '.ma', '*.*'], label=''):
        self.parent = parent
        self.filters = filters
        self.illegalChar = ['.', '*']
        self.form = name + '_form'
        self.opt = name + '_opt'
        self.cancelButton = name + '_cancelButton'
        self.actionButton = name + '_actionButton'
        self.openButton = name + '_openButton'
        self.actionMessage = name + '_actionMessage'
        self.label = label
        self.cmdFilter = cmdFilter
        self.cmdCancel = cmdCancel
        self.cmdAction = cmdAction
        self.cmdOpen = cmdOpen
        self.ui = [self.form, self.opt, self.cancelButton, self.actionButton]
        self.h = h
        self.w = w
        self.heightForm = 30
        self.cleanUI()
        self.buildForm()
        self.buildFilter()
        self.buildAction()
        self.buildCancel()
        self.buildOpen()

    def cleanUI(self):
        cmds.setParent(self.parent)
        for ui in self.ui:
            if cmds.control(ui, q=True, exists=True):
                cmds.deleteUI(ui)

    def buildForm(self):
        cmds.setParent(self.parent)
        self.form = cmds.formLayout(self.form, h=self.heightForm)

    def buildFilter(self):
        self.opt = cmds.optionMenuGrp(self.opt, label='Filter:', cc=self.cmdFilter, cw2=[40, 75], height=20)
        for i, item in enumerate(self.filters):
            itm = (item + '_%02d_menuItem' % i)
            cmds.menuItem(itm, l=item)
        attachForm = [(self.opt, 'bottom', 5), (self.opt, 'left', 0)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm)

    def buildAction(self):
        self.actionButton = cmds.button(self.actionButton, label=self.label.upper(), c=self.cmdAction)
        attachForm = [(self.actionButton, 'bottom', 0), (self.actionButton, 'right', 0)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm)

    def buildCancel(self):
        self.cancelButton = cmds.button(self.cancelButton, label='CLOSE', c=self.cmdCancel)
        attachForm = [(self.cancelButton, 'bottom', 0)]
        attachControl = [(self.cancelButton, 'right', 5, self.actionButton)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)

    def buildOpen(self):
        self.openButton = cmds.button(self.openButton, label='  Open Folder  ', c=self.cmdOpen)
        attachForm = [(self.openButton, 'bottom', 0)]
        attachControl = [(self.openButton, 'right', 50, self.cancelButton)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)

    def buildFlush(self):
        self.flushButton = cmds.button(self.flushButton, label='  Flush Sets  ', c=self.cmdFlush)
        attachForm = [(self.flushButton, 'bottom', 0)]
        attachControl = [(self.flushButton, 'right', 5, self.openButton)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)

    def buildUnflush(self):
        self.unflushButton = cmds.button(self.unflushButton, label='  Un-flush Sets  ', c=self.cmdUnflush)
        attachForm = [(self.unflushButton, 'bottom', 0)]
        attachControl = [(self.unflushButton, 'right', 5, self.flushButton)]
        cmds.formLayout(self.form, edit=True, attachForm=attachForm, attachControl=attachControl)
