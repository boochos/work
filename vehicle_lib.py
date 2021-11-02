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
app = web.mod( "atom_appendage_lib" )
jnt = web.mod( 'atom_joint_lib' )
dnm = web.mod( 'atom_dynamicSpline_lib' )


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            print( what )


def fix_normals( del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    geo = get_geo_list( all = True )
    cmds.select( geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( geo, ch = True )


def mirror_jnts():
    '''
    
    '''
    # jnts - new joints for pivots
    mirrorj = [
    'axle_back_L_jnt',
    'axle_front_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = True )


def skin( joint = '', geos = [], constraint = True ):
    '''
    skin geo list to joint
    '''
    #
    # alternate method
    # cmds.select( [geo_hub[1], jnt_hub[1]] )
    # mel.eval( 'SmoothBindSkin;' )
    #
    sel = cmds.ls( sl = 1 )
    # skin
    for g in geos:
        if constraint:
            cmds.parentConstraint( joint, g, mo = True )
        else:
            cmds.select( [g, joint] )
            mel.eval( 'SmoothBindSkin;' )
            # cmds.bindSkin( tsb = True )  # toSelectedBones
            # cmds.bindSkin( g, joint, tsb = True ) # toSelectedBones
            # cmds.bindSkin()
    cmds.select( sel )


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
    MoveCt = place.Controller2( Move, MasterCt[0], False, 'splineStart_ctrl', moveX * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( MoveCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], MoveCt[0], mo = True )
    cmds.parentConstraint( MoveCt[4], 'root_jnt', mo = True )
    # cmds.parentConstraint( opfCt[4], MoveCt[0], mo = True )

    # steer #
    Steer = 'steer'
    SteerCt = place.Controller2( Steer, 'front_jnt', False, 'splineStart_ctrl', moveX * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( SteerCt[0], CONTROLS )
    # cmds.setAttr( SteerCt[0] + '.tz', moveX * 5 )
    if steerParent:
        cmds.parentConstraint( steerParent, SteerCt[0], mo = True )
    else:
        cmds.parentConstraint( MoveCt[4], SteerCt[0], mo = True )
    place.translationLock( SteerCt[2], True )
    place.rotationXLock( SteerCt[2], True )
    place.rotationZLock( SteerCt[2], True )

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


def wheel( master_move_controls = [], axle = '', steer = '', center = '', bottom = '', top = '', spin = '', tire_geo = [], rim_geo = [], caliper_geo = [], name = '', suffix = '', X = 1.0, exp = True, pressureMult = 0.3 ):
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
    # clusters[0]
    clstr = tire_pressure( obj = tire_geo, center = center, name = name, suffix = suffix, pressureMult = pressureMult )
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
        skin( spin, rim_geo )
    # caliper, skin if exists
    if caliper_geo:
        skin( center, caliper_geo )

    # root
    cmds.parentConstraint( move, axle, mo = True )

    # wheels shouldnt spin when master is moved, use drive / move control
    WHEEL_SPACE = 'WHEEL_SPACE'
    if not cmds.objExists( WHEEL_SPACE ):
        WHEEL_SPACE = cmds.group( name = WHEEL_SPACE, em = True )
        cmds.parent( WHEEL_SPACE, CONTROLS )
        cmds.parentConstraint( master, WHEEL_SPACE, mo = True )

    # contact # wheel spin derived from top group node of this control
    Contact = name + '_contact' + sffx
    contact = place.Controller( Contact, bottom, False, 'squareYup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    ContactCt = contact.createController()
    # cmds.setAttr( ContactCt[0] + '.visibility', 0 )
    cmds.parent( ContactCt[0], WHEEL_SPACE )
    cmds.parentConstraint( steer, ContactCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( ContactCt[2], [True, False], [True, False], [True, False], [True, False, False] )

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

    # center / pressure
    Pressure = name + '_pressure' + sffx
    pressure = place.Controller( Pressure, center, False, 'diamond_ctrl', X * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    PressureCt = pressure.createController()
    cmds.parent( PressureCt[0], WHEEL_GRP )
    cmds.parentConstraint( PressureCt[4], center, mo = True )
    cmds.parentConstraint( ContactCt[4], PressureCt[0], mo = True )
    # math node
    mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = PressureCt[2] + '_mltp_ty' )
    cmds.setAttr( mltp + '.operation', 1 )  # multiply
    cmds.setAttr( mltp + '.input2Y', -1 )
    # connect
    cmds.connectAttr( PressureCt[2] + '.translateY', mltp + '.input1Y' )
    cmds.connectAttr( mltp + '.outputY', clstr + '.translateY' )
    # sidewall
    place.optEnum( PressureCt[2], attr = 'Tire', enum = 'CONTROL' )
    place.addAttribute( [PressureCt[2]], ['sidewallFlex'], -1, 1, True, attrType = 'float' )
    cmds.connectAttr( PressureCt[2] + '.sidewallFlex', clstr + '.translateX' )

    # spin
    Spin = name + '_spin' + sffx
    spinct = place.Controller( Spin, spin, False, ctrlShp, X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    SpinCt = spinct.createController()
    cmds.parent( SpinCt[0], WHEEL_GRP )
    cmds.parentConstraint( SpinCt[4], spin, mo = True )
    cmds.parentConstraint( PressureCt[4], SpinCt[0], mo = True )
    place.translationLock( SpinCt[2], True )
    place.rotationLock( SpinCt[2], True )
    place.rotationXLock( SpinCt[2], False )
    #
    place.optEnum( SpinCt[2], attr = 'wheelRoll', enum = 'CONTROL' )
    #
    cmds.addAttr( SpinCt[2], ln = 'radius' )
    cmds.setAttr( ( SpinCt[2] + '.radius' ), cb = True )
    cmds.setAttr( ( SpinCt[2] + '.radius' ), keyable = False )
    #
    cmds.addAttr( SpinCt[2], ln = 'roll' )
    cmds.setAttr( ( SpinCt[2] + '.roll' ), cb = True )
    cmds.setAttr( ( SpinCt[2] + '.roll' ), keyable = False )
    #
    place.addAttribute( [SpinCt[2]], ['rollMultiplier'], 0, 1, True, attrType = 'float' )
    #
    cmds.connectAttr( r1 + '.distance', SpinCt[2] + '.radius' )
    cmds.connectAttr( SpinCt[2] + '.roll', SpinCt[1] + '.rotateX' )
    #
    if exp:
        wheel_exp( ctrl = ContactCt[0] )
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

    return [Steer_F_LCt[1], ContactCt[2], PressureCt[2], PressureCt[1]]
    '''
    return [steer, ContactCt, PressureCt]


def wheel_roll_math( name = 'pathRadius1', distanceObjAttr = 'onPath_front.pathTraveled', radiusObjAttr = 'onPath_front.wheelRadius', outputObjAttr = 'onPath_front.wheelRoll', outputObjModAttr = 'onPath_front.wheelRollModulus' ):
    '''
    create nodes to calculate wheel rotation
    # ( ( $distance / ( pi2 * base_TopGrp.Radius ) ) * 360.0 ) # ROLL FORMULA
    '''
    #
    pi2 = 6.283185
    radiusPi2 = cmds.shadingNode( 'multDoubleLinear', name = name + '__radiusPi2_mult', asUtility = True )
    cmds.setAttr( radiusPi2 + '.input2', pi2 )
    cmds.connectAttr( radiusObjAttr, radiusPi2 + '.input1' )
    #
    radis = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '__distanceTraveled_radiusPi2_div' )
    cmds.setAttr( radis + '.operation', 2 )  # divide
    cmds.connectAttr( distanceObjAttr, radis + '.input1X' )
    cmds.connectAttr( radiusPi2 + '.output', radis + '.input2X' )
    #
    mlt360 = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + '__mlt360_mult' )
    cmds.connectAttr( radis + '.outputX', mlt360 + '.input1' )
    cmds.setAttr( mlt360 + '.input2', 360 )
    # output
    cmds.connectAttr( mlt360 + '.output', outputObjAttr )
    if outputObjModAttr:
        modulus_node( name = name, objectAttrDvdnd = outputObjAttr, objectAttrRmndr = outputObjModAttr, divisor = 360 )

    return [radiusPi2, radis, mlt360]


def wheel_connect( name = '', suffix = '', axle_jnt = '', master_move_controls = [], pivot_grp = '', tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], pressureMult = 0.03, X = 1.0 ):
    '''
    # expected wheel joint order
    # 'axle_front_L_jnt',    'wheel_front_steer_L_jnt',    'wheel_front_center_L_jnt',    'wheel_front_bottom_L_jnt',    'wheel_front_top_L_jnt',    'wheel_front_spin_L_jnt'
    '''
    #
    cmds.select( axle_jnt, hi = True )
    j = cmds.ls( sl = True )

    # whl = [steer, ContactCt, CenterCt]
    whl = wheel( master_move_controls = master_move_controls, axle = j[0], steer = j[1], center = j[2], bottom = j[3], top = j[4], spin = j[5],
                     tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, name = name, suffix = suffix, X = X, exp = False, pressureMult = pressureMult )
    place.translationYLock( whl[1][2], False )
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( name + '_contactLock_' + suffix, whl[1][2], whl[1][1], whl[1][0], j[1], pivot_grp, True, False, False, True, 'pivot', 1.0 )
    place.breakConnection( whl[1][1], 'tx' )
    place.breakConnection( whl[1][1], 'tz' )
    # steer
    if 'front' in name:
        cmds.orientConstraint( master_move_controls[2], j[1], mo = True )
        place.breakConnection( j[1], 'rx' )
        place.breakConnection( j[1], 'rz' )
    # whl   = [steer, ContactCt, CenterCt]
    place.smartAttrBlend( master = whl[2][2], slave = pivot_grp, masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whl[2][2], slave = whl[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )


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


def tire_pressure( obj = '', center = '', name = '', suffix = '', lattice = ( 2, 29, 5 ), pressureMult = 0.3 ):
    '''
    add tire pressure behaviour
    lattice = object local space (X, Y, Z)
    '''
    # group
    # g = cmds.group( name = name + '_clusterGrp_' + suffix, em = True )
    g = place.null2( name + '_clusterGrp_' + suffix, center, orient = False )
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
    point_A = cmds.xform( clusters[0], query = True, ws = True, rp = True )
    point_B = cmds.xform( clusters[1], query = True, ws = True, rp = True )
    lattice_row_gap = place.distance2Pts( point_A, point_B )  # guess, should find a way to measure it
    print( lattice_row_gap )
    cls = int( len( clusters ) / 2 ) - 3  # len( clusters ) - 1
    for i in range( cls ):
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
    weight = pressureMult
    weight_add = pressureMult * 0.5
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
    weight = lattice_row_gap
    weight_add = lattice_row_gap * 0.5
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


def piston( name = '', suffix = '', obj1 = '', obj2 = '', parent1 = '', parent2 = '', parentUp1 = '', parentUp2 = '', aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, 1], up2 = [0, 1, 0], X = 1, color = 'yellow' ):
    '''
    obj objects should have proper pivot point for objects to place and constrain correctly
    '''
    #
    shape = 'squareZup_ctrl'
    if aim1 == [0, 1, 0] or aim1 == [0, -1, 0]:
        shape = 'squareYup_ctrl'
    attr = 'Up_Vis'
    #
    distance = dsp.measureDis( obj1 = obj1, obj2 = obj2 ) * 0.5
    if suffix:
        suffix = '_' + suffix

    # add rig group for cleanliness
    piston_grp = cmds.group( name = name + '_' + suffix + '_AllGrp', em = True )
    cmds.parent( piston_grp, CONTROLS() )

    # obj1
    name1 = name + '_top' + suffix
    name1_Ct = place.Controller2( name1, obj1, True, shape, X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name1_Ct[0], piston_grp )
    cmds.pointConstraint( name1_Ct[4], obj1, mo = True )
    if parent1:
        cmds.parentConstraint( parent1, name1_Ct[0], mo = True )
    place.rotationLock( name1_Ct[2], True )

    # obj2
    name2 = name + '_bottom' + suffix
    name2_Ct = place.Controller2( name2, obj2, True, shape, X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    # return
    cmds.parent( name2_Ct[0], piston_grp )
    # rot = cmds.xform( name2_Ct[0], q = True, os = True, ro = True )
    # cmds.xform( name2_Ct[0], ws = True, ro = ( rot[0] + 180, 0, 0 ) )
    cmds.pointConstraint( name2_Ct[4], obj2, mo = True )
    if parent2:
        cmds.parentConstraint( parent2, name2_Ct[0], mo = True )
    place.rotationLock( name2_Ct[2], True )
    # return

    # obj1 up
    nameUp1 = name + '_topUp' + suffix
    nameUp1_Ct = place.Controller2( nameUp1, obj1, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp1_Ct[0], piston_grp )
    cmds.setAttr( nameUp1_Ct[1] + place.vector( up1 ), distance )
    if parentUp1:
        cmds.parentConstraint( parentUp1, nameUp1_Ct[0], mo = True )
    place.rotationLock( nameUp1_Ct[2], True )
    # vis
    place.addAttribute( name1_Ct[2], attr, 0, 1, False, 'long' )
    cmds.connectAttr( name1_Ct[2] + '.' + attr, nameUp1_Ct[0] + '.visibility' )

    # obj2 up
    nameUp2 = name + '_bottomUp' + suffix
    nameUp2_Ct = place.Controller2( nameUp2, obj2, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp2_Ct[0], piston_grp )
    cmds.setAttr( nameUp2_Ct[1] + place.vector( up2 ), distance )
    if parentUp2:
        cmds.parentConstraint( parentUp2, nameUp2_Ct[0], mo = True )
    place.rotationLock( nameUp2_Ct[2], True )
    # vis
    place.addAttribute( name2_Ct[2], attr, 0, 1, False, 'long' )
    cmds.connectAttr( name2_Ct[2] + '.' + attr, nameUp2_Ct[0] + '.visibility' )

    # aim
    cmds.aimConstraint( name2_Ct[4], obj1, wut = 'object', wuo = nameUp1_Ct[4], aim = aim1, u = up1, mo = True )
    cmds.aimConstraint( name1_Ct[4], obj2, wut = 'object', wuo = nameUp2_Ct[4], aim = aim2, u = up2, mo = True )

    return [name1_Ct, name2_Ct, nameUp1_Ct, nameUp2_Ct]


def spline( name = '', start_jnt = '', end_jnt = '', splinePrnt = '', splineStrt = '', splineEnd = '', startSkpR = False, endSkpR = False, color = 'yellow', X = 2 ):
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

    # attr control
    attr_Ct = place.Controller2( name, start_jnt, True, 'squareZup_ctrl', X * 7, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( attr_Ct[0], CONTROLS() )
    cmds.parentConstraint( splineStrt, attr_Ct[0], mo = True )
    # lock translation
    place.rotationLock( attr_Ct[2], True )
    place.translationLock( attr_Ct[2], True )

    # SPINE
    splineName = name
    splineSize = X * 1
    splineDistance = X * 4
    splineFalloff = 0

    spline = [start_jnt, end_jnt]
    # build spline
    SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
    cmds.select( spline )

    stage.splineStage( 4, colorScheme = color )
    # assemble
    splineAttr = attr_Ct[2]
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


def ik( name = '', start_jnt = '', end_jnt = '', start_parent = '', end_parent = '', pv_parent = '', X = 1.0, color = 'yellow' ):
    '''
    3 joint ik, for folding parts
    '''
    StartCt = place.Controller2( name, start_jnt, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parentConstraint( start_parent, StartCt[0], mo = True )
    cmds.pointConstraint( StartCt[4], start_jnt, mo = True )
    place.cleanUp( StartCt[0], Ctrl = True )
    #
    EndCt = place.Controller2( name, end_jnt, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parentConstraint( end_parent, EndCt[0], mo = True )
    place.cleanUp( EndCt[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv2( stJnt = start_jnt, endJnt = end_jnt, prefix = name, suffix = '', distance_offset = 0.0, orient = True, color = color, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( pv_parent, PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    #
    ik = app.create_ik2( stJnt = start_jnt, endJnt = end_jnt, pv = PvCt[4], parent = EndCt[4], name = name, suffix = '', setChannels = True )


def four_point_pivot( name = 'vhcl', parent = '', center = '', front = '', frontL = '', frontR = '', back = '', backL = '', backR = '', up = '', chassis_geo = [], X = 1, hide = False ):
    '''
    - main control, with 4 point pivot control and up vector
    - will assume single pivot if either left or right not given
    - assume translateZ is forward
    '''
    pvt = 'pivot'
    vis_attr = 'pivot_Vis'
    #
    if name:
        name = name + '_'
    #
    color = 'yellow'
    colorc = 'yellow'
    colorL = 'blue'
    colorR = 'red'
    #
    single_front_pivot = False
    single_back_pivot = False

    # skin
    if chassis_geo:
        skin( center, chassis_geo )

    # body grp
    BODY_GRP = cmds.group( name = name + 'Pvt_AllGrp', em = True )
    cmds.parent( BODY_GRP, CONTROLS() )

    # ##########
    # body
    nameb = name + 'pivot'
    body_Ct = place.Controller2( nameb, center, False, 'rectangleTallYup_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( body_Ct[0], BODY_GRP )
    cmds.parentConstraint( parent, body_Ct[0], mo = True )
    place.translationLock( body_Ct[2], True )
    place.translationYLock( body_Ct[2], False )
    place.addAttribute( body_Ct[2], vis_attr, 0, 1, False, 'long' )

    # ##########
    # front
    namef = name + 'front_' + pvt
    namef_Ct = place.Controller2( namef, front, False, 'L_ctrl', X * 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( namef_Ct[0], BODY_GRP )
    cmds.parentConstraint( namef_Ct[4], center, mo = True )
    cmds.parentConstraint( body_Ct[4], namef_Ct[0], mo = True )
    place.rotationLock( namef_Ct[2], True )
    place.translationZLock( namef_Ct[2], True )
    place.translationXLock( namef_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namef_Ct[0] + '.visibility' )

    # back
    nameb = name + 'back_' + pvt
    nameb_Ct = place.Controller2( nameb, back, False, 'invL_ctrl', X * 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameb_Ct[0], BODY_GRP )
    cmds.parentConstraint( body_Ct[4], nameb_Ct[0], mo = True )
    place.rotationLock( nameb_Ct[2], True )
    place.translationZLock( nameb_Ct[2], True )
    place.translationXLock( nameb_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, nameb_Ct[0] + '.visibility' )

    # up
    nameu = name + 'up_' + pvt
    nameu_Ct = place.Controller2( nameu, up, False, 'squareYup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameu_Ct[0], BODY_GRP )
    if hide:
        cmds.setAttr( nameu_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( nameu_Ct[4], up, mo = True )
    cmds.parentConstraint( body_Ct[4], nameu_Ct[0], mo = True )
    place.rotationLock( nameu_Ct[2], True )
    place.translationZLock( nameu_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, nameu_Ct[0] + '.visibility' )

    # ##########
    namefl_Ct = None
    namefr_Ct = None
    namefc_Ct = None  # center
    if frontL and frontR:  # dual front pivot
        # frontL
        namefl = name + 'front_L_' + pvt
        namefl_Ct = place.Controller2( namefl, frontL, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
        cmds.parent( namefl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefl_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefl_Ct[0], mo = True )
        place.rotationLock( namefl_Ct[2], True )
        # place.translationZLock( namefl_Ct[2], True )
        # place.translationXLock( namefl_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefl_Ct[0] + '.visibility' )

        # frontR
        namefr = name + 'front_R_' + pvt
        namefr_Ct = place.Controller2( namefr, frontR, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
        cmds.parent( namefr_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefr_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefr_Ct[0], mo = True )
        place.rotationLock( namefr_Ct[2], True )
        # place.translationZLock( namefr_Ct[2], True )
        # place.translationXLock( namefr_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefr_Ct[0] + '.visibility' )
    else:  # single front pivot
        single_front_pivot = True
        # front center
        namefc = name + 'front_C_' + pvt
        namefc_Ct = place.Controller2( namefc, front, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
        cmds.parent( namefc_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefc_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefc_Ct[0], mo = True )
        place.rotationLock( namefc_Ct[2], True )
        place.translationZLock( namefc_Ct[2], True )
        place.translationXLock( namefc_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefc_Ct[0] + '.visibility' )

    # ##########
    namebl_Ct = None
    namebr_Ct = None
    namebc_Ct = None  # center
    if backL and backR:  # dual back pivot
        # backL
        namebl = name + 'back_L_' + pvt
        namebl_Ct = place.Controller2( namebl, backL, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
        cmds.parent( namebl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebl_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebl_Ct[0], mo = True )
        place.rotationLock( namebl_Ct[2], True )
        # place.translationZLock( namebl_Ct[2], True )
        # place.translationXLock( namebl_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebl_Ct[0] + '.visibility' )

        # backR
        namebr = name + 'back_R_' + pvt
        namebr_Ct = place.Controller2( namebr, backR, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
        cmds.parent( namebr_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebr_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebr_Ct[0], mo = True )
        place.rotationLock( namebr_Ct[2], True )
        # place.translationZLock( namebr_Ct[2], True )
        # place.translationXLock( namebr_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebr_Ct[0] + '.visibility' )
    else:  # single back pivot
        # back center
        single_back_pivot = True
        namebc = name + 'back_C_' + pvt
        namebc_Ct = place.Controller2( namebc, back, False, 'boxZup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
        cmds.parent( namebl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebc_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebc_Ct[0], mo = True )
        place.rotationLock( namebc_Ct[2], True )
        place.translationZLock( namebc_Ct[2], True )
        place.translationXLock( namebc_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebc_Ct[0] + '.visibility' )

    # ##########
    # aim
    cmds.aimConstraint( nameb_Ct[4], namef_Ct[4], wut = 'object', wuo = nameu_Ct[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( namef_Ct[3], True )

    # ##########
    # pivot connections
    # 5 blend attr nodes
    # 2 multdiv nodes

    # front pivots ( left/ right ) ty blend
    if not single_front_pivot:
        frontBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_Blend' )
        cmds.setAttr( frontBlend + '.attributesBlender', 0.5 )
        # front left
        place.smartAttrBlend( master = namefl_Ct[2], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[3], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[4], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        # front right
        place.smartAttrBlend( master = namefr_Ct[2], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[3], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[4], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        cmds.connectAttr( frontBlend + '.output', namef_Ct[1] + '.translateY' )
        place.smartAttrBlend( master = frontBlend, slave = nameu_Ct[1], masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 0.5, reverse = False )  # add influence ty of up grp control
        # cmds.connectAttr( frontBlend + '.output', nameu_Ct[1] + '.translateY' )
    else:
        place.smartAttrBlend( master = namefc_Ct[2], slave = namef_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namefc_Ct[3], slave = namef_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namefc_Ct[4], slave = namef_Ct[4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )

    # back pivots ( left/ right ) ty blend
    if not single_back_pivot:
        backBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_Blend' )
        cmds.setAttr( backBlend + '.attributesBlender', 0.5 )
        # back left
        place.smartAttrBlend( master = namebl_Ct[2], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[3], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[4], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        # back right
        place.smartAttrBlend( master = namebr_Ct[2], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[3], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[4], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        cmds.connectAttr( backBlend + '.output', nameb_Ct[1] + '.translateY' )
        place.smartAttrBlend( master = backBlend, slave = nameu_Ct[1], masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 0.5, reverse = False )  # add influence ty of up grp control
        # cmds.connectAttr( backBlend + '.output', nameu_Ct[1] + '.translateY' )
    else:
        place.smartAttrBlend( master = namebc_Ct[2], slave = nameb_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namebc_Ct[3], slave = nameb_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namebc_Ct[4], slave = nameb_Ct[4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        # cmds.connectAttr( namebc_Ct[2] + '.translateY', nameb_Ct[1] + '.translateY' )

    # ###########
    # blend front up vector pivots (l/r) - prep nodes, ty to blend into tx of up vector control, left side converted to negative for neg tx
    frontUpBlend = None
    if not single_front_pivot:
        frontUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_up_Blend' )  # recieves 2 ty inputs, one converted to negative
        cmds.setAttr( frontUpBlend + '.attributesBlender', 0.5 )  # each gets a weights of half
        # mltp only for left side, invert value
        # frontlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_front_l_mlt' )
        # cmds.setAttr( frontlmlt + '.operation', 1 )  # multiply
        # cmds.setAttr( frontlmlt + '.input2Y', -1 )
        # new
        place.smartAttrBlend( master = namefl_Ct[2], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[3], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[4], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # insert second weighted connection
        #
        place.smartAttrBlend( master = namefr_Ct[2], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[3], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[4], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection

        # old
        # cmds.connectAttr( namefr_Ct[2] + '.translateY', frontUpBlend + '.input[0]' )  # right to blend
        # cmds.connectAttr( namefl_Ct[2] + '.translateY', frontlmlt + '.input1Y' )  # left to negative node
        # cmds.connectAttr( frontlmlt + '.outputY', frontUpBlend + '.input[1]' )  # negative node to blend
    else:
        pass

    # blend back up vector pivots (l/r) - prep nodes, ty to blend into tx of up vector control, left side converted to negative for neg tx
    backUpBlend = None
    if not single_back_pivot:
        backUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_up_Blend' )  # recieves 2 ty inputs, one converted to negative
        cmds.setAttr( backUpBlend + '.attributesBlender', 0.5 )  # each gets a weights of half
        # mltp only for left side, invert value
        # backlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_back_l_mlt' )
        # cmds.setAttr( backlmlt + '.operation', 1 )  # multiply
        # cmds.setAttr( backlmlt + '.input2Y', -1 )
        # new
        place.smartAttrBlend( master = namebl_Ct[2], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[3], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[4], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # insert second weighted connection
        # back right
        place.smartAttrBlend( master = namebr_Ct[2], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[3], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[4], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection

        # old
        # cmds.connectAttr( namebr_Ct[2] + '.translateY', backUpBlend + '.input[0]' )  # right to blend
        # cmds.connectAttr( namebl_Ct[2] + '.translateY', backlmlt + '.input1Y' )  # left to negative node
        # cmds.connectAttr( backlmlt + '.outputY', backUpBlend + '.input[1]' )  # negative node to blend
    else:
        pass

    # blend result of front/back translateY values to up translateX
    result = []
    if not single_front_pivot  or not single_back_pivot:  # make sure at least one pivot is dual
        upBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'up_Blend' )
        cmds.setAttr( upBlend + '.attributesBlender', 0.5 )
        #
        if not single_front_pivot:
            cmds.connectAttr( frontUpBlend + '.output', upBlend + '.input[0]' )
            result.append( namefl_Ct )
            result.append( namefr_Ct )
        else:
            result.append( namefc_Ct )
        #
        if not single_back_pivot:
            cmds.connectAttr( backUpBlend + '.output', upBlend + '.input[1]' )
            result.append( namebl_Ct )
            result.append( namebr_Ct )
        else:
            result.append( namebc_Ct )
        #
        cmds.connectAttr( upBlend + '.output', nameu_Ct[1] + '.translateX' )
    else:
        return [namefc_Ct, namebc_Ct]

    result.append( namef_Ct )
    result.append( nameb_Ct )
    return result
    # return [namefl_Ct[2], namefr_Ct[2], namebl_Ct[2], namebr_Ct[2]]


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
        place.translationXLock( name_Ct[2], False )
    if translations[1]:
        place.translationYLock( name_Ct[2], False )
    if translations[2]:
        place.translationZLock( name_Ct[2], False )

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


def dynamic_target( name = 'chassis', root = 'root_jnt', target = 'up_jnt', front = 'front_jnt', constrainObj = 'chassis_jnt', parentObj = 'move_Grp', attrObj = 'move', aim = [0, 1, 0], up = [0, 0, 1], X = 10.0 ):
    '''
    name          = chassis      string
    root          = root_jnt,    crv start
    target        = up_jnt,      crv end, aim vector
    front         = front_jnt,   up vector
    constrainObj  = chassis_jnt, object to aim at target
    parentObj     = move_Grp,    parent of dynamics
    attrObj       = move,        objects receives dynamic attributes
    X             = 10.0         scale of controls
    '''
    # curve
    crv = dnm.makeCurve( start = root, end = target, name = name + '_dynamicTargetCrv', points = 4 )

    # aim control
    base = name + '_dynamicBase'
    base_Ct = place.Controller2( base, root, True, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( base_Ct[0], CONTROLS() )
    cmds.setAttr( base_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( base_Ct[4], constrainObj, mo = True )
    # cmds.parentConstraint( parentObj, base_Ct[0], mo = True )
    # aim control
    a = name + '_dynamicTarget'
    aim_Ct = place.Controller2( a, target, True, 'diamondYup_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( aim_Ct[0], CONTROLS() )
    place.rotationLock( aim_Ct[2], True )
    # up control
    u = name + '_dynamicUp'
    up_Ct = place.Controller2( u, front, True, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( up_Ct[0], CONTROLS() )
    # cmds.parentConstraint( parentObj, up_Ct[0], mo = True )
    # move for stability
    point_A = cmds.xform( aim_Ct[0], query = True, ws = True, rp = True )
    point_B = cmds.xform( base_Ct[0], query = True, ws = True, rp = True )
    d = place.distance2Pts( point_A, point_B )
    cmds.setAttr( up_Ct[1] + '.translateZ', d * 10 )
    cmds.setAttr( up_Ct[0] + '.visibility', 0 )

    # constrain base to target
    cmds.aimConstraint( aim_Ct[4], base_Ct[1], wut = 'object', wuo = up_Ct[4], aim = aim, u = up, mo = True )

    # attach aim
    mp = dnm.attachObj( obj = aim_Ct[0], upObj = up_Ct[4], crv = crv, position = 1.0 )

    # make dynamic
    # [ follicle_Grp, dynGrp, sharedDynGrp ]
    grps = dnm.makeDynamic( parentObj = '', attrObj = aim_Ct[2], mstrCrv = crv )
    follicle_Grp = grps[0]
    place.cleanUp( grps[1], World = True )
    place.cleanUp( grps[2], World = True )

    return [base_Ct, aim_Ct, up_Ct, follicle_Grp ]


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
    # cmds.setAttr( MasterCt[2] + '.overrideColor', 23 )

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
    crvInfo = None
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
        if layer == 0:
            crvInfo = cmds.arclen( pth, ch = True, n = ( pth + '_arcLength' ) )
            #
            # crvLength = cmds.getAttr(crvInfo + '.arcLength')
            # dvd = cmds.shadingNode('multiplyDivide', au=True, n=(curve + '_scale'))
            #
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
    color = 9
    i = 1
    Ctrls = []
    # CtrlCtGrps = []
    CtrlGrps = []
    for handle in cluster_layers[0]:
        #
        cnt = place.Controller( 'point' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ), handle, orient = False, shape = 'splineStart_ctrl', size = 60 * X, color = color, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'brown' )
        cntCt = cnt.createController()
        # cmds.setAttr( handle + '.visibility', 0 )
        cmds.parentConstraint( MasterCt[4], cntCt[0], mo = True )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        Ctrls.append( cntCt[2] )
        # CtrlCtGrps.append( cntCt[1] )
        CtrlGrps.append( cntCt[4] )
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1

    # guides
    guideGp = cmds.group( em = True, name = 'path_guideGrp' )
    for i in range( len( CtrlGrps ) - 1 ):
        gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
        place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
        cmds.parent( gd[0], guideGp )
        cmds.parent( gd[1], guideGp )
        place.cleanUp( guideGp, World = True )

    # path
    s = 0.0
    travel = 'travel'
    spacing = 'spacing'
    frontTwist = 'frontTwist'
    upTwist = 'upTwist'
    sideTwist = 'sideTwist'
    wheelRadius = 'wheelRadius'
    pathLength = 'pathLength'
    pathTraveled = 'pathTraveled'
    wheelRoll = 'wheelRoll'
    wheelRollMod = 'wheelRollModulus'
    msgPths = 'paths'
    msgMp = 'motionPath'
    # vehicle on path, front of vehicle
    opf = 'onPath_front'
    opfCt = place.Controller2( opf, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.parent( opfCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True )
    place.rotationLock( opfCt[2], True )
    misc.optEnum( opfCt[2], attr = 'path', enum = 'CONTROL' )
    misc.addAttribute( [opfCt[2]], [travel], 0.0, 10.0, True, 'float' )
    cmds.setAttr( opfCt[2] + '.' + travel, 0.01 )
    # misc.addAttribute( [opfCt[2]], [spacing], -10.0, 10.0, True, 'float' )
    misc.addAttribute( [opfCt[2]], [frontTwist], -360, 360, True, 'float' )
    misc.addAttribute( [opfCt[2]], [upTwist], -360, 360, True, 'float' )
    misc.addAttribute( [opfCt[2]], [sideTwist], -360, 360, True, 'float' )
    misc.optEnum( opfCt[2], attr = 'wheelMath', enum = 'COMPUTE' )
    misc.addAttribute( [opfCt[2]], [wheelRadius], 0.001, 1000, False, 'float' )
    # cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.addAttr( opfCt[2], ln = pathLength, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathLength , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathLength , k = False )
    misc.hijackAttrs( opfCt[2], crvInfo, pathLength, 'arcLength', set = False, default = None, force = True )
    cmds.addAttr( opfCt[2], ln = pathTraveled, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRoll, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRollMod, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , k = False )
    # cmds.setAttr( opfCt[2] + '.' + spacing, -0.15 )
    # vehicle on path, back of vehicle
    opb = 'onPath_back'
    opbCt = place.Controller2( opb, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.addAttr( opbCt[2], ln = msgPths, at = 'message' )
    cmds.addAttr( opbCt[2], ln = msgMp, at = 'message' )
    cmds.parent( opbCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )
    place.rotationLock( opbCt[2], True )
    misc.optEnum( opbCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    # misc.addAttribute( [opbCt[2]], ['weightedPath'], 0, 1, True, 'float' )
    # cmds.setAttr( opbCt[2] + '.weightedPath', 0.2 )
    misc.addAttribute( [opbCt[2]], [spacing], -10.0, 10.0, True, 'float' )
    cmds.setAttr( opbCt[2] + '.' + spacing, -0.02 )
    # vehicle on path, top of vehicle
    opu = 'onPath_up'
    opuCt = place.Controller2( opu, MasterCt[4], False, 'loc_ctrl', X * 50, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.parent( opuCt[0], CONTROLS )
    cmds.setAttr( opuCt[0] + '.ty', X * 100 )
    cmds.setAttr( opuCt[0] + '.visibility', 0 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )
    # aim
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( opfCt[3], True )

    # front - attach to path
    motpth_f = cmds.pathAnimation( opfCt[1], name = 'front_motionPath' , c = paths[0], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_f + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_f + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_f + '.' + sideTwist )
    cmds.setAttr( opfCt[2] + '.' + frontTwist, 180 )
    cmds.setAttr( opfCt[2] + '.' + sideTwist, 90 )
    # back - attach to path
    motpth_b = cmds.pathAnimation( opbCt[1], name = 'back_motionPath' , c = paths[2], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.addAttr( motpth_b, ln = msgMp, at = 'message' )
    cmds.connectAttr( opbCt[2] + '.' + msgMp, motpth_b + '.' + msgMp )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_b + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_b + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_b + '.' + sideTwist )
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
    cmds.connectAttr( opbCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )
    # distance traveled
    uvlen = cmds.shadingNode( 'multDoubleLinear', name = 'uValuePathLen_mult', asUtility = True )
    cmds.connectAttr( opfCt[2] + '.pathLength', uvlen + '.input1' )
    cmds.connectAttr( motpth_f + '.uValue', uvlen + '.input2' )
    cmds.connectAttr( uvlen + '.output', opfCt[2] + '.' + pathTraveled )
    # wheel roll
    wheel_roll_math( distanceObjAttr = opfCt[2] + '.' + pathTraveled, radiusObjAttr = opfCt[2] + '.' + wheelRadius, outputObjAttr = opfCt[2] + '.' + wheelRoll )

    # smooth display
    cmds.select( paths )
    cmds.displaySmoothness( pointsWire = 32 )

    # message, for switching path connection in script later
    for p in paths:
        shape = path_shape( p )
        cmds.addAttr( shape, ln = msgPths, at = 'message' )
        cmds.connectAttr( opbCt[2] + '.' + msgPths, shape + '.' + msgPths )

    # message for path controllers, meant to attach all controls with geo constraint to ground plane
    msg = 'control'
    cmds.addAttr( MasterCt[2], ln = msg, at = 'message' )
    for g in Ctrls:
        cmds.addAttr( g, ln = msg, at = 'message' )
        cmds.connectAttr( MasterCt[2] + '.' + msg, g + '.' + msg )

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


def path_shape( curve = '' ):
    '''
    return shape node
    '''
    shapes = cmds.listRelatives( curve, s = 1 )  # s = shapes
    if shapes:
        for s in shapes:
            if 'Orig' not in s:
                return s
    print( 'no shapes found' )
    return None


def path_switch():
    '''
    uses selection
    assumes selection has specific message connections
    '''
    # object on path
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 1:
        sel = sel[0]
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    if 'onPath_back' in sel:
        # motionPath node
        motionPathNode = cmds.listConnections( sel + '.motionPath' )
        if motionPathNode:
            motionPathNode = motionPathNode[0]
        else:
            motionPathNode = None
        # path shape nodes
        pathShapes = cmds.listConnections( sel + '.paths' )
        if pathShapes:
            pathShapes.sort()
        else:
            pathShapes = None
        # current path
        current_path = cmds.listConnections( motionPathNode + '.geometryPath' )
        if current_path:
            current_path = current_path[0]
        else:
            current_path = None
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    # iterate to new
    if motionPathNode and pathShapes and current_path:
        i = 0
        for i in range( len( pathShapes ) ):
            if pathShapes[i] == current_path:
                if i + 1 <= len( pathShapes ) - 1:
                    cmds.connectAttr( pathShapes[i + 1] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[i + 1] )
                else:
                    cmds.connectAttr( pathShapes[0] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[0] )
            else:
                # print( 'no match', pathShapes[i], current_path )
                pass
    else:
        message( 'Connections missing, aborted', warning = True )


def car_to_ground():
    '''
    attach selected namespace(vehicle) to selected ground plane
    '''
    pivots = [
    'chassis_front_L_pivot',
    'chassis_front_R_pivot',
    'chassis_back_L_pivot',
    'chassis_back_R_pivot'
    ]
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        ground = sel[1]
        for p in pivots:
            cmds.pointConstraint( veh_ns + ':move', veh_ns + ':' + p, mo = True )
            cmds.geometryConstraint( ground, veh_ns + ':' + p )
    else:
        message( 'Select 2 objects: vehicle 1st, ground 2nd', warning = True )


def path_to_ground():
    '''
    master of path should be selected
    is assumed it has message connections to all path controls
    iterate and constrain each control
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        controls = cmds.listConnections( sel[0] + '.control' )
        if controls:
            # namespaces
            veh_ns = sel[0].split( ':' )[0]
            ground = sel[1]
            for c in controls:
                cmds.geometryConstraint( ground, c )
        else:
            message( 'Couldnt find path controls on first object:' + sel[0], warning = True )
    else:
        message( 'Select 2 objects: expecting master control of path and ground geo as selection.', warning = True )


def car_to_path( wheels = ['wheel_front_spin_L', 'wheel_front_spin_R', 'wheel_back_spin_L', 'wheel_back_spin_R'], mod = True ):
    '''
    select controls first and path object with namespace last
    assumes controls are sorted in proper order
    adds modulus node in between roll connection
    '''
    # objects
    path_obj = 'onPath_front_Grp'
    path_steer = 'onPath_front'
    path_radius = 'onPath_front.wheelRadius'
    path_roll = 'onPath_front.wheelRoll'
    path_rollMod = 'onPath_front.wheelRollModulus'
    veh_obj = 'move_CtGrp'
    veh_offset = 'move_Offset'
    veh_steer = 'steer_CtGrp'

    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        path_ns = sel[1].split( ':' )[0]
        # objects
        path_obj = path_ns + ':' + path_obj
        path_steer = path_ns + ':' + path_steer
        veh_obj = veh_ns + ':' + veh_obj
        veh_steer = veh_ns + ':' + veh_steer
        veh_offset = veh_ns + ':' + veh_offset
        # attrs
        path_radius = path_ns + ':' + path_radius
        path_roll = path_ns + ':' + path_roll
        path_rollMod = path_ns + ':' + path_rollMod
        #
        if cmds.objExists( path_obj ) and cmds.objExists( veh_obj ):
            # wheel spin
            for wheel in wheels:
                veh_radius = veh_ns + ':' + wheel + '.radius'
                veh_roll = veh_ns + ':' + wheel + '.roll'
                cmds.connectAttr( veh_radius, path_radius, f = True )  # should only connect once per radius change, this breaks previous connections, should add smarter logic
                if mod:
                    cmds.connectAttr( path_rollMod, veh_roll )
                else:
                    cmds.connectAttr( path_roll, veh_roll )
                # modulus_node( name = wheel, objectAttrDvdnd = path_roll, objectAttrRmndr = veh_roll, divisor = 360 )
            # amount to shift offset control
            point_A = cmds.xform( veh_obj, query = True, ws = True, rp = True )
            point_B = cmds.xform( veh_steer, query = True, ws = True, rp = True )
            distance = place.distance2Pts( point_A, point_B )
            print( distance )
            cmds.setAttr( veh_offset + '.translateZ', distance * -1 )
            # attach
            cmds.parentConstraint( path_obj, veh_obj, mo = False )
            cmds.parentConstraint( path_steer, veh_steer, mo = False )
        else:
            message( 'Expected objects dont exist', warning = True )
            print( path_obj, veh_obj )
    else:
        message( 'Select 2 objects: vehicle 1st, path 2nd', warning = True )


def car( name = '', X = 1.1 ):
    '''
    chassis
    4 wheels
    '''
    #
    mirror_jnts()

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    # SteerCt[4] = returned only if given as argument, otherwise this is returned: MasterCt[4], MoveCt[4]
    master_move_controls = vehicle_master( masterX = X * 8, moveX = X * 10 )
    # [base_Ct, aim_Ct, up_Ct, follicle_Grp]
    Ct = dynamic_target( name = 'chassis', root = 'root_jnt', target = 'up_jnt', front = 'front_jnt', constrainObj = 'chassis_jnt', parentObj = 'move_Grp', attrObj = 'move', aim = [0, 1, 0], up = [0, 0, 1], X = 100.0 )
    # return
    place.cleanUp( 'Jeep_Wrangler', Body = True )

    # mass to pivot, body
    chassis_joint = 'chassis_jnt'
    chassis_geo = get_geo_list( chassis = True )
    skin( chassis_joint, chassis_geo )
    # pivot_controls = [frontl, frontr, backl, backr, front, back] # entire controller hierarchy [0-4]
    pivot_controls = four_point_pivot( name = 'chassis', parent = master_move_controls[1], center = Ct[0][0], front = 'front_jnt', frontL = 'wheel_front_bottom_L_jnt', frontR = 'wheel_front_bottom_R_jnt', back = 'back_jnt', backL = 'wheel_back_bottom_L_jnt', backR = 'wheel_back_bottom_R_jnt', up = 'up_jnt', chassis_geo = '', X = X * 2 )
    cmds.parentConstraint( pivot_controls[4][4], Ct[2][0], mo = True )  # front vector for dynamic rig
    cmds.parentConstraint( pivot_controls[4][4], Ct[3], mo = True )  # follicle_Grp
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( 'dynamic', Ct[1][2], Ct[1][1], Ct[1][0], pivot_controls[4][4], Ct[1][0], False, False, True, False, 'dynamic', 1.0 )

    # return
    # wheel front L
    tire_geo = get_geo_list( tire_front_l = True )
    rim_geo = get_geo_list( rim_front_l = True )
    caliper_geo = get_geo_list( caliper_front_l = True )
    wheel_connect( name = 'wheel_front', suffix = 'L', axle_jnt = 'axle_front_L_jnt', master_move_controls = [master_move_controls[0], chassis_joint, master_move_controls[2]], pivot_grp = pivot_controls[0][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # wheel front R
    tire_geo = get_geo_list( tire_front_r = True )
    rim_geo = get_geo_list( rim_front_r = True )
    caliper_geo = get_geo_list( caliper_front_r = True )
    wheel_connect( name = 'wheel_front', suffix = 'R', axle_jnt = 'axle_front_R_jnt', master_move_controls = [master_move_controls[0], chassis_joint, master_move_controls[2]], pivot_grp = pivot_controls[1][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # wheel back L
    tire_geo = get_geo_list( tire_back_l = True )
    rim_geo = get_geo_list( rim_back_l = True )
    caliper_geo = get_geo_list( caliper_back_l = True )
    wheel_connect( name = 'wheel_back', suffix = 'L', axle_jnt = 'axle_back_L_jnt', master_move_controls = [master_move_controls[0], chassis_joint, master_move_controls[2]], pivot_grp = pivot_controls[2][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # wheel back R
    tire_geo = get_geo_list( tire_back_r = True )
    rim_geo = get_geo_list( rim_back_r = True )
    caliper_geo = get_geo_list( caliper_back_r = True )
    wheel_connect( name = 'wheel_back', suffix = 'R', axle_jnt = 'axle_back_R_jnt', master_move_controls = [master_move_controls[0], chassis_joint, master_move_controls[2]], pivot_grp = pivot_controls[3][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )

    fix_normals()


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


def modulus_node( name = 'wheelRoll', objectAttrDvdnd = '', objectAttrRmndr = '', divisor = None ):
    '''
    create mod node
    create output mod value objAttrRmndr
    '''
    # attrs
    divdA = 'dividend'
    divsA = 'divisor'
    rsltA = 'result'
    rsltIntA = 'resultInteger'
    qtntA = 'quotient'
    rmndA = 'remainderRaw'
    rmndPosA = 'remainderProcessed'  # force positive
    rmndDgrsA = 'remainder'
    attrList = [divdA, divsA, rsltA, rsltIntA, qtntA, rmndA, rmndPosA, rmndDgrsA]
    mod = '__modulus'

    # mod object
    modNode = cmds.group( name = name + mod, em = True )
    place.translationLock( modNode, True )
    place.rotationLock( modNode, True )
    place.scaleLock( modNode, True )
    # add attrs
    for attr in attrList:
        if 'Integer' in attr:
            cmds.addAttr( modNode, ln = attr, at = 'long', h = False )
        else:
            cmds.addAttr( modNode, ln = attr, at = 'float', h = False )
        cmds.setAttr( modNode + '.' + attr , k = False )
        cmds.setAttr( modNode + '.' + attr , cb = False )
    #
    cmds.setAttr( modNode + '.' + divdA , cb = True )
    cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + divsA , cb = True )
    cmds.addAttr( modNode + '.' + divsA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + qtntA , cb = True )
    cmds.setAttr( modNode + '.' + rmndDgrsA , cb = True )
    cmds.setAttr( modNode + '.visibility' , k = False )
    cmds.setAttr( modNode + '.visibility' , cb = False )

    # connect inputs
    if objectAttrDvdnd:
        cmds.connectAttr( objectAttrDvdnd, modNode + '.' + divdA )
    else:
        cmds.setAttr( modNode + '.' + divdA, 1 )
    if divisor:
        cmds.setAttr( modNode + '.' + divsA, divisor )
    else:
        cmds.setAttr( modNode + '.' + divsA, 1 )
    # connect output
    if objectAttrRmndr:
        cmds.connectAttr( modNode + '.' + rmndDgrsA, objectAttrRmndr )

    # div , wheel rotation / 360
    ddd = cmds.shadingNode( 'multiplyDivide', au = True, n = name + mod + '__dividendDivisor_div' )
    cmds.setAttr( ddd + '.operation', 2 )  # divide
    cmds.connectAttr( modNode + '.' + divdA, ddd + '.input1X' )
    cmds.connectAttr( modNode + '.' + divsA, ddd + '.input2X' )

    # result
    cmds.connectAttr( ddd + '.outputX', modNode + '.' + rsltA )
    # result integer
    cmds.connectAttr( modNode + '.' + rsltA, modNode + '.' + rsltIntA )

    # remainder part a
    rra = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderRaw_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rra + '.input1' )
    # remainder part b
    rinm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__remainderRaw_mult' )
    cmds.connectAttr( modNode + '.' + rsltIntA, rinm + '.input1' )
    cmds.setAttr( rinm + '.input2', -1 )
    cmds.connectAttr( rinm + '.output', rra + '.input2' )
    # remainder part c
    cmds.connectAttr( rra + '.output', modNode + '.' + rmndA )

    # condition, force remainder to positive part a
    cndtn = cmds.shadingNode( 'condition', au = True, n = name + mod + '__remainderProcess_cnd' )
    cmds.setAttr( cndtn + '.operation', 4 )  # less than
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.firstTerm' )
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.colorIfFalseR' )
    # condition true, flip remainder, part b
    rfa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderProcess_add' )
    cmds.setAttr( rfa + '.input2', 1 )
    cmds.connectAttr( modNode + '.' + rmndA, rfa + '.input1' )
    cmds.connectAttr( rfa + '.output', cndtn + '.colorIfTrueR' )
    # condition c, output positive remainder
    cmds.connectAttr( cndtn + '.outColorR', modNode + '.' + rmndPosA )

    # remainder to degrees
    rdm = cmds.createNode( 'multDoubleLinear', name = name + mod + '__remainder_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rdm + '.input1' )
    cmds.connectAttr( modNode + '.' + divsA, rdm + '.input2' )
    cmds.connectAttr( rdm + '.output', modNode + '.' + rmndDgrsA )

    # quotient result minus remainder
    rqa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__quotient_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rqa + '.input1' )
    # remainder part b
    rnm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__quotient_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rnm + '.input1' )
    cmds.setAttr( rnm + '.input2', -1 )
    cmds.connectAttr( rnm + '.output', rqa + '.input2' )
    # remainder part c
    cmds.connectAttr( rqa + '.output', modNode + '.' + qtntA )

    place.cleanUp( modNode, World = True )
    return modNode


def get_geo_list( chassis = False,
                  tire_front_l = False, rim_front_l = False, caliper_front_l = False,
                  tire_front_r = False, rim_front_r = False, caliper_front_r = False,
                  tire_back_l = False, rim_back_l = False, caliper_back_l = False,
                  tire_back_r = False, rim_back_r = False, caliper_back_r = False,
                  all = False ):
    '''
    geo members
    '''
    #
    geo_chassis = [
    'frontFender1',
    'polySurface543',
    'Jeep_Exterior_Group|Jeep_Body|Jeep_Grill',
    'frontFender',
    'polySurface784',
    'back_lugnuts',
    'back_rim',
    'backTire',
    'Jeep_Logo',
    'pCube1',
    'Jeep_DoorHandles',
    'Jeep_Undercarriage_Group|Jeep_Undercarriage',
    'Jeep_Cloth_Wallace',
    'Jeep_Cloth_Techtonic',
    'Jeep_Seats_Group|Jeep_Chrome',
    'Jeep_Radiator',
    'polySurface541',
    'polySurface540',
    'Jeep_Black_Rubber',
    'Jeep_Black_Vinyl',
    'Jeep_Seatbelts',
    'Jeep_Black_Carpet',
    'Jeep_Interior_Group|Jeep_Glass',
    'Jeep_Anodized_Metal',
    'Jeep_Interior_Group|Jeep_Body',
    'Jeep_Windshield_Trim',
    'Jeep_Exterior_Group|Jeep_Undercarriage',
    'Jeep_Rubber',
    'Jeep_Headlight_Red',
    'Jeep_Headlight_Amber',
    'Jeep_Headlight_Chrome',
    'Jeep_Exterior_Group|Jeep_Glass',
    'polySurface524',
    'polySurface29',
    'polySurface27',
    'polySurface26',
    'polySurface25',
    'polySurface24',
    'polySurface23',
    'polySurface22',
    'polySurface21',
    'polySurface20',
    'polySurface19',
    'polySurface18',
    'polySurface15',
    'polySurface14',
    'polySurface13',
    'polySurface12',
    'polySurface11',
    'polySurface10',
    'polySurface9',
    'polySurface8',
    'polySurface7'
    ]

    #
    geo_tire_front_l = ['Jeep_Tires_Front_Left']
    geo_rim_front_l = [
    'Jeep_Rims_Front_Left',
    'Jeep_Chrome_Front_Left'
    ]
    geo_caliper_front_l = [
    'Jeep_Brakes_Front_Left',
    'Grp_FLTyre|Grp_DiscBrake|DiscBrake'
    ]

    #
    geo_tire_front_r = ['Jeep_Tires_Front_Right']
    geo_rim_front_r = [
    'Jeep_Rims_Front_Right',
    'Jeep_Chrome_Front_Right'
    ]
    geo_caliper_front_r = [
    'Jeep_Brakes_Front_Right',
    'Grp_FRTyre|Grp_DiscBrake|DiscBrake'
    ]

    #
    geo_tire_back_l = ['LR_tire']
    geo_rim_back_l = [
    'LR_rim',
    'LR_lugnuts'
    ]
    geo_caliper_back_l = [
    'polySurface548'
    ]

    #
    geo_tire_back_r = ['RR_tire']
    geo_rim_back_r = [
    'RR_rim',
    'RR_lugnuts'
    ]
    geo_caliper_back_r = [
    'Grp_BRTyre|Grp_DiscBrake|DiscBrake'
    ]
    #
    a = []

    # chassis
    if chassis:
        return geo_chassis

    # front l
    if tire_front_l:
        return geo_tire_front_l
    if rim_front_l:
        return geo_rim_front_l
    if caliper_front_l:
        return geo_caliper_front_l

    # front r
    if tire_front_r:
        return geo_tire_front_r
    if rim_front_r:
        return geo_rim_front_r
    if caliper_front_r:
        return geo_caliper_front_r

    # back l
    if tire_back_l:
        return geo_tire_back_l
    if rim_back_l:
        return geo_rim_back_l
    if caliper_back_l:
        return geo_caliper_back_l

    # back r
    if tire_back_r:
        return geo_tire_back_r
    if rim_back_r:
        return geo_rim_back_r
    if caliper_back_r:
        return geo_caliper_back_r

    # all
    if all:
        for g in geo_chassis:
            a.append( g )
        for g in geo_tire_front_l:
            a.append( g )
        for g in geo_rim_front_l:
            a.append( g )
        for g in geo_caliper_front_l:
            a.append( g )
        for g in geo_tire_front_r:
            a.append( g )
        for g in geo_rim_front_r:
            a.append( g )
        for g in geo_caliper_front_r:
            a.append( g )
        for g in geo_tire_back_l:
            a.append( g )
        for g in geo_rim_back_l:
            a.append( g )
        for g in geo_caliper_back_l:
            a.append( g )
        for g in geo_tire_back_r:
            a.append( g )
        for g in geo_rim_back_r:
            a.append( g )
        for g in geo_caliper_back_r:
            a.append( g )
        return a
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
