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


def panel_master():
    '''
    build defaults
    '''
    X = 50
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = X * 13 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    master = 'master_Grp'

    #
    geo_grp = get_geo_list()
    # nurbs influence
    skin = [
    'nurbsPlane1',
    'nurbsPlane1Base'
    ]

    # root joint
    root_jnt = 'root_jnt'

    # middle of panel
    Nm = 'panel'
    nm = place.Controller( Nm, root_jnt, False, 'facetYup_ctrl', X * 3, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' )
    NmCt = nm.createController()
    # lock geo - [lock, keyable], [visible, lock, keyable]
    # place.setChannels( NmCt[2], [True, False], [True, False], [True, False], [True, False, False] )
    cmds.parent( NmCt[0], '___CONTROLS' )
    cmds.parentConstraint( master, NmCt[0], mo = True )
    cmds.parentConstraint( NmCt[4], root_jnt, mo = True )

    # geo history and normals
    # fix_normals( del_history = False )

    #
    cmds.parent( root_jnt, SKIN_JOINTS )
    cmds.parent( 'mdl_grp', GEO[0] )
    cmds.parent( skin, WORLD_SPACE )
    cmds.setAttr( skin[0] + '.visibility', 0 )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    # place.setChannels( geo_grp[0], [True, False], [True, False], [True, False], [True, False, False] )

    # splines
    chain_splines()

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
    splineDistance = X * 0.55
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
    cmds.setAttr( splineAttr + '.' + splineName + 'Vis', 1 )
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
    joints_s = ['panel_00_L_jnt', 'panel_00_R_jnt', 'panelTop_00_L_jnt', 'panelTop_00_R_jnt']
    joints_e = ['panel_04_L_jnt', 'panel_04_R_jnt', 'panelTop_04_L_jnt', 'panelTop_04_R_jnt']
    names = ['panel_L_base', 'panel_R_base', 'panelTop_L_base', 'panelTop_R_base']
    splineEnd = ['master_Grp', 'master_Grp', 'panel_L_base_E_IK_Cntrl_Offst', 'panel_R_base_E_IK_Cntrl_Offst' ]
    shapes = ['splineStart_ctrl', 'splineEnd_ctrl', 'splineStart_ctrl', 'splineEnd_ctrl']
    #

    clrs = ['red', 'blue', 'red', 'blue']
    #
    X = 1
    for i in range( len( names ) ):
        # base control
        Nm = names[i]
        nm = place.Controller( Nm, joints_s[i], True, shapes[i], X * 100, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = clrs[i] )
        NmCt = nm.createController()
        # lock geo - [lock, keyable], [visible, lock, keyable]
        place.setChannels( NmCt[2], [True, False], [True, False], [True, False], [True, False, False] )
        cmds.parent( NmCt[0], '___CONTROLS' )
        cmds.parentConstraint( 'panel_Grp', NmCt[0], mo = True )
        # spline
        spline( name = names[i], root_jnt = joints_s[i], tip_jnt = joints_e[i], splinePrnt = NmCt[4], splineStrt = NmCt[4], splineEnd = splineEnd[i], splineAttr = NmCt[2], startSkpR = False, endSkpR = False, X = 5 )

    #
    '''
    cmds.setAttr( 'hub.ClstrMidIkBlend', 0 )
    # adjust rig for spline hub
    cmds.parentConstraint( 'hubX_Grp', 'chainX_S_IK_Cntrl', mo = True )
    cmds.setAttr( 'chainX_S_IK_Cntrl.visibility', 0 )'''


def fix_normals( del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    geo = get_geo_list()
    cmds.select( geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( geo, ch = True )


def get_geo_list():
    '''
    return requested geo list
    '''
    #
    geo = 'dmz103_corrugatedPanel_mdl_V001:pCube1'
    return [geo]

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

