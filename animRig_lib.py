import maya.cmds as cmds
import maya.mel as mel
import characterSet_lib as cs
import constraint_lib as cn
import display_lib as ds
reload(ds)
reload(cn)


def fingerRig(name='', obj=[], size=1.0, aim=[1,0,0], u=[0,1,0], mlt=1.0, baseWorld=False):
    '''
    obj[0] = tip control
    obj[1] = mid control
    obj[2] = base control
    obj[3] = hand
    '''
    offset = ds.measureDis(obj1=obj[0], obj2=obj[1])
    #print offset

    #base
    master = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__MASTER__')[0]
    cmds.parentConstraint(obj[3], master, mo=1)

    #base
    base = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__BASE__')[0]
    if not baseWorld:
        cmds.parent(base, master)
    #cmds.parentConstraint(obj[2], base, mo=1)
    cn.bakeConstrained(base, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[2], BBB=base, subtractive=True)

    #base up
    baseUp = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__BASEUP__')[0]
    cmds.setAttr(baseUp + '.visibility', 0)
    cmds.parent(baseUp, base)
    cmds.setAttr(baseUp + '.ty', offset*mlt)
    cmds.parent(baseUp, master)
    cmds.parentConstraint(obj[2], baseUp, mo=1)
    cn.bakeConstrained(baseUp, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[2], BBB=baseUp, subtractive=True)

    #mid base
    mid = cn.locator(obj=obj[1], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__MID__')[0]
    cmds.parent(mid, master)
    #cmds.parentConstraint(obj[1], mid, mo=1)
    cn.bakeConstrained(mid, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[1], BBB=mid, subtractive=True)

    #mid up
    midUp = cn.locator(obj=obj[1], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__MIDUP__')[0]
    cmds.setAttr(midUp + '.visibility', 0)
    cmds.parent(midUp, mid)
    cmds.setAttr(midUp + '.ty', offset*mlt)
    #cmds.parent(midUp, mid)
    cmds.parentConstraint(obj[1], midUp, mo=1)
    cn.bakeConstrained(midUp, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[1], BBB=midUp, subtractive=True)

    #tip base, tip target, tip up
    #1 loc (tip base)
    tip = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__TIP__')[0]
    #cmds.parentConstraint(obj[0], tip, mo=1)

    #2 loc (tip target)
    tipTarget = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__TARGET__')[0]
    cmds.parent(tipTarget, tip)
    cmds.setAttr(tipTarget + '.tx', offset )
    cmds.parent(tipTarget, w=1)
    cmds.parentConstraint(tip, tipTarget, mo=1)
    cn.bakeConstrained(tipTarget, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[0], BBB=tipTarget, subtractive=True)

    #3 loc (tip up)
    tipUp = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__TIPUP__')[0]
    cmds.setAttr(tipUp + '.visibility', 0)
    cmds.parent(tipUp, tipTarget)
    cmds.setAttr(tipUp + '.ty', offset*mlt)
    cmds.parentConstraint(tip, tipUp, mo=1)
    cn.bakeConstrained(tipUp, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[0], BBB=tipUp, subtractive=True)

    #loc 1 (tip base)
    cmds.parent(tip, tipTarget)
    cn.bakeConstrained(tip, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(AAA=obj[0], BBB=tip, subtractive=True)

    #aim constraints
    cmds.aimConstraint(mid, obj[2], wut='object', wuo=baseUp, aim=aim, u=u, mo=1) #base @ mid
    cmds.aimConstraint(tip, obj[1], wut='object', wuo=midUp, aim=aim, u=u, mo=1) #mid @ tip
    cmds.aimConstraint(tipTarget, obj[0], wut='object', wuo=tipUp, aim=aim, u=u, mo=1) #mid @ tip

    #group
    gr = cmds.group( tipTarget, master, n='__' + name + '__' )

    return gr

def switchLHand(*args):
    mlt = 3.0
    thumb = [
    'l_handThumb2_CTRL',
    'l_handThumb1_CTRL',
    'l_handThumb_CTRL',
    'l_handThumbBase_CTRL'
    ]
    th = fingerRig(name='Lthumb', obj=thumb, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    index = [
    'l_handFingerA2Fk_CTRL',
    'l_handFingerA1Fk_CTRL',
    'l_handFingerA0Fk_CTRL',
    'l_handIk_CTRL'
    ]
    ind = fingerRig(name='Lindex', obj=index, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    middle = [
    'l_handFingerB2Fk_CTRL',
    'l_handFingerB1Fk_CTRL',
    'l_handFingerB0Fk_CTRL',
    'l_handIk_CTRL'
    ]
    mid = fingerRig(name='Lmiddle', obj=middle, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    ring = [
    'l_handFingerC2Fk_CTRL',
    'l_handFingerC1Fk_CTRL',
    'l_handFingerC0Fk_CTRL',
    'l_handIk_CTRL'
    ]
    rin = fingerRig(name='Lring', obj=ring, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    pinky = [
    'l_handFingerD2Fk_CTRL',
    'l_handFingerD1Fk_CTRL',
    'l_handFingerD0Fk_CTRL',
    'l_handIk_CTRL'
    ]
    pin = fingerRig(name='Lpinky', obj=pinky, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    #group
    cmds.group( th, ind, mid, rin, pin, n='__LEFT_HAND__' )

def switchRHand(*args):
    mlt = 3.0
    thumb = [
    'r_handThumb2_CTRL',
    'r_handThumb1_CTRL',
    'r_handThumb_CTRL',
    'r_handThumbBase_CTRL'
    ]
    th = fingerRig(name='Rthumb', obj=thumb, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    index = [
    'r_handFingerA2Fk_CTRL',
    'r_handFingerA1Fk_CTRL',
    'r_handFingerA0Fk_CTRL',
    'r_handIk_CTRL'
    ]
    ind = fingerRig(name='Rindex', obj=index, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    middle = [
    'r_handFingerB2Fk_CTRL',
    'r_handFingerB1Fk_CTRL',
    'r_handFingerB0Fk_CTRL',
    'r_handIk_CTRL'
    ]
    mid = fingerRig(name='Rmiddle', obj=middle, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    ring = [
    'r_handFingerC2Fk_CTRL',
    'r_handFingerC1Fk_CTRL',
    'r_handFingerC0Fk_CTRL',
    'r_handIk_CTRL'
    ]
    rin = fingerRig(name='Rring', obj=ring, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    pinky = [
    'r_handFingerD2Fk_CTRL',
    'r_handFingerD1Fk_CTRL',
    'r_handFingerD0Fk_CTRL',
    'r_handIk_CTRL'
    ]
    pin = fingerRig(name='Rpinky', obj=pinky, size=0.2, aim=[1,0,0], u=[0,1,0], mlt=mlt)

    #group
    cmds.group( th, ind, mid, rin, pin, n='__RIGHT_HAND__' )

def aimRig(objAim='', objBase='', size=0.3, aim=[1,0,0], u=[0,1,0], tipOffset=1.0):
    locs = []
    if objAim == '':
        sel = cmds.ls(sl=1)#order = tip,base
        objAim = sel[0]
        objUp  = sel[1]
    #place locator at locale A and constrain
    locA = locator(obj=objAim, ro='zxy', X=size, constrain=True, toSelection=True)[0]
    locA = cmds.rename(locA, locA.replace('PLACE', 'AIM'))
    locs.append(locA)
    #print locA
    #bake locator A
    bakeConstrained(locA, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    #match keys
    matchKeyedFrames(AAA=objAim, BBB=locA, subtractive=True)
    #bake locator on location B
    locB = controllerToLocator(objBase, p=False, r=True, sparseKeys=True, timeLine=False, sim=True, size=0.1)[0]
    locB = cmds.rename(locB, locB.replace('BAKE', 'BASE'))
    locs.append(locB)
    #print locB
    #place up locator on location B
    locUp = locator(obj=objBase, ro='zxy', X=size, constrain=False, toSelection=False)[0]
    locUp = cmds.rename(locUp, locUp.replace('PLACE', 'UP'))
    #locs.append(locUp)
    #print locUp
    #parent up locator, move up in ty, unparent
    cmds.parent(locUp, locB)
    cmds.setAttr(locUp + '.ty', 5)
    cmds.parent(locUp, w=1)
    #constraint up locator to locator B
    cmds.parentConstraint(objBase, locUp, mo=1)
    #parent locUp to locator A, bake up locator
    cmds.parent(locUp, locA)
    bakeConstrained(locUp, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    matchKeyedFrames(AAA=objAim, BBB=locUp, subtractive=True)
    #aim constrain Locator A to B, using up locator as up vector
    cmds.aimConstraint(locA, locB, wut='object', wuo=locUp, aim=aim, u=u, mo=1)
    return locs

def parentRig(bake=False):
    #store selection
    sel = cmds.ls(sl=True)
    #place 3 locators on selection
    loc1 = locator(obj=sel[0], constrain=False, X=1) #add option to bake with matching keys
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
    bakeConstrained(offset, sparseKeys=True, removeConstraint=True, timeLine=False, sim=True)
    #create final rig constraints
    constrainEnabled(offset, sel[0], mo=True)
    #cmds.parentConstraint(offset, sel[0], mo=True)
    locSize(root, X=0.1)
    cmds.select(offset)
