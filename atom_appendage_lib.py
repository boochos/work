import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from pymel.core import *
import atom_miscellaneous_lib as misc
import atom_joint_lib as joint
import atom_ui_lib as ui
import atom_placement_lib as place


def extractSebastionsControlSubgroup(obj):
    children = cmds.listRelatives(obj, c=True)
    subgrp = None
    for child in children:
        if cmds.nodeType(child) == 'transform':
            subChildren = cmds.listRelatives(child, c=True)
            for subChild in subChildren:
                if cmds.nodeType(subChild) == 'transform':
                    subgrp = subChild

    return subgrp


def createVerticalScapRig(shoulder, shoulder_dbl, shoulder_grp, scapula, control, spine, suffix, setChannels=False):
    '''
    Vertical is refering to the position of the parent of the scap, usually a neck or chest joint in this case
    the neck has the following orientation"
    z(up)
    |
    x--y(-1 aim)
    '''

    pointDis = misc.distance2Pts(cmds.xform(shoulder, query=True, ws=True, rp=True),
                                 cmds.xform(scapula, query=True, ws=True, rp=True))

    scap_aimGrp = cmds.group(name='scapula_aimGrp' + suffix, em=True)
    scap_aimLoc = cmds.spaceLocator(n='scapula_aimLoc' + suffix)[0]
    cmds.parent(scap_aimLoc, scap_aimGrp)
    cmds.setAttr(scap_aimGrp + '.visibility', 0)

    scap_jnt_pos = cmds.xform(scapula, query=True, ws=True, rp=True)
    # position of aim vector is at shoulder, not forward of scapula joint, as it was prior to this line:
    shoulder_pos = cmds.xform(shoulder_dbl, query=True, ws=True, rp=True)
    #shoulder_pos = cmds.xform(shoulder_grp,query=True, ws=True, rp=True)
    cmds.xform(scap_aimGrp, ws=True, t=[shoulder_pos[0], shoulder_pos[1], shoulder_pos[2]])

    scap_upGrp = cmds.group(name='scapula_upGrp' + suffix, em=True)
    scap_upLoc = cmds.spaceLocator(n='scapula_upLoc' + suffix)[0]
    cmds.setAttr(scap_upLoc + '.visibility', 0)

    cmds.parent(scap_upLoc, scap_upGrp)

    cmds.xform(scap_upGrp, ws=True, t=[scap_jnt_pos[0], scap_jnt_pos[1] + (pointDis * 2), scap_jnt_pos[2]])

    cmds.parent(scap_upGrp, spine)
    cmds.parent(scap_aimGrp, shoulder_grp)

    cmds.aimConstraint(scap_aimLoc, scapula, mo=True, wuo=scap_upLoc, wut='object', aim=[0, -1, 0], u=[0, 0, 1])

    adl = cmds.createNode('addDoubleLinear', name='scapula_adl' + suffix)
    cmds.setAttr(adl + '.input1', cmds.getAttr(scapula + '.translateZ'))
    cmds.connectAttr(adl + '.output', scapula + '.translateZ')

    mult = cmds.createNode('multiplyDivide', name='scapula_MD' + suffix)
    cmds.setAttr(mult + '.input2Y', .2)
    cmds.connectAttr(control + '.translateY', mult + '.input1Y')
    cmds.connectAttr(mult + '.outputY', adl + '.input2')


def createClavicleRig(obj, aimObj, upParent, suffix, aim, up):
    # clavical
    pyObj = ls(obj)[0]
    objPos = pyObj.getTranslation(space='world')
    objRot = pyObj.getRotation(space='world')
    # clavical child
    pyChild = pyObj.getChildren()[0]
    childPos = pyChild.getTranslation(space='world')
    childRot = pyChild.getRotation(space='world')

    # aim loc
    aimLoc = spaceLocator(name='clavicle_aimLoc' + suffix)
    aimLoc.setTranslation(childPos)
    aimLoc.setRotation(childRot)
    aimLoc.setParent(upParent)
    aimLoc.visibility.set(0)

    # up loc
    upLoc = spaceLocator(name='clavicle_upLoc' + suffix)
    upLoc.setTranslation(objPos)
    upLoc.setRotation(objRot)
    upLoc.setParent(obj)
    upLoc.setTranslation([0, 10, 0], space='object')
    upLoc.setParent(upParent)
    upLoc.visibility.set(0)

    aimConstraint(aimObj, obj, mo=True, wuo=upLoc, wut='object', aim=aim, u=up)


def createQuadScapulaRig(shoulder, shoulder_grp, scapula, control, spine, suffix, setChannels=False):

    pointDis = misc.distance2Pts(cmds.xform(shoulder, query=True, ws=True, rp=True),
                                 cmds.xform(scapula, query=True, ws=True, rp=True))

    scap_aimGrp = cmds.group(name='scapula_aimGrp' + suffix, em=True)
    scap_aimLoc = cmds.spaceLocator(n='scapula_aimLoc' + suffix)[0]
    cmds.parent(scap_aimLoc, scap_aimGrp)

    scap_jnt_pos = cmds.xform(scapula, query=True, ws=True, rp=True)
    cmds.xform(scap_aimGrp, ws=True, t=[scap_jnt_pos[0], cmds.xform(control, query=True, ws=True, t=True)[1], scap_jnt_pos[2]])

    scap_upGrp = cmds.group(name='scapula_upGrp' + suffix, em=True)
    scap_upLoc = cmds.spaceLocator(n='scapula_upLoc' + suffix)[0]

    cmds.parent(scap_upLoc, scap_upGrp)

    cmds.xform(scap_upGrp, ws=True, t=[scap_jnt_pos[0], scap_jnt_pos[1], scap_jnt_pos[2] + (pointDis * 2)])

    cmds.parent(scap_upGrp, spine)
    cmds.parent(scap_aimGrp, shoulder_grp)

    cmds.aimConstraint(scap_aimLoc, scapula, mo=True, wuo=scap_upLoc, wut='object', aim=[0, -1, 0], u=[1, 0, 0])

    adl = cmds.createNode('addDoubleLinear', name='scapula_adl' + suffix)
    cmds.setAttr(adl + '.input1', cmds.getAttr(scapula + '.translateY'))
    cmds.connectAttr(control + '.translateY', adl + '.input2')
    cmds.connectAttr(adl + '.output', scapula + '.translateY')
    cmds.connectAttr(control + '.translateY', scap_upLoc + '.translateY')

    if setChannels == True:
        misc.setChannels(scap_aimGrp, [True, False], [True, False], [True, False], [False, True, False])
        misc.setChannels(scap_aimLoc, [True, False], [True, False], [True, False], [False, True, False])

        misc.setChannels(scap_upGrp, [True, False], [True, False], [True, False], [False, True, False])
        misc.setChannels(scap_upLoc, [True, False], [True, False], [True, False], [False, True, False])


def ankleTwist(name, Master, Top, Btm, Ct, UpObj, AimObj, setChannels=True, up=[1, 0, 0], aim=[0, -1, 0]):
    """creates auto ankle twist rig with on/off switch
    \n*
    Master    = lowest master controller of char          --(not manipulated, 3 objs are constrained to it, for twist value calc)\n
    Top       = shoulder or hip control                   --(not manipulated, ankleTwist group is parented under this object)\n
    Btm       = group above group being aimed             --()\n
    Ct        = ankle control                             --()\n
    UpObj     = ankle up object for aimConstraint         --()\n
    AimObj    = ankle aim object for aimConstraint        --()\n
    up        = [int, int, int]                           --(ie. [1,0,0], use controller space not joint space)\n
    aim       = [int, int, int]                           --(ie. [0,-1,0], use controller space not joint space)\n
    *\n
    Note      = Master, Top, Btm should all have the same rotation order.
    ie.       = Twist axis should be main axis. If 'y'is main axis, rotate order = 'zxy' or 'xzy'
    """

    import atom_placement_lib as place

    aimAxis = None
    upAxis = None
    upAnimDir = []
    skipAxis = ['x', 'y', 'z']
    rotOrder = None
    upDir = 1
    # rotate order dict
    rotOrderList = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}

    def setRotOrder(obj, rotOrder):
        cmds.setAttr(obj + '.rotateOrder', rotOrder)

    # find rotate order
    # last/main axis in rotate order
    if aim[0] != 0:
        rotOrder = 'x'
        aimAxis = 'X'
        skipAxis.remove(rotOrder)
    elif aim[1] != 0:
        rotOrder = 'y'
        aimAxis = 'Y'
        skipAxis.remove(rotOrder)
    elif aim[2] != 0:
        rotOrder = 'z'
        aimAxis = 'Z'
        skipAxis.remove(rotOrder)

    # second axis in rotate order
    if up[0] != 0:
        rotOrder += 'x'
        upAxis = 'X'
        if up[0] < 0:  # is 'x' negative
            upDir = -1
    elif up[1] != 0:
        rotOrder += 'y'
        upAxis = 'Y'
        if up[1] < 0:  # is 'y' negative
            upDir = -1
    elif up[2] != 0:
        rotOrder += 'z'
        upAxis = 'Z'
        if up[2] < 0:  # is 'z' negative
            upDir = -1

    # first axis in rotate order
    if 'x' not in rotOrder:
        rotOrder += 'x'
        upAnimDir = ['Y', 'Z']
    elif 'y' not in rotOrder:
        rotOrder += 'y'
        upAnimDir = ['X', 'Z']
    elif 'z' not in rotOrder:
        rotOrder += 'z'
        upAnimDir = ['X', 'Y']

    # reverse string order
    rotOrder = rotOrder[::-1]

    # convert to value from dictionary
    for item in rotOrderList:
        if item == rotOrder:
            rotOrder = rotOrderList[item]

    # Groups
    # Master Twist group
    twstGp = place.null2(name + '_TwistGp', Top)[0]
    ##cmds.parent(twstGp, Top)
    misc.cleanUp(twstGp, Ctrl=True)
    cmds.orientConstraint(Top, twstGp, w=1, mo=False)
    cmds.pointConstraint(Top, twstGp, w=1, mo=False)

    # Top
    MstrTopGp = place.null2(name + '_MstrTopGp', Top)[0]
    IsoTopGp = place.null2(name + '_IsoTopGp', Top)[0]
    setRotOrder(MstrTopGp, rotOrder)
    setRotOrder(IsoTopGp, rotOrder)
    cmds.parent(IsoTopGp, MstrTopGp)
    cmds.parent(MstrTopGp, twstGp)
    cmds.pointConstraint(Top, MstrTopGp, w=1, mo=False)
    cmds.orientConstraint(Master, MstrTopGp, w=1, mo=False)
    cmds.orientConstraint(Top, IsoTopGp, w=1, mo=False)

    # Twst
    MstrTwstGp = place.null2(name + '_MstrTwstGp', Top)[0]
    IsoTwstGp = place.null2(name + '_IsoTwstGp', Top)[0]
    setRotOrder(MstrTwstGp, rotOrder)
    setRotOrder(IsoTwstGp, rotOrder)
    cmds.parent(IsoTwstGp, MstrTwstGp)
    cmds.parent(MstrTwstGp, twstGp)
    cmds.pointConstraint(Top, MstrTwstGp, w=1, mo=False)
    OrntSwtch = cmds.orientConstraint(Master, MstrTwstGp, w=1, mo=False)[0]

    # Btm
    MstrBtmGp = place.null2(name + '_MstrBtmGp', Btm)[0]
    IsoBtmGp = place.null2(name + '_IsoBtmGp', Btm)[0]
    setRotOrder(MstrBtmGp, rotOrder)
    setRotOrder(IsoBtmGp, rotOrder)
    cmds.parent(IsoBtmGp, MstrBtmGp)
    cmds.parent(MstrBtmGp, twstGp)
    cmds.pointConstraint(Btm, MstrBtmGp, w=1, mo=False)
    cmds.orientConstraint(Master, MstrBtmGp, w=1, mo=False)
    cmds.orientConstraint(Btm, IsoBtmGp, w=1, mo=False)

    # Auto Switch Gps
    TwistTopGp = place.null2(name + '_TwistTopSwitchGp', Top)[0]
    TwistSwitchGp = place.null2(name + '_TwistSwitchGp', Top)[0]
    setRotOrder(TwistTopGp, rotOrder)
    setRotOrder(TwistSwitchGp, rotOrder)
    cmds.parent(UpObj, TwistSwitchGp)
    cmds.parent(AimObj, TwistSwitchGp)
    TwistBtmGp = place.null2(name + '_TwistBtmSwitchGp', Top)[0]
    cmds.parentConstraint(Btm, TwistBtmGp, w=1, mo=True)
    cmds.parent(TwistTopGp, IsoTwstGp)
    cmds.parent(TwistSwitchGp, IsoTwstGp)
    cmds.parent(TwistBtmGp, IsoTwstGp)
    # Auto Switch
    AutoOffOn = 'AutoAnkle'
    Auto = 'TwistWeight'
    cmds.addAttr(Ct, ln=AutoOffOn, attributeType='float', k=True, dv=1, min=0.0, max=1.0)
    cmds.addAttr(Ct, ln=Auto, attributeType='enum', en='OPTNS')
    cmds.setAttr(Ct + '.' + Auto, cb=True)
    LockUp = cmds.parentConstraint(TwistTopGp, TwistSwitchGp, w=1.0, mo=False)[0]
    cmds.parentConstraint(TwistBtmGp, TwistSwitchGp, w=0.0, mo=False)
    wghtAttr = cmds.listAttr(LockUp, k=True, ud=True)
    revrsLock = cmds.shadingNode('reverse', au=True, n=(name + '_AnkleLockRev'))
    cmds.connectAttr(Ct + '.' + AutoOffOn, revrsLock + '.input' + aimAxis)
    cmds.connectAttr(revrsLock + '.output' + aimAxis, LockUp + '.' + wghtAttr[1])
    cmds.connectAttr(Ct + '.' + AutoOffOn, LockUp + '.' + wghtAttr[0])
    '''
    cmds.connectAttr(Ct + '.translateX', UpObj + '.translateX')
    cmds.connectAttr(Ct + '.translateY', UpObj + '.translateY')
    cmds.connectAttr(Ct + '.translateZ', UpObj + '.translateZ')
    '''

    # twistBlend
    # attrs on Btm
    OnOff = 'OffOn'
    TwistBlndAttr = 'TopBtm'
    # blend Node
    TwstBlnd = cmds.shadingNode('blendColors', name=name + TwistBlndAttr, asUtility=True)
    cmds.addAttr(Ct, ln=OnOff, attributeType='long', k=False, dv=1, min=0, max=1)
    cmds.addAttr(Ct, ln=TwistBlndAttr, attributeType='float', k=True, dv=1.0, min=0.0, max=1.0)
    # mltpl Nodes
    mltplTop = cmds.shadingNode('multiplyDivide', au=True, n=(name + '_MltplTopTwist'))
    mltplBtm = cmds.shadingNode('multiplyDivide', au=True, n=(name + '_MltplBtmTwist'))
    cmds.setAttr((mltplTop + '.operation'), 1)
    cmds.setAttr((mltplBtm + '.operation'), 1)
    # reverse node to 'TwistBlndAttr' attr
    revrsTop = cmds.shadingNode('reverse', au=True, n=(name + '_MltplBtmTwist'))
    cmds.connectAttr(Ct + '.' + TwistBlndAttr, revrsTop + '.input' + aimAxis)
    # connect mltpl nodes
    cmds.connectAttr(IsoTopGp + '.rotate' + aimAxis, mltplTop + '.input1' + aimAxis)
    cmds.connectAttr(IsoBtmGp + '.rotate' + aimAxis, mltplBtm + '.input1' + aimAxis)
    cmds.connectAttr(revrsTop + '.output' + aimAxis, mltplTop + '.input2' + aimAxis)
    cmds.connectAttr(Ct + '.' + TwistBlndAttr, mltplBtm + '.input2' + aimAxis)
    # merge twist values
    Add = cmds.createNode('addDoubleLinear', n=name + '_MergeTwist')
    cmds.connectAttr(mltplTop + '.output' + aimAxis, Add + '.input1')
    cmds.connectAttr(mltplBtm + '.output' + aimAxis, Add + '.input2')
    # blend node connections (TwstBlnd)
    wghtAttr = cmds.listAttr(OrntSwtch, k=True, ud=True)[0]
    cmds.connectAttr(TwstBlnd + '.outputR', OrntSwtch + '.' + wghtAttr)
    cmds.connectAttr(Ct + '.' + OnOff, TwstBlnd + '.blender')
    cmds.connectAttr(Add + '.output', TwstBlnd + '.color1G')
    cmds.connectAttr(TwstBlnd + '.outputG', IsoTwstGp + '.rotate' + aimAxis)

    if setChannels == True:
        misc.setChannels(twstGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(MstrTopGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(IsoTopGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(MstrTwstGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(IsoTwstGp, [True, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(MstrBtmGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(IsoBtmGp, [True, False], [True, False], [True, False], [True, False, False])

    return TwistSwitchGp


def pvRig(name, Master, Top, Btm, Twist, pv, midJnt, X, slider, setChannels=True, up=[1, 0, 0], aim=[0, -1, 0], color=17):
    """creates pole vector rig
    \n*
    Master    = lowest master controller of char          --(not manipulated, 3 objs are constrained to it, for twist value calc)\n
    Top       = controller at top of ik                   --(not manipulated, pvRig group is parented under this object)\n
    Btm       = bottom of ik, controlling group or null   --(not manipulated, aim object for 'Top')\n
    Twist     = object from which twist is derived        --(not manipulated, axis is derived from 'aim' variable)\n
    pv        = pre-positioned pole vector object         --(object gets parented, turned off)\n
    midJnt    = connection joint for guideline            --(not manipulated)\n
    X         = size
    up        = [int, int, int]                           --(ie. [1,0,0], use controller space not joint space)\n
    aim       = [int, int, int]                           --(ie. [0,-1,0], use controller space not joint space)\n
    color     = int 1-31                                  --(ie. 17 is yellow)\n
    *\n
    Note      = Master, Top, Twist should all have the same rotation order.
    ie.       = Twist axis should be main axis. If 'y'is main axis, rotate order = 'zxy' or 'xzy'
    """

    import atom_placement_lib as place
    # place.loc('pv___1', pv)
    aimAxis = None
    upAxis = None
    upAnimDir = []
    skipAxis = ['x', 'y', 'z']
    rotOrder = None
    if '_R' in name:
        upDir = 1
    else:
        upDir = 1
    # rotate order dict
    rotOrderList = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}

    # guide grp
    guideGp = 'GuideGp'
    try:
        cmds.parent(guideGp, '___WORLD_SPACE')
    except:
        pass
    if cmds.objExists(guideGp) == 0:
        cmds.group(em=True, name=guideGp)
        if setChannels == True:
            misc.setChannels(guideGp, [True, False], [True, False], [True, False], [True, False, False])
    guides = misc.guideLine(midJnt, pv, name + '_gLine')
    pvGds = cmds.group(em=True, name=name + '_PVutlsGp')

    cmds.parent(pvGds, guideGp)
    cmds.select(guides[0], pvGds)
    cmds.parent()
    cmds.select(guides[1], pvGds)
    cmds.parent()
    cmds.connectAttr(pv + '.visibility', pvGds + '.visibility')

    # set rotate order
    def setRotOrder(obj, rotOrder):
        cmds.setAttr(obj + '.rotateOrder', rotOrder)

    # find rotate order
    # last/main axis in rotate order
    if aim[0] != 0:
        rotOrder = 'x'
        aimAxis = 'X'
        skipAxis.remove(rotOrder)
    elif aim[1] != 0:
        rotOrder = 'y'
        aimAxis = 'Y'
        skipAxis.remove(rotOrder)
    elif aim[2] != 0:
        rotOrder = 'z'
        aimAxis = 'Z'
        skipAxis.remove(rotOrder)

    print aimAxis, '__________ aimAxis'

    # second axis in rotate order
    if up[0] != 0:
        rotOrder += 'x'
        upAxis = 'X'
        if up[0] < 0:  # is 'x' negative
            upDir = -1
    elif up[1] != 0:
        rotOrder += 'y'
        upAxis = 'Y'
        if up[1] < 0:  # is 'y' negative
            upDir = -1
    elif up[2] != 0:
        rotOrder += 'z'
        upAxis = 'Z'
        if up[2] < 0:  # is 'z' negative
            upDir = -1

    # first axis in rotate order
    if 'x' not in rotOrder:
        rotOrder += 'x'
        upAnimDir = ['Y', 'Z']
    elif 'y' not in rotOrder:
        rotOrder += 'y'
        upAnimDir = ['X', 'Z']
    elif 'z' not in rotOrder:
        rotOrder += 'z'
        upAnimDir = ['X', 'Y']

    # reverse string order
    rotOrder = rotOrder[::-1]

    # convert to value from dictionary
    for item in rotOrderList:
        if item == rotOrder:
            rotOrder = rotOrderList[item]

    # rig grp
    rig = place.null2(name + '_RigGp', Top)[0]
    cmds.orientConstraint(Top, rig, w=1, mo=False)
    cmds.pointConstraint(Top, rig, w=1, mo=False)

    # top grp
    topGp = place.null2(name + '_AimGp', Top)[0]
    setRotOrder(topGp, rotOrder)
    cmds.parent(topGp, rig)
    cmds.pointConstraint(Top, topGp, w=0.5, mo=False)

    # bottom group
    btmGp = place.null2(name + '_TargetGp', Btm)[0]
    cmds.parent(btmGp, rig)
    cmds.pointConstraint(Btm, btmGp, w=1.0, mo=False)

    # up group
    # main groups
    MstrUpGp = place.null2(name + '_AimUpGp', Top)[0]
    IsoUpGp = place.null2(name + '_IsoUpGp', Top)[0]
    setRotOrder(MstrUpGp, rotOrder)
    setRotOrder(IsoUpGp, rotOrder)
    cmds.parent(IsoUpGp, MstrUpGp)
    OrntSwtch = cmds.orientConstraint(Master, MstrUpGp, w=1, mo=False)[0]
    cmds.pointConstraint(Top, MstrUpGp, w=1, mo=False)
    # up Object group
    cmds.select(IsoUpGp)
    upObjGp = (misc.insert('null', 0, name + '_UpVctrGp')[0])[0]
    cmds.select(upObjGp)
    # up vector/obj controller
    upObj = place.circle(name + '_UpVctr', upObjGp, 'diamond_ctrl', X, color, 8, 1, (0, 0, 1))[0]

    cmds.setAttr(upObj + '.translate' + upAnimDir[0], k=False, cb=True)
    cmds.setAttr(upObj + '.translate' + upAnimDir[1], k=False, cb=True)
    cmds.parent(upObj, upObjGp)
    cmds.setAttr(upObjGp + '.translate' + upAxis, 1 * upDir)
    cmds.parent(MstrUpGp, rig)
    # aimConstraint top to bottom group, up group as up space
    #place.null2(name + '______beforeAim_____', topGp)[0]
    # print aim, up, '___________ aims'
    cmds.aimConstraint(btmGp, topGp, worldUpType='object', worldUpObject=upObj, mo=False, w=1, aim=aim, u=up)
    #place.null2(name + '______afterAim_____', topGp)[0]
    #place.null2(name + '______upObj_____', upObj)[0]

    # pv weighted group
    pvWtGp = place.null2(name + '_pvWtGp', topGp)[0]
    #place.null2(name + '______what_____', topGp)[0]
    cmds.parent(pvWtGp, topGp)
    pvWtCt = place.circle(name + '_Twist', topGp, 'facetXup_ctrl', X * 1, color, 8, 1, (0, 1, 0))[0]
    cmds.parent(pvWtCt, pvWtGp)
    cmds.setAttr(pv + '.visibility', False)
    misc.addAttribute(pvWtCt, 'Pv_Vis', 0, 1, False, 'long')
    cmds.connectAttr(pvWtCt + '.Pv_Vis', pv + '.visibility')
    ##misc.hijackAttrs(pv, pvWtCt, 'visibility', 'pvVisibility', set=False)
    setRotOrder(pvWtGp, rotOrder)
    cmds.pointConstraint(topGp, pvWtGp, w=0.5, mo=False)
    cmds.pointConstraint(btmGp, pvWtGp, w=0.5, mo=False)
    # correct upObj position
    upOffst = cmds.getAttr(pvWtGp + '.translate' + aimAxis)
    cmds.setAttr(upObjGp + '.translate' + upAxis, upDir * (upOffst / 2))
    # new height adjust for biped rig, make var if needed
    # cmds.setAttr(upObjGp + '.translate' + 'Y', 1.5 * (upOffst / 2))

    # twist group
    twstGp = place.null2(name + '_TwistGp', Top)[0]
    cmds.parent(twstGp, rig)

    # Top
    MstrTopGp = place.null2(name + '_MstrTopGp', Top)[0]
    IsoTopGp = place.null2(name + '_IsoTopGp', Top)[0]
    setRotOrder(MstrTopGp, rotOrder)
    setRotOrder(IsoTopGp, rotOrder)
    cmds.parent(IsoTopGp, MstrTopGp)
    cmds.parent(MstrTopGp, twstGp)
    cmds.pointConstraint(Top, MstrTopGp, w=1, mo=False)
    # constraint maintain offset changed... #account for shoulder joint not being at zero world orient
    #cmds.orientConstraint(Master, MstrTopGp, w=1, mo=False)
    cmds.orientConstraint(Master, MstrTopGp, w=1, mo=True)
    cmds.orientConstraint(Top, IsoTopGp, w=1, mo=False)
    # Btm
    MstrBtmGp = place.null2(name + '_MstrBtmGp', Btm)[0]
    IsoBtmGp = place.null2(name + '_IsoBtmGp', Btm)[0] #likely cause of elbow flipping. interpolated value can be a flipped one 
    
    setRotOrder(MstrBtmGp, rotOrder)
    setRotOrder(IsoBtmGp, rotOrder)
    cmds.parent(IsoBtmGp, MstrBtmGp)
    
    ### try and fix flipping ########################
    #null inserts in a flipped position but cranked values at 180 degrees
    import zero as z
    cmds.select(IsoBtmGp)
    z.zero()
    import anim_lib as anm
    cmds.select(IsoBtmGp, Twist)
    anm.matchObj()
    ### seems to work more reliabley ####################################
    
    
    cmds.parent(MstrBtmGp, twstGp)
    cmds.pointConstraint(Btm, MstrBtmGp, w=1, mo=False)
    cmds.orientConstraint(Master, MstrBtmGp, w=1, mo=False)
    # new for biped setup, orient controls to joints, pole vectors break
    # cmds.orientConstraint(Twist, IsoBtmGp, w=1, mo=False)
    cmds.orientConstraint(Twist, IsoBtmGp, w=1, mo=True)

    # twistBlend
    # attrs on Twist
    OnOff = 'TwistOff_On'
    TwistBlndAttr = 'TwistBlendTopBtm'
    # blend Node
    TwstBlnd = cmds.shadingNode('blendColors', name=name + TwistBlndAttr, asUtility=True)
    #misc.hijackAttrs(TwstBlnd, pvWtCt, 'blender', OnOff, False)
    cmds.addAttr(pvWtCt, ln=OnOff, attributeType='long', k=True, dv=1, min=0, max=1)
    cmds.addAttr(pvWtCt, ln=TwistBlndAttr, attributeType='float', k=True, dv=1.0, min=0.0, max=1.0)
    # mltpl Nodes
    mltplTop = cmds.shadingNode('multiplyDivide', au=True, n=(name + '_MltplTopTwist'))
    mltplBtm = cmds.shadingNode('multiplyDivide', au=True, n=(name + '_MltplBtmTwist'))
    cmds.setAttr((mltplTop + '.operation'), 1)
    cmds.setAttr((mltplBtm + '.operation'), 1)
    # reverse node to 'TwistBlndAttr' attr
    revrsTop = cmds.shadingNode('reverse', au=True, n=(name + '_MltplBtmTwist'))
    cmds.connectAttr(pvWtCt + '.' + TwistBlndAttr, revrsTop + '.input' + aimAxis)
    # connect mltpl nodes
    cmds.connectAttr(IsoTopGp + '.rotate' + aimAxis, mltplTop + '.input1' + aimAxis)
    cmds.connectAttr(IsoBtmGp + '.rotate' + aimAxis, mltplBtm + '.input1' + aimAxis)
    cmds.connectAttr(revrsTop + '.output' + aimAxis, mltplTop + '.input2' + aimAxis)
    cmds.connectAttr(pvWtCt + '.' + TwistBlndAttr, mltplBtm + '.input2' + aimAxis)
    # merge twist values
    Add = cmds.createNode('addDoubleLinear', n=name + '_MergeTwist')
    cmds.connectAttr(mltplTop + '.output' + aimAxis, Add + '.input1')
    cmds.connectAttr(mltplBtm + '.output' + aimAxis, Add + '.input2')
    # blend node connections (TwstBlnd)
    wghtAttr = cmds.listAttr(OrntSwtch, k=True, ud=True)[0]
    cmds.connectAttr(TwstBlnd + '.outputR', OrntSwtch + '.' + wghtAttr)
    cmds.connectAttr(pvWtCt + '.' + OnOff, TwstBlnd + '.blender')
    cmds.connectAttr(Add + '.output', TwstBlnd + '.color1G')
    cmds.connectAttr(TwstBlnd + '.outputG', IsoUpGp + '.rotate' + aimAxis)

    # pv position group
    pvPsGp = place.null2(name + '_PsGp', pv)[0]
    cmds.parent(pv, pvPsGp)
    cmds.parent(pvPsGp, pvWtCt)
    cmds.connectAttr(slider + '.KneeTwist', pvWtCt + '.ry')

    if setChannels == True:
        misc.setChannels(pvGds, [True, False], [True, False], [True, False], [False, False, False])
        misc.setChannels(rig, [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(topGp, [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(btmGp, [False, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(upObj, [False, True], [True, False], [True, False], [False, False, False])
        misc.setChannels(MstrUpGp, [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(IsoUpGp, [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(pvWtGp, [False, False], [True, False], [True, False], [True, False, False])

        misc.setChannels(pvWtCt, [True, False], [True, False], [True, False], [True, False, False])
        cmds.setAttr(pvWtCt + '.rotate' + aimAxis, l=False)
        ##cmds.setAttr(pvWtCt+ '.rotateZ', k=False,l=True)

        misc.setChannels(upObjGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(twstGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(MstrTopGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(IsoTopGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(MstrBtmGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(IsoBtmGp, [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(pvPsGp, [True, False], [True, False], [True, False], [True, False, False])

    # done, return rig group
    ##cmds.parent(rig, Top)
    # place.loc('pv___After_1', pv)
    misc.cleanUp(rig, Ctrl=True)
    return rig


def stepToGoal(goal=[0.0, 0.0, 0.0], sample=0.001, obj=[], operation='<', goalAxis=1, axis=[0, 0, 1], uiFlip=[False, True, True]):
    # print goal, '  goal'
    # print sample, '  sample'
    # print obj, '  obj'
    # print operation, '  operation'
    # print goalAxis, '   goalAxis'
    # print axis, '  axis'
    # print uiFlip, '  uiFlip'
    goal = goal[goalAxis]
    loc_pos = cmds.xform(obj, query=True, ws=True, t=True)[goalAxis]
    # print 'set goal'
    flip = [1, 1, 1]
    for i in range(0, 3, 1):
        if uiFlip[i] == 1:
            flip[i] = -1
    # print flip, '  flip'
    quit = 1000
    i = 0
    if operation == '<':
        while loc_pos < goal:
            cmds.xform(obj, r=True, os=True, t=[-(axis[0] * flip[0]), -(axis[1] * flip[1]), -(axis[2] * flip[2])])
            loc_pos = cmds.xform(obj, query=True, ws=True, t=True)[goalAxis]
            # print operation, goal, loc_pos
            i = i + 1
            if i > quit:
                break
    else:
        # print loc_pos, goal
        while loc_pos > goal:
            cmds.xform(obj, r=True, os=True, t=[0, 0, -sample])
            loc_pos = cmds.xform(obj, query=True, ws=True, t=True)[goalAxis]
            # print operation, goal, loc_pos


def xformDigitLoc(locator, flip, axis, dis, scale):
    flip = misc.convertFlipValue(flip)
    dis = flip[2] * dis
    cmds.setAttr(locator + '.translate' + axis, dis)

    cmds.setAttr(locator + '.scaleX', scale)
    cmds.setAttr(locator + '.scaleY', scale)
    cmds.setAttr(locator + '.scaleZ', scale)


def create_ik(fstJnt, lstJnt, prefix, suffix, limbName, curveShapePath=None, createControl=False, clean=True, orient=True):
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    printMeta(fstJnt + '__' + lstJnt)
    returnList = []
    ikName = misc.buildName(prefix, suffix, limbName + '_ikh')
    ikHandle = cmds.ikHandle(name=ikName, sj=fstJnt, ee=lstJnt, sol='ikRPsolver', w=1, pw=1, fs=1, shf=1, s=0)
    printMeta('added ik')
    returnList.append(ikHandle)
    ctrl = None

    if createControl == True:
        # create group at the end joint
        lstRot = cmds.xform(lstJnt, query=True, ws=True, ro=True)
        lstPos = cmds.xform(lstJnt, query=True, ws=True, rp=True)
        orntGrp = place.null(misc.buildName(prefix, suffix, limbName + '_ctrl_ornt_grp'))[0]

        if cmds.xform(lstJnt, q=True, ws=True, t=True)[0] < 0:
            cmds.xform(orntGrp, ws=True, t=lstPos, ro=[lstRot[0] + 180, lstRot[1], lstRot[2]])
        else:
            cmds.xform(orntGrp, ws=True, t=lstPos, ro=lstRot)

        if orient == False:
            cmds.setAttr(orntGrp + '.rotateX', 0)

        ctrl = place.circle(misc.buildName(prefix, suffix, limbName + '_ctrl'), orntGrp, 'facetXup_ctrl', X * 1.50, 17, 8, 1, [0, 0, 1])
        cmds.parent(ctrl, orntGrp)
        cmds.parent(ikHandle[0], ctrl)
        returnList.append(ctrl)
        returnList.append(orntGrp)

        if clean == True:
            # set the channels for the control
            misc.setChannels(ctrl[0], [False, True], [False, True], [True, False], [True, False, False], [True, True])

    if clean == True:
        misc.setChannels(ikHandle[0], [False, False], [True, False], [True, False], [False, False, False], [True, True])

    return returnList


def create_3_joint_pv(stJnt, endJnt, prefix, suffix, limbName, rotControl, aimControl, upControl, disFactor, locScale, curveShapePath, useFlip=True, flipVar=[0, 0, 0]):
    # make a copy of flipVar so the original varaible doesnt get changed
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    flip = misc.convertFlipValue(flipVar)

    #        A
    #       /|
    #     c/ |
    #     / _| d is the length from a to right angle.
    #  B /_|_|
    #    \   | b, is the length from A to C.
    #     \  |
    #     a\ |
    #       \|
    #        C
    # A,B and C are angles, a,b and c are the distances lengths points
    midJnt = joint.jointTravers(stJnt, 1)

    point_A = cmds.xform(stJnt, query=True, ws=True, rp=True)
    point_B = cmds.xform(midJnt, query=True, ws=True, rp=True)
    point_C = cmds.xform(endJnt, query=True, ws=True, rp=True)

    # solve the lengths
    a = misc.distance2Pts(point_B, point_C)
    b = misc.distance2Pts(point_A, point_C)
    c = misc.distance2Pts(point_A, point_B)

    # solve the angle for A when all lengths are known
    # cos_d is a radian and must be converted
    import math
    cos_d = (math.pow(c, 2) + math.pow(b, 2) - math.pow(a, 2)) / (2 * b * c)

    # convert cos_d to degrees from radians
    angle = flip[0] * (math.degrees(math.acos(cos_d)))

    # get the length to the right angle which is d
    length = flip[1] * (c * cos_d)

    # create the tmp grps
    tmpGrp = cmds.group(n='tmpPosGrp', em=True, world=True)
    cmds.xform(tmpGrp, ws=True, t=point_A)
    cmds.parent(tmpGrp, stJnt)
    cmds.makeIdentity(tmpGrp, apply=True, t=True, r=True, s=True, n=False)

    rotList = ui.createListForTransform(rotControl, angle)
    aimList = ui.createListForTransform(aimControl, length)

    # test if the trianlge is pointing forward or back using the midJnt
    rotAxis = ui.convertAxisNum(cmds.radioButtonGrp(rotControl, query=True, sl=True))
    flipRot = ui.getCheckBoxSelectionAsList('atom_qls_pvFlip_checkBoxGrp')
    flipIt = [1, 1, 1]
    if useFlip == True:
        for i in range(0, 3, 1):
            if flipRot[i] == 1:
                flipIt[i] = -1

    rotValue = cmds.getAttr(midJnt + '.jointOrient' + rotAxis)

    if midJnt[len(midJnt) - 2:] == '_L' or midJnt[len(midJnt) - 2:] == '_R':
        midJnt = midJnt[:-2]

    tmpLoc = place.loc('tmpLoc')

    # place the locator at the first selection
    cmds.xform(tmpLoc, ws=True, t=point_A)
    cmds.parent(tmpLoc, tmpGrp)
    cmds.makeIdentity(tmpLoc, apply=True, t=True, r=True, s=True, n=False)
    cmds.xform(tmpGrp, os=True, ro=[rotList[0] * flipIt[0], rotList[1] * flipIt[1], rotList[2] * flipIt[2]])
    cmds.xform(tmpGrp, os=True, t=[aimList[0], aimList[1], aimList[2]])

    # get the distance from point_B to the tmp_pv
    pv_pos = cmds.xform(tmpLoc, query=True, ws=True, t=True)
    # get the distance from d to b, then add the distance from  a to b
    # a to b is also multiplied by the disFactor incase the user wants control
    # over the total distance

    upList = ui.createListForTransform(upControl, disFactor)
    cmds.xform(tmpLoc, os=True, t=upList)

    cmds.parent(tmpLoc, w=True)
    #cmds.makeIdentity(tmpLoc, apply=True, t=True, r=True,s=True,n=False)
    cmds.delete(tmpGrp)

    locName = misc.buildName(prefix, suffix, midJnt + '_pv_loc')
    pvCtrl = place.circle(locName, tmpLoc, 'diamond_ctrl', X * 1, color=17, sections=8, degree=1, normal=(0, 1, 0))[0]
    cmds.delete(tmpLoc)

    return pvCtrl


def createLimb(name, stJnt, endJnt, disPoint, pvLocPos, buildPlane, suffix, scale, freeze=True, pv=True):
    # create an IK chain from stJnt to the second joint in the hierarchy
    ikHandle = cmds.ikHandle(sj=stJnt, ee=endJnt, sol='ikRPsolver', w=1, pw=1, fs=1, shf=1,
                             s=0, name=name + '_ikh_' + suffix)[0]

    returnVal = None
    ikLoc = None
    if pv == True:
        pnt_1 = cmds.xform(stJnt, query=True, ws=True, rp=True)
        pnt_2 = cmds.xform(pvLocPos, query=True, ws=True, rp=True)
        dis = misc.distance2Pts(pnt_1, pnt_2)
        ikLoc = cmds.spaceLocator(name=name + '_pvLoc_' + suffix)[0]
        # move the locator to the second joint
        cmds.xform(ikLoc, ws=True, t=pnt_2)

        # move the locator out the distance from the 1st joint to the 2nd
        mvDis = misc.axisMulti(buildPlane, dis)
        cmds.xform(ikLoc, ws=True, r=True, t=mvDis)

        # create the poleVectorConstraint
        cmds.poleVectorConstraint(ikLoc, ikHandle)
        if freeze == True:
            cmds.makeIdentity(ikLoc, apply=True, t=True, r=True, s=True, n=False)
            cmds.makeIdentity(ikHandle, apply=True, t=True, r=True, s=True, n=False)
        # Set the scale of the locator

        #cmds.setAttr(ikLoc + '.scaleX', scale)
        #cmds.setAttr(ikLoc + '.scaleY', scale)
        #cmds.setAttr(ikLoc + '.scaleZ', scale)

    return [ikHandle, ikLoc]


def createStandardDigit(base_digit, end_digit, prefix, suffix, limbName, rotAxis, aimAxis, upAxis, disFactor, scale, aimAxisList, upAxisList, flipVar=[0, 0, 0], clean=True, curveShapePath=None):
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    base_digit_pos = cmds.xform(base_digit, query=True, ws=True, rp=True)
    base_digit_rot = cmds.xform(base_digit, query=True, ws=True, ro=True)

    end_digit_pos = cmds.xform(end_digit, query=True, ws=True, rp=True)
    if cmds.xform(base_digit, q=True, ws=True, t=True)[0] < 0:
        base_digit_rot[0] = base_digit_rot[0] + 180
        #cmds.xform(digit_ornt_grp, os=True, ro=[ro[0] + 180,ro[1],ro[2]])
    if suffix == 'none':
        suffix = ''
    if limbName == 'none':
        limbName = ''

    digit_up_loc = cmds.spaceLocator(name=misc.buildName(prefix, suffix, limbName + '_up_loc'))[0]
    digit_aim_loc = cmds.spaceLocator(name=misc.buildName(prefix, suffix, limbName + '_aim_loc'))[0]

    digit_ornt_grp = cmds.group(name=misc.buildName(prefix, suffix, limbName + '_ornt_grp'), em=True, w=True)
    digit_ctrl_grp = cmds.group(name=misc.buildName(prefix, suffix, limbName + '_ctrl_grp'), em=True, w=True)

    cmds.xform(digit_ornt_grp, ws=True, ro=base_digit_rot)
    cmds.xform(digit_ornt_grp, ws=True, t=base_digit_pos)
    cmds.xform(digit_ctrl_grp, ws=True, t=base_digit_pos)
    cmds.xform(digit_up_loc, r=True, t=base_digit_pos)

    base_ctrl = place.circle(misc.buildName(prefix, suffix, limbName + '_ctrl'), digit_ornt_grp, 'facetXup_ctrl', X * 1.25, 17, 8, 1, [0, 0, 1])
    end_ctrl = cmds.circle(n=misc.buildName(prefix, suffix, limbName + '_end_ctrl'), ch=False, nr=(0, 0, 0), c=(0, 0, 0), s=8, d=1)
    cmds.select(end_ctrl)
    ui.importCurveShape('diamond_ctrl', curveShapePath, X * 1.25, 17)

    cmds.xform(digit_aim_loc, ws=True, t=end_digit_pos)
    cmds.xform(end_ctrl, ws=True, t=end_digit_pos)
    cmds.xform(end_ctrl, ws=True, ro=base_digit_rot)
    ctrl_list = [base_ctrl, end_ctrl]

    for ctrl in ctrl_list:
        cmds.setAttr(ctrl[0] + '.scaleX', scale)
        cmds.setAttr(ctrl[0] + '.scaleY', scale)
        cmds.setAttr(ctrl[0] + '.scaleZ', scale)

    cmds.parent(digit_ctrl_grp, digit_ornt_grp)
    cmds.parent(base_ctrl, digit_ornt_grp)
    cmds.parent(digit_up_loc, base_ctrl)
    cmds.parent(end_ctrl, base_ctrl)
    cmds.parent(digit_aim_loc, end_ctrl)
    cmds.makeIdentity(base_ctrl, apply=True, t=True, r=True, s=True, n=False)
    cmds.makeIdentity(end_ctrl, apply=True, t=True, r=True, s=True, n=False)

    digitAim = aimAxisList[:]
    digitUp = upAxisList[:]
    # flip the correct axis for the aim control
    for i in range(0, len(flipVar), 1):
        # 0 =x, 1=y, 2=z
        if flipVar[i] == 1:
            digitAim[i] = -1 * (digitAim[i])
            digitUp[i] = -1 * (digitUp[i])

    xformDigitLoc(digit_up_loc, [0, 0, 0], upAxis, disFactor, scale)
    cmds.aimConstraint(digit_aim_loc, base_digit, wuo=digit_up_loc, wut='object', aim=digitAim, u=[0, 1, 0])
    # clean up the locators
    if clean == True:
        # set the controls
        misc.setChannels(base_ctrl[0], [True, False], [False, True], [True, False], [True, False, False], [True, True])
        misc.setChannels(end_ctrl[0], [False, True], [True, False], [True, False], [True, False, False], [True, True])

        clean_loc_list = [digit_up_loc, digit_aim_loc]

        clean_grp_list = [digit_ctrl_grp, digit_ornt_grp]

        for loc in clean_loc_list:
            misc.setChannels(loc, [True, False], [True, False], [True, False], [False, True, False], [True, True])
        # Dont lock the transmforms of grps that will later on be reparents. Odd transformation can occure
        for grp in clean_grp_list:
            misc.setChannels(grp, [False, False], [False, False], [False, False], [True, False, False], [True, True])
    return digit_ornt_grp


def createReverseAnkle(prefix, suffix, name, ankleJnt, paw_fk, aimAxisList, upAxisList, flipVal, setChannels=True):
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    ankle_pos = cmds.xform(ankleJnt, query=True, ws=True, rp=True)
    ankle_rot = cmds.xform(ankleJnt, query=True, ws=True, ro=True)
    ball_pos = cmds.xform(paw_fk, query=True, ws=True, rp=True)

    loc_pos = cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', query=True, v=True)
    curveShapePath = cmds.textField('atom_csst_exportPath_textField', query=True, text=True)
    #ankle_up_loc = cmds.spaceLocator(name = misc.buildName(prefix, suffix, name + '_ankle_up_loc'))
    ankle_up_grp = cmds.group(name=misc.buildName(prefix, suffix, name + '_ankle_up_grp'), em=True)
    ankle_up_loc = place.circle(misc.buildName(prefix, suffix, '_ankle_aim_ctrl'), ankle_up_grp, 'diamond_ctrl', X * 1, 17, 8, 1, [0, 1, 0])
    cmds.parent(ankle_up_loc, ankle_up_grp)

    cmds.xform(ankle_up_grp, ws=True, t=ankle_pos)
    cmds.parent(ankle_up_grp, ankleJnt)
    cmds.setAttr(ankle_up_grp + '.rx', 0)
    cmds.setAttr(ankle_up_grp + '.ry', 0)
    cmds.setAttr(ankle_up_grp + '.rz', 0)
    cmds.xform(ankle_up_grp, os=True, t=loc_pos)
    cmds.parent(ankle_up_grp, w=True)

    # Old moving the ankle_up_grp, didnt work, changed on Oct 13th 2010
    #cmds.xform(ankle_up_grp, ws=True, t= [ankle_pos[0] + loc_pos[0], ankle_pos[1]+loc_pos[1], ankle_pos[2]+loc_pos[2]], ro=ankle_rot)

    ankle_aim_loc = cmds.spaceLocator(name=misc.buildName(prefix, suffix, '_ankle_aim_loc'))
    cmds.xform(ankle_aim_loc, ws=True, t=ball_pos)

    # For some reason Maya doesnt seem to want to return all the values at the same time
    revAnkleUpAxis = upAxisList[:]
    revAnkleAimAxis = aimAxisList[:]
    for i in range(0, len(flipVal), 1):
        # 0 =x, 1=y, 2=z
        if flipVal[i] == 1:
            revAnkleAimAxis[i] = -1 * (revAnkleAimAxis[i])
            revAnkleUpAxis[i] = -1 * (revAnkleUpAxis[i])

    cmds.aimConstraint(ankle_aim_loc[0], ankleJnt, wuo=ankle_up_loc[0], wut='object', aim=revAnkleAimAxis, u=revAnkleUpAxis, mo=False)
    '''
    if setChannels == True:
        misc.setChannels(ankle_up_grp, [True, False], [True, False], [True, False], [True, True,False], [True,True])
        misc.setChannels(ankle_up_loc[0], [False, True], [True, False], [True, False], [True, True,False], [True,True])
        misc.setChannels(ankle_aim_loc[0],[False, False], [True, False], [True, False], [False, True,False], [True,True])
    '''
    return [ankle_aim_loc[0], ankle_up_loc[0], ankle_up_grp]


def createReverseLeg(setChannels=True, traversDepth=2, ballRollOffset=0.3):
    '''
    ballRollOffset = multiplier for ball roll positioning.\n
    default pivot is at the toe roll\n
    this is implemented per digit as well, in rudamentary fashion\n
    toe roll and digit roll joints in the skeleton template should be in the same tz location\n
    '''
    # create a single quad limb with a pole vector
    printMeta('start')
    sel = cmds.ls(selection=True)
    setChannels = cmds.checkBox('atom_setChannel_checkBox', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    # print '+'
    if len(sel) != 0:
        if cmds.window('atom_win', ex=True):
            hipJnt = sel[0]
            hip_ctrl = extractSebastionsControlSubgroup(sel[1])
            limb_mainCtrl = sel[2]
            limb_ctrl = extractSebastionsControlSubgroup(sel[2])
            if cmds.nodeType(hipJnt) == 'joint':
                curveShapePath = cmds.textField('atom_csst_exportPath_textField', query=True, text=True)
                # print '+'
                kneeJnt = joint.jointTravers(hipJnt, 1)
                ankleJnt = joint.jointTravers(hipJnt, traversDepth)

                paw_fk = ''
                vol_metacarpal = ''
                limbPlacementJnt = ''
                toeRollPlacementJnt = ''
                heelRollPlacementJnt = ''
                printMeta('ankle 1')
                # find the placement joints
                ankleChildren = cmds.listRelatives(ankleJnt, children=True)

                for i in range(0, len(ankleChildren), 1):
                    # cull out the digit metacarpals, they have two children one joint down from the ankleJnt
                    if len(cmds.listRelatives(ankleChildren[i], ad=True)) == 4:
                        # test the chain to be either the placement chain or the pad volume chain
                        # print ankleChildren[i], len(cmds.listRelatives(ankleChildren[i], ad=True))
                        paw_fk = ankleChildren[i]
                        limbPlacementJnt = joint.jointTravers(ankleChildren[i], 1)
                        toeRollPlacementJnt = joint.jointTravers(ankleChildren[i], 2)
                        heelRollPlacementJnt = joint.jointTravers(ankleChildren[i], 3)
                    elif len(cmds.listRelatives(ankleChildren[i], ad=True)) == 3:
                        vol_metacarpal = ankleChildren[i]

                printMeta('ankle 2')
                # print '+'
                # return None
                # For best results paw_fk should have 0 transform in the x
                if cmds.getAttr(paw_fk + '.rx') != 0:
                    wStr = '%s has non 0 transformX: %s' % (paw_fk, cmds.getAttr(paw_fk + '.tx'))
                    OpenMaya.MGlobal.displayError(wStr)

                # get the position to place the limb, toe and heel
                limbPlacementPos = cmds.xform(limbPlacementJnt, query=True, ws=True, rp=True)
                toePlacementPos = cmds.xform(toeRollPlacementJnt, query=True, ws=True, rp=True)
                heelPlacementPos = cmds.xform(heelRollPlacementJnt, query=True, ws=True, rp=True)
                anklePos = cmds.xform(ankleJnt, query=True, ws=True, rp=True)
                pawFkPos = cmds.xform(paw_fk, query=True, ws=True, rp=True)

                # get some information from the UI
                prefix = cmds.textField('atom_prefix_textField', query=True, tx=True)
                suffix = cmds.optionMenu('atom_suffix_optionMenu', query=True, v=True)
                limbName = cmds.optionMenu('atom_qls_limb_optionMenu', query=True, v=True)

                # If the ui is blank, set empyt the variables
                if suffix == 'none':
                    suffix = ''
                if limbName == 'none':
                    limbName = ''
                # Main control
                limbCtrl_grp = cmds.group(n=misc.buildName(prefix, suffix, 'limb_ctrl_grp'), em=True)
                cmds.xform(limbCtrl_grp, ws=True, t=limbPlacementPos)
                cmds.makeIdentity(limbCtrl_grp, apply=True, t=True, r=True, s=True, n=False)
                # connect scales, another scale connection made after the ankleTwist() at the end
                # '''
                cmds.select(ankleJnt, hi=True)
                scaleJnts = cmds.ls(sl=1)
                for jnt in scaleJnts:
                    if '_phal_' not in jnt and '_end_' not in jnt:
                        pass
                        # print jnt, '_____________'
                    misc.hijackScale(jnt, limbCtrl_grp)
                # '''

                # Toe Roll Control
                toeRollCtrl = cmds.circle(n=misc.buildName(prefix, suffix, '_toe_roll_ctrl'), ch=False, nr=(0, 1, 0), c=(0, 0, 0), s=8, d = 1)
                toeShape = cmds.listRelatives(toeRollCtrl[0], typ='shape')[0]
                cmds.connectAttr(sel[2] + '.Pivot', toeShape + '.visibility')
                cmds.select(toeRollCtrl)
                ui.importCurveShape('pawToeRoll_ctrl', curveShapePath, X * 3, 17)
                cmds.xform(toeRollCtrl, ws=True, t=toePlacementPos)
                cmds.parent(toeRollCtrl, limbCtrl_grp)
                # new
                # '''
                toeRollCtrlGrp = place.null2(toeRollCtrl[0] + 'Grp', toeRollPlacementJnt, orient=True)[0]
                cmds.parent(toeRollCtrlGrp, limbCtrl_grp)
                cmds.parent(toeRollCtrl, toeRollCtrlGrp)
                toePos = cmds.xform(toeRollCtrlGrp, query=True, ws=True, rp=True)
                toeOr = cmds.xform(toeRollCtrlGrp, query=True, ws=True, ro=True)
                cmds.xform(toeRollCtrl, ws=True, ro=toeOr, t=toePos)
                # '''
                # new end
                cmds.makeIdentity(toeRollCtrl, apply=True, t=True, r=True, s=True, n=False)
                cmds.connectAttr(sel[2] + '.ToeRoll', toeRollCtrl[0] + '.rx')

                # Heel Control
                heelRollCtrl = cmds.circle(n=misc.buildName(prefix, suffix, '_heel_roll_ctrl'), ch=False, nr=(0, 1, 0), c=(0, 0, 0), s=8, d = 1)
                heelShape = cmds.listRelatives(heelRollCtrl[0], typ='shape')[0]
                cmds.connectAttr(sel[2] + '.Pivot', heelShape + '.visibility')
                cmds.select(heelRollCtrl)
                ui.importCurveShape('pawHeelRoll_ctrl', curveShapePath, X * 3, 17)
                cmds.xform(heelRollCtrl, ws=True, t=heelPlacementPos)
                cmds.parent(heelRollCtrl, toeRollCtrl)
                # new
                # '''
                heelRollCtrlGrp = place.null2(heelRollCtrl[0] + 'Grp', heelRollPlacementJnt, orient=True)[0]
                cmds.parent(heelRollCtrlGrp, toeRollCtrl)
                cmds.parent(heelRollCtrl, heelRollCtrlGrp)
                heelPos = cmds.xform(heelRollCtrlGrp, query=True, ws=True, rp=True)
                heelOr = cmds.xform(heelRollCtrlGrp, query=True, ws=True, ro=True)
                cmds.xform(heelRollCtrl, ws=True, ro=heelOr, t=heelPos)
                # '''
                # new end
                cmds.makeIdentity(heelRollCtrl, apply=True, t=True, r=True, s=True, n=False)
                cmds.connectAttr(sel[2] + '.HeelRoll', heelRollCtrl[0] + '.rx')

                # Paw FK Control
                placeGrp = cmds.group(n='sebastianEatThisTemporaryPlacementGroup', em=True, w=True)
                cmds.xform(placeGrp, ws=True, t=cmds.xform(paw_fk, q=True, ws=True, rp=True))
                pawFkCtrl = place.circle(misc.buildName(prefix, suffix, '_paw_fk_ctrl'), placeGrp, 'facetXup_ctrl', X * 3.5, 12, 8, 1, [0, 1, 0])
                fkShape = cmds.listRelatives(pawFkCtrl[0], typ='shape')[0]
                cmds.connectAttr(sel[2] + '.Fk', fkShape + '.visibility')
                cmds.delete(placeGrp)
                cmds.parent(pawFkCtrl, heelRollCtrl)
                # new
                pawFkPos = cmds.xform(paw_fk, query=True, ws=True, rp=True)
                pawFkOr = cmds.xform(paw_fk, query=True, ws=True, ro=True)
                cmds.xform(pawFkCtrl, ws=True, ro=pawFkOr, t=pawFkPos)
                pawFkCtrlGrp = place.null2(pawFkCtrl[0] + 'Grp', pawFkCtrl, orient=True)[0]
                cmds.parent(pawFkCtrl, pawFkCtrlGrp)
                cmds.parent(pawFkCtrlGrp, heelRollCtrl)
                # new end
                cmds.makeIdentity(pawFkCtrl, apply=True, t=True, r=True, s=True, n=False)
                # return None

                # Ball Roll Control
                ballRollCtrl = place.circle(misc.buildName(prefix, suffix, 'ball_roll_ctrl'), paw_fk, 'ballRoll_ctrl', X * 4, 12, 8, 1, [0, 0, 1])
                # To accomodate how atom_placement.circle is working
                cmds.xform(ballRollCtrl[0], ws=True, ro=[0, 0, 0])

                # expose this to a varaible

                nameSample = ankleJnt.split('_')[1]
                divisionOffset = 2
                if nameSample == 'wrist':
                    divisionOffset = 1.1

                # changing the position of "ballRollCtrl" does not affect the the actual rotation of the ball roll.
                # That is a direct connection
                # doesnt work for bipeds, turned off
                # cmds.xform(ballRollCtrl, ws=True, t=[pawFkPos[0], pawFkPos[1] / divisionOffset, pawFkPos[2]])
                cmds.parent(ballRollCtrl, heelRollCtrl)
                cmds.makeIdentity(ballRollCtrl, apply=True, t=True, r=True, s=True, n=False)

                # create the base rotation group
                limb_rot_grp = cmds.group(name=misc.buildName(prefix, suffix, '_limb_rot_grp'), em=True)
                cmds.xform(limb_rot_grp, ws=True, rp=cmds.xform(paw_fk, query=True, ws=True, rp=True))
                cmds.parent(limb_rot_grp, heelRollCtrl)
                cmds.makeIdentity(limb_rot_grp, apply=True, t=True, r=True, s=True, n=False)

                # Delete the joints used to get the placment transformation
                cmds.delete(limbPlacementJnt)

                #--------------------------------------------------
                # Create the IK for the main leg and the paw digits
                #--------------------------------------------------

                ldf = cmds.floatField('atom_qls_ldf_floatField', query=True, v=True)
                locScale = cmds.floatField('atom_qls_scale_floatField', query=True, v=True)
                pawLdf = cmds.floatField('atom_paw_qls_ldf_floatField', query=True, v=True)
                dgtLocScale = cmds.floatField('atom_qls_paw_scale_floatField', query=True, value=True)

                # For some reason Maya doesnt seem to want to return all the values at the same time
                flipVal = []
                flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v1=True))
                flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v2=True))
                flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v3=True))

                aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_qls_limbAim_radioButtonGrp', query=True, sl=True))
                aimAxisList = ui.getRadioSelectionAsList('atom_qls_limbAim_radioButtonGrp')

                upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_qls_limbUp_radioButtonGrp', query=True, sl=True))
                upAxisList = ui.getRadioSelectionAsList('atom_qls_limbUp_radioButtonGrp')

                rotAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_qls_limbRot_radioButtonGrp', query=True, sl=True))
                aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_qls_limbAim_radioButtonGrp', query=True, sl=True))
                upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_qls_limbUp_radioButtonGrp', query=True, sl=True))

                digitLdf = cmds.floatField('atom_paw_qls_ldf_floatField', query=True, v=True)
                digitScale = cmds.floatField('atom_qls_paw_scale_floatField', query=True, value=True)

                # connect the rotation attributes from the pawFkCtrl
                cmds.connectAttr(pawFkCtrl[0] + '.rotate' + aimAxis, limb_rot_grp + '.rotate' + aimAxis)
                cmds.connectAttr(pawFkCtrl[0] + '.rotate' + upAxis, limb_rot_grp + '.rotate' + upAxis)

                # Create the IK from the hip to the ankle
                ankleIkh = create_ik(hipJnt, ankleJnt, prefix, suffix, limbName, None, False, setChannels)

                # Set up the Pole Vector Locator for the ankleIkh
                ankle_pv_loc = create_3_joint_pv(hipJnt, ankleJnt, prefix, suffix, limbName, 'atom_qls_limbRot_radioButtonGrp', 'atom_qls_limbAim_radioButtonGrp',
                                                 'atom_qls_limbUp_radioButtonGrp', ldf, locScale * 1, curveShapePath, True, flipVal)

                # Pole Vector Constrain the Ikh to the ankle_pv_loc
                ankle_pvc = cmds.poleVectorConstraint(ankle_pv_loc, ankleIkh[0][0])
                # return None
                # print 'before loop'
                printMeta('start digits')
                cnt = 1
                for i in range(0, len(ankleChildren), 1):
                    # check if the current child has any children, if it doesn't it's the paw_fk
                    # print 'loooping'
                    printMeta('looping digits')
                    if joint.jointTravers(ankleChildren[i], 1):
                        child = ankleChildren[i]
                        if child != vol_metacarpal:
                            name = 'digit_' + str(cnt)
                            cnt += 1

                            # sort the joints to the correct variable
                            metacarpal = child
                            proximal_phalanx = joint.jointTravers(child, 1)
                            mid_phalanx = ''
                            distal_phalanx = ''
                            end_jnt = ''
                            roll_jnt = ''
                            prox_children = cmds.listRelatives(proximal_phalanx, children=True)
                            # find the roll joint in the template rig
                            for prox_child in prox_children:
                                if cmds.listRelatives(prox_child, children=True) == None:
                                    roll_jnt = prox_child
                                else:
                                    mid_phalanx = prox_child
                            distal_phalanx = joint.jointTravers(mid_phalanx, 1)
                            end_jnt = joint.jointTravers(mid_phalanx, 2)

                            # ik[0] is the IK info which is a list of ikHandle and end effector
                            # ik[1] is the digit control
                            # ik[2] is the orient group

                            # moved pv creation above ik creation
                            # create a poleVector constraint for the metacarpal IK
                            meta_pv = cmds.spaceLocator(n=misc.buildName(prefix, '', 'pv_' + metacarpal))
                            cmds.xform(meta_pv, ws=True, t=cmds.xform(metacarpal, query=True, ws=True, rp=True),
                                       ro=cmds.xform(metacarpal, query=True, ws=True, ro=True))
                            # dont want to change the original values, so making a copy
                            meta_up = [0, 0, 0]

                            for i in range(0, len(meta_up), 1):
                                if upAxisList[i] == 1:
                                    if flipVal[i] == 1:
                                        meta_up[i] = -1
                                    else:
                                        meta_up[i] = 1

                            cmds.xform(meta_pv, os=True, r=True, t=meta_up)
                            cmds.parent(meta_pv, ankleJnt)
                            cmds.makeIdentity(meta_pv, apply=True, t=True, r=True, s=False, n=False)
                            # meta ik
                            meta_ik = create_ik(metacarpal, proximal_phalanx, prefix, suffix, 'metacarpal_' + str(cnt), None, False, setChannels)
                            printMeta('created meta ik ' + metacarpal)
                            cmds.poleVectorConstraint(meta_pv, meta_ik[0][0])

                            # digit pv first
                            pv_loc = create_3_joint_pv(proximal_phalanx, distal_phalanx, prefix, suffix, limbName, 'atom_qls_limbRot_radioButtonGrp', 'atom_qls_limbAim_radioButtonGrp',
                                                       'atom_qls_limbUp_radioButtonGrp', pawLdf, X * .8, curveShapePath, False, flipVal)
                            # digit ik after
                            ik = create_ik(proximal_phalanx, distal_phalanx, prefix, suffix, name, curveShapePath, True, setChannels, orient=False)

                            printMeta('created digit ik and pv')
                            cmds.addAttr(ik[1], longName='Tip_Vis', attributeType='long', min=0, max=1)
                            cmds.setAttr(ik[1][0] + '.Tip_Vis', cb=True)
                            ikShape = cmds.listRelatives(ik[1][0], typ='shape')[0]
                            cmds.connectAttr(sel[2] + '.MidDigit', ikShape + '.visibility')
                            pv_loc_grp = cmds.group(n=misc.buildName(prefix, suffix, name + '_pv_point_grp'), em=True, w=True)
                            cmds.xform(pv_loc_grp, ws=True, t=cmds.xform(proximal_phalanx, query=True, ws=True, rp=True))
                            #cmds.parent(pv_loc, pv_loc_grp)
                            pvShape = cmds.listRelatives(pv_loc, typ='shape')[0]
                            cmds.connectAttr(sel[2] + '.PvDigit', pvShape + '.visibility')

                            #=====Digit Creation=====#
                            digit_grp = createStandardDigit(distal_phalanx, end_jnt, prefix, suffix, 'tip_' + name, rotAxis, aimAxis, upAxis,
                                                            digitLdf, digitScale, aimAxisList, upAxisList, flipVal, True, curveShapePath)

                            printMeta('created standard digit rig')
                            cmds.connectAttr(ik[1][0] + '.Tip_Vis', digit_grp + '.visibility', force=True)
                            '''
                            baseCtrlGrp = cmds.group(n=misc.buildName(prefix, suffix, name + '_base_ctrl_grp'), em=True, w=True)
                            pivot_grp = cmds.group(n=misc.buildName(prefix, suffix, name + '_base_pivot_grp'), em=True, w=True)
                            ornt_grp = cmds.group(n=misc.buildName(prefix, suffix, name + '_base_orient_grp'), em=True, w=True)
                            '''
                            # new type, match digit orientation
                            baseCtrlGrp = place.null2(misc.buildName(prefix, suffix, name + '_base_ctrl_grp'), proximal_phalanx, orient=True)[0]
                            pivot_grp = place.null2(misc.buildName(prefix, suffix, name + '_base_pivot_grp'), proximal_phalanx, orient=True)[0]
                            ornt_grp = place.null2(misc.buildName(prefix, suffix, name + '_base_orient_grp'), proximal_phalanx, orient=True)[0]
                            #
                            baseCtrl = place.circle(misc.buildName(prefix, suffix, name + '_base_ctrl'), baseCtrlGrp, 'digitBase_ctrl', X * 3.5, 17, 8, 1, [0, 0, 1])
                            cmds.parent(pivot_grp, baseCtrlGrp)
                            cmds.parent(ornt_grp, pivot_grp)
                            cmds.parent(baseCtrl, ornt_grp)
                            cmds.xform(baseCtrlGrp, ws=True, t=cmds.xform(proximal_phalanx, query=True, ws=True, rp=True))
                            pp_rot = cmds.xform(proximal_phalanx, q=True, ws=True, ro=True)
                            baseShape = cmds.listRelatives(baseCtrl[0], typ='shape')[0]
                            cmds.connectAttr(sel[2] + '.BaseDigit', baseShape + '.visibility')
                            printMeta('created digit base')
                            #
                            # scale connection for digit
                            # '''
                            cmds.select(proximal_phalanx, hi=True)
                            digitSel = cmds.ls(sl=True)
                            i = 0
                            attrPrefix = ['base', 'mid', 'tip']
                            for jnt in digitSel:
                                if i == 3:
                                    break
                                if cmds.nodeType(jnt) == 'joint':
                                    # misc.hijackScale(jnt, baseCtrl[0])
                                    misc.optEnum(baseCtrl[0], attrPrefix[i])
                                    misc.hijackHybridScale(jnt, baseCtrl[0], lengthAttr='scaleZ', attrPrefix=attrPrefix[i])
                                i = i + 1
                            # '''
                            #
                            if cmds.xform(proximal_phalanx, q=True, ws=True, t=True)[0] < 0:
                                cmds.xform(baseCtrlGrp, ws=True, ro=[pp_rot[0] + 180, pp_rot[1], pp_rot[2]])
                            else:
                                cmds.xform(baseCtrlGrp, ws=True, ro=pp_rot)

                            printMeta('moved mystery group' + baseCtrlGrp)
                            # misc.flatten(ornt_grp)
                            misc.setChannels(ornt_grp, [True, False], [True, False], [True, False], [True, False, False])

                            # set up the roll grp,
                            jnt_roll_grp = cmds.group(name=misc.buildName(prefix, suffix, name + '_roll_grp'), em=True)
                            cmds.xform(jnt_roll_grp, ws=True, t=cmds.xform(roll_jnt, query=True, ws=True, rp=True))
                            cmds.parent(jnt_roll_grp, heelRollCtrl)
                            cmds.setAttr(jnt_roll_grp + '.tz', cmds.getAttr(jnt_roll_grp + '.tz') * ballRollOffset)
                            cmds.parent(jnt_roll_grp, baseCtrl)
                            cmds.makeIdentity(jnt_roll_grp, apply=True, t=True, r=True, s=True, n=False)
                            cmds.delete(roll_jnt)
                            misc.hijack(jnt_roll_grp, ballRollCtrl[0], rotate=False, scale=False, visibility=False)

                            printMeta('setup roll group')
                            # parent the metacarpal IK to the jnt_roll_grp
                            cmds.parent(meta_ik[0][0], jnt_roll_grp)

                            # set up the connection for the roll
                            cmds.connectAttr(ballRollCtrl[0] + '.rotate' + rotAxis, jnt_roll_grp + '.rotate' + rotAxis)

                            cmds.parent(digit_grp, baseCtrl)
                            cmds.parent(baseCtrlGrp, limb_rot_grp)
                            cmds.parent(pv_loc_grp, baseCtrl)
                            cmds.makeIdentity(pv_loc_grp, apply=True, t=True, r=True, s=False, n=False)
                            pv_loc_ornt_grp = place.null2(misc.buildName(prefix, suffix, name + '_pv_orient_grp'), pv_loc)[0]
                            cmds.parent(pv_loc_ornt_grp, pv_loc_grp)
                            misc.setChannels(pv_loc_ornt_grp, [True, False], [True, False], [True, False], [True, False, False])
                            cmds.parent(pv_loc, pv_loc_ornt_grp)
                            pvc = cmds.poleVectorConstraint(pv_loc, ik[0][0])
                            printMeta('added pv constraint for digit')
                            # ik[2] is the orient group
                            cmds.parent(ik[2], baseCtrl)
                            cmds.parentConstraint(ik[1], digit_grp, mo=True)
                            cmds.pointConstraint(proximal_phalanx, pv_loc_grp)
                            cmds.connectAttr(pawFkCtrl[0] + '.rotate' + rotAxis, pivot_grp + '.rotate' + rotAxis)
                            printMeta('end of loop')

                            if setChannels == True:
                                misc.setChannels(digit_grp, [False, False], [False, False], [True, False], [False, False, True], [True, True])
                                misc.setChannels(baseCtrlGrp, [True, False], [True, False], [True, False], [True, True, False], [True, True])
                                misc.setChannels(baseCtrl[0], [True, False], [False, True], [True, False], [True, True, False], [True, True])
                                misc.setChannels(pivot_grp, [True, False], [False, False], [True, False], [True, True, False])
                                misc.setChannels(meta_pv[0], [False, True], [True, False], [True, False], [False, False, True], [True, True])
                                misc.setChannels(pv_loc, [False, True], [True, False], [True, False], [True, True, False], [True, True])
                # print 'after loop'
                # return None
                printMeta('done digit loop')
                # Set up the hip autoAnkleParent group
                hipJntPos = cmds.xform(hipJnt, query=True, ws=True, rp=True)
                autoAnkleGrp = cmds.group(n=misc.buildName(prefix, suffix, '_auto_ankle_parent_grp'), em=True, world=True)
                cmds.xform(autoAnkleGrp, ws=True, t=hipJntPos)

                # freeze transforms
                cmds.makeIdentity(autoAnkleGrp, apply=True, t=True, r=True, s=True, n=False)

                # point and orient y the autoAnkleGrp
                cmds.pointConstraint(hipJnt, autoAnkleGrp, n=misc.buildName(prefix, suffix, '_auto_ankle_parent_grp_pntCon'))
                cmds.orientConstraint(limbCtrl_grp, autoAnkleGrp, n=misc.buildName(prefix, suffix, '_auto_ankle_parent_grp_ortCon'), mo=True, skip=('x', 'z'))

                # knee_pv_grp
                kneePvGrp = cmds.group(n=misc.buildName(prefix, suffix, '_knee_pv_grp'), em=True, world=True)
                cmds.xform(kneePvGrp, ws=True, t=cmds.xform(ankle_pv_loc, query=True, ws=True, rp=True))
                cmds.parentConstraint(limbCtrl_grp, kneePvGrp)

                # Create the control for the ankle to ball
                ankle_aim_loc = createReverseAnkle(prefix, suffix, limbName, ankleJnt, paw_fk, aimAxisList, upAxisList, flipVal, setChannels)
                ankleShape = cmds.listRelatives(ankle_aim_loc[1], typ='shape')[0]
                cmds.connectAttr(sel[2] + '.AnkleUp', ankleShape + '.visibility')
                # print 'line 1222'
                # return None
                ankleFromToeRollGrp = cmds.group(n=misc.buildName(prefix, suffix, '_ankle_fromToeRoll_grp'), em=True, world=True)
                ankleFromToeRollGrpPos = cmds.xform(paw_fk, query=True, ws=True, rp=True)
                # print 'line 1226'
                # return None
                cmds.xform(ankleFromToeRollGrp, ws=True, t=pawFkPos)
                cmds.parent(ankleFromToeRollGrp, limbCtrl_grp)
                cmds.makeIdentity(ankleFromToeRollGrp, apply=True, t=True, r=True, s=True, n=False)
                # This is a reparent, the orignal parenting is done in
                cmds.parent(ankle_aim_loc[2], ankleFromToeRollGrp)
                # print 'line 1232'
                # return None
                autoAnkleUp_loc = cmds.spaceLocator(n=misc.buildName(prefix, suffix, '_autoAnkleParent_up_loc'))

                ankleFromToeRollGrp_aim_loc = cmds.spaceLocator(n=misc.buildName(prefix, suffix, '_ankleFromToeRollGrp_aim_loc'))
                cmds.xform(ankleFromToeRollGrp_aim_loc, ws=True, t=cmds.xform(ankleJnt, query=True, ws=True, rp=True))
                cmds.parent(ankleFromToeRollGrp_aim_loc, ankleJnt)
                cmds.makeIdentity(ankleFromToeRollGrp_aim_loc, apply=True, t=True, r=True, s=True, n=False)
                # print 'line 1229'
                # return None
                goal = cmds.xform(hipJnt, query=True, ws=True, rp=True)
                stepToGoal(goal=goal, sample=0.001, obj=ankleFromToeRollGrp_aim_loc, operation='<', goalAxis=1, axis=aimAxisList, uiFlip=flipVal)
                # return None
                cmds.makeIdentity(autoAnkleUp_loc, apply=True, t=True, r=True, s=True, n=False)
                cmds.xform(autoAnkleUp_loc[0], r=True, t=[hipJntPos[0], hipJntPos[1], hipJntPos[2] + 15])
                cmds.parent(autoAnkleUp_loc, heelRollCtrl)
                # print 'line 1245'
                # return None
                ankleFromToeRollGrpAim = cmds.aimConstraint(ankleFromToeRollGrp_aim_loc, ankleFromToeRollGrp,
                                                            wuo=autoAnkleUp_loc[0], mo=True, wut='object', aim=[0, 1, 0], u=[0, 0, 1])

                ankleCtrl = cmds.circle(n=misc.buildName(prefix, suffix, limbName + '_ankle_ctrl'), ch=False, nr=(0, 1, 0), c=(0, 0, 0), s=8, d = 1)
                cmds.select(ankleCtrl)
                ui.importCurveShape('diamond_ctrl', curveShapePath, X * 4, 17)
                cmds.xform(ankleCtrl, ws=True, t=anklePos)
                cmds.parent(ankleCtrl, ankleFromToeRollGrp)
                cmds.makeIdentity(ankleCtrl, apply=True, t=True, r=True, s=True, n=False)

                # create a group for pivot the ankle from halfway between the toe tip and foot placement
                toeRollPivot_ornt_grp = cmds.group(n=misc.buildName(prefix, suffix, '_toeRollPivot_ornt_grp'), em=True, world=True)
                toeRollPivot_grp = cmds.group(n=misc.buildName(prefix, suffix, '_toeRollPivot_grp'), em=True, parent=toeRollPivot_ornt_grp)

                cmds.xform(toeRollPivot_ornt_grp, ws=True, t=toePlacementPos)
                cmds.parent(toeRollPivot_ornt_grp, heelRollCtrl)
                cmds.setAttr(toeRollPivot_ornt_grp + '.tz', cmds.getAttr(toeRollPivot_ornt_grp + '.tz') * ballRollOffset)
                cmds.connectAttr(ballRollCtrl[0] + '.rotate' + rotAxis, toeRollPivot_grp + '.rotate' + rotAxis)

                # create a group under the locator
                ankleCtrlGrp = cmds.group(n=misc.buildName(prefix, suffix, '_ankle_ctrl_grp'), em=True, parent=ankleCtrl[0])
                cmds.xform(ankleCtrlGrp, ws=True, t=cmds.xform(ankleCtrl, query=True, ws=True, rp=True))
                cmds.makeIdentity(ankleCtrlGrp, apply=True, t=True, r=True, s=True, n=False)

                ankleToToeRollGrp = cmds.group(n=misc.buildName(prefix, suffix, '_ankle_toToeRoll_grp'), em=True, world=True)
                ankleToToeRollGrpPos = cmds.xform(ankleToToeRollGrp, ws=True, t=pawFkPos)
                cmds.pointConstraint(ankleToToeRollGrp, ankleFromToeRollGrp)

                cmds.parent(ankleToToeRollGrp, toeRollPivot_grp)
                cmds.xform(ankleToToeRollGrp, ws=True, t=pawFkPos)
                cmds.parent(ankle_aim_loc[0], toeRollPivot_grp)
                cmds.makeIdentity(ankle_aim_loc[0], apply=True, t=True, r=True, s=True, n=False)
                misc.hijack(ankle_aim_loc[0], ballRollCtrl[0], rotate=False, scale=False, visibility=False)

                # create the ankleIkParentGrp
                ankleIkParentGrp = cmds.group(n=misc.buildName(prefix, suffix, '_ankleIkParent_grp'), em=True, world=True)
                cmds.xform(ankleIkParentGrp, ws=True, t=pawFkPos)
                cmds.parent(ankleIkParentGrp, toeRollPivot_grp)
                cmds.makeIdentity(ankleIkParentGrp, apply=True, t=True, r=True, s=True, n=False)
                misc.hijack(ankleIkParentGrp, ballRollCtrl[0], rotate=False, scale=False, visibility=False)

                ankleIkParent_up_loc = cmds.spaceLocator(n=misc.buildName(prefix, suffix, '_ankleIkParent_up_loc'))
                cmds.parent(ankleIkParent_up_loc, ballRollCtrl)
                cmds.xform(ankleIkParent_up_loc, ws=True, t=[pawFkPos[0], pawFkPos[1] + 1, pawFkPos[2] + 1])
                cmds.makeIdentity(ankleIkParent_up_loc, apply=True, t=True, r=True, s=True, n=False)
                cmds.aimConstraint(ankleCtrl, ankleIkParentGrp, wuo=ankleIkParent_up_loc[0], wut='object', aim=aimAxisList, u=upAxisList)
                cmds.parent(ankleIkh[0][0], ankleIkParentGrp)

                # set the rotate order
                cmds.setAttr(ankleCtrlGrp + '.rotateOrder', 2)
                cmds.setAttr(limbCtrl_grp + '.rotateOrder', 2)
                cmds.setAttr(ankle_pv_loc + '.rotateOrder', 2)
                cmds.setAttr(heelRollCtrl[0] + '.rotateOrder', 2)
                # print 'before pv rig'
                # return None
                # Rig up the reverse ankle aim constraints
                pvRig(misc.buildName(prefix, suffix, '_pv_ctrl'), 'master_Grp', hip_ctrl, ankleCtrlGrp, heelRollCtrl[0], ankle_pv_loc, kneeJnt, X * 4, sel[2], setChannels)
                # pvRig(misc.buildName(prefix, suffix, '_pv_ctrl'), 'master_Grp', hip_ctrl, ankleCtrlGrp, heelRollCtrl[0], ankle_pv_loc, kneeJnt, X * 4, sel[2], setChannels)

                cmds.setAttr(ankleToToeRollGrp + '.rotateOrder', 2)
                cmds.setAttr(ankleCtrl[0] + '.rotateOrder', 2)
                cmds.setAttr(autoAnkleUp_loc[0] + '.rotateOrder', 2)
                cmds.setAttr(ankleFromToeRollGrp_aim_loc[0] + '.rotateOrder', 2)
                ankleScaleGp = ankleTwist(misc.buildName(prefix, suffix, '_ankle_control_grp'), 'master_Grp', hip_ctrl, ankleToToeRollGrp,
                                          ankleCtrl[0], autoAnkleUp_loc, ankleFromToeRollGrp_aim_loc, setChannels)

                # scale connection
                # '''
                misc.hijackScale(ankleScaleGp, limbCtrl_grp)
                # '''
                cmds.parentConstraint(limb_ctrl, limbCtrl_grp)

                printMeta('before set channels')
                # set the channels
                if setChannels == True:
                    misc.setChannels(ballRollCtrl[0], [False, True], [False, True], [True, False], [True, False, False], [True, True])
                    cmds.setAttr(ballRollCtrl[0] + '.rotate' + aimAxis, lock=True, k=False)
                    cmds.setAttr(ballRollCtrl[0] + '.rotate' + upAxis, lock=True, k=False)
                    #cmds.setAttr(ballRollCtrl[0] + '.translate' + rotAxis, lock=True, k=False)
                    cmds.setAttr(ankleFromToeRollGrp_aim_loc[0] + '.visibility', 0)
                    misc.setChannels(pawFkCtrl[0], [True, False], [False, True], [True, False], [True, False, False], [True, True])
                    cmds.setAttr(pawFkCtrl[0] + '.rotate' + aimAxis, l=True, k=False)
                    cmds.setAttr(pawFkCtrl[0] + '.rotate' + upAxis, l=True, k=False)
                    misc.setChannels(kneePvGrp, [False, False], [False, False], [True, False], [True, False, False], [True, True])
                    misc.setChannels(autoAnkleGrp, [False, True], [False, True], [True, False], [False, False, True], [True, True])
                    misc.setChannels(autoAnkleUp_loc[0], [True, False], [True, False], [True, False], [False, True, False], [True, True])
                    misc.setChannels(ankleFromToeRollGrp, [False, False], [False, False], [True, False], [True, True, False], [True, True])
                    misc.setChannels(ankleCtrl[0], [False, True], [True, False], [True, False], [True, True, False], [True, True])
                    misc.setChannels(ankleToToeRollGrp, [True, False], [True, False], [True, False], [False, True, False], [True, True])
                    misc.setChannels(ankleIkParentGrp, [True, False], [True, False], [True, False], [False, True, False], [True, True])
                    misc.setChannels(ankleIkParent_up_loc[0], [True, False], [True, False], [True, False], [False, True, False], [True, True])
                    misc.setChannels(limb_rot_grp, [True, False], [False, False], [True, False], [True, False, False])
                    misc.setChannels(heelRollCtrl[0], [True, False], [False, True], [True, False], [True, True, False])
                    cmds.setAttr(heelRollCtrl[0] + '.rx', l=True)
                    cmds.setAttr(heelRollCtrl[0] + '.rx', k=False)
                    misc.setChannels(toeRollCtrl[0], [True, False], [False, True], [True, False], [True, True, False])
                    cmds.setAttr(toeRollCtrl[0] + '.rx', l=True)
                    cmds.setAttr(toeRollCtrl[0] + '.rx', k=False)
                    misc.setChannels(ankle_pv_loc, [False, True], [True, False], [True, False], [True, True, False])
                    misc.setChannels(ankle_aim_loc[2], [True, False], [True, False], [True, False], [True, True, False], [True, True])
                    misc.setChannels(ankle_aim_loc[1], [False, True], [True, False], [True, False], [True, True, False], [True, True])
                    misc.setChannels(ankle_aim_loc[0], [False, False], [True, False], [True, False], [False, True, False], [True, True])
                printMeta('after set channels')
            else:
                OpenMaya.MGlobal.displayError('A joint isn\'t selected...joints make skeletons...select a joint')
        else:
            OpenMaya.MGlobal.displayError('Atom Window not found...open the damn Atom UI(User Interface) to make some magic...')
    else:
        OpenMaya.MGlobal.displayError('Nothing is selected, are you qualified to use this tool?')


def create3jointIK(control):
    sel = cmds.ls(sl=True)
    if len(sel) != 0:
        if cmds.window('atom_win', ex=True):
            if cmds.nodeType(sel[0]) == 'joint':
                setChannels = None
                curveShapePath = cmds.textField('atom_csst_exportPath_textField', query=True, text=True)
                checkValue = cmds.checkBox(control, query=True, v=True)
                if checkValue == 0:
                    setChannels = False
                else:
                    setChannels = True

                for child in sel:
                    shoulderJnt = child
                    elbowJnt = joint.jointTravers(shoulderJnt, 1)
                    wristJnt = joint.jointTravers(shoulderJnt, 2)

                    prefix = cmds.textField('atom_prefix_textField', query=True, tx=True)
                    suffix = cmds.optionMenu('atom_suffix_optionMenu', query=True, v=True)
                    limbName = cmds.optionMenu('atom_bls_limb_optionMenu', query=True, v=True)
                    if suffix == 'none':
                        suffix = ''
                    if limbName == 'none':
                        limbName = ''

                    wristPos = cmds.xform(wristJnt, query=True, ws=True, rp=True)

                    #--------------------------------------------------
                    # Create the IK for the main leg and the paw digits
                    #--------------------------------------------------

                    rotAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbRot_radioButtonGrp', query=True, sl=True))
                    aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbAim_radioButtonGrp', query=True, sl=True))
                    upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbUp_radioButtonGrp', query=True, sl=True))
                    ldf = cmds.floatField('atom_bls_ldf_floatField', query=True, v=True)
                    locScale = cmds.floatField('atom_bls_scale_floatField', query=True, v=True)

                    # For some reason Maya doesnt seem to want to return all the values at the same time
                    flipVal = []
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v1=True))
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v2=True))
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v3=True))

                    aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbAim_radioButtonGrp', query=True, sl=True))
                    aimAxisList = ui.getRadioSelectionAsList('atom_bls_limbAim_radioButtonGrp')

                    upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbUp_radioButtonGrp', query=True, sl=True))
                    upAxisList = ui.getRadioSelectionAsList('atom_bls_limbUp_radioButtonGrp')
                    wristIkh = create_ik(shoulderJnt, wristJnt, prefix, suffix, limbName, False, setChannels)

                    # flipVal is based on a joint orientation of x rotation, y up and z down the bone. To flip the location of the of the
                    # poleVector spaceLocator x and z need to be flipped.
                    wrist_pv_loc = create_3_joint_pv(shoulderJnt, wristJnt, prefix, suffix, limbName, 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                                     'atom_bls_limbUp_radioButtonGrp', ldf, locScale, curveShapePath, True, flipVal)
                    wrist_pvc = cmds.poleVectorConstraint(wrist_pv_loc, wristIkh[0][0])

                    # set the channels
                    if setChannels == True:
                        misc.setChannels(wrist_pv_loc, [False, False], [True, True], [True, True], [False, True, True], [True, True])

        else:
            OpenMaya.MGlobal.displayError('Atom Window not found...open the damn Atom UI(User Interface) to make some magic...')
    else:
        OpenMaya.MGlobal.displayError('Nothing is selected, are you qualified to use this tool?')


def createDigitCMD(control):
    sel = cmds.ls(sl=True)
    if len(sel) != 0:
        if cmds.window('atom_win', ex=True):
            if cmds.nodeType(sel[0]) == 'joint':
                setChannels = None
                checkValue = cmds.checkBox(control, query=True, v=True)
                if checkValue == 0:
                    setChannels = False
                else:
                    setChannels = True

                for child in sel:
                    firstDigit = child
                    endDigit = joint.jointTravers(firstDigit, 1)

                    prefix = cmds.textField('atom_prefix_textField', query=True, tx=True)
                    suffix = cmds.optionMenu('atom_suffix_optionMenu', query=True, v=True)
                    limbName = cmds.optionMenu('atom_bls_limb_optionMenu', query=True, v=True)
                    if suffix == 'none':
                        suffix = ''
                    if limbName == 'none':
                        limbName = ''

                    #--------------------------------------------------
                    # Create the IK for the main leg and the paw digits
                    #--------------------------------------------------

                    rotAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbRot_radioButtonGrp', query=True, sl=True))
                    aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbAim_radioButtonGrp', query=True, sl=True))
                    upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbUp_radioButtonGrp', query=True, sl=True))
                    ldf = cmds.floatField('atom_bls_ldf_floatField', query=True, v=True)
                    locScale = cmds.floatField('atom_bls_scale_floatField', query=True, v=True)

                    # For some reason Maya doesnt seem to want to return all the values at the same time
                    flipVal = []
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v1=True))
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v2=True))
                    flipVal.append(1 * cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', query=True, v3=True))

                    aimAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbAim_radioButtonGrp', query=True, sl=True))
                    aimAxisList = ui.getRadioSelectionAsList('atom_bls_limbAim_radioButtonGrp')

                    upAxis = ui.convertAxisNum(cmds.radioButtonGrp('atom_bls_limbUp_radioButtonGrp', query=True, sl=True))
                    upAxisList = ui.getRadioSelectionAsList('atom_bls_limbUp_radioButtonGrp')

                    # flipVal is based on a joint orientation of x rotation, y up and z down the bone. To flip the location of the of the
                    # poleVector spaceLocator x and z need to be flipped.
                    digit_grp = createStandardDigit(firstDigit, endDigit, prefix, suffix, 'tip_', rotAxis, aimAxis, upAxis,
                                                    ldf, locScale, aimAxisList, upAxisList, flipVal, setChannels)

        else:
            OpenMaya.MGlobal.displayError('Atom Window not found...open the damn Atom UI(User Interface) to make some magic...')
    else:
        OpenMaya.MGlobal.displayError('Nothing is selected, are you qualified to use this tool?')

# parent the joints


def parentForarmRigJoints(parent, name, suffix):
    for i in range(1, 4, 1):
        jnt = '%s_%02d_jnt_%s' % (name, i, suffix)
        if cmds.objExists(jnt):
            if cmds.listRelatives(jnt, parent=True) == None:
                cmds.parent(jnt, parent)


def createForarmTwistRig(suffixList, w=0.5):
    for side in suffixList:
        parentForarmRigJoints('front_lower_knee_jnt_%s' % side, 'front_twist', side)

        cmds.parent('front_radius_jnt_%s' % side, 'front_ankle_jnt_%s' % side)
        ik = cmds.ikHandle(sj='front_radius_jnt_%s' % side, ee='front_radius_end_jnt_%s' % side)
        cmds.parent(ik[0], 'front_lower_knee_jnt_%s' % side)

        loc = 'front_twist_aim_jnt_%s' % side
        ctrl = place.Controller('twist_control_%s' % side, loc, color=12, size=1, shape='facetYup_ctrl', orient=True, groups=True)
        ctrl_group = ctrl.createController()

        cmds.parentConstraint(loc, ctrl_group[0], mo=True)
        if side == 'L':
            cmds.aimConstraint('front_ankle_jnt_%s' % side, 'front_twist_03_jnt_%s' % side,
                               wuo=ctrl_group[4], wut='object', u=[1, 0, 0], aim=[0, 0, 1], mo=True)
        else:
            cmds.aimConstraint('front_ankle_jnt_%s' % side, 'front_twist_03_jnt_%s' % side,
                               wuo=ctrl_group[4], wut='object', u=[-1, 0, 0], aim=[0, 0, -1], mo=True)

        # front_twist_aim_loc_L
        rootMd = cmds.createNode('multiplyDivide', name='root_twist_MD_%s' % side)
        cmds.setAttr(rootMd + '.input2Z', w)
        midMd = cmds.createNode('multiplyDivide', name='root_mid_MD_%s' % side)
        cmds.setAttr(midMd + '.input2Z', w)

        # make the connections
        cmds.connectAttr('front_twist_03_jnt_%s.rotateZ' % side, rootMd + '.input1Z')
        cmds.connectAttr(rootMd + '.outputZ', 'front_twist_02_jnt_%s.rotateZ' % side)

        cmds.connectAttr('front_twist_02_jnt_%s.rotateZ' % side, midMd + '.input1Z')
        cmds.connectAttr(midMd + '.outputZ', 'front_twist_01_jnt_%s.rotateZ' % side)

        misc.cleanUp(ctrl_group[0], Ctrl=True)
        misc.setChannels(ctrl_group[2], [False, True], [True, False], [True, False], [True, False, False], [True, True])
        misc.setChannels(ctrl_group[3], [False, True], [True, False], [True, False], [True, True, False], [True, True])


def createThighTwistRig(suffixList, w=-0.75):
    for side in suffixList:
        parentForarmRigJoints('back_hip_jnt_%s' % side, 'back_twist', side)

        # front_twist_aim_loc_L
        rootMd = cmds.createNode('multiplyDivide', name='back_twist_MD_%s' % side)
        cmds.setAttr(rootMd + '.input2Z', w)

        # make the connections
        cmds.connectAttr('back_hip_jnt_%s.rotateZ' % side, rootMd + '.input1Z')
        cmds.connectAttr(rootMd + '.outputZ', 'back_twist_01_jnt_%s.rotateZ' % side)


def createDeltTwistRig(suffixList, w=-0.75):
    for side in suffixList:
        parentForarmRigJoints('front_shoulder_jnt_%s' % side, 'delt_twist', side)

        # front_twist_aim_loc_L
        rootMd = cmds.createNode('multiplyDivide', name='delt_twist_MD_%s' % side)
        cmds.setAttr(rootMd + '.input2Z', w)

        # make the connections
        cmds.connectAttr('front_shoulder_jnt_%s.rotateZ' % side, rootMd + '.input1Z')
        cmds.connectAttr(rootMd + '.outputZ', 'delt_twist_01_jnt_%s.rotateZ' % side)


def createButtVolumeRig(suffixList, w=0.1):
    for side in suffixList:
        parentForarmRigJoints('back_hip_jnt_%s' % side, 'butt_twist', side)

        # front_twist_aim_loc_L
        rootMd = cmds.createNode('multiplyDivide', name='butt_volume_MD_%s' % side)
        cmds.setAttr(rootMd + '.input2X', w)
        cmds.setAttr(rootMd + '.input2Y', w)
        cmds.setAttr(rootMd + '.input2Z', w)

        # make the connections
        cmds.connectAttr('back_hip_jnt_%s.rotateX' % side, rootMd + '.input1X')
        cmds.connectAttr(rootMd + '.outputX', 'butt_volume_01_jnt_%s.rotateX' % side)
        #
        cmds.connectAttr('back_hip_jnt_%s.rotateY' % side, rootMd + '.input1Y')
        cmds.connectAttr(rootMd + '.outputY', 'butt_volume_01_jnt_%s.rotateY' % side)
        #
        cmds.connectAttr('back_hip_jnt_%s.rotateZ' % side, rootMd + '.input1Z')
        cmds.connectAttr(rootMd + '.outputZ', 'butt_volume_01_jnt_%s.rotateZ' % side)


def createDeltVolumeRig(suffixList, w=0.25):
    for side in suffixList:
        parentForarmRigJoints('front_shoulder_jnt_%s' % side, 'delt_twist', side)

        # front_twist_aim_loc_L
        rootMd = cmds.createNode('multiplyDivide', name='delt_volume_MD_%s' % side)
        cmds.setAttr(rootMd + '.input2X', w)
        cmds.setAttr(rootMd + '.input2Y', w)
        cmds.setAttr(rootMd + '.input2Z', w)

        # make the connections
        cmds.connectAttr('front_shoulder_jnt_%s.rotateX' % side, rootMd + '.input1X')
        cmds.connectAttr(rootMd + '.outputX', 'delt_volume_jnt_%s.rotateX' % side)
        #
        cmds.connectAttr('front_shoulder_jnt_%s.rotateY' % side, rootMd + '.input1Y')
        cmds.connectAttr(rootMd + '.outputY', 'delt_volume_jnt_%s.rotateY' % side)
        #
        cmds.connectAttr('front_shoulder_jnt_%s.rotateZ' % side, rootMd + '.input1Z')
        cmds.connectAttr(rootMd + '.outputZ', 'delt_volume_jnt_%s.rotateZ' % side)


def splitPivot(pseudoRoot='front_pseudo_ankle_root_jnt_L', attach='front_ankle_jnt_L', aimUp='front_lower_knee_jnt_L', aimDown='front_paw_Fk_jnt_L'):
    '''
        arguements are joints\n
    all joints need to exist, and be oriented correctly\n
        '''
    # pymel nodes
    pseudoAnkleRoot = PyNode(pseudoRoot)
    pseudoAnkle = pseudoAnkleRoot.getChildren()[0]
    tmp = pseudoAnkle.getChildren()
    attach = PyNode(attach)
    aimUp = PyNode(aimUp)
    aimDown = PyNode(aimDown)
    upperAnkleRoot = None
    upperAnkle = None
    lowerAnkleRoot = None
    lowerAnkle = None
    upperAnkleUp = None
    lowerAnkleUp = None
    for item in tmp:
        if 'upper_ankle_root' in item.name():
            upperAnkleRoot = item
            upperAnkle = upperAnkleRoot.getChildren()[0]
        elif 'lower_ankle_root' in item.name():
            lowerAnkleRoot = item
            lowerAnkle = lowerAnkleRoot.getChildren()[0]
        elif 'upper_ankle_up' in item.name():
            upperAnkleUp = item
        elif 'lower_ankle_up' in item.name():
            lowerAnkleUp = item
    # pseudo ankle
    cmds.parentConstraint(aimUp.name(), pseudoAnkleRoot.name(), mo=True)
    mltp = cmds.shadingNode('multiplyDivide', au=True, n=('ankleRot' + '_reduce'))
    # set operation: 2 = divide, 1 = multiply
    cmds.setAttr((mltp + '.operation'), 1)
    # set 2nd input of multi to 0.5
    x = 0.5
    cmds.setAttr('%s.input2' % mltp, x, x, x)
    # output of ankle rotate to multi node 1st input
    cmds.connectAttr("%s.rotate" % (attach.name()), "%s.input1" % (mltp), f=True)
    # result to pseudo ankle rotate
    cmds.connectAttr("%s.output" % (mltp), "%s.rotate" % (pseudoAnkle.name()), f=True)
    # Controllers
    # ...in time
    # upper ankle
    cmds.aimConstraint(aimUp.name(), upperAnkle.name(),
                       mo=True,
                       aimVector=(0, 0, 1),
                       upVector=(0, 1, 0),
                       worldUpType='object',
                       worldUpObject=upperAnkleUp.name())
    # lower ankle
    cmds.aimConstraint(aimDown.name(), lowerAnkle.name(),
                       mo=True,
                       aimVector=(0, 0, 1),
                       upVector=(0, 1, 0),
                       worldUpType='object',
                       worldUpObject=lowerAnkleUp.name())


def ikStretch(obj, rootJnt, rootCt, tipCt, percent=100):
    '''\n
    assumes translateZ is the aim vector for the joints\n
    obj = to recieve stretch attr\n
    rootJnt = root joint of 3 jnt chain with ik connected\n
    rootCt = controller or group at root of ik\n
    tipCt = controller or group at end effector position\n
    percent = range of movement (ie. 100= fully extends, 0= locks up at current position)\n
    percent: anything below zero will unstick the tip joint form the controller...should be adressed\n
    '''
    name = obj
    attr = 'autoStretch'
    root = rootJnt
    mid = cmds.listRelatives(root, typ='joint', c=True)[0]
    tip = cmds.listRelatives(mid, typ='joint', c=True)[0]
    rootTZ = cmds.getAttr(root + '.tz')
    midTZ = cmds.getAttr(mid + '.tz')
    tipTZ = cmds.getAttr(tip + '.tz')
    value = cmds.getAttr(mid + '.tz') + cmds.getAttr(tip + '.tz')

    # hook up joints to distance
    # distance nodes
    dis = cmds.createNode('distanceBetween', name=name + '_dis')
    rootLoc = place.loc(name + '_rootLoc', root)[0]
    cmds.pointConstraint(root, rootLoc, mo=False)
    tipLoc = place.loc(name + '_tipLoc', tip)[0]
    cmds.pointConstraint(tipCt, tipLoc, mo=False)
    locGrp = cmds.group(name=name + '_LocGrp', em=True)
    cmds.setAttr(locGrp + '.visibility', 0)
    cmds.parent(rootLoc, locGrp)
    cmds.parent(tipLoc, locGrp)
    misc.cleanUp(locGrp, World=True)
    cmds.connectAttr(rootLoc + '.worldPosition[0]', dis + '.point1')
    cmds.connectAttr(tipLoc + '.worldPosition[0]', dis + '.point2')
    # clamp node
    clmp = cmds.shadingNode('clamp', asUtility=True, name=name + '_clmp')
    cmds.setAttr(clmp + '.minR', value)
    # cnnct distance clamp
    cmds.connectAttr(dis + '.distance', clmp + '.inputR')

    # create/connect stretch attr
    limit = 100
    misc.addAttribute(name, attr, 0, limit, True, 'float')
    cmds.setAttr(name + '.' + attr, limit)
    adl = cmds.createNode('addDoubleLinear', name='_adl')
    cmds.setAttr(adl + '.input2', value)
    cmds.connectAttr(name + '.' + attr, adl + '.input1')
    # connect adl to clmp
    cmds.connectAttr(adl + '.output', clmp + '.maxR')

    # divide node
    div = cmds.createNode('multiplyDivide', name=name + '_div')
    cmds.setAttr(div + '.operation', 2)
    cmds.setAttr(div + '.input2X', value)
    cmds.connectAttr(clmp + '.outputR', div + '.input1X')

    # mid translate stretch value / connect
    midSt_mlt = cmds.createNode('multiplyDivide', name=name + '_midStretchMlt')
    cmds.setAttr(midSt_mlt + '.input2X', midTZ)
    cmds.connectAttr(div + '.outputX', midSt_mlt + '.input1X')
    cmds.connectAttr(midSt_mlt + '.outputX', mid + '.tz')

    # tip translate stretch value / connect
    tipSt_mlt = cmds.createNode('multiplyDivide', name=name + '_tipStretchMlt')
    cmds.setAttr(tipSt_mlt + '.input2X', tipTZ)
    cmds.connectAttr(div + '.outputX', tipSt_mlt + '.input1X')
    cmds.connectAttr(tipSt_mlt + '.outputX', tip + '.tz')

    # set percent of rotation limit
    joint.ikJntRange(mid, percent)


def createBoneScale(name='', joint='', control=None, lengthAttr='scaleZ', newAttr='', unified=False):
    '''
    name = if control is None this string is used for the new control
    joint = joint to get scale setup
    control = to recieve attrs for control, if None, control is created on joint location and constrained
    lengthAttr = scale axis to be used as length, remaining get girth behaviour
    '''
    if not control:
        ctrl = place.Controller(name, joint, color=12, size=1, shape='loc_ctrl', orient=True, groups=True)
        scaleCt = ctrl.createController()
        cmds.parentConstraint(joint, scaleCt[0])
        control = scaleCt[1]
        misc.setChannels(control, translate=[False, False], rotate=[False, False], scale=[False, False], visibility=[True, False, True], other=[False, True])
    misc.optEnum(control, attr='Scale')
    if unified:
        misc.hijackAttrs(joint, control, 'scaleX', newAttr, set=False, default=None)
        misc.hijackAttrs(joint, control, 'scaleY', newAttr, set=False, default=None)
        misc.hijackAttrs(joint, control, 'scaleZ', newAttr, set=False, default=None)
    else:
        misc.hijackHybridScale(joint, control, lengthAttr)


def printMeta(mes=''):
    meta = 'front_mid_phal_jnt_03_L'
    print cmds.xform(meta, q=True, ro=True), '____ ' + mes + ' ____'
