import os

import maya.cmds as cmds
import webrImport as web

#
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
zero = web.mod( 'zero' )
krl = web.mod( "key_rig_lib" )


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
    # sck_geo = sock_geo()[0]
    # lg_geo = leg_geo()[0]
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


def build( X = 1 ):
    '''
    
    '''
    prebuild = Prebuild( X = X )
    # core
    cg = cog( X = X, parent = prebuild.masterCt[4] )
    plvs = pelvis( X = X )
    chst = chest( X = X )
    # limbs
    shldrL = shoulder( obj = 'shoulder_root_jnt_L', X = X )
    shldrR = shoulder( obj = 'shoulder_root_jnt_R', X = X )
    # neck
    nck = neck( X = X )
    hd = head( X = X, parent = nck[4] )
    # splines
    spline( name = 'neck_spline', start_jnt = 'neck_jnt_01', end_jnt = 'neck_jnt_05', splinePrnt = nck[4], splineStrt = nck[4], splineEnd = hd[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 2 )
    spline( name = 'spine_spline', start_jnt = 'pelvis_jnt', end_jnt = 'spine_jnt_06', splinePrnt = cg[4], splineStrt = plvs[4], splineEnd = chst[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 3 )


class Prebuild():

    def __init__( self, X = 150 ):
        '''
        Top  = (0 creates ___CHARACTER___ group) (1 creates ___PROP___ group) (2 creates ___VEHICLE___ group)  (3 creates ___ACCSS___ group) (4 creates ___UTIL___ group)\n
        '''
        preBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 150 * X )
        self.CHARACTER = preBuild[0]
        self.CONTROLS = preBuild[1]
        self.SKIN_JOINTS = preBuild[2]
        self.GEO = preBuild[3]
        self.WORLD_SPACE = preBuild[4]
        self.masterCt = preBuild[5]


def head( obj = 'neck_jnt_06', parent = 'neck_jnt_05', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'head', obj = obj, groups = True, orient = False, orientCt = False, shape = 'boxTallZup_ctrl', size = 40 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


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
    attr_Ct = place.Controller2( name, start_jnt, True, 'squareZup_ctrl', X * 12, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
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
    cmds.setAttr( splineAttr + '.' + splineName + 'Stretch', 0 )
    cmds.setAttr( splineAttr + '.ClstrVis', 1 )
    cmds.setAttr( splineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrVis', 0 )
    cmds.setAttr( splineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_E_IK_curve_scale.input2Z' )


def neck( obj = 'neck_jnt_01', parent = 'spine_jnt_06', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'neck', obj = obj, groups = True, orient = True, orientCt = False, shape = 'boxTallZup_ctrl', size = 40 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def clavicle():
    '''
    
    '''
    pass


def scapula():
    '''
    
    '''
    pass


def shoulder( obj = 'shoulder_root_jnt_L', parent = 'spine_jnt_06', X = 1.0 ):
    '''
    
    '''
    #
    name = ''
    shape = ''
    color = ''
    if obj[-1] == 'L':
        name = 'shoulder_L'
        shape = 'shldrL_ctrl'
        color = 'blue'
    else:
        name = 'shoulder_R'
        shape = 'shldrR_ctrl'
        color = 'red'
    #
    Ct = place.Controller2( name = name, obj = obj, groups = True, orient = True, orientCt = False, shape = shape, size = 30 * X, colorName = color ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def cog( obj = 'root_jnt', parent = 'root_jnt', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'cog', obj = obj, groups = True, orient = False, orientCt = False, shape = 'cog_ctrl', size = 3 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def pelvis( obj = 'pelvis_jnt', parent = 'root_jnt', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'pelvis', obj = obj, groups = True, orient = False, orientCt = False, shape = 'biped_hip', size = 3 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def chest( obj = 'spine_jnt_06', parent = 'root_jnt', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'chest', obj = obj, groups = True, orient = False, orientCt = False, shape = 'biped_hip', size = 3 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


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
