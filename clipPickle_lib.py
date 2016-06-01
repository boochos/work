import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import time
import getpass
import os
import platform
import json
import math
import webrImport as web
# web
cpb = web.mod('clipPickleBezier2_lib')
# TODO: add new class to deal with multi ref selections


def curveNodeFromName(crv=''):
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(crv)
    dependNode = OpenMaya.MObject()
    selectionList.getDependNode(0, dependNode)
    crvNode = OpenMayaAnim.MFnAnimCurve(dependNode)
    return crvNode


def selectionToNodes():
    objects = OpenMaya.MObjectArray()
    # get a list of the currently selected items
    selected = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selected)
    # iterate through the list of items returned
    for i in range(selected.length()):
        obj = OpenMaya.MObject()
        # returns the i'th selected dependency node
        selected.getDependNode(i, obj)
        if (obj.hasFn(OpenMaya.MFn.kTransform)):
            trans = OpenMaya.MFnTransform(obj)
            objects.append(obj)
            # Attach a function set to the selected object
            fn = OpenMaya.MFnDependencyNode(obj)
            # write the object name to the script editor
            # OpenMaya.MGlobal.displayInfo( fn.name() )
    return objects


def nameToNode(name):
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(name)
    node = OpenMaya.MObject()
    selectionList.getDependNode(0, node)
    return node


def nameToNodePlug(attrName, nodeObject):
    depNodeFn = OpenMaya.MFnDependencyNode(nodeObject)
    attrObject = depNodeFn.attribute(attrName)
    plug = OpenMaya.MPlug(nodeObject, attrObject)
    return plug


def plugToAnimCurve(plug):
    con = OpenMaya.MPlugArray()
    # print con.length()
    plug.connectedTo(con, True, False)
    # print con.length()
    plugNum = con.length()
    # print plugNum
    n = con[0].node()
    if n:
        if n.hasFn(OpenMaya.MFn.kAnimCurve):
            animCurveNode = OpenMayaAnim.MFnAnimCurve(n)
            return animCurveNode


def transformTangentType(t=0):
    '''
    api query type returns int, function translates to cmds compatible
    '''
    if t == 11:
        return 'auto'
    if t == 8:
        return 'clamped'
    if t == 1:
        return 'fixed'
    if t == 3:
        return 'flat'
    if t == 2:
        return 'linear'
    if t == 9:
        return 'plateau'
    if t == 4:
        return 'spline'
    if t == 5:
        return 'step'
    if t == 10:
        return 'stepNext'
    else:
        return 'auto'

'''
# https://nccastaff.bournemouth.ac.uk/jmacey/RobTheBloke/www/research/maya/mfnanimcurve.htm
'''


def transformRotationType(object='', rooNew=0):
    #-------------------------------------------
    # Part 1:  Get a MMatrix from an object for the sake of the example.
    # You can use your own MMatrix if it already exists of course.
    # Get the node's rotate order value:
    node = cmds.ls(sl=1)[0]
    rotOrder = cmds.getAttr('%s.rotateOrder' % object)
    print rotOrder
    # Get the world matrix as a list
    matrixList = cmds.getAttr('%s.worldMatrix' % object)  # len(matrixList) = 16
    # Create an empty MMatrix:
    mMatrix = OpenMaya.MMatrix()  # MMatrix
    # And populate the MMatrix object with the matrix list data:
    OpenMaya.MScriptUtil.createMatrixFromList(matrixList, mMatrix)
    #-------------------------------------------
    # Part 2, get the euler values
    # Convert to MTransformationMatrix to extract rotations:
    mTransformMtx = OpenMaya.MTransformationMatrix(mMatrix)
    # Get an MEulerRotation object
    eulerRot = mTransformMtx.eulerRotation()  # MEulerRotation
    # Update rotate order to match original object, since the orig MMatrix has
    # no knoweldge of it:
    eulerRot.reorderIt(rooNew)
    # Convert from radians to degrees:
    angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]
    print angles, "MMatrix"
    return angles


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def uiEnable(controls='modelPanel'):
    model = cmds.lsUI(panels=True, l=True)
    ed = []
    for m in model:
        # print m
        if controls in m:
            ed.append(m)
    # ed sometimes contains modelPanels that arent attached to anything, use
    # loop with try to filter them out
    state = False
    for item in ed:
        try:
            state = cmds.control(item, q=1, m=1)
            # print item
            break
        except:
            pass
    for p in ed:
        if cmds.modelPanel(p, q=1, ex=1):
            r = cmds.modelEditor(p, q=1, p=1)
            if r:
                cmds.control(p, e=1, m=not state)


class Key():

    def __init__(self, obj='', attr='', crv='', frame=0.0, offset=0, weightedTangents=None, auto=True, i=0, c=[]):
        # BUG: tangent angles are being overridden by something
        # BUG: if clip doesnt have a key, just pose value, no key is set,, pose may be lost once current frame is changed
        self.obj = obj
        self.attr = attr
        self.frame = frame
        self.i = i
        if c:
            self.crvApi = c[0]
        self.value = None
        self.crv = crv
        self.weightedTangents = weightedTangents
        self.weightLock = False
        self.inTangentType = None
        self.inWeight = None
        self.inAngle = None
        self.outTangentType = None
        self.outWeight = None
        self.outAngle = None
        self.lock = None
        self.offset = offset
        self.auto = auto
        '''
        if self.auto:
            self.getKey()
        '''

    def get(self):
        if self.auto:
            # self.getKey()
            self.getKeyApi()

    def getKey(self):
        self.value = cmds.keyframe(self.crv, q=True, time=(self.frame, self.frame), valueChange=True, a=True)[0]
        self.inAngle = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inAngle=True)[0]
        self.outAngle = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outAngle=True)[0]
        self.inTangentType = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inTangentType=True)[0]
        self.outTangentType = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outTangentType=True)[0]
        self.lock = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), lock=True)[0]
        if self.weightedTangents:
            self.weightLock = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), weightLock=True)[0]
            self.inWeight = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inWeight=True)[0]
            self.outWeight = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outWeight=True)[0]

    def getKeyApi(self):
        '''
        # curve types
        # pref dependant
        # returns are assumed to be in radians for angles and centimeteres for distance
        0 = TA time to angle = angular
        1 = TL time to linear = distance
        2 = TT time to time = ?
        4 = TU time to unitless
        # also
        # UA unitless to angular
        # UL unitless to linear
        # UT unitless to time
        # UU unitless to unitless
        '''
        # for value attr, make unit conversions for individual curve types
        if self.crvApi.animCurveType() == 0:  # angular
            ui = OpenMaya.MAngle.uiUnit()
            unit = OpenMaya.MAngle(self.crvApi.value(self.i))
            self.value = unit.asUnits(ui)
            # self.value = self.crvApi.value(self.i) * 180 / math.pi # from radians to angles
        elif self.crvApi.animCurveType() == 1:  # distance
            ui = OpenMaya.MDistance.uiUnit()
            unit = OpenMaya.MDistance(self.crvApi.value(self.i))
            self.value = unit.asUnits(ui)
            # self.value = self.crvApi.value(self.i)
        else:  # all other cases until further notice
            self.value = self.crvApi.value(self.i)

        # in angle, weight
        # FIXME: sometimes doesnt work, first key angle is often stored wrong incorrectly, perhaps type is also wrong
        tangentAngle = OpenMaya.MAngle()
        scriptUtil = OpenMaya.MScriptUtil()
        curveWeightPtr = scriptUtil.asDoublePtr()
        self.crvApi.getTangent(self.i, tangentAngle, curveWeightPtr, True)
        self.inAngle = tangentAngle.asDegrees()
        inw = scriptUtil.getDouble(curveWeightPtr)
        # out angle, weight
        tangentAngle = OpenMaya.MAngle()
        scriptUtil = OpenMaya.MScriptUtil()
        curveWeightPtr = scriptUtil.asDoublePtr()
        self.crvApi.getTangent(self.i, tangentAngle, curveWeightPtr, False)
        self.outAngle = tangentAngle.asDegrees()
        outw = scriptUtil.getDouble(curveWeightPtr)
        # tangent types
        self.inTangentType = transformTangentType(t=self.crvApi.inTangentType(self.i))
        self.outTangentType = transformTangentType(t=self.crvApi.outTangentType(self.i))

        self.lock = self.crvApi.tangentsLocked(self.i)
        if self.weightedTangents:
            self.weightLock = self.crvApi.weightsLocked(self.i)
            self.inWeight = inw
            self.outWeight = outw

    def putKey(self):
        # set key, creates curve node
        # print self.obj, self.attr, self.frame, self.offset, self.value,
        # '_____________________________'
        if cmds.getAttr(self.obj + '.' + self.attr, se=True):
            s = cmds.setKeyframe(self.obj, at=self.attr, time=(
                self.frame + self.offset, self.frame + self.offset), value=self.value, shape=False)
            if s:
                # update curve name, set curve type, set weights
                self.crv = cmds.findKeyframe(self.obj, at=self.attr, c=True)[0]
                cmds.keyframe(self.crv, time=(self.frame + self.offset, self.frame +
                                              self.offset), valueChange=self.value)  # correction, hacky, should fix
                cmds.setAttr(self.crv + '.weightedTangents', self.weightedTangents)
                cmds.keyTangent(self.crv, edit=True, time=(self.frame + self.offset, self.frame + self.offset),
                                inTangentType=self.inTangentType, outTangentType=self.outTangentType)
                if self.inAngle != None:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), inAngle=self.inAngle)
                if self.outAngle != None:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), outAngle=self.outAngle)
                if self.lock == True or self.lock == False:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), lock=self.lock)
                if self.weightedTangents:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), weightLock=self.weightLock)
                    if self.inWeight != None:
                        cmds.keyTangent(self.crv, edit=True, time=(
                            self.frame + self.offset, self.frame + self.offset), inWeight=self.inWeight)
                    if self.outWeight != None:
                        cmds.keyTangent(self.crv, edit=True, time=(
                            self.frame + self.offset, self.frame + self.offset), outWeight=self.outWeight)
            else:
                # message('Unable to add animation to ' + self.obj + '.' + self.attr)
                pass


class Attribute(Key):

    def __init__(self, obj='', attr='', offset=0, auto=True, poseOnly=False, settable=False):
        '''
        add get/put keys from Key class to this one
        '''
        self.obj = obj
        self.name = attr
        self.crv = None
        # print self.crv
        self.frames = []
        self.keys = []
        self.value = None
        self.offset = offset
        self.preInfinity = None
        self.postInfinity = None
        self.weightedTangents = None
        self.baked = False
        self.settable = settable
        self.auto = auto
        self.poseOnly = poseOnly
        '''
        if auto:
            self.getCurve()
        '''

    def get(self):
        #
        self.value = cmds.getAttr(self.obj + '.' + self.name)
        if not self.poseOnly:
            self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)
            if self.auto:
                self.getCurve()

    def getCurve(self):
        if self.crv:
            if len(self.crv) == 1:
                self.crv = self.crv[0]
                self.getCurveAttrs()
                self.getFrames()  # can be removed, only used once to feed next function
                # self.getKeys()  # convert to api
                self.getKeysApi()

    def getCurveAttrs(self):
        self.preInfinity = cmds.getAttr(self.crv + '.preInfinity')
        self.postInfinity = cmds.getAttr(self.crv + '.postInfinity')
        self.weightedTangents = cmds.getAttr(self.crv + '.weightedTangents')

    def getFrames(self):
        if self.crv:
            self.getCurveAttrs()
            framesTmp = cmds.keyframe(self.crv, q=True)
            for frame in framesTmp:
                self.frames.append(frame)
            self.frames = list(set(self.frames))
            self.frames.sort()

    def getKeys(self):
        for frame in self.frames:
            a = Key(self.obj, self.name, self.crv, frame,
                    weightedTangents=self.weightedTangents)
            a.get()
            self.keys.append(a)

    def getKeysApi(self):
        # node = nameToNode(self.obj)
        # plug = nameToNodePlug(self.name, node)
        # crv = plugToAnimCurve(plug)
        if self.crv:
            # print self.crv
            # print self.name
            c = []
            crvApi = curveNodeFromName(self.crv)
            c.append(crvApi)
            for i in range(crvApi.numKeys()):
                a = Key(self.obj, self.name, self.crv, crvApi.time(i).value(),
                        weightedTangents=self.weightedTangents, i=i, c=c)
                a.get()
                del a.crvApi
                self.keys.append(a)

    def putCurve(self):
        if not self.poseOnly:
            if self.keys:
                for k in self.keys:
                    k.obj = self.obj
                    k.offset = self.offset
                    k.crv = self.crv
                    # make sure attr exists, is not locked
                    if cmds.objExists(self.obj + '.' + self.name):
                        if not cmds.getAttr(self.obj + '.' + self.name, l=True):
                            k.putKey()
                            self.putCurveAttrs()
                    else:
                        # print 'obj doesnt exist', self.obj + '.' + self.name
                        pass
            else:
                # print 'no keys'
                self.putAttr()
        else:
            self.putAttr()

    def putAttr(self):
        # print self.obj, self.name
        if cmds.objExists(self.obj + '.' + self.name):
            if not cmds.getAttr(self.obj + '.' + self.name, l=True):
                if cmds.getAttr(self.obj + '.' + self.name, se=True):
                    # TODO: set attr does not make a key, pose is lost if live scene has keys
                    # should set key if curve exists in scene, or inform user or potential problem
                    # TODO: on clicking clip, find potential problems, try and find a remedy
                    # TODO: replace parts of clip feature, manual value attr change
                    # TODO: auto refresh ui for new files
                    try:
                        cmds.setAttr(self.obj + '.' + self.name, self.value)
                    except:
                        message('setAttr failed on  ' + self.obj + '.' + self.name)

    def putCurveAttrs(self):
        # need to update curve name, isnt the same as stored, depends on how
        # curves and layers are ceated
        self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)
        if self.crv:
            self.crv = self.crv[0]
            cmds.setAttr(self.crv + '.preInfinity', self.preInfinity)
            cmds.setAttr(self.crv + '.postInfinity', self.postInfinity)


class Obj(Attribute):

    def __init__(self, obj='', offset=0, poseOnly=False, bakeRange=[0, 0]):
        self.name = obj
        self.offset = offset
        self.attributes = []
        self.attributesDriven = []
        self.poseOnly = poseOnly
        self.bakeRange = bakeRange
        '''
        self.getAllDriven()
        self.getAttribute()
        self.getBakedAttribute()
        '''

    def get(self):
        self.getAllDriven()
        self.getAttribute()
        self.getBakedAttribute()

    def getAttribute(self):
        # if lattice point is selected, returning list is 'attr.attr'
        keyable = cmds.listAttr(self.name, k=True, s=True)
        if keyable:
            for attr in keyable:
                if attr not in self.attributesDriven:
                    # hacky -- if attr.attr format, remove first attr
                    if '.' in attr:
                        attr = attr.split('.')[1]
                    a = Attribute(self.name, attr, poseOnly=self.poseOnly)
                    a.get()
                    self.attributes.append(a)
        settable = cmds.listAttr(self.name, cb=True)  # future fix, make part of one pass, current code copied from above
        if settable:
            for attr in settable:
                if attr not in self.attributesDriven:
                    # hacky -- if attr.attr format, remove first attr
                    if '.' in attr:
                        attr = attr.split('.')[1]
                    a = Attribute(self.name, attr, poseOnly=self.poseOnly, settable=True)
                    a.get()
                    self.attributes.append(a)

    def getBakedAttribute(self):
        if self.attributesDriven:
            # turn off UI
            # uiEnable()
            # create frame list from frame range
            min = self.bakeRange[0]  # cmds.playbackOptions(q=True, ast=True)
            max = self.bakeRange[1]  # cmds.playbackOptions(q=True, aet=True)
            # print self.bakeRange
            # print min, max
            rng = range(int(min), int(max + 1))
            rng = [float(i) for i in rng]
            # instantiate class for every driven attr
            attributesBaked = []
            for a in self.attributesDriven:
                attr = Attribute(self.name, a, auto=False, poseOnly=self.poseOnly)
                attr.get()
                attr.preInfinity = 0
                attr.postInfinity = 0
                attributesBaked.append(attr)
            # loop through frames and add key class manually for all attrs
            current = cmds.currentTime(q=True)
            for frame in rng:
                # move to frame
                cmds.currentTime(frame)
                for attr in attributesBaked:
                    # get value of attribute from maya
                    val = cmds.getAttr(self.name + '.' + attr.name)
                    # store value in attr class, instantiate Key class
                    k = Key(
                        self.name, attr.name, '', frame, weightedTangents=False, auto=False)
                    # print self.name, attr.name, '____BAKED____'
                    k.get()
                    k.value = val
                    k.inTangentType = 'auto'
                    k.outTangentType = 'auto'
                    attr.keys.append(k)
            for attr in attributesBaked:
                self.attributes.append(attr)
            # restore current frame
            cmds.currentTime(current)
            # turn on UI
            # uiEnable()
        else:
            # message('nothing to bake', maya=True)
            pass

    def getDrivers(self, obj, typ='', plugs=True):
        # Returns nodes that are driving given node
        # typ=return only node types
        # plugs=True will return with driving attribute(s)
        con = cmds.listConnections(obj, d=False, s=True, t=typ, plugs=plugs)
        if con:
            con = list(set(con))
        return con

    def getDriven(self, obj, typ='', plugs=True):
        # Returns nodes that are driven by given node
        # typ=return only node types
        # plugs=True will return with driven attribute(s)
        con = cmds.listConnections(obj, s=False, d=True, t=typ, plugs=plugs)
        if con:
            con = list(set(con))
        return con

    def getDrivenAttrsByType(self, typ=''):
        # Returns attributes of the given object which are driven by a node
        # type
        drivers = self.getDrivers(self.name, typ=typ, plugs=True)
        driven = []
        if drivers:
            for driver in drivers:
                driven.append(
                    self.getDriven(driver, typ='', plugs=True)[0].split('.')[1])
            return sorted(driven)
        else:
            return None

    def getAllDriven(self, types=['constraint', 'pairBlend', 'expression']):
        # set driven not supported
        self.attributesDriven = []
        for t in types:
            con = self.getDrivenAttrsByType(typ=t)
            if con:
                for c in con:
                    self.attributesDriven.append(c)

    def putAttribute(self):
        # print self.name, '__________________________putAttr'
        for attr in self.attributes:
            attr.obj = self.name
            attr.offset = self.offset
            attr.putCurve()
            # print attr.obj


class Layer(Obj):

    def __init__(self, sel=[], name=None, offset=0, ns=None, comment='', poseOnly=False, bakeRange=[0, 0]):
        '''
        can use to copy and paste animation
        '''
        self.sel = sel
        self.start = None
        self.end = None
        self.length = None
        self.comment = comment
        self.objects = []
        self.offset = offset
        self.ns = ns
        self.poseOnly = poseOnly
        self.bakeRange = bakeRange
        # layer attrs
        self.name = name
        self.mute = None
        self.solo = None
        self.lock = None
        self.ghost = None
        self.ghostColor = None
        self.override = None
        self.passthrough = None
        self.weight = None
        self.rotationAccumulationMode = None  # test if enums work
        self.scaleAccumulationMode = None
        #
        '''
        self.getObjects()
        self.getLayerAttrs()
        self.getStartEndLength()
        '''

    def get(self):
        self.getObjects()
        self.getLayerAttrs()
        self.getStartEndLength()

    def getObjects(self):
        num = len(self.sel)
        i = 1
        uiEnable()
        for obj in self.sel:
            message(str(i) + ' of ' + str(num) + ' --  ' + obj, maya=True)
            cmds.refresh(f=1)
            a = Obj(obj, poseOnly=self.poseOnly, bakeRange=self.bakeRange)
            a.get()
            self.objects.append(a)
            i = i + 1
        uiEnable()

    def getStartEndLength(self):
        frames = []
        for obj in self.objects:
            for attr in obj.attributes:
                if len(attr.keys) > 0:
                    for k in attr.keys:
                        frames.append(k.frame)
        frames = sorted(list(set(frames)))
        if frames:
            self.start = frames[0]
            self.end = frames[len(frames) - 1]
            self.length = self.end - self.start + 1

    def getLayerAttrs(self):
        if self.name:
            self.mute = cmds.getAttr(self.name + '.mute')
            self.solo = cmds.getAttr(self.name + '.solo')
            self.lock = cmds.getAttr(self.name + '.lock')
            self.ghost = cmds.getAttr(self.name + '.ghost')
            self.ghostColor = cmds.getAttr(self.name + '.ghostColor')
            self.override = cmds.getAttr(self.name + '.override')
            self.passthrough = cmds.getAttr(self.name + '.passthrough')
            self.weight = Attribute(self.name, 'weight')
            self.weight.get()
            self.rotationAccumulationMode = cmds.getAttr(
                self.name + '.rotationAccumulationMode')
            self.scaleAccumulationMode = cmds.getAttr(
                self.name + '.scaleAccumulationMode')

    def putObjects(self, atCurrentFrame=False):
        # print self.sel
        # print self.putObjectList
        autoKey = cmds.autoKeyframe(q=True, state=True)
        cmds.autoKeyframe(state=False)
        # current #NO LONGER USED, REMOVE ONCE MERGED WITH WORK COPY OF KET
        # CLASS
        if atCurrentFrame:
            current = cmds.currentTime(q=True)
            if self.start > current:
                self.offset = current - self.start
            else:
                self.offset = ((self.start - current) * -1.0) + 0.0
            # print self.offset
        # put
        num = len(self.objects)
        i = 1
        uiEnable()
        for obj in self.objects:
            if cmds.objExists(obj.name):
                message(str(i) + ' of ' + str(num) + ' --  ' + obj.name, maya=True)
                cmds.refresh(f=1)
                obj.offset = self.offset
                obj.putAttribute()
            else:
                cmds.warning(
                    'Object   ' + obj.name + '   does not exist, skipping.')
            i = i + 1
        uiEnable()
        cmds.autoKeyframe(state=autoKey)

    def putLayerAttrs(self):
        # static attrs
        cmds.setAttr(self.name + '.mute', self.mute)
        cmds.setAttr(self.name + '.solo', self.solo)
        cmds.setAttr(self.name + '.lock', self.lock)
        cmds.setAttr(self.name + '.ghost', self.ghost)
        cmds.setAttr(self.name + '.ghostColor', self.ghostColor)
        cmds.setAttr(self.name + '.override', self.override)
        cmds.setAttr(self.name + '.passthrough', self.passthrough)
        cmds.setAttr(
            self.name + '.rotationAccumulationMode', self.rotationAccumulationMode)
        cmds.setAttr(
            self.name + '.scaleAccumulationMode', self.scaleAccumulationMode)
        # animated attrs
        self.weight.offset = self.offset
        self.weight.obj = self.name
        self.weight.putCurve()


class Clip(Layer):

    def __init__(self, name='', comment='', poseOnly=False, bakeRange=[0, 0]):
        self.sel = None
        #
        self.name = name
        self.comment = comment
        self.poseOnly = poseOnly
        self.bakeRange = bakeRange
        self.source = None
        self.path = None
        self.user = None
        self.date = None
        #
        self.start = None
        self.end = None
        self.length = None
        self.layers = []  # list of class layers
        self.layerNames = None
        self.rootLayer = None
        # set on import of clip
        self.offset = 0  # import
        '''
        self.getLayers()
        self.getClipAttrs()
        self.getClipStartEndLength()
        '''

    def get(self):
        # timer start
        start = cmds.timerX()
        #
        self.sel = cmds.ls(sl=True, fl=True)
        self.user = getpass.getuser()
        self.date = time.strftime("%c")
        self.getLayers()
        self.getClipAttrs()
        self.getClipStartEndLength()
        # timer end
        # code that is being timed
        totalTime = cmds.timerX(startTime=start)
        print "------------  Total time: ", totalTime

    def getClipAttrs(self):
        # scene name
        sceneName = cmds.file(q=True, sn=True)
        self.path = sceneName
        self.source = sceneName[sceneName.rfind('/') + 1:]

    def getLayers(self):
        # get layers in scene
        # should consider reversing order
        self.layerNames = cmds.ls(type='animLayer')
        self.rootLayer = cmds.animLayer(q=True, root=True)
        if self.layerNames:
            for layer in self.layerNames:
                # collect objects in layer
                currentLayerMembers = []
                connected = cmds.listConnections(
                    layer, s=1, d=0, t='transform')
                if connected:
                    objects = list(set(connected))
                    for s in self.sel:
                        if s in objects:
                            currentLayerMembers.append(s)
                    if currentLayerMembers:
                        self.setActiveLayer(layer)
                        # build class
                        # print layer, '_________'
                        clp = Layer(
                            name=layer, sel=currentLayerMembers, comment=self.comment, poseOnly=self.poseOnly, bakeRange=self.bakeRange)
                        clp.get()
                        self.layers.append(clp)
                else:
                    print layer, '     no members'
            self.setActiveLayer(l=self.rootLayer)
            # build root layer class
            clp = Layer(sel=self.sel, comment=self.comment, poseOnly=self.poseOnly, bakeRange=self.bakeRange)
            clp.get()
            self.layers.append(clp)
        else:
            # no anim layers, create single layer class
            clp = Layer(name=None, sel=self.sel, comment=self.comment, poseOnly=self.poseOnly, bakeRange=self.bakeRange)
            clp.get()
            self.layers.append(clp)
        # print self.putLayerList

    def getClipStartEndLength(self):
        for layer in self.layers:
            if not self.start:
                self.start = layer.start
                self.end = layer.end
            else:
                if layer.start < self.start:
                    self.start = layer.start
                if layer.end > self.end:
                    self.end = layer.end
        if self.start and self.end:
            self.length = self.end - self.start + 1

    def setActiveLayer(self, l=None):
        # maya 2014, this does not activate layer: cmds.animLayer( ex, e=True, sel=False )
        # need to source mel script, otherwise selectLayer command doesn't exist
        # source "C:/Program
        # Files/Autodesk/Maya2014/scripts/startup/buildSetAnimLayerMenu.mel";
        mel.eval('source "buildSetAnimLayerMenu.mel";')
        if l:
            mel.eval('selectLayer(\"' + l + '\");')
        else:
            mel.eval('selectLayer(\"");')

    def layerAddObjects(self, layer='', objects=[]):
        # set layer to current
        self.setActiveLayer(l=layer)
        if objects:
            for obj in objects:
                if cmds.objExists(obj.name):
                    cmds.select(obj.name)
                    print '___adding here'
                    print layer
                    cmds.animLayer(layer, e=True, aso=True)

    def layerNew(self, name='', prefix='CLASH__'):
        i = 0
        prfx = prefix
        while cmds.animLayer(prfx + name, q=True, ex=True) == True:
            prfx = prfx + prefix
            i = i+1
            if i == 100:
                break
        cmds.animLayer(prfx + name)
        return prfx + name

    def putLayers(self, mergeExistingLayers=True, applyLayerSettings=True, applyRootAsOverride=False):
        # restore layers from class
        clash = 'CLASH__'
        for layer in self.layers:
            # set import options
            layer.offset = self.offset
            sceneRootLayer = cmds.animLayer(q=True, root=True)
            # check if iteration is root layer, root layer name = None
            if not layer.name:
                if not applyRootAsOverride:
                    self.setActiveLayer(l=sceneRootLayer)
                else:
                    # creates new name for base layer
                    layer.name = self.layerNew(name='BaseAnimation')
                    cmds.setAttr(layer.name + '.override', True)
                    self.layerAddObjects(layer=layer.name, objects=layer.objects)
                layer.putObjects()
            else:
                if not cmds.animLayer(layer.name, q=True, ex=True):
                    # create layer
                    cmds.animLayer(layer.name)
                else:
                    # print mergeExistingLayers
                    if not mergeExistingLayers: # dont merge with existing layer of same name
                        if not cmds.animLayer(clash + layer.name, q=True, ex=True):
                            # update name in class with clashing prefix
                            layer.name = cmds.animLayer(clash + layer.name)
                            message('Layer ' + layer.name + ' already exists')
                        else:
                            layer.name = clash + layer.name
                            # message( 'Layer ' + layer.name + ' already exists' )
                            pass
                            # break
                # set layer attrs
                if applyLayerSettings:
                    layer.putLayerAttrs()
                # set layer to current
                self.setActiveLayer(l=layer.name)
                if layer.objects:
                    for obj in layer.objects:
                        if cmds.objExists(obj.name):
                            cmds.select(obj.name)
                            cmds.animLayer(layer.name, e=True, aso=True)
                
                # should check if layer is empty, no objects exist in scene that existed during export, should delete if layer is empty or putObjects
                # add animation
                layer.putObjects()


def clipSave(name='clipTemp', comment='', poseOnly=False, temp=False, bakeRange=[0, 0]):
    '''
    save clip to file
    '''
    path = clipPath(name=name + '.clip', temp=temp)
    clp = Clip(name=name, comment=comment, poseOnly=poseOnly, bakeRange=bakeRange)
    clp.get()
    # print clp.name
    fileObjectJSON = open(path, 'wb')
    # pretty encoding
    json.dump(clp, fileObjectJSON, default=to_json, indent=1)
    # compact encoding
    # json.dump(clp, fileObjectJSON, default=to_json, separators=(',', ':'))
    fileObjectJSON.close()


def clipOpen(path=''):
    '''
    open clip form file
    '''
    fileObjectJSON = open(path, 'r')
    clpJSON = json.load(fileObjectJSON, object_hook=from_json)
    # print clpJSON.__dict__, '   reconstructed'
    fileObjectJSON.close()
    return clpJSON


def to_json(python_object):
    if isinstance(python_object, Clip):
        return {'__class__': 'Clip',
                '__value__': python_object.__dict__}
    if isinstance(python_object, Layer):
        return {'__class__': 'Layer',
                '__value__': python_object.__dict__}
    if isinstance(python_object, Obj):
        return {'__class__': 'Obj',
                '__value__': python_object.__dict__}
    if isinstance(python_object, Attribute):
        return {'__class__': 'Attribute',
                '__value__': python_object.__dict__}
    if isinstance(python_object, Key):
        return {'__class__': 'Key',
                '__value__': python_object.__dict__}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object:
        if json_object['__class__'] == 'Clip':
            # !!! decoding breaks here !!!
            # print 'Clip'
            clp = Clip()
            clp = populate_from_json(clp, json_object['__value__'])
            return clp
            # return Clip(**json_object['__value__'])
        if json_object['__class__'] == 'Layer':
            # print 'Layer'
            lyr = Layer()
            lyr = populate_from_json(lyr, json_object['__value__'])
            return lyr
            # return Layer(**json_object['__value__'])
        if json_object['__class__'] == 'Obj':
            # print 'Obj'
            obj = Obj()
            obj = populate_from_json(obj, json_object['__value__'])
            return obj
            # return Obj(**json_object['__value__'])
        if json_object['__class__'] == 'Attribute':
            # print 'Attribute'
            attr = Attribute()
            attr = populate_from_json(attr, json_object['__value__'])
            return attr
            # return Attribute(**json_object['__value__'])
        if json_object['__class__'] == 'Key':
            # print 'Key'
            key = Key()
            key = populate_from_json(key, json_object['__value__'])
            return key
            # return Key(**json_object['__value__'])
    return json_object


def populate_from_json(cls, dct={}):
    for key in dct:
        try:
            getattr(cls, key)
        except AttributeError:
            pass
            # print "Doesn't exist"
        else:
            setattr(cls, key, dct[key])
    return cls


def clipApply(path='', ns=True, onCurrentFrame=True, mergeExistingLayers=True, applyLayerSettings=True, applyRootAsOverride=False, 
              putLayerList=[], putObjectList=[], start=None, end=None, poseOnly=False):
    '''
    apply animation from file
    #FIX: note <>
    need to add option to import on existing layer with same name,
    add option to not apply layer settings to layers with same name,
    apply to selected object no matter what name discrepancies exist
    '''
    # BUG:linear curves don't import correctly
    # TODO: apply should only take name, path should be predetermined
    # update all other functions that use the behaviour
    sel = cmds.ls(sl=1, fl=1)
    # set import attrs
    clp = clipOpen(path=path)
    # print clp.__dict__
    if onCurrentFrame:
        clp.offset = onCurrentFrameOffset(start=clp.start)
    if ns:
        clp = putNS(clp)
    if putObjectList:
        clp = pruneObjects(clp, putObjectList)  # not working
    if putLayerList:
        clp = pruneLayers(clp, putLayerList)  # working
    # set type of import
    clp = setType(clp, poseOnly=poseOnly)
    # frame range
    if clp.start != start or clp.end != end:
        clp = cutKeysToRange(clp, start, end)
    clp.putLayers(mergeExistingLayers, applyLayerSettings, applyRootAsOverride)
    # print clp.layers
    if sel:
        cmds.select(sel)


def clipPath(name='', temp=False):
    if temp:
        path = clipDefaultTempPath()
    else:
        path = clipDefaultPath()
    if os.path.isdir(path):
        return os.path.join(path, name)
    else:
        os.mkdir(path)
        return os.path.join(path, name)


def clipDefaultPath():
    # print os.name
    varPath = cmds.internalVar(userAppDir=True)
    path = os.path.join(varPath, 'clipLibrary')
    # print path
    return path


def clipDefaultTempPath():
    varPath = cmds.internalVar(userAppDir=True)
    path = os.path.join(varPath, 'clipTemp')
    return path


def onCurrentFrameOffset(start=0.0):
    if start:
        current = cmds.currentTime(q=True)
        offset = 0.0
        if start > current:
            offset = current - start
        else:
            offset = ((start - current) * -1.0) + 0.0
        # print offset
        return offset
    else:
        return 0.0


def insertKey(clp, frame=0.0):
    for layer in clp.layers:
        for obj in layer.objects:
            for attr in obj.attributes:
                if attr.crv:
                    # make sure no key exists on given frame, add short form
                    # loop, if it does dont overwrite
                    # find appropriate value
                    k = insertKeyValue(attr, frame)
                    print k.frame
                    attr.keys.append(k)
                else:
                    # print 'no crv exists, skipping insert'
                    pass
    return clp


def insertKeyValue(attr, frame=0.0):
    # does not consider tangents, only key positions
    val = 0.0
    i = 0
    # weighted
    weighted = attr.keys[i].weightedTangents
    # can reach end of list before finding a qualifying frame number
    # do not insert frames out of original range
    # may adversly affect offest and start positions, should investigate
    while frame > attr.keys[i].frame:
        i = i + 1
        if len(attr.keys) - 1 < i:
            print 'done'
            return None  # needs an actual value to work
    else:
        preVal = attr.keys[i - 1].value
        nexVal = attr.keys[i].value
        preFrm = attr.keys[i - 1].frame
        nexFrm = attr.keys[i].frame
        p0 = [preFrm, preVal, attr.keys[i - 1].outAngle]
        p3 = [nexFrm, nexVal, attr.keys[i].inAngle]
        corX, corY = cpb.getControlPoints(p0, p3)
        print corX, corY
        degIn, hlengthIn, value, degOut, hlengthOut = cpb.seekPoint(corX, corY, frame)
        k = Key(attr.obj, attr.name, attr.crv, frame, weightedTangents=weighted, auto=False)
        # print degIn, value, degOut, crv
        k.value = value
        k.inAngle = degIn
        k.outAngle = degOut
        k.inTangentType = 'auto'
        k.outTangentType = 'auto'
        if weighted:
            k.inWeight = hlengthIn
            k.outWeight = hlengthOut
            # adjust existing tangent weights
            ow = attr.keys[i - 1].outWeight
            iw = attr.keys[i].inWeight
            #
            gap = p3[0] - p0[0]
            #
            front = (frame - p0[0])
            back = (p3[0] - frame)
            #
            front = (time - p0[0]) / gap
            back = (p3[0] - time) / gap
            #
            attr.keys[i - 1].outWeightt = ow * front
            attr.keys[i].inWeightinWeight = iw * back
        return k


def cutKeysToRange(clp, start=None, end=None):
    if start:
        clp = insertKey(clp, start)
        clp = insertKey(clp, end)
        for layer in clp.layers:
            for obj in layer.objects:
                for attr in obj.attributes:
                    if attr.crv:
                        keys = []
                        for key in attr.keys:
                            if key.frame >= start and key.frame <= end:
                                keys.append(key)
                        if keys:
                            attr.keys = keys
    return clp


def putNS(clp):
    '''
    update namespace in clip, returns modified clip
    '''
    ns = getNS()
    if ns:
        for layer in clp.layers:
            for obj in layer.objects:
                # print obj.name
                if ':' in obj.name:
                    obj.name = replaceNS(obj=obj.name, ns=ns)
                    for attr in obj.attributes:
                        # print attr.obj
                        attr.obj = replaceNS(obj=attr.obj, ns=ns)
                        for key in attr.keys:
                            # print key.obj
                            key.obj = replaceNS(obj=key.obj, ns=ns)
    else:
        cmds.warning('No namespace in selection. Namespace cannot be updated.')
    return clp


def getNS():
    '''
    get it from selection
    FIX: why is there an extra for loop<>
    '''
    sel = cmds.ls(sl=True)
    if sel:
        for item in sel:
            if ':' in sel[0]:
                ns = sel[0].split(':')[0]
                return ns
            else:
                return None
    else:
        return None


def replaceNS(obj='', ns=''):
    '''
    obj = original object with namespace
    ns = new namespace
    '''
    result = obj.replace(obj.split(':')[0], ns)
    # print result
    return result


def pruneLayers(clp, layers=[]):
    # remove layers from clip that arent in 'layer' list arg
    isolated = []
    for layer in clp.layers:
        if layer.name in layers:
            isolated.append(layer)
    clp.layers = isolated
    return clp


def pruneObjects(clp, objects=[]):
    # remove objects from clip that arent in 'objects' list arg
    for layer in clp.layers:
        isolated = []
        for obj in layer.objects:
            if obj.name in objects:
                isolated.append(obj)
        layer.objects = isolated
        isolated = []
    return clp


def setType(clp, poseOnly=False):
    # remove objects from clip that arent in 'objects' list arg
    clp.poseOnly = poseOnly
    for layer in clp.layers:
        layer.poseOnly = poseOnly
        for obj in layer.objects:
            obj.poseOnly = poseOnly
            for attr in obj.attributes:
                attr.poseOnly = poseOnly
    return clp


def updateObjName(clp, names=[]):
    '''
    only for single object
    '''
    if len(clp.layers) == 1:
        for layer in clp.layers:
            if len(names) == len(layer.objects):
                for obj in layer.objects:
                    obj.name = names[0]
                    for attr in obj.attributes:
                        attr.obj = names[0]
                        for key in attr.keys:
                            key.obj = names[0]
                # print clp.layers[0].objects[0].name
                return clp
            else:
                message('new names list does not match object number in clip', maya=True)
    else:
        message('multi animlayers not supported', maya=True)


def selectObjectsInClip(clp):
    select = []
    for layer in clp.layers:
        for obj in layer.objects:
            if cmds.objExists(obj.name):
                select.append(obj.name)
    if select:
        cmds.select(select)


def selectObjectsInLayers(clp, layers=[]):
    select = []
    for layer in clp.layers:
        # print layer.name
        if layer.name in layers:
            for obj in layer.objects:
                if cmds.objExists(obj.name):
                    select.append(obj.name)
    if select:
        cmds.select(select)
