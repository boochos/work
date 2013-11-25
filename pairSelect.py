import os
import maya.cmds as cmds
import maya.mel as mel

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

class Get():
    def __init__ (self):
        self.iconPath  = 'C:/Users/Sebastian/Documents/maya/2013-x64/prefs/icons'
        self.iconOn    = self.iconPath + '/srv_mirSel_on_icon.xpm'
        self.iconOff   = self.iconPath + '/srv_mirSel_off_icon.xpm'
        self.rootPath  = "C:/Users/Sebastian/Documents/maya/scripts"
        self.pairPath  = self.rootPath + "/faceRig_selection_pair.txt"

def nameSpace(ns = '', base=False):
    if ':' in ns:
        i = ns.rfind(':')
        ref  = ns[:i]
        obj = ns[i+1:]
        if base == False:
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
    p = Get()
    pairList = []
    pair = []
    lf = True
    #load pairs
    for line in open(p.pairPath).readlines():
        line = line.strip('\n')
        if lf:
            pair.append(line)
            lf = False
        else:
            pair.append(line)
            pairList.append(pair)
            pair= []
            lf = True
    #find pairs od selection
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        proceed = undoSel()
        if proceed:
            sel = sel[len(sel)-1]
            if ':' in sel:
                i = sel.rfind(':')
                ref  = sel[:i]
                obj = sel[i+1:]
            else:
                ref = None
                obj = sel
            for p in pairList:
                if obj in p:
                    p.remove(obj)
                    if ref:
                        selPair = ref + ':' + p[0]
                    else:
                        selPair = p[0]
                    cmds.select(selPair, tgl=True)
                    message('Pair Selected', maya=True)
                    break
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

#global id for script job
id = None

def toggleJob():
    p = Get()
    global id
    if id:
        killJob()
        cmds.scriptJob( kill=id, force=True)
        id = None
        toggleIcon()
        message('Pair Selection OFF', maya=True)
    else:
        killJob()
        id = cmds.scriptJob( e= ["SelectionChanged", "import pairSelect as ps\nps.job()"])
        toggleIcon()
        message('Pair Selection ON', maya=True)
        
def toggleIcon(off=False):
    p = Get()
    global id
    #List all the layouts in Maya
    controlLayouts = cmds.lsUI(controls = True)
    #interate through the layouts and find the shelves
    for control in controlLayouts:
        if control == 'Custom' or control == 'Rendering':
            children = cmds.shelfLayout(control, query = True, ca = True)
            if children:
                for child in children:
                    #find that shelfButton that's using the appropriate image, then change it
                    getImage = cmds.shelfButton(child, query = True, image = True)
                    if getImage == p.iconOff or getImage == p.iconOn:
                        if off:
                            cmds.shelfButton(child, edit = True, image = p.iconOff)
                        else:
                            if id:
                                cmds.shelfButton(child, edit = True, image = p.iconOn)
                            else:
                                cmds.shelfButton(child, edit = True, image = p.iconOff)