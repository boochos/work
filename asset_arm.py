import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )


def CONTROLS():
    return '___CONTROLS'


def arm( *args ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 300 )
    cmds.parentConstraint( 'master_Grp', 'root_jnt', mo = True )

    X = 0.25
    geo = 'cbw100_cg_arm_mdl_pub:Arm_geo'
    cmds.deltaMush( geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
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
    place.cleanUp( geo, Body = True )

    #
    shldr_Ct = place.Controller2( 'shoulder', 'shoulder_jnt', False, 'diamond_ctrl', X * 150, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.parentConstraint( shldr_Ct[4], 'shoulder_jnt', mo = True )
    cmds.parentConstraint( 'root_jnt', shldr_Ct[0], mo = True )
    cmds.parent( shldr_Ct[0], CONTROLS() )
    # return
    #
    wrst_Ct = place.Controller2( 'wrist', 'wrist_jnt', False, 'facetYup_ctrl', X * 150, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    # cmds.setAttr( wrst_Ct[0] + '.rx', -90 )
    # cmds.setAttr( wrst_Ct[0] + '.ry', -180 )
    # cmds.setAttr( wrst_Ct[0] + '.rz', 0 )
    cmds.orientConstraint( wrst_Ct[4], 'wrist_jnt', mo = True )
    cmds.parentConstraint( 'root_jnt', wrst_Ct[0], mo = True )
    cmds.parent( wrst_Ct[0], CONTROLS() )
    #
    place.smartAttrBlend( master = 'wrist_jnt', slave = 'forearm_jnt', masterAttr = 'rotateY', slaveAttr = 'rotateZ', blendAttrObj = wrst_Ct[2], blendAttrString = 'wristTwist', blendWeight = 1.0, reverse = False, blendAttrExisting = False )

    #
    '''
    digits, fk
    wrist twist
    joint orient fixes
    paint weight fixes
    maybe retainer shapes, if no scale is required
    '''

    # main pv
    sjnt = 'shoulder_jnt'
    ejnt = 'wrist_jnt'
    # problem, pv build on wrong side, compensated with negative offset, cuz joints arent mirrored from left side
    pv_Ct = appendage.create_3_joint_pv2( stJnt = sjnt, endJnt = ejnt, prefix = sjnt.split( '_jnt' )[0], suffix = 'R', distance_offset = X * -150.0, orient = True, color = 'red', X = 50, midJnt = '' )
    cmds.parent( pv_Ct[0], CONTROLS() )
    cmds.parentConstraint( 'master_Grp', pv_Ct[0], mo = True )
    # main ik
    name = ejnt.split( '_' )[0] + '_ik_R'
    cmds.ikHandle( n = name, sj = sjnt, ee = ejnt, sol = 'ikRPsolver', p = 2, w = .5, srp = True )
    cmds.poleVectorConstraint( pv_Ct[4], name )
    cmds.setAttr( name + '.visibility', 0 )
    cmds.parent( name, wrst_Ct[4] )

    # digits
    thumb_jnts = [
    'thumb_01_jnt',
    'thumb_02_jnt',
    'thumb_03_jnt'
    ]
    index_jnts = [
    'index_01_jnt',
    'index_02_jnt',
    'index_03_jnt',
    'index_04_jnt'
    ]
    middle_jnts = [
    'middle_01_jnt',
    'middle_02_jnt',
    'middle_03_jnt',
    'middle_04_jnt'
    ]
    ring_jnts = [
    'ring_01_jnt',
    'ring_02_jnt',
    'ring_03_jnt',
    'ring_04_jnt'
    ]
    pinky_jnts = [
    'pinky_01_jnt',
    'pinky_02_jnt',
    'pinky_03_jnt',
    'pinky_04_jnt'
    ]
    #
    finger_jnt_lsts = [thumb_jnts, index_jnts, middle_jnts, ring_jnts, pinky_jnts]
    #
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
                cmds.parentConstraint( 'wrist_jnt', fngr_Ct[0], mo = True )
            else:
                cmds.parentConstraint( finger_jnts[i - 1], fngr_Ct[0], mo = True )
            cmds.parent( fngr_Ct[0], CONTROLS() )
            i = i + 1

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

