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


def ____PREBUILD():
    pass


def prebuild():
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


def ____FACE():
    pass


def tongue():
    # tongue
    # TongueCt = place.Controller2( 'Tongue', 'jaw_jnt', False, 'splineStart_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    tongueMicro = faceRig.snakeTongue( 'tongue', 0.50 )


def fangs():
    # fangs
    fangL = place.Controller( 'fang_L', 'fang_jnt_L', orient = True, shape = 'squareXup_ctrl', size = 2, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    fangLCt = fangL.createController()
    fangR = place.Controller( 'fang_R', 'fang_jnt_R', orient = True, shape = 'squareXup_ctrl', size = 2, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    fangRCt = fangR.createController()
    cmds.parentConstraint( fangLCt[4], 'fang_jnt_L', mo = True )
    cmds.parentConstraint( fangRCt[4], 'fang_jnt_R', mo = True )
    cmds.parentConstraint( 'head_jnt', fangLCt[0], mo = True )
    cmds.parentConstraint( 'head_jnt', fangRCt[0], mo = True )
    place.cleanUp( fangLCt[0], Ctrl = True )
    place.cleanUp( fangRCt[0], Ctrl = True )


def jaw():
    JawCt = place.Controller2( 'jaw', 'jaw_jnt', True, 'neckMaster_ctrl', 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( JawCt[4], 'jaw_jnt', mo = True )
    cmds.parentConstraint( 'head_jnt', JawCt[0], mo = True )
    place.cleanUp( JawCt[0], Ctrl = True )
    JawTipCt = place.Controller2( 'jawTip', 'jawTip_jnt', True, 'squareZup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( 'jaw_jnt', JawTipCt[0], mo = True )
    place.cleanUp( JawTipCt[0], Ctrl = True )
    JawLCt = place.Controller2( 'jawTip_L', 'jawTip_jnt_L', True, 'squareZup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.parentConstraint( JawTipCt[4], JawLCt[0], mo = True )
    place.cleanUp( JawLCt[0], Ctrl = True )
    JawRCt = place.Controller2( 'jawTip_R', 'jawTip_jnt_R', True, 'squareZup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.parentConstraint( JawTipCt[4], JawRCt[0], mo = True )
    place.cleanUp( JawRCt[0], Ctrl = True )
    apg.aimRig( name = 'jaw_L', obj = 'jaw_jnt_L', aimObj = JawLCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, 1], up = [0, 1, 0] )
    apg.aimRig( name = 'jaw_R', obj = 'jaw_jnt_R', aimObj = JawRCt[4], upParent = JawCt[4], distance = 5, aim = [0, 0, -1], up = [0, -1, 0] )


def ____BODY():
    pass


def head():
    '''
    
    '''
    X = 1
    #
    head_Ct = place.Controller2( 'head', 'head_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parentConstraint( head_Ct[4], 'head_jnt', mo = True )
    cmds.parentConstraint( 'neck_01_jnt', head_Ct[0], mo = True )
    place.cleanUp( head_Ct[0], Ctrl = True )
    #
    place.parentSwitch( head_Ct[2], head_Ct[2], head_Ct[1], head_Ct[0], 'master_Grp', 'neck_01_jnt', False, True, False, True, 'Neck', 0.0 )
    #
    tongue()
    fangs()
    jaw()


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
    returnsNothing_FixIt = ump.path2( length = 120, layers = layers, X = 18.0, prebuild = False, ctrl_shape = 'diamond_ctrl', reverse = reverse )
    #
    position_ctrl = place.Controller2( 'Position', 'neck_01_jnt', True, 'splineStart_ctrl', 20, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    #
    pathIk( curve = 'path_layer_05', position_ctrl = position_ctrl, tail_as_root = tail_as_root )
    #
    misc.optEnum( position_ctrl[2], attr = 'path', enum = 'CONTROL' )
    cmds.setAttr( master + '.path', cb = False )
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
    - if head needs to be locked the joints need to be duplicated and reversed,
    by default tail is locked
    - assumed path and controls are already created, objects should be fed into this function, (they arent), they are hard coded
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
    Vect = 'VectorVis'
    # fix parent, should be startTw
    PositionCt = None
    if not position_ctrl:
        PositionCt = place.Controller2( 'Position', start_jnt, True, 'splineStart_ctrl', 20, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    else:
        PositionCt = position_ctrl
    #
    # place.addAttribute( PositionCt[2], CtVis, 0, 1, True, 'float' )
    # cmds.setAttr( PositionCt[2] + '.' + CtVis, k = False, cb = True )
    place.addAttribute( PositionCt[2], Vect, 0, 1, True, 'float' )
    cmds.setAttr( PositionCt[2] + '.' + Vect, k = False, cb = True )
    cmds.xform( PositionCt[0], r = True, t = ( 0, path_ctrl_height, 0 ) )
    cmds.parentConstraint( start_jnt, PositionCt[0], mo = True )
    place.setChannels( PositionCt[2], [False, False], [False, False], [False, False], [True, True, False] )
    place.cleanUp( PositionCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    # create twist controls
    # cmds.select( Ctrls[0] )
    cmds.select( 'layer_05_point_32' )
    startTwParent = place.null( 'startTwist_Grp' )
    startTw = place.loc( 'startTwist' )
    cmds.parent( startTw[0], startTwParent )
    cmds.setAttr( startTw[0] + '.localScaleX', 30 )
    cmds.setAttr( startTw[0] + '.localScaleY', 30 )
    cmds.setAttr( startTw[0] + '.localScaleZ', 30 )
    cmds.parentConstraint( 'master_Grp', startTwParent, mo = True )
    cmds.connectAttr( PositionCt[2] + '.' + Vect, startTw[0] + '.visibility' )
    place.setChannels( startTw[0], [True, False], [False, True], [False, False], [True, True, False] )
    place.cleanUp( startTwParent, Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    # cmds.select( Ctrls[42] )
    cmds.select( 'layer_05_point_00' )
    endTwParent = place.null( 'endTwist_Grp' )
    endTw = place.loc( 'endTwist' )
    cmds.parent( endTw, endTwParent )
    cmds.setAttr( endTw[0] + '.localScaleX', 30 )
    cmds.setAttr( endTw[0] + '.localScaleY', 30 )
    cmds.setAttr( endTw[0] + '.localScaleZ', 30 )
    cmds.parentConstraint( 'master_Grp', endTwParent, mo = True )
    cmds.connectAttr( PositionCt[2] + '.' + Vect, endTw[0] + '.visibility' )
    place.setChannels( endTw[0], [True, False], [False, True], [False, False], [True, True, False] )
    place.cleanUp( endTwParent, Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    # Create Ik Handle
    ikhandle = cmds.ikHandle( sj = path_jnts[0], ee = path_jnts[-1], sol = 'ikSplineSolver', ccv = False, c = curve, pcv = False )[0]
    cmds.setAttr( ikhandle + '.dTwistControlEnable', 1 )
    # cmds.setAttr( ikhandle + '.dWorldUpType', 4 )
    cmds.setAttr( ikhandle + '.dWorldUpType', 7 )
    cmds.setAttr( ikhandle + '.dForwardAxis', 4 )
    cmds.setAttr( ikhandle + '.dWorldUpAxis', 0 )
    cmds.connectAttr( endTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrix' )  # likely wont use this
    cmds.connectAttr( startTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrixEnd' )  # likely wont use this
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
    '''
    # add twist controls that slide along curve connected to ramp 'position' attribute
    Twst00Ct = place.Controller2( 'Twist_00', start_jnt, True, 'squareZup_ctrl', 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    place.addAttribute( Twst00Ct[2], 'position', 0.0, 31.0, True, 'float' )  # max is number of points in curve
    cmds.setAttr( Twst00Ct[2] + '.position', 31 )
    mo_path = cmds.pathAnimation( Twst00Ct[0], name = Twst00Ct[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
    ac.deleteAnim2( mo_path, attrs = ['uValue'] )
    #
    twst00_rvrs = cmds.shadingNode( 'reverse', n = Twst00Ct[2] + '_rvrs', asUtility = True )
    cmds.connectAttr( Twst00Ct[2] + '.rotateZ', twst00_rvrs + '.inputZ', force = True )
    cmds.connectAttr( twst00_rvrs + '.outputZ', ramp + '.colorEntryList[1].colorR', force = True )
    # multiply ramp position to match travel along curve
    twst00_mlt = cmds.shadingNode( 'multDoubleLinear', n = Twst00Ct[2] + '_mlt', asUtility = True )
    cmds.setAttr( twst00_mlt + '.input2', 1 / 31 )
    cmds.connectAttr( Twst00Ct[2] + '.position', twst00_mlt + '.input1', force = True )
    cmds.connectAttr( twst00_mlt + '.output', ramp + '.colorEntryList[1].position', force = True )

    cmds.connectAttr( Twst00Ct[2] + '.position', mo_path + '.uValue', force = True )

    Twst00Ct = place.Controller2( 'Twist_01', start_jnt, True, 'squareZup_ctrl', 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    place.addAttribute( Twst00Ct[2], 'position', 0.0, 31.0, True, 'float' )  # max is number of points in curve
    cmds.setAttr( Twst00Ct[2] + '.position', 31 - ( 7.5 * 1 ) )
    mo_path = cmds.pathAnimation( Twst00Ct[0], name = Twst00Ct[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
    ac.deleteAnim2( mo_path, attrs = ['uValue'] )
    #
    twst00_rvrs = cmds.shadingNode( 'reverse', n = Twst00Ct[2] + '_rvrs', asUtility = True )
    cmds.connectAttr( Twst00Ct[2] + '.rotateZ', twst00_rvrs + '.inputZ', force = True )
    cmds.connectAttr( twst00_rvrs + '.outputZ', ramp + '.colorEntryList[2].colorR', force = True )
    # multiply ramp position to match travel along curve
    twst00_mlt = cmds.shadingNode( 'multDoubleLinear', n = Twst00Ct[2] + '_mlt', asUtility = True )
    cmds.setAttr( twst00_mlt + '.input2', 1 / 31 )
    cmds.connectAttr( Twst00Ct[2] + '.position', twst00_mlt + '.input1', force = True )
    cmds.connectAttr( twst00_mlt + '.output', ramp + '.colorEntryList[2].position', force = True )

    cmds.connectAttr( Twst00Ct[2] + '.position', mo_path + '.uValue', force = True )

    Twst00Ct = place.Controller2( 'Twist_02', start_jnt, True, 'squareZup_ctrl', 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    place.addAttribute( Twst00Ct[2], 'position', 0.0, 31.0, True, 'float' )  # max is number of points in curve
    cmds.setAttr( Twst00Ct[2] + '.position', 31 - ( 7.5 * 2 ) )
    mo_path = cmds.pathAnimation( Twst00Ct[0], name = Twst00Ct[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
    ac.deleteAnim2( mo_path, attrs = ['uValue'] )
    #
    twst00_rvrs = cmds.shadingNode( 'reverse', n = Twst00Ct[2] + '_rvrs', asUtility = True )
    cmds.connectAttr( Twst00Ct[2] + '.rotateZ', twst00_rvrs + '.inputZ', force = True )
    cmds.connectAttr( twst00_rvrs + '.outputZ', ramp + '.colorEntryList[3].colorR', force = True )
    # multiply ramp position to match travel along curve
    twst00_mlt = cmds.shadingNode( 'multDoubleLinear', n = Twst00Ct[2] + '_mlt', asUtility = True )
    cmds.setAttr( twst00_mlt + '.input2', 1 / 31 )
    cmds.connectAttr( Twst00Ct[2] + '.position', twst00_mlt + '.input1', force = True )
    cmds.connectAttr( twst00_mlt + '.output', ramp + '.colorEntryList[3].position', force = True )

    cmds.connectAttr( Twst00Ct[2] + '.position', mo_path + '.uValue', force = True )

    Twst00Ct = place.Controller2( 'Twist_03', start_jnt, True, 'squareZup_ctrl', 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    place.addAttribute( Twst00Ct[2], 'position', 0.0, 31.0, True, 'float' )  # max is number of points in curve
    cmds.setAttr( Twst00Ct[2] + '.position', 31 - ( 7.5 * 3 ) )
    mo_path = cmds.pathAnimation( Twst00Ct[0], name = Twst00Ct[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
    ac.deleteAnim2( mo_path, attrs = ['uValue'] )
    #
    twst00_rvrs = cmds.shadingNode( 'reverse', n = Twst00Ct[2] + '_rvrs', asUtility = True )
    cmds.connectAttr( Twst00Ct[2] + '.rotateZ', twst00_rvrs + '.inputZ', force = True )
    cmds.connectAttr( twst00_rvrs + '.outputZ', ramp + '.colorEntryList[4].colorR', force = True )
    # multiply ramp position to match travel along curve
    twst00_mlt = cmds.shadingNode( 'multDoubleLinear', n = Twst00Ct[2] + '_mlt', asUtility = True )
    cmds.setAttr( twst00_mlt + '.input2', 1 / 31 )
    cmds.connectAttr( Twst00Ct[2] + '.position', twst00_mlt + '.input1', force = True )
    cmds.connectAttr( twst00_mlt + '.output', ramp + '.colorEntryList[4].position', force = True )

    cmds.connectAttr( Twst00Ct[2] + '.position', mo_path + '.uValue', force = True )
    '''
    #
    # end up vector ramp
    #

    # Hide and Parent ikhandle
    cmds.setAttr( ikhandle + '.lodVisibility', 0 )
    place.cleanUp( ikhandle, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # create and connect attribute for IK Slide on 'end' control

    attr = 'Travel'
    place.addAttribute( PositionCt[2], attr, 0.0, 200.0, True, 'float' )  # max is number of points on curve 31 * 10 = 310 # multiplier, MD node

    mlt = cmds.createNode( 'multiplyDivide', n = 'Travel_mlt' )
    cmds.connectAttr( PositionCt[2] + '.' + attr, mlt + '.input1X' )
    cmds.setAttr( mlt + '.input2X', 0.1 )
    cmds.connectAttr( mlt + '.outputX', ikhandle + '.offset' )

    #
    cmds.select( ikhandle, ramp )
    mm.eval( 'dgdirty;' )


def pathTwist( amount = 4, ramp = '', curve = '' ):
    '''
    
    '''
    #
    twist_c = []
    mlts_n = []
    rvrs_n = []
    ramp_int = 1
    cvs = cmds.getAttr( curve + '.cp', s = 1 )
    print( 'cvs: ', cvs )
    spans = cmds.getAttr( curve + '.spans' )
    print( 'spans: ', spans )
    distribute = spans / ( amount + 1 )
    distribute = 1 / ( amount + 1 )
    print( 'distribute: ', distribute )
    i = 0
    #
    while i <= amount:
        #
        TwstCt = place.Controller2( 'Twist_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ), curve, True, 'squareZup_ctrl', 16, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result  # use curve node for initial placement
        twist_c.append( TwstCt )
        place.addAttribute( TwstCt[2], 'position', 0.0, spans, True, 'float' )  # max is number of points in curve
        v = spans - ( distribute * ramp_int )
        v = distribute * ramp_int
        print( 'set position: ', v )
        cmds.setAttr( TwstCt[2] + '.position', v )
        mo_path = cmds.pathAnimation( TwstCt[0], name = TwstCt[2] + '_motionPath' , c = curve, startU = 0.5, follow = True, wut = 'object', wuo = 'up_Grp', fm = False, fa = 'z', ua = 'y' )
        cmds.setAttr( mo_path + '.fractionMode', True )
        ac.deleteAnim2( mo_path, attrs = ['uValue'] )
        #
        rvrs = cmds.shadingNode( 'reverse', n = TwstCt[2] + '_rvrs', asUtility = True )
        rvrs_n.append( rvrs )
        cmds.connectAttr( TwstCt[2] + '.rotateZ', rvrs + '.inputZ', force = True )
        cmds.connectAttr( rvrs + '.outputZ', ramp + '.colorEntryList[' + str( ramp_int ) + '].colorR', force = True )
        # multiply ramp position to match travel along curve
        mlt = cmds.shadingNode( 'multDoubleLinear', n = TwstCt[2] + '_mlt', asUtility = True )
        mlts_n.append( mlt )
        # cmds.setAttr( mlt + '.input2', 1 / spans )
        cmds.setAttr( mlt + '.input2', 1 )
        cmds.connectAttr( TwstCt[2] + '.position', mlt + '.input1', force = True )
        cmds.connectAttr( mlt + '.output', ramp + '.colorEntryList[' + str( ramp_int ) + '].position', force = True )

        cmds.connectAttr( TwstCt[2] + '.position', mo_path + '.uValue', force = True )

        ramp_int += 1
        i += 1


def dynamicJiggle():
    '''
    
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


def path_joint_chain( start_jnt = '', end_jnt = '' ):
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

    # rename
    cmds.select( dup[0], hi = True )
    names = cmds.ls( sl = True )
    num = len( names )
    i = num - 1
    for jnt in names:
        cmds.rename( jnt, 'path_jnt_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) )
        i -= 1

    # reroot chain and fix joint orients
    path_jnts = cmds.ls( sl = True )
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
    path_joints_to_ground( path_jnts = path_jnts )
    print( 'grounded' )
    print( path_jnts )
    # return

    # constrain
    skin_jnts_to_path_jnts( skin_jnts = skin_jnts, path_jnts = path_jnts )
    print( 'constrained' )
    print( path_jnts )
    # return

    place.cleanUp( path_jnts[-1], SknJnts = True )
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


def path_joints_to_ground( path_jnts = [] ):
    '''
    unparent all joints and set tranlsateY to 0.0
    reparent
    '''
    path_jnts.reverse()
    cmds.parent( path_jnts, w = True )  # world is parent
    for j in path_jnts:
        cmds.setAttr( j + '.translateY', 0.0 )
    for j in range( len( path_jnts ) ):
        if j < len( path_jnts ) - 1:
            cmds.parent( path_jnts[j + 1], path_jnts[j] )
    path_jnts.reverse()  # for some reason i need to reverse the change as it effects the list outside this function


def skin_jnts_to_path_jnts( skin_jnts = [], path_jnts = [] ):
    '''
    
    '''
    # path_jnts.reverse()
    for i in range( len( skin_jnts ) ):
        cmds.parentConstraint( path_jnts[i], skin_jnts[i], mo = True )
        # print( i )
    # path_jnts.reverse()


def ____UTIL():
    pass


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
    attr_Ct = place.Controller2( name, start_jnt, True, 'splineStart_ctrl', X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'brown' ).result
    cmds.parent( attr_Ct[0], CONTROLS() )
    cmds.parentConstraint( splineStrt, attr_Ct[0], mo = True )
    # lock translation
    place.rotationLock( attr_Ct[2], True )
    place.translationLock( attr_Ct[2], True )

    # SPINE
    splineName = name
    splineSize = X * 1
    splineDistance = X * 4

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
    return ['cor:snake_anim_mesh']


def high_geo():
    return ['statue_man_model:Statue_man_High']

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
