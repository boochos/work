import maya.cmds as cmds
import maya.mel as mel
#import place_lib as place
#import util_lib as util
#import lists_lib as lists
#reload(lists)

def mocapSkelAnim():
    sel = cmds.ls(sl=True)
    if len(sel) == 2:
        get = sel[0]
        put = sel[1].split(':')[0]
        mocap = 'mocap_'
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
                        #crv = cn.AnimCrv(obj, attr.split('.')[1])
                        #update obj class attr to pasted version
                        if ':' in obj:
                            obj = obj.split(':')[1]
                        crv.obj = put + ':' + obj
                        #paste/buildCurve
                        #crv.build()
    else:
        print 'Select node from copy namespace, select node from paste namespace'

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
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
                pm.renderManip(shapes, cam=[False,False,False,False,False])
                message('Clip planes Off', maya=True)
            else:
                pm.renderManip(shapes, cam=[False,False,False,True,False])
                message('Clip planes On', maya=True)
        else:
            message('Select a camera to toggle Frustum.', maya=True)
    except:
        message('Select a camera to toggle Frustum.', maya=True)

def proceduralVis(objs):
    #preview toggle
    attrs = ['parm_modifiers_p0_camera',
    'parm_modifiers_p0_shadowMaps',
    'parm_modifiers_p0_master']
    if objs:
        shapes = cmds.listRelatives(objs, type='shape', f=True)
        proc = []
        for shape in shapes:
            if 'proceduralShape' in shape:
                proc.append(shape)
        if proc:
            now = cmds.getAttr( proc[0] + '.' + attrs[0])
            if now == True:
                for shape in proc:
                    for attr in attrs:
                        cmds.setAttr( shape + '.' + attr, 0)
                message('Visibility Off' + '--        ' + str(attrs), maya=True)
            else:
                for shape in proc:
                    for attr in attrs:
                        cmds.setAttr( shape + '.' + attr, 1)
                message('Visibility On' + '--        ' + str(attrs), maya=True)
        else:
            message("No 'proceduralShape' found in selection", maya=True)
    else:
        message('Select a layout object(s).  ---  Expect shape attrs:  --  parm_modifiers_p0_camera  --  parm_modifiers_p0_shadowMaps  --  parm_modifiers_p0_master', maya=True)

def proceduralPreview(objs, all=True):
    #preview toggle
    shapes = []
    if all:
        shapes = cmds.ls(type='shape')
    else:
        shapes = cmds.listRelatives(objs, type='shape', f=True)
    proc = []
    for shape in shapes:
        if 'proceduralShape' in shape:
            proc.append(shape)
    if proc:
        now = cmds.getAttr( proc[0] + '.glPreview')
        if now == True:
            for shape in proc:
                cmds.setAttr( shape + '.glPreview', 0)
            message('Preview Off', maya=True)
        else:
            for shape in proc:
                cmds.setAttr( shape + '.glPreview', 1)
            message('Preview On', maya=True)
    else:
        message("No 'proceduralShape' found in scene", maya=True)

def proceduralBox():
    #boundingbox toggle
    scene = cmds.ls(type='shape')
    proc  = []
    for shape in scene:
        if 'proceduralShape' in shape:
            proc.append(shape)
    if proc:
        now = cmds.getAttr( proc[0] + '.drawBound')
        if now:
            for shape in proc:
                cmds.setAttr( shape + '.drawBound', 0)
        else:
            for shape in proc:
                cmds.setAttr( shape + '.drawBound', 1)
    else:
        message("No 'proceduralShape' found in scene", maya=True)

def layoutAnim(offset=1):
    #cache offset
    sel = cmds.ls(sl=True)
    for obj in sel:
        obj = obj.split('.')[0]
        now = cmds.getAttr( obj + '.parm_modifiers_p6_offset')
        cmds.setAttr( obj + '.parm_modifiers_p6_offset', now + offset)

def locSize(lc, X=0.5):
    axis = ['X','Y','Z']
    for axs in axis:
            cmds.setAttr(lc + 'Shape.localScale' + axs, X)

def locator(ro='zxy', size=0.1, constrain=False):
    locs = []
    sel = cmds.ls(sl=True)
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
            r = cmds.xform(item, q=True, ws=True, ro=True )
            t = cmds.xform(item, q=True, ws=True, rp=True )
            cmds.xform(lc, t=t, ro=r)
            cmds.setAttr(lc + '.rotateOrder', roo)
            cmds.xform(lc, roo=ro )
            if constrain == True:
                cmds.parentConstraint(item, lc, mo=True)
        return locs
    else:
        cmds.warning('Select something!')

def getRange():
    min = cmds.playbackOptions(q=True, minTime=True)
    max = cmds.playbackOptions(q=True, maxTime=True)
    current = cmds.currentTime(q=True)
    return min, max, current

class GetRange():
    def __init__(self):
        self.min = cmds.playbackOptions(q=True, minTime=True)
        self.max = cmds.playbackOptions(q=True, maxTime=True)
        self.current = cmds.currentTime(q=True)

def nonKey(obj):
    pos = ['tx','ty','tz']
    rot = ['rx','ry','rz']
    nonKeyT = []
    nonKeyR = []
    for axis in pos:
        if cmds.getAttr(obj + '.' + axis, k=True) == False:
            at = axis.split('t')[1]
            nonKeyT.append(at)
    for axis in rot:
        if cmds.getAttr(obj + '.' + axis, k=True) == False:
            at = axis.split('r')[1]
            nonKeyR.append(at)
    return nonKeyT, nonKeyR

def changeRO(obj, ro):
    '''
    '''
    r = getRange()
    autoK = cmds.autoKeyframe(q=True, state=True)
    cmds.autoKeyframe(state=False)
    min =r[0]
    max =r[1]
    current = r[2]
    i = min
    origRO = cmds.getAttr(obj + '.rotateOrder')
    cmds.currentTime(i)
    cmds.currentTime(cmds.findKeyframe(which='previous'))
    cmds.xform(obj, roo=ro)
    keyframes = keyedFrames(obj)
    for key in keyframes:
        cmds.currentTime(key)
        cmds.setAttr(obj + '.rotateOrder', origRO)
        cmds.xform(obj, roo=ro)
        cmds.setKeyframe(obj + '.rotate')
    '''
    while (cmds.currentTime(q=True) != cmds.findKeyframe(which='next')):
        #may be problematic if autokeyframe is off
        next = cmds.currentTime(cmds.findKeyframe(which='next'))
        cmds.setAttr(obj + '.rotateOrder', origRO)
        cmds.xform(obj, roo=ro)
        if cmds.currentTime(q=True) > max:
            break
    '''
    cmds.currentTime(current)
    cmds.autoKeyframe(state=autoK)

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

def changeRoMulti(ro='zxy'):
	#changes rotate order of an object to the desired order without changing the pose. tangent will bust.
	#will use current frame range
	#assumes you have/want a key on every frame
    sel = cmds.ls(sl=True)
    for item in sel:
        changeRO(item, ro=ro)

def keyHi(v=0):
    cmds.select(hierarchy=True)
    h = cmds.ls(sl=True)
    print h
    for item in h:
        cmds.setKeyframe( item, attribute='visibility', v=v )
    
def matchObj():
    #queries dont work correctly when constraints, pairBlends and characterSets get involved
    #objs
    sel = cmds.ls(sl=True)
    if len(sel) == 2:
        #collect get
        get = sel[1]
        roo = cmds.getAttr(get + '.rotateOrder')
        r = cmds.xform(get, q=True, ws=True, ro=True )
        t = cmds.xform(get, q=True, ws=True, t=True )
        #collect put
        put = sel[0]
        origRO = cmds.xform(put, q=True, roo=True)
        try:
            #put
            cmds.setAttr(put + '.rotateOrder', roo)
            cmds.xform(put, ws=True, t=t)
            cmds.xform(put, ws=True, ro=r)
            cmds.xform(put, roo=origRO)
        except:
            #intermediate object
            loc = cmds.spaceLocator(name='getSpace_deleteMe')[0]
            cmds.setAttr(loc + '.rotateOrder', roo)
            cmds.xform(loc, ws=True, t=t)
            cmds.xform(loc, ws=True, ro=r)
            cmds.xform(put, roo=origRO)
            #collect get
            r = cmds.xform(loc, q=True, ws=True, ro=True )
            t = cmds.xform(loc, q=True, ws=True, t=True )
            #put
            cmds.xform(put, ws=True, t=t)
            cmds.xform(put, ws=True, ro=r)
            #delete
            cmds.delete(loc)
    else:
        message('Select 2 objects.')

def selectFngrs(R=False):
    sel = cmds.ls(sl=True)
    ref = sel[0].split(':')[0]
    cmds.select(clear=True)
    for item in lists.fingers:
        if R == True:
            item = item.replace('l_', 'r_')
        print item
        cmds.select(ref + ':' + item, add=True)

def shapeSize(obj=None, mltp=1):
    '''\n
    mltp = size multiplier of shape nodes
    '''
    if obj == None:
	#make a list from selection
	obj = cmds.ls(sl=True, l=True)
    elif type(obj) == list:
	#no need to accomodate
    	pass
    else:
    	#obj must be a single item, make a list
    	obj = [obj]
        #run the loop on list
        for item in obj:
        	shape = cmds.listRelatives(item, s=True, f=True)
        	if shape != None:
        	    for node in shape:
            		if 'SharedAttr' not in node:
            		    cmds.scale( mltp, mltp, mltp, node + '.cv[*]')

def scaleCrv(val):
    '''
    -Scale selected Graph Editor curves with given value.
    -Pivot derived from selection - get selected keys of curves, if values are the same, the assumption is made to pivot from that position, otherwise pivot defaults to 0.
    '''
    #get curves of selected keys
    crvs = cmds.keyframe(q=True, name=True, sl=True)
    pvt = 0
    if len(crvs) == 1:
        #keys selected from one curve
        selKey_1 = cmds.keyframe(crvs, q=True, vc=True, sl=True)
        selKey_2 = list(set(cmds.keyframe(crvs, q=True, vc=True, sl=True)))
        if len(selKey_1) != len(selKey_2):
            #multiple keys selected, same value, pivot = 0
            cmds.scaleKey(crvs, vs=val, vp=pvt)
        elif len(selKey_1) == 1:
            #single key selected, pivot = selKey
            pvt = selKey_1[0]
            cmds.scaleKey(crvs, vs=val, vp=pvt)
        else:
            #multiple keys selected, pivot = 0
            cmds.scaleKey(crvs, vs=val, vp=pvt)
    else:
        #keys selected from multiple curves
        selKey = list(set(cmds.keyframe(crvs, q=True, vc=True, sl=True)))
        if len(selKey) == 1:
            #multiple keys have same value, pivot = selKey
            pvt = selKey[0]
        cmds.scaleKey(crvs, vs=val, vp=pvt)

def holdCrv(postCurrent=True, preCurrent=True):
    crvs = cmds.keyframe(q=True, name=True, sl=True)
    if crvs != None:
        current = getRange()[2]
        for crv in crvs:
            frames = cmds.keyframe(crv, q=True, tc=True)
            val = cmds.keyframe(crv, q=True, eval=True, t=(current,current))[0]
            for frame in frames:
                if postCurrent == True:
                    if frame >= current:
                        cmds.keyframe(crv, vc=val, t=(frame,frame))
                        cmds.keyTangent( crv, inTangentType='auto', outTangentType='auto', time=(frame,frame) )
                if preCurrent == True:
                    if frame <= current:
                        cmds.keyframe(crv, vc=val, t=(frame,frame))
                        cmds.keyTangent( crv, inTangentType='auto', outTangentType='auto', time=(frame,frame) )
    else:
        print '-- Select a curve --'

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