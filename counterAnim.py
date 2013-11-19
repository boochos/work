#setup ideal
obj1, obj2 = buildDisObjs()
ideal = measureDis(obj1, obj2)
print ideal
#counter
counterPos(ideal, cmds.ls(sl=True)[1], 0.1)
counterPosRange(907, 946, ac=0.1)


def percentOf(prcnt, of):
    result = prcnt * of * 0.01
    return result

def buildDisObjs():
    sel = cmds.ls(sl=True)[0]
    ref = sel.split(':')[0]
    obj1 = ref + ':DEFORM:SKEL:shoulder_L_JNT'
    obj2 = ref + ':DEFORM:SKEL:arm_L_EFF'
    if '_R_' in sel:
        obj1 = obj1.replace('_L_', '_R_')
        obj2 = obj2.replace('_L_', '_R_')
    return obj1, obj2
    
def measureDis(obj1, obj2):
    p1 = cmds.xform(obj1, q=True, ws=True, t=True )
    p2 = cmds.xform(obj2, q=True, ws=True, t=True )
    v = [0,0,0]
    v[0] = p1[0] - p2[0]
    v[1] = p1[1] - p2[1]
    v[2] = p1[2] - p2[2]
    distance = v[0]*v[0] + v[1]*v[1] + v[2]*v[2]
    from math import sqrt
    distance = sqrt(distance)
    return distance

def counterAdd(ideal, counterObj, ac=0.25):
    limit = 200
    state = cmds.autoKeyframe( q=True, st=True )
    cmds.autoKeyframe( st=False )
    nudge = percentOf(ac, ideal)
    obj1, obj2 = buildDisObjs()
    currentDis = measureDis(obj1, obj2)
    i = 0
    while (currentDis < ideal):
        if i < 200:
            tz = cmds.getAttr(counterObj + '.tz')
            cmds.setAttr(counterObj + '.tz', tz + nudge)
            currentDis = measureDis(obj1, obj2)
        else:
            print '-- limit reached --'
            break
        i=i+1
    cmds.setKeyframe(counterObj, at='tz' )
    cmds.autoKeyframe( st=state )

def counterSub(ideal, counterObj, ac=0.25):
    limit = 200
    state = cmds.autoKeyframe( q=True, st=True )
    cmds.autoKeyframe( st=False )
    nudge = percentOf(ac, ideal) * -1.0
    obj1, obj2 = buildDisObjs()
    currentDis = measureDis(obj1, obj2)
    i = 0
    while (currentDis > ideal):
        if i < limit:
            tz = cmds.getAttr(counterObj + '.tz')
            cmds.setAttr(counterObj + '.tz', tz + nudge)
            currentDis = measureDis(obj1, obj2)
        else:
            print '-- limit reached --'
            break
        i=i+1
    cmds.setKeyframe(counterObj, at='tz' )
    cmds.autoKeyframe( st=state )

def counterPos(ideal, counterObj, ac=0.25):
    obj1, obj2 = buildDisObjs()
    current = measureDis(obj1, obj2)
    if current < ideal:
        counterAdd(ideal, counterObj, ac)
    else:
        counterSub(ideal, counterObj, ac)

def counterPosRange(min, max, ac=0.25):
    print '-- range starting--'
    orig = cmds.currentTime(q=True)
    current = cmds.currentTime(min)
    while (cmds.currentTime(q=True) <= max):
        counterPos(ideal, cmds.ls(sl=True)[1], 0.5)
        counterPos(ideal, cmds.ls(sl=True)[1], ac)
        current = cmds.currentTime(q=True)
        cmds.currentTime(current + 1)
    cmds.currentTime(orig)
    print '-- range done --'
