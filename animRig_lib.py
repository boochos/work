import maya.cmds as cmds
import maya.mel as mel
#
import webrImport as web
# web
cs = web.mod('characterSet_lib')
cn = web.mod('constraint_lib')
ds = web.mod('display_lib')
ac = web.mod('animCurve_lib')


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def matchCharSet(source=None, objs=[]):
    '''
    source = get character set if connected
    objs = make members of list in same set as source
    '''
    char = cmds.listConnections(source, t='character', s=False, d=True)
    if char:
        char = list(set(char))
        if len(char) == 1:
            for obj in objs:
                cmds.character(obj, include=char[0])
        else:
            message('Object not added to Charecter set. More than one option found.')


def fingerRig(name='', obj=[], size=1.0, aim=[1, 0, 0], u=[0, 1, 0], mlt=1.0, baseWorld=False):
    '''
    obj[0] = tip control
    obj[1] = mid control
    obj[2] = base control
    obj[3] = hand
    '''
    offset = ds.measureDis(obj1=obj[0], obj2=obj[1])
    # print offset

    # base
    master = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__MASTER__')[0]
    cmds.parentConstraint(obj[3], master, mo=1)

    # base
    base = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__BASE__')[0]
    if not baseWorld:
        cmds.parent(base, master)
    # cmds.parentConstraint(obj[2], base, mo=1)
    cn.bakeConstrained(base, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[2], B=base, subtractive=True)

    # base up
    baseUp = cn.locator(obj=obj[2], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__BASEUP__')[0]
    cmds.setAttr(baseUp + '.visibility', 0)
    cmds.parent(baseUp, base)
    cmds.setAttr(baseUp + '.ty', offset * mlt)
    cmds.parent(baseUp, master)
    cmds.parentConstraint(obj[2], baseUp, mo=1)
    cn.bakeConstrained(baseUp, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[2], B=baseUp, subtractive=True)

    # mid base
    mid = cn.locator(obj=obj[1], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__MID__')[0]
    cmds.parent(mid, master)
    # cmds.parentConstraint(obj[1], mid, mo=1)
    cn.bakeConstrained(mid, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[1], B=mid, subtractive=True)

    # mid up
    midUp = cn.locator(obj=obj[1], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__MIDUP__')[0]
    cmds.setAttr(midUp + '.visibility', 0)
    cmds.parent(midUp, mid)
    cmds.setAttr(midUp + '.ty', offset * mlt)
    # cmds.parent(midUp, mid)
    cmds.parentConstraint(obj[1], midUp, mo=1)
    cn.bakeConstrained(midUp, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[1], B=midUp, subtractive=True)

    # tip base, tip target, tip up
    # 1 loc (tip base)
    tip = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=True, toSelection=True, suffix='__TIP__')[0]
    # cmds.parentConstraint(obj[0], tip, mo=1)

    # 2 loc (tip target)
    tipTarget = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__TARGET__')[0]
    cmds.parent(tipTarget, tip)
    cmds.setAttr(tipTarget + '.tx', offset)
    cmds.parent(tipTarget, w=1)
    cmds.parentConstraint(tip, tipTarget, mo=1)
    cn.bakeConstrained(tipTarget, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[0], B=tipTarget, subtractive=True)

    # 3 loc (tip up)
    tipUp = cn.locator(obj=obj[0], ro='zxy', X=size, constrain=False, toSelection=True, suffix='__TIPUP__')[0]
    cmds.setAttr(tipUp + '.visibility', 0)
    cmds.parent(tipUp, tipTarget)
    cmds.setAttr(tipUp + '.ty', offset * mlt)
    cmds.parentConstraint(tip, tipUp, mo=1)
    cn.bakeConstrained(tipUp, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[0], B=tipUp, subtractive=True)

    # loc 1 (tip base)
    cmds.parent(tip, tipTarget)
    cn.bakeConstrained(tip, removeConstraint=True, timeLine=False, sim=True)
    cn.matchKeyedFrames(A=obj[0], B=tip, subtractive=True)

    # aim constraints
    cmds.aimConstraint(mid, obj[2], wut='object', wuo=baseUp, aim=aim, u=u, mo=1)  # base @ mid
    cmds.aimConstraint(tip, obj[1], wut='object', wuo=midUp, aim=aim, u=u, mo=1)  # mid @ tip
    cmds.aimConstraint(tipTarget, obj[0], wut='object', wuo=tipUp, aim=aim, u=u, mo=1)  # mid @ tip

    # group
    gr = cmds.group(tipTarget, master, n='__' + name + '__')

    return gr


def nameSpace(ns='', base=False):
    if ':' in ns:
        i = ns.rfind(':')
        ref = ns[:i]
        obj = ns[i + 1:]
        if not base:
            return ref
        else:
            return ref, obj
    else:
        return ns


def switchLHand():
    ns = nameSpace(ns=cmds.ls(sl=1)[0])
    mlt = 3.0
    thumb = [ns + ':' + 'l_handThumb2_CTRL',
             ns + ':' + 'l_handThumb1_CTRL',
             ns + ':' + 'l_handThumb_CTRL',
             ns + ':' + 'l_handThumbBase_CTRL']
    th = fingerRig(name='Lthumb', obj=thumb, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    index = [ns + ':' + 'l_handFingerA2Fk_CTRL',
             ns + ':' + 'l_handFingerA1Fk_CTRL',
             ns + ':' + 'l_handFingerA0Fk_CTRL',
             ns + ':' + 'l_handIk_CTRL']
    ind = fingerRig(name='Lindex', obj=index, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    middle = [ns + ':' + 'l_handFingerB2Fk_CTRL',
              ns + ':' + 'l_handFingerB1Fk_CTRL',
              ns + ':' + 'l_handFingerB0Fk_CTRL',
              ns + ':' + 'l_handIk_CTRL']
    mid = fingerRig(name='Lmiddle', obj=middle, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    ring = [ns + ':' + 'l_handFingerC2Fk_CTRL',
            ns + ':' + 'l_handFingerC1Fk_CTRL',
            ns + ':' + 'l_handFingerC0Fk_CTRL',
            ns + ':' + 'l_handIk_CTRL']
    rin = fingerRig(name='Lring', obj=ring, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    pinky = [ns + ':' + 'l_handFingerD2Fk_CTRL',
             ns + ':' + 'l_handFingerD1Fk_CTRL',
             ns + ':' + 'l_handFingerD0Fk_CTRL',
             ns + ':' + 'l_handIk_CTRL']
    pin = fingerRig(name='Lpinky', obj=pinky, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    # group
    cmds.group(th, ind, mid, rin, pin, n='__LEFT_HAND__')


def switchRHand():
    ns = nameSpace(ns=cmds.ls(sl=1)[0])
    mlt = 3.0
    thumb = [ns + ':' + 'r_handThumb2_CTRL',
             ns + ':' + 'r_handThumb1_CTRL',
             ns + ':' + 'r_handThumb_CTRL',
             ns + ':' + 'r_handThumbBase_CTRL']
    th = fingerRig(name='Rthumb', obj=thumb, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    index = [ns + ':' + 'r_handFingerA2Fk_CTRL',
             ns + ':' + 'r_handFingerA1Fk_CTRL',
             ns + ':' + 'r_handFingerA0Fk_CTRL',
             ns + ':' + 'r_handIk_CTRL']
    ind = fingerRig(name='Rindex', obj=index, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    middle = [ns + ':' + 'r_handFingerB2Fk_CTRL',
              ns + ':' + 'r_handFingerB1Fk_CTRL',
              ns + ':' + 'r_handFingerB0Fk_CTRL',
              ns + ':' + 'r_handIk_CTRL']
    mid = fingerRig(name='Rmiddle', obj=middle, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    ring = [ns + ':' + 'r_handFingerC2Fk_CTRL',
            ns + ':' + 'r_handFingerC1Fk_CTRL',
            ns + ':' + 'r_handFingerC0Fk_CTRL',
            ns + ':' + 'r_handIk_CTRL']
    rin = fingerRig(name='Rring', obj=ring, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    pinky = [ns + ':' + 'r_handFingerD2Fk_CTRL',
             ns + ':' + 'r_handFingerD1Fk_CTRL',
             ns + ':' + 'r_handFingerD0Fk_CTRL',
             ns + ':' + 'r_handIk_CTRL']
    pin = fingerRig(name='Rpinky', obj=pinky, size=0.2, aim=[1, 0, 0], u=[0, 1, 0], mlt=mlt)

    # group
    cmds.group(th, ind, mid, rin, pin, n='__RIGHT_HAND__')


def aimRig(target=None, obj=None, size=0.3, aim=[1, 0, 0], u=[0, 1, 0], tipOffset=1.0, mo=False, bake=True):
    # BUG: does not support negative numbers for aim vectors, use for offset direction
    locs = []
    if not target:
        sel = cmds.ls(sl=1)  # order = tip,base
        if len(sel) == 2:
            target = sel[0]
            obj = sel[1]
        else:
            cmds.warning('-- function requires 2 objects to be selected or fed as variables --')
            return None
    if target is not None and obj is not None:
        # sort axis
        aAxs = ['.tx', '.ty', '.tz']
        aAxs = aAxs[aim.index(1.0)]
        uAxs = ['.tx', '.ty', '.tz']
        uAxs = uAxs[u.index(1.0)]
        # distance
        offset = ds.measureDis(obj1=target, obj2=obj)
        # place locator at locale A and constrain
        locA = cn.locator(obj=target, ro='zxy', constrain=True, toSelection=True, X=size * 0.1, color=28, suffix='__AIM__')[0]
        locs.append(locA)
        # match keys
        cn.matchKeyedFrames(A=target, B=locA, subtractive=True)
        # bake locator A
        cn.bakeConstrained(locA, removeConstraint=True, timeLine=False, sim=False)
        # bake locator on location B
        locB = cn.controllerToLocator(obj, p=False, r=True, timeLine=False, sim=False, size=0.1, suffix='__BASE__')[0]
        locs.append(locB)
        # place up locator on location B
        locUp = cn.locator(obj=obj, ro='zxy', constrain=False, toSelection=False, X=size * 0.5, color=29, suffix='__UP__')[0]
        locs.append(locUp)
        # print locUp
        # parent up locator, move up in ty, unparent
        cmds.parent(locUp, locB)
        cmds.setAttr(locUp + uAxs, offset)
        # constraint up locator to locator B
        cmds.parentConstraint(obj, locUp, mo=1)
        # parent locUp to locator A, bake up locator
        cmds.parent(locUp, locA)
        cn.matchKeyedFrames(A=target, B=locUp, subtractive=True)
        cn.bakeConstrained(locUp, removeConstraint=True, timeLine=False, sim=False)
        # aim offset
        locAim = cn.locator(obj=obj, ro='zxy', constrain=False, toSelection=False, X=size * 1, color=15, suffix='__OFFSET__')[0]
        locs.append(locAim)
        cmds.parent(locAim, locB)
        cmds.setAttr(locAim + aAxs, offset)
        cmds.parent(locAim, locA)
        cmds.parentConstraint(obj, locAim, mo=1)
        cn.matchKeyedFrames(A=target, B=locAim, subtractive=True)
        cn.bakeConstrained(locAim, removeConstraint=True, timeLine=False, sim=False)
        # delete helper
        con = cn.getConstraint(obj, nonKeyedRoute=True, keyedRoute=True, plugRoute=True)
        cmds.delete(con, locB)
        locs.remove(locB)
        # aim constrain Locator A to B, using up locator as up vector
        cmds.aimConstraint(locAim, obj, wut='object', wuo=locUp, aim=aim, u=u, mo=mo)
        # bake
        if not bake:
            for loc in locs:
                attrs = ['rotateX', 'rotateY', 'rotateZ', 'translateX', 'translateY', 'translateZ']
                ac.deleteAnim(loc, attrs=attrs)
        else:
            print bake
        # cleanup
        cmds.group(locA, n='__AIMRIG__#')
        matchCharSet(obj, locs)
        cmds.select(locAim)

        message('Aim rig built', maya=True)
        return locs
    else:
        cmds.warning('-- function requires 2 objects to be selected or fed as variables --')
        return None


def aimPivotRig(size=0.3, aim=(0.0, 0.0, 1.0), u=(0.0, 1.0, 0.0), offset=20.0, masterControl=False, masterPosition=0):
    '''
    master control: moves entire constraint rig
    master position options:
    0 = core
    1 = root
    2 = aim
    3 = up
    '''
    # store selection
    sel = cmds.ls(sl=True)
    selectedMaster = None
    if sel:
        if len(sel) == 2:
            selectedMaster = sel[1]
            sel = sel[0]
        else:
            sel = sel[0]
        # sort axis
        aAxs = ['.tx', '.ty', '.tz']
        aAxs = aAxs[aim.index(1.0)]
        uAxs = ['.tx', '.ty', '.tz']
        uAxs = uAxs[u.index(1.0)]
        # place locators on selection
        locs = []
        coreL = cn.locator(obj=sel, constrain=False, X=5, color=15, suffix='__CORE__')[0]
        locs.append(coreL)
        rootL = cn.locator(obj=sel, constrain=False, X=2, color=15, suffix='__ROOT__')[0]
        locs.append(rootL)
        aimL = cn.locator(obj=sel, constrain=False, X=5, color=28, suffix='__AIM__')[0]
        locs.append(aimL)
        upL = cn.locator(obj=sel, constrain=False, X=5, color=29, suffix='__UP__')[0]
        locs.append(upL)
        upG = cn.null(obj=sel, suffix='__UP_GRP')
        # heirarchy, prep for offsets
        cmds.parent(rootL, coreL)
        cmds.parent(aimL, coreL)
        cmds.parent(upG, coreL)
        cmds.parent(upL, upG)
        # offsets
        cmds.setAttr(aimL + aAxs, offset)
        cmds.setAttr(rootL + aAxs, offset * -1)
        cmds.setAttr(upG + uAxs, abs(offset))
        # constraints, prep for basking
        cmds.parentConstraint(sel, aimL, mo=True, sr=('x', 'y', 'z'))
        cmds.parentConstraint(sel, upL, mo=True, sr=('x', 'y', 'z'))
        cmds.parentConstraint(sel, rootL, mo=True, sr=('x', 'y', 'z'))
        coreCn = cmds.parentConstraint(sel, coreL, mo=True)
        cmds.pointConstraint(rootL, upG, mo=True)
        cmds.pointConstraint(aimL, upG, mo=True)
        # check if 2nd object was selected
        if selectedMaster:
            masterGrp = cn.null(obj=selectedMaster, suffix='temp')
            masterGrp = cmds.rename(masterGrp, '__PIVOTAIM_RIG__#')
            cmds.parentConstraint(selectedMaster, masterGrp, mo=False)
            cmds.parent(coreL, masterGrp)
            ac.deleteAnim(masterGrp, attrs=['scaleX', 'scaleY', 'scaleZ'], lock=True, keyable=False)
            ac.deleteAnim(masterGrp, attrs=['visibility'], lock=False, keyable=False)
        else:
            masterGrp = cmds.group(coreL, n='__PIVOTAIM_RIG__#')
        # add master control if necessary
        if masterControl:
            if masterPosition == 0:
                masterL = cn.locator(obj=coreL, constrain=False, X=5, color=15, suffix='__MASTER__')[0]
                cmds.parentConstraint(coreL, masterL, mo=True, sr=('x', 'y', 'z'))
            if masterPosition == 1:
                masterL = cn.locator(obj=rootL, constrain=False, X=5, color=15, suffix='__MASTER__')[0]
                cmds.parentConstraint(rootL, masterL, mo=True, sr=('x', 'y', 'z'))
            if masterPosition == 2:
                masterL = cn.locator(obj=aimL, constrain=False, X=5, color=15, suffix='__MASTER__')[0]
                cmds.parentConstraint(aimL, masterL, mo=True, sr=('x', 'y', 'z'))
            if masterPosition == 3:
                masterL = cn.locator(obj=upL, constrain=False, X=5, color=15, suffix='__MASTER__')[0]
                cmds.parentConstraint(upL, masterL, mo=True, sr=('x', 'y', 'z'))
            # bake master
            cmds.parent(masterL, masterGrp)
            cn.matchKeyedFrames(A=sel, B=masterL, subtractive=True)
            cmds.setAttr(masterL + '.rotate', 0, 0, 0)
            ac.deleteAnim(masterL, attrs=['rotateX', 'rotateY', 'rotateZ'], lock=True)
            cn.bakeConstrained(masterL, removeConstraint=True, timeLine=False, sim=False)
            # adjust hierachy
            cmds.parent(rootL, masterL)
            cmds.parent(aimL, masterL)
            cmds.parent(coreL, masterL)
            cmds.parent(upG, masterL)
            # return None
        else:
            cmds.parent(rootL, masterGrp)
            cmds.parent(aimL, masterGrp)
            cmds.parent(upG, masterGrp)
        # return None
        # core needs to be under root for the aim constraint
        cmds.parent(coreL, rootL)
        # bake the rest, manage attrs
        cn.matchKeyedFrames(A=sel, B=aimL, subtractive=True)
        ac.deleteAnim(aimL, attrs=['rotateX', 'rotateY', 'rotateZ'], lock=True)
        cn.bakeConstrained(aimL, removeConstraint=True, timeLine=False, sim=False)
        cn.matchKeyedFrames(A=sel, B=upL, subtractive=True)
        ac.deleteAnim(upL, attrs=['rotateX', 'rotateY', 'rotateZ'], lock=True)
        cn.bakeConstrained(upL, removeConstraint=True, timeLine=False, sim=False)
        cn.matchKeyedFrames(A=sel, B=rootL, subtractive=True)
        ac.deleteAnim(upL, attrs=['rotateX', 'rotateY', 'rotateZ'], lock=True)
        cn.bakeConstrained(rootL, removeConstraint=True, timeLine=False, sim=False)
        # aim constraint
        cmds.aimConstraint(aimL, rootL, wut='object', wuo=upL, aim=aim, u=u, mo=False)
        ac.deleteAnim(rootL, attrs=['rotateX', 'rotateY', 'rotateZ'], lock=True)
        # constrain selected object
        cmds.delete(coreCn)
        cmds.parentConstraint(coreL, sel, mo=True)
        # final constraints
        cmds.pointConstraint(rootL, coreL, mo=True)
        cmds.pointConstraint(aimL, coreL, mo=True)
        ac.deleteAnim(coreL, attrs=['translateX', 'translateY', 'translateZ'], lock=True)
        cn.matchKeyedFrames(A=sel, B=coreL, subtractive=True)
        # match char Set
        matchCharSet(sel, locs)
        # done
    else:
        message('select an object')


def parentRig(bake=True, *args):
    '''
    sometimes adds 2 pairblends, needs to be fixed as it breaks active char set key ticks.
    '''
    # store selection
    sel = cmds.ls(sl=True)
    if len(sel) == 2:
        # place 3 locators on selection
        offset = cn.locator(obj=sel[0], constrain=False, X=1, color=15, suffix='__OFFSET__')[0]
        root = cn.locator(obj=sel[1], constrain=False, X=0.1, color=28, suffix='__ROOT__')[0]
        spin = cn.locator(obj=sel[1], constrain=False, X=0.5, color=29, suffix='__SPIN__')[0]
        # heirarchy
        cmds.parent(offset, spin)
        cmds.parent(spin, root)
        cmds.parentConstraint(sel[1], root, mo=True)
        # bake anim to offset loc
        cmds.parentConstraint(sel[0], offset, mo=True)
        cn.matchKeyedFrames(A=sel[0], B=offset, subtractive=True)
        if bake:
            cn.bakeConstrained(offset, removeConstraint=True, timeLine=False, sim=False)
        else:
            con = cn.getConstraint(offset)
            if con:
                cmds.delete(con)
        # create final rig constraints
        cn.constrainEnabled(offset, sel[0], mo=True)
        # cn.locSize(root, X=0.1)
        cmds.select(offset)
        # group
        cmds.group(root, n='__PARENTRIG__#')
        # match char set
        matchCharSet(sel[0], [offset])
        # select new control
        cmds.select(offset)
        message('Parent rig built. -- New control Selected ', maya=True)
    else:
        cmds.warning('-- Select 2 objects --')
