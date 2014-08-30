import maya.cmds  as cmds
import constraintUI_micro_lib as ui
import constraint_lib as cn
import maya.mel as mel
import anim_lib as al

reload(al)
reload(cn)
reload(ui)

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

class CSUI(object):
    '''
    Build CharacterSet UI
    '''

    def __init__(self, columnWidth=80):
        #external
        self.columnWidth                  = columnWidth
        #internal
        self.windowName                   = 'Clip Manager'
        #store/restore
        self.objects  = []
        self.animBucket = []
        self.objX = None
        self.anim = None
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
        self.actionColumn = ui.Action('clipAction', cmdAction='', label='', w=self.columnWidth)
        cmds.button(self.actionColumn.actionButton1, e=True, c=self.cmdBake)
        cmds.button(self.actionColumn.actionButton2, e=True, c=self.cmdPlace)
        cmds.button(self.actionColumn.actionButton16, e=True, c=self.cmdDistributeKeys)

        cmds.showWindow(self.win)

    def cmdBake(self, *args):
        import constraint_lib as cn
        reload(cn)
        #v1 = cmds.checkBox(self.actionColumn.c1, q=True, v=True)
        v2 = cmds.checkBox(self.actionColumn.c2, q=True, v=True)
        v3 = cmds.checkBox(self.actionColumn.c3, q=True, v=True)
        v4 = cmds.checkBox(self.actionColumn.c4, q=True, v=True)
        #cn.bakeConstrainedSelection(sparseKeys=v1, removeConstraint=v2, timeLine=v3, sim=v4)
        cn.bakeConstrainedSelection( removeConstraint=v2, timeLine=v3, sim=v4)

    def cmdPlace(self,*args):
        import constraint_lib as cn
        reload(cn)
        sel = cmds.ls(sl=1)
        sl=False
        v5 = cmds.checkBox(self.actionColumn.c5, q=True, v=True)
        v13 = cmds.checkBox(self.actionColumn.c13, q=True, v=True)
        if v5:
            btn = cmds.radioCollection(self.actionColumn.col1, q=True, sl=True)
            lab = cmds.radioButton(btn, q=True, l=True)
            if 'selection' in lab: #string dependant on query working, dont change UI
                sl = True
        #print sl, '========='
        locs = cn.locatorOnSelection(ro='zxy', X=1.0, constrain=v5, toSelection=sl)
        if v13:
            for loc in locs:
                cn.matchKeyedFrames(A=sel[0], B=loc, subtractive=True)

    def cmdDistributeKeys(self, *args):
        import anim_lib as al
        reload(al)
        fld1 = cmds.textField(self.actionColumn.actionField1, q=1, tx=1)
        v14 = cmds.checkBox(self.actionColumn.c14, q=True, v=True)
        al.distributeKeys(count=float(fld1), destructive=v14)
        #message('distribute keys on ' , maya=True)
