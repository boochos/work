import imp
import os

from atom_face_lib import skn
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
import webrImport as web

#
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
jnt = web.mod( 'atom_joint_lib' )
anm = web.mod( "anim_lib" )
vhl = web.mod( 'vehicle_lib' )
app = web.mod( "atom_appendage_lib" )
ss = web.mod( "selectionSet_lib" )


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            print( what )


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


def mirror_jnts():
    '''
    
    '''
    # jnts - new joints for pivots
    mirrorj = [
    'front_L_jnt',
    'back_L_jnt',
    'propeller_01_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = False )


def ferry( name = 'ferry', geo_grp = 'ferry_grp', X = 1.1, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\ferry\\model\\maya\\scenes\\ferry_model_v004.ma' ):
    '''
    build ferry
    '''
    # ref geo
    if ns and ref_geo:
        vhl.reference_geo( ns = ns, path = ref_geo )
        # return
    #
    mirror_jnts()
    # return

    # hide
    # name = 'boat'
    hide = [
    'steer_TopGrp'
    ]

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    # SteerCt[4] = returned only if given as argument, otherwise this is returned: MasterCt[4], MoveCt[4]
    master_move_controls = vhl.vehicle_master( masterX = X * 8, moveX = X * 10, geo_grp = '' )
    # return

    #
    chassis_jnt = 'chassis_jnt'
    prop_l_jnt = 'propeller_02_L_jnt'
    prop_r_jnt = 'propeller_02_R_jnt'

    # skin
    chassis_geo = get_geo_list( name = name, ns = ns, chassis = True )
    vhl.skin( chassis_jnt, chassis_geo )
    prop_l = get_geo_list( name = name, ns = ns, prop_l = True )
    vhl.skin( prop_l_jnt, prop_l )
    prop_r = get_geo_list( name = name, ns = ns, prop_r = True )
    vhl.skin( prop_r_jnt, prop_r )
    # return
    # pivot_controls = [frontl, frontr, backl, backr, front, back] # entire controller hierarchy [0-4]
    pivot_controls = vhl.four_point_pivot( name = '', parent = master_move_controls[1], center = chassis_jnt, front = 'front_jnt', frontL = 'front_L_jnt', frontR = 'front_R_jnt', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', chassis_geo = '', X = X * 2, shapes = 'squareYup_ctrl' )
    # return
    #
    props( chassis_jnt = chassis_jnt, X = X * 14 )
    # return
    #
    # rudders( chassis_jnt = chassis_jnt, X = X * 14 )
    #
    for h in hide:
        cmds.setAttr( h + '.visibility', 0 )

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
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
    # uncommenting since no tires, should work, will find out when geo is ready
    misc.scaleUnlock( '___GEO', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, ns + ':' + geo_grp + s )  # geo is referenced
        # cmds.connectAttr( mstr + '.' + uni, '___GEO' + s ) ns = ns, path = ref_geo # geo group parented under ___GEO
        # cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush
    '''
    # HACK :
    # REF MODEL GROUP, LEAVE ALL GEO HEIRARCHY AS IS
    # TIRES GEO MUST BE IN WORLD SPACE, THEY ARE BEING DEFORMED VIA BLENDSHAPE
    # INSTEAD OF SCALING ENTIRE GROUP WITH RIG, SCALE INDIVIDUAL OBJECTS...
    all_geo = get_geo_list( name = name, ns = ns, all = True )
    tires = []
    # print( get_geo_list( name = name, tire_front_l = True ) )
    tires.append( get_geo_list( name = name, ns = ns, tire_front_l = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_front_r = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_back_l = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_back_r = True )[0] )
    # add dynamic parts
    # all_geo.append( Ct[1][0] )  # target control
    # all_geo.append( Ct[3] )  # follicle groupo
    #
    for geo in all_geo:
        if geo not in tires:
            for s in scl:
                cmds.connectAttr( mstr + '.' + uni, geo + s )
                '''


def props( chassis_jnt = '', X = 1.0 ):
    '''
    
    '''
    #
    # left
    clr = 'blue'
    j = 'propeller_02_L_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = chassis_jnt, rotations = [0, 0, 1], X = X, shape = 'facetZup_ctrl', color = clr )
    # right
    clr = 'red'
    j = 'propeller_02_R_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = chassis_jnt, rotations = [0, 0, 1], X = X, shape = 'facetZup_ctrl', color = clr )


def rudders( chassis_jnt = '', X = 1.0 ):
    '''
    
    '''
    #
    # left
    clr = 'blue'
    j = 'rudder_02_L_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'L', obj = j, objConstrain = True, parent = chassis_jnt, rotations = [0, 0, 1], X = X, shape = 'squareXup_ctrl', color = clr )
    # right
    clr = 'red'
    j = 'rudder_02_R_jnt'
    nm = j.split( '_' )[0]
    vhl.rotate_part( name = nm, suffix = 'R', obj = j, objConstrain = True, parent = chassis_jnt, rotations = [0, 0, 1], X = X, shape = 'squareXup_ctrl', color = clr )


def get_geo_list( name = '', ns = '', chassis = False,
                  prop_l = False, rudder_l = False,
                  prop_r = False, rudder_r = False,
                  all = False ):
    '''
    geo members via selection set
    '''
    geos = []
    geo_sets = []

    # chassis
    if chassis or all:
        geo_list = process_geo_list( name = name + '_' + 'chassis' )
        geo_sets.append( geo_list )

    # back l
    if prop_l or all:
        geo_list = process_geo_list( name = name + '_' + 'prop_l' )
        geo_sets.append( geo_list )
    '''
    if rudder_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rudder_l' )
        geo_sets.append( geo_list )
    '''
    # back r
    if prop_r or all:
        geo_list = process_geo_list( name = name + '_' + 'prop_r' )
        geo_sets.append( geo_list )
    '''
    if rudder_r or all:
        geo_list = process_geo_list( name = name + '_' + 'rudder_r' )
        geo_sets.append( geo_list )
    '''

    # build list
    for geo_set in geo_sets:
        for geo in geo_set:
            if ns:
                geos.append( ns + ':' + geo )
            else:
                geos.append( geo )

    return geos


def process_geo_list( name = '' ):
    '''
    
    '''
    s = []
    setDict = ss.loadDict( os.path.join( ss.defaultPath(), name + '.sel' ) )
    # print( setDict )
    for obj in setDict.values():
        s.append( obj )
    # print( s )
    return s


def passengers( X = 1 ):
    '''
    master with individual controls for each passenger
    add scale
    '''
    #
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = X )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    #
    root = 'root_jnt'
    place.cleanUp( root, SknJnts = True )
    cmds.parentConstraint( MasterCt[4], root, mo = True )
    #
    color = 'yellow'
    shape = 'facetYup_ctrl'
    shapeH = 'facetZup_ctrl'
    #
    jnts = [
    'Peter_root_jnt',
    'Paula_root_jnt',
    'Vojta_root_jnt',
    'Filip_root_jnt'
    ]
    names = [
    'Peter',
    'Paula',
    'Vojta',
    'Filip'
    ]
    # loop
    for i in range( len( jnts ) ):
        name = names[i]
        jnt = jnts[i]
        # butt
        name_Ct = place.Controller2( name, jnt, True, shape, X * 0.8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        place.cleanUp( name_Ct[0], Ctrl = True )
        cmds.parentConstraint( name_Ct[4], jnt, mo = True )
        cmds.parentConstraint( MasterCt[4], name_Ct[0], mo = False )
        # head
        head_Ct = place.Controller2( name + '_head', name + '_3_jnt', True, shapeH, X * 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        place.cleanUp( head_Ct[0], Ctrl = True )
        cmds.orientConstraint( head_Ct[4], name + '_3_jnt', mo = True )
        cmds.pointConstraint( name + '_3_jnt', head_Ct[0], mo = True )
        # pose
        place.hijackAttrs( name + '_1_jnt', name_Ct[2], 'rotateX', 'kneeBend', set = False, default = 60, force = True )
        place.hijackScaleMerge( name + '_root_jnt', name_Ct[2], mergeAttr = 'Scale' )
        cmds.setAttr( name_Ct[2] + '.Scale', 0.83 )

#
#
'''
imp.reload( web )
symd = web.mod( "assets_symd" )
symd.king_air()
'''
#
