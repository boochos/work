import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
#
import webrImport as web
# web
cs = web.mod('characterSet_lib')
hj = web.mod('hijack_lib')
fr = web.mod('frameRange_lib')
plc = web.mod('atom_place_lib')


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
            print wha


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


def listX(l=[]):
    if l is not None:
        if len(l) is not None:
            return list(set(l))
        else:
            return l


def matchKeyedFramesLoop():
    '''
    uses first selection to add keys on consequent objects in selection
    '''
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        # one object selected, add same key on all curves
        matchKeyedFrames(A=None, B=None, subtractive=True)
    else:
        # 2 objects
        obj1 = sel[0]
        for item in sel:
            if item != obj1:
                cmds.select(obj1, item)
                matchKeyedFrames(A=None, B=None, subtractive=True)
        cmds.select(sel)


def subframe():
    sel = cmds.ls(sl=True)
    if sel:
        for s in sel:
            animCurves = cmds.findKeyframe(s, c=True)
            if animCurves is not None:
                for crv in animCurves:
                    frames = cmds.keyframe(crv, q=True)
                    if frames:
                        for frame in frames:
                            rnd = round(frame, 0)
                            if rnd != frame:
                                message(
                                    'removing: ' + crv + ' -- ' + str(frame))
                                if cmds.setKeyframe(crv, time=(rnd, rnd), i=1) == 0:
                                    cmds.cutKey(crv, time=(frame, frame))
                                else:
                                    cmds.setKeyframe(crv, time=(rnd, rnd), i=1)
                                    cmds.cutKey(crv, time=(frame, frame))
                    else:
                        message('no keys')
            else:
                message('Object ' + s + ' has no keys')
                # return None
    else:
        message('Select object', maya=1)


def matchKeyedFrames(A=None, B=None, subtractive=True):
    '''
    A = get keyed frames
    B = put keyed frames
    '''
    if A is None and B is None:
        sel = cmds.ls(sl=True)
        if sel:
            crvs = cmds.keyframe(sel[0], q=True, name=True)
        if crvs is None:
            message('No keys on object', maya=True)
            return None
    if A is None and B is None:
        if len(sel) == 2:
            A = sel[0]
            B = sel[1]
        elif len(sel) == 1:
            A = sel[0]
            B = sel[0]
        else:
            message(
                'Select 1 or 2 objects. Second object will get matching timeline keys.')
            return None
    # add additive or destructive
    # keyed frames on A
    framesAdd = keyedFrames(A)
    # print '---------', framesAdd
    if framesAdd:
        # list attrs on B and add key
        old = cmds.listAttr(B, k=True)
        for attr in old:
            try:
                if cmds.setKeyframe(B + '.' + attr, i=True) == 0:
                    cmds.setKeyframe(B + '.' + attr)
            except:
                print 'sanity check: FAILED ATTRS ____', B, attr
        # check if new constraint blend attr is created after keying
        new = cmds.listAttr(B, k=True)
        created = list(set(new) - set(old))
        if len(created) != 0:
            for attr in created:
                cmds.setKeyframe(B + '.' + attr, v=1)
    # add keys to B from A
    if framesAdd:
        for frame in framesAdd:
            cmds.setKeyframe(B, i=True, t=frame)
        if subtractive:
            # remove keys from B, which A doesnt have
            min = framesAdd[0]
            max = framesAdd[len(framesAdd) - 1]
            framesRem = keyedFrames(B)
            for frame in framesRem:
                if frame not in framesAdd:
                    cmds.cutKey(B, t=(frame, frame))
        # check if current frame should be keyed
        current = cmds.currentTime(q=True)
        if current not in framesAdd:
            cmds.cutKey(B, t=(current, current))


def keyedFrames(obj):
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
        message('Object ' + obj + ' has no keys')
        return None


class reConnect():

    '''
    Use to reconnect after baking animation. For now only works with pairBlends.
    Which means the object should be keyed and have some type of attribute driver. (ie, constraint, motion trail)
    '''

    def __init__(self, sel=''):
        self.selection = sel
        self.pairs = {}
        self.nodes = []
        self.getDict()
        self.getNodes()

    def getNodes(self):
        self.nodes = list(
            set(cmds.listConnections(self.selection, s=True, d=False)))

    def getDict(self):
        # get attributes
        connections = cmds.listConnections(
            self.selection, s=True, d=False, type='pairBlend', c=True)
        if connections is not None:
            for con in connections:
                if '.' in con:
                    # build key:value pair
                    self.pairs[con] = cmds.listConnections(
                        con, s=True, d=False, type='pairBlend', p=True)[0]
        else:
            cmds.warning('No pairBlend node was found')

    def connect(self):
        # reconnect pairBlend.
        for key in self.pairs:
            try:
                cmds.connectAttr(self.pairs[key], key, f=True)
            except:
                message(
                    'Failed Connection -- ' + self.pairs[key] + ' -- to -- ' + key)


def updateConstraintOffset(obj=''):
    # currently assuming list is being fed with one object
    obj = obj[0]
    # find constraint
    con = getConstraint(obj, nonKeyedRoute=True, keyedRoute=True, plugRoute=True)
    if con:
        con = con[0]
        print con
        # find target
        driver = []
        # lists [constrained object, constraint, driving object] not in this order
        drivers = getDrivers(con, typ='transform', plugs=False)
        for item in drivers:
            if item != con and item != obj:
                print item, obj, con
                driver.append(item)
        # print driver
        # update
        cmds.parentConstraint(driver[0], con, e=1, maintainOffset=1)
        message('Offset Updated -- ' + con, maya=1)
    else:
        message('No constraint detected')


def updateConstrainedCurves(obj=None, sim=False):
    if obj is None:
        obj = cmds.ls(sl=True)
        if len(obj) != 1:
            message('Select one object.')
            return None
        else:
            obj = cmds.ls(sl=True)[0]
    # print obj
    # getBlendAttr returns list, need for loop
    blndAttrs = getBlendAttr(obj)
    blndAttrState = []
    for attr in blndAttrs:
        blndAttrState.append(AnimCrv(obj, attr.split('.')[1]))
    # print blndAttrState
    # state = AnimCrv(obj, getBlendAttr(obj)[0].split('.')[1])
    # connection class
    rcc = reConnect(obj)
    # bake attributes driven by pairBlend
    objAttrs = getDrivenAttrsByNodeType(obj)
    bakeConstrained(objAttrs, removeConstraint=False, timeLine=False, sim=sim)
    # reconnect constraint/pairBlend
    rcc.connect()
    for state in blndAttrState:
        if state.crv is not None:
            state.build()
        else:
            cmds.setAttr(obj + '.' + state.attr, state.value)


def curveNodeFromName(crv=''):
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(crv)
    dependNode = OpenMaya.MObject()
    selectionList.getDependNode(0, dependNode)
    crvNode = OpenMayaAnim.MFnAnimCurve(dependNode)
    return crvNode


def eulerFilter(obj, tangentFix=False):
    curves = cmds.keyframe(obj, q=True, name=True)
    euler = []
    if curves:
        for crv in curves:
            c = curveNodeFromName(crv)
            if c.animCurveType() == 0:  # angular
                euler.append(crv)
        if euler:
            cmds.filterCurve(euler)
        if tangentFix:
            fixTangents(obj)
        # print 'here'


def fixTangents(obj, attrs=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']):
    animCurves = cmds.findKeyframe(obj, c=True)
    for crv in animCurves:
        for attr in attrs:
            if attr in crv:
                if 'step' in cmds.keyTangent(crv, q=True, ott=True):
                    frames = cmds.keyframe(crv, q=True)
                    ott = cmds.keyTangent(crv, q=True, ott=True)
                    ot = []
                    it = []
                    for o in ott:
                        if o == 'step':
                            ot.append('step')
                            it.append('auto')
                        else:
                            ot.append('auto')
                            it.append('auto')
                    for i in range(len(frames)):
                        cmds.keyTangent(crv, edit=True, t=(frames[i], frames[i]), itt=it[i], ott=ot[i])
                else:
                    cmds.keyTangent(crv, edit=True, itt='auto', ott='auto')


def getConstraint(obj, nonKeyedRoute=True, keyedRoute=True, plugRoute=True):
    # fails with characterSets
    cons = []
    if plugRoute:
        # if character set is connected, other checks fail
        # this method asks for specific plug string
        # if plug is consistent with all constraints, this may be most reliable
        plug = getDriven(obj, typ='constraint', plugs=True)
        if plug:
            for p in plug:
                if 'constraintParentInverseMatrix' in p:
                    cons.append(p.split('.')[0])
    if nonKeyedRoute:
        con = listX(cmds.listConnections(obj, s=True, d=False, t='constraint'))
        if con:
            for c in con:
                cons.append(c)
    if keyedRoute:
        p = listX(cmds.listConnections(obj, s=True, d=False, t='pairBlend'))
        if p:
            con = listX(
                cmds.listConnections(p, s=True, d=False, t='constraint'))
            if con is not None:
                for c in con:
                    cons.append(c)
    return listX(cons)


def getDrivers(obj, typ='', plugs=True):
    # Returns nodes that are driving given node
    # typ=return only node types
    # plugs=True will return with driving attribute(s)
    con = cmds.listConnections(obj, d=False, s=True, t=typ, plugs=plugs)
    if con is not None:
        con = list(set(con))
    return con


def getDriven(obj, typ='', plugs=True):
    # Returns nodes that are driven by given node
    # typ=return only node types
    # plugs=True will return with driven attribute(s)
    con = cmds.listConnections(obj, s=False, d=True, t=typ, plugs=plugs)
    if con is not None:
        con = list(set(con))
    return con


def getDrivenAttrsByNodeType(obj, typ='pairBlend'):
    # Returns attributes of the given object which are driven by a node type
    drivers = getDrivers(obj, typ=typ, plugs=True)
    driven = []
    if drivers:
        for driver in drivers:
            driven.append(getDriven(driver, typ='', plugs=True)[0])
        return driven
    else:
        return None


def getBlendAttr(obj, delete=False):
    attrs = []
    con = cmds.listConnections(obj, d=True, s=False, t='pairBlend', c=True)
    if con is not None:
        con = listX(con)
        for c in con:
            if '.blend' in c:
                attrs.append(c)
        if len(attrs) != 0:
            if delete:
                for attr in attrs:
                    cmds.deleteAttr(attrs[0])
                    message('Attribute  ' + attrs[0] + '  is deleted')
            else:
                return attrs
        else:
            print 'no attrs'


def deleteAttrList(objects):
    if objects is not None:
        if len(objects) != 0:
            for obj in objects:
                name = obj.split('.')[0]
                attr = obj.split('.')[1]
                if cmds.attributeQuery(attr, node=name, exists=True):
                    cmds.deleteAttr(obj)
                    message('Attribute | ' + obj + '  is deleted')


def deleteList(objects):
    if len(objects) != 0:
        for obj in objects:
            typ = cmds.nodeType(obj)
            cmds.delete(obj)
            message(typ + ' | ' + obj + '  is deleted')


def bakeStep(obj, time=(), sim=False, uiOff=False):
    '''
    custom bake function
    sim = keys only, dont step through frame at a time
    '''
    # print time, '___inside bake'
    # TODO: account for timewarp curve
    if uiOff:
        uiEnable(controls='modelPanel')
    # r = getRange()
    attrs = []
    min = time[0]
    max = time[1]
    i = min
    current = cmds.currentTime(q=1)
    # print obj, '________'
    keyframes = keyedFrames(obj)
    autoK = cmds.autoKeyframe(q=True, state=True)
    cmds.autoKeyframe(state=False)
    # find atttrs from constraint or pairblend
    drivenP = getDrivenAttrsByNodeType(obj, typ='pairBlend')
    if drivenP:
        for attr in drivenP:
            attrs.append(attr)
    drivenC = getDrivenAttrsByNodeType(obj, typ='constraint')
    if drivenC:
        for attr in drivenC:
            attrs.append(attr)
        # handle blend attr, weight to one
        old = cmds.listAttr(obj, k=True)
        for attr in old:
            try:
                if cmds.setKeyframe(obj + '.' + attr, i=True) == 0:
                    cmds.setKeyframe(obj + '.' + attr)
            except:
                print 'sanity check: FAILED ATTRS ____', obj, attr
        # check if new constraint blend attr is created after keying
        new = cmds.listAttr(obj, k=True)
        created = list(set(new) - set(old))
        if len(created):
            for attr in created:
                cmds.setKeyframe(obj + '.' + attr, v=1)
    if not attrs:
        message('No PAIRBLEND or CONSTRAINT found: -- ' + obj)
        return None
        '''
        message(
            'No PAIRBLEND or CONSTRAINT found. Creating a new locator to bake.')
        loc = locatorOnSelection(
            ro='zxy', X=1.0, constrain=True, toSelection=True)[0]
        bakeStep(loc, time=(time[0], time[1]), sim=True, uiOff=uiOff)
        cmds.autoKeyframe(state=autoK)
        return None
        '''
    #
    cmds.currentTime(i)
    #
    if sim:
        while i <= max:
            cmds.currentTime(i)
            # what am i keying  ???
            for attr in attrs:
                cmds.setKeyframe(attr)
            i = i + 1
    else:
        cmds.currentTime(cmds.findKeyframe(which='previous'))
        if keyframes:
            for key in keyframes:
                if key >= min and key <= max:
                    cmds.currentTime(key)
                    for attr in attrs:
                        cmds.setKeyframe(attr)
        else:
            # message('no keys__________________________')
            bakeStep(obj, time=(time[0], time[1]), sim=True, uiOff=uiOff)
            cmds.autoKeyframe(state=autoK)
            return None
    if attrs:
        # add option to only correct tangents of baked frames
        cmds.keyTangent(
            attrs, edit=True, itt='auto', ott='auto', time=(time[0], time[1]))
    cmds.currentTime(current)
    cmds.autoKeyframe(state=autoK)
    if uiOff:
        uiEnable(controls='modelPanel')


def bakeConstrained(obj, removeConstraint=True, timeLine=False, sim=False, uiOff=True, timeOverride=()):
    if uiOff:
        uiEnable()
    # workaround
    sel = cmds.ls(sl=1)
    # needs to beselected to prioritze keyed range of given object over
    # selection
    cmds.select(obj)
    # build bake range
    gRange = fr.Get()
    # reselect selection
    cmds.select(sel)
    # end workaround
    cons = getConstraint(obj)
    blndAttr = getBlendAttr(obj, delete=False)
    keyedOrig = keyedFrames(obj)
    #
    print gRange.start, gRange.end, '___baking feed'
    # print 'start baking\n'
    if timeLine:
        message('Bake range: ' + str(gRange.start) + ' - ' + str(gRange.end))
        bakeStep(obj, time=(gRange.start, gRange.end), sim=sim)
        # print 'done baking\n'
    else:
        if timeOverride:
            bakeStep(obj, time=(timeOverride[0], timeOverride[1]), sim=sim)
            message(
                'Bake range: ' + str(gRange.start) + ' - ' + str(gRange.end))
        else:
            if keyedOrig is not None:
                '''
                message(
                    '0  Bake range: ' + str(gRange.keyStart) + ' - ' + str(gRange.keyEnd))
                    '''
                if gRange.keyStart == gRange.keyEnd:
                    bakeStep(obj, time=(gRange.start, gRange.end), sim=sim)
                    message(
                        'Bake range: ' + str(gRange.start) + ' - ' + str(gRange.end))
                    # print '1  done baking\n'
                else:
                    bakeStep(obj, time=(gRange.keyStart, gRange.keyEnd), sim=sim)
                    message(
                        'Bake range: ' + str(gRange.keyStart) + ' - ' + str(gRange.keyEnd))
                    # print '2  done baking\n'
            else:
                message("Target object has no keys. Can't bake to keyed timeline.  Bake range: " +
                        str(gRange.start) + ' - ' + str(gRange.end))
                bakeStep(obj, time=(gRange.start, gRange.end), sim=sim)
                # print '3  done baking\n'
    # keyedBake = keyedFrames(obj)
    # print 'frames\n'
    eulerFilter(obj)
    if removeConstraint:
        deleteList(cons)
        deleteAttrList(blndAttr)

    # recover range
    if gRange.selection:
        gRange.selRangeRecover()
    '''
    if sparseKeys:
        if keyedOrig:
            for key in keyedBake:
                if key not in keyedOrig:
                    cmds.cutKey(obj, t=(key,key))
        else:
            message("Baked! Didn't create sparseKeys. Object had no keys.")
            '''
    # print 'done\n'
    if uiOff:
        uiEnable()


def bakeConstrainedSelection(removeConstraint=True, timeLine=False, sim=False, uiOff=True, timeOverride=()):
    sel = cmds.ls(sl=True)
    if len(sel) != 0:
        # i = 1
        # num = len(sel)
        for obj in sel:
            # message(str(i) + ' of ' + str(num) + ' --  ' + obj, maya=True)
            # i = i+1
            bakeConstrained(
                obj, removeConstraint=removeConstraint, timeLine=timeLine, sim=sim, uiOff=uiOff, timeOverride=timeOverride)
    else:
        cmds.warning('Select constrained object(s)')


def controllerToLocator(obj=None, p=True, r=True, timeLine=False, sim=False, size=1, uiOff=True, color=30, suffix='__BAKE__', matchSet=True, shape='loc_ctrl'):
    '''
    all three axis per transform type have to be unlocked, all rotates or translates
    takes every object in selection creates a locator in world space
    constraints locator to control
    bakes animation to locator
    deletes constraint
    constrains controller to locator
    '''
    # bake from timeline  and selection
    if not obj:
        sel = cmds.ls(sl=True)
    else:
        if type(obj) != list:
            sel = [obj]
        else:
            sel = obj
    pos = ['tx', 'ty', 'tz']
    rot = ['rx', 'ry', 'rz']
    posSkp = []
    rotSkp = []
    cnT = None
    cnR = None
    locs = []
    if len(sel) != 0:
        for item in sel:
            # setup locator
            if not getConstraint(item):
                lc = locator(obj=item, ro='zxy', X=size, constrain=False, toSelection=False, suffix=suffix, color=color, matchSet=False, shape=shape)[0]
                # check keyable transforms
                tState = cmds.getAttr(item + '.tx', k=True)
                rState = cmds.getAttr(item + '.rx', k=True)
                # if translates are keyable constrain locator and store constraint
                # in cnT
                if tState:
                    cnT = cmds.pointConstraint(item, lc, mo=False)
                # if rotations are keyable constrain locator and store constraint
                # in cnR
                if rState:
                    cnR = cmds.orientConstraint(item, lc, mo=False)
                # bake locator in frame range
                matchKeyedFrames(item, lc)
                bakeConstrained(
                    lc, removeConstraint=False, timeLine=timeLine, sim=sim, uiOff=uiOff)
                if sim is not True:
                    matchKeyedFrames(item, lc)
                if p is False:
                    if cnT is not None:
                        cmds.delete(cnT)
                    cnT = None
                if r is False:
                    if cnR is not None:
                        cmds.delete(cnR)
                    cnR = None
                # if both cnT and cnR are not None a parent constraint can be
                # used...
                if cnT and cnR is not None:
                    try:
                        cmds.delete(cnT)
                    except:
                        pass
                    try:
                        cmds.delete(cnR)
                    except:
                        pass
                    cmds.parentConstraint(lc, item, mo=False)
                # ...else use point or orient constraint. Must assume pos or rot wont be constrained or edited with new locator
                else:
                    if cnT is not None:
                        # in this state it is assumed a translates are keyable, a
                        # contraint was made
                        cmds.delete(cnT)
                        cnStick = cmds.orientConstraint(item, lc, mo=False)
                        cmds.pointConstraint(lc, item, mo=False)
                        for axis in rot:
                            cmds.cutKey(lc, at=axis, cl=True, t=())
                            cmds.setAttr(lc + '.' + axis, k=False, cb=True)
                            cmds.setAttr(lc + '.' + axis, l=True)
                    if cnR is not None:
                        # in this state it is assumed a rotations are keyable, a
                        # constraint was made
                        cmds.delete(cnR)
                        cnStick = cmds.pointConstraint(item, lc, mo=False)
                        cmds.orientConstraint(lc, item, mo=False)
                        for axis in pos:
                            cmds.cutKey(lc, at=axis, cl=True, t=())
                            cmds.setAttr(lc + '.' + axis, k=False, cb=True)
                            cmds.setAttr(lc + '.' + axis, l=True)
                cnT = None
                cnR = None
                if matchSet:
                    cs.matchCharSet(source=item, objs=[lc])
                locs.append(lc)
                prnt = plc.assetParent(item)
                cmds.parent(lc, prnt)
            else:
                message('Object is already constrained')
        return locs
    else:
        cmds.warning(
            'Select an object. Selection will be constrained to a locator with the same anim.')


def locator(obj=None, ro='zxy', X=0.01, constrain=True, toSelection=False, suffix='__PLACE__', color=30, matchSet=True, shape='loc_ctrl'):
    '''
    matchSet only if locators hierarchy wont be edited. The connection forces the attributes to stay at their pre-edited value 
    '''
    locs = []
    roo = None
    if obj is not None:
        if not shape:
            lc = cmds.spaceLocator(name=plc.getUniqueName(obj + suffix))[0]
            locSize(lc, X=X)
            objColor(lc, color)
        else:
            lc = plc.circle(name=plc.getUniqueName(obj + suffix), obj=obj, color=color, shape=shape)[0]
            s = getControlSize(obj)
            if s:
                putControlSize(lc, s * X)
            else:
                putControlSize(lc, X)
            # print getControlSize(lc), 'edited'
        # print lc
        cmds.setAttr(lc + '.sx', k=False, cb=True)
        cmds.setAttr(lc + '.sy', k=False, cb=True)
        cmds.setAttr(lc + '.sz', k=False, cb=True)
        cmds.setAttr(lc + '.v', k=False, cb=True)
        if '.' in obj:  # component selection
            roo = 0
        else:
            roo = cmds.getAttr(obj + '.rotateOrder')
        if '.' in obj:  # component selection
            t = cmds.pointPosition(obj)
            r = 0.0, 0.0, 0.0
            # print t
        else:
            r = cmds.xform(obj, q=True, ws=True, ro=True)
            t = cmds.xform(obj, q=True, ws=True, rp=True)
        cmds.setAttr(lc + '.rotateOrder', roo)
        cmds.xform(lc, ws=True, t=t, ro=r)
        cmds.xform(lc, roo=ro)
        if constrain:
            if toSelection:
                constrainEnabled(obj, lc, mo=True)
                # cmds.parentConstraint(obj, lc, mo=True)
            else:
                constrainEnabled(lc, obj, mo=True)
                # cmds.parentConstraint(lc, obj, mo=True)
        locs.append(lc)
        if matchSet:
            cs.matchCharSet(source=obj, objs=locs)
    else:
        loc = cmds.spaceLocator()[0]
        cmds.xform(loc, roo=ro)
        loc = cmds.rename(loc, plc.getUniqueName('locator' + suffix))
        locs.append(loc)
    # hj.hijackAttrs(locs[0], locs[0], 'overrideColor', 'color', set=True, default=None)
    return locs


def objColorHijack(obj=''):
    cmds.setAttr(obj + '.overrideEnabled', 1)
    cmds.setAttr(obj + '.overrideColor', 1)


def locatorOnSelection(ro='zxy', X=1.0, constrain=True, toSelection=False, color=30, matchSet=False):
    sel = cmds.ls(sl=True)
    locs = []
    if len(sel) != 0:
        for item in sel:
            locs.append(locator(
                obj=item, ro=ro, X=X, constrain=constrain, toSelection=toSelection, color=color, matchSet=matchSet)[0])
    else:
        locs.append(
            locator(ro=ro, X=X, constrain=False, toSelection=toSelection, color=color, matchSet=matchSet))
    return locs


def getControlSize(obj=''):
    '''sel[0]
    gets high average bbox size, use to establish default size of a new control based on selection
    '''
    shapeNode = cmds.listRelatives(obj, shapes=True)
    if shapeNode:
        shapeNode = shapeNode[0]
        minBB = cmds.getAttr(shapeNode + '.boundingBoxMin')
        maxBB = cmds.getAttr(shapeNode + '.boundingBoxMax')
        x = maxBB[0][0] - minBB[0][0]
        y = maxBB[0][1] - minBB[0][1]
        z = maxBB[0][2] - minBB[0][2]
        mn = sorted([x, y, z])[0]
        mx = sorted([x, y, z])[-1]
        high = ((mx - mn) / 4.0) * 3
        return mn + high
    else:
        return None


def putControlSize(obj='', sizeBB=1.0):
    currentBB = getControlSize(obj)
    if currentBB:
        mltp = (sizeBB / currentBB)
        shapeNode = cmds.listRelatives(obj, shapes=True)[0]
        if cmds.nodeType(shapeNode) == 'nurbsCurve':
            cvInfo = cmds.getAttr(shapeNode + '.cv[*]')
            for i in range(0, len(cvInfo), 1):
                crnt = cmds.xform(shapeNode + '.cv[' + str(i) + ']', query=True, os=True, t=True)
                cmds.xform(shapeNode + '.cv[' + str(i) + ']', os=True, t=[crnt[0] * mltp, crnt[1] * mltp, crnt[2] * mltp])
        else:
            return None


def locSize(lc, X=0.5):
    axis = ['X', 'Y', 'Z']
    # sketchy path building
    if '|' in lc:
        # print lc
        lc = '|' + lc.split('|')[1] + lc
        # print lc, '++++++++++++'
    for axs in axis:
        cmds.setAttr(lc + 'Shape.localScale' + axs, X)
        # cmds.setAttr(lc + '.scale' + axs, X)


def objColor(obj='', color=07):
    # print obj, '---------'
    cmds.setAttr(obj + '.overrideEnabled', 1)
    cmds.setAttr(obj + '.overrideColor', color)


def null(obj='', suffix='', order='zxy'):
    sel = cmds.ls(sl=True, fl=True, l=True)[0]
    if obj:
        sel = obj
    if sel:
        m = cmds.xform(sel, q=True, m=True, ws=True)
        n = cmds.group(name=sel + suffix, em=True)
        cmds.xform(n, m=m, ws=True)
        if order:
            cmds.xform(n, roo=order)
        return n
    else:
        message('select one object or use the "obj" variable')
        return None


def attrStrings(pos=True, rot=True, period=True):
    p = ['tx', 'ty', 'tz']
    r = ['rx', 'ry', 'rz']
    result = []
    if period:
        for i in range(len(p)):
            p[i] = '.' + p[i]
        for i in range(len(r)):
            r[i] = '.' + r[i]
    if pos:
        result.append(p)
    if rot:
        result.append(r)
    return result


def constrainEnabled(obj1, obj2, mo=True):
    # check keyable transforms
    tState = cmds.getAttr(obj2 + attrStrings(rot=False)[0][0], k=True)
    rState = cmds.getAttr(obj2 + attrStrings(pos=False)[0][0], k=True)
    allState = [tState, rState]
    if False not in allState:
        cnAll = cmds.parentConstraint(obj1, obj2, mo=mo)
        # print 'here ========='
        return cnAll
    else:
        # print 'there ========='
        result = []
        # if translates are keyable constrain locator and store constraint in
        # cnT
        if tState:
            cnT = cmds.pointConstraint(obj1, obj2, mo=mo)
            result.append(cnT)
        # if rotations are keyable constrain locator and store constraint in
        # cnR
        if rState:
            cnR = cmds.orientConstraint(obj1, obj2, mo=mo)
            result.append(cnR)
        return result[0]


def stickAttr():
    return 'STICKY'


def stick(offset=True):
    # needs work
    sel = cmds.ls(sl=True)
    gRange = fr.Get()
    if len(sel) == 1:
        sel = sel[0]
        loc = locator(sel, X=1.5, constrain=False, shape=False)[0]
        # print loc
        cmds.addAttr(loc, longName=stickAttr(), at='message')
        cmds.connectAttr(sel + '.message', loc + '.' + stickAttr())
        name = loc.replace(
            'PLACE', stickAttr() + '_frame' + str(int(gRange.current)))
        loc = cmds.rename(loc, name)
        # print loc
        constrainEnabled(loc, sel, mo=True)
    elif len(sel) == 2:
        constrainEnabled(sel[1], sel[0], mo=offset)
    else:
        cmds.warning(
            '      #    Stick to world = Select 1 object.       #    Stick to 2nd selection = Select 2 objects.')


def unStick(timeLine=False, sim=False):
    # needs work
    activeSet = cs.GetSetOptions()
    sel = cmds.ls(sl=True)
    gRange = fr.Get()
    start = None
    end = None
    if gRange.range == 1:
        if gRange.current == gRange.selStart:
            start = gRange.current
            end = gRange.current
        else:
            print gRange.current
            print gRange.range
            print gRange.selStart, gRange.selEnd
    else:
        start = gRange.selStart
        end = gRange.selEnd
    # cons = getConstraint(sel)
    print start, end, '___'
    if activeSet.current:
        bakeConstrainedSelection(
            removeConstraint=True, timeLine=timeLine, sim=sim, timeOverride=(start, end))

    else:
        bakeConstrainedSelection(
            removeConstraint=True, timeLine=timeLine, sim=sim, timeOverride=(start, end))
    # delete associated objects
    blndAttr = getBlendAttr(sel, delete=True)
    # cmds.delete(cons)
    plugs = cmds.listConnections(sel[0] + '.message', s=False, d=True, p=True)
    if plugs is not None:
        for p in plugs:
            if '.' + stickAttr() in p:
                cmds.delete(p.split('.')[0])


class Key():

    def __init__(self, obj, attr, frame):
        self.obj = obj
        self.attr = attr
        self.frame = frame
        self.value = None
        self.inTangentType = None
        self.inWeight = None
        self.inAngle = None
        self.outTangentType = None
        self.outWeight = None
        self.outAngle = None
        self.lock = None
        self.get()

    def get(self):
        index = cmds.keyframe(self.obj, q=True, time=(
            self.frame, self.frame), at=self.attr, indexValue=True)[0]
        self.value = cmds.keyframe(
            self.obj, q=True, index=(index, index), at=self.attr, valueChange=True)[0]
        self.inAngle = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, inAngle=True)[0]
        self.outAngle = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, outAngle=True)[0]
        self.inTangentType = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, inTangentType=True)[0]
        self.outTangentType = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, outTangentType=True)[0]
        self.inWeight = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, inWeight=True)[0]
        self.outWeight = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, outWeight=True)[0]
        self.lock = cmds.keyTangent(self.obj, q=True, time=(
            self.frame, self.frame), attribute=self.attr, lock=True)[0]

    def put(self):
        cmds.setKeyframe(
            self.obj, at=self.attr, time=(self.frame, self.frame), value=self.value)
        cmds.keyTangent(self.obj, edit=True, time=(self.frame, self.frame), attribute=self.attr,
                        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inWeight=self.inWeight,
                        outWeight=self.outWeight, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock)


class AnimCrv(Key):

    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
        self.crv = cmds.findKeyframe(self.obj, at=self.attr, c=True)
        self.frames = []
        self.key = []
        self.value = cmds.getAttr(self.obj + '.' + self.attr)
        self.qualify()

    def qualify(self):
        if self.crv is not None:
            if len(self.crv) == 1:
                self.crv = self.crv[0]
                self.keyedFrames()
                self.keyAttrs()

    def keyedFrames(self):
        if self.crv is not None:
            framesTmp = cmds.keyframe(self.crv, q=True)
            for frame in framesTmp:
                self.frames.append(frame)
            self.frames = list(set(self.frames))
            self.frames.sort()

    def keyAttrs(self):
        for frame in self.frames:
            a = Key(self.obj, self.attr, frame)
            self.key.append(a)

    def build(self, replace=True):
        if replace:
            self.crv = cmds.findKeyframe(self.obj, at=self.attr, c=True)
            if self.crv:
                cmds.delete(self.crv)
        for key in self.key:
            key.obj = self.obj
            key.put()


def consolidatePairBlends():
    # BUG: If given control has 2 pairblends consolidate
    # connected check if the source is the same constraint. If yes, consolidate or check to make sure weight attr is affected by both
    pass


def bakeUndo():
    que = cmds.undoInfo(q=1, un=1)
    if 'bake' in que.lower() or 'changeRO' in que.lower() or 'changeRo' in que.lower() or 'aimRig' in que or 'switch' in que.lower() or 'parentRig' in que.lower():
        uiEnable()
        cmds.undo()
        uiEnable()
        message(que)
    else:
        cmds.undo()


def quickUndo():
    que = 'Undo Action: ' + cmds.undoInfo(q=1, un=1)
    uiEnable()
    cmds.undo()
    uiEnable()
    message(que, maya=True)
