# run to list unknown plugins
from shutil import copyfile
import imp
import json
import os
import subprocess
import time

from PySide2 import QtCore, QtGui, QtWidgets
import maya

import cache_abc_sil as cas
import maya.cmds as cmds
import maya.mel as mel

imp.reload( cas )

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


def init_ui():
    # main
    main_window = QtWidgets.QDialog()
    main_window.setWindowTitle( 'Cache ABC' )
    main_layout = QtWidgets.QVBoxLayout()
    main_window.setLayout( main_layout )
    # width, height
    # main_window.setFixedSize( 250, 200 )
    main_window.resize( 320, 200 )
    # main_window.setMaximumHeight( 150 )
    # main_window.setMaximumWidth( 200 )

    # always on top
    alwaysOnTop_layout = QtWidgets.QHBoxLayout()
    alwaysOnTop_label = QtWidgets.QLabel( 'Always On Top:  ' )
    alwaysOnTop_check = QtWidgets.QCheckBox()
    alwaysOnTop_check.setChecked( False )
    alwaysOnTop_check.clicked.connect( lambda:onTopToggle( main_window ) )
    #
    alwaysOnTop_layout.addWidget( alwaysOnTop_label, 0 )
    alwaysOnTop_layout.addWidget( alwaysOnTop_check, 0 )
    alwaysOnTop_layout.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter )
    main_layout.addLayout( alwaysOnTop_layout )

    # tggl button
    tggl_layout = QtWidgets.QHBoxLayout()
    tggl_button = QtWidgets.QPushButton( 'TOGGLE VIEWPORTS' )
    tggl_button.clicked.connect( lambda:cas.uiEnable() )
    #
    tggl_layout.addWidget( tggl_button, 0 )
    #
    main_layout.addLayout( tggl_layout )

    # frame pad
    framePad_layout = QtWidgets.QHBoxLayout()
    framePad_label = QtWidgets.QLabel( 'Frame Range Pad:' )
    framePad_line_edit = QtWidgets.QLineEdit( '5' )
    #
    framePad_layout.addWidget( framePad_label, 0 )
    framePad_layout.addWidget( framePad_line_edit, 0 )
    main_layout.addLayout( framePad_layout )

    # frame step
    frameStep_layout = QtWidgets.QHBoxLayout()
    frameStep_label = QtWidgets.QLabel( 'Frame Step:' )
    frameStep_line_edit = QtWidgets.QLineEdit( '1.0' )
    #
    frameStep_layout.addWidget( frameStep_label, 0 )
    frameStep_layout.addWidget( frameStep_line_edit, 0 )
    main_layout.addLayout( frameStep_layout )

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
    cache_button.clicked.connect( lambda:create_alembic( pad = framePad_line_edit, step = frameStep_line_edit, overwrite = forceOverwrite_check, forceTyp = forceType_check, cam = forceRadio_cam ) )
    #
    cache_layout.addWidget( cache_button, 0 )
    #
    main_layout.addLayout( cache_layout )

    return main_window


def onTopToggle( w ):
    '''
    window always on top toggle
    '''
    w.setWindowFlags( w.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint )
    # w.setWindowFlags( w.windowFlags() | QtCore.Qt.WindowStaysOnTopHint ) # enable
    # window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint) # disable
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


def create_alembic( pad, step, overwrite, forceTyp, cam ):
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
            not_cached = cas.cache_abc( framePad = framePad, frameSample = frameSample, forceType = forceType, camera = camera, forceOverwrite = forceOverwrite )
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


if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    #
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    main_window.move( centerPoint - main_window.frameGeometry().center() * 3 )
    #
    main_window.show()
    app.exec_()
else:
    print( 'nah' )
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    #
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    main_window.move( centerPoint - main_window.frameGeometry().center() * 3 )
    #
    main_window.show()
    app.exec_()
