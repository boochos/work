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
    aprox_button.clicked.connect( lambda: approximateTimeWarp_ui( warp_list_widget, members_list_widget ) )
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
    refresh_button.clicked.connect( lambda: getWarps_ui( warp_list_widget ) )
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
    getWarps_ui( warp_list_widget )
    #
    # parse current scene
    # get_current( project_list_widget, members_list_widget, tasks_list_widget, scene_list_widget )

    return main_window


def getWarps_ui( warp_list_widget ):
    '''
    
    '''
    warp_list_widget.clear()
    timewarps = getTimeWarps()
    if timewarps:
        for t in timewarps:
            warp_list_widget.addItem( t )


def getMembers_ui( warp_list_widget, members_list_widget ):
    '''
    
    '''
    # print warpNode
    timewarp = warp_list_widget.currentItem().text()
    members_list_widget.clear()
    if cmds.objExists( timewarp ):
        # print( timewarp )
        members = getTimeWarpMembers2( timewarp )
        if members:
            for m in members:
                members_list_widget.addItem( m )
    else:
        print( 'object doesnt exist' )
        warp_list_widget.clear()
        members_list_widget.clear()
        # redraw
        getWarps_ui( warp_list_widget )


def createTimeWarp_ui( warp_list_widget, members_list_widget, suffix = '' ):
    '''
    
    '''
    cmds.undoInfo( openChunk = True )
    #
    sel = cmds.ls( sl = 1 )
    timewarp = createTimeWarp( suffix )
    print( sel )
    print( timewarp )
    connectTimeWarp( sel, timewarp )
    # redraw
    getWarps_ui( warp_list_widget )
    #
    cmds.undoInfo( closeChunk = True )


def connectTimeWarp_ui( warp_list_widget, members_list_widget, connect = True ):
    '''
    
    '''
    cmds.undoInfo( openChunk = True )
    #
    timewarp = warp_list_widget.currentItem().text()
    sel = cmds.ls( sl = 1 )
    if timewarp not in sel:
        if connect:
            connectTimeWarp( sel, timewarp )
        else:
            connectTimeWarp( sel, timewarp, connect )
        # redraw
        getMembers_ui( warp_list_widget, members_list_widget )
        #
    else:
        message( 'Remove ___timeWarpNode___ node from selection of objects to connect.', warning = True )
    cmds.undoInfo( closeChunk = True )


def bakeTimeWarp_ui( warp_list_widget ):
    # pass
    cmds.undoInfo( openChunk = True )
    #
    go = selectTimeWarpMembers_ui( warp_list_widget )
    if go:
        bakeWarp( sparseKeys = False, sim = False )
    #
    cmds.undoInfo( closeChunk = True )


def approximateTimeWarp_ui():
    pass
    cmds.undoInfo( openChunk = True )
    #
    #
    cmds.undoInfo( closeChunk = True )


def selectTimeWarpMembers_ui( warp_list_widget ):
    '''
    
    '''
    cmds.undoInfo( openChunk = True )
    #
    try:
        timewarp = warp_list_widget.currentItem().text()
        members = getTimeWarpMembers2( timewarp )
        cmds.select( members )
    except:
        message( 'Select a timewarp node in the left column', warning = True )
        return False
    #
    cmds.undoInfo( closeChunk = True )


def deleteTimeWarp_ui( warp_list_widget, members_list_widget ):
    '''
    
    '''
    cmds.undoInfo( openChunk = True )
    #
    twarp = warp_list_widget.currentItem().text()
    warp_list_widget.clear()
    members_list_widget.clear()
    deleteWarp( twarp )
    # redraw
    getWarps_ui( warp_list_widget )
    #
    cmds.undoInfo( closeChunk = True )


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
    attr = warpAttrStr()
    name = warpNodeStr() + suffix
    if not cmds.objExists( name ):
        loc = cmds.spaceLocator( n = name )[0]
        # attr
        cmds.addAttr( loc, ln = attr, h = False )
        cmds.setAttr( ( loc + '.' + attr ), cb = True )
        cmds.setAttr( ( loc + '.' + attr ), k = True )
        # range
        ast = cmds.playbackOptions( q = True, ast = True )
        aet = cmds.playbackOptions( q = True, aet = True )
        # key
        cmds.setKeyframe( loc, at = attr, time = ( ast, ast ), value = ast, ott = 'spline', itt = 'spline' )
        cmds.setKeyframe( loc, at = attr, time = ( aet, aet ), value = aet, ott = 'spline', itt = 'spline' )
        # lock - [lock, keyable], [visible, lock, keyable]
        place.setChannels( loc, [True, False], [True, False], [True, False], [True, False, False] )
        return loc
    else:
        print( 'choose different prefix, object already exists', name )


def connectTimeWarp( objects = [], timewarp = '', connect = True ):
    '''
    objects and timewarp loc
    add support for character sets and anim layers
    '''
    allAnimCurves = []
    warpAttr = '_' + warpAttrStr()
    warpCurve = None
    #

    #
    if objects and timewarp:
        '''
        warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr() )
        #
        if warpCurve:
            warpCurve = warpCurve[0]
            print( warpCurve )
            '''
        for obj in objects:
            # animCurves = cmds.findKeyframe( obj, c = True )
            animCurves = getAnimCurves( object = obj, max_recursion = 1 )
            if animCurves:
                for curve in animCurves:
                    allAnimCurves.append( curve )
                    if connect:
                        # add check to already connected retimeNode, if exists, disconnect first
                        # cmds.connectAttr( warpCurve + '.output', curve + '.input', f = True ) # skips attr control, only connects to animcurve
                        cmds.connectAttr( timewarp + '.' + warpAttrStr(), curve + '.input', f = True )
                    else:
                        # cmds.disconnectAttr( warpCurve + '.output', curve + '.input', f = True ) # skips attr control, only connects to animcurve
                        cmds.disconnectAttr( timewarp + '.' + warpAttrStr(), curve + '.input' )
            else:
                print( 'No animCurves connected to object:', obj )
            # print( animCurves )
        if not connect:
            # clean up
            cleanConversionNodes( timewarp + '.' + warpAttrStr() )
        # print allAnimCurves
        '''
        else:
            print( timewarp + '.' + warpAttrStr(), 'has no keys' )
            '''
    else:
        message( 'Select objects to connect / disconnect', warning = True )


def bakeWarp( sparseKeys = True, sim = False ):
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
    cmds.bakeResults( objs, t = ( start, end ), simulation = sim, pok = True, sac = sparseKeys, sampleBy = 1 )
    cmds.refresh( suspend = 0 )
    message( str( len( objs ) ) + ' curves baked --' + str( objs ), maya = 1 )


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
                print( 'delete', c )
                cmds.delete( c )
    else:
        # print('No conversion nodes to clean.')
        pass


def ____GET____():
    pass


def getAnimCurves( object = '', max_recursion = 0 ):
    '''
    find animCurves, 3 types
    '''
    result = []
    # print( '___TL' )
    tl = getConnections( object = object, direction = 'in', find = 'animCurveTL', skip = [object], max_recursion = max_recursion, ignore_types = ['transform'] )
    if tl:
        for t in tl:
            result.append( t )
    # print( '___TA' )
    ta = getConnections( object = object, direction = 'in', find = 'animCurveTA', skip = [object], max_recursion = max_recursion, ignore_types = ['transform'] )
    if ta:
        for t in ta:
            result.append( t )
    # print( '___TU' )
    tu = getConnections( object = object, direction = 'in', find = 'animCurveTU', skip = [object], max_recursion = max_recursion, ignore_types = ['transform'] )
    if tl:
        for t in tu:
            result.append( t )
    # print( '___T*', result )
    return result


def getTimeWarpMembers( timewarp, select = False, typ = 'transform' ):
    '''
    typ = transform / character
    '''
    objects = []
    #
    warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr() )
    if warpCurve:
        warpCurve = warpCurve[0]
        # print( warpCurve )
        animCurves = cmds.listConnections( warpCurve, t = 'animCurve', scn = 1 )  # curves connected to timewarp
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
                    print( 'no transforms' )
            if select and objects:
                cmds.select( objects )
        else:
            print( 'no members' )
    else:
        print( timewarp + '.' + warpAttrStr(), 'has no keys' )
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


def getTimeWarpMembers2( timewarp, select = False, typ = 'transform' ):
    '''
    animCurveTU
    unitToTimeConversion
    animCurveTA
    character
    animBlendNodeAdditiveRotation
    
    '''
    objects = []
    #
    skip = [timewarp ]
    found = getConnections( timewarp + '.' + warpAttrStr(), direction = 'out', find = 'transform', skip = skip )
    # print( 'found', found )
    # return None
    if found:
        found = list( set( found ) )
        objects = found
    # print 'objects', objects
    if timewarp in objects:
        objects.remove( timewarp )
    objects.sort()
    return objects


def getConnections( object = '', direction = 'in', find = 'animCurveTU', skip = [], max_recursion = 1, recursion = 0, ignore_types = [] ):
    '''
    object = object with/without attr ==> "___timeWarpNode___b.timeWarpedFrame", "___timeWarpNode___b"
    direction = in / out
    find = returns node type specified ie. animCurveTU or transform
    '''
    result = []
    found = False
    done = False
    localSkip = []
    #
    if direction == 'in':
        s = 1
        d = 0
    elif direction == 'out':
        s = 0
        d = 1
    #
    i = 0
    max = 2
    print( type( i ), type( max ) )
    while not found and i < max:
        charSet = False
        i = i + 1
        if i == max:
            # print( '______________________________________________________ loop done' )
            return []
        connections = cmds.listConnections( object, s = s, d = d, scn = True )
        # remove duplicates and skip objects
        if connections:
            connections = list( set( connections ) )
            # print( '+ _________ connections', object, ' -- ', direction , ' -- ', connections )
            x = []
            for c in connections:
                # print( c )
                if c in skip or cmds.objectType( c ) in ignore_types:  # remove if in skip or ignore types
                    x.append( c )
                else:
                    # print( 'keeper: ', c )
                    pass
            #
            for i in x:
                connections.remove( i )
            #
            # print( '- _________ connections', object, ' -- ', direction , ' -- ', connections )
        # check for proper type
        if connections:
            for c in connections:
                if cmds.objectType( c ) == find:
                    result.append( c )
                    found = True
                    # print( 'found', c, find )
                    # print( 'skip', skip )
                else:
                    # print( 'search:', object, direction, c )
                    pass
        #
        if not found and connections:
            # print( 'not found' )
            #
            if recursion > max_recursion:
                # print( 'max recursion' )
                break
            else:
                recursion = recursion + 1
                #
                for c in connections:
                    skip.append( c )
                    rslt = getConnections( c, direction = direction, find = find, skip = skip, max_recursion = max_recursion, recursion = recursion, ignore_types = ignore_types )
                    if rslt:
                        for r in rslt:
                            result.append( r )
        if result:
            result = list( set( result ) )
            return result
        if not connections:
            return []
    return []


def getTimeWarps():
    '''
    find timewarp nodes
    '''
    pass
    name = warpNodeStr()
    tw_nodes = []
    objs = cmds.ls( type = 'transform' )
    for o in objs:
        if name in o:
            tw_nodes.append( o )
    print( tw_nodes )
    return tw_nodes


def getKeyedFrames( obj ):
    animCurves = cmds.findKeyframe( obj, c = True )
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


def getBakeRange():
    '''
    
    '''
    frames = []
    sel = cmds.ls( sl = 1 )
    for s in sel:
        crvs = getAnimCurves( object = s, max_recursion = 1 )
        if crvs:
            #
            for crv in crvs:
                framesTmp = cmds.keyframe( crv, q = True )
                for frame in framesTmp:
                    frames.append( frame )
            frames = list( set( frames ) )
            frames.sort()
            #
    start = cmds.playbackOptions( q = True, minTime = True )
    end = cmds.playbackOptions( q = True, maxTime = True )
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
