import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )


def cattr( *args ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 10 )

    # lists for joints and controllers
    endJntL = [
    'leg_01_End_jnt_L',
    'leg_02_End_jnt_L',
    'leg_03_End_jnt_L',
    'leg_04_End_jnt_L',
    'leg_05_End_jnt_L',
    'leg_06_End_jnt_L',
    'leg_07_End_jnt_L',
    'leg_08_End_jnt_L'
    ]
    endJntR = [
    'leg_01_End_jnt_R',
    'leg_02_End_jnt_R',
    'leg_03_End_jnt_R',
    'leg_04_End_jnt_R',
    'leg_05_End_jnt_R',
    'leg_06_End_jnt_R',
    'leg_07_End_jnt_R',
    'leg_08_End_jnt_R'
    ]
    kneeJntL = [
    'leg_01_Mid2_jnt_L',
    'leg_02_Mid2_jnt_L',
    'leg_03_Mid2_jnt_L',
    'leg_04_Mid2_jnt_L',
    'leg_05_Mid2_jnt_L',
    'leg_06_Mid2_jnt_L',
    'leg_07_Mid2_jnt_L',
    'leg_08_Mid2_jnt_L'
    ]
    kneeJntR = [
    'leg_01_Mid2_jnt_R',
    'leg_02_Mid2_jnt_R',
    'leg_03_Mid2_jnt_R',
    'leg_04_Mid2_jnt_R',
    'leg_05_Mid2_jnt_R',
    'leg_06_Mid2_jnt_R',
    'leg_07_Mid2_jnt_R',
    'leg_08_Mid2_jnt_R'
    ]
    legJntL = [
    'leg_01_Base_jnt_L',
    'leg_02_Base_jnt_L',
    'leg_03_Base_jnt_L',
    'leg_04_Base_jnt_L',
    'leg_05_Base_jnt_L',
    'leg_06_Base_jnt_L',
    'leg_07_Base_jnt_L',
    'leg_08_Base_jnt_L'
    ]
    legJntR = [
    'leg_01_Base_jnt_R',
    'leg_02_Base_jnt_R',
    'leg_03_Base_jnt_R',
    'leg_04_Base_jnt_R',
    'leg_05_Base_jnt_R',
    'leg_06_Base_jnt_R',
    'leg_07_Base_jnt_R',
    'leg_08_Base_jnt_R'
    ]

    btmCtrl_L = [
    'leg_01_Ct_L',
    'leg_02_Ct_L',
    'leg_03_Ct_L',
    'leg_04_Ct_L',
    'leg_05_Ct_L',
    'leg_06_Ct_L',
    'leg_07_Ct_L',
    'leg_08_Ct_L'
    ]
    btmCtrl_R = [
    'leg_01_Ct_R',
    'leg_02_Ct_R',
    'leg_03_Ct_R',
    'leg_04_Ct_R',
    'leg_05_Ct_R',
    'leg_06_Ct_R',
    'leg_07_Ct_R',
    'leg_08_Ct_R'
    ]
    topCtrl_L = [
    'legTop_01_Ct_L',
    'legTop_02_Ct_L',
    'legTop_03_Ct_L',
    'legTop_04_Ct_L',
    'legTop_05_Ct_L',
    'legTop_06_Ct_L',
    'legTop_07_Ct_L',
    'legTop_08_Ct_L'
    ]
    topCtrl_R = [
    'legTop_01_Ct_R',
    'legTop_02_Ct_R',
    'legTop_03_Ct_R',
    'legTop_04_Ct_R',
    'legTop_05_Ct_R',
    'legTop_06_Ct_R',
    'legTop_07_Ct_R',
    'legTop_08_Ct_R'
    ]

    pvNamesL = [
    'legPv_01_Ct_L',
    'legPv_02_Ct_L',
    'legPv_03_Ct_L',
    'legPv_04_Ct_L',
    'legPv_05_Ct_L',
    'legPv_06_Ct_L',
    'legPv_07_Ct_L',
    'legPv_08_Ct_L'
    ]
    pvNamesR = [
    'legPv_01_Ct_R',
    'legPv_02_Ct_R',
    'legPv_03_Ct_R',
    'legPv_04_Ct_R',
    'legPv_05_Ct_R',
    'legPv_06_Ct_R',
    'legPv_07_Ct_R',
    'legPv_08_Ct_R'
    ]
    ikNamesL = [
    'legIk_01_Ct_L',
    'legIk_02_Ct_L',
    'legIk_03_Ct_L',
    'legIk_04_Ct_L',
    'legIk_05_Ct_L',
    'legIk_06_Ct_L',
    'legIk_07_Ct_L',
    'legIk_08_Ct_L'
    ]
    ikNamesR = [
    'legIk_01_Ct_R',
    'legIk_02_Ct_R',
    'legIk_03_Ct_R',
    'legIk_04_Ct_R',
    'legIk_05_Ct_R',
    'legIk_06_Ct_R',
    'legIk_07_Ct_R',
    'legIk_08_Ct_R'
    ]
    legParents = [
    'head_jnt_04',
    'head_jnt_03',
    'head_jnt_02',
    'spine_jnt_04',
    'spine_jnt_05',
    'spine_jnt_06',
    'spine_jnt_07',
    'tail_jnt_04'
    ]
    geo = 'caterpillar_c_geo_lod_0'
    cmds.deltaMush( geo, smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    # Create COG Controller and clean up
    cog = 'Cog'
    cnt = place.Controller( cog, 'root_jnt', orient = False, shape = 'facetZup_ctrl', size = 4.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
    cmds.parentConstraint( cntCt[4], 'root_jnt', mo = True )

    chest = 'Chest'
    chst = place.Controller( chest, 'spine_jnt_01', orient = False, shape = 'facetZup_ctrl', size = 3, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    chstCt = chst.createController()
    place.cleanUp( chstCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], chstCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    pelvis = 'Pelvis'
    plvs = place.Controller( pelvis, 'spine_jnt_07', orient = False, shape = 'facetZup_ctrl', size = 2.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    plvsCt = plvs.createController()
    place.cleanUp( plvsCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], plvsCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    neck = 'Neck'
    nck = place.Controller( neck, 'head_jnt_01', orient = False, shape = 'facetZup_ctrl', size = 2.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    nckCt = nck.createController()
    place.cleanUp( nckCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'spine_jnt_01', nckCt[0], mo = True )

    head = 'Head'
    hd = place.Controller( head, 'head_jnt_05', orient = False, shape = 'facetZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    hdCt = hd.createController()
    place.cleanUp( hdCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], hdCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    tail = 'Tail'
    tl = place.Controller( tail, 'tail_jnt_05', orient = False, shape = 'facetZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    tlCt = tl.createController()
    place.cleanUp( tlCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], tlCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    # LeftSide of Rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsL = []
    for jnt in endJntL:
        cnt = place.Controller( btmCtrl_L[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
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
    # print 'catch baseGrpsL:'
    # print baseGrpsL

    i = 0
    scktGrpsL = []
    for jnt in legJntL:
        cnt = place.Controller( topCtrl_L[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.25, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( legParents[i], cntCt[0], mo = True )
        cmds.parentConstraint( cntCt[4], jnt, mo = True )
        scktGrpsL.append( cntCt[4] )
        i = i + 1
    # print 'catch scktGrpsL:'
    # print scktGrpsL

    # Rightside of rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsR = []
    for jnt in endJntR:
        cnt = place.Controller( btmCtrl_R[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
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
    # print 'catch baseGrpsR:'
    # print baseGrpsR

    i = 0
    scktGrpsR = []
    for jnt in legJntR:
        cnt = place.Controller( topCtrl_R[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.25, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( legParents[i], cntCt[0], mo = True )
        cmds.parentConstraint( cntCt[4], jnt, mo = True )
        scktGrpsR.append( cntCt[4] )
        i = i + 1
    # print 'catch scktGrpsR:'
    # print scktGrpsR

    # create PoleVectors, place and clean up into groups

    # LeftSide of Rig

    curveShapePath = 'C:\\Users\\sebas\\Documents\\maya\\controlShapes'

    i = 0
    pvLocListL = []
    for jnt in legJntL:
        pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', 1.0, 0.2, curveShapePath, True, flipVar = [0, 0, 0], X = 0.05 )
        pvLocListL.append( pvLoc )
        place.cleanUp( pvLocListL[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # print 'catch pvLocListL:'
    # print pvLocListL

    # RightSide of Rig

    i = 0
    pvLocListR = []
    for jnt in legJntR:
        pvLoc = appendage.create_3_joint_pv( jnt, endJntR[i], 'pv', 'R', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', -1.0, 0.2, curveShapePath, True, flipVar = [0, 1, 1], X = 0.05 )
        pvLocListR.append( pvLoc )
        place.cleanUp( pvLocListR[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # print 'catch pvLocListR:'
    # print pvLocListR

    # Creates poleVector Rig for appendages
    """
    creates pole vector rig
    \n*
    name      = name
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
        appendage.pvRig( pvNamesL[i], 'master_Grp', scktGrpsL[i], baseGrpsL[i], baseGrpsL[i], pvLocListL[i], kneeJntL[i], 0.1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
        i = i + 1

    i = 0
    for cnt in btmCtrl_R:
        appendage.pvRig( pvNamesR[i], 'master_Grp', scktGrpsR[i], baseGrpsR[i], baseGrpsR[i], pvLocListR[i], kneeJntR[i], 0.1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
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
    place.cleanUp( geo, Ctrl = False, SknJnts = False, Body = True, Accessory = False, Utility = False, World = False, olSkool = False )
    # place.cleanUp( 'subdiv', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = True, World = False, olSkool = False )
    #
    buildSplines()

    # have to run last cuz consraint node parent under spine joint breaks spline build
    '''
    i = 0
    for jnt in legParents:
        cmds.parentConstraint( jnt, legJntL[i], mo = True )
        cmds.parentConstraint( jnt, legJntR[i], mo = True )
        i = i + 1'''


def buildSplines( *args ):
    '''\n
    Build splines for quadraped character\n
    '''
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 0.15

    def SplineOpts( name, size, distance, falloff ):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField( 'atom_prefix_textField', e = True, tx = name )
        cmds.floatField( 'atom_spln_scaleFactor_floatField', e = True, v = size )
        cmds.floatField( 'atom_spln_vectorDistance_floatField', e = True, v = distance )
        cmds.floatField( 'atom_spln_falloff_floatField', e = True, v = falloff )

    def OptAttr( obj, attr ):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( obj + '.' + attr, cb = True )

    # SPINE
    spineName = 'spine'
    spineSize = X * 1
    spineDistance = X * 20
    spineFalloff = 0
    spinePrnt = 'Cog_Grp'
    spineStrt = 'Chest_Grp'
    spineEnd = 'Pelvis_Grp'
    spineAttr = 'Chest'
    spineRoot = 'spine_jnt_01'
    'spine_S_IK_Jnt'
    spine = ['spine_jnt_01', 'spine_jnt_07']
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # return None
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 1 )
    cmds.setAttr( spineAttr + '.ClstrVis', 0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', .25 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_E_IK_curve_scale.input2Z' )
    # add hack to move joint only at end of spline
    pelvis = 'spine_M6_IK_Cntrl'
    plvs = place.Controller( pelvis, 'spine_jnt_07', orient = True, shape = 'tacZ_ctrl', size = 1.0, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    plvsCt = plvs.createController()
    place.cleanUp( plvsCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parent( plvsCt[0], spineName + '_E_IK_Cntrl' )
    cmds.connectAttr( plvsCt[2] + '.translateX', spineName + '_jnt_07_pointConstraint1.offsetX' )
    cmds.connectAttr( plvsCt[2] + '.translateY', spineName + '_jnt_07_pointConstraint1.offsetY' )
    cmds.connectAttr( plvsCt[2] + '.translateZ', spineName + '_jnt_07_pointConstraint1.offsetZ' )

    # NECK
    neckName = 'Neck'
    neckSize = X * 1
    neckDistance = X * 20
    neckFalloff = 0
    neckPrnt = 'Neck_Grp'
    neckStrt = 'Neck_Grp'
    neckEnd = 'Head_Grp'
    neckAttr = 'Neck'
    neck = ['head_jnt_01', 'head_jnt_05']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # assemble
    OptAttr( neckAttr, 'NeckSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 1 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )
    # return False
    # TAIL
    neckName = 'Tail'
    neckSize = X * 1
    neckDistance = X * 20
    neckFalloff = 0
    neckPrnt = 'Pelvis_Grp'
    neckStrt = 'spine_jnt_07'
    neckEnd = 'Tail_Grp'
    neckAttr = 'Tail'
    neck = ['tail_jnt_01', 'tail_jnt_05']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( neckAttr, 'TailSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    # return None
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 1 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # scale
    # scale
    geo = 'caterpillar_c_geo_lod_0'
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    # misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush

