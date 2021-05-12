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
# atl.path(segments=5, size=0.05, length=10)


def chain( dupx = 20 ):
    '''
    
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 150 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'chain_grp'
    # print GEO
    cmds.parent( geo_grp, GEO[0] )

    # initial geo list
    chn = [
    'chainLink_geo1',
    'chainLink_geo2',
    'chainLink_geo3',
    'chainLink_geo4'
    ]

    #
    links = []
    odd = True
    strt = 2.772
    shift = 5.539
    i = 0

    # position geo
    for c in chn:
        links.append( c )
        cmds.setAttr( c + '.rotateX', 90 )
        cmds.setAttr( c + '.translateZ', ( shift * i ) + strt )
        if odd:
            cmds.setAttr( c + '.rotateZ', 90 )
            odd = False
        else:
            odd = True
        i = i + 1

    # duplicate geo
    # dupx = 10
    cmds.select( chn )
    i = 1
    while i <= dupx:
        dup = cmds.duplicate( chn )
        for d in dup:
            links.append( d )
        cmds.move( 0, 0, shift * len( chn ) * i, dup, r = True )
        i = i + 1

    # place joints
    jnts = place.jointChain( suffix = 'chain_jnt', pad = 3, length = shift, amount = len( links ), radius = 0.4 )

    # bind geo
    i = 0
    for i in range( len( jnts ) - 1 ):
        # print i
        cmds.bindSkin( links[i], jnts[i], tsb = True )
        i = i + 1

    #
    cmds.parent( jnts[0], SKIN_JOINTS )

    #
    # root #
    Root = 'root'
    root = place.Controller( Root, jnts[0], False, 'facetYup_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True )
    RootCt = root.createController()
    place.setRotOrder( RootCt[0], 2, True )
    cmds.parent( RootCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], RootCt[0], mo = True )

    # tip #
    Tip = 'tip'
    tip = place.Controller( Tip, jnts[-1], False, 'facetYup_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True )
    TipCt = tip.createController()
    place.setRotOrder( TipCt[0], 2, True )
    cmds.parent( TipCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], TipCt[0], mo = True )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    #
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # spline
    chainSplines( jnts[0], jnts[-1] )
    chainKink()

    return jnts[0], jnts[-1]


def chainSplines( root_jnt = '', tip_jnt = '', X = 2 ):
    '''\n
    Build splines\n
    '''
    face = None
    check = cmds.checkBox( 'atom_rat_faceCheck', query = True, v = True )
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)

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

    # SPINE
    spineName = 'chain'
    spineSize = X * 1
    spineDistance = X * 4
    spineFalloff = 0
    spinePrnt = 'master_Grp'
    spineStrt = 'root_Grp'
    spineEnd = 'tip_Grp'
    spineAttr = 'master'
    spineRoot = root_jnt

    spine = [root_jnt, tip_jnt]
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 0 )
    cmds.setAttr( spineAttr + '.ClstrVis', 0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )


def chainKink( master = 'master_Grp', middle = 'chain_Clstr_M43_Ctrl', root = 'root_CtGrp', tip = 'tip_CtGrp', CONTROLS = '___CONTROLS', X = 2, up_distance = 100 ):
    '''
    places controller on mid position and constrains mid position to controller, 
    aims both ends at controller with 2 up vectors above mid position
    
    '''
    # mid #
    Mid = 'mid'
    mid = place.Controller( Mid, middle, False, 'loc_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True )
    MidCt = mid.createController()
    place.setRotOrder( MidCt[0], 2, True )
    cmds.parent( MidCt[0], CONTROLS )
    cmds.parentConstraint( master, MidCt[0], mo = True )
    cmds.parentConstraint( MidCt[4], middle, mo = True )

    # up root #
    Upr = 'up_root'
    upr = place.Controller( Upr, root, False, 'loc_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True )
    UprCt = upr.createController()
    place.setRotOrder( UprCt[0], 2, True )
    cmds.parent( UprCt[0], CONTROLS )
    cmds.setAttr( UprCt[0] + '.translateY', up_distance )
    cmds.parentConstraint( master, UprCt[0], mo = True )
    cmds.aimConstraint( MidCt[4], root, wut = 'object', wuo = UprCt[4], aim = [0, 0, 1], u = [0, 1, 0], mo = False )

    # up tip #
    Upt = 'up_t'
    upt = place.Controller( Upt, tip, False, 'loc_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True )
    UptCt = upt.createController()
    place.setRotOrder( UptCt[0], 2, True )
    cmds.parent( UptCt[0], CONTROLS )
    cmds.setAttr( UptCt[0] + '.translateY', up_distance )
    cmds.parentConstraint( master, UptCt[0], mo = True )
    cmds.aimConstraint( MidCt[4], tip, wut = 'object', wuo = UptCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = False )

    cmds.setAttr( middle + '.scaleZ', 0.2 )


def amulet():
    '''
    
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 10 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'iceCreamAmulet_grp'
    geo = [
    'iceCreamAmulet_grp|UW_ICECREAM_high',
    'iceCreamAmulet_grp|UW_ICECREAM_low'
    ]

    #
    cmds.parent( geo_grp, GEO[0] )
    cmds.setAttr( geo_grp + '.rotateX', -3.426 )

    # lock geo - [lock, keyable]
    place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'amulet'
    amulet = place.Controller( Amulet, geo_grp, False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.setAttr( AmuletCt[0] + '.translateY', 0.75 )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # amulet up #
    Amulet_u = 'amulet_up'
    amulet_u = place.Controller( Amulet_u, geo_grp, False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Amulet_u_Ct = amulet_u.createController()
    place.setRotOrder( Amulet_u_Ct[0], 2, True )
    cmds.parent( Amulet_u_Ct[0], CONTROLS )
    cmds.setAttr( Amulet_u_Ct[0] + '.translateZ', 9.829 / 2 )
    cmds.parentConstraint( MasterCt[4], Amulet_u_Ct[0], mo = True )

    # amulet tip #
    Amulet_t = 'amulet_tip'
    amulet_t = place.Controller( Amulet_t, geo_grp, False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Amulet_t_Ct = amulet_t.createController()
    place.setRotOrder( Amulet_t_Ct[0], 2, True )
    cmds.parent( Amulet_t_Ct[0], CONTROLS )
    cmds.setAttr( Amulet_t_Ct[0] + '.translateY', 9.829 )
    cmds.parentConstraint( MasterCt[4], Amulet_t_Ct[0], mo = True )
    cmds.aimConstraint( Amulet_t_Ct[4], AmuletCt[2], wut = 'object', wuo = Amulet_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( AmuletCt[2], [False, True], [True, False], [True, False], [True, False, False] )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    # misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    #
    rel = cmds.listRelatives( '___CONTROLS' )
    for g in rel:
        if not 'master' in g:
            misc.scaleUnlock( g, sx = True, sy = True, sz = True )
            for s in scl:
                cmds.connectAttr( mstr + '.' + uni, g + s )
    misc.scaleUnlock( geo_grp, sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, geo_grp + s )


def lid_1():
    '''
    
    '''
    X = 20
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 5 * X )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'coffind1_grp'
    geo = [
    'coffin1_offset_grp|Coffin1_Hi',
    'coffin1_offset_grp|Coffin1_low'
    ]

    #
    cmds.parent( geo_grp, GEO[0] )
    # cmds.setAttr( geo_grp + '.translateY', -0.082 )
    cmds.setAttr( geo_grp + '.translateZ', -9 )
    # cmds.setAttr( geo_grp + '.rotateX', 0.735 )
    # cmds.setAttr( geo_grp + '.rotateY', -2.965 )

    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( geo[0], [True, False], [True, False], [True, False], [False, False, False] )
    place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # lid_2 #
    Lid_2 = 'lid_2'
    lid_2 = place.Controller( Lid_2, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2Ct = lid_2.createController()
    place.setRotOrder( Lid_2Ct[0], 2, True )
    cmds.parent( Lid_2Ct[0], CONTROLS )
    # cmds.setAttr( Lid_2Ct[0] + '.translateY', 0.75 )
    cmds.parentConstraint( MasterCt[4], Lid_2Ct[0], mo = True )
    cmds.parentConstraint( Lid_2Ct[4], geo_grp, mo = True )

    # lid_2 up #
    Lid_2_u = 'lid_2_up'
    lid_2_u = place.Controller( Lid_2_u, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_u_Ct = lid_2_u.createController()
    place.setRotOrder( Lid_2_u_Ct[0], 2, True )
    cmds.parent( Lid_2_u_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_u_Ct[0] + '.translateZ', 189 / 2 )
    cmds.parentConstraint( MasterCt[4], Lid_2_u_Ct[0], mo = True )

    # lid_2 tip #
    Lid_2_t = 'lid_2_tip'
    lid_2_t = place.Controller( Lid_2_t, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_t_Ct = lid_2_t.createController()
    place.setRotOrder( Lid_2_t_Ct[0], 2, True )
    cmds.parent( Lid_2_t_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_t_Ct[0] + '.translateY', 189 )
    cmds.parentConstraint( MasterCt[4], Lid_2_t_Ct[0], mo = True )
    cmds.aimConstraint( Lid_2_t_Ct[4], Lid_2Ct[2], wut = 'object', wuo = Lid_2_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( Lid_2Ct[2], [False, True], [True, False], [True, False], [True, False, False] )

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


def lid_2():
    '''
    
    '''
    X = 20
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 7 * X )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'UW_coffinlid2_grp'
    geo = [
    'UW_coffinlid2_geo_HI',
    'UW_coffinlid2_geo_low'
    ]

    #
    cmds.parent( geo_grp, GEO[0] )
    cmds.setAttr( geo_grp + '.translateX', -1.789 )
    cmds.setAttr( geo_grp + '.translateZ', -7.5 )
    cmds.setAttr( geo_grp + '.rotateY', 1.98 )

    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( geo[0], [True, False], [True, False], [True, False], [False, False, False] )
    place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # lid_2 #
    Lid_2 = 'lid_2'
    lid_2 = place.Controller( Lid_2, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2Ct = lid_2.createController()
    place.setRotOrder( Lid_2Ct[0], 2, True )
    cmds.parent( Lid_2Ct[0], CONTROLS )
    # cmds.setAttr( Lid_2Ct[0] + '.translateY', 0.75 )
    cmds.parentConstraint( MasterCt[4], Lid_2Ct[0], mo = True )
    cmds.parentConstraint( Lid_2Ct[4], geo_grp, mo = True )

    # lid_2 up #
    Lid_2_u = 'lid_2_up'
    lid_2_u = place.Controller( Lid_2_u, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_u_Ct = lid_2_u.createController()
    place.setRotOrder( Lid_2_u_Ct[0], 2, True )
    cmds.parent( Lid_2_u_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_u_Ct[0] + '.translateZ', 189 / 2 )
    cmds.parentConstraint( MasterCt[4], Lid_2_u_Ct[0], mo = True )

    # lid_2 tip #
    Lid_2_t = 'lid_2_tip'
    lid_2_t = place.Controller( Lid_2_t, MasterCt[0], False, 'loc_ctrl', X * 4, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_t_Ct = lid_2_t.createController()
    place.setRotOrder( Lid_2_t_Ct[0], 2, True )
    cmds.parent( Lid_2_t_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_t_Ct[0] + '.translateY', 189 )
    cmds.parentConstraint( MasterCt[4], Lid_2_t_Ct[0], mo = True )
    cmds.aimConstraint( Lid_2_t_Ct[4], Lid_2Ct[2], wut = 'object', wuo = Lid_2_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( Lid_2Ct[2], [False, True], [True, False], [True, False], [True, False, False] )

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


def amulet_string( segments = 9, joints_in_seg = 9 ):
    '''
    # segments = 13  # choose odd number
    # joints_in_seg = 5  # choose odd number
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 33 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    # print GEO
    # return None
    #
    geo_grp = 'Amulet_grp'
    geo_root = [
    'AMULET_GOLDEN1',
    'AMULET_BODY',
    'AMULET_BLUE',
    'AMULET_RED',
    'AMULET_CYAN',
    ]
    geo_hinge_l = [     'DETAIL_L', 'AMULET_CYLINDER_L']
    geo_hinge_r = [     'DETAIL_R', 'AMULET_CYLINDER_R']

    geo_string = 'AMULET_CHAIN'
    #
    cmds.parent( geo_grp, GEO[0] )
    # model v004
    '''
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -8.661 )
    cmds.setAttr( geo_grp + '.translateZ', 1.623 )'''
    # model v012
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -0.213 )
    cmds.setAttr( geo_grp + '.translateZ', -6.84 )

    #
    # cmds.deltaMush( 'AMULET_CHAIN', smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    '''
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )'''
    #
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # lock geo - [lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'amulet'
    amulet = place.Controller( Amulet, MasterCt[4], False, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    # cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # root
    cmds.select( cl = True )
    rt_jnt = place.joint( 0, 'stringRoot_jnt', pad = 2, rpQuery = True )[0]
    cmds.parentConstraint( AmuletCt[4], rt_jnt, mo = True )
    cmds.parent( rt_jnt, SKIN_JOINTS )
    # bind root geo
    for geo in geo_root:
        # cmds.bindSkin( 'am', 'stringRoot_jnt' ) # doesnt work cuz gay, trying mel
        cmds.select( [geo, rt_jnt] )
        mel.eval( 'SmoothBindSkin;' )

    # l/R hinge
    cmds.select( cl = True )
    hingeL_jnt = place.joint( 0, 'string_jnt_L', pad = 2, rpQuery = True )[0]
    cmds.setAttr( hingeL_jnt + '.translateX', 5.645 )
    cmds.setAttr( hingeL_jnt + '.translateY', 0.379 )
    cmds.setAttr( hingeL_jnt + '.translateZ', 4.918 )
    cmds.setAttr( hingeL_jnt + '.rotateY', -3.683 )
    cmds.parent( hingeL_jnt, rt_jnt )
    hingeR_jnt = cmds.mirrorJoint( mirrorYZ = True, mirrorBehavior = True, searchReplace = ( '_L', '_R' ) )[0]
    # bind l
    for geo in geo_hinge_l:
        cmds.select( [geo, hingeL_jnt] )
        print cmds.ls( sl = 1 )
        mel.eval( 'SmoothBindSkin -tsb;' )
    # bind r
    for geo in geo_hinge_r:
        cmds.select( [geo, hingeR_jnt] )
        mel.eval( 'SmoothBindSkin -tsb;' )

    # return None
    # hinge_L #
    Hinge_L = 'hinge_L'
    hinge_L = place.Controller( Hinge_L, hingeL_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_LCt = hinge_L.createController()
    place.setRotOrder( Hinge_LCt[0], 2, True )
    cmds.parent( Hinge_LCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_LCt[0], mo = True )
    cmds.parentConstraint( Hinge_LCt[4], hingeL_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_LCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_LCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # hinge_R #
    Hinge_R = 'hinge_R'
    hinge_R = place.Controller( Hinge_R, hingeR_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_RCt = hinge_R.createController()
    place.setRotOrder( Hinge_RCt[0], 2, True )
    cmds.parent( Hinge_RCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_RCt[0], mo = True )
    cmds.parentConstraint( Hinge_RCt[4], hingeR_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_RCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_RCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # stringA #
    StringA = 'stringA'
    stringA = place.Controller( StringA, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    StringACt = stringA.createController()
    cmds.setAttr( StringACt[0] + '.translateX', 4.168 )
    cmds.setAttr( StringACt[0] + '.translateY', 0.32 )
    cmds.setAttr( StringACt[0] + '.translateZ', 6.6 )
    place.setRotOrder( StringACt[0], 2, True )
    cmds.parent( StringACt[0], CONTROLS )
    cmds.parentConstraint( Hinge_LCt[4], StringACt[0], mo = True )
    place.setChannels( StringACt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( StringACt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # string_Tip #
    String_Tip = 'string_Tip'
    string_Tip = place.Controller( String_Tip, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    String_TipCt = string_Tip.createController()
    cmds.setAttr( String_TipCt[0] + '.translateX', -4.168 )
    cmds.setAttr( String_TipCt[0] + '.translateY', 0.32 )
    cmds.setAttr( String_TipCt[0] + '.translateZ', 6.6 )
    place.setRotOrder( String_TipCt[0], 2, True )
    cmds.parent( String_TipCt[0], CONTROLS )
    cmds.parentConstraint( Hinge_RCt[4], String_TipCt[0], mo = True )
    place.setChannels( String_TipCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( String_TipCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # STRING CHAIN
    # string variables
    gap = 8.336  # gap between hinges, correct segment to this length
    full_length = 111.44  # string length
    # math
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    # correct length for connection to base
    over_length = seg_length - gap  # will need to shorten segment
    reduce_length = over_length / lengths_in_seg  # each joint needs to be this much shorter
    new_length = length - reduce_length
    # chain
    suffix = 'string'
    pad = 2
    jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    cmds.parent( jnts[0], SKIN_JOINTS )

    # TUBE
    # temp joint for more geo length
    cmds.select( jnts[-1] )
    tmp_jnt = place.joint( 0, 'tmp_jnt', pad = 2, rpQuery = True, radius = 0.4 )[0]
    cmds.parent( tmp_jnt, jnts[-1] )
    cmds.setAttr( tmp_jnt + '.translateZ', length )
    jnts.append( tmp_jnt )
    crv = place.curve( 'crv', jnts, d = 2 )
    # clean up temp jnt
    cmds.delete( tmp_jnt )
    jnts.pop( -1 )
    # tube radius
    crcl = place.circle( 'radius', obj = jnts[0], radius = 0.36, degree = 5 )[0]
    cmds.select( [crv, crcl] )
    tube = cmds.extrude( ch = True, rn = False, po = 0, et = 2, ucp = 1, fpt = 1, upn = 1, rotation = 0, scale = 1, rsp = 1 )[0]
    cmds.reverseSurface( tube, rpo = True )
    tube_poly = cmds.nurbsToPoly( tube, format = 3, uType = 3, vType = 3, cht = 0.2, chr = 0.1 )[0]
    tube_poly = cmds.rename( tube_poly, suffix + '_Deformer' )
    cmds.polyNormal( tube_poly, nm = 0 )
    cmds.delete( tube_poly, constructionHistory = True )
    cmds.delete( tube, crv, crcl )
    cmds.parent( tube_poly, jnts[0] )
    cmds.setAttr( jnts[0] + '.translateX', 4.168 )
    cmds.setAttr( jnts[0] + '.translateY', 0.32 )
    cmds.setAttr( jnts[0] + '.translateZ', 6.6 )
    cmds.setAttr( tube_poly + '.translateZ', ( length * 0.7 ) * -1 )  # move so default weights distribute properly, loop cant lay directly on joint
    cmds.parent( tube_poly, world = True )  # unparent
    cmds.select( jnts[0], hi = True )
    cmds.select( tube_poly, add = True )
    # python or mel binSkin didnt work, created too many skinClusters
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    # wrap
    dfrmr = createWrap( tube_poly, geo_string )
    # clean up
    cmds.parent( tube_poly, GEO[1] )
    cmds.parent( tube_poly + 'Base', GEO[1] )

    # return None
    # correct joint length, for bend and connect to other side
    for jnt in jnts:
        if '_01' not in jnt:
            pass
            cmds.setAttr( jnt + '.translateZ', new_length )

    # bend into place, connect tip to opposite end of amulet
    bend_seg = int( ( segments / 2 ) + 0.5 )  # double joint, first joint in segment
    bend_letter = chr( ord( 'a' ) + bend_seg ).upper()  # number to letter
    bend_letter_next = chr( ord( 'a' ) + bend_seg + 1 ).upper()  # number to letter
    jnt_num = str( ( '%0' + str( pad ) + 'd' ) % ( 1 ) )  # pad jnt number
    cmds.setAttr( suffix + bend_letter + '_jnt_' + jnt_num + '.rotateY', -90 )
    cmds.setAttr( suffix + bend_letter_next + '_jnt_' + jnt_num + '.rotateY', -90 )

    # place segment controls
    seg = []
    # seg.append( jnts[0] )
    cmds.select( jnts[0], hi = True )
    sel = cmds.ls( sl = True )
    for jnt in sel:
        if '_01' in jnt and jnt != sel[0]:
            seg.append( jnt )
    # print seg
    # return None

    # fk chain
    suffix_fk = suffix + 'Macro'
    fkjnts = place.jointChain( suffix = suffix_fk, pad = pad, length = new_length * lengths_in_seg, amount = ( segments - 1 ) / 2, radius = 0.4, dbl = 0 )
    cmds.parent( fkjnts[0], SKIN_JOINTS )
    # should match string location, but center, no tx
    cmds.setAttr( fkjnts[0] + '.translateY', 0.32 )
    cmds.setAttr( fkjnts[0] + '.translateZ', 6.6 )
    # fk controls
    i = 0
    for joint in fkjnts:
        # print i
        if i == 0:
            parent = AmuletCt[4]
        else:
            parent = fkjnts[i - 1]
            # print 'parent', parent
        # Upper = joint[:7]
        Upper = suffix_fk + '_' + str( i )
        # print Upper
        upperMaster = place.Controller( Upper, joint, False, 'facetZup_ctrl', X * 3.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
        UpperCt = upperMaster.createController()
        #
        cmds.parentConstraint( UpperCt[4], joint )
        cmds.parent( UpperCt[0], CONTROLS )
        cmds.select( UpperCt[0] )
        UpperCt_TopGrp1 = place.insert( 'null', 1, Upper + '_TopGrp1' )[0][0]
        UpperCt_CtGrp1 = place.insert( 'null', 1, Upper + '_CtGrp1' )[0][0]
        place.setRotOrder( UpperCt_TopGrp1, 2, True )
        place.setRotOrder( UpperCt[2], 3, False )
        #
        place.parentSwitch( Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '', 1.0 )
        place.parentSwitch( Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '', 1.0 )
        #
        cmds.parentConstraint( parent, UpperCt_TopGrp1, mo = True )
        place.setChannels( UpperCt[0], [False, False], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[1], [False, True], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[2], [False, True], [False, True], [True, False], [True, False, False] )
        place.setChannels( UpperCt[3], [False, True], [False, True], [True, False], [False, False, False] )
        cmds.setAttr( UpperCt[3] + '.visibility', cb = False )
        place.setChannels( UpperCt[4], [True, False], [False, True], [True, False], [True, False, False] )
        #
        i = i + 1

    # string segment controls #
    i = 0
    iMax_letter = 'A'
    al = len( seg )
    for joint in seg:
        if cmds.objExists( joint ):
            if i == 0:
                parent = fkjnts[i + 1]
                # parent = 'stringA_Grp'
            else:
                if i <= 3:
                    parent = fkjnts[i + 1]
                else:
                    parent = fkjnts[ al - i]
                # parent = joint[:6] + chr( ord( 'a' ) + i ).upper() + '_Grp'
            #
            Upper = joint[:7]
            # print Upper
            upperMaster = place.Controller( Upper, joint, False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
            UpperCt = upperMaster.createController()
            # place.addText( UpperCt[2], t = joint[5], c = 17, rotOffset = [0, 0, 0], posOffset = [-1.5, 8, 0] )
            cmds.parent( UpperCt[0], CONTROLS )
            cmds.select( UpperCt[0] )
            UpperCt_TopGrp1 = place.insert( 'null', 1, Upper + '_TopGrp1' )[0][0]
            UpperCt_CtGrp1 = place.insert( 'null', 1, Upper + '_CtGrp1' )[0][0]
            place.setRotOrder( UpperCt_TopGrp1, 2, True )
            place.setRotOrder( UpperCt[2], 3, False )
            # switch these for fk chain down middle
            place.parentSwitch( Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '', 1.0 )
            place.parentSwitch( Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '', 1.0 )
            #
            cmds.parentConstraint( parent, UpperCt_TopGrp1, mo = True )
            place.setChannels( UpperCt[0], [False, False], [False, False], [True, False], [True, False, False] )
            place.setChannels( UpperCt[1], [False, True], [False, False], [True, False], [True, False, False] )
            place.setChannels( UpperCt[2], [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( UpperCt[3], [False, True], [False, True], [True, False], [False, False, False] )
            cmds.setAttr( UpperCt[3] + '.visibility', cb = False )
            place.setChannels( UpperCt[4], [True, False], [False, True], [True, False], [True, False, False] )
            #
            i = i + 1
            iMax_letter = chr( ord( 'a' ) + i ).lower()
            # print iMax_letter

    # return None

    # necklace base hinge aim vectors
    iMax = ord( iMax_letter ) - 96
    end = str( ( '%0' + str( pad ) + 'd' ) % ( joints_in_seg ) )
    # print iMax
    amuletSplines( iMax, end = end )


def amuletSplines( iMax = 1, end = 01 ):
    '''\n
    Build splines for amulet\n
    iMax = number of iterations
    end = last joint number in spline, in proper format pad, for name building
    '''
    face = None
    # X = cmds.floatField( 'atom_srig_conScale', query = True, value = True )
    X = 0.25  # cmds.floatField( 'atom_srig_conScale', query = True, value = True )

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

    def chain( prefix = 'upper', iMax = 4, endPrefix = 'neck', EOrient = 0 ):
        '''\n

        '''
        i = 0
        while i < iMax:
            letter = chr( ord( 'a' ) + i ).upper()
            letterPrev = chr( ord( 'a' ) + ( i - 1 ) ).upper()
            letterNext = chr( ord( 'a' ) + ( i + 1 ) ).upper()
            splineName = prefix + letter
            splineSize = X * 1
            splineDistance = X * 16.0
            splineFalloff = 0
            if i == 0:
                # splinePrnt = 'A_Grp'
                # splineStrt = 'A_Grp'
                splinePrnt = prefix + 'A_Grp'
                splineStrt = prefix + 'A_Grp'
                newPrefix = prefix[0].upper() + prefix[1:]
                # splineAttr = 'A_' + newPrefix
                splineAttr = prefix + 'A'
            else:
                splinePrnt = prefix + letter + '_Grp'
                splineStrt = prefix + letterPrev + '_jnt_' + end
                splineAttr = prefix + letter + '_Offset'
            if i == iMax - 1:
                splineEnd = endPrefix + '_Grp'
            else:
                splineEnd = prefix + letterNext + '_Grp'
            # splineRoot = 'root_jnt'
            spline = [prefix + letter + '_jnt_01', prefix + letter + '_jnt_' + end]
            # build spline
            SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
            cmds.select( spline )
            stage.splineStage( 4 )
            # assemble
            OptAttr( splineAttr, prefix + letter )
            # insert group above _IK_CtrlGrp # fixes mid ik orientation and position
            '''
            splinePrnt_s = place.null2( splineName + '_PARENT_S', splineName + '_IK_CtrlGrp', orient = True )[0]
            cmds.parent( splinePrnt_s, splineName + '_SplnCtrlGrp' )
            splinePrnt_e = place.null2( splineName + '_PARENT_E', splineName + '_IK_CtrlGrp', orient = True )[0]
            cmds.parent( splinePrnt_e, splineName + '_SplnCtrlGrp' )
            p = cmds.parentConstraint( splinePrnt, splinePrnt_s, mo = True )[0]
            cmds.setAttr( p + '.interpType', 0 )
            p = cmds.parentConstraint( splineEnd, splinePrnt_e, mo = True )[0]
            cmds.setAttr( p + '.interpType', 0 )
            p = cmds.parentConstraint( splinePrnt_s, splineName + '_IK_CtrlGrp', mo = True )[0]
            p = cmds.parentConstraint( splinePrnt_e, splineName + '_IK_CtrlGrp', mo = True )[0]
            cmds.setAttr( p + '.interpType', 0 )'''
            #
            cmds.parentConstraint( splinePrnt, splineName + '_IK_CtrlGrp', mo = True )  # no(unstable for string): above constraints are taking over
            cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True )
            cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True )
            # # cmds.parentConstraint(splineName + '_S_IK_Jnt', splineRoot, mo=True)
            # set options
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Vis', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Root', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Stretch', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrVis', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrMidIkBlend', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrVis', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidIkBlend', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5 )
            cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
            cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', EOrient )
            place.hijackCustomAttrs( splineName + '_IK_CtrlGrp', splineAttr )

            # connect multi/div node of spline curves(S/E) to Control group scale
            misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
            cmds.connectAttr( '___CONTROLS.scaleZ', prefix + letter + '_S_IK_curve_scale.input2Z' )
            cmds.connectAttr( '___CONTROLS.scaleZ', prefix + letter + '_E_IK_curve_scale.input2Z' )

            i = i + 1

    chain( prefix = 'string', iMax = iMax, endPrefix = 'string_Tip', EOrient = 1 )
    # chain(prefix='lower', iMax=18, endPrefix='lowerTip', EOrient=0)


def leafs():
    '''
    
    '''
    X = 5
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 7 * X )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'Leaf_maple'
    geo_grps = [
    'Leaf_maple5',
    'Leaf_maple4',
    'Leaf_maple3',
    'Leaf_maple2',
    'Leaf_maple1'
    ]
    # cmds.select( geo_grps )
    cmds.group( geo_grps, n = geo_grp )

    geo = [
    'Leaf_maple1_leaf',
    'Leaf_maple1_stem',
    'Leaf_maple2_leaf',
    'Leaf_maple2_stem',
    'Leaf_maple3_stem',
    'Leaf_maple3_leaf',
    'Leaf_maple4_leaf',
    'Leaf_maple4_stem',
    'Leaf_maple5_leaf',
    'Leaf_maple5_stem'
    ]

    #
    cmds.parent( geo_grp, GEO[0] )
    # cmds.setAttr( geo_grp + '.translateX', -1.789 )
    # cmds.setAttr( geo_grp + '.translateZ', -7.5 )
    # cmds.setAttr( geo_grp + '.rotateY', 1.98 )

    # bend
    cmds.select( geo )
    bendRy = cmds.nonLinear( type = 'bend', name = 'bendRy', curvature = 0.0 )
    cmds.select( geo )
    bendRx = cmds.nonLinear( type = 'bend', name = 'bendRx', curvature = 0.0 )
    # bendY deformer rotations
    cmds.setAttr( bendRy[1] + '.rotateX', -90 )  # [1] handle # [0] deformer
    cmds.setAttr( bendRy[1] + '.rotateY', -90 )
    # bendX deformer rotations
    cmds.setAttr( bendRx[1] + '.rotateY', -90 )
    cmds.parent( bendRy[1], geo_grp )
    cmds.parent( bendRx[1], geo_grp )

    # return None
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( bendRy[1], [False, False], [False, False], [True, False], [False, False, False] )
    place.setChannels( bendRx[1], [False, False], [False, False], [True, False], [False, False, False] )

    # leaf #
    Leaf = 'leaf'
    leaf = place.Controller( Leaf, MasterCt[0], False, 'loc_ctrl', X * 1, 17, 8, 1, ( 0, 0, 1 ), True, True )
    LeafCt = leaf.createController()
    place.setRotOrder( LeafCt[0], 2, True )
    cmds.parent( LeafCt[0], CONTROLS )
    cmds.setAttr( LeafCt[0] + '.translateY', -8 )
    cmds.parentConstraint( MasterCt[4], LeafCt[0], mo = True )
    cmds.parentConstraint( LeafCt[4], geo_grp, mo = True )
    # cmds.parentConstraint( LeafCt[4], bendRy[1], mo = True )
    # cmds.parentConstraint( LeafCt[4], bendRx[1], mo = True )
    # return None

    # leafBendY #
    LeafBendY = 'leafBendY'
    leafBendY = place.Controller( LeafBendY, MasterCt[0], False, 'diamond_ctrl', X * 1, 17, 8, 1, ( 0, 0, 1 ), True, True )
    LeafBendYCt = leafBendY.createController()
    place.setRotOrder( LeafBendYCt[0], 2, True )
    cmds.parent( LeafBendYCt[0], CONTROLS )
    cmds.parentConstraint( LeafCt[4], LeafBendYCt[0], mo = True )
    cmds.parentConstraint( LeafBendYCt[4], bendRy[1], mo = True )
    place.hijackAttrs( bendRy[0] + 'HandleShape', LeafBendYCt[2], 'curvature', 'curvature', set = False, default = 0, force = True )

    # leafBendX #
    LeafBendX = 'leafBendX'
    leafBendX = place.Controller( LeafBendX, MasterCt[0], False, 'diamond_ctrl', X * 0.9, 17, 8, 1, ( 0, 0, 1 ), True, True )
    LeafBendXCt = leafBendX.createController()
    place.setRotOrder( LeafBendXCt[0], 2, True )
    cmds.parent( LeafBendXCt[0], CONTROLS )
    cmds.parentConstraint( LeafCt[4], LeafBendXCt[0], mo = True )
    cmds.parentConstraint( LeafBendXCt[4], bendRx[1], mo = True )
    place.hijackAttrs( bendRx[0] + 'HandleShape', LeafBendXCt[2], 'curvature', 'curvature', set = False, default = 0, force = True )

    # leaf up #
    Leaf_u = 'leaf_up'
    leaf_u = place.Controller( Leaf_u, MasterCt[0], False, 'loc_ctrl', X * 1, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Leaf_u_Ct = leaf_u.createController()
    place.setRotOrder( Leaf_u_Ct[0], 2, True )
    cmds.parent( Leaf_u_Ct[0], CONTROLS )
    cmds.setAttr( Leaf_u_Ct[0] + '.translateZ', 8 / 2 )
    cmds.parentConstraint( MasterCt[4], Leaf_u_Ct[0], mo = True )

    # leaf tip #
    Leaf_t = 'leaf_tip'
    leaf_t = place.Controller( Leaf_t, MasterCt[0], False, 'loc_ctrl', X * 1, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Leaf_t_Ct = leaf_t.createController()
    place.setRotOrder( Leaf_t_Ct[0], 2, True )
    cmds.parent( Leaf_t_Ct[0], CONTROLS )
    cmds.setAttr( Leaf_t_Ct[0] + '.translateY', 8 )
    cmds.parentConstraint( MasterCt[4], Leaf_t_Ct[0], mo = True )
    cmds.aimConstraint( Leaf_t_Ct[4], LeafCt[2], wut = 'object', wuo = Leaf_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( LeafCt[2], [False, True], [True, False], [True, False], [True, False, False] )

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


def createWrap( *args, **kwargs ):
    print args
    influence = args[0]
    surface = args[1]

    shapes = cmds.listRelatives( influence, shapes = True )
    influenceShape = shapes[0]

    shapes = cmds.listRelatives( surface, shapes = True )
    surfaceShape = shapes[0]

    weightThreshold = kwargs.get( 'weightThreshold', 0.0 )
    maxDistance = kwargs.get( 'maxDistance', 1.0 )
    exclusiveBind = kwargs.get( 'exclusiveBind', False )
    autoWeightThreshold = kwargs.get( 'autoWeightThreshold', True )
    falloffMode = kwargs.get( 'falloffMode', 0 )

    wrapData = cmds.deformer( surface, type = 'wrap' )
    wrapNode = wrapData[0]

    cmds.setAttr( wrapNode + '.weightThreshold', weightThreshold )
    cmds.setAttr( wrapNode + '.maxDistance', maxDistance )
    cmds.setAttr( wrapNode + '.exclusiveBind', exclusiveBind )
    cmds.setAttr( wrapNode + '.autoWeightThreshold', autoWeightThreshold )
    cmds.setAttr( wrapNode + '.falloffMode', falloffMode )

    cmds.connectAttr( surface + '.worldMatrix[0]', wrapNode + '.geomMatrix' )

    duplicateData = cmds.duplicate( influence, name = influence + 'Base' )
    base = duplicateData[0]
    shapes = cmds.listRelatives( base, shapes = True )
    baseShape = shapes[0]
    cmds.hide( base )

    if not cmds.attributeQuery( 'dropoff', n = influence, exists = True ):
        cmds.addAttr( influence, sn = 'dr', ln = 'dropoff', dv = 4.0, min = 0.0, max = 20.0 )
        cmds.setAttr( influence + '.dr', k = True )

    if cmds.nodeType( influenceShape ) == 'mesh':
        if not cmds.attributeQuery( 'smoothness', n = influence, exists = True ):
            cmds.addAttr( influence, sn = 'smt', ln = 'smoothness', dv = 0.0, min = 0.0 )
            cmds.setAttr( influence + '.smt', k = True )

        if not cmds.attributeQuery( 'inflType', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'ift', ln = 'inflType', dv = 2, min = 1, max = 2 )

        cmds.connectAttr( influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.worldMesh', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.inflType', wrapNode + '.inflType[0]' )
        cmds.connectAttr( influence + '.smoothness', wrapNode + '.smoothness[0]' )

    if cmds.nodeType( influenceShape ) == 'nurbsCurve' or cmds.nodeType( influenceShape ) == 'nurbsSurface':
        if not cmds.attributeQuery( 'wrapSamples', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'wsm', ln = 'wrapSamples', dv = 10, min = 1 )
            cmds.setAttr( influence + '.wsm', k = True )

        cmds.connectAttr( influenceShape + '.ws', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.ws', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.wsm', wrapNode + '.nurbsSamples[0]' )

    cmds.connectAttr( influence + '.dropoff', wrapNode + '.dropoff[0]' )
    return wrapNode


def offsets2rig( reverse = False ):
    '''
    
    '''
    #
    offsets = [
    'amlt:stringB__OFFSET__',
    'amlt:stringC__OFFSET__',
    'amlt:stringD__OFFSET__',
    'amlt:stringE__OFFSET__',
    'amlt:stringF__OFFSET__',
    'amlt:stringG__OFFSET__',
    'amlt:stringH__OFFSET__',
    'amlt:stringI__OFFSET__'
    ]
    #
    actual = [
    'amlt:stringB',
    'amlt:stringC',
    'amlt:stringD',
    'amlt:stringE',
    'amlt:stringF',
    'amlt:stringG',
    'amlt:stringH',
    'amlt:stringI'
    ]
    #
    sel = cmds.ls( sl = True )
    cmds.select( cl = True )
    #
    i = 0
    for i in range( len( actual ) ):
        print actual[i]
        print offsets[i]
        if reverse:
            cmds.select( [actual[i], offsets[i]] )
        else:
            cmds.select( [offsets[i], actual[i]] )
        anm.matchObj()
    #
    cmds.select( sel )


def amuletABC():
    '''
    
    '''
    geo = [
    'amlt:AMULET_CHAIN',
    'amlt:AMULET_CYLINDER_L',
    'amlt:AMULET_BLUE',
    'amlt:DETAIL_R',
    'amlt:AMULET_GOLDEN1',
    'amlt:DETAIL_L',
    'amlt:AMULET_CYLINDER_R',
    'amlt:AMULET_CYAN',
    'amlt:AMULET_BODY',
    'amlt:AMULET_RED'
    ]
    '''
    if os.name == 'posix':
        project = m.workspace(rd=True, q=True).split('scenes/')[0]
    else:
        project = m.workspace(rd=True, q=True)
    dataDir = project+'data/'
    index = project[:-1].rindex('/')
    shotDir = project[:index]+'/'
    index = shotDir[:-1].rindex('/')
    #parse scene path to derrive scene name to be used in folder
    s_string = m.file(sn=True, q=True)
    s_splitString = s_string.split('/')
    i_splitStringLength = len(s_splitString)
    s_filename = s_splitString[(i_splitStringLength - 1)]
    #parse scene name to derrive name 
    s_splitFolder = s_filename.split('.')
    i_splitStringLengthFolder = len(s_splitFolder)
    s_foldername = s_splitFolder[(i_splitStringLengthFolder - 2)]
    #specify the plate name here
    plate = shotDir[index+1:-1]+ '_plate_01'
    imageDir = shotDir + 'images/' + plate + '/'
    imageList  = []
    #images = os.listdir(imageDir)
    #for i in images:
       # if 'plate' in i:
           # imageList.append(i)
   
    start = m.playbackOptions (ast=True, q=True)
    end = m.playbackOptions (aet=True, q=True)

    #set timeline to images
    m.playbackOptions( ast = start, aet = end, min = start, max = end)    

    #make geo caache directory
    geoCacheDir = dataDir + 'geoCache/'
    print geoCacheDir
    if not os.path.exists(os.path.join(dataDir, 'geoCache')):
        os.mkdir(geoCacheDir)
    #make cache version directory
    versions = os.listdir(geoCacheDir)
    if versions:
        nextVersion = s_foldername
        cacheVersionDir = geoCacheDir+s_foldername #modified this line to use scene name as folder name
        if not os.path.exists(cacheVersionDir):
            os.mkdir(cacheVersionDir)
    else:
        cacheVersionDir = geoCacheDir+s_foldername #modified this line to use scene name as folder name
        os.mkdir(cacheVersionDir)
    '''

    # AbcExport -j "-frameRange 1001 1085 -attr vrayUserString_id -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_CHAIN -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_CYLINDER_L -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_BLUE -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:DETAIL_R -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_GOLDEN1 -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:DETAIL_L -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_CYLINDER_R -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_CYAN -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_BODY -root |amlt:___PROP___|amlt:___GEO|amlt:Amulet_grp|amlt:AMULET_RED -file P:/uw/shots/amulet/UWRP_123_180/3d/maya/cache/alembic/uwrp_123_180_abc_v001.abc";
    # workspace -q -fre "alembicCache";


def leafABC():
    '''
    
    '''
    # os
    if os.name == 'posix':
        project = cmds.workspace( rd = True, q = True ).split( 'scenes/' )[0]
    else:
        project = cmds.workspace( rd = True, q = True )
    # cache poath
    dataDir = project + 'cache/'
    index = project[:-1].rindex( '/' )
    shotDir = project[:index] + '/'
    index = shotDir[:-1].rindex( '/' )
    # parse scene path to derive scene name to be used in folder
    s_string = cmds.file( sn = True, q = True )
    s_splitString = s_string.split( '/' )
    i_splitStringLength = len( s_splitString )
    s_filename = s_splitString[( i_splitStringLength - 1 )]
    # parse scene name to derive name
    s_splitFolder = s_filename.split( '.' )
    i_splitStringLengthFolder = len( s_splitFolder )
    s_foldername = s_splitFolder[( i_splitStringLengthFolder - 2 )]
    # specify the plate name here
    '''
    plate = shotDir[index + 1:-1] + '_plate_01'
    imageDir = shotDir + 'images/' + plate + '/'
    imageList = []
    # images = os.listdir(imageDir)
    # for i in images:
       # if 'plate' in i:
           # imageList.append(i)
    '''

    start = cmds.playbackOptions ( ast = True, q = True )
    end = cmds.playbackOptions ( aet = True, q = True )
    print( start )

    # set timeline to images
    # cmds.playbackOptions( ast = start, aet = end, min = start, max = end )

    # make geo caache directory
    geoCacheDir = dataDir + 'alembic/'
    print geoCacheDir
    if not os.path.exists( os.path.join( dataDir, 'alembic' ) ):
        os.mkdir( geoCacheDir )
    # make cache version directory
    versions = os.listdir( geoCacheDir )
    print versions
    if versions:
        nextVersion = s_foldername
        cacheVersionDir = geoCacheDir + s_foldername.replace( 'anim', 'abc' )  # modified this line to use scene name as folder name
        if not os.path.exists( cacheVersionDir ):
            os.mkdir( cacheVersionDir )
    else:
        cacheVersionDir = geoCacheDir + s_foldername.replace( 'anim', 'abc' )  # modified this line to use scene name as folder name
        os.mkdir( cacheVersionDir )
    print cacheVersionDir
    print os.path.join( cacheVersionDir, s_filename.replace( 'anim', 'abc' ) )
    # return None
    leafs = cmds.ls( sl = True )
    print leafs
    #
    i = 1
    for leaf in leafs:
        leaf_stripped = leaf.split( ':' )[1]
        print s_filename.replace( 'anim', 'abc__' + leaf_stripped + '_' )
        path = cacheVersionDir + '//' + s_filename.replace( 'anim', 'abc__' + leaf_stripped + '_' )
        path = path.replace( '.ma', '.abc' )
        if os.path.isfile( path ):
            path = path.replace( leaf_stripped, leaf_stripped + '_reuse' )
        print path
        m = 'AbcExport -j "-frameRange ' + str( int( start ) ) + ' ' + str( int( end ) ) + ' ' + '-attr vrayUserString_id -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root ' + leaf + ' -file ' + path + '";'
        print m
        mel.eval( m )
        i = i + 1


def amulet_string2( segments = 9, joints_in_seg = 9 ):
    '''
    # segments = 13  # choose odd number
    # joints_in_seg = 5  # choose odd number
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 33 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    # print GEO
    # return None
    #
    geo_grp = 'Amulet_grp'
    geo_root = [
    'AMULET_GOLDEN1',
    'AMULET_BODY',
    'AMULET_BLUE',
    'AMULET_RED',
    'AMULET_CYAN',
    ]
    geo_hinge_l = [     'DETAIL_L', 'AMULET_CYLINDER_L']
    geo_hinge_r = [     'DETAIL_R', 'AMULET_CYLINDER_R']

    geo_string = 'AMULET_CHAIN'
    #
    cmds.parent( geo_grp, GEO[0] )
    # model v004
    '''
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -8.661 )
    cmds.setAttr( geo_grp + '.translateZ', 1.623 )'''
    # model v012
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -0.213 )
    cmds.setAttr( geo_grp + '.translateZ', -6.84 )

    #
    # cmds.deltaMush( 'AMULET_CHAIN', smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    '''
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )'''
    #
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # lock geo - [lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'amulet'
    amulet = place.Controller( Amulet, MasterCt[4], False, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    # cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # root
    cmds.select( cl = True )
    rt_jnt = place.joint( 0, 'stringRoot_jnt', pad = 2, rpQuery = True )[0]
    cmds.parentConstraint( AmuletCt[4], rt_jnt, mo = True )
    cmds.parent( rt_jnt, SKIN_JOINTS )
    # bind root geo
    for geo in geo_root:
        # cmds.bindSkin( 'am', 'stringRoot_jnt' ) # doesnt work cuz gay, trying mel
        cmds.select( [geo, rt_jnt] )
        mel.eval( 'SmoothBindSkin;' )

    # l/R hinge
    cmds.select( cl = True )
    hingeL_jnt = place.joint( 0, 'string_jnt_L', pad = 2, rpQuery = True )[0]
    cmds.setAttr( hingeL_jnt + '.translateX', 5.645 )
    cmds.setAttr( hingeL_jnt + '.translateY', 0.379 )
    cmds.setAttr( hingeL_jnt + '.translateZ', 4.918 )
    cmds.setAttr( hingeL_jnt + '.rotateY', -3.683 )
    cmds.parent( hingeL_jnt, rt_jnt )
    hingeR_jnt = cmds.mirrorJoint( mirrorYZ = True, mirrorBehavior = True, searchReplace = ( '_L', '_R' ) )[0]
    # bind l
    for geo in geo_hinge_l:
        cmds.select( [geo, hingeL_jnt] )
        print cmds.ls( sl = 1 )
        mel.eval( 'SmoothBindSkin -tsb;' )
    # bind r
    for geo in geo_hinge_r:
        cmds.select( [geo, hingeR_jnt] )
        mel.eval( 'SmoothBindSkin -tsb;' )

    # return None
    # hinge_L #
    Hinge_L = 'hinge_L'
    hinge_L = place.Controller( Hinge_L, hingeL_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_LCt = hinge_L.createController()
    place.setRotOrder( Hinge_LCt[0], 2, True )
    cmds.parent( Hinge_LCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_LCt[0], mo = True )
    cmds.parentConstraint( Hinge_LCt[4], hingeL_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_LCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_LCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # hinge_R #
    Hinge_R = 'hinge_R'
    hinge_R = place.Controller( Hinge_R, hingeR_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_RCt = hinge_R.createController()
    place.setRotOrder( Hinge_RCt[0], 2, True )
    cmds.parent( Hinge_RCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_RCt[0], mo = True )
    cmds.parentConstraint( Hinge_RCt[4], hingeR_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_RCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_RCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # stringA #
    StringA = 'stringA'
    stringA = place.Controller( StringA, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    StringACt = stringA.createController()
    cmds.setAttr( StringACt[0] + '.translateX', 4.168 )
    cmds.setAttr( StringACt[0] + '.translateY', 0.32 )
    cmds.setAttr( StringACt[0] + '.translateZ', 6.6 )
    place.setRotOrder( StringACt[0], 2, True )
    cmds.parent( StringACt[0], CONTROLS )
    cmds.parentConstraint( Hinge_LCt[4], StringACt[0], mo = True )
    place.setChannels( StringACt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( StringACt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # string_Tip #
    String_Tip = 'string_Tip'
    string_Tip = place.Controller( String_Tip, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    String_TipCt = string_Tip.createController()
    cmds.setAttr( String_TipCt[0] + '.translateX', -4.168 )
    cmds.setAttr( String_TipCt[0] + '.translateY', 0.32 )
    cmds.setAttr( String_TipCt[0] + '.translateZ', 6.6 )
    place.setRotOrder( String_TipCt[0], 2, True )
    cmds.parent( String_TipCt[0], CONTROLS )
    cmds.parentConstraint( Hinge_RCt[4], String_TipCt[0], mo = True )
    place.setChannels( String_TipCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( String_TipCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # STRING CHAIN
    # string variables
    gap = 8.336  # gap between hinges, correct segment to this length
    full_length = 111.44  # string length
    # math
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    # correct length for connection to base
    over_length = seg_length - gap  # will need to shorten segment
    reduce_length = over_length / lengths_in_seg  # each joint needs to be this much shorter
    new_length = length - reduce_length
    # chain
    suffix = 'string'
    pad = 2
    # jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = '' )
    cmds.parent( jnts[0], SKIN_JOINTS )

    # TUBE
    # temp joint for more geo length
    cmds.select( jnts[-1] )
    tmp_jnt = place.joint( 0, 'tmp_jnt', pad = 2, rpQuery = True, radius = 0.4 )[0]
    cmds.parent( tmp_jnt, jnts[-1] )
    cmds.setAttr( tmp_jnt + '.translateZ', length )
    jnts.append( tmp_jnt )
    crv = place.curve( 'crv', jnts, d = 2 )
    # clean up temp jnt
    cmds.delete( tmp_jnt )
    jnts.pop( -1 )
    # tube radius
    crcl = place.circle( 'radius', obj = jnts[0], radius = 0.36, degree = 5 )[0]
    cmds.select( [crv, crcl] )
    tube = cmds.extrude( ch = True, rn = False, po = 0, et = 2, ucp = 1, fpt = 1, upn = 1, rotation = 0, scale = 1, rsp = 1 )[0]
    cmds.reverseSurface( tube, rpo = True )
    tube_poly = cmds.nurbsToPoly( tube, format = 3, uType = 3, vType = 3, cht = 0.2, chr = 0.1 )[0]
    tube_poly = cmds.rename( tube_poly, suffix + '_Deformer' )
    cmds.polyNormal( tube_poly, nm = 0 )
    cmds.delete( tube_poly, constructionHistory = True )
    cmds.delete( tube, crv, crcl )
    cmds.parent( tube_poly, jnts[0] )
    cmds.setAttr( jnts[0] + '.translateX', 4.168 )
    cmds.setAttr( jnts[0] + '.translateY', 0.32 )
    cmds.setAttr( jnts[0] + '.translateZ', 6.6 )
    # return None
    cmds.setAttr( tube_poly + '.translateZ', ( length * 0.7 ) * -1 )  # move so default weights distribute properly, loop cant lay directly on joint
    cmds.parent( tube_poly, world = True )  # unparent
    cmds.select( jnts[0], hi = True )
    cmds.select( tube_poly, add = True )
    # python or mel binSkin didnt work, created too many skinClusters
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    # wrap
    dfrmr = createWrap( tube_poly, geo_string )
    # clean up
    cmds.parent( tube_poly, GEO[1] )
    cmds.parent( tube_poly + 'Base', GEO[1] )

    # return None
    # correct joint length, for bend and connect to other side
    for jnt in jnts:
        if '_00' not in jnt:
            pass
            cmds.setAttr( jnt + '.translateZ', new_length )

    '''
    # bend into place, connect tip to opposite end of amulet
    bend_seg = int( ( segments / 2 ) + 0.5 )  # double joint, first joint in segment
    bend_letter = chr( ord( 'a' ) + bend_seg ).upper()  # number to letter
    bend_letter_next = chr( ord( 'a' ) + bend_seg + 1 ).upper()  # number to letter
    jnt_num = str( ( '%0' + str( pad ) + 'd' ) % ( 1 ) )  # pad jnt number
    cmds.setAttr( suffix + bend_letter + '_jnt_' + jnt_num + '.rotateY', -90 )
    cmds.setAttr( suffix + bend_letter_next + '_jnt_' + jnt_num + '.rotateY', -90 )'''

    # place segment controls
    seg = []
    # seg.append( jnts[0] )
    cmds.select( jnts[0], hi = True )
    sel = cmds.ls( sl = True )
    for jnt in sel:
        if '_01' in jnt and jnt != sel[0]:
            seg.append( jnt )
    # print seg
    # return None

    amuletSplines2( jnts[0], jnts[-1], X = 0.5 )


def amuletSplines2( root_jnt = '', tip_jnt = '', X = 2, upDis = 12 ):
    '''\n
    Build splines\n
    '''
    face = None
    check = cmds.checkBox( 'atom_rat_faceCheck', query = True, v = True )
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)

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

    # SPINE
    spineName = 'chain'
    spineSize = X * 1
    spineDistance = X * upDis
    spineFalloff = 0
    spinePrnt = 'master_Grp'
    spineStrt = 'stringA_Grp'
    spineEnd = 'string_Tip_Grp'
    spineAttr = 'stringA'
    spineRoot = root_jnt

    spine = [root_jnt, tip_jnt]
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = False )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 1 )
    cmds.setAttr( spineAttr + '.ClstrVis', 1 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 1 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # connect multi/div node of spline curves(S/E) to Control group scale
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_E_IK_curve_scale.input2Z' )
    # special case
    cmds.setAttr( spineName + '_E_IK_Cntrl.rotateY', -180 )
    cmds.setAttr( spineName + '_Vctr_M36_Ctrl.rotateY', -90 )
    cmds.setAttr( spineName + '_Clstr_M37_Ctrl.rotateY', -90 )

'''
import webrImport as web
anmRg = web.mod("animRig_lib")
sel = cmds.ls(sl=True)
anmRg.guideLine(sel[0], sel[1], 'guide')
cmds.select(sel)
'''


def snapAmuletString():
    '''
    
    '''
    seg = ['stringA', 'stringB', 'stringC', 'stringD', 'stringE', 'stringF', 'stringG', 'stringH', 'stringI']
    segfront = 'amlt:'
    segback = [
    '_Clstr_M2_Ctrl',
    '_Clstr_M3_Ctrl',
    '_Clstr_M4_Ctrl',
    '_Clstr_M5_Ctrl',
    '_Clstr_M6_Ctrl',
    '_Clstr_M7_Ctrl',
    '_Clstr_M8_Ctrl',
    '_Clstr_E_Ctrl'
    ]
    am_alt = [
    'amlt_alt:chain_Clstr_M',
    '_Ctrl'
    ]
    j = 2
    for s in seg:
        for sb in segback:
            if j == 73:
                break
            # match am to am_alt
            if j == 37:
                # j = 38
                a_alt = am_alt[0] + str( j ) + am_alt[1] + '_Hack'
            else:
                a_alt = am_alt[0] + str( j ) + am_alt[1]
            a = segfront + s + sb

            print a, a_alt
            #
            cmds.select( a_alt, a )
            cmds.pointConstraint( a, a_alt, mo = False )
            # anm.matchObj()
            j = j + 1


def snapAmuletBase():
    '''
    
    '''
    a_base = [
    'amlt:amulet',
    'amlt:master_Offset',
    'amlt:master'
    ]

    alt_base = [
    'amlt_alt:amulet',
    'amlt_alt:master_Offset',
    'amlt_alt:master'
    ]
    for i in range( len( a_base ) ):
        cmds.parentConstraint( a_base[i], alt_base[i], mo = False )

    a_base = [
    'amlt:hinge_R',
    'amlt:string_Tip',
    'amlt:stringA',
    'amlt:hinge_L'
    ]

    alt_base = [
    'amlt_alt:hinge_R',
    'amlt_alt:string_Tip',
    'amlt_alt:stringA',
    'amlt_alt:hinge_L'
    ]
    for i in range( len( a_base ) ):
        cmds.orientConstraint( a_base[i], alt_base[i], mo = False )
'''
ar = web.mod('animRig_lib')
a = [
'amlt:stringI',
'amlt:stringH',
'amlt:stringE',
'amlt:stringD',
'amlt:stringG',
'amlt:stringF',
'amlt:stringC',
'amlt:stringB'
]
cam = cmds.ls(ls=True)[0]
for i in a:
    cmds.select(i, cam )
    ar.parentRig()'''

'''
geo_con = [
'amlt:stringB__PLACE__',
'amlt:stringC__PLACE__',
'amlt:stringD__PLACE__',
'amlt:stringE__PLACE__',
'amlt:stringF__PLACE__',
'amlt:stringG__PLACE__',
'amlt:stringH__PLACE__',
'amlt:stringI__PLACE__'
]

bkp_anim = [
'amlt:stringB__PLACE____PLACE__',
'amlt:stringC__PLACE____PLACE__',
'amlt:stringD__PLACE____PLACE__',
'amlt:stringE__PLACE____PLACE__',
'amlt:stringF__PLACE____PLACE__',
'amlt:stringG__PLACE____PLACE__',
'amlt:stringH__PLACE____PLACE__',
'amlt:stringI__PLACE____PLACE__'
]
#
sel = cmds.ls( sl = True )
cmds.select( cl = True )
#
i = 0
for i in range( len( actual ) ):
    #print actual[i]
    #print offsets[i]
    cmds.select( [geo_con[i], bkp_anim[i]] )
    anm.matchObj()
#
cmds.select( sel )
'''
