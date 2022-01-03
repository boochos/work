import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
atl = web.mod( "atom_path_lib" )
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
anm = web.mod( "anim_lib" )
ss = web.mod( "selectionSet_lib" )
# atl.path(segments=5, size=0.05, length=10)


def apple():
    '''
    
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 10 * X )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo = 'Apple_geo'
    geo_grp = 'apple_grp'
    # cmds.group( geo, n = geo_grp )

    #
    cmds.parent( geo_grp, GEO[0] )
    # cmds.setAttr( geo_grp + '.translateY', -0.082 )
    # cmds.setAttr( geo_grp + '.translateZ', -9 )
    # cmds.setAttr( geo_grp + '.rotateX', 0.735 )
    # cmds.setAttr( geo_grp + '.rotateY', -2.965 )

    # lock geo - [lock, keyable], [visible, lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [False, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    distance = 4.0

    # puck #
    Puck = 'apple'
    puck = place.Controller( Puck, MasterCt[0], False, 'diamond_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    PuckCt = puck.createController()
    place.setRotOrder( PuckCt[0], 2, True )
    cmds.parent( PuckCt[0], CONTROLS )
    # cmds.setAttr( PuckCt[0] + '.translateY', distance )
    cmds.parentConstraint( MasterCt[4], PuckCt[0], mo = True )
    cmds.parentConstraint( PuckCt[4], geo_grp, mo = True )

    # puck up #
    Puck_u = 'apple_up'
    puck_u = place.Controller( Puck_u, MasterCt[0], False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Puck_u_Ct = puck_u.createController()
    place.setRotOrder( Puck_u_Ct[0], 2, True )
    cmds.parent( Puck_u_Ct[0], CONTROLS )
    cmds.setAttr( Puck_u_Ct[0] + '.translateZ', distance * 3 )
    cmds.parentConstraint( MasterCt[4], Puck_u_Ct[0], mo = True )

    # puck tip #
    Puck_t = 'apple_tip'
    puck_t = place.Controller( Puck_t, MasterCt[0], False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Puck_t_Ct = puck_t.createController()
    place.setRotOrder( Puck_t_Ct[0], 2, True )
    cmds.parent( Puck_t_Ct[0], CONTROLS )
    cmds.setAttr( Puck_t_Ct[0] + '.translateY', distance )
    cmds.parentConstraint( MasterCt[4], Puck_t_Ct[0], mo = True )
    cmds.aimConstraint( Puck_t_Ct[4], PuckCt[2], wut = 'object', wuo = Puck_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( PuckCt[2], [False, True], [True, False], [True, False], [True, False, False] )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 20.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    #
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___GEO', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___GEO' + s )


def sleigh():
    '''
    fix
    '''
    X = 10
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 2, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 30 * X )
    # [u'___PROP___', u'___CONTROLS', u'___SKIN_JOINTS', [u'___GEO', u'___UTILITY', u'___ACCESSORY', u'___BODY'], u'___WORLD_SPACE', (u'master_TopGrp', u'master_CtGrp', u'master', u'master_Offset', u'master_Grp')]
    print( PreBuild )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    nm = 'sleigh'
    #
    # group everything else under group
    sel_set_member = 'M_A_I_N___D_E_R_O_R_M_E_R'
    cmds.select( sel_set_member )
    ss.selectSet()
    everything = cmds.ls( sl = True )
    geo_grp = nm + '_everything_grp'
    cmds.group( everything, n = geo_grp )

    #
    cmds.parent( geo_grp, GEO[0] )

    # constrain santa to sleigh
    santa = 'snt:cam:Santa_APose_402_LP'
    loc = place.loc( 'santa_attach' )[0]
    cmds.select( ['pasted__polySurface91.map[90]', 'pasted__polySurface91.map[421]', loc] )
    import maya.internal.common.cmd.base; maya.internal.common.cmd.base.executeCommand( 'uvpin.cmd_create' )
    cmds.parentConstraint( loc, santa, mo = True )
    cmds.parent( loc, WORLD_SPACE )
    cmds.parent( santa, WORLD_SPACE )
    cmds.setAttr( loc + '.visibility', 0 )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( loc, [True, False], [True, False], [True, False], [True, False, False] )

    # controls for path cvs
    curve = 'ANIMATION_PATH_MOVE_THIS'
    cmds.setAttr( curve + 'Shape.overrideEnabled', 1 )
    cmds.setAttr( curve + 'Shape.overrideDisplayType', 1 )
    cmds.parent( curve, WORLD_SPACE )
    clstr = place.clstrOnCV( curve, nm )
    #
    i = 0
    offst = -200
    for c in clstr:
        # path #
        Path = 'path_' + str( i )
        path = place.Controller( Path, c, False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
        PathCt = path.createController()
        place.setRotOrder( PathCt[0], 2, True )
        cmds.parent( PathCt[0], CONTROLS )
        cmds.parent( c, WORLD_SPACE )
        cmds.setAttr( PathCt[0] + '.translateY', -1.267 )
        cmds.setAttr( PathCt[0] + '.translateZ', offst * i )
        cmds.parentConstraint( MasterCt[4], PathCt[0], mo = True )
        cmds.parentConstraint( PathCt[4], c, mo = False )
        i = i + 1

    # create path travel attr
    mpath = 'motionPath1'
    mattr = 'uValue'
    place.hijackAttrs( mpath, MasterCt[2], mattr, 'travel', set = True, default = 0.0, force = True )

    # some stuff off
    stf = [
    'turbulenceField3',
    'gravityField1',
    'turbulenceField2'
    ]
    for item in stf:
        cmds.setAttr( item + '.visibility', 0 )
