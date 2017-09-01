# from __future__ import with_statement
# import os, sys, sys_lib, fnmatch
import maya.cmds as cmds
import maya.mel as mel
# import pymel.core as pm
# import characterSet_lib as cs
# import ast
# reload(cs)
#


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


class Action(object):
    # builds row of buttons for bottom of window

    def __init__(self, name, parent=None, h=15, w=80, cmdAction='', label=''):
        self.fn = 'obliqueLabelFont'
        self.bld = 'boldLabelFont'
        self.parent = parent
        self.illegalChar = ['.', '*']
        self.form = name + '_form'
        self.form1 = name + '_form1'
        self.column = name + '_column'
        self.row = name + '_row'
        self.row2 = name + '_row2'
        self.row3 = name + '_row3'
        self.row4 = name + '_row4'
        self.row5 = name + '_row5'
        self.row6 = name + '_row6'
        self.opt = name + '_opt'
        self.int1 = name + '_int1'
        self.int2 = name + '_int2'
        self.sl1 = name + '_sl1'
        self.sl2 = name + '_sl2'
        self.field1 = name + '_field1'
        self.field2 = name + '_field2'
        self.float1 = name + '_float1'
        self.float2 = name + '_float2'
        self.button1 = name + '_button1'
        self.button2 = name + '_button2'
        self.button3 = name + '_button3'
        self.button4 = name + '_button4'
        self.scroll1 = name + '_scroll1'
        self.scroll2 = name + '_scroll2'
        self.scroll3 = name + '_scroll3'
        self.heading0 = name + '_heading0'
        self.heading1 = name + '_heading1'
        self.heading2 = name + '_heading2'
        self.heading3 = name + '_heading3'
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
        self.heading23 = name + '_heading23'
        self.heading24 = name + '_heading24'
        self.heading25 = name + '_heading25'
        self.heading26 = name + '_heading26'
        self.c1 = ''
        self.c2 = ''
        self.c3 = ''
        self.c4 = ''
        self.c5 = ''
        self.c6 = ''
        self.c7 = ''
        self.c8 = ''
        self.s0 = ''
        self.s1 = ''
        self.s2 = ''
        self.s3 = ''
        self.s4 = ''
        self.s5 = ''
        self.opt1 = ''
        self.col1 = ''
        self.col2 = ''
        self.r1 = ''
        self.r2 = ''
        self.typGrpEx = ''
        self.typGrpIm = ''
        self.srcGrp = ''
        self.label = label
        self.cmdAction = cmdAction
        self.ui = [self.row, self.row2, self.row3, self.row4, self.row5, self.row6, self.int1, self.int2, self.form, self.form1, self.opt, self.button1, self.button2, self.button3, self.button4, self.field1, self.heading1, self.field2, self.heading2, self.heading3, self.heading4, self.heading5, self.heading6, self.heading7, self.heading8, self.heading9, self.heading10, self.heading11, self.heading12, self.heading13, self.heading14, self.heading15, self.heading16, self.heading17, self.heading18, self.heading19, self.heading20, self.heading21, self.heading22, self.heading23, self.heading24, self.heading25, self.heading26, self.scroll1, self.scroll2, self.scroll3, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, self.s0, self.s1, self.s2, self.s3, self.s4, self.s5, self.opt1, self.col1, self.r1, self.r2, self.sl1, self.sl2]
        self.h = h
        self.w = w
        self.heightForm = 30
        self.sepH = 15
        self.sepStl = 'in'
        # self.cleanUI()
        self.buildColumn()
        self.buildAction()

    def cleanUI(self):
        cmds.setParent(self.parent)
        for ui in self.ui:
            if cmds.control(ui, q=True, exists=True):
                cmds.deleteUI(ui)

    def buildColumn(self):
        cmds.setParent(self.parent)
        self.column = cmds.columnLayout(adjustableColumn=True)

    def buildAction(self):
        # colors
        grey = [0.5, 0.5, 0.5]
        greyD = [0.2, 0.2, 0.2]
        red = [0.5, 0.2, 0.2]
        redD = [0.4, 0.2, 0.2]
        blue = [0.2, 0.3, 0.5]
        green = [0.2, 0.5, 0.0]
        teal = [0.0, 0.5, 0.5]
        purple = [0.35, 0.35, 0.5]
        purple2 = [0.28, 0.28, 0.39]
        orange = [0.5, 0.35, 0.0]
        # ann
        existing = 'Will only bake on existing frames.\nTurn off to get a key on every frame.'
        time = 'Force timeline range to be baked.\nOtherwise range is gathered in this priority:\n-Use selected range\n-Use range from animation, if any\n-Use range from timeline.'
        simu = 'Step through every frame.'

        # Export
        '''
        self.s0 = cmds.separator(height=self.sepH, style=self.sepStl)
        self.heading0 = cmds.text(self.heading0, label='EXPORT CLIP', al='center')
        self.s1 = cmds.separator(height=self.sepH, style=self.sepStl)
        '''
        # import type
        self.srcGrp = cmds.radioButtonGrp(label='Source:', labelArray2=['me', 'public', ], select=1, numberOfRadioButtons=2, w=self.w, ad3=1, cw3=[50, 50, 50], cl3=['left', 'both', 'right'], ct3=['left', 'both', 'right'])
        self.s4 = cmds.separator(height=self.sepH, style=self.sepStl)

        self.heading1 = cmds.text(self.heading1, label='Name:', al='left', fn=self.fn)
        self.field1 = cmds.textField(self.field1, tx='', pht='None')
        self.heading2 = cmds.text(self.heading2, label='Comment:', al='left', fn=self.fn)
        self.field2 = cmds.textField(self.field2, tx='', pht='None')
        #
        self.typGrpEx = cmds.radioButtonGrp(label='Export Type:', labelArray2=['anim', 'pose', ], select=1, numberOfRadioButtons=2, w=self.w, ad3=1, cw3=[50, 50, 50], cl3=['left', 'both', 'right'], ct3=['left', 'both', 'right'])
        # range
        self.row = cmds.rowLayout(self.row, numberOfColumns=3, columnWidth3=(100, 50, 50), adjustableColumn=1, columnAlign=(1, 'left'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        cmds.text('Range for driven attrs:')
        self.float1 = cmds.floatField(self.float1, value=cmds.playbackOptions(q=True, min=True), pre=2)
        self.float2 = cmds.floatField(self.float2, value=cmds.playbackOptions(q=True, max=True), pre=2)
        cmds.setParent('..')
        self.button1 = cmds.button(self.button1, label='E X P O R T', c=self.cmdAction, bgc=redD,
                                   ann='Export selected controls to a clip file')
        self.s2 = cmds.separator(height=self.sepH, style=self.sepStl)
        #

        # Import
        self.heading3 = cmds.button(self.heading3, label='CLIP LIBRARY', al='center')
        # self.s3 = cmds.separator(height=self.sepH, style=self.sepStl)

        # 2 scroll lists in form: clip, clip version
        self.form1 = cmds.formLayout(self.form1, h=295, w=1)
        self.scroll1 = cmds.textScrollList(self.scroll1, sc=self.cmdAction, allowMultiSelection=False, dcc=self.cmdAction, fn='plainLabelFont', h=200, w=10)
        attachForm = [(self.scroll1, 'left', 0), (self.scroll1, 'right', 50)]
        cmds.formLayout(self.form1, edit=True, attachForm=attachForm)
        self.scroll2 = cmds.textScrollList(self.scroll2, sc=self.cmdAction, allowMultiSelection=False, dcc=self.cmdAction, fn='plainLabelFont', h=200, w=45)
        attachForm = [(self.scroll2, 'right', 0)]
        attachControl = [(self.scroll2, 'left', 5, self.scroll1)]
        cmds.formLayout(self.form1, edit=True, attachForm=attachForm, attachControl=attachControl)
        self.scroll3 = cmds.textScrollList(self.scroll3, sc=self.cmdAction, allowMultiSelection=True, dcc=self.cmdAction, fn='plainLabelFont', h=85, w=10)
        attachForm = [(self.scroll3, 'left', 0), (self.scroll3, 'right', 0)]
        attachControl = [(self.scroll3, 'top', 5, self.scroll1)]
        cmds.formLayout(self.form1, edit=True, attachForm=attachForm, attachControl=attachControl)
        cmds.setParent('..')

        # Clip attrs
        # commenting out and using export field instead
        '''
        self.heading4 = cmds.text(self.heading4, label='Comment:', al='left', fn=self.fn)
        self.heading5 = cmds.textField(self.heading5, pht='None')
        '''
        self.row6 = cmds.rowLayout(self.row6, numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'left'), columnAttach=[(1, 'left', 0), (2, 'left', 0)])
        self.heading6 = cmds.button(self.heading6, label='Filename:', al='left')
        self.heading7 = cmds.textField(self.heading7, tx='', en=True, pht='None', ed=False)
        cmds.setParent('..')
        self.s0 = cmds.separator(height=self.sepH, style=self.sepStl)
        self.row5 = cmds.rowLayout(self.row5, numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'left'), columnAttach=[(1, 'left', 0), (2, 'left', 0)])
        self.heading8 = cmds.text(self.heading8, label='User:', al='left', fn=self.fn)
        self.heading9 = cmds.text(self.heading9, label='', al='right', en=True)
        cmds.setParent('..')
        self.row4 = cmds.rowLayout(self.row4, numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'left'), columnAttach=[(1, 'left', 0), (2, 'left', 0)])
        self.heading10 = cmds.text(self.heading10, label='Date:', al='left', fn=self.fn)
        self.heading11 = cmds.text(self.heading11, label='', al='right', en=True)
        cmds.setParent('..')
        # import type
        self.typGrpIm = cmds.radioButtonGrp(label='Import Type:', labelArray2=['anim', 'pose', ], select=1, numberOfRadioButtons=2, w=self.w, ad3=1, cw3=[50, 50, 50], cl3=['left', 'both', 'right'], ct3=['left', 'both', 'right'])
        self.s4 = cmds.separator(height=self.sepH, style=self.sepStl)
        # range
        self.row3 = cmds.rowLayout(self.row3, numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'left'), columnAttach=[(1, 'left', 0), (2, 'left', 0)])
        self.heading12 = cmds.text(self.heading12, label='Length:', al='left', fn=self.fn)
        self.heading13 = cmds.text(self.heading13, label='', al='right', en=True)
        cmds.setParent('..')
        # range
        self.col2 = cmds.columnLayout(self.col2, adjustableColumn=True)
        self.row2 = cmds.rowLayout(self.row2, numberOfColumns=5, adjustableColumn=3, columnAlign=(1, 'left'), columnAttach=[(1, 'left', 0), (2, 'left', 0), (3, 'right', 0), (4, 'right', 0), (5, 'right', 0)])
        self.heading24 = cmds.text(self.heading24, l='Start:')
        self.int1 = cmds.floatField(self.int1, en=False, pre=2)
        self.heading25 = cmds.text(' - ')
        self.heading26 = cmds.text(self.heading26, l='End:')
        self.int2 = cmds.floatField(self.int2, en=False, pre=2)
        cmds.setParent('..')
        self.sl1 = cmds.intSlider(self.sl1)
        self.sl2 = cmds.intSlider(self.sl2)
        cmds.setParent('..')
        # self.button2 = cmds.button( self.button2, label='Select objects in clip', c=self.cmdAction, bgc=greyD, h=20 )
        self.c1 = cmds.checkBox(label='Current frame as START frame', v=False, ann='...annotation...')
        self.s4 = cmds.separator(height=self.sepH, style=self.sepStl)
        self.c2 = cmds.checkBox(label='Filter selected objects only', v=True, ann='...annotation...')
        # self.c3 = cmds.checkBox( label='Apply infinity', v=True, ann='...annotation...' )
        # self.c4 = cmds.checkBox( label='Import pose on exported frame', v=True, ann='...annotation...' )
        self.c5 = cmds.checkBox(label='NAMESPACE from selection', v=True, ann='...annotation...')
        self.s5 = cmds.separator(height=self.sepH, style=self.sepStl)
        self.c6 = cmds.checkBox(label='Merge with existing layers', v=True, ann='...annotation...')
        self.c7 = cmds.checkBox(label='Apply layer attributes', v=True, ann='...annotation...')
        self.c8 = cmds.checkBox(label='Base layer as new OVERRIDE layer', v=False, ann='...annotation...')
        # import
        self.button3 = cmds.button(self.button3, label='I M P O R T', c=self.cmdAction, bgc=blue)
        # self.heading22 = cmds.text(self.heading22, label='\n', al='left')
