# run to list unknown plugins
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

# print os.environ


def message( what = '' ):
    maya.mel.eval( 'print \"' + '-- ' + what + ' --' + '\";' )
    # print "\n"


def init_ui():
    # main
    main_window = QtWidgets.QDialog()
    main_layout = QtWidgets.QVBoxLayout()
    # prefs
    top_layout = QtWidgets.QHBoxLayout()
    prefs_button = QtWidgets.QPushButton( "Preferences" )
    prefs_button.clicked.connect( lambda: pref_window( 'path' ) )
    #
    top_layout.addWidget( prefs_button )
    main_layout.addLayout( top_layout )
    # directories
    directory_layout = QtWidgets.QHBoxLayout()
    project_list_widget = QtWidgets.QListWidget()
    shots_and_assets_list_widget = QtWidgets.QListWidget()
    tasks_list_widget = QtWidgets.QListWidget()
    scene_list_widget = QtWidgets.QListWidget()
    #
    projects = get_projects()
    for project in projects:
        project_list_widget.addItem( project )
    directory_layout.addWidget( project_list_widget )
    directory_layout.addWidget( shots_and_assets_list_widget )
    directory_layout.addWidget( tasks_list_widget )
    directory_layout.addWidget( scene_list_widget )
    main_layout.addLayout( directory_layout )
    # buttons
    bottom_layout = QtWidgets.QHBoxLayout()
    set_project_button = QtWidgets.QPushButton( "Set Project" )
    set_project_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget ) )
    create_button = QtWidgets.QPushButton( "Create Scene" )
    create_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene = None, opn = False, create = scene_list_widget ) )
    set_open_button = QtWidgets.QPushButton( "Open" )
    set_open_button.clicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, True ) )
    ref_button = QtWidgets.QPushButton( "Reference" )
    ref_button.clicked.connect( lambda: ref_scene( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    explore_button = QtWidgets.QPushButton( "Explore" )
    explore_button.clicked.connect( lambda: explore_path( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    range_button = QtWidgets.QPushButton( "Set Scene Range" )
    range_button.clicked.connect( lambda: frameRangeFromMaFile( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    sync_button = QtWidgets.QPushButton( "Sync File" )
    sync_button.clicked.connect( lambda: sync_file( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget ) )
    #
    bottom_layout.addWidget( set_project_button )
    bottom_layout.addWidget( create_button )
    bottom_layout.addWidget( set_open_button )
    bottom_layout.addWidget( ref_button )
    top_layout.addWidget( explore_button )
    top_layout.addWidget( sync_button )
    top_layout.addWidget( range_button )
    main_layout.addLayout( bottom_layout )

    main_window.setLayout( main_layout )

    main_window.setWindowTitle( 'Set Project Tool' )
    project_list_widget.itemSelectionChanged.connect( lambda: get_shots_assets( shots_and_assets_list_widget, project_list_widget.currentItem().text() ) )
    project_list_widget.itemSelectionChanged.connect( lambda: tasks_list_widget.clear() )
    shots_and_assets_list_widget.itemSelectionChanged.connect( lambda: get_tasks( tasks_list_widget, project_list_widget.currentItem().text(), shots_and_assets_list_widget.currentItem().text(), scene_list_widget ) )
    tasks_list_widget.itemSelectionChanged.connect( lambda: get_scenes( scene_list_widget, project_list_widget.currentItem().text(), shots_and_assets_list_widget.currentItem().text(), tasks_list_widget ) )
    scene_list_widget.itemDoubleClicked.connect( lambda: set_project( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget, True ) )
    main_window.resize( 900, 400 )

    # parse current scene
    get_current( project_list_widget, shots_and_assets_list_widget, tasks_list_widget, scene_list_widget )

    return main_window


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
    prefs = Prefs()
    skips = prefs.prefs['p_str']
    # print skips
    raw_projects = os.listdir( os.environ['PROJ_ROOT'] )
    clean = []
    for r in raw_projects:
        if r not in skips and '.' not in r:
            clean.append( r )

    return clean


def get_shots_assets( list_widget, project ):
    """Get both shots and assets for a project."""
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
    list_widget.clear()
    for project in shots_n_assets:
        list_widget.addItem( project )
    list_widget.setVisible( True )


def get_assets( ep_path ):
    # print ep_path
    """Get assets in new structure."""
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


def get_tasks( list_widget, project, entity, scenes ):
    """Get tasks."""
    #
    scenes.clear()
    default_tasks = ['anim',
                     'model',
                     'rig',
                     'fx',
                     'layout',
                     'light',
                     'lookdev']
    prefs = Prefs()
    default_tasks = prefs.prefs['t_str']
    #
    current_task = None
    if list_widget.selectedItems():
        current_task = list_widget.selectedItems()[0].text()
    #
    raw_tasks_directory = os.path.join( os.environ['PROJ_ROOT'], project, entity )
    if not os.path.isdir( raw_tasks_directory ):
        list_widget.clear()
        return
    raw_tasks = os.listdir( raw_tasks_directory )
    tasks = []
    for task in raw_tasks:
        if task in default_tasks:
            tasks.append( task )
    tasks.sort()
    if not tasks:
        no_path( os.path.join( os.environ['PROJ_ROOT'], project, entity ).replace( '\\', '/' ) )
        list_widget.clear()
        return
    list_widget.clear()
    for task in tasks:
        list_widget.addItem( task )
    list_widget.setVisible( True )
    # reselect task
    if current_task:
        item = list_widget.findItems( current_task, QtCore.Qt.MatchExactly )
        if item:
            list_widget.setCurrentItem( item[0] )
        # print items


def get_scenes( list_widget, project, entity, task ):
    """
    Get scenes
    """
    if task.selectedItems():
        task = task.selectedItems()[0].text()
    else:
        list_widget.clear()
        return
    raw_scene_directory = os.path.join( os.environ['PROJ_ROOT'], project, entity, task, 'maya', 'scenes' )
    if not os.path.isdir( raw_scene_directory ):
        list_widget.clear()
        return
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


def get_current( projects = None, entities = None, tasks = None, scenes = None ):
    '''
    inputs are QListWidget objects
    parse current scene path, load and set project
    '''
    path = cmds.file( query = True, sn = True )
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
                item = entities.findItems( os.path.join( parts[2], parts[3], parts[4] ), QtCore.Qt.MatchExactly )
                # print item
                if item:
                    entities.setCurrentItem( item[0] )
                # task
                item = tasks.findItems( parts[5], QtCore.Qt.MatchExactly )
                if item:
                    tasks.setCurrentItem( item[0] )
                # scene
                item = scenes.findItems( parts[8], QtCore.Qt.MatchExactly )
                if item:
                    scenes.setCurrentItem( item[0] )
            else:
                item = entities.findItems( os.path.join( parts[2], parts[3] ), QtCore.Qt.MatchExactly )
                # print item
                if item:
                    entities.setCurrentItem( item[0] )
                # task
                item = tasks.findItems( parts[4], QtCore.Qt.MatchExactly )
                if item:
                    tasks.setCurrentItem( item[0] )
                # scene
                item = scenes.findItems( parts[7], QtCore.Qt.MatchExactly )
                if item:
                    scenes.setCurrentItem( item[0] )


def no_path( path ):
    """Error dialog."""
    pass
    '''
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon( QtWidgets.QMessageBox.Warning )
    msg_box.setText( '{}\n\nThis path does not exist or it is missing all of its key folders.\n\n'.format( path ) )
    msg_box.setWindowTitle( "Missing Path" )
    msg_box.exec_()'''


def set_project( project, entity, task, scene = None, opn = False, create = None ):
    """
    Set Project in Maya.
    """
    #
    refresh_scenes = [create, project, entity, task]
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
    if scene:
        if scene.selectedItems():
            scene = scene.selectedItems()[0].text()
        else:
            scene = None
    #
    project_path = False
    if go:
        project_dir = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya' ).replace( '\\', '/' )
        if not os.path.exists( project_dir ):
            no_path( project_dir )
        else:
            project_path = True
            mel_command = ( 'setProject "' + project_dir + '";' )

            maya.mel.eval( mel_command )
            # print( 'Project set to:\n{}'.format( project_dir ) )
            # print 'Project set to: ', project_dir
            maya.mel.eval( 'print \" -- Project set to  -- ' + project_dir + ' -- \";' )
            '''
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText( 'Project has been set to\n\n{}'.format( project_dir ) )
            msg_box.setWindowTitle( "Maya Project Set" )
            msg_box.exec_()
            '''
        if opn:
            if scene:
                pth = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
                cmds.file( pth, open = True, force = True )
            else:
                pth = cmds.fileDialog2( fileMode = 1, startingDirectory = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes' ) )
                if pth:
                    cmds.file( pth, open = True, force = True )
        if create:
            if project_path:
                pth = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes' )
                result = filename( pth, entity, task )
                if result:
                    get_scenes( refresh_scenes[0], project, entity, refresh_scenes[3] )
            else:
                maya.mel.eval( 'print \" -- Project set FAIL -- cant create scene -- \";' )
    else:
        maya.mel.eval( 'print \" -- Cant build project path, select more variables -- \";' )


def ref_scene( project, entity, task, scene = None ):
    """
    reference scene
    """
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
    if scene:
        if scene.selectedItems():
            scene = scene.selectedItems()[0].text()
        else:
            scene = None
    #
    if go:
        project_dir = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya' ).replace( '\\', '/' )
        if not os.path.exists( project_dir ):
            no_path( project_dir )
        # ref scene
        ns = nmspc( entity = entity, task = task )
        if scene:
            pth = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
            cmds.file( pth, reference = True, namespace = ns )
        # open dialog if task
        elif task:
            pth = cmds.fileDialog2( fileMode = 1, startingDirectory = os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya' ) )
            if pth:
                cmds.file( pth, reference = True, namespace = ns )
        else:
            maya.mel.eval( 'print \" -- no task or file selected -- \";' )
    else:
        maya.mel.eval( 'print \" -- Cant build reference path, select more variables -- \";' )


def explore_path( project, entity, task, scene ):
    '''
    os.path.join( os.environ["PROJ_ROOT"], project, entity, task, 'maya', 'scenes', scene )
    '''
    path = None
    #
    if project.selectedItems():
        project = project.selectedItems()[0].text()
        path = os.path.join( os.environ["PROJ_ROOT"], project )
    if entity.selectedItems():
        entity = entity.selectedItems()[0].text()
        path = os.path.join( path, entity )
    if task.selectedItems():
        task = task.selectedItems()[0].text()
        path = os.path.join( path, task )
    if scene.selectedItems():
        path = os.path.join( path, 'maya', 'scenes' )
    #
    if os.path.isdir( path ):
        subprocess.Popen( r'explorer /open, ' + path )


def nmspc( entity = '', task = '' ):
    '''
    iterate namespace string unttil namespace is unused
    for referencing same file multiple times
    '''
    e = entity.split( '\\' )
    if e:
        e = e[-1]
    ns = e + '_' + task
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
    '''
    scene_info = [basepath, basename, extension]

    # make sure the correct file format is being used
    if scene_info is not False:
        # if no number was found, force it to 0000
        # find the highest version of the current scene name in the folder, then increment the current scene to one more than that then save
        files = os.listdir( scene_info[0] )
        num = 000
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
                            if file_info[1] > num:
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
    save_button.clicked.connect( lambda: Prefs( prj_edit, entity_edit, assets_edit, assettype_edit, task_edit, sync_edit ) )
    close_button = QtWidgets.QPushButton( "Close" )
    close_button.clicked.connect( lambda: main_window.close() )

    buttons_layout.addWidget( save_button )
    buttons_layout.addWidget( close_button )
    main_layout.addLayout( buttons_layout )

    # draw window
    main_window.setLayout( main_layout )
    main_window.setWindowTitle( "Preferences" )
    main_window.setMinimumWidth( 1000 )
    main_window.exec_()

    '''
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon( QtWidgets.QMessageBox.Warning )
    msg_box.setText( '{}\n\nThis path does not exist or it is missing all of its key folders.\n\n'.format( path ) )
    msg_box.setWindowTitle( "Preferences" )
    msg_box.exec_()'''


class Prefs():

    def __init__( self, projects = None, entities = None, assets = None, assettypes = None, tasks = None, sync = None ):
        '''
        '''
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
                print( 'parse sync roots' )
                self.prefSync()

    def prefPath( self, *args ):
        varPath = cmds.internalVar( userAppDir = True )
        path = os.path.join( varPath, 'scripts' )
        path = os.path.join( path, 'SetProjectToolPrefs.json' )
        return path

    def prefSave( self, *args ):
        # save
        fileObjectJSON = open( self.prefPath(), 'wb' )
        json.dump( self.prefs, fileObjectJSON, indent = 1 )
        fileObjectJSON.close()

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


def frameRangeFromMaFile( project, entity, task, scene, handles = 0 ):
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
                    print( line )
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
                    print( play_start )
                    print( play_end )
                    print( all_start )
                    print( all_end )
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
        else:
            maya.mel.eval( 'print \" -- Select a .ma file  -- \";' )
            # print 'not a directory'
    else:
        maya.mel.eval( 'print \" -- Select a .ma file  -- \";' )


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

'''
{
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
'''
