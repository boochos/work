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
    #
    cmds.parentConstraint( 'master_Grp', 'root_jnt', mo = True )


def ____FACE():
    pass


def tongue():
    # tongue
    TongueCt = place.Controller2( 'Tongue', 'jaw_jnt', False, 'splineStart_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
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
    JawCt = place.Controller2( 'jaw', 'jaw_jnt', True, 'squareZup_ctrl', 1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
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
    place.cleanUp( head_Ct[0], Ctrl = True )
    #
    tongue()
    fangs()
    jaw()


def body_spline():
    '''
    
    '''
    #
    master = 'master'
    layers = 6
    ump.path2( length = 120, layers = layers, X = 12.0, prebuild = False, ctrl_shape = 'diamond_ctrl', reverse = True )
    #
    position_ctrl = place.Controller2( 'Position', 'neck_01_jnt', True, 'splineStart_ctrl', 20, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    #
    pathIk( curve = 'path_layer_05', position_ctrl = position_ctrl )
    #
    misc.optEnum( position_ctrl[2], attr = 'path', enum = 'CONTROL' )
    cmds.setAttr( master + '.path', cb = False )
    i = 0
    while i <= layers - 1:
        place.hijackAttrs( master, position_ctrl[2], 'ctrlLayer' + str( i ), 'ctrlLayer' + str( i ), set = False, default = None, force = True )
        cmds.setAttr( master + '.ctrlLayer' + str( i ), cb = False )
        i += 1

    #
    return
    pth = 'P:\\SYMD\\assets\\chr\\coralSnake\\rig\\maya\\scenes\\coralSnake_path_v001.ma'
    cmds.file( pth, reference = True, namespace = 'pth', force = True )

    '''
    #
    start_Ct = place.Controller2( 'neck', 'neck_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( start_Ct[0], Ctrl = True )
    end_Ct = place.Controller2( 'tail', 'tail_11_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( end_Ct[0], Ctrl = True )
    #
    vhc.spline( name = 'snake', start_jnt = 'neck_01_jnt', end_jnt = 'tail_11_jnt', splinePrnt = 'master_Grp', splineStrt = start_Ct[4], splineEnd = end_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1 )
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


def pathIk( curve = '', path_ctrl_height = 0, position_ctrl = None ):
    '''
    if head needs to be locked the joints need to be duplicated and reversed,
    by default tail is locked
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

    # Create Path Position Controller
    CtVis = 'SpineCt_Vis'
    Vect = 'VectorVis'
    # fix parent, should be startTw
    EndCt = None
    if not position_ctrl:
        EndCt = place.Controller2( 'Position', newSpine, True, 'splineStart_ctrl', 20, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    else:
        EndCt = position_ctrl
    #
    # place.addAttribute( EndCt[2], CtVis, 0, 1, True, 'float' )
    # cmds.setAttr( EndCt[2] + '.' + CtVis, k = False, cb = True )
    place.addAttribute( EndCt[2], Vect, 0, 1, True, 'float' )
    cmds.setAttr( EndCt[2] + '.' + Vect, k = False, cb = True )
    cmds.xform( EndCt[0], r = True, t = ( 0, path_ctrl_height, 0 ) )
    cmds.parentConstraint( newSpine, EndCt[0], mo = True )
    place.setChannels( EndCt[2], [False, False], [False, False], [False, False], [True, True, False] )
    place.cleanUp( EndCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

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
    cmds.connectAttr( EndCt[2] + '.' + Vect, startTw[0] + '.visibility' )
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
    cmds.connectAttr( EndCt[2] + '.' + Vect, endTw[0] + '.visibility' )
    place.setChannels( endTw[0], [True, False], [False, True], [False, False], [True, True, False] )
    place.cleanUp( endTwParent, Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    # Create Ik Handle
    ikhandle = cmds.ikHandle( sj = startJnt, ee = endJnt, sol = 'ikSplineSolver', ccv = False, c = curve, pcv = False )[0]
    cmds.setAttr( ikhandle + '.dTwistControlEnable', 1 )
    cmds.setAttr( ikhandle + '.dWorldUpType', 4 )
    cmds.setAttr( ikhandle + '.dForwardAxis', 4 )
    cmds.setAttr( ikhandle + '.dWorldUpAxis', 0 )
    cmds.connectAttr( endTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrix' )
    cmds.connectAttr( startTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrixEnd' )

    # Hide and Parent ikhandle
    cmds.setAttr( ikhandle + '.visibility', 0 )
    place.cleanUp( ikhandle, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # create and connect attribute for IK Slide on 'end' control------------------------------------------------------------------------------------------------------------------------------------------------------------------

    attr = 'ikPos'
    place.addAttribute( EndCt[2], attr, 0.0, 200.0, True, 'float' )  # max is number of points on curve 31 * 10 = 310 # multiplier, MD node

    MD = cmds.createNode( 'multiplyDivide', n = 'Speed_MD' )
    cmds.connectAttr( EndCt[2] + '.' + attr, MD + '.input1X' )
    cmds.setAttr( MD + '.input2X', 0.1 )
    cmds.connectAttr( MD + '.outputX', ikhandle + '.offset' )


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
