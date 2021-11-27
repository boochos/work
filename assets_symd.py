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
    'back_L_jnt',
    'front_L_jnt',
    'chassis_L_jnt',
    'axle_back_L_jnt',
    'landing_doorA_00_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = True )


def king_air( X = 16, ns = 'geo', ref_geo = 'P:\\SYMD\\assets\\veh\\kingAirB200\\model\\maya\\scenes\\kingAirB200_model_v003.ma' ):
    '''
    build plane
    '''
    # ref geo
    if ns and ref_geo:
        vhl.reference_geo( ns = ns, path = ref_geo )
    #
    mirror_jnts()

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vhl.vehicle_master( masterX = X * 10, moveX = X * 10, steerParent = 'landingGear_retract_jnt' )
    # mass to pivot, chassis
    chassis_joint = 'chassis_jnt'
    chassis_geo = get_geo_list( chassis = True )
    vhl.skin( chassis_joint, chassis_geo )
    # pivot_controls = [frontl, frontr, backl, backr] use to be control[2] is now returning entire structure[0-4]
    pivot_controls = vhl.four_point_pivot( name = 'chassis', parent = 'move_Grp', center = chassis_joint, front = 'wheel_front_bottom_L_jnt', frontL = '', frontR = '', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )

    #
    landing_gear_front( ctrls, chassis_joint, pivot_controls, X )
    landing_gear_left( ctrls, chassis_joint, pivot_controls, X )
    landing_gear_right( ctrls, chassis_joint, pivot_controls, X )
    wings( X )
    # hoses( X )


def landing_gear_front( ctrls = [], chassis_joint = '', pivot_controls = [], X = 1.0 ):
    '''
    
    '''
    #
    hide = []
    # main
    nm = 'landingGear_front'
    vhl.rotate_part( name = nm, suffix = '', obj = 'landingGear_retract_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 8, shape = 'squareXup_ctrl', color = 'yellow' )
    # ctrls  = [MasterCt[4], MoveCt[4], SteerCt[4]]
    # piston = [name1_Ct, name2_Ct, nameUp1_Ct, nameUp2_Ct]
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt',
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
    # retract landing gear ik
    name = 'front_A_retract_arm'
    CtA = place.Controller2( name, 'landing_arm_00_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( chassis_joint, CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'landing_arm_00_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'front_B_retract_arm'
    CtB = place.Controller2( name, 'landing_arm_02_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'landing_arm_00_jnt', endJnt = 'landing_arm_02_jnt', prefix = 'front_retract', suffix = '', distance_offset = 0.0, orient = True, color = 'yellow', X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'landingGear_retract_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    #
    ik = app.create_ik2( stJnt = 'landing_arm_00_jnt', endJnt = 'landing_arm_02_jnt', pv = PvCt[4], parent = CtB[4], name = 'front_retract', suffix = '', setChannels = True )
    # landing gear / suspension link node (position from upper suspension, rotation from lower suspension)
    name = 'front_suspension_steer_link'
    LinkCt = place.Controller2( name, 'suspension_piston_00_jnt', True, 'squareYup_ctrl', X, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', LinkCt[0], mo = True )
    cmds.orientConstraint( 'suspension_piston_01_jnt', LinkCt[1], mo = True )
    place.cleanUp( LinkCt[0], Ctrl = True )
    hide.append( LinkCt[0] )
    # steering piston
    pstnCtrls = vhl.piston( name = 'steer_piston', suffix = '', obj1 = 'steering_piston_00_jnt', obj2 = 'steering_piston_01_jnt',
                            parent1 = 'suspension_piston_00_jnt', parent2 = LinkCt[4], parentUp1 = 'suspension_piston_00_jnt', parentUp2 = LinkCt[4],
                            aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'yellow' )
    hide.append( pstnCtrls[0][0] )
    hide.append( pstnCtrls[1][0] )
    # ik pv
    # return
    # suspension ik
    name = 'front_A_suspension_arm'
    CtA = place.Controller2( name, 'suspension_arm_00_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( LinkCt[4], CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'suspension_arm_00_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'front_B_suspension_arm'
    CtB = place.Controller2( name, 'suspension_arm_02_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'suspension_piston_01_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', prefix = 'front_suspension', suffix = '', distance_offset = 0.0, orient = True, color = 'yellow', X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    #
    ik = app.create_ik2( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', pv = PvCt[4], parent = CtB[4], name = 'front_suspension', suffix = '', setChannels = True )
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
    # whl   = [steer, ContactCt, CenterCt] # old = [steer, contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    whl = vhl.wheel( master_move_controls = [ctrls[0], 'suspension_piston_01_jnt'], axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = '', X = X * 0.5, exp = False )
    # whl   = [steer, ContactCt, CenterCt]
    # pivot_controls   = [frontl, frontr, backl, backr]
    place.smartAttrBlend( master = whl[2][2], slave = pivot_controls[0][4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whl[2][2], slave = whl[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    # return


def landing_gear_left( ctrls = [], chassis_joint = '', pivot_controls = [], X = 1.0 ):
    '''
    back left landing gear
    '''
    #
    hide = []
    # main
    clr = 'blue'
    suffix = 'L'
    nm = 'landingGear_back'
    vhl.rotate_part( name = nm, suffix = suffix, obj = 'landingGear_retract_L_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 8, shape = 'squareXup_ctrl', color = clr )
    # suspension piston
    # pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt', parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2],
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = suffix, obj1 = 'suspension_piston_00_L_jnt', obj2 = 'suspension_piston_01_L_jnt',
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
    # retract landing gear ik
    name = 'back_A_retract_arm' + '_' + suffix
    CtA = place.Controller2( name, 'landing_arm_00_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( chassis_joint, CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'landing_arm_00_L_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_retract_arm' + '_' + suffix
    CtB = place.Controller2( name, 'landing_arm_02_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'landingGear_retract_L_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'landing_arm_00_L_jnt', endJnt = 'landing_arm_02_L_jnt', prefix = 'back_retract', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'landingGear_retract_L_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    #
    ik = app.create_ik2( stJnt = 'landing_arm_00_L_jnt', endJnt = 'landing_arm_02_L_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_retract', suffix = suffix, setChannels = True )

    # ik pv
    # suspension ik
    name = 'back_A_suspension_arm' + '_' + suffix
    CtA = place.Controller2( name, 'suspension_arm_00_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_00_L_jnt', CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'suspension_arm_00_L_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_suspension_arm' + '_' + suffix
    CtB = place.Controller2( name, 'suspension_arm_02_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_01_L_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'suspension_arm_00_L_jnt', endJnt = 'suspension_arm_02_L_jnt', prefix = 'back_suspension', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_L_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    # return
    #
    ik = app.create_ik2( stJnt = 'suspension_arm_00_L_jnt', endJnt = 'suspension_arm_02_L_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_suspension', suffix = suffix, setChannels = True )

    # back A
    sel = [
    'axle_back_L_jnt',
    'wheelA_back_steer_L_jnt',
    'wheelA_back_center_L_jnt',
    'wheelA_back_bottom_L_jnt',
    'wheelA_back_top_L_jnt',
    'wheelA_back_spin_L_jnt'
    ]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'suspension_piston_01_L_jnt']
    whlA = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5],
                     tire_geo = ['tireA_back_L_geo'], rim_geo = ['rimA_back_L_geo'], caliper_geo = [], name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False )
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
                     tire_geo = ['tireB_back_L_geo'], rim_geo = ['rimB_back_L_geo'], caliper_geo = [], name = 'wheelB_back', suffix = suffix, X = X * 0.25, exp = False )
    # whlB = [steer, ContactCt, PressureCt]
    place.smartAttrBlend( master = whlB[2][2], slave = whlB[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = whlA[2][2], slave = whlB[2][2], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.translationYLock( whlB[2][2], True )

    # landing gear doors
    j = 'landing_doorA_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'chassis_jnt', rotations = [0, 0, 1], X = X * 2.3, shape = 'squareZup_ctrl', color = 'yellow' )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def landing_gear_right( ctrls = [], chassis_joint = '', pivot_controls = [], X = 1.0 ):
    '''
    back right landing gear
    '''
    #
    hide = []
    # main
    clr = 'red'
    suffix = 'R'
    nm = 'landingGear_back'
    vhl.rotate_part( name = nm, suffix = suffix, obj = 'landingGear_retract_R_jnt', objConstrain = True, parent = chassis_joint, rotations = [1, 0, 0], X = X * 8, shape = 'squareXup_ctrl', color = clr )
    # suspension piston
    # pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt', parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2],
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = suffix, obj1 = 'suspension_piston_00_R_jnt', obj2 = 'suspension_piston_01_R_jnt',
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
    # retract landing gear ik
    name = 'back_A_retract_arm' + '_' + suffix
    CtA = place.Controller2( name, 'landing_arm_00_R_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( chassis_joint, CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'landing_arm_00_R_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_retract_arm' + '_' + suffix
    CtB = place.Controller2( name, 'landing_arm_02_R_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'landingGear_retract_R_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'landing_arm_00_R_jnt', endJnt = 'landing_arm_02_R_jnt', prefix = 'back_retract', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'landingGear_retract_R_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    #
    ik = app.create_ik2( stJnt = 'landing_arm_00_R_jnt', endJnt = 'landing_arm_02_R_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_retract', suffix = suffix, setChannels = True )

    # ik pv
    # suspension ik
    name = 'back_A_suspension_arm' + '_' + suffix
    CtA = place.Controller2( name, 'suspension_arm_00_R_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_00_R_jnt', CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'suspension_arm_00_R_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    hide.append( CtA[0] )
    #
    name = 'back_B_suspension_arm' + '_' + suffix
    CtB = place.Controller2( name, 'suspension_arm_02_R_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'suspension_piston_01_R_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    hide.append( CtB[0] )
    #
    PvCt = app.create_3_joint_pv2( stJnt = 'suspension_arm_00_R_jnt', endJnt = 'suspension_arm_02_R_jnt', prefix = 'back_suspension', suffix = suffix, distance_offset = 0.0, orient = True, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_R_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    hide.append( PvCt[0] )
    # return
    #
    ik = app.create_ik2( stJnt = 'suspension_arm_00_R_jnt', endJnt = 'suspension_arm_02_R_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_suspension', suffix = suffix, setChannels = True )

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
                     tire_geo = ['tireA_back_R_geo'], rim_geo = ['rimA_back_R_geo'], caliper_geo = [], name = 'wheelA_back', suffix = suffix, X = X * 0.5, exp = False )
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
                     tire_geo = ['tireB_back_R_geo'], rim_geo = ['rimB_back_R_geo'], caliper_geo = [], name = 'wheelB_back', suffix = suffix, X = X * 0.25, exp = False )
    # whlB = [steer, ContactCt, PressureCt]
    place.smartAttrBlend( master = whlB[2][2], slave = whlB[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = whlA[2][2], slave = whlB[2][2], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.translationYLock( whlB[2][2], True )

    # return

    # landing gear doors
    j = 'landing_doorA_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'chassis_jnt', rotations = [0, 0, 1], X = X * 2.3, shape = 'squareZup_ctrl', color = 'yellow' )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def wings( X = 1.0 ):
    '''
    wings flaps and things
    '''
    #
    hide = []
    #
    j = 'rudder_00_jnt'
    geo = get_geo_list( rudder_c = True )
    vhl.skin( j, geo )
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = 'chassis_jnt', rotations = [0, 0, 1], X = X * 6, shape = 'rectangleTallYup_ctrl', color = 'yellow' )

    size = X
    # wings left
    clr = 'blue'
    wing_L_jnts = [
    'flaps_00_L_jnt',
    'flaps_02_L_jnt',
    'aileron_00_L_jnt',
    'elevator_00_L_jnt',
    'landing_doorB_00_L_jnt',
    'landing_doorC_00_L_jnt',
    'mufflerA_L_jnt',
    'mufflerB_L_jnt'
    ]
    # REMOVED MUFFLERS
    wing_L_jnts = [
    'flaps_00_L_jnt',
    'flaps_02_L_jnt',
    'aileron_00_L_jnt',
    'elevator_00_L_jnt',
    'landing_doorB_00_L_jnt',
    'landing_doorC_00_L_jnt'
    ]
    Ct = []
    shape = 'rectangleWideXup_ctrl'
    for j in wing_L_jnts:
        if 'door' in j or 'muffler' in j:
            size = X * 3
            shape = 'squareZup_ctrl'
        else:
            size = X * 6
        if 'muffler' in j:
            nm = j.split( '_' )[0]
        else:
            n = j.split( '_' )
            nm = n[0] + '_' + n[1]
        ct = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'chassis_L_jnt', rotations = [0, 0, 1], X = size, shape = shape, color = clr )
        Ct.append( ct )
    # place.translationLock( Ct[6][2], False ) # muffler
    # place.translationLock( Ct[7][2], False ) # muffler
    #
    parent = 'aileron_00_L_jnt'
    geo = get_geo_list( aileron_l = True )
    vhl.skin( parent, geo )
    j = 'aileron_02_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'rectangleWideXup_ctrl', color = clr )
    #
    parent = 'elevator_00_L_jnt'
    geo = get_geo_list( elevator_l = True )
    vhl.skin( parent, geo )
    j = 'elevator_02_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'rectangleWideXup_ctrl', color = clr )
    #
    parent = 'chassis_L_jnt'
    j = 'propeller_L_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 7, shape = 'shldrR_ctrl', color = clr )
    geo = get_geo_list( prop_l = True )
    vhl.skin( j, geo )

    size = X * 1
    # wings right
    clr = 'red'
    wing_R_jnts = []
    for j in wing_L_jnts:
        jr = j.replace( '_L_', '_R_' )
        wing_R_jnts.append( jr )
    #
    Ct = []
    shape = 'rectangleWideXup_ctrl'
    for j in wing_R_jnts:
        if 'door' in j or 'muffler' in j:
            size = X * 3
            shape = 'squareZup_ctrl'
        else:
            size = X * 6
        if 'muffler' in j:
            nm = j.split( '_' )[0]
        else:
            n = j.split( '_' )
            nm = n[0] + '_' + n[1]
        ct = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'chassis_R_jnt', rotations = [0, 0, 1], X = size, shape = shape, color = clr )
        Ct.append( ct )
    # place.translationLock( Ct[6][2], False ) # muffler
    # place.translationLock( Ct[7][2], False ) # muffler
    #
    parent = 'aileron_00_R_jnt'
    geo = get_geo_list( aileron_r = True )
    vhl.skin( parent, geo )
    j = 'aileron_02_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'rectangleWideXup_ctrl', color = clr )
    #
    parent = 'elevator_00_R_jnt'
    geo = get_geo_list( elevator_r = True )
    vhl.skin( parent, geo )
    j = 'elevator_02_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 3, shape = 'rectangleWideXup_ctrl', color = clr )
    #
    parent = 'chassis_R_jnt'
    j = 'propeller_R_jnt'
    nm = j.split( '_' )[0]
    PrpCt = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = parent, rotations = [0, 0, 1], X = X * 7, shape = 'shldrR_ctrl', color = clr )
    ro = cmds.xform( PrpCt[0], query = True, os = True, ro = True )
    cmds.xform( PrpCt[0], os = True, ro = [ro[0], ro[1] + 180, ro[2] + 180] )
    cn.updateConstraintOffset( PrpCt[0] )
    geo = get_geo_list( prop_r = True )
    vhl.skin( j, geo )

    # hide unnecessary
    for i in hide:
        cmds.setAttr( i + '.visibility', 0 )


def hoses( X = 1.0 ):
    '''
    
    '''
    #
    size = X * 0.15
    # Left
    name = 'hoseA_L'
    vhl.spline( name = name, start_jnt = 'hoseA_01_L', end_jnt = 'hoseA_15_L', splinePrnt = 'suspension_piston_00_L_jnt', splineStrt = 'suspension_piston_00_L_jnt', splineEnd = 'suspension_piston_01_L_jnt', startSkpR = False, endSkpR = False, color = 'blue', X = size )
    #
    name = 'hoseB_L'
    vhl.spline( name = name, start_jnt = 'hoseB_01_L', end_jnt = 'hoseB_17_L', splinePrnt = 'suspension_piston_00_L_jnt', splineStrt = 'suspension_piston_00_L_jnt', splineEnd = 'suspension_piston_01_L_jnt', startSkpR = False, endSkpR = False, color = 'blue', X = size )

    # Right
    name = 'hoseA_R'
    vhl.spline( name = name, start_jnt = 'hoseA_01_R', end_jnt = 'hoseA_15_R', splinePrnt = 'suspension_piston_00_R_jnt', splineStrt = 'suspension_piston_00_R_jnt', splineEnd = 'suspension_piston_01_R_jnt', startSkpR = False, endSkpR = False, color = 'red', X = size )
    #
    name = 'hoseB_R'
    vhl.spline( name = name, start_jnt = 'hoseB_01_R', end_jnt = 'hoseB_17_R', splinePrnt = 'suspension_piston_00_R_jnt', splineStrt = 'suspension_piston_00_R_jnt', splineEnd = 'suspension_piston_01_R_jnt', startSkpR = False, endSkpR = False, color = 'red', X = size )


def get_geo_list( name = 'kingAir', ns = 'geo',
                aileron_l = False,
                aileron_r = False,
                caliper_back_l = False,
                caliper_back_r = False,
                caliper_front_c = False,
                chassis = False,
                elevator_l = False,
                elevator_r = False,
                flaps_l = False,
                flaps_r = False,
                hoses_back_l = False,
                hoses_back_r = False,
                landingDoorA_l = False,
                landingDoorA_r = False,
                landingDoorB_l = False,
                landingDoorB_r = False,
                landingDoorC_l = False,
                landingDoorC_r = False,
                pistonBottom_back_l = False,
                pistonBottom_back_r = False,
                pistonBottom_front_c = False,
                pistonTop_back_l = False,
                pistonTop_back_r = False,
                pistonTop_front_c = False,
                prop_l = False,
                prop_r = False,
                rim_back_l = False,
                rim_back_r = False,
                rim_front_c = False,
                rudder_c = False,
                steerPistonBottom = False,
                steerPistonTop = False,
                suspensionArmBottom_c = False,
                suspensionArmBottom_l = False,
                suspensionArmBottom_r = False,
                suspensionArmTop_c = False,
                suspensionArmTop_l = False,
                suspensionArmTop_r = False,
                tire_back_l = False,
                tire_back_r = False,
                tire_front_c = False,
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

    # flaps
    if flaps_l or all:
        geo_list = process_geo_list( name = name + '_' + 'flaps_l' )
        geo_sets.append( geo_list )
    if flaps_r or all:
        geo_list = process_geo_list( name = name + '_' + 'flaps_r' )
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
    if landingDoorC_l or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorC_l' )
        geo_sets.append( geo_list )
    if landingDoorC_r or all:
        geo_list = process_geo_list( name = name + '_' + 'landingDoorC_r' )
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

    # rims
    if rim_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_l' )
        geo_sets.append( geo_list )
    if rim_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_r' )
        geo_sets.append( geo_list )
    if rim_front_c or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_front_c' )
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

    # suspension Arm Bottom
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

    # tires
    if tire_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_l' )
        geo_sets.append( geo_list )
    if tire_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_r' )
        geo_sets.append( geo_list )
    if tire_front_c or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_front_c' )
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
