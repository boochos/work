import datetime
import json
import os
import random
import shutil
import subprocess
import sys
import time

from PySide2 import QtCore, QtGui, QtWidgets


def ____UI():
    pass


class UI():

    def __init__( self ):
        '''
        
        '''

        self.p = Prefs()
        self.p_d = Prefs_dynamic()
        self.final_directory = todays_directory_name()
        self.sources_ui_list = []
        # main
        self.main_window = QtWidgets.QDialog()
        self.main_window.setWindowTitle( 'Copy Sources Tool' )
        # main_window = CustomQDialog()  # close event altered
        w = 600
        h = 100
        if self.p_d.prefs[self.p_d.session_window_width]:
            w = int( self.p_d.prefs[self.p_d.session_window_width] )
            h = int( self.p_d.prefs[self.p_d.session_window_height] )
            self.main_window.resize( w, h )
        else:
            self.main_window.resize( w, h )
        #
        # win.main_window = main_window  # ADD TO CLASS
        # print( main_window )
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_window.setLayout( self.main_layout )
        #
        self.add_sources_layout = QtWidgets.QVBoxLayout()
        # rows
        self.on_top_row()
        self.destination_row()
        self.add_source_row()
        self.main_layout.addLayout( self.add_sources_layout )
        self.source_row()
        self.copy_row()

        #
        self.main_window.show()

    def add_source_row( self ):
        '''
        
        '''
        #
        self.add_source_layout = QtWidgets.QHBoxLayout()
        self.add_source_button = QtWidgets.QPushButton( "Add Source" )
        self.add_source_button.clicked.connect( lambda:self.source_row() )
        #
        self.add_source_layout = QtWidgets.QHBoxLayout()
        self.add_source_layout.addWidget( self.add_source_button )
        #
        self.main_layout.addLayout( self.add_source_layout )

    def destination_row( self ):
        '''
        
        '''
        #
        self.destination_label = QtWidgets.QLabel( 'Destination Path:  ' )
        self.destination_edit = QtWidgets.QLineEdit()
        #
        self.destination_layout = QtWidgets.QHBoxLayout()
        self.destination_layout.addWidget( self.destination_label )
        self.destination_layout.addWidget( self.destination_edit )
        #
        self.main_layout.addLayout( self.destination_layout )

    def source_row( self ):
        '''
        
        '''
        #
        self.source_label = QtWidgets.QLabel( 'Source Path:  ' )
        self.source_edit = QtWidgets.QLineEdit()
        self.sources_ui_list.append( self.source_edit )
        #
        self.source_layout = QtWidgets.QHBoxLayout()
        self.source_layout.addWidget( self.source_label )
        self.source_layout.addWidget( self.source_edit )
        #
        self.add_sources_layout.addLayout( self.source_layout )

    def on_top_row( self ):
        '''
        
        '''
        # on top
        self.alwaysOnTop_label = QtWidgets.QLabel( 'Always On Top:  ' )
        self.alwaysOnTop_check = QtWidgets.QCheckBox()
        if self.p_d.prefs[self.p_d.on_top]:
            self.alwaysOnTop_check.setChecked( True )
        else:
            self.alwaysOnTop_check.setChecked( False )
        self.alwaysOnTop_check.clicked.connect( lambda:self.onTopToggle_ui() )
        #
        self.ontop_layout = QtWidgets.QHBoxLayout()
        self.ontop_layout.addWidget( self.alwaysOnTop_label )
        self.ontop_layout.addWidget( self.alwaysOnTop_check )
        self.ontop_layout.setAlignment( QtCore.Qt.AlignRight )
        #
        self.main_layout.addLayout( self.ontop_layout )

    def copy_row( self ):
        '''
        
        '''
        #
        self.copy_layout = QtWidgets.QHBoxLayout()
        self.copy_button = QtWidgets.QPushButton( "Copy" )
        self.copy_button.clicked.connect( lambda:self.copy_sources() )
        #
        self.copy_layout = QtWidgets.QHBoxLayout()
        self.copy_layout.addWidget( self.copy_button )
        #
        self.main_layout.addLayout( self.copy_layout )

    def message( self, what = '', warning = False ):
        '''
        add message to UI
        '''
        pass
        '''
        what = '-- ' + what + ' --'
        if '\\' in what:
            what = what.replace( '\\', '/' )
        if warning:
            nuke.warning( what )
        else:
            nuke.warning( what )'''

    def onTopToggle_ui( self ):
        '''
        window always on top toggle
        '''
        self.main_window.setWindowFlags( self.main_window.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint )
        p = Prefs_dynamic()
        p.prefs[p.on_top] = self.alwaysOnTop_check.isChecked()
        p.prefSave()
        #
        self.main_window.show()
        pass

    def copy_sources( self ):
        '''
        
        '''
        destination_path = self.destination_edit.text()
        print( destination_path )
        #
        if os.path.isdir( destination_path ):
            if self.final_directory not in destination_path:
                destination_path = os.path.join( destination_path, self.final_directory )
            self.make_final_directory( destination_path )
            #
            for source in self.sources_ui_list:
                #
                source_path = source.text()
                print( source_path )
                go = False
                if os.path.isdir( source_path ):
                    go = True
                elif os.path.isfile( source_path ):
                    go = True
                if go:
                    name = ''
                    if '\\' in source_path:
                        name = source_path.split( '\\' )[-1]
                    elif '/' in source_path:
                        name = source_path.split( '/' )[-1]
                    shutil.copytree( source_path, os.path.join( destination_path, name ), symlinks = True, ignore = None )
                else:
                    print( 'source is not a path' )
        else:
            print( 'destination is not a path' )

    def make_final_directory( self, destination_path = '' ):
        '''
        
        '''
        if not os.path.isdir( destination_path ):
            os.mkdir( destination_path )


def todays_directory_name():
    '''
    
    '''

    e = datetime.datetime.now()
    name = e.strftime( "%Y_%m_%d" )
    print ( name )
    return name


def ____PREFS():
    pass


def pref_window( win ):
    '''
    prefs settings window
    '''
    #
    p = Prefs()
    p_str = p.list_to_string( p.prefs[p.project_blacklist] )
    e_str = p.list_to_string( p.prefs[p.shot_blacklist] )
    a_str = p.list_to_string( p.prefs[p.asset_blacklist] )
    at_str = p.list_to_string( p.prefs[p.asset_type_blacklist] )
    t_str = p.list_to_string( p.prefs[p.task_whitelist] )
    ''''
    w_str = str( p.prefs[p.window_width] )
    h_str = str( p.prefs[p.window_height] )'''
    #
    w = 150
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # tip
    tip = 'Separate NAMES via comma.'
    tip_label = QtWidgets.QLabel( tip )
    tip_label.setAlignment( QtCore.Qt.AlignCenter )
    qframe1 = QtWidgets.QFrame()
    main_layout.addWidget( tip_label )
    main_layout.addWidget( qframe1 )
    # project
    prj_line_layout = QtWidgets.QHBoxLayout()
    prj_label = QtWidgets.QLabel( 'Project blacklist:' )
    prj_edit = QtWidgets.QLineEdit( p_str )
    prj_label.setMinimumWidth( w )
    #
    prj_line_layout.addWidget( prj_label )
    prj_line_layout.addWidget( prj_edit )
    main_layout.addLayout( prj_line_layout )

    # entity
    entity_line_layout = QtWidgets.QHBoxLayout()
    entity_label = QtWidgets.QLabel( 'Entity blacklist:' )
    entity_edit = QtWidgets.QLineEdit( e_str )
    entity_label.setMinimumWidth( w )
    #
    entity_line_layout.addWidget( entity_label )
    entity_line_layout.addWidget( entity_edit )
    main_layout.addLayout( entity_line_layout )

    # assets
    assets_line_layout = QtWidgets.QHBoxLayout()
    assets_label = QtWidgets.QLabel( 'Asset blacklist:' )
    assets_edit = QtWidgets.QLineEdit( a_str )
    assets_label.setMinimumWidth( w )
    #
    assets_line_layout.addWidget( assets_label )
    assets_line_layout.addWidget( assets_edit )
    main_layout.addLayout( assets_line_layout )

    # asset type
    assettype_line_layout = QtWidgets.QHBoxLayout()
    assettype_label = QtWidgets.QLabel( 'Asset Type blacklist:' )
    assettype_edit = QtWidgets.QLineEdit( at_str )
    assettype_label.setMinimumWidth( w )
    #
    assettype_line_layout.addWidget( assettype_label )
    assettype_line_layout.addWidget( assettype_edit )
    main_layout.addLayout( assettype_line_layout )

    # task
    task_line_layout = QtWidgets.QHBoxLayout()
    task_label = QtWidgets.QLabel( 'Task whitelist:' )
    task_edit = QtWidgets.QLineEdit( t_str )
    task_label.setMinimumWidth( w )
    #
    task_line_layout.addWidget( task_label )
    task_line_layout.addWidget( task_edit )
    main_layout.addLayout( task_line_layout )

    # restore navigation
    radio_layout = QtWidgets.QHBoxLayout()
    radio_label = QtWidgets.QLabel( 'At Launch Navigate to:' )
    radio_label.setMinimumWidth( w )
    sel_radio = QtWidgets.QRadioButton( 'Previous Selection' )
    # sel_radio.setChecked( True )
    sel_radio.toggled.connect( lambda: store_navigation_type( sel_radio, project_radio, scene_radio ) )
    project_radio = QtWidgets.QRadioButton( 'Previous Project' )
    project_radio.toggled.connect( lambda: store_navigation_type( sel_radio, project_radio, scene_radio ) )
    scene_radio = QtWidgets.QRadioButton( 'Current Scene' )
    scene_radio.toggled.connect( lambda: store_navigation_type( sel_radio, project_radio, scene_radio ) )
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.navigate_to_last_selection]:
        sel_radio.setChecked( True )
    if p_d.prefs[p_d.navigate_to_last_project]:
        project_radio.setChecked( True )
    if p_d.prefs[p_d.navigate_to_current_scene]:
        scene_radio.setChecked( True )

    #
    radio_layout.addWidget( radio_label )
    radio_layout.addWidget( sel_radio )
    radio_layout.addWidget( project_radio )
    radio_layout.addWidget( scene_radio )
    main_layout.addLayout( radio_layout )

    # window size
    '''
    widnow_size_layout = QtWidgets.QHBoxLayout()
    window_size_label = QtWidgets.QLabel( 'WILL BE REMOVED - Window Size w/h :' )
    window_size_x_edit = QtWidgets.QLineEdit( w_str )
    window_size_y_edit = QtWidgets.QLineEdit( h_str )
    current_size_button = QtWidgets.QPushButton( "Get Current Size" )
    current_size_button.clicked.connect( lambda: input_window_size( win, window_size_x_edit, window_size_y_edit ) )
    window_size_label.setMinimumWidth( w )
    #
    widnow_size_layout.addWidget( window_size_label )
    widnow_size_layout.addWidget( window_size_x_edit )
    widnow_size_layout.addWidget( window_size_y_edit )
    widnow_size_layout.addWidget( current_size_button )
    main_layout.addLayout( widnow_size_layout )'''

    # save and close
    buttons_layout = QtWidgets.QHBoxLayout()
    save_button = QtWidgets.QPushButton( "Save" )
    save_button.clicked.connect( lambda: Prefs( main_window, prj_edit, entity_edit, assets_edit, assettype_edit, task_edit ) )
    close_button = QtWidgets.QPushButton( "Close" )
    close_button.clicked.connect( lambda: main_window.close() )

    buttons_layout.addWidget( save_button )
    buttons_layout.addWidget( close_button )
    main_layout.addLayout( buttons_layout )

    # draw window
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( "Preferences" )
    main_window.setMinimumWidth( 1000 )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.exec_()


def input_window_size( win = None, ui_x = None, ui_y = None ):
    '''
    
    '''
    ui_x.setText( str( win.width() ) )
    ui_y.setText( str( win.height() ) )


def store_navigation_type( sel_radio, project_radio, scene_radio ):
    '''
    
    '''
    p = Prefs_dynamic()
    p.prefs[p.navigate_to_last_selection] = sel_radio.isChecked()
    p.prefs[p.navigate_to_last_project] = project_radio.isChecked()
    p.prefs[p.navigate_to_current_scene] = scene_radio.isChecked()
    p.prefSave()


class Prefs():

    def __init__( self, main_window = None, projects = None, entities = None, assets = None, assettypes = None, tasks = None ):
        '''
        '''
        self.main_window = main_window
        self.global_prefs_path = ''
        self.local_prefs_path = ''
        self.ui_string = ''
        # keys for dict
        self.project_blacklist = 'project_blacklist'
        self.shot_blacklist = 'shot_blacklist'
        self.asset_blacklist = 'asset_blacklist'
        self.asset_type_blacklist = 'asset_type_blacklist'
        self.task_whitelist = 'task_whitelist'
        self.remote_pref_path = 'remote_pref_path'
        #
        self.prefs = {
            self.project_blacklist:[],
            self.shot_blacklist:[],
            self.asset_blacklist:[],
            self.asset_type_blacklist:[],
            self.task_whitelist:[],
            self.remote_pref_path: ''
            }
        #
        if projects:
            # string to list, needs to execute as part of instantiation so ui can load prefs
            self.string_to_list( projects, self.project_blacklist )
            self.string_to_list( entities, self.shot_blacklist )
            self.string_to_list( assets, self.asset_blacklist )
            self.string_to_list( assettypes, self.asset_type_blacklist )
            self.string_to_list( tasks, self.task_whitelist )
            # print( self.prefs[self.window_width], self.prefs[self.window_height] )
            # save
            self.prefSave()
        else:
            self.prefLoad()

    def list_to_string( self, pref_list = [] ):
        '''
        list to string
        '''
        # print( pref_list )
        _str = ""
        for i in range( len( pref_list ) ):
            if i > 0:
                _str = _str + ',' + pref_list[i]
            else:
                _str = _str + '' + pref_list[i]
        self.ui_string = _str
        return _str

    def string_to_list( self, ui_field = None, pref_list = [] ):
        '''
        string to list
        '''
        _str = ui_field.text()
        _list = _str.split( ',' )
        for i in _list:
            self.prefs[pref_list].append( i )

    def prefPath( self, *args ):
        '''
        not sure what happens with OS other than windows
        '''
        varPath = os.path.expanduser( "~" )
        # path = os.path.join( varPath, '.nuke' )
        path = varPath
        path = os.path.join( path, 'siCopySourcesToolPrefs.json' )
        return path

    def prefPathRemote( self ):
        '''
        not sure what happens with OS other than windows
        '''
        varPath = os.path.expanduser( "~" )
        # path = os.path.join( varPath, '.nuke' )
        path = varPath
        path = os.path.join( path, 'siCopySourcesToolPrefs.json' )
        return path

    def prefSave( self, *args ):
        # save
        fileObjectJSON = open( self.prefPath(), 'w' )
        json.dump( self.prefs, fileObjectJSON, indent = 4 )
        fileObjectJSON.close()
        if self.main_window:
            self.main_window.close()

    def prefLoad( self, *args ):
        # load
        prefs_temp = {}
        if os.path.isfile( self.prefPath() ):
            try:
                fileObjectJSON = open( self.prefPath(), 'r' )
                prefs_temp = json.load( fileObjectJSON )
                fileObjectJSON.close()
            except:
                pass
                # message( 'Pref file not compatible. Using defaults.', warning = 1 )
            # load state
            if prefs_temp:
                # print( prefs_temp )
                if self.project_blacklist in prefs_temp:
                    for key in self.prefs:
                        if key in prefs_temp:
                            self.prefs[key] = prefs_temp[key]
                        else:
                            pass
                            # message( 'Missing attribute in file. Skipping: ' + key, warning = 1 )
                else:
                    self.prefs = prefs_dict_default()
                    self.prefSave()
        else:
            self.prefs = prefs_dict_default()
            self.prefSave()


def prefs_dict_default():
    '''
    if files dont exist, use this
    '''
    prefs_default = {
     "shot_blacklist": [
      "global",
      "transfer",
      "_transfer",
      "admin",
      "pipe",
      ".DS_Store",
      "Thumbs.db",
      "plates",
      "proxy"
     ],
     "asset_type_blacklist": [
      "asset_old",
      "lightkit",
      "renderpass"
     ],
     "asset_blacklist": [
      "pipeline"
     ],
     "task_whitelist": [
      "anim",
      "model",
      "rig",
      "layout",
      "previs",
      "fx"
     ],
     "project_blacklist": [
      ".DS_Store",
      "cockroach999",
      "Thumbs.db",
      "_library",
      "EDITORIAL",
      "STUDIO",
      "pipeline",
      "$RECYCLE.BIN",
      "VFX_Animation",
      "projects"
     ],
     "remote_pref_path": ""
    }
    return prefs_default


class Prefs_dynamic():
    '''
    
    '''

    def __init__( self, *args ):
        '''
        prefs that are persistent next time ui starts.
        '''
        self.on_top = 'on_top'
        self.last_project = 'last_project'  # last project set before window was closed
        #
        self.last_selected_project = 'last_selected_project'
        self.last_selected_entity = 'last_selected_entity'
        self.last_selected_task = 'last_selected_task'
        self.last_selected_scene = 'last_selected_scene'
        #
        self.entity_search = 'entity_search'
        self.task_search = 'task_search'
        #
        self.navigate_to_current_scene = 'navigate_to_current_scene'  # parse scene name
        self.navigate_to_last_project = 'navigate_to_last_project'  # last project set before window was closed
        self.navigate_to_last_selection = 'navigate_to_last_selection'  # restore exact selection before window was closed
        #
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_pos_x = 'session_window_pos_x'
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_width = 'session_window_width'
        self.session_window_height = 'session_window_height'
        self.session_project = 'session_project'
        self.session_entity = 'session_entity'
        self.session_task = 'session_task'
        self.session_scene = 'session_scene'
        #
        self.prefs = {
            self.on_top: False,
            self.last_project: '',
            self.last_selected_project: '',
            self.last_selected_entity: '',
            self.last_selected_task: '',
            self.last_selected_scene: '',
            self.entity_search: '',
            self.task_search: '',
            self.navigate_to_current_scene:False,
            self.navigate_to_last_project:False,
            self.navigate_to_last_selection:True,
            self.session_window_pos_x: None,
            self.session_window_pos_y: None,
            self.session_window_width: None,
            self.session_window_height: None,
            self.session_project: None,
            self.session_entity: None,
            self.session_task: None,
            self.session_scene: None
        }
        #
        self.prefLoad()

    def prefFileName( self ):
        return 'siCopySourcesToolDynamicPrefs.json'

    def prefPath( self, *args ):
        '''
        not sure what happens with OS other than windows
        '''
        varPath = os.path.expanduser( "~" )
        # path = os.path.join( varPath, '.nuke' )
        path = varPath
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
                pass
                # message( 'Pref file not compatible. Using defaults.', warning = 1 )
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


# n = UI()
if __name__ == '__main__':
    # n = UI()
    # n.main_window.show()

    app = QtWidgets.QApplication( sys.argv )
    '''
    file = QtCore.QFile( ":/dark.qss" )
    file.open( QtCore.QFile.ReadOnly | QtCore.QFile.Text )
    stream = QtCore.QTextStream( file )
    app.setStyleSheet( stream.readAll() )
    '''
    ex = UI()
    sys.exit( app.exec_() )
else:
    pass
