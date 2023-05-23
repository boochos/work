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


def ____PREBUILD():
    pass


def prebuild():
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 5 )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]


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


def body_spline():
    '''
    
    '''
    #
    X = 1
    #
    start_Ct = place.Controller2( 'neck', 'neck_01_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( start_Ct[0], Ctrl = True )
    end_Ct = place.Controller2( 'tail', 'tail_11_jnt', True, 'squareZup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    place.cleanUp( end_Ct[0], Ctrl = True )
    #
    vhc.spline( name = 'snake', start_jnt = 'neck_01_jnt', end_jnt = 'tail_11_jnt', splinePrnt = 'master_Grp', splineStrt = start_Ct[4], splineEnd = end_Ct[4], startSkpR = False, endSkpR = False, color = 'yellow', X = 1 )


def body_splineIk():
    '''
    
    '''
    pass


def body_splineFk():
    '''
    
    '''
    pass


def ____PATH():
    pass


def path():
    '''
    
    '''
    ump.path2( length = 116, layers = 6, X = 12.0 )


def pathIk( *args ):
    '''
    if head needs to be locked the joints need to be duplicated and reversed,
    by default tail is locked
    '''
    newSpine = 'cor:neck_01_jnt'

    # Create Path Position Controller
    CtVis = 'SpineCt_Vis'
    Vect = 'VectorVis'
    # fix parent, should be startTw
    EndCt = place.Controller2( 'Position', newSpine, True, 'loc_ctrl', 20, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    # cnt = place.Controller( 'Position', newSpine[0], orient = False, shape = 'loc_ctrl', size = 20, color = 12, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    # EndCt = cnt.createController()
    place.addAttribute( EndCt[2], CtVis, 0, 1, True, 'float' )
    cmds.setAttr( EndCt[2] + '.' + CtVis, k = False, cb = True )
    place.addAttribute( EndCt[2], Vect, 0, 1, True, 'float' )
    cmds.setAttr( EndCt[2] + '.' + Vect, k = False, cb = True )
    cmds.xform( EndCt[0], r = True, t = ( 0, 60, 0 ) )
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
    ikhandle = cmds.ikHandle( sj = 'cor:neck_01_jnt', ee = 'cor:tail_11_jnt', sol = 'ikSplineSolver', ccv = False, c = 'path_layer_05', pcv = False )[0]
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
