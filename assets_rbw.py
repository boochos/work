import os

from atom_face_lib import skn
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


def cage_master():
    '''
    build defaults
    '''
    X = 50
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = X * 12 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    master = 'master_Grp'

    #
    geo_grp = get_geo_list( grp = True )
    geo_cage = get_geo_list( cage = True )
    # root = 'cage_root_jnt'
    hub_jnt = 'chain_hub_jnt'
    hang_jnt = 'chain_hang_jnt'  # new root
    top_jnt = 'cage_top_jnt'
    bottom_jnt = 'cage_bottom_jnt'

    # geo history and normals
    fix_normals( del_history = True )

    #
    cmds.parent( hang_jnt, SKIN_JOINTS )
    cmds.parent( geo_grp, GEO[0] )
    cmds.setAttr( geo_grp + '.rotateY', -35.999 )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( geo_grp, [True, False], [True, False], [True, False], [True, False, False] )

    for g in geo_cage:
        cmds.bindSkin( g, top_jnt, tsb = True )

    # top #
    Top = 'cage_top'
    top = place.Controller( Top, top_jnt, True, 'facetYup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    TopCt = top.createController()
    # lock geo - [lock, keyable], [visible, lock, keyable]
    # place.setChannels( TopCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.parent( TopCt[0], CONTROLS )
    cmds.parentConstraint( hub_jnt, TopCt[0], mo = True )
    cmds.parentConstraint( TopCt[4], top_jnt, mo = True )

    # bottom #
    Bottom = 'cage_bottom'
    bottom = place.Controller( Bottom, bottom_jnt, True, 'facetYup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    BottomCt = bottom.createController()
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( BottomCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.parent( BottomCt[0], CONTROLS )
    cmds.parentConstraint( hub_jnt, BottomCt[0], mo = True )
    cmds.parentConstraint( BottomCt[4], bottom_jnt, mo = True )

    # up #
    Upc = 'front_cage'
    upc = place.Controller( Upc, top_jnt, False, 'loc_ctrl', X * 1, 17, 8, 1, ( 0, 0, 1 ), True, True )
    UpcCt = upc.createController()
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( UpcCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.parent( UpcCt[0], CONTROLS )
    cmds.setAttr( UpcCt[0] + '.translateZ', 250 )
    cmds.parentConstraint( hub_jnt, UpcCt[0], mo = True )

    # cage aim
    cmds.aimConstraint( BottomCt[4], TopCt[2], wut = 'object', wuo = UpcCt[4], aim = [0, -1, 0], u = [0, 0, 1], mo = False )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( TopCt[2], [False, True], [True, False], [True, False], [True, False, False] )

    # sway #
    Sway = 'sway'
    sway = place.Controller( Sway, bottom_jnt, True, 'loc_ctrl', X * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    SwayCt = sway.createController()
    # cmds.setAttr( SwayCt[0] + '.translateY', -100 )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( SwayCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.parent( SwayCt[0], CONTROLS )
    cmds.parentConstraint( master, SwayCt[0], mo = True )

    # up #
    Up = 'front_hang'
    up = place.Controller( Up, top_jnt, False, 'loc_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True )
    UpCt = up.createController()
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( UpCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.parent( UpCt[0], CONTROLS )
    cmds.setAttr( UpCt[0] + '.translateZ', 350 )
    cmds.parentConstraint( master, UpCt[0], mo = True )

    # up #
    Hang = 'hang'
    hang = place.Controller( Hang, hang_jnt, False, 'facetYup_ctrl', X * 5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    HangCt = hang.createController()
    cmds.parent( HangCt[0], CONTROLS )
    cmds.parentConstraint( HangCt[4], hang_jnt, mo = True )
    cmds.parentConstraint( master, HangCt[0], mo = True )

    # sway aim
    cmds.aimConstraint( SwayCt[4], HangCt[2], wut = 'object', wuo = UpCt[4], aim = [0, -1, 0], u = [0, 0, 1], mo = False )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( HangCt[2], [False, True], [True, False], [True, False], [True, False, False] )

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
        # cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def chain_hub():
    '''
    add hub controls
    '''
    X = 10
    CONTROLS = '___CONTROLS'
    hang = 'hang_Grp'
    splineX = 'chainX_jnt_000'  # parent for hubA, hubB
    WORLD_SPACE = '___WORLD_SPACE'
    GEO = '___GEO'
    SKIN_JOINTS = '___SKIN_JOINTS'

    # a, b
    geo_hub = [
    'chain_geo_grp|chain_geo163',
    'chain_geo_grp|chain_geo168'
    ]
    jnt_hub = [
    'chain_hubA_jnt',
    'chain_hubB_jnt',
    'chain_hub_jnt'
    ]
    # hub main #
    Hub = 'hub'
    hub = place.Controller( Hub, jnt_hub[2], True, 'facetYup_ctrl', X * 11, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    HubCt = hub.createController()
    cmds.parent( HubCt[0], CONTROLS )
    cmds.parentConstraint( hang, HubCt[0], mo = True )
    cmds.parentConstraint( HubCt[4], jnt_hub[2], mo = True )

    # hub main #
    HubX = 'hubX'
    hubx = place.Controller( HubX, jnt_hub[2], True, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    HubXCt = hubx.createController()
    cmds.parent( HubXCt[0], CONTROLS )
    cmds.parentConstraint( HubCt[4], HubXCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( HubXCt[2], [False, True], [True, False], [True, False], [True, False, False] )
    cmds.setAttr( HubXCt[2] + '.rotateY', keyable = True, lock = False )

    # hub A #
    HubA = 'hubA'
    huba = place.Controller( HubA, jnt_hub[0], False, 'diamond_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' )
    HubACt = huba.createController()
    cmds.parent( HubACt[0], CONTROLS )
    cmds.parentConstraint( splineX, HubACt[0], mo = True )
    cmds.parentConstraint( HubACt[4], jnt_hub[0], mo = True )
    cmds.select( [geo_hub[0], jnt_hub[0]] )
    mel.eval( 'SmoothBindSkin;' )

    # hub A #
    HubB = 'hubB'
    hubb = place.Controller( HubB, jnt_hub[1], False, 'diamond_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' )
    HubBCt = hubb.createController()
    cmds.parent( HubBCt[0], CONTROLS )
    cmds.parentConstraint( splineX, HubBCt[0], mo = True )
    cmds.parentConstraint( HubBCt[4], jnt_hub[1], mo = True )
    cmds.select( [geo_hub[1], jnt_hub[1]] )
    mel.eval( 'SmoothBindSkin;' )


def cage_gates():
    '''
    add doors
    '''
    #
    X = 30
    CONTROLS = '___CONTROLS'
    top_jnt = 'cage_top_jnt'
    WORLD_SPACE = '___WORLD_SPACE'
    GEO = '___GEO'
    SKIN_JOINTS = '___SKIN_JOINTS'

    #
    geo_gate_l = get_geo_list( gate_l = True )
    jnt_gate_l = 'gate_01_L_jnt'
    # gate l #
    GateL = 'gate_l'
    gatel = place.Controller( GateL, jnt_gate_l, True, 'diamond_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' )
    GateLCt = gatel.createController()
    cmds.parent( GateLCt[0], CONTROLS )
    cmds.select( GateLCt[2] )
    cmds.transformLimits( erz = [0, 1], rz = ( -90, 0 ) )
    cmds.parentConstraint( top_jnt, GateLCt[0], mo = True )
    cmds.parentConstraint( GateLCt[4], jnt_gate_l, mo = True )
    # skin
    for g in geo_gate_l:
        cmds.bindSkin( g, jnt_gate_l, tsb = True )

    #
    geo_gate_r = get_geo_list( gate_r = True )
    jnt_gate_r = 'gate_01_R_jnt'
    # gate r #
    GateR = 'gate_r'
    gater = place.Controller( GateR, jnt_gate_r, True, 'diamond_ctrl', X * 2, 17, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' )
    GateRCt = gater.createController()
    cmds.parent( GateRCt[0], CONTROLS )
    cmds.select( GateRCt[2] )
    cmds.transformLimits( erz = [0, 1], rz = ( -90, 0 ) )
    cmds.parentConstraint( top_jnt, GateRCt[0], mo = True )
    cmds.parentConstraint( GateRCt[4], jnt_gate_r, mo = True )
    # skin
    for g in geo_gate_r:
        cmds.bindSkin( g, jnt_gate_r, tsb = True )


def spline( name = '', root_jnt = '', tip_jnt = '', splinePrnt = '', splineStrt = '', splineEnd = '', splineAttr = '', startSkpR = False, endSkpR = False, X = 2 ):
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

    # SPINE
    splineName = name
    splineSize = X * 1
    splineDistance = X * 4
    splineFalloff = 0

    spline = [root_jnt, tip_jnt]
    # build spline
    SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
    cmds.select( spline )

    stage.splineStage( 4 )
    # assemble
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
    cmds.setAttr( splineAttr + '.' + splineName + 'Stretch', 1 )
    cmds.setAttr( splineAttr + '.ClstrVis', 1 )
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


def chain_splines():
    '''
    rig chains with splines
    '''
    # spline( name = 'chainA', root_jnt = 'chainA_jnt_000', tip_jnt = 'chainA_jnt_016', splinePrnt = 'cage_top_Grp', splineStrt = 'cage_top_Grp', splineEnd = 'hubA_Grp', splineAttr = 'master', X = 2 )
    #
    joints_s = ['chainA_jnt_000', 'chainB_jnt_000', 'chainC_jnt_000', 'chainD_jnt_000', 'chainE_jnt_000']
    joints_e = ['chainA_jnt_016', 'chainB_jnt_016', 'chainC_jnt_016', 'chainD_jnt_016', 'chainE_jnt_016']
    names = ['chainA_base', 'chainB_base', 'chainC_base', 'chainD_base', 'chainE_base']
    splineEnd = ['hubA_Grp', 'hubB_Grp', 'hubB_Grp', 'hubA_Grp', 'hubA_Grp']
    #
    geo_A = get_geo_list( chainA = True )
    geo_B = get_geo_list( chainB = True )
    geo_C = get_geo_list( chainC = True )
    geo_D = get_geo_list( chainD = True )
    geo_E = get_geo_list( chainE = True )
    geo = [geo_A, geo_B, geo_C, geo_D, geo_E]
    clrs = ['red', 'blue', 'blue', 'red', 'red']
    #
    X = 1
    for i in range( len( names ) ):
        # base control
        Nm = names[i]
        nm = place.Controller( Nm, joints_s[i], False, 'facetYup_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clrs[i] )
        NmCt = nm.createController()
        # lock geo - [lock, keyable], [visible, lock, keyable]
        place.setChannels( NmCt[2], [True, False], [True, False], [True, False], [True, False, False] )
        cmds.parent( NmCt[0], '___CONTROLS' )
        cmds.parentConstraint( 'cage_top_Grp', NmCt[0], mo = True )
        # spline joints
        cmds.select( joints_s[i], hi = True )
        skn_jnts = cmds.ls( sl = 1 )
        # bind
        j = 0
        for g in geo[i]:
            cmds.bindSkin( g, skn_jnts[j], tsb = True )
            j = j + 1
        # spline
        spline( name = names[i], root_jnt = joints_s[i], tip_jnt = joints_e[i], splinePrnt = NmCt[4], splineStrt = NmCt[4], splineEnd = splineEnd[i], splineAttr = NmCt[2], startSkpR = False, endSkpR = True, X = 2 )

    # spline X
    root = 'chainX_jnt_000'
    tip = 'chainX_jnt_088'
    geo_X = get_geo_list( chainX = True )
    cmds.select( 'chainX_jnt_000', hi = True )
    skn_jnts = cmds.ls( sl = 1 )
    # bind
    for i in range( len( geo_X ) ):
        cmds.bindSkin( geo_X[i], skn_jnts[i], tsb = True )
    # spline x
    spline( name = 'chainX', root_jnt = root, tip_jnt = tip, splinePrnt = 'hang_Grp', splineStrt = 'hub_Grp', splineEnd = 'hang_Grp', splineAttr = 'hub', startSkpR = False, endSkpR = False, X = 5 )
    cmds.setAttr( 'hub.ClstrMidIkBlend', 0 )
    # adjust rig for spline hub
    cmds.parentConstraint( 'hubX_Grp', 'chainX_S_IK_Cntrl', mo = True )
    cmds.setAttr( 'chainX_S_IK_Cntrl.visibility', 0 )


def fix_normals( del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    geo = get_geo_list( all = True )
    cmds.select( geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( geo, ch = True )


def get_geo_list( grp = False, cage = False, gate_l = False, gate_r = False, chainA = False, chainB = False, chainC = False, chainD = False, chainE = False, chainX = False, hub = False, all = False ):
    '''
    return requested geo list
    '''
    #
    geo_grp = 'cage_grp'
    geo_hub = [
    'chain_geo_grp|chain_geo163',
    'chain_geo_grp|chain_geo168'
    ]
    geo_cage = [
    'cage_geo_grp|cage_geo84',
    'cage_geo_grp|cage_geo63',
    'cage_geo_grp|cage_geo66',
    'cage_geo_grp|cage_geo65',
    'cage_geo_grp|cage_geo64',
    'cage_geo_grp|cage_geo335',
    'cage_geo_grp|cage_geo332',
    'cage_geo_grp|cage_geo331',
    'cage_geo_grp|cage_geo333',
    'cage_geo_grp|cage_geo337',
    'cage_geo_grp|cage_geo334',
    'cage_geo_grp|cage_geo336',
    'cage_geo_grp|cage_geo168',
    'cage_geo_grp|cage_geo170',
    'cage_geo_grp|cage_geo171',
    'cage_geo_grp|cage_geo172',
    'cage_geo_grp|cage_geo173',
    'cage_geo_grp|cage_geo174',
    'cage_geo_grp|cage_geo175',
    'cage_geo_grp|cage_geo177',
    'cage_geo_grp|cage_geo176',
    'cage_geo_grp|cage_geo154',
    'cage_geo_grp|cage_geo155',
    'cage_geo_grp|cage_geo156',
    'cage_geo_grp|cage_geo158',
    'cage_geo_grp|cage_geo157',
    'cage_geo_grp|cage_geo159',
    'cage_geo_grp|cage_geo160',
    'cage_geo_grp|cage_geo161',
    'cage_geo_grp|cage_geo162',
    'cage_geo_grp|cage_geo163',
    'cage_geo_grp|cage_geo165',
    'cage_geo_grp|cage_geo164',
    'cage_geo_grp|cage_geo142',
    'cage_geo_grp|cage_geo143',
    'cage_geo_grp|cage_geo144',
    'cage_geo_grp|cage_geo145',
    'cage_geo_grp|cage_geo147',
    'cage_geo_grp|cage_geo146',
    'cage_geo_grp|cage_geo148',
    'cage_geo_grp|cage_geo149',
    'cage_geo_grp|cage_geo150',
    'cage_geo_grp|cage_geo151',
    'cage_geo_grp|cage_geo153',
    'cage_geo_grp|cage_geo152',
    'cage_geo_grp|cage_geo130',
    'cage_geo_grp|cage_geo131',
    'cage_geo_grp|cage_geo132',
    'cage_geo_grp|cage_geo133',
    'cage_geo_grp|cage_geo134',
    'cage_geo_grp|cage_geo135',
    'cage_geo_grp|cage_geo136',
    'cage_geo_grp|cage_geo137',
    'cage_geo_grp|cage_geo138',
    'cage_geo_grp|cage_geo139',
    'cage_geo_grp|cage_geo141',
    'cage_geo_grp|cage_geo140',
    'cage_geo_grp|cage_geo107',
    'cage_geo_grp|cage_geo109',
    'cage_geo_grp|cage_geo108',
    'cage_geo_grp|cage_geo110',
    'cage_geo_grp|cage_geo111',
    'cage_geo_grp|cage_geo112',
    'cage_geo_grp|cage_geo113',
    'cage_geo_grp|cage_geo114',
    'cage_geo_grp|cage_geo115',
    'cage_geo_grp|cage_geo116',
    'cage_geo_grp|cage_geo118',
    'cage_geo_grp|cage_geo117',
    'cage_geo_grp|cage_geo97',
    'cage_geo_grp|cage_geo96',
    'cage_geo_grp|cage_geo98',
    'cage_geo_grp|cage_geo99',
    'cage_geo_grp|cage_geo100',
    'cage_geo_grp|cage_geo101',
    'cage_geo_grp|cage_geo102',
    'cage_geo_grp|cage_geo103',
    'cage_geo_grp|cage_geo104',
    'cage_geo_grp|cage_geo105',
    'cage_geo_grp|cage_geo106',
    'cage_geo_grp|cage_geo85',
    'cage_geo_grp|cage_geo86',
    'cage_geo_grp|cage_geo87',
    'cage_geo_grp|cage_geo88',
    'cage_geo_grp|cage_geo89',
    'cage_geo_grp|cage_geo90',
    'cage_geo_grp|cage_geo91',
    'cage_geo_grp|cage_geo92',
    'cage_geo_grp|cage_geo93',
    'cage_geo_grp|cage_geo94',
    'cage_geo_grp|cage_geo95',
    'cage_geo_grp|cage_geo73',
    'cage_geo_grp|cage_geo74',
    'cage_geo_grp|cage_geo75',
    'cage_geo_grp|cage_geo76',
    'cage_geo_grp|cage_geo77',
    'cage_geo_grp|cage_geo78',
    'cage_geo_grp|cage_geo79',
    'cage_geo_grp|cage_geo80',
    'cage_geo_grp|cage_geo81',
    'cage_geo_grp|cage_geo82',
    'cage_geo_grp|cage_geo83',
    'cage_geo_grp|cage_geo61',
    'cage_geo_grp|cage_geo62',
    'cage_geo_grp|cage_geo67',
    'cage_geo_grp|cage_geo68',
    'cage_geo_grp|cage_geo69',
    'cage_geo_grp|cage_geo70',
    'cage_geo_grp|cage_geo71',
    'cage_geo_grp|cage_geo72',
    'cage_geo_grp|cage_geo49',
    'cage_geo_grp|cage_geo50',
    'cage_geo_grp|cage_geo51',
    'cage_geo_grp|cage_geo52',
    'cage_geo_grp|cage_geo53',
    'cage_geo_grp|cage_geo54',
    'cage_geo_grp|cage_geo55',
    'cage_geo_grp|cage_geo56',
    'cage_geo_grp|cage_geo57',
    'cage_geo_grp|cage_geo58',
    'cage_geo_grp|cage_geo59',
    'cage_geo_grp|cage_geo60',
    'cage_geo_grp|cage_geo37',
    'cage_geo_grp|cage_geo38',
    'cage_geo_grp|cage_geo39',
    'cage_geo_grp|cage_geo40',
    'cage_geo_grp|cage_geo41',
    'cage_geo_grp|cage_geo42',
    'cage_geo_grp|cage_geo43',
    'cage_geo_grp|cage_geo44',
    'cage_geo_grp|cage_geo45',
    'cage_geo_grp|cage_geo46',
    'cage_geo_grp|cage_geo47',
    'cage_geo_grp|cage_geo48',
    'cage_geo_grp|cage_geo25',
    'cage_geo_grp|cage_geo26',
    'cage_geo_grp|cage_geo27',
    'cage_geo_grp|cage_geo28',
    'cage_geo_grp|cage_geo29',
    'cage_geo_grp|cage_geo30',
    'cage_geo_grp|cage_geo31',
    'cage_geo_grp|cage_geo32',
    'cage_geo_grp|cage_geo33',
    'cage_geo_grp|cage_geo34',
    'cage_geo_grp|cage_geo35',
    'cage_geo_grp|cage_geo36',
    'cage_geo_grp|cage_geo13',
    'cage_geo_grp|cage_geo14',
    'cage_geo_grp|cage_geo15',
    'cage_geo_grp|cage_geo16',
    'cage_geo_grp|cage_geo17',
    'cage_geo_grp|cage_geo18',
    'cage_geo_grp|cage_geo19',
    'cage_geo_grp|cage_geo20',
    'cage_geo_grp|cage_geo21',
    'cage_geo_grp|cage_geo22',
    'cage_geo_grp|cage_geo23',
    'cage_geo_grp|cage_geo24',
    'cage_geo_grp|cage_geo1',
    'cage_geo_grp|cage_geo2',
    'cage_geo_grp|cage_geo3',
    'cage_geo_grp|cage_geo4',
    'cage_geo_grp|cage_geo5',
    'cage_geo_grp|cage_geo7',
    'cage_geo_grp|cage_geo6',
    'cage_geo_grp|cage_geo8',
    'cage_geo_grp|cage_geo9',
    'cage_geo_grp|cage_geo10',
    'cage_geo_grp|cage_geo11',
    'cage_geo_grp|cage_geo12',
    'cage_geo_grp|cage_geo327',
    'cage_geo_grp|cage_geo328',
    'cage_geo_grp|cage_geo329',
    'cage_geo_grp|cage_geo330',
    'roots_geo55',
    'roots_geo54',
    'roots_geo52',
    'roots_geo51',
    'roots_geo49',
    'roots_geo48',
    'roots_geo42',
    'roots_geo38',
    'roots_geo37',
    'roots_geo32',
    'roots_geo30',
    'roots_geo14',
    'roots_geo13',
    'chair_geo_grp|chair_geo2',
    'chair_geo_grp|chair_geo1',
    'chair_geo_grp|chair_geo5',
    'chair_geo_grp|chair_geo4',
    'chair_geo_grp|chair_geo3',
    'cage_geo_grp|cage_geo322',
    'cage_geo_grp|cage_geo321',
    'cage_geo_grp|cage_geo320',
    'cage_geo_grp|cage_geo319',
    'cage_geo_grp|cage_geo309',
    'cage_geo_grp|cage_geo310',
    'cage_geo_grp|cage_geo311',
    'cage_geo_grp|cage_geo312',
    'cage_geo_grp|cage_geo313',
    'cage_geo_grp|cage_geo314',
    'cage_geo_grp|cage_geo315',
    'cage_geo_grp|cage_geo316',
    'cage_geo_grp|cage_geo318',
    'cage_geo_grp|cage_geo317',
    'cage_geo_grp|cage_geo119',
    'cage_geo_grp|cage_geo125',
    'cage_geo_grp|cage_geo127',
    'cage_geo_grp|cage_geo128',
    'cage_geo_grp|cage_geo129',
    'cage_geo_grp|cage_geo307',
    'cage_geo_grp|cage_geo308',
    'cage_geo_grp|cage_geo324',
    'cage_geo_grp|cage_geo325',
    'cage_geo_grp|cage_geo326',
    'cage_geo_grp|cage_geo323',
    'cage_geo_grp|cage_geo249',
    'cage_geo_grp|cage_geo250',
    'cage_geo_grp|cage_geo251',
    'cage_geo_grp|cage_geo252',
    'cage_geo_grp|cage_geo253',
    'cage_geo_grp|cage_geo254',
    'cage_geo_grp|cage_geo255',
    'cage_geo_grp|cage_geo305',
    'cage_geo_grp|cage_geo306',
    'cage_geo_grp|cage_geo296',
    'cage_geo_grp|cage_geo297',
    'cage_geo_grp|cage_geo304',
    'cage_geo_grp|cage_geo303',
    'cage_geo_grp|cage_geo302',
    'cage_geo_grp|cage_geo301',
    'cage_geo_grp|cage_geo300',
    'cage_geo_grp|cage_geo299',
    'cage_geo_grp|cage_geo298',
    'cage_geo_grp|cage_geo287',
    'cage_geo_grp|cage_geo288',
    'cage_geo_grp|cage_geo295',
    'cage_geo_grp|cage_geo294',
    'cage_geo_grp|cage_geo293',
    'cage_geo_grp|cage_geo292',
    'cage_geo_grp|cage_geo291',
    'cage_geo_grp|cage_geo290',
    'cage_geo_grp|cage_geo289',
    'cage_geo_grp|cage_geo279',
    'cage_geo_grp|cage_geo286',
    'cage_geo_grp|cage_geo285',
    'cage_geo_grp|cage_geo284',
    'cage_geo_grp|cage_geo283',
    'cage_geo_grp|cage_geo269',
    'cage_geo_grp|cage_geo278',
    'cage_geo_grp|cage_geo277',
    'cage_geo_grp|cage_geo276',
    'cage_geo_grp|cage_geo275',
    'cage_geo_grp|cage_geo274',
    'cage_geo_grp|cage_geo273',
    'cage_geo_grp|cage_geo272',
    'cage_geo_grp|cage_geo271',
    'cage_geo_grp|cage_geo270',
    'cage_geo_grp|cage_geo256',
    'cage_geo_grp|cage_geo257',
    'cage_geo_grp|cage_geo267',
    'cage_geo_grp|cage_geo266',
    'cage_geo_grp|cage_geo265',
    'cage_geo_grp|cage_geo264',
    'cage_geo_grp|cage_geo263',
    'cage_geo_grp|cage_geo262',
    'cage_geo_grp|cage_geo237',
    'cage_geo_grp|cage_geo240',
    'cage_geo_grp|cage_geo241',
    'cage_geo_grp|cage_geo242',
    'cage_geo_grp|cage_geo243',
    'cage_geo_grp|cage_geo244',
    'cage_geo_grp|cage_geo245',
    'cage_geo_grp|cage_geo247',
    'cage_geo_grp|cage_geo246',
    'cage_geo_grp|cage_geo248',
    'cage_geo_grp|cage_geo226',
    'cage_geo_grp|cage_geo227',
    'cage_geo_grp|cage_geo228',
    'cage_geo_grp|cage_geo229',
    'cage_geo_grp|cage_geo230',
    'cage_geo_grp|cage_geo231',
    'cage_geo_grp|cage_geo232',
    'cage_geo_grp|cage_geo233',
    'cage_geo_grp|cage_geo234',
    'cage_geo_grp|cage_geo235',
    'cage_geo_grp|cage_geo236',
    'cage_geo_grp|cage_geo214',
    'cage_geo_grp|cage_geo216',
    'cage_geo_grp|cage_geo219',
    'cage_geo_grp|cage_geo220',
    'cage_geo_grp|cage_geo221',
    'cage_geo_grp|cage_geo222',
    'cage_geo_grp|cage_geo223',
    'cage_geo_grp|cage_geo224',
    'cage_geo_grp|cage_geo225',
    'cage_geo_grp|cage_geo203',
    'cage_geo_grp|cage_geo204',
    'cage_geo_grp|cage_geo205',
    'cage_geo_grp|cage_geo206',
    'cage_geo_grp|cage_geo207',
    'cage_geo_grp|cage_geo208',
    'cage_geo_grp|cage_geo209',
    'cage_geo_grp|cage_geo210',
    'cage_geo_grp|cage_geo211',
    'cage_geo_grp|cage_geo212',
    'cage_geo_grp|cage_geo213',
    'cage_geo_grp|cage_geo191',
    'cage_geo_grp|cage_geo190',
    'cage_geo_grp|cage_geo192',
    'cage_geo_grp|cage_geo193',
    'cage_geo_grp|cage_geo194',
    'cage_geo_grp|cage_geo195',
    'cage_geo_grp|cage_geo196',
    'cage_geo_grp|cage_geo197',
    'cage_geo_grp|cage_geo198',
    'cage_geo_grp|cage_geo199',
    'cage_geo_grp|cage_geo200',
    'cage_geo_grp|cage_geo201',
    'cage_geo_grp|cage_geo178',
    'cage_geo_grp|cage_geo180',
    'cage_geo_grp|cage_geo179',
    'cage_geo_grp|cage_geo181',
    'cage_geo_grp|cage_geo182',
    'cage_geo_grp|cage_geo183',
    'cage_geo_grp|cage_geo184',
    'cage_geo_grp|cage_geo185',
    'cage_geo_grp|cage_geo186',
    'cage_geo_grp|cage_geo187',
    'cage_geo_grp|cage_geo189',
    'cage_geo_grp|cage_geo188',
    'cage_geo_grp|cage_geo166',
    'cage_geo_grp|cage_geo167',
    'cage_geo_grp|cage_geo169'
    ]
    geo_gate_r = [
    'cage_geo_grp|cage_geo122',
    'cage_geo_grp|cage_geo121',
    'cage_geo_grp|cage_geo261',
    'cage_geo_grp|cage_geo268',
    'cage_geo_grp|cage_geo281',
    'cage_geo_grp|cage_geo217',
    'cage_geo_grp|cage_geo259',
    'cage_geo_grp|cage_geo258',
    'cage_geo_grp|cage_geo215',
    'cage_geo_grp|cage_geo124'
    ]
    geo_gate_l = [
    'cage_geo_grp|cage_geo123',
    'cage_geo_grp|cage_geo260',
    'cage_geo_grp|cage_geo120',
    'cage_geo_grp|cage_geo126',
    'cage_geo_grp|cage_geo282',
    'cage_geo_grp|cage_geo280',
    'cage_geo_grp|cage_geo202',
    'roots_geo46',
    'roots_geo57',
    'cage_geo_grp|cage_geo239',
    'cage_geo_grp|cage_geo238',
    'cage_geo_grp|cage_geo218',
    'roots_geo4'
    ]
    geo_chainA = [
    'chain_geo_grp|chain_geo123',
    'chain_geo_grp|chain_geo92',
    'chain_geo_grp|chain_geo124',
    'chain_geo_grp|chain_geo91',
    'chain_geo_grp|chain_geo125',
    'chain_geo_grp|chain_geo90',
    'chain_geo_grp|chain_geo126',
    'chain_geo_grp|chain_geo82',
    'chain_geo_grp|chain_geo128',
    'chain_geo_grp|chain_geo73',
    'chain_geo_grp|chain_geo131',
    'chain_geo_grp|chain_geo74',
    'chain_geo_grp|chain_geo130',
    'chain_geo_grp|chain_geo75',
    'chain_geo_grp|chain_geo129',
    'chain_geo_grp|chain_geo84'
    ]
    geo_chainB = [
    'chain_geo_grp|chain_geo116',
    'chain_geo_grp|chain_geo83',
    'chain_geo_grp|chain_geo115',
    'chain_geo_grp|chain_geo81',
    'chain_geo_grp|chain_geo107',
    'chain_geo_grp|chain_geo80',
    'chain_geo_grp|chain_geo108',
    'chain_geo_grp|chain_geo79',
    'chain_geo_grp|chain_geo109',
    'chain_geo_grp|chain_geo78',
    'chain_geo_grp|chain_geo110',
    'chain_geo_grp|chain_geo77',
    'chain_geo_grp|chain_geo111',
    'chain_geo_grp|chain_geo76',
    'chain_geo_grp|chain_geo112',
    'chain_geo_grp|chain_geo60'
    ]
    geo_chainC = [
    'chain_geo_grp|chain_geo151',
    'chain_geo_grp|chain_geo119',
    'chain_geo_grp|chain_geo150',
    'chain_geo_grp|chain_geo118',
    'chain_geo_grp|chain_geo149',
    'chain_geo_grp|chain_geo117',
    'chain_geo_grp|chain_geo148',
    'chain_geo_grp|chain_geo114',
    'chain_geo_grp|chain_geo147',
    'chain_geo_grp|chain_geo113',
    'chain_geo_grp|chain_geo146',
    'chain_geo_grp|chain_geo104',
    'chain_geo_grp|chain_geo145',
    'chain_geo_grp|chain_geo95',
    'chain_geo_grp|chain_geo139',
    'chain_geo_grp|chain_geo96'
    ]
    geo_chainD = [
    'chain_geo_grp|chain_geo138',
    'chain_geo_grp|chain_geo97',
    'chain_geo_grp|chain_geo132',
    'chain_geo_grp|chain_geo98',
    'chain_geo_grp|chain_geo133',
    'chain_geo_grp|chain_geo99',
    'chain_geo_grp|chain_geo134',
    'chain_geo_grp|chain_geo106',
    'chain_geo_grp|chain_geo135',
    'chain_geo_grp|chain_geo105',
    'chain_geo_grp|chain_geo136',
    'chain_geo_grp|chain_geo103',
    'chain_geo_grp|chain_geo137',
    'chain_geo_grp|chain_geo102',
    'chain_geo_grp|chain_geo140',
    'chain_geo_grp|chain_geo101'
    ]
    geo_chainE = [
    'chain_geo_grp|chain_geo141',
    'chain_geo_grp|chain_geo100',
    'chain_geo_grp|chain_geo142',
    'chain_geo_grp|chain_geo85',
    'chain_geo_grp|chain_geo144',
    'chain_geo_grp|chain_geo86',
    'chain_geo_grp|chain_geo143',
    'chain_geo_grp|chain_geo87',
    'chain_geo_grp|chain_geo127',
    'chain_geo_grp|chain_geo88',
    'chain_geo_grp|chain_geo120',
    'chain_geo_grp|chain_geo89',
    'chain_geo_grp|chain_geo121',
    'chain_geo_grp|chain_geo94',
    'chain_geo_grp|chain_geo122',
    'chain_geo_grp|chain_geo93'
    ]
    geo_chainX = [
    'chain_geo_grp|chain_geo71',
    'chain_geo_grp|chain_geo152',
    'chain_geo_grp|chain_geo61',
    'chain_geo_grp|chain_geo153',
    'chain_geo_grp|chain_geo72',
    'chain_geo_grp|chain_geo27',
    'chain_geo_grp|chain_geo70',
    'chain_geo_grp|chain_geo23',
    'chain_geo_grp|chain_geo69',
    'chain_geo_grp|chain_geo24',
    'chain_geo_grp|chain_geo68',
    'chain_geo_grp|chain_geo25',
    'chain_geo_grp|chain_geo67',
    'chain_geo_grp|chain_geo26',
    'chain_geo_grp|chain_geo66',
    'chain_geo_grp|chain_geo28',
    'chain_geo_grp|chain_geo65',
    'chain_geo_grp|chain_geo29',
    'chain_geo_grp|chain_geo64',
    'chain_geo_grp|chain_geo30',
    'chain_geo_grp|chain_geo63',
    'chain_geo_grp|chain_geo31',
    'chain_geo_grp|chain_geo62',
    'chain_geo_grp|chain_geo32',
    'chain_geo_grp|chain_geo49',
    'chain_geo_grp|chain_geo34',
    'chain_geo_grp|chain_geo48',
    'chain_geo_grp|chain_geo33',
    'chain_geo_grp|chain_geo50',
    'chain_geo_grp|chain_geo16',
    'chain_geo_grp|chain_geo51',
    'chain_geo_grp|chain_geo15',
    'chain_geo_grp|chain_geo52',
    'chain_geo_grp|chain_geo10',
    'chain_geo_grp|chain_geo53',
    'chain_geo_grp|chain_geo11',
    'chain_geo_grp|chain_geo54',
    'chain_geo_grp|chain_geo12',
    'chain_geo_grp|chain_geo55',
    'chain_geo_grp|chain_geo13',
    'chain_geo_grp|chain_geo56',
    'chain_geo_grp|chain_geo14',
    'chain_geo_grp|chain_geo57',
    'chain_geo_grp|chain_geo17',
    'chain_geo_grp|chain_geo58',
    'chain_geo_grp|chain_geo18',
    'chain_geo_grp|chain_geo59',
    'chain_geo_grp|chain_geo22',
    'chain_geo_grp|chain_geo38',
    'chain_geo_grp|chain_geo21',
    'chain_geo_grp|chain_geo37',
    'chain_geo_grp|chain_geo20',
    'chain_geo_grp|chain_geo35',
    'chain_geo_grp|chain_geo19',
    'chain_geo_grp|chain_geo36',
    'chain_geo_grp|chain_geo1',
    'chain_geo_grp|chain_geo39',
    'chain_geo_grp|chain_geo2',
    'chain_geo_grp|chain_geo40',
    'chain_geo_grp|chain_geo3',
    'chain_geo_grp|chain_geo41',
    'chain_geo_grp|chain_geo4',
    'chain_geo_grp|chain_geo42',
    'chain_geo_grp|chain_geo5',
    'chain_geo_grp|chain_geo43',
    'chain_geo_grp|chain_geo6',
    'chain_geo_grp|chain_geo44',
    'chain_geo_grp|chain_geo7',
    'chain_geo_grp|chain_geo47',
    'chain_geo_grp|chain_geo9',
    'chain_geo_grp|chain_geo46',
    'chain_geo_grp|chain_geo8',
    'chain_geo_grp|chain_geo45',
    'chain_geo_grp|chain_geo165',
    'chain_geo_grp|chain_geo159',
    'chain_geo_grp|chain_geo161',
    'chain_geo_grp|chain_geo157',
    'chain_geo_grp|chain_geo166',
    'chain_geo_grp|chain_geo158',
    'chain_geo_grp|chain_geo167',
    'chain_geo_grp|chain_geo156',
    'chain_geo_grp|chain_geo164',
    'chain_geo_grp|chain_geo154',
    'chain_geo_grp|chain_geo169',
    'chain_geo_grp|chain_geo155',
    'chain_geo_grp|chain_geo162',
    'chain_geo_grp|chain_geo160'
    ]
    #  grp = False, cage = False, gate_l = False, gate_r = False, chainA = False, chainB = False, chainC = False, chainD = False, chainE = False, chainX = False
    a = []
    if grp:
        for g in geo_grp:
            a.append( g )
        return geo_grp
    if cage:
        for g in geo_cage:
            a.append( g )
        return geo_cage
    if gate_l:
        for g in geo_gate_l:
            a.append( g )
        return geo_gate_l
    if gate_r:
        for g in geo_gate_r:
            a.append( g )
        return geo_gate_r
    if chainA:
        for g in geo_chainA:
            a.append( g )
        return geo_chainA
    if chainB:
        for g in geo_chainB:
            a.append( g )
        return geo_chainB
    if chainC:
        for g in geo_chainC:
            a.append( g )
        return geo_chainC
    if chainD:
        for g in geo_chainD:
            a.append( g )
        return geo_chainD
    if chainE:
        for g in geo_chainE:
            a.append( g )
        return geo_chainE
    if chainX:
        for g in geo_chainX:
            a.append( g )
        return geo_chainX
    if hub:
        for g in geo_hub:
            a.append( g )
        return geo_hub
    if all:
        for g in geo_cage:
            a.append( g )
        for g in geo_gate_l:
            a.append( g )
        for g in geo_gate_r:
            a.append( g )
        for g in geo_chainA:
            a.append( g )
        for g in geo_chainB:
            a.append( g )
        for g in geo_chainC:
            a.append( g )
        for g in geo_chainD:
            a.append( g )
        for g in geo_chainE:
            a.append( g )
        for g in geo_chainX:
            a.append( g )
        for g in geo_hub:
            a.append( g )
        return a

'''
#
#
import imp
import webrImport as web
imp.reload(web)
rbw = web.mod( "rbw_assets" )
rbw.cage_master()
rbw.cage_gates()
rbw.chain_hub()
rbw.chain_splines()

import imp
import webrImport as web
imp.reload(web)
place = web.mod( "atom_place_lib" )
anm = web.mod("anim_lib")

target = [
'joint10A',
'joint10B',
'joint10C',
'joint10D',
'joint10E'
]
shift = [
5.33,
5.25,
5.29,
5.36,
5.242
]
radius = 1.0

# X
jnts = place.jointChain( suffix = 'chainX', pad = 3, length = 8.202, amount = 87, radius = radius )
cmds.select(jnts[0], 'joint1X')
anm.matchObj()


# A
i = 0
jnts = place.jointChain( suffix = 'chainA', pad = 3, length = shift[i], amount = 16, radius = radius )
cmds.select(jnts[0], target[i])
anm.matchObj()
#
# B
i = 1
jnts = place.jointChain( suffix = 'chainB', pad = 3, length = shift[i], amount = 16, radius = radius )
cmds.select(jnts[0], target[i])
anm.matchObj()
#
# C
i = 2
jnts = place.jointChain( suffix = 'chainC', pad = 3, length = shift[i], amount = 16, radius = radius )
cmds.select(jnts[0], target[i])
anm.matchObj()
#
# D
i = 3
jnts = place.jointChain( suffix = 'chainD', pad = 3, length = shift[i], amount = 16, radius = radius )
cmds.select(jnts[0], target[i])
anm.matchObj()
#
# E
i = 4
jnts = place.jointChain( suffix = 'chainE', pad = 3, length = shift[i], amount = 16, radius = radius )
cmds.select(jnts[0], target[i])
anm.matchObj()
#
sel = cmds.ls(sl=1)
print(len(sel))
'''

