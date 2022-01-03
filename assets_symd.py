import imp
import os

from atom_face_lib import skn
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
import webrImport as web

#
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
jnt = web.mod( 'atom_joint_lib' )
anm = web.mod( "anim_lib" )
vhl = web.mod( 'vehicle_lib' )
app = web.mod( "atom_appendage_lib" )
ss = web.mod( "selectionSet_lib" )
cn = web.mod( 'constraint_lib' )


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
    geo = get_geo_list( name = 'kingAir', ns = 'geo', tire_front_l = True, tire_back_l = True, tire_back_r = True )
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
    'back_L_jnt',
    'front_L_jnt',
    'chassis_L_jnt',
    'axle_back_L_jnt',
    'landing_doorA_00_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = True )


def king_air( X = 12, ns = 'geo', ref_geo = 'P:\\SYMD\\assets\\veh\\kingAirB200\\model\\maya\\scenes\\kingAirB200_model_v005.ma' ):
    '''
    build plane
    '''
    name = 'kingAir'
    # ref geo
    if ns and ref_geo:
        vhl.reference_geo( ns = ns, path = ref_geo )
    #
    mirror_jnts()

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vhl.vehicle_master( masterX = X * 10, moveX = X * 9, steerParent = 'landingGear_retract_jnt' )
    # move
    move = 'move'
    # mass to pivot, chassis
    chassis_joint = 'chassis_jnt'
    chassis_geo = get_geo_list( chassis = True )
    vhl.skin( chassis_joint, chassis_geo )
    # pivot_controls = [frontl, frontr, backl, backr] use to be control[2] is now returning entire structure[0-4]
    pivot_controls = vhl.four_point_pivot( name = 'chassis', parent = 'move_Grp', center = chassis_joint, front = 'wheel_front_bottom_L_jnt', frontL = '', frontR = '', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )

    # tire curves R, left should already exist
    crvs_f_l = vhl.tire_curves( position = 'front', side = 'L', mirror = False )
    crvsA_b_l = vhl.tire_curves( position = 'back', side = 'L', suffix = 'A', mirror = False )
    crvsB_b_l = vhl.tire_curves( position = 'back', side = 'L', suffix = 'B', mirror = False )
    crvsA_b_r = vhl.tire_curves( position = 'back', side = 'R', suffix = 'A', mirror = True )
    crvsB_b_r = vhl.tire_curves( position = 'back', side = 'R', suffix = 'B', mirror = True )
    # remove point constraint to joint
    crv_lists = [crvs_f_l, crvsA_b_l, crvsB_b_l, crvsA_b_r, crvsB_b_r]
    for lst in crv_lists:
        grp = cmds.listRelatives( lst[0], parent = True )[0]
        # print( grp )
        cmds.setAttr( grp + '.visibility', 0 )
        con = cn.getConstraint( grp, nonKeyedRoute = False, keyedRoute = False, plugRoute = True )
        cmds.delete( con )

    # proxy tires
    prxy_f_l = vhl.tire_proxy2( position = 'front', side = 'L', crvs = crvs_f_l )  # [tire_proxy, lofted[0]]
    prxyA_b_l = vhl.tire_proxy2( position = 'back', side = 'L', suffix = 'A', crvs = crvsA_b_l )
    prxyB_b_l = vhl.tire_proxy2( position = 'back', side = 'L', suffix = 'B', crvs = crvsB_b_l )
    prxyA_b_r = vhl.tire_proxy2( position = 'back', side = 'R', suffix = 'A', crvs = crvsA_b_r )
    prxyB_b_r = vhl.tire_proxy2( position = 'back', side = 'R', suffix = 'B', crvs = crvsB_b_r )

    tires_proxy = [prxy_f_l[0], prxyA_b_l[0], prxyB_b_l[0], prxyA_b_r[0], prxyB_b_r[0]]
    # tire geo
    tire_geo_f_l = get_geo_list( name = name, ns = ns, tire_front_l = True )
    tire_geo_b_l = get_geo_list( name = name, ns = ns, tire_back_l = True )
    tire_geo_b_r = get_geo_list( name = name, ns = ns, tire_back_r = True )
    tires_geo = [tire_geo_f_l, tire_geo_b_l, tire_geo_b_r]

    # wrap
    vhl.tire_wrap( master = prxy_f_l[0], slaves = tire_geo_f_l )
    vhl.tire_wrap( master = prxyA_b_l[0], slaves = [tire_geo_b_l[0]] )
    vhl.tire_wrap( master = prxyB_b_l[0], slaves = [tire_geo_b_l[1]] )
    vhl.tire_wrap( master = prxyA_b_r[0], slaves = [tire_geo_b_r[1]] )
    vhl.tire_wrap( master = prxyB_b_r[0], slaves = [tire_geo_b_r[0]] )

    # add tire vis switch (tire geo / proxy geo)

    place.optEnum( move, attr = 'tires', enum = 'VIS' )
    for geos in tires_geo:
        for g in geos:
            place.hijackVis( g, move, name = 'tireGeo', suffix = False, default = None, mode = 'visibility' )
    for g in tires_proxy:
        place.hijackVis( g, move, name = 'tireProxy', suffix = False, default = None, mode = 'visibility' )
    cmds.setAttr( move + '.tireGeo', 1 )

    #
    tire_geo = prxy_f_l[0]
    rim_geo = get_geo_list( name = name, ns = ns, rim_front_l = True )
    landing_gear_front( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, X )
    #
    tire_geo = [prxyA_b_l[0], prxyB_b_l[0]]  # double wheel, final function needs list
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_l = True )
    landing_gear_left( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, X )
    #
    tire_geo = [prxyA_b_r[0], prxyB_b_r[0]]  # double wheel, final function needs list
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_r = True )
    landing_gear_right( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, X )
    landing_gear_doors( X )
    #
    wings( X )
    mini_pistons( X )
    hoses( X )
    #
    fix_normals()


def landing_gear_front( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], X = 1.0 ):
    '''
    
    '''
    #
    hide = []

    #
    nm = 'landingGear_front'
    m = vhl.rotate_part( name = nm, suffix = '', obj = 'landingGear_retract_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 14, shape = 'squareYup_ctrl', color = 'yellow' )
    cmds.transformLimits( m[2] , erx = [1, 1], rx = ( 0, 96 ) )
    # ctrls  = [MasterCt[4], MoveCt[4], SteerCt[4]]
    # piston = [name1_Ct, name2_Ct, nameUp1_Ct, nameUp2_Ct]
    obj1 = 'suspension_piston_00_jnt'
    obj2 = 'suspension_piston_01_jnt'
    geo = get_geo_list( pistonTop_front_c = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( pistonBottom_front_c = True )
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2],
                            aim1 = [0, -1, 0], up1 = [0, 0, 1], aim2 = [0, 1, 0], up2 = [0, 0, 1], X = X * 7, color = 'yellow' )
    hide.append( pstnCtrls[0][0] )
    place.translationXLock( pstnCtrls[1][2], True )
    place.translationZLock( pstnCtrls[1][2], True )
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( 'contactLock', pstnCtrls[1][2], pstnCtrls[1][1], pstnCtrls[1][0], pstnCtrls[0][4], pivot_controls[0][4], True, False, False, True, 'pivot', 0.0 )
    place.breakConnection( pstnCtrls[1][1], 'tx' )
    place.breakConnection( pstnCtrls[1][1], 'tz' )
    # return

    # landing gear / suspension link node (position from upper suspension, rotation from lower suspension)
    name = 'front_suspension_steer_link'
    LinkCt = place.Controller2( name, 'suspension_piston_00_jnt', True, 'squareYup_ctrl', X, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', LinkCt[0], mo = True )
    cmds.orientConstraint( 'suspension_piston_01_jnt', LinkCt[1], mo = True )
    place.cleanUp( LinkCt[0], Ctrl = True )
    hide.append( LinkCt[0] )
    # steering piston
    obj1 = 'steering_piston_00_jnt'
    obj2 = 'steering_piston_01_jnt'
    geo = get_geo_list( steerPistonTop = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( steerPistonBottom = True )
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'steer_piston', suffix = '', obj1 = obj1, obj2 = obj2,
                            parent1 = 'suspension_piston_00_jnt', parent2 = LinkCt[4], parentUp1 = 'suspension_piston_00_jnt', parentUp2 = LinkCt[4],
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'yellow' )
    geo = get_geo_list( suspensionArmLink_c = True )
    vhl.skin( LinkCt[4], geo )
    hide.append( pstnCtrls[0][0] )
    hide.append( pstnCtrls[1][0] )

    # suspension ik
    obj1 = 'suspension_arm_00_jnt'
    obj2 = 'suspension_arm_01_jnt'
    obj3 = 'suspension_arm_02_jnt'
    geo = get_geo_list( suspensionArmTop_c = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( suspensionArmBottom_c = True )
    vhl.skin( obj2, geo )
    name = 'front_A_suspension_arm'
    CtA = place.Controller2( name, obj1, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( LinkCt[4], CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], obj1, mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'front_B_suspension_arm'
    CtB = place.Controller2( name, obj3, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'suspension_piston_01_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = obj1, endJnt = obj3, prefix = 'front_suspension', suffix = '', distance_offset = 0.0, orient = True, color = 'yellow', X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    #
    ik = app.create_ik2( stJnt = obj1, endJnt = obj3, pv = PvCt[4], parent = CtB[4], name = 'front_suspension', suffix = '', setChannels = True )
    # return

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
    # geo
    # whl   = [steer, ContactCt, CenterCt] # old = [steer, contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    whl = vhl.wheel( master_move_controls = [ctrls[0], 'suspension_piston_01_jnt'], axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo], rim_geo = rim_geo, caliper_geo = [], name = 'wheel_front', suffix = '', X = X * 0.5, exp = False, pressureMult = 0.15 )
    # whl   = [steer, ContactCt, CenterCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whl[2][2], slave = pivot_controls[0][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whl[2][2], slave = whl[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_left( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], X = 1.0 ):
    '''
    back left landing gear
    '''
    #
    hide = []
    # main
    clr = 'blue'
    suffix = 'L'

    #
    nm = 'landingGear_back'
    m = vhl.rotate_part( name = nm, suffix = suffix, obj = 'landingGear_retract_L_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 14, shape = 'squareYup_ctrl', color = clr )
    cmds.transformLimits( m[2] , erx = [1, 1], rx = ( -83, 0 ) )
    # suspension piston
    # pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt', parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2],
    obj1 = 'suspension_piston_00_L_jnt'
    obj2 = 'suspension_piston_01_L_jnt'
    geo = get_geo_list( pistonTop_back_l = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( pistonBottom_back_l = True )
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = suffix, obj1 = obj1, obj2 = obj2,
                            parent1 = 'landingGear_retract_L_jnt', parent2 = 'landingGear_retract_L_jnt', parentUp1 = 'landingGear_retract_L_jnt', parentUp2 = 'landingGear_retract_L_jnt',
                            aim1 = [0, -1, 0], up1 = [0, 0, 1], aim2 = [0, 1, 0], up2 = [0, 0, 1], X = X * 7, color = clr )
    hide.append( pstnCtrls[0][0] )
    place.translationXLock( pstnCtrls[1][2], True )
    place.translationZLock( pstnCtrls[1][2], True )
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    # pivot_controls = [frontl, frontr, backl, backr]
    place.parentSwitch( 'contactLock_' + suffix, pstnCtrls[1][2], pstnCtrls[1][1], pstnCtrls[1][0], pstnCtrls[0][4], pivot_controls[1][4], True, False, False, True, 'pivot', 0.0 )
    place.breakConnection( pstnCtrls[1][1], 'tx' )
    place.breakConnection( pstnCtrls[1][1], 'tz' )

    #
    obj1 = 'landing_arm_00_L_jnt'
    obj2 = 'landing_arm_01_L_jnt'
    geo = get_geo_list( retractArm_l = True )
    vhl.skin( obj1, geo )
    pstnCtrls = vhl.piston( name = 'landing_arm', suffix = suffix, obj1 = obj1, obj2 = obj2,
                            parent1 = 'landingGear_retract_L_jnt', parent2 = 'chassis_L_jnt', parentUp1 = None, parentUp2 = None,
                            aim1 = [0, 0, 1], up1 = [0, -1, 0], aim2 = [0, 0, -1], up2 = [0, -1, 0], X = X * 1, color = clr )
    cmds.orientConstraint( 'chassis_L_jnt', pstnCtrls[0][1], mo = True )

    # suspension ik
    obj1 = 'suspension_arm_00_L_jnt'
    obj2 = 'suspension_arm_01_L_jnt'
    obj3 = 'suspension_arm_02_L_jnt'
    geo = get_geo_list( suspensionArmTop_l = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( suspensionArmBottom_l = True )
    vhl.skin( obj2, geo )
    name = 'back_A_suspension_arm' + '_' + suffix
    CtA = place.Controller2( name, obj1, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_00_L_jnt', CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], obj1, mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_suspension_arm' + '_' + suffix
    CtB = place.Controller2( name, obj3, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_01_L_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = obj1, endJnt = obj3, prefix = 'back_suspension', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_L_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    # return
    #
    ik = app.create_ik2( stJnt = obj1, endJnt = obj3, pv = PvCt[4], parent = CtB[4], name = 'back_suspension', suffix = suffix, setChannels = True )

    # back A
    sel = [
    'axle_back_L_jnt',
    'wheelA_back_steer_L_jnt',
    'wheelA_back_center_L_jnt',
    'wheelA_back_bottom_L_jnt',
    'wheelA_back_top_L_jnt',
    'wheelA_back_spin_L_jnt'
    ]
    print( '_____________', tire_geo, rim_geo )
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'suspension_piston_01_L_jnt']
    whlA = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[0]], rim_geo = [rim_geo[1]], caliper_geo = [], name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False, pressureMult = 0.15 )
    # whlA  = [steer, ContactCt, PressureCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whlA[2][2], slave = pivot_controls[1][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whlA[2][2], slave = whlA[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return
    # back B
    sel = [
    'axle_back_L_jnt',
    'wheelB_back_steer_L_jnt',
    'wheelB_back_center_L_jnt',
    'wheelB_back_bottom_L_jnt',
    'wheelB_back_top_L_jnt',
    'wheelB_back_spin_L_jnt'
    ]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'suspension_piston_01_L_jnt']
    whlB = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[1]], rim_geo = [rim_geo[0]], caliper_geo = [], name = 'wheelB_back', suffix = suffix, X = X * 0.25, exp = False, pressureMult = 0.15 )
    # whlB = [steer, ContactCt, PressureCt]
    place.smartAttrBlend( master = whlB[2][2], slave = whlB[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = whlA[2][2], slave = whlB[2][2], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.translationYLock( whlB[2][2], True )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_right( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], X = 1.0 ):
    '''
    back right landing gear
    '''
    #
    hide = []
    # main
    clr = 'red'
    suffix = 'R'

    #
    nm = 'landingGear_back'
    m = vhl.rotate_part( name = nm, suffix = suffix, obj = 'landingGear_retract_R_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 14, shape = 'squareYup_ctrl', color = clr )
    cmds.transformLimits( m[2] , erx = [1, 1], rx = ( -83, 0 ) )
    # suspension piston
    # pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt', parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2],
    obj1 = 'suspension_piston_00_R_jnt'
    obj2 = 'suspension_piston_01_R_jnt'
    geo = get_geo_list( pistonTop_back_r = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( pistonBottom_back_r = True )
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = suffix, obj1 = obj1, obj2 = obj2,
                            parent1 = 'landingGear_retract_R_jnt', parent2 = 'landingGear_retract_R_jnt', parentUp1 = 'landingGear_retract_R_jnt', parentUp2 = 'landingGear_retract_R_jnt',
                            aim1 = [0, -1, 0], up1 = [0, 0, 1], aim2 = [0, 1, 0], up2 = [0, 0, 1], X = X * 7, color = clr )
    hide.append( pstnCtrls[0][0] )
    place.translationXLock( pstnCtrls[1][2], True )
    place.translationZLock( pstnCtrls[1][2], True )
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    # pivot_controls = [frontl, frontr, backl, backr]
    place.parentSwitch( 'contactLock_' + suffix, pstnCtrls[1][2], pstnCtrls[1][1], pstnCtrls[1][0], pstnCtrls[0][4], pivot_controls[2][4], True, False, False, True, 'pivot', 0.0 )
    place.breakConnection( pstnCtrls[1][1], 'tx' )
    place.breakConnection( pstnCtrls[1][1], 'tz' )

    #
    obj1 = 'landing_arm_00_R_jnt'
    obj2 = 'landing_arm_01_R_jnt'
    geo = get_geo_list( retractArm_r = True )
    vhl.skin( obj1, geo )
    pstnCtrls = vhl.piston( name = 'landing_arm', suffix = suffix, obj1 = obj1, obj2 = obj2,
                            parent1 = 'landingGear_retract_R_jnt', parent2 = 'chassis_R_jnt', parentUp1 = None, parentUp2 = None,
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 1, color = clr )
    cmds.orientConstraint( 'chassis_R_jnt', pstnCtrls[0][1], mo = True )

    # suspension ik
    obj1 = 'suspension_arm_00_R_jnt'
    obj2 = 'suspension_arm_01_R_jnt'
    obj3 = 'suspension_arm_02_R_jnt'
    geo = get_geo_list( suspensionArmTop_r = True )
    vhl.skin( obj1, geo )
    geo = get_geo_list( suspensionArmBottom_r = True )
    vhl.skin( obj2, geo )
    name = 'back_A_suspension_arm' + '_' + suffix
    CtA = place.Controller2( name, obj1, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_00_R_jnt', CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], obj1, mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_suspension_arm' + '_' + suffix
    CtB = place.Controller2( name, obj3, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_01_R_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = obj1, endJnt = obj3, prefix = 'back_suspension', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_R_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    # return
    #
    ik = app.create_ik2( stJnt = obj1, endJnt = obj3, pv = PvCt[4], parent = CtB[4], name = 'back_suspension', suffix = suffix, setChannels = True )

    # back A
    sel = [
    'axle_back_R_jnt',
    'wheelA_back_steer_R_jnt',
    'wheelA_back_center_R_jnt',
    'wheelA_back_bottom_R_jnt',
    'wheelA_back_top_R_jnt',
    'wheelA_back_spin_R_jnt'
    ]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'suspension_piston_01_R_jnt']
    whlA = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[0]], rim_geo = [rim_geo[0]], caliper_geo = [], name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False, pressureMult = 0.15 )
    # whlA = [steer, ContactCt, PressureCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whlA[2][2], slave = pivot_controls[2][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whlA[2][2], slave = whlA[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return
    # back B
    sel = [
    'axle_back_R_jnt',
    'wheelB_back_steer_R_jnt',
    'wheelB_back_center_R_jnt',
    'wheelB_back_bottom_R_jnt',
    'wheelB_back_top_R_jnt',
    'wheelB_back_spin_R_jnt'
    ]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'suspension_piston_01_R_jnt']
    whlB = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[1]], rim_geo = [rim_geo[1]], caliper_geo = [], name = 'wheelB_back', suffix = suffix, X = X * 0.25, exp = False, pressureMult = 0.15 )
    # whlB = [steer, ContactCt, PressureCt]
    place.smartAttrBlend( master = whlB[2][2], slave = whlB[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = whlA[2][2], slave = whlB[2][2], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.translationYLock( whlB[2][2], True )

    # return

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_doors( X = 1.0 ):
    '''
    landing gear doors
    '''
    # left front
    parent = 'chassis_jnt'
    j = 'landing_doorA_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorA_l = True )
    vhl.skin( j, geo )
    door_f_l = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 5, shape = 'squareZup_ctrl', color = 'yellow' )
    cmds.transformLimits( door_f_l[2] , erz = [1, 1], rz = ( 0, 70 ) )

    # left back
    parent = 'chassis_L_jnt'
    j = 'landing_doorB_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorB_l = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'squareZup_ctrl', color = 'blue' )
    cmds.transformLimits( m[2] , erz = [1, 1], rz = ( 0, 90 ) )
    doorB = m
    #  doorB hingeA
    parent = 'chassis_L_jnt'
    j = 'landing_doorBHingeA_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorBHingeA_l = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeA', blendWeight = 0.8, reverse = False )
    # doorB hingeB
    parent = 'chassis_L_jnt'
    j = 'landing_doorBHingeB_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorBHingeB_l = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.4, reverse = False )

    # doorC
    parent = 'chassis_L_jnt'
    j = 'landing_doorC_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorC_l = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'squareZup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = doorB[2], slave = m[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = doorB[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = True )
    #  doorC hingeA
    parent = 'chassis_L_jnt'
    j = 'landing_doorCHingeA_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorCHingeA_l = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeA', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = doorB[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = doorB[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = True )
    # doorC hingeB
    parent = 'chassis_L_jnt'
    j = 'landing_doorCHingeB_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorCHingeB_l = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.5, reverse = False )
    place.smartAttrBlend( master = doorB[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.5, reverse = True )

    # right front
    parent = 'chassis_jnt'
    j = 'landing_doorA_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorA_r = True )
    vhl.skin( j, geo )
    door_f_r = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'squareZup_ctrl', color = 'yellow' )
    place.smartAttrBlend( master = door_f_l[2], slave = door_f_r[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = door_f_l[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = False )

    # right back
    parent = 'chassis_R_jnt'
    j = 'landing_doorB_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorB_r = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'squareZup_ctrl', color = 'red' )
    cmds.transformLimits( m[2] , erz = [1, 1], rz = ( 0, 90 ) )
    doorB = m
    #  doorB hingeA
    parent = 'chassis_R_jnt'
    j = 'landing_doorBHingeA_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorBHingeA_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeA', blendWeight = 0.8, reverse = False )
    # doorB hingeB
    parent = 'chassis_R_jnt'
    j = 'landing_doorBHingeB_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorBHingeB_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.4, reverse = False )

    #
    parent = 'chassis_R_jnt'
    j = 'landing_doorC_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorC_r = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'squareZup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = doorB[2], slave = m[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = doorB[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = True )
    #  doorC hingeA
    parent = 'chassis_R_jnt'
    j = 'landing_doorCHingeA_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorCHingeA_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeA', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = doorB[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = doorB[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = True )
    # doorC hingeB
    parent = 'chassis_R_jnt'
    j = 'landing_doorCHingeB_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( landingDoorCHingeB_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 1, shape = 'squareZup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.5, reverse = False )
    place.smartAttrBlend( master = doorB[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'hingeB', blendWeight = 0.5, reverse = True )


def wings( X = 1.0 ):
    '''
    wings flaps and things
    '''
    #
    hide = []
    #
    parent = 'chassis_jnt'
    j = 'rudder_00_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( rudder_c = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 10, shape = 'rectangleTallYup_ctrl', color = 'yellow' )

    size = X
    # wings left
    clr = 'blue'

    # flap A L
    parent = 'chassis_L_jnt'
    j = 'flapsA_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( flapsA_l = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 9, shape = 'rectangleWideXup_ctrl', color = clr )
    cmds.transformLimits( m[2] , erz = [1, 1], rz = ( -60, 0 ) )
    flapA = m
    # flap B L
    parent = 'chassis_L_jnt'
    j = 'flapsB_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( flapsB_l = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = False )
    # aileron L
    parent = 'chassis_L_jnt'
    j = 'aileron_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( aileron_l = True )
    vhl.skin( j, geo )
    ail_l = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 10, shape = 'rectangleWideXup_ctrl', color = clr )
    # aileron spoiler L
    parent = 'aileron_00_L_jnt'
    j = 'aileronSpoiler_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( aileronSpoiler_l = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 2, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
    # elevator L
    parent = 'chassis_L_jnt'
    j = 'elevator_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( elevator_l = True )
    vhl.skin( j, geo )
    elv = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 9, shape = 'rectangleWideXup_ctrl', color = clr )
    # elevator Spoiler L
    parent = 'elevator_00_L_jnt'
    j = 'elevatorSpoiler_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( elevatorSpoiler_l = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 2, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
    #
    # propeller
    parent = 'chassis_L_jnt'
    j = 'propeller_L_jnt'
    nm = j.split( '_' )[0]
    geo = get_geo_list( prop_l = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 7, shape = 'shldrR_ctrl', color = clr )

    size = X * 1
    # wings right
    clr = 'red'

    # flap A R
    parent = 'chassis_R_jnt'
    j = 'flapsA_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( flapsA_r = True )
    vhl.skin( j, geo )
    m = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 9, shape = 'rectangleWideXup_ctrl', color = clr )
    place.smartAttrBlend( master = flapA[2], slave = m[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = flapA[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )
    # flap BR
    parent = 'chassis_R_jnt'
    j = 'flapsB_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( flapsB_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = m[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = m[2], blendAttrString = 'sync', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = flapA[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = flapA[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )
    # aileron R
    parent = 'chassis_R_jnt'
    j = 'aileron_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( aileron_r = True )
    vhl.skin( j, geo )
    ail_r = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 10, shape = 'rectangleWideXup_ctrl', color = clr )
    place.smartAttrBlend( master = ail_l[2], slave = ail_r[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = ail_l[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = True )
    # aileron spoiler R
    parent = 'aileron_00_R_jnt'
    j = 'aileronSpoiler_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( aileronSpoiler_r = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 2, shape = 'rectangleWideXup_ctrl', color = 'pink' )
    # elevator R
    parent = 'chassis_R_jnt'
    j = 'elevator_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( elevator_r = True )
    vhl.skin( j, geo )
    s = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 9, shape = 'rectangleWideXup_ctrl', color = clr )
    place.smartAttrBlend( master = elv[2], slave = s[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = elv[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )
    # elevator Spoiler R
    parent = 'elevator_00_R_jnt'
    j = 'elevatorSpoiler_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( elevatorSpoiler_r = True )
    vhl.skin( j, geo )
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 2, shape = 'rectangleWideXup_ctrl', color = 'pink' )
    #
    #
    parent = 'chassis_R_jnt'
    j = 'propeller_R_jnt'
    nm = j.split( '_' )[0]
    PrpCt = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 7, shape = 'shldrR_ctrl', color = clr )
    ro = cmds.xform( PrpCt[0], query = True, os = True, ro = True )
    cmds.xform( PrpCt[0], os = True, ro = [ro[0], ro[1] + 180, ro[2] + 180] )
    cn.updateConstraintOffset( PrpCt[0] )
    # skin after xform
    geo = get_geo_list( prop_r = True )
    vhl.skin( j, geo )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def mini_pistons( X = 1 ):
    '''
    
    '''
    # main wings
    obj1 = 'aileronSpoilerPiston_00_L_jnt'
    obj2 = 'aileronSpoilerPiston_01_L_jnt'
    geo = ['geo:left_wing_spoiler_joint_2']
    vhl.skin( obj1, geo )
    geo = ['geo:left_wing_spoiler_joint_1']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'aileronSpoiler_Piston', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'aileron_00_L_jnt', parent2 = 'aileronSpoiler_00_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )
    obj1 = 'aileronSpoilerPiston_00_R_jnt'
    obj2 = 'aileronSpoilerPiston_01_R_jnt'
    geo = ['geo:right_wing_spoiler_joint_2']
    vhl.skin( obj1, geo )
    geo = ['geo:right_wing_spoiler_joint_1']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'aileronSpoiler_Piston', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'aileron_00_R_jnt', parent2 = 'aileronSpoiler_00_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )
    # rear wings
    obj1 = 'elevatorSpoilerPiston_00_L_jnt'
    obj2 = 'elevatorSpoilerPiston_01_L_jnt'
    # geo = ['geo:left_wing_spoiler_joint_2']
    # vhl.skin( obj1, geo )
    geo = ['geo:left_elevator_spoiler_joint']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'elevatorSpoiler_Piston', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'elevator_00_L_jnt', parent2 = 'elevatorSpoiler_00_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )
    obj1 = 'elevatorSpoilerPiston_00_R_jnt'
    obj2 = 'elevatorSpoilerPiston_01_R_jnt'
    # geo = ['geo:left_wing_spoiler_joint_2']
    # vhl.skin( obj1, geo )
    geo = ['geo:right_elevator_spoiler_joint']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'elevatorSpoiler_Piston', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'elevator_00_R_jnt', parent2 = 'elevatorSpoiler_00_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )

    # left landing doorB
    obj1 = 'landing_doorBPiston_00_L_jnt'
    obj2 = 'landing_doorBPiston_01_L_jnt'
    geo = ['geo:left_engine_landing_gear_parts_1_top', 'geo:left_engine_landing_gear_parts_1_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:left_engine_landing_gear_parts_1', 'geo:left_engine_landing_gear_parts_1_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorBPistonA', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorBHingeA_L_jnt', parent2 = 'landing_doorB_00_L_jnt',  # parentUp1 = 'landing_doorBPiston_01_L_jnt', parentUp2 = 'landing_doorBPiston_00_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )
    #
    obj1 = 'landing_doorBPiston_03_L_jnt'
    obj2 = 'landing_doorBPiston_04_L_jnt'
    geo = ['geo:left_engine_landing_gear_parts_3_screw_top', 'geo:left_engine_landing_gear_parts_3_top']
    vhl.skin( obj1, geo )
    geo = ['geo:left_engine_landing_gear_parts_3', 'geo:left_engine_landing_gear_parts_3_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorBPistonB', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorBHingeB_L_jnt', parent2 = 'landing_doorBHingeA_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )
    # left landing doorC
    obj1 = 'landing_doorCPiston_00_L_jnt'
    obj2 = 'landing_doorCPiston_01_L_jnt'
    geo = ['geo:left_engine_landing_gear_parts_5_top', 'geo:left_engine_landing_gear_parts_5_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:left_engine_landing_gear_parts_5', 'geo:left_engine_landing_gear_parts_5_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorCPistonA', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorCHingeA_L_jnt', parent2 = 'landing_doorC_00_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )
    #
    obj1 = 'landing_doorCPiston_03_L_jnt'
    obj2 = 'landing_doorCPiston_04_L_jnt'
    geo = ['geo:left_engine_landing_gear_parts_7_top', 'geo:left_engine_landing_gear_parts_7_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:left_engine_landing_gear_parts_7', 'geo:left_engine_landing_gear_parts_7_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorCPistonB', suffix = 'L', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorCHingeB_L_jnt', parent2 = 'landing_doorCHingeA_L_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'lightBlue' )

    # right landing doorB
    obj1 = 'landing_doorBPiston_00_R_jnt'
    obj2 = 'landing_doorBPiston_01_R_jnt'
    geo = ['geo:right_engine_landing_gear_parts_1_top', 'geo:right_engine_landing_gear_parts_1_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:right_engine_landing_gear_parts_1', 'geo:right_engine_landing_gear_parts_1_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorBPistonA', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorBHingeA_R_jnt', parent2 = 'landing_doorB_00_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )
    #
    obj1 = 'landing_doorBPiston_03_R_jnt'
    obj2 = 'landing_doorBPiston_04_R_jnt'
    geo = ['geo:right_engine_landing_gear_parts_3_screw_top', 'geo:right_engine_landing_gear_parts_3_top']
    vhl.skin( obj1, geo )
    geo = ['geo:right_engine_landing_gear_parts_3', 'geo:right_engine_landing_gear_parts_3_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorBPistonB', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorBHingeB_R_jnt', parent2 = 'landing_doorBHingeA_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )
    # right landing doorC
    obj1 = 'landing_doorCPiston_00_R_jnt'
    obj2 = 'landing_doorCPiston_01_R_jnt'
    geo = ['geo:right_engine_landing_gear_parts_5_top', 'geo:right_engine_landing_gear_parts_5_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:right_engine_landing_gear_parts_5', 'geo:right_engine_landing_gear_parts_5_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorCPistonA', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorCHingeA_R_jnt', parent2 = 'landing_doorC_00_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )
    #
    obj1 = 'landing_doorCPiston_03_R_jnt'
    obj2 = 'landing_doorCPiston_04_R_jnt'
    geo = ['geo:right_engine_landing_gear_parts_7_top', 'geo:right_engine_landing_gear_parts_7_screw_top']
    vhl.skin( obj1, geo )
    geo = ['geo:right_engine_landing_gear_parts_7', 'geo:right_engine_landing_gear_parts_7_screw']
    vhl.skin( obj2, geo )
    pstnCtrls = vhl.piston( name = 'landing_doorCPistonB', suffix = 'R', obj1 = obj1, obj2 = obj2,
                            parent1 = 'landing_doorCHingeB_R_jnt', parent2 = 'landing_doorCHingeA_R_jnt',
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'pink' )


def hoses( X = 1.0 ):
    '''
    
    '''
    #
    size = X * 0.15
    # Left
    start_jnt = 'hoseA_01_L'  # fat hose
    cmds.select( start_jnt, hi = True )
    vhl.skin( geos = ['geo:Chassis_left_hose_bottom'], constraint = False, selectedJoints = True )
    name = 'hoseA_L'
    vhl.spline( name = name, start_jnt = 'hoseA_01_L', end_jnt = 'hoseA_15_L', splinePrnt = 'suspension_piston_00_L_jnt', splineStrt = 'suspension_piston_00_L_jnt', splineEnd = 'suspension_piston_01_L_jnt', startSkpR = False, endSkpR = False, color = 'blue', X = size )
    #
    start_jnt = 'hoseB_01_L'  # skinny hose
    cmds.select( start_jnt, hi = True )
    vhl.skin( geos = ['geo:Chassis_left_7'], constraint = False, selectedJoints = True )
    name = 'hoseB_L'
    vhl.spline( name = name, start_jnt = 'hoseB_01_L', end_jnt = 'hoseB_17_L', splinePrnt = 'suspension_piston_00_L_jnt', splineStrt = 'suspension_piston_00_L_jnt', splineEnd = 'suspension_piston_01_L_jnt', startSkpR = False, endSkpR = False, color = 'blue', X = size )

    # Right
    start_jnt = 'hoseA_01_R'  # fat hose
    cmds.select( start_jnt, hi = True )
    vhl.skin( geos = ['geo:Chassis_right_hose_bottom'], constraint = False, selectedJoints = True )
    name = 'hoseA_R'
    vhl.spline( name = name, start_jnt = 'hoseA_01_R', end_jnt = 'hoseA_15_R', splinePrnt = 'suspension_piston_00_R_jnt', splineStrt = 'suspension_piston_00_R_jnt', splineEnd = 'suspension_piston_01_R_jnt', startSkpR = False, endSkpR = False, color = 'red', X = size )
    #
    start_jnt = 'hoseB_01_R'  # skinny hose
    cmds.select( start_jnt, hi = True )
    vhl.skin( geos = ['geo:Chassis_right_7'], constraint = False, selectedJoints = True )
    name = 'hoseB_R'
    vhl.spline( name = name, start_jnt = 'hoseB_01_R', end_jnt = 'hoseB_17_R', splinePrnt = 'suspension_piston_00_R_jnt', splineStrt = 'suspension_piston_00_R_jnt', splineEnd = 'suspension_piston_01_R_jnt', startSkpR = False, endSkpR = False, color = 'red', X = size )
    # left lock ends
    cmds.setAttr( 'hoseB_L_E_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseA_L_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseB_L_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseA_L_E_IK_Cntrl.LockOrientOffOn', 1 )
    # right
    cmds.setAttr( 'hoseB_R_E_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseA_R_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseB_R_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( 'hoseA_R_E_IK_Cntrl.LockOrientOffOn', 1 )


def get_geo_list( name = 'kingAir', ns = 'geo',
                aileron_l = False,
                aileron_r = False,
                aileronSpoiler_l = False,
                aileronSpoiler_r = False,
                caliper_back_l = False,
                caliper_back_r = False,
                caliper_front_c = False,
                chassis = False,
                elevator_l = False,
                elevator_r = False,
                elevatorSpoiler_l = False,
                elevatorSpoiler_r = False,
                flapsA_l = False,
                flapsB_l = False,
                flapsA_r = False,
                flapsB_r = False,
                hoses_back_l = False,
                hoses_back_r = False,
                landingDoorA_l = False,
                landingDoorA_r = False,
                landingDoorB_l = False,
                landingDoorB_r = False,
                landingDoorBHingeA_l = False,
                landingDoorBHingeA_r = False,
                landingDoorBHingeB_l = False,
                landingDoorBHingeB_r = False,
                landingDoorC_l = False,
                landingDoorC_r = False,
                landingDoorCHingeA_l = False,
                landingDoorCHingeA_r = False,
                landingDoorCHingeB_l = False,
                landingDoorCHingeB_r = False,
                pistonBottom_back_l = False,
                pistonBottom_back_r = False,
                pistonBottom_front_c = False,
                pistonTop_back_l = False,
                pistonTop_back_r = False,
                pistonTop_front_c = False,
                prop_l = False,
                prop_r = False,
                retractArm_l = False,
                retractArm_r = False,
                rim_back_l = False,
                rim_back_r = False,
                rim_front_l = False,
                rudder_c = False,
                steerPistonBottom = False,
                steerPistonTop = False,
                suspensionArmBottom_c = False,
                suspensionArmBottom_l = False,
                suspensionArmBottom_r = False,
                suspensionArmTop_c = False,
                suspensionArmTop_l = False,
                suspensionArmTop_r = False,
                suspensionArmLink_c = False,
                tire_back_l = False,
                tire_back_r = False,
                tire_front_l = False,
                all = False ):
    '''
    geo members via selection set
    '''
    geos = []
    geo_sets = []

    # aileron
    if aileron_l or all:
        geo_list = process_geo_list( name = name + '_' + 'aileron_l' )
        geo_sets.append( geo_list )
    if aileron_r or all:
        geo_list = process_geo_list( name = name + '_' + 'aileron_r' )
        geo_sets.append( geo_list )
    if aileronSpoiler_l or all:
        geo_list = process_geo_list( name = name + '_' + 'aileronSpoiler_l' )
        geo_sets.append( geo_list )
    if aileronSpoiler_r or all:
        geo_list = process_geo_list( name = name + '_' + 'aileronSpoiler_r' )
        geo_sets.append( geo_list )

    # calipers
    if caliper_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_back_l' )
        geo_sets.append( geo_list )
    if caliper_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_back_r' )
        geo_sets.append( geo_list )
    if caliper_front_c or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_front_c' )
        geo_sets.append( geo_list )

    # chassis
    if chassis or all:
        geo_list = process_geo_list( name = name + '_' + 'chassis' )
        geo_sets.append( geo_list )

    # elevator
    if elevator_l or all:
        geo_list = process_geo_list( name = name + '_' + 'elevator_l' )
        geo_sets.append( geo_list )
    if elevator_r or all:
        geo_list = process_geo_list( name = name + '_' + 'elevator_r' )
        geo_sets.append( geo_list )
    if elevatorSpoiler_l or all:
        geo_list = process_geo_list( name = name + '_' + 'elevatorSpoiler_l' )
        geo_sets.append( geo_list )
    if elevatorSpoiler_r or all:
        geo_list = process_geo_list( name = name + '_' + 'elevatorSpoiler_r' )
        geo_sets.append( geo_list )

    # flaps
    if flapsA_l or all:
        geo_list = process_geo_list( name = name + '_' + 'flapsA_l' )
        geo_sets.append( geo_list )
    if flapsB_l or all:
        geo_list = process_geo_list( name = name + '_' + 'flapsB_l' )
        geo_sets.append( geo_list )
    if flapsA_r or all:
        geo_list = process_geo_list( name = name + '_' + 'flapsA_r' )
        geo_sets.append( geo_list )
    if flapsB_r or all:
        geo_list = process_geo_list( name = name + '_' + 'flapsB_r' )
        geo_sets.append( geo_list )

    # hoses
    if hoses_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'hoses_back_l' )
        geo_sets.append( geo_list )
    if hoses_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'hoses_back_r' )
        geo_sets.append( geo_list )

    # landing bay doors
    if landingDoorA_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorA_l' )
        geo_sets.append( geo_list )
    if landingDoorA_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorA_r' )
        geo_sets.append( geo_list )
    if landingDoorB_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorB_l' )
        geo_sets.append( geo_list )
    if landingDoorB_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorB_r' )
        geo_sets.append( geo_list )
        #
    if landingDoorBHingeA_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorBHingeA_l' )
        geo_sets.append( geo_list )
    if landingDoorBHingeA_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorBHingeA_r' )
        geo_sets.append( geo_list )
    if landingDoorBHingeB_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorBHingeB_l' )
        geo_sets.append( geo_list )
    if landingDoorBHingeB_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorBHingeB_r' )
        geo_sets.append( geo_list )
        #
    if landingDoorC_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorC_l' )
        geo_sets.append( geo_list )
    if landingDoorC_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorC_r' )
        geo_sets.append( geo_list )
        #
    if landingDoorCHingeA_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorCHingeA_l' )
        geo_sets.append( geo_list )
    if landingDoorCHingeA_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorCHingeA_r' )
        geo_sets.append( geo_list )
    if landingDoorCHingeB_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorCHingeB_l' )
        geo_sets.append( geo_list )
    if landingDoorCHingeB_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorCHingeB_r' )
        geo_sets.append( geo_list )

    # landing gear pistons
    if pistonBottom_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonBottom_back_l' )
        geo_sets.append( geo_list )
    if pistonBottom_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonBottom_back_r' )
        geo_sets.append( geo_list )
    if pistonBottom_front_c or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonBottom_front_c' )
        geo_sets.append( geo_list )
    if pistonTop_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonTop_back_l' )
        geo_sets.append( geo_list )
    if pistonTop_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonTop_back_r' )
        geo_sets.append( geo_list )
    if pistonTop_front_c or all:
        geo_list = process_geo_list( name = name + '_' + 'pistonTop_front_c' )
        geo_sets.append( geo_list )

    # props
    if prop_l or all:
        geo_list = process_geo_list( name = name + '_' + 'prop_l' )
        geo_sets.append( geo_list )
    if prop_r or all:
        geo_list = process_geo_list( name = name + '_' + 'prop_r' )
        geo_sets.append( geo_list )

    # retract arm
    if retractArm_l or all:
        geo_list = process_geo_list( name = name + '_' + 'retractArm_l' )
        geo_sets.append( geo_list )
    if retractArm_r or all:
        geo_list = process_geo_list( name = name + '_' + 'retractArm_r' )
        geo_sets.append( geo_list )

    # rims
    if rim_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_l' )
        geo_sets.append( geo_list )
    if rim_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_r' )
        geo_sets.append( geo_list )
    if rim_front_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_front_l' )
        geo_sets.append( geo_list )

    # rudder
    if rudder_c or all:
        geo_list = process_geo_list( name = name + '_' + 'rudder_c' )
        geo_sets.append( geo_list )

    # steering piston
    if steerPistonBottom or all:
        geo_list = process_geo_list( name = name + '_' + 'steerPistonBottom' )
        geo_sets.append( geo_list )
    if steerPistonTop or all:
        geo_list = process_geo_list( name = name + '_' + 'steerPistonTop' )
        geo_sets.append( geo_list )

    # suspension Arm
    if suspensionArmBottom_c or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmBottom_c' )
        geo_sets.append( geo_list )
    if suspensionArmBottom_l or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmBottom_l' )
        geo_sets.append( geo_list )
    if suspensionArmBottom_r or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmBottom_r' )
        geo_sets.append( geo_list )
    if suspensionArmTop_c or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmTop_c' )
        geo_sets.append( geo_list )
    if suspensionArmTop_l or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmTop_l' )
        geo_sets.append( geo_list )
    if suspensionArmTop_r or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmTop_r' )
        geo_sets.append( geo_list )
    if suspensionArmLink_c or all:
        geo_list = process_geo_list( name = name + '_' + 'suspensionArmLink_c' )
        geo_sets.append( geo_list )

    # tires
    if tire_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_l' )
        geo_sets.append( geo_list )
    if tire_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_r' )
        geo_sets.append( geo_list )
    if tire_front_l or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_front_l' )
        geo_sets.append( geo_list )

    # build list
    for geo_set in geo_sets:
        if geo_set:
            for geo in geo_set:
                if ns:
                    if cmds.objExists( ns + ':' + geo ):
                        geos.append( ns + ':' + geo )
                    else:
                        print( geo_set, geo )
                else:
                    geos.append( geo )

    return geos


def process_geo_list( name = '' ):
    '''
    
    '''
    s = []
    setDict = ss.loadDict( os.path.join( ss.defaultPath(), name + '.sel' ) )
    # print( setDict )
    if setDict:
        for obj in setDict.values():
            s.append( obj )
        # print( s )
        return s
    return None

#
#
'''
imp.reload( web )
symd = web.mod( "assets_symd" )
symd.king_air()
'''
#
