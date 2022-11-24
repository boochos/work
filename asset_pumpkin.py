import os

import createWrap as cw
import maya.cmds as cmds
import webrImport as web

#
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
aul = web.mod( 'atom_ui_lib' )
anm = web.mod( "anim_lib" )
krl = web.mod( "key_rig_lib" )


def rig():
    '''
    
    '''
    # ref geo
    ns = pumpkin_ns()
    path = 'P:\\UW2\\assets\\props\\pumpkin\\model\\maya\\scenes\\pumpkin_model_v001.ma'
    cmds.file( path, reference = True, ns = ns )
    geo = ns + ':' + pumpkin_geo()

    # weights
    weights_meshImport()
    # delta
    cmds.deltaMush( geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    # rig
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 80 )
    #
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    cmds.parentConstraint( MasterCt[4], 'root_jnt', mo = True )

    # controls
    cv_shape = 'diamondZup_ctrl'
    colors = [ 'lightBlue', 'pink', 'hotPink', 'purple']
    X = 1
    for crv in outer_curves():
        #
        grp = cmds.group( name = crv + '_clstr_grp', em = True )
        cmds.setAttr( grp + '.visibility', 0 )
        place.cleanUp( grp, World = True )
        #
        clstrs = place.clstrOnCV( crv, clstrSuffix = crv )
        #
        i = 1
        for clstr in clstrs:
            cmds.parent( clstr, grp )
            cv_name = crv + '_clstr_' + str( i )
            cv_Ct = place.Controller2( cv_name, clstr, False, cv_shape, X * 1.0, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[0] ).result
            cmds.parentConstraint( cv_Ct[4], clstr, mo = True )
            cmds.parentConstraint( MasterCt[4], cv_Ct[0], mo = True )
            place.cleanUp( cv_Ct[0], Ctrl = True )
            i = i + 1

    for crv in inner_curves():
        cmds.parentConstraint( MasterCt[4], crv, mo = True )

    # cleanup
    for geo in nurbs():
        cmds.setAttr( geo + '.visibility', 0 )
        place.cleanUp( geo, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    for geo in nurbs():
        place.cleanUp( geo + 'Base', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    for geo in outer_curves():
        cmds.setAttr( geo + '.visibility', 0 )
        place.cleanUp( geo, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    for geo in inner_curves():
        cmds.setAttr( geo + '.visibility', 0 )
        place.cleanUp( geo, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    for geo in inner_curves():
        place.cleanUp( 'root_jnt', Ctrl = False, SknJnts = True, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )

    #
    fix_normals()


def pumpkin_ns():
    '''
    namespace
    '''
    return 'model'


def pumpkin_geo():
    '''
    geo names
    '''
    return 'pumpkin'


def nurbs():
    '''
    lofted surfaces from curves
    '''
    return [
    'eye_L_loft',
    'eye_R_loft',
    'nose_loft',
    'mouth_loft'
    ]


def outer_curves():
    '''
    curves used for lofting, create ribbon, surface of geo
    '''
    return [
    'eye_outer_L_crv',
    'eye_outer_R_crv',
    'nose_outer_crv',
    'mouth_outer_crv'
    ]


def inner_curves():
    '''
    curves used for lofting, create ribbon, inside geo
    '''
    return [
    'eye_inner_R_crv',
    'nose_inner_crv',
    'eye_inner_L_crv',
    'mouth_inner_crv'
    ]


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


def weights_meshExport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = pumpkin_geo()
    all_geo = [pumpkin_ns() + ':' + all_geo]
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        if ':' in g:
            g = g.split( ':' )[-1]
        ex_path = os.path.join( path, g )
        krl.exportMeshWeights( ex_path, geo, updatebar = True )


def weights_nurbsExport():
    '''
    exportNurbsCurveWeights( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        # krl.exportNurbsSurfaceWeights( ex_path, geo )
        krl.exportWeights02( geo, ex_path )


def weights_meshImport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = pumpkin_geo()
    all_geo = [pumpkin_ns() + ':' + all_geo]
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        if ':' in g:
            g = g.split( ':' )[-1]
        im_path = os.path.join( path, g )
        # krl.importMeshWeights( im_path, geo, updatebar = True )
        krl.importWeights02( geo, im_path )


def weights_nurbsImport():
    '''
    importNurbSurfaceWeights2( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importNurbSurfaceWeights2( im_path, geo )


def fix_normals( del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    all_geo = [pumpkin_ns() + ':' + pumpkin_geo()]
    cmds.select( all_geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in all_geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( all_geo, ch = True )


def softMod_control( name = 'top', geo = '', X = 10 ):
    '''
    
    '''
    cmds.select( geo )
    sm = cmds.softMod()  # [deformer, handle]
    cmds.setAttr( sm[0] + '.falloffAroundSelection', 0 )
    #
    cv_Ct = place.Controller2( name + '_softMod', sm[1], False, 'diamondYup_ctrl', X * 1.0, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.setAttr( cv_Ct[2] + '.ty', 12 )
    cmds.parentConstraint( 'master_Grp', cv_Ct[0], mo = True )
    place.cleanUp( cv_Ct[0], Ctrl = True )
    #
    cmds.connectAttr( cv_Ct[2] + '.tx', sm[0] + '.falloffCenterX' )
    # place.smartAttrBlend( master = 'master', slave = sm[0], masterAttr = 'tx', slaveAttr = 'falloffCenterX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False )
    cmds.connectAttr( cv_Ct[2] + '.ty', sm[0] + '.falloffCenterY' )
    cmds.connectAttr( cv_Ct[2] + '.tz', sm[0] + '.falloffCenterZ' )
    #
    place.hijackAttrs( sm[0], cv_Ct[3], 'falloffRadius', 'falloffRadius', set = True, default = 10, force = True )
    place.hijack( sm[1], cv_Ct[3], translate = True, rotate = True, scale = False, visibility = False )


def scale():
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
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush

'''
# pumpkin weights export
import webrImport as web
pmp = web.mod('asset_pumpkin')
pmp.weights_meshExport()

# pumpkin rig
import webrImport as web
pmp = web.mod('asset_pumpkin')
pmp.rig()

# path rig
import webrImport as web
ump = web.mod('universalMotionPath')
ump.path2(layers = 3)

# pumpkin rig
import webrImport as web
pmp = web.mod('asset_pumpkin')
geo = cmds.ls(sl=1)[0]
pmp.softMod_control(name='top', geo=geo)

# pumpkin rig
import webrImport as web
pmp = web.mod('asset_pumpkin')
geo = cmds.ls(sl=1)[0]
pmp.softMod_control(name='bottom', geo=geo)

# pumpkin rig scale
import webrImport as web
pmp = web.mod('asset_pumpkin')
pmp.scale()

'''
