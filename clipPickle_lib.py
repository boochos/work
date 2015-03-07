import maya.cmds as cmds
import maya.mel as mel
import time
import getpass
import os
import json
# TODO: add new class to deal with multi ref selections


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

    def __init__(self, obj='', attr='', crv='', frame=0.0, offset=0, weightedTangents=None, auto=True):
        # BUG: tangent angles are being overridden by something
        # BUG: if clip doesnt have a key, just pose value, no key is set,, pose may be lost once current frame is changed
        self.obj = obj
        self.attr = attr
        self.frame = frame
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
            self.getKey()

    def getKey(self):
        # print self.obj
        # print self.crv
        # print self.frame
        # print self.attr
        # print index
        self.value = cmds.keyframe(self.crv, q=True, time=(self.frame, self.frame), valueChange=True, a=True)[0]
        # print self.value
        self.inAngle = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inAngle=True)[0]
        self.outAngle = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outAngle=True)[0]
        self.inTangentType = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inTangentType=True)[0]
        self.outTangentType = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outTangentType=True)[0]
        self.lock = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), lock=True)[0]
        if self.weightedTangents:
            self.weightLock = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), weightLock=True)[0]
            self.inWeight = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), inWeight=True)[0]
            self.outWeight = cmds.keyTangent(self.crv, q=True, time=(self.frame, self.frame), outWeight=True)[0]

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
                if self.lock:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), lock=self.lock)
                if self.inAngle:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), inAngle=self.inAngle)
                if self.outAngle:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), outAngle=self.outAngle)
                if self.weightedTangents:
                    cmds.keyTangent(self.crv, edit=True, time=(
                        self.frame + self.offset, self.frame + self.offset), weightLock=self.weightLock,)
                    if self.inWeight:
                        cmds.keyTangent(self.crv, edit=True, time=(
                            self.frame + self.offset, self.frame + self.offset), inWeight=self.inWeight)
                    if self.outWeight:
                        cmds.keyTangent(self.crv, edit=True, time=(
                            self.frame + self.offset, self.frame + self.offset), outWeight=self.outWeight)
            else:
                # message('Unable to add animation to ' + self.obj + '.' + self.attr)
                pass


class Attribute(Key):

    def __init__(self, obj='', attr='', offset=0, auto=True):
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
        self.auto = auto
        '''
        if auto:
            self.getCurve()
        '''

    def get(self):
        #
        self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)
        self.value = cmds.getAttr(self.obj + '.' + self.name)
        if self.auto:
            self.getCurve()

    def getCurve(self):
        if self.crv:
            if len(self.crv) == 1:
                self.crv = self.crv[0]
                self.getCurveAttrs()
                self.getFrames()
                self.getKeys()

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

    def putCurve(self):
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
            if cmds.objExists(self.obj + '.' + self.name):
                if not cmds.getAttr(self.obj + '.' + self.name, l=True):
                    if cmds.getAttr(self.obj + '.' + self.name, se=True):
                        # TODO: set attr does not make a key, pose is lost if live scene has keys
                        # should set key if curve exists in scene, or inform user or potential problem
                        # TODO: on clicking clip, find potential problems, try and find a remedy
                        # TODO: replace parts of clip feature, manual value attr change
                        # TODO: auto refresh ui for new files
                        cmds.setAttr(self.obj + '.' + self.name, self.value)

    def putCurveAttrs(self):
        # need to update curve name, isnt the same as stored, depends on how
        # curves and layers are ceated
        self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)
        if self.crv:
            self.crv = self.crv[0]
            cmds.setAttr(self.crv + '.preInfinity', self.preInfinity)
            cmds.setAttr(self.crv + '.postInfinity', self.postInfinity)


class Obj(Attribute):

    def __init__(self, obj='', offset=0):
        self.name = obj
        self.offset = offset
        self.attributes = []
        self.attributesDriven = []
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
                    a = Attribute(self.name, attr)
                    a.get()
                    self.attributes.append(a)

    def getBakedAttribute(self):
        if self.attributesDriven:
            # turn off UI
            uiEnable()
            # create frame list from frame range
            min = cmds.playbackOptions(q=True, ast=True)
            max = cmds.playbackOptions(q=True, aet=True)
            rng = range(int(min), int(max + 1))
            rng = [float(i) for i in rng]
            # instantiate class for every driven attr
            attributesBaked = []
            for a in self.attributesDriven:
                attr = Attribute(self.name, a, auto=False)
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
            uiEnable()
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

    def __init__(self, sel=[], name=None, offset=0, ns=None, comment=''):
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
        for obj in self.sel:
            a = Obj(obj)
            a.get()
            self.objects.append(a)

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
        for obj in self.objects:
            if cmds.objExists(obj.name):
                obj.offset = self.offset
                obj.putAttribute()
            else:
                cmds.warning(
                    'Object   ' + obj.name + '   does not exist, skipping.')
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

    def __init__(self, name='', comment='', poseOnly=False):
        self.sel = None
        #
        self.name = name
        self.comment = comment
        self.poseOnly = poseOnly
        self.source = None
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
        #
        self.sel = cmds.ls(sl=True, fl=True)
        self.user = getpass.getuser()
        self.date = time.strftime("%c")
        self.getLayers()
        self.getClipAttrs()
        self.getClipStartEndLength()

    def getClipAttrs(self):
        # scene name
        sceneName = cmds.file(q=True, sn=True)
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
                            name=layer, sel=currentLayerMembers, comment=self.comment)
                        clp.get()
                        self.layers.append(clp)
                else:
                    print layer, '     no members'
            self.setActiveLayer(l=self.rootLayer)
            # build root layer class
            clp = Layer(sel=self.sel, comment=self.comment)
            clp.get()
            self.layers.append(clp)
        else:
            # no anim layers, create single layer class
            clp = Layer(name=None, sel=self.sel, comment=self.comment)
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

    def putLayers(self, mergeExistingLayers=True, applyLayerSettings=True):
        # restore layers from class
        clash = '__CLASH__'
        for layer in self.layers:
            # set import options
            layer.offset = self.offset
            sceneRootLayer = cmds.animLayer(q=True, root=True)
            # check if iteration is root layer, root layer name = None
            if not layer.name:
                self.setActiveLayer(l=sceneRootLayer)
                layer.putObjects()
            else:
                if not cmds.animLayer(layer.name, q=True, ex=True):
                    # create layer
                    cmds.animLayer(layer.name)
                else:
                    # print mergeExistingLayers
                    if not mergeExistingLayers:
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


def clipSave(name='clipTemp', comment='', poseOnly=False, temp=False):
    '''
    save clip to file
    '''
    path = clipPath(name=name + '.clip', temp=temp)
    clp = Clip(name=name, comment=comment, poseOnly=poseOnly)
    clp.get()
    # print clp.name
    # fileObject = open(path, 'wb')
    # pickle.dump(clp, fileObject)
    # fileObject.close()
    #
    fileObjectJSON = open(path, 'wb')
    json.dump(clp, fileObjectJSON, default=to_json, indent=1)
    fileObjectJSON.close()


def clipOpen(path=''):
    '''
    open clip form file
    '''
    # fileObject = open(path, 'r')
    # clp = pickle.load(fileObject)
    # fileObject.close()
    #
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


def clipApply(path='', ns=True, onCurrentFrame=True, mergeExistingLayers=True, applyLayerSettings=True, putLayerList=[], putObjectList=[],
              start=None, end=None):
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
    #
    # clp = cutKeysToRange(clp, 1020.0, 1090)
    clp.putLayers(mergeExistingLayers, applyLayerSettings)
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
    user = os.path.expanduser('~')
    path = user + '/maya/clipLibrary/'
    return path


def clipDefaultTempPath():
    user = os.path.expanduser('~')
    path = user + '/maya/clipTemp/'
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
                    k = Key(attr.obj, attr.name, attr.crv, frame,
                            weightedTangents=False, auto=False)
                    # find appropriate value
                    k.value = insertKeyValue(attr, frame)
                    k.inTangentType = 'auto'
                    k.outTangentType = 'auto'
                    attr.keys.append(k)
                else:
                    # print 'no crv exists, skipping insert'
                    pass
    return clp


def insertKeyValue(attr, frame=0.0):
    # HACK: lack of calculus skills method, good for approximation.
    # does not consider tangents, only key positions
    val = 0.0
    i = 0
    # can reach end of list before finding a qualifying frame number
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
        # frame range between keys
        frameRange = int((preFrm - nexFrm) * -1)
        valueRange = preVal - nexVal
        if valueRange != 0.0:
            # force positive
            if valueRange < 0:
                valueRange = valueRange * -1
            # find increments
            inc = valueRange / frameRange
            # how many increments to add
            mlt = int((preFrm - frame) * -1)
            # add up increments
            val = inc * mlt
            # operation depends on preVal relative to nexVal value
            if preVal < nexVal:
                val = preVal + val
            else:
                val = preVal - val
        else:
            return preVal
        return val


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
