import maya.cmds  as cmds
import maya.mel as mel
#
# import constraintUI_micro_lib as ui
# import constraint_lib as cn
# import anim_lib as al
import webrImport as web
# web
ui = web.mod('constraintUI_micro_lib')
cn = web.mod('constraint_lib')
al = web.mod('anim_lib')


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class CSUI(object):
    '''
    Build CharacterSet UI
    '''

    def __init__(self, columnWidth=80):
        # external
        self.columnWidth = columnWidth
        # internal
        self.windowName = 'CN Tools'
        # store/restore
        self.objects = []
        self.animBucket = []
        self.objX = None
        self.anim = None
        # execute
        self.cleanUI()
        self.gui()

    def cleanUI(self, *args):
        try:
            cmds.deleteUI(self.windowName)
        except:
            pass

    def gui(self):
        # window
        self.win = cmds.window(self.windowName, w=self.columnWidth, rtf=1)
        # action
        self.actionColumn = ui.Action('action', cmdAction='', label='', w=self.columnWidth)
        cmds.button(self.actionColumn.actionButton1, e=True, c=self.cmdBake)
        cmds.button(self.actionColumn.actionButton2, e=True, c=self.cmdPlace)
        cmds.button(self.actionColumn.actionButton3, e=True, c=self.cmdBakeToLoc)
        cmds.button(self.actionColumn.actionButton4, e=True, c=self.cmdMatchKeys)
        cmds.button(self.actionColumn.actionButton5, e=True, c=self.cmdConstrain)
        cmds.button(self.actionColumn.actionButton6, e=True, c=self.cmdA2B)
        cmds.button(self.actionColumn.actionButton7, e=True, c=self.cmdRO)
        cmds.button(self.actionColumn.actionButton8, e=True, c=self.cmdStore)
        cmds.button(self.actionColumn.actionButton9, e=True, c=self.cmdRestore)
        cmds.button(self.actionColumn.actionButton14, e=True, c=self.cmdRestoreToSelected)
        cmds.button(self.actionColumn.actionButton10, e=True, c=self.cmdStick)
        cmds.button(self.actionColumn.actionButton11, e=True, c=self.cmdUnStick)
        cmds.button(self.actionColumn.actionButton12, e=True, c=self.cmdParentRig)
        cmds.button(self.actionColumn.actionButton13, e=True, c=self.cmdAimRig)
        cmds.button(self.actionColumn.actionButton15, e=True, c=self.cmdUpdateConstraintOffset)
        cmds.button(self.actionColumn.actionButton16, e=True, c=self.cmdDistributeKeys)
        # TODO: Add aimPivotRig, remove other buttons that overlap the shelf
        # TODO: Add aim and up vector options
        # TODO: add point/orient constraint buttons or drop down for constraint type
        # TODO: dockable window, tools used like in Nuke, with scroll bar ?maybe?
        # TODO: delete constraint button
        # TODO: add help section of some sort

        cmds.showWindow(self.win)

    def cmdBake(self, *args):
        import constraint_lib as cn
        reload(cn)
        # v1 = cmds.checkBox(self.actionColumn.c1, q=True, v=True)
        v2 = cmds.checkBox(self.actionColumn.c2, q=True, v=True)
        v3 = cmds.checkBox(self.actionColumn.c3, q=True, v=True)
        v4 = cmds.checkBox(self.actionColumn.c4, q=True, v=True)
        # cn.bakeConstrainedSelection(sparseKeys=v1, removeConstraint=v2, timeLine=v3, sim=v4)
        cn.bakeConstrainedSelection(removeConstraint=v2, timeLine=v3, sim=v4)

    def cmdPlace(self, *args):
        import constraint_lib as cn
        reload(cn)
        sel = cmds.ls(sl=1)
        sl = False
        v5 = cmds.checkBox(self.actionColumn.c5, q=True, v=True)
        v13 = cmds.checkBox(self.actionColumn.c13, q=True, v=True)
        if v5:
            btn = cmds.radioCollection(self.actionColumn.col1, q=True, sl=True)
            lab = cmds.radioButton(btn, q=True, l=True)
            if 'selection' in lab:  # string dependant on query working, dont change UI
                sl = True
        # print sl, '========='
        locs = cn.locatorOnSelection(ro='zxy', X=1.0, constrain=v5, toSelection=sl)
        i = 0
        if v13:
            for loc in locs:
                cn.matchKeyedFrames(A=sel[i], B=loc, subtractive=True)
                i = i + 1

    def cmdBakeToLoc(self, *args):
        import constraint_lib as cn
        reload(cn)
        # v6 = cmds.checkBox(self.actionColumn.c6, q=True, v=True)
        v7 = cmds.checkBox(self.actionColumn.c7, q=True, v=True)
        v8 = cmds.checkBox(self.actionColumn.c8, q=True, v=True)
        v12 = cmds.checkBox(self.actionColumn.c12, q=True, v=True)
        # cn.controllerToLocator(p=v7, r=v8, sparseKeys=v6, timeLine=False, sim=v12)
        cn.controllerToLocator(p=v7, r=v8, timeLine=False, sim=v12)

    def cmdMatchKeys(self, *args):
        import constraint_lib as cn
        reload(cn)
        cn.matchKeyedFrames()

    def cmdConstrain(self, *args):
        sel = cmds.ls(sl=True)
        if len(sel) == 2:
            v9 = cmds.checkBox(self.actionColumn.c9, q=True, v=True)
            v10 = cmds.checkBox(self.actionColumn.c10, q=True, v=True)
            if v10:
                v10 = 'none'
            else:
                v10 = ['x', 'y', 'z']
            v11 = cmds.checkBox(self.actionColumn.c11, q=True, v=True)
            if v11:
                v11 = 'none'
            else:
                v11 = ['x', 'y', 'z']
            cmds.parentConstraint(sel[0], sel[1], mo=v9, st=v10, sr=v11)
        else:
            cmds.warning('-- Select 2 objects --')

    def cmdA2B(self, *args):
        import anim_lib as anim
        reload(anim)
        anim.matchObj()

    def cmdRO(self, *args):
        t1 = cmds.optionMenuGrp(self.actionColumn.opt1, q=True, v=True)
        al.changeRoMulti(ro=t1)

    def cmdStore(self, *args):
        self.animBucket = []
        self.objects = cmds.ls(sl=1)
        # self.objX = cmds.ls(sl=1)[0]
        # self.anim = al.SpaceSwitch(self.objX)
        # message('Animation Stored: -- ' + self.objX, maya=True)
        for obj in self.objects:
            self.animBucket.append(al.SpaceSwitch(obj))
            message('Animation Stored: -- ' + obj, maya=True)
            cmds.refresh(f=1)

    def cmdRestore(self, *args):
        for obj in self.animBucket:
            obj.restore()
            message('Animation ReStored: -- ' + obj.obj, maya=True)
            cmds.refresh(f=1)
        # self.anim.restore()
        # message('Animation ReStored: -- ' + self.objX, maya=True)

    def cmdRestoreToSelected(self, *args):
        self.animBucket[0].restore(useSelected=True)
        message('Animation ReStored: -- ' + self.animBucket[0].obj, maya=True)
        cmds.refresh(f=1)

    def cmdStick(self, *args):
        import constraint_lib as cn
        reload(cn)
        self.objX = cmds.ls(sl=1)[0]
        cn.stick(offset=True)
        message('sticky: -- ' + self.objX, maya=True)

    def cmdUnStick(self, *args):
        import constraint_lib as cn
        reload(cn)
        v1 = cmds.checkBox(self.actionColumn.c1, q=True, v=True)
        self.objX = cmds.ls(sl=1)[0]
        cn.unStick(timeLine=False, sim=v1)
        message('un~sticky: -- ' + self.objX, maya=True)

    def cmdParentRig(self, *args):
        import animRig_lib as ar
        reload(ar)
        ar.parentRig(bake=True)
        message('parent rig built. -- new control Selected ', maya=True)

    def cmdAimRig(self, *args):
        import animRig_lib as ar
        reload(ar)
        ar.aimRig(mo=False)
        message('aimRig: -- ', maya=True)

    def cmdDistributeKeys(self, *args):
        import anim_lib as al
        reload(al)
        fld1 = cmds.textField(self.actionColumn.actionField1, q=1, tx=1)
        v14 = cmds.checkBox(self.actionColumn.c14, q=True, v=True)
        al.distributeKeys(count=float(fld1), destructive=v14)
        # message('distribute keys on ' , maya=True)

    def cmdUpdateConstraintOffset(self, *args):
        cn.updateConstraintOffset(obj=cmds.ls(sl=1))
