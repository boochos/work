import time

from PySide2 import QtCore, QtGui, QtWidgets

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

place = web.mod( "atom_place_lib" )


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


def ____UI____():
    pass


def init_ui():
    # main
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    top_layout = QtWidgets.QHBoxLayout()
    bottom_layout = QtWidgets.QHBoxLayout()
    #
    # suffix layout
    sffx_line_layout = QtWidgets.QHBoxLayout()
    sffx_label = QtWidgets.QLabel( 'Warp node suffix:' )
    sffx_edit = QtWidgets.QLineEdit()
    sffx_label.setMinimumWidth( 50 )
    #
    sffx_line_layout.addWidget( sffx_label )
    sffx_line_layout.addWidget( sffx_edit )
    main_layout.addLayout( sffx_line_layout )
    #
    # lists
    lists_layout = QtWidgets.QHBoxLayout()
    warp_list_widget = QtWidgets.QListWidget()
    members_list_widget = QtWidgets.QListWidget()
    members_list_widget.setSelectionMode( QtWidgets.QAbstractItemView.NoSelection )
    #
    lists_layout.addWidget( warp_list_widget )
    lists_layout.addWidget( members_list_widget )
    #
    main_layout.addLayout( top_layout )
    main_layout.addLayout( lists_layout )
    main_layout.addLayout( bottom_layout )
    #
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( 'Time Warp Tool' )
    main_window.resize( 500, 500 )
    #
    warp_list_widget.itemSelectionChanged.connect( lambda: getMembers_ui( warp_list_widget, members_list_widget ) )
    # members_list_widget.itemSelectionChanged.connect( lambda: get_tasks( warp_list_widget.currentItem().text(), members_list_widget.currentItem().text() ) )
    #
    # buttons
    #
    create_warp_button = QtWidgets.QPushButton( "Create Warp" )
    create_warp_button.clicked.connect( lambda: createTimeWarp_ui( warp_list_widget, members_list_widget, sffx_edit.text() ) )
    create_warp_button.setStyleSheet( "background-color: darkgreen" )
    #
    connect_button = QtWidgets.QPushButton( "Connect Objects" )
    connect_button.clicked.connect( lambda: connectTimeWarp_ui( warp_list_widget, members_list_widget ) )
    #
    disconnect_button = QtWidgets.QPushButton( "Disconnect Objects" )
    disconnect_button.clicked.connect( lambda: connectTimeWarp_ui( warp_list_widget, members_list_widget, connect = False ) )
    #
    bake_button = QtWidgets.QPushButton( "Bake Warp" )
    bake_button.clicked.connect( lambda: bakeTimeWarp_ui( warp_list_widget ) )
    # bake_button.setStyleSheet( "background-color: darkgreen" )
    #
    aprox_button = QtWidgets.QPushButton( "Approximate Warp" )
    aprox_button.clicked.connect( lambda: approximateTimeWarp_ui( warp_list_widget ) )
    # aprox_button.setStyleSheet( "background-color: darkgreen" )
    #
    select_button = QtWidgets.QPushButton( "Select Objects" )
    select_button.clicked.connect( lambda: selectTimeWarpMembers_ui( warp_list_widget ) )
    #
    delete_button = QtWidgets.QPushButton( "Delete Warp" )
    delete_button.clicked.connect( lambda: deleteTimeWarp_ui( warp_list_widget, members_list_widget ) )
    delete_button.setStyleSheet( "background-color: darkred" )
    #
    refresh_button = QtWidgets.QPushButton( "Refresh UI" )
    refresh_button.clicked.connect( lambda: getWarps_ui( warp_list_widget, members_list_widget ) )
    #
    # layouts
    bottom_layout.addWidget( refresh_button )
    bottom_layout.addWidget( select_button )
    bottom_layout.addWidget( bake_button )
    bottom_layout.addWidget( aprox_button )
    #
    top_layout.addWidget( create_warp_button )
    top_layout.addWidget( connect_button )
    top_layout.addWidget( disconnect_button )
    top_layout.addWidget( delete_button )
    #
    #
    getWarps_ui( warp_list_widget, members_list_widget )
    #
    # parse current scene
    # get_current( project_list_widget, members_list_widget, tasks_list_widget, scene_list_widget )

    return main_window


def getWarps_ui( warp_list_widget, members_list_widget ):
    '''
    
    '''
    print( 'getwarpsui' )
    warp_list_widget.clear()
    members_list_widget.clear()
    timewarps = getTimeWarps()
    if timewarps:
        for t in timewarps:
            warp_list_widget.addItem( t )


def getMembers_ui( warp_list_widget, members_list_widget ):
    '''
    
    '''
    print( 'membersui' )
    timewarp = warp_list_widget.currentItem().text()
    members_list_widget.clear()
    if cmds.objExists( timewarp ):
        # print( timewarp )
        members = getTimeWarpMembers2( timewarp )
        if members:
            for m in members:
                members_list_widget.addItem( m )
    else:
        # redraw
        getWarps_ui( warp_list_widget, members_list_widget )


def createTimeWarp_ui( warp_list_widget, members_list_widget, suffix = '' ):
    '''
    
    '''
    print( 'createui' )
    cmds.undoInfo( openChunk = True )
    #
    sel = cmds.ls( sl = 1 )
    timewarp = createTimeWarp( suffix )
    # print( sel )
    # print( timewarp )
    connectTimeWarp( sel, timewarp )
    # redraw
    getWarps_ui( warp_list_widget, members_list_widget )
    # select new timewarp
    item = warp_list_widget.findItems( timewarp, QtCore.Qt.MatchExactly )
    if item:
        warp_list_widget.setCurrentItem( item[0] )
    #
    cmds.undoInfo( closeChunk = True )


def connectTimeWarp_ui( warp_list_widget, members_list_widget, connect = True ):
    '''
    
    '''
    print( 'connectui' )
    chunkName = ''
    if connect:
        chunkName = 'connectTimeWarp_ui'
    else:
        chunkName = 'disconnectTimeWarp_ui'
    #
    # cmds.undoInfo( openChunk = True, chunkName = chunkName )
    #
    go = True
    timewarp = warp_list_widget.currentItem().text()  # get selected warp
    sel = cmds.ls( sl = 1 )
    if sel:
        for s in sel:
            if cmds.objectType( s ) != 'transform':
                go = False
                break
    if go:
        if timewarp and sel:  #
            # selectTimeWarpMembers_ui( warp_list_widget ) # turned off, doesnt seem to be needed
            # sel = cmds.ls( sl = 1 )
            if timewarp not in sel:
                if connect:
                    connectTimeWarp( sel, timewarp )
                else:
                    connectTimeWarp( sel, timewarp, connect )
                # redraw ui
                getMembers_ui( warp_list_widget, members_list_widget )
                #
            else:
                message( 'Remove ___timeWarpNode___ node from selection of objects to connect.', warning = True )
        else:
            message( ' select a timewarp in the ui and objects in the scene.', warning = True )
    #
    else:
        message( 'everything in the selection has to be a transform.', warning = True )
    # cmds.undoInfo( closeChunk = True, chunkName = chunkName )


def bakeTimeWarp_ui( warp_list_widget ):
    # pass
    cmds.undoInfo( openChunk = True, chunkName = 'bakeTimeWarp_ui' )
    #
    go = selectTimeWarpMembers_ui( warp_list_widget )
    # getKeyedFramesList()
    if go:
        pass
        bakeTimeWarp( sparseKeys = True, sim = False, sampleBy = 1 )
    else:
        pass
        # print( 'no go' )
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'bakeTimeWarp_ui' )


def approximateTimeWarp_ui( warp_list_widget ):
    pass
    cmds.undoInfo( openChunk = True, chunkName = 'approximateTimeWarp_ui' )
    #
    members = None
    timeWarp = getTimeWarpNode( warp_list_widget )
    if timeWarp:
        members = getTimeWarpMembers2( timeWarp, select = True )
        if members:
            approximateTimeWarp( timeWarp )
        else:
            message( 'No members connected to timeWarp node', warning = True )
    else:
        message( 'Select a timeWarp node in the left column', warning = True )
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'approximateTimeWarp_ui' )


def selectTimeWarpMembers_ui( warp_list_widget ):
    '''
    
    '''
    print( 'selectui' )
    cmds.undoInfo( openChunk = True, chunkName = 'selectTimeWarpMembers_ui' )
    #
    try:
        timewarp = warp_list_widget.currentItem().text()
        members = getTimeWarpMembers2( timewarp, select = True )
        # cmds.select( members )
        if members:
            return True
        else:
            message( 'No members for given TimeWarp', warning = True )
    except:
        message( 'Select a timewarp node in the left column', warning = True )
        return False
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'selectTimeWarpMembers_ui' )


def deleteTimeWarp_ui( warp_list_widget, members_list_widget ):
    '''
    
    '''
    print( 'deleteui' )
    cmds.undoInfo( openChunk = True, chunkName = 'deleteTimeWarp_ui' )
    #

    twarp = warp_list_widget.currentItem()
    if twarp:
        twarp = warp_list_widget.currentItem().text()
        deleteWarp( twarp )
        # redraw
        getWarps_ui( warp_list_widget, members_list_widget )
    else:
        message( ' No TimeWarp node selected in UI list' , warning = 1 )
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'deleteTimeWarp_ui' )


def ____MISC____():
    pass


def warpAttrStr():
    return 'timeWarpedFrame'


def warpNodeStr():
    return '___timeWarpNode___'


def createTimeWarp( suffix = '' ):
    '''
    stuff
    '''
    print( 'create' )
    attr = warpAttrStr()
    name = warpNodeStr() + suffix
    if not cmds.objExists( name ):
        loc = cmds.spaceLocator( n = name )[0]
        # attr
        cmds.addAttr( loc, ln = attr, h = False, at = 'time' )  # time attr !!!
        cmds.setAttr( ( loc + '.' + attr ), cb = True )
        cmds.setAttr( ( loc + '.' + attr ), k = True )
        # range
        ast = cmds.playbackOptions( q = True, ast = True )
        aet = cmds.playbackOptions( q = True, aet = True )
        # key
        cmds.setKeyframe( loc, at = attr, time = ( ast, ast ), value = ast, ott = 'spline', itt = 'spline' )
        cmds.setKeyframe( loc, at = attr, time = ( aet, aet ), value = aet, ott = 'spline', itt = 'spline' )
        cmds.setInfinity( pri = 'linear' )
        cmds.setInfinity( poi = 'linear' )
        # lock - [lock, keyable], [visible, lock, keyable]
        place.setChannels( loc, [True, False], [True, False], [True, False], [True, False, False] )
        return loc
    else:
        print( 'choose different prefix, object already exists', name )


def connectTimeWarp( objects = [], timeWarp = '', connect = True ):
    '''
    objects and timewarp loc
    add support for character sets and anim layers
    '''
    print( 'connect ANIMCURVES______________', connect )
    # start timer
    start = time.time()
    allAnimCurves = []
    warpAttr = '_' + warpAttrStr()
    warpCurve = None
    #

    #
    if objects and timeWarp:
        '''
        warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr() )
        #
        if warpCurve:
            warpCurve = warpCurve[0]
            print( warpCurve )
            '''
        for obj in objects:
            # print( 'conn obj', obj )
            # animCurves = cmds.findKeyframe( obj, c = True )
            animCurves = getAnimCurves( object = obj, max_recursion = 1 )  # character sets cause problems, also animLayers also cause problems
            # print( 'connect', obj, animCurves )
            # return
            if animCurves:
                for curve in animCurves:
                    # print( 'conn curve', curve )
                    allAnimCurves.append( curve )
                    if connect:
                        # add check to already connected retimeNode, if exists, disconnect first
                        # cmds.connectAttr( warpCurve + '.output', curve + '.input', f = True ) # skips attr control, only connects to animcurve
                        cmds.connectAttr( timeWarp + '.' + warpAttrStr(), curve + '.input', f = True )
                    else:
                        # cmds.disconnectAttr( warpCurve + '.output', curve + '.input', f = True ) # skips attr control, only connects to animcurve
                        # connections = getConnections( timeWarp + '.' + warpAttrStr(), direction = 'out', find = cmds.objectType( curve ), find_through = [] )  # cant use this, really slow and finds too many anim curves
                        connections = cmds.listConnections( timeWarp + '.' + warpAttrStr(), s = 0, d = 1 )
                        # print( 'connections: ', connections )
                        # print( 'curve: ', curve )
                        if connections:
                            if curve in connections:
                                cmds.disconnectAttr( timeWarp + '.' + warpAttrStr(), curve + '.input' )
            else:
                # print( 'No animCurves connected to object:', obj )
                pass
            # print( animCurves )
        if not connect:
            # clean up
            cleanConversionNodes( timeWarp + '.' + warpAttrStr() )
        # print allAnimCurves
        '''
        else:
            print( timeWarp + '.' + warpAttrStr(), 'has no keys' )
            '''
    else:
        message( 'Select objects to connect / disconnect', warning = True )

    # end timer
    end = time.time()
    elapsed = end - start
    print( 'Connect time: ' + str( elapsed / 60 ) + ' min', connect )


def bakeTimeWarp( sparseKeys = True, sim = False, sampleBy = 1.0 ):
    '''
    
    '''
    #
    result = getBakeRange()
    start = result[0]
    end = result[1]
    #
    objs = cmds.ls( sl = 1 )
    cmds.refresh( suspend = 1 )
    #
    # print( 'sparseKeys: ', sparseKeys )
    # print( 'simulation: ', sim )
    # print( 'sampleBy: ', sampleBy )
    cmds.bakeResults( objs, t = ( start, end ), simulation = sim, pok = True, sac = sparseKeys, sampleBy = sampleBy )
    cmds.refresh( suspend = 0 )
    message( str( len( objs ) ) + ' curves baked --' + str( objs ), maya = 1 )


def approximateTimeWarp( timeWarp = '' ):
    '''
    
    '''
    print( 'apprx' )
    # ui off
    uiEnable()
    #
    members = cmds.ls( sl = 1 )  # members are selected
    # print(members)
    frames = getKeyedFramesList()
    frames.reverse()
    # print('reversed: ', frames)
    remap_frames_dict = remapFrames( timeWarp = timeWarp, frames = frames, step = 10.0 )
    animCurves = getAnimCurves( object = timeWarp, max_recursion = 1, direction = 'out' )
    sel = cmds.ls( sl = 1 )  # members are selected
    # print(sel)
    # print( animCurves )
    # return
    if remap_frames_dict:
        for animCurve in animCurves:
            cmds.select( animCurve )
            # print(animCurve)
            #
            for f in frames:
                # print( f, remap_frames_dict[f] )
                cmds.keyframe( edit = 1, absolute = 1, timeChange = remap_frames_dict[f], time = ( f, f ), option = 'over' )  # only works for active animLayer
        # disconnect timeWarp
        cmds.select( members )
        if timeWarp not in members:
                connectTimeWarp( members, timeWarp, False )
    # ui on
    uiEnable()
    #
    # watch for remapped frames clashing with original frame, can put key on top of existing key


def remapFrames( timeWarp = '', frames = [], step = 1.0 ):
    '''
    
    '''
    remapped_frames = []
    remap_frames_dict = {}
    #
    for frame in frames:
        remapped_frames.append( seekWardpedFrame( timeWarp, frame, step = step ) )
    #
    if len( frames ) == len( remapped_frames ):
        #
        for f in range( len( frames ) ):
            remap_frames_dict[frames[f]] = remapped_frames[f]
        print( 'dict: ', remap_frames_dict )
        return remap_frames_dict
    else:
        message( 'mismatch number of frames and warped frames', warning = True )
        return False


def seekWardpedFrame( timeWarp = '', frame = 1, step = 1.0 ):
    '''
    
    '''
    tolerance = 0.025  # 0.005
    forward = True
    steps = 20000  # max steps in one direction(forward)
    direction = step
    #
    # cmds.currentTime( frame )
    warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttrStr(), time = frame )
    #
    if warpedFrame > frame:
        forward = False  # warped frame is earlier in timeline, step back
        direction = direction * -1
        # stepDown
    elif warpedFrame < frame:
        forward = True  # warped frame is later in timeline, step back
        # stepUp
    else:
        # print( '-- new: ', frame, '-- old: ', frame )
        return frame  # no change
    #
    # print( 'direction: ', direction )
    current = frame
    for k in range( steps ):
        #
        warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttrStr(), time = current )
        # heading backward
        if warpedFrame < frame and not forward:  # moved backward past frame
            dif = frame - warpedFrame
            #
            if dif > tolerance:
                # print( 'too far: ', dif, 'reverse', k, 'step: ', step )
                return seekWardpedFrame( timeWarp = timeWarp, frame = frame, step = step / 2 )
            else:
                print( '-- new: ', current, '-- old: ', frame, '-- dif: ', dif, k )
                return  current
        # heading forward
        if warpedFrame > frame and forward:  # moved forward past frame
            dif = warpedFrame - frame
            #
            if dif > tolerance:
                # print( 'too far: ', dif, 'reverse', k, 'step: ', step )
                return seekWardpedFrame( timeWarp = timeWarp, frame = frame, step = step / 2 )
            else:
                # print( '-- new: ', current, '-- old: ', frame, '-- dif: ', dif, k )
                return current
        current = current + direction
    message( 'max steps reached', warning = True )


def subframe():
    frames = None
    animCurves = cmds.keyframe( q = True, name = True, sl = True )
    # print animCurves
    if animCurves:
        for crv in animCurves:
            frames = cmds.keyframe( crv, q = True )
            # print frames
            if frames:
                for frame in frames:
                    rnd = round( frame, 0 )
                    # print rnd, frame
                    if rnd != frame:
                        message( 'removing: ' + 'key' + ' -- ' + str( frame ) )
                        cmds.refresh( f = 1 )
                        if cmds.setKeyframe( animCurves, time = ( rnd, rnd ), i = 1 ) == 0:
                            cmds.cutKey( animCurves, time = ( frame, frame ) )
                        else:
                            cmds.setKeyframe( animCurves, time = ( rnd, rnd ), i = 1 )
                            cmds.cutKey( animCurves, time = ( frame, frame ) )
            else:
                message( 'no keys' )
    else:
        message( 'no curves selected' )


class GraphSelection():

    def __init__( self ):
        self.selection = cmds.ls( sl = True )
        self.crvs = cmds.keyframe( q = True, name = True, sl = True )
        self.pack = []
        if self.crvs:
            for item in self.crvs:
                cr = []
                cr.append( item )
                cr.append( cmds.keyframe( item, q = True, sl = True ) )
                self.pack.append( cr )

    def reselect( self, objects = True ):
        if objects:
            if self.selection:
                sel = cmds.ls( sl = True )
                if sel != self.selection:
                    cmds.select( self.selection )
        if self.pack:
            for cr in self.pack:
                cmds.selectKey( cr[0], add = True, time = ( cr[1][0], cr[1][len( cr[1] ) - 1] ) )


def deleteWarp( timewarp ):
    '''
    
    '''
    print( 'delete' )
    objects = getTimeWarpMembers( timewarp )
    if objects:
        connectTimeWarp( objects, timewarp, connect = False )
    cmds.delete( timewarp )


def cleanConversionNodes( object = '' ):
    '''
    find conversion nodes connected to object with no output connection and delete them
    leftovers form disconnect objects from timewarp node
    '''
    sel = cmds.ls( sl = 1 )[0]
    # out
    s = 0
    d = 1
    cons = cmds.listConnections( object, d = d, s = s, type = 'unitToTimeConversion' )
    print( cons )
    #
    if cons:
        for c in cons:
            out = cmds.listConnections( c, d = d, s = s )
            if not out:
                # print( 'delete', c )
                cmds.delete( c )
    else:
        # print('No conversion nodes to clean.')
        pass


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


def ____GET____():
    pass


def getTimeWarpNode( warp_list_widget ):
    '''
    get selected time warp node
    '''
    print( 'getwarpnode' )
    #
    try:
        timeWarp = warp_list_widget.currentItem().text()
        print( 'getTimeWarpNode, here' )
        return timeWarp
    except:
        return False


def getAnimCurves( object = '', max_recursion = 0, direction = 'in' ):
    '''
    find animCurves, 3 types
    animurveTT = time, not part of search
    '''
    # print( 'getanimcurves', object )
    result = []
    attrs = cmds.listAttr( object, k = 1 )
    # return
    for attr in attrs:  # should optimize for attr type. too many loops
        obj = object + '.' + attr
        # print( '___attr', attr )
        animCrvs = getConnections( object = obj, direction = direction, find = 'animCurve', find_through = [], skip = [object], max_recursion = max_recursion, ignore_types = ['transform', 'animLayer'], results = [] )
        # print( '___curves', animCrvs )
        if animCrvs:
            for c in animCrvs:
                result.append( c )
        '''
        # if only one type gets queried it works, if alll breaks !!!!
        print( '___TL' )
        tl = getConnections( object = obj, direction = 'in', find = 'animCurveTL', find_through = [], skip = [object], max_recursion = max_recursion, ignore_types = ['transform', 'animLayer'] )
        if tl:
            for t in tl:
                result.append( t )
        print( '___TA' )
        ta = getConnections( object = obj, direction = 'in', find = 'animCurveTA', find_through = [], skip = [object], max_recursion = max_recursion, ignore_types = ['transform', 'animLayer'] )
        if ta:
            for t in ta:
                result.append( t )
        print( '___TU' )
        tu = getConnections( object = obj, direction = 'in', find = 'animCurveTU', find_through = [], skip = [object], max_recursion = max_recursion, ignore_types = ['transform', 'animLayer'] )
        if tu:
            for t in tu:
                result.append( t )'''
        # print( '___T*', result )
    # clean, remove plugs
    result_clean = []
    if result:
        for r in result:
            if '.' in r:
                r = r.split( '.' )[0]  # remove plug
            result_clean.append( r )
    result_clean = list( dict.fromkeys( result_clean ) )  # doesnt actually work for some reason, fixed above 'if r not in result_clean'
    # print( '___', result_clean )
    return result_clean


def getAnimCurvesList():
    '''
    list of objects
    '''
    print( 'getanimcurvelist' )
    animCurves = []
    sel = cmds.ls( sl = 1 )
    print( sel )
    for s in sel:
        # print( s )
        crvs = getAnimCurves( object = s, max_recursion = 1 )
        # print( crvs )
        if crvs:
            for c in crvs:
                animCurves.append( c )
    if animCurves:
        animCurves = list( set( animCurves ) )
        animCurves.sort()
        # print( 'animCurves list result', animCurves )
        return animCurves
    else:
        return False


def getTimeWarpMembers( timeWarp, select = False, typ = 'transform' ):
    '''
    typ = transform / character
    '''
    objects = []
    #
    warpCurve = cmds.listConnections( timeWarp + '.' + warpAttrStr() )
    if warpCurve:
        warpCurve = warpCurve[0]
        # print( warpCurve )
        animCurves = cmds.listConnections( warpCurve, t = 'animCurve', scn = 1 )  # curves connected to timeWarp
        # print( animCurves )
        if animCurves:
            for curve in animCurves:
                # print 0, curve
                connected_nodes = cmds.listConnections( curve, scn = 1, t = typ )  # objects connected to anim curves
                # print curve, 'connected to', connected_node
                if connected_nodes:
                    for n in connected_nodes:
                        if n not in objects:
                            objects.append( n )
                else:
                    # print( 'no transforms' )
                    pass
            if select and objects:
                cmds.select( objects )
        else:
            print( 'no members' )
    else:
        print( timeWarp + '.' + warpAttrStr(), 'has no keys' )
    #
    print( objects )
    return objects

    '''
    # find all objects connected to character set
    sel = cmds.ls(sl=1)[0]
    cons = cmds.listConnections(sel, t='character')
    chars = []
    if cons:
        for c in cons:
            if c not in chars:
                chars.append(c)
    print cons
    print chars
    objs = []
    for char in chars:
        members = cmds.character( char, q = True )
        for m in members:
            m = m.split('.')[0]
            if m not in objs:
                objs.append(m)
    print objs
    # three methods to find connection to timewarp
    # 1 through transform connection
    # 2 through character set connection
    # 3 through animLayer connection
    '''
    '''
    timwarp maps
    assume first curve node is always baseLayer animCurve
    tw => conv => curve => node
    tw => conv => curve => char => node
    tw => conv => curve => animLayerBlendNode... => node
    tw => conv => curve => char => animLayerBlendNode... => node
    '''


def getTimeWarpMembers2( timeWarp, select = False ):
    '''
    animCurveTU
    unitToTimeConversion
    animCurveTA
    character
    animBlendNodeAdditiveRotation
    
    '''
    print( 'getmembers2 TRANSFORM______________' )
    objects = []
    #
    skip = [timeWarp ]
    found = getConnections( timeWarp + '.' + warpAttrStr(), direction = 'out', find = 'transform', find_through = [], skip = skip, results = [] )  # had to add results value, app wasnt clearing its state for some reason
    # print( 'found', found )
    # return None
    if found:
        found = list( dict.fromkeys( found ) )
        objects = found
    # print( 'objects', objects)
    if timeWarp in objects:
        objects.remove( timeWarp )
    objects.sort()
    # build list for selection, no plug
    clean_objects = []
    for c in objects:
        # print( c )
        if '.' in c:
            clean_objects.append( c.split( '.' )[0] )
        else:
            clean_objects.append( c )
    if select:
        cmds.select( clean_objects )
    # return list with plugs
    return objects


def getConnections( object = '', direction = 'in', find = 'animCurveTU', find_through = [], skip = [], max_recursion = 5, recursion = 0, ignore_types = [], plugs = True, results = [] ):
    '''
    object = object with/without attr ==> "___timeWarpNode___b.timeWarpedFrame", "___timeWarpNode___b"
    direction = in / out
    find = returns node type specified ie. animCurveTU or transform
    '''
    # print( 'getconnections RESULTS______________', results, 'recursion', recursion )
    # return
    # results = []
    # nodes which qualify to find connection through, add constraint node
    find_through = [
        'animBlendNodeAdditiveDA',
        'animBlendNodeAdditiveDL',
        'animBlendNodeAdditiveF',
        'animBlendNodeAdditiveFA',
        'animBlendNodeAdditiveFL',
        'animBlendNodeAdditiveI16',
        'animBlendNodeAdditiveI32',
        'animBlendNodeAdditiveRotation',
        'animBlendNodeAdditiveScale',
        'animBlendNodeAdditive',
        'animBlendNodeEnum',
        'animBlendNodeBoolean',
        'animCurveTL',
        'animCurveTU',
        'animCurveTA',
        'character',
        'pairBlend'  # PROBLEM, CANT FIND PROPER PLUG ROUTE, INCLUDES ALL ATTRS AS CONNECTED, WILL NEED TO MAP ATTRS IN/OUT
        ]
    # nodes which have dif in/out plugs
    non_pass_through = [
        'animBlendNodeAdditiveDA',
        'animBlendNodeAdditiveDL',
        'animBlendNodeAdditiveF',
        'animBlendNodeAdditiveFA',
        'animBlendNodeAdditiveFL',
        'animBlendNodeAdditiveI16',
        'animBlendNodeAdditiveI32',
        'animBlendNodeAdditiveRotation',
        'animBlendNodeAdditiveScale',
        'animBlendNodeAdditive',
        'animBlendNodeEnum',
        'animBlendNodeBoolean',
        'animCurveTL',
        'animCurveTU',
        'animCurveTA',
        'pairBlend'  # PROBLEM, CANT FIND PROPER PLUG ROUTE, INCLUDES ALL ATTRS AS CONNECTED (LIKELY CUZ PLUGS ARENT USED)
        ]
    #
    found = False
    localSkip = []
    max_recursion = 5

    if recursion == max_recursion:
        # print( '__________________________', recursion )
        return results
    else:
        #
        if cmds.objectType( object ) == 'character':
            plugs = True
        # plugs = False

        #
        if direction == 'in':
            s = 1
            d = 0
            # print( '---- get incoming connection to: ', object )
        elif direction == 'out':
            s = 0
            d = 1
            # print( '---- get outgoing connection from: ', object )
        #
        i = 0
        max = 2
        # print( type( i ), type( max ) )
        '''
        while not found and i < max:
            charSet = False
            i = i + 1
            print( i )
            if i == max:
                # print( '______________________________________________________ loop done' )
                return []'''
        connections = cmds.listConnections( object, s = s, d = d, scn = True, plugs = plugs )
        # print( connections )

        # remove duplicates and skip objects
        if connections:
            connections = list( dict.fromkeys( connections ) )
            # print( '+ _________ connections', object, ' -- ', direction , ' -- ', connections )
            x = []
            for c in connections:
                # print( 'c: ', c )
                if c in skip or cmds.objectType( c ) in ignore_types:  # remove if in skip or ignore types
                    # print( 'remove list c: ', c )
                    x.append( c )
            # remove wrong type
            for j in x:
                # print( '__ is in skip list or --ignore-- types, removed: ', j, cmds.objectType( j ) )
                skip.append( j )
                connections.remove( j )

        # check for proper type
        # print( 'qualified connections: ', connections, find, results )
        clean_connections = []  # remove plug, in/out for curve arent the same connection, breaks algo
        if connections:
            #
            for c in connections:
                if cmds.objectType( c ) in non_pass_through:  # remove plug, then append
                    # this may not actually be the problem, bug persists with this fix
                    if cmds.objectType( c ) == 'pairBlend':  # remove plug unless pairBlend, need plug to stop cycle
                        # print( direction )
                        if '.inTranslate' in c:
                            c = c.replace( '.inTranslate', '.outTranslate' )
                        if '.inRotate' in c:
                            c = c.replace( '.inRotate', '.outRotate' )

                        #
                        if direction == 'out':
                            c = c[:-1]  # remove number, output has not number ie. inTranslateX1
                        else:
                            c = c.split( '.' )[0]
                        # print( c )
                        clean_connections.append( c )
                    else:
                        clean_connections.append( c.split( '.' )[0] )
                else:
                    clean_connections.append( c )
            clean_connections = list( dict.fromkeys( clean_connections ) )
            #
            x = []
            for c in clean_connections:
                if find in cmds.objectType( c ):  # find = abbreviated ie. animCurveTL = animCurve
                    if c not in results:
                        results.append( c )
                    if c not in x:
                        x.append( c )  # death loop with out this
                    found = True
                    # print( 'found', c, find, cmds.objectType( c ) )
                    # print( 'skip', skip )
                else:
                    if cmds.objectType( c ) not in find_through:  # has to be in find_through, or same as find
                        x.append( c )
                    # print( c, 'is wrong type: ', cmds.objectType( c ), ' ... looking for: ', find )
                    if direction == 'in':
                        # print( 'search for incoming connection to: ', object, 'through: ', c )
                        pass
                    else:
                        # print( 'search for outgoing connection from: ', object, 'through: ', c )
                        pass
            # remove wrong type, again
            for j in x:
                # print( 'removed: ', j, cmds.objectType( c ) )
                skip.append( j )  # !!!! could loop forever unless skip is added
                clean_connections.remove( j )
                # print( '__ is in skip list or --wrong-- type, removed: ', j, cmds.objectType( j ) )
        #
        # if not found and clean_connections:
        if clean_connections:
            # print( 'keep looking: ', 'results: ', results, 'clean_con: ', clean_connections )
            #
            if recursion >= max_recursion:
                # print( '________________________________________________max recursion' )
                pass
                # break
            else:
                recursion = recursion + 1
                #
                # print( '-- start loop --', clean_connections )
                x = []
                for c in clean_connections:
                    skip.append( c )
                    # print( '-- start new --', c, clean_connections )
                    rslt = None

                    if '.' in c:
                        pass
                        rslt = getConnections( c, direction = direction, find = find, find_through = [], skip = skip, max_recursion = max_recursion, recursion = recursion, ignore_types = ignore_types, plugs = True, results = results )
                    else:
                        rslt = getConnections( c, direction = direction, find = find, find_through = [], skip = skip, max_recursion = max_recursion, recursion = recursion, ignore_types = ignore_types, plugs = True, results = results )
                    if rslt:
                        for r in rslt:
                            results.append( r )
                    x.append( c )  # remove from list as already tried route
                    # print( '-------- recursion end: ', clean_connections )
                    # return results
                # remove attempted routes
                for j in x:
                    # print( 'removed: ', j )
                    clean_connections.remove( j )
                # print( '-------- recursion loop end: ', clean_connections )
        else:
            # print( '-------- no leftovers: ', clean_connections )
            pass
        if results:
            results = list( set( results ) )
            # print( '---- found: ', results, find )
            # print( '---- leftovers: ', clean_connections )
            return results
        else:
            # print( 'end: ', clean_connections )
            pass

    # print( '___________________________ nothing' )
    return results


def getConnections1( object = '', direction = 'in', find = 'animCurveTU', find_through = [], skip = [], max_recursion = 5, recursion = 0, ignore_types = [], plugs = True, results = [] ):
    '''
    
    '''
    print( '####################################################' )
    print( 'object_________________________', object )
    print( 'direction______________________', direction )
    print( 'find___________________________', find )
    print( 'find_through___________________', find_through )
    print( 'skip___________________________', skip )
    print( 'max_recursion__________________', max_recursion )
    print( 'recursion______________________', recursion )
    print( 'ignore_types___________________', ignore_types )
    print( 'plugs__________________________', plugs )
    print( 'results________________________', results )
    pass

'''
import imp
import webrImport as web
imp.reload(web)
arl = web.mod('animRetime_lib')
# retime test
arl.getConnections( 
object = 'locator1_translateX_AnimLayer1', 
direction = 'in', 
find = 'animCurveTL', 
find_through = [], 
skip = [u'locator1', u'locator1_translateX_AnimLayer1'], 
max_recursion = 2, 
recursion = 1, 
ignore_types = ['transform', 'animLayer'], 
plugs = True, 
results = [] )
'''


def getTimeWarps():
    '''
    find timewarp nodes
    '''
    print( 'gettimewarps' )
    name = warpNodeStr()
    tw_nodes = []
    objs = cmds.ls( type = 'transform' )
    for o in objs:
        if name in o:
            tw_nodes.append( o )
    print( tw_nodes )
    return tw_nodes


def getKeyedFrames( obj ):
    '''
    
    '''
    # print( 'getframes' )
    # animCurves = cmds.findKeyframe( obj, c = True )  # may have to use getAnimCurves(), this command seems tonly get active animlayer curves
    # print(len(animCurves), animCurves)
    animCurves = getAnimCurves( object = obj, max_recursion = 1 )
    # print(len(animCurves),animCurves)
    frames = []
    if animCurves:
        for crv in animCurves:
            framesTmp = cmds.keyframe( crv, q = True )
            for frame in framesTmp:
                frames.append( frame )
        frames = list( set( frames ) )
        frames.sort()
        return frames
    else:
        message( '-- Object given has no keys --' )
        return frames


def getKeyedFramesList():
    '''
    single timewarp node expected to be selected
    or could be wrong....
    members are selected, likely always
    '''
    frames = []
    sel = cmds.ls( sl = 1 )
    # print( sel )
    for s in sel:
        # print( s )
        frms = getKeyedFrames( s )
        # print( frms )
        if frms:
            for f in frms:
                frames.append( f )
    frames = list( set( frames ) )
    frames.sort()
    # print( 'frames list result', frames )
    return frames


def getBakeRange( keyRange = True ):
    '''
    keyRange = expand bake range if keys are outside playbackOptions
    '''
    #
    start = cmds.playbackOptions( q = True, minTime = True )
    end = cmds.playbackOptions( q = True, maxTime = True )
    #
    if keyRange:
        frames = getKeyedFramesList()
        if frames:
            if frames[0] < start:
                start = frames[0]
            if frames[-1] > end:
                start = frames[-1]

    return [start, end]


if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    main_window.show()
    app.exec_()
else:
    print( 'nah' )
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    main_window.show()
    app.exec_()
