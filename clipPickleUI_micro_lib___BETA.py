#from __future__ import with_statement
#import os, sys, sys_lib, fnmatch
import maya.cmds  as cmds
import maya.mel   as mel
#import pymel.core as pm
#import characterSet_lib as cs
#import ast
#reload(cs)
#

def message(what=''):
    mm.eval('print \"' + '-- ' + what + ' --' + '\";')
    #print "\n"

class Action(object):
    #builds row of buttons for bottom of window
    def __init__(self, name, parent=None, h=15, w=80, cmdAction='', label=''):
        self.parent        = parent
        self.illegalChar   = ['.', '*']
        self.form          = name + '_form'
        self.column        = name + '_column'
        self.opt           = name + '_opt'
        self.actionButton1  = name + '_actionButton1'

        self.c1            = ''

        self.s1            = ''

        self.opt1          = ''
        self.col1          = ''
        self.r1            = ''
        self.r2            = ''
        self.label         = label
        self.cmdAction     = cmdAction
        self.ui            = [self.form, self.opt,self.actionButton1, self.c1, self.s1, self.opt1, self.col1, self.r1, self.r2 ]
        self.h             = h
        self.w             = w
        self.heightForm    = 30
        self.sepH          = 15
        self.sepStl        = 'in'
        #self.cleanUI()
        self.buildColumn()
        self.buildAction()

    def cleanUI(self):
        cmds.setParent(self.parent)
        for ui in self.ui:
            if cmds.control(ui, q=True, exists=True):
                cmds.deleteUI(ui)

    def buildColumn(self):
        cmds.setParent(self.parent)
        self.column = cmds.columnLayout( adjustableColumn=True )

    def buildAction(self):
        #colors
        grey = [0.5, 0.5, 0.5]
        greyD = [0.2, 0.2, 0.2]
        red = [0.5, 0.2, 0.2]
        redD = [0.4, 0.2, 0.2]
        blue = [0.2, 0.3, 0.5]
        green = [0.2, 0.5, 0.0]
        teal = [0.0,0.5,0.5]
        purple = [0.35, 0.35, 0.5]
        purple2 = [0.28, 0.28, 0.39]
        orange = [0.5, 0.35, 0.0]
        #ann
        existing = 'Will only bake on existing frames.\nTurn off to get a key on every frame.'
        time = 'Force timeline range to be baked.\nOtherwise range is gathered in this priority:\n-Use selected range\n-Use range from animation, if any\n-Use range from timeline.'
        simu = 'Step through every frame.'

        self.actionField1 = cmds.textField(self.actionField1, tx=5.0)



        #bake
        self.actionButton1 = cmds.button(self.actionButton1, label='Bake', c=self.cmdAction, bgc=red,
        ann='Bake selected objects if they are connected to a pairBlend node or constraint.')

        self.c1 = cmds.checkBox( label='Remove Constraint', v=True,
        ann='Remove constraint after baking.\nIf off, anim curves are updated and the constraint remains connected.' )

        self.opt1 = cmds.optionMenuGrp(label='Rotate Order: ', w=self.w, cw=[1, self.w],
        ann='Select rotate order to bake to.')
        ro = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        for o in ro:
            cmds.menuItem(o)

        self.s1 = cmds.separator( height=self.sepH, style=self.sepStl )

        #place loc, constain
        self.actionButton2 = cmds.button(self.actionButton2, label='Place LOC', c=self.cmdAction, bgc=blue)
        self.c5 = cmds.checkBox( label='Constrain to', v=True, ann='Use constraint option.' )
        self.col1 = cmds.radioCollection()
        self.r1 = cmds.radioButton( label='  selection', sl=1, ann='Constrain new locator to selection.' )
        self.r2 = cmds.radioButton( label='  reverse', ann='Constrain selection to new locator.' )
        self.c13 = cmds.checkBox( label='Match Keys', v=True, ann='Will add keys on the same frames as source object.' )

        #distribute keys
        self.actionButton16 = cmds.button(self.actionButton16, label='Distribute Keys', c=self.cmdAction, bgc=grey)
        self.actionField1 = cmds.textField(self.actionField1, tx=5.0)
        ann='Destructive Mode. Removes keys that dont fall on the frame itteration.'
        self.c14 = cmds.checkBox( label='Destructive', v=True, ann=ann )