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
        self.actionButton8  = name + '_actionButton8'
        self.actionButton9  = name + '_actionButton9'
        self.actionButton10  = name + '_actionButton10'
        self.actionButton11  = name + '_actionButton11'
        self.actionButton12  = name + '_actionButton12'
        self.actionButton13  = name + '_actionButton13'
        self.actionButton14  = name + '_actionButton14'
        self.actionButton15  = name + '_actionButton15'
        self.actionButton16  = name + '_actionButton16'
        self.c1            = ''
        self.c2            = ''
        self.c3            = ''
        self.c4            = ''
        self.c5            = ''
        #self.c6            = ''
        self.c7            = ''
        self.c8            = ''
        self.c9            = ''
        self.c10           = ''
        self.c11           = ''
        self.c12           = ''
        self.c13           = ''
        self.s0            = ''
        self.s1            = ''
        self.s2            = ''
        self.s3            = ''
        self.s4            = ''
        self.s5            = ''
        self.s6            = ''
        self.s7            = ''
        self.opt1          = ''
        self.col1          = ''
        self.r1            = ''
        self.r2            = ''
        self.label         = label
        self.cmdAction     = cmdAction
        self.ui            = [self.form, self.opt,self.actionButton1, self.actionButton2, self.actionButton3, self.actionButton4, self.actionButton5,            self.actionButton6, self.actionField1, self.actionButton7, self.actionButton8, self.actionButton9,self.actionButton10, self.actionButton11, self.actionButton12, self.actionButton13, self.actionButton14, self.actionButton15, self.actionButton16, self.c1, self.c2, self.c3, self.c4, self.c5, self.c7, self.c8, self.c9, self.c10, self.c11, self.c12, self.c13, self.s0, self.s1, self.s2, self.s3, self.s4, self.s5, self.s6, self.s7, self.opt1, self.col1, self.r1, self.r2 ]
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
        existing = 'Will only bake on existing frames.\nTurn off to get a key on every frame.'
        time = 'Force timeline range to be baked.\nOtherwise range is gathered in this priority:\n-Use selected range\n-Use range from animation, if any\n-Use range from timeline.'
        simu = 'Step through every frame.'
        #self.s0 = cmds.separator( height=self.sepH, style=self.sepStl )
        #bake
        self.actionButton1 = cmds.button(self.actionButton1, label='Bake', c=self.cmdAction, bgc=red,
        ann='Bake selected objects if they are connected to a pairBlend node or constraint.')
        #self.c1 = cmds.checkBox( label='On Existing Frames', v=True, ann=existing )
        self.c2 = cmds.checkBox( label='Remove Constraint', v=True,
        ann='Remove constraint after baking.\nIf off, anim curves are updated and the constraint remains connected.' )
        self.c3 = cmds.checkBox( label='Timeline Range', ann=time )
        self.c4 = cmds.checkBox( label='On All Frames', v=False, ann=simu )
        #rotate order
        self.actionButton7 = cmds.button(self.actionButton7, label='Bake Rotate Order', c=self.cmdAction, bgc=red,
        ann='Change rotate order of selected Object.')
        self.opt1 = cmds.optionMenuGrp(label='Rotate Order: ', w=self.w, cw=[1, self.w],
        ann='Select rotate order to bake to.')
        ro = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        for o in ro:
            cmds.menuItem(o)
        self.s1 = cmds.separator( height=self.sepH, style=self.sepStl )
        #bake to locator
        self.actionButton3 = cmds.button(self.actionButton3, label='Bake To LOC', c=self.cmdAction, bgc=redD,
        ann='Bake all selected objects to a locator in world space.')
        #self.c6 = cmds.checkBox( label='On Existing Frames', v=True, ann=existing )
        self.c7 = cmds.checkBox( label='Translation', v=True, ann='Only bake translation attributes.\nRotation will be constrained to follow object.' )
        self.c8 = cmds.checkBox( label='Rotation', v=True, ann='Only bake rotation attributes.\nTranslation will be constrained to follow object.'  )
        self.c12 = cmds.checkBox( label='On All Frames', v=False, ann=simu )
        self.s2 = cmds.separator( height=self.sepH, style=self.sepStl )
        #space switcher
        self.actionButton8 = cmds.button(self.actionButton8, label='Store Xform Anim', c=self.cmdAction, bgc=purple,
        ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Restore animation using restore button.')
        self.actionButton9 = cmds.button(self.actionButton9, label='ReStore Xform Anim', c=self.cmdAction, bgc=purple,
        ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Restore animation using restore button.')
        self.actionButton14 = cmds.button(self.actionButton14, label='ReStore to Selected', c=self.cmdAction, bgc=purple2,
        ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Override - Restore animation to selected object.')
        self.s3 = cmds.separator( height=self.sepH, style=self.sepStl )
        #match things
        self.actionButton4 = cmds.button(self.actionButton4, label='Match Keys', c=self.cmdAction, bgc=green,
        ann='Select 2 objects.\nSecond object will be keyed on same frames as the first.\nNo animation is added, the object is just keyed.')
        self.actionButton6 = cmds.button(self.actionButton6, label='Match Transforms', c=self.cmdAction, bgc=green,
        ann='Match the position of first object to second object.')
        self.s6 = cmds.separator( height=self.sepH, style=self.sepStl )
        #stick
        self.actionButton10 = cmds.button(self.actionButton10, label='Stick', c=self.cmdAction, bgc=teal,
        ann='1 object selected:\nA locator is created and the object is constrained to it on that position.\n\n2 objects selected:\nThe first is constrained to second with an offset.')
        self.actionButton11 = cmds.button(self.actionButton11, label='UnStick', c=self.cmdAction, bgc=teal,
        ann='Selected object is baked.\nhighlight a frame range to use it instead of the full animation.\nExtra objects are deleted.')
        self.c1 = cmds.checkBox( label='On All Frames', v=False, ann=existing )
        self.s4 = cmds.separator( height=self.sepH, style=self.sepStl )
        #anim Rigs
        self.actionButton12 = cmds.button(self.actionButton12, label='Parent Rig', c=self.cmdAction, bgc=greyD,
        ann='A parent rig is created between 2 objects.\n Animation is preserved and transfered to a locator.\nSelect child first.\nROOT/SPIN/OFFSET')
        self.actionButton13 = cmds.button(self.actionButton13, label='Aim Rig', c=self.cmdAction, bgc=greyD,
        ann='An aim rig is created between 2 objects.\n Animation is preserved and transfered to locator.\nSelect target first.\nROOT/BASE\nROOT/AIM/OFFSET\nROOT/AIM/UP')
        self.s5 = cmds.separator( height=self.sepH, style=self.sepStl )
        #update constraint offset
        self.actionButton15 = cmds.button(self.actionButton15, label='Constraint Update', c=self.cmdAction, bgc=blue)
        self.s2 = cmds.separator( height=self.sepH, style=self.sepStl )
        #place loc, constain
        self.actionButton2 = cmds.button(self.actionButton2, label='Place LOC', c=self.cmdAction, bgc=blue)
        self.c5 = cmds.checkBox( label='Constrain to', v=True, ann='Use constraint option.' )
        self.col1 = cmds.radioCollection()
        self.r1 = cmds.radioButton( label='  selection', sl=1, ann='Constrain new locator to selection.' )
        self.r2 = cmds.radioButton( label='  reverse', ann='Constrain selection to new locator.' )
        self.c13 = cmds.checkBox( label='Match Keys', v=True, ann='Will add keys on the same frames as source object.' )
        #constrain
        self.actionButton5 = cmds.button(self.actionButton5, label='Parent Constraint', c=self.cmdAction, bgc=blue)
        self.c9 = cmds.checkBox( label='Offset', v=True )
        self.c10 = cmds.checkBox( label='Translation', v=True )
        self.c11 = cmds.checkBox( label='Rotation', v=True )
        self.s7 = cmds.separator( height=self.sepH, style=self.sepStl )
        #distribute keys
        self.actionButton16 = cmds.button(self.actionButton16, label='Distribute Keys', c=self.cmdAction, bgc=grey)
        self.actionField1 = cmds.textField(self.actionField1, tx=5.0)