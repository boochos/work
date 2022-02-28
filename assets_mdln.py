import glob
import imp
import os
import shutil
import time

# from pymel.core import *

from atom_face_lib import skn
import maya.cmds as cmds
import maya.mel as mel
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
pb = web.mod( "playblast_lib" )
ac = web.mod( "animCurve_lib" )
ffm = web.mod( "ffMpg" )
cas = web.mod( "cache_abc_sil" )
ds = web.mod( "display_lib" )
tp = web.mod( "togglePlate" )


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


def ferry( name = 'ferry', geo_grp = 'ferry_grp', X = 1.1, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\ferry\\model\\maya\\scenes\\ferry_model_v011.ma' ):
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
    geo_vis = [
    'geo:GTP_EMan_Peter_20_Stt_Drvg_Adl_Ccs_Gry',
    'geo:GTP_CWman_Paula_18_Stt_Clp_Obs_Sd_Adl_Asn',
    'geo:GTP_CMan_Vojta_03_Stt_Lsn_Adl_Ccs_Mgr',
    'geo:GTP_CMan_Filip_10_Stt_Exp_Adl_Ccs_Adl_Ccs_Mgr'
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
        cmds.pointConstraint( name + '_3_jnt', head_Ct[0], mo = True )
        cmds.orientConstraint( MasterCt[4], head_Ct[0], mo = True )
        cmds.orientConstraint( head_Ct[4], name + '_3_jnt', mo = True )
        # pose
        place.hijackAttrs( name + '_1_jnt', name_Ct[2], 'rotateX', 'kneeBend', set = False, default = 60, force = True )
        place.hijackScaleMerge( name + '_root_jnt', name_Ct[2], mergeAttr = 'Scale' )
        cmds.setAttr( name_Ct[2] + '.Scale', 0.83 )
        # visibility
        place.hijackAttrs( geo_vis[i], name_Ct[2], 'visibility', 'geoVis', set = False, default = 1, force = True )


def ref_cars( ref = False ):
    '''
    ref things
    '''
    #
    path = 'P:\\MDLN\\assets\\set\\setCorolla\\rig\\maya\\scenes\\setCorolla_rigCombined_v006.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setCorolla' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setHyundaiTucson\\rig\\maya\\scenes\\setHyundaiTucson_rigCombined_v003.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setHyundaiTucson' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMazda3\\rig\\maya\\scenes\\setMazda3_rigCombined_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMazda3' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMazdaCX7\\rig\\maya\\scenes\\setMazdaCX7_rigCombined_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMazdaCX7' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMercedesC63\\rig\\maya\\scenes\\setMercedesC63_rigCombined_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMercedesC63' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setToyotaRav4\\rig\\maya\\scenes\\setToyotaRav4_rigCombined_v003.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setToyotaRav4' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setVolkswagenPassat\\rig\\maya\\scenes\\setVolkswagenPassat_rigCombined_v008.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setVolkswagenPassat' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\2019ToyotaRav4\\rig\\maya\\scenes\\2019ToyotaRav4_rigCombined_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = '2019ToyotaRav4' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\AcuraMdx\\rig\\maya\\scenes\\AcuraMdx_rigCombined_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'AcuraMdx' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\MazdaCx5\\rig\\maya\\scenes\\MazdaCx5_rigCombined_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'MazdaCx5' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\MercedesSprinter\\rig\\maya\\scenes\\MercedesSprinter_rigCombined_v006.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'MercedesSprinter' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\Toyota4runner\\rig\\maya\\scenes\\Toyota4runner_rigCombined_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'Toyota4runner' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\Truck\\rig\\maya\\scenes\\Truck_rigCombined_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'Truck' )
    else:
        print( 'no___', path )


def ref_cars_passengers( ref = False ):
    '''
    ref things
    '''
    #
    path = 'P:\\MDLN\\assets\\set\\setCorolla\\rig\\maya\\scenes\\setCorolla_rigPassengers_v006.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setCorolla' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setHyundaiTucson\\rig\\maya\\scenes\\setHyundaiTucson_rigPassengers_v003.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setHyundaiTucson' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMazda3\\rig\\maya\\scenes\\setMazda3_rigPassengers_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMazda3' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMazdaCX7\\rig\\maya\\scenes\\setMazdaCX7_rigPassengers_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMazdaCX7' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setMercedesC63\\rig\\maya\\scenes\\setMercedesC63_rigPassengers_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setMercedesC63' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setToyotaRav4\\rig\\maya\\scenes\\setToyotaRav4_rigPassengers_v003.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setToyotaRav4' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\set\\setVolkswagenPassat\\rig\\maya\\scenes\\setVolkswagenPassat_rigPassengers_v008.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'setVolkswagenPassat' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\2019ToyotaRav4\\rig\\maya\\scenes\\2019ToyotaRav4_rigPassengers_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = '2019ToyotaRav4' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\AcuraMdx\\rig\\maya\\scenes\\AcuraMdx_rigPassengers_v004.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'AcuraMdx' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\MazdaCx5\\rig\\maya\\scenes\\MazdaCx5_rigPassengers_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'MazdaCx5' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\MercedesSprinter\\rig\\maya\\scenes\\MercedesSprinter_rigPassengers_v006.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'MercedesSprinter' )
    else:
        print( 'no___', path )
    #
    path = 'P:\\MDLN\\assets\\veh\\Toyota4runner\\rig\\maya\\scenes\\Toyota4runner_rigPassengers_v005.ma'
    if os.path.isfile( path ):
        print( path )
        if ref:
            cmds.file( path, reference = True, namespace = 'Toyota4runner' )
    else:
        print( 'no___', path )


def set_for_animation():
    '''
    
    '''
    # dynamics
    try:
        cmds.select( "*:*:chassis_dynamicTarget" )
        sel = cmds.ls( sl = 1 )
        for s in sel:
            cmds.setAttr( s + '.dynamicParentOffOn', 0 )
            cmds.setAttr( s + '.enable', 0 )
    except:
        pass
    # tires
    try:
        cmds.select( "*:*:move" )
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                cmds.setAttr( s + '.tireGeo', 0 )
                cmds.setAttr( s + '.tireProxy', 1 )
    except:
        pass
    # traffic tires
    try:
        cmds.select( "*:*:*:move" )
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                cmds.setAttr( s + '.tireGeo', 0 )
                cmds.setAttr( s + '.tireProxy', 1 )
    except:
        pass
    # time
    cmds.playbackOptions( minTime = 1001 )
    cmds.playbackOptions( animationStartTime = 1001 )


def set_all_dynamics():
    '''
    
    '''
    # time
    cmds.playbackOptions( minTime = 970 )
    cmds.playbackOptions( animationStartTime = 970 )
    # dynamics
    cmds.select( clear = True )
    try:
        cmds.select( "*:*:chassis_dynamicTarget" )
    except:
        pass
    sel = cmds.ls( sl = 1 )
    if sel:
        for s in sel:
            cmds.setAttr( s + '.dynamicParentOffOn', 1 )
            cmds.setAttr( s + '.enable', 1 )
            cmds.setAttr( s + '.startFrame', 970 )


def set_obj_dynamics( obj = '', on = False ):
    '''
    
    '''
    if on:
        cmds.setAttr( obj + '.dynamicParentOffOn', 1 )
        cmds.setAttr( obj + '.enable', 1 )
        cmds.setAttr( obj + '.startFrame', 970 )
    else:
        cmds.setAttr( obj + '.dynamicParentOffOn', 0 )
        cmds.setAttr( obj + '.enable', 0 )
        cmds.setAttr( obj + '.startFrame', 970 )


def set_for_playblast( dynamics = False, tires = False ):
    '''
    
    '''
    # time
    cmds.playbackOptions( minTime = 1001 )
    cmds.playbackOptions( animationStartTime = 1001 )
    # dynamics
    if dynamics:
        # delete anim
        transform = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        try:
            cmds.select( "*:*:chassis_dynamicBase" )
            sel = cmds.ls( sl = 1 )
            #
            if sel:
                for s in sel:
                    if rig_qualified_to_bake( s ):
                        ac.deleteAnim2( s, attrs = transform )
                        for i in transform:
                            cmds.setAttr( s + '.' + i, 0 )
                # set
                set_all_dynamics()
        except:
            pass
    # tires
    if tires:
        try:
            cmds.select( "*:*:move" )
            sel = cmds.ls( sl = 1 )
            if sel:
                for s in sel:
                    cmds.setAttr( s + '.tireGeo', 1 )
                    cmds.setAttr( s + '.tireProxy', 0 )
        except:
            pass
        # traffic tires
        try:
            cmds.select( "*:*:*:move" )
            sel = cmds.ls( sl = 1 )
            if sel:
                for s in sel:
                    cmds.setAttr( s + '.tireGeo', 1 )
                    cmds.setAttr( s + '.tireProxy', 0 )
        except:
            pass


def renderLayerBlast():
    '''
    using animPublish file
    *:*:geo:*
    '''
    # clear selection
    cmds.select( cl = 1 )

    path = cmds.file( query = True, exn = True )
    print( path )
    subDir = ''
    cars = False
    if '101_001' in path or '101_027' in path:
        # ferry shot
        subDir = 'ferryAnimBty'
    else:
        # bridge shot
        subDir = 'carAnimBty'
        cars = True
    #
    if '_animPublish_' in path:
        path = path.replace( '_animPublish_', '_anim_' )
        # rename the current file
        cmds.file( path, rn = path )

    # rename the current file
    # cmds.file( path, rn = path )

    # geo
    go = True
    geoAll = []
    if cars:
        # env
        cmds.select( 'Bridge:*' )
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                geoAll.append( s )
        else:
            print( 'no sel, env' )
        cmds.setAttr( '____env.visibility', 1 )
        # hero cars
        cmds.select( clear = 1 )
        try:
            cmds.select( '*:*:geo:*' )
        except:
            pass
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                if ':geo:' in s and 'f[' not in s:
                    geoAll.append( s )
        else:
            print( 'no sel, hero cars' )
        # traffic cars
        cmds.select( clear = 1 )
        try:
            cmds.select( '*:*:*:geo:*' )
        except:
            pass
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                if ':geo:' in s and 'f[' not in s:
                    geoAll.append( s )
        else:
            print( 'no sel, traffic cars' )
    else:
        # ferry
        cmds.select( '*:geo:ferry_grp' )
        cmds.select( 'directionalLight1', add = True )
        sel = cmds.ls( sl = 1 )
        if sel:
            for s in sel:
                geoAll.append( s )

    #
    if geoAll:
        #
        existing_layers = cmds.ls( type = 'renderLayer' )
        if subDir not in existing_layers:
            cmds.select( geoAll )
            lyr = cmds.createRenderLayer( name = subDir, makeCurrent = True )
            cmds.select( cl = 1 )
        else:
            cmds.editRenderLayerGlobals( crl = subDir )
        #
        pnl = cmds.getPanel( withFocus = True )
        try:
            cmds.editRenderLayerGlobals( crl = subDir )
        except:
            go = False
        #
        if go:
            set_for_playblast( dynamics = False, tires = True )
            cmds.setFocus( pnl )
            cmds.currentTime( 1002 )
            cmds.currentTime( 1001 )
            cmds.select( clear = 1 )
            result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = subDir, play = False )
            print( result )  # [u'C:/Users/sebas/Documents/maya/__PLAYBLASTS__\\101_009_0100_animPublish_v014\\101_009_0100_animPublish_v014_carAnimBty', u'101_009_0100_animPublish_v014_carAnimBty']
            mp4 = ffm.imgToMp4( pathIn = result[0], image = result[1], start = 1001, pathOut = result[0], pathOutName = result[1] )
            pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_' + subDir )

            #
            cmds.editRenderLayerGlobals( currentRenderLayer = 'defaultRenderLayer' )
            cmds.delete( lyr )
        else:
            message( 'go == False, skipping shot', warning = True )
    else:
        message( 'no car geo found, skipping shot', warning = True )


def witness_camera():
    '''
    
    '''
    #
    result = cmds.ls( type = 'camera', o = 1 )
    for r in result:
        p = cmds.listRelatives( r, parent = 1 )
        if p:
            if ':witness_cam' in p[0]:
                return p[0]


def witness_plate( on = True ):
    '''
    
    '''
    cam = camName()
    #
    st = 0
    if on:
        st = 3
    #
    if cam:
        #
        connections = cmds.listConnections( cam, sh = True, t = 'imagePlane' )
        print( connections )
        #
        if connections:
            connections = list( set( connections ) )
            plates = platesOnly( connections )
            #
            for plate in plates:
                p = plate.split( '->' )[1]
                if ':' not in p:
                    cmds.setAttr( p + '.displayMode', st )
                    cmds.setAttr( p + '.frameCache', 0 )
        else:
            message( 'No plates' )
    else:
        message( 'Not a camera' )


def camName():
    pnl = cmds.getPanel( withFocus = True )
    typ = cmds.getPanel( typeOf = pnl )
    if typ == 'modelPanel':
        cam = cmds.modelPanel( pnl, q = True, cam = True )
        if cam:
            typ = cmds.objectType( cam )
            if typ == 'camera':
                return cam
            else:
                if typ == 'transform':
                    trans = PyNode( cam )
                    # get the transform's shape, aka the camera node
                    cam = trans.getShape()
                    return str( cam )
        else:
            # print 'no model returned', cam
            pass
    else:
        # print 'not model panel', pnl
        pass


def platesOnly( connections ):
    plates = []
    for item in connections:
        if cmds.nodeType( item ) == 'imagePlane':
            plates.append( item )
    return plates


def witness_blast():
    '''
    for ferry, prfile view
    using animPublish file
    *:*:geo:*
    '''
    # clear selection
    cmds.select( cl = 1 )

    path = cmds.file( query = True, exn = True )
    print( path )
    subDir = ''
    cars = False
    if '101_001' in path:
        # ferry shot
        subDir = 'ferryWitness'
    #
    if '_animPublish_' in path:
        path = path.replace( '_animPublish_', '_anim_' )
        # rename the current file
        cmds.file( path, rn = path )

    # geo
    go = True
    geoAll = []

    # ferry
    cmds.select( clear = True )
    cmds.select( '*:geo:ferry_grp' )
    cmds.select( 'directionalLight1', add = True )
    cmds.select( '*:witness_cam', add = True )
    cmds.select( '*:cam_grp', add = True )
    sel = cmds.ls( sl = 1 )
    if sel:
        for s in sel:
            geoAll.append( s )

    #
    lyr = None
    if geoAll:
        #
        existing_layers = cmds.ls( type = 'renderLayer' )
        if subDir not in existing_layers:
            cmds.select( geoAll )
            lyr = cmds.createRenderLayer( name = subDir, makeCurrent = True )
            cmds.select( cl = 1 )
        else:
            lyr = subDir
            cmds.editRenderLayerGlobals( crl = subDir )
        #
        pnl = cmds.getPanel( withFocus = True )
        cam = cmds.modelPanel( pnl, q = True, camera = True )
        wit_cam = witness_camera()
        cmds.setAttr( wit_cam + '.nearClipPlane', 100 )
        cmds.modelPanel( pnl, e = True, cam = wit_cam )
        mel.eval( 'modelEditor -e -udm true ' + pnl + ';' )
        mel.eval( 'modelEditor -e -dl "default" ' + pnl + ';' )
        try:
            cmds.editRenderLayerGlobals( crl = subDir )
        except:
            go = False
        #
        if go:
            set_for_playblast( dynamics = False, tires = True )
            cmds.setFocus( pnl )
            cmds.currentTime( 1002 )
            cmds.currentTime( 1001 )
            cmds.select( clear = 1 )
            result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = subDir, play = False )
            print( result )  # [u'C:/Users/sebas/Documents/maya/__PLAYBLASTS__\\101_009_0100_animPublish_v014\\101_009_0100_animPublish_v014_carAnimBty', u'101_009_0100_animPublish_v014_carAnimBty']
            mp4 = ffm.imgToMp4( pathIn = result[0], image = result[1], start = 1001, pathOut = result[0], pathOutName = result[1] )
            result = pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_' + subDir )
            #
            source = result[0]
            print( source )
            path = cmds.file( query = True, exn = True )
            sht = path.rsplit( '/', 1 )[1].split( '.' )[0]
            sht = sht.replace( '_anim_', '_anim_' + subDir + '_' )
            print( sht )
            dest = path.split( 'maya' )[0]
            dest = os.path.join( dest, 'playblasts' )
            dest = os.path.join( dest, sht )
            print( dest )
            if os.path.isdir( dest ):
                shutil.rmtree( dest )
            shutil.copytree( source.replace( '\\', '/' ), dest.replace( '\\', '/' ) )
            shutil.rmtree( source.replace( '\\', '/' ) )

            #
            cmds.modelPanel( pnl, e = True, cam = cam )
            mel.eval( 'modelEditor -e -udm false ' + pnl + ';' )
            mel.eval( 'modelEditor -e -dl "all" ' + pnl + ';' )
            cmds.editRenderLayerGlobals( currentRenderLayer = 'defaultRenderLayer' )
            cmds.delete( lyr )
        else:
            message( 'go == False, skipping shot', warning = True )
    else:
        message( 'no ferry geo found, skipping shot', warning = True )


def blast( dynamics = False, burn_in = True ):
    '''
    
    '''
    start = 1001

    # res
    special_shot = '101_009_1000'
    special_shot2 = '101_001_'
    special_shot3 = '101_027_'
    special_shot4 = '101_009_0310'
    path = cmds.file( query = True, exn = True )
    # resolution
    if special_shot in path or special_shot2 in path or special_shot3 in path or special_shot4 in path:
        cmds.setAttr( 'defaultResolution.width', 3840 )
        cmds.setAttr( 'defaultResolution.height', 2160 )
    else:
        cmds.setAttr( 'defaultResolution.width', 4448 )
        cmds.setAttr( 'defaultResolution.height', 3096 )
    # ferry or bridge
    if special_shot2 in path or special_shot3 in path:
        special_shot2 = True
    else:
        special_shot2 = False

    # blast
    set_for_playblast( dynamics = dynamics )

    #
    # witness_plate( on = False )
    '''
    if special_shot2:
        witness_blast()'''
        # return

    #
    if burn_in:
        # blast
        #
        #
        if special_shot2:
            # witness_plate( on = True )
            result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = 'precomp', play = False )  # blastPath, blastName
            # to mp4
            pathOut = result[0].replace( result[1], '' )
            pathOutName = result[1].replace( '_precomp', '____cam' )  # added cam string, burnin expects cam suffix
            mp4 = ffm.imgToMp4( pathIn = result[0], image = result[1], start = start, pathOut = pathOut, pathOutName = pathOutName )
            # copy mp4 to image seq directory, matching name
            shutil.copyfile( mp4, os.path.join( result[0], result[1] + '.mp4' ) )
            print( result[0] )
            shutil.rmtree( result[0] )
            # add burn in
            ffm.burn_in( filein = mp4, startFrame = start, size = 35, rndrFrames = False )
            # witness_plate( on = False )
        #
        #
        # return
        cmds.select( clear = 1 )
        result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = 'precomp', play = False )  # blastPath, blastName
        # to mp4
        if not special_shot2:
            pathOut = result[0].replace( result[1], '' )
            pathOutName = result[1].replace( '_precomp', '____cam' )  # added cam string, burnin expects cam suffix
        else:
            pathOut = result[0]
            pathOutName = result[1]
        mp4 = ffm.imgToMp4( pathIn = result[0], image = result[1], start = start, pathOut = pathOut, pathOutName = pathOutName )
        if not special_shot2:
            # copy mp4 to image seq directory, matching name
            shutil.copyfile( mp4, os.path.join( result[0], result[1] + '.mp4' ) )
            # add burn in
            ffm.burn_in( filein = mp4, startFrame = start, size = 35, rndrFrames = False )
        # move precomp string in all image seq names, including new copied mp4
        pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_precomp' )
        # beauty blast with qt
        renderLayerBlast()
        # witness_plate( on = True )
    else:
        # expecting traffic shots from bridge
        result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = '', play = False )  # blastPath, blastNam
        source = result[0]
        print( source )
        path = cmds.file( query = True, exn = True )
        sht = path.rsplit( '/', 1 )[1].split( '.' )[0]
        print( sht )
        dest = path.split( 'maya' )[0]
        dest = os.path.join( dest, 'playblasts' )
        dest = os.path.join( dest, sht )
        print( dest )
        if os.path.isdir( dest ):
            shutil.rmtree( dest )
        shutil.copytree( source.replace( '\\', '/' ), dest.replace( '\\', '/' ) )

        # pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_traffic' )
    #
    set_for_animation()


def rig_qualified_to_bake( obj = '' ):
    '''
    if object moving on path, qualified
    '''
    pth = 'pth'
    ns = obj.split( ":", 1 )[0]
    onPath_front = ns + ':' + pth + ':onPath_front'
    if cmds.objExists( onPath_front ):
        animCurves = cmds.findKeyframe( onPath_front, c = True )
        if animCurves:
            # print( 'bake', ns )
            return True
        else:
            # print( 'no bake', ns )
            return False
    else:
        return False


def shot_qualified_to_bake( path = '' ):
    '''
    
    '''
    shots = [ '101_009_0300', '101_009_0400', '101_009_0500', '101_009_0700']
    for s in shots:
        if s in path:
            return True
    return False


def bake_dynamics():
    '''

    '''
    #
    cmds.playbackOptions( minTime = 970 )
    cmds.playbackOptions( animationStartTime = 970 )
    #
    transform = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    cmds.select( clear = 1 )
    try:
        cmds.select( "*:*:chassis_dynamicBase" )
    except:
        pass
    sel = cmds.ls( sl = 1 )
    qualified_rigs = []
    n = None
    # qualify
    if sel:
        for s in sel:
            if rig_qualified_to_bake( s ):
                ac.deleteAnim2( s, attrs = transform )
                for i in transform:
                    cmds.setAttr( s + '.' + i, 0 )
                #
                ref = s.rsplit( ':', 1 )[0]
                set_obj_dynamics( ref + ':chassis_dynamicTarget', on = True )
                qualified_rigs.append( ref + ':chassis_dynamicTarget' )
    #
    if qualified_rigs:
        print( qualified_rigs )
        cmds.select( qualified_rigs )
        # store
        n = anm.SpaceSwitchList()
        # restore
        for q in qualified_rigs:
                set_obj_dynamics( q, on = False )
        n.restore()
    #
    cmds.playbackOptions( minTime = 1001 )
    cmds.playbackOptions( animationStartTime = 1001 )


def load_offloaded( find = '' ):
    '''
    pplRN
    '''
    #
    rfs = cmds.ls( typ = 'reference' )
    for ref in rfs:
        stt = True
        try:
            stt = cmds.referenceQuery( ref, isLoaded = True )
        except:
            pass
        if not stt:
            if find:
                if find in ref:
                    cmds.file( lr = ref, lrd = 'all' )
            else:
                cmds.file( lr = ref, lrd = 'all' )


def offload_loaded( find = '' ):
    '''
    pplRN
    '''
    #
    rfs = cmds.ls( typ = 'reference' )
    for ref in rfs:
        stt = False
        try:
            stt = cmds.referenceQuery( ref, isLoaded = True )
        except:
            pass
        if stt:
            if find:
                if find in ref:
                    cmds.file( ur = ref )
            else:
                cmds.file( ur = ref )


def save_publish( find = '_anim_', addSuffix = '_animPublish_' ):
    '''
    add suffix to scene, save
    '''
    # current name, path
    path = cmds.file( query = True, exn = True )
    print( path )
    if find in path:
        path = path.replace( find, addSuffix )
    print( path )
    #
    # get the current file type
    if cmds.file( sn = True , q = True ):
        fileType = cmds.file( query = True, typ = True )
    else:
        fileType = ['mayaAscii']
    # add the file about to be saved to the recent files menu
    mel.eval( 'addRecentFile "' + path + '" ' + fileType[0] + ';' )
    # rename the current file
    cmds.file( path, rn = path )
    # save it
    cmds.file( save = True, typ = fileType[0] )


def publish( full = True ):
    '''
    publish: playblast and save maya scene version
    '''
    # start timer
    start = time.time()

    # publish layout, cam, proxies
    success = publish_layout()

    #
    ferry = False
    special_shot = '101_001_'
    path = cmds.file( query = True, exn = True )
    if special_shot in path:
        ferry = True

    #
    if success and full:

        if not ferry:
            # bake dynamics
            if shot_qualified_to_bake( path ):
                bake_dynamics()
            #
            load_offloaded()  # all
            offload_loaded( find = 'pplRN' )  # remove people
            blast()
            set_for_playblast( tires = True )
        else:
            blast()
        save_publish()
        if cmds.objExists( 'directionalLight1' ):
            cmds.setAttr( 'directionalLight1.visibility', 0 )

    # end timer
    end = time.time()
    elapsed = end - start
    print( 'Publish time: ' + str( elapsed / 60 ) + ' min' )


def publish_layout():
    '''
    
    '''
    #
    setProxies = 'setProxies'
    special_shot = '101_001_'
    special_shot1 = '101_027_'
    path = cmds.file( query = True, exn = True )
    if special_shot in path or special_shot1 in path:
        setProxies = 'cam_grp'
    #
    cams = publish_cameras()
    if cams:
        ns = cams[0].split( ':' )[0]
        proxy = ns + ':' + setProxies
        if cmds.objExists( proxy ):
            publish_proxies( proxies = [proxy] )
            return True
        else:
            print( 'proxy fail: ', proxy )
    else:
        print( 'cams fail: ', cams )
    return False


def publish_cameras():
    '''
    
    '''
    exclude = ['front', 'persp', 'side', 'top']
    cams = []
    result = cmds.ls( type = 'camera', o = 1 )
    for r in result:
        p = cmds.listRelatives( r, parent = 1 )
        if p:
            if p[0] not in exclude and 'cam_follow' not in p[0] and 'witness_cam' not in p[0]:
                cams.append( p[0] )
    print( cams )
    for cam in cams:
        cmds.select( cam )
        cas.cache_abc( framePad = 5, frameSample = 0.25, forceType = False, camera = True, forceOverwrite = True )
    return cams


def publish_proxies( proxies = [] ):
    '''
    
    '''
    for p in proxies:
        cmds.select( p )
        cas.cache_abc( framePad = 5, frameSample = 1.0, forceType = False, camera = False, forceOverwrite = True )
    cmds.select( clear = 1 )


def publish_all_layouts( publish_layouts = False, publish_full = False ):
    '''
    find latest files in assumed shots, publish cameras and proxies 
    '''
    # start timer
    start = time.time()

    shots = [
        'P:\\MDLN\\101\\101_009_0100\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0200\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0300\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0400\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0500\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0700\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0800\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_0900\\anim\\maya\\',
        'P:\\MDLN\\101\\101_009_1000\\anim\\maya\\'
        ]
    '''
    shots = [
        'P:\\MDLN\\101\\101_009_0100\\anim\\maya\\'
        ]'''
    # cache
    for project_path in shots:
        project_path = project_path.replace( '\\', '/' )
        # set project
        mel_command = ( 'setProject "' + project_path + '";' )
        mel.eval( mel_command )
        mel.eval( 'print \" -- Project set to  -- ' + project_path + ' -- \";' )
        # latest scene
        scenes_path = os.path.join( project_path, 'scenes' )
        list_of_files = glob.glob( os.path.join( scenes_path, '*.ma' ) )  # * means all if need specific format then *.csv
        filtered_list = []
        for f in list_of_files:
            if 'Traffic' not in f and 'Publish' not in f:
                filtered_list.append( f )
        latest_file = max( filtered_list, key = os.path.getctime )
        # print( latest_file )
        # open latest
        latest_file_path = os.path.join( scenes_path, latest_file )
        print( latest_file_path )
        # publish type
        if publish_layouts and not publish_full:
            # file existance
            if os.path.isfile( latest_file_path ):
                cmds.file( latest_file_path, open = True, force = True )
                publish( full = False )
        elif publish_full and not publish_layouts:
            # file existance
            if os.path.isfile( latest_file_path ):
                cmds.file( latest_file_path, open = True, force = True )
                # find camera for playblast before starting full publish
                camera = look_through_publish_camera()
                if camera:
                    publish( full = True )
                else:
                    print( 'Quitting. Couldnt find camera for scene: ', latest_file_path )
                    break
        else:
            if os.path.isfile( latest_file_path ):
                print( 'is file... options not set to publish.' )

    # end timer
    end = time.time()
    elapsed = end - start
    print( 'Shots Publish time: ' + str( elapsed / 60 ) + ' min' )


def look_through_publish_camera():
    '''
    
    '''
    exclude = ['front', 'persp', 'side', 'top']
    cams = []
    result = cmds.ls( type = 'camera', o = 1 )
    for r in result:
        p = cmds.listRelatives( r, parent = 1 )
        if p:
            if p[0] not in exclude and 'cam_follow' not in p[0] and 'renderCam' not in p[0] and ':' in p[0]:
                cams.append( p[0] )
    if len( cams ) == 1:
        cmds.lookThru( 'perspView', cams[0] )
        ds.toggleObjectDisplay( purpose = 'cam' )
        tp.platesAllOn()
        print( 'playblast camera: ', cams[0] )
        return cams[0]
    else:
        print( 'too many cameras' )
    print( cams )
    return None


#
geo_grps = [
    'setCorolla_grp',
    'setHyundaiTuscon_grp',
    'mazda3_grp',
    'mazda_cx_7_grp',
    'merc_grp',
    'toyotaRav4_grp',
    'setVolkswagenPassat_grp',
    'Toyota_RAV4',
    'acuraMdx_grp',
    'mazdaCx5_grp',
    'mercedesSprinter_grp',
    'Toyota4Runner_grp',
    'Truck_grp'
    ]
#
'''
# people off
cmds.select('*:*:*:driver_grp')
sel = cmds.ls(sl=1)
for s in sel:
    cmds.setAttr(s + '.visibility', 0)
# people on
cmds.select('*:*:*:driver_grp')
sel = cmds.ls(sl=1)
for s in sel:
    cmds.setAttr(s + '.visibility', 1)


# select path masters
cmds.select('*:pth:master')



imp.reload( web )
symd = web.mod( "assets_symd" )
symd.king_air()
'''
#
