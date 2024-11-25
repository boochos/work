# -*- coding: utf-8 -*-
import imp
import json
import os
import shutil
import time

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QColor
from PySide2.QtWidgets import ( QWidget, QVBoxLayout, QHBoxLayout,
                              QRadioButton, QButtonGroup, QTreeWidget,
                              QTreeWidgetItem, QListWidget, QLabel,
                              QSplitter, QMenu, QFrame, QPushButton, QComboBox, QToolButton, QLineEdit, QGridLayout, QSizePolicy )
from shiboken2 import wrapInstance

from under_construction.uc_char_set_manager import char_set_core as core
from under_construction.uc_data import data_root
from under_construction.uc_theme import theme_colors as tc
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os.path as osPath

imp.reload( tc )

# TODO: build list of buttons cahracter set toolbox needs. ie, import, export/edit, member toggle, flush/unflush, select objects in set, prefs, activate cycle


def maya_main_window():
    """Return Maya's main window"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance( int( main_window ), QWidget )


class CharacterSetDirectoryManager:
    """Manages the directory structure and file operations for character sets"""
    # TODO: flushed directory needs to support directory handling when arcgived/unarchived

    def __init__( self ):
        self.data_manager = data_root.data_dir_manager
        self.base_dir = None
        self.flushed_dir = None
        self.archived_dir = None
        self.setup_directories()

    def setup_directories( self ):
        """Create the necessary directory structure"""
        try:
            # Get base directory and create characterSets subdirectory
            data_dir = self.data_manager.create_data_directory()
            self.base_dir = os.path.join( data_dir, 'characterSets' )

            # Create subdirectories
            self.flushed_dir = os.path.join( self.base_dir, 'flushed' )
            self.archived_dir = os.path.join( self.base_dir, 'archived' )

            # Ensure directories exist
            for directory in [self.base_dir, self.flushed_dir, self.archived_dir]:
                if not os.path.exists( directory ):
                    os.makedirs( directory )

        except Exception as e:
            cmds.warning( "Failed to setup directories: {}".format( str( e ) ) )

    def get_files( self, directory_type = 'main' ):
        """Get list of character set files from specified directory"""
        try:
            directory = {
                'main': self.base_dir,
                'flushed': self.flushed_dir,
                'archived': self.archived_dir
            }.get( directory_type )

            if not directory or not os.path.exists( directory ):
                return []

            # Get only json files and strip extension
            files = []
            for f in os.listdir( directory ):
                if os.path.isfile( os.path.join( directory, f ) ) and f.endswith( '.json' ):
                    # Strip .json extension
                    name = os.path.splitext( f )[0]
                    files.append( name )

            return sorted( files )  # Return sorted list

        except Exception as e:
            cmds.warning( "Failed to get files from {}: {}".format( directory_type, str( e ) ) )
            return []

    def get_file_content( self, filename, directory_type = 'main' ):
        """Read and return the content of a character set file"""
        try:
            directory = {
                'main': self.base_dir,
                'flushed': self.flushed_dir,
                'archived': self.archived_dir
            }.get( directory_type )

            if not directory:
                return None

            # Add .json extension if it's not there
            if not filename.endswith( '.json' ):
                filename = "{}.json".format( filename )

            file_path = os.path.join( directory, filename )

            if not os.path.exists( file_path ):
                cmds.warning( "File not found: {}".format( file_path ) )
                return None

            with open( file_path, 'r' ) as f:
                return json.load( f )

        except Exception as e:
            cmds.warning( "Failed to read file {}: {}".format( filename, str( e ) ) )
            return None

    def get_directory( self, directory_type ):
        """Get directory path for given type"""
        return {
            'main': self.base_dir,
            'flushed': self.flushed_dir,
            'archived': self.archived_dir
        }.get( directory_type )


class CharacterSetManagerUI( QWidget ):

    def __init__( self, parent = maya_main_window() ):
        # TODO: expansion button is too white, copy what was done, the triangle stylesheet in combobox
        # TODO: try increasing selected content color vibrancy
        # TODO: add some templates sets, biped, quadraped, face, insect, use a dict keep in module.
        # TODO: build import/edit version of the ui
        # TODO: resizing drag button, bottom right corner
        # TODO: ? help button, top left corner
        # TODO: slightly brighter edge border, or darker, around window
        # TODO: move refresh functionality to 'N S:' label, get rid of other button.
        # TODO: if file is deselected in the file list. the treeview should clear its contents
        super( CharacterSetManagerUI, self ).__init__( parent )
        # self.theme = CharSetThemeManager()
        self.themes = tc.ThemeColorManager( 'orange' )

        # Remove window frame and keep it as tool window
        self.setWindowFlags( Qt.Window | Qt.FramelessWindowHint )

        # Variables to track mouse position for moving window
        self.drag_position = None

        # rgb(56, 56, 56 )
        self.setObjectName( "CharacterSetImporter" )
        # TODO: this color should come from the theme module.
        self.setStyleSheet( """
            #CharacterSetImporter {
                background-color: rgb(56, 56, 56 );
            }
        """ )

        self.char_set_manager = CharacterSetDirectoryManager()

        # self.setWindowTitle( "Character Set Manager" )
        # self.setWindowFlags( Qt.Window )
        self.resize( 500, 450 )

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # Initial update
        self.update_file_list( 'main' )
        self.update_namespace_dropdown()

    # Add these new methods for window dragging
    def mousePressEvent( self, event ):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent( self, event ):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move( event.globalPos() - self.drag_position )
            event.accept()

    def mouseReleaseEvent( self, event ):
        self.drag_position = None

    def create_widgets( self ):
        # Radio buttons for directory selection
        self.main_radio = QRadioButton( "M A I N" )
        self.flushed_radio = QRadioButton( "F L U S H E D " )
        self.archived_radio = QRadioButton( "A R K" )
        self.main_radio.setChecked( True )
        self.main_radio.setStyleSheet( self.themes.get_stylesheet_colors( "QRadioButton" ) )
        self.flushed_radio.setStyleSheet( self.themes.get_stylesheet_colors( "QRadioButton" ) )
        self.archived_radio.setStyleSheet( self.themes.get_stylesheet_colors( "QRadioButton" ) )

        # Create button group
        self.directory_group = QButtonGroup()
        self.directory_group.addButton( self.main_radio, 0 )
        self.directory_group.addButton( self.flushed_radio, 1 )
        self.directory_group.addButton( self.archived_radio, 2 )

        # File list widget
        self.file_list = QListWidget()

        self.file_list.setContextMenuPolicy( Qt.CustomContextMenu )
        self.file_list.setMouseTracking( True )  # Add this line
        self.file_list.setFocusPolicy( Qt.NoFocus )
        self.file_list.setStyleSheet( self.themes.get_stylesheet_colors( "QListWidget" ) )

        # Tree widget for character set content
        self.content_tree = QTreeWidget()
        self.content_tree.setMouseTracking( True )  # Add this line
        self.content_tree.setHeaderLabel( "C O N T E N T S" )
        self.content_tree.header().setDefaultAlignment( Qt.AlignCenter )  # Add this line
        self.content_tree.setFocusPolicy( Qt.NoFocus )
        self.content_tree.setStyleSheet( self.themes.get_stylesheet_colors( "QTreeWidget" ) )

        # Create metadata panel with modern styling
        self.metadata_frame = QFrame()
        self.metadata_frame.setFrameStyle( QFrame.StyledPanel | QFrame.Raised )

        # Create metadata labels with headers and content
        self.created_label = QLabel()
        self.created_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        self.modified_label = QLabel()
        self.modified_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        self.size_label = QLabel()
        self.size_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        self.char_count_label = QLabel()
        self.char_count_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        self.attr_count_label = QLabel()
        self.attr_count_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        #
        self.sets_label = QLabel( "Sets :" )
        self.sets_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        # Add import button
        self.import_button = QPushButton( "I M P O R T" )
        self.import_button.setStyleSheet( self.themes.get_stylesheet_colors( "QPushButton" ) )

        # Add namespace dropdown
        self.namespace_label = QLabel( "N S:" )
        self.namespace_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )
        self.namespace_combo = QComboBox()
        self.namespace_combo.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.namespace_combo.setStyleSheet( self.themes.get_stylesheet_colors( "QComboBox" ) )

        # Add refresh button for namespaces
        self.refresh_namespace_btn = QPushButton( "@" )
        self.refresh_namespace_btn.setFixedSize( 19, 19 )
        self.refresh_namespace_btn.setStyleSheet
        self.refresh_namespace_btn.setStyleSheet( self.themes.get_stylesheet_colors( "QPushButton_alt1" ) )

        # In create_widgets method, add:
        self.search_replace_toggle = QToolButton()
        self.search_replace_toggle.setFocusPolicy( Qt.NoFocus )
        self.search_replace_toggle.setArrowType( Qt.RightArrow )  # Collapsed state arrow
        # self.search_replace_toggle.setText( "S / R" )
        # self.search_replace_toggle.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        self.search_replace_toggle.setFixedHeight( 12 )  # Even smaller height

        # Make the arrow smaller
        self.search_replace_toggle.setIconSize( QSize( 6, 6 ) )  # Smaller arrow

        # Create the collapsible widget that will contain our search/replace fields
        self.search_replace_widget = QWidget()
        self.search_replace_widget.setVisible( False )  # Hidden by default

        # Add the rest of the search/replace widgets as before
        self.search_label = QLabel( "S E A R C H :" )
        self.search_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )
        self.replace_label = QLabel( "R E P L A C E :" )
        self.replace_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel" ) )

        self.search_field = QLineEdit()
        self.replace_field = QLineEdit()
        self.search_field.setStyleSheet( self.themes.get_stylesheet_colors( "QLineEdit" ) )
        self.replace_field.setStyleSheet( self.themes.get_stylesheet_colors( "QLineEdit" ) )

    def create_layouts( self ):
        main_layout = QVBoxLayout( self )

        # Add custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight( 25 )
        # title_bar.setStyleSheet( self.theme.get_title_bar_style() )

        # Title bar layout
        title_layout = QHBoxLayout( title_bar )
        title_layout.setContentsMargins( 6, 0, 6, 0 )

        # Add title label
        title_label = QLabel( "C h a r a c t e r   S e t   M a n a g e r".upper() )
        title_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel_title" ) )
        title_layout.addWidget( title_label )

        # Add close button
        close_button = QPushButton( "X" )
        close_button.setFixedSize( 19, 19 )
        close_button.setStyleSheet( self.themes.get_stylesheet_colors( "QPushButton_alt1" ) )
        close_button.clicked.connect( self.close )
        title_layout.addWidget( close_button )

        # Add title bar to main layout
        main_layout.addWidget( title_bar )

        # Create splitter
        self.splitter = QSplitter( Qt.Horizontal )

        # Left widget container
        left_widget = QWidget()
        left_layout = QVBoxLayout( left_widget )
        left_layout.setContentsMargins( 2, 2, 2, 2 )

        # Radio button layout
        radio_layout = QHBoxLayout()
        radio_layout.addWidget( self.main_radio )
        radio_layout.addWidget( self.flushed_radio )
        radio_layout.addWidget( self.archived_radio )

        left_layout.addLayout( radio_layout )
        left_layout.addWidget( self.sets_label )
        left_layout.addWidget( self.file_list )

        # Metadata section
        metadata_layout = QVBoxLayout( self.metadata_frame )
        metadata_layout.setContentsMargins( 8, 8, 8, 8 )
        metadata_layout.setSpacing( 4 )

        # Add a header
        header_label = QLabel( "M E T A" )
        header_label.setStyleSheet( self.themes.get_stylesheet_colors( "QLabel_subtitle" ) )
        metadata_layout.addWidget( header_label )

        # Add separator line
        separatorH = QFrame()
        separatorH.setFrameStyle( QFrame.HLine | QFrame.Plain )
        # TODO: color should come from the theme module
        separatorH.setStyleSheet( "QFrame { color: rgb(230, 230, 230); }" )  # Brighter for better visibility
        metadata_layout.addWidget( separatorH )

        # Add metadata labels with some spacing
        metadata_layout.addWidget( separatorH )
        metadata_layout.addWidget( self.char_count_label )
        metadata_layout.addWidget( self.attr_count_label )
        metadata_layout.addWidget( self.created_label )
        metadata_layout.addWidget( self.modified_label )
        metadata_layout.addWidget( self.size_label )

        metadata_layout.addStretch()

        self.metadata_frame.setFixedHeight( 100 )
        left_layout.addWidget( self.metadata_frame )

        # Right widget container
        right_widget = QWidget()
        right_layout = QVBoxLayout( right_widget )
        right_layout.setContentsMargins( 2, 2, 2, 2 )
        right_layout.addWidget( self.content_tree )

        # Create search/replace section
        search_replace_container = QWidget()
        search_replace_container_layout = QVBoxLayout( search_replace_container )
        search_replace_container_layout.setContentsMargins( 0, 0, 0, 0 )
        search_replace_container_layout.setSpacing( 0 )

        # Add toggle button
        search_replace_container_layout.addWidget( self.search_replace_toggle )

        # Setup the collapsible widget
        search_replace_layout = QGridLayout( self.search_replace_widget )
        search_replace_layout.setContentsMargins( 20, 5, 0, 5 )  # Left margin for indentation
        search_replace_layout.setSpacing( 5 )

        # Add labels in first row
        search_replace_layout.addWidget( self.search_label, 0, 0 )
        search_replace_layout.addWidget( self.replace_label, 0, 1 )

        # Add text fields in second row
        search_replace_layout.addWidget( self.search_field, 1, 0 )
        search_replace_layout.addWidget( self.replace_field, 1, 1 )

        # Add collapsible widget to container
        search_replace_container_layout.addWidget( self.search_replace_widget )

        # Add namespace section
        namespace_widget = QWidget()
        namespace_layout = QHBoxLayout( namespace_widget )
        namespace_layout.setContentsMargins( 0, 5, 0, 5 )
        namespace_layout.addWidget( self.namespace_label )
        namespace_layout.addWidget( self.namespace_combo )
        namespace_layout.addWidget( self.refresh_namespace_btn )

        right_layout.addWidget( search_replace_container )
        right_layout.addWidget( namespace_widget )
        right_layout.addWidget( self.import_button )  # Add import button below content tree

        # Add widgets to splitter
        self.splitter.addWidget( left_widget )
        self.splitter.addWidget( right_widget )

        # Set initial sizes (1:2 ratio)
        self.splitter.setSizes( [300, 500] )

        # Add splitter to main layout
        main_layout.addWidget( self.splitter )

    def create_connections( self ):
        self.directory_group.buttonClicked.connect( self.on_directory_changed )
        self.file_list.itemClicked.connect( self.on_file_selected )
        self.file_list.customContextMenuRequested.connect( self.show_context_menu )
        self.import_button.clicked.connect( self.import_character_set )
        self.refresh_namespace_btn.clicked.connect( self.update_namespace_dropdown )
        self.search_replace_toggle.clicked.connect( self.toggle_search_replace )

    def show_context_menu( self, position ):
        """Show context menu for file list items"""
        item = self.file_list.itemAt( position )
        if not item:
            return

        menu = QMenu()
        menu.setStyleSheet( self.themes.get_stylesheet_colors( "QMenu" ) )  # Add this line
        current_dir = self.get_current_directory()

        if current_dir in ['main', 'flushed']:
            archive_action = menu.addAction( "Archive" )
            archive_action.triggered.connect( lambda: self.archive_file( item.text() ) )
        elif current_dir == 'archived':
            unarchive_action = menu.addAction( "Un-archive" )
            unarchive_action.triggered.connect( lambda: self.unarchive_file( item.text() ) )

        cursor = self.file_list.mapToGlobal( position )
        menu.exec_( cursor )

    def get_current_directory( self ):
        """Get currently selected directory type"""
        if self.main_radio.isChecked():
            return 'main'
        elif self.flushed_radio.isChecked():
            return 'flushed'
        elif self.archived_radio.isChecked():
            return 'archived'
        return None

    def update_metadata( self, filename = None ):
        """Update metadata panel with file information"""
        try:
            if not filename:
                # Clear metadata if no file selected
                self.created_label.setText( "Created: --" )
                self.modified_label.setText( "Modified: --" )
                self.size_label.setText( "File Size: --" )
                self.char_count_label.setText( "Character Sets: --" )
                self.attr_count_label.setText( "Attributes: --" )
                return

            # Get file path
            current_dir = self.get_current_directory()
            filepath = osPath.join( self.char_set_manager.get_directory( current_dir ), filename + '.json' )

            if not osPath.exists( filepath ):
                return

            # Get file stats
            stats = os.stat( filepath )

            # Format timestamps
            created_time = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( stats.st_ctime ) )
            modified_time = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( stats.st_mtime ) )

            # Format file size
            size_bytes = stats.st_size
            if size_bytes < 1024:
                size_str = "{} bytes".format( size_bytes )
            elif size_bytes < 1024 * 1024:
                size_str = "{:.1f} KB".format( size_bytes / 1024.0 )
            else:
                size_str = "{:.1f} MB".format( size_bytes / ( 1024.0 * 1024.0 ) )

            # Get content stats
            content = self.char_set_manager.get_file_content( filename, current_dir )
            counts = [0, 0]  # [char_count, attr_count]

            def count_items( data, counts ):
                if isinstance( data, dict ):
                    if 'character' in data:
                        counts[0] += 1
                    if 'attribute' in data:
                        counts[1] += 1
                    if 'members' in data and isinstance( data['members'], list ):
                        for member in data['members']:
                            count_items( member, counts )
                return counts

            if content:
                counts = count_items( content, counts )

            # Update labels
            self.created_label.setText( "Created: {}".format( created_time ) )
            self.modified_label.setText( "Modified: {}".format( modified_time ) )
            self.size_label.setText( "File Size: {}".format( size_str ) )
            self.char_count_label.setText( "Character Sets: {}".format( counts[0] ) )
            self.attr_count_label.setText( "Attributes: {}".format( counts[1] ) )

        except Exception as e:
            cmds.warning( "Failed to update metadata: {}".format( str( e ) ) )

    def update_file_list( self, directory_type ):
        """Update the file list based on selected directory"""
        self.file_list.clear()
        files = self.char_set_manager.get_files( directory_type )
        self.file_list.addItems( files )

    def update_content_tree( self, content ):
        """Update the tree widget with character set hierarchy"""
        try:
            self.content_tree.clear()

            if not content:
                return

            def add_character_set( parent_item, data ):
                """Recursively add character sets and their members to the tree"""
                if not isinstance( data, dict ):
                    return

                # If this is a simple attribute entry
                if 'attribute' in data:
                    QTreeWidgetItem( parent_item, [data['attribute']] )
                    return

                # For character sets
                if 'character' in data:
                    # Create character set item
                    char_item = QTreeWidgetItem( parent_item, [data['character']] )

                    # Process members
                    has_attributes = False
                    if 'members' in data and isinstance( data['members'], list ):
                        for member in data['members']:
                            if isinstance( member, dict ) and 'attribute' in member:
                                has_attributes = True
                            add_character_set( char_item, member )

                    # Collapse if it has attributes
                    if has_attributes:
                        char_item.setExpanded( False )
                    else:
                        char_item.setExpanded( True )

                    return char_item

            # Start with root character set
            root_item = add_character_set( self.content_tree, content )
            if root_item:
                root_item.setExpanded( True )  # Always expand root

        except Exception as e:
            cmds.warning( "Failed to update content tree: {}".format( str( e ) ) )

    def on_file_selected( self, item ):
        """Handle file selection"""
        try:
            # Update metadata
            self.update_metadata( item.text() )

            # Update content tree
            current_dir = self.get_current_directory()
            filename = item.text()
            content = self.char_set_manager.get_file_content( filename, current_dir )
            self.update_content_tree( content )

            # Find and select matching namespace
            self.match_namespace_from_content( content )

        except Exception as e:
            cmds.warning( "Failed to handle file selection: {}".format( str( e ) ) )

    def on_directory_changed( self, button ):
        """Handle directory radio button selection"""
        directory_map = {
            self.main_radio: 'main',
            self.flushed_radio: 'flushed',
            self.archived_radio: 'archived'
        }
        self.update_file_list( directory_map[button] )

    def archive_file( self, filename ):
        """Move file to archive directory"""
        try:
            src_filename = filename + '.json'
            current_dir = self.get_current_directory()

            src_path = os.path.join( self.char_set_manager.get_directory( current_dir ), src_filename )
            dst_path = os.path.join( self.char_set_manager.archived_dir, src_filename )

            shutil.move( src_path, dst_path )
            self.update_file_list( current_dir )
            cmds.warning( "File archived: {}".format( filename ) )

        except Exception as e:
            cmds.warning( "Failed to archive file: {}".format( str( e ) ) )

    def unarchive_file( self, filename ):
        """Move file back to main directory"""
        try:
            src_filename = filename + '.json'

            src_path = os.path.join( self.char_set_manager.archived_dir, src_filename )
            dst_path = os.path.join( self.char_set_manager.base_dir, src_filename )

            shutil.move( src_path, dst_path )
            self.update_file_list( 'archived' )
            cmds.warning( "File un-archived: {}".format( filename ) )

        except Exception as e:
            cmds.warning( "Failed to un-archive file: {}".format( str( e ) ) )

    def import_character_set( self ):
        """Import the selected character set"""
        try:
            # Get selected file
            selected_items = self.file_list.selectedItems()
            if not selected_items:
                cmds.warning( "Please select a character set to import." )
                return

            filename = selected_items[0].text()
            current_dir = self.get_current_directory()

            # Import the character set
            import_path = os.path.join( self.char_set_manager.get_directory( current_dir ), filename + '.json' )
            core.importFileFromJSON( path = import_path )

            cmds.warning( "Successfully imported character set: {}".format( filename ) )

        except Exception as e:
            cmds.warning( "Failed to import character set: {}".format( str( e ) ) )

    # Add this method for tooltip functionality
    def update_namespace_dropdown( self ):
        """Update the namespace dropdown with current Maya scene namespaces"""
        try:
            self.namespace_combo.clear()
            self.namespace_combo.addItem( ":" )

            namespaces = cmds.namespaceInfo( listOnlyNamespaces = True, recurse = True ) or []

            if namespaces:
                namespaces.sort()
                for namespace in namespaces:
                    if namespace not in ['UI', 'shared']:
                        self.namespace_combo.addItem( namespace )
                        # Add tooltip for each item
                        index = self.namespace_combo.count() - 1
                        self.namespace_combo.setItemData( index, namespace, Qt.ToolTipRole )
        except Exception as e:
            cmds.warning( "Failed to update namespaces: {}".format( str( e ) ) )

    def match_namespace_from_content( self, content ):
        """Find and select matching namespace from content"""
        try:
            if not content or 'members' not in content:
                return

            # Extract first attribute path to get namespace
            attr_namespace = None

            def find_first_attribute( data ):
                """Recursively find first attribute in content"""
                if isinstance( data, dict ):
                    if 'attribute' in data:
                        attr_path = data['attribute']
                        # Split by : and get namespace if exists
                        if ':' in attr_path:
                            return attr_path.split( ':' )[0]
                    elif 'members' in data:
                        for member in data['members']:
                            result = find_first_attribute( member )
                            if result:
                                return result
                return None

            attr_namespace = find_first_attribute( content )

            # If we found a namespace in the attributes
            if attr_namespace:
                # Get index of matching namespace in combo box
                index = self.namespace_combo.findText( attr_namespace )
                if index >= 0:
                    self.namespace_combo.setCurrentIndex( index )
                    print( "Found and selected namespace: {}".format( attr_namespace ) )
                else:
                    print( "Namespace in file {} not found in scene".format( attr_namespace ) )

        except Exception as e:
            cmds.warning( "Failed to match namespace: {}".format( str( e ) ) )

    def toggle_search_replace( self ):
        """Toggle the visibility of search/replace section"""
        is_visible = self.search_replace_widget.isVisible()
        self.search_replace_widget.setVisible( not is_visible )

        # Change arrow direction
        if is_visible:
            self.search_replace_toggle.setArrowType( Qt.RightArrow )
        else:
            self.search_replace_toggle.setArrowType( Qt.DownArrow )


def show():
    """Show the Character Set Manager UI"""
    global character_set_manager_ui

    try:
        character_set_manager_ui.close()
        character_set_manager_ui.deleteLater()
    except:
        pass

    character_set_manager_ui = CharacterSetManagerUI()
    character_set_manager_ui.show()
