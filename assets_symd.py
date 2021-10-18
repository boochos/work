import os

from atom_face_lib import skn
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
jnt = web.mod( 'atom_joint_lib' )
anm = web.mod( "anim_lib" )
vhl = web.mod( 'vehicle_lib' )
app = web.mod( "atom_appendage_lib" )


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
    # jnts
    mirrorj = [
    'front_L_jnt',
    'back_L_jnt',
    'body_L_jnt',
    'axle_back_L_jnt',
    'landing_doorA_00_L_jnt'
    ]
    # jnts - new joints for pivots
    mirrorj = [
    'front_L_jnt',
    'back_L_jnt',
    'body_L_jnt',
    'axle_back_L_jnt',
    'landing_doorA_00_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j )


def king_air( name = 'vehicle', X = 16 ):
    '''
    build plane
    '''
    #
    mirror_jnts()
    # mass to pivot, body
    bodyj = 'body_jnt'
    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vhl.vehicle_master( masterX = X * 10, moveX = X * 10, steerParent = 'landingGear_retract_jnt' )
    # ctrls = vhl.vehicle_master( masterX = X * 1, moveX = X * 1 )
    cmds.setAttr( '___SKIN_JOINTS.visibility', 1 )

    # [frontl, frontr, backl, backr]
    bdy = vhl.four_point_pivot( name = 'body', parent = 'move_Grp', center = bodyj, front = 'front_jnt', frontL = 'front_L_jnt', frontR = 'front_R_jnt', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )

    j = 'rudder_00_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = 'body_jnt', rotations = [0, 0, 1], X = X * 10, shape = 'facetZup_ctrl', color = 'yellow' )
    j = 'landing_doorA_00_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'body_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = 'yellow' )
    j = 'landing_doorA_00_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'body_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = 'yellow' )

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
    Ct = []
    for j in wing_L_jnts:
        if 'door' in j or 'muffler' in j:
            size = X * 5
        else:
            size = X * 10
        if 'muffler' in j:
            nm = j.split( '_' )[0]
        else:
            n = j.split( '_' )
            nm = n[0] + '_' + n[1]
        ct = vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'body_L_jnt', rotations = [0, 0, 1], X = size, shape = 'facetZup_ctrl', color = clr )
        Ct.append( ct )
    place.translationLock( Ct[6][2], False )
    place.translationLock( Ct[7][2], False )
    #
    j = 'aileron_02_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'aileron_00_L_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = clr )
    j = 'elevator_02_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'elevator_00_L_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = clr )
    j = 'propeller_L_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'body_L_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'shldrL_ctrl', color = clr )

    size = X * 1
    # wings right
    clr = 'red'
    wing_R_jnts = []
    for j in wing_L_jnts:
        jr = j.replace( '_L_', '_R_' )
        wing_R_jnts.append( jr )
    Ct = []
    for j in wing_R_jnts:
        if 'door' in j or 'muffler' in j:
            size = X * 5
        else:
            size = X * 10
        if 'muffler' in j:
            nm = j.split( '_' )[0]
        else:
            n = j.split( '_' )
            nm = n[0] + '_' + n[1]
        ct = vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'body_R_jnt', rotations = [0, 0, 1], X = size, shape = 'facetZup_ctrl', color = clr )
        Ct.append( ct )
    place.translationLock( Ct[6][2], False )
    place.translationLock( Ct[7][2], False )
    #
    j = 'aileron_02_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'aileron_00_R_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = clr )
    j = 'elevator_02_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'elevator_00_R_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'facetZup_ctrl', color = clr )
    j = 'propeller_R_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'body_R_jnt', rotations = [0, 0, 1], X = X * 5, shape = 'shldrR_ctrl', color = clr )
    # return

    # FRONT LANDING GEAR
    # main
    nm = 'landingGear_front'
    vhl.rotate_part( name = nm, suffix = '', obj = 'landingGear_retract_jnt', objConstrain = True, parent = bodyj, rotations = [1, 0, 0], X = X * 8, shape = 'facetXup_ctrl', color = 'yellow' )
    # suspension piston - ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    pstnCtrls = vhl.piston( name = 'suspension_piston', suffix = '', obj1 = 'suspension_piston_00_jnt', obj2 = 'suspension_piston_01_jnt', parent1 = 'landingGear_retract_jnt', parent2 = 'landingGear_retract_jnt', parentUp1 = 'landingGear_retract_jnt', parentUp2 = ctrls[2], aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 7, color = 'yellow' )
    # return
    # retract landing gear ik
    name = 'front_A_retract_arm'
    CtA = place.Controller2( name, 'landing_arm_00_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( bodyj, CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'landing_arm_00_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    #
    name = 'front_B_retract_arm'
    CtB = place.Controller2( name, 'landing_arm_02_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv___FIX( stJnt = 'landing_arm_00_jnt', endJnt = 'landing_arm_02_jnt', prefix = 'front_retract', suffix = '', distance_multi = 1.0, useFlip = True, flipVar = [0, 0, 0], orient = False, color = 'yellow', X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'landingGear_retract_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    #
    ik = app.create_ik___FIX( stJnt = 'landing_arm_00_jnt', endJnt = 'landing_arm_02_jnt', pv = PvCt[4], parent = CtB[4], name = 'front_retract', suffix = '', setChannels = True )
    # landing gear / suspension link node (position from upper suspension, rotation from lower suspension)
    name = 'front_suspension_steer_link'
    LinkCt = place.Controller2( name, 'suspension_piston_00_jnt', True, 'facetZup_ctrl', X, 6, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', LinkCt[0], mo = True )
    cmds.orientConstraint( 'suspension_piston_01_jnt', LinkCt[1], mo = True )
    place.cleanUp( LinkCt[0], Ctrl = True )
    # steering piston
    vhl.piston( name = 'steer_piston', suffix = '', obj1 = 'steering_piston_00_jnt', obj2 = 'steering_piston_01_jnt', parent1 = 'suspension_piston_00_jnt', parent2 = LinkCt[4], parentUp1 = 'suspension_piston_00_jnt', parentUp2 = LinkCt[4], aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 0.5, color = 'yellow' )
    # ik pv
    # return
    # suspension ik
    name = 'front_A_suspension_arm'
    CtA = place.Controller2( name, 'suspension_arm_00_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( LinkCt[4], CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'suspension_arm_00_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    #
    name = 'front_B_suspension_arm'
    CtB = place.Controller2( name, 'suspension_arm_02_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'suspension_piston_01_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv___FIX( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', prefix = 'front_suspension', suffix = '', distance_multi = 1.0, useFlip = True, flipVar = [0, 0, 0], orient = False, color = 'yellow', X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'suspension_piston_01_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    #
    ik = app.create_ik___FIX( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', pv = PvCt[4], parent = CtB[4], name = 'front_suspension', suffix = '', setChannels = True )
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
    # whl   = [steer[1], contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    whl = vhl.wheel( master_move_controls = [ctrls[0], 'suspension_piston_01_jnt'], axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = '', X = X * 0.5, exp = False )
    # return
    print( 'done wheel' )
    # cmds.parentConstraint( ctrls[2], whl[0], mo = True )  # steering
    cmds.orientConstraint( ctrls[2], whl[0], mo = True )  # steering, no aim constraint
    cmds.orientConstraint( bodyj, whl[3], skip = ( 'x', 'y' ) )  # tire tilt with body, will likely remove
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = 'body' + '_add_fl_ty' )
    cmds.connectAttr( pstnCtrls[1][2] + '.tz', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    # [frontl, frontr, backl, backr]
    cmds.connectAttr( addfl + '.output', bdy[0] + '.ty' )
    cmds.connectAttr( addfl + '.output', bdy[1] + '.ty' )  # single front wheel, connecting right side as well

    return

    # BACK L LANDING GEAR
    # main
    clr = 'blue'
    suffix = 'L'
    nm = 'landingGear_back'
    vhl.rotate_part( name = nm, suffix = 'L', obj = 'landingGear_retract_L_jnt', objConstrain = True, parent = bodyj, rotations = [1, 0, 0], X = X * 8, shape = 'facetXup_ctrl', color = clr )
    # ik pv
    # suspension ik
    name = 'back_A_suspension_arm' + '_' + suffix
    CtA = place.Controller2( name, 'suspension_arm_00_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'wheelA_back_steer_L_jnt', CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'suspension_arm_00_L_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    #
    name = 'back_B_suspension_arm' + '_' + suffix
    CtB = place.Controller2( name, 'suspension_arm_02_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'wheelA_back_center_L_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv___FIX( stJnt = 'suspension_arm_00_L_jnt', endJnt = 'suspension_arm_02_L_jnt', prefix = 'back_suspension', suffix = suffix, distance_multi = 1.0, useFlip = True, flipVar = [0, 0, 0], orient = False, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'wheelA_back_steer_L_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    # return
    #
    ik = app.create_ik___FIX( stJnt = 'suspension_arm_00_L_jnt', endJnt = 'suspension_arm_02_L_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_suspension', suffix = suffix, setChannels = True )
    # suspension piston
    vhl.piston( name = 'suspension_piston', suffix = suffix, obj1 = 'suspension_piston_00_L_jnt', obj2 = 'suspension_piston_01_L_jnt', parent1 = 'landingGear_retract_L_jnt', parent2 = 'wheelA_back_steer_L_jnt', aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, -1], up2 = [0, 1, 0], X = X * 1, color = clr )
    # retract landing gear ik
    name = 'back_A_retract_arm' + '_' + suffix
    CtA = place.Controller2( name, 'landing_arm_00_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( bodyj, CtA[0], mo = True )
    cmds.pointConstraint( CtA[4], 'landing_arm_00_L_jnt', mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    #
    name = 'back_B_retract_arm' + '_' + suffix
    CtB = place.Controller2( name, 'landing_arm_02_L_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clr ).result
    cmds.parentConstraint( 'landingGear_retract_L_jnt', CtB[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv___FIX( stJnt = 'landing_arm_00_L_jnt', endJnt = 'landing_arm_02_L_jnt', prefix = 'back_retract', suffix = suffix, distance_multi = 1.0, useFlip = True, flipVar = [0, 0, 0], orient = False, color = clr, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( 'landingGear_retract_L_jnt', PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    #
    ik = app.create_ik___FIX( stJnt = 'landing_arm_00_L_jnt', endJnt = 'landing_arm_02_L_jnt', pv = PvCt[4], parent = CtB[4], name = 'back_retract', suffix = suffix, setChannels = True )
    return
    '''
    # back A
    sel = [
    'axle_back_L_jnt',
    'wheelA_back_steer_L_jnt',
    'wheelA_back_center_L_jnt',
    'wheelA_back_bottom_L_jnt',
    'wheelA_back_top_L_jnt',
    'wheelA_back_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'landingGear_retract_L_jnt', ctrls[2]]
    whl = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tireA_back_L_geo'], rim_geo = ['rimA_back_L_geo'], caliper_geo = [], name = 'wheelA_back', suffix = suffix, X = X * 0.5 )
    cmds.orientConstraint( bodyj, whl[3], skip = ( 'x', 'y' ) )
    # body pivots connection from wheel contact
    addfl = cmds.createNode( 'addDoubleLinear', name = 'body' + '_add_bl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[2] + '.ty' )
    # back B
    sel = [
    'axle_back_L_jnt',
    'wheelB_back_steer_L_jnt',
    'wheelB_back_center_L_jnt',
    'wheelB_back_bottom_L_jnt',
    'wheelB_back_top_L_jnt',
    'wheelB_back_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    new_ctrls = [ctrls[0], 'landingGear_retract_L_jnt', ctrls[2]]
    whl = vhl.wheel( master_move_controls = new_ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tireB_back_L_geo'], rim_geo = ['rimB_back_L_geo'], caliper_geo = [], name = 'wheelB_back', suffix = suffix, X = X * 0.5 )
    cmds.orientConstraint( bodyj, whl[3], skip = ( 'x', 'y' ) )
    '''
    return

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
    whl = vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_R_geo'], rim_geo = ['rim_back_R_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'R', X = X * 1.0 )
    cmds.orientConstraint( bodyj, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_add_br_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[3] + '.ty' )

    # bug, contact group in wheels dont update
    cmds.dgdirty( allPlugs = True )
