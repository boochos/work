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
vcl = web.mod( "vehicle_lib" )
ac = web.mod( "animCurve_lib" )
# atl.path(segments=5, size=0.05, length=10)


def cadillac():
    '''
    build car
    '''
    vcl.car( name = 'cadillac', geo_grp = 'car_grp', frontSolidAxle = False, backSolidAxle = False, chassisAxleLock = False, X = 6.0,
            ns = 'geo',
            ref_geo = 'P:\\UW2\\assets\\veh\\cadillac\\model\\maya\\scenes\\cadillac_model_v010.ma' )


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
        cmds.select( "*:chassis_dynamicBase" )  # added for UW2
    sel = cmds.ls( sl = 1 )
    qualified_rigs = []
    n = None
    # qualify
    if sel:
        for s in sel:
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


def attachToPath():
    '''
    ref path and attach
    '''
    path = 'P:\\UW2\\assets\\util\\path\\rig\\maya\\scenes\\path_rig_v006.ma'
    cmds.file( path, reference = True, ns = 'path_rig' )
    cmds.select( ['cadillac_rig:move', 'path_rig:onPath_front' ] )
    vcl.car_to_path()


def selSets():
    vcl.create_geo_set_files( name = 'cadillac' )


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
    # print args
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
    print( geoCacheDir )
    if not os.path.exists( os.path.join( dataDir, 'alembic' ) ):
        os.mkdir( geoCacheDir )
    # make cache version directory
    versions = os.listdir( geoCacheDir )
    print( versions )
    if versions:
        nextVersion = s_foldername
        cacheVersionDir = geoCacheDir + s_foldername.replace( 'anim', 'abc' )  # modified this line to use scene name as folder name
        if not os.path.exists( cacheVersionDir ):
            os.mkdir( cacheVersionDir )
    else:
        cacheVersionDir = geoCacheDir + s_foldername.replace( 'anim', 'abc' )  # modified this line to use scene name as folder name
        os.mkdir( cacheVersionDir )
    print( cacheVersionDir )
    print( os.path.join( cacheVersionDir, s_filename.replace( 'anim', 'abc' ) ) )
    # return None
    leafs = cmds.ls( sl = True )
    print( leafs )
    #
    i = 1
    for leaf in leafs:
        leaf_stripped = leaf.split( ':' )[1]
        # print s_filename.replace( 'anim', 'abc__' + leaf_stripped + '_' )
        path = cacheVersionDir + '//' + s_filename.replace( 'anim', 'abc__' + leaf_stripped + '_' )
        path = path.replace( '.ma', '.abc' )
        if os.path.isfile( path ):
            path = path.replace( leaf_stripped, leaf_stripped + '_reuse' )
        print( path )
        m = 'AbcExport -j "-frameRange ' + str( int( start ) ) + ' ' + str( int( end ) ) + ' ' + '-attr vrayUserString_id -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root ' + leaf + ' -file ' + path + '";'
        print( m )
        mel.eval( m )
        i = i + 1

