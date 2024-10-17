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


def cache_abc( framePad = 5, frameSample = 1.0, forceType = False, camera = False, forceOverwrite = True, eulerFilter = True, useFile = True ):
    '''
    alembic cache selected object to assumed directory structure:
    
    P:\fov\fov100\FOV_099_290\assets\cameras
    P:\fov\fov100\FOV_099_290\assets\geo
    
    assumed file source:
    
    P:\fov\fov100\FOV_099_290\*\maya\scenes
    
    mel sample:
    AbcExport -j "-frameRange 1001 1100 -step 0.02 -attr vrayUserString_id -attr vrayUserScalar_shaderId -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa -root |cam_grp|trackGeo|SceneSolvedpoints -file P:/fov/fov100/FOV_099_290/layout/maya/cache/alembic/blah.abc";
    '''
    # print( '____START' )
    # assumed directories
    assets = 'assets'
    cameras = 'cameras'
    geo = 'geo'
    path_front = ''
    path_back = ''
    result = None
    suffix = ''

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
    scene_path = cmds.file( query = True, exn = True )
    project = cmds.workspace( rd = True, q = True )
    # print( project )
    if project not in scene_path:
        message( 'Scene path and Project path mismatch. --- Parsing project path from Scene path', warning = True )
        project = scene_path.split( 'scenes' )[0]
    parts = project.split( '/' )
    # print( parts )
    scene_name_raw = scene_path.rsplit( '/', 1 )[1].split( '.' )[0]  # file name
    shot = parts[-4]  # isolate shot name
    task = parts[-3]
    if shot in scene_name_raw and task in scene_name_raw:  # assume name is standardized, go look for suffix
        suffix = filename_getSuffix( task )
    else:
        # print( 'NO !' )
        # print( shot )
        # print( scene_name_raw )
        # print( task )
        # print( scene_name_raw )
        pass
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
    # pipe removal
    if '|' in sel:
        sel_name = sel_name.replace( '|', '_' )
    # print( sel_name, 'HERE' )
    # return
    #
    if useFile:
            version_name = sel_name
            version_dir = scene_name_raw
    else:
        if qualify_filename() == [True, True, True]:  # project match, scene saved, naming conventions
            if suffix:
                version_name = shot + '_' + task + '_' + suffix + '_' + sel_name + '_' + version
                version_dir = shot + '_' + task + '_' + suffix + '_' + version
            else:
                version_name = shot + '_' + task + '_' + sel_name + '_' + version
                version_dir = shot + '_' + task + '_' + version
        else:  # use file name instead
            version_name = sel_name
            version_dir = scene_name_raw

    # print( version_name )
    # return
    #
    path = os.path.join( path, version_dir )
    # print( path )
    path = path.replace( '\\', '/' )
    if not os.path.exists( path ):
        # make version directory
        os.mkdir( path )
    path = os.path.join( path, version_name + '.abc' )
    path = path.replace( '\\', '/' )
    # print( path, '________here' )
    # return

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
        # print( path )
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


def filename_getSuffix( task = '' ):
    '''
    
    '''
    #
    suffix = ''
    s_path = cmds.file( query = True, sn = True )
    if s_path:
        if s_path[-8:] != 'untitled':
            if 'v' == s_path[-7]:
                s_path = s_path.split( '/' )[-1]
                if task in s_path:
                    sfx = s_path.split( task )[1]
                    # print( sfx )
                    sfx = sfx[1:-8]  # excludes '_' on either side
                    # print( 'sfx__', sfx )
                    if sfx:
                        suffix = sfx
    # print( 'suffix___', suffix )
    return suffix

    # above working, fixed bug elsewhere
    #
    '''
    # below works, with extra precautions
    entity = ''
    suffix = ''
    s_path = cmds.file( q = 1, exn = 1 )  # file path
    s_name = s_path.rsplit( '/', 1 )[1].split( '.' )[0]  # file name
    #
    occ = s_path.count( '/' )
    if occ == 7:  # expected directory depth
        find_entity = s_path.split( '/', 2 )[2]
        print( 'here ', find_entity )
        entity = find_entity.rsplit( '/', 5 )[1]
        print( 'there', entity )
    # print( 'n ', s_name )
    # print( 'v ', s_path[-8] )
    if s_path and entity:
        if entity in s_name and task in s_name:  # qualify name convention
            if s_name[-8:] != 'untitled':
                if 'v' == s_path[-7]:  # qualify version convention
                    sfx = s_name.split( task )[1]
                    print( sfx )
                    sfx = sfx[1:-5]  # excludes '_' on either side
                    print( 'sfx__', sfx )
                    if sfx:
                        suffix = sfx
        else:
            message( 'Found unconventional name: ' + s_path, warning = True )
    else:
        message( 'Found unconventional name and/or directory structure: ' + s_path, warning = True )
    print( 'suffix: ', suffix )
    return suffix
    '''


def qualify_filename():
    '''
    parse file path, file name, project path
    make sure file path matches project path
    make sure file naming convention is used
    return bool
    if false, default export path to file path and use file name as version name
    '''
    #
    p_path = cmds.workspace( rd = True, q = True )  # project path
    s_path = cmds.file( q = 1, exn = 1 )  # file path
    # print( 's_path ', s_path )
    #
    s_name = ''
    # project = ''
    entity = ''
    task = ''
    p_go = False
    s_go = False
    f_go = False

    # qualify project was set properly relative to scene path
    if s_path:
        s_name = s_path.rsplit( '/', 1 )[1].split( '.' )[0]  # file name
        if s_name[-8:] != 'untitled':
            s_go = True
            if p_path in s_path:
                p_go = True
                parts = p_path.split( '/' )
                # project = parts[1]
                task = parts[-3]
            else:
                message( 'Scene path and Project path mismatch.', warning = True )
            #
            occ = s_path.count( '/' )  # occurrences
            if occ == 7:  # expected directory depth
                find_entity = s_path.split( '/', 2 )[2]
                entity = find_entity.rsplit( '/', 5 )[1]
                # print( 'entity ', entity )
            else:
                message( 'Directory depth unexpected.', warning = True )
            # print( 'n ', s_name )
            # print( 'v ', s_path[-8] )
            if s_name and entity and task:
                if entity in s_name and task in s_name:  # qualify name convention
                    # find '_v'
                    if s_name[-5:-3] == '_v':  # qualify version convention
                        # print( '_v', s_name[-5:-3] )
                        try:
                            ver = int( s_name[-3:] )
                            # print( 'ver ', ver )
                            f_go = True
                        except:
                            message( 'Version number unconventional.', warning = True )
                    else:
                        message( 'Version suffix not where expected', s_name, warning = True )
                else:
                    message( 'Found unconventional name. Missing Shot or Task in name. ' + s_path, warning = True )
            else:
                message( 'Found unconventional name and/or directory structure: ' + s_path, warning = True )
        else:
            message( 'Scene is untitled.', warning = True )
    else:
        message( 'No file path found.', warning = True )

    #
    if p_go and s_go and f_go:
        print( 'conventions found' )
    elif p_go or s_go or f_go:
        print( 'conventions partial' )
    else:
        print( 'conventions fail' )
    # project matches scene path, scene is named, naming conventions found
    return [p_go, s_go, f_go]
