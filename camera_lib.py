import maya.cmds as cmds
import maya.mel as mel
import os

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def getName():
    #string find...
    a = 'anim'
    #string replace...
    c = 'camera'
    #get current file
    path = cmds.file(q=1, sn=1)
    #replace
    if a in path:
        path = path.replace(a, c)
        print path
        return path

def camTag(tag='shotCam'):
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        sel = sel[0]
        #conditions, try, exception, else(no exception)
        try:
            #select shape node
            try:
                shape = cmds.listRelatives(shapes=True)[0] #first item only
            except:
                if cmds.nodeType(sel) == 'camera':
                    shape = sel
        except:
            #if no shape node exists in selection
            message('Selection is not of camera type')
        else:
            #is shape node a camera
            if cmds.nodeType(shape) == 'camera':
                cmds.addAttr(ln=tag, at='bool', )
    else:
        message('Select 1 camera.')
        
def camEx():
    path = getName()
    #get camera to export
    cmds.file(path, force=True, options='v=0', es=True, type='mayaAscii')