# run to list unknown plugins
from distutils.command.check import check
from shutil import copyfile
import json
import os
import random
import subprocess
import time

from PySide2 import QtCore, QtGui, QtWidgets
import maya
import maya.cmds as cmds

# from PyQt4 import QtCore, QtGui, QtWidgets
a = cmds.unknownPlugin( q = True, l = True )
if a:
    for i in a:
        print( i )
    # run to remove unknown plugins
    for i in a:
        try:
            cmds.unknownPlugin( i, r = True )
        except:
            print( 'cant remove plugin ', i )

# import sys
if 'PROJ_ROOT' not in os.environ:
    os.environ['PROJ_ROOT'] = 'P:\\'

global setProject_window

#
try:
    #
    if setProject_window:
        if not setProject_window.main_window.isHidden():
            setProject_window.store_session()
            setProject_window.main_window.close()
        else:
            setProject_window = None
except:
    # print( 'failed' )
    pass

# timers
save_start = None
fps_start = None
range_start = None
open_start = None
ref_start = None
pub_start = None

# print os.environ


def message( what = '', warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        maya.mel.eval( 'print \"' + what + '\";' )


def ____UI():
    pass


class CustomQDialog( QtWidgets.QDialog ):
    '''
    
    '''

    def __init__( self ):
        super().__init__()

    def closeEvent( self, event ):
        '''
        
        '''
        # do stuff, figure out how to get session info and save it
        #
        p_d = Prefs_dynamic()
        p_d.prefs[p_d.session_window_pos_x] = self.frameGeometry().x()
        p_d.prefs[p_d.session_window_pos_y] = self.frameGeometry().y()
        p_d.prefs[p_d.session_window_width] = self.geometry().width()
        p_d.prefs[p_d.session_window_height] = self.geometry().height()
        # setProject_window = None
        p_d.prefSave()
        #
        event.accept()
        # print( 'Window closed' )


class CustomListView( QtWidgets.QListWidget ):
    '''
    
    '''

    def __init__( self ):
        super().__init__()
        #
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.root = os.environ["PROJ_ROOT"]
        self._file = False
        self.path = ''
        self._p = ''
        self._e = ''
        self._t = ''
        self._s = ''
        self._selected = ''
        #

    def contextMenuEvent( self, e ):
        '''
        
        '''
        #
        item = self.itemAt( e.pos() )
        if item:
            self.if_file( e )
            #
            context = QtWidgets.QMenu( self )
            action_copy = context.addAction( "Copy" )
            #
            if self._file:
                action_copy_file_path = context.addAction( "Copy File Path" )
            else:
                action_copy_file_path = 'Wrong column, do nothing'
            #
            action_copy_path = context.addAction( "Copy Path" )
            action_browse = context.addAction( "Browse" )
            #
            action = context.exec_( e.globalPos() )
            #
            if action == action_copy:
                self.clipboard_item( e )
            elif action == action_copy_file_path:
                self.clipboard_path( e )
            elif action == action_copy_path:
                self.clipboard_path( e, directory_only = True )
            elif action == action_browse:
                self.browse( e )
            else:
                pass
        else:
            # print( 'nothing under mouse' )
            pass

    def if_file( self, e ):
        '''
        
        '''
        #
        item = self.itemAt( e.pos() )
        if item:
            _selected = item.text()
            _s = ''
            if setProject_window.scenes.selectedItems():
                _s = setProject_window.scenes.selectedItems()[0].text()
            #
            if _selected == _s:
                self._file = True
        else:
            # print( 'nothing selected, if file' )
            pass

    def _pets( self, e, directory_only = False ):
        '''
        
        '''
        #
        item = self.itemAt( e.pos() )
        if item:
            self._selected = item.text()

            # get strings in lists
            if setProject_window.projects.selectedItems():
                self._p = setProject_window.projects.selectedItems()[0].text()
            if setProject_window.entities.selectedItems():
                self._e = setProject_window.entities.selectedItems()[0].text()
            if setProject_window.tasks.selectedItems():
                self._t = setProject_window.tasks.selectedItems()[0].text()
            if setProject_window.scenes.selectedItems():
                self._s = setProject_window.scenes.selectedItems()[0].text()
            #
            self._path( directory_only )
        else:
            pass

    def _path( self, directory_only = False ):
        # project

        if self._selected == self._p:
            self.path = os.path.join( self.root, self._p )
        elif self._selected == self._e:
            self.path = os.path.join( self.root, self._p, self._e )
        elif self._selected == self._t:
            self.path = os.path.join( self.root, self._p, self._e, self._t )
        elif self._selected == self._s:
            if 'asset' in self._e:
                # self.path = os.path.join( self.root, self._p, self._e, self._t )
                if directory_only:
                    self.path = os.path.join( self.root, self._p, self._e, self._t, 'maya', 'scenes' )
                else:
                    self.path = os.path.join( self.root, self._p, self._e, self._t, 'maya', 'scenes', self._s )
            else:
                if directory_only:
                    self.path = os.path.join( self.root, self._p, self._e, self._t, 'maya', 'scenes' )
                else:
                    self.path = os.path.join( self.root, self._p, self._e, self._t, 'maya', 'scenes', self._s )

    def clipboard_item( self, e ):
        # only selection text
        item = self.itemAt( e.pos() )
        if item:
            print( item.text() )
            self.clipboard.setText( item.text() )
        else:
            # print( 'nothing selected, item' )
            pass

    def clipboard_path( self, e, directory_only = False ):
        # path
        self._pets( e, directory_only )
        print( self.path )
        self.clipboard.setText( self.path )

    def browse( self, e ):
        #
        self._pets( e, directory_only = True )
        # open file browser
        if os.path.isdir( self.path ):
            subprocess.Popen( r'explorer /open, ' + self.path )


class SessionElements():

    def __init__( self, main_window = None, projects = None, entities = None, tasks = None, scenes = None ):
        '''
        
        '''

        self.main_window = main_window
        self.projects = projects
        self.entities = entities
        self.tasks = tasks
        self.scenes = scenes
        self.color = None

    def store_session( self ):
        '''
        
        '''
        #
        p_d = Prefs_dynamic()
        #
        if self.projects.selectedItems():
            p_d.prefs[p_d.last_selected_project] = self.projects.selectedItems()[0].text()
        else:
            p_d.prefs[p_d.last_selected_project] = ''
        if self.entities.selectedItems():
            p_d.prefs[p_d.last_selected_entity] = self.entities.selectedItems()[0].text()
        else:
            p_d.prefs[p_d.last_selected_entity] = ''
        if self.tasks.selectedItems():
            p_d.prefs[p_d.last_selected_task] = self.tasks.selectedItems()[0].text()
        else:
            p_d.prefs[p_d.last_selected_task] = ''
        if self.scenes.selectedItems():
            p_d.prefs[p_d.last_selected_scene] = self.scenes.selectedItems()[0].text()
        else:
            p_d.prefs[p_d.last_selected_scene] = ''
        #
        p_d.prefs[p_d.session_window_pos_x] = self.main_window.frameGeometry().x()
        p_d.prefs[p_d.session_window_pos_y] = self.main_window.frameGeometry().y()
        p_d.prefs[p_d.session_window_width] = self.main_window.geometry().width()
        p_d.prefs[p_d.session_window_height] = self.main_window.geometry().height()
        p_d.prefSave()

    def sample_code_iterate_widgets( self ):
        '''
        for unknown ui hierarchy look for whatever, do whatever once found
        '''
        for i in range( self.main_window.count() ):
            item = self.main_window.itemAt( i ).widget()
            if isinstance( item, QtWidgets.QLineEdit ):
                print( item.text() )


def init_ui():
    '''
    build UI
    '''

    # orange = QtGui.QColor( 0.850, 0.474, 0.090 )
    # orn = orange.spec()
    # print( orn )
    # print( orange )
    #
    win = SessionElements()
    p = Prefs()
    p_d = Prefs_dynamic()
    #
    min_width = 150
    # main
    # main_window = QtWidgets.QDialog()
    main_window = CustomQDialog()  # close event altered
    #
    win.main_window = main_window  # ADD TO CLASS
    # print( main_window )
    main_layout = QtWidgets.QVBoxLayout()
    # color tag
    s = 25
    tag_button = QtWidgets.QPushButton( '' )
    tag_button.setMaximumWidth( s )
    tag_button.setMinimumWidth( s )
    tag_button.setToolTip( "Maya session" )
    color = get_tag_color()
    tag_button.setStyleSheet( "background-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");" )  # QtGui.QColor( 1, 0.219, 0.058 )
    # always on top
    ontop_layout = QtWidgets.QHBoxLayout()
    alwaysOnTop_label = QtWidgets.QLabel( 'Always On Top:  ' )
    alwaysOnTop_check = QtWidgets.QCheckBox()
    if p_d.prefs[p_d.on_top]:
        alwaysOnTop_check.setChecked( True )
    else:
        alwaysOnTop_check.setChecked( False )
    alwaysOnTop_check.clicked.connect( lambda:onTopToggle_ui( main_window, alwaysOnTop_check ) )
    #
    ontop_layout.addWidget( alwaysOnTop_label )
    ontop_layout.addWidget( alwaysOnTop_check )
    ontop_layout.setAlignment( QtCore.Qt.AlignRight )
    # prefs
    prefs_button = QtWidgets.QPushButton( "Preferences" )
    prefs_button.clicked.connect( lambda: pref_window( main_window ) )
    prefs_button.setMaximumWidth( min_width )
    prefs_button.setStyleSheet( "background-color: grey" )
    # print( prefs_button.toolTip() )
    #
    top_layout = QtWidgets.QHBoxLayout()
    top_layout.addWidget( tag_button, alignment = QtCore.Qt.AlignLeft )
    top_layout.addLayout( ontop_layout )
    main_layout.addLayout( top_layout )
    # directories
    directory_layout = QtWidgets.QHBoxLayout()
    # column 1 - projects
    col1_layout = QtWidgets.QVBoxLayout()
    project_list_widget = CustomListView()  # QtWidgets.QListWidget()
    project_list_widget.setMaximumWidth( min_width )
    project_list_widget.setMinimumWidth( min_width )
    #
    win.projects = project_list_widget  # ADD TO CLASS
    #
    col1_layout.addWidget( prefs_button )
    col1_layout.addWidget( project_list_widget )
    # column 2 - assets, shots
    col2_layout = QtWidgets.QVBoxLayout()
    new_scene_button = QtWidgets.QPushButton( "New Scene" )
    new_scene_button.clicked.connect( lambda:new_scene_detect() )
    new_scene_button.setMaximumWidth( min_width * 2 )
    shots_and_assets_list_widget = CustomListView()  # QtWidgets.QListWidget()
    shots_and_assets_list_widget.setMaximumWidth( min_width * 2 )
    shots_and_assets_list_widget.setMinimumWidth( min_width )
    search_edit = QtWidgets.QLineEdit( p_d.prefs[p_d.entity_search] )
    search_edit.textChanged.connect( lambda: get_shots_assets( shots_and_assets_list_widget, project_list_widget, tasks_list_widget, search_edit, scene_list_widget ) )
    search_edit.setMaximumWidth( min_width * 2 )
    #
    win.entities = shots_and_assets_list_widget  # ADD TO CLASS
    #
    col2_layout.addWidget( new_scene_button )
    col2_layout.addWidget( search_edit )
    col2_layout.addWidget( shots_and_assets_list_widget )
    # column 3 - departments
    col3_layout = QtWidgets.QVBoxLayout()
    tasks_list_widget = CustomListView()  # QtWidgets.QListWidget()
    # tasks_list_widget.setMaximumWidth( min_width * 2 )
    tasks_list_widget.setMinimumWidth( min_width )
    set_project_button = QtWidgets.QPushButton( "Set Project" )
    set_project_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    # set_project_button.setMaximumWidth( min_width * 2 )
    search_task_edit = QtWidgets.QLineEdit( p_d.prefs[p_d.task_search] )
    search_task_edit.textChanged.connect( lambda: get_tasks( tasks_list_widget, project_list_widget, shots_and_assets_list_widget, scene_list_widget, search_task_edit ) )
    # search_task_edit.setMaximumWidth( min_width * 2 )
    #
    win.tasks = tasks_list_widget  # ADD TO CLASS

    #
    col3_layout.addWidget( set_project_button )
    col3_layout.addWidget( search_task_edit )
    col3_layout.addWidget( tasks_list_widget )
    # column 4 - scenes
    pad = str( 10 )
    col4_layout = QtWidgets.QVBoxLayout()
    scene_list_widget = CustomListView()  # QtWidgets.QListWidget()
    scene_list_widget.setMinimumWidth( min_width * 2 )
    #
    win.scenes = scene_list_widget  # ADD TO CLASS
    #
    suffix_layout_col4 = QtWidgets.QHBoxLayout()
    suffix_label_col4 = QtWidgets.QLabel( 'Add Suffix:  ' )
    suffix_edit = QtWidgets.QLineEdit()
    suffix_layout_col4.addWidget( suffix_label_col4 )
    suffix_layout_col4.addWidget( suffix_edit )
    #
    create_button = QtWidgets.QPushButton( "Save Scene +" )
    create_button.clicked.connect( lambda: save_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene = None, opn = False, create = scene_list_widget, suffix_edit = suffix_edit ) )
    set_open_button = QtWidgets.QPushButton( "Open" )
    set_open_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    set_open_button.clicked.connect( lambda: open_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, True ) )
    ref_button = QtWidgets.QPushButton( "Reference" )
    ref_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    ref_button.clicked.connect( lambda: ref_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    '''
    explore_button = QtWidgets.QPushButton( "File Browser" )
    explore_button.clicked.connect( lambda: explore_path( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    explore_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px; background-color: grey;" )
    '''
    navigate_button = QtWidgets.QPushButton( "Navigate to Scene" )
    navigate_button.clicked.connect( lambda: get_current( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, navigate_to_scene = True ) )
    navigate_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px; background-color: grey;" )

    range_button = QtWidgets.QPushButton( "Import Range" )
    range_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    range_button.clicked.connect( lambda: rangeFromMaFile( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, handles = 0 ) )
    fps_button = QtWidgets.QPushButton( "Import FPS" )
    fps_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    fps_button.clicked.connect( lambda: fpsFromMaFile( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    pub_button = QtWidgets.QPushButton( "Publish" )
    pub_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    pub_button.clicked.connect( lambda: publish_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    # qframe1 = QtWidgets.QFrame()
    #
    col4_layout.addWidget( create_button )
    col4_layout.addLayout( suffix_layout_col4 )
    col4_layout.addWidget( scene_list_widget )
    # col4_layout.addWidget( qframe1 )
    col4_layout.addWidget( fps_button )
    col4_layout.addWidget( range_button )
    col4_layout.addWidget( set_open_button )
    col4_layout.addWidget( ref_button )
    col4_layout.addWidget( pub_button )
    col4_layout.addWidget( navigate_button )
    #
    projects = get_projects()
    for project in projects:
        project_list_widget.addItem( project )
    #
    directory_layout.addLayout( col1_layout )
    directory_layout.addLayout( col2_layout )
    directory_layout.addLayout( col3_layout )
    directory_layout.addLayout( col4_layout )
    main_layout.addLayout( directory_layout )
    # buttons
    # bottom_layout = QtWidgets.QHBoxLayout()
    #
    # main_layout.addLayout( bottom_layout )

    main_window.setLayout( main_layout )

    main_window.setWindowTitle( 'Set Project Tool' )
    project_list_widget.itemSelectionChanged.connect( lambda: get_shots_assets( shots_and_assets_list_widget, project_list_widget, tasks_list_widget, search_edit, scene_list_widget ) )
    project_list_widget.itemDoubleClicked.connect( lambda: explore_path( project_list_widget ) )
    # project_list_widget.itemSelectionChanged.connect( lambda: tasks_list_widget.clear() )
    shots_and_assets_list_widget.itemSelectionChanged.connect( lambda: get_tasks( tasks_list_widget, project_list_widget, shots_and_assets_list_widget, scene_list_widget, search_task_edit ) )
    shots_and_assets_list_widget.itemDoubleClicked.connect( lambda: explore_path( project_list_widget, shots_and_assets_list_widget, ) )
    tasks_list_widget.itemSelectionChanged.connect( lambda: get_scenes( scene_list_widget, project_list_widget, shots_and_assets_list_widget, tasks_list_widget ) )
    tasks_list_widget.itemDoubleClicked.connect( lambda: explore_path( project_list_widget, shots_and_assets_list_widget, tasks_list_widget ) )
    scene_list_widget.itemDoubleClicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, True ) )
    scene_list_widget.itemSelectionChanged.connect( lambda: scenes_click_event( scene_list_widget ) )

    # size
    w = 900
    h = 800
    p = Prefs()
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.session_window_width]:
        w = int( p_d.prefs[p_d.session_window_width] )
        h = int( p_d.prefs[p_d.session_window_height] )
    main_window.resize( w, h )
    # main_window.resize( 900, 800 )

    # parse current scene
    get_current( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget )

    #
    # print( '______', win.tasks )
    return win


def ____GET_CONTENTS():
    pass


def get_projects():
    '''
    Get Projects from Project root.
    '''
    #
    # print( 'get_shots_assets' )
    #
    p = Prefs()
    # print( p.prefs )
    skips = p.prefs[p.project_blacklist]
    # print skips
    raw_projects = os.listdir( os.environ['PROJ_ROOT'] )
    clean = []
    for r in raw_projects:
        if r not in skips and '.' not in r:
            clean.append( r )

    return clean


def get_shots_assets( list_widget, project, tasks, search_edit, scenes = None ):
    '''
    Get both shots and assets for a project.
    '''
    #
    p_d = Prefs_dynamic()
    p_d.prefs[p_d.entity_search] = search_edit.text()
    p_d.prefSave()
    #
    # print( 'get_shots_assets' )
    #
    current_entity = ''
    if list_widget.selectedItems():
        current_entity = list_widget.selectedItems()[0].text()
        # message( current_entity, warning = 1 )
    else:
        # message( 'no current entity', warning = 1 )
        pass
    #
    p_d = Prefs_dynamic()
    if project.selectedItems():
        project = project.selectedItems()[0].text()
        p_d.prefs[p_d.last_selected_project] = project
        p_d.prefSave()
    else:
        # message( 'Select a project' )  # too much feedback
        p_d.prefs[p_d.last_selected_project] = ''
        p_d.prefSave()

    #
    #
    p = Prefs()
    skips = p.prefs[p.shot_blacklist]
    #
    raw_eps = os.listdir( os.path.join( os.environ['PROJ_ROOT'], project ) )
    eps = []
    shots_all = []
    assets_only = []
    for epp in raw_eps:
        if epp not in skips and epp != 'assets':
            eps.append( epp )  # should catch assets
        if epp == 'assets':
            # print( epp )
            assets_only = get_assets( os.path.join( os.environ['PROJ_ROOT'], project, epp ) )

    for ep in eps:
        ep_path = os.path.join( os.environ['PROJ_ROOT'], project, ep )
        if not os.path.isdir( ep_path ):
            continue
        shots = os.listdir( ep_path )
        for sht in shots:
            if '.' not in sht:
                shots_all.append( os.path.join( ep, sht ) )
            else:
                # print( sht )
                pass
    shots_all.sort()
    assets_only.extend( shots_all )
    shots_n_assets = assets_only
    # message( 'clearing entity list', warning = 1 )
    list_widget.clear()
    #
    for item in shots_n_assets:
        if search_edit:
            if search_edit.text() in item:
                list_widget.addItem( item )
        else:
            list_widget.addItem( item )
    list_widget.setVisible( True )
    # reselect task
    if current_entity:
        item = list_widget.findItems( current_entity, QtCore.Qt.MatchExactly )
        if item:
            # print( 'reselect entity' )
            list_widget.setCurrentItem( item[0] )
        else:
            # message( 'didnt reselect: ' + current_entity, warning = 1 )
            if tasks:
                tasks.clear()
                scenes.clear()
                pass
    else:
        # message( 'couldnt reselect current entity: ' + current_entity , warning = 1 )
        pass

    if scenes:
        # scenes.clear()
        pass


def get_assets( ep_path ):
    '''
    Get assets in new structure
    '''
    #
    # print( 'get_assets' )
    #
    p = Prefs()
    typeskips = p.prefs[p.asset_type_blacklist]
    skips = p.prefs[p.asset_blacklist]
    asset_list = []
    asstypes = os.listdir( ep_path )
    for asstype in asstypes:
        if asstype not in typeskips:
            if os.path.isdir( os.path.join( ep_path, asstype ) ):
                assets = os.listdir( os.path.join( ep_path, asstype ) )
                for asset in assets:
                    if asset not in skips and '.' not in asset:
                        asset_list.append( os.path.join( 'assets', asstype, asset ) )
    asset_list.sort()
    return asset_list


def get_tasks( list_widget, project, entity, scenes, search_task_edit ):
    '''
    Get tasks
    '''
    #
    # print( 'get_tasks' )
    #
    p_d = Prefs_dynamic()
    if entity.selectedItems():
        p_d.prefs[p_d.last_selected_entity] = entity.selectedItems()[0].text()
    else:
        p_d.prefs[p_d.last_selected_entity] = ''
    p_d.prefs[p_d.task_search] = search_task_edit.text()
    p_d.prefSave()
    #
    # store current task
    current_task = ''
    if list_widget.selectedItems():
        current_task = list_widget.selectedItems()[0].text()
    # store current scene
    current_scene = ''
    if scenes.selectedItems():
        current_scene = scenes.selectedItems()[0].text()
    #
    if project.selectedItems() and entity.selectedItems():
        project = project.selectedItems()[0].text()
        entity = entity.selectedItems()[0].text()
    else:
        # message( 'Cant list Tasks. Need a Project and Entity selected.', warning = 1 )
        if project.selectedItems():
            project = project.selectedItems()[0].text()
            # print( project )
        if entity.selectedItems():
            entity = entity.selectedItems()[0].text()
            # print( entity )
        # message( 'task exit', warning = 1 )
        return
    #
    scenes.clear()  # only clear now not above, it clears selection
    #
    skips = ['assets']
    #
    p = Prefs()
    default_tasks = p.prefs[p.task_whitelist]
    # build task root path
    raw_tasks_directory = os.path.join( os.environ['PROJ_ROOT'], project, entity )
    # make sure path exists
    if not os.path.isdir( raw_tasks_directory ):
        list_widget.clear()
        return
    # lists task directories
    raw_tasks = os.listdir( raw_tasks_directory )
    tasks = []
    for task in raw_tasks:
        if default_tasks != ['']:
            if task in default_tasks and task not in skips:  # check against white list
                tasks.append( task )
        else:
            if task not in skips:
                tasks.append( task )  # white list is empty, include all
    tasks.sort()
    cam_versions = get_cam_cache_versions( raw_tasks_directory )
    tasks.extend( cam_versions )
    geo_versions = get_geo_cache_versions( raw_tasks_directory )
    tasks.extend( geo_versions )

    # make sure tasks isnt empty
    if not tasks:
        no_path( os.path.join( os.environ['PROJ_ROOT'], project, entity ).replace( '\\', '/' ) )
        list_widget.clear()
        return
    # clear widget and add items
    list_widget.clear()
    for task in tasks:
        if search_task_edit:
            if search_task_edit.text() in task:
                list_widget.addItem( task )
        else:
            list_widget.addItem( task )
    list_widget.setVisible( True )
    # reselect task
    if current_task:
        item = list_widget.findItems( current_task, QtCore.Qt.MatchExactly )
        if item:
            list_widget.setCurrentItem( item[0] )
    # reselect scene
    if current_scene:
        item = scenes.findItems( current_scene, QtCore.Qt.MatchExactly )
        if item:
            scenes.setCurrentItem( item[0] )


def get_geo_cache_versions( tasks_path = '' ):
    '''
    gets published cache directories
    '''
    #
    # print( 'get_geo_cache_versions' )
    #
    # ignore for now
    '''
    typeskips = ['asset_old',
                 'lightkit',
                 'renderpass']
    skips = ['pipeline']
    prefs = Prefs()
    typeskips = prefs.prefs['at_str']
    skips = prefs.prefs['a_str']
    '''
    #
    version_list = []
    asset_type = os.path.join( 'assets', 'geo' )
    asset_path = os.path.join( tasks_path, asset_type )
    #
    if os.path.isdir( asset_path ):
        raw_versions = os.listdir( asset_path )
        for v in raw_versions:
            if os.path.isdir( os.path.join( asset_path, v ) ):
                if '.' not in v:
                    version_list.append( os.path.join( asset_type, v ) )
    version_list.sort()
    return version_list


def get_cam_cache_versions( tasks_path = '' ):
    '''
    gets published cache directories
    '''
    #
    # print( 'get_cam_cache_versions' )
    #
    # ignore for now
    '''
    typeskips = ['asset_old',
                 'lightkit',
                 'renderpass']
    skips = ['pipeline']
    prefs = Prefs()
    typeskips = prefs.prefs['at_str']
    skips = prefs.prefs['a_str']
    '''
    #
    version_list = []
    asset_type = os.path.join( 'assets', 'cameras' )
    asset_path = os.path.join( tasks_path, asset_type )
    #
    if os.path.isdir( asset_path ):
        raw_versions = os.listdir( asset_path )
        for v in raw_versions:
            if os.path.isdir( os.path.join( asset_path, v ) ):
                if '.' not in v:
                    version_list.append( os.path.join( asset_type, v ) )
    version_list.sort()
    return version_list


def get_scenes( list_widget = None, project = None, entity = None, task = None ):
    '''
    Get scenes
    list_widget = widget
    project = text
    entity = text
    task = widget, then text
    '''
    #
    # print( 'get_scenes' )
    #
    p_d = Prefs_dynamic()
    if task.selectedItems():
        p_d.prefs[p_d.last_selected_task] = task.selectedItems()[0].text()
    else:
        p_d.prefs[p_d.last_selected_task] = ''
    p_d.prefSave()
    # qualify
    if project.selectedItems() and entity.selectedItems():
        project = project.selectedItems()[0].text()
        entity = entity.selectedItems()[0].text()
    else:
        # message( 'Cant list Scenes. Need a Project and Entity selected.', warning = 1 )
        if project.selectedItems():
            project = project.selectedItems()[0].text()
            # print( project )
        if entity.selectedItems():
            entity = entity.selectedItems()[0].text()
            # print( entity )
        return
    #
    current_scene = ''
    if list_widget.selectedItems():
        current_scene = list_widget.selectedItems()[0].text()
        # message( 'stored current scene', warning = 1 )
    #
    scenes = []
    # qualify task is selected
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        list_widget.clear()
        # message( 'Task not selected', warning = 1 )
        return
    # carry-on
    if task[:6] == 'assets':  # alembics
        scenes = get_caches( project, entity, task )
    else:  # maya scenes
        raw_scene_directory = os.path.join( os.environ['PROJ_ROOT'], project, entity, task, 'maya', 'scenes' )
        # qualify
        if not os.path.isdir( raw_scene_directory ):
            list_widget.clear()
            return
        # carry-on
        raw_scene = os.listdir( raw_scene_directory )
        scenes = []
        for scene in raw_scene:
            if scene[-3:] == '.ma'  or scene[-3:] == '.mb':
                scenes.append( scene )
        scenes.sort()
    if not scenes:
        no_path( os.path.join( os.environ['PROJ_ROOT'], project, entity, task ).replace( '\\', '/' ) )
        list_widget.clear()
        return
    list_widget.clear()
    for scene in scenes:
        list_widget.addItem( scene )
    list_widget.setVisible( True )
    # reselect scene
    if current_scene:
        item = list_widget.findItems( current_scene, QtCore.Qt.MatchExactly )
        if item:
            list_widget.setCurrentItem( item[0] )
            # message( 'reselect scene', warning = 1 )
        else:
            # print( 'no__', item )
            pass


def get_caches( project = '', entity = '', task = '' ):
    '''
    
    '''
    #
    # print( 'get_caches' )
    #
    scenes = []
    raw_scene_directory = os.path.join( os.environ['PROJ_ROOT'], project, entity, task )
    # qualify
    if not os.path.isdir( raw_scene_directory ):
        return
    # carry-on
    raw_alembics = os.listdir( raw_scene_directory )
    for alembic in raw_alembics:
        if alembic[-4:] == '.abc':
            scenes.append( alembic )
    scenes.sort()
    return scenes


def get_current( projects = None, entities = None, tasks = None, scenes = None, navigate_to_scene = False ):
    '''
    only good for last project and current scene, 
    maya spits back forward slash paths and back slashs stored in prefs are not compatible
    path.split() breaks with prefs paths
    inputs are QListWidget objects
    parse current scene path, load and set project

    '''
    p_d = Prefs_dynamic()
    path = ''
    scene_path = ''
    try:
        '''
        s_path = cmds.file( query = True, exn = True )
        if s_path:
            if s_path[-8:] != 'untitled':
                scene_path = s_path
            else:
                scene_path = p_d.prefs[p_d.last_project]
                '''
        s_path = cmds.file( query = True, sn = True )
        if s_path:
            scene_path = s_path
        else:
            scene_path = p_d.prefs[p_d.last_project]

    except:
        print( 'fail' )
        pass
    #
    if navigate_to_scene:
        path = scene_path
    else:
        if p_d.prefs[p_d.navigate_to_current_scene]:
            path = scene_path  # scene path
        elif p_d.prefs[p_d.navigate_to_last_project]:
            path = p_d.prefs[p_d.last_project]
        else:
            get_last_selected( projects , entities, tasks , scenes )
            return

    #
    if path:
        # print( path )
        parts = path.split( '/' )
        if parts:
            # print( parts )
            # project
            item = projects.findItems( parts[1], QtCore.Qt.MatchExactly )
            if item:
                projects.setCurrentItem( item[0] )
            # entity
            if 'assets' in path:
                if len( parts ) > 3:
                    item = entities.findItems( os.path.join( parts[2], parts[3], parts[4] ), QtCore.Qt.MatchExactly )
                    # print item
                    if item:
                        entities.setCurrentItem( item[0] )
                # task
                if len( parts ) > 4:
                    item = tasks.findItems( parts[5], QtCore.Qt.MatchExactly )
                    if item:
                        tasks.setCurrentItem( item[0] )
                # scene
                if len( parts ) > 7:
                    item = scenes.findItems( parts[8], QtCore.Qt.MatchExactly )
                    if item:
                        scenes.setCurrentItem( item[0] )
            else:
                if len( parts ) > 2:
                    item = entities.findItems( os.path.join( parts[2], parts[3] ), QtCore.Qt.MatchExactly )
                # print item
                if item:
                    entities.setCurrentItem( item[0] )
                # task
                if len( parts ) > 3:
                    item = tasks.findItems( parts[4], QtCore.Qt.MatchExactly )
                    if item:
                        tasks.setCurrentItem( item[0] )
                # scene
                if len( parts ) > 6:
                    item = scenes.findItems( parts[7], QtCore.Qt.MatchExactly )
                    if item:
                        scenes.setCurrentItem( item[0] )
    else:
        print( 'path : ', path )


def get_last_selected( projects = None, entities = None, tasks = None, scenes = None ):
    '''
    
    '''
    p_d = Prefs_dynamic()
    path = ''
    root = get_root()
    '''
    project = p_d.prefs[p_d.session_project]
    entity = p_d.prefs[p_d.session_entity]
    task = p_d.prefs[p_d.session_task]
    scene = p_d.prefs[p_d.session_scene]
    '''
    _p = p_d.prefs[p_d.last_selected_project]
    _e = p_d.prefs[p_d.last_selected_entity]
    _t = p_d.prefs[p_d.last_selected_task]
    _s = p_d.prefs[p_d.last_selected_scene]
    # project
    item = projects.findItems( _p, QtCore.Qt.MatchExactly )
    if item:
        projects.setCurrentItem( item[0] )
    item = entities.findItems( _e, QtCore.Qt.MatchExactly )
    if item:
        entities.setCurrentItem( item[0] )
    item = tasks.findItems( _t, QtCore.Qt.MatchExactly )
    if item:
        tasks.setCurrentItem( item[0] )
    item = scenes.findItems( _s, QtCore.Qt.MatchExactly )
    if item:
        scenes.setCurrentItem( item[0] )


def get_root():
    return os.environ["PROJ_ROOT"]


def ____MISC():
    pass


def scenes_click_event( scenes = None ):
    '''
    
    '''
    p_d = Prefs_dynamic()
    if scenes.selectedItems():
        p_d.prefs[p_d.last_selected_scene] = scenes.selectedItems()[0].text()
    else:
        p_d.prefs[p_d.last_selected_scene] = ''
    p_d.prefSave()


def select_item_in_list( txt = '', ui_list = None ):
    '''
    txt =  text to match
    ui_list = list widget
    '''
    item = ui_list.findItems( txt, QtCore.Qt.MatchExactly )
    if item:
        ui_list.setCurrentItem( item[0] )


def onTopToggle_ui( w, check_box ):
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


def no_path( path ):
    """Error dialog."""
    pass
    '''
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon( QtWidgets.QMessageBox.Warning )
    msg_box.setText( '{}\n\nThis path does not exist or it is missing all of its key folders.\n\n'.format( path ) )
    msg_box.setWindowTitle( "Missing Path" )
    msg_box.exec_()'''


def set_project( project, entity, task, scene, opn = False, create = None, suffix_edit = None ):
    """
    sets project
    opens scenes
    creates scenes, with/out suffix
    """
    #
    refresh_scenes = [create, project, entity, task]
    go = True
    if project.selectedItems():
        project_txt = project.selectedItems()[0].text()
    else:
        go = False
    if entity.selectedItems():
        entity_txt = entity.selectedItems()[0].text()
    else:
        go = False
    if task.selectedItems():
        task_txt = task.selectedItems()[0].text()
    else:
        go = False
    if scene:
        if scene.selectedItems():
            scene_txt = scene.selectedItems()[0].text()
        else:
            scene_txt = None
    #
    project_path = False
    if go:
        project_dir = os.path.join( os.environ["PROJ_ROOT"], project_txt, entity_txt, task_txt, 'maya' ).replace( '\\', '/' )
        if not os.path.exists( project_dir ):
            message( 'Cant set project in this location: ' + project_dir, warning = 1 )
            no_path( project_dir )
        else:
            project_path = True
            mel_command = ( 'setProject "' + project_dir + '";' )
            maya.mel.eval( mel_command )
            # store in prefs
            p = Prefs_dynamic()
            p.prefs[p.last_project] = project_dir
            p.prefSave()
            #
            message( 'Project set to: ' + project_dir )

        if opn:
            if scene_txt:
                if task_txt[:6] != 'assets':  # alembics:
                    pth = os.path.join( os.environ["PROJ_ROOT"], project_txt, entity_txt, task_txt, 'maya', 'scenes', scene_txt )
                    changes = cmds.file( q = True, modified = True )
                    if changes:
                        open_prompt( path = pth )
                    else:
                        cmds.file( pth, open = True, force = False )
                else:
                    message( 'Alembic cannot be opened. Reference only', warning = 1 )
            else:
                pth = cmds.fileDialog2( fileMode = 1, startingDirectory = os.path.join( os.environ["PROJ_ROOT"], project_txt, entity_txt, task_txt, 'maya', 'scenes' ) )
                if pth:
                    cmds.file( pth, open = True, force = False )
        if create:
            if project_path:
                pth = os.path.join( os.environ["PROJ_ROOT"], project_txt, entity_txt, task_txt, 'maya', 'scenes' )
                result = None
                if suffix_edit.text():
                    sfx = suffix_edit.text()
                    result = filename( pth, entity_txt, task_txt + '_' + sfx )
                else:
                    sfx = filename_getSuffix( pth, entity_txt, task_txt )
                    if sfx:
                        result = filename( pth, entity_txt, task_txt + '_' + sfx )
                    else:
                        result = filename( pth, entity_txt, task_txt )
                if result:
                    # print( project, entity )
                    get_scenes( refresh_scenes[0], project, entity, refresh_scenes[3] )
            else:
                message( 'Project set FAIL -- cant create scene', warning = 1 )
    else:
        message( 'Cant build project path, select more variables', warning = 1 )


def explore_path( project, entity = None, task = None, scene = None ):
    '''
    os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
    '''
    path = None
    # must have
    if project.selectedItems():
        project = project.selectedItems()[0].text()
        path = os.path.join( os.environ["PROJ_ROOT"], project )
    # options
    if entity:
        if entity.selectedItems():
            entity = entity.selectedItems()[0].text()
            path = os.path.join( path, entity )
    if task:
        if task.selectedItems():
            task = task.selectedItems()[0].text()
            path = os.path.join( path, task, 'maya', 'scenes' )
    # open file browser
    if os.path.isdir( path ):
        subprocess.Popen( r'explorer /open, ' + path )


def nmspc( entity = '', task = '' ):
    '''
    iterate namespace string unttil namespace is unused
    for referencing same file multiple times
    '''
    #
    # print( entity )
    ns = ''
    e = entity.split( '\\' )
    if e:
        e = e[-1]
    #
    if 'assets' in entity:
        ns = e[:3]
    else:
        if task[:6] == 'assets':  # alembic
            ns = task.split( '\\' )[1]
            # print( ns )
        else:
            ns = task  # wait for Dmitry to change his mind
    #
    if not cmds.namespace( ex = ns ):
        return ns
    else:
        i = 1
        while cmds.namespace( ex = ns + str( i ) ):
            i = i + 1
        return ns + str( i )


def filename_getSuffix( path = '', entity = '', task = '' ):
    '''
    
    '''
    suffix = ''
    # s_path = cmds.file( query = True, exn = True )
    s_path = cmds.file( query = True, sn = True )
    if s_path:
        if s_path[-8:] != 'untitled':
            if 'v' == s_path[-7]:
                s_path = s_path.split( '/' )[-1]
                sfx = s_path.split( task )[1]
                # print( sfx )
                sfx = sfx[1:-8]  # excludes '_' on either side
                # print( 'sfx__', sfx )
                if sfx:
                    suffix = sfx
    return suffix


def filename( path, entity, task ):
    '''
    
    '''
    e = entity.split( '\\' )
    if e:
        e = e[-1]
    fl = e + '_' + task + '_v001'
    result = incrementalSave( path, fl, 'ma' )
    return result


def incrementalSave( basepath, basename, extension ):
    '''
    return [basepath, basename, extension]
    ['P:\\SANDBOX\\001\\SANDBOX_001_001\\rig\\maya\\scenes', 'SANDBOX_001_001_rig__v001', 'ma']
    '''
    scene_info = [basepath, basename, extension]
    # print( scene_info )
    current_version = basename[-3:]
    # print( current_version )

    # make sure the correct file format is being used
    if scene_info is not False:
        # print( 'inc________' )
        # if no number was found, force it to 0000
        # find the highest version of the current scene name in the folder, then increment the current scene to one more than that then save
        files = os.listdir( scene_info[0] )
        num = int( current_version ) - 1
        string_info = splitEndNumFromString( scene_info[1] )

        for f in files:
            # make sure the current file is not a directory
            if os.path.isfile( os.path.join( scene_info[0], f ) ):
                # remove any file that has a '.' as the first character
                if f[0] != '.':
                    phile = parseSceneFilePath( os.path.join( scene_info[0], f ) )
                    if phile is not False:
                        file_info = splitEndNumFromString( phile[1] )
                        if string_info[0] == file_info[0]:
                            if int( file_info[1] ) > int( num ):
                                num = file_info[1]
        # increment the suffix
        version = '%03d' % ( int( num ) + 1 )
        name = os.path.join( scene_info[0], string_info[0] ) + str( version ) + '.' + scene_info[2]
        name = name.replace( '\\', '/' )
        # get the current file type
        if cmds.file( sn = True , q = True ):
            fileType = cmds.file( query = True, typ = True )
        else:
            fileType = ['mayaAscii']
        # add the file about to be saved to the recent files menu
        maya.mel.eval( 'addRecentFile "' + name + '" ' + fileType[0] + ';' )
        # rename the current file
        message( name )
        cmds.file( name, rn = name )
        # save it
        cmds.file( save = True, typ = fileType[0] )
        return True


def splitEndNumFromString( name ):
    num = ''
    rName = ''
    for i in name:
        try:
            int( i )
            num += i
        except:
            rName += num + i
            num = ''
    if num == '':
        extracted = '%04d' % ( 0000 )
    else:
        extracted = '%04d' % ( int( num ) )

    return rName, extracted


def parseSceneFilePath( path ):
    # return_list = []
    # if path is empty, the scene hasn't not been saved yet
    if not len( path ):
        print( 'Save the scene first using the correct naming convention, name_#### ".ma" or ".mb"' )
        return False
    else:
        # look for the furthest '.' to make sure there is an extension
        if path.rfind( '.' ) > -1:
            # split the scene file name appart
            basename = os.path.basename( path ).split( '.' )[0]
            extension = os.path.basename( path ).split( '.' )[1]
            basepath = os.path.dirname( path )
            return [basepath, basename, extension]
        else:
            print( 'no .' )
            return False


def rangeFromMaFile( project, entity, task, scene, handles = 0 ):
    '''
    
    '''
    go = range_start_timer()
    if not go:
        print( 'range - accidental click' )
        return
    if project.selectedItems():
        project = project.selectedItems()[0].text()
    else:
        go = False
    if entity.selectedItems():
        entity = entity.selectedItems()[0].text()
    else:
        go = False
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        go = False
    if scene.selectedItems():
        scene = scene.selectedItems()[0].text()
    else:
        go = False

    if go:
        path = 'P:/XMAG/075/XMAG_075_035/anim/maya/scenes/XMAG_075_035_anim_v003.ma'
        path = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
        play_start = 0
        play_end = 0
        all_start = 0
        all_end = 0
        # print path
        if os.path.isfile( path ) and '.ma' in path:
            inFile = open( path, 'r' )
            for line in inFile.readlines():
                cvLine = line.strip( '\n' )
                if 'playbackOptions' in line:
                    # print( line )
                    line_parts = line.split( ' ' )
                    i = 0
                    for part in line_parts:
                        if part == '-min':
                            play_start = int( line_parts[i + 1] )
                        if part == '-max':
                            play_end = int( line_parts[i + 1] )
                        if part == '-ast':
                            all_start = int( line_parts[i + 1] )
                        if part == '-aet':
                            all_end = int( line_parts[i + 1] )
                        i = i + 1
                    # print( play_start )
                    # print( play_end )
                    # print( all_start )
                    # print( all_end )
                    cmds.playbackOptions( animationStartTime = all_start )
                    cmds.playbackOptions( animationEndTime = all_end )
                    if handles:
                        cmds.playbackOptions( minTime = play_start + handles )
                        cmds.playbackOptions( maxTime = play_end - handles )
                    else:
                        cmds.playbackOptions( minTime = play_start )
                        cmds.playbackOptions( maxTime = play_end )
                    inFile.close()
                    return None
            inFile.close()
            return None
        else:
            message( 'Select a .ma file', warning = 1 )
            # print 'not a directory'
    else:
        message( 'Select a .ma file', warning = 1 )


def fpsFromMaFile( project, entity, task, scene ):
    '''
    currentUnit -l centimeter -a degree -t film;
    '''
    go = fps_start_timer()
    if not go:
        print( 'fps - accidental click' )
        return
    # print( go )
    all_start = cmds.playbackOptions( animationStartTime = True, q = True )
    all_end = cmds.playbackOptions( animationEndTime = True, q = True )
    play_start = cmds.playbackOptions( minTime = True, q = True )
    play_end = cmds.playbackOptions( maxTime = True, q = True )
    fps = ''
    if project.selectedItems():
        project = project.selectedItems()[0].text()
    else:
        go = False
    if entity.selectedItems():
        entity = entity.selectedItems()[0].text()
    else:
        go = False
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        go = False
    if scene.selectedItems():
        scene = scene.selectedItems()[0].text()
    else:
        go = False

    if go:
        path = 'P:/XMAG/075/XMAG_075_035/anim/maya/scenes/XMAG_075_035_anim_v003.ma'
        path = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )

        # print path
        if os.path.isfile( path ) and '.ma' in path:
            inFile = open( path, 'r' )
            for line in inFile.readlines():
                cvLine = line.strip( '\n' )
                if 'currentUnit' in line:  # currentUnit -l centimeter -a degree -t film;
                    # print( line )
                    fps = line.split( ' ' )[-1]
                    fps = fps.split( ';' )[0]
                    # print( fps )
                    old_fps = cmds.currentUnit( q = 1, time = 1 )
                    cmds.currentUnit( time = fps, updateAnimation = False )
                    # reset range
                    cmds.playbackOptions( animationStartTime = all_start )
                    cmds.playbackOptions( animationEndTime = all_end )
                    cmds.playbackOptions( minTime = play_start )
                    cmds.playbackOptions( maxTime = play_end )
                    # exit
                    inFile.close()
                    message( 'old fps: ' + old_fps + '  ---  new fps: ' + fps )
                    return None
            inFile.close()
            return None
        else:
            message( 'Select a .ma file', warning = 1 )
            # print 'not a directory'
    else:
        message( 'Select a .ma file', warning = 1 )


def setRateRange( project, entity, task, scene, handles ):
    '''
    
    '''
    fpsFromMaFile( project, entity, task, scene )
    rangeFromMaFile( project, entity, task, scene, handles )
    # fpsFromMaFile( project, entity, task, scene )


def sync_file( project, entity, task, scene ):
    '''
    
    '''
    go = True
    if project.selectedItems():
        project = project.selectedItems()[0].text()
    else:
        go = False
    if entity.selectedItems():
        entity = entity.selectedItems()[0].text()
    else:
        go = False
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        go = False
    if scene.selectedItems():
        scene = scene.selectedItems()[0].text()
    else:
        go = False

    if go:
        # sync file
        prefs = Prefs()
        sync_roots = prefs.sync_roots
        for k in sync_roots.keys():
            if k == project:
                project_root = sync_roots[k]
                destination_path = os.path.join( project_root, entity, task, 'maya', 'scenes' )
                if os.path.isdir( destination_path ):
                    working_path = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
                    sync_path = os.path.join( project_root, entity, task, 'maya', 'scenes', scene )
                    copyfile( working_path, sync_path )
                    # subprocess.Popen( r'explorer /open, ' + destination_path )
                    print( sync_path )
                else:
                    print( 'Destination path doesnt exist' )
            else:
                print( 'Project sync path not defined' )
    else:
        maya.mel.eval( 'print \" -- Cant build sync path, select more variables -- \";' )


def delete_renderLayers():
    '''

    '''
    rlayers = cmds.ls( type = 'renderLayer' )

    for l in rlayers:
        if 'defaultRenderLayer' not in l:
            cmds.delete( l )


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
            cmds.button( name, bgc = color, label = '', h = 36, w = 36 )
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


def ____SCENES():
    pass


def save_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene = None, opn = False, create = None, suffix_edit = None ):
    '''
    
    '''
    # qualify
    go = ref_start_timer()
    if not go:
        print( 'save - accidental click' )
        return
    set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene = scene, opn = opn, create = create, suffix_edit = suffix_edit )


def open_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, opn = True ):
    '''
    
    '''
    # qualify
    go = open_start_timer()
    if not go:
        print( 'open - accidental click' )
        return
    set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, opn = opn )


def ref_scene( project, entity, task, scene = None ):
    """
    reference scene
    """
    # qualify
    go = ref_start_timer()
    if not go:
        print( 'ref - accidental click' )
        return
    # go
    project_dir = ''
    #
    if project.selectedItems():
        project = project.selectedItems()[0].text()
    else:
        go = False
    if entity.selectedItems():
        entity = entity.selectedItems()[0].text()
    else:
        go = False
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        go = False
    if scene:
        if scene.selectedItems():
            scene = scene.selectedItems()[0].text()
        else:
            scene = None
    #
    if go:
        if task[:6] == 'assets':  # alembics
            project_dir = os.path.join( os.environ["PROJ_ROOT"], project, entity, task ).replace( '\\', '/' )
        else:  # maya scene
            project_dir = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya' ).replace( '\\', '/' )
        if not os.path.exists( project_dir ):
            no_path( project_dir )
        # ref scene
        ns = nmspc( entity = entity, task = task )
        if scene:
            if task[:6] == 'assets':  # alembics
                pth = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, scene )
            else:
                pth = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
            cmds.file( pth, reference = True, namespace = ns, force = True )
        # open dialog if task
        elif task:
            pth = cmds.fileDialog2( fileMode = 1, startingDirectory = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya' ) )
            if pth:
                cmds.file( pth, reference = True, namespace = ns )
        else:
            message( 'No task or file selected', warning = 1 )
    else:
        message( 'Cant build reference path, select more variables', warning = 1 )
    #
    # end timer
    '''
    end = time.time()
    elapsed = end - start
    print( elapsed )
    if elapsed < 1.0:
        time.sleep( 5 )
    else:
        print( 'longer than 1 sec' )
    # window['-Start-'].update( disabled = False )
    # window.setEnabled( True )'''


def save_open_scene( main_window, path = '' ):
    '''
    save then open
    '''
    cmds.SaveScene()
    cmds.file( path, open = True, force = True )
    main_window.close()


def dont_save_open_scene( main_window, path = '' ):
    '''
    part of save before open, is actually dont save, just open
    '''
    cmds.file( path, open = True, force = True )
    main_window.close()


def new_scene_detect():
    '''
    
    '''
    changes = cmds.file( q = True, modified = True )
    if changes:
        new_prompt()
    else:
        cmds.file( new = True, force = True )


def save_new_scene( main_window ):
    '''
    save then open
    '''
    cmds.SaveScene()
    cmds.file( new = True, force = True )
    main_window.close()


def new_scene( main_window ):
    '''
    
    '''
    cmds.file( new = True, force = True )
    main_window.close()


def save_plus():

    scene = cmds.file( query = True, sn = True )
    scene_info = parseSceneFilePath( scene )
    current_version = scene_info[1][-3:]

    # make sure the correct file format is being used
    if scene_info is not False:
        # if no number was found, force it to 0000
        # find the highest version of the current scene name in the folder, then increment the current scene to one more than that then save
        files = os.listdir( scene_info[0] )
        num = int( current_version ) - 1
        string_info = splitEndNumFromString( scene_info[1] )

        for f in files:
            # make sure the current file is not a directory
            if os.path.isfile( os.path.join( scene_info[0], f ) ):
                # remove any file that has a '.' in the front of it
                if f[0] != '.':
                    phile = parseSceneFilePath( os.path.join( scene_info[0], f ) )
                    if phile is not False:
                        file_info = splitEndNumFromString( phile[1] )
                        if string_info[0] == file_info[0]:
                            if int( file_info[1] ) > int( num ):
                                num = file_info[1]
        # increment the suffix
        version = '%03d' % ( int( num ) + 1 )
        name = os.path.join( scene_info[0], string_info[0] ) + str( version ) + '.' + scene_info[2]
        name = name.replace( '\\', '/' )
        # get the current file type
        fileType = cmds.file( query = True, typ = True )
        # add the file about to be saved to the recent files menu
        maya.mel.eval( 'addRecentFile "' + name + '" ' + fileType[0] + ';' )
        # rename the current file
        cmds.file( name, rn = name )
        # save it
        cmds.file( save = True, typ = fileType[0] )


def overwrite_scene( project = None, entity = None, task = None, scenes = None, scene_info = [], main_window = None ):
    '''
    
    '''
    # print( 'save' )
    #
    fileType = cmds.file( query = True, typ = True )
    path = os.path.join( scene_info[0], scene_info[1] + '.' + scene_info[2] )
    cmds.file( path, rn = path )
    cmds.file( save = True, typ = fileType[0] )
    # refresh
    get_scenes( scenes, project, entity, task )
    # close prompt
    if main_window:
        main_window.close()


def publish_scene( project = None, entity = None, task = None, scenes = None ):
    '''
    input vars are all list widgets, except scenes
    '''
    go = pub_start_timer()
    if not go:
        print( 'pub - accidental click' )
        return
    pub = 'PUB'
    # delete layers
    delete_renderLayers()
    # edit suffix
    scene = cmds.file( query = True, sn = True )
    # print( scene, '_____' )
    if scene:
        scene_info = parseSceneFilePath( scene )  # [basepath, basename, extension]
        if '_' + pub + '_' not in scene_info[1]:
            # insert suffix
            file_name = scene_info[1]
            file_name_parts = file_name.split( '_' )
            file_name_parts.insert( -1, pub )
            # new file name
            new_file_name = file_name_parts[0]
            for part in file_name_parts[1:]:
                    new_file_name = new_file_name + '_' + part
            # create pub scene
            new_scene = scene.replace( scene_info[1], new_file_name )
            new_scene_info = [scene_info[0], new_file_name, scene_info[2]]
            if os.path.isfile( new_scene ):
                # prompt
                overwrite_prompt( project, entity, task, scenes, new_scene_info )
            else:
                # save
                overwrite_scene( project, entity, task, scenes, new_scene_info )
        else:
            message( 'Current scene is already a publish. It contains _PUB_ string in the filename.', warning = True )
    else:
        message( 'Cant parse scene name', warning = 1 )


def ___TIMERS():
    pass


def save_start_timer():
    '''
    
    '''
    # qualify
    global save_start
    go = False
    #
    new_start = time.time()
    if save_start:
        elapsed = new_start - save_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        save_start = new_start
    else:
        save_start = new_start
        go = True
    return go


def fps_start_timer():
    '''
    
    '''
    # qualify
    global fps_start
    # print( 'fps____', fps_start )
    go = False
    #
    new_start = time.time()
    if fps_start:
        elapsed = new_start - fps_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        fps_start = new_start
    else:
        fps_start = new_start
        go = True
    return go


def range_start_timer():
    '''
    
    '''
    # qualify
    global range_start
    go = False
    #
    new_start = time.time()
    if range_start:
        elapsed = new_start - range_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        range_start = new_start
    else:
        range_start = new_start
        go = True
    return go


def open_start_timer():
    '''
    
    '''
    # qualify
    global open_start
    go = False
    #
    new_start = time.time()
    if open_start:
        elapsed = new_start - open_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        open_start = new_start
    else:
        open_start = new_start
        go = True
    return go


def ref_start_timer():
    '''
    
    '''
    # qualify
    global ref_start
    go = False
    #
    new_start = time.time()
    if ref_start:
        elapsed = new_start - ref_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        ref_start = new_start
    else:
        ref_start = new_start
        go = True
    return go


def pub_start_timer():
    '''
    
    '''
    # qualify
    global pub_start
    go = False
    #
    new_start = time.time()
    if pub_start:
        elapsed = new_start - pub_start
        if elapsed > 1.0:
            go = True
        else:
            go = False
        pub_start = new_start
    else:
        pub_start = new_start
        go = True
    return go


def ____DIALOGS():
    pass


def open_prompt( path = '' ):
    '''
    save before opening
    '''
    w = 150
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # project
    changes_label = QtWidgets.QLabel( 'Save changes ?' )
    changes_label.setAlignment( QtCore.Qt.AlignCenter )
    main_layout.addWidget( changes_label )
    #
    button_layout = QtWidgets.QHBoxLayout()
    save_button = QtWidgets.QPushButton( "Save" )
    dont_button = QtWidgets.QPushButton( "Dont Save" )
    cancel_button = QtWidgets.QPushButton( "Cancel" )
    #
    button_layout.addWidget( save_button )
    button_layout.addWidget( dont_button )
    button_layout.addWidget( cancel_button )
    main_layout.addLayout( button_layout )
    #
    save_button.clicked.connect( lambda: save_open_scene( main_window, path ) )
    dont_button.clicked.connect( lambda: dont_save_open_scene( main_window, path ) )
    cancel_button.clicked.connect( lambda: main_window.close() )
    # draw window
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( "Confirm Open Scene" )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.exec_()


def new_prompt():
    '''
    save before new scene
    '''
    w = 150
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # project
    changes_label = QtWidgets.QLabel( 'Save changes ?' )
    changes_label.setAlignment( QtCore.Qt.AlignCenter )
    main_layout.addWidget( changes_label )
    #
    button_layout = QtWidgets.QHBoxLayout()
    save_button = QtWidgets.QPushButton( "Save" )
    dont_button = QtWidgets.QPushButton( "Dont Save" )
    cancel_button = QtWidgets.QPushButton( "Cancel" )
    #
    button_layout.addWidget( save_button )
    button_layout.addWidget( dont_button )
    button_layout.addWidget( cancel_button )
    main_layout.addLayout( button_layout )
    #
    save_button.clicked.connect( lambda: save_new_scene( main_window ) )
    dont_button.clicked.connect( lambda: new_scene( main_window ) )
    cancel_button.clicked.connect( lambda: main_window.close() )
    # draw window
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( "Confirm New Scene" )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.exec_()


def overwrite_prompt( project = None, entity = None, task = None, scenes = None, new_scene = '' ):
    '''
    save before new scene
    '''
    w = 150
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # project
    changes_label = QtWidgets.QLabel( 'Overwrite File ?' )
    changes_label.setAlignment( QtCore.Qt.AlignCenter )
    main_layout.addWidget( changes_label )
    #
    button_layout = QtWidgets.QHBoxLayout()
    save_button = QtWidgets.QPushButton( "Overwrite" )
    # dont_button = QtWidgets.QPushButton( "Dont Save" )
    cancel_button = QtWidgets.QPushButton( "Cancel" )
    #
    button_layout.addWidget( save_button )
    # button_layout.addWidget( dont_button )
    button_layout.addWidget( cancel_button )
    main_layout.addLayout( button_layout )
    #
    save_button.clicked.connect( lambda: overwrite_scene( project, entity, task, scenes, new_scene, main_window ) )
    # dont_button.clicked.connect( lambda: new_scene( main_window ) )
    cancel_button.clicked.connect( lambda: main_window.close() )
    # draw window
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( "Confirm Overwrite Scene" )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.exec_()


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
        varPath = cmds.internalVar( userAppDir = True )
        path = os.path.join( varPath, 'scripts' )
        path = os.path.join( path, 'SetProjectToolPrefs.json' )
        return path

    def prefPathRemote( self ):
        varPath = cmds.internalVar( userAppDir = True )
        path = os.path.join( varPath, 'scripts' )
        path = os.path.join( path, 'SetProjectToolPrefs.json' )
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
                message( 'Pref file not compatible. Using defaults.', warning = 1 )
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
        return 'SetProjectDynamicPrefs.json'

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
else:
    '''
    # setProject_window.main_window.setWindowFlags( setProject_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    # setProject_window.main_window.setWindowFlags( setProject_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    '''
    # ui
    app = QtWidgets.QApplication.instance()
    setProject_window = init_ui()  # returns class
    # prefs
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.on_top]:
        setProject_window.main_window.setWindowFlags( setProject_window.main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    # move
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    _offset = [0, 0]  # [1, 31]
    if p_d.prefs[p_d.session_window_pos_x]:
        setProject_window.main_window.move( p_d.prefs[p_d.session_window_pos_x] - _offset[0], p_d.prefs[p_d.session_window_pos_y] - _offset[1] )
    else:
        setProject_window.main_window.move( centerPoint.x() * 0.5, centerPoint.y() * 0.25 )
    # show
    setProject_window.main_window.show()
    app.exec_()

