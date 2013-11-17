import maya.cmds as cmds
import maya.mel as mel
import characterSet_lib as cs

def message(what='', maya=False):
    #print
    what = '-- ' + what + ' --'
    if maya == True:
    	mel.eval('print \"' + what + '\";')
    else:
        print what

def listX(l=[]):
    if l != None:
        if len(l) != None:
            return list(set(l))
        else:
            return l

def matchKeyedFramesLoop():
    '''
    uses first selection to add keys on consequent objects in selection
    '''
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        #one object selected, add same key on all curves
        matchKeyedFrames(AAA=None, BBB=None, subtractive=True)
    else:
        #2 objects
        obj1 = sel[0]
        for item in sel:
            if item != obj1:
                cmds.select(obj1, item)
                matchKeyedFrames(AAA=None, BBB=None, subtractive=True)
        cmds.select(sel)

def matchKeyedFrames(AAA=None, BBB=None, subtractive=True):
    '''
    AAA = get keyed frames
    BBB = put keyed frames
    '''
    sel = cmds.ls(sl=True)
    crvs = cmds.keyframe(sel[0], q=True, name=True)
    if crvs == None:
        message('No keys on object', maya=True)
        return None
    if AAA==None and BBB==None:
        if len(sel) == 2:
            AAA = sel[0]
            BBB = sel[1]
        elif len(sel) == 1:
            AAA = sel[0]
            BBB = sel[0]
        else:
            message('Select 1 or 2 objects. Second object will get matching timeline keys.')
            return None
    #add additive or destructive
    #keyed frames on AAA
    framesAdd = keyedFrames(AAA)
    print framesAdd
    #list attrs on BBB and add key
    old = cmds.listAttr(BBB, k=True)
    for attr in old:
        try:
            if cmds.setKeyframe(BBB + '.' + attr, i=True) == 0:
                cmds.setKeyframe(BBB + '.' + attr)
        except:
              print 'sanity check: FAILED ATTRS ____', BBB, attr
    #check if new constraint blend attr is created after keying
    new = cmds.listAttr(BBB, k=True)
    created = list(set(new)-set(old))
    if len(created) != 0:
        for attr in created:
            cmds.setKeyframe(BBB + '.' + attr, v=1)
    #add keys to BBB from AAA
    for frame in framesAdd:
        cmds.setKeyframe(BBB, i=True, t=frame)
    if subtractive == True:
        #remove keys from BBB, which AAA doesnt have
        min = framesAdd[0]
        max = framesAdd[len(framesAdd)-1]
        framesRem = keyedFrames(BBB)
        for frame in framesRem:
            if frame not in framesAdd:
                cmds.cutKey(BBB, t=(frame,frame))
    #check if current frame should be keyed
    current = cmds.currentTime(q=True)
    if current not in framesAdd:
        cmds.cutKey(BBB, t=(current,current))

class GetRange():
    def __init__(self):
        self.min       = cmds.playbackOptions(q=True, minTime=True)
        self.max       = cmds.playbackOptions(q=True, maxTime=True)
        self.selStart  = cmds.playbackOptions(q=True, minTime=True)
        self.selEnd    = cmds.playbackOptions(q=True, maxTime=True)
        self.start     = 0
        self.end       = 0
        self.current   = cmds.currentTime(q=True)
        self.setStartEnd()
        self.keyStart  = 0
        self.keyEnd    = 0
        self.keyedFrames()
        #Has to be last
        self.selRange()
            
    def selRange(self):
        #overide range if selected range is detected
        sel = cmds.timeControl('timeControl1', q=True, ra=True)
        range = sel[1] - sel[0]
        if range > 1:
            self.selStart = sel[0]
            self.selEnd = sel[1]
            self.keyStart = sel[0]
            self.keyEnd = sel[1]

    def setStartEnd(self):
        if self.selStart != 0:
            self.start = self.selStart
            self.end = self.selEnd
        else:
            self.start = self.min
            self.end = self.max

    def keyedFrames(self):
        selAll = cmds.ls(sl=True)
        frames = []
        if selAll:
            for sel in selAll:
                animCurves = cmds.findKeyframe(sel, c=True)
                if animCurves != None:
                    for crv in animCurves:
                        framesTmp = cmds.keyframe(crv, q=True)
                        for frame in framesTmp:
                            frames.append(frame)
                    frames = list(set(frames))
                    #print frames
                    self.keyStart = min(frames)
                    self.keyEnd = max(frames)
        else:
            print '-- Select an object. --'

def keyedFrames(obj):
    animCurves = cmds.findKeyframe(obj, c=True)
    if animCurves != None:
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

def constraintRig(*args):
    #store selection
    sel = cmds.ls(sl=True)
    #place 3 locators on selection
    loc1 = locator(obj=sel[0], constrain=False, X=1)
    loc2 = locator(obj=sel[1], constrain=False, X=1)
    spin = locator(obj=sel[1], constrain=False, X=1)
    #rename
    offset = cmds.rename(loc1, sel[0] + '__OFFSET')
    spin = cmds.rename(spin, sel[0] + '__SPIN')
    root = cmds.rename(loc2, sel[0] + '__ROOT')
    cmds.parent(offset, spin)
    cmds.parent(spin, root)
    cmds.parentConstraint(sel[1], root, mo=True)
    #bake anim to offset loc
    cmds.parentConstraint(sel[0], offset, mo=True)
    cmds.select(sel[0], offset)
    matchKeyedFrames(AAA=sel[0], BBB=offset, subtractive=True)
    bakeConstrained(offset, sparseKeys=True, removeConstraint=True, timeLine=False, sim=False)
    #create final rig constraints
    constrainEnabled(offset, sel[0], mo=True)
    #cmds.parentConstraint(offset, sel[0], mo=True)
    locSize(root, X=0.1)
    cmds.select(offset)

class reConnect():
    '''
    Use to reconnect after baking animation. For now only works with pairBlends. Which means the object should be keyed and have some type of attribute driver. (ie, constraint, motion trail)
    '''
    def __init__(self, sel=''):
        self.selection       = sel
        self.pairs           = {}
        self.nodes           = []
        self.getDict()
        self.getNodes()

    def getNodes(self):
        self.nodes = list(set(cmds.listConnections(self.selection, s=True, d=False)))

    def getDict(self):
        #get attributes
        connections = cmds.listConnections(self.selection, s=True, d=False, type='pairBlend', c=True )
        if connections != None:
            for con in connections:
                if '.' in con:
                    #build key:value pair
                    self.pairs[con] = cmds.listConnections(con, s=True, d=False, type='pairBlend', p=True )[0]
        else:
            cmds.warning('No pairBlend node was found')

    def connect(self):
        #reconnect pairBlend.
        for key in self.pairs:
            try:
                cmds.connectAttr(self.pairs[key], key, f=True)
            except:
                message('Failed Connection -- ' + self.pairs[key] + ' -- to -- ' + key)

def updateConstrainedCurves(obj=None):
    if obj == None:
        obj = cmds.ls(sl=True)
        if len(obj) != 1:
            message('Select one object.')
            return None
        else:
            obj = cmds.ls(sl=True)[0]
    print obj
    #getBlendAttr returns list, need for loop
    blndAttrs = getBlendAttr(obj)
    blndAttrState = []
    for attr in blndAttrs:
        blndAttrState.append(AnimCrv(obj, attr.split('.')[1]))
    #print blndAttrState
    #state = AnimCrv(obj, getBlendAttr(obj)[0].split('.')[1])
    #connection class
    rcc = reConnect(obj)
    #bake attributes driven by pairBlend
    objAttrs = getDrivenAttrsByNodeType(obj)
    bakeConstrained(objAttrs, sparseKeys=True, removeConstraint=False, timeLine=False)
    #reconnect constraint/pairBlend
    rcc.connect()
    for state in blndAttrState:
        if state.crv != None:
            state.build()
        else:
            cmds.setAttr(obj + '.' + state.attr, state.value)

def eulerFilter(obj):
    curves = cmds.keyframe(obj, q=True, name=True)
    euler = []
    for crv in curves:
        if 'rotate' in crv.lower():
            euler.append(crv)
    if len(euler) != 0:
        cmds.filterCurve(euler)

def getConstraint(obj, nonKeyedRoute=True, keyedRoute=True, plugRoute=True):
    #fails with characterSets
    cons = []
    if plugRoute == True:
        #if character set is connected, other checks fail
        #this method asks for specific plug string
        #if plug is consistent with all constraints, this may be most reliable
        plug = getDriven(obj, typ='constraint', plugs=True)
        if plug:
            for p in plug:
                if 'constraintParentInverseMatrix' in p:
                    cons.append(p.split('.')[0])
    if nonKeyedRoute == True:
        con = listX(cmds.listConnections(obj, s=True, d=False, t='constraint'))
        if con:
            for c in con:
                cons.append(c)
    if keyedRoute == True:
        p = listX(cmds.listConnections(obj, s=True, d=False, t='pairBlend'))
        if p:
            con = listX(cmds.listConnections(p, s=True, d=False, t='constraint'))
            if con != None:
                for c in con:
                    cons.append(c)
    return listX(cons)

def getDrivers(obj, typ='', plugs=True):
    #Returns nodes that are driving given node
    #typ=return only node types
    #plugs=True will return with driving attribute(s)
    con = cmds.listConnections(obj, d=False, s=True, t=typ, plugs=plugs)
    if con != None:
        con = list(set(con))
    return con

def getDriven(obj, typ='', plugs=True):
    #Returns nodes that are driven by given node
    #typ=return only node types
    #plugs=True will return with driven attribute(s)
    con = cmds.listConnections(obj, s=False, d=True, t=typ, plugs=plugs)
    if con != None:
        con = list(set(con))
    return con

def getDrivenAttrsByNodeType(obj, typ='pairBlend'):
    #Returns attributes of the given object which are driven by a node type
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
    if con != None:
        con = listX(con)
        for c in con:
            if '.blend' in c:
                attrs.append(c)
        if len(attrs) != 0:
            if delete == True:
                for attr in attrs:
                    cmds.deleteAttr(attrs[0])
                    message('Attribute  ' + attrs[0] + '  is deleted')
            else:
                return attrs
        else:
            print 'no attrs'

def deleteAttrList(objects):
    if objects != None:
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
            
def bakeConstrained(obj, sparseKeys=True, removeConstraint=True, timeLine=False, sim=False):
    gRange = GetRange()
    cons = getConstraint(obj)
    blndAttr = getBlendAttr(obj, delete=False)
    keyedOrig = keyedFrames(obj)
    if timeLine == True:
        message('Bake range: ' + str(gRange.start) + ' - ' + str(gRange.end))
        cmds.bakeResults( obj, t=(gRange.start,gRange.end), simulation=sim, pok=True)
    else:
        if keyedOrig != None:
            message('Bake range: ' + str(gRange.keyStart) + ' - ' + str(gRange.keyEnd))
            if gRange.keyStart == gRange.keyEnd:
                cmds.bakeResults( obj, t=(gRange.start,gRange.end), simulation=sim, pok=True)
                message('Bake range: ' + str(gRange.start) + ' - ' + str(gRange.end))
            else:
                cmds.bakeResults( obj, t=(gRange.keyStart,gRange.keyEnd), simulation=sim, pok=True)
                message('Bake range: ' + str(gRange.keyStart) + ' - ' + str(gRange.keyEnd))
        else:
            message("Target object has no keys. Can't bake to keyed timeline.  Bake range: " + str(gRange.start) + ' - ' + str(gRange.end))
            cmds.bakeResults( obj, t=(gRange.start,gRange.end), simulation=sim, pok=True)
    keyedBake = keyedFrames(obj)
    eulerFilter(obj)
    if removeConstraint == True:
        deleteList(cons)
        deleteAttrList(blndAttr)
    if sparseKeys:
        if keyedOrig != None:
            for key in keyedBake:
                if key not in keyedOrig:
                    cmds.cutKey(obj, t=(key,key))
        else:
            message("Baked! Didn't create sparseKeys. Object had no keys.")

def bakeConstrainedSelection(sparseKeys=True, removeConstraint=True, timeLine=False, sim=False):
    sel = cmds.ls(sl=True)
    if len(sel) != 0:
        for obj in sel:
            bakeConstrained(obj, sparseKeys=sparseKeys, removeConstraint=removeConstraint, timeLine=timeLine, sim=sim)
    else:
        cmds.warning('Select constrained object(s)')

def locSize(lc, X=0.5):
    axis = ['X','Y','Z']
    for axs in axis:
        cmds.setAttr(lc + 'Shape.localScale' + axs, X)

def controllerToLocator(p=True, r=True, sparseKeys=True, timeLine=False):
    '''
    all three axis per transform type have to be unlocked, all rotates or translates
    takes every object in selection creates a locator in world space
    constraints locator to control
    bakes animation to locator
    deletes constraint
    constrains controller to locator
    '''
    #bake from timeline  and selection 
    sel = cmds.ls(sl=True)
    pos = ['tx','ty','tz']
    rot = ['rx','ry','rz']
    posSkp = []
    rotSkp = []
    cnT = None
    cnR = None
    locs = []
    if len(sel) != 0:
        for item in sel:
            #setup locator
            lc = cmds.spaceLocator(name=item + '__BAKE__')[0]
            locSize(lc, X=4)
            cmds.setAttr(lc + '.sx', k=False, cb=True)
            cmds.setAttr(lc + '.sy', k=False, cb=True)
            cmds.setAttr(lc + '.sz', k=False, cb=True)
            cmds.setAttr(lc + '.v', k=False, cb=True)
            cmds.setAttr(lc + '.rotateOrder', 2)
            #check keyable transforms
            tState = cmds.getAttr(item + '.tx', k=True)
            rState = cmds.getAttr(item + '.rx', k=True)
            #if translates are keyable constrain locator and store constraint in cnT
            if tState == True:
                cnT = cmds.pointConstraint(item, lc, mo=False)
            #if rotations are keyable constrain locator and store constraint in cnR
            if rState == True:
                cnR = cmds.orientConstraint(item, lc, mo=False)
            #bake locator in frame range
            matchKeyedFrames(item, lc)
            bakeConstrained(lc, sparseKeys=False, removeConstraint=False, timeLine=timeLine)
            if sparseKeys == True:
                matchKeyedFrames(item, lc)
            if p == False:
                if cnT != None:
                    cmds.delete(cnT)
                cnT = None
            if r == False:
                if cnR != None:
                    cmds.delete(cnR)
                cnR = None
            #if both cnT and cnR are not None a parent constraint can be used...
            if cnT and cnR != None:
                cmds.delete(cnT)
                cmds.delete(cnR)
                cmds.parentConstraint(lc, item, mo=False)
            #...else use point or orient constraint. Must assume pos or rot wont be constrained or edited with new locator
            else:
                if cnT != None:
                    #in this state it is assumed a translates are keyable, a contraint was made
                    cmds.delete(cnT)
                    cnStick = cmds.orientConstraint(item, lc, mo=False)
                    cmds.pointConstraint(lc, item, mo=False)
                    for axis in rot:
                        cmds.cutKey(lc, at=axis, cl=True, t=())
                        cmds.setAttr(lc + '.' + axis, k=False, cb=True)
                        cmds.setAttr(lc + '.' + axis, l=True)
                if cnR != None:
                    #in this state it is assumed a rotations are keyable, a constraint was made
                    cmds.delete(cnR)
                    cnStick = cmds.pointConstraint(item, lc, mo=False)
                    cmds.orientConstraint(lc, item, mo=False)
                    for axis in pos:
                        cmds.cutKey(lc, at=axis, cl=True, t=())
                        cmds.setAttr(lc + '.' + axis, k=False, cb=True)
                        cmds.setAttr(lc + '.' + axis, l=True)
            locs.append(lc)
        return locs
    else:
        cmds.warning('Select an object. Selection will be constrainted to a locator with the same anim.')

def locator(obj=None, ro='zxy', X=0.01, constrain=True):
    locs = []
    plc = '__PLACE__'
    if obj != None:
        lc = cmds.spaceLocator(name=obj + plc)[0]
        print lc
        cmds.setAttr(lc + '.sx', k=False, cb=True)
        cmds.setAttr(lc + '.sy', k=False, cb=True)
        cmds.setAttr(lc + '.sz', k=False, cb=True)
        cmds.setAttr(lc + '.v', k=False, cb=True)
        locSize(lc, X=X)
        locs.append(lc)
        roo = cmds.getAttr(obj + '.rotateOrder')
        r = cmds.xform(obj, q=True, ws=True, ro=True )
        t = cmds.xform(obj, q=True, ws=True, rp=True )
        cmds.xform(lc, t=t, ro=r)
        cmds.setAttr(lc + '.rotateOrder', roo)
        cmds.xform(lc, roo=ro )
        if constrain == True:
            cmds.parentConstraint(obj, lc, mo=True)
    else:
        loc = cmds.spaceLocator()[0]
        cmds.xform(loc, roo=ro )
        loc = cmds.rename(loc, 'locator' + plc)
        locs.append(loc)
    return locs

def locatorOnSelection(ro='zxy', X=0.01, constrain=True):
    sel = cmds.ls(sl=True)
    locs = []
    if len(sel) != 0:
        for item in sel:
            locs.append(locator(obj=item, ro=ro, X=X, constrain=constrain)[0])
    else:
        locs.append(locator(ro=ro, X=X, constrain=False))
    return locs

def locSize(lc, X=0.5):
    axis = ['X','Y','Z']
    for axs in axis:
        cmds.setAttr(lc + 'Shape.localScale' + axs, X)

def attrStrings(pos=True, rot=True, period=True):
    p = ['tx','ty','tz']
    r = ['rx','ry','rz']
    result = []
    if period == True:
        for i in range(len(p)):
            p[i] = '.' + p[i]
        for i in range(len(r)):
            r[i] = '.' + r[i]
    if pos == True:
        result.append(p)
    if rot == True:
        result.append(r)
    return result

def constrainEnabled(obj1, obj2, mo=True):
    #check keyable transforms
    tState = cmds.getAttr(obj2 + attrStrings(rot=False)[0][0], k=True)
    rState = cmds.getAttr(obj2 + attrStrings(pos=False)[0][0], k=True)
    allState = [tState, rState]
    if False not in allState:
        cnAll = cmds.parentConstraint(obj1, obj2, mo=mo)
        return cnAll
    else:
        result = []
        #if translates are keyable constrain locator and store constraint in cnT
        if tState == True:
            cnT = cmds.pointConstraint(obj1, obj2, mo=mo)
            result.append(cnT)
        #if rotations are keyable constrain locator and store constraint in cnR
        if rState == True:
            cnR = cmds.orientConstraint(obj1, obj2, mo=mo)
            result.append(cnR)
        return result[0]

def collectEnabled():
    #check keyable transforms
    tState = cmds.getAttr(obj2 + attrStrings(rot=False)[0][0], k=True)
    rState = cmds.getAttr(obj2 + attrStrings(pos=False)[0][0], k=True)
    attrs = []
    if tState == True:
        pass

def collectOrigCurves(obj):
    pass

def collectNewCurves(obj):
    pass

def mergeCurves(obj, orig, new):
    pass

def stickAttr():
    return 'STICKY'

def stick(offset=True):
    #needs work
    sel = cmds.ls(sl=True)
    gRange = GetRange()
    if len(sel) == 1:
        sel = sel[0]
        loc = locator(sel, X=1, constrain=False)[0]
        print loc
        cmds.addAttr(loc, longName=stickAttr(), at='message')
        cmds.connectAttr(sel + '.message', loc + '.' + stickAttr())
        name = loc.replace('PLACE', stickAttr() + '_frame' + str(int(gRange.current)))
        loc = cmds.rename(loc, name)
        print loc
        constrainEnabled(loc, sel, mo=True)
    elif len(sel) == 2:
        constrainEnabled(sel[1], sel[0], mo=offset)
    else:
        cmds.warning('      #    Stick to world = Select 1 object.       #    Stick to 2nd selection = Select 2 objects.')

def unStick():
    #needs work
    activeSet = cs.GetSetOptions()
    sel = cmds.ls(sl=True)
    gRange = GetRange()
    cons = getConstraint(sel)
    if activeSet.current:
        #bakeConstrained(activeSet.current, sparseKeys=False, removeConstraint=True, timeLine=False, sim=False)
        cmds.bakeResults( activeSet.current, t=(gRange.selStart,gRange.selEnd), simulation=False, pok=True)
        
    else:
        #bakeConstrainedSelection(sparseKeys=False, removeConstraint=True, timeLine=False, sim=False)
        cmds.bakeResults( sel, t=(gRange.selStart,gRange.selEnd), simulation=False, pok=True)
    #delete associated objects
    blndAttr = getBlendAttr(sel, delete=True)
    cmds.delete(cons)
    plugs = cmds.listConnections(sel[0] + '.message', s=False, d=True, p=True)
    if plugs != None:
        for p in plugs:
            if '.' + stickAttr() in p:
                cmds.delete(p.split('.')[0])

class Key():
    def __init__(self, obj, attr, frame):
        self.obj            = obj
        self.attr           = attr
        self.frame          = frame
        self.value          = None
        self.inTangentType  = None
        self.inWeight       = None
        self.inAngle        = None
        self.outTangentType = None
        self.outWeight      = None
        self.outAngle       = None
        self.lock           = None
        self.get()

    def get(self):
        index = cmds.keyframe(self.obj, q=True, time=(self.frame,self.frame), at=self.attr, indexValue=True)[0]
        self.value = cmds.keyframe(self.obj, q=True, index=(index,index), at=self.attr, valueChange=True)[0]
        self.inAngle = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, inAngle=True)[0]
        self.outAngle = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, outAngle=True)[0]
        self.inTangentType = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, inTangentType=True)[0]
        self.outTangentType = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, outTangentType=True)[0]
        self.inWeight = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, inWeight=True)[0]
        self.outWeight = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, outWeight=True)[0]
        self.lock = cmds.keyTangent( self.obj, q=True, time=(self.frame,self.frame), attribute=self.attr, lock=True)[0]
        
    def put(self):
        cmds.setKeyframe(self.obj, at=self.attr, time=(self.frame, self.frame), value=self.value)
        cmds.keyTangent( self.obj, edit=True, time=(self.frame,self.frame), attribute=self.attr,
        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inWeight=self.inWeight, 
        outWeight=self.outWeight, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock)

class AnimCrv(Key):
    def __init__(self, obj, attr):
        self.obj            = obj
        self.attr           = attr
        self.crv            = cmds.findKeyframe(self.obj, at=self.attr, c=True)
        self.frames         = []
        self.key            = []
        self.value          = cmds.getAttr(self.obj + '.' + self.attr)
        self.qualify()

    def qualify(self):
        if self.crv != None:
            if len(self.crv) == 1:
                self.crv = self.crv[0]
                self.keyedFrames()
                self.keyAttrs()

    def keyedFrames(self):
        if self.crv != None:
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
        if replace == True:
            self.crv = cmds.findKeyframe(self.obj, at=self.attr, c=True)
            if self.crv:
                cmds.delete(self.crv)
        for key in self.key:
            key.obj = self.obj
            key.put()
