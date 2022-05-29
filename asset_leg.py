import os
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
krl = web.mod( "key_rig_lib" )


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
    weights_meshImport()
    sck_geo = sock_geo()[0]
    lg_geo = leg_geo()[0]
    cmds.deltaMush( sck_geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # cmds.deltaMush( leg_geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # wrap
    # dfrmr = cw.createWrap( sock_geo, leg_geo )
    # cw.wrapDeformer( master = sck_geo, slave = lg_geo )
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
    place.cleanUp( leg_geo()[0].split( ':' )[0] + 'geo_grp', Body = True )

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
    place.smartAttrBlend( master = 'ankle_jnt', slave = 'ankleTwist_jnt', masterAttr = 'rotateY', slaveAttr = 'rotateZ', blendAttrObj = ankl_Ct[2], blendAttrString = 'ankleTwist', blendWeight = 1.0, reverse = False, blendAttrExisting = False )

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
    pv_Ct = appendage.create_3_joint_pv2( stJnt = sjnt, endJnt = ejnt, prefix = sjnt.split( '_jnt' )[0], suffix = 'R', distance_offset = X * 250.0, orient = True, color = 'red', X = 30, midJnt = '' )
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


def leg_geo():
    leg_geo = ['cbw100_cg_leg_mdl_v003:Leg_geo']
    return leg_geo


def sock_geo():
    sock_geo = ['cbw100_cg_leg_mdl_v003:Leg_sock']
    return sock_geo


def leg_nurbs():
    '''
    not used in this rig
    '''
    return ''


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


def weights_meshExport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    print( path )
    # geo
    all_geo = sock_geo()
    print( all_geo )
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        print( ex_path )
        krl.exportMeshWeights( ex_path, geo, updatebar = True )


def weights_nurbsExport():
    '''
    exportNurbsCurveWeights( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = leg_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        krl.exportNurbsSurfaceWeights( ex_path, geo )


def weights_meshImport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = sock_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importMeshWeights( im_path, geo, updatebar = True )


def weights_nurbsImport():
    '''
    importNurbSurfaceWeights2( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = leg_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importNurbSurfaceWeights2( im_path, geo )
