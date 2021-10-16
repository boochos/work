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
    'wheel_back_steer_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j )


def king_air( name = 'vehicle', X = 160 ):
    '''
    build plane
    '''
    #
    mirror_jnts()
    # mass to pivot, body
    center = 'body_jnt'
    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vhl.vehicle_master( masterX = X * 1, moveX = X * 1 )

    j = 'rudder_00_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = '', obj = j, objConstrain = True, parent = 'body_jnt', rotations = [0, 0, 1], X = X, shape = 'facetZup_ctrl', color = 'yellow' )

    size = X
    # wings left
    clr = 'blue'
    wing_L_jnts = [
    'flaps_00_L_jnt',
    'flaps_02_L_jnt',
    'aileron_00_L_jnt',
    'elevator_00_L_jnt',
    'landing_doorB_00_L_jnt',
    'landing_doorA_00_L_jnt',
    'mufflerA_L_jnt',
    'mufflerB_L_jnt'
    ]
    Ct = []
    for j in wing_L_jnts:
        if 'door' in j or 'muffler' in j:
            size = X / 2
        else:
            size = X
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
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'aileron_00_L_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'facetZup_ctrl', color = clr )
    j = 'elevator_02_L_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'elevator_00_L_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'facetZup_ctrl', color = clr )
    j = 'propeller_L_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = 'body_L_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'shldrL_ctrl', color = clr )

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
            size = X / 2
        else:
            size = X
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
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'aileron_00_R_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'facetZup_ctrl', color = clr )
    j = 'elevator_02_R_jnt'
    n = j.split( '_' )
    nm = n[0] + '_' + n[1]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'elevator_00_R_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'facetZup_ctrl', color = clr )
    j = 'propeller_R_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = 'body_R_jnt', rotations = [0, 0, 1], X = X / 2, shape = 'shldrR_ctrl', color = clr )

    X = 16
    # [frontl, frontr, backl, backr]
    bdy = vhl.four_point_pivot( name = 'body', parent = 'move_Grp', center = center, front = 'front_jnt', frontL = 'front_L_jnt', frontR = 'front_R_jnt', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )
    # print( '_____body' )
    # print( bdy )
    # return

    # FRONT LANDING GEAR
    nm = 'landingGear_front'
    vhl.rotate_part( name = nm, suffix = '', obj = 'landingGear_retract_jnt', objConstrain = True, parent = center, rotations = [1, 0, 0], X = X * 10, shape = 'ballRoll_ctrl', color = 'yellow' )
    # ik pv
    cmds.setAttr( '___SKIN_JOINTS.visibility', 1 )
    name = 'frontA_ik'
    CtA = place.Controller2( name, 'suspension_arm_00_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'landingGear_retract_jnt', CtA[0], mo = True )
    place.cleanUp( CtA[0], Ctrl = True )
    name = 'frontB_ik'
    CtB = place.Controller2( name, 'suspension_arm_02_jnt', False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'axle_front_jnt', CtA[0], mo = True )
    place.cleanUp( CtB[0], Ctrl = True )
    PvCt = app.create_3_joint_pv___FIX( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', prefix = 'front_suspension', suffix = '', distance_multi = 1.0, useFlip = True, flipVar = [0, 0, 0], orient = False, color = 'yellow', X = X * 0.5, midJnt = '' )
    place.cleanUp( PvCt[0], Ctrl = True )
    ik = app.create_ik___FIX( stJnt = 'suspension_arm_00_jnt', endJnt = 'suspension_arm_02_jnt', pv = PvCt[4], parent = CtB[4], name = 'suspension_arm', suffix = '', setChannels = True )
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
    whl = vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'L', X = X * 0.5 )
    print( 'done wheel' )
    cmds.parentConstraint( ctrls[2], whl[0], mo = True )  # steering
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )  # tire tilt with body, will likely remove
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addfl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[0] + '.ty' )
    return
    #
    sel = [
    'axle_front_jnt',
    'wheel_front_steer_R_jnt',
    'wheel_front_center_R_jnt',
    'wheel_front_bottom_R_jnt',
    'wheel_front_top_R_jnt',
    'wheel_front_spin_R_jnt'
    ]
    # whl   = [steer[1], contact[2], center[2], center[1]]
    # ctrls = [MasterCt[4], MoveCt[4], SteerCt[4]]
    whl = vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_R_geo'], rim_geo = ['rim_front_R_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'R', X = X * 1.0 )
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
    whl = vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_L_geo'], rim_geo = ['rim_back_L_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'L', X = X * 1.0 )
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
    whl = vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_R_geo'], rim_geo = ['rim_back_R_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'R', X = X * 1.0 )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addbr_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[3] + '.ty' )

    # bug, contact group in wheels dont update
    cmds.dgdirty( allPlugs = True )
