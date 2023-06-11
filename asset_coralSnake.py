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


def ____PREBUILD():
    pass


def prebuild():
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
    # weights
    weights_meshImport()
    #
    cmds.parentConstraint( 'master_Grp', 'root_jnt', mo = True )
    place.cleanUp( 'root_jnt', SknJnts = True )
    cmds.deltaMush( low_geo(), smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

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
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def build():
    '''
    
    '''
    prebuild()
    head()
    con = cmds.parentConstraint( 'neck_03_jnt', 'neckIk_base_jnt', mo = True )  # need micro body controls to exist, have to constraint to skin joint, and apply rig after body_spline
    body_spline( tail_as_root = False )
    cmds.delete( con )
    neck()


def ____FACE():
    pass


def tongue():
    # tongue
    # TongueCt = place.Controller2( 'Tongue', 'jaw_jnt', False, 'splineStart_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    tongueMicro = faceRig.snakeTongue( 'tongue', 0.3 )


def throat():
    '''
    
    '''
    #
    baseCt = place.Controller2( 'throat', 'throat_base_jnt', True, 'facetXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'neck_02_jnt', baseCt[0], mo = True )
    cmds.parentConstraint( baseCt[4], 'throat_base_jnt', mo = True )
    place.cleanUp( baseCt[0], Ctrl = True )
    #
    tipCt = place.Controller2( 'throat_tip', 'throat_tip_jnt', True, 'facetXup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'jawTip_jnt', tipCt[0], mo = True )
    cmds.parentConstraint( tipCt[4], 'throat_tip_jnt', mo = True )
    place.cleanUp( tipCt[0], Ctrl = True )

    # spline
    name = 'throatMicro'
    spline( name = name, start_jnt = 'throat_01_jnt', end_jnt = 'throat_05_jnt', splinePrnt = 'neck_02_jnt', splineStrt = baseCt[4], splineEnd = tipCt[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 0.1, splineFalloff = 1 )
    #
    cmds.setAttr( name + '.Stretch', 1 )
    cmds.setAttr( name + '.ClstrMidIkBlend', 0.5 )
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
    cmds.parentConstraint( 'head_jnt', fangLCt[0], mo = True )
    cmds.parentConstraint( 'head_jnt', fangRCt[0], mo = True )
    place.cleanUp( fangLCt[0], Ctrl = True )
    place.cleanUp( fangRCt[0], Ctrl = True )


def jaw():
    #
    JawCt = place.Controller2( 'jaw', 'jaw_jnt', True, 'rectangleZforward_ctrl', 2.45, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.setAttr( JawCt[2] + '.showManipDefault', 2 )
    place.translationLock( JawCt[2], True )
    cmds.parentConstraint( JawCt[4], 'jaw_jnt', mo = True )
    cmds.parentConstraint( 'head_jnt', JawCt[0], mo = True )
    place.cleanUp( JawCt[0], Ctrl = True )
    #
    JawTipCt = place.Controller2( 'jaw_tip', 'jawTip_jnt', True, 'rectangleWideZup_ctrl', 0.75, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.setAttr( JawTipCt[2] + '.showManipDefault', 2 )
    place.translationLock( JawTipCt[2], True )
    place.rotationLock( JawTipCt[2], True )
    place.rotationZLock( JawTipCt[2], False )
    cmds.parentConstraint( 'jaw_jnt', JawTipCt[0], mo = True )
    cmds.parentConstraint( JawTipCt[4], 'jawTip_jnt', mo = True )
    place.cleanUp( JawTipCt[0], Ctrl = True )
    #
    JawLCt = place.Controller2( 'jaw_tip_L', 'jawTip_jnt_L', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.setAttr( JawLCt[2] + '.showManipDefault', 1 )
    place.translationLock( JawLCt[2], True )
    place.rotationLock( JawLCt[2], True )
    place.translationYLock( JawLCt[2], False )
    cmds.parentConstraint( JawTipCt[4], JawLCt[0], mo = True )
    place.cleanUp( JawLCt[0], Ctrl = True )
    cmds.setAttr( JawLCt[0] + '.v', 0 )
    #
    JawRCt = place.Controller2( 'jaw_tip_R', 'jawTip_jnt_R', True, 'squareZup_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.setAttr( JawRCt[2] + '.showManipDefault', 1 )
    place.translationLock( JawRCt[2], True )
    place.rotationLock( JawRCt[2], True )
    place.translationYLock( JawRCt[2], False )
    cmds.parentConstraint( JawTipCt[4], JawRCt[0], mo = True )
    place.cleanUp( JawRCt[0], Ctrl = True )
    cmds.setAttr( JawRCt[0] + '.v', 0 )
    #
    apg.aimRig( name = 'jaw_L', obj = 'jaw_jnt_L', aimObj = JawLCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, 1], up = [0, 1, 0] )
    apg.aimRig( name = 'jaw_R', obj = 'jaw_jnt_R', aimObj = JawRCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, -1], up = [0, -1, 0] )


def ____BODY():
    pass


def head():
    '''
    
    '''
    X = 1
    #
    head_Ct = place.Controller2( 'head', 'head_jnt', True, 'bedZforward_ctrl', X * 3.25, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.setAttr( head_Ct[2] + '.showManipDefault', 2 )
    place.translationLock( head_Ct[2], lock = True )
    cmds.parentConstraint( head_Ct[4], 'head_jnt', mo = True )
    cmds.parentConstraint( 'neck_01_jnt', head_Ct[0], mo = True )
    place.cleanUp( head_Ct[0], Ctrl = True )
    #
    place.parentSwitch( head_Ct[2], head_Ct[2], head_Ct[1], head_Ct[0], 'master_Grp', 'neck_01_jnt', False, True, False, True, 'Neck', 0.0 )
    #
    throat()
    tongue()
    fangs()
    jaw()


def neck( micro_body_control = 'micro_body_02' ):
    '''
    need micro body control at base of neck
    parent option for micro controls
    should easily be able to change length of neck.... should be able to place spline joints, instead of having them pre-made
    '''
    #
    baseCt = place.Controller2( 'neck_ik_base', 'neckIk_base_jnt', True, 'facetZup_ctrl', 4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( micro_body_control, baseCt[0], mo = True )
    cmds.parentConstraint( baseCt[4], 'neckIk_base_jnt', mo = True )
    place.cleanUp( baseCt[0], Ctrl = True )
    #
    tipCt = place.Controller2( 'neck_ik_tip', 'neckIk_tip_jnt', True, 'facetZup_ctrl', 5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( micro_body_control, tipCt[0], mo = True )
    cmds.parentConstraint( tipCt[4], 'neckIk_tip_jnt', mo = True )
    place.cleanUp( tipCt[0], Ctrl = True )
    '''
    tip needs control rotating with world from base as a parent or fk. add switch
    '''

    # spline
    name = 'neck_ik'
    spline( name = name, start_jnt = 'neckIk_01_jnt', end_jnt = 'neckIk_03_jnt', splinePrnt = baseCt[4], splineStrt = baseCt[4], splineEnd = tipCt[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 0.4, splineFalloff = 1 )
    cmds.setAttr( name + '.ClstrMidIkBlend', 0.5 )
    '''
    need spline spline joint chain so microbody receive parent switches to ik neck
    '''

    #
    '''
    place.hijackAttrs( baseCt[0], name, 'visibility', 'baseVis', set = True, default = 0.0, force = True )
    place.hijackAttrs( tipCt[0], name, 'visibility', 'tipVis', set = True, default = 0.0, force = True )
    '''


def body_spline( tail_as_root = True ):
    '''
    fix hard coded names
    '''
    # TODO: need to reverse chain so tail sticks, not head
    #
    reverse = True
    if tail_as_root:
        reverse = False

    #
    master = 'master'
    layers = 6
    # returnsNothing_FixIt = ump.path2( length = 120, layers = layers, X = 18.0, prebuild = False, ctrl_shape = 'diamond_ctrl', reverse = reverse )
    curve, curve_up = ump.ribbon_path( name = '', layers = 6, length = 120, width = 3, X = 2.0, ctrl_shape = 'halfPyramidZ_ctrl', reverse = True, prebuild = False, prebuild_type = 4 )
    #
    position_ctrl = place.Controller2( 'position', 'neck_01_jnt', True, 'pinYup_ctrl', 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    #
    # pathIk( curve = 'path_layer_05', position_ctrl = position_ctrl, tail_as_root = tail_as_root )
    pathIk2( curve = curve, position_ctrl = position_ctrl, tail_as_root = tail_as_root, curve_up = curve_up )
    #
    misc.optEnum( position_ctrl[2], attr = 'path', enum = 'CONTROL' )
    # cmds.setAttr( master + '.path', cb = False )
    i = 0
    while i <= layers - 1:
        place.hijackAttrs( master, position_ctrl[2], 'ctrlLayer' + str( i ), 'ctrlLayer' + str( i ), set = False, default = None, force = True )
        cmds.setAttr( master + '.ctrlLayer' + str( i ), cb = False )
        i += 1

    cmds.setAttr( position_ctrl[2] + '.ctrlLayer' + str( 3 ), 1 )
    #
    return
    #
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\coralSnake_path_v001.ma'
    cmds.file( pth, reference = True, namespace = 'pth', force = True )


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


def pathIk2( curve = 'path_layer_05', position_ctrl = None, start_jnt = 'neck_01_jnt', end_jnt = 'tail_11_jnt', tail_as_root = False, curve_up = '' ):
    '''
    based on cmds.pathAnimation()
    spline ik has parametric curve travel, the span between each cv is the same value no matter the length, can have linear travel across entire length of curve
    '''
    # travel control
    PositionCt = None
    if not position_ctrl:
        PositionCt = place.Controller2( 'position', start_jnt, True, 'pinYup_ctrl', 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    else:
        PositionCt = position_ctrl
    # create attribute
    t_attr = 'travel'
    travel_max = 2000.0  # meant to be used as percent. length is 50%, 300% ,of original length
    place.addAttribute( PositionCt[3], t_attr, 0.0, travel_max, True, 'float' )
    mlt_merge_travel_length = cmds.shadingNode( 'multDoubleLinear', n = PositionCt[3] + '_mergeLengthMlt', asUtility = True )  # connect below, twice
    cmds.connectAttr( PositionCt[3] + '.' + t_attr, mlt_merge_travel_length + '.input1', force = True )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], t_attr, t_attr, set = False, default = None, force = True )
    # root attr
    root_attr = 'headAsRoot'
    place.addAttribute( PositionCt[3], root_attr, 0.0, 1.0, True, 'float' )
    place.hijackAttrs( position_ctrl[3], position_ctrl[2], root_attr, root_attr, set = True, default = 1.0, force = True )
    #
    cmds.parentConstraint( start_jnt, PositionCt[0], mo = True )
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

    #
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
    microBodyCts = []
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
        if curve_up:
            # up vector control
            name = 'micro_up_' + pad_number( i = i )
            microUpCt = place.Controller2( name, j, True, 'loc_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
            upCts.append( microUpCt[4] )
            place.translationLock( microUpCt[2] )
            place.rotationLock( microUpCt[2] )
            place.translationYLock( microUpCt[2] )
            # cmds.connectAttr( PositionCt[2] + '.' + m_up_attr, microUpCt[0] + '.visibility', force = True )
            cmds.parent( microUpCt[0], m_up_grp )
            # stick to path
            mo_path_up = cmds.pathAnimation( microUpCt[0], name = microUpCt[2] + '_motionPath' , c = curve_up, startU = 0.0, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
            cmds.setAttr( mo_path_up + '.fractionMode', True )  # turn off parametric, sets start/end range 0-1
            ac.deleteAnim2( mo_path_up, attrs = ['uValue'] )

        # control for body
        fk_start = 50
        color = 'brown'
        if i >= fk_start:
            color = 'yellow'
        name = 'micro_body_' + pad_number( i = i )
        microBodyCt = place.Controller2( name, skin_jnts[i], False, 'facetZup_ctrl', 3.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        cmds.parent( microBodyCt[0], m_body_grp )
        cmds.parentConstraint( microBodyCt[4], skin_jnts[i], mo = True )
        cmds.parentConstraint( j, microBodyCt[0], mo = True )
        microBodyCts.append( microBodyCt )
        # fk down chain
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
        place.addAttribute( microCt[2], 'position', 0.0, 100.0, True, 'float' )  # max is number of points in curve
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
        subNew_tail_add = cmds.createNode( 'addDoubleLinear', name = ( microCt[2] + '_subtractNew_Add' ) )
        cmds.setAttr( subNew_tail_add + '.input1', 100.0 )
        cmds.connectAttr( lengthNeg_tail_mlt + '.output', subNew_tail_add + '.input2' )

        # NEED TO CONNECT TRAVEL TO TAIL LOCK

        #
        blnd_root_typs = cmds.shadingNode( 'blendColors', name = ( microCt[2] + '_rootTypeBlend' ), asUtility = True )
        cmds.connectAttr( subNew_tail_add + '.output', blnd_root_typs + '.color2R' )  # # change
        cmds.connectAttr( position_ctrl[3] + '.' + root_attr, blnd_root_typs + '.blender', force = True )
        #
        cmds.connectAttr( dbl_path + '.output', blnd_root_typs + '.color1R' )  # into blend before normalizing
        cmds.connectAttr( blnd_root_typs + '.outputR', mlt_path + '.input1', force = True )
        cmds.connectAttr( mlt_path + '.output', mo_path + '.uValue', force = True )

        cmds.connectAttr( mlt_path + '.output', mo_path_up + '.uValue', force = True )
        # finish up vector travel and aim constraint for snake
        # connect travel, matching joint below
        if i > 0:
            # cmds.connectAttr( mlt_path + '.output', mo_path_up + '.uValue', force = True )
            # add aim constraint
            cmds.aimConstraint( attach_jnts[i - 1], microCt[1], mo = True, wuo = microUpCt[4], wut = 'object', aim = [0, 0, 1], u = [0, 1, 0] )

        #
        i += 1

    '''
    # fk up chain, doesnt work. gonna use spline
    i = 0
    for ct  in microBodyCts:
        if i < 10:
            place.parentSwitch( 
                name = ct[2],
                Ct = ct[2],
                CtGp = ct[1],
                TopGp = ct[0],
                ObjOff = attach_jnts[i],
                ObjOn = microBodyCts[i + 1][4],
                Pos = False,
                Ornt = False,
                Prnt = True,
                OPT = True,
                attr = 'fk',
                w = 0.0 )
        i += 1
        '''

    # guides
    # guides_grp = guide_many_to_many( PositionCt[2], attach_jnts, upCts, 5 )
    guides_grp = guide_many_to_many( prefix = 'many', vis_object = PositionCt[2], many1 = attach_jnts, many2 = upCts, offset = 0.0, every_nth = 5 )
    '''
    tail lock working, need to add travel offset
    '''


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


def neck_joint_chain( start_jnt = '', end_jnt = '', reroot = False ):
    '''
    duplicate skin joint chain and reverse hierarchy
    '''
    pass


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
            cmds.rename( jnt, 'path_jnt_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) )
            i -= 1
    else:
        # num = len( names )
        i = 0
        for jnt in names:
            cmds.rename( jnt, 'path_jnt_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) )
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
    cmds.parent( attr_Ct[0], CONTROLS() )
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
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_E_IK_curve_scale.input2Z' )


def ____SKIN():
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
    return ['cor:snake_body_Low_geo', 'cor:snake_tongue_low_geo']


def high_geo():
    return ['cor:snake_body_geo', 'cor:snake_tongue_geo']

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
