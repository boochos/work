import maya.cmds as cmds
import maya.mel as mel
import os
import json


def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')
    # print "\n"


class Action(object):
    # builds row of buttons for bottom of window

    def __init__(self, name, parent=None, h=15, w=80, cmdAction='', label=''):
        self.parent = parent
        self.prefs = {}
        self.illegalChar = ['.', '*']
        self.form = name + '_form'
        self.column = name + '_column'
        self.opt = name + '_opt'
        self.actionButton1 = name + '_actionButton1'
        self.actionButton2 = name + '_actionButton2'
        self.actionButton3 = name + '_actionButton3'
        self.actionButton4 = name + '_actionButton4'
        self.actionButton5 = name + '_actionButton5'
        self.actionButton6 = name + '_actionButton6'
        self.actionField1 = name + '_actionField1'
        self.actionButton7 = name + '_actionButton7'
        self.actionButton8 = name + '_actionButton8'
        self.actionButton9 = name + '_actionButton9'
        #self.actionButton10 = name + '_actionButton10'
        #self.actionButton11 = name + '_actionButton11'
        self.actionButton12 = name + '_actionButton12'
        self.actionButton13 = name + '_actionButton13'
        self.actionButton14 = name + '_actionButton14'
        self.actionButton15 = name + '_actionButton15'
        self.actionButton16 = name + '_actionButton16'
        self.actionButton17 = name + '_actionButton17'
        self.actionButton18 = name + '_actionButton18'
        self.c1 = ''
        self.c2 = ''
        self.c3 = ''
        self.c4 = ''
        self.c5 = ''
        # self.c6            = ''
        self.c7 = ''
        self.c8 = ''
        self.c9 = ''
        self.c10 = ''
        self.c11 = ''
        self.c12 = ''
        self.c13 = ''
        self.c14 = ''
        self.c15 = ''
        self.c16 = ''
        self.c17 = ''
        self.c18 = ''
        self.c19 = ''
        self.c20 = ''
        self.c21 = ''
        self.s0 = ''
        self.s1 = ''
        self.s2 = ''
        self.s3 = ''
        self.s4 = ''
        self.s5 = ''
        self.s6 = ''
        self.s7 = ''
        self.opt1 = ''
        self.sl1 = ''
        #self.col1 = ''
        #self.r1 = ''
        #self.r2 = ''
        self.conGrp = ''
        self.aimGrp = ''
        self.upGrp = ''
        self.label = label
        self.cmdAction = cmdAction
        #
        self.h = h
        self.w = w
        self.heightForm = 30
        self.sepH = 15
        self.sepStl = 'in'
        self.buildColumn()
        self.buildAction()

    def prefPath(self, *args):
        varPath = cmds.internalVar(userAppDir=True)
        path = os.path.join(varPath, 'scripts')
        path = os.path.join(path, 'HelpersPrefs.json')
        return path

    def prefSave(self, *args):
        # save
        fileObjectJSON = open(self.prefPath(), 'wb')
        json.dump(self.prefs, fileObjectJSON, indent=1)
        fileObjectJSON.close()

    def prefLoad(self, *args):
        # load
        if os.path.isfile(self.prefPath()):
            fileObjectJSON = open(self.prefPath(), 'r')
            self.prefs = json.load(fileObjectJSON)
            # print clpJSON.__dict__, '   reconstructed'
            fileObjectJSON.close()
            self.prefPut()

    def prefGet(self, *args):
        self.prefs['BkRmvCon'] = cmds.checkBox(self.c2, q=True, v=True)
        self.prefs['BkTmRng'] = cmds.checkBox(self.c3, q=True, v=True)
        self.prefs['BkAllFrms'] = cmds.checkBox(self.c4, q=True, v=True)
        self.prefs['LocTrns'] = cmds.checkBox(self.c7, q=True, v=True)
        self.prefs['LocRot'] = cmds.checkBox(self.c8, q=True, v=True)
        self.prefs['LocAllFrms'] = cmds.checkBox(self.c12, q=True, v=True)
        self.prefs['PrntRgPosOnly'] = cmds.checkBox(self.c17, q=True, v=True)
        self.prefs['AimRgNegAim'] = cmds.checkBox(self.c15, q=True, v=True)
        self.prefs['AimRgAim'] = cmds.radioButtonGrp(self.aimGrp, q=True, select=True)
        self.prefs['AimRgNegUp'] = cmds.checkBox(self.c16, q=True, v=True)
        self.prefs['AimRgUp'] = cmds.radioButtonGrp(self.upGrp, q=True, select=True)
        self.prefs['PvtRgNegAim'] = cmds.checkBox(self.c18, q=True, v=True)
        self.prefs['PvtRgAim'] = cmds.radioButtonGrp(self.aimPivotGrp, q=True, select=True)
        self.prefs['PvtRgNegUp'] = cmds.checkBox(self.c19, q=True, v=True)
        self.prefs['PvtRgUp'] = cmds.radioButtonGrp(self.upPivotGrp, q=True, select=True)
        self.prefs['PvtRgMstr'] = cmds.checkBox(self.c21, q=True, v=True)
        self.prefs['PvtRgMstrSl'] = cmds.radioButtonGrp(self.masterGrp, q=True, select=True)
        self.prefs['PvtRgMstrEnbl'] = cmds.radioButtonGrp(self.masterGrp, q=True, en=True)
        self.prefs['PvtRgDstnc'] = cmds.floatSliderGrp(self.sl1, q=True, v=True)
        self.prefs['LcAllFrms'] = cmds.checkBox(self.c21, q=True, v=True)
        self.prefs['PlcCon'] = cmds.checkBox(self.c5, q=True, v=True)
        self.prefs['PlcConTo'] = cmds.radioButtonGrp(self.conGrp, q=True, select=True)
        self.prefs['PlcConToEnbl'] = cmds.radioButtonGrp(self.conGrp, q=True, en=True)
        self.prefs['PlcMtchKys'] = cmds.checkBox(self.c13, q=True, v=True)
        self.prefs['ConOffst'] = cmds.checkBox(self.c9, q=True, v=True)
        self.prefs['ConTrns'] = cmds.checkBox(self.c10, q=True, v=True)
        self.prefs['ConRot'] = cmds.checkBox(self.c11, q=True, v=True)
        self.prefs['DstKys'] = cmds.intField(self.actionField1, q=True, v=True)
        self.prefs['DstKysDstrct'] = cmds.checkBox(self.c14, q=True, v=True)
        self.prefSave()

    def prefPut(self):
        cmds.checkBox(self.c2, e=True, v=self.prefs['BkRmvCon'])
        cmds.checkBox(self.c3, e=True, v=self.prefs['BkTmRng'])
        cmds.checkBox(self.c4, e=True, v=self.prefs['BkAllFrms'])
        cmds.checkBox(self.c7, e=True, v=self.prefs['LocTrns'])
        cmds.checkBox(self.c8, e=True, v=self.prefs['LocRot'])
        cmds.checkBox(self.c12, e=True, v=self.prefs['LocAllFrms'])
        cmds.checkBox(self.c17, e=True, v=self.prefs['PrntRgPosOnly'])
        cmds.checkBox(self.c15, e=True, v=self.prefs['AimRgNegAim'])
        cmds.radioButtonGrp(self.aimGrp, e=True, select=self.prefs['AimRgAim'])
        cmds.checkBox(self.c16, e=True, v=self.prefs['AimRgNegUp'])
        cmds.radioButtonGrp(self.upGrp, e=True, select=self.prefs['AimRgUp'])
        cmds.checkBox(self.c18, e=True, v=self.prefs['PvtRgNegAim'])
        cmds.radioButtonGrp(self.aimPivotGrp, e=True, select=self.prefs['PvtRgAim'])
        cmds.checkBox(self.c19, e=True, v=self.prefs['PvtRgNegUp'])
        cmds.radioButtonGrp(self.upPivotGrp, e=True, select=self.prefs['PvtRgUp'])
        cmds.checkBox(self.c21, e=True, v=self.prefs['PvtRgMstr'])
        cmds.radioButtonGrp(self.masterGrp, e=True, select=self.prefs['PvtRgMstrSl'])
        cmds.radioButtonGrp(self.masterGrp, e=True, en=self.prefs['PvtRgMstrEnbl'])
        cmds.floatSliderGrp(self.sl1, e=True, v=self.prefs['PvtRgDstnc'])
        cmds.checkBox(self.c21, e=True, v=self.prefs['LcAllFrms'])
        cmds.checkBox(self.c5, e=True, v=self.prefs['PlcCon'])
        cmds.radioButtonGrp(self.conGrp, e=True, select=self.prefs['PlcConTo'])
        cmds.radioButtonGrp(self.conGrp, e=True, en=self.prefs['PlcConToEnbl'])
        cmds.checkBox(self.c13, e=True, v=self.prefs['PlcMtchKys'])
        cmds.checkBox(self.c9, e=True, v=self.prefs['ConOffst'])
        cmds.checkBox(self.c10, e=True, v=self.prefs['ConTrns'])
        cmds.checkBox(self.c11, e=True, v=self.prefs['ConRot'])
        cmds.intField(self.actionField1, e=True, v=self.prefs['DstKys'])
        cmds.checkBox(self.c14, e=True, v=self.prefs['DstKysDstrct'])

    def buildColumn(self):
        cmds.setParent(self.parent)
        self.column = cmds.columnLayout(adjustableColumn=True)

    def buildAction(self):
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
        existing = 'Will only bake on existing frames.\nTurn off to get a key on every frame.'
        time = 'Force timeline range to be baked.\nOtherwise range is gathered in this priority:\n-Use selected range\n-Use range from animation, if any\n-Use range from timeline.'
        simu = 'Step through every frame.'
        # self.s0 = cmds.separator( height=self.sepH, style=self.sepStl )
        # bake
        self.actionButton1 = cmds.button(self.actionButton1, label='Bake', c=self.cmdAction, bgc=red,
                                         ann='Bake selected objects if they are connected to a pairBlend node or constraint.')
        self.c2 = cmds.checkBox(label='Remove Constraint', v=True, cc=self.prefGet,
                                ann='Remove constraint after baking.\nIf off, anim curves are updated and the constraint remains connected.')
        self.c3 = cmds.checkBox(label='Timeline Range', cc=self.prefGet, ann=time)
        self.c4 = cmds.checkBox(label='On All Frames', v=False, cc=self.prefGet, ann=simu)
        self.s7 = cmds.separator(height=self.sepH, style=self.sepStl)
        # bake to locator
        self.actionButton3 = cmds.button(self.actionButton3, label='Bake To HELPER', c=self.cmdAction, bgc=red,
                                         ann='Bake all selected objects to a locator in world space.')
        # self.c6 = cmds.checkBox( label='On Existing Frames', v=True, ann=existing )
        self.c7 = cmds.checkBox(label='Translation', v=True, cc=self.prefGet, ann='Only bake translation attributes.\nRotation will be constrained to follow object.')
        self.c8 = cmds.checkBox(label='Rotation', v=True, cc=self.prefGet, ann='Only bake rotation attributes.\nTranslation will be constrained to follow object.')
        self.c12 = cmds.checkBox(label='On All Frames', v=False, cc=self.prefGet, ann=simu)
        self.s2 = cmds.separator(height=self.sepH, style=self.sepStl)
        # distribute keys
        cmds.rowLayout( numberOfColumns=2, ad2=1)
        self.actionButton16 = cmds.button(self.actionButton16, label='Distribute keys every nth frame:', c=self.cmdAction, bgc=redD)
        self.actionField1 = cmds.intField(self.actionField1, cc=self.prefGet, v=5, w=50)
        cmds.setParent('..')
        ann = 'Destructive Mode. Removes keys that dont fall on the same frame.'
        self.c14 = cmds.checkBox(label='Destructive', v=True, cc=self.prefGet, ann=ann)
        self.s1 = cmds.separator(height=self.sepH, style=self.sepStl)
        # rotate order
        cmds.rowLayout( numberOfColumns=3, ad3=1)
        self.actionButton7 = cmds.button(self.actionButton7, label='Transform Rotate Order', c=self.cmdAction, bgc=redD, ann='Transform animation to different rotation order.')
        self.actionButton18 = cmds.button(self.actionButton18, label='Query', c=self.cmdAction, ann='Selects objects current Rotate Order')
        self.opt1 = cmds.optionMenuGrp(label='', cw2=[0, 40], cat=(1, 'left', 0), ann='Select rotate order to bake to.')
        ro = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        for o in ro:
            cmds.menuItem(o)
        cmds.setParent('..')
        self.s6 = cmds.separator(height=self.sepH, style=self.sepStl)
        # space switcher
        self.actionButton8 = cmds.button(self.actionButton8, label='Store World Space Anim', c=self.cmdAction, bgc=purple,
                                         ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Restore animation using restore button.')
        self.actionButton9 = cmds.button(self.actionButton9, label='Restore', c=self.cmdAction, bgc=purple,
                                         ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Restore animation using restore button.')
        self.actionButton14 = cmds.button(self.actionButton14, label='Restore to Selected', c=self.cmdAction, bgc=purple2,
                                          ann='Space switch tool\n1. Store animation before making changes to attributes.\n2. Make changes to attributes\n3. Override - Restore animation to selected object.')
        self.s3 = cmds.separator(height=self.sepH, style=self.sepStl)
        #
        # match things
        # self.actionButton4 = cmds.button(self.actionButton4, label='Match Keys', c=self.cmdAction, bgc=green,
        #                                ann='Select 2 objects.\nSecond object will be keyed on same frames as the first.\nNo animation is added, the object is just keyed.')
        # self.actionButton6 = cmds.button(self.actionButton6, label='Match Transforms', c=self.cmdAction, bgc=green,
        #                                 ann='Match the position of first object to second object.')
        # self.s6 = cmds.separator(height=self.sepH, style=self.sepStl)
        # stick
        # self.actionButton10 = cmds.button(self.actionButton10, label='Stick', c=self.cmdAction, bgc=teal,
        # ann='1 object selected:\nA locator is created and the object is constrained to it on that position.\n\n2 objects selected:\nThe first is constrained to second with an offset.')
        # self.actionButton11 = cmds.button(self.actionButton11, label='UnStick', c=self.cmdAction, bgc=teal,
        # ann='Selected object is baked.\nhighlight a frame range to use it instead of the full animation.\nExtra objects are deleted.')
        # self.c1 = cmds.checkBox(label='On All Frames', v=False, ann=existing)
        # self.s4 = cmds.separator(height=self.sepH, style=self.sepStl)
        #
        #
        # parent rig
        self.actionButton12 = cmds.button(self.actionButton12, label='Parent Rig', c=self.cmdAction, bgc=greyD,
                                          ann='A parent rig is created between 2 objects.\n Animation is preserved and transfered to a locator.\nSelect child first.\nROOT/SPIN/OFFSET')
        self.c17 = cmds.checkBox(label='Position Only', v=False, cc=self.prefGet, ann='Rotations in world space or in the space of third selection')
        # aim rig
        self.actionButton13 = cmds.button(self.actionButton13, label='Aim Rig', c=self.cmdAction, bgc=greyD,
                                          ann='An aim rig is created between 2 objects.\n Animation is preserved and transfered to locator.\nSelect target first.\nROOT/BASE\nROOT/AIM/OFFSET\nROOT/AIM/UP')
        self.c15 = cmds.checkBox(label='Negative Aim', v=False, cc=self.prefGet, ann='Specifies the AIM should be in the negative direction')
        self.aimGrp = cmds.radioButtonGrp(label='Aim:', cc=self.prefGet, labelArray3=['x', 'y', 'z'], select=1, numberOfRadioButtons=3, w=self.w, ad4=5, cw4=[40, 35, 35, 35], cl4=['left', 'left', 'left', 'left'], ct4=['left', 'left', 'left', 'left'])
        self.c16 = cmds.checkBox(label='Negative Up', v=False, cc=self.prefGet, ann='Specifies the UP should be in the negative direction')
        self.upGrp = cmds.radioButtonGrp(label='Up:', cc=self.prefGet, labelArray3=['x', 'y', 'z'], select=2, numberOfRadioButtons=3, w=self.w, ad4=5, cw4=[40, 35, 35, 35], cl4=['left', 'left', 'left', 'left'], ct4=['left', 'left', 'left', 'left'])
        # pivot rig
        # aimPivotRig(size=0.3, aim=(0, 0, 1), u=(0, 1, 0), offset=20.0, masterControl=False, masterPosition=0)
        self.actionButton17 = cmds.button(self.actionButton17, label='Pivot Rig', c=self.cmdAction, bgc=greyD)
        # aim
        self.c18 = cmds.checkBox(label='Negative Aim', v=False, cc=self.prefGet, ann='Specifies the AIM should be in the negative direction')
        self.aimPivotGrp = cmds.radioButtonGrp(label='Aim:', cc=self.prefGet, labelArray3=['x', 'y', 'z'], select=1, numberOfRadioButtons=3, w=self.w, ad4=5, cw4=[40, 35, 35, 35], cl4=['left', 'left', 'left', 'left'], ct4=['left', 'left', 'left', 'left'])
        # up
        self.c19 = cmds.checkBox(label='Negative Up', v=False, cc=self.prefGet, ann='Specifies the UP should be in the negative direction')
        self.upPivotGrp = cmds.radioButtonGrp(label='Up:', cc=self.prefGet, labelArray3=['x', 'y', 'z'], select=2, numberOfRadioButtons=3, w=self.w, ad4=5, cw4=[40, 35, 35, 35], cl4=['left', 'left', 'left', 'left'], ct4=['left', 'left', 'left', 'left'])
        # master
        self.c21 = cmds.checkBox(label='Master Control Location', v=False, cc=self.prefGet, ann='Create master control at one of the 4 pivot points.')
        self.masterGrp = cmds.radioButtonGrp(label='', cc=self.prefGet, en=False, labelArray4=['Core', 'Root', 'Aim', 'Up'], select=1, numberOfRadioButtons=4, w=self.w, ad5=5, cw5=[0, 50, 50, 40, 35], cl5=['left', 'left', 'left', 'left', 'left'], ct5=['left', 'left', 'left', 'left', 'left'])
        # offset
        self.sl1 = cmds.floatSliderGrp(label='Distance:', cc=self.prefGet, cw3=[50, 40, 30], cl3=['left', 'left', 'left'], w=self.w, field=True, minValue=0.5, maxValue=100.0, fieldMinValue=-0.0, fieldMaxValue=100.0, value=20)
        self.s5 = cmds.separator(height=self.sepH, style=self.sepStl)
        # update constraint offset
        self.actionButton15 = cmds.button(self.actionButton15, label='Constraint Offset Update', c=self.cmdAction, bgc=blue)
        self.s2 = cmds.separator(height=self.sepH, style=self.sepStl)
        # place loc, constain
        self.actionButton2 = cmds.button(self.actionButton2, label='Place HELPER', c=self.cmdAction, bgc=blue)
        self.c5 = cmds.checkBox(label='Constrain to:', v=True, cc=self.prefGet, ann='Use constraint option.')
        self.conGrp = cmds.radioButtonGrp(label='', cc=self.prefGet, labelArray2=['selection', 'reverse'], select=1, numberOfRadioButtons=2, w=self.w, ad3=3, cw3=[0, 70, 35], cl3=['both', 'left', 'left'], ct3=['left', 'left', 'left'])
        self.c13 = cmds.checkBox(label='Match Keys', v=True, cc=self.prefGet, ann='Will add keys on the same frames as source object.')
        # constrain
        self.actionButton5 = cmds.button(self.actionButton5, label='Parent Constraint', c=self.cmdAction, bgc=blue)
        self.c9 = cmds.checkBox(label='Offset', cc=self.prefGet, v=True)
        self.c10 = cmds.checkBox(label='Translation', cc=self.prefGet, v=True)
        self.c11 = cmds.checkBox(label='Rotation', cc=self.prefGet, v=True)
