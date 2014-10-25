import maya.cmds as cmds
import maya.mel as mel
import time
import getpass
import pickle
import os

#


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class Key():

    def __init__(self, obj, attr, crv, frame, offset=0, weightedTangents=None):
        # dont think this currently accounts for weighted tangents
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
        self.getKey()

    def getKey(self):
        # print self.obj
        # print self.crv
        # print self.frame
        # print self.attr
        # print index
        self.value = cmds.keyframe(
            self.crv, q=True, time=(self.frame, self.frame), valueChange=True, a=True)[0]
        # print self.value
        self.inAngle = cmds.keyTangent(
            self.crv, q=True, time=(self.frame, self.frame), inAngle=True)[0]
        self.outAngle = cmds.keyTangent(
            self.crv, q=True, time=(self.frame, self.frame), outAngle=True)[0]
        self.inTangentType = cmds.keyTangent(
            self.crv, q=True, time=(self.frame, self.frame), inTangentType=True)[0]
        self.outTangentType = cmds.keyTangent(
            self.crv, q=True, time=(self.frame, self.frame), outTangentType=True)[0]
        self.lock = cmds.keyTangent(
            self.crv, q=True, time=(self.frame, self.frame), lock=True)[0]
        if self.weightedTangents:
            self.weightLock = cmds.keyTangent(
                self.crv, q=True, time=(self.frame, self.frame), weightLock=True)[0]
            self.inWeight = cmds.keyTangent(
                self.crv, q=True, time=(self.frame, self.frame), inWeight=True)[0]
            self.outWeight = cmds.keyTangent(
                self.crv, q=True, time=(self.frame, self.frame), outWeight=True)[0]

    def putKey(self):
        # set key, creates curve node
        # print self.obj, self.attr, self.frame, self.offset, self.value,
        # '_____________________________'
        cmds.setKeyframe(self.obj, at=self.attr, time=(
            self.frame + self.offset, self.frame + self.offset), value=self.value, shape=False)
        # update curve name, set curve type, set weights
        self.crv = cmds.findKeyframe(self.obj, at=self.attr, c=True)[0]
        cmds.keyframe(self.crv, time=(self.frame + self.offset, self.frame +
                                      self.offset), valueChange=self.value)  # correction, hacky, should fix
        cmds.setAttr(self.crv + '.weightedTangents', self.weightedTangents)
        cmds.keyTangent(self.crv, edit=True, time=(self.frame + self.offset, self.frame + self.offset),
                        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock)
        if self.weightedTangents:
            cmds.keyTangent(self.crv, edit=True, time=(self.frame + self.offset, self.frame + self.offset), weightLock=self.weightLock,
                            inWeight=self.inWeight, outWeight=self.outWeight)


class Attribute(Key):

    def __init__(self, obj, attr, offset=0):
        '''
        add get/put keys from Key class to this one
        '''
        self.obj = obj
        self.name = attr
        self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)
        # print self.crv
        self.frames = []
        self.keys = []
        self.value = cmds.getAttr(self.obj + '.' + self.name)
        self.offset = offset
        self.preInfinity = None
        self.postInfinity = None
        self.weightedTangents = None
        self.baked = False
        self.getCurve()

    def getCurve(self):
        if self.crv != None:
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
        if self.crv != None:
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
            self.keys.append(a)

    def putCurve(self):
        # print self.obj, '________________________obj'
        if self.keys:
            # print len(self.keys)
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
            # print '_______putcurve set attr'
            if cmds.objExists(self.obj + '.' + self.name):
                if not cmds.getAttr(self.obj + '.' + self.name, l=True):
                    cmds.setAttr(self.obj + '.' + self.name, self.value)

    def putCurveAttrs(self):
        # need to update curve name, isnt the same as stored, depends on how
        # curves and layers are ceated
        self.crv = cmds.findKeyframe(self.obj, at=self.name, c=True)[0]
        cmds.setAttr(self.crv + '.preInfinity', self.preInfinity)
        cmds.setAttr(self.crv + '.postInfinity', self.postInfinity)


class Obj(Attribute):

    def __init__(self, obj, offset=0):
        self.name = obj
        # print self.name, '_______name__'
        self.offset = offset
        self.attributes = []
        self.getAttribute()

    def getAttribute(self):
        keyable = cmds.listAttr(self.name, k=True, s=True)
        # print keyable
        non_keyable = cmds.listAttr(self.name, cb=True)  # cb non keyable
        # print keyable
        if keyable:
            for k in keyable:
                a = Attribute(self.name, k)
                self.attributes.append(a)

    def getDrivenAttribute(self):
        # collect constrained, setDriven, expression attrs
        # create
        pass

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
        self.getObjects()
        self.getLayerAttrs()
        self.getStartEndLength()

    def getObjects(self):
        for obj in self.sel:
            a = Obj(obj)
            self.objects.append(a)
        # print self.sel
        # print self.putObjectList

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
                cmds.warning('Object   ' + obj.name + '   does not exist, skipping.')
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
        self.sel = cmds.ls(sl=True)
        self.name = name
        self.comment = comment
        self.poseOnly = poseOnly
        self.source = None
        self.user = getpass.getuser()
        self.date = time.strftime("%c")
        #
        self.start = None
        self.end = None
        self.length = None
        self.layers = []  # list of class layers
        self.layerNames = None
        self.rootLayer = None
        # set on import of clip
        self.offset = 0  # import
        #
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
                        self.layers.append(clp)
                else:
                    print layer, '     no members'
            self.setActiveLayer(l=self.rootLayer)
            # build root layer class
            clp = Layer(sel=self.sel, comment=self.comment)
            self.layers.append(clp)
        else:
            # no anim layers, create single layer class
            clp = Layer(name=None, sel=self.sel, comment=self.comment)
            self.layers.append(clp)
        # print self.putLayerList

    def getClipStartEndLength(self):
        for layer in self.layers:
            if self.start == None:
                self.start = layer.start
                self.end = layer.end
            else:
                if layer.start < self.start:
                    self.start = layer.start
                if layer.end > self.end:
                    self.end = layer.end
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


def clipSave(name='clipTemp', path='', comment='', poseOnly=False):
    '''
    save clip to file
    '''
    path = clipPath(name=name + '.clip')
    clp = Clip(name=name, comment=comment)
    # print clp.name
    fileObject = open(path, 'wb')
    pickle.dump(clp, fileObject)
    fileObject.close()


def clipOpen(path=''):
    '''
    open clip form file
    '''
    fileObject = open(path, 'r')
    clp = pickle.load(fileObject)
    return clp


def clipApply(path='', ns=True, onCurrentFrame=True, mergeExistingLayers=True, applyLayerSettings=True, putLayerList=[], putObjectList=[], poseOnly=False):
    '''
    apply animation from file
    FIX
    need to add option to import on existing layer with same name
    add option to not apply layer settings to layers with same name
    '''
    sel = cmds.ls(sl=1)
    # set import attrs
    clp = clipOpen(path=path)
    if onCurrentFrame:
        clp.offset = onCurrentFrameOffset(start=clp.start)
    if ns:
        clp = putNS(clp)
    if putObjectList:
        clp = isolateObjects(clp, putObjectList)  # not working
    if putLayerList:
        clp = isolateLayers(clp, putLayerList)  # working
    clp.poseOnly = poseOnly  # doesn't do anything yet
    #
    clp.putLayers(mergeExistingLayers, applyLayerSettings)
    if sel:
        cmds.select(sel)


def clipPath(name=''):
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


def onCurrentFrameOffset(start=0.0):
    current = cmds.currentTime(q=True)
    offset = 0.0
    if start > current:
        offset = current - start
    else:
        offset = ((start - current) * -1.0) + 0.0
    # print offset
    return offset


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


def getNS(*args):
    '''
    get it from selection
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


def isolateLayers(clp, layers=[]):
    # remove layers from clip that arent in 'layer' list arg
    isolated = []
    for layer in clp.layers:
        if layer.name in layers:
            isolated.append(layer)
    clp.layers = isolated
    return clp


def isolateObjects(clp, objects=[]):
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
