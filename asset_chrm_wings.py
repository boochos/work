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


def wings( wingSplines = False ):
    # creates groups and master controller from arguments specified as 'True'
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 80 )

    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # geo import
    geo_path = 'P:\\CS4\\assets\\props\\Wings\\model\\maya\\scenes\\fairyWings_model_v001.ma'
    cmds.file( geo_path, i = True )

    # import nurbs weights
    weights_nurbsImport()

    # lists for joints and controllers
    geo_grp = 'wings_grp'
    # geo = 'dragonfly_grp|Dragonfly_body'
    # cmds.deltaMush( geo, smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    place.cleanUp( 'root_thorax_jnt', SknJnts = True )

    # Create COG Controller and clean up
    cog = 'Cog'
    cog = place.Controller( cog, 'root_thorax_jnt', orient = False, shape = 'facetZup_ctrl', size = 30.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cogCt = cog.createController()
    cogCt = cogCt
    place.cleanUp( cogCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'master_Grp', cogCt[0], mo = True )
    cmds.parentConstraint( cogCt[4], 'root_thorax_jnt', mo = True )

    winga = 'WingA'
    wnga = place.Controller( winga, 'wingA_jnt', orient = False, shape = 'arrow_ctrl', size = 10.25, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    wngaCt = wnga.createController()
    place.cleanUp( wngaCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cogCt[4], wngaCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngaCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngaCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    winga_l = 'WingA_L'
    wnga_l = place.Controller( winga_l, 'wingA_00_jnt_L', orient = True, shape = 'arrow_ctrl', size = 10.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
    wnga_lCt = wnga_l.createController()
    place.cleanUp( wnga_lCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngaCt[4], wnga_lCt[0], mo = True )
    cmds.parentConstraint( wnga_lCt[4], 'wingA_00_jnt_L', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wnga_lCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wnga_lCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    winga_r = 'WingA_R'
    wnga_r = place.Controller( winga_r, 'wingA_00_jnt_R', orient = True, shape = 'arrow_ctrl', size = 10.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'red' )
    wnga_rCt = wnga_r.createController()
    place.cleanUp( wnga_rCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngaCt[4], wnga_rCt[0], mo = True )
    cmds.parentConstraint( wnga_rCt[4], 'wingA_00_jnt_R', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wnga_rCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wnga_rCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    # return None
    wingb = 'WingB'
    wngb = place.Controller( wingb, 'wingB_jnt', orient = False, shape = 'arrow_ctrl', size = 10.25, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    wngbCt = wngb.createController()
    place.cleanUp( wngbCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cogCt[4], wngbCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngbCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngbCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    wingb_l = 'WingB_L'
    wngb_l = place.Controller( wingb_l, 'wingB_00_jnt_L', orient = True, shape = 'arrow_ctrl', size = 10.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
    wngb_lCt = wngb_l.createController()
    place.cleanUp( wngb_lCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngbCt[4], wngb_lCt[0], mo = True )
    cmds.parentConstraint( wngb_lCt[4], 'wingB_00_jnt_L', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngb_lCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngb_lCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    wingb_r = 'WingB_R'
    wngb_r = place.Controller( wingb_r, 'wingB_00_jnt_R', orient = True, shape = 'arrow_ctrl', size = 10.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True , colorName = 'red' )
    wngb_rCt = wngb_r.createController()
    place.cleanUp( wngb_rCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngbCt[4], wngb_rCt[0], mo = True )
    cmds.parentConstraint( wngb_rCt[4], 'wingB_00_jnt_R', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngb_rCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngb_rCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    # return None

    curveShapePath = 'C:\\Users\\sebas\\Documents\\maya\\controlShapes'

    # wing fk chain

    # wing util
    wngUtl = [
    'wingA_util_L',
    'wingA_util_R',
    'wingB_util_L',
    'wingB_util_R'
    ]
    wngMesh = [
    'Right_Small_Wing',
    'Left_Small_Wing',
    'Right_Big_Wing',
    'Left_Big_Wing'
    ]
    names = [
    'wingA_fk_L',
    'wingA_fk_R',
    'wingB_fk_L',
    'wingB_fk_R'
    ]
    fk_jnts = [
        ['wingA_00_jnt_L', 'wingA_05_jnt_L'],
        ['wingA_00_jnt_R', 'wingA_05_jnt_R'],
        ['wingB_00_jnt_L', 'wingB_05_jnt_L'],
        ['wingB_00_jnt_R', 'wingB_05_jnt_R']
        ]
    fk_prnts = [
        ['WingA_L_Grp', 'WingA_Grp'],
        ['WingA_R_Grp', 'WingA_Grp'],
        ['WingB_L_Grp', 'WingB_Grp'],
        ['WingB_R_Grp', 'WingB_Grp']
        ]
    i = 0
    for util in wngUtl:
        #
        cw.createWrap( util, wngMesh[i] )
        place.cleanUp( util, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = True, World = False, olSkool = False )
        place.cleanUp( util + 'Base', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        #
        if not wingSplines:
            color = 'blue'
            if '_R' in util:
                color = 'red'
            aRig = sfk.SplineFK( names[i], fk_jnts[i][0], fk_jnts[i][1], None,
                                      controllerSize = 10.5, rootParent = fk_prnts[i][0], parent1 = fk_prnts[i][1], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = color )
        i = i + 1

    if wingSplines:
        buildSplines( wingSplines = True )
    else:
        buildSplines( wingSplines = False )


def buildSplines( wingSplines = False ):
    '''\n
    Build splines for quadraped character\n
    '''
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 0.15

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

    if wingSplines:
        # WING A L
        neckName = 'WingA_L'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingA_L_Grp'
        neckStrt = 'WingA_L_Grp'
        neckEnd = 'WingA_L_Grp'
        neckAttr = 'WingA_L'  # pre-existing control name
        neck = ['wingA_01_jnt_L', 'wingA_05_jnt_L']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingA_LSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING A R
        neckName = 'WingA_R'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingA_R_Grp'
        neckStrt = 'WingA_R_Grp'
        neckEnd = 'WingA_R_Grp'
        neckAttr = 'WingA_R'  # pre-existing control name
        neck = ['wingA_01_jnt_R', 'wingA_05_jnt_R']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingA_RSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING B L
        neckName = 'WingB_L'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingB_L_Grp'
        neckStrt = 'WingB_L_Grp'
        neckEnd = 'WingB_L_Grp'
        neckAttr = 'WingB_L'  # pre-existing control name
        neck = ['wingB_01_jnt_L', 'wingB_05_jnt_L']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingB_LSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING B R
        neckName = 'WingB_R'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingB_R_Grp'
        neckStrt = 'WingB_R_Grp'
        neckEnd = 'WingB_R_Grp'
        neckAttr = 'WingB_R'  # pre-existing control name
        neck = ['wingB_01_jnt_R', 'wingB_05_jnt_R']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingB_RSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # scale
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
        # cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def wings_geo():
    '''
    geo names
    '''
    return [
    'Right_Small_Wing',
    'Left_Big_Wing',
    'Right_Big_Wing',
    'Left_Small_Wing'
    ]


def wings_nurbs():
    return [
    'wingA_util_L',
    'wingA_util_R',
    'wingB_util_R',
    'wingB_util_L'
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
    all_geo = wings_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        krl.exportMeshWeights( ex_path, geo, updatebar = True )


def weights_nurbsExport():
    '''
    exportNurbsCurveWeights( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = wings_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        krl.exportNurbsSurfaceWeights( ex_path, geo )


def weights_meshImport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = wings_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importMeshWeights( im_path, geo, updatebar = True )


def weights_nurbsImport():
    '''
    importNurbSurfaceWeights2( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = wings_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importNurbSurfaceWeights2( im_path, geo )


def renameJointSelection( name = '', pad = 2, suffix = '' ):
    sel = cmds.ls( sl = 1 )
    d = 1
    for i in sel:
        j = cmds.rename( i, name + '_' + str( ( '%0' + str( pad ) + 'd' ) % ( d ) ) + '_jnt' )
        if suffix:
            cmds.rename( j, j + '_' + suffix )
        d = d + 1
