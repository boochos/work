from PySide2 import QtCore, QtGui, QtWidgets

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


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
    main_window.resize( 500, 400 )
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
    bake_button.clicked.connect( lambda: bakeTimeWarp_ui( warp_list_widget, members_list_widget ) )
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
    bottom_layout.addWidget( bake_button )
    bottom_layout.addWidget( aprox_button )
    bottom_layout.addWidget( select_button )
    bottom_layout.addWidget( refresh_button )
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
        print( timewarp )
        members = getTimeWarpMembers2( timewarp )
        if members:
            for m in members:
                members_list_widget.addItem( m )
    else:
        print( 'objects doesnt exist' )
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
    if connect:
        connectTimeWarp( sel, timewarp )
    else:
        connectTimeWarp( sel, timewarp, connect )
    # redraw
    getMembers_ui( warp_list_widget, members_list_widget )
    #
    cmds.undoInfo( closeChunk = True )


def bakeTimeWarp_ui():
    pass
    cmds.undoInfo( openChunk = True )
    #


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
    timewarp = warp_list_widget.currentItem().text()
    members = getTimeWarpMembers( timewarp )
    cmds.select( members )
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
        return loc
    else:
        print( 'choose different prefix, object already exists', name )


def connectTimeWarp( objects, timewarp, connect = True ):
    '''
    objects and timewarp loc
    add support for character sets and anim layers
    '''
    allAnimCurves = []
    warpAttr = '_' + warpAttrStr()
    warpCurve = None
    #

    #
    warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr() )
    if warpCurve:
        warpCurve = warpCurve[0]
        print( warpCurve )
        for obj in objects:
            animCurves = cmds.findKeyframe( obj, c = True )
            for curve in animCurves:
                allAnimCurves.append( curve )
                if connect:
                    # add check to already connected retimeNode, if exists, disconnect first
                    cmds.connectAttr( warpCurve + '.output', curve + '.input', f = True )
                else:
                    cmds.disconnectAttr( warpCurve + '.output', curve + '.input' )
            # print animCurves
        # print allAnimCurves
    else:
        print( timewarp + '.' + warpAttrStr(), 'has no keys' )


def getTimeWarpMembers( timewarp, select = False, typ = 'transform' ):
    '''
    typ = transform / character
    '''
    objects = []
    #
    warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr() )
    if warpCurve:
        warpCurve = warpCurve[0]
        print( warpCurve )
        animCurves = cmds.listConnections( warpCurve, t = 'animCurve', scn = 1 )  # curves connected to timewarp
        print( animCurves )
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
    
    make recursive function to find connected transforms incoming / outgoing connection variable
    
    # incoming connections
    c = cmds.listConnections( '___timeWarpNode___b.timeWarpedFrame', s=1, d=0, scn = True )[0]
    print c
    # if not animCurve keep going
    c = cmds.listConnections( c, s=1, d=0, scn = True )
    print c
    # once found switch to outgoing connections
    # loop curve nodes follow connections, ignore if connections lead back to timewarp node
    
    '''
    objects = []
    #
    '''
    warpCurve = cmds.listConnections( timewarp + '.' + warpAttrStr(), scn = True, et = True, t = 'animCurveTU' )
    if warpCurve:
        warpCurve = warpCurve[0]
        print warpCurve
        #
        nodes = cmds.listConnections( warpCurve, d = 1, s = 0, p = 1 )  # initial query, nodes connected to timewarp
        print nodes
    else:
        print 'nothing'
    '''
    skip = [timewarp ]
    found = getConnections( timewarp + '.' + warpAttrStr(), direction = 'in', find = 'animCurveTU', skip = skip )
    print( 'found', found )
    # return None
    if found:
        for f in found:
            skip.append( f )
        for f in found:
            result = getConnections( f, direction = 'out', find = 'transform', skip = skip )

            for r in result:
                if r not in objects:
                    objects.append( r )
    # print 'objects', objects
    if timewarp in objects:
        objects.remove( timewarp )
    return objects


def getConnections( object = '', direction = 'in', find = 'animCurveTU', skip = [] ):
    '''
    object = object with/without attr ==> "___timeWarpNode___b.timeWarpedFrame", "___timeWarpNode___b"
    direction = in / out
    find = returns node type specified
    '''
    result = []
    found = False
    done = False
    #
    if direction == 'in':
        s = 1
        d = 0
    elif direction == 'out':
        s = 0
        d = 1
    #
    i = 0
    max = 30
    while not found and i < max:
        charSet = False
        i = i + 1
        if i == max:
            print( '______________________________________________________FAIL' )
            return []
        connections = cmds.listConnections( object, s = s, d = d, scn = True )
        # remove duplicates and skip objects
        if connections:
            connections = list( set( connections ) )
            for c in connections:
                if c in skip:
                    connections.remove( c )
                if cmds.objectType( c ) == 'character':
                    charSet = True
                    break
        # redo connections if character !!!!!!
        print( 'connections', connections )
        # check for proper type
        if connections:
            for c in connections:
                if cmds.objectType( c ) == find:
                    result.append( c )
                    found = True
                    print( 'found', c, find )
                    print( 'skip', skip )
                else:
                    pass
                    print( 'search:', object, direction, c )
        #
        if not found and connections:
            print( 'not found' )
            for c in connections:
                rslt = getConnections( c, direction = direction, find = find, skip = skip )
                if rslt:
                    for r in rslt:
                        result.append( r )
        if result:
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


def bakeTimeWarp( timewarp = None, objects = [] ):
    '''
    remap object keys
    '''
    pass


def unWarpFrame( timeWarp, frame = 0 ):
    '''
    # find new frame position
    timeWarpCurve = animCurve from timewarp node
    frame = frame number to parse
    '''
    #
    f_plus = None  # frames step forward
    f_minus = None  # frames step backward
    increment = 0.001
    warpAttr = warpAttrStr()
    warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttr, time = frame )
    #
    if warpedFrame != frame:
        #
        if warpedFrame < frame:
            f_plus = frame  # frame iterator
            # loop foorward
            while warpedFrame < frame:
                warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttr, time = f_plus )
                if warpedFrame > frame:  # reached pivot, step backward
                    f_minus = f_plus - increment
                    # loop backward, increment
                    while warpedFrame > frame:
                        warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttr, time = f_minus )
                        f_minus = f_minus - increment
                        # temp precaution
                        if f_minus == -5000:
                            print( 'maxed out' )
                            return None
                    print( f_minus )
                    return f_minus

                f_plus = f_plus + 1
                # temp precaution
                if f_plus == 5000:
                    print( 'maxed out' )
                    return None
        else:
            f_minus = frame  # frame iterator
            # loop foorward
            while warpedFrame > frame:
                warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttr, time = f_minus )
                if warpedFrame < frame:  # reached pivot, step backward
                    f_plus = f_minus + increment
                    # loop backward, increment
                    while warpedFrame < frame:
                        warpedFrame = cmds.getAttr( timeWarp + '.' + warpAttr, time = f_plus )
                        f_plus = f_plus + increment
                        # temp precaution
                        if f_plus == 5000:
                            print( 'maxed out' )
                            return None
                    print( f_plus )
                    return f_plus

                f_minus = f_minus - 1
                # temp precaution
                if f_minus == -5000:
                    print( 'maxed out' )
                    return None
    else:  # no warp
        print( 'no warp on frame', frame )
        return frame


def deleteWarp( timewarp ):
    '''
    
    '''
    objects = getTimeWarpMembers( timewarp )
    if objects:
        connectTimeWarp( objects, timewarp, connect = False )
    cmds.delete( timewarp )


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


def bakeInfinity( sparseKeys = True, smart = True, sim = False ):
    crvs = cmds.keyframe( q = True, name = True, sl = True )
    if crvs:
        start = cmds.playbackOptions( q = True, minTime = True )
        end = cmds.playbackOptions( q = True, maxTime = True )
        objs = cmds.listConnections( crvs, d = True, s = False, plugs = True )
        cmds.refresh( suspend = 1 )
        print( sim, '________' )
        cmds.bakeResults( objs, t = ( start, end ), simulation = sim, pok = True, smart = smart, sac = sparseKeys, sampleBy = 1 )
        cmds.refresh( suspend = 0 )
        message( str( len( objs ) ) + ' curves baked --' + str( objs ), maya = 1 )
    else:
        message( 'no curves are selected', maya = 1 )


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
