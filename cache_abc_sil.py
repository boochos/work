import os
import time

import maya.cmds as cmds
import maya.mel as mel


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


def uiEnable( controls = 'modelPanel' ):
    model = cmds.lsUI( panels = True, l = True )
    ed = []
    for m in model:
        # print m
        if controls in m:
            ed.append( m )
    # ed sometimes contains modelPanels that arent attached to anything, use
    # loop with try to filter them out
    state = False
    for item in ed:
        try:
            state = cmds.control( item, q = 1, m = 1 )
            # print item
            break
        except:
            pass
    for p in ed:
        if cmds.modelPanel( p, q = 1, ex = 1 ):
            r = cmds.modelEditor( p, q = 1, p = 1 )
            if r:
                cmds.control( p, e = 1, m = not state )


def cache_abc( framePad = 5, frameSample = 1.0, forceType = False, camera = False, forceOverwrite = True, eulerFilter = True ):
    '''
    alembic cache selected object to assumed directory structure:
    
    P:\fov\fov100\FOV_099_290\assets\cameras
    P:\fov\fov100\FOV_099_290\assets\geo
    
    assumed file source:
    
    P:\fov\fov100\FOV_099_290\*\maya\scenes
    
    mel sample:
    AbcExport -j "-frameRange 1001 1100 -step 0.02 -attr vrayUserString_id -attr vrayUserScalar_shaderId -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root |cam_grp|trackGeo|SceneSolvedpoints -file P:/fov/fov100/FOV_099_290/layout/maya/cache/alembic/blah.abc";
    '''
    # assumed directories
    assets = 'assets'
    cameras = 'cameras'
    geo = 'geo'
    path_front = ''
    path_back = ''
    result = None

    # cache range
    start = cmds.playbackOptions ( ast = True, q = True )
    end = cmds.playbackOptions ( aet = True, q = True )
    start = start - framePad
    end = end + framePad
    # print( start, end )

    # selection qualify
    sel = cmds.ls( sl = 1 )
    # print( sel )
    if sel:
        sel = sel[0]
    else:
        message( 'Select 1 object', warning = True )
        return None

    # selection type
    if not forceType:
        camera = False
        shapes = cmds.listRelatives( sel, shapes = True )
        if shapes:
            for s in shapes:
                if cmds.objectType( s, isType = 'camera' ):
                    camera = True
                    break

    # build path_back
    if camera:
        path_back = os.path.join( assets, cameras )
    else:
        path_back = os.path.join( assets, geo )

    # print( path_back )

    # build path_front
    project = cmds.workspace( rd = True, q = True )
    parts = project.split( '/' )
    shot = parts[-4]  # isolate shot name
    path_front = project.split( shot )[0]
    path_front = os.path.join( path_front, shot )
    # print( path_front )

    # path destination
    path = os.path.join( path_front, path_back )
    # print( path )
    # create path if cam or geo doesnt exist
    if not os.path.exists( path ):
        # make version directory
        os.mkdir( path )

    # parse department
    dpt = project.split( '/' )[-3]
    # print( dpt )

    # parse scene version
    scenePath = cmds.file( sn = True, q = True )
    sceneName = ''
    if scenePath:
        sceneName = scenePath.split( '/' )[-1]
    else:
        message( 'Scene has no name', warning = True )
        return None
    sceneName = sceneName.split( '.' )[0]
    chunks = sceneName.split( '_' )
    # print( chunks )
    version = ''
    for chunk in chunks:
        if 'v' in chunk and len( chunk ) == 4:
            n = chunk.split( 'v' )[-1]
            try:
                n = int( n )
                # print( n )
                version = chunk
                # print( version )
                break
            except:
                # print( 'no', n )
                pass

    # version name / dir
    sel_name = ''
    if ':' in sel:
        sel_name = sel.replace( ':', '_' )
    else:
        sel_name = sel
    #
    version_name = shot + '_' + dpt + '_' + sel_name + '_' + version
    version_dir = shot + '_' + dpt + '_' + version
    #
    path = os.path.join( path, version_dir )
    # print( path )
    path = path.replace( '\\', '/' )
    if not os.path.exists( path ):
        # make version directory
        os.mkdir( path )
    path = os.path.join( path, version_name + '.abc' )
    path = path.replace( '\\', '/' )
    # print( path )

    # check if version exists
    version_qualified = False
    if forceOverwrite:
        version_qualified = True
    else:
        if not os.path.isfile( path ):
            # print( 'doesnt exist' )
            version_qualified = True

    # euler filter
    eulerString = ''
    if eulerFilter:
        eulerString = ' -eulerFilter'

    # turn off ui
    ui = True

    if version_qualified:

        # render layer
        abc_layer = 'abc_layer_tmp'
        lyr = cmds.createRenderLayer( sel, noRecurse = True, name = abc_layer, makeCurrent = True )
        # print( lyr )

        # command build
        m = 'AbcExport -j "-frameRange ' + str( int( start ) ) + ' ' + str( int( end ) ) + ' ' + '-step ' + str( float( frameSample ) ) + eulerString + ' -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root ' + sel + ' -file ' + path + '";'
        print( m )

        # ui off
        if ui:
            uiEnable()

        # execute and time
        start = time.time()
        mel.eval( m )
        end = time.time()
        elapsed = end - start
        # print( shot )
        path = path.replace( '/', '\\' )
        print( path )
        # message( 'Elapsed time: ' + str( elapsed ), warning = False )

        # ui on
        if ui:
            uiEnable()

        # render layer, delete
        cmds.editRenderLayerGlobals( currentRenderLayer = 'defaultRenderLayer' )
        cmds.delete( lyr )
    else:
        message( 'Version exists, not CACHED: ' + version_name, warning = True )
        result = sel

    return result
