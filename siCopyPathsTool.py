import datetime
import json
import os
import random
import shutil
import subprocess
import sys
import time
import traceback

from PySide2 import QtCore, QtGui, QtWidgets


def ____UI():
    pass


class CustomQDialog( QtWidgets.QDialog ):
    '''
    
    '''

    def __init__( self ):
        super().__init__()
        self.validate = True

    def closeEvent( self, event ):
        '''
        
        '''
        # do stuff, figure out how to get session info and save it
        #
        self.validate = False
        p_d = Prefs_dynamic()
        p_d.prefs[p_d.session_window_pos_x] = self.frameGeometry().x()
        p_d.prefs[p_d.session_window_pos_y] = self.frameGeometry().y()
        p_d.prefs[p_d.session_window_width] = self.geometry().width()
        # p_d.prefs[p_d.session_window_height] = self.geometry().height()
        # setProject_window = None
        p_d.prefSave()
        #
        event.accept()
        # print( 'Window closed' )


class UI():

    def __init__( self ):
        '''
        
        '''
        self.kill = False
        self.copying = False
        self.all_valid = True
        # self.p = Prefs()
        self.p_d = Prefs_dynamic()
        self.final_directory = todays_directory_name()
        self.sources_ui_list = []
        self.sources_ui_layouts = []
        # main
        # self.main_window = QtWidgets.QDialog()
        self.main_window = CustomQDialog()  # close event altered

        self.main_window.setWindowTitle( 'SI Copy Sources' )
        #
        w = 600
        h = 80
        if self.p_d.prefs[self.p_d.session_window_width]:
            w = int( self.p_d.prefs[self.p_d.session_window_width] )
            # h = int( self.p_d.prefs[self.p_d.session_window_height] )
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
        self.source_row()
        self.source_row()
        self.daily_row()
        self.copy_row()
        self.message_row()

        #
        # self.main_window.show()

        self.threadpool = QtCore.QThreadPool()
        # print( "Multithreading with maximum %d threads" % self.threadpool.maxThreadCount() )
        self.start_validation_thread()

    def add_source_row( self ):
        '''
        
        '''
        #
        self.add_source_layout = QtWidgets.QHBoxLayout()
        self.add_source_button = QtWidgets.QPushButton( "A D D   S O U R C E " )
        self.add_source_button.clicked.connect( lambda:self.source_row() )
        color = [ 0.701, 0.690, 0.678 ]
        bg = "background-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border = "border: 4px solid;"
        border_color_top = "border-top-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_left = "border-left-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_right = "border-right-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_bottom = "border-bottom-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        self.add_source_button.setStyleSheet( bg + border + border_color_top + border_color_left + border_color_right + border_color_bottom )  # QtGui.QColor( 1, 0.219, 0.058 )

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
        self.destination_edit = QtWidgets.QLineEdit( self.p_d.prefs[self.p_d.last_destination] )
        self.destination_edit.textChanged.connect( lambda: self.destination_validate() )
        #
        #
        self.destination_dir_button = QtWidgets.QPushButton( "D i r" )
        self.destination_dir_button.clicked.connect( lambda:self.source_dir_select( self.destination_edit ) )
        #
        self.destination_layout = QtWidgets.QHBoxLayout()
        self.destination_layout.addWidget( self.destination_label )
        self.destination_layout.addWidget( self.destination_edit )
        self.destination_layout.addWidget( self.destination_dir_button )
        #
        self.main_layout.addLayout( self.destination_layout )
        #
        # self.separate_0 = QtWidgets.QFrame()
        # self.main_layout.addWidget( self.separate_0 )
        #
        self.destination_validate()

    def destination_save( self ):
        '''
        
        '''
        p_d = Prefs_dynamic()
        p_d.prefs[p_d.last_destination] = self.destination_edit.text()
        p_d.prefSave()

    def destination_validate( self ):
        '''
        
        '''
        if self.destination_edit.text() == '':
            self.destination_edit.setStyleSheet( "border: 1px solid gray;" )
        else:
            if not os.path.isdir( self.destination_edit.text() ):
                self.destination_edit.setStyleSheet( "border: 1px solid red;" )
            else:
                self.destination_edit.setStyleSheet( "border: 1px solid lightgreen;" )
        #
        self.destination_save()

    def source_row( self ):
        '''
        
        '''
        #
        self.exists = 2
        self.overwrite = 3
        self.invalid = 4
        #
        source_layout = QtWidgets.QHBoxLayout()  # need this to already exist
        #
        source_group = []
        source_label = QtWidgets.QLabel( 'Source Path:  ' )
        source_edit = QtWidgets.QLineEdit()
        source_edit.textChanged.connect( lambda: self.source_validate( source_edit, source_layout ) )
        source_group.append( source_edit )
        #
        exists_label = QtWidgets.QLabel( ' Destination exists' )
        exists_label.setStyleSheet( "color:  red;" "font-weight: bold" )
        exists_label.setVisible( False )
        #
        overwrite_label = QtWidgets.QLabel( ' File overwrite' )
        overwrite_label.setStyleSheet( "color:  green;" "font-weight: bold" )
        overwrite_label.setVisible( False )
        #
        invalid_label = QtWidgets.QLabel( ' Source invalid' )
        invalid_label.setStyleSheet( "color:  red;" "font-weight: bold" )
        invalid_label.setVisible( False )
        #
        browse_file_button = QtWidgets.QPushButton( "F i l e" )
        browse_file_button.clicked.connect( lambda:self.source_file_select( source_edit ) )
        source_group.append( browse_file_button )
        #
        browse_dir_button = QtWidgets.QPushButton( "D i r" )
        browse_dir_button.clicked.connect( lambda:self.source_dir_select( source_edit ) )
        source_group.append( browse_dir_button )
        #
        source_layout.addWidget( source_label )
        source_layout.addWidget( source_edit )
        source_layout.addWidget( exists_label )
        source_layout.addWidget( overwrite_label )
        source_layout.addWidget( invalid_label )
        source_layout.addWidget( browse_file_button )
        source_layout.addWidget( browse_dir_button )
        #
        self.add_sources_layout.addLayout( source_layout )
        #
        self.sources_ui_list.append( source_group )
        self.sources_ui_layouts.append( source_layout )

    def source_validate( self, source_edit = None, source_layout = None ):
        '''
        
        '''
        #

        #
        valid = True
        if not self.copying:
            if source_edit.text() == '':
                # source_edit.setStyleSheet( "border: 1px solid gray;" )
                if self.all_valid:
                    # self.copy_button.setDisabled( False )
                    pass
                #
                source_layout.itemAt( self.exists ).widget().setVisible( False )
                source_layout.itemAt( self.overwrite ).widget().setVisible( False )
                source_layout.itemAt( self.invalid ).widget().setVisible( False )
                valid = True
            else:
                go = False
                if os.path.isdir( source_edit.text() ):
                    go = True
                    # source_edit.setStyleSheet( "border: 1px solid red;" )
                elif os.path.isfile( source_edit.text() ):
                    go = True
                #
                if go:
                    qualified = self.source_remap_qualify( source_edit )
                    if qualified:
                        if qualified == 'exists':
                            source_layout.itemAt( self.exists ).widget().setVisible( False )
                            source_layout.itemAt( self.overwrite ).widget().setVisible( True )
                            source_layout.itemAt( self.invalid ).widget().setVisible( False )
                            valid = True
                        elif qualified == 'error':

                            source_layout.itemAt( self.exists ).widget().setVisible( False )
                            source_layout.itemAt( self.overwrite ).widget().setVisible( False )
                            source_layout.itemAt( self.invalid ).widget().setText( 'Destination error' )
                            # source_layout.itemAt( self.invalid ).widget().setStyleSheet( "color:  green;" "font-weight: bold" )
                            source_layout.itemAt( self.invalid ).widget().setVisible( True )
                        else:
                            # source_edit.setStyleSheet( "border: 1px solid lightgreen;" )
                            # if self.all_valid:
                                # self.copy_button.setDisabled( False )
                                # pass
                            #
                            # '''
                            source_layout.itemAt( self.exists ).widget().setVisible( False )
                            source_layout.itemAt( self.overwrite ).widget().setVisible( False )
                            source_layout.itemAt( self.invalid ).widget().setVisible( False )
                            valid = True
                        # '''
                    else:
                        # source_edit.setStyleSheet( "border: 1px solid orange;" )
                        # self.copy_button.setDisabled( True )
                        #
                        # '''
                        source_layout.itemAt( self.exists ).widget().setVisible( True )
                        source_layout.itemAt( self.overwrite ).widget().setVisible( False )
                        source_layout.itemAt( self.invalid ).widget().setVisible( False )
                        valid = False
                        # '''
                else:
                    # source_edit.setStyleSheet( "border: 1px solid red;" )
                    # self.copy_button.setDisabled( True )
                    #
                    # '''
                    source_layout.itemAt( self.exists ).widget().setVisible( False )
                    source_layout.itemAt( self.overwrite ).widget().setVisible( False )
                    source_layout.itemAt( self.invalid ).widget().setVisible( True )
                    valid = False

        return valid
                # '''
        # itm = source_layout.itemAt( self.invalid ).widget()
        # itm.setVisible( True )
        # print( source_layout.itemAt( self.invalid ) )

    def source_remap_qualify( self, source_edit = None ):
        '''
        fix entire function to qualify a given source path to a given destination, without creating any files or directories
        '''
        qualified = False
        final_destination = ''
        destination_path = self.destination_edit.text()
        # print( 'destination: ', destination_path )
        #
        if os.path.isdir( destination_path ):
            #
            if self.daily_check.isChecked():
                if self.final_directory not in destination_path:
                    destination_path = os.path.join( destination_path, self.final_directory )
                self.make_final_directory( destination_path )
            #
            source_path = source_edit.text()
            if source_path:
                # print( 'source: ', source_path )
                go = False
                _dir = False
                if os.path.isdir( source_path ):
                    go = True
                    _dir = True
                elif os.path.isfile( source_path ):
                    go = True
                if go:
                    #
                    name = ''
                    if '\\' in source_path:
                        name = source_path.split( '\\' )[-1]
                    elif '/' in source_path:
                        name = source_path.split( '/' )[-1]
                    # print( 'name: ', name )
                    #
                    final_destination = os.path.join( destination_path, name )
                    final_destination = final_destination.replace( '\\', '/' )

                    # print( 'final destination:', final_destination )
                    #
                    result = ''
                    if os.path.isdir( destination_path ):
                        if _dir:
                            if os.path.isdir( final_destination ):
                                pass
                                # self.ui_message( 'Directory already exists --- ' + final_destination )  # need to format properly
                            else:
                                qualified = True
                        else:
                            if  os.path.isfile( os.path.join( destination_path, name ) ):
                                qualified = 'exists'
                            else:
                                qualified = True
                    else:
                        pass
                        # self.ui_message( 'Destination doesnt exist --- ' + destination_path )
                    # print( 'result: ', result )
                else:
                    pass
                    # self.ui_message( 'Source doesnt exist --- ' + source_path )
        else:
            qualified = 'error'
            # self.ui_message( 'Destination doesnt exist --- ' + destination_path )
        return qualified

    def source_file_select( self, source_edit = None ):
        '''
        
        '''
        # path = QtWidgets.QFileDialog.getOpenFileName( self, QtCore.QObject.tr( "Load Image" ), QtCore.QObject.tr( "~/Desktop/" ), QtCore.QObject.tr( "Images (*.jpg)" ) )
        # source_edit.setText( path )
        path = source_edit.text()
        if path:
            path = QtWidgets.QFileDialog.getOpenFileName( None, None, path )
        else:
            path = self.source_default()
            # print( path )
            path = QtWidgets.QFileDialog.getOpenFileName( None, None, path )
        # print( path )
        if path[0]:
            source_edit.setText( path[0] )
        #
        self.ui_message( '' )

    def source_dir_select( self, source_edit = None ):
        '''
        
        '''
        # path = QtWidgets.QFileDialog.getOpenFileName( self, QtCore.QObject.tr( "Load Image" ), QtCore.QObject.tr( "~/Desktop/" ), QtCore.QObject.tr( "Images (*.jpg)" ) )
        # source_edit.setText( path )
        path = source_edit.text()
        if path:
            path = QtWidgets.QFileDialog.getExistingDirectory( None, None, path )
        else:
            path = self.source_default()
            # print( path )
            path = QtWidgets.QFileDialog.getExistingDirectory( None, None, path )
        # print( path )
        if path:
            source_edit.setText( path )
        #
        self.ui_message( '' )

    def source_default( self ):
        '''
        
        '''
        return 'P:\\'

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
        '''
        self.legend_label = QtWidgets.QLabel( 'Legend:  ' )
        self.valid_edit = QtWidgets.QLineEdit( 'path valid' )
        self.valid_edit.setReadOnly( True )
        self.valid_edit.setStyleSheet( "border: 1px solid lightgreen;" )
        self.doesnt_edit = QtWidgets.QLineEdit( 'path invalid' )
        self.doesnt_edit.setReadOnly( True )
        self.doesnt_edit.setStyleSheet( "border: 1px solid red;" )
        self.exists_edit = QtWidgets.QLineEdit( 'path already copied, copying will stop.' )
        self.exists_edit.setReadOnly( True )
        self.exists_edit.setStyleSheet( "border: 1px solid orange;" )
        '''
        #
        self.ontop_layout = QtWidgets.QHBoxLayout()
        #
        '''
        self.ontop_layout.addWidget( self.legend_label )
        self.ontop_layout.addWidget( self.valid_edit )
        self.ontop_layout.addWidget( self.doesnt_edit )
        self.ontop_layout.addWidget( self.exists_edit )
        '''
        #
        self.ontop_layout.addWidget( self.alwaysOnTop_label )
        self.ontop_layout.addWidget( self.alwaysOnTop_check )
        self.ontop_layout.setAlignment( QtCore.Qt.AlignRight )
        #
        self.main_layout.addLayout( self.ontop_layout )
        #
        self.separate_1 = QtWidgets.QFrame()
        self.main_layout.addWidget( self.separate_1 )

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

    def daily_row( self ):
        '''
        
        '''
        #
        self.separate_1 = QtWidgets.QFrame()
        self.main_layout.addWidget( self.separate_1 )
        #
        self.daily_label = QtWidgets.QLabel( 'Create Daily Directory:  ' + todays_directory_name() )
        self.daily_check = QtWidgets.QCheckBox()
        if self.p_d.prefs[self.p_d.daily_check]:
            self.daily_check.setChecked( True )
        else:
            self.daily_check.setChecked( False )
        #
        self.daily_layout = QtWidgets.QHBoxLayout()
        self.daily_layout.setAlignment( QtCore.Qt.AlignRight )
        self.daily_layout.addWidget( self.daily_label )
        self.daily_layout.addWidget( self.daily_check )
        #
        self.main_layout.addLayout( self.daily_layout )

    def copy_row( self ):
        '''
        
        '''
        # copy
        self.copy_button = QtWidgets.QPushButton( "C O P Y" )
        self.copy_idle_color()
        # self.copy_button.setStyleSheet( "background-color: red" )
        self.copy_button.clicked.connect( lambda:self.start_worker_thread() )
        # cancel
        self.quit_button = QtWidgets.QPushButton( "C A N C E L" )
        self.quit_button.clicked.connect( lambda:self.quit_worker_thread() )
        self.quit_button.setDisabled( True )
        # self.quit_button.setStyleSheet( "background-color: red" )
        #
        self.copy_layout = QtWidgets.QHBoxLayout()
        self.copy_layout.addWidget( self.copy_button )
        self.copy_layout.addWidget( self.quit_button )
        #
        self.main_layout.addLayout( self.copy_layout )

    def copy_idle_color( self ):
        '''
        
        '''
        # print( '___idle' )
        pad = str( 3 )
        color = [ 0.192, 0.647, 0.549 ]  # aqua
        open = "QPushButton {"
        bg = "background-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border = "border: 1px solid;"
        padding = "padding-top: " + pad + "px; padding-bottom: " + pad + "px;"
        border_color_top = "border-top-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_left = "border-left-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_right = "border-right-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        border_color_bottom = "border-bottom-color: rgb(" + str( color[0] * 255 ) + "," + str( color[1] * 255 ) + "," + str( color[2] * 255 ) + ");"
        close = "}"
        #
        pressed_color = "QPushButton:pressed{background-color : lightgreen;}"
        hover_color = "QPushButton:hover{background-color : lightgreen;}"
        #
        self.copy_button.setStyleSheet( open + bg + border + padding + border_color_top + border_color_left + border_color_right + border_color_bottom + close + pressed_color + hover_color )  # QtGui.QColor( 1, 0.219, 0.058 )

    def copy_busy_color( self ):
        '''
        
        '''
        # print( '___busy' )
        pad = str( 3 )
        bg = "background-color: lightgreen;"
        border = "border: 1px solid;"
        padding = "padding-top: " + pad + "px; padding-bottom: " + pad + "px;"
        border_color_top = "border-top-color: lightgreen;"
        border_color_left = "border-left-color: lightgreen;"
        border_color_right = "border-right-color: lightgreen;"
        border_color_bottom = "border-bottom-color: lightgreen;"
        self.copy_button.setStyleSheet( bg + border + padding + border_color_top + border_color_left + border_color_right + border_color_bottom )  # QtGui.QColor( 1, 0.219, 0.058 )

    def copy_sources( self ):
        '''
        
        '''
        #
        i = 0
        self.copying = True
        self.ui_message( ' --- Copying Sources --- ' )
        self.qualified_dir = []
        self.qualified_files = []
        self.ui_disable()
        #
        self.copy_busy_color()
        destination_path = self.destination_edit.text()
        # print( 'destination: ', destination_path )
        #
        if os.path.isdir( destination_path ):
            #
            if self.daily_check.isChecked():
                if self.final_directory not in destination_path:
                    destination_path = os.path.join( destination_path, self.final_directory )
                self.make_final_directory( destination_path )
            #
            for source_group in self.sources_ui_list:
                if not self.kill:
                    #
                    source_path = source_group[0].text()
                    if source_path:
                        # print( 'source: ', source_path )
                        go = False
                        _dir = False
                        if os.path.isdir( source_path ):
                            go = True
                            _dir = True
                        elif os.path.isfile( source_path ):
                            go = True
                        if go:
                            #
                            name = ''
                            if '\\' in source_path:
                                name = source_path.split( '\\' )[-1]
                            elif '/' in source_path:
                                name = source_path.split( '/' )[-1]
                            # print( 'name: ', name )
                            #
                            final_destination = os.path.join( destination_path, name )
                            final_destination = final_destination.replace( '\\', '/' )

                            # print( 'final destination:', final_destination )
                            #
                            result = ''
                            if os.path.isdir( destination_path ):
                                if _dir:
                                    if os.path.isdir( final_destination ):
                                        self.ui_message( 'Directory already exists --- ' + final_destination )  # need to format properly
                                        break
                                    else:
                                        result = shutil.copytree( source_path, os.path.join( destination_path, name ), symlinks = True, ignore = None )
                                        self.ui_disable_source( source_group, False )
                                else:
                                    result = shutil.copyfile( source_path, os.path.join( destination_path, name ) )
                                    self.ui_disable_source( source_group, False )
                                i += 1
                            else:
                                self.ui_message( 'Destination doesnt exist --- ' + destination_path )
                            # print( 'result: ', result )
                        else:
                            self.ui_message( 'Source doesnt exist --- ' + source_path )
                else:
                    break
        else:
            self.ui_message( 'Destination doesnt exist --- ' + destination_path )
        #
        processed = 'copied ' + str( i ) + ' sources'
        if self.kill:
            self.ui_message( '--- Canceled, ' + processed + ' ---' )
        else:
            self.ui_message( '--- Finished, ' + processed + ' ---' )
        self.kill = False
        self.copying = False
        self.ui_disable( False )

    def make_final_directory( self, destination_path = '' ):
        '''
        
        '''
        if not os.path.isdir( destination_path ):
            os.mkdir( destination_path )

    def message_row( self ):
        '''
        
        '''
        # message
        self.message_label = QtWidgets.QLabel( 'M E S S A G E  ' )
        self.message_content = QtWidgets.QLabel( '' )

        #
        self.message_layout = QtWidgets.QHBoxLayout()
        self.message_layout.addWidget( self.message_label )
        self.message_layout.addWidget( self.message_content )
        self.message_layout.setAlignment( QtCore.Qt.AlignLeft )
        #
        self.main_layout.addLayout( self.message_layout )

    def ui_message( self, message = '' ):
        '''
        ui feedback
        '''
        self.message_content.setText( message )

    def start_worker_thread( self ):
        '''
        
        '''
        if self.all_valid:
            # Pass the function to execute
            self.worker = Worker( self.copy_sources )  # Any other args, kwargs are passed to the run function
            # worker.signals.result.connect(self.print_output)
            self.worker.signals.finished.connect( self.copy_idle_color )
            # worker.signals.progress.connect(self.progress_fn)

            # Execute
            self.threadpool.start( self.worker )
        else:
            self.ui_message( '--- Resolve conflicts before copying ---' )

    def quit_worker_thread( self ):
        '''
        kill thread, will finish current iteration
        '''
        self.ui_message( ' --- Copying will stop after current source is finished. --- ' )
        self.kill = True

    def start_validation_thread( self ):
        '''
        
        '''
        # Pass the function to execute
        self.v_worker = Worker( self.sources_validation, sources_ui_list = self.sources_ui_list, sources_ui_layouts = self.sources_ui_layouts )  # Any other args, kwargs are passed to the run function
        # Execute
        self.threadpool.start( self.v_worker )

    def sources_validation( self, sources_ui_list = None, sources_ui_layouts = None ):
        '''
        
        '''
        loops = 0
        while self.main_window.validate:
            print( 'loop', loops )
            # sources_ui_list = self.sources_ui_list
            # sources_ui_layouts = self.sources_ui_layouts
            self.all_valid = True
            i = 0
            for source_group in sources_ui_list:
                # print( 'before valid' )
                valid = self.source_validate( source_group[0], sources_ui_layouts[i] )
                if not valid:
                    self.all_valid = False
                # print( 'after valid' )
                i += 1
            # print( 'sleep' )
            time.sleep( 0.1 )

            loops += 1
        print( 'quit' )
        return False

    def ui_disable( self, disable = True ):
        '''
        on copy disable editing
        '''
        if disable:
            self.quit_button.setDisabled( False )
        else:
            self.quit_button.setDisabled( True )
        self.alwaysOnTop_check.setDisabled( disable )
        self.destination_edit.setDisabled( disable )
        self.destination_dir_button.setDisabled( disable )
        self.add_source_button.setDisabled( disable )
        for source_group in self.sources_ui_list:
            for s in source_group:
                s.setDisabled( disable )
        self.daily_check.setDisabled( disable )
        self.copy_button.setDisabled( disable )  # should be replaced with cancel

    def ui_disable_source( self, source_group = [], disable = True ):
        '''
        
        '''
        for s in source_group:
            s.setDisabled( disable )


def source_file_select( source_edit = None ):
    '''
    
    '''
    # path = QtWidgets.QFileDialog.getOpenFileName( self, QtCore.QObject.tr( "Load Image" ), QtCore.QObject.tr( "~/Desktop/" ), QtCore.QObject.tr( "Images (*.jpg)" ) )
    # source_edit.setText( path )
    path = source_edit.text()
    if path:
        path = QtWidgets.QFileDialog.getOpenFileName( None, path )
    else:
        path = source_default()
        print( path )
        path = QtWidgets.QFileDialog.getOpenFileName( None, path )
    print( path )
    source_edit.setText( path[0] )


def source_dir_select( source_edit = None ):
    '''
    
    '''
    # path = QtWidgets.QFileDialog.getOpenFileName( self, QtCore.QObject.tr( "Load Image" ), QtCore.QObject.tr( "~/Desktop/" ), QtCore.QObject.tr( "Images (*.jpg)" ) )
    # source_edit.setText( path )
    path = source_edit.text()
    if path:
        path = QtWidgets.QFileDialog.getExistingDirectory( None, None, path )
    else:
        path = source_default()
        print( path )
        path = QtWidgets.QFileDialog.getExistingDirectory( None, None, path )
    print( path )
    source_edit.setText( path )


def source_default():
    '''
    
    '''
    return 'C:/Users/sebas/__TEST__'


def todays_directory_name():
    '''
    
    '''

    e = datetime.datetime.now()
    name = e.strftime( "%Y_%m_%d" )
    # print ( name )
    return name


def ____THREAD():
    pass


class Worker( QtCore.QRunnable ):

    start = QtCore.Signal( str )
    finished = QtCore.Signal( str )

    def __init__( self, function, *args, **kwargs ):
        super( Worker, self ).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        # self.start.connect( self.run )
        self.signals = WorkerSignals()

    '''
    #QtCore.Slot()
    def run( self, *args, **kwargs ):
        self.function()'''

    @QtCore.Slot()
    def run( self ):
        '''
        Initialize the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.function( *self.args, **self.kwargs )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit( ( exctype, value, traceback.format_exc() ) )
            print( 'exept' )
        else:
            try:
                self.signals.result.emit( result )  # Return the result of the processing
            except:
                print( 'else except' )
        finally:
            try:
                self.signals.finished.emit()  # Done
            except:
                print( 'finally except' )


class WorkerSignals( QtCore.QObject ):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = QtCore.Signal()  # QtCore.Signal
    error = QtCore.Signal( tuple )
    result = QtCore.Signal( object )
    progress = QtCore.Signal( int )


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


def get_color():
    '''
    red = QtGui.QColor( 1, 0.219, 0.058 )
    '''
    green = [ 0.152, 0.627, 0.188 ]
    blue = [ 0.152, 0.403, 0.627 ]
    orange = [ 0.850, 0.474, 0.090 ]
    grey = [ 0.701, 0.690, 0.678 ]
    brown = [ 0.552, 0.403, 0.164 ]
    aqua = [ 0.192, 0.647, 0.549 ]
    #
    c = [aqua]

    color = random.randint( 0, len( c ) - 1 )
    # print( c[color] )
    return c[color]


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
        self.daily_check = 'daily_check'
        self.last_destination = 'last_destination'  # last project set before window was closed
        #
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_pos_x = 'session_window_pos_x'
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_width = 'session_window_width'
        self.session_window_height = 'session_window_height'
        #
        self.prefs = {
            self.on_top: False,
            self.daily_check:True,
            self.last_destination: '',
            self.session_window_pos_x: None,
            self.session_window_pos_y: None,
            self.session_window_width: None,
            self.session_window_height: None,
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
    #
    win = UI()
    #
    p_d = Prefs_dynamic()
    if p_d.prefs[p_d.on_top]:
        win.main_window.setWindowFlags( win.main_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint )
    # move
    centerPoint = QtGui.QGuiApplication.screens()[0].geometry().center()
    #
    if p_d.prefs[p_d.session_window_pos_x]:
        win.main_window.move( p_d.prefs[p_d.session_window_pos_x], p_d.prefs[p_d.session_window_pos_y] )
    else:
        win.main_window.move( centerPoint.x(), centerPoint.y() )
    #
    win.main_window.show()
    sys.exit( app.exec_() )
else:
    pass
