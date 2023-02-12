# run to list unknown plugins
from distutils.command.check import check
from shutil import copyfile
import json
import os
import subprocess

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
try:
    setProject_window.close()
except:
    pass

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


def init_ui():
    #
    min_width = 150
    # main
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # always on top
    ontop_layout = QtWidgets.QHBoxLayout()
    alwaysOnTop_label = QtWidgets.QLabel( 'Window On Top:  ' )
    alwaysOnTop_check = QtWidgets.QCheckBox()
    p = Prefs_dynamic()
    if p.prefs[p.on_top]:
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
    prefs_button.clicked.connect( lambda: pref_window( 'path' ) )
    prefs_button.setMaximumWidth( min_width )
    prefs_button.setStyleSheet( "background-color: grey" )
    #
    top_layout = QtWidgets.QHBoxLayout()
    # top_layout.addWidget( prefs_button )
    top_layout.addLayout( ontop_layout )
    main_layout.addLayout( top_layout )
    # directories
    directory_layout = QtWidgets.QHBoxLayout()
    # column 1 - projects
    col1_layout = QtWidgets.QVBoxLayout()
    project_list_widget = QtWidgets.QListWidget()
    project_list_widget.setMaximumWidth( min_width )
    project_list_widget.setMinimumWidth( min_width )
    #
    col1_layout.addWidget( prefs_button )
    col1_layout.addWidget( project_list_widget )
    # column 2 - assets, shots
    col2_layout = QtWidgets.QVBoxLayout()
    new_scene_button = QtWidgets.QPushButton( "New Scene" )
    new_scene_button.clicked.connect( lambda:new_scene_detect() )
    new_scene_button.setMaximumWidth( min_width * 2 )
    shots_and_assets_list_widget = QtWidgets.QListWidget()
    shots_and_assets_list_widget.setMaximumWidth( min_width * 2 )
    shots_and_assets_list_widget.setMinimumWidth( min_width )
    search_edit = QtWidgets.QLineEdit()
    search_edit.textChanged.connect( lambda: get_shots_assets( shots_and_assets_list_widget, project_list_widget, tasks_list_widget, search_edit, scene_list_widget ) )
    search_edit.setMaximumWidth( min_width * 2 )
    #
    col2_layout.addWidget( new_scene_button )
    col2_layout.addWidget( search_edit )
    col2_layout.addWidget( shots_and_assets_list_widget )
    # column 3 - departments
    col3_layout = QtWidgets.QVBoxLayout()
    tasks_list_widget = QtWidgets.QListWidget()
    tasks_list_widget.setMaximumWidth( min_width * 2 )
    tasks_list_widget.setMinimumWidth( min_width )
    set_project_button = QtWidgets.QPushButton( "Set Project" )
    set_project_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    set_project_button.setMaximumWidth( min_width * 2 )
    search_task_edit = QtWidgets.QLineEdit()
    search_task_edit.textChanged.connect( lambda: get_tasks( tasks_list_widget, project_list_widget, shots_and_assets_list_widget, scene_list_widget, search_task_edit ) )
    search_task_edit.setMaximumWidth( min_width * 2 )

    #
    col3_layout.addWidget( set_project_button )
    col3_layout.addWidget( search_task_edit )
    col3_layout.addWidget( tasks_list_widget )
    # column 4 - scenes
    pad = str( 10 )
    col4_layout = QtWidgets.QVBoxLayout()
    scene_list_widget = QtWidgets.QListWidget()
    scene_list_widget.setMinimumWidth( min_width * 2 )
    #
    suffix_layout_col4 = QtWidgets.QHBoxLayout()
    suffix_label_col4 = QtWidgets.QLabel( 'Add Suffix:  ' )
    suffix_edit = QtWidgets.QLineEdit()
    suffix_layout_col4.addWidget( suffix_label_col4 )
    suffix_layout_col4.addWidget( suffix_edit )
    #
    create_button = QtWidgets.QPushButton( "Save Scene +" )
    create_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene = None, opn = False, create = scene_list_widget, suffix_edit = suffix_edit ) )
    set_open_button = QtWidgets.QPushButton( "Open" )
    set_open_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    set_open_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, True ) )
    ref_button = QtWidgets.QPushButton( "Reference" )
    ref_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px;" )
    ref_button.clicked.connect( lambda: ref_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    explore_button = QtWidgets.QPushButton( "File Browser" )
    explore_button.clicked.connect( lambda: explore_path( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    explore_button.setStyleSheet( "padding-top: " + pad + "px; padding-bottom: " + pad + "px; background-color: grey;" )
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
    # qframe2 = QtWidgets.QFrame()
    # qframe3 = QtWidgets.QFrame()
    #
    col4_layout.addWidget( create_button )
    col4_layout.addLayout( suffix_layout_col4 )
    col4_layout.addWidget( scene_list_widget )
    # col4_layout.addWidget( qframe1 )
    col4_layout.addWidget( fps_button )
    col4_layout.addWidget( range_button )
    # col4_layout.addWidget( qframe2 )
    col4_layout.addWidget( set_open_button )
    col4_layout.addWidget( ref_button )
    col4_layout.addWidget( pub_button )
    # col4_layout.addWidget( qframe3 )
    col4_layout.addWidget( explore_button )
    #
    projects = get_projects()
    for project in projects:
        project_list_widget.addItem( project )
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
    main_window.resize( 900, 800 )

    # parse current scene
    get_current( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget )

    return main_window


def ____GET_CONTENTS():
    pass


def get_projects():
    """Get Projects from Project root."""
    skips = ['.DS_Store',
             'cockroach999',
             'Thumbs.db',
             '_library',
             'EDITORIAL',
             'STUDIO',
             'pipeline',
             '$RECYCLE.BIN']
    #
    # print( 'get_shots_assets' )
    #
    prefs = Prefs()
    skips = prefs.prefs['p_str']
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
    if project.selectedItems():
        project = project.selectedItems()[0].text()
    else:
        # message( 'Select a project' )  # too much feedback
        return
    #
    skips = ['global',
             'transfer',
             '_transfer',
             'admin',
             'pipe',
             '.DS_Store',
             'Thumbs.db',
             'plates',
             'proxy']
    prefs = Prefs()
    skips = prefs.prefs['e_str']
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
    typeskips = ['asset_old',
                 'lightkit',
                 'renderpass']
    skips = ['pipeline']
    prefs = Prefs()
    typeskips = prefs.prefs['at_str']
    skips = prefs.prefs['a_str']
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

    skips = ['assets']
    default_tasks = ['anim',
                     'model',
                     'rig',
                     'fx',
                     'layout',
                     'light',
                     'lookdev']
    prefs = Prefs()
    default_tasks = prefs.prefs['t_str']
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
        if default_tasks:
            if task in default_tasks and task not in skips:  # check against white list
                tasks.append( task )
        elif task not in skips:
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


def get_current( projects = None, entities = None, tasks = None, scenes = None ):
    '''
    inputs are QListWidget objects
    parse current scene path, load and set project
    '''
    path = cmds.file( query = True, sn = True )
    if not path:
        p = Prefs_dynamic()
        path = p.prefs[p.last_project]
    if path:
        # print( path )
        parts = path.split( '/' )
        if parts:
            # print parts
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


def ____MISC():
    pass


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
    go = True
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


def ____SCENES():
    pass


def ref_scene( project, entity, task, scene = None ):
    """
    reference scene
    """
    go = True
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


def save_open_scene( main_window, path = '' ):
    '''
    save then open
    '''
    cmds.SaveScene()
    cmds.file( path, open = True, force = True )
    main_window.close()


def open_scene( main_window, path = '' ):
    '''
    
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
    dont_button.clicked.connect( lambda: open_scene( main_window, path ) )
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


def pref_window( path ):
    '''
    prefs settings window
    '''
    # temp strings
    # bkp
    p_str = "'.DS_Store', 'cockroach999', 'Thumbs.db', '_library', 'EDITORIAL', 'STUDIO', 'pipeline', '$RECYCLE.BIN'"
    e_str = "'global','transfer','_transfer','admin','pipe','.DS_Store','Thumbs.db','plates','proxy'"
    a_str = ""
    at_str = "'asset_old','lightkit','renderpass'"
    t_str = "'anim','model','rig','fx','layout','light','lookdev'"
    #
    prefs = Prefs()
    p_str = prefs.p_str
    # print( p_str )
    e_str = prefs.e_str
    a_str = prefs.a_str
    at_str = prefs.at_str
    t_str = prefs.t_str
    prj_sync_str = prefs.prj_sync_str
    #
    w = 150
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
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

    # sync
    sync_line_layout = QtWidgets.QHBoxLayout()
    sync_label = QtWidgets.QLabel( 'Sync roots:' )
    sync_edit = QtWidgets.QLineEdit( prj_sync_str )
    sync_label.setMinimumWidth( w )
    #
    sync_line_layout.addWidget( sync_label )
    sync_line_layout.addWidget( sync_edit )
    main_layout.addLayout( sync_line_layout )

    # prefs manage
    # prefs = Prefs()
    # save and close
    buttons_layout = QtWidgets.QHBoxLayout()
    save_button = QtWidgets.QPushButton( "Save" )
    save_button.clicked.connect( lambda: Prefs( main_window, prj_edit, entity_edit, assets_edit, assettype_edit, task_edit, sync_edit ) )
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

    '''
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon( QtWidgets.QMessageBox.Warning )
    msg_box.setText( '{}\n\nThis path does not exist or it is missing all of its key folders.\n\n'.format( path ) )
    msg_box.setWindowTitle( "Preferences" )
    msg_box.exec_()'''


class Prefs():

    def __init__( self, main_window = None, projects = None, entities = None, assets = None, assettypes = None, tasks = None, sync = None ):
        '''
        '''
        self.main_window = main_window
        self.global_prefs_path = ''
        self.local_prefs_path = ''
        self.default_prefs = ''
        self.prefs = {'p_str':[], 'e_str':[], 'at_str':[], 't_str':[], 'a_str':[], 'prj_sync_str':[]}
        self.sync_roots = {}
        # qt objects
        self.p_str = ''
        self.e_str = ''
        self.a_str = ''
        self.at_str = ''
        self.t_str = ''
        self.prj_sync_str = ''
        # dict value strings
        #
        if projects:
            # parse
            self.p_str = projects.text()
            p_ = self.p_str.split( ',' )
            for i in p_:
                self.prefs['p_str'].append( i )
            #
            self.e_str = entities.text()
            e_ = self.e_str.split( ',' )
            for i in e_:
                self.prefs['e_str'].append( i )
            #
            self.a_str = assets.text()
            a_ = self.a_str.split( ',' )
            for i in a_:
                self.prefs['a_str'].append( i )
            #
            self.at_str = assettypes.text()
            at_ = self.at_str.split( ',' )
            for i in at_:
                self.prefs['at_str'].append( i )
            #
            self.t_str = tasks.text()
            t_ = self.t_str.split( ',' )
            for i in t_:
                self.prefs['t_str'].append( i )
            #
            self.prj_sync_str = sync.text()
            s_ = self.prj_sync_str.split( ',' )
            for i in s_:
                self.prefs['prj_sync_str'].append( i )
            # save
            '''
            for k, v in self.prefs.items():
                print( v )'''
            self.prefSave()
        else:
            self.prefLoad()
            # parse
            c = ''
            #
            self.p_str = ""
            for i in range( len( self.prefs['p_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.p_str = self.p_str + c + self.prefs['p_str'][i]
            #
            self.e_str = ''
            for i in range( len( self.prefs['e_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.e_str = self.e_str + c + self.prefs['e_str'][i]
            #
            self.a_str = ''
            for i in range( len( self.prefs['a_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.a_str = self.a_str + c + self.prefs['a_str'][i]
            #
            self.at_str = ''
            for i in range( len( self.prefs['at_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.at_str = self.at_str + c + self.prefs['at_str'][i]
            #
            self.t_str = ''
            for i in range( len( self.prefs['t_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.t_str = self.t_str + c + self.prefs['t_str'][i]
            #
            self.prj_sync_str = ''
            for i in range( len( self.prefs['prj_sync_str'] ) ):
                if i > 0:
                    c = ','
                else:
                    c = ''
                self.prj_sync_str = self.prj_sync_str + c + self.prefs['prj_sync_str'][i]
                # print( 'parse sync roots' )
                self.prefSync()

    def prefPath( self, *args ):
        varPath = cmds.internalVar( userAppDir = True )
        path = os.path.join( varPath, 'scripts' )
        path = os.path.join( path, 'SetProjectToolPrefs.json' )
        return path

    def prefSave( self, *args ):
        # save
        fileObjectJSON = open( self.prefPath(), 'w' )
        json.dump( self.prefs, fileObjectJSON, indent = 1 )
        fileObjectJSON.close()
        self.main_window.close()

    def prefLoad( self, *args ):
        # load
        if os.path.isfile( self.prefPath() ):
            # fileObjectJSON = open( self.prefPath(), 'r' )
            # self.prefs = json.load( fileObjectJSON )
            try:
                fileObjectJSON = open( self.prefPath(), 'r' )
                self.prefs = json.load( fileObjectJSON )
                # print( 'prefs    ', self.prefs )
                fileObjectJSON.close()
            except:
                # os.remove( self.prefPath() )
                message( 'Pref file not compatible.' )

    def prefSync( self ):
        roots = self.prj_sync_str.split( ',' )
        # print roots
        for root in roots:
            k = root.split( ':' )[0]
            v = root.replace( k + ':', '' )
            # print k
            # print v
            self.sync_roots[k] = v
        # print( self.sync_roots )


class Prefs_dynamic():
    '''
    '''

    def __init__( self, *args ):
        '''
        prefs that are persistent next time ui starts.
        '''
        self.on_top = 'on_top'
        self.last_project = 'last_project'
        #
        self.prefs = {
            self.on_top: False,
            self.last_project: ''
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
                            message( 'Missing attribute in file. Skipping: ' + key, warning = 1 )


def prefs_dict_default():
    '''
    if files dont exist, use this
    '''
    prefs_default = {
     "e_str": [
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
     "prj_sync_str": [
      "SGW:G:\\Shared drives\\SGW"
     ],
     "at_str": [
      "asset_old",
      "lightkit",
      "renderpass"
     ],
     "a_str": [
      "pipeline"
     ],
     "t_str": [
      "anim",
      "model",
      "rig",
      "layout",
      "assets",
      "previs"
     ],
     "p_str": [
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
     ]
    }
    return prefs_default


if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    main_window = init_ui()
    # main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    main_window.setWindowFlags( main_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    main_window.show()
    app.exec_()
else:
    #
    app = QtWidgets.QApplication.instance()
    setProject_window = init_ui()
    p = Prefs_dynamic()
    if p.prefs[p.on_top]:
        setProject_window.setWindowFlags( setProject_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    setProject_window.setWindowFlags( setProject_window.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint )
    setProject_window.setWindowFlags( setProject_window.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint )
    # move
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    setProject_window.move( centerPoint.x() * 0.5, centerPoint.y() * 0.25 )
    # show
    setProject_window.show()
    app.exec_()

'''
{
 "p_str": [
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
 "e_str": [
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
 "at_str": [
  "asset_old",
  "lightkit",
  "renderpass"
 ],
 "t_str": [
  "anim",
  "model",
  "rig",
  "layout",
  "assets",
  "previs",
  "fx"
 ],
 "a_str": [
  "pipeline"
 ],
 "prj_sync_str": [
  "SGW:G:\\Shared drives\\SGW"
 ]
}
    '''
