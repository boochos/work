import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
# web
place = web.mod( 'atom_place_lib' )
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
zero = web.mod( 'zero' )
krl = web.mod( "key_rig_lib" )
cn = web.mod( 'constraint_lib' )
atom = web.mod( "atom_lib" )
wrp = web.mod( "createWrap" )


def CONTROLS():
    return '___CONTROLS'


def arm( master = '', chest = '', side = '', X = 1 ):
    '''
    
    '''
    fk_wrist = True  # needs better solution
    suffix = ''
    color = ''
    #
    if side == 'L':
        suffix = '_L'
        color = 'blue'
        color2 = 'lightBlue'
    else:
        suffix = '_R'
        color = 'red'
        color2 = 'pink'
    #
    wrst_jnt = 'wrist_jnt' + suffix
    shldr_jnt = 'shoulder_jnt' + suffix
    #
    shldr_Ct = place.Controller2( name = 'shoulder' + suffix, obj = shldr_jnt, groups = True, orient = False, orientCt = False, shape = 'squareXup_ctrl', size = X * 33, colorName = color ).result
    place.rotationLock( shldr_Ct[2], lock = True )
    place.translationXLock( shldr_Ct[2], lock = True )
    cmds.parentConstraint( shldr_Ct[4], shldr_jnt, mo = True )
    cmds.parentConstraint( chest, shldr_Ct[0], mo = True )
    cmds.parent( shldr_Ct[0], CONTROLS() )

    # hand
    shape = 'boxTallZup_ctrl'
    orientCt = True
    if fk_wrist:
        shape = 'loc_ctrl'
        orientCt = False
    hnd_Ct = place.Controller2( name = 'hand' + suffix, obj = wrst_jnt, groups = True, orient = False, orientCt = orientCt, shape = shape, size = X * 30, colorName = color ).result
    cmds.parentConstraint( master, hnd_Ct[0], mo = True )
    cmds.parent( hnd_Ct[0], CONTROLS() )
    place.parentSwitch( 'SHLDR' + suffix, Ct = hnd_Ct[2], CtGp = hnd_Ct[1], TopGp = hnd_Ct[0], ObjOff = master, ObjOn = shldr_Ct[4],
                        Pos = True, Ornt = False, Prnt = False, OPT = True, attr = 'Shldr', w = 1.0 )
    if fk_wrist:
        place.rotationLock( hnd_Ct[2], lock = True )

    # fk wrist
    wrstfk_Ct = place.Controller2( name = 'wrist_fk' + suffix, obj = wrst_jnt, groups = True, orient = True, orientCt = True, shape = 'squareZup_ctrl', size = X * 20, colorName = color ).result
    cmds.pointConstraint( wrst_jnt, wrstfk_Ct[2], mo = True )
    place.translationLock( wrstfk_Ct[2], lock = True )
    cmds.orientConstraint( wrstfk_Ct[2], wrst_jnt, mo = True )
    cmds.orientConstraint( cmds.listRelatives( wrst_jnt, p = True )[0], wrstfk_Ct[1], mo = True )  # to forearm
    cmds.parent( wrstfk_Ct[0], CONTROLS() )

    if not fk_wrist:
        # wrist
        wrst_Ct = place.Controller2( name = 'wrist' + suffix, obj = wrst_jnt, groups = True, orient = True, orientCt = True, shape = 'facetZup_ctrl', size = X * 30, colorName = color ).result
        cmds.parentConstraint( wrst_Ct[4], wrstfk_Ct[0], mo = True )
        cmds.parent( wrst_Ct[0], CONTROLS() )

        # roll
        roll_Ct = place.Controller2( name = 'finger_roll' + suffix, obj = 'fingerC_02_jnt' + suffix, groups = True, orient = True, orientCt = True, shape = 'rectangleWideZup_ctrl', size = X * 12, colorName = color ).result
        cmds.parentConstraint( roll_Ct[4], wrst_Ct[0], mo = True )
        cmds.parentConstraint( hnd_Ct[4], roll_Ct[0], mo = True )
        cmds.parent( roll_Ct[0], CONTROLS() )

    # main pv
    pv_Ct = appendage.create_3_joint_pv2( stJnt = shldr_jnt, endJnt = wrst_jnt, prefix = shldr_jnt.split( '_jnt' )[0], suffix = side, distance_offset = X * -70.0, orient = True, color = color, X = 30, midJnt = '' )
    place.rotationLock( pv_Ct[2], lock = True )
    zero.zeroRotations( pv_Ct[0] )
    cmds.parent( pv_Ct[0], CONTROLS() )
    cmds.parentConstraint( master, pv_Ct[0], mo = True )

    # main ik
    name = wrst_jnt.split( '_' )[0] + '_ik' + suffix
    cmds.ikHandle( n = name, sj = shldr_jnt, ee = wrst_jnt, sol = 'ikRPsolver', p = 2, w = .5, srp = True )
    cmds.poleVectorConstraint( pv_Ct[4], name )
    cmds.setAttr( name + '.visibility', 0 )
    if fk_wrist:
        cmds.parent( name, hnd_Ct[4] )
    else:
        cmds.parent( name, wrst_Ct[4] )

    # digits
    finger_jnt_lsts = finger_joints( suffix = suffix )
    '''
    name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    '''
    direction = 0
    if side == 'R':
        direction = 1
    for jnts in finger_jnt_lsts:
        name = jnts[0].split( '_' )[0] + suffix
        if fk_wrist:
            # fk wrist parents
            digitRig = sfk.SplineFK( name, jnts[0], jnts[-1], None, direction = direction,
                                      controllerSize = X * 8, rootParent = wrstfk_Ct[4], parent1 = hnd_Ct[4], parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'ik', colorScheme = color )
        else:
            # roll parents
            digitRig = sfk.SplineFK( name, jnts[0], jnts[-1], None, direction = direction,
                                      controllerSize = X * 8, rootParent = wrst_Ct[4], parent1 = hnd_Ct[4], parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'ik', colorScheme = color )

            cmds.setAttr( digitRig.ctrlList[2][2] + '.FK_ParentOffOn', 0 )
            cmds.setAttr( digitRig.ctrlList[3][2] + '.FK_ParentOffOn', 0 )


def leg( master = '', pelvis = '', side = '', X = 1 ):
    '''
    
    '''
    suffix = ''
    color = ''
    if side == 'L':
        suffix = '_L'
        color = 'blue'
        color2 = 'lightBlue'
    else:
        suffix = '_R'
        color = 'red'
        color2 = 'pink'
    #
    hp_jnt = 'hip_jnt' + suffix
    ankl_jnt = 'ankle_jnt' + suffix
    # hip
    hip_Ct = place.Controller2( name = 'hip' + suffix, obj = hp_jnt, groups = True, orient = False, orientCt = False, shape = 'squareYup_ctrl', size = X * 30, colorName = color ).result
    place.rotationLock( hip_Ct[2], lock = True )
    # place.translationXLock( hip_Ct[2], lock = True )
    cmds.parentConstraint( hip_Ct[4], hp_jnt, mo = True )
    cmds.parentConstraint( pelvis, hip_Ct[0], mo = True )
    cmds.parent( hip_Ct[0], CONTROLS() )

    # foot
    foot_Ct = place.Controller2( name = 'foot' + suffix, obj = ankl_jnt, groups = True, orient = False, orientCt = False, shape = 'boxZup_ctrl', size = X * 30, colorName = color ).result
    cmds.setAttr( foot_Ct[0] + '.ty', 0 )
    cmds.parentConstraint( master, foot_Ct[0], mo = True )
    cmds.parent( foot_Ct[0], CONTROLS() )

    # ankle
    ankl_Ct = place.Controller2( name = 'ankle' + suffix, obj = ankl_jnt, groups = True, orient = False, orientCt = False, shape = 'facetYup_ctrl', size = X * 30, colorName = color ).result
    cmds.orientConstraint( ankl_Ct[4], ankl_jnt, mo = True )
    cmds.parent( ankl_Ct[0], CONTROLS() )

    # roll
    pvt = 'toeB_02_jnt'
    if not cmds.objExists( pvt ):
        pvt = 'toeA_02_jnt'
    roll_Ct = place.Controller2( name = 'toe_roll' + suffix, obj = pvt + suffix, groups = True, orient = True, orientCt = True, shape = 'rectangleWideZup_ctrl', size = X * 12, colorName = color ).result
    cmds.parentConstraint( roll_Ct[4], ankl_Ct[0], mo = True )
    cmds.parentConstraint( foot_Ct[4], roll_Ct[0], mo = True )
    cmds.parent( roll_Ct[0], CONTROLS() )

    # main pv
    pv_Ct = appendage.create_3_joint_pv2( stJnt = hp_jnt, endJnt = ankl_jnt, prefix = hp_jnt.split( '_jnt' )[0], suffix = side, distance_offset = X * 80.0, orient = True, color = color, X = 30, midJnt = '' )
    place.rotationLock( pv_Ct[2], lock = True )
    zero.zeroRotations( pv_Ct[0] )
    cmds.parent( pv_Ct[0], CONTROLS() )
    cmds.parentConstraint( foot_Ct[4], pv_Ct[0], mo = True )

    # main ik
    name = ankl_jnt.split( '_' )[0] + '_ik' + suffix
    cmds.ikHandle( n = name, sj = hp_jnt, ee = ankl_jnt, sol = 'ikRPsolver', p = 2, w = .5, srp = True )
    cmds.poleVectorConstraint( pv_Ct[4], name )
    cmds.setAttr( name + '.visibility', 0 )
    cmds.parent( name, ankl_Ct[4] )

    # digits
    toe_jnt_lsts = toe_joints( suffix = suffix )
    '''
    name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    '''
    direction = 0
    if side == 'R':
        direction = 1
    for jnts in toe_jnt_lsts:
        if cmds.objExists( jnts[0] ):
            name = jnts[0].split( '_' )[0] + suffix
            digitRig = sfk.SplineFK( name, jnts[0], jnts[-1], None, direction = direction,
                                      controllerSize = X * 8, rootParent = ankl_Ct[4], parent1 = foot_Ct[4], parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'ik', colorScheme = color )
            # print( tailRig.ctrlList[2][2] )
            cmds.setAttr( digitRig.ctrlList[2][2] + '.FK_ParentOffOn', 0 )
            cmds.setAttr( digitRig.ctrlList[3][2] + '.FK_ParentOffOn', 0 )


def build( X = 0.7, lite = 1 ):
    '''
    elbow_dbl_jnt_L
    '''
    #
    atom.win()
    #
    '''
    weights_meshImport()
    fix_normals( lite = lite )'''

    # wrp.createWrap2( low_geo()[0], mid_geo()[0] )
    # wrp.wrapDeformer( master = low_geo()[0], slave = high_geo()[0] )
    # return
    '''
    skin1 = 'skinCluster1'
    inf = cmds.skinCluster( skin1, q = True, inf = True )
    skinCluster = skin( joints = inf, geo = mid_geo() )
    cmds.copySkinWeights( ss = skin1, ds = skinCluster, mirrorMode = 'YZ', mirrorInverse = False )
    skinCluster = skin( joints = inf, geo = high_geo() )
    cmds.copySkinWeights( ss = skin1, ds = skinCluster, mirrorMode = 'YZ', mirrorInverse = True )
    '''
    #
    prebuild = Prebuild( X = X )
    # core
    cg = cog( X = X, parent = prebuild.masterCt[4] )
    plvs = pelvis( X = X, parent = cg[4] )
    chst = chest( X = X, parent = cg[4] )
    # arms
    armL = arm( master = prebuild.masterCt[4], chest = 'spine_jnt_06', side = 'L', X = X )
    clavicle( obj = 'clavicle_jnt_01_L', shoulder = 'shoulder_jnt_L', parent = 'spine_jnt_06' )
    armR = arm( master = prebuild.masterCt[4], chest = 'spine_jnt_06', side = 'R', X = X )
    clavicle( obj = 'clavicle_jnt_01_R', shoulder = 'shoulder_jnt_R', parent = 'spine_jnt_06' )
    # legs
    lgsL = leg( master = prebuild.masterCt[4], pelvis = plvs, side = 'L', X = X )
    lgsR = leg( master = prebuild.masterCt[4], pelvis = plvs, side = 'R', X = X )
    # neck
    nck = neck( X = X )
    hd = head( X = X, parent = nck[4] )
    place.parentSwitch( hd[2], hd[2], hd[1], hd[0], prebuild.masterCt[4], nck[4], False, True, False, True, 'Neck', 0.0 )
    # splines
    spline( name = 'neck_spline', start_jnt = 'neck_jnt_01', end_jnt = 'neck_jnt_05', splinePrnt = nck[4], splineStrt = nck[4], splineEnd = hd[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 2 )
    spline( name = 'spine_spline', start_jnt = 'pelvis_jnt', end_jnt = 'spine_jnt_06', splinePrnt = cg[4], splineStrt = plvs[4], splineEnd = chst[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 3 )
    # shorts
    shorts( master = prebuild.masterCt[4], pelvis = plvs, side = 'L', X = X )
    shorts( master = prebuild.masterCt[4], pelvis = plvs, side = 'R', X = X )
    # scale
    scale_rig()


class Prebuild():

    def __init__( self, X = 150 ):
        '''
        Top  = (0 creates ___CHARACTER___ group) (1 creates ___PROP___ group) (2 creates ___VEHICLE___ group)  (3 creates ___ACCSS___ group) (4 creates ___UTIL___ group)\n
        '''
        preBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 170 * X )
        self.CHARACTER = preBuild[0]
        self.CONTROLS = preBuild[1]
        self.SKIN_JOINTS = preBuild[2]
        self.GEO = preBuild[3]
        self.WORLD_SPACE = preBuild[4]
        self.masterCt = preBuild[5]
        #
        cmds.parentConstraint( self.masterCt[4], 'root_jnt', mo = 1 )
        cmds.parent( 'root_jnt', self.SKIN_JOINTS )
        #
        geos = low_geo()
        for geo in geos:
            cmds.deltaMush( geo, smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
        # cmds.deltaMush( mid_geo()[0], smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
        # cmds.deltaMush( high_geo()[0], smoothingIterations = 10, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
        #
        '''
        # not using cuz mesh had only one LOD and doesnt support multi geos per LOD
        misc.optEnum( self.masterCt[2], attr = 'LOD', enum = 'OPTNS' )
        place.hijackVis( low_geo()[0], self.masterCt[2], name = 'lowGeo', suffix = False, default = 1, mode = 'visibility' )
        place.hijackVis( mid_geo()[0], self.masterCt[2], name = 'medGeo', suffix = False, default = 0, mode = 'visibility' )
        place.hijackVis( high_geo()[0], self.masterCt[2], name = 'highGeo', suffix = False, default = 0, mode = 'visibility' )
        '''


def head( obj = 'neck_jnt_06', parent = 'neck_jnt_05', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'head', obj = obj, groups = True, orient = False, orientCt = False, shape = 'biped_head', size = 35 * X, colorName = 'yellow' ).result
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
    OptAttr( splineAttr, 'Spline' )
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
    cmds.setAttr( splineAttr + '.Vis', 0 )
    cmds.setAttr( splineAttr + '.Root', 0 )
    cmds.setAttr( splineAttr + '.Stretch', 0 )
    cmds.setAttr( splineAttr + '.ClstrVis', 0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkBlend', 0.5 )
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
    Ct = place.Controller2( name = 'neck', obj = obj, groups = True, orient = True, orientCt = False, shape = 'squareOriginZupInv_ctrl', size = 40 * X, colorName = 'yellow' ).result
    place.translationLock( Ct[2], lock = True )
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def clavicle( obj = 'clavicle_jnt_01_L', shoulder = 'arm_shoulder_jnt_L', parent = 'spine_jnt_06' ):
    '''
    
    '''
    #
    suffix = ''
    if obj[-1] == 'L':
        suffix = '_L'
    else:
        suffix = '_R'
    #
    appendage.createClavicleRig( obj, shoulder, parent, suffix, [0, 0, 1], [0, 1, 0] )


def scapula():
    '''
    
    '''
    appendage.createVerticalScapRig( 'arm_shoulder_jnt_R', 'arm_shoulder_dbl_jnt_R', 'shldr_R_Grp', 'arm_scapula_jnt_01_R', 'shldr_R', 'spine_jnt_06', '_R', flip = True )
    # appendage.createClavicleRig( 'arm_clavicle_jnt_01_R', 'arm_shoulder_jnt_R', 'spine_jnt_07', '_R', [0, 0, 1], [0, 1, 0] )


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
    Ct = place.Controller2( name = name, obj = obj, groups = True, orient = False, orientCt = False, shape = shape, size = 30 * X, colorName = color ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def cog( obj = 'root_jnt', parent = 'root_jnt', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'cog', obj = obj, groups = True, orient = False, orientCt = False, shape = 'facetYup_ctrl', size = 110 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def pelvis( obj = 'pelvis_jnt', parent = '', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'pelvis', obj = obj, groups = True, orient = False, orientCt = False, shape = 'biped_pelvis', size = 65 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


def chest( obj = 'spine_jnt_06', parent = '', X = 1.0 ):
    '''
    
    '''
    Ct = place.Controller2( name = 'chest', obj = obj, groups = True, orient = False, orientCt = False, shape = 'biped_chest', size = 65 * X, colorName = 'yellow' ).result
    cmds.parentConstraint( parent, Ct[0], mo = True )
    cmds.parent( Ct[0], CONTROLS() )
    return Ct


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
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
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


def low_geo():
    return ['male_model:T_Shirt_Geo001',
    'male_model:Shorts_Geo001',
    'male_model:Shuze01',
    'male_model:Body_Geo001',
    'male_model:Shuze02']


def mid_geo():
    return ['statue_man_model:Statue_man_Middle']


def high_geo():
    return ['statue_man_model:Statue_man_High']


def skin( joints = [], geo = '' ):
    '''
    skin object
    '''
    cmds.select( joints )
    cmds.select( geo, add = True )
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    return sknClstr


def finger_joints( suffix = '' ):
    '''
    
    '''
    # digits
    fingerA_jnts = [
    'fingerA_00_jnt' + suffix,
    'fingerA_01_jnt' + suffix,
    'fingerA_02_jnt' + suffix,
    'fingerA_03_jnt' + suffix,
    'fingerA_04_jnt' + suffix
    ]
    fingerB_jnts = [
    'fingerB_00_jnt' + suffix,
    'fingerB_01_jnt' + suffix,
    'fingerB_02_jnt' + suffix,
    'fingerB_03_jnt' + suffix,
    'fingerB_04_jnt' + suffix,
    'fingerB_05_jnt' + suffix
    ]
    fingerC_jnts = [
    'fingerC_00_jnt' + suffix,
    'fingerC_01_jnt' + suffix,
    'fingerC_02_jnt' + suffix,
    'fingerC_03_jnt' + suffix,
    'fingerC_04_jnt' + suffix,
    'fingerC_05_jnt' + suffix
    ]
    fingerD_jnts = [
    'fingerD_00_jnt' + suffix,
    'fingerD_01_jnt' + suffix,
    'fingerD_02_jnt' + suffix,
    'fingerD_03_jnt' + suffix,
    'fingerD_04_jnt' + suffix,
    'fingerD_05_jnt' + suffix
    ]
    fingerE_jnts = [
    'fingerE_00_jnt' + suffix,
    'fingerE_01_jnt' + suffix,
    'fingerE_02_jnt' + suffix,
    'fingerE_03_jnt' + suffix,
    'fingerE_04_jnt' + suffix,
    'fingerE_05_jnt' + suffix
    ]
    #
    finger_jnt_lsts = [fingerA_jnts, fingerB_jnts, fingerC_jnts, fingerD_jnts, fingerE_jnts]
    return finger_jnt_lsts


def toe_joints( suffix = '' ):
    '''
    
    '''
    # digits
    toeA_jnts = [
    'toeA_00_jnt' + suffix,
    'toeA_01_jnt' + suffix,
    'toeA_02_jnt' + suffix,
    'toeA_03_jnt' + suffix,
    'toeA_04_jnt' + suffix
    ]
    toeB_jnts = [
    'toeB_00_jnt' + suffix,
    'toeB_01_jnt' + suffix,
    'toeB_02_jnt' + suffix,
    'toeB_03_jnt' + suffix,
    'toeB_04_jnt' + suffix
    ]
    toeC_jnts = [
    'toeC_00_jnt' + suffix,
    'toeC_01_jnt' + suffix,
    'toeC_02_jnt' + suffix,
    'toeC_03_jnt' + suffix,
    'toeC_04_jnt' + suffix
    ]
    toeD_jnts = [
    'toeD_00_jnt' + suffix,
    'toeD_01_jnt' + suffix,
    'toeD_02_jnt' + suffix,
    'toeD_03_jnt' + suffix,
    'toeD_04_jnt' + suffix
    ]
    toeE_jnts = [
    'toeE_00_jnt' + suffix,
    'toeE_01_jnt' + suffix,
    'toeE_02_jnt' + suffix,
    'toeE_03_jnt' + suffix,
    'toeE_04_jnt' + suffix
    ]
    #
    toe_jnt_lsts = [toeA_jnts, toeB_jnts, toeC_jnts, toeD_jnts, toeE_jnts]
    return toe_jnt_lsts


def fix_normals( del_history = False, lite = True ):
    '''
    after skinning geo gets weird normals
    '''
    if lite:
        geo = [low_geo()[0]]
    else:
        geo = [low_geo()[0], mid_geo()[0], high_geo()[0]]
    cmds.select( geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( geo, ch = True )


def shorts( master = '', pelvis = '', side = 'L', X = 1 ):
    '''
    
    '''
    suffix = ''
    color = ''
    if side == 'L':
        suffix = '_L'
        color = 'blue'
        color2 = 'lightBlue'
    else:
        suffix = '_R'
        color = 'red'
        color2 = 'pink'
    #
    hp_jnt = 'hip_jnt' + suffix
    shrts_jnt = 'shorts_jnt' + suffix
    # hip
    shrts_Ct = place.Controller2( name = 'shorts' + suffix, obj = hp_jnt, groups = True, orient = True, orientCt = True, shape = 'squareXup_ctrl', size = X * 80, colorName = color ).result
    #
    cmds.parentConstraint( shrts_Ct[4], shrts_jnt, mo = True )
    cmds.parentConstraint( hp_jnt, shrts_Ct[0], mo = True )
    cmds.parent( shrts_Ct[0], CONTROLS() )


def scale_rig():
    '''
    
    '''
    # scale
    # geo = 'caterpillar_c_geo_lod_0'
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
    geos = low_geo()
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
        i = 1
        for geo in geos:
            cmds.connectAttr( mstr + '.' + uni, 'deltaMush' + str( i ) + s )  # set scale, apply deltaMush, add scale connection for deltaMush
            i = i + 1

'''
# rig build
import webrImport as web
ft = web.mod('asset_fate2')
ft.build()

# skin export
import webrImport as web
ft = web.mod('asset_fate2')
ft.weights_meshExport()


# skin import
import webrImport as web
ft = web.mod('asset_fate2')
ft.weights_meshImport()
'''
