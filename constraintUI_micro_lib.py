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
        self.actionButton2  = name + '_actionButton2'
        self.actionButton3  = name + '_actionButton3'
        self.actionButton4  = name + '_actionButton4'
        self.actionButton5  = name + '_actionButton5'
        self.actionButton6  = name + '_actionButton6'
        self.actionField1   = name + '_actionField1'
        self.actionButton7  = name + '_actionButton7'
        self.c1            = ''
        self.c2            = ''
        self.c3            = ''
        self.c4            = ''
        self.c5            = ''
        self.c6            = ''
        self.c7            = ''
        self.c8            = ''
        self.c9            = ''
        self.c10           = ''
        self.c11           = ''
        self.c12           = ''
        self.s0            = ''
        self.s1            = ''
        self.s2            = ''
        self.s3            = ''
        self.s4            = ''
        self.s5            = ''
        self.opt1          = ''
        self.col1          = ''
        self.r1            = ''
        self.r2            = ''
        self.label         = label
        self.cmdAction     = cmdAction
        self.ui            = [self.form, self.opt,self.actionButton1, self.actionButton2, self.actionButton3, self.actionButton4, self.actionButton5,            self.actionButton6, self.actionField1, self.actionButton7, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, self.c9, self.c10, self.c11, self.c12, self.s0, self.s1, self.s2, self.s3, self.s4, self.s5, self.opt1, self.col1, self.r1, self.r2 ]
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
        #self.s0 = cmds.separator( height=self.sepH, style=self.sepStl )
        #bake
        self.actionButton1 = cmds.button(self.actionButton1, label='Bake', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.c1 = cmds.checkBox( label='On Existing Frames', v=True )
        self.c2 = cmds.checkBox( label='Remove Constraint', v=True )
        self.c3 = cmds.checkBox( label='Timeline Range' )
        self.c4 = cmds.checkBox( label='Simulation', v=True )
        self.actionButton3 = cmds.button(self.actionButton3, label='Bake To Locator', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.c6 = cmds.checkBox( label='On Existing Frames', v=True )
        self.c7 = cmds.checkBox( label='Translation', v=True )
        self.c8 = cmds.checkBox( label='Rotation', v=True )
        self.c12 = cmds.checkBox( label='Simulation', v=True )
        #rotate order
        self.actionButton7 = cmds.button(self.actionButton7, label='Bake Rotate Order', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.opt1 = cmds.optionMenuGrp(label='Rotate Order: ', w=self.w, cw=[1, self.w])
        ro = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        for o in ro:
            cmds.menuItem(o)
        self.s1 = cmds.separator( height=self.sepH, style=self.sepStl )
        #match things
        self.actionButton4 = cmds.button(self.actionButton4, label='Match Keys', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.actionButton6 = cmds.button(self.actionButton6, label='Match Transforms', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        #random
        self.s5 = cmds.separator( height=self.sepH, style=self.sepStl )
        self.actionButton2 = cmds.button(self.actionButton2, label='Place Locator', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.c5 = cmds.checkBox( label='Constrain to' )
        self.col1 = cmds.radioCollection()
        self.r1 = cmds.radioButton( label='  selection', sl=1 )
        self.r2 = cmds.radioButton( label='  reverse' )
        #self.s2 = cmds.separator( height=self.sepH, style=self.sepStl )
        #constrain
        self.actionButton5 = cmds.button(self.actionButton5, label='Parent Constraint', c=self.cmdAction, bgc=[0.5,0.5,0.5])
        self.c9 = cmds.checkBox( label='Offset', v=True )
        self.c10 = cmds.checkBox( label='Translation', v=True )
        self.c11 = cmds.checkBox( label='Rotation', v=True )
        #self.s3 = cmds.separator( height=self.sepH, style=self.sepStl )
        #sticky ,...
