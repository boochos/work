import maya.cmds as cmds
from pymel.core import *
import maya.OpenMaya as OpenMaya
import datetime
from ctypes import *


class struct_timespec(Structure):
    _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]


class struct_stat64(Structure):
    _fields_ = [
        ('st_dev', c_int32),
        ('st_mode', c_uint16),
        ('st_nlink', c_uint16),
        ('st_ino', c_uint64),
        ('st_uid', c_uint32),
        ('st_gid', c_uint32),
        ('st_rdev', c_int32),
        ('st_atimespec', struct_timespec),
        ('st_mtimespec', struct_timespec),
        ('st_ctimespec', struct_timespec),
        ('st_birthtimespec', struct_timespec),
        ('dont_care', c_uint64 * 8)
    ]


def get_creation_time(path):
    libc = CDLL('libc.dylib')
    stat64 = libc.stat64
    stat64.argtypes = [c_char_p, POINTER(struct_stat64)]

    buf = struct_stat64()
    rv = stat64(path, pointer(buf))
    if rv != 0:
        raise OSError("Couldn't stat file %r" % path)
    return buf.st_birthtimespec.tv_sec


def stripNamespaceFromReferenceImport(*args):
    objs = ls(fl=True)
    for obj in objs:
        colIdx = obj.rfind(':')
        if colIdx > -1:
            if objExists(obj):
                lockNode(obj, lock=False)
                strName = str(obj)
                name = strName[colIdx + 1:]
                rename(obj, name)


def setPerspClippingPlane(*args):
    import math

    perspCam = ls('perspShape')[0]
    pCamTransformNode = perspCam.getParent()
    tran = pCamTransformNode.getTranslation()

    camXun = math.sqrt(tran[0] * tran[0])
    camYun = math.sqrt(tran[1] * tran[1])
    camZun = math.sqrt(tran[2] * tran[2])

    clipPlaneFar = camXun + camYun + camZun
    clipPlaneNear = (camXun + camYun + camZun) / 10000

    perspCam.farClipPlane.set(clipPlaneFar)
    perspCam.nearClipPlane.set(clipPlaneNear)


def distance2Pts(p1, p2):
    error = 0
    if len(p1) != 3:
        OpenMaya.MGlobal.displayError('First argument list needs to have three elements...')
        error = 1
    if len(p2) != 3:
        OpenMaya.MGlobal.displayError('Second argument list needs to have three elements...')
        error = 1

    if error != 1:
        v = [0, 0, 0]
        v[0] = p1[0] - p2[0]
        v[1] = p1[1] - p2[1]
        v[2] = p1[2] - p2[2]
        distance = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
        from math import sqrt
        distance = sqrt(distance)
        return distance
    else:
        return None

# some random shelf buttons for something I know little to nothing about


def FGC0(*args):
    sel = cmds.ls(sl=True, l=True)
    shape = None
    for item in sel:
        shape = cmds.listRelatives(item, s=True, f=True)[0]
        if shape != None:
            cmds.setAttr(shape + '.miFinalGatherCast', 0)
            print shape


def FGC1(*args):
    sel = cmds.ls(sl=True, l=True)
    shape = None
    for item in sel:
        shape = cmds.listRelatives(item, s=True, f=True)[0]
        if shape != None:
            cmds.setAttr(shape + '.miFinalGatherCast', 1)
            print shape


def FGR0(*args):
    sel = cmds.ls(sl=True, l=True)
    shape = None
    for item in sel:
        shape = cmds.listRelatives(item, s=True, f=True)[0]
        if shape != None:
            cmds.setAttr(shape + '.miFinalGatherReceive', 0)
            print shape


def FGR1(*args):
    sel = cmds.ls(sl=True, l=True)
    shape = None
    for item in sel:
        shape = cmds.listRelatives(item, s=True, f=True)[0]
        if shape != None:
            cmds.setAttr(shape + '.miFinalGatherReceive', 1)
            print shape


def shapeSize(mltp):
    '''\n
    mltp = multiplier of shape nodes
    '''
    sel = cmds.ls(sl=True, l=True)
    shape = None
    for item in sel:
        shape = cmds.listRelatives(item, s=True, f=True)
        if shape != None:
            for node in shape:
                if 'SharedAttr' not in node:
                    cmds.scale(mltp, mltp, mltp, node + '.cv[*]')


def transferPolySelectionSet(*args):
    '''
    Name        :trasferSelectionSet
    Description :Usage, select a character set then the mesh you want to
    create a newset from. This will create a new set from the currently
    select set from the mesh selection. Transferring the set information
    from oneobject to another.
    Objects must have the same vertex index for predictable results.
    '''
    if len(cmds.ls(selection=True)) == 2:
        master_set = cmds.ls(selection=True)[0]
        target = cmds.ls(sl=True)[1]
        sel_set = cmds.select(master_set)
        sel_face = cmds.ls(sl=True, fl=True)

        cmds.select(cl=True)
        selList = []
        for face in sel_face:
            faceCheck = face.find('.f')
            if faceCheck > -1:
                addFace = '%s.f%s' % (target, face.partition('.f')[2])
                selList.append(addFace)

        cmds.select(selList)
        target_set = cmds.sets(n=target + '_set')
        cmds.select(cl=True)
    else:
        print 'Need exactly two objects selected selection set, and a mesh'


def cleanCacheNodes():
    historySwitches = cmds.ls(type='historySwitch')

    for switch in historySwitches:
        his = cmds.listHistory(switch)
        for h in his:
            if cmds.objExists(h):
                if cmds.nodeType(h) != 'time':
                    cmds.delete(h)
                    OpenMaya.MGlobal.displayInfo('== %s has been deleted ==' % h)
    # begin the dumbest fucking hack ever
    # maya will delete any sets that connected to the orig node. The connection
    # only becomes visible when the Relationship Editor is open. Locking the nodes
    # prevents their deletion
    sets = cmds.ls(type='objectSet')
    for s in sets:
        # lock-em up...dumb as shitty way of doing things
        cmds.lockNode(s, l=True)
    nodes = cmds.ls(type='mesh')
    for node in nodes:
        if cmds.getAttr(node + '.intermediateObject'):
            cmds.delete(node)
            OpenMaya.MGlobal.displayInfo('== %s has been deleted ==' % node)
    # end the dumbest fucking hack ever
    for s in sets:
        # unlock the nodes
        cmds.lockNode(s, l=False)


class positionHud():
    #
    # First HUD for Cam Origin
    #

    def __init__(self, camStartObj='cam_StartPos', camOriginObj='cam_OriginPos', camAnimateObj='cam_AnimatePos', posCamStart="CAM: pos from rail on 1st frame", posCamAnimate="CAM: current pos (relative to 1st frame)"):
        namespace = 'Distance3Pnt:'
        self.camOriginObj = namespace + camOriginObj
        self.camStartObj = namespace + camStartObj
        self.camAnimateObj = namespace + camAnimateObj
        self.posCamStart = posCamStart
        self.posCamAnimate = posCamAnimate
        self.disCamOrigin = 'DISTANCE: cam from sleigh rail'
        self.disCamAnimate = 'DISTANCE: cam traveled'
        self.hud = None

    def runHud(self):
        self.displayStartHud(self.posCamStart)
        self.displayOrigDisHud(self.disCamOrigin)
        self.displayAnimateHud(self.posCamAnimate)
        self.displayAnimatedDisHud(self.disCamAnimate)

    def cmToin(self, values):
        # values is expected to be made a tuple with 3 values
        n = 'in'
        if type(values) == tuple:
            conversion = []
            axis = ['X', 'Y', 'Z']
            i = 0
            for value in values:
                tmp = cmds.convertUnit(value, fromUnit='cm', toUnit=n)
                flt = float(str(tmp).rstrip(n))
                tmp = str(round(flt, 1))
                conversion.append(axis[i] + ' = ' + tmp + n)
                i = i + 1
            return conversion
        else:
            tmp = cmds.convertUnit(values, fromUnit='cm', toUnit=n)
            flt = float(str(tmp).rstrip(n))
            tmp = str(round(flt, 1)) + n
            return tmp

    def posStart(self):
        try:
            positionList = cmds.getAttr('%s.translate' % self.camStartObj)[0]
            positionList = self.cmToin(positionList)
            return positionList
        except:
            return (0.0, 0.0, 0.0)

    def posAnimate(self):
        try:
            positionList = cmds.getAttr('%s.translate' % self.camAnimateObj)[0]
            positionList = self.cmToin(positionList)
            return positionList
        except:
            return (0.0, 0.0, 0.0)

    def disOrigin(self):
        try:
            p1 = cmds.xform(self.camOriginObj, q=True, ws=True, t=True)
            p2 = cmds.xform(self.camStartObj, q=True, ws=True, t=True)
            distance = distance2Pts(p1, p2)
            distance = self.cmToin(distance)
            return distance
        except:
            return 0

    def disAnimate(self):
        try:
            p1 = cmds.xform(self.camStartObj, q=True, ws=True, t=True)
            p2 = cmds.xform(self.camAnimateObj, q=True, ws=True, t=True)
            distance = distance2Pts(p1, p2)
            distance = self.cmToin(distance)
            return distance
        except:
            return 0

    def labelName(self, label='position'):
        sel = cmds.ls(sl=True)
        string = ''
        if len(sel) == 0:
            string = label + '  ---'
        else:
            string = label + '  ' + str(cmds.selectedNodes()[0].rsplit('|')[1])
        return string

    def displayStartHud(self, hudName):
        self.hud = hudName
        section = 4
        cmds.headsUpDisplay(hudName, rem=True)
        cmds.headsUpDisplay(
            hudName,
            section=section,
            block=cmds.headsUpDisplay(nfb=section),
            attachToRefresh=True,
            blockSize='medium',
            label=hudName,
            labelFontSize='small',
            command=self.posStart
        )

    def displayAnimateHud(self, hudName):
        self.hud = hudName
        section = 4
        cmds.headsUpDisplay(hudName, rem=True)
        cmds.headsUpDisplay(
            hudName,
            section=section,
            block=cmds.headsUpDisplay(nfb=section),
            attachToRefresh=True,
            blockSize='medium',
            label=hudName,
            labelFontSize='small',
            command=self.posAnimate
        )

    def displayOrigDisHud(self, hudName):
        self.hud = hudName
        section = 4
        cmds.headsUpDisplay(hudName, rem=True)
        cmds.headsUpDisplay(
            hudName,
            section=section,
            block=cmds.headsUpDisplay(nfb=section),
            attachToRefresh=True,
            blockSize='medium',
            label=hudName,
            labelFontSize='small',
            command=self.disOrigin
        )

    def displayAnimatedDisHud(self, hudName):
        self.hud = hudName
        section = 4
        cmds.headsUpDisplay(hudName, rem=True)
        cmds.headsUpDisplay(
            hudName,
            section=section,
            block=cmds.headsUpDisplay(nfb=section),
            attachToRefresh=True,
            blockSize='medium',
            label=hudName,
            labelFontSize='small',
            command=self.disAnimate
        )
