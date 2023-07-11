from _ast import Pass
import os

import maya.cmds as cmds
import maya.mel as mm
import webrImport as web

#
faceRig = web.mod( 'atom_faceRig_lib' )
place = web.mod( 'atom_place_lib' )
apg = web.mod( 'atom_appendage_lib' )
vhc = web.mod( 'vehicle_lib' )
ump = web.mod( 'universalMotionPath' )
misc = web.mod( 'atom_miscellaneous_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
stage = web.mod( 'atom_splineStage_lib' )
krl = web.mod( "key_rig_lib" )
# jnt = web.mod( 'atom_joint_lib' )
ac = web.mod( 'animCurve_lib' )
# cn = web.mod( 'constraint_lib' )
cpl = web.mod( "clipPickle_lib" )
arl = web.mod( 'atom_retainer_lib' )


def ____PREBUILD():
    pass


def prebuild( lod100 = True, lod300 = False, deltaMush = False ):
    '''
    
    '''
    atom_ui()
    #
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 35 )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # retainers
    neck_retainer()
    throat_retainer()
    cheek_retainer_l()
    jaw_retainer_l()
    cheek_retainer_r()
    jaw_retainer_r()
    # return

    # weights
    weights_meshImport( lod100 = lod100, lod300 = lod300 )
    # geo
    # print( GEO )
    cmds.parent( 'cor:coralSnake_grp', GEO[0] )
    #
    cmds.parentConstraint( 'master_Grp', 'root_jnt', mo = True )
    place.cleanUp( 'root_jnt', SknJnts = True )
    if deltaMush:
        if lod100:
            node = cmds.deltaMush( low_geo(), smoothingIterations = 8, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )[0]
            cmds.setAttr( node + '.inwardConstraint' , 0.4 )
            cmds.setAttr( node + '.outwardConstraint' , 0.2 )
            cmds.setAttr( node + '.distanceWeight' , 0.3 )
        if lod300:
            node = cmds.deltaMush( high_geo(), smoothingIterations = 8, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )[0]
            cmds.setAttr( node + '.inwardConstraint' , 0.4 )
            cmds.setAttr( node + '.outwardConstraint' , 0.2 )
            cmds.setAttr( node + '.distanceWeight' , 0.3 )

    misc.optEnum( MasterCt[2], attr = 'LOD', enum = 'OPTNS' )
    place.hijackVis( 'cor:body_low_grp', MasterCt[2], name = 'lowGeo', suffix = False, default = 1, mode = 'visibility' )
    place.hijackVis( 'cor:body_high_grp_anim', MasterCt[2], name = 'highGeo', suffix = False, default = 0, mode = 'visibility' )

    #
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
        if deltaMush:
            cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush
            if lod100 and lod300:
                cmds.connectAttr( mstr + '.' + uni, 'deltaMush2' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def build( lod100 = True, lod300 = False, fk = False, dynamics = False, deltaMush = False ):
    '''
    assumes joints are in scene and geo groups and object are referenced, 
    objects are hard coded
    '''
    prebuild( lod100 = lod100, lod300 = lod300, deltaMush = deltaMush )
    # return

    # neck spline part 1
    start_jnt = 'body_001_jnt'
    end_jnt = 'body_009_jnt'
    neck_ik_jnts = neck_joint_chain( start_jnt = start_jnt, end_jnt = end_jnt, reroot = True )
    # return
    con = cmds.parentConstraint( end_jnt, neck_ik_jnts[-1], mo = True )

    #
    head()
    # return
    micro_body_cts = body_spline( fk = fk, dynamics = dynamics )

    # neck spline part 2
    cmds.delete( con )
    neck( neck_jnt_chain = neck_ik_jnts, micro_body_cts = micro_body_cts )
    #
    connect_cache_geo()


def ____FACE():
    pass


def build_face():
    '''
    rig face
    '''
    atom_ui()
    # rig parts
    # throat_retainer()
    jaw()
    throat()
    cheek_retainer_l()
    jaw_retainer_l()
    cheek_retainer_r()
    jaw_retainer_r()
    # skin
    weights_face_meshImport()


def tongue():
    # tongue
    # TongueCt = place.Controller2( 'Tongue', 'jaw_jnt', False, 'splineStart_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    tongueMicro = faceRig.snakeTongue( 'tongue', 0.3 )


def throat():
    '''
    
    '''
    #
    baseCt = place.Controller2( 'throat', 'throat_base_jnt', True, 'facetXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'body_003_jnt', baseCt[0], mo = True )
    # add smart blend for auto throat rotation at base
    #
    #
    #
    cmds.parentConstraint( baseCt[4], 'throat_base_jnt', mo = True )
    place.cleanUp( baseCt[0], Ctrl = True )
    #
    tipCt = place.Controller2( 'throat_tip', 'throat_tip_jnt', True, 'facetXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'jaw_tip_jnt', tipCt[0], mo = True )
    cmds.parentConstraint( tipCt[4], 'throat_tip_jnt', mo = True )
    place.cleanUp( tipCt[0], Ctrl = True )

    # spline
    name = 'throatMicro'
    spline( name = name, start_jnt = 'throat_01_jnt', end_jnt = 'throat_05_jnt', splinePrnt = 'body_003_jnt', splineStrt = baseCt[4], splineEnd = tipCt[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 0.1, splineFalloff = 1 )
    #
    cmds.setAttr( name + '.Stretch', 1 )
    cmds.setAttr( name + '.ClstrMidIkBlend', 0.6 )
    cmds.setAttr( name + '.ClstrMidIkSE_W', 0.0 )
    cmds.setAttr( name + '.VctrMidIkBlend', 0.5 )
    #
    place.hijackAttrs( baseCt[0], name, 'visibility', 'baseVis', set = True, default = 0.0, force = True )
    place.hijackAttrs( tipCt[0], name, 'visibility', 'tipVis', set = True, default = 0.0, force = True )


def fangs():
    # fangs
    # fangL = place.Controller( 'fang_L', 'fang_jnt_L', orient = True, shape = 'squareXup_ctrl', size = 2, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    # fangLCt = fangL.createController()
    fangLCt = place.Controller2( 'fang_L', 'fang_jnt_L', True, 'squareXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( fangLCt[2] + '.showManipDefault', 2 )
    place.translationLock( fangLCt[2], True )
    place.rotationLock( fangLCt[2], True )
    place.rotationXLock( fangLCt[2], False )
    # fangR = place.Controller( 'fang_R', 'fang_jnt_R', orient = True, shape = 'squareXup_ctrl', size = 2, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    # fangRCt = fangR.createController()
    fangRCt = place.Controller2( 'fang_R', 'fang_jnt_R', True, 'squareXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.setAttr( fangRCt[2] + '.showManipDefault', 2 )
    place.translationLock( fangRCt[2], True )
    place.rotationLock( fangRCt[2], True )
    place.rotationXLock( fangRCt[2], False )
    #
    cmds.parentConstraint( fangLCt[4], 'fang_jnt_L', mo = True )
    cmds.parentConstraint( fangRCt[4], 'fang_jnt_R', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_L', fangLCt[0], mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_R', fangRCt[0], mo = True )
    place.cleanUp( fangLCt[0], Ctrl = True )
    place.cleanUp( fangRCt[0], Ctrl = True )
    # pose, tuck away
    cmds.setAttr( fangLCt[2] + '.rotateX', 50 )
    cmds.setAttr( fangRCt[2] + '.rotateX', 50 )


def jaw_ik():
    '''
    create left/right jawk ik for lipline attachment
    move lower jaw pivot to corner of mouth, anatomically the geo is wrong. need to adjust to fit geo
    add pivot offset group to cvs in retainer, for constraining to rig
    TODO: create upper jaw ik, sliding forward when jaw opens for folding fang snakes
    TODO: create tilting outer upper jaw control
    
    '''
    pass


def jaw():
    #
    JawCt = place.Controller2( 'jaw', 'jaw_jnt', True, 'digitBaseInv_ctrl', 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.setAttr( JawCt[2] + '.showManipDefault', 2 )
    place.translationLock( JawCt[2], True )
    cmds.parentConstraint( JawCt[4], 'jaw_jnt', mo = True )
    cmds.parentConstraint( 'head_jnt', JawCt[0], mo = True )
    place.cleanUp( JawCt[0], Ctrl = True )
    #
    JawTipCt = place.Controller2( 'jaw_tip', 'jaw_tip_jnt', True, 'rectangleWideZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.setAttr( JawTipCt[2] + '.showManipDefault', 2 )
    place.translationLock( JawTipCt[2], True )
    place.rotationLock( JawTipCt[2], True )
    place.rotationZLock( JawTipCt[2], False )
    cmds.parentConstraint( 'jaw_jnt', JawTipCt[0], mo = True )
    cmds.parentConstraint( JawTipCt[4], 'jaw_tip_jnt', mo = True )
    place.cleanUp( JawTipCt[0], Ctrl = True )
    place.hijackVis( JawTipCt[0], JawCt[2], name = 'jawTipVis', suffix = True, default = 0, mode = 'visibility' )
    #
    JawLCt = place.Controller2( 'jaw_tip_L', 'jaw_lower_tip_jnt_L', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( JawLCt[2] + '.showManipDefault', 1 )
    place.translationLock( JawLCt[2], True )
    place.rotationLock( JawLCt[2], True )
    place.translationYLock( JawLCt[2], False )
    cmds.parentConstraint( JawTipCt[4], JawLCt[0], mo = True )
    place.cleanUp( JawLCt[0], Ctrl = True )
    cmds.setAttr( JawLCt[0] + '.v', 0 )
    #
    JawRCt = place.Controller2( 'jaw_tip_R', 'jaw_lower_tip_jnt_R', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.setAttr( JawRCt[2] + '.showManipDefault', 1 )
    place.translationLock( JawRCt[2], True )
    place.rotationLock( JawRCt[2], True )
    place.translationYLock( JawRCt[2], False )
    cmds.parentConstraint( JawTipCt[4], JawRCt[0], mo = True )
    place.cleanUp( JawRCt[0], Ctrl = True )
    cmds.setAttr( JawRCt[0] + '.v', 0 )

    #
    apg.aimRig( name = 'jaw_L', obj = 'jaw_lower_jnt_L', aimObj = JawLCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, 1], up = [0, 1, 0] )
    apg.aimRig( name = 'jaw_R', obj = 'jaw_lower_jnt_R', aimObj = JawRCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, -1], up = [0, -1, 0] )

    #
    JawLowerLCt = place.Controller2( 'jaw_lower_L', 'jaw_lower_jnt_L', True, 'shldrL_ctrl', 1.0, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( JawLowerLCt[2] + '.showManipDefault', 1 )
    # place.translationLock( JawLowerLCt[2], True )
    place.rotationLock( JawLowerLCt[2], True )
    # place.translationYLock( JawLowerLCt[2], False )
    cmds.parentConstraint( 'head_jnt', JawLowerLCt[0], mo = True )
    place.cleanUp( JawLowerLCt[0], Ctrl = True )
    # cmds.setAttr( JawLowerLCt[0] + '.v', 0 )
    #
    JawLowerRCt = place.Controller2( 'jaw_lower_R', 'jaw_lower_jnt_R', True, 'shldrR_ctrl', 1.0, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.setAttr( JawLowerRCt[2] + '.showManipDefault', 1 )
    # place.translationLock( JawLowerRCt[2], True )
    place.rotationLock( JawLowerRCt[2], True )
    # place.translationYLock( JawLowerRCt[2], False )
    cmds.parentConstraint( 'head_jnt', JawLowerRCt[0], mo = True )
    place.cleanUp( JawLowerRCt[0], Ctrl = True )
    # cmds.setAttr( JawLowerRCt[0] + '.v', 0 )

    apg.aimRig( name = 'jaw_root_L', obj = 'jaw_jnt_L', aimObj = JawLowerLCt[4], upParent = 'head_jnt', distance = 1, aim = [0, 0, 1], up = [-1, 0, 0] )
    apg.aimRig( name = 'jaw_root_R', obj = 'jaw_jnt_R', aimObj = JawLowerRCt[4], upParent = 'head_jnt', distance = 1, aim = [0, 0, -1], up = [1, 0, 0] )

    #
    JawUpperLCt = place.Controller2( 'jaw_upper_L', 'jaw_upper_tip_jnt_L', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( JawUpperLCt[2] + '.showManipDefault', 1 )
    # place.translationLock( JawUpperLCt[2], True )
    place.rotationLock( JawUpperLCt[2], True )
    # place.translationYLock( JawUpperLCt[2], False )
    cmds.parentConstraint( 'head_jnt', JawUpperLCt[0], mo = True )
    place.cleanUp( JawUpperLCt[0], Ctrl = True )
    # cmds.setAttr( JawUpperLCt[0] + '.v', 0 )
    #
    JawUpperRCt = place.Controller2( 'jaw_upper_R', 'jaw_upper_tip_jnt_R', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.setAttr( JawUpperRCt[2] + '.showManipDefault', 1 )
    # place.translationLock( JawUpperRCt[2], True )
    place.rotationLock( JawUpperRCt[2], True )
    # place.translationYLock( JawUpperRCt[2], False )
    cmds.parentConstraint( 'head_jnt', JawUpperRCt[0], mo = True )
    place.cleanUp( JawUpperRCt[0], Ctrl = True )
    # cmds.setAttr( JawUpperRCt[0] + '.v', 0 )

    apg.aimRig( name = 'jaw_upper_L', obj = 'jaw_upper_jnt_L', aimObj = JawUpperLCt[4], upParent = 'head_jnt', distance = 1, aim = [0, 0, 1], up = [-1, 0, 0] )
    apg.aimRig( name = 'jaw_upper_R', obj = 'jaw_upper_jnt_R', aimObj = JawUpperRCt[4], upParent = 'head_jnt', distance = 1, aim = [0, 0, -1], up = [1, 0, 0] )


def ____RETAINERS():
    pass


def neck_retainer():
    '''
    repose geo, lost latest update
    2 rows at base of skull
    add row to neck side, 2 on either end to help transition off retainer
    row in middle gets majority of the weight to skin
    also lost weight settings for retainer
    current skin weights should indicate position of retainer
    '''
    ns = 'neck_rtnr'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_cylinder_4_original_v001.ma'
    cmds.file( pth, reference = True, namespace = ns, force = True )
    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\neck_retainer.0002.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\neck_retainer_cvs.0003.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'body_001_jnt', ns + ':master', mo = True )
    # rows
    cmds.parentConstraint( 'body_003_jnt', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'body_002_jnt', ns + ':row_1_twistPvt', mo = True )
    cmds.parentConstraint( 'body_001_jnt', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'head_jnt', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'head_jnt', ns + ':row_4_twistPvt', mo = True )
    # cvs
    cmds.parentConstraint( 'throat_03_jnt', ns + ':cv_4_3_cvPvt', mo = True )
    cmds.parentConstraint( 'throat_03_jnt', ns + ':cv_3_3_cvPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':cv_2_3_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_4_4_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_3_4_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_4_2_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_3_2_cvPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':cv_2_2_cvPvt', mo = True, w = 1 )
    cmds.parentConstraint( 'body_001_jnt', ns + ':cv_2_2_cvPvt', mo = True, w = 1 )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':cv_2_4_cvPvt', mo = True, w = 1 )
    cmds.parentConstraint( 'body_001_jnt', ns + ':cv_2_4_cvPvt', mo = True, w = 1 )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass


def throat_retainer():
    '''

    '''
    # retainer
    # arl.createPlane( patchesU = 2, patchesV = 4, degree = 3, axis = [ 0, 1, 0 ], X = 0.5, hideRows = True, length = 4, width = 1.0 )

    ns = 'throat_rtnr'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_plane_5_pivotAlt_v001.ma'  # need to change to non mirrored
    cmds.file( pth, reference = True, namespace = ns, force = True )

    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\throat_retainer.0005.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\throat_retainer_cvs.0002.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'throat_base_jnt', ns + ':master', mo = True )
    #
    cmds.parentConstraint( 'jaw_jnt', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_jnt', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_jnt', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'neck_rtnr:cv_4_3_Grp', ns + ':row_4_twistPvt', mo = True )
    cmds.parentConstraint( 'neck_rtnr:cv_2_3_Grp', ns + ':row_5_twistPvt', mo = True )
    cmds.parentConstraint( 'neck_rtnr:cv_1_3_Grp', ns + ':row_7_twistPvt', mo = True )
    # cmds.parentConstraint( 'throat_base_jnt', ns + ':row_8_twistPvt', mo = True )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass

    # import pose, settings


def cheek_retainer_l():
    '''
    
    '''
    ns = 'cheek_rtnr_l'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_plane_5_v001.ma'
    cmds.file( pth, reference = True, namespace = ns, force = True )
    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\cheek_retainer_l.0004.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\cheek_retainer_l_cv.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'head_jnt', ns + ':master', mo = True )
    # rows
    cmds.parentConstraint( 'head_jnt', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':row_4_twistPvt', mo = True )
    cmds.parentConstraint( 'body_002_jnt', ns + ':row_5_twistPvt', mo = True )
    cmds.parentConstraint( 'body_003_jnt', ns + ':row_7_twistPvt', mo = True )
    # cvs
    cmds.parentConstraint( 'throat_01_jnt', ns + ':cv_5_7_cvPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':cv_5_5_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_5_4_cvPvt', mo = True )
    #
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':cv_5_3_cvPvt', mo = True, w = 0.75 )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_5_3_cvPvt', mo = True, w = 0.25 )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass


def cheek_retainer_r():
    '''
    
    '''
    ns = 'cheek_rtnr_r'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_plane_5_v001.ma'
    cmds.file( pth, reference = True, namespace = ns, force = True )
    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\cheek_retainer_r.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\cheek_retainer_r_cv.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'head_jnt', ns + ':master', mo = True )
    # rows
    cmds.parentConstraint( 'head_jnt', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':row_4_twistPvt', mo = True )
    cmds.parentConstraint( 'body_002_jnt', ns + ':row_5_twistPvt', mo = True )
    cmds.parentConstraint( 'body_003_jnt', ns + ':row_7_twistPvt', mo = True )
    # cvs
    cmds.parentConstraint( 'throat_01_jnt', ns + ':cv_5_7_cvPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':cv_5_5_cvPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_5_4_cvPvt', mo = True )
    #
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':cv_5_3_cvPvt', mo = True, w = 0.75 )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_5_3_cvPvt', mo = True , w = 0.25 )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass


def jaw_retainer_l():
    '''
    
    '''
    ns = 'jaw_rtnr_l'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_plane_5_v001.ma'
    cmds.file( pth, reference = True, namespace = ns, force = True )
    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\jaw_retainer_l.0006.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\jaw_retainer_l_cv.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'head_jnt', ns + ':master', mo = True )
    # rows
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_03_jnt', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_03_jnt', ns + ':row_4_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':row_5_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_base_jnt', ns + ':row_7_twistPvt', mo = True )

    # cv in row 2
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':cv_0_2_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_0_2_cvPvt', mo = True, w = 0.75 )
    # cv in row 3
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':cv_0_3_cvPvt', mo = True, w = 0.75 )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_0_3_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':cv_2_3_cvPvt', mo = True, w = 0.1 )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_2_3_cvPvt', mo = True, w = 0.9 )
    # cv in row 4
    cmds.parentConstraint( 'jaw_upper_jnt_L', ns + ':cv_0_4_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_lower_jnt_L', ns + ':cv_0_4_cvPvt', mo = True, w = 0.75 )
    # cv in row 5
    # cmds.parentConstraint( 'jaw_jnt_L', ns + ':cv_0_5_cvPvt', mo = True )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass


def jaw_retainer_r():
    '''
    
    '''
    ns = 'jaw_rtnr_r'
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\retainer_plane_5_v001.ma'
    cmds.file( pth, reference = True, namespace = ns, force = True )
    # settings
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\jaw_retainer_r.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    path = 'C:\\Users\\s.weber\\Documents\\maya\\clipLibrary\\jaw_retainer_r_cv.0001.clip'
    cpl.clipApply( path = path, ns = False, onCurrentFrame = True, mergeExistingLayers = True, applyLayerSettings = True, applyRootAsOverride = False,
                  putLayerList = [], putObjectList = [], start = None, end = None, poseOnly = False, clp = '' )
    cmds.select( ns + ':cv_0_0' )
    arl.neutralizeDistances()
    #
    cmds.parentConstraint( 'head_jnt', ns + ':master', mo = True )
    # rows
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':row_0_twistPvt', mo = True )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':row_2_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_03_jnt', ns + ':row_3_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_03_jnt', ns + ':row_4_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_02_jnt', ns + ':row_5_twistPvt', mo = True )
    cmds.parentConstraint( 'throat_base_jnt', ns + ':row_7_twistPvt', mo = True )

    # cv in row 2
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':cv_5_2_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_5_2_cvPvt', mo = True, w = 0.75 )
    # cv in row 3
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':cv_5_3_cvPvt', mo = True, w = 0.75 )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_5_3_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':cv_3_3_cvPvt', mo = True, w = 0.1 )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_3_3_cvPvt', mo = True, w = 0.9 )
    # cv in row 4
    cmds.parentConstraint( 'jaw_upper_jnt_R', ns + ':cv_5_4_cvPvt', mo = True, w = 0.25 )
    cmds.parentConstraint( 'jaw_lower_jnt_R', ns + ':cv_5_4_cvPvt', mo = True, w = 0.75 )
    # cv in row 5
    # cmds.parentConstraint( 'jaw_jnt_R', ns + ':cv_5_5_cvPvt', mo = True )
    #
    cmds.setAttr( ns + ':___UTIL___.visibility', 0 )
    try:
        cmds.parent( ns + ':___UTIL___', WORLD_SPACE() )
    except:
        pass


def ____CONNECT_FACE():
    '''
    this whole sections was a fail. throat deformations were too broad. should be limited to expressions
    '''
    pass


def connect_face():
    '''
    
    '''
    # Assume that the current open file has been opened from the correct directory and get the base path from that
    ns = 'face_rig'
    path = os.path.dirname( cmds.file( query = True, exn = True ) )
    face_rig_file = 'coralSnake_rigFaceWeights_v024.ma'
    path = os.path.join( path, face_rig_file )
    cmds.file( path, reference = True, namespace = ns, force = True )

    # Geo to connect outMesh
    from_geoList = [ns + ':face:snake_body_geo_anim']

    # Geo to connect inMesh
    to_geoList = ['cor:snake_body_geo_anim']

    # import the face assets
    # importFaceAssets( path, importList )

    '''
    # Connect the outMesh to the inMesh of the specific geo
    connectInToOutMesh( from_geoList, to_geoList )

    # Connect the tongue geo
    if cmds.objExists( 'tongue_FrGeo' ) == True:
        tongueShape = cmds.listRelatives( 'tongue_FrGeo', shapes = True )[0]
        if cmds.objExists( 'tongue_Geo' ) == True:
            tongueOrg = extractShapeNode( 'tongue_Geo', True )
            cmds.connectAttr( tongueShape + '.outMesh', tongueOrg + '.inMesh', force = True )
        else:
            print( '=====tongue_Geo does not exist, skipping tongue connection.=====' )
    else:
        print( '=====tongue_FrGeo does not exist, skipping tongue connection.=====' )
    '''

    # extract the shape and orig nodes from their transforms
    head = extractShapeNode( 'cor:snake_body_geo_anim', False )
    headOrig = extractShapeNode( 'cor:snake_body_geo_anim', True )
    headFr = extractShapeNode( ns + ':face:snake_body_geo_anim', False )
    ear = None
    # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
    headInter = cmds.duplicate( head, name = head + '_intermediateGeo' )[0]

    # setup the objects to connect
    connectionList = [headFr, headInter]
    # Build the ears
    '''
    if cmds.checkBox('atom_ghstDog_earCheck', q=True, v=True):
        agd.buildGhostDogEars()
        ear = extractShapeNode('earRig_head_Geo', False)
        cmds.setAttr('earRig_head_Geo.visibility', 0)
    '''
    # create the blendShape
    blendNode = cmds.blendShape( headFr, ear, headInter, n = 'face_blendshape' )

    # set the blendNode target weights
    trgCnt = len( cmds.blendShape( blendNode, query = True, t = True ) )
    for i in range( 0, trgCnt, 1 ):
        cmds.blendShape( blendNode, edit = True, w = ( i, 1 ) )

    # Connect the blendShape to the Orig node
    cmds.connectAttr( blendNode[0] + '.outputGeometry[0]', headOrig + '.inMesh', force = True, )

    return

    # Visibility list
    setVisList = ['faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                  'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo']
    # setFaceItemsVis( setVisList )

    # parent the face grp to the head
    cmds.parentConstraint( 'neck_jnt_06', 'faceCtrl_Gp', mo = True )

    # Sebastian made me add this --starting here
    # create deformer contorllers
    # dfrm.master( deformer = True )

    # clean up OL_SKOOL rig, add to Finalize later
    cmds.setAttr( 'Up_lip_2x|faceSharedAttr.macroVisibility', 0 )
    cmds.setAttr( 'Up_lip_2x|faceSharedAttr.mainVisibility', 1 )
    cmds.setAttr( 'Up_lip_2x|faceSharedAttr.microVisibility', 0 )
    cmds.setAttr( 'Up_lip_2x|faceSharedAttr.tongueVisibility', 0 )
    cmds.select( 'LfUpBk_lipShape.cv[0:12]', 'LfUpBk_lipShape1.cv[0:12]', 'LfUpBk_lipShape2.cv[0:12]' )
    cmds.scale( 0.5, 0.5, 0.5 )
    cmds.select( 'RtUpBk_lipShape.cv[0:12]', 'RtUpBk_lipShape1.cv[0:12]', 'RtUpBk_lipShape2.cv[0:12]' )
    cmds.scale( 0.5, 0.5, 0.5 )
    cmds.select( 'Lf_eyeFK.cv[0:16]' )
    cmds.scale( 2.0, 1.0, 1.0 )
    cmds.select( 'Rt_eyeFK.cv[0:16]' )
    cmds.scale( 2.0, 1.0, 1.0 )
    cmds.delete( 'Lf_eyeFKAim_GpGp', 'Rt_eyeFKAim_GpGp ' )
    # --ending here

    # parent the face grp to the head
    cmds.parentConstraint( 'neck_jnt_06', 'faceCtrl_Gp', mo = True )
    # parent all the non parented mesh
    # parentNonParentedMesh()
    # Parent the facerig groups to the proper group
    parentList = ['faceCtrl_Gp', 'faceJnt_Gp', 'faceUtil_Gp', 'faceGeo_Gp', 'Lf_eyeFKAim_Gp', 'Rt_eyeFKAim_Gp']

    for obj in parentList:
        if cmds.objExists( obj ) == True:
            # added this in case the
            try:
                cmds.parent( obj, '___OL_SKOOL' )
            except:
                pass


def connectInToOutMesh( from_geoList, to_geoList ):
    # check that the from and to geoLists are the same size
    if len( from_geoList ) == len( to_geoList ):
        # interate through the outList
        for i in range( 0, len( from_geoList ), 1 ):
            # interate through the sides
            sides = ['Lf_', 'Rt_']
            for side in sides:
                # Check that the from object exists
                if cmds.objExists( side + from_geoList[i] ) == True:
                    fromShape = cmds.listRelatives( side + from_geoList[i], shapes = True )[0]
                    # check that the to object exists
                    if cmds.objExists( side + to_geoList[i] ) == True:
                        toOrig = extractShapeNode( side + to_geoList[i], True )
                        if toOrig != None:
                            cmds.connectAttr( fromShape + '.outMesh', toOrig + '.inMesh', force = True )
                        else:
                            print( 'Warning...' + side + to_geoList[i] + ' has no shapeOrig to connect.' )
    else:
        print( '=====List size miss match, from and to geo lists must have the same length.=====' )


def extractShapeNode( name, orig = False ):
    '''
    this can clearly have less 'if' and 'for' stupidity... fix
    '''
    objects = cmds.ls( type = 'transform' )
    returnNode = None
    if cmds.objExists( name ):
        for obj in objects:
            # find the 'name' in the object name
            if name == obj:
                shapeList = cmds.listRelatives( obj, shapes = True )
                if name == 'sculpt_Geo' or name == 'special_Geo':
                    return shapeList[0]

                elif shapeList != None:
                    for i in shapeList:
                        # if list connections returns None then the ShapeOrig has been found
                        con = cmds.listConnections( i, s = True, d = False )

                        if orig == True:
                            if con == None:
                                returnNode = i
                        else:
                            if con != None:
                                returnNode = i
    else:
        print( '=====%s, does not exists, extraction failed.=====' % ( name ) )
    return returnNode


def ____BODY():
    pass


def head():
    '''
    
    '''
    X = 1
    #
    head_Ct = place.Controller2( 'head', 'head_jnt', True, 'digitBase_ctrl', X * 7, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.setAttr( head_Ct[2] + '.showManipDefault', 2 )
    place.translationLock( head_Ct[2], lock = True )
    cmds.parentConstraint( head_Ct[4], 'head_jnt', mo = True )
    cmds.parentConstraint( 'body_001_jnt', head_Ct[0], mo = True )
    place.cleanUp( head_Ct[0], Ctrl = True )
    #
    attr = 'isolate'
    place.parentSwitch( head_Ct[2], head_Ct[2], head_Ct[1], head_Ct[0], 'body_001_jnt', 'master_Grp', False, True, False, True, attr, 0.0 )
    cmds.setAttr( head_Ct[2] + '.' + attr + 'OrientOffOn', 0.8 )
    #
    throat()
    tongue()
    fangs()
    jaw()


def neck( neck_jnt_chain = [], micro_body_cts = [] ):
    '''
    need micro body control at base of neck
    neck chain order matches micros, list is reversed
    '''
    parent_micro = micro_body_cts[len( neck_jnt_chain ) - 1]
    #
    baseCt = place.Controller2( 'neck_ik_base', neck_jnt_chain[-1], False, 'boxTallZup_ctrl', 4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( parent_micro[4], baseCt[0], mo = True )
    place.cleanUp( baseCt[0], Ctrl = True )
    place.translationLock( baseCt[2], lock = True )
    cmds.setAttr( baseCt[0] + '.v', 0 )
    #
    tipIsolateCt = place.Controller2( 'neck_ik_isolate', neck_jnt_chain[-1], False, 'squareZup_ctrl', 5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( MASTERCT()[4], tipIsolateCt[0], mo = True )
    cmds.pointConstraint( baseCt[4], tipIsolateCt[1], mo = True )
    place.cleanUp( tipIsolateCt[0], Ctrl = True )
    cmds.setAttr( tipIsolateCt[0] + '.v', 0 )

    #
    tipCt = place.Controller2( 'neck_ik_tip', neck_jnt_chain[0], False, 'boxTallZup_ctrl', 5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    pos_grp = place.group( name = tipIsolateCt[2] + '_head_position', obj = tipCt[2], order = None )  # need assisting group, point constraint parent needs exact match
    cmds.parent( pos_grp, tipIsolateCt[4] )
    cmds.parentConstraint( 'path_00_jnt', tipCt[0], mo = True )  # change, create isolated space
    place.cleanUp( tipCt[0], Ctrl = True )
    #
    attr = 'offOn'
    misc.optEnum( tipCt[2], attr = 'neckIk', enum = 'CONTROL' )
    place.addAttribute( tipCt[2], attr, 0.0, 1.0, True, 'float' )
    cmds.setAttr( tipCt[2] + '.' + attr, 1.0 )
    # position
    conPos = place.parentSwitch( 
        name = tipCt[2],
        Ct = tipCt[2],
        CtGp = tipCt[1],
        TopGp = tipCt[0],
        ObjOff = tipCt[0],
        ObjOn = pos_grp,
        Pos = True,
        Ornt = False,
        Prnt = False,
        OPT = False,
        attr = 'isolate',
        w = 0.2 )[0]
    print( conPos )
    '''
    # blend parent switches to zero
    # this is wrong, weight has to be normalized. end result when off should be so isolate value is set to the off position
    mlt1 = cmds.shadingNode( 'multDoubleLinear', n = tipCt[2] + '_ikPosWeightMlt_1', asUtility = True )
    cmds.connectAttr( tipCt[2] + '.' + attr, mlt1 + '.input1' )
    cmds.connectAttr( 'neck_ik_tip_revrsPos.outputX', mlt1 + '.input2' )
    cmds.connectAttr( mlt1 + '.output', conPos + '.neck_ik_tip_PosOffGpW0', f = True )
    #
    mlt2 = cmds.shadingNode( 'multDoubleLinear', n = tipCt[2] + '_ikPosWeightMlt_2', asUtility = True )
    cmds.connectAttr( tipCt[2] + '.' + attr, mlt2 + '.input1' )
    cmds.connectAttr( tipCt[2] + '.isolatePositionOffOn', mlt2 + '.input2' )
    cmds.connectAttr( mlt2 + '.output', conPos + '.neck_ik_tip_PosOnGpW1', f = True )
    '''
    # rotation
    conRot = place.parentSwitch( 
        name = tipCt[2],
        Ct = tipCt[2],
        CtGp = tipCt[1],
        TopGp = tipCt[0],
        ObjOff = tipCt[0],
        ObjOn = 'master_Grp',
        Pos = False,
        Ornt = True,
        Prnt = False,
        OPT = False,
        attr = 'isolate',
        w = 0.8 )[1]
    '''
    #  blend parent switches to zero
    mlt1 = cmds.shadingNode( 'multDoubleLinear', n = tipCt[2] + '_ikOrntWeightMlt_1', asUtility = True )
    cmds.connectAttr( tipCt[2] + '.' + attr, mlt1 + '.input1' )
    cmds.connectAttr( 'neck_ik_tip_revrsOrnt.outputX', mlt1 + '.input2' )
    cmds.connectAttr( mlt1 + '.output', conRot + '.neck_ik_tip_OrntOffGpW0', f = True )
    #
    mlt2 = cmds.shadingNode( 'multDoubleLinear', n = tipCt[2] + '_ikOrntWeightMlt_2', asUtility = True )
    cmds.connectAttr( tipCt[2] + '.' + attr, mlt2 + '.input1' )
    cmds.connectAttr( tipCt[2] + '.isolateOrientOffOn', mlt2 + '.input2' )
    cmds.connectAttr( mlt2 + '.output', conRot + '.neck_ik_tip_OrntOnGpW1', f = True )
    '''
    # neck to spline switch
    micros_with_spline = []
    i = 0
    s_attr = 'splineIk'
    for jnt in neck_jnt_chain:
        if parent_micro != micro_body_cts[i]:
            # neck spline down chain
            place.parentSwitch( 
                name = micro_body_cts[i][2],
                Ct = micro_body_cts[i][2],
                CtGp = micro_body_cts[i][1],
                TopGp = micro_body_cts[i][0],
                ObjOff = micro_body_cts[i][0],
                ObjOn = jnt,
                Pos = False,
                Ornt = False,
                Prnt = True,
                OPT = True,
                attr = s_attr,
                w = 0.0 )
            micros_with_spline.append( micro_body_cts[i] )
            # add hijack parent switch to one controls, skip second last one, more stable
            if i < len( neck_jnt_chain ) - 2:
                cmds.connectAttr( tipCt[2] + '.' + attr, micro_body_cts[i][2] + '.' + s_attr + 'ParentOffOn' )
            #
        i += 1

    # spline
    name = 'neck_ik'
    spline( name = name, start_jnt = neck_jnt_chain[-1], end_jnt = neck_jnt_chain[0], splinePrnt = baseCt[4], splineStrt = baseCt[4], splineEnd = tipCt[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 0.4, splineFalloff = 1 )
    cmds.setAttr( name + '.ClstrMidIkBlend', 0.9 )
    cmds.setAttr( name + '_S_IK_Cntrl.LockOrientOffOn', 1.0 )
    cmds.setAttr( name + '_E_IK_Cntrl.LockOrientOffOn', 1.0 )
    '''
    need spline spline joint chain so microbody receive parent switches to ik neck
    '''

    #
    '''
    place.hijackAttrs( baseCt[0], name, 'visibility', 'baseVis', set = True, default = 0.0, force = True )
    place.hijackAttrs( tipCt[0], name, 'visibility', 'tipVis', set = True, default = 0.0, force = True )
    '''


def body_spline( fk = False, dynamics = False, tail_as_root = False ):
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
        length = 120,
        width = 3,
        X = 2.0,
        ctrl_shape = 'pinYupZfront_ctrl',
        reverse = True,
        prebuild = False,
        prebuild_type = 4,
        fk = fk,
        dynamics = dynamics
        )
    #
    position_ctrl = place.Controller2( 'position', 'body_001_jnt', True, 'splineEnd_ctrl', 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'green' ).result
    #
    # pathIk( curve = 'path_layer_05', position_ctrl = position_ctrl, tail_as_root = tail_as_root )
    micro_body_cts = pathIk2( curve = curve, position_ctrl = position_ctrl, tail_as_root = tail_as_root, curve_up = curve_up, fk = fk )

    misc.optEnum( position_ctrl[2], attr = 'path', enum = 'CONTROL' )
    # cmds.setAttr( master + '.path', cb = False )
    i = 0
    while i <= layers - 1:
        place.hijackAttrs( master, position_ctrl[2], 'ctrlLayer' + str( i ), 'ctrlLayer' + str( i ), set = False, default = None, force = True )
        cmds.setAttr( master + '.ctrlLayer' + str( i ), cb = False )
        i += 1

    # cmds.setAttr( position_ctrl[2] + '.ctrlLayer' + str( 3 ), 1 )
    #
    return micro_body_cts
    #
    '''
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\coralSnake_path_v001.ma'
    cmds.file( pth, reference = True, namespace = 'pth', force = True )
    '''


def body_splineIk():
    '''
    sucks
    '''
    X = 1
    #
    neck_Ct = place.Controller2( 'neck_main', 'neck_00_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( neck_Ct[0], Ctrl = True )
    bodyA_Ct = place.Controller2( 'bodyA_main', 'bodyA_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( bodyA_Ct[0], Ctrl = True )
    bodyB_Ct = place.Controller2( 'bodyB_main', 'bodyB_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( bodyB_Ct[0], Ctrl = True )
    bodyC_Ct = place.Controller2( 'bodyC_main', 'bodyC_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( bodyC_Ct[0], Ctrl = True )
    bodyD_Ct = place.Controller2( 'bodyD_main', 'bodyD_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( bodyD_Ct[0], Ctrl = True )
    tail_Ct = place.Controller2( 'tail_main', 'tail_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( tail_Ct[0], Ctrl = True )
    tailTip_Ct = place.Controller2( 'tailTip_main', 'tail_11_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( tailTip_Ct[0], Ctrl = True )
    #
    # return
    spline( name = 'neck', start_jnt = 'neck_01_jnt', end_jnt = 'neck_11_jnt', splinePrnt = neck_Ct[4], splineStrt = neck_Ct[4], splineEnd = bodyA_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )
    spline( name = 'bodyA', start_jnt = 'bodyA_01_jnt', end_jnt = 'bodyA_11_jnt', splinePrnt = bodyA_Ct[4], splineStrt = 'neck_11_jnt', splineEnd = bodyB_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )
    spline( name = 'bodyB', start_jnt = 'bodyB_01_jnt', end_jnt = 'bodyB_11_jnt', splinePrnt = bodyB_Ct[4], splineStrt = 'bodyA_11_jnt', splineEnd = bodyC_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )
    spline( name = 'bodyC', start_jnt = 'bodyC_01_jnt', end_jnt = 'bodyC_11_jnt', splinePrnt = bodyC_Ct[4], splineStrt = 'bodyB_11_jnt', splineEnd = bodyD_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )
    spline( name = 'bodyD', start_jnt = 'bodyD_01_jnt', end_jnt = 'bodyD_11_jnt', splinePrnt = bodyD_Ct[4], splineStrt = 'bodyC_11_jnt', splineEnd = tail_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )
    spline( name = 'tail', start_jnt = 'tail_01_jnt', end_jnt = 'tail_11_jnt', splinePrnt = tail_Ct[4], splineStrt = 'bodyD_11_jnt', splineEnd = tailTip_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1, splineFalloff = 0 )


def body_splineFk():
    '''
    sucks
    '''
    snakeFk = sfk.SplineFK( name = 'snake', startJoint = 'neck_00_jnt', endJoint = 'tail_11_jnt', suffix = 'C', direction = 0, controllerSize = 10, rootParent = 'master_Grp', parent1 = 'master_Grp', parent2 = None, parentDefault = [1, 0], segIteration = 11, stretch = 0, ik = 'splineIK', colorScheme = 'yellow' )
    cmds.parentConstraint( snakeFk.ctrlList[0][4], 'neck_00_jnt', mo = True )
    print( snakeFk.ctrlList )


def ____PATH():
    pass


def path():
    '''
    
    '''
    ump.path2( length = 116, layers = 6, X = 12.0 )


def pathIk( curve = '', path_ctrl_height = 0, position_ctrl = None, start_jnt = 'neck_01_jnt', end_jnt = 'tail_11_jnt', tail_as_root = False ):
    '''
    ---- 
    DEAL BREAKER
    spline ik has parametric curve travel, 
    the span between each cv is the same value no matter the length, 
    can have linear travel across entire length of curve
    ----
    if head needs to be locked the joints need to be duplicated and reversed, by default tail is locked
    its assumed path and controls are already created, objects should be fed into this function, (they arent), they are hard coded
    '''
    path_jnts = get_joint_chain_hier( start_jnt = start_jnt, end_jnt = end_jnt )
    # print( path_jnts )
    # return
    if tail_as_root:
        # build reverse chain
        path_jnts = path_joint_chain( start_jnt = start_jnt, end_jnt = end_jnt )
        path_jnts.reverse()  # reverse so start joint is first in list
        print( 'path ik, as root' )
        print( path_jnts )

    # return

    #
    '''
    ns = ''
    #
    newSpine = ''
    startJnt = ''
    endJnt = ''
    #
    if ns:
        newSpine = ns + ':neck_01_jnt'
        startJnt = newSpine
        endJnt = ns + ':tail_11_jnt'
    else:
        newSpine = ns + 'neck_01_jnt'
        startJnt = newSpine
        endJnt = ns + 'tail_11_jnt'
    '''

    # Create Path Position Controller
    CtVis = 'SpineCt_Vis'
    Vect = 'upVectorVis'
    # fix parent, should be startTw
    PositionCt = None
    if not position_ctrl:
        PositionCt = place.Controller2( 'Position', start_jnt, True, 'splineStart_ctrl', 15, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    else:
        PositionCt = position_ctrl

    # create attribute for IK Slide
    attr = 'travel'
    travel_max = 100.0
    place.addAttribute( PositionCt[2], attr, 0.0, travel_max, True, 'float' )  # max is number of points on curve 31 * 10 = 310 # multiplier, MD node

    #
    # place.addAttribute( PositionCt[2], CtVis, 0, 1, True, 'float' )
    # cmds.setAttr( PositionCt[2] + '.' + CtVis, k = False, cb = True )
    place.addAttribute( PositionCt[2], Vect, 0, 1, True, 'float' )
    cmds.setAttr( PositionCt[2] + '.' + Vect, k = False, cb = True )
    cmds.xform( PositionCt[0], r = True, t = ( 0, path_ctrl_height, 0 ) )
    cmds.parentConstraint( start_jnt, PositionCt[0], mo = True )
    place.setChannels( PositionCt[2], [True, False], [True, False], [True, False], [True, True, False] )
    # place.translationLock( PositionCt[2], lock = True )
    # place.rotationLock( PositionCt[2], lock = True )
    place.cleanUp( PositionCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    # Create Ik Handle
    ikhandle = cmds.ikHandle( sj = path_jnts[0], ee = path_jnts[-1], sol = 'ikSplineSolver', ccv = False, c = curve, pcv = False )[0]
    cmds.setAttr( ikhandle + '.dTwistControlEnable', 1 )
    # cmds.setAttr( ikhandle + '.dWorldUpType', 4 )
    cmds.setAttr( ikhandle + '.dWorldUpType', 7 )
    cmds.setAttr( ikhandle + '.dForwardAxis', 4 )
    cmds.setAttr( ikhandle + '.dWorldUpAxis', 0 )
    place.hijackAttrs( ikhandle, 'Position', 'dWorldUpType', 'upVectorType', set = True, default = 2, force = True )

    # start twist
    startCt = place.Controller2( 'startTwist', start_jnt, True, 'loc_ctrl', 30, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'pink' ).result
    cmds.setAttr( startCt[0] + '.translateY', 75 )
    cmds.parentConstraint( 'master_Grp', startCt[0], mo = True )
    cmds.connectAttr( PositionCt[2] + '.' + Vect, startCt[0] + '.visibility' )
    place.setChannels( startCt[2], [False, True], [True, False], [True, False], [True, True, False] )  # [lock, keyable]
    place.cleanUp( startCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    guide_line_one_to_many( startCt[2], path_jnts )

    # end twist
    endCt = place.Controller2( 'endTwist', end_jnt, True, 'loc_ctrl', 30, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'pink' ).result
    cmds.setAttr( endCt[0] + '.translateY', 75 )
    cmds.parentConstraint( 'master_Grp', endCt[0], mo = True )
    cmds.connectAttr( PositionCt[2] + '.' + Vect, endCt[0] + '.visibility' )
    place.setChannels( endCt[2], [False, True], [True, False], [True, False], [True, True, False] )  # [lock, keyable]
    place.cleanUp( endCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    guide_line_one_to_many( endCt[2], path_jnts )

    cmds.connectAttr( startCt[4] + '.worldMatrix', ikhandle + '.dWorldUpMatrix' )  # likely wont use this
    cmds.connectAttr( endCt[4] + '.worldMatrix', ikhandle + '.dWorldUpMatrixEnd' )  # likely wont use this
    #
    # start up vector ramp
    #
    cmds.setAttr( ikhandle + '.dTwistValueType', 2 )
    twist_mlt = -3.4
    if tail_as_root:
        twist_mlt = twist_mlt * -1
    cmds.setAttr( ikhandle + '.dTwistRampMult', twist_mlt )  # guessing at multiplier
    ramp = cmds.shadingNode( 'ramp', name = ikhandle + '_twistRamp', asTexture = True )
    cmds.connectAttr( ramp + '.outColor', ikhandle + '.dTwistRamp', force = True )
    #
    cmds.connectAttr( 'head.rotateZ', ramp + '.colorEntryList[0].colorR', force = True )
    #
    # add twist controls
    pathTwist( amount = 4, ramp = ramp, curve = curve )

    # Hide and Parent ikhandle
    cmds.setAttr( ikhandle + '.lodVisibility', 0 )
    place.cleanUp( ikhandle, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # normalize travel to 100
    spans = cmds.getAttr( curve + '.spans' )
    mlt = cmds.createNode( 'multiplyDivide', n = 'travel_mlt' )
    cmds.connectAttr( PositionCt[2] + '.' + attr, mlt + '.input1X' )
    cmds.setAttr( mlt + '.input2X', spans / travel_max )
    cmds.connectAttr( mlt + '.outputX', ikhandle + '.offset' )

    #
    cmds.select( ikhandle, ramp )
    mm.eval( 'dgdirty;' )


def pathTwist( amount = 4, ramp = '', curve = '' ):
    '''
    could be missing connections to ramp texture, eval doesnt happen properly, check against manual build, with ramp texture... maybe 2d texture node
    '''
    # math for changing path length, should keep twists at same spot from root
    crv_info = cmds.arclen( curve, ch = True, n = ( curve + '_arcLength' ) )  # add math nodes so twist controls stick to body no matter the length of the curve
    arc_length = cmds.getAttr( crv_info + '.arcLength' )
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

    #
    twist_c = []
    mlts_n = []
    rvrs_n = []
    ramp_int = 1
    # spans = cmds.getAttr( curve + '.spans' )
    # print( 'spans: ', spans )
    distribute = 1 / ( amount + 1 )
    # print( 'distribute: ', distribute )
    i = 0
    #
    while i <= amount:
        #
        TwstCt = place.Controller2( 'Twist_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ), curve, True, 'facetZup_ctrl', 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result  # use curve node for initial placement
        cmds.setAttr( TwstCt[2] + '.showManipDefault', 2 )
        place.cleanUp( TwstCt[0], Ctrl = True )
        place.translationLock( TwstCt[2], lock = True )
        place.rotationLock( TwstCt[2], lock = True )
        place.rotationZLock( TwstCt[2], lock = False )
        twist_c.append( TwstCt )
        place.addAttribute( TwstCt[2], 'position', 0.0, 100.0, True, 'float' )  # max is number of points in curve

        # Normalize start position to 100, matches Travel attr
        v = distribute * ramp_int * 100
        # print( 'set position: ', v )
        cmds.setAttr( TwstCt[2] + '.position', v )
        mo_path = cmds.pathAnimation( TwstCt[0], name = TwstCt[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
        cmds.setAttr( mo_path + '.fractionMode', True )  # turn off parametric, sets start/end range 0/1
        ac.deleteAnim2( mo_path, attrs = ['uValue'] )

        # reverse rotation
        rvrs = cmds.shadingNode( 'reverse', n = TwstCt[2] + '_rvrs', asUtility = True )  # reverse rotation
        rvrs_n.append( rvrs )
        cmds.connectAttr( TwstCt[2] + '.rotateZ', rvrs + '.inputZ', force = True )
        cmds.connectAttr( rvrs + '.outputZ', ramp + '.colorEntryList[' + str( ramp_int ) + '].colorR', force = True )

        # multiply to merge length changes and position input form control, math prepped at start of function
        mlt_merge_length = cmds.shadingNode( 'multDoubleLinear', n = TwstCt[2] + '_mergeLengthMlt', asUtility = True )
        cmds.connectAttr( TwstCt[2] + '.position', mlt_merge_length + '.input1', force = True )
        cmds.connectAttr( dvd_multiplier + '.outputZ', mlt_merge_length + '.input2', force = True )

        # multiply ramp position to match travel along curve
        mlt_ramp = cmds.shadingNode( 'multDoubleLinear', n = TwstCt[2] + '_rampMlt', asUtility = True )
        mlts_n.append( mlt_ramp )
        cmds.setAttr( mlt_ramp + '.input2', 0.01 )
        cmds.connectAttr( TwstCt[2] + '.position', mlt_ramp + '.input1', force = True )
        cmds.connectAttr( mlt_ramp + '.output', ramp + '.colorEntryList[' + str( ramp_int ) + '].position', force = True )

        # add twist position attr and main travel attr values
        dbl_path = cmds.createNode( 'addDoubleLinear', name = ( TwstCt[2] + '_DblLnr' ) )
        cmds.connectAttr( mlt_merge_length + '.output', dbl_path + '.input1', force = True )
        cmds.connectAttr( 'Position.travel', dbl_path + '.input2', force = True )  # hardcoded control, shouldnt be, fix it
        # normalize result
        mlt_path = cmds.shadingNode( 'multDoubleLinear', n = TwstCt[2] + '_pathMlt', asUtility = True )
        cmds.setAttr( mlt_path + '.input2', 0.01 )
        cmds.connectAttr( dbl_path + '.output', mlt_path + '.input1', force = True )
        cmds.connectAttr( mlt_path + '.output', mo_path + '.uValue', force = True )

        ramp_int += 1
        i += 1


def pathIk2( curve = 'path_layer_05_result', position_ctrl = None, start_jnt = 'body_001_jnt', end_jnt = 'body_121_jnt', tail_as_root = False, curve_up = '', fk = False, ribn = 'layer_05_ribbon' ):
    '''
    based on cmds.pathAnimation()
    spline ik has parametric curve travel, the span between each cv is the same value no matter the length, can have linear travel across entire length of curve
    '''
    new_up = False  # this is a fail, remove code that relates
    # travel control
    PositionCt = None
    if not position_ctrl:
        PositionCt = place.Controller2( 'position', start_jnt, True, 'splineEnd_ctrl', 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'green' ).result
    else:
        PositionCt = position_ctrl
    # create attribute
    t_attr = 'travel'
    travel_min = -10000.0  # meant to be used as percent. length is 50%, 300% ,of original length
    travel_max = 10000.0
    place.addAttribute( PositionCt[3], t_attr, travel_min, travel_max, True, 'float' )
    mlt_merge_travel_length = cmds.shadingNode( 'multDoubleLinear', n = PositionCt[3] + '_mergeLengthMlt', asUtility = True )  # connect below, twice
    cmds.connectAttr( PositionCt[3] + '.' + t_attr, mlt_merge_travel_length + '.input1', force = True )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], t_attr, t_attr, set = False, default = None, force = True )
    # root attr
    root_attr = 'headAsRoot'
    place.addAttribute( PositionCt[3], root_attr, 0.0, 1.0, True, 'float' )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], root_attr, root_attr, set = True, default = 1.0, force = True )
    #
    cmds.pointConstraint( start_jnt, PositionCt[0], mo = True )
    cmds.orientConstraint( MASTERCT()[2], PositionCt[0], mo = True )
    place.setChannels( PositionCt[2], [True, False], [True, False], [True, False], [True, True, False] )
    place.cleanUp( PositionCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( PositionCt[2] + '.v', k = False, cb = False )
    cmds.setAttr( PositionCt[2] + '.ro', k = False, cb = False )
    cmds.setAttr( PositionCt[2] + '.Offset_Vis', k = False, cb = False )
    #
    misc.optEnum( PositionCt[2], attr = 'extra', enum = 'CONTROL' )
    #
    '''
    v_attr = 'upVis'
    place.addAttribute( PositionCt[2], v_attr, 0, 1, True, 'long' )
    cmds.setAttr( PositionCt[2] + '.' + v_attr, k = False, cb = True )
    '''
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

    '''
    # up path
    crv_info_up = cmds.arclen( curve_up, ch = True, n = ( curve_up + '_arcLength' ) )  # add math nodes so twist controls stick to body no matter the length of the curve
    # divide 2 arcLengths
    dvd_length_up = cmds.shadingNode( 'multiplyDivide', au = True, n = ( curve_up + '_lengthDvd' ) )
    cmds.setAttr( ( dvd_length_up + '.operation' ), 2 )  # set operation: 2 = divide, 1 = multiply
    cmds.connectAttr( ( crv_info_up + '.arcLength' ), ( dvd_length_up + '.input1Z' ) )
    cmds.connectAttr( ( crv_info + '.arcLength' ), ( dvd_length_up + '.input2Z' ) )
    '''
    #
    '''
    # create tail as root nodes
    mlt_tail_length = cmds.shadingNode( 'multDoubleLinear', n = curve + '_tailLockMlt', asUtility = True )  # to negative, to percent
    cmds.setAttr( mlt_tail_length + '.input2', -100 )
    cmds.connectAttr( dvd_multiplier + '.outputZ', mlt_tail_length + '.input1' )
    #
    add_tail_shift = cmds.createNode( 'addDoubleLinear', name = ( curve + '_tailAddLnr' ) )  # percent to move, so distance remains the same at tail
    cmds.connectAttr( mlt_tail_length + '.output', add_tail_shift + '.input2' )
    cmds.setAttr( add_tail_shift + '.input1', 100 )'''

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
            microUpCt = place.Controller2( name, j, True, 'loc_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
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
        microBodyCt = place.Controller2( name, skin_jnts[i], False, 'facetZup_ctrl', 3.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
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
        microCt = place.Controller2( name, j, True, 'rectangleWideYup_ctrl', 2, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
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

        # multiply ramp position to match travel along curve
        '''
        mlt_ramp = cmds.shadingNode( 'multDoubleLinear', n = microCt[2] + '_rampMlt', asUtility = True )
        # mlts_n.append( mlt_ramp )
        cmds.setAttr( mlt_ramp + '.input2', 0.01 )
        cmds.connectAttr( microCt[2] + '.position', mlt_ramp + '.input1', force = True )
        cmds.connectAttr( mlt_ramp + '.output', ramp + '.colorEntryList[' + str( ramp_int ) + '].position', force = True )
        '''

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
        cmds.connectAttr( position_ctrl[3] + '.' + t_attr, travel_tail_add + '.input1' )
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

        '''
        #
        # multiply final position result by this output
        mlt_length_dif = cmds.shadingNode( 'multDoubleLinear', n = microCt[2] + '_lengthDifMlt', asUtility = True )
        cmds.connectAttr( ( dvd_length_up + '.outputZ' ), ( mlt_length_dif + '.input2' ) )
        # out needs to be multiplied by length change of up curve vs path curve
        cmds.connectAttr( mlt_path + '.output', ( mlt_length_dif + '.input1' ) )
        cmds.connectAttr( mlt_length_dif + '.output', mo_path_up + '.uValue', force = True )
        # finish up vector travel and aim constraint for snake
        '''

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
            cmds.aimConstraint( attach_jnts[i - 1], microCt[1], mo = True, wuo = microUpCt[4], wut = 'object', aim = [0, 0, 1], u = [0, 1, 0] )

        #
        i += 1

    # guides
    # guides_grp = guide_many_to_many( PositionCt[2], attach_jnts, upCts, 5 )
    guides_grp = guide_many_to_many( prefix = 'many', vis_object = PositionCt[2], many1 = attach_jnts, many2 = upCts, offset = 0.0, every_nth = 5 )
    '''
    tail lock working, need to add travel offset
    '''
    return micro_body_cts


def dynamicJiggle():
    '''
    should be added to main controller class
    convert this to standalone so already existing controls can receive functionality
    '''
    name = 'control'
    # plane
    plane = cmds.polyPlane( n = name + '_planeGoal', sx = 2, sy = 2 )[0]
    place.cleanUp( plane, World = True )
    cmds.setAttr( plane + '.visibility', 0 )
    # dynamic plane
    mm.eval( 'dynCreateNSoft 0 0 1 0.5 1;' )
    plane_dy = cmds.rename( 'copyOf' + plane, name + '_planeDynamic' )
    cmds.setAttr( plane_dy + '.visibility', 1 )
    place.cleanUp( plane_dy, World = True )
    c = cmds.listRelatives( plane_dy, children = True )
    plane_particle = cmds.rename( c[1], plane_dy + '_particle' )
    plane_particle = cmds.listRelatives( plane_particle, shapes = True )[0]
    # control
    _Ct = place.Controller2( name, plane, True, 'boxZup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( _Ct[0], Ctrl = True )
    cmds.parentConstraint( _Ct[3], plane )
    cmds.pointOnPolyConstraint( plane_dy + '.vtx[4]', _Ct[4] )
    # hijack attrs
    misc.optEnum( _Ct[2], attr = 'Dynamic', enum = 'CONTROL' )
    # dynamic enable attr connection
    en_attr = 'isDynamic'
    place.hijackAttrs( plane_particle, _Ct[2], en_attr, en_attr, set = False, default = 0, force = True )
    cmds.setAttr( _Ct[2] + '.' + en_attr, k = False )
    cmds.setAttr( _Ct[2] + '.' + en_attr, cb = True )
    #
    s_attr = 'startFrame'
    cmds.addAttr( _Ct[2], ln = s_attr, at = 'long', h = False )
    cmds.setAttr( _Ct[2] + '.' + s_attr, cb = True )
    cmds.setAttr( _Ct[2] + '.' + s_attr, k = False )
    cmds.setAttr( _Ct[2] + '.' + s_attr, 1001 )
    cmds.connectAttr( _Ct[2] + '.' + s_attr, plane_particle + '.' + s_attr, force = True )
    # connectAttr -f control.startFrame control_planeDynamic_particleShape.goalWeight[0];
    goal_attr = 'goalWeight'
    cmds.addAttr( _Ct[2], ln = goal_attr, at = 'float', h = False )
    cmds.setAttr( _Ct[2] + '.' + goal_attr, cb = True )
    cmds.setAttr( _Ct[2] + '.' + goal_attr, k = True )
    cmds.setAttr( _Ct[2] + '.' + goal_attr, 0.25 )
    cmds.connectAttr( _Ct[2] + '.' + goal_attr, plane_particle + '.' + goal_attr + '[0]', force = True )
    # place.hijackAttrs( plane_particle, _Ct[2], goal_attr, goal_attr, set = False, default = 0.25, force = True )
    #
    damp_attr = 'damp'
    place.hijackAttrs( plane_particle, _Ct[2], damp_attr, damp_attr, set = False, default = 0.04, force = True )


def ____JOINTS():
    pass


def neck_joint_chain( start_jnt = '', end_jnt = '', reroot = True ):
    '''
    duplicate skin joint chain, rename and reverse hierarchy
    '''
    # duplicate
    dup = cmds.duplicate( start_jnt, rc = True )
    cmds.parent( dup[0], w = True )  # unparent
    #
    cmds.delete( 'head_jnt1' )  # cleanup children, should automate this at some stage.

    # rename
    cmds.select( dup[0], hi = True )
    names = cmds.ls( sl = True )
    print( names )
    #
    i = 1
    for jnt in names:
        print( jnt )
        if jnt == end_jnt + '1':
            children = cmds.listRelatives( jnt, children = True )
            if children:
                cmds.delete( children )
            cmds.rename( jnt, 'neck_ik_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) + '_jnt' )
            break
        else:
            cmds.rename( jnt, 'neck_ik_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) + '_jnt' )
        i += 1

    # reroot chain and fix joint orients
    neck_ik_jnts = cmds.ls( sl = True )
    if reroot:
        cmds.reroot( neck_ik_jnts[-1] )
        for j in neck_ik_jnts:
            if j == neck_ik_jnts[0]:  # first is the last joint(reversed list), needs manual correction, maya skips it
                # doesnt work cuz the, likely previous joint reverts the change
                cmds.setAttr( j + '.jointOrientX', 0 )
                cmds.setAttr( j + '.jointOrientY', 0 )
                cmds.setAttr( j + '.jointOrientZ', 0 )
            else:
                cmds.select( j )
                cmds.joint( e = True, oj = 'zyx', secondaryAxisOrient = 'yup', ch = True, zso = True )

    cmds.setAttr( neck_ik_jnts[0] + '.jointOrientX', 0 )
    cmds.setAttr( neck_ik_jnts[0] + '.jointOrientY', 0 )
    cmds.setAttr( neck_ik_jnts[0] + '.jointOrientZ', 0 )
    # neck_ik_jnts.reverse()
    print( 'duplicated' )
    print( neck_ik_jnts )

    if reroot:
        place.cleanUp( neck_ik_jnts[-1], SknJnts = True )
    else:
        place.cleanUp( neck_ik_jnts[0], SknJnts = True )
    return neck_ik_jnts


def path_joint_chain( start_jnt = '', end_jnt = '', reroot = False ):
    '''
    duplicate skin joint chain and reverse hierarchy
    skin joints will be in the middle of the body, path joints need to placed down to ground level
    '''
    #
    skin_jnts = get_joint_chain_hier( start_jnt = start_jnt, end_jnt = end_jnt, chain = None )

    # duplicate
    dup = cmds.duplicate( start_jnt, rc = True )
    cmds.parent( dup[0], w = True )  # unparent
    #
    cmds.delete( 'head_jnt1' )  # cleanup children, should automate this at some stage.

    # to world
    '''
    print( dup )
    for j in dup:
        print( j )
        if j != dup[0]:
            cmds.parent( j, w = True )
    # to ground
    for j in dup:
        cmds.setAttr( j + '.ty', 0.0 )
    # reparent
    for j in range( len( dup ) - 1 ):
        cmds.parent( dup[j + 1], dup[j] )'''

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


def skin_jnts_to_path_jnts( skin_jnts = [], path_jnts = [], controls = True ):
    '''
    
    '''
    # path_jnts.reverse()
    for i in range( len( skin_jnts ) ):
        cmds.parentConstraint( path_jnts[i], skin_jnts[i], mo = True )
        # print( i )
    # path_jnts.reverse()


def ____UTIL():
    pass


def atom_ui():
    '''
    dumb legacy hack
    splines dont build unless window is open, maybe other tools as well
    '''
    atom = web.mod( "atom_lib" )
    atom.win()


def guide_line_one_to_many( obj = '', many = [], offset = 1.5 ):
    '''
    
    '''
    n = cmds.group( name = obj + '_up_GuideGrp', em = True )
    place.hijackVis( n, obj, name = 'guides', suffix = True, default = False, mode = 'visibility' )
    place.cleanUp( n, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    for m in many:
        g = cmds.group( name = obj + '___' + m, em = True )
        result = place.guideLine( obj, m, Name = 'guide' )
        #
        cmds.select( result[1][1] )
        cmds.pickWalk( d = 'down' )
        cmds.pickWalk( d = 'left' )
        c = cmds.ls( sl = True )[0]
        cmds.setAttr( c + '.offsetY', offset )
        #
        cmds.parent( result[0], g )
        cmds.parent( result[1], g )
        cmds.parent( g, n )


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


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def CONTROLS():
    return '___CONTROLS'


def WORLD_SPACE():
    return '___WORLD_SPACE'


def MASTERCT():
    return [
    'master_TopGrp',
    'master_CtGrp',
    'master',
    'master_Offset',
    'master_Grp'
    ]


def spline( name = '', start_jnt = '', end_jnt = '', splinePrnt = '', splineStrt = '', splineEnd = '', startSkpR = False, endSkpR = False, color = 'yellow', X = 2, splineFalloff = 1 ):
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
    attr_Ct = place.Controller2( name, start_jnt, True, 'pinYup_ctrl', X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    try:
        cmds.parent( attr_Ct[0], CONTROLS() )
    except:
        pass
    cmds.parentConstraint( splineStrt, attr_Ct[0], mo = True )
    # lock translation
    place.rotationLock( attr_Ct[2], True )
    place.translationLock( attr_Ct[2], True )

    # SPINE
    splineName = name
    splineSize = X * 1
    splineDistance = X * 10

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
    cmds.setAttr( splineAttr + '.' + 'Vis', 0 )
    cmds.setAttr( splineAttr + '.' + 'Root', 0 )
    cmds.setAttr( splineAttr + '.' + 'Stretch', 0 )
    cmds.setAttr( splineAttr + '.ClstrVis', 0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrVis', 0 )
    cmds.setAttr( splineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # scale
    try:
        cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_E_IK_curve_scale.input2Z' )
    except:
        pass


def mirror_neg_x():
    '''
    basic code, needs work, simple variation
    '''
    # wildcard
    cmds.select( '*:*cvPvt' )
    sel = cmds.ls( sl = True )
    for s in sel:
            if 'jaw' in s:
                ty = cmds.getAttr( s + '.ty' )
                cmds.setAttr( s + '.ty', ty * -1 )


def mirror_complex():
    '''
    cvs in same row swap values from left to right, need method
    '''
    pass


def connect_cache_geo():
    '''
    connect rig geo to cache geo
    '''
    rig_geo = high_geo()
    cache = cache_geo()
    i = 0
    for geo in rig_geo:
        name = geo.split( ':' )[-1]
        node = cmds.blendShape( geo, cache[i], n = name )[0]
        cmds.setAttr( node + '.' + name, 1 )
        i += 1


def ____SKIN():
    pass


def weights_meshExport():
    '''
    snake
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

    # geo
    all_geo = high_geo()
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


def weights_meshImport( lod100 = True, lod300 = True ):
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    if lod100:
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
            try:
                krl.importWeights02( geo, im_path )
            except:
                print( 'geo failed to import weights: ', geo )
    #
    if lod300:
        all_geo = high_geo()
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
            try:
                krl.importWeights02( geo, im_path )
            except:
                print( 'geo failed to import weights: ', geo )


def weights_face_meshExport():
    '''
    snake
    '''
    # path
    path = weights_path()
    # geo
    all_geo = low_face_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, '_face_' + g )
        cmds.select( geo )
        krl.exportWeights02( ex_path )

    # geo
    all_geo = high_face_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        elif ':' in geo:
            g = geo.split( ':' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, '_face_' + g )
        cmds.select( geo )
        krl.exportWeights02( ex_path )


def weights_face_meshImport( lod100 = True, lod300 = True ):
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    if lod100:
        # geo
        all_geo = low_face_geo()
        for geo in all_geo:
            g = ''
            if '|' in geo:
                g = geo.split( '|' )[-1]
            elif ':' in geo:
                g = geo.split( ':' )[-1]
            else:
                g = geo
            im_path = os.path.join( path, '_face_' + g )
            cmds.select( geo )
            # print( im_path )
            try:
                krl.importWeights02( geo, im_path )
            except:
                print( 'geo failed to import weights: ', geo )
    #
    if lod300:
        all_geo = high_face_geo()
        for geo in all_geo:
            g = ''
            if '|' in geo:
                g = geo.split( '|' )[-1]
            elif ':' in geo:
                g = geo.split( ':' )[-1]
            else:
                g = geo
            im_path = os.path.join( path, '_face_' + g )
            cmds.select( geo )
            # print( im_path )
            try:
                krl.importWeights02( geo, im_path )
            except:
                print( 'geo failed to import weights: ', geo )


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
    return ['cor:snake_body_Low_geo', 'cor:snake_tongue_low_geo', 'cor:snake_eye_low_right', 'cor:snake_eye_low_left']


def high_geo():
    return ['cor:snake_body_geo_anim', 'cor:snake_tongue_geo_anim', 'cor:snake_eye_right_anim', 'cor:snake_eye_left_anim']


def cache_geo():
    return ['cor:snake_body_geo', 'cor:snake_tongue_geo', 'cor:snake_eye_right', 'cor:snake_eye_left']
'''
import webrImport as web
acs = web.mod( 'asset_coralSnake' )
acs.prebuild()
acs.head()
acs.body_spline()
#acs.dynamicJiggle()
#acs.body_splineFk()
#acs.body_splineIk()


# weights
acs.weights_meshExport()
'''


def low_face_geo():
    return ['face:snake_body_Low_geo']


def high_face_geo():
    '''
    face only, body geo
    '''
    return ['face:snake_body_geo_anim']
