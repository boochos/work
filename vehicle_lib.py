import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
atl = web.mod( "atom_path_lib" )
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
anm = web.mod( "anim_lib" )
dsp = web.mod( "display_lib" )
cn = web.mod( 'constraint_lib' )


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def CONTROLS():
    return '___CONTROLS'


def WORLD_SPACE():
    return '___WORLD_SPACE'


def vehicle_master( masterX = 10, moveX = 10, steerParent = '' ):
    '''
    default group structure
    master and move controls
    '''
    # temp for dev, remove when building actual vehicle
    PreBuild = place.rigPrebuild( Top = 2, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = masterX * 20 )

    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # root joint
    root = 'root_jnt'
    cmds.parent( root, SKIN_JOINTS )

    '''
    # vehicle on path, front of vehicle
    opf = 'pathAttach_front'
    opfCt = place.Controller2( opf, 'on_path_front_jnt', False, 'vctrArrow_ctrl', moveX * 4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opfCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True )

    # vehicle on path, back of vehicle
    opb = 'pathAttach_back'
    opbCt = place.Controller2( opb, 'on_path_back_jnt', False, 'vctrArrowInv_ctrl', moveX * 4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opbCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )

    # vehicle on path, top of vehicle
    opu = 'pathAttach_up'
    opuCt = place.Controller2( opu, 'on_path_back_jnt', False, 'loc_ctrl', moveX * 3, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opuCt[0], CONTROLS )
    cmds.setAttr( opuCt[0] + '.ty', moveX * 5 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )'''

    # move #
    Move = 'move'
    MoveCt = place.Controller2( Move, MasterCt[0], False, 'splineStart_ctrl', moveX * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( MoveCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], MoveCt[0], mo = True )
    cmds.parentConstraint( MoveCt[4], 'root_jnt', mo = True )
    # cmds.parentConstraint( opfCt[4], MoveCt[0], mo = True )

    # steer #
    Steer = 'steer'
    SteerCt = place.Controller2( Steer, 'on_path_front_jnt', False, 'ballRoll_ctrl', moveX * 3, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( SteerCt[0], CONTROLS )
    # cmds.setAttr( SteerCt[0] + '.tz', moveX * 5 )
    if steerParent:
        cmds.parentConstraint( steerParent, SteerCt[0], mo = True )
    else:
        cmds.parentConstraint( MoveCt[4], SteerCt[0], mo = True )
    place.translationLock( SteerCt[2], True )
    place.rotationX( SteerCt[2], True )
    place.rotationZ( SteerCt[2], True )

    # constrain Move to path front / back
    # cmds.parentConstraint( opfCt[4], MoveCt[1], mo = True )
    '''
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    '''

    # pivots for ground
    # pvts = four_point_pivot( name = 'vehicle', parent = MoveCt[3], center = MoveCt[4], front = 'on_path_front_jnt', frontL = 'wheel_front_bottom_L_jnt', frontR = 'wheel_front_bottom_R_jnt', back = 'on_path_back_jnt', backL = 'wheel_back_bottom_L_jnt', backR = 'wheel_back_bottom_R_jnt', up = 'up_jnt', X = 2 )

    if steerParent:
        return [MasterCt[4], steerParent, SteerCt[4]]
    else:
        return [MasterCt[4], MoveCt[4], SteerCt[4]]


def wheel( master_move_controls = [], axle = '', steer = '', center = '', bottom = '', top = '', spin = '', tire_geo = [], rim_geo = [], caliper_geo = [], name = '', suffix = '', X = 1.0, exp = True ):
    '''
    create wheel rig
    - translation based rotation
    - inflattion / deflation
    - steering
    inputs
    - 2 pre-existing controls = master_move_controls -- vehicle_master(), list may have more, but only need the first 2
    - master                  = 'WHEEL_SPACE' group is constrained to this object, 'contact' control lives inside 
    - move                    = axle joint and steering controls get constrained to this object
    - jnts                    = axle, steer, center, bottom, top, spin
    - geo                     = tire_geo, rim_geo, caliper_geo
    - naming strings          = name, suffix
    - controller size         = X
    
    '''

    colorName = ''
    # side
    if 'L' in suffix:
        colorName = 'blue'
        ctrlShp = 'shldrL_ctrl'
    elif 'R' in suffix:
        colorName = 'red'
        ctrlShp = 'shldrR_ctrl'
    else:
        colorName = 'yellow'
        ctrlShp = 'shldrL_ctrl'

    if suffix:
        sffx = '_' + suffix
    else:
        sffx = suffix

    CONTROLS = '___CONTROLS'
    master = master_move_controls[0]
    move = master_move_controls[1]
    #
    WHEEL_GRP = cmds.group( name = name + sffx + '_AllGrp', em = True )
    # cmds.parentConstraint( move, WHEEL_GRP, mo = True )
    cmds.parent( WHEEL_GRP, CONTROLS )
    # return
    # tire has to be facing forward in Z
    clstr = tire_pressure( obj = tire_geo, center = center, name = name, suffix = suffix )
    # return
    # geo cleanup
    cmds.parent( tire_geo, '___WORLD_SPACE' )
    if tire_geo:
        for i in tire_geo:
            # print( i )
            cmds.connectAttr( spin + '.rotateX', i + '.rotateX' )
    else:
        # print( 'no' )
        pass
    # return
    # rim, change to skin
    if rim_geo:
        for i in rim_geo:
            cmds.parent( i, spin )
    # caliper, skin if exists
    if caliper_geo:
        for i in caliper_geo:
            cmds.parent( i, center )

    # root
    cmds.parentConstraint( move, axle, mo = True )

    # wheels shouldnt spin when master is moved, use drive / move control
    WHEEL_SPACE = 'WHEEL_SPACE'
    if not cmds.objExists( WHEEL_SPACE ):
        WHEEL_SPACE = cmds.group( name = WHEEL_SPACE, em = True )
        cmds.parent( WHEEL_SPACE, CONTROLS )
        cmds.parentConstraint( master, WHEEL_SPACE, mo = True )

    # contact # wheel spin derived from top group node of this control
    Contact_F_L = name + '_contact' + sffx
    contact_F_L = place.Controller( Contact_F_L, bottom, False, 'pawMaster_ctrl', X * 12, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Contact_F_LCt = contact_F_L.createController()
    cmds.parent( Contact_F_LCt[0], WHEEL_SPACE )
    cmds.parentConstraint( steer, Contact_F_LCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( Contact_F_LCt[2], [True, False], [True, False], [True, False], [True, False, False] )
    cmds.setAttr( Contact_F_LCt[2] + '.translateY', keyable = True, lock = False )
    #
    place.optEnum( Contact_F_LCt[2], attr = 'Wheel', enum = 'OPTNS' )
    place.addAttribute( [Contact_F_LCt[2]], ['autoRoll'], 0, 1, True, attrType = 'float' )
    #
    place.optEnum( Contact_F_LCt[0], attr = 'Roll', enum = 'INPUTS' )
    #
    cmds.addAttr( Contact_F_LCt[0], ln = 'Radius' )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Radius' ), cb = True )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Radius' ), keyable = True )
    #
    cmds.addAttr( Contact_F_LCt[0], ln = 'Drive' )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Drive' ), cb = True )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Drive' ), keyable = True )

    # live radius
    g = cmds.group( name = name + '_Radius' + sffx + '_Grp', em = True )
    cmds.parent( g, WHEEL_GRP )
    cmds.setAttr( g + '.visibility', 0 )
    #
    r1 = place.loc( name + '_radius1' + sffx )[0]
    cmds.select( r1, spin )
    anm.matchObj()
    cmds.parent( r1, g )
    #
    r2 = place.loc( name + '_radius2' + sffx )[0]
    cmds.select( r2, top )
    anm.matchObj()
    cmds.parent( r2, g )
    #
    dsp.distance( obj1 = r1, obj2 = r2 )
    cmds.connectAttr( r1 + '.distance', Contact_F_LCt[0] + '.Radius' )

    # center
    Center_front_L = name + '_pressure' + sffx
    center_front_L = place.Controller( Center_front_L, center, False, 'diamond_ctrl', X * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Center_front_LCt = center_front_L.createController()
    cmds.parent( Center_front_LCt[0], WHEEL_GRP )
    cmds.parentConstraint( Center_front_LCt[4], center, mo = True )
    cmds.parentConstraint( Contact_F_LCt[4], Center_front_LCt[0], mo = True )
    # math node
    mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = Center_front_LCt[2] + '_mltp_ty' )
    cmds.setAttr( mltp + '.operation', 1 )  # multiply
    cmds.setAttr( mltp + '.input2Y', -1 )
    # connect
    cmds.connectAttr( Center_front_LCt[2] + '.translateY', mltp + '.input1Y' )
    cmds.connectAttr( mltp + '.outputY', clstr + '.translateY' )
    # sidewall
    place.optEnum( Center_front_LCt[2], attr = 'Tire', enum = 'OPTNS' )
    place.addAttribute( [Center_front_LCt[2]], ['sidewallFlex'], -1, 1, True, attrType = 'float' )
    cmds.connectAttr( Center_front_LCt[2] + '.sidewallFlex', clstr + '.translateX' )

    # spin
    Spin_front_L = name + '_spin' + sffx
    spin_front_L = place.Controller( Spin_front_L, spin, False, ctrlShp, X * 7, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Spin_front_LCt = spin_front_L.createController()
    cmds.parent( Spin_front_LCt[0], WHEEL_GRP )
    cmds.parentConstraint( Spin_front_LCt[4], spin, mo = True )
    cmds.parentConstraint( Center_front_LCt[4], Spin_front_LCt[0], mo = True )
    #
    cmds.connectAttr( Contact_F_LCt[0] + '.Drive', Spin_front_LCt[1] + '.rotateX' )
    #
    if exp:
        wheel_exp( ctrl = Contact_F_LCt[0] )
    '''
    # steer #
    Steer_F_L = name + '_steer' + sffx
    steer_F_L = place.Controller( Steer_F_L, steer, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Steer_F_LCt = steer_F_L.createController()
    cmds.setAttr( Steer_F_LCt[0] + '.visibility', 0 )
    cmds.parent( Steer_F_LCt[0], WHEEL_GRP )
    cmds.xform( Steer_F_LCt[0], relative = True, t = ( 0, 0, 20 ) )
    cmds.parentConstraint( axle, Steer_F_LCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( Steer_F_LCt[2], [True, False], [True, False], [True, False], [True, False, False] )
    cmds.setAttr( Steer_F_LCt[2] + '.translateX', keyable = True, lock = False )
    # steer up
    SteerUp_F_L = name + '_steerUp' + sffx
    steerUp_F_L = place.Controller( SteerUp_F_L, steer, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    SteerUp_F_LCt = steerUp_F_L.createController()
    cmds.parent( SteerUp_F_LCt[0], WHEEL_GRP )
    cmds.xform( SteerUp_F_LCt[0], relative = True, t = ( 0, 10, 0 ) )
    cmds.parentConstraint( axle, SteerUp_F_LCt[0], mo = True )
    cmds.setAttr( SteerUp_F_LCt[0] + '.visibility', 0 )

    cmds.aimConstraint( Steer_F_LCt[4], steer, wut = 'object', wuo = SteerUp_F_LCt[4], aim = [0, 0, 1], u = [0, 1, 0], mo = True )
    # cmds.aimConstraint( locAim, obj, wut = 'object', wuo = locUp, aim = aim, u = u, mo = mo )

    return [Steer_F_LCt[1], Contact_F_LCt[2], Center_front_LCt[2], Center_front_LCt[1]]
    '''
    return [steer, Contact_F_LCt[2], Center_front_LCt[2], Center_front_LCt[1]]


def piston( name = '', suffix = '', obj1 = '', obj2 = '', parent1 = '', parent2 = '', parentUp1 = '', parentUp2 = '', aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, 1], up2 = [0, 1, 0], X = 1, color = 'yellow' ):
    '''
    obj objects should have proper pivot point for objects to place and constrain correctly
    '''
    #
    distance = dsp.measureDis( obj1 = obj1, obj2 = obj2 ) * 0.5
    if suffix:
        suffix = '_' + suffix

    # add rig group for cleanliness
    piston_grp = cmds.group( name = name + '_' + suffix + '_AllGrp', em = True )
    cmds.parent( piston_grp, CONTROLS() )

    # obj1
    name1 = name + '_aim1' + suffix
    name1_Ct = place.Controller2( name1, obj1, True, 'facetZup_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name1_Ct[0], piston_grp )
    cmds.pointConstraint( name1_Ct[4], obj1, mo = True )
    if parent1:
        cmds.parentConstraint( parent1, name1_Ct[0], mo = True )
    place.rotationLock( name1_Ct[2], True )

    # obj2
    name2 = name + '_aim2' + suffix
    name2_Ct = place.Controller2( name2, obj2, True, 'facetZup_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name2_Ct[0], piston_grp )
    rot = cmds.xform( name2_Ct[0], q = True, os = True, ro = True )
    cmds.xform( name2_Ct[0], ws = True, ro = ( rot[0] + 180, 0, 0 ) )
    cmds.pointConstraint( name2_Ct[4], obj2, mo = True )
    if parent2:
        cmds.parentConstraint( parent2, name2_Ct[0], mo = True )
    place.rotationLock( name2_Ct[2], True )

    # obj1 up
    nameUp1 = name + '_up1' + suffix
    nameUp1_Ct = place.Controller2( nameUp1, obj1, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp1_Ct[0], piston_grp )
    cmds.setAttr( nameUp1_Ct[1] + place.vector( up1 ), distance )
    if parentUp1:
        cmds.parentConstraint( parentUp1, nameUp1_Ct[0], mo = True )
    place.rotationLock( nameUp1_Ct[2], True )

    # obj2 up
    nameUp2 = name + '_up2' + suffix
    nameUp2_Ct = place.Controller2( nameUp2, obj2, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp2_Ct[0], piston_grp )
    cmds.setAttr( nameUp2_Ct[1] + place.vector( up2 ), distance )
    if parentUp2:
        cmds.parentConstraint( parentUp2, nameUp2_Ct[0], mo = True )
    place.rotationLock( nameUp2_Ct[2], True )

    # aim
    cmds.aimConstraint( name2_Ct[4], obj1, wut = 'object', wuo = nameUp1_Ct[4], aim = aim1, u = up1, mo = True )
    cmds.aimConstraint( name1_Ct[4], obj2, wut = 'object', wuo = nameUp2_Ct[4], aim = aim2, u = up2, mo = True )

    return [name1_Ct, name2_Ct, nameUp1_Ct, nameUp2_Ct]


def spline( name = '', root_jnt = '', tip_jnt = '', splinePrnt = '', splineStrt = '', splineEnd = '', splineAttr = '', startSkpR = False, endSkpR = False, X = 2 ):
    '''\n
    Build splines\n
    name      = 'chainA'         - name of chain
    root_jnt  = 'chainA_jnt_000' - provide first joint in chain
    tip_jnt   = 'chainA_jnt_016' - provide last joint in chain
    splinePrnt = 'master_Grp'     - parent of spline
    splineStrt = 'root_Grp'       - parent for start of spline
    splineEnd  = 'tip_Grp'        - parent for end of spline
    splineAttr = 'master'         - control to receive option attrs
    X         = 2                - controller scale
    '''

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
    splineName = name
    splineSize = X * 1
    splineDistance = X * 4
    splineFalloff = 0

    spline = [root_jnt, tip_jnt]
    # build spline
    SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
    cmds.select( spline )

    stage.splineStage( 4 )
    # assemble
    OptAttr( splineAttr, name + 'Spline' )
    cmds.parentConstraint( splinePrnt, splineName + '_IK_CtrlGrp', mo = True )
    if startSkpR:
        cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True, sr = ( 'x', 'y', 'z' ) )
    else:
        cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True )
    if endSkpR:
        cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True, sr = ( 'x', 'y', 'z' ) )
    else:
        cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( splineName + '_IK_CtrlGrp', splineAttr )
    # set options
    cmds.setAttr( splineAttr + '.' + splineName + 'Vis', 0 )
    cmds.setAttr( splineAttr + '.' + splineName + 'Root', 0 )
    cmds.setAttr( splineAttr + '.' + splineName + 'Stretch', 1 )
    cmds.setAttr( splineAttr + '.ClstrVis', 1 )
    cmds.setAttr( splineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrVis', 0 )
    cmds.setAttr( splineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_E_IK_curve_scale.input2Z' )


def fold_ik( name = '', strt_jnt = '', end_jnt = '', X = 1.0, color = 'yellow' ):
    '''
    3 joint ik, for folding parts
    '''
    pass


def four_point_pivot( name = 'vhcl', parent = '', center = '', front = '', frontL = '', frontR = '', back = '', backL = '', backR = '', up = '', X = 1 ):
    '''
    main control, with 4 point pivot control and up vector
    assume translateZ is forward
    '''
    pvt = 'pivot'
    #
    if name:
        name = name + '_'
    #
    color = 'yellow'
    colorc = 'brown'
    colorL = 'blue'
    colorR = 'red'

    # body grp
    BODY_GRP = cmds.group( name = name + 'Pvt_AllGrp', em = True )
    cmds.parent( BODY_GRP, CONTROLS() )

    # ##########
    # body
    nameb = name + 'pivot'
    body_Ct = place.Controller2( nameb, center, False, 'pawMaster_ctrl', X * 80, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( body_Ct[0], BODY_GRP )
    cmds.parentConstraint( parent, body_Ct[0], mo = True )
    place.translationLock( body_Ct[2], True )
    place.translationY( body_Ct[2], False )

    # ##########
    # front
    namef = name + 'front_' + pvt
    namef_Ct = place.Controller2( namef, front, False, 'pawToeRoll_ctrl', X * 12, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( namef_Ct[0], BODY_GRP )
    cmds.parentConstraint( namef_Ct[4], center, mo = True )
    cmds.parentConstraint( body_Ct[4], namef_Ct[0], mo = True )
    place.rotationLock( namef_Ct[2], True )
    place.translationZ( namef_Ct[2], True )
    place.translationX( namef_Ct[2], True )

    # back
    nameb = name + 'back_' + pvt
    nameb_Ct = place.Controller2( nameb, back, False, 'pawHeelRoll_ctrl', X * 12, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameb_Ct[0], BODY_GRP )
    cmds.parentConstraint( body_Ct[4], nameb_Ct[0], mo = True )
    place.rotationLock( nameb_Ct[2], True )
    place.translationZ( nameb_Ct[2], True )
    place.translationX( nameb_Ct[2], True )

    # up
    nameu = name + 'up_' + pvt
    nameu_Ct = place.Controller2( nameu, up, False, 'diamond_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameu_Ct[0], BODY_GRP )
    cmds.setAttr( nameu_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( nameu_Ct[4], up, mo = True )
    cmds.parentConstraint( body_Ct[4], nameu_Ct[0], mo = True )
    place.rotationLock( nameu_Ct[2], True )
    place.translationZ( nameu_Ct[2], True )

    # ##########
    # frontL
    namefl = name + 'front_L_' + pvt
    namefl_Ct = place.Controller2( namefl, frontL, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
    cmds.parent( namefl_Ct[0], BODY_GRP )
    cmds.setAttr( namefl_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( body_Ct[4], namefl_Ct[0], mo = True )
    place.rotationLock( namefl_Ct[2], True )
    place.translationZ( namefl_Ct[2], True )
    place.translationX( namefl_Ct[2], True )

    # frontR
    namefr = name + 'front_R_' + pvt
    namefr_Ct = place.Controller2( namefr, frontR, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
    cmds.parent( namefr_Ct[0], BODY_GRP )
    cmds.setAttr( namefr_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( body_Ct[4], namefr_Ct[0], mo = True )
    place.rotationLock( namefr_Ct[2], True )
    place.translationZ( namefr_Ct[2], True )
    place.translationX( namefr_Ct[2], True )

    # backL
    namebl = name + 'back_L_' + pvt
    namebl_Ct = place.Controller2( namebl, backL, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
    cmds.parent( namebl_Ct[0], BODY_GRP )
    cmds.setAttr( namebl_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( body_Ct[4], namebl_Ct[0], mo = True )
    place.rotationLock( namebl_Ct[2], True )
    place.translationZ( namebl_Ct[2], True )
    place.translationX( namebl_Ct[2], True )

    # backR
    namebr = name + 'back_R_' + pvt
    namebr_Ct = place.Controller2( namebr, backR, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
    cmds.parent( namebr_Ct[0], BODY_GRP )
    cmds.setAttr( namebr_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( body_Ct[4], namebr_Ct[0], mo = True )
    place.rotationLock( namebr_Ct[2], True )
    place.translationZ( namebr_Ct[2], True )
    place.translationX( namebr_Ct[2], True )

    # ##########
    # aim
    cmds.aimConstraint( nameb_Ct[4], namef_Ct[4], wut = 'object', wuo = nameu_Ct[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( namef_Ct[3], True )

    # ##########
    # pivot connections
    # 5 blend attr nodes
    # 2 multdiv nodes

    # front pivots ( left/ right ) ty blend
    frontBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_Blend' )
    cmds.setAttr( frontBlend + '.attributesBlender', 0.5 )
    cmds.connectAttr( namefl_Ct[2] + '.translateY', frontBlend + '.input[0]' )
    cmds.connectAttr( namefr_Ct[2] + '.translateY', frontBlend + '.input[1]' )
    cmds.connectAttr( frontBlend + '.output', namef_Ct[1] + '.translateY' )

    # back pivots ( left/ right ) ty blend
    backBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_Blend' )
    cmds.setAttr( backBlend + '.attributesBlender', 0.5 )
    cmds.connectAttr( namebl_Ct[2] + '.translateY', backBlend + '.input[0]' )
    cmds.connectAttr( namebr_Ct[2] + '.translateY', backBlend + '.input[1]' )
    cmds.connectAttr( backBlend + '.output', nameb_Ct[1] + '.translateY' )

    # blend front up vector pivots (l/r)
    frontUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_up_Blend' )
    cmds.setAttr( frontUpBlend + '.attributesBlender', 0.5 )
    # mltp only for left side, invert value
    frontlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_front_l_mlt' )
    cmds.setAttr( frontlmlt + '.operation', 1 )  # multiply
    cmds.setAttr( frontlmlt + '.input2Y', -1 )
    #
    cmds.connectAttr( namefr_Ct[2] + '.translateY', frontUpBlend + '.input[0]' )
    cmds.connectAttr( namefl_Ct[2] + '.translateY', frontlmlt + '.input1Y' )
    cmds.connectAttr( frontlmlt + '.outputY', frontUpBlend + '.input[1]' )

    # blend back up vector pivots (l/r)
    backUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_up_Blend' )
    cmds.setAttr( backUpBlend + '.attributesBlender', 0.5 )
    # mltp only for left side, invert value
    backlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_back_l_mlt' )
    cmds.setAttr( backlmlt + '.operation', 1 )  # multiply
    cmds.setAttr( backlmlt + '.input2Y', -1 )
    #
    cmds.connectAttr( namebr_Ct[2] + '.translateY', backUpBlend + '.input[0]' )
    cmds.connectAttr( namebl_Ct[2] + '.translateY', backlmlt + '.input1Y' )
    cmds.connectAttr( backlmlt + '.outputY', backUpBlend + '.input[1]' )

    # blend result of front/back translateY values to up translateX
    upBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'up_Blend' )
    cmds.setAttr( upBlend + '.attributesBlender', 0.5 )
    cmds.connectAttr( frontUpBlend + '.output', upBlend + '.input[0]' )
    cmds.connectAttr( backUpBlend + '.output', upBlend + '.input[1]' )
    cmds.connectAttr( upBlend + '.output', nameu_Ct[1] + '.translateX' )

    return [namefl_Ct[2], namefr_Ct[2], namebl_Ct[2], namebr_Ct[2]]


def translate_part( name = '', suffix = '', obj = '', objConstrain = True, parent = '', translations = [0, 0, 1], X = 1, shape = 'facetYup_ctrl', color = 'yellow' ):
    '''
    doors and things
    rotations = [0, 0, 1] : ( x, y, z )
    '''
    #
    if suffix:
        suffix = '_' + suffix

    # obj
    name = name + suffix
    name_Ct = place.Controller2( name, obj, True, shape, X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name_Ct[0], CONTROLS() )
    if objConstrain:
        cmds.parentConstraint( name_Ct[4], obj, mo = True )
    if parent:
        cmds.parentConstraint( parent, name_Ct[0], mo = True )
    # lock translation
    place.rotationLock( name_Ct[2], True )
    if translations[0]:
        place.translationX( name_Ct[2], False )
    if translations[1]:
        place.translationY( name_Ct[2], False )
    if translations[2]:
        place.translationZ( name_Ct[2], False )

    return name_Ct


def rotate_part( name = '', suffix = '', obj = '', objConstrain = True, parent = '', rotations = [0, 0, 1], X = 1, shape = 'facetYup_ctrl', color = 'yellow' ):
    '''
    doors and things
    rotations = [0, 0, 1] : ( x, y, z )
    '''
    #
    if suffix:
        suffix = '_' + suffix

    # obj
    name = name + suffix
    name_Ct = place.Controller2( name, obj, True, shape, X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name_Ct[0], CONTROLS() )
    if objConstrain:
        cmds.parentConstraint( name_Ct[4], obj, mo = True )
    if parent:
        cmds.parentConstraint( parent, name_Ct[0], mo = True )
    # lock translation
    place.translationLock( name_Ct[2], True )
    # lock all rotations, unlock one at a time
    place.rotationLock( name_Ct[2], True )
    if rotations[0]:
        place.rotationX( name_Ct[2], False )
    if rotations[1]:
        place.rotationY( name_Ct[2], False )
    if rotations[2]:
        place.rotationZ( name_Ct[2], False )

    return name_Ct


def dynamic_part():
    '''
    last thing
    '''
    pass


def tire_pressure( obj = '', center = '', name = '', suffix = '', lattice = ( 2, 29, 5 ) ):
    '''
    add tire pressure behaviour
    lattice = object local space (X, Y, Z)
    '''
    # group
    g = cmds.group( name = name + '_clusterGrp_' + suffix, em = True )
    cmds.parent( g, '___WORLD_SPACE' )
    cmds.setAttr( g + '.visibility', 0 )
    # return
    # store selection
    sel = cmds.ls( sl = 1 )
    # lattice
    cmds.select( obj )
    # [u'wheel_front_lattice_L_', u'wheel_front_lattice_L_Lattice', u'wheel_front_lattice_L_Base']
    result = cmds.lattice( name = name + '_ltc_' + suffix + '_', dv = lattice, oc = True, outsideLattice = 1 )
    # result[0] is a component apparently, cant be parented
    cmds.parent( result[1], '___WORLD_SPACE' )
    cmds.parent( result[2], '___WORLD_SPACE' )
    # return
    cmds.setAttr( result[1] + '.visibility', 0 )
    cmds.setAttr( result[2] + '.visibility', 0 )
    # print( result )
    # clusters
    clusters = []
    ltc = result[1]
    depth = lattice[0]  # X
    row = ( lattice[1] - 1 ) / 2  # Y
    column = lattice[2]  # Z
    for i in range( row ):  # depth
        sl = ltc + '.pt[' + str( i ) + '][0:' + str( depth - 1 ) + '][0:' + str( column - 1 ) + ']'
        sl = ltc + '.pt[0:' + str( depth - 1 ) + '][' + str( i ) + '][0:' + str( column - 1 ) + ']'
        # print( sl )
        cmds.select( sl )
        c = cmds.cluster( name = name + '_clstr_' + str( i ) + '_' + suffix + '_' )[1]
        clusters.append( c )

    # top cluster (lattice[row])
    sl = ltc + '.pt[' + str( row ) + ':' + str( lattice[1] ) + '][0:' + str( depth - 1 ) + '][0:' + str( column - 1 ) + ']'
    sl = ltc + '.pt[0:' + str( depth - 1 ) + '][' + str( row ) + ':' + str( lattice[1] ) + '][0:' + str( column - 1 ) + ']'
    # print( sl )
    cmds.select( sl )
    c = cmds.cluster( name = name + '_clstrTop_' + suffix + '_' )[1]
    # clusters.append( c )
    # return
    # parent clusters
    cmds.parent( clusters, g )
    cmds.parent( c, g )
    # connect to rig
    cmds.parentConstraint( center, g, mo = True )

    # translate y math nodes
    lattice_row_gap = 0.3  # guess, should find a way to measure it
    for i in range( len( clusters ) - 1 ):
        # create nodes for translation
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_ty' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_ty' )
        # set node attrs
        cmds.setAttr( cndtn + '.colorIfFalseR', 0 )
        cmds.setAttr( cndtn + '.colorIfFalseG', 0 )
        cmds.setAttr( cndtn + '.colorIfFalseB', 0 )
        cmds.setAttr( cndtn + '.secondTerm', lattice_row_gap )
        cmds.setAttr( cndtn + '.operation', 3 )  # greater or equal
        cmds.setAttr( addDL + '.input2', lattice_row_gap * -1 )
        # connect math in
        cmds.connectAttr( clusters[i] + '.translateY', addDL + '.input1' )
        cmds.connectAttr( clusters[i] + '.translateY', cndtn + '.firstTerm' )
        # connect math out
        cmds.connectAttr( addDL + '.output', cndtn + '.colorIfTrueG' )
        cmds.connectAttr( cndtn + '.outColorG', clusters[i + 1] + '.translateY' )

    # tire bulge scale X
    weight = 0.3
    weight_add = 0.1
    cls = int( len( clusters ) / 2 ) - 3
    for i in range( cls ):
        # create nodes for scale bulge
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_sclx' )
        mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = clusters[i] + '_mltDv_sclx' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_sclx' )
        # set node attrs
        cmds.setAttr( mltp + '.operation', 1 )  # multiply
        cmds.setAttr( mltp + '.input2X', weight )
        cmds.setAttr( addDL + '.input2', 1 )
        # connect mltp in
        cmds.connectAttr( clusters[0] + '.translateY', mltp + '.input1X' )
        # connect addDL in
        cmds.connectAttr( mltp + '.outputX', addDL + '.input1' )
        # connect next cluster in
        cmds.connectAttr( addDL + '.output', clusters[i + 1] + '.scaleX' )
        #
        if i <= 1:
            # weight_add = weight_add * 2
            weight = weight + weight_add
        else:
            # weight_add = weight_add * 2
            weight = weight - ( weight_add * 2 )

    # tx sidewall, direct copy of above loop, altered names, couple connections
    weight = 0.3
    weight_add = 0.1
    cls = int( len( clusters ) / 2 ) - 3
    for i in range( cls ):
        # create nodes for scale bulge
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_tx' )
        mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = clusters[i] + '_mltDv_tx' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_tx' )
        # set node attrs
        cmds.setAttr( mltp + '.operation', 1 )  # multiply
        cmds.setAttr( mltp + '.input2X', weight )
        cmds.setAttr( addDL + '.input2', 0 )
        # connect mltp in
        cmds.connectAttr( clusters[0] + '.translateX', mltp + '.input1X' )
        # connect addDL in
        cmds.connectAttr( mltp + '.outputX', addDL + '.input1' )
        # connect next cluster in
        cmds.connectAttr( addDL + '.output', clusters[i + 1] + '.translateX' )
        #
        if i <= 1:
            # weight_add = weight_add * 2
            weight = weight + weight_add
        else:
            # weight_add = weight_add * 2
            weight = weight - ( weight_add * 2 )

    # limits
    cmds.select( clusters[0] )
    cmds.transformLimits( ety = [1, 0], ty = ( 0, 100 ) )

    cmds.select( sel )

    return clusters[0]


def wheel_exp( ctrl = '' ):
    '''
    add expression to control, connect drive attr to wheel rotation
    '''
    ln1 = "global vector $" + ctrl + "vPos = << 0, 0, 0 >>;\n"
    ln2 = "float $" + ctrl + "distance = 0.0;\n"
    ln3 = "int $" + ctrl + "direction = 1;\n"
    ln4 = "vector $" + ctrl + "vPosChange = `getAttr " + ctrl + ".translate`;\n"
    ln5 = "float $" + ctrl + "cx = $" + ctrl + "vPosChange.x - $" + ctrl + "vPos.x;\n"
    ln6 = "float $" + ctrl + "cy = $" + ctrl + "vPosChange.y - $" + ctrl + "vPos.y;\n"
    ln7 = "float $" + ctrl + "cz = $" + ctrl + "vPosChange.z - $" + ctrl + "vPos.z;\n"
    ln8 = "float $" + ctrl + "distance = sqrt( `pow $" + ctrl + "cx 2` + `pow $" + ctrl + "cy 2` + `pow $" + ctrl + "cz 2` );\n"
    ln9 = "if ( ( $" + ctrl + "vPosChange.x == $" + ctrl + "vPos.x ) && ( $" + ctrl + "vPosChange.y != $" + ctrl + "vPos.y ) && ( $" + ctrl + "vPosChange.z == $" + ctrl + "vPos.z ) ){}\n"
    ln10 = "else {\n"
    ln11 = "    float $" + ctrl + "angle = " + ctrl + ".rotateY%360;\n"
    ln12 = "    if ( $" + ctrl + "angle == 0 ){ \n"
    ln13 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = 1;\n"
    ln14 = "        else $" + ctrl + "direction=-1;}\n"
    ln15 = "    if ( ( $" + ctrl + "angle > 0 && $" + ctrl + "angle <= 90 ) || ( $" + ctrl + "angle <- 180 && $" + ctrl + "angle >= -270 ) ){ \n"
    ln16 = "        if ( $" + ctrl + "vPosChange.x > $" + ctrl + "vPos.x ) $" + ctrl + "direction = 1 * $" + ctrl + "direction;\n"
    ln17 = "        else $" + ctrl + "direction = -1 * $" + ctrl + "direction; }\n"
    ln18 = "    if ( ( $" + ctrl + "angle > 90 && $" + ctrl + "angle <= 180 ) || ( $" + ctrl + "angle < -90 && $" + ctrl + "angle >= -180 ) ){\n"
    ln19 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = -1 * $" + ctrl + "direction;\n"
    ln20 = "        else $" + ctrl + "direction = 1 * $" + ctrl + "direction; }\n"
    ln21 = "    if ( ( $" + ctrl + "angle > 180 && $" + ctrl + "angle <= 270 ) || ( $" + ctrl + "angle < 0 && $" + ctrl + "angle >= -90 ) ){\n"
    ln22 = "        if ( $" + ctrl + "vPosChange.x > $" + ctrl + "vPos.x ) $" + ctrl + "direction = -1 * $" + ctrl + "direction;\n"
    ln23 = "        else $" + ctrl + "direction = 1 * $" + ctrl + "direction; }\n"
    ln24 = "    if ( ( $" + ctrl + "angle > 270 && $" + ctrl + "angle <= 360 ) || ( $" + ctrl + "angle < -270 && $" + ctrl + "angle >= -360 ) ) {\n"
    ln25 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = 1 * $" + ctrl + "direction;\n"
    ln26 = "        else $" + ctrl + "direction = -1 * $" + ctrl + "direction; }\n"
    ln27 = "    " + ctrl + ".Drive = " + ctrl + ".Drive + ( ( $" + ctrl + "direction * ( ( $" + ctrl + "distance / ( 6.283185 * " + ctrl + ".Radius ) ) * 360.0 ) ) ); }\n"
    ln28 = "$" + ctrl + "vPos = << " + ctrl + ".translateX, " + ctrl + ".translateY, " + ctrl + ".translateZ >>;\n"

    exp = ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7 + ln8 + ln9 + ln10 + ln11 + ln12 + ln13 + ln14 + ln15 + ln16 + ln17 + ln18 + ln19 + ln20 + ln21 + ln22 + ln23 + ln24 + ln25 + ln26 + ln27 + ln28
    cmds.expression( o = ctrl, s = exp )


def rear_end_path( X = 1.0 ):
    '''
    for front steering vehicles back end follows more direct line relative to front end
    make 2 point path, attach to main path
    '''
    #
    name = 'path_rear'
    result = []
    curveTmp = cmds.curve( d = 1, p = [( 0, 0, 0 ), ( 0, 0, 10 )], k = [0, 1] )
    curve = cmds.rename( curveTmp, ( name + '_Crv' ) )
    cmds.setAttr( curve + '.overrideEnabled', 1 )
    cmds.setAttr( curve + '.overrideDisplayType', 1 )
    #
    clstr = []
    i = 0
    num = cmds.getAttr( ( curve + '.cv[*]' ) )
    for item in num:
        #
        c = cmds.cluster( ( curve + '.cv[' + str( i ) + ']' ), n = ( name + '_Clstr' + str( i ) ), envelope = True )[1]
        cmds.setAttr( c + '.visibility', 0 )
        #
        name_Ct = place.Controller2( name + str( i ), c, False, 'facetYup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
        # cmds.parent( name_Ct[0], CONTROLS() )
        cmds.parentConstraint( name_Ct[4], c, mo = True )
        #
        i = i + 1
        clstr.append( c )
    #
    result.append( curve )
    result.append( clstr )
    null = cmds.group( name = name + 'Grp', em = True )
    # cmds.parent( result[0], null )
    # cmds.parent( result[1], null )
    return null


def path( points = 5, X = 0.05, length = 10.0, layers = 3 ):
    '''
    # creates groups and master controller from arguments specified as 'True'
    segment = 4 points
    
    '''
    #
    if points < 4:
        message( 'Points variable should be higher than 3.' )
        return None
    #
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = False, Geo = False, World = True, Master = True, OlSkool = False, Size = 150 * X )
    #
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    WORLD_SPACE = PreBuild[2]
    MasterCt = PreBuild[3]
    #
    misc.optEnum( MasterCt[2], attr = 'path', enum = 'OPTNS' )
    misc.addAttribute( [MasterCt[2]], ['weightedPath'], 0, 1, True, 'float' )
    cmds.setAttr( MasterCt[2] + '.weightedPath', 0.2 )

    # up
    upCnt = place.Controller( place.getUniqueName( 'up' ), 'master', orient = True, shape = 'loc_ctrl', size = 60 * X, color = 17, setChannels = True, groups = True )
    upCntCt = upCnt.createController()
    place.cleanUp( upCntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCntCt[0] + '.ty', length / 2 )
    cmds.parentConstraint( 'master_Grp', upCntCt[0], mo = True )

    #
    path = place.getUniqueName( 'path' )

    # layers
    cluster_layers = []
    paths = []
    layer = 0
    while layer < layers:
        # build curve
        lengthSeg = length / ( points + layer - 1.0 )
        i = 1
        p = '[( 0, 0, -1.128 )'
        while i < points + layer:
            p = p + ',( 0, 0,' + str( lengthSeg * i ) + ')'
            i = i + 1
        p = p + ']'
        # print( p )
        pth = cmds.curve( n = path + '_layer_' + pad_number( i = layer ), d = 3, p = eval( p ) )
        # cmds.setAttr( pth + '.visibility', 0 )
        # print( pth )
        paths.append( pth )
        # return
        cmds.setAttr( pth + '.template', 1 )
        place.cleanUp( pth, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cl = place.clstrOnCV( pth, 'layer' + pad_number( i = layer ) + '_Clstr' )
        # cleanup clusters and controllers
        cGrp = 'clstr_' + pad_number( i = layer ) + '_Grp'
        cmds.group( cl, n = cGrp, w = True )
        cmds.setAttr( cGrp + '.visibility', 0 )
        place.cleanUp( cGrp, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cluster_layers.append( cl )
        layer = layer + 1
    # print( paths )
    for l in range( len( cluster_layers ) - 1 ):
        # constrain start, end
        c = 0
        for c in range( len( cluster_layers[l + 1] ) - 0 ):
            # print( '____', c )
            # first
            if c == 0:
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
            # last
            elif cluster_layers[l + 1][c] == cluster_layers[l + 1][-1]:
                cmds.parentConstraint( cluster_layers[l][-1], cluster_layers[l + 1][c], mo = False )
                break
            else:
                constraint = cmds.parentConstraint( cluster_layers[l][c - 1], cluster_layers[l + 1][c], mo = False )[0]
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
                place.hijackConstraints( master = MasterCt[2], attr = 'weightedPath', value = 0.5, constraint = constraint )
            c = c + 1

    # place Controls on Clusters and Constrain
    color = 12
    i = 1
    Ctrls = []
    for handle in cluster_layers[0]:
        #
        cnt = place.Controller( 'point' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ), handle, orient = False, shape = 'splineStart_ctrl', size = 60 * X, color = color, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'brown' )
        cntCt = cnt.createController()
        # cmds.setAttr( handle + '.visibility', 0 )
        cmds.parentConstraint( MasterCt[4], cntCt[0], mo = True )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        Ctrls.append( cntCt[2] )
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1

    # path
    s = 0.0
    travel = 'travel'
    spacing = 'spacing'
    # vehicle on path, front of vehicle
    opf = 'onPath_front'
    opfCt = place.Controller2( opf, MasterCt[4], False, 'vctrArrow_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opfCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True )
    place.rotationLock( opfCt[2], True )
    misc.optEnum( opfCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    misc.addAttribute( [opfCt[2]], [travel], 0.0, 10.0, True, 'float' )
    misc.addAttribute( [opfCt[2]], [spacing], -10.0, 10.0, True, 'float' )
    misc.addAttribute( [opfCt[2]], ['frontTwist'], -360, 360, True, 'float' )
    misc.addAttribute( [opfCt[2]], ['upTwist'], -360, 360, True, 'float' )
    misc.addAttribute( [opfCt[2]], ['sideTwist'], -360, 360, True, 'float' )
    cmds.setAttr( opfCt[2] + '.' + spacing, -0.15 )
    # vehicle on path, back of vehicle
    opb = 'onPath_back'
    opbCt = place.Controller2( opb, MasterCt[4], False, 'vctrArrowInv_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opbCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )
    place.rotationLock( opbCt[2], True )
    # misc.optEnum( opbCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    # misc.addAttribute( [opbCt[2]], [spacing], 0.0, 1.0, True, 'float' )
    # vehicle on path, top of vehicle
    opu = 'onPath_up'
    opuCt = place.Controller2( opu, MasterCt[4], False, 'loc_ctrl', X * 50, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( opuCt[0], CONTROLS )
    cmds.setAttr( opuCt[0] + '.ty', X * 100 )
    cmds.setAttr( opuCt[0] + '.visibility', 0 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )
    # aim
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( opfCt[3], True )

    # front - attach to path
    motpth_f = cmds.pathAnimation( opfCt[1], c = paths[0], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.frontTwist', motpth_f + '.frontTwist' )
    cmds.connectAttr( opfCt[2] + '.upTwist', motpth_f + '.upTwist' )
    cmds.connectAttr( opfCt[2] + '.sideTwist', motpth_f + '.sideTwist' )
    cmds.setAttr( opfCt[2] + '.frontTwist', 180 )
    cmds.setAttr( opfCt[2] + '.sideTwist', 90 )
    # back - attach to path
    motpth_b = cmds.pathAnimation( opbCt[1], c = paths[2], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.frontTwist', motpth_b + '.frontTwist' )
    cmds.connectAttr( opfCt[2] + '.upTwist', motpth_b + '.upTwist' )
    cmds.connectAttr( opfCt[2] + '.sideTwist', motpth_b + '.sideTwist' )
    # nodes
    mltNode = cmds.shadingNode( 'multiplyDivide', au = True, n = ( travel + '_MltDv' ) )  # increase travel from (0.0-1.0 to 0.0-10.0)
    cmds.setAttr( ( mltNode + '.operation' ), 1 )  # set operation: 2 = divide, 1 = multiply
    cmds.setAttr( mltNode + '.input2Z', 0.1 )
    dblLnrNode = cmds.createNode( 'addDoubleLinear', name = ( spacing + '_DblLnr' ) )
    # travel
    cmds.connectAttr( opfCt[2] + '.' + travel, mltNode + '.input1Z' )
    cmds.connectAttr( mltNode + '.outputZ', motpth_f + '.uValue', f = True )
    # spacing
    cmds.connectAttr( mltNode + '.outputZ', dblLnrNode + '.input2' )
    cmds.connectAttr( opfCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )


def attach( up = '', reverse = False, orientNode = '' ):
    '''
    select controls first and path object with namespace last
    assumes controls are sorted in proper order
    orientNode should be last selection
    '''
    #
    cmds.undoInfo( openChunk = True )

    #
    cmds.undoInfo( closeChunk = True )


def car_sandbox( name = 'car', X = 1 ):
    '''
    test build
    addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_ty' )
    '''
    # mass to pivot, body
    center = 'body_jnt'
    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vehicle_master( masterX = X * 10, moveX = X * 10 )

    # [frontl, frontr, backl, backr]
    bdy = four_point_pivot( name = 'body', parent = 'move_Grp', center = center, front = 'front_jnt', frontL = 'front_L_jnt', frontR = 'front_R_jnt', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )
    print( '_____body' )
    print( bdy )
    # wheels
    # front
    sel = [
    'axle_front_jnt',
    'wheel_front_steer_L_jnt',
    'wheel_front_center_L_jnt',
    'wheel_front_bottom_L_jnt',
    'wheel_front_top_L_jnt',
    'wheel_front_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'L', X = X * 1.0 )
    print( 'done wheel' )
    cmds.parentConstraint( ctrls[2], whl[0], mo = True )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addfl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[0] + '.ty' )

    #
    sel = [
    'axle_front_jnt',
    'wheel_front_steer_R_jnt',
    'wheel_front_center_R_jnt',
    'wheel_front_bottom_R_jnt',
    'wheel_front_top_R_jnt',
    'wheel_front_spin_R_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_R_geo'], rim_geo = ['rim_front_R_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'R', X = X * 1.0 )
    cmds.parentConstraint( ctrls[2], whl[0], mo = True )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addfr_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[1] + '.ty' )

    # back
    sel = [
    'axle_back_jnt',
    'wheel_back_steer_L_jnt',
    'wheel_back_center_L_jnt',
    'wheel_back_bottom_L_jnt',
    'wheel_back_top_L_jnt',
    'wheel_back_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_L_geo'], rim_geo = ['rim_back_L_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'L', X = X * 1.0 )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addbl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[2] + '.ty' )

    #
    sel = [
    'axle_back_jnt',
    'wheel_back_steer_R_jnt',
    'wheel_back_center_R_jnt',
    'wheel_back_bottom_R_jnt',
    'wheel_back_top_R_jnt',
    'wheel_back_spin_R_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_R_geo'], rim_geo = ['rim_back_R_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'R', X = X * 1.0 )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addbr_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[3] + '.ty' )

    # bug, contact group in wheels dont update
    cmds.dgdirty( allPlugs = True )

'''
#
#
import imp
import webrImport as web
imp.reload(web)
#
import vehicle_lib as vhl
imp.reload(vhl)
# vehicle rig
X = 1
vhl = web.mod('vehicle_lib')
vhl.car_sandbox( name = 'car', X = X * 1 )
# vehicle path
X = 0.2
vhl = web.mod('vehicle_lib')
vhl.path(  segments = 2, size = X * 1, length = 100)


# path
pth = web.mod('atom_path_lib')
pth.path(  segments = 5, size = X * 1, length = 500 )
# select front object first
pth.attach( up = 'wheel_rig1:up', reverse = False, orientNode = 'wheel_rig1:master' )


#
'''
