import maya.cmds as cmds
import maya.mel as mel
import os
import urllib2
#
import webrImport as web
# web
cn = web.mod('constraint_lib')
fr = web.mod('frameRange_lib')


def motionPathRandom():
    # project
    sel = cmds.ls(sl=1)  # select poly and curve to project
    cmds.polyProjectCurve(sel[0], sel[1], ch=True, direction=(0, 1, 0))

    # attach truck
    sel = cmds.ls(sl=1)  # select: control attached to path and new curve
    moP = cmds.listConnections(sel[0], source=True, destination=False, type='motionPath')[0]
    cmds.select(sel[1])
    shape = cmds.pickWalk(d='down')[0]
    cmds.connectAttr(shape + '.worldSpace[0]', moP + '.geometryPath', force=True)


def mocapSkelAnim():
    '''
    forgot what this is for
    '''
    sel = cmds.ls(sl=True)
    if len(sel) == 2:
        get = sel[0]
        # put = sel[1].split(':')[0]
        # mocap = 'mocap_'
        grp = 'mocap_JNTS'
        if ':' in get:
            grpNS = get.split(':')[0] + ':' + grp
        else:
            grpNS = grp
        rel = cmds.listRelatives(grpNS, ad=True)
        for obj in rel:
            if cmds.nodeType(obj) == 'joint':
                attrs = cn.getDrivenAttrsByNodeType(obj, typ='animCurve')
                if attrs:
                    for attr in attrs:
                        # crv = cn.AnimCrv(obj, attr.split('.')[1])
                        # update obj class attr to pasted version
                        if ':' in obj:
                            obj = obj.split(':')[1]
                        # crv.obj = put + ':' + obj
                        # paste/buildCurve
                        # crv.build()
    else:
        print 'Select node from copy namespace, select node from paste namespace'


def message(what='', maya=True, warning=False):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace('\\', '/')
    if warning:
        cmds.warning(what)
    else:
        if maya:
            mel.eval('print \"' + what + '\";')
        else:
            print what


def toggleFrustum():
    import pymel.core as pm
    try:
        sel = cmds.ls(sl=True)[0]
        shapes = []
        if cmds.nodeType(sel) != 'camera':
            shapes = cmds.listRelatives(sel, type='shape', f=True)
        else:
            shapes.append(sel)
        if cmds.nodeType(shapes) == 'camera':
            now = pm.renderManip(shapes, q=True, st=True)
            if now:
                pm.renderManip(shapes, cam=[False, False, False, False, False])
                message('Clip planes Off', maya=True)
            else:
                pm.renderManip(shapes, cam=[False, False, False, True, False])
                message('Clip planes On', maya=True)
        else:
            message('Select a camera to toggle Frustum.', maya=True)
    except:
        message('Select a camera to toggle Frustum.', maya=True)


def locSize(lc, X=0.5):
    axis = ['X', 'Y', 'Z']
    for axs in axis:
        cmds.setAttr(lc + 'Shape.localScale' + axs, X)


def locator(ro='zxy', size=0.1, constrain=False):
    locs = []
    sel = cmds.ls(sl=True, fl=True)
    if len(sel) > 0:
        for item in sel:
            lc = cmds.spaceLocator(name=item + '__PLACE__')[0]
            cmds.setAttr(lc + '.sx', k=False, cb=True)
            cmds.setAttr(lc + '.sy', k=False, cb=True)
            cmds.setAttr(lc + '.sz', k=False, cb=True)
            cmds.setAttr(lc + '.v', k=False, cb=True)
            locSize(lc, X=size)
            locs.append(lc)
            roo = cmds.getAttr(item + '.rotateOrder')
            r = cmds.xform(item, q=True, ws=True, ro=True)
            t = cmds.xform(item, q=True, ws=True, rp=True)
            cmds.xform(lc, t=t, ro=r)
            cmds.setAttr(lc + '.rotateOrder', roo)
            cmds.xform(lc, roo=ro)
            if constrain:
                cmds.parentConstraint(item, lc, mo=True)
        return locs
    else:
        cmds.warning('Select something!')


def getRange():
    min = cmds.playbackOptions(q=True, minTime=True)
    max = cmds.playbackOptions(q=True, maxTime=True)
    current = cmds.currentTime(q=True)
    return min, max, current


def nonKey(obj):
    pos = ['tx', 'ty', 'tz']
    rot = ['rx', 'ry', 'rz']
    nonKeyT = []
    nonKeyR = []
    for axis in pos:
        if not cmds.getAttr(obj + '.' + axis, k=True):
            at = axis.split('t')[1]
            nonKeyT.append(at)
    for axis in rot:
        if not cmds.getAttr(obj + '.' + axis, k=True):
            at = axis.split('r')[1]
            nonKeyR.append(at)
    return nonKeyT, nonKeyR


def changeRO(obj, ro):
    '''
    '''
    if cmds.getAttr(obj + '.rotateOrder', settable=1):
        cn.uiEnable(controls='modelPanel')
        r = getRange()
        autoK = cmds.autoKeyframe(q=True, state=True)
        cmds.autoKeyframe(state=False)
        i = r[0]
        current = r[2]
        origRO = cmds.getAttr(obj + '.rotateOrder')
        cmds.currentTime(i)
        cmds.currentTime(cmds.findKeyframe(which='previous'))
        cmds.xform(obj, roo=ro)
        keyframes = getKeyedFrames(obj)
        for key in keyframes:
            cmds.currentTime(key)
            cmds.setAttr(obj + '.rotateOrder', origRO)
            cmds.xform(obj, roo=ro)
            cmds.setKeyframe(obj + '.rotate')
        cmds.currentTime(current)
        cmds.autoKeyframe(state=autoK)
        cn.eulerFilter(obj, tangentFix=True)
        cn.uiEnable(controls='modelPanel')
    else:
        message('FAIL. Rotate order is LOCKED or CONNECTED to a custom attribute.', maya=True)


class SpaceSwitch():

    def __init__(self, obj):
        self.obj = obj
        self.mtrx = []
        self.pos = []
        self.rot = []
        self.keys = getKeyedFrames(self.obj)
        self.store()

        '''
        min
        max
        selStart
        selEnd
        start
        end
        current
        keyStart
        keyEnd
        '''
        self.rng = fr.Get()

    def store(self):
        '''
        store animation
        '''
        # make sure o
        if self.keys:
            current = cmds.currentTime(q=True)
            # ui off
            cn.uiEnable(controls='modelPanel')
            # autokey state
            autoK = cmds.autoKeyframe(q=True, state=True)
            cmds.autoKeyframe(state=False)
            for key in self.keys:
                cmds.currentTime(key)
                self.mtrx.append(cmds.xform(self.obj, q=True, m=True, ws=True))
                # self.pos.append(cmds.xform(self.obj, q=True, rp=True, ws=True))
                # self.rot.append(cmds.xform(self.obj, q=True, ro=True, ws=True))
            # restore everything
            cmds.currentTime(current)
            cmds.autoKeyframe(state=autoK)
            cn.uiEnable(controls='modelPanel')
        else:
            message('No keys.', maya=True)

    def restore(self, useSelected=False):
        '''
        restore animation
        '''
        if useSelected:
            self.obj = cmds.ls(sl=1)[0]

        if self.keys:
            current = cmds.currentTime(q=True)
            # ui off
            cn.uiEnable(controls='modelPanel')
            # autokey state
            autoK = cmds.autoKeyframe(q=True, state=True)
            cmds.autoKeyframe(state=False)
            i = 0
            for key in self.keys:
                if key >= self.rng.keyStart and key <= self.rng.keyEnd:
                    # message(str(key))
                    cmds.currentTime(key)
                    cmds.xform(self.obj, m=self.mtrx[i], ws=True)
                    # cmds.xform(self.obj, t=self.pos[i], ws=True)
                    # cmds.xform(self.obj, ro=self.rot[i], ws=True)
                    # account for non-keyable rotate or translate attrs
                    cmds.setKeyframe(self.obj + '.rotate')
                    cmds.setKeyframe(self.obj + '.translate')
                    # getCurves for translate and rotate
                    # crv = getAnimCurves(self.obj)
                    cn.eulerFilter(self.obj, tangentFix=True)
                i = i + 1
            # tangent fix
            # cn.eulerFilter(crv, tangentFix=True)
            # restore everything
            cmds.currentTime(current)
            cmds.autoKeyframe(state=autoK)
            cn.uiEnable(controls='modelPanel')
        else:
            message('No keys.', maya=True)


def getAnimCurves(obj='', attrs=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']):
    animCurves = cmds.findKeyframe(obj, c=True)
    curves = []
    for crv in animCurves:
        for attr in attrs:
            if attr in crv:
                curves.append(crv)
    return curves


def getKeyedFrames(obj):
    animCurves = cmds.findKeyframe(obj, c=True)
    if animCurves is not None:
        frames = []
        for crv in animCurves:
            framesTmp = cmds.keyframe(crv, q=True)
            if framesTmp:
                for frame in framesTmp:
                    frames.append(frame)
            else:
                print 'no keys'
        frames = list(set(frames))
        frames.sort()
        return frames
    else:
        if type(obj) == list:
            for o in obj:
                message('Object ' + o + ' has no keys')
        else:
            message('Object ' + obj + ' has no keys')
        return None


def changeRoMulti(ro='zxy'):
    # changes rotate order of an object to the desired order without changing the pose. tangent will bust.
    # will use current frame range
    sel = cmds.ls(sl=True)
    if sel:
        for item in sel:
            changeRO(item, ro=ro)
    else:
        cmds.warning('Select object(s)')


def keyHi(v=0):
    cmds.select(hierarchy=True)
    h = cmds.ls(sl=True)
    print h
    for item in h:
        cmds.setKeyframe(item, attribute='visibility', v=v)


def matchObj():
    # queries dont work correctly when constraints, pairBlends and characterSets get involved
    # objs
    # BUG: works like a turd, if rotations are locked it works half the time
    # print ' run '
    sel = cmds.ls(sl=True, fl=True)
    if len(sel) == 2:
        # print ' if '
        # collect get
        get = sel[1]
        '''
        roo = cmds.getAttr(get + '.rotateOrder')
        r = cmds.xform(get, q=True, ws=True, ro=True )
        t = cmds.xform(get, q=True, ws=True, t=True )
        '''
        mtrx = cmds.xform(get, q=True, m=True, ws=True)
        # collect put
        put = sel[0]
        # origRO = cmds.xform(put, q=True, roo=True)
        #
        # cmds.xform(put, m=mtrx, ws=True)
        #
        try:
            # print ' try '
            # put
            # cmds.setAttr(put + '.rotateOrder', roo)
            # cmds.xform(put, ws=True, t=t)
            # cmds.xform(put, ws=True, ro=r)
            # cmds.xform(put, roo=origRO)
            cmds.xform(put, m=mtrx, ws=True)
        except:
            # print 'exception'
            # intermediate object
            loc = cmds.spaceLocator(name='getSpace_deleteMe')[0]
            cmds.setAttr(loc + '.rotateOrder', roo)
            cmds.xform(loc, ws=True, t=t)
            cmds.xform(loc, ws=True, ro=r)
            cmds.xform(put, roo=origRO)
            # collect get
            r = cmds.xform(loc, q=True, ws=True, ro=True)
            t = cmds.xform(loc, q=True, ws=True, t=True)
            # put
            cmds.xform(put, ws=True, t=t)
            cmds.xform(put, ws=True, ro=r)
            # delete
            cmds.delete(loc)
        else:
            # print 'else'
            pass
        # reselect objects
        cmds.select(sel)
    else:
        message('Select 2 objects.', maya=True, warning=True)


def shapeSize(obj=None, mltp=1):
    '''\n
    mltp = size multiplier of shape nodes
    '''
    if obj is None:
        # make a list from selection
        obj = cmds.ls(sl=True, l=True)
    elif type(obj) == list:
        # no need to accomodate
        pass
    else:
        # obj must be a single item, make a list
        obj = [obj]
        # run the loop on list
        for item in obj:
            shape = cmds.listRelatives(item, s=True, f=True)
            if shape is not None:
                for node in shape:
                    if 'SharedAttr' not in node:
                        cmds.scale(mltp, mltp, mltp, node + '.cv[*]')


def toggleRes():
    sel = cmds.ls(sl=True)
    c = ':c_master_CTRL.'
    attrHi = 'hiResGeoVis'
    attrLo = 'loResGeoVis'
    name = sel[0].split(':')[0]
    if cmds.getAttr(name + c + attrHi) == 1:
        cmds.setAttr(name + c + attrHi, 0)
        cmds.setAttr(name + c + attrLo, 1)
    else:
        cmds.setAttr(name + c + attrHi, 1)
        cmds.setAttr(name + c + attrLo, 0)


def distributeKeys(count=3.0, destructive=True):
    sel = cmds.ls(sl=1, fl=True)
    rng = fr.Get()
    if sel:
        # gather info
        autoK = cmds.autoKeyframe(q=True, state=True)
        frames = getKeyedFrames(sel)
        if not frames:
            # add a bake if no keys exist, then get keys again
            message('No keys found, setting a key start/end of range.', maya=1)
            cmds.setKeyframe(sel, t=(rng.start, rng.start))
            cmds.setKeyframe(sel, t=(rng.end, rng.end))
            frames = getKeyedFrames(sel)
            # return None
        # process start/end of loop
        framesNew = []
        if rng.selection:
            for f in frames:
                if f >= rng.keyStart and f <= rng.keyEnd:
                    framesNew.append(f)
            frames = framesNew
        #
        print frames
        lastFrame = frames[len(frames) - 1]
        step = frames[0]
        i = frames[0]
        cut = []
        # turn off autokey
        cmds.autoKeyframe(state=False)
        # process keys
        while i < lastFrame:
            if i == step:
                cmds.setKeyframe(sel, i=True, t=step)
                step = step + count
            else:
                if i in frames:
                    cut.append(i)
            i = i + 1
        # remove keys is destructive
        if destructive:
            # print cut, '_________'
            if cut:
                for frame in cut:
                    cmds.cutKey(sel, clear=1, time=(frame, frame))
        # restore autokey
        cmds.autoKeyframe(state=autoK)
    else:
        message('Select one or more objects', maya=1)


def panelOnSelection():
    sel = cmds.ls(sl=1, fl=True)
    if len(sel) == 4:
        p = cmds.polyPlane(w=1, h=1, sx=1, sy=1, ax=(0, 1, 0), cuv=2, ch=1)[0]
        # vtx = cmds.polyEvaluate(p, v=1)
        j = 0
        for i in sel:
            pos = cmds.xform(i, q=True, ws=True, rp=True)
            cmds.xform(p + '.vtx[' + str(j) + ']', ws=True, t=pos)
            j = j + 1
    else:
        message('Select 4 objects', maya=True)


def loadCurveShape(name=None, local=False, *args):
    # paths
    if name:
        if local:
            path = os.path.expanduser('~') + '/maya/controlShapes/'
        else:
            url = 'https://raw.githubusercontent.com/boochos/controlShapes/master/'
            url = url + name + '.txt'
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            contents = response.read()
            contents = contents.split("\n")
            shape = []
            for line in contents:
                if line:
                    shape.append(line)
            # returns 3 floats in string form
            return shape


def importCurveShape(name='loc_ctrl', scale=1.0, overRide=False):
    selection = cmds.ls(selection=True, tr=True)
    # change the shape of multiple selected curves
    if len(selection) > 0:
        for sel in selection:
            # get the shape node
            shapeNode = cmds.listRelatives(sel, shapes=True)[0]
            # cvInfo is populated then interated through later
            cvInfo = []
            if cmds.nodeType(shapeNode) == 'nurbsCurve':
                shape = loadCurveShape(name)
                for line in shape:
                    # split string floats, and convert to real floats
                    cvLine = line.split(' ')
                    tmp = float(cvLine[0]) * scale, float(cvLine[1]) * scale, float(cvLine[2]) * scale
                    cvInfo.append(tmp)
                # Shape the curve
                if not overRide:
                    cmds.setAttr(shapeNode + '.overrideEnabled', 1)
                    cmds.setAttr(shapeNode + '.overrideColor', overRide)

                if len(cvInfo) == len(cmds.getAttr(shapeNode + '.cv[*]')):
                    for i in range(0, len(cvInfo), 1):
                        cmds.xform(shapeNode + '.cv[' + str(i) + ']', os=True, t=cvInfo[i])
                else:
                    # Curves with different CV counts are not compatible
                    message('CV count[' + str(len(cmds.getAttr(shapeNode + '.cv[*]'))) + '] from selected does not match import CV count[' + str(len(cvInfo)) + ']')
    else:
        message('Select a NURBS curve if you truly want to proceed...')
