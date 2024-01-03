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
krl = web.mod( "key_rig_lib" )
ac = web.mod( 'animCurve_lib' )
ump = web.mod( 'universalMotionPath' )
sfk = web.mod( 'atom_splineFk_lib' )


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


def __________________BUILD():
    pass


def cessna( X = 12, ns = 'geo', ref_geo = 'P:\\FLR\\assets\\veh\\cessna\\model\\maya\\scenes\\cessna_model_v017.ma', pilot_geo = '' ):
    '''
    build plane
    '''
    name = 'cessna'
    # ref geo
    if ns and ref_geo:
        vhl.reference_geo( ns = ns, path = ref_geo )
    #
    mirror_jnts()

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    # ctrls = vhl.vehicle_master( masterX = X * 10, moveX = X * 9, steerParent = 'landingGear_retract_jnt' )
    ctrls = vhl.vehicle_master( masterX = X * 10, moveX = X * 11, steerParent = 'chassis_jnt' )
    # move
    move = 'move'
    # mass to pivot, chassis
    chassis_joint = 'chassis_jnt'
    chassis_geo = get_geo_list( chassis = True )
    for g in chassis_geo:
        print( g )
    # return
    vhl.skin( chassis_joint, chassis_geo )
    # pivot_controls = [frontl, frontr, backl, backr] use to be control[2] is now returning entire structure[0-4]
    pivot_controls = vhl.four_point_pivot( name = 'chassis', parent = 'move_Grp', center = chassis_joint, front = 'wheel_front_bottom_L_jnt', frontL = '', frontR = '', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )
    cmds.setAttr( 'chassis_up_pivot.multiplier', 4.25 )

    # tire curves R, left should already exist
    crvs_f_l = vhl.tire_curves( position = 'front', side = 'L', mirror = False )
    crvsA_b_l = vhl.tire_curves( position = 'back', side = 'L', suffix = 'A', mirror = False )
    # crvsB_b_l = vhl.tire_curves( position = 'back', side = 'L', suffix = 'B', mirror = False )
    crvsA_b_r = vhl.tire_curves( position = 'back', side = 'R', suffix = 'A', mirror = True )
    # crvsB_b_r = vhl.tire_curves( position = 'back', side = 'R', suffix = 'B', mirror = True )
    # remove point constraint to joint
    # crv_lists = [crvs_f_l, crvsA_b_l, crvsB_b_l, crvsA_b_r, crvsB_b_r]
    crv_lists = [crvs_f_l, crvsA_b_l, crvsA_b_r]
    for lst in crv_lists:
        grp = cmds.listRelatives( lst[0], parent = True )[0]
        # print( grp )
        cmds.setAttr( grp + '.visibility', 0 )
        con = cn.getConstraint( grp, nonKeyedRoute = False, keyedRoute = False, plugRoute = True )
        cmds.delete( con )

    # proxy tires
    prxy_f_l = vhl.tire_proxy2( position = 'front', side = 'L', crvs = crvs_f_l )  # [tire_proxy, lofted[0]]
    prxyA_b_l = vhl.tire_proxy2( position = 'back', side = 'L', suffix = 'A', crvs = crvsA_b_l )
    # prxyB_b_l = vhl.tire_proxy2( position = 'back', side = 'L', suffix = 'B', crvs = crvsB_b_l )
    prxyA_b_r = vhl.tire_proxy2( position = 'back', side = 'R', suffix = 'A', crvs = crvsA_b_r )
    # prxyB_b_r = vhl.tire_proxy2( position = 'back', side = 'R', suffix = 'B', crvs = crvsB_b_r )

    # tires_proxy = [prxy_f_l[0], prxyA_b_l[0], prxyB_b_l[0], prxyA_b_r[0], prxyB_b_r[0]]
    tires_proxy = [prxy_f_l[0], prxyA_b_l[0], prxyA_b_r[0]]
    # tire geo
    tire_geo_f_l = get_geo_list( name = name, ns = ns, tire_front_l = True )
    tire_geo_b_l = get_geo_list( name = name, ns = ns, tire_back_l = True )
    tire_geo_b_r = get_geo_list( name = name, ns = ns, tire_back_r = True )
    tires_geo = [tire_geo_f_l, tire_geo_b_l, tire_geo_b_r]

    # wrap
    # print( prxyA_b_l )
    # print( tire_geo_b_l )
    vhl.tire_wrap( master = prxy_f_l[0], slaves = tire_geo_f_l )
    vhl.tire_wrap( master = prxyA_b_l[0], slaves = [tire_geo_b_l[0]] )
    # vhl.tire_wrap( master = prxyB_b_l[0], slaves = [tire_geo_b_l[1]] )
    vhl.tire_wrap( master = prxyA_b_r[0], slaves = [tire_geo_b_r[0]] )
    # vhl.tire_wrap( master = prxyB_b_r[0], slaves = [tire_geo_b_r[0]] )

    # add tire vis switch (tire geo / proxy geo)

    place.optEnum( move, attr = 'tires', enum = 'VIS' )
    for geos in tires_geo:
        for g in geos:
            try:
                place.hijackVis( g, move, name = 'tireGeo', suffix = False, default = None, mode = 'visibility' )
            except:
                pass
    for g in tires_proxy:
        place.hijackVis( g, move, name = 'tireProxy', suffix = False, default = None, mode = 'visibility' )
    cmds.setAttr( move + '.tireGeo', 1 )

    #
    tire_geo = prxy_f_l[0]
    rim_geo = get_geo_list( name = name, ns = ns, rim_front_l = True )
    landing_gear_front( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, X )

    #
    # tire_geo = [prxyA_b_l[0], prxyB_b_l[0]]  # double wheel, final function needs list
    tire_geo = [prxyA_b_l[0]]  # double wheel, final function needs list
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_l = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_back_l = True )
    landing_gear_left( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, caliper_geo, X )

    #
    # tire_geo = [prxyA_b_r[0], prxyB_b_r[0]]  # double wheel, final function needs list
    tire_geo = [prxyA_b_r[0]]  # double wheel, final function needs list
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_r = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_back_r = True )
    landing_gear_right( ctrls, chassis_joint, pivot_controls, tire_geo, rim_geo, caliper_geo, X )

    # landing_gear_doors( X )

    #
    doors( X )
    wings( X )
    propellers( X )
    # return
    wings_broken( X )
    weights_meshImport()

    # broken wing
    joints = [
    'chassis_R_jnt',
    'wingBreak_00_R_jnt'
    ]
    geos = wing_broken_geo()
    default_skin( joints = joints, geos = geos )
    # broken flap
    joints = [
    'flapsA_00_R_jnt',
    'flapsA_01_R_jnt'
    ]
    geos = flap_broken_geo()
    default_skin( joints = joints, geos = geos )

    #
    # mini_pistons( X )
    # hoses( X )
    #
    fix_normals()
    # need to match move pivot with chassis pivot
    cmds.setAttr( 'move_Grp.translateZ', -76.97 )


def landing_gear_front( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], X = 1.0 ):
    '''
    
    '''
    #
    hide = []

    #
    nm = 'landingGear_front'
    '''
    m = vhl.rotate_part( name = nm, suffix = '', obj = 'landingGear_retract_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 14, shape = 'squareYup_ctrl', color = 'yellow' )
    cmds.transformLimits( m[2] , erx = [1, 1], rx = ( 0, 96 ) )
    hide.append( m[0] )
    '''
    FgearCt = place.Controller2( nm, 'landingGear_retract_jnt', False, 'squareYup_ctrl', X * 14, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.setAttr( FgearCt[0] + '.translateY', 85 )
    cmds.parentConstraint( FgearCt[4], 'landingGear_retract_jnt', mo = True )
    cmds.parentConstraint( FgearCt[4], 'steer_CtGrp', mo = True )
    cmds.parentConstraint( chassis_joint, FgearCt[0], mo = True )
    place.cleanUp( FgearCt[0], Ctrl = True )
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

    place.smartAttrBlend( master = 'steer', slave = obj1, masterAttr = 'rotateY', slaveAttr = 'rotateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
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
    '''
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
    '''

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
                     tire_geo = [tire_geo], rim_geo = rim_geo, caliper_geo = [], name = 'wheel_front', suffix = '', X = X * 0.5, exp = False, pressureMult = 0.05 )
    # whl   = [steer, ContactCt, CenterCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whl[2][2], slave = pivot_controls[0][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whl[2][2], slave = whl[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_left( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], caliper_geo = [], X = 1.0 ):
    '''
    back left landing gear
    '''
    #
    hide = []
    # main
    clr = 'blue'
    suffix = 'L'

    # flex
    flex = [
    'landingGear_flex_01_L_jnt',
    'landingGear_flex_02_L_jnt',
    'landingGear_flex_03_L_jnt',
    'landingGear_flex_04_L_jnt',
    'landingGear_flex_05_L_jnt',
    'landingGear_flex_06_L_jnt'
    ]
    #
    name = 'landingGear' + '_back_' + suffix
    flexCt = place.Controller2( name, flex[-1], True, 'pinYup_ctrl', X * 11, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'landingGear_flex_00_L_jnt', flexCt[0], mo = True )
    place.translationZLock( flexCt[2], True )
    place.rotationLock( flexCt[2], True )
    place.cleanUp( flexCt[0], Ctrl = True )
    for j in flex:
        place.smartAttrBlend( master = flexCt[2], slave = j, masterAttr = 'translateY', slaveAttr = 'rotateX', blendAttrObj = flexCt[2], blendAttrString = 'flex', blendWeight = 0.22, reverse = True )
        place.smartAttrBlend( master = flexCt[2], slave = j, masterAttr = 'translateX', slaveAttr = 'rotateY', blendAttrObj = flexCt[2], blendAttrString = 'flex', blendWeight = 0.22, reverse = False )

    # wheel all control
    name = 'wheelA' + '_back_' + suffix
    whlA = place.Controller2( name, 'wheelA_back_steer_L_jnt', False, 'squareXup_ctrl', X * 11, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( flex[-1], whlA[0], mo = True )
    place.cleanUp( whlA[0], Ctrl = True )
    # parentSwitch( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( whlA[2], whlA[2], whlA[1], whlA[0], 'master_Grp', whlA[0], False, False, True, True, 'wheel', 1.0 )

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
    new_ctrls = [ctrls[0], whlA[4]]
    whlA = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[0]], rim_geo = [rim_geo[0]], caliper_geo = caliper_geo, name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False, pressureMult = 0.05 )
    # whlA  = [steer, ContactCt, PressureCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whlA[2][2], slave = pivot_controls[1][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whlA[2][2], slave = whlA[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_right( ctrls = [], chassis_joint = '', pivot_controls = [], tire_geo = [], rim_geo = [], caliper_geo = [], X = 1.0 ):
    '''
    back right landing gear
    '''
    #
    hide = []
    # main
    clr = 'red'
    suffix = 'R'

    # flex
    flex = [
    'landingGear_flex_01_R_jnt',
    'landingGear_flex_02_R_jnt',
    'landingGear_flex_03_R_jnt',
    'landingGear_flex_04_R_jnt',
    'landingGear_flex_05_R_jnt',
    'landingGear_flex_06_R_jnt'
    ]
    #
    name = 'landingGear' + '_back_' + suffix
    flexCt = place.Controller2( name, flex[-1], True, 'pinYup_ctrl', X * 11, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.xform( flexCt[2], os = True, r = True, ro = ( 180, 180, 0 ) )  # right side
    cmds.parentConstraint( 'landingGear_flex_00_R_jnt', flexCt[0], mo = True )
    place.translationZLock( flexCt[2], True )
    place.rotationLock( flexCt[2], True )
    place.cleanUp( flexCt[0], Ctrl = True )
    for j in flex:
        place.smartAttrBlend( master = flexCt[2], slave = j, masterAttr = 'translateY', slaveAttr = 'rotateX', blendAttrObj = flexCt[2], blendAttrString = 'flex', blendWeight = 0.22, reverse = False )
        place.smartAttrBlend( master = flexCt[2], slave = j, masterAttr = 'translateX', slaveAttr = 'rotateY', blendAttrObj = flexCt[2], blendAttrString = 'flex', blendWeight = 0.22, reverse = True )

    # wheel all control
    name = 'wheelA' + '_back_' + suffix
    whlA = place.Controller2( name, 'wheelA_back_steer_R_jnt', False, 'squareXup_ctrl', X * 11, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( flex[-1], whlA[0], mo = True )
    place.cleanUp( whlA[0], Ctrl = True )
    # parentSwitch( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( whlA[2], whlA[2], whlA[1], whlA[0], 'master_Grp', whlA[0], False, False, True, True, 'wheel', 1.0 )

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
    new_ctrls = [ctrls[0], whlA[4]]
    whlA = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = [tire_geo[0]], rim_geo = [rim_geo[0]], caliper_geo = caliper_geo, name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False, pressureMult = 0.05 )
    # whlA = [steer, ContactCt, PressureCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whlA[2][2], slave = pivot_controls[2][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whlA[2][2], slave = whlA[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
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
    place.translationXLock( m[2], lock = False )
    place.translationYLock( m[2], lock = False )
    flapA = m
    flaps_slide( side = 'L' )

    # flap broken
    '''
    parent = m[4]
    j = 'flapsA_01_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    flap_brkn_l = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [1, 1, 1], X = X * 7, shape = 'rectangleWideZup_ctrl', color = 'lightBlue' )
    '''

    # spoiler L
    parent = 'wingBreak_01_L_jnt'
    j = 'spoiler_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( spoiler_l = True )
    vhl.skin( j, geo )
    spl_l = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
    # aileron L
    parent = 'wingBreak_01_L_jnt'
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
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
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
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'lightBlue' )
    #

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
    place.translationXLock( m[2], lock = False )
    place.smartAttrBlend( master = flapA[2], slave = m[1], masterAttr = 'tx', slaveAttr = 'tx', blendAttrObj = flapA[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = True )
    place.translationYLock( m[2], lock = False )
    place.smartAttrBlend( master = flapA[2], slave = m[1], masterAttr = 'ty', slaveAttr = 'ty', blendAttrObj = flapA[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = True )
    flaps_slide( side = 'R' )

    # flap broken
    parent = m[4]
    j = 'flapsA_01_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    flap_brkn_r = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [1, 1, 1], X = X * 7, shape = 'rectangleWideZup_ctrl', color = 'pink' )

    # spoiler L
    parent = 'wingBreak_01_R_jnt'
    j = 'spoiler_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = get_geo_list( spoiler_r = True )
    vhl.skin( j, geo )
    spl_r = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'pink' )
    place.smartAttrBlend( master = spl_l[2], slave = spl_r[1], masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = ail_l[2], blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )

    # aileron R
    parent = 'wingBreak_01_R_jnt'
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
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'pink' )
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
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 4, shape = 'rectangleWideXup_ctrl', color = 'pink' )
    #

    # BROKEN GEO
    broken_wing_grp = 'geo:ces:cessna_wings_grp'
    cmds.setAttr( broken_wing_grp + '.visibility', 1 )
    #
    parent = 'chassis_jnt'
    move = 'move'
    place.optEnum( move, attr = 'wingBack', enum = 'VIS' )
    # back r wing vis
    geos = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:tail_group|geo:ast:right_horizontal_stabilizer_group',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:tail_group|geo:ast:right_elevator_group'
    ]
    for g in geos:
        try:
            place.hijackVis( g, move, name = 'elevator', suffix = False, default = None, mode = 'visibility' )
            # cmds.parentConstraint( parent, g, mo = True )
        except:
            pass
    geos = [
    'geo:ces:right_wing_breaking_lines_grp'
    ]
    for g in geos:
        place.hijackVis( g, move, name = 'elevatorBroken', suffix = False, default = None, mode = 'visibility' )
        cmds.parentConstraint( parent, g, mo = True )
    cmds.setAttr( move + '.elevator', 1 )

    #
    place.optEnum( move, attr = 'wingFront', enum = 'VIS' )
    # back r wing vis
    geos = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group'
    ]
    for g in geos:
        try:
            place.hijackVis( g, move, name = 'wing', suffix = False, default = None, mode = 'visibility' )
            # cmds.parentConstraint( parent, g, mo = True )
        except:
            pass
    geos = [
    'geo:ces:Front_right_wing_breaking_lines_Groups'
    ]
    for g in geos:
        place.hijackVis( g, move, name = 'wingBroken', suffix = False, default = None, mode = 'visibility' )
        cmds.parentConstraint( parent, g, mo = True )
    cmds.setAttr( move + '.wing', 1 )

    # controls for broken geo
    parent = 'chassis_jnt'
    j = 'wingBroken_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = [
    'geo:ces:Front_right_wing_Part1'
    ]
    vhl.skin( j, geo )
    brkn_wingCt = place.Controller2( nm, j, False, 'rectangleWideXup_ctrl', X * 13, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( brkn_wingCt[4], j, mo = True )
    cmds.parentConstraint( parent, brkn_wingCt[0], mo = True )
    place.parentSwitch( 'wingTip', brkn_wingCt[2], brkn_wingCt[1], brkn_wingCt[0], 'master_Grp', parent, Pos = False, Ornt = False, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.cleanUp( brkn_wingCt[0], Ctrl = True )

    j = 'elevatorBroken_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    geo = [
    'geo:ces:rear_right_wing_Part1'
    ]
    vhl.skin( j, geo )
    brkn_elevCt = place.Controller2( nm, j, False, 'rectangleWideXup_ctrl', X * 10, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( brkn_elevCt[4], j, mo = True )
    cmds.parentConstraint( parent, brkn_elevCt[0], mo = True )
    place.parentSwitch( 'elevatorTip', brkn_elevCt[2], brkn_elevCt[1], brkn_elevCt[0], 'master_Grp', parent, Pos = False, Ornt = False, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.cleanUp( brkn_elevCt[0], Ctrl = True )

    # vis controls with geo
    move = 'move'
    cmds.connectAttr( move + '.wingBroken', brkn_wingCt[0] + '.visibility', f = True )
    cmds.connectAttr( move + '.wingBroken', brkn_elevCt[0] + '.visibility', f = True )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def doors( X = 1 ):
    '''
    
    '''
    # door upper
    parent = 'chassis_jnt'
    name = 'door_upper'
    UpprCt = place.Controller2( name, 'door_upper_00_L_jnt', True, 'boxZup_ctrl', X * 6, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.parentConstraint( parent, UpprCt[0], mo = True )
    place.parentSwitch( 'doorUppr', UpprCt[2], UpprCt[1], UpprCt[0], 'master_Grp', parent, Pos = False, Ornt = False, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.cleanUp( UpprCt[0], Ctrl = True )

    # hinge
    j = 'door_upper_01_L_jnt'
    nm = 'door_hinge_upper'
    geo = get_geo_list( door_upper = True )
    vhl.skin( j, geo )
    door_up = vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = UpprCt[4], rotations = [0, 0, 1], X = X * 5, shape = 'squareZup_ctrl', color = 'lightBlue' )
    cmds.transformLimits( door_up[2] , erz = [1, 1], rz = ( -160, 0 ) )

    # door lower
    parent = 'chassis_jnt'
    name = 'door_lower'
    LwrCt = place.Controller2( name, 'door_lower_00_L_jnt', True, 'boxZup_ctrl', X * 6, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.parentConstraint( parent, LwrCt[0], mo = True )
    place.parentSwitch( 'doorLwr', LwrCt[2], LwrCt[1], LwrCt[0], 'master_Grp', parent, Pos = False, Ornt = False, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.cleanUp( LwrCt[0], Ctrl = True )

    # hinge
    j = 'door_lower_01_L_jnt'
    nm = 'door_hinge_lower'
    geo = get_geo_list( door_lower = True )
    vhl.skin( j, geo )
    door_up = vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = LwrCt[4], rotations = [0, 0, 1], X = X * 5, shape = 'squareZup_ctrl', color = 'lightBlue' )
    cmds.transformLimits( door_up[2] , erz = [1, 1], rz = ( -160, 0 ) )


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


def wings_broken( X = 1.0 ):
    '''
    
    '''
    '''
    # wings left
    clr = 'blue'
    
    parent = 'chassis_jnt'
    j = 'wingBreak_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    brkn_l = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [1, 1, 1], X = X * 13, shape = 'rectangleWideZup_ctrl', color = clr )

    # broken driver
    j = 'flapsA_01_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1] + '_L'
    place.smartAttrBlend( master = brkn_l[2], slave = nm + '_CtGrp', masterAttr = 'rx', slaveAttr = 'rx', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = brkn_l[2], slave = nm + '_CtGrp', masterAttr = 'ry', slaveAttr = 'ry', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = brkn_l[2], slave = nm + '_CtGrp', masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    # cmds.orientConstraint( brkn_l[4], 'flapsA_01_L_jnt', mo = True )
    '''

    # wings right
    clr = 'red'

    parent = 'chassis_jnt'
    j = 'wingBreak_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    brkn_r = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [1, 1, 1], X = X * 13, shape = 'rectangleWideZup_ctrl', color = clr )

    # broken driver
    j = 'flapsA_01_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1] + '_R'
    place.smartAttrBlend( master = brkn_r[2], slave = nm + '_CtGrp', masterAttr = 'rx', slaveAttr = 'rx', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = brkn_r[2], slave = nm + '_CtGrp', masterAttr = 'ry', slaveAttr = 'ry', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = brkn_r[2], slave = nm + '_CtGrp', masterAttr = 'rz', slaveAttr = 'rz', blendAttrObj = nm, blendAttrString = 'broken', blendWeight = 1.0, reverse = False )
    # cmds.orientConstraint( brkn_r[4], 'flapsA_01_R_jnt', mo = True )

    # controller vis when geo hidden
    move = 'move'
    cmds.connectAttr( move + '.wing', 'wingBreak_00_R_TopGrp.visibility', f = True )
    cmds.connectAttr( move + '.wing', 'flapsA_01_R_TopGrp.visibility', f = True )


def flaps_slide( side = '', X = 1.0 ):
    '''
    
    '''
    if side == 'R':
        # crv 1
        crv = cmds.duplicate( 'flap_curve1_L', n = 'flap_curve1_L'.replace( '_L', '_R' ) )[0]
        tx = cmds.getAttr( crv + '.tx' )
        cmds.setAttr( crv + '.tx', tx * -1 )
        # crv 2
        crv = cmds.duplicate( 'flap_curve2_L', n = 'flap_curve2_L'.replace( '_L', '_R' ) )[0]
        tx = cmds.getAttr( crv + '.tx' )
        cmds.setAttr( crv + '.tx', tx * -1 )
    #
    parent = 'chassis_' + side + '_jnt'
    # track 1
    crv1 = 'flap_curve1_' + side
    cmds.parentConstraint( parent, crv1, mo = True )
    name = 'flap_track1_' + side
    flp1_l = place.Controller2( name, crv1, False, 'loc_ctrl', X * 6, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( flp1_l[0] + '.visibility', False )
    cmds.setAttr( crv1 + '.visibility', False )
    place.cleanUp( flp1_l[0], Ctrl = True )
    place.cleanUp( crv1, Ctrl = True )
    #
    mo_path1 = cmds.pathAnimation( flp1_l[0], name = flp1_l[2] + '_motionPath' , c = crv1, startU = 0.0, follow = True, wut = 'object', wuo = 'up_jnt', fm = False, fa = 'z', ua = 'y' )
    cmds.setAttr( mo_path1 + '.fractionMode', True )  # turn off parametric, sets start/end range 0-1
    ac.deleteAnim2( mo_path1, attrs = ['uValue'] )

    # track 2
    crv2 = 'flap_curve2_' + side
    cmds.parentConstraint( parent, crv2, mo = True )
    name = 'flap_track2_' + side
    flp2_l = place.Controller2( name, crv2, False, 'loc_ctrl', X * 6, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( flp2_l[0] + '.visibility', False )
    cmds.setAttr( crv2 + '.visibility', False )
    place.cleanUp( flp2_l[0], Ctrl = True )
    place.cleanUp( crv2, Ctrl = True )
    #
    mo_path2 = cmds.pathAnimation( flp2_l[0], name = flp2_l[2] + '_motionPath' , c = crv2, startU = 0.0, follow = True, wut = 'object', wuo = 'up_jnt', fm = False, fa = 'z', ua = 'y' )
    cmds.setAttr( mo_path2 + '.fractionMode', True )  # turn off parametric, sets start/end range 0-1
    ac.deleteAnim2( mo_path2, attrs = ['uValue'] )

    cmds.aimConstraint( flp2_l[4], flp1_l[1], wut = 'object', wuo = 'flapUp_' + side + '_jnt', aim = [0, 0, 1], u = [0, 1, 0], mo = False )

    # connect flap
    j = 'flapsA_00_' + side + '_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1] + '_' + side
    attr = 'slide'
    misc.optEnum( nm, attr = 'flaps', enum = 'CONTROL' )
    place.addAttribute( nm, attr, 0.0, 1.0, True, 'float' )
    cmds.connectAttr( nm + '.' + attr, mo_path1 + '.uValue' )
    cmds.connectAttr( nm + '.' + attr, mo_path2 + '.uValue' )
    constraint_delete( obj = nm + '_TopGrp' )
    cmds.parentConstraint( flp1_l[4], nm + '_TopGrp', mo = True )
    #
    reverse = False
    if side == 'R':
        reverse = True
    place.smartAttrBlend( master = nm, slave = 'flapUp_' + side + '_jnt', masterAttr = attr, slaveAttr = 'ty', blendAttrObj = nm, blendAttrString = 'tilt', blendWeight = 8.0, reverse = reverse, minmax = [0, 20] )

    # sync opposite
    if side == 'R':
        nm = nm.replace( '_R', '_L' )
        # slide
        place.smartAttrBlend( master = nm, slave = mo_path1, masterAttr = attr, slaveAttr = 'uValue', blendAttrObj = nm, blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = nm, slave = mo_path2, masterAttr = attr, slaveAttr = 'uValue', blendAttrObj = nm, blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = False )
        # tilt
        place.smartAttrBlend( master = 'flapUp_L_jnt', slave = 'flapUp_R_jnt', masterAttr = 'ty', slaveAttr = 'ty', blendAttrObj = nm, blendAttrString = 'syncOpposite', blendWeight = 1.0, reverse = True )


def propellers( X = 1 ):
    '''
    
    '''
    # spin
    # propeller 4x
    vis_grp = 'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:propeller_4x_group'
    parent = 'chassis_jnt'
    j = 'propeller_jnt'
    nm = j.split( '_' )[0]
    geo = get_geo_list( prop_l = True )
    geo = [vis_grp]
    vhl.skin( j, geo, constraint = False )
    PrpCt = vhl.rotate_part( name = nm, suffix = 'C', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 7, shape = 'shldrL_ctrl', color = 'yellow' )
    vis_obj = nm + '_C'
    place.optEnum( vis_obj, attr = 'propeller', enum = 'VIS' )
    place.hijackVis( vis_grp, vis_obj, name = 'prop_4_Geo', suffix = False, default = None, mode = 'visibility' )
    cmds.setAttr( vis_obj + '.prop_4_Geo', 1 )

    # propeller 3x
    vis_grp = 'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:propeller_3x_group'
    parent = 'chassis_jnt'
    j = 'propeller_jnt'
    nm = j.split( '_' )[0]
    geo = get_geo_list( prop_r = True )
    vhl.skin( j, geo, constraint = False )
    vis_obj = nm + '_C'
    place.hijackVis( vis_grp, vis_obj, name = 'prop_3_Geo', suffix = False, default = None, mode = 'visibility' )
    cmds.setAttr( vis_obj + '.prop_3_Geo', 0 )

    # bend
    p = 'propeller_jnt'
    #
    joints = [
    'blade_1_3x_01_jnt',
    'blade_1_3x_02_jnt',
    'blade_1_3x_03_jnt',
    'blade_1_3x_04_jnt',
    'blade_1_3x_05_jnt',
    'blade_1_3x_06_jnt'
    ]
    geos = blade_1_3x()
    default_skin( joints = joints, geos = geos, mi = 2 )
    cmds.deltaMush( geos, smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # spline
    name = 'Tri_blade_1'
    direction = 1
    digitRig = sfk.SplineFK( name, joints[0], joints[-1], None, direction = direction,
                              controllerSize = X * 2, rootParent = p, parent1 = p, parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'ik', colorScheme = 'yellow' )

    #
    joints = [
    'blade_2_3x_01_jnt',
    'blade_2_3x_02_jnt',
    'blade_2_3x_03_jnt',
    'blade_2_3x_04_jnt',
    'blade_2_3x_05_jnt',
    'blade_2_3x_06_jnt'
    ]
    geos = blade_2_3x()
    default_skin( joints = joints, geos = geos, mi = 2 )
    cmds.deltaMush( geos, smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # spline
    name = 'Tri_blade_2'
    direction = 1
    digitRig = sfk.SplineFK( name, joints[0], joints[-1], None, direction = direction,
                              controllerSize = X * 2, rootParent = p, parent1 = p, parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK', colorScheme = 'yellow' )

    #
    joints = [
    'blade_3_3x_01_jnt',
    'blade_3_3x_02_jnt',
    'blade_3_3x_03_jnt',
    'blade_3_3x_04_jnt',
    'blade_3_3x_05_jnt',
    'blade_3_3x_06_jnt'
    ]
    geos = blade_3_3x()
    default_skin( joints = joints, geos = geos, mi = 2 )
    cmds.deltaMush( geos, smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # spline
    name = 'Tri_blade_3'
    direction = 1
    digitRig = sfk.SplineFK( name, joints[0], joints[-1], None, direction = direction,
                              controllerSize = X * 2, rootParent = p, parent1 = p, parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'ik', colorScheme = 'yellow' )


def wingBend():
    '''
    
    '''
    # wingA_L bend
    place.optEnum( wnga_lCt[2], attr = 'bend', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings1' )
    wbend = cmds.nonLinear( type = 'bend', name = 'wingA_Bend_L', curvature = 0.0, lowBound = 0.0, highBound = 2.0 )
    cmds.select( wbend[1], 'wingA_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wbend[1], 'wingA_01_jnt_L' )
    cmds.setAttr( wbend[1] + '.rotateX', 90 )  # [1] handle # [0] deformer
    cmds.setAttr( wbend[1] + '.rotateZ', 90 )
    place.hijackAttrs( wbend[1], wnga_lCt[2], 'translateZ', 'bendSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wbend[0] + 'HandleShape', wnga_lCt[2], 'curvature', 'bendCurvature', set = False, default = 0, force = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wbend[1], [False, False], [False, False], [True, False], [False, False, False] )
    # wingA_L twist
    place.optEnum( wnga_lCt[2], attr = 'twist', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings1' )
    wtwist = cmds.nonLinear( type = 'twist', name = 'wingA_Twist_L', lowBound = 0.0, highBound = 2.0 )
    cmds.select( wtwist[1], 'wingA_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wtwist[1], 'wingA_01_jnt_L' )
    cmds.setAttr( wtwist[1] + '.rotateX', 90 )
    cmds.setAttr( wtwist[1] + '.rotateZ', -90 )
    place.hijackAttrs( wtwist[1], wnga_lCt[2], 'translateZ', 'twistSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_lCt[2], 'highBound', 'twistBound', set = False, default = 2, force = True )
    cmds.setAttr( wnga_lCt[2] + '.twistBound', k = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_lCt[2], 'endAngle', 'twistAngle', set = False, default = 0, force = True )
    cmds.setAttr( wnga_lCt[2] + '.twistAngle', k = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wtwist[1], [False, False], [False, False], [True, False], [False, False, False] )


def __________________PATH():
    pass


def path( fk = False, dynamics = False, tail_as_root = False, X = 100.0 ):
    '''
    fix hard coded names
    '''
    #
    reverse = True
    '''
    if tail_as_root:
        reverse = False'''

    #
    master = 'master'
    layers = 6
    # returnsNothing_FixIt = ump.path2( length = 120, layers = layers, X = 18.0, prebuild = False, ctrl_shape = 'diamond_ctrl', reverse = reverse )
    curve, curve_up = ump.ribbon_path( 
        name = '',
        layers = layers,
        length = 1200,
        width = 3,
        X = X * 2.0,
        ctrl_shape = 'pinYupZfront_ctrl',
        reverse = False,
        prebuild = True,
        prebuild_type = 4,
        fk = fk,
        dynamics = dynamics
        )
    #
    # return
    position_ctrl = place.Controller2( 'position', 'body_001_jnt', True, 'splineStart_ctrl', X * 15, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'green' ).result
    #
    # pathIk( curve = 'path_layer_05', position_ctrl = position_ctrl, tail_as_root = tail_as_root ) #
    micro_body_cts = pathIk2( curve = curve, position_ctrl = position_ctrl, tail_as_root = tail_as_root, curve_up = curve_up, fk = fk, X = X )

    misc.optEnum( position_ctrl[2], attr = 'path', enum = 'CONTROL' )
    # cmds.setAttr( master + '.path', cb = False )
    i = 0
    while i <= layers - 1:
        place.hijackAttrs( master, position_ctrl[2], 'ctrlLayer' + str( i ), 'ctrlLayer' + str( i ), set = False, default = None, force = True )
        cmds.setAttr( master + '.ctrlLayer' + str( i ), cb = False )
        i += 1

    place.cleanUp( 'body_001_jnt', World = True )
    cmds.setAttr( 'body_001_jnt.visibility', False )
    place.cleanUp( 'path_00_jnt', World = True )
    cmds.setAttr( 'path_00_jnt.visibility', False )

    # cmds.setAttr( position_ctrl[2] + '.ctrlLayer' + str( 3 ), 1 )
    #
    # return micro_body_cts


def pathIk2( curve = 'path_layer_05_result', position_ctrl = None, start_jnt = 'body_001_jnt', end_jnt = 'body_121_jnt', tail_as_root = False, curve_up = '', fk = False, ribn = 'layer_05_ribbon', X = 1.0 ):
    '''
    based on cmds.pathAnimation()
    spline ik has parametric curve travel, the span between each cv is the same value no matter the length, can have linear travel across entire length of curve
    '''
    new_up = False  # this is a fail, remove code that relates
    # travel control
    PositionCt = None
    if not position_ctrl:
        PositionCt = place.Controller2( 'position', start_jnt, True, 'splineEnd_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'green' ).result
    else:
        PositionCt = position_ctrl
    # create attribute
    t_attr = 'travel'
    travel_min = -1000000.0  # meant to be used as percent. length is 50%, 300% ,of original length
    travel_max = 1000000.0
    place.addAttribute( PositionCt[3], t_attr, travel_min, travel_max, True, 'float' )
    mlt_merge_travel_length = cmds.shadingNode( 'multDoubleLinear', n = PositionCt[3] + '_mergeLengthMlt', asUtility = True )  # connect below, twice
    cmds.connectAttr( PositionCt[3] + '.' + t_attr, mlt_merge_travel_length + '.input1', force = True )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], t_attr, t_attr, set = False, default = None, force = True )
    # root attr
    root_attr = 'backIsRoot'
    place.addAttribute( PositionCt[3], root_attr, 0.0, 1.0, True, 'float' )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], root_attr, root_attr, set = True, default = 1.0, force = True )
    #
    cmds.pointConstraint( start_jnt, PositionCt[0], mo = True )
    cmds.orientConstraint( start_jnt, PositionCt[0], mo = True )  # used to be parent: MASTERCT()[2]
    place.setChannels( PositionCt[2], [True, False], [True, False], [True, False], [True, True, False] )
    place.cleanUp( PositionCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( PositionCt[2] + '.v', k = False, cb = False )
    cmds.setAttr( PositionCt[2] + '.ro', k = False, cb = False )
    cmds.setAttr( PositionCt[2] + '.Offset_Vis', k = False, cb = False )
    #
    misc.optEnum( PositionCt[2], attr = 'extra', enum = 'CONTROL' )

    #
    m_body_attr = 'microBodyVis'
    place.addAttribute( PositionCt[2], m_body_attr, 0, 1, True, 'long' )
    cmds.setAttr( PositionCt[2] + '.' + m_body_attr, k = False, cb = True )
    m_body_grp = cmds.group( em = True, n = 'microBody_Grp' )
    place.cleanUp( m_body_grp, Ctrl = True )
    cmds.connectAttr( PositionCt[2] + '.' + m_body_attr, m_body_grp + '.visibility', force = True )
    #
    m_ground_attr = 'microGroundVis'
    place.addAttribute( PositionCt[2], m_ground_attr, 0, 1, True, 'long' )
    cmds.setAttr( PositionCt[2] + '.' + m_ground_attr, k = False, cb = True )
    m_ground_grp = cmds.group( em = True, n = 'microGround_Grp' )
    place.cleanUp( m_ground_grp, Ctrl = True )
    cmds.connectAttr( PositionCt[2] + '.' + m_ground_attr, m_ground_grp + '.visibility', force = True )
    #
    m_up_attr = 'microUpVis'
    place.addAttribute( PositionCt[2], m_up_attr, 0, 1, True, 'long' )
    cmds.setAttr( PositionCt[2] + '.' + m_up_attr, k = False, cb = False )
    m_up_grp = cmds.group( em = True, n = 'microUp_Grp' )
    place.cleanUp( m_up_grp, Ctrl = True )
    cmds.connectAttr( PositionCt[2] + '.' + m_up_attr, m_up_grp + '.visibility', force = True )

    # path
    crv_info = cmds.arclen( curve, ch = True, n = ( curve + '_arcLength' ) )  # add math nodes so twist controls stick to body no matter the length of the curve
    arc_length = cmds.getAttr( crv_info + '.arcLength' )  # original
    # new length divide by original length
    dvd_length = cmds.shadingNode( 'multiplyDivide', au = True, n = ( curve + '_lengthDvd' ) )
    cmds.setAttr( ( dvd_length + '.operation' ), 2 )  # set operation: 2 = divide, 1 = multiply
    cmds.connectAttr( ( crv_info + '.arcLength' ), ( dvd_length + '.input1Z' ) )
    cmds.setAttr( dvd_length + '.input2Z', arc_length )
    # create length change multiplier from above result
    dvd_multiplier = cmds.shadingNode( 'multiplyDivide', au = True, n = ( curve + '_lockDvd' ) )  # create length change multiplier, locks control in place from curve length changes
    cmds.setAttr( ( dvd_multiplier + '.operation' ), 2 )
    cmds.setAttr( dvd_multiplier + '.input1Z', 1.0 )
    cmds.connectAttr( ( dvd_length + '.outputZ' ), ( dvd_multiplier + '.input2Z' ) )
    cmds.connectAttr( ( dvd_multiplier + '.outputZ' ), ( mlt_merge_travel_length + '.input2' ) )

    length = 0.0
    arc_fraction = 0.0
    # hierarchy
    skin_jnts = get_joint_chain_hier( start_jnt = start_jnt, end_jnt = end_jnt )
    attach_jnts = []
    # create new set of joints at ground level
    if tail_as_root:
        # build reverse chain
        attach_jnts = path_joint_chain( start_jnt = start_jnt, end_jnt = end_jnt, reroot = True )
    else:
        attach_jnts = path_joint_chain( start_jnt = start_jnt, end_jnt = end_jnt )

    # return
    # for parent switches up chain
    micro_body_cts = []
    # attachs
    upCts = []
    #
    ground_cts = []

    i = 0
    for j in attach_jnts:
        # position, startU value
        if j == attach_jnts[0]:
            length = 0.0
        else:
            _l = cmds.getAttr( j + '.translateZ' )  # assumes joint aim vector is translateZ
            length = length + _l  # accumulated length
            arc_fraction = length / arc_length  # accumulated arc length
            # print( 'length: ', length, 'fraction: ', arc_fraction )

        #
        microUpCt = None
        mo_path_up = None
        if curve_up:
            # up vector control
            name = 'micro_up_' + pad_number( i = i )
            microUpCt = place.Controller2( name, j, True, 'loc_ctrl', X * 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
            # cmds.setAttr( microUpCt[1] + '.translateY', 10 ) # has to stay at 0.0
            upCts.append( microUpCt[4] )
            place.translationLock( microUpCt[2] )
            place.rotationLock( microUpCt[2] )
            place.translationYLock( microUpCt[2] )
            # cmds.connectAttr( PositionCt[2] + '.' + m_up_attr, microUpCt[0] + '.visibility', force = True )
            cmds.parent( microUpCt[0], m_up_grp )
            # stick to path
            if not new_up:
                #
                mo_path_up = cmds.pathAnimation( microUpCt[0], name = microUpCt[2] + '_motionPath' , c = curve_up, startU = 0.0, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
                cmds.setAttr( mo_path_up + '.fractionMode', True )  # turn off parametric, sets start/end range 0-1
                ac.deleteAnim2( mo_path_up, attrs = ['uValue'] )

        # control for body
        fk_start = 110
        color = 'brown'
        if i >= fk_start:
            color = 'yellow'
        name = 'micro_body_' + pad_number( i = i )
        microBodyCt = place.Controller2( name, skin_jnts[i], False, 'facetZup_ctrl', X * 3.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        cmds.parent( microBodyCt[0], m_body_grp )
        cmds.parentConstraint( microBodyCt[4], skin_jnts[i], mo = True )
        cmds.parentConstraint( j, microBodyCt[0], mo = True )
        micro_body_cts.append( microBodyCt )
        # fk down chain
        if fk:
            if i >= fk_start:  # old: if i > 0:
                place.parentSwitch( 
                    name = microBodyCt[2],
                    Ct = microBodyCt[2],
                    CtGp = microBodyCt[1],
                    TopGp = microBodyCt[0],
                    ObjOff = j,
                    ObjOn = skin_jnts[i - 1],
                    Pos = False,
                    Ornt = False,
                    Prnt = True,
                    OPT = True,
                    attr = 'fk',
                    w = 0.0 )

        # control on ground
        name = 'micro_ground_' + pad_number( i = i )
        microCt = place.Controller2( name, j, True, 'rectangleWideYup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
        ground_cts.append( microCt )
        cmds.parent( microCt[0], m_ground_grp )
        cmds.parentConstraint( microCt[4], j, mo = False )
        # cmds.parentConstraint( 'master_Grp', microCt[0], mo = True )
        place.addAttribute( microCt[2], 'position', travel_min, travel_max, True, 'float' )  # max is number of points in curve
        cmds.setAttr( microCt[2] + '.position', arc_fraction * 100 )
        cmds.setAttr( microCt[2] + '.position', lock = True )

        # use the first control on the up vector curve
        mo_path = cmds.pathAnimation( microCt[0], name = microCt[2] + '_motionPath' , c = curve, startU = 0.0, follow = True, wut = 'object', wuo = microUpCt[4], fm = False, fa = 'z', ua = 'y' )
        cmds.setAttr( mo_path + '.fractionMode', True )  # turn off parametric, sets start/end range 0-1
        ac.deleteAnim2( mo_path, attrs = ['uValue'] )

        # travel and stretch nodes

        # multiply to merge length changes and position input form control, math prepped at start of function
        mlt_merge_length = cmds.shadingNode( 'multDoubleLinear', n = microCt[2] + '_mergeLengthMlt', asUtility = True )
        cmds.connectAttr( microCt[2] + '.position', mlt_merge_length + '.input1', force = True )
        cmds.connectAttr( dvd_multiplier + '.outputZ', mlt_merge_length + '.input2', force = True )

        # add twist position attr and main travel attr values, quickly growing into maze :(
        dbl_path = cmds.createNode( 'addDoubleLinear', name = ( microCt[2] + '_DblLnr' ) )
        cmds.connectAttr( mlt_merge_length + '.output', dbl_path + '.input1', force = True )
        cmds.connectAttr( mlt_merge_travel_length + '.output', dbl_path + '.input2', force = True )
        # normalize result
        mlt_path = cmds.shadingNode( 'multDoubleLinear', n = microCt[2] + '_normalizeMlt', asUtility = True )
        cmds.setAttr( mlt_path + '.input2', 0.01 )

        # tail lock for stretch, tail as root
        neg_tail_mlt = cmds.createNode( 'multDoubleLinear', name = microCt[2] + '_tailMakeNegative_Mlt' )
        cmds.connectAttr( microCt[2] + '.position', neg_tail_mlt + '.input1', force = True )
        cmds.setAttr( neg_tail_mlt + '.input2', -1.0 )
        #
        sub_tail_add = cmds.createNode( 'addDoubleLinear', name = microCt[2] + '_tailToEnd_Add' )
        cmds.connectAttr( neg_tail_mlt + '.output', sub_tail_add + '.input2' )
        cmds.setAttr( sub_tail_add + '.input1', 100.0 )
        #
        length_tail_mlt = cmds.createNode( 'multDoubleLinear', name = microCt[2] + '_tailLengthChange_Mlt' )
        cmds.connectAttr( sub_tail_add + '.output', length_tail_mlt + '.input1' )
        cmds.connectAttr( dvd_multiplier + '.outputZ', length_tail_mlt + '.input2' )
        #
        lengthNeg_tail_mlt = cmds.createNode( 'multDoubleLinear', name = microCt[2] + '_tailMakeLengthNeg_Mlt' )
        cmds.connectAttr( length_tail_mlt + '.output', lengthNeg_tail_mlt + '.input1' )
        cmds.setAttr( lengthNeg_tail_mlt + '.input2', -1.0 )
        #
        subNew_tail_add = cmds.createNode( 'addDoubleLinear', name = ( microCt[2] + '_tailSubtractNew_Add' ) )
        cmds.setAttr( subNew_tail_add + '.input1', 100.0 )
        cmds.connectAttr( lengthNeg_tail_mlt + '.output', subNew_tail_add + '.input2' )
        #
        # tail travel
        travel_tail_add = cmds.createNode( 'addDoubleLinear', name = ( microCt[2] + '_tailTravel_Add' ) )
        # cmds.connectAttr( position_ctrl[3] + '.' + t_attr, travel_tail_add + '.input1' ) # math doesnt work
        cmds.connectAttr( mlt_merge_travel_length + '.output', travel_tail_add + '.input1' )
        cmds.connectAttr( subNew_tail_add + '.output', travel_tail_add + '.input2' )

        # ADD CLAMPS ON TRAVEL VALUES SO JOINTS SLIDE ON TOP OF THEIR NEIGHBHOURS ON EITHER END

        #
        blnd_root_typs = cmds.shadingNode( 'blendColors', name = ( microCt[2] + '_rootTypeBlend' ), asUtility = True )
        cmds.connectAttr( travel_tail_add + '.output', blnd_root_typs + '.color2R' )  # # change
        cmds.connectAttr( position_ctrl[3] + '.' + root_attr, blnd_root_typs + '.blender', force = True )
        #
        cmds.connectAttr( dbl_path + '.output', blnd_root_typs + '.color1R' )  # into blend before normalizing
        cmds.connectAttr( blnd_root_typs + '.outputR', mlt_path + '.input1', force = True )
        cmds.connectAttr( mlt_path + '.output', mo_path + '.uValue', force = True )

        if new_up:
            fol = ump.follicle_on_nurbs( name = microCt[2] + '_up', ribn = ribn, parent = m_up_grp, u = 0.5 )
            cmds.parentConstraint( fol[0], microUpCt[0], mo = False )
            cmds.connectAttr( mlt_path + '.output', fol[1] + '.parameterV', force = True )
        else:
            # original method
            cmds.connectAttr( mlt_path + '.output', mo_path_up + '.uValue', force = True )

        # connect travel, matching joint below
        if i > 0:
            # cmds.connectAttr( mlt_path + '.output', mo_path_up + '.uValue', force = True )
            # add aim constraint
            # cmds.aimConstraint( attach_jnts[i - 1], microCt[1], mo = True, wuo = microUpCt[4], wut = 'object', aim = [0, 0, 1], u = [0, 1, 0] ) # wrong direction
            cmds.aimConstraint( microCt[4], ground_cts[i - 1][1], mo = True, wuo = upCts[i - 1], wut = 'object', aim = [0, 0, 1], u = [0, 1, 0] )

        #
        i += 1

    # guides
    # guides_grp = guide_many_to_many( PositionCt[2], attach_jnts, upCts, 5 )
    guides_grp = guide_many_to_many( prefix = 'many', vis_object = PositionCt[2], many1 = attach_jnts, many2 = upCts, offset = 0.0, every_nth = 5 )
    '''
    tail lock working, need to add travel offset
    '''
    return micro_body_cts


def get_joint_chain_hier( start_jnt = '', end_jnt = '', chain = None ):
    '''
    cant find end joint if it encounters multiple children
    '''
    # list the children of the parent
    if chain == None:
        chain = []
        chain.append( start_jnt )
    # print( chain )
    children = cmds.listRelatives( start_jnt, children = True )
    # print( children )
    if children:
        for child in children:
            # test the child count
            if child != end_jnt:
                chain.append( child )
                return get_joint_chain_hier( child, end_jnt, chain )
            else:
                chain.append( child )
                # print( '______YUP', child )
                # break
                return chain
    # return None


def path_joint_chain( start_jnt = '', end_jnt = '', reroot = False ):
    '''
    duplicate skin joint chain and reverse hierarchy
    skin joints will be in the middle of the body, path joints need to placed down to ground level
    '''
    #
    skin_jnts = get_joint_chain_hier( start_jnt = start_jnt, end_jnt = end_jnt, chain = None )

    # duplicate
    dup = cmds.duplicate( start_jnt, rc = True )
    # cmds.parent( dup[0], w = True )  # unparent
    #
    # cmds.delete( 'head_jnt1' )  # cleanup children, should automate this at some stage.

    # rename
    cmds.select( dup[0], hi = True )
    names = cmds.ls( sl = True )
    if reroot:
        num = len( names )
        i = num - 1
        for jnt in names:
            cmds.rename( jnt, 'path_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) + '_jnt' )
            i -= 1
    else:
        # num = len( names )
        i = 0
        for jnt in names:
            cmds.rename( jnt, 'path_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) + '_jnt' )
            i += 1

    # reroot chain and fix joint orients
    path_jnts = cmds.ls( sl = True )
    if reroot:
        cmds.reroot( path_jnts[-1] )
        for j in path_jnts:
            if j == path_jnts[0]:  # first is the last joint(reversed list), needs manual correction, maya skips it
                cmds.setAttr( j + '.jointOrientX', 0 )
                cmds.setAttr( j + '.jointOrientY', 0 )
                cmds.setAttr( j + '.jointOrientZ', 0 )
            else:
                cmds.select( j )
                cmds.joint( e = True, oj = 'zyx', secondaryAxisOrient = 'yup', ch = True, zso = True )

    # path_jnts.reverse()
    print( 'duplicated' )
    print( path_jnts )
    # return
    # to ground
    if reroot:
        path_joints_to_ground( path_jnts = path_jnts )
    else:
        path_joints_to_ground( path_jnts = path_jnts )
        # cmds.setAttr( path_jnts[0] + '.translateY', 0 )
    print( 'grounded' )
    print( path_jnts )
    # return

    # constrain
    '''
    # skipping, will add controls instead of joint to joint constraint
    skin_jnts_to_path_jnts( skin_jnts = skin_jnts, path_jnts = path_jnts, controls = True )
    print( 'constrained' )
    print( path_jnts )
    '''
    # return

    if reroot:
        place.cleanUp( path_jnts[-1], SknJnts = True )
    else:
        place.cleanUp( path_jnts[0], SknJnts = True )
    return path_jnts


def guide_many_to_many( prefix = 'many', vis_object = '', many1 = [], many2 = [], offset = 0.0, every_nth = 4 ):
    '''
    
    '''
    grp = cmds.group( name = prefix + '_GuideGrp', em = True )
    print( grp, vis_object )
    place.hijackVis( grp, vis_object, name = 'guides', suffix = True, default = False, mode = 'visibility' )
    place.cleanUp( grp, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    n = 0
    for i in range( len( many1 ) ):
        #
        if n == 0:
            g = cmds.group( name = prefix + '___' + many1[i] + '___' + many2[i], em = True )
            result = place.guideLine( many1[i], many2[i], Name = 'guide' )
            #
            cmds.select( result[1][1] )
            cmds.pickWalk( d = 'down' )
            cmds.pickWalk( d = 'left' )
            c = cmds.ls( sl = True )[0]
            cmds.setAttr( c + '.offsetY', offset )
            #
            cmds.parent( result[0], g )
            cmds.parent( result[1], g )
            cmds.parent( g, grp )
        #
        if n == every_nth - 1:
            n = 0
        else:
            n += 1

    #
    return grp


def path_joints_to_ground( path_jnts = [], reroot = False ):
    '''
    unparent all joints and set tranlsateY to 0.0
    reparent
    '''
    if reroot:
        path_jnts.reverse()
    cmds.parent( path_jnts, w = True )  # world is parent
    for j in path_jnts:
        cmds.setAttr( j + '.translateY', 0.0 )
    for j in range( len( path_jnts ) ):
        if j < len( path_jnts ) - 1:
            cmds.parent( path_jnts[j + 1], path_jnts[j] )
    if reroot:
        path_jnts.reverse()  # for some reason i need to reverse the change as it effects the list outside this function


def connect_to_path():
    '''
    
    '''
    # ref rigs
    vhl = 'vhl'
    path = 'P:\\FLR\\assets\\veh\\cessna\\rig\\maya\\scenes\\cessna_rig_v007.ma'
    cmds.file( path, reference = True, ns = vhl )
    pth = 'pth'
    path = 'P:\\FLR\\assets\\veh\\cessna\\rig\\maya\\scenes\\cessna_path_rig_v002.ma'
    cmds.file( path, reference = True, ns = pth )

    #
    cmds.parentConstraint( pth + ':position', vhl + ':move', mo = False )
    cmds.setAttr( vhl + ':chassis_pivot.translateY', -207.829 )


def __________________GEO():
    pass


def get_geo_list( name = 'cessna', ns = 'geo',
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
                door_upper = False,
                door_lower = False,
                spoiler_l = False,
                spoiler_r = False,
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

    # doors
    if door_lower or all:
        geo_list = process_geo_list( name = name + '_' + 'door_lower' )
        geo_sets.append( geo_list )
    if door_upper or all:
        geo_list = process_geo_list( name = name + '_' + 'door_upper' )
        geo_sets.append( geo_list )

    # spoilers
    if spoiler_l or all:
        geo_list = process_geo_list( name = name + '_' + 'spoiler_l' )
        geo_sets.append( geo_list )
    if spoiler_r or all:
        geo_list = process_geo_list( name = name + '_' + 'spoiler_r' )
        geo_sets.append( geo_list )

    # build list
    for geo_set in geo_sets:
        if geo_set:
            for geo in geo_set:
                if ns:
                    if '|' in geo:  # multiple objs with same name
                        nested_ns = 'ces:'
                        if nested_ns in geo:
                            geo = geo.replace( nested_ns, ns + ':' )
                    if cmds.objExists( geo ):
                        geos.append( geo )
                        print( 'yes', geo )
                    else:
                        if 'pilot' in geo:
                            # geos.append( ns + ':plt:' + geo )
                            pass
                    '''
                    # kingAir method
                    if cmds.objExists( ns + ':ast:' + geo ):
                        geos.append( ns + ':ast:' + geo )
                        print( 'yes', geo )
                    else:
                        if 'pilot' in geo:
                            # geos.append( ns + ':plt:' + geo )
                            pass
                        else:
                            # print( 'not here', geo_set, geo )
                            pass
                            '''
                else:
                    geos.append( geo )

    return geos


def process_geo_list( name = '' ):
    '''
    
    '''
    tire = False
    if 'tire' in name:
        tire = True
    s = []
    setDict = ss.loadDict( os.path.join( ss.defaultPath(), name + '.sel' ) )
    if tire:
        # print( name )
        # print( setDict )
        # print( '___ loaded raw', setDict )
        pass
    if setDict:
        for obj in setDict.keys():
            if tire:
                # print( obj )
                # print( setDict[obj] )
                pass
            s.append( obj )
        # print( s )
        return s
    return None


def low_geo():
    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes_base_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes_base_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes_base',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes_base',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes_cable',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes_base_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes_base_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes_cable',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_right_brakes_base_2_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:chassis_group|geo:ast:rear_left_brakes_base_2_rivets'
    ]
    return geo


def __________________SKIN():
    pass


def weights_meshExport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = low_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
            if ':' in g:
                g = g.split( ':' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        cmds.select( geo )
        krl.exportWeights02( ex_path )


def weights_meshImport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = low_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
            if ':' in g:
                g = g.split( ':' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        # make no constraint
        c = cn.getConstraint( geo, nonKeyedRoute = True, keyedRoute = True, plugRoute = True )
        if c:
            print( c )
            cmds.delete( c )
        cmds.select( geo )
        # print( im_path )
        krl.importWeights02( geo, im_path )


def weights_path():
    '''
    make path if not present from current file
    '''
    # path
    path = cmds.file( query = True, sceneName = True )
    filename = cmds.file( query = True, sceneName = True , shortName = True )
    path = path.split( filename )[0]
    path = os.path.join( path, 'weights' )
    if not os.path.isdir( path ):
        os.mkdir( path )
    return path


def default_skin( joints = [], geos = [], mi = 1 ):
    '''
    skin geo list to joint
    mi = max influence
    '''
    #
    # alternate method
    # cmds.select( [geo_hub[1], jnt_hub[1]] )
    # mel.eval( 'SmoothBindSkin;' )
    #
    sel = cmds.ls( sl = 1 )
    # print( len( geos ), geos )
    # skin
    for g in geos:
        # print( g )
        # delete constraint
        c = cn.getConstraint( g, nonKeyedRoute = True, keyedRoute = True, plugRoute = True )
        if c:
            print( c )
            cmds.delete( c )
        #
        cmds.select( joints )
        cmds.select( g, add = True )
        mel.eval( 'SmoothBindSkin "-mi ' + str( mi ) + '";' )
    cmds.select( sel )


def __________________UTIL():
    pass


def MASTERCT():
    return [
    'master_TopGrp',
    'master_CtGrp',
    'master',
    'master_Offset',
    'master_Grp'
    ]


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def constraint_delete( obj = '' ):
    '''
    
    '''
    c = cn.getConstraint( obj, nonKeyedRoute = True, keyedRoute = True, plugRoute = True )
    if c:
        print( c )
        cmds.delete( c )


def fix_normals( del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    geo = get_geo_list( name = 'cessna', ns = 'geo', tire_front_l = True, tire_back_l = True, tire_back_r = True )
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
    'axle_back_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = True )


def rename_files( s = 'kingAir', r = 'cessna', d = 'C:\\Users\\s.weber\\Documents\\maya\\selectionSets' ):
    '''
    s = search
    r = replace
    d = directory
    '''
    return
    # List all files in the current working directory
    files = os.listdir( d )
    i = 1

    for f in files:
        # print( f )
        if s in f:
            replaced = f.replace( s, r )
            # print( 'here', s )
            path_from = os.path.join( d, f )
            path_to = os.path.join( d, replaced )
            print( path_to )
            os.rename( path_from, path_to )
        else:
            # print( 'no', fyl )
            pass
        i += 1


def blade_1_3x():

    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:propeller_3x_group|geo:ast:blades_3x_01'
    ]
    return geo


def blade_2_3x():

    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:propeller_3x_group|geo:ast:blades_3x_02'
    ]
    return geo


def blade_3_3x():

    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:propeller_3x_group|geo:ast:blades_3x_03'
    ]
    return geo


def flap_broken_geo():

    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_flaps_group|geo:ast:wing_right_flaps_rivets|geo:ast:wing_right_flaps_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_flaps_group|geo:ast:wing_right_flaps|geo:ast:wing_right_flaps',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_flaps_group|geo:ast:wing_right_flaps_track_joint|geo:ast:wing_right_flaps_track_joint'
    ]
    return geo


def wing_broken_geo():

    geo = [
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_glass_rear|geo:ast:wing_right_position_lights_glass_rear',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_fuel_cap_screw|geo:ast:wing_right_fuel_cap_screw',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_rivets|geo:ast:wing_right_position_lights_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_skin_top_rivets|geo:ast:wing_right_skin_top_rivets',
    'geo:ast:wing_right_landing_light_reflectors',
    'geo:ast:wing_right_leading_edge',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_wires_1|geo:ast:wing_right_landing_light_wires_1',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_flap_track_frames|geo:ast:wing_right_flap_track_frames',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_skin_middle|geo:ast:wing_right_skin_middle',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_glass_bulb_2|geo:ast:wing_right_landing_light_glass_bulb_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_skin_bottom_rivets|geo:ast:wing_right_skin_bottom_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_wires_2|geo:ast:wing_right_landing_light_wires_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_base|geo:ast:wing_right_position_lights_base',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_access_panels_1|geo:ast:wing_right_access_panels_1',
    'geo:ast:wing_right_landing_light_holder',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_fuel_cap|geo:ast:wing_right_fuel_cap',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_glass|geo:ast:wing_right_position_lights_glass',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_wires_rear|geo:ast:wing_right_position_lights_wires_rear',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_rear_pannels|geo:ast:wing_right_rear_pannels',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_metal_rivets|geo:ast:wing_right_metal_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_inner_parts_group|geo:ast:wing_right_landing_light_inner_frames|geo:ast:wing_right_landing_light_inner_frames',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_tip|geo:ast:wing_right_tip',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_glass_lens|geo:ast:wing_right_landing_light_glass_lens',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_tip_rivets|geo:ast:wing_right_tip_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_inner_parts_group|geo:ast:wing_right_ribs|geo:ast:wing_right_ribs',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_tip_outlet|geo:ast:wing_right_tip_outlet',
    'geo:ast:wing_right_landing_light_frame',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_wires_front|geo:ast:wing_right_position_lights_wires_front',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_skin_top|geo:ast:wing_right_skin_top',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_base_front|geo:ast:wing_right_position_lights_base_front',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_inner_parts_group|geo:ast:wing_right_spar|geo:ast:wing_right_spar',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_glass|geo:ast:wing_right_landing_light_glass',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_wing_skin_bottom|geo:ast:wing_right_wing_skin_bottom',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_fuel_decalls|geo:ast:wing_right_fuel_decalls',
    'geo:ast:wing_right_pitot_tube_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_rear_access_panels|geo:ast:wing_right_rear_access_panels',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_access_panels_2|geo:ast:wing_right_access_panels_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_base_1|geo:ast:wing_right_landing_light_base_1',
    'geo:ast:wing_right_pitot_tube_collar',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_base_2|geo:ast:wing_right_landing_light_base_2',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_glass_front|geo:ast:wing_right_position_lights_glass_front',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_inner_parts_group|geo:ast:wing_right_stringer|geo:ast:wing_right_stringer',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_rear_access_panels_rivets|geo:ast:wing_right_rear_access_panels_rivets',
    'geo:ast:wing_right_pitot_tube',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_access_panels_round_rivets|geo:ast:wing_right_access_panels_round_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_small_glass|geo:ast:wing_right_small_glass',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_position_lights_base_rear|geo:ast:wing_right_position_lights_base_rear',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_access_panels_round|geo:ast:wing_right_access_panels_round',
    'geo:ast:wing_right_landing_light_frame_rivets',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_landing_light_glass_bulb_1|geo:ast:wing_right_landing_light_glass_bulb_1',
    'geo:cessna_grp|geo:ast:cessna_208_group|geo:ast:wing_right_group|geo:ast:wing_right_flap_tracks|geo:ast:wing_right_flap_tracks'
    ]
    return geo

#
#
'''
imp.reload( web )
symd = web.mod( "assets_symd" )
symd.king_air()
'''
#
