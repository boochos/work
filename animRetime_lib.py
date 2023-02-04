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
    # always on top
    alwaysOnTop_label = QtWidgets.QLabel( 'Window On Top:  ' )
    alwaysOnTop_check = QtWidgets.QCheckBox()
    alwaysOnTop_check.setChecked( True )
    alwaysOnTop_check.clicked.connect( lambda:onTopToggle_ui( main_window ) )
    # suffix layout
    sffx_line_layout = QtWidgets.QHBoxLayout()
    sffx_label = QtWidgets.QLabel( 'Warp node suffix option:  ' )
    sffx_edit = QtWidgets.QLineEdit()
    sffx_label.setMinimumWidth( 50 )
    #
    # sffx_line_layout.addWidget( alwaysOnTop_label )
    # sffx_line_layout.addWidget( alwaysOnTop_check )
    #
    sffx_line_layout.addWidget( sffx_label )
    sffx_line_layout.addWidget( sffx_edit )
    sffx_line_layout.addWidget( alwaysOnTop_label )
    sffx_line_layout.addWidget( alwaysOnTop_check )
    main_layout.addLayout( sffx_line_layout )
    #
    # buttons
    create_warp_button = QtWidgets.QPushButton( "Create Warp" )
    create_warp_button.clicked.connect( lambda: createTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 , sffx_edit.text() ) )
    create_warp_button.setStyleSheet( "background-color: darkgreen" )
    #
    connect_button = QtWidgets.QPushButton( "Add Controls" )
    connect_button.clicked.connect( lambda: connectToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ) )
    #
    disconnect_button = QtWidgets.QPushButton( "Remove Controls" )
    disconnect_button.clicked.connect( lambda: connectToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14, connect = False, connectLayers = True ) )
    #
    bake_button = QtWidgets.QPushButton( "Bake Warp" )
    bake_button.clicked.connect( lambda: bakeTimeWarp_ui( warp_list_widget ) )
    bake_button.setStyleSheet( "background-color: grey" )
    #
    aprox_button = QtWidgets.QPushButton( "Approximate Warp" )
    aprox_button.clicked.connect( lambda: approximateTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ) )
    aprox_button.setStyleSheet( "background-color: grey" )
    #
    select_button = QtWidgets.QPushButton( "Select Controls" )
    select_button.clicked.connect( lambda: selectTimeWarpMembers_ui( warp_list_widget ) )
    #
    delete_button = QtWidgets.QPushButton( "Delete Warp" )
    delete_button.clicked.connect( lambda: deleteTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ) )
    delete_button.setStyleSheet( "background-color: darkred" )
    #
    refresh_button = QtWidgets.QPushButton( "Refresh UI" )
    refresh_button.clicked.connect( lambda: refresh_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ) )
    refresh_button.setStyleSheet( "background-color: darkcyan" )
    #
    connectLayer_button = QtWidgets.QPushButton( "Add Layers" )
    connectLayer_button.clicked.connect( lambda: connectLayerToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14, connect = True, connectLayers = True ) )
    #
    disconnectLayer_button = QtWidgets.QPushButton( "Remove Layers" )
    disconnectLayer_button.clicked.connect( lambda: connectLayerToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14, connect = True, connectLayers = False ) )

    feedback_color = "white"
    # column lists
    lists_layout = QtWidgets.QHBoxLayout()
    # col 1
    col1_layout = QtWidgets.QVBoxLayout()
    col1_label1 = QtWidgets.QLabel( 'Time Warp Nodes :' )
    warp_list_widget = QtWidgets.QListWidget()
    col1_label2 = QtWidgets.QLabel( 'Anim Layers :' )
    animLayers_list_widget = QtWidgets.QListWidget()
    animLayers_list_widget.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
    # col 2
    col2_layout = QtWidgets.QVBoxLayout()
    col2_row1Label0_layout = QtWidgets.QHBoxLayout()
    col2_row1Label1_layout = QtWidgets.QHBoxLayout()
    col2_row1Label0_layout.addLayout( col2_row1Label1_layout )
    col2_row1Label1_layout.setAlignment( QtCore.Qt.AlignLeft )
    col2_label1 = QtWidgets.QLabel( 'Controls in scope:' )
    col2_label2 = QtWidgets.QLabel( '' )
    col2_label2.setStyleSheet( "color: " + feedback_color + ";" "font-weight: bold" )
    col2_row1Label2_layout = QtWidgets.QHBoxLayout()
    col2_row1Label0_layout.addLayout( col2_row1Label2_layout )
    col2_row1Label2_layout.setAlignment( QtCore.Qt.AlignRight )
    col2_label3 = QtWidgets.QLabel( 'Curves:' )
    col2_label4 = QtWidgets.QLabel( '' )
    col2_label4.setStyleSheet( "color: " + feedback_color + ";" "font-weight: bold" )
    col2_row1Label1_layout.addWidget( col2_label1 )
    col2_row1Label1_layout.addWidget( col2_label2 )
    col2_row1Label2_layout.addWidget( col2_label3 )
    col2_row1Label2_layout.addWidget( col2_label4 )
    members_list_widget = QtWidgets.QListWidget()
    members_list_widget.setSelectionMode( QtWidgets.QAbstractItemView.NoSelection )
    col2_row2Label0_layout = QtWidgets.QHBoxLayout()
    col2_row2Label1_layout = QtWidgets.QHBoxLayout()
    col2_row2Label0_layout.addLayout( col2_row2Label1_layout )
    col2_row2Label1_layout.setAlignment( QtCore.Qt.AlignLeft )
    col2_label11 = QtWidgets.QLabel( 'Anim Layers in scope:' )
    col2_label12 = QtWidgets.QLabel( '' )
    col2_label12.setStyleSheet( "color: " + feedback_color + ";" "font-weight: bold" )
    col2_row2Label2_layout = QtWidgets.QHBoxLayout()
    col2_row2Label0_layout.addLayout( col2_row2Label2_layout )
    col2_row2Label2_layout.setAlignment( QtCore.Qt.AlignRight )
    col2_label13 = QtWidgets.QLabel( 'Curves:' )
    col2_label14 = QtWidgets.QLabel( '' )
    col2_label14.setStyleSheet( "color: " + feedback_color + ";" "font-weight: bold" )
    col2_row2Label1_layout.addWidget( col2_label11 )
    col2_row2Label1_layout.addWidget( col2_label12 )
    col2_row2Label2_layout.addWidget( col2_label13 )
    col2_row2Label2_layout.addWidget( col2_label14 )
    animLayerMembers_list_widget = QtWidgets.QListWidget()
    animLayerMembers_list_widget.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
    # attach columns
    lists_layout.addLayout( col1_layout )  # attach col 1
    lists_layout.addLayout( col2_layout )  # attach col 2
    # attach rows
    main_layout.addLayout( top_layout )
    main_layout.addLayout( lists_layout )
    main_layout.addLayout( bottom_layout )
    #
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( 'Time Warp Tool' )
    main_window.resize( 450, 500 )
    #
    warp_list_widget.itemSelectionChanged.connect( lambda: getMembers_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ) )
    # members_list_widget.itemSelectionChanged.connect( lambda: get_tasks( warp_list_widget.currentItem().text(), members_list_widget.currentItem().text() ) )
    #
    #
    # layouts
    bottom_layout.addWidget( refresh_button )
    # col1
    create_layout = QtWidgets.QHBoxLayout()
    col1_layout.addLayout( create_layout )
    create_layout.addWidget( create_warp_button )
    create_layout.addWidget( delete_button )
    col1_layout.addWidget( col1_label1 )
    col1_layout.addWidget( warp_list_widget )
    col1_layout.addWidget( col1_label2 )
    col1_layout.addWidget( animLayers_list_widget )
    col1_layout.addWidget( connectLayer_button )
    col1_layout.addWidget( refresh_button )
    # col2
    connection_layout = QtWidgets.QHBoxLayout()
    col2_layout.addLayout( connection_layout )
    connection_layout.addWidget( select_button )
    connection_layout.addWidget( connect_button )
    connection_layout.addWidget( disconnect_button )
    col2_layout.addLayout( col2_row1Label0_layout )
    col2_layout.addWidget( members_list_widget )
    col2_layout.addLayout( col2_row2Label0_layout )
    # col2_layout.addWidget( col2_label11 )
    col2_layout.addWidget( animLayerMembers_list_widget )
    col2_layout.addWidget( disconnectLayer_button )
    bake_layout = QtWidgets.QHBoxLayout()
    col2_layout.addLayout( bake_layout )
    bake_layout.addWidget( bake_button )
    bake_layout.addWidget( aprox_button )
    #
    #
    getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
    #
    # parse current scene
    # get_current( project_list_widget, members_list_widget, tasks_list_widget, scene_list_widget )

    return main_window


def getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ):
    '''
    clears all lists, populates timewarps and anim layers in scene
    '''
    print( 'getwarpsui' )
    # clear columns
    warp_list_widget.clear()
    animLayers_list_widget.clear()
    members_list_widget.clear()
    animLayerMembers_list_widget.clear()
    #
    getMemberCount( None, col2_label2, col2_label4, col2_label12, col2_label14 )
    # populate
    timewarps = getTimeWarps()
    if timewarps:
        for t in timewarps:
            warp_list_widget.addItem( t )
    #
    animLayers = getAnimLayers()
    if animLayers:
        for a in animLayers:
            animLayers_list_widget.addItem( a )
        animLayers_list_widget.selectAll()


def getMembers_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget , col2_label2, col2_label4, col2_label12, col2_label14 ):
    '''
    import webrImport as web
    ar = web.mod("animRetime_lib_DEVS")
    sel = cmds.ls(sl=1, fl=1)[0] 
    members = ar.getTimeWarpMembers2( sel )
    
    populates members of timewarp selected: controls and anim layers
    will add labels for number of members in list
    '''
    print( 'membersui' )
    timewarp = ''
    timewarp = warp_list_widget.currentItem().text()
    members_list_widget.clear()
    animLayerMembers_list_widget.clear()
    if cmds.objExists( timewarp ):
        # print( timewarp )
        # members = getTimeWarpMembers2( timewarp )
        members = getTimeWarpMembers3( timewarp )
        if members:
            for m in members:
                members_list_widget.addItem( m )
        # members = getTimeWarpMembers2( timewarp )
        layerMembers = getTimeWarpAnimLayerMembers( timewarp )
        if layerMembers:
            for m in layerMembers:
                animLayerMembers_list_widget.addItem( m )
        getMemberCount( timewarp, col2_label2, col2_label4, col2_label12, col2_label14 )
    else:
        # redraw
        getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )


def getMemberCount( timeWarp, col2_label2, col2_label4, col2_label12, col2_label14 ):
    '''
    
    '''
    if timeWarp:
        # control
        n = cmds.sets( setControlName( timeWarp ), q = True, s = True )
        col2_label2.setText( str( n ) )
        # curve
        n = cmds.sets( setCurveName( timeWarp ), q = True, s = True )
        col2_label4.setText( str( n ) )
        # layers
        n = cmds.sets( setLayerName( timeWarp ), q = True, s = True )
        col2_label12.setText( str( n ) )
        # layer curves
        n = cmds.sets( setLayerCurveName( timeWarp ), q = True, s = True )
        col2_label14.setText( str( n ) )
    else:
        # control
        col2_label2.setText( str( '' ) )
        # curve
        col2_label4.setText( str( '' ) )
        # layers
        col2_label12.setText( str( '' ) )
        # layer curves
        col2_label14.setText( str( '' ) )


def createTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 , suffix = '' ):
    '''
    
    '''
    print( 'createui' )
    cmds.undoInfo( openChunk = True )
    #
    sel = cmds.ls( sl = 1 )
    timewarp = createTimeWarp( suffix )
    #
    layers = []
    qLayers = animLayers_list_widget.selectedItems()
    for q in qLayers:
        layers.append( q.text() )
    #
    setCreate( timewarp )
    #
    connectToTimeWarp( layers, timewarp, [] )  # layers
    connectToTimeWarp( sel, timewarp, layers )  # objects
    # redraw
    getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
    # select new timewarp
    selectTimeWarp_ui( timewarp, warp_list_widget )
    #
    cmds.select( sel )
    #
    cmds.undoInfo( closeChunk = True )


def connectToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14, connect = True, connectLayers = True ):
    '''
    
    '''
    print( 'connectui' )
    chunkName = ''
    if connect:
        chunkName = 'connectToTimeWarp_ui'
    else:
        chunkName = 'disconnectToTimeWarp_ui'
    #
    # cmds.undoInfo( openChunk = True, chunkName = chunkName )
    #
    go = True
    layers = []
    #
    timewarp = ''
    qtimewarp = warp_list_widget.currentItem()  # get selected warp
    if qtimewarp:
        timewarp = qtimewarp.text()
    #
    sel = cmds.ls( sl = 1 )
    if not sel:
        go = False

    if go:
        if timewarp and sel:  #
            if timewarp in sel:
                sel.remove( timewarp )
            # get currently connected layers
            layers = cmds.sets( setLayerName( timewarp ), q = True )
            # sel = cmds.ls( sl = 1 )
            if timewarp not in sel:
                connectToTimeWarp( sel, timewarp, layers, connect )
                # redraw ui
                getMembers_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
                #
            else:
                message( 'Remove ___timeWarpNode___ node from selection of objects to connect.', warning = True )
        else:
            message( ' select a timewarp in the ui and objects in the scene.', warning = True )
    #
    else:
        message( 'Nothing selected.', warning = True )
    # cmds.undoInfo( closeChunk = True, chunkName = chunkName )


def connectLayerToTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14, connect = True, connectLayers = True ):
    '''
    
    '''
    #
    go = True
    members = []
    layers = []
    timewarp = ''
    qtimewarp = warp_list_widget.currentItem()  # get selected warp
    if qtimewarp:
        timewarp = qtimewarp.text()
    #
    if timewarp:
        members = getTimeWarpMembers3( timewarp )
        #
        if connectLayers:
            qLayers = animLayers_list_widget.selectedItems()
            if qLayers:
                for q in qLayers:
                    layers.append( q.text() )
            else:
                message( 'Select a layer', warning = True )
                go = False
        else:
            qLayers = animLayerMembers_list_widget.selectedItems()
            if qLayers:
                for q in qLayers:
                    layers.append( q.text() )
            else:
                message( 'Select a layer', warning = True )
                go = False
        #
        if go:
            connectToTimeWarp( members, timewarp, layers, connect = connect, connectLayers = connectLayers )  # timewarp connects/disconnects with object curves associated with given layers
            connectToTimeWarp( layers, timewarp, [], connect = connect, connectLayers = connectLayers )  # timewarp connects/disconnects with layer(s) curves
            getMembers_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
        else:
            print( layers )
            message( 'No layers selected', warning = True )
    else:
        message( 'Select a timewarp', warning = True )


def bakeTimeWarp_ui( warp_list_widget ):
    # pass
    cmds.undoInfo( openChunk = True, chunkName = 'bakeTimeWarp_ui' )
    #
    sel = cmds.ls( sl = 1 )
    members = None
    timeWarp = getTimeWarpNode( warp_list_widget )
    if timeWarp:
        # members = getTimeWarpMembers2( timeWarp, select = True )
        members = getTimeWarpMembers3( timeWarp )
        # layers = getTimeWarpAnimLayerMembers( timeWarp )
        if members:
            bakeTimeWarp( timeWarp, members, sparseKeys = True, sim = False, sampleBy = 1 )
            selectTimeWarp_ui( timeWarp, warp_list_widget )
        else:
            message( 'No members connected to timeWarp node', warning = True )
    else:
        message( 'Select a timeWarp node in the left column', warning = True )
    #
    cmds.select( sel )
    cmds.undoInfo( closeChunk = True, chunkName = 'bakeTimeWarp_ui' )


def approximateTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ):
    pass
    cmds.undoInfo( openChunk = True, chunkName = 'approximateTimeWarp_ui' )
    #
    sel = cmds.ls( sl = 1 )
    members = None
    timeWarp = getTimeWarpNode( warp_list_widget )
    if timeWarp:
        # members = getTimeWarpMembers2( timeWarp, select = True )
        members = getTimeWarpMembers3( timeWarp )
        layers = getTimeWarpAnimLayerMembers( timeWarp )
        if members:
            approximateTimeWarp( timeWarp, members, layers )
        else:
            message( 'No members connected to timeWarp node', warning = True )
    else:
        message( 'Select a timeWarp node in the left column', warning = True )
    #
    getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
    selectTimeWarp_ui( timeWarp, warp_list_widget )
    cmds.select( sel )
    cmds.undoInfo( closeChunk = True, chunkName = 'approximateTimeWarp_ui' )


def selectTimeWarpMembers_ui( warp_list_widget ):
    '''
    
    '''
    print( 'selectui' )
    cmds.undoInfo( openChunk = True, chunkName = 'selectTimeWarpMembers_ui' )
    #
    timewarp = ''
    qtimewarp = warp_list_widget.currentItem()  # get selected warp
    if qtimewarp:
        timewarp = qtimewarp.text()
        if timewarp:
            # members = getTimeWarpMembers2( timewarp, select = True )
            members = getTimeWarpMembers3( timewarp, select = True )
            if members:
                return True
            else:
                message( 'No members for given TimeWarp', warning = True )
    else:
        message( 'Select a timewarp node in the left column', warning = True )
        return False
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'selectTimeWarpMembers_ui' )


def deleteTimeWarp_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ):
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
        getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
    else:
        message( ' No TimeWarp node selected in UI list' , warning = 1 )
    #
    cmds.undoInfo( closeChunk = True, chunkName = 'deleteTimeWarp_ui' )


def onTopToggle_ui( w ):
    '''
    window always on top toggle
    '''
    w.setWindowFlags( w.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint )
    # w.setWindowFlags( w.windowFlags() | QtCore.Qt.WindowStaysOnTopHint ) # enable
    # window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint) # disable
    w.show()
    pass


def selectTimeWarp_ui( timewarp, warp_list_widget ):
    '''
    
    '''
    # select new timewarp
    item = warp_list_widget.findItems( timewarp, QtCore.Qt.MatchExactly )
    if item:
        warp_list_widget.setCurrentItem( item[0] )


def refresh_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 ):
    '''
    
    '''
    #
    timewarp = ''
    qtimewarp = warp_list_widget.currentItem()  # get selected warp
    if qtimewarp:
        timewarp = qtimewarp.text()
    #
    getWarps_ui( warp_list_widget, animLayers_list_widget, members_list_widget, animLayerMembers_list_widget, col2_label2, col2_label4, col2_label12, col2_label14 )
    #
    if timewarp:
        if cmds.objExists( timewarp ):
            selectTimeWarp_ui( timewarp, warp_list_widget )
            print( 'here' )
            #
            getDeadCurves( timewarp )


def findDisconnected_ui():
    '''
    Check scope for disconnected curves
    Compare against currently connected
    '''
    pass


def ____MISC____():
    pass


def warpAttrStr():
    return 'warpedFrame'


def warpTimeAttrStr():
    return 'timeWarpedFrame'


def warpNodeStr():
    return '___timeWarpNode___'


def createTimeWarp( suffix = '' ):
    '''
    stuff
    '''
    print( 'create' )
    # active_layer = getActiveLayer()
    locked = False
    base_layer = 'BaseAnimation'
    found_layers = cmds.ls( type = 'animLayer' )
    attr = warpAttrStr()
    if suffix:
        name = warpNodeStr() + suffix + '___'
    else:
        name = warpNodeStr()
    name = getUniqueName( name )
    if not cmds.objExists( name ):
        loc = cmds.spaceLocator( n = name )[0]
        # attr
        cmds.addAttr( loc, ln = attr, h = False, at = 'float' )  # fake time attr !!!
        cmds.setAttr( ( loc + '.' + attr ), cb = True )
        cmds.setAttr( ( loc + '.' + attr ), k = True )
        cmds.addAttr( loc, ln = warpTimeAttrStr(), h = False, at = 'time' )  # time attr !!!
        cmds.setAttr( ( loc + '.' + warpTimeAttrStr() ), cb = True )
        cmds.setAttr( ( loc + '.' + warpTimeAttrStr() ), k = False )
        cmds.connectAttr( loc + '.' + attr, loc + '.' + warpTimeAttrStr() )  # try this to see if problems with values gets fixed with export/import animations
        # range
        ast = cmds.playbackOptions( q = True, ast = True )
        aet = cmds.playbackOptions( q = True, aet = True )
        # key
        if base_layer in found_layers:
            locked = cmds.animLayer( base_layer, q = True, lock = True )
            if locked:
                cmds.animLayer( base_layer, edit = True, lock = False )
            # mel.eval( 'selectLayer(\"' + 'BaseAnimation' + '\");' )
        cmds.setKeyframe( loc, at = attr, time = ( ast, ast ), value = ast, ott = 'spline', itt = 'spline' )
        cmds.setKeyframe( loc, at = attr, time = ( aet, aet ), value = aet, ott = 'spline', itt = 'spline' )
        cmds.setInfinity( pri = 'linear' )
        cmds.setInfinity( poi = 'linear' )
        if base_layer in found_layers:
            cmds.animLayer( base_layer, edit = True, lock = locked )
        #
        # lock - [lock, keyable], [visible, lock, keyable]
        place.setChannels( loc, [True, False], [True, False], [True, False], [False, False, False] )
        return loc
    else:
        print( 'choose different prefix, object already exists', name )


def connectToTimeWarp( objects = [], timeWarp = '', layers = [], connect = True, connectLayers = True ):
    '''
    objects and animLayers get added/removed to/from sets
    anim curves get connected/disconnected to/from retime
    '''
    print( 'connect ANIMCURVES______________', connect )
    # start timer
    start = time.time()
    num = 0
    if objects:
        num = len( objects )
    i = 1
    allAnimCurves = []
    warpAttr = '_' + warpTimeAttrStr()
    warpCurve = None
    lockStatus = getAnimLayersLockSatus()
    animLayersUnlock()
    #
    if timeWarp:
        if objects:
            for obj in objects:
                message( str( i ) + ' of ' + str( num ) + ' --  ' + obj, maya = True )
                animCurves = getAnimCurves2( object = obj, layers = layers )
                #
                if animCurves:
                    for curve in animCurves:
                        # store state, unlock
                        curve_lock_state = cmds.getAttr( curve + '.ktv', l = True )
                        cmds.setAttr( curve + '.ktv', l = 1 )
                        cmds.setAttr( curve + '.ktv', l = 0 )
                        # allAnimCurves.append( curve ) # does nothing currently
                        connections = cmds.listConnections( timeWarp + '.' + warpTimeAttrStr(), s = 0, d = 1 )
                        if connect and connectLayers:
                            # connect anim curves to retime and add to sets
                            if connections:
                                if curve not in connections:
                                    # print( 'no', curve )
                                    cmds.connectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input', f = True )
                                    if cmds.objectType( obj ) == 'animLayer':
                                        cmds.sets( curve , add = setLayerCurveName( timeWarp ), e = True )
                                    else:
                                        cmds.sets( curve , add = setCurveName( timeWarp ), e = True )
                            else:
                                cmds.connectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input', f = True )
                                if cmds.objectType( obj ) == 'animLayer':
                                    cmds.sets( curve , add = setLayerCurveName( timeWarp ), e = True )
                                else:
                                    cmds.sets( curve , add = setCurveName( timeWarp ), e = True )
                        else:
                            # disconnect anim curves from retime and remove from sets
                            if connections:
                                if curve in connections:
                                    cmds.disconnectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input' )
                                    if cmds.objectType( obj ) == 'animLayer':
                                        cmds.sets( curve , remove = setLayerCurveName( timeWarp ), e = True )
                                    else:
                                        cmds.sets( curve , remove = setCurveName( timeWarp ), e = True )
                        # restore state
                        cmds.setAttr( curve + '.ktv', l = curve_lock_state )
                else:
                    # print( 'No animCurves connected to object:', obj )
                    pass
                # object set membership
                if cmds.objectType( obj ) != 'animLayer':
                    if connect:
                        setAddMembers( [obj] , setControlName( timeWarp ) )
                    else:
                        setRemoveMembers( [obj] , setControlName( timeWarp ) )
                else:
                    if connectLayers:
                        setAddMembers( [obj] , setLayerName( timeWarp ) )
                    else:
                        setRemoveMembers( [obj] , setLayerName( timeWarp ) )
                #
                i = i + 1
            # cleanup
            cleanConversionNodes( timeWarp + '.' + warpTimeAttrStr() )
        else:
            message( 'No objects to connect / disconnect', warning = True )
        # anim layer set membership
        '''
        if connectLayers:
            if layers:
                setAddMembers( layers , setLayerName( timeWarp ) )
        else:
            if layers:
                setRemoveMembers( layers , setLayerName( timeWarp ) )'''

    animLayersRestoreLock( lockStatus )
    # end timer
    end = time.time()
    elapsed = end - start
    print( 'Connect time: ' + str( elapsed / 60 ) + ' min', connect )


def bakeTimeWarp( timeWarp = '', members = [], sparseKeys = True, sim = False, sampleBy = 1.0, unlock = True ):
    '''
    
    '''
    #
    result = []
    start = 0.0
    end = 0.0

    #
    if unlock:
        layerMembers = cmds.sets( setLayerName( timeWarp ), q = True )
        for layer in layerMembers:
            cmds.animLayer( layer, edit = True, lock = True )
            cmds.animLayer( layer, edit = True, lock = False )

    # discrepancy check
    animCurveMembers = getAnimCurveMembers( timeWarp, select = False )
    animCurveMembersInt = 0
    if animCurveMembers:
        animCurveMembersInt = len( animCurveMembers )

    layerCurveMembers = getLayerCurveMembers( timeWarp, select = False )
    layerCurveMembersInt = 0
    if layerCurveMembers:
        layerCurveMembersInt = len( layerCurveMembers )

    animCurves = getWarpedAnimCurves( timeWarp )
    if animCurves:
        if len( animCurves ) != animCurveMembersInt + layerCurveMembersInt:
            print( 'connected curves:', len( animCurves ), 'curves in sets:', len( animCurveMembers ) + len( layerCurveMembers ) )
            message( 'Discrepancy between connected curves and curves in sets. Operations Stopped', warning = True )
            return

        #
        for animCurve in animCurves:
            if unlock:
                cmds.setAttr( animCurve + '.ktv', l = 1 )
                cmds.setAttr( animCurve + '.ktv', l = 0 )

        result = getBakeRange( animCurves = animCurves )
        start = result[0]
        end = result[1]

        #
        cmds.refresh( suspend = 1 )
        #
        # print( 'sparseKeys: ', sparseKeys )
        # print( 'simulation: ', sim )
        # print( 'sampleBy: ', sampleBy )
        if members:
            cmds.bakeResults( members, t = ( start, end ), simulation = sim, pok = True, sac = sparseKeys, sampleBy = sampleBy )
        else:
            message( 'No members given to bake' )

        connections = cmds.listConnections( timeWarp + '.' + warpTimeAttrStr(), s = 0, d = 1 )
        if connections:
            for curve in animCurves:
                if curve in connections:
                    cmds.disconnectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input' )
                    if animCurveMembers:
                        if curve in animCurveMembers:
                            setRemoveMembers( [curve], setCurveName( timeWarp ) )
                    if layerCurveMembers:
                        if curve in layerCurveMembers:
                            setRemoveMembers( [curve], setLayerCurveName( timeWarp ) )

        cmds.refresh( suspend = 0 )
        message( str( len( members ) ) + ' curves baked --' + str( members ), maya = 1 )
    else:
        message( 'No anim curves provided to derive at bake range.' )


def approximateTimeWarp( timeWarp = '', members = [], layers = [], unlock = True ):
    '''
    
    '''
    print( 'apprx' )
    start = time.time()
    # ui off
    uiEnable()
    #
    if unlock:
        layerMembers = cmds.sets( setLayerName( timeWarp ), q = True )
        for layer in layerMembers:
            cmds.animLayer( layer, edit = True, lock = True )
            cmds.animLayer( layer, edit = True, lock = False )

    # discrepancy check
    animCurveMembers = getAnimCurveMembers( timeWarp, select = False )
    animCurveMembersInt = 0
    if animCurveMembers:
        animCurveMembersInt = len( animCurveMembers )

    layerCurveMembers = getLayerCurveMembers( timeWarp, select = False )
    layerCurveMembersInt = 0
    if layerCurveMembers:
        layerCurveMembersInt = len( layerCurveMembers )

    animCurves = getWarpedAnimCurves( timeWarp )
    if animCurves:
        if len( animCurves ) != animCurveMembersInt + layerCurveMembersInt:
            print( 'connected curves:', len( animCurves ), 'curves in sets:', animCurveMembersInt + layerCurveMembersInt )
            message( 'Discrepancy between connected curves and curves in sets. Operations Stopped', warning = True )
            return
        #
        frames = getKeyedFrames2( animCurves )
        frames.reverse()
        remap_frames_dict = remapFrames( timeWarp = timeWarp, frames = frames, step = 10.0 )
        # print( frames )
        # return
        if remap_frames_dict:
            for animCurve in animCurves:
                # store state
                curve_lock_state = cmds.getAttr( animCurve + '.ktv', l = True )
                # print( animCurve )
                cmds.select( animCurve )
                if unlock:
                    cmds.setAttr( animCurve + '.ktv', l = 1 )
                    cmds.setAttr( animCurve + '.ktv', l = 1 )
                    cmds.setAttr( animCurve + '.ktv', l = 0 )
                    # bug, using hotkeys(h,j) doesnt set the 'lock' attr in maya internally, forcing to unlock
                    # mel.eval( 'GraphEditorLockChannel;' )
                    # mel.eval( 'GraphEditorUnlockChannel;' )
                framesTmp = cmds.keyframe( animCurve, q = True )
                #
                for f in frames:
                    if f in framesTmp and f != remap_frames_dict[f]:
                        # print( str( f ) + ' ' + str( remap_frames_dict[f] ) )
                        try:
                            cmds.keyframe( edit = 1, absolute = 1, timeChange = remap_frames_dict[f], time = ( f, f ), option = 'over' )  # only works for active animLayer
                        except:
                            # curve could be locked, run mel command to unluck, curve should be selected
                            '''
                            cmds.setAttr('head_mainIk_ctrl_translateZ_head_tremble_inputB.ktv', l=0)
                            l = cmds.getAttr('head_mainIk_ctrl_translateZ_head_tremble_inputB.ktv', l=1) # ktv = key/time value, on every anim curve
                            print(l)
                            '''
                            # cmds.keyframe( edit = 1, absolute = 1, timeChange = remap_frames_dict[f], time = ( f, f ), option = 'over' )  # only works for active animLayer
                            print( 'Fail. Couldnt move keys on frame: ' + str( f ) + ' to frame: ' + str( remap_frames_dict[f] ) + ' on curve: ' + animCurve )
                            # return
                # restore state
                cmds.setAttr( animCurve + '.ktv', l = curve_lock_state )

            # disconnect timeWarp
            if timeWarp not in members:
                connections = cmds.listConnections( timeWarp + '.' + warpTimeAttrStr(), s = 0, d = 1 )
                #
                if connections:
                    for curve in animCurves:
                        if curve in connections:
                            cmds.disconnectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input' )
                            if animCurveMembers:
                                if curve in animCurveMembers:
                                    setRemoveMembers( [curve], setCurveName( timeWarp ) )
                            if layerCurveMembers:
                                if curve in layerCurveMembers:
                                    setRemoveMembers( [curve], setLayerCurveName( timeWarp ) )
    else:
        message( 'Found no curves to approximate' )

    #
    end = time.time()
    elapsed = end - start
    message( 'Approx elapse time: ' + str( elapsed ), warning = False )
    # ui on
    uiEnable()
    #
    # watch for remapped frames clashing with original frame, can put key on top of existing key


def remapFrames( timeWarp = '', frames = [], step = 1.0 ):
    '''
    
    '''
    remapped_frames = []
    remap_frames_dict = {}
    go = False
    start = time.time()
    #
    for frame in frames:
        remapped_frames.append( seekWardpedFrame( timeWarp, frame, step = step ) )
    #
    if len( frames ) == len( remapped_frames ):
        #
        for f in range( len( frames ) ):
            remap_frames_dict[frames[f]] = remapped_frames[f]
        print( 'dict: ', remap_frames_dict )
        go = True
    else:
        message( 'mismatch number of frames and warped frames', warning = True )

    #
    end = time.time()
    elapsed = end - start
    message( 'RemapFrames elapse time: ' + str( elapsed ), warning = False )

    if go:
        return remap_frames_dict
    else:
        return False


def seekWardpedFrame( timeWarp = '', frame = 1, step = 1.0 ):
    '''
    
    '''
    tolerance = 0.05  # 0.005
    forward = True
    steps = 50000  # max steps in one direction(forward)
    direction = step
    #
    # cmds.currentTime( frame )
    warpedFrame = cmds.getAttr( timeWarp + '.' + warpTimeAttrStr(), time = frame )
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
        warpedFrame = cmds.getAttr( timeWarp + '.' + warpTimeAttrStr(), time = current )
        # heading backward
        if warpedFrame < frame and not forward:  # moved backward past frame
            dif = frame - warpedFrame
            #
            if dif > tolerance:
                # print( 'too far: ', dif, 'reverse', k, 'step: ', step )
                return seekWardpedFrame( timeWarp = timeWarp, frame = frame, step = step * 0.98 )
            else:
                # print( '-- new: ', current, '-- old: ', frame, '-- dif: ', dif, k )
                return  round( current, 2 )  # maya timeline seems to like up to 2 decimal points
        # heading forward
        if warpedFrame > frame and forward:  # moved forward past frame
            dif = warpedFrame - frame
            #
            if dif > tolerance:
                # print( 'too far: ', dif, 'reverse', k, 'step: ', step )
                return seekWardpedFrame( timeWarp = timeWarp, frame = frame, step = step * 0.98 )
            else:
                # print( '-- new: ', current, '-- old: ', frame, '-- dif: ', dif, k )
                return round( current, 2 )  # maya timeline seems to like up to 2 decimal points
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
    objects = getTimeWarpMembers3( timewarp )
    if objects:
        connectToTimeWarp( objects, timewarp, connect = False )
    cmds.delete( [setMasterName( timewarp ), setControlName( timewarp ), setLayerName( timewarp ), setCurveName( timewarp ), setLayerCurveName( timewarp )] )
    cmds.delete( timewarp )


def cleanConversionNodes( object = '' ):
    '''
    find conversion nodes connected to object with no output connection and delete them
    leftovers form disconnect objects from timewarp node
    '''
    # sel = cmds.ls( sl = 1 )[0]
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


def manuallyDisconnectAnimLayer( timeWarp = '' ):
    '''
    assumes 
    active anim layer is meant to be disconnected from retime
    retime node is selected
    '''
    # store selection, assume
    timeWarp = cmds.ls( sl = 1 )
    if timeWarp:
        timeWarp = timeWarp[0]
    if warpNodeStr() in timeWarp:
        #
        animLayers = cmds.ls( type = 'animLayer' )
        activeLayer = None
        for lyr in animLayers:
            if cmds.animLayer( lyr, sel = 1, q = 1 ):
                activeLayer = lyr
                break
        # get curves
        result = cmds.animLayer( activeLayer, q = 1, anc = 1 )
        cmds.select( result )
        print( result )
        # disconnect
        for curve in result:
            # pass
            try:
                cmds.disconnectAttr( timeWarp + '.' + warpTimeAttrStr(), curve + '.input' )
            except:
                print( 'No connection or error: ', curve )
        # reselect
        cmds.select( timeWarp )
    else:
        print( 'Selection is not a timewarp node' )


def ___SETS___():
    pass


def setStr():
    return 'set'


def setControlStr():
    return 'anim_controls___'


def setLayerStr():
    return 'layers___'


def setCurveStr():
    return 'anim_curves___'


def setLayerCurveStr():
    return 'layer_curves___'


def setMasterName( name = '' ):
    return name + setStr()


def setControlName( name = '' ):
    return name + setControlStr() + setStr()


def setLayerName( name = '' ):
    return name + setLayerStr() + setStr()


def setCurveName( name = '' ):
    return name + setCurveStr() + setStr()


def setLayerCurveName( name = '' ):
    return name + setLayerCurveStr() + setStr()


def setCreate( name = '', hide = False ):
    '''
    
    '''
    sel = cmds.ls( sl = 1 )
    cmds.select( clear = 1 )
    # create
    control_set = cmds.sets( name = setControlName( name = name ) )
    layer_set = cmds.sets( name = setLayerName( name = name ) )
    curve_set = cmds.sets( name = setCurveName( name = name ) )
    layerCurve_set = cmds.sets( name = setLayerCurveName( name = name ) )
    master = cmds.sets( name = setMasterName( name = name ) )
    # add
    cmds.sets( [name, control_set, layer_set, curve_set, layerCurve_set] , add = master, e = True )
    # hide
    if hide:
        cmds.setAttr( control_set + '.hiddenInOutliner', True )
        cmds.setAttr( layer_set + '.hiddenInOutliner', True )
        cmds.setAttr( curve_set + '.hiddenInOutliner', True )
        cmds.setAttr( layerCurve_set + '.hiddenInOutliner', True )
        cmds.setAttr( master + '.hiddenInOutliner', True )
    #
    cmds.select( sel )


def setAddMembers( members = [], set = '' ):
    '''
    
    '''
    # print( members )
    # print( set )
    if members:
        cmds.sets( members , add = set, e = True )
    else:
        message( 'No members to add' )


def setRemoveMembers( members = [], set = '' ):
    '''
    
    '''
    # print( members )
    # print( set )
    if members:
        current_members = cmds.sets( set, q = True )
        if current_members:
            for member in members:
                if member in current_members:
                    cmds.sets( member , remove = set, e = True )
        else:
            message( 'No current members' )
    else:
        message( 'No members to remove' )


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


def getWarpedAnimCurves( timeWarp = '' ):
    '''
    
    '''
    curveTypes = [
        'animCurveTL',
        'animCurveTU',
        'animCurveTA',
        ]
    animCurves = []
    connections = cmds.listConnections( timeWarp + '.' + warpTimeAttrStr(), s = 0, d = 1 )
    if connections:
        for c in connections:
            t = cmds.objectType( c )
            if t in curveTypes:
                animCurves.append( c )
    # print(animCurves)
    return animCurves


def getWarpedAnimCurvesQC( timeWarp = '' ):
    '''
    
    '''
    # discrepancy check
    animCurveMembers = getAnimCurveMembers( timeWarp, select = False )
    layerCurveMembers = getLayerCurveMembers( timeWarp, select = False )
    animCurves = getWarpedAnimCurves( timeWarp )
    if len( animCurves ) != len( animCurveMembers ) + len( layerCurveMembers ):
        print( 'connected curves:', len( animCurves ), 'curves in sets:', len( animCurveMembers ) + len( layerCurveMembers ) )
        message( 'Discrepancy between connected curves and curves in sets. Operations Stopped', warning = True )
        return []
    return animCurves


def getObjectsAnimLayers( object = '' ):
    '''
    
    '''
    #
    animLayers = []
    isAnimLayer = False
    sel = cmds.ls( sl = 1 )
    #
    t = cmds.objectType( object )
    if t == 'animLayer':
        isAnimLayer = True
    #
    if isAnimLayer:
        cmds.select( object )
        animLayers = cmds.animLayer( q = 1, afl = 1 )
    else:
        con = cmds.listConnections( object, s = 0, d = 1, t = 'animLayer' )
        if con:
            animLayers = list( set( con ) )
    cmds.select( sel )
    return animLayers


def getAnimCurves( object = '', max_recursion = 0, direction = 'in' ):
    '''
    find animCurves, 3 types
    animurveTT = time, not part of search
    '''
    # print( 'getanimcurves', object )
    result = []
    attrs = cmds.listAttr( object, cb = 1 )
    # return
    for attr in attrs:  # should optimize for attr type. too many loops
        obj = object + '.' + attr
        # print( '___attr', attr )
        animCrvs = getConnections( object = obj, direction = direction, find = 'animCurve', find_through = [], skip = [object], max_recursion = max_recursion, ignore_types = ['transform', 'animLayer'], results = [] )
        # print( '___curves', animCrvs )
        if animCrvs:
            for c in animCrvs:
                result.append( c )
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


def getAnimCurves2( object = '', layers = [] ):
    '''
    list of objects
    if no layers are given assume all layers are in scope
    '''
    # print( 'getanimcurves2 beta' )
    #
    mel.eval( 'source "buildSetAnimLayerMenu.mel";' )
    # find layers
    active_layer = getActiveLayer()
    found_layers = cmds.ls( type = 'animLayer' )
    member_of_layers = getObjectsAnimLayers( object )
    attrs = cmds.listAttr( object, k = 1 )
    crvs = []
    #
    if attrs:
        t = cmds.objectType( object )
        if t != 'animLayer':
            if member_of_layers:
                # print( 'member: ', member_of_layers )
                if found_layers and layers:  # specific layers
                    for found_layer in found_layers:
                        if found_layer in layers:
                            if found_layer in member_of_layers:
                                #
                                mel.eval( 'selectLayer(\"' + found_layer + '\");' )
                                for attr in attrs:
                                    crv = cmds.findKeyframe( object, at = attr, c = 1 )
                                    if crv:
                                        crvs.append( crv[0] )
                            elif found_layer == 'BaseAnimation':
                                #
                                mel.eval( 'selectLayer(\"' + found_layer + '\");' )
                                for attr in attrs:
                                    crv = cmds.findKeyframe( object, at = attr, c = 1 )
                                    if crv:
                                        crvs.append( crv[0] )
                            else:
                                # no curves to grab, not a member of layer
                                pass
                        else:
                            # curves not queried for this layer
                            pass
            elif found_layers and not member_of_layers:
                # print( 'not a member of any existing layers' )
                # not a member of any layer,
                # need BaseAnimation curves, despite no connection to BaseAnimation layer
                if layers:
                    if 'BaseAnimation' in layers:
                        mel.eval( 'selectLayer(\"' + 'BaseAnimation' + '\");' )
                        for attr in attrs:
                            crv = cmds.findKeyframe( object, at = attr, c = 1 )
                            if crv:
                                crvs.append( crv[0] )
            elif not found_layers:  # no layers exist, ask for curves
                # print( 'no layers in scene' )
                for attr in attrs:
                    crv = cmds.findKeyframe( object, at = attr, c = 1 )
                    if crv:
                        crvs.append( crv[0] )
            else:
                pass
                # message('No anim layer scenario was used')
        else:
            # print( 'is anim layer' )
            # is animLayer, need BaseAnimation curves, only supports animLayers with BaseAnimation curves, not layered
            if 'BaseAnimation' in found_layers:
                mel.eval( 'selectLayer(\"' + 'BaseAnimation' + '\");' )
                for attr in attrs:
                    crv = cmds.findKeyframe( object, at = attr, c = 1 )
                    if crv:
                        crvs.append( crv[0] )
    # restore active layer
    if active_layer:
        mel.eval( 'selectLayer(\"' + active_layer + '\");' )
    elif 'BaseAnimation' in found_layers:
        mel.eval( 'animLayerEditorOnSelect \"' + 'BaseAnimation' + '\" 0;' )
    else:
        pass
    #
    crvs = list( set( crvs ) )
    # print( crvs )
    return crvs


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
        # crvs = getAnimCurves( object = s, max_recursion = 1 )
        crvs = getAnimCurves2( object = s )
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
    warpCurve = cmds.listConnections( timeWarp + '.' + warpTimeAttrStr() )
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
        print( timeWarp + '.' + warpTimeAttrStr(), 'has no keys' )
    #
    # print( objects )
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
    # found = getConnections( timeWarp + '.' + warpTimeAttrStr(), direction = 'out', find = 'transform', find_through = [], skip = skip, results = [] )  # had to add results value, app wasnt clearing its state for some reason
    found = getConnections( timeWarp + '.' + warpTimeAttrStr(), direction = 'out', find = '', find_through = [], skip = skip, results = [] )  #
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


def getTimeWarpMembers3( timeWarp, select = False ):
    '''
    find via set
    '''
    controls = cmds.sets( setControlName( timeWarp ), q = True )
    if select:
        cmds.select( controls )
    return controls


def getTimeWarpAnimLayerMembers( timeWarp, select = False ):
    '''
    find via set
    '''
    animLayers = cmds.sets( setLayerName( timeWarp ), q = True )
    if select:
        cmds.select( animLayers )
    return animLayers


def getAnimCurveMembers( timeWarp, select = False ):
    '''
    find via set
    '''
    curves = cmds.sets( setCurveName( timeWarp ), q = True )
    if select:
        cmds.select( curves )
    return curves


def getLayerCurveMembers( timeWarp, select = False ):
    '''
    find via set
    '''
    curves = cmds.sets( setLayerCurveName( timeWarp ), q = True )
    if select:
        cmds.select( curves )
    return curves


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
    dead_end = [
        'nodeGraphEditorInfo',
        'animLayer'
        ]
    for d in dead_end:
        ignore_types.append( d )
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
                if find:
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
                else:
                    if cmds.objectType( c ) not in find_through and cmds.objectType( c ) not in non_pass_through:  # find = abbreviated ie. animCurveTL = animCurve
                        if c not in results:
                            results.append( c )
                        if c not in x:
                            x.append( c )  # death loop with out this
                        found = True
                        print( 'found: ', c, find )
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


def getAnimLayers():
    '''
    get layers
    '''
    animLayers = cmds.ls( type = 'animLayer' )
    return animLayers


def getAnimLayersLockSatus():
    '''
    
    '''
    lockStatus = {}
    animLayers = cmds.ls( type = 'animLayer' )
    for layer in animLayers:
        # s = cmds.animLayer( layer, q = True, lock = True )
        lockStatus[layer] = cmds.animLayer( layer, q = True, lock = True )
    print( lockStatus )
    return lockStatus


def animLayersUnlock():
    '''
    
    '''
    animLayers = cmds.ls( type = 'animLayer' )
    for layer in animLayers:
        cmds.animLayer( layer, edit = True, lock = False )


def animLayersRestoreLock( lockStatus = {} ):
    '''
    
    '''
    for key in lockStatus:
        cmds.animLayer( key, edit = True, lock = lockStatus[key] )


def getTimeWarpAnimLayers():
    '''
    get warped layers
    '''
    return


def getKeyedFrames( obj ):
    '''
    
    '''
    # print( 'getframes' )
    # animCurves = cmds.findKeyframe( obj, c = True )  # may have to use getAnimCurves(), this command seems tonly get active animlayer curves
    # print(len(animCurves), animCurves)
    # animCurves = getAnimCurves( object = obj, max_recursion = 1 )
    animCurves = getAnimCurves2( object = obj )
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
        message( ' Object given has no keys ' + obj )
        return frames


def getKeyedFrames2( animCurves = [] ):
    '''
    
    '''
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
        message( 'No anim curves provided' )
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


def getBakeRange( animCurves = [], keyRange = True ):
    '''
    keyRange = expand bake range if keys are outside playbackOptions
    '''
    #
    start = cmds.playbackOptions( q = True, minTime = True )
    end = cmds.playbackOptions( q = True, maxTime = True )
    #
    if keyRange:
        # frames = getKeyedFramesList()
        frames = getKeyedFrames2( animCurves )
        if frames:
            if frames[0] < start:
                start = frames[0]
            if frames[-1] > end:
                start = frames[-1]

    return [start, end]


def getUniqueName( name = '' ):
    # print( name )
    if '|' in name:
        name = name.split( '|' )[-1]
    if not cmds.objExists( name ):
        return name
    else:
        i = 1
        while cmds.objExists( name + str( i ) + '___' ):
            i = i + 1
        return name + str( i ) + '___'


def getActiveLayer():
    '''
    return current active anim layer
    '''
    layerNames = cmds.ls( type = 'animLayer' )
    # rootLayer = cmds.animLayer( q = True, root = True )
    for layer in layerNames:
        if cmds.animLayer( layer, q = True, selected = True ):
            return layer
    return None


def getDeadCurves( timeWarp = '' ):
    '''
    
    '''
    #
    blah = 'MayaNodeEditorSavedTabsInfo'
    animCurves = []
    deadCurves = []
    sets = [setCurveName( timeWarp ), setLayerCurveName( timeWarp )]
    # print( sets )
    #
    animCurveMembers = getAnimCurveMembers( timeWarp, select = False )
    for curve in animCurveMembers:
        animCurves.append( curve )
    layerCurveMembers = getLayerCurveMembers( timeWarp, select = False )
    for curve in layerCurveMembers:
        animCurves.append( curve )
    #
    for curve in animCurves:
        # print( curve )
        con = cmds.listConnections( curve , s = 0, d = 1 )
        if blah in con:
            con.remove( blah )
        if len( con ) == 1:
            if con[0] in sets:
                deadCurves.append( curve )
            else:
                # print( 'not in sets' )
                pass
        else:
            # print( 'more than one', con )
            pass
    if deadCurves:
        print( '-- AnimCurves with no outputs : --' )
        print( deadCurves )
        message( 'Found (' + str( len( deadCurves ) ) + ') dead animCurves. Listed above.', warning = True )
    #
    return deadCurves


if __name__ == '__main__':
    print( 'run only in maya' )
else:
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    main_window.show()
    app.exec_()
