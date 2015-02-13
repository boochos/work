import os
import maya.cmds as cmds
import maya.mel as mel


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class Get():
    def __init__(self):
        # scripts
        scriptDir = cmds.internalVar(usd=1)
        scriptDir = scriptDir.partition('maya')
        scriptDir = os.path.join(scriptDir[0], scriptDir[1])
        self.rootPath = os.path.join(scriptDir, 'scripts')
        # prefs
        prefDir = cmds.internalVar(upd=1)
        # build paths
        self.iconPath = os.path.join(prefDir, 'icons')
        self.iconOn = os.path.join(self.iconPath, 'srv_mirSel_on_icon.xpm')
        self.iconOff = os.path.join(self.iconPath, 'srv_mirSel_off_icon.xpm')
        self.pairPath = os.path.join(self.rootPath, 'pairSelectList.txt')


def nameSpace(ns='', base=False):
    if ':' in ns:
        i = ns.rfind(':')
        ref = ns[:i]
        obj = ns[i + 1:]
        if base is False:
            return ref
        else:
            return ref, obj
    else:
        return ns


def undoSel():
    sel = cmds.ls(sl=True)
    info = cmds.undoInfo(q=True, un=True)
    if 'selectKey' in info:
        return None
    elif 'select' in info:
        cmds.undo()
        cmds.select(clear=True)
        cmds.select(sel)
        return True


def job(*args):
    # left/right scheme
    side = ['r_', 'l_']
    p = Get()
    pairList = []
    pair = []
    lf = True
    # find pairs of selection
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        proceed = undoSel()
        if proceed:
            sel = sel[len(sel) - 1]
            if ':' in sel:
                i = sel.rfind(':')
                ref = sel[:i]
                obj = sel[i + 1:]
            else:
                ref = None
                obj = sel
                # load pairs
            for line in open(p.pairPath).readlines():
                line = line.strip('\n')
                if lf:
                    pair.append(line)
                    lf = False
                else:
                    pair.append(line)
                    pairList.append(pair)
                    pair = []
                    lf = True
            # find pair in file
            for p in pairList:
                if obj in p:
                    p.remove(obj)
                    if ref:
                        selPair = ref + ':' + p[0]
                    else:
                        selPair = p[0]
                    cmds.select(selPair, tgl=True)
                    message('Pair Selected', maya=True)
                    return None
            # if loop finds nothing, try auto resolving name
            if side[0] in obj:
                selPair = obj.replace(side[0], side[1])
            elif side[1] in obj:
                selPair = obj.replace(side[1], side[0])
            else:
                return None
            try:
                if ref:
                    selPair = ref + ':' + selPair
                cmds.select(selPair, tgl=True)
                message('Pair Selected', maya=True)
                return None
            except:
                pass
    else:
        pass


def killJob():
    getJobs = cmds.scriptJob(lj=True)
    jobs = []
    for job in getJobs:
        if "selUI.job()" in job:
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)


# global id for script job
id = None


def toggleJob():
    p = Get()
    global id
    if id:
        killJob()
        cmds.scriptJob(kill=id, force=True)
        id = None
        toggleIcon()
        message('Pair Selection OFF', maya=True)
    else:
        # print id
        killJob()
        id = cmds.scriptJob(e=["SelectionChanged", "import pairSelect as ps\nps.job()"])
        toggleIcon()
        message('Pair Selection ON', maya=True)


def toggleIcon(off=False):
    p = Get()
    global id
    # List shelf buttons
    buttons = cmds.lsUI(type='shelfButton')
    # interate through buttons to find one using appropriate images
    for btn in buttons:
        img = cmds.shelfButton(btn, q=1, image=1)
        if img in p.iconOff or img in p.iconOn:
            if off:
                cmds.shelfButton(btn, edit=True, image=p.iconOff)
            else:
                if id:
                    cmds.shelfButton(btn, edit=True, image=p.iconOn)
                else:
                    cmds.shelfButton(btn, edit=True, image=p.iconOff)
