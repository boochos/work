import maya.cmds  as cmds
import constraintUI_micro_lib as ui
import constraint_lib as cn
import maya.mel as mel
import anim_lib as al

reload(al)
reload(cn)
reload(ui)

class CSUI(object):
    '''
    Build CharacterSet UI
    '''
    def __init__(self, columnWidth=80):
        #external
        self.columnWidth                  = columnWidth
        #internal
        self.windowName                   = 'CN Tools'
        #execute
        self.cleanUI()
        self.gui()

    def cleanUI(self, *args):
        try:
            cmds.deleteUI(self.windowName)
        except:
            pass

    def gui(self):
        #window
        self.win = cmds.window(self.windowName, w=self.columnWidth, rtf=1)
        #action
        self.actionColumn = ui.Action('action', cmdAction='', label='', w=self.columnWidth)
        cmds.button(self.actionColumn.actionButton1, e=True, c=self.cmdBake)
        cmds.button(self.actionColumn.actionButton2, e=True, c=self.cmdPlace)
        cmds.button(self.actionColumn.actionButton3, e=True, c=self.cmdBakeToLoc)
        cmds.button(self.actionColumn.actionButton4, e=True, c=self.cmdMatchKeys)
        cmds.button(self.actionColumn.actionButton5, e=True, c=self.cmdConstrain)
        cmds.button(self.actionColumn.actionButton6, e=True, c=self.cmdA2B)
        cmds.button(self.actionColumn.actionButton7, e=True, c=self.cmdRO)

        cmds.showWindow(self.win)

    def cmdBake(self, *args):
        import constraint_lib as cn
        reload(cn)
        v1 = cmds.checkBox(self.actionColumn.c1, q=True, v=True)
        v2 = cmds.checkBox(self.actionColumn.c2, q=True, v=True)
        v3 = cmds.checkBox(self.actionColumn.c3, q=True, v=True)
        v4 = cmds.checkBox(self.actionColumn.c4, q=True, v=True)
        cn.bakeConstrainedSelection(sparseKeys=v1, removeConstraint=v2, timeLine=v3, sim=v4)

    def cmdPlace(self,*args):
        import constraint_lib as cn
        reload(cn)
        sl=False
        v5 = cmds.checkBox(self.actionColumn.c5, q=True, v=True)
        if v5:
            btn = cmds.radioCollection(self.actionColumn.col1, q=True, sl=True)
            lab = cmds.radioButton(btn, q=True, l=True)
            if 'selection' in lab: #string dependant on query working, dont change UI
                sl = True
        #print sl, '========='
        cn.locatorOnSelection(ro='zxy', X=1.0, constrain=v5, toSelection=sl)

    def cmdBakeToLoc(self,*args):
        import constraint_lib as cn
        reload(cn)
        v6 = cmds.checkBox(self.actionColumn.c6, q=True, v=True)
        v7 = cmds.checkBox(self.actionColumn.c7, q=True, v=True)
        v8 = cmds.checkBox(self.actionColumn.c8, q=True, v=True)
        v12 = cmds.checkBox(self.actionColumn.c12, q=True, v=True)
        cn.controllerToLocator(p=v7, r=v8, sparseKeys=v6, timeLine=False, sim=v12)

    def cmdMatchKeys(self, *args):
        import constraint_lib as cn
        reload(cn)
        cn.matchKeyedFrames()

    def cmdConstrain(self, *args):
        sel = cmds.ls(sl=True)
        if len(sel) == 2:
            v9 = cmds.checkBox(self.actionColumn.c9, q=True, v=True)
            v10 = cmds.checkBox(self.actionColumn.c10, q=True, v=True)
            if v10 == True:
                v10 = 'none'
            else:
                v10 = ['x','y','z']
            v11 = cmds.checkBox(self.actionColumn.c11, q=True, v=True)
            if v11 == True:
                v11 = 'none'
            else:
                v11 = ['x','y','z']
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