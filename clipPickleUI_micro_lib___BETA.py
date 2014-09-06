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
        self.field1  = name + '_field1'
        self.field2  = name + '_field2'
        self.button1  = name + '_button1'
        self.button2  = name + '_button2'
        self.button3  = name + '_button3'
        self.button4  = name + '_button4'
        self.scroll1        = name + '_scroll1'
        self.heading0  = name + '_heading0'
        self.heading1  = name + '_heading1'
        self.heading2  = name + '_heading2'
        self.heading3  = name + '_heading3'
        self.heading4 = name + '_heading4'
        self.heading5 = name + '_heading5'
        self.heading6 = name + '_heading6'
        self.heading7 = name + '_heading7'
        self.heading8 = name + '_heading8'
        self.heading9 = name + '_heading9'
        self.heading10 = name + '_heading10'
        self.heading11 = name + '_heading11'
        self.heading12 = name + '_heading12'
        self.heading13 = name + '_heading13'
        self.heading14 = name + '_heading14'
        self.heading15 = name + '_heading15'
        self.heading16 = name + '_heading16'
        self.heading17 = name + '_heading17'
        self.heading18 = name + '_heading18'
        self.heading19 = name + '_heading19'
        self.heading20 = name + '_heading20'
        self.heading21 = name + '_heading21'
        self.heading22 = name + '_heading22'
        self.c1            = ''
        self.c2            = ''
        self.c3            = ''
        self.c4            = ''
        self.c5            = ''
        self.s0            = ''
        self.s1            = ''
        self.s2            = ''
        self.s3            = ''
        self.s4            = ''
        self.opt1          = ''
        self.col1          = ''
        self.r1            = ''
        self.r2            = ''
        self.label         = label
        self.cmdAction     = cmdAction
        self.ui            = [self.form, self.opt,self.button1, self.button2, self.button3, self.button4, self.field1, self.heading1, self.field2, self.heading2, self.heading3, self.heading4, self.heading5, self.heading6, self.heading7, self.heading8, self.heading9, self.heading10, self.heading11, self.heading12, self.heading13, self.heading14, self.heading15, self.heading16, self.heading17, self.heading18, self.heading19, self.heading20,  self.heading21, self.heading22, self.scroll1, self.c1,  self.c2, self.c3, self.c4, self.c5, self.s0, self.s1, self.s2, self.s3, self.s4, self.opt1, self.col1, self.r1, self.r2]
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

        #Export
        self.s0 = cmds.separator( height=self.sepH, style=self.sepStl )
        self.heading0 = cmds.text(self.heading0, label='\nExport Clips\n', al='center')
        self.s1 = cmds.separator( height=self.sepH, style=self.sepStl )
        self.heading1 = cmds.text(self.heading1, label='Name:', al='left')
        self.field1 = cmds.textField(self.field1, tx='')
        self.heading2 = cmds.text(self.heading2, label='Comment:', al='left')
        self.field2 = cmds.textField(self.field2, tx='')
        self.button1 = cmds.button(self.button1, label='Export Clip', c=self.cmdAction, bgc=greyD,
        ann='Export selected controls to a clip file')
        self.s2 = cmds.separator( height=self.sepH, style=self.sepStl )
        #

        #Import
        self.heading3 = cmds.text(self.heading3, label='\nImport Clips\n', al='center')
        self.s3 = cmds.separator( height=self.sepH, style=self.sepStl )
        self.scroll1 = cmds.textScrollList( self.scroll1, sc=self.cmdAction, allowMultiSelection=False, dcc=self.cmdAction, fn='plainLabelFont', h=150, w=10 )
        #attachForm = [( self.scroll1, 'bottom', 0 ), ( self.scroll1, 'left', 0 ), ( self.scroll1, 'right', 0 )]
        #attachControl = [( self.scroll1, 'top', 0, self.button1 )]
        #cmds.columnLayout( self.form, edit=True, attachForm=attachForm, attachControl=attachControl )

        #Clip attrs
        self.heading4 = cmds.text(self.heading4, label='comment:', al='left')
        self.heading5 = cmds.text(self.heading5, label='na', al='left')
        self.heading6 = cmds.text(self.heading6, label='animlayers:', al='left')
        self.heading7 = cmds.text(self.heading7, label='na', al='left')
        self.heading8 = cmds.text(self.heading8, label='start:', al='left')
        self.heading9 = cmds.text(self.heading9, label='na', al='left')
        self.heading10 = cmds.text(self.heading10, label='end:', al='left')
        self.heading11 = cmds.text(self.heading11, label='na', al='left')
        self.heading12 = cmds.text(self.heading12, label='length:', al='left')
        self.heading13 = cmds.text(self.heading13, label='na', al='left')
        self.heading14 = cmds.text(self.heading14, label='objects:', al='left')
        self.heading15 = cmds.text(self.heading15, label='na', al='left')
        self.heading16 = cmds.text(self.heading16, label='source:', al='left')
        self.heading17 = cmds.text(self.heading17, label='na', al='left')
        self.heading18 = cmds.text(self.heading18, label='user:', al='left')
        self.heading19 = cmds.text(self.heading19, label='na', al='left')
        self.heading20 = cmds.text(self.heading20, label='date:', al='left')
        self.heading21 = cmds.text(self.heading21, label='na', al='left')
        self.s4 = cmds.separator( height=self.sepH, style=self.sepStl )


        #import options
        self.button2 = cmds.button(self.button2, label='Select objects in clip', c=self.cmdAction, bgc=greyD, h=20)
        self.c1 = cmds.checkBox( label='import on current frame', v=True, ann='...annotation...' )
        self.c2 = cmds.checkBox( label='selected objects only', v=True, ann='...annotation...' )
        self.c3 = cmds.checkBox( label='apply infinity', v=True, ann='...annotation...' )
        self.c4 = cmds.checkBox( label='import pose on exported frame', v=True, ann='...annotation...' )
        self.c5 = cmds.checkBox( label='use selection namespace', v=True, ann='...annotation...' )
        self.button3 = cmds.button(self.button3, label='Import Clip', c=self.cmdAction, bgc=blue)
        #self.heading22 = cmds.text(self.heading22, label='\n', al='left')
        #self.s4 = cmds.separator( height=self.sepH, style=self.sepStl )