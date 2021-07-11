import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )


def hexapod( *args ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 12 )

    # lists for joints and controllers

    endJntL = ['front_leg_end_jnt_L', 'mid_leg_end_jnt_L', 'back_leg_end_jnt_L']
    endJntR = ['front_leg_end_jnt_R', 'mid_leg_end_jnt_R', 'back_leg_end_jnt_R']
    kneeJntL = ['front_knee_jnt_L', 'mid_knee_jnt_L', 'back_knee_jnt_L']
    kneeJntR = ['front_knee_jnt_R', 'mid_knee_jnt_R', 'back_knee_jnt_R']
    legJntL = ['front_leg_jnt_L', 'mid_leg_jnt_L', 'back_leg_jnt_L']
    legJntR = ['front_leg_jnt_R', 'mid_leg_jnt_R', 'back_leg_jnt_R']

    btmCtrl_L = ['front_L', 'mid_L', 'back_L']
    btmCtrl_R = ['front_R', 'mid_R', 'back_R']
    topCtrl_L = ['frontTop_L', 'midTop_L', 'backTop_L']
    topCtrl_R = ['frontTop_R', 'midTop_R', 'backTop_R']

    pvNamesL = ['front_pv_L', 'mid_pv_L', 'back_pv_L']
    pvNamesR = ['front_pv_R', 'mid_pv_R', 'back_pv_R']
    ikNamesL = ['frontIk_L', 'midIK_L', 'backIk_L']
    ikNamesR = ['frontIk_R', 'midIk_R', 'backIk_R']

    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    # Create COG Controller and clean up

    cnt = place.Controller( 'COG', 'root_jnt', orient = False, shape = 'facetZup_ctrl', size = 5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
    cmds.parentConstraint( 'COG', 'root_jnt', mo = True )

    # LeftSide of Rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsL = []
    for jnt in endJntL:
        cnt = place.Controller( btmCtrl_L[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 1, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsL.append( cntCt[4] )
        i = i + 1
    print( 'catch baseGrpsL:' )
    print( baseGrpsL )

    i = 0
    scktGrpsL = []
    for jnt in legJntL:
        cnt = place.Controller( topCtrl_L[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.5, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'COG', cntCt[0], mo = True )
        scktGrpsL.append( cntCt[4] )
        i = i + 1
    print( 'catch scktGrpsL:' )
    print( scktGrpsL )

    # Rightside of rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsR = []
    for jnt in endJntR:
        cnt = place.Controller( btmCtrl_R[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 1, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsR.append( cntCt[4] )
        i = i + 1
    print( 'catch baseGrpsR:' )
    print( baseGrpsR )

    i = 0
    scktGrpsR = []
    for jnt in legJntR:
        cnt = place.Controller( topCtrl_R[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.5, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'COG', cntCt[0], mo = True )
        scktGrpsR.append( cntCt[4] )
        i = i + 1
    print( 'catch scktGrpsR:' )
    print( scktGrpsR )

    # create PoleVectors, place and clean up into groups

    # LeftSide of Rig

    curveShapePath = '/home/sweber/key_local_tool_development/key_base/3d/maya/python/atom/control_shape_templates'

    i = 0
    pvLocListL = []
    for jnt in legJntL:
        pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', 1.5, 0.2, curveShapePath, True, flipVar = [0, 0, 0] )
        pvLocListL.append( pvLoc )
        place.cleanUp( pvLocListL[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    print( 'catch pvLocListL:' )
    print( pvLocListL )

    # RightSide of Rig

    i = 0
    pvLocListR = []
    for jnt in legJntR:
        pvLoc = appendage.create_3_joint_pv( jnt, endJntR[i], 'pv', 'R', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', -1.5, 0.2, curveShapePath, True, flipVar = [0, 1, 1] )
        pvLocListR.append( pvLoc )
        place.cleanUp( pvLocListR[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    print( 'catch pvLocListR:' )
    print( pvLocListR )

    # Creates poleVector Rig for appendages
    """
    creates pole vector rig
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
    i = 0
    for cnt in btmCtrl_L:
        appendage.pvRig( pvNamesL[i], 'master_Grp', scktGrpsL[i], baseGrpsL[i], baseGrpsL[i], pvLocListL[i], kneeJntL[i], .1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
        i = i + 1

    i = 0
    for cnt in btmCtrl_R:
        appendage.pvRig( pvNamesR[i], 'master_Grp', scktGrpsR[i], baseGrpsR[i], baseGrpsR[i], pvLocListR[i], kneeJntR[i], .1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
        i = i + 1

    place.cleanUp( 'GuideGp', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # Create an ik handle from TopJoint to end effector

    i = 0
    for jnt in legJntL:
        cmds.ikHandle( n = ikNamesL[i], sj = jnt, ee = endJntL[i], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListL[i], ikNamesL[i] )
        cmds.setAttr( ikNamesL[i] + '.visibility', 0 )
        cmds.parent( ikNamesL[i], baseGrpsL[i] )
        i = i + 1
    i = 0
    for jnt in legJntR:
        cmds.ikHandle( n = ikNamesR[i], sj = jnt, ee = endJntR[i], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListR[i], ikNamesR[i] )
        cmds.setAttr( ikNamesR[i] + '.visibility', 0 )
        cmds.parent( ikNamesR[i], baseGrpsR[i] )
        i = i + 1

    # cleanup of root_jnt and body_Geo

    place.cleanUp( 'root_jnt', Ctrl = False, SknJnts = True, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    place.cleanUp( 'body_Geo', Ctrl = False, SknJnts = False, Body = True, Accessory = False, Utility = False, World = False, olSkool = False )
