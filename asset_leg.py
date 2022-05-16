import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
cw = web.mod( 'createWrap' )
zero = web.mod( 'zero' )


def CONTROLS():
    return '___CONTROLS'


def legJoints():
    '''
    return leg joints
    '''
    jnts = [
    'hip_jnt',
    'knee_jnt',
    'knee_dbl_jnt',
    'ankleTwist_jnt',
    'ankle_jnt',
    'thumb_01_jnt',
    'thumb_02_jnt',
    'thumb_03_jnt',
    'index_01_jnt',
    'index_02_jnt',
    'index_03_jnt',
    'ring_01_jnt',
    'ring_02_jnt',
    'ring_03_jnt',
    'middle_01_jnt',
    'middle_02_jnt',
    'middle_03_jnt',
    'pinky_01_jnt',
    'pinky_02_jnt',
    'pinky_03_jnt'
    ]
    return jnts


def leg( *args ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 100 )
    cmds.parentConstraint( 'master_Grp', 'root_jnt', mo = True )

    X = 0.2
    sock_geo = 'cbw100_cg_leg_mdl_v002:Leg_sock'
    leg_geo = 'cbw100_cg_leg_mdl_v002:Leg_geo'
    cmds.deltaMush( sock_geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # cmds.deltaMush( leg_geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # wrap
    # dfrmr = cw.createWrap( sock_geo, leg_geo )
    # cw.wrapDeformer( master = sock_geo, slave = leg_geo )
    # return
    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    #
    # clean to:
    '''
    Ctrl
    SknJnts
    Body
    Accessory
    Utility
    World
    olSkool
    '''
    place.cleanUp( 'root_jnt', SknJnts = True )
    place.cleanUp( 'cbw100_cg_leg_mdl_v002:geo_grp', Body = True )

    # hip
    hip_Ct = place.Controller2( 'hip', 'hip_jnt', False, 'diamond_ctrl', X * 150, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.parentConstraint( hip_Ct[4], 'hip_jnt', mo = True )
    cmds.parentConstraint( 'root_jnt', hip_Ct[0], mo = True )
    cmds.parent( hip_Ct[0], CONTROLS() )

    # ankle
    ankl_Ct = place.Controller2( 'ankle', 'ankle_jnt', False, 'facetYup_ctrl', X * 100, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.orientConstraint( ankl_Ct[4], 'ankle_jnt', mo = True )
    cmds.parent( ankl_Ct[0], CONTROLS() )
    #
    place.smartAttrBlend( master = 'ankle_jnt', slave = 'ankleTwist_jnt', masterAttr = 'rotateY', slaveAttr = 'rotateZ', blendAttrObj = ankl_Ct[2], blendAttrString = 'ankleTwist', blendWeight = 1.0, reverse = True, blendAttrExisting = False )

    # ball
    ball_Ct = place.Controller2( 'ball', 'index_02_jnt', False, 'ballRoll_ctrl', X * 150, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    #
    cmds.parentConstraint( ball_Ct[4], ankl_Ct[0], mo = True )
    cmds.parent( ball_Ct[0], CONTROLS() )

    # foot
    foot_Ct = place.Controller2( 'foot', 'ankle_jnt', False, 'boxZup_ctrl', X * 150, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.select( foot_Ct[0] )
    zero.zero()
    cmds.setAttr( foot_Ct[0] + '.tz', 8 )
    cmds.parentConstraint( foot_Ct[4], ball_Ct[0], mo = True )
    cmds.parentConstraint( 'root_jnt', foot_Ct[0], mo = True )
    cmds.parent( foot_Ct[0], CONTROLS() )

    #
    '''
    digits, fk
    ankle twist
    joint orient fixes
    paint weight fixes
    maybe retainer shapes, if no scale is required
    '''

    # main pv
    sjnt = 'hip_jnt'
    ejnt = 'ankle_jnt'
    # problem, pv build on wrong side, compensated with negative offset, cuz joints arent mirrored from left side
    pv_Ct = appendage.create_3_joint_pv2( stJnt = sjnt, endJnt = ejnt, prefix = sjnt.split( '_jnt' )[0], suffix = 'R', distance_offset = X * -250.0, orient = True, color = 'red', X = 30, midJnt = '' )
    cmds.parent( pv_Ct[0], CONTROLS() )
    cmds.parentConstraint( 'master_Grp', pv_Ct[0], mo = True )
    # main ik
    name = ejnt.split( '_' )[0] + '_ik_R'
    cmds.ikHandle( n = name, sj = sjnt, ee = ejnt, sol = 'ikRPsolver', p = 2, w = .5, srp = True )
    cmds.poleVectorConstraint( pv_Ct[4], name )
    cmds.setAttr( name + '.visibility', 0 )
    cmds.parent( name, ankl_Ct[4] )

    # digits
    thumb_jnts = [
    'thumb_00_jnt',
    'thumb_01_jnt',
    'thumb_02_jnt',
    'thumb_03_jnt',
    'thumb_04_jnt'
    ]
    index_jnts = [
    'index_00_jnt',
    'index_01_jnt',
    'index_02_jnt',
    'index_03_jnt',
    'index_04_jnt'
    ]
    middle_jnts = [
    'middle_00_jnt',
    'middle_01_jnt',
    'middle_02_jnt',
    'middle_03_jnt',
    'middle_04_jnt'
    ]
    ring_jnts = [
    'ring_00_jnt',
    'ring_01_jnt',
    'ring_02_jnt',
    'ring_03_jnt',
    'ring_04_jnt'
    ]
    pinky_jnts = [
    'pinky_00_jnt',
    'pinky_01_jnt',
    'pinky_02_jnt',
    'pinky_03_jnt',
    'pinky_04_jnt'
    ]
    #
    finger_jnt_lsts = [thumb_jnts, index_jnts, middle_jnts, ring_jnts, pinky_jnts]
    #

    # toes
    '''
    name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    '''
    for finger_jnts in finger_jnt_lsts:
        name = finger_jnts[0].split( '_' )[0]
        tailRig = sfk.SplineFK( name, finger_jnts[0], finger_jnts[-1], None,
                                  controllerSize = 6, rootParent = ankl_Ct[4], parent1 = 'foot_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK', colorScheme = 'red' )
        print( tailRig.ctrlList[2][2] )
        cmds.setAttr( tailRig.ctrlList[2][2] + '.FK_ParentOffOn', 0 )
        cmds.setAttr( tailRig.ctrlList[3][2] + '.FK_ParentOffOn', 0 )
    '''
    for finger_jnts in finger_jnt_lsts:
        #
        i = 0
        for jnt in finger_jnts:
            shape = 'facetZup_ctrl'
            size = X * 30
            if i == 0:
                shape = 'facetXup_ctrl'
                size = X * 40
            name = jnt.split( '_jnt' )[0]
            fngr_Ct = place.Controller2( name, jnt, True, shape, size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
            cmds.orientConstraint( fngr_Ct[4], jnt, mo = True )
            if i == 0:
                cmds.parentConstraint( 'ankle_jnt', fngr_Ct[0], mo = True )
            else:
                cmds.parentConstraint( finger_jnts[i - 1], fngr_Ct[0], mo = True )
            cmds.parent( fngr_Ct[0], CONTROLS() )
            i = i + 1
    '''

    # scale
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

