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
import maya.cmds as cmds
import maya.mel as mel

import webrImport as web
ss = web.mod( "selectionSet_lib" )


def ____UI():
    pass


class CustomQDialog( QtWidgets.QDialog ):
    '''
    
    '''

    def __init__( self ):
        super( CustomQDialog, self ).__init__()
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
        self.daily_check = None
        self.message_content = None
        # self.p = Prefs()
        self.p_d = Prefs_dynamic()
        self.sources_ui_list = []
        self.sources_ui_layouts = []
        # main
        # self.main_window = QtWidgets.QDialog()
        self.main_window = CustomQDialog()  # close event altered

        self.main_window.setWindowTitle( 'Charybdis Tentacle Selection' )
        #
        w = 600
        h = 80
        if self.p_d.prefs[self.p_d.session_window_width]:
            w = int( self.p_d.prefs[self.p_d.session_window_width] )
            # h = int( self.p_d.prefs[self.p_d.session_window_height] )
            self.main_window.resize( w, h )
        else:
            self.main_window.resize( w, h )
        self.main_window.setMaximumWidth( 200 )
        self.main_window.setMaximumHeight( 200 )
        #
        # win.main_window = main_window  # ADD TO CLASS
        # print( main_window )
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_window.setLayout( self.main_layout )
        self.main_layout.setAlignment( QtCore.Qt.AlignTop )
        #
        self.hide_widget = QtWidgets.QWidget()  # widget to hide detail buttons
        if self.p_d.prefs[self.p_d.display_details]:
            self.hide_widget.setVisible( True )
        else:
            self.hide_widget.setVisible( False )
        # self.main_layout.addWidget( self.hide_widget )

        self.add_tantacles_layout = QtWidgets.QHBoxLayout( self.hide_widget )
        self.add_tantacles_layout_l = QtWidgets.QVBoxLayout()
        self.add_tantacles_layout.addLayout( self.add_tantacles_layout_l )
        self.add_tantacles_layout_r = QtWidgets.QVBoxLayout()
        self.add_tantacles_layout.addLayout( self.add_tantacles_layout_r )

        # rows
        self.on_top_row()
        self.namespace_row()
        #
        self.sel_button = QtWidgets.QPushButton( "---    S E L E C T    M E M B E R S    ---" )
        self.sel_button.clicked.connect( lambda:self.select_members() )
        self.sel_button.setStyleSheet( "background-color: grey" )
        self.main_layout.addWidget( self.sel_button )
        #
        self.sel_button = QtWidgets.QPushButton( "---    S E L E C T    G L O B A L S    ---" )
        self.sel_button.clicked.connect( lambda:self.select_globals() )
        self.sel_button.setStyleSheet( "background-color: grey" )
        self.main_layout.addWidget( self.sel_button )
        #
        self.sel_button = QtWidgets.QPushButton( "---    S E L E C T    A L L    ---" )
        self.sel_button.clicked.connect( lambda:self.select_all_tentacles() )
        self.sel_button.setStyleSheet( "background-color: grey" )
        self.main_layout.addWidget( self.sel_button )
        #
        self.geo_button = QtWidgets.QPushButton( "---    G E O    V I S    ---" )
        self.geo_button.clicked.connect( lambda:self.toggle_all_geo() )
        # self.geo_button.setStyleSheet( "background-color: grey" )
        # self.geo_button.setStyleSheet( "background-color: rgb(" + str( color1[0] * 255 ) + "," + str( color1[1] * 255 ) + "," + str( color1[2] * 255 ) + ");" )
        self.main_layout.addWidget( self.geo_button )
        #
        self.vis_button = QtWidgets.QPushButton( "---    C O N T R O L    V I S    ---" )
        self.vis_button.clicked.connect( lambda:self.toggle_all_vis() )
        self.main_layout.addWidget( self.vis_button )
        #
        self.main_layout.addWidget( self.hide_widget )
        #
        self.long_label_l = QtWidgets.QLabel( '______    L O N G    L   ______' )
        self.long_label_l.setStyleSheet( "font-weight: bold" )
        self.long_label_l.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_l.addWidget( self.long_label_l )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle05_geo', vis = 'L_tentacle4_controls' )
        #
        self.med_label_l = QtWidgets.QLabel( '______    M E D I U M    L   ______' )
        self.med_label_l.setStyleSheet( "font-weight: bold" )
        self.med_label_l.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_l.addWidget( self.med_label_l )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle08_geo', vis = 'L_tentacle1_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle07_geo', vis = 'L_tentacle2_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle06_geo', vis = 'L_tentacle3_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle04_geo', vis = 'L_tentacle5_controls' )
        #
        self.short_label_l = QtWidgets.QLabel( '______    S H O R T    L   ______' )
        self.short_label_l.setStyleSheet( "font-weight: bold" )
        self.short_label_l.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_l.addWidget( self.short_label_l )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle01_geo', vis = 'L_tentacle8_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle02_geo', vis = 'L_tentacle7_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_l, geo = 'L_tentacle03_geo', vis = 'L_tentacle6_controls' )
        #
        self.long_label_r = QtWidgets.QLabel( '______    L O N G    R   ______' )
        self.long_label_r.setStyleSheet( "font-weight: bold" )
        self.long_label_r.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_r.addWidget( self.long_label_r )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle05_geo', vis = 'R_tentacle4_controls' )
        #
        self.med_label_r = QtWidgets.QLabel( '______    M E D I U M    R   ______' )
        self.med_label_r.setStyleSheet( "font-weight: bold" )
        self.med_label_r.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_r.addWidget( self.med_label_r )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle08_geo', vis = 'R_tentacle1_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle07_geo', vis = 'R_tentacle2_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle06_geo', vis = 'R_tentacle3_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle04_geo', vis = 'R_tentacle5_controls' )
        #
        self.short_label_r = QtWidgets.QLabel( '______    S H O R T    R   ______' )
        self.short_label_r.setStyleSheet( "font-weight: bold" )
        self.short_label_r.setAlignment( QtCore.Qt.AlignCenter )
        self.add_tantacles_layout_r.addWidget( self.short_label_r )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle01_geo', vis = 'R_tentacle8_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle02_geo', vis = 'R_tentacle7_controls' )
        self.tantacle_row( layout = self.add_tantacles_layout_r, side = 'r', geo = 'R_tentacle03_geo', vis = 'R_tentacle6_controls' )
        #
        # self.message_row()
        #

    def namespace_row( self ):
        '''
        
        '''
        #
        self.namespace_label = QtWidgets.QLabel( 'Namespace:  ' )
        self.namespace_label.setMaximumWidth( 80 )
        self.namespace_combo = QtWidgets.QComboBox()  # self.p_d.prefs[self.p_d.last_destination]
        ns = cmds.namespaceInfo( listOnlyNamespaces = True, recurse = True )
        blacklist = ['UI', 'shared']
        for n in ns:
            if n not in blacklist:
                self.namespace_combo.addItems( [n] )
        #
        self.namespace_layout = QtWidgets.QHBoxLayout()
        # self.namespace_layout.setAlignment( QtCore.Qt.AlignLeft )
        self.namespace_layout.addWidget( self.namespace_label )
        self.namespace_layout.addWidget( self.namespace_combo )
        #
        self.main_layout.addLayout( self.namespace_layout )
        #
        self.separate_0 = QtWidgets.QFrame()
        self.main_layout.addWidget( self.separate_0 )

    def tantacle_row( self, layout = None, side = 'l', geo = '', vis = '' ):
        '''
        geo = attr name
        vis = attr name
        
        name variations = [
        'body01:L_tentacle1_broadTwist2_ctrl',
        'body01:L_tentacle1_sub9Offset_ctrl',
        'body01:L_tentacle1_sub9_ctrl',
        'body01:L_tentacle1_4Offset_ctrl',
        'body01:L_tentacle1_4_ctrl'
        ]
        '''
        #
        s = 30
        if side == 'l':
            color1 = [ 0.152, 0.403, 0.627 ]  # blue
        else:
            color1 = [0.65, 0.2, 0.2 ]  # red
        color2 = [0.22, 0.22, 0.22 ]
        #
        name = vis.replace( 'controls', 'global_ctrl' )
        button_name = vis.split( '_' )[1]
        button_name = add_space( button_name )
        #
        tentacle_layout = QtWidgets.QVBoxLayout()  # main
        layout.addLayout( tentacle_layout )
        #
        geo_button = QtWidgets.QPushButton( button_name )
        geo_button.setStyleSheet( "font-weight: bold;" )
        geo_button.clicked.connect( lambda:self.toggle_geo( geo ) )
        # geo_button.setStyleSheet( "font-weight: bold;background-color: rgb(" + str( color2[0] * 255 ) + "," + str( color2[1] * 255 ) + "," + str( color2[2] * 255 ) + ");" )
        tentacle_layout.addWidget( geo_button )
        #
        tentacle_sel_layout = QtWidgets.QHBoxLayout()  # selection layout
        tentacle_layout.addLayout( tentacle_sel_layout )
        #
        all_sel_button = QtWidgets.QPushButton( "S e l" )
        all_sel_button.setStyleSheet( "background-color: rgb(" + str( color1[0] * 255 ) + "," + str( color1[1] * 255 ) + "," + str( color1[2] * 255 ) + ");" )
        all_sel_button.clicked.connect( lambda:self.select_entire_tentacle( vis ) )
        #
        layer1_button = QtWidgets.QPushButton( "S" )
        layer1_button.clicked.connect( lambda:self.select_main( name = vis ) )
        layer1_button.setMaximumWidth( s )
        layer1_button.setMinimumWidth( s )
        layer2_button = QtWidgets.QPushButton( "S" )
        layer2_button.clicked.connect( lambda:self.select_mainOffset( name = vis ) )
        layer2_button.setMaximumWidth( s )
        layer2_button.setMinimumWidth( s )
        layer3_button = QtWidgets.QPushButton( "S" )
        layer3_button.clicked.connect( lambda:self.select_sub( name = vis ) )
        layer3_button.setMaximumWidth( s )
        layer3_button.setMinimumWidth( s )
        layer4_button = QtWidgets.QPushButton( "S" )
        layer4_button.clicked.connect( lambda:self.select_subOffset( name = vis ) )
        layer4_button.setMaximumWidth( s )
        layer4_button.setMinimumWidth( s )

        tentacle_sel_layout.addWidget( all_sel_button )
        tentacle_sel_layout.addWidget( layer1_button )
        tentacle_sel_layout.addWidget( layer2_button )
        tentacle_sel_layout.addWidget( layer3_button )
        tentacle_sel_layout.addWidget( layer4_button )
        #

        tentacle_sel_layout = QtWidgets.QHBoxLayout()  # selection layout
        tentacle_layout.addLayout( tentacle_sel_layout )
        #
        all_vis_button = QtWidgets.QPushButton( "V i s" )
        all_vis_button.setStyleSheet( "background-color: rgb(" + str( color1[0] * 255 ) + "," + str( color1[1] * 255 ) + "," + str( color1[2] * 255 ) + ");" )
        all_vis_button.clicked.connect( lambda:self.toggle_vis( vis ) )
        #
        layer1_button = QtWidgets.QPushButton( "V" )
        layer1_button.clicked.connect( lambda:self.toggle_main_vis( name ) )
        layer1_button.setMaximumWidth( s )
        layer1_button.setMinimumWidth( s )
        layer2_button = QtWidgets.QPushButton( "V" )
        layer2_button.clicked.connect( lambda:self.toggle_mainOffset_vis( name ) )
        layer2_button.setMaximumWidth( s )
        layer2_button.setMinimumWidth( s )
        layer3_button = QtWidgets.QPushButton( "V" )
        layer3_button.clicked.connect( lambda:self.toggle_sub_vis( name ) )
        layer3_button.setMaximumWidth( s )
        layer3_button.setMinimumWidth( s )
        layer4_button = QtWidgets.QPushButton( "V" )
        layer4_button.clicked.connect( lambda:self.toggle_subOffset_vis( name ) )
        layer4_button.setMaximumWidth( s )
        layer4_button.setMinimumWidth( s )

        tentacle_sel_layout.addWidget( all_vis_button )
        tentacle_sel_layout.addWidget( layer1_button )
        tentacle_sel_layout.addWidget( layer2_button )
        tentacle_sel_layout.addWidget( layer3_button )
        tentacle_sel_layout.addWidget( layer4_button )
        #
        # separate_0 = QtWidgets.QFrame()
        # tentacle_layout.addWidget( separate_0 )

    def on_top_row( self ):
        '''
        
        '''
        # on top
        self.alwaysOnTop_label = QtWidgets.QLabel( '       Always On Top:  ' )
        self.alwaysOnTop_check = QtWidgets.QCheckBox()
        if self.p_d.prefs[self.p_d.on_top]:
            self.alwaysOnTop_check.setChecked( True )
        else:
            self.alwaysOnTop_check.setChecked( False )
        self.alwaysOnTop_check.clicked.connect( lambda:self.onTopToggle_ui() )
        #
        self.detail_label = QtWidgets.QLabel( 'Display Details:  ' )
        self.detail_check = QtWidgets.QCheckBox()
        if self.p_d.prefs[self.p_d.display_details]:
            self.detail_check.setChecked( True )
        else:
            self.detail_check.setChecked( False )
        self.detail_check.clicked.connect( lambda:self.toggle_details() )
        #
        self.check_layout = QtWidgets.QHBoxLayout()
        self.details_layout = QtWidgets.QHBoxLayout()
        self.check_layout.addLayout( self.details_layout )
        self.ontop_layout = QtWidgets.QHBoxLayout()
        self.check_layout.addLayout( self.ontop_layout )
        #
        self.details_layout.addWidget( self.detail_label )
        self.details_layout.addWidget( self.detail_check )
        self.details_layout.setAlignment( QtCore.Qt.AlignLeft )
        #
        self.ontop_layout.addWidget( self.alwaysOnTop_label )
        self.ontop_layout.addWidget( self.alwaysOnTop_check )
        self.ontop_layout.setAlignment( QtCore.Qt.AlignRight )
        #
        self.main_layout.addLayout( self.check_layout )
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

    def ui_message( self, message = '', color = '' ):
        '''
        ui feedback
        '''
        if color:
            self.message_content.setStyleSheet( "color:  " + color + "; font-weight: bold" )
        else:
            self.message_content.setStyleSheet( "color:  gray;" )
        self.message_content.setText( message )
        print( message )

    def toggle_details( self ):
        if self.detail_check.isChecked():
            self.hide_widget.setVisible( True )
            # self.main_window.setMaximumWidth( 400 )
            # self.main_window.setMaximumHeight( 650 )
        else:
            self.hide_widget.setVisible( False )
            # self.main_window.setMaximumWidth( 300 )
            # self.main_window.setMaximumHeight( 210 )

        p = Prefs_dynamic()
        p.prefs[p.display_details] = self.detail_check.isChecked()
        p.prefSave()

    def __VIS( self ):
        pass

    def toggle_geo( self, attr = '' ):
        '''
        
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':preferences.' + attr
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_all_geo( self ):
        '''
        R_tentacle01_geo
        '''
        #
        ns = self.namespace_combo.currentText()
        sides = ['L', 'R']
        attr_pre = '_tentacle0'
        attr_post = '_geo'
        i = 1
        # status
        status = cmds.getAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post )
        #
        # return
        while i <= 8:
            if status:
                cmds.setAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post, 0 )
                cmds.setAttr( ns + ':preferences.' + sides[1] + attr_pre + str( i ) + attr_post, 0 )
            else:
                cmds.setAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post, 1 )
                cmds.setAttr( ns + ':preferences.' + sides[1] + attr_pre + str( i ) + attr_post, 1 )
            i += 1

    def toggle_vis( self, attr = '' ):
        '''
        
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':preferences.' + attr
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_all_vis( self ):
        '''
        L_tentacle1_controls
        '''
        #
        ns = self.namespace_combo.currentText()
        sides = ['L', 'R']
        attr_pre = '_tentacle'
        attr_post = '_controls'
        i = 1
        # status
        status = cmds.getAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post )
        #
        # return
        while i <= 8:
            if status:
                cmds.setAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post, 0 )
                cmds.setAttr( ns + ':preferences.' + sides[1] + attr_pre + str( i ) + attr_post, 0 )
            else:
                cmds.setAttr( ns + ':preferences.' + sides[0] + attr_pre + str( i ) + attr_post, 1 )
                cmds.setAttr( ns + ':preferences.' + sides[1] + attr_pre + str( i ) + attr_post, 1 )
            i += 1

    def toggle_main_vis( self, name = '' ):
        '''
        L_tentacle1_global_ctrl
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':' + name + '.mainControlVisibility'
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_mainOffset_vis( self, name = '' ):
        '''
        L_tentacle1_global_ctrl
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':' + name + '.mainOffsetControlVisibility'
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_sub_vis( self, name = '' ):
        '''
        L_tentacle1_global_ctrl
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':' + name + '.subControlVisibility'
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_subOffset_vis( self, name = '' ):
        '''
        L_tentacle1_global_ctrl
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':' + name + '.subOffsetControlVisibility'
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def toggle_twist_vis( self, name = '' ):
        '''
        L_tentacle1_global_ctrl
        '''
        ns = self.namespace_combo.currentText()
        item = ns + ':' + name + '.broadTwistControlVisibility'
        if cmds.getAttr( item ):
            cmds.setAttr( item, 0 )
        else:
            cmds.setAttr( item, 1 )

    def __SEL( self ):
        pass

    def select_main( self, name = '' ):
        '''
        name = 'R_tentacle1_controls'
        #
        name variations = [
        'body01:L_tentacle1_4_ctrl'
        ]
        '''
        controls = []
        ns = self.namespace_combo.currentText()
        prefix = name.split( 'controls' )[0]
        i = 0
        go = True
        #
        while go and i < 20:
            control = ns + ':' + prefix + str( i ) + '_ctrl'
            print( control )
            if cmds.objExists( control ):
                controls.append( control )
            else:
                go = False
            i += 1
        #
        cmds.select( controls, add = True )

    def select_mainOffset( self, name = '' ):
        '''
        name = 'R_tentacle1_controls'
        #
        name variations = [
        'body01:L_tentacle1_4Offset_ctrl'
        ]
        '''
        controls = []
        ns = self.namespace_combo.currentText()
        prefix = name.split( 'controls' )[0]
        i = 0
        go = True
        #
        while go and i < 20:
            control = ns + ':' + prefix + str( i ) + 'Offset_ctrl'
            print( control )
            if cmds.objExists( control ):
                controls.append( control )
            else:
                go = False
            i += 1
        #
        cmds.select( controls, add = True )

    def select_sub( self, name = '' ):
        '''
        name = 'R_tentacle1_controls'
        #
        name variations = [
        'body01:L_tentacle1_sub9_ctrl',
        ]
        '''
        controls = []
        ns = self.namespace_combo.currentText()
        prefix = name.split( 'controls' )[0]
        i = 0
        go = True
        #
        while go and i < 20:
            control = ns + ':' + prefix + 'sub' + str( i ) + '_ctrl'
            print( control )
            if cmds.objExists( control ):
                controls.append( control )
            else:
                go = False
            i += 1
        #
        cmds.select( controls, add = True )

    def select_subOffset( self, name = '' ):
        '''
        name = 'R_tentacle1_controls'
        #
        name variations = [
        'body01:L_tentacle1_sub9Offset_ctrl',
        ]
        '''
        controls = []
        ns = self.namespace_combo.currentText()
        prefix = name.split( 'controls' )[0]
        i = 0
        go = True
        #
        while go and i < 20:
            control = ns + ':' + prefix + 'sub' + str( i ) + 'Offset_ctrl'
            print( control )
            if cmds.objExists( control ):
                controls.append( control )
            else:
                go = False
            i += 1
        #
        cmds.select( controls, add = True )

    def select_globals( self ):
        '''
        all lolypop controls / globals
        '''
        ns = self.namespace_combo.currentText()
        controls = [
        ns + ':R_tentacle4_global_ctrl',
        ns + ':L_tentacle1_global_ctrl',
        ns + ':R_tentacle5_global_ctrl',
        ns + ':L_tentacle4_global_ctrl',
        ns + ':R_tentacle3_global_ctrl',
        ns + ':R_tentacle1_global_ctrl',
        ns + ':L_tentacle6_global_ctrl',
        ns + ':R_tentacle6_global_ctrl',
        ns + ':R_tentacle7_global_ctrl',
        ns + ':L_tentacle3_global_ctrl',
        ns + ':R_tentacle2_global_ctrl',
        ns + ':L_tentacle5_global_ctrl',
        ns + ':R_tentacle8_global_ctrl',
        ns + ':L_tentacle7_global_ctrl',
        ns + ':L_tentacle8_global_ctrl',
        ns + ':L_tentacle2_global_ctrl'
        ]
        cmds.select( controls, add = True )

    def select_members( self ):
        '''
        
        '''
        ss.selectSet()

    def select_entire_tentacle( self, name = '' ):
        '''
        name = L_tentacle1_controls
        '''
        #
        ns = self.namespace_combo.currentText()
        sel_sets = []
        tnt = int( name[10:11] )
        side = name[0]
        print( tnt, side )
        #
        if tnt == 1:
            if side == 'L':
                sel_sets = set_l_tnt_1()
            else:
                sel_sets = set_r_tnt_1()
        if tnt == 2:
            if side == 'L':
                sel_sets = set_l_tnt_2()
            else:
                sel_sets = set_r_tnt_2()
        if tnt == 3:
            if side == 'L':
                sel_sets = set_l_tnt_3()
            else:
                sel_sets = set_r_tnt_3()
        if tnt == 4:
            if side == 'L':
                sel_sets = set_l_tnt_4()
            else:
                sel_sets = set_r_tnt_4()
        if tnt == 5:
            if side == 'L':
                sel_sets = set_l_tnt_5()
            else:
                sel_sets = set_r_tnt_5()
        if tnt == 6:
            if side == 'L':
                sel_sets = set_l_tnt_6()
            else:
                sel_sets = set_r_tnt_6()
        if tnt == 7:
            if side == 'L':
                sel_sets = set_l_tnt_7()
            else:
                sel_sets = set_r_tnt_7()
        if tnt == 8:
            if side == 'L':
                sel_sets = set_l_tnt_8()
            else:
                sel_sets = set_r_tnt_8()
        #
        ss.selectExplicitSet( sets = sel_sets, ns = ns )

    def select_all_tentacles( self ):
        '''
        
        '''
        ns = self.namespace_combo.currentText()
        sel_sets = set_all()
        #
        ss.selectExplicitSet( sets = sel_sets, ns = ns )


def ____ACTION():
    pass


def toggle_geo( combo_box = None, attr = '' ):
    '''
    
    '''
    ns = combo_box.currentText()
    item = ns + ':' + attr
    if cmds.getAttr( item ):
        cmds.setAttr( ns + ':' + attr, 0 )
    else:
        cmds.setAttr( ns + ':' + attr, 0 )


def add_space( name = '' ):
    '''
    add space between letters. return
    '''
    i = 0
    last = len( name )
    # print( last )
    spaced = ''
    for n in name:
        print( i )
        if i != 0:
            if i == last - 1:
                print( 'here' )
                spaced = spaced + '   ' + n
            else:
                spaced = spaced + ' ' + n
        else:
            spaced = n
        i += 1
        # print( i )
    return spaced.upper()


def ____PREFS():
    pass


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
    c = [ aqua]

    color = random.randint( 0, len( c ) - 1 )
    # print( c[color] )
    return c[color]


class Prefs_dynamic():
    '''
    
    '''

    def __init__( self, *args ):
        '''
        prefs that are persistent next time ui starts.
        '''
        self.on_top = 'on_top'
        #
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_pos_x = 'session_window_pos_x'
        self.session_window_pos_y = 'session_window_pos_y'
        self.session_window_width = 'session_window_width'
        self.session_window_height = 'session_window_height'
        self.display_details = 'display_details'
        #
        self.prefs = {
            self.on_top: False,
            self.session_window_pos_x: None,
            self.session_window_pos_y: None,
            self.session_window_width: None,
            self.session_window_height: None,
            self.display_details: False,
        }
        #
        self.prefLoad()

    def prefFileName( self ):
        return 'dnegCharybdisTentacleDynamicPrefs.json'

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
                            # print( key, prefs_temp[key] )
                        else:
                            pass
                            # message( 'Missing attribute in file. Skipping: ' + key, warning = 1 )
        else:
            self.prefSave()


def ____SETS_L():
    pass


def set_l_tnt_1():
    return [u'l_tnt_1_main', u'l_tnt_1_mainOffset', u'l_tnt_1_sub', u'l_tnt_1_subOffset', u'l_tnt_1_twst', u'l_tnt_1_globals']


def set_l_tnt_2():
    return [u'l_tnt_2_main', u'l_tnt_2_mainOffset', u'l_tnt_2_sub', u'l_tnt_2_subOffset', u'l_tnt_2_twst', u'l_tnt_2_globals']


def set_l_tnt_3():
    return [u'l_tnt_3_main', u'l_tnt_3_mainOffset', u'l_tnt_3_sub', u'l_tnt_3_subOffset', u'l_tnt_3_twst', u'l_tnt_3_globals']


def set_l_tnt_4():
    return [u'l_tnt_4_main', u'l_tnt_4_mainOffset', u'l_tnt_4_sub', u'l_tnt_4_subOffset', u'l_tnt_4_twst', u'l_tnt_4_globals']


def set_l_tnt_5():
    return [u'l_tnt_5_main', u'l_tnt_5_mainOffset', u'l_tnt_5_sub', u'l_tnt_5_subOffset', u'l_tnt_5_twst', u'l_tnt_5_globals']


def set_l_tnt_6():
    return [u'l_tnt_6_main', u'l_tnt_6_mainOffset', u'l_tnt_6_sub', u'l_tnt_6_subOffset', u'l_tnt_6_twst', u'l_tnt_6_globals']


def set_l_tnt_7():
    return [u'l_tnt_7_main', u'l_tnt_7_mainOffset', u'l_tnt_7_sub', u'l_tnt_7_subOffset', u'l_tnt_7_twst', u'l_tnt_7_globals']


def set_l_tnt_8():
    return [u'l_tnt_8_main', u'l_tnt_8_mainOffset', u'l_tnt_8_sub', u'l_tnt_8_subOffset', u'l_tnt_8_twst', u'l_tnt_8_globals']


def ____SETS_R():
    pass


def set_r_tnt_1():
    return [u'r_tnt_1_main', u'r_tnt_1_mainOffset', u'r_tnt_1_sub', u'r_tnt_1_subOffset', u'r_tnt_1_twst', u'r_tnt_1_globals']


def set_r_tnt_2():
    return [u'r_tnt_2_main', u'r_tnt_2_mainOffset', u'r_tnt_2_sub', u'r_tnt_2_subOffset', u'r_tnt_2_twst', u'r_tnt_2_globals']


def set_r_tnt_3():
    return [u'r_tnt_3_main', u'r_tnt_3_mainOffset', u'r_tnt_3_sub', u'r_tnt_3_subOffset', u'r_tnt_3_twst', u'r_tnt_3_globals']


def set_r_tnt_4():
    return [u'r_tnt_4_main', u'r_tnt_4_mainOffset', u'r_tnt_4_sub', u'r_tnt_4_subOffset', u'r_tnt_4_twst', u'r_tnt_4_globals']


def set_r_tnt_5():
    return [u'r_tnt_5_main', u'r_tnt_5_mainOffset', u'r_tnt_5_sub', u'r_tnt_5_subOffset', u'r_tnt_5_twst', u'r_tnt_5_globals']


def set_r_tnt_6():
    return [u'r_tnt_6_main', u'r_tnt_6_mainOffset', u'r_tnt_6_sub', u'r_tnt_6_subOffset', u'r_tnt_6_twst', u'r_tnt_6_globals']


def set_r_tnt_7():
    return [u'r_tnt_7_main', u'r_tnt_7_mainOffset', u'r_tnt_7_sub', u'r_tnt_7_subOffset', u'r_tnt_7_twst', u'r_tnt_7_globals']


def set_r_tnt_8():
    return [u'r_tnt_8_main', u'r_tnt_8_mainOffset', u'r_tnt_8_sub', u'r_tnt_8_subOffset', u'r_tnt_8_twst', u'r_tnt_8_globals']


def ____SETS_GROUPS():
    pass


def set_globals():
    return [u'tnt_global']


def set_globalsOffset():
    return [u'tnt_globalOffset']


def set_all():
    '''
    select every tenticle control
    '''
    all = []
    #
    # all.append( set_globals()[0] )
    # all.append( set_globalsOffset()[0] )
    # L
    for i in set_l_tnt_1():
        all.append( i )
    for i in set_l_tnt_2():
        all.append( i )
    for i in set_l_tnt_3():
        all.append( i )
    for i in set_l_tnt_4():
        all.append( i )
    for i in set_l_tnt_5():
        all.append( i )
    for i in set_l_tnt_6():
        all.append( i )
    for i in set_l_tnt_7():
        all.append( i )
    for i in set_l_tnt_8():
        all.append( i )
    # R
    for i in set_r_tnt_1():
        all.append( i )
    for i in set_r_tnt_2():
        all.append( i )
    for i in set_r_tnt_3():
        all.append( i )
    for i in set_r_tnt_4():
        all.append( i )
    for i in set_r_tnt_5():
        all.append( i )
    for i in set_r_tnt_6():
        all.append( i )
    for i in set_r_tnt_7():
        all.append( i )
    for i in set_r_tnt_8():
        all.append( i )
    return all


# n = UI()
if __name__ == '__main__':
    # n = UI()
    # n.main_window.show()


    '''
    app = QtWidgets.QApplication( sys.argv )
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
    sys.exit( app.exec_() )'''


else:


    app = QtWidgets.QApplication.instance()
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
    app.exec_()

'''
import imp
import dnegTentacleSelection as dts
imp.reload(dts)
    '''
