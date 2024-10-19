# run to list unknown plugins
from shutil import copyfile
import imp
import json
import os
import random
import subprocess
import time

from PySide2 import QtCore, QtGui, QtWidgets
import cache_abc_sil as cas
import maya
import maya.cmds as cmds
import maya.mel as mel

imp.reload( cas )

global cache_window

# cache_window = None
'''
if cache_window:
    if not cache_window.main_window.isHidden():
        cache_window.store_session()
        cache_window.main_window.close()
    else:
        # print( 'none' )
        cache_window = None
'''
try:
    #
    if cache_window:
        if not cache_window.main_window.isHidden():
            cache_window.store_session()
            cache_window.main_window.close()
        else:
            # print( 'none' )
            cache_window = None
except:
    # print( 'no variable' )
    pass
# print os.environ


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


def UI____():
    pass


class CustomQDialog( QtWidgets.QDialog ):
    '''
    
    '''

    def __init__( self ):
        super().__init__()

    def closeEvent( self, event ):
        '''
        
        '''
        #
        cache_window.store_session()
        '''
        p_d = Prefs_dynamic()
        p_d.prefs[p_d.session_window_pos_x] = self.frameGeometry().x()
        p_d.prefs[p_d.session_window_pos_y] = self.frameGeometry().y()
        p_d.prefs[p_d.session_window_width] = self.geometry().width()
        p_d.prefs[p_d.session_window_height] = self.geometry().height()
        # setProject_window = None
        p_d.prefSave()
        '''
        #
        event.accept()
        # print( 'Window closed' )


class SessionElements():

    def __init__( self, main_window = None, on_top = None, frame_pad = None, frame_step = None ):
        '''
        
        '''

        self.main_window = main_window
        self.on_top = on_top
        self.frame_pad = frame_pad
        self.frame_step = frame_step
        self.color = None

    def store_session( self ):
        '''
        
        '''
        #
        p_d = Prefs_dynamic()
        #
        p_d.prefs[p_d.session_window_pos_x] = self.main_window.frameGeometry().x()
        p_d.prefs[p_d.session_window_pos_y] = self.main_window.frameGeometry().y()
        p_d.prefs[p_d.session_window_width] = self.main_window.geometry().width()
        p_d.prefs[p_d.session_window_height] = self.main_window.geometry().height()
        p_d.prefs[p_d.frame_pad] = self.frame_pad.text()
        p_d.prefs[p_d.frame_step] = self.frame_step.text()
        #
        p_d.prefSave()


def init_ui():
    '''
    
    '''
    win = SessionElements()
    # main
    win.main_window = CustomQDialog()
    win.main_window.setWindowTitle( 'Cache ABC' )
    main_layout = QtWidgets.QVBoxLayout()
    win.main_window.setLayout( main_layout )
    # size
    w = 320
    h = 200
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.session_window_width]:
        w = int( p_d.prefs[p_d.session_window_width] )
        h = int( p_d.prefs[p_d.session_window_height] )
        win.main_window.resize( w, h )
    else:
        win.main_window.resize( w, h )
    # color tag
    row1_layout = QtWidgets.QHBoxLayout()
    s = 25
    tag_button = QtWidgets.QPushButton( '' )
    tag_button.setMaximumWidth( s )
    tag_button.setMinimumWidth( s )
    tag_button.setToolTip( "Maya session" )
    color = get_tag_color()
    tag_button.setStyleSheet( "background-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");" )  # QtGui.QColor( 1, 0.219, 0.058 )

    # always on top
    alwaysOnTop_layout = QtWidgets.QHBoxLayout()
    alwaysOnTop_label = QtWidgets.QLabel( 'Always On Top:  ' )
    alwaysOnTop_check = QtWidgets.QCheckBox()
    if p_d.prefs[p_d.on_top]:
        alwaysOnTop_check.setChecked( True )
    else:
        alwaysOnTop_check.setChecked( False )
    win.on_top = alwaysOnTop_check
    alwaysOnTop_check.clicked.connect( lambda:onTopToggle( win.main_window, alwaysOnTop_check ) )
    #
    alwaysOnTop_layout.addWidget( alwaysOnTop_label, 0 )
    alwaysOnTop_layout.addWidget( alwaysOnTop_check, 0 )
    alwaysOnTop_layout.setAlignment( QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter )
    #
    row1_layout.addWidget( tag_button, alignment = QtCore.Qt.AlignLeft )
    row1_layout.addLayout( alwaysOnTop_layout )
    main_layout.addLayout( row1_layout )

    # tggl button
    tggl_layout = QtWidgets.QHBoxLayout()
    tggl_button = QtWidgets.QPushButton( 'TOGGLE VIEWPORTS' )
    tggl_button.clicked.connect( lambda:cas.uiEnable() )
    tggl_layout.addWidget( tggl_button, 0 )
    main_layout.addLayout( tggl_layout )

    # frame pad
    framePad_layout = QtWidgets.QHBoxLayout()
    framePad_label = QtWidgets.QLabel( 'Frame Range Pad:' )
    f_pad = '5'
    if p_d.prefs[p_d.frame_pad]:
        f_pad = p_d.prefs[p_d.frame_pad]
    framePad_line_edit = QtWidgets.QLineEdit( str( f_pad ) )
    win.frame_pad = framePad_line_edit
    #
    framePad_layout.addWidget( framePad_label, 0 )
    framePad_layout.addWidget( framePad_line_edit, 0 )
    main_layout.addLayout( framePad_layout )

    # frame step
    frameStep_layout = QtWidgets.QHBoxLayout()
    frameStep_label = QtWidgets.QLabel( 'Frame Step:' )
    f_step = '1.0'
    if p_d.prefs[p_d.frame_step]:
        f_step = p_d.prefs[p_d.frame_step]
    frameStep_line_edit = QtWidgets.QLineEdit( str( f_step ) )
    win.frame_step = frameStep_line_edit
    #
    frameStep_layout.addWidget( frameStep_label, 0 )
    frameStep_layout.addWidget( frameStep_line_edit, 0 )
    main_layout.addLayout( frameStep_layout )

    # use file name
    useFileName_layout = QtWidgets.QHBoxLayout()
    useFileName_label = QtWidgets.QLabel( 'Use File Name:  ' )
    useFileName_label.setToolTip( "Dont rebuild the export name from the file path" )
    useFileName_check = QtWidgets.QCheckBox()
    useFileName_check.setChecked( True )
    #
    useFileName_layout.addWidget( useFileName_label, 0 )
    useFileName_layout.addWidget( useFileName_check, 0 )
    useFileName_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( useFileName_layout )

    # euler filter
    eulerFilter_layout = QtWidgets.QHBoxLayout()
    eulerFilter_label = QtWidgets.QLabel( 'Euler Filter:  ' )
    eulerFilter_check = QtWidgets.QCheckBox()
    eulerFilter_check.setChecked( True )
    #
    eulerFilter_layout.addWidget( eulerFilter_label, 0 )
    eulerFilter_layout.addWidget( eulerFilter_check, 0 )
    eulerFilter_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( eulerFilter_layout )

    # force overwrite
    forceOverwrite_layout = QtWidgets.QHBoxLayout()
    forceOverwrite_label = QtWidgets.QLabel( 'Force Overwrite:  ' )
    forceOverwrite_check = QtWidgets.QCheckBox()
    forceOverwrite_check.setChecked( True )
    #
    forceOverwrite_layout.addWidget( forceOverwrite_label, 0 )
    forceOverwrite_layout.addWidget( forceOverwrite_check, 0 )
    forceOverwrite_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( forceOverwrite_layout )

    # force type
    forceType_layout = QtWidgets.QHBoxLayout()
    forceType_label = QtWidgets.QLabel( 'Force Asset Type:' )
    forceType_check = QtWidgets.QCheckBox()
    #
    forceType_layout.addWidget( forceType_label, 0 )
    forceType_layout.addWidget( forceType_check, 0 )
    forceType_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( forceType_layout )

    # force type radio
    forceRadio_layout = QtWidgets.QHBoxLayout()
    forceRadio_cam = QtWidgets.QRadioButton( "cam" )
    forceRadio_cam.setChecked( True )
    forceRadio_cam.toggled.connect( lambda:radio_state( forceRadio_cam ) )
    forceRadio_geo = QtWidgets.QRadioButton( "geo" )
    forceRadio_geo.toggled.connect( lambda:radio_state( forceRadio_geo ) )
    #
    forceType_check.clicked.connect( lambda:radio_toggle( r = [forceRadio_cam, forceRadio_geo] ) )
    #
    forceRadio_layout.addWidget( forceRadio_cam, 0 )
    forceRadio_layout.addWidget( forceRadio_geo, 0 )
    forceRadio_cam.setDisabled( True )
    forceRadio_geo.setDisabled( True )
    forceRadio_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( forceRadio_layout )

    # cache button
    cache_layout = QtWidgets.QHBoxLayout()
    cache_button = QtWidgets.QPushButton( 'CREATE ALEMBIC' )
    cache_button.clicked.connect( lambda:create_alembic( pad = framePad_line_edit, step = frameStep_line_edit, overwrite = forceOverwrite_check, forceTyp = forceType_check, cam = forceRadio_cam, eulerFltr = eulerFilter_check, useFl = useFileName_check ) )
    #
    cache_layout.addWidget( cache_button, 0 )
    #
    main_layout.addLayout( cache_layout )

    return win


def onTopToggle( w, check_box ):
    '''
    window always on top toggle
    '''
    w.setWindowFlags( w.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint )
    p = Prefs_dynamic()
    p.prefs[p.on_top] = check_box.isChecked()
    p.prefSave()
    #
    w.show()
    pass


def radio_state( b ):
    '''
    currently pointless
    '''
    if b.text() == "cam":
        if b.isChecked() == True:
            print( b.text() + " is selected" )
        else:
            print( b.text() + " is deselected" )

    if b.text() == "geo":
        if b.isChecked() == True:
            print( b.text() + " is selected" )
        else:
            print( b.text() + " is deselected" )


def radio_toggle( r = [] ):
    '''
    toggle force asset type radios
    '''
    if r[0].isEnabled():
        for radio in r:
            radio.setDisabled( True )
    else:
        for radio in r:
            radio.setEnabled( True )


def warning( objects = [] ):
    '''
    caches not created
    '''
    mes = ''
    # build message
    for o in objects:
        mes = mes + o + '\n'
    # open
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText( 'Objects with existing versions not CACHED: ' + '\n\n' + mes )
    print( 'here' )
    msgBox.exec_()


def show_window():
    '''
    
    '''
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    #
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    main_window.move( centerPoint - main_window.frameGeometry().center() * 3 )
    #
    main_window.show()
    app.exec_()


def ____CACHE():
    pass


def create_alembic( pad, step, overwrite, forceTyp, cam, eulerFltr, useFl ):
    '''
    vars are ui elements
    '''
    # objects not cached
    result = []
    #
    project = cmds.workspace( rd = True, q = True )
    parts = project.split( '/' )
    shot = parts[-4]  # isolate shot name
    print( shot )

    # pad amount
    framePad = int( pad.text() )

    # step every nth frame
    frameSample = float( step.text() )

    # eulerFltr state
    eulerFilter = eulerFltr.isChecked()

    # useFile state
    useFile = useFl.isChecked()
    # overwrite state
    forceOverwrite = overwrite.isChecked()

    # force type state
    forceType = forceTyp.isChecked()

    # camera type state
    camera = cam.isChecked()

    # start timer
    start = time.time()

    # CACHE
    sel = cmds.ls( sl = 1 )
    if sel:
        for i in sel:
            cmds.select( i )
            not_cached = cas.cache_abc( framePad = framePad, frameSample = frameSample, forceType = forceType, camera = camera, forceOverwrite = forceOverwrite, eulerFilter = eulerFilter, useFile = useFile )
            if not_cached:
                # print( 'not' )
                result.append( not_cached )

        # reselect objects
        cmds.select( sel )

        # end timer
        end = time.time()
        elapsed = end - start
        print( 'All Alembics - Elapsed time: ' + str( elapsed ) )
        if result:
            # print( 'Version exists, objects not cached: ', result )
            warning( result )
    else:
        message( 'Select an object', warning = True )


def ____TAGS():
    pass


def tag_name():
    return 'SIL'


def tag_ui_parent():
    return 'ToolBox|MainToolboxLayout|frameLayout5|flowLayout2'


def toggle_maya_ui_tag():
    '''
    add color button to ui so tools can color code with same color
    for use in multi maya session use cases
    '''
    ui = tag_ui_parent()
    name = tag_name()
    color = get_color()
    #
    if cmds.control( ui, ex = True ):
        cmds.setParent( ui )
        if cmds.control( name, ex = True ):
            cmds.deleteUI( name )
        else:
            cmds.button( name, bgc = color, label = '', h = 32, w = 32 )
            # cmds.flowLayout( ui, edit = True, bgc = color )
    else:
        message( 'Maya Color Tag Failed --- Hard coded maya UI element doesnt exist: ' + ui, warning = True )


def get_tag_color():
    '''
    
    '''
    color = None
    if cmds.control( tag_name(), ex = True ):
        color = cmds.button( tag_name(), q = True, bgc = True )
    else:
        toggle_maya_ui_tag()
        color = cmds.button( tag_name(), q = True, bgc = True )
    # print( color )
    return color


def get_color():
    '''
    red = QtGui.QColor( 1, 0.219, 0.058 )
    '''
    red = [1, 0.219, 0.058 ]
    green = [ 0.152, 0.627, 0.188 ]
    blue = [ 0.152, 0.403, 0.627 ]
    orange = [ 0.850, 0.474, 0.090 ]
    l_grey = [ 0.701, 0.690, 0.678 ]
    grey = [ 0.701, 0.690, 0.678 ]
    purple = [ 0.564, 0.121, 0.717 ]
    yellow = [ 0.870, 0.811, 0.090 ]
    brown = [ 0.552, 0.403, 0.164 ]
    aqua = [ 0.192, 0.647, 0.549 ]
    white = [ 1.0, 1.0, 1.0 ]
    black = [ 0.0, 0.0, 0.0 ]
    #
    c = [red, green, blue, orange, l_grey, grey, purple, yellow, brown, aqua, white, black]

    color = random.randint( 0, len( c ) - 1 )
    # print( c[color] )
    return c[color]


def ____PREFS():
    pass


class Prefs_dynamic():
    '''
    
    '''

    def __init__( self, *args ):
        '''
        prefs that are persistent next time ui starts.
        '''
        self.on_top = 'on_top'
        self.frame_pad = 'frame_pad'
        self.frame_step = 'frame_step'
        #
        self.session_window_pos_x = 'session_window_pos_x'
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_width = 'session_window_width'
        self.session_window_height = 'session_window_height'
        #
        self.prefs = {
            self.on_top: False,
            self.frame_pad: 5,
            self.frame_step: 1,
            self.session_window_pos_x: None,
            self.session_window_pos_y: None,
            self.session_window_width: None,
            self.session_window_height: None
        }
        #
        self.prefLoad()

    def prefFileName( self ):
        return 'CacheDynamicPrefs.json'

    def prefPath( self, *args ):
        varPath = cmds.internalVar( userAppDir = True )
        path = os.path.join( varPath, 'scripts' )
        path = os.path.join( path, self.prefFileName() )
        return path

    def prefSave( self, *args ):
        # save
        fileObjectJSON = open( self.prefPath(), 'w' )
        json.dump( self.prefs, fileObjectJSON, indent = 4 )
        fileObjectJSON.close()

    def prefLoad( self, *args ):
        # load
        prefs_temp = {}
        if os.path.isfile( self.prefPath() ):
            try:
                fileObjectJSON = open( self.prefPath(), 'r' )
                prefs_temp = json.load( fileObjectJSON )
                fileObjectJSON.close()
            except:
                message( 'Pref file not compatible. Using defaults.', warning = 1 )
            # load state
            if prefs_temp:
                if self.on_top in prefs_temp:
                    for key in self.prefs:
                        if key in prefs_temp:
                            self.prefs[key] = prefs_temp[key]
                        else:
                            pass
                            # message( 'Missing attribute in file. Skipping: ' + key, warning = 1 )
        else:
            self.prefSave()


if __name__ == '__main__':
    pass
    '''
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    #
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    main_window.move( centerPoint - main_window.frameGeometry().center() * 3 )
    #
    main_window.show()
    app.exec_()'''
else:
    # print( 'nah' )
    app = QtWidgets.QApplication.instance()
    cache_window = init_ui()  # returns class
    # prefs
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.on_top]:
        cache_window.main_window.setWindowFlags( cache_window.main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    #
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    _offset = [0, 0]  # [1, 31]  # framed window has border, position query is not accounting for the border
    if p_d.prefs[p_d.session_window_pos_x]:
        cache_window.main_window.move( p_d.prefs[p_d.session_window_pos_x] - _offset[0], p_d.prefs[p_d.session_window_pos_y] - _offset[1] )
    else:
        cache_window.main_window.move( centerPoint.x() * 0.5, centerPoint.y() * 0.25 )
    #
    cache_window.main_window.show()
    app.exec_()

'''
# launch code in maya
import imp
import cache_abc_ui_sil as cau
imp.reload(cau)
'''
