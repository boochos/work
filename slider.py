# Version 1.5
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QDialog, QLabel, QSlider, QHBoxLayout, QVBoxLayout, QPushButton
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

# Initialize the global variable
global custom_dialog

# Constants
UNDO_CHUNK_NAME = 'BlendPose'
DEFAULT_SLIDER_WIDTH = 400
DEFAULT_LABEL_WIDTH = 30
DEFAULT_RANGE = 150.0  # Changed to 80% as per requirement


def cleanup_dialog():
    """
    Safely clean up the existing dialog.
    Returns True if cleanup was successful, False otherwise.
    """
    global custom_dialog
    try:
        if custom_dialog and not custom_dialog.isHidden():
            custom_dialog.close()
        custom_dialog = None
        return True
    except Exception as e:
        print( 'Dialog cleanup error: {0}'.format( e ) )
        custom_dialog = None
        return False


# Clean up on import
cleanup_dialog()


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


class CustomSlider( QSlider ):
    """
    Custom slider widget for blending between animation poses.
    Handles the core functionality of the blend pose tool.
    """

    def __init__( self, parent = None ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )
        self._setup_ui()
        self._connect_signals()
        self.reset_state()

    def _setup_ui( self ):
        """Initialize UI elements and their properties"""
        self.r = DEFAULT_RANGE
        self.setRange( int( self.r * -1 ), int( self.r ) )
        self.setValue( 0 )
        self.setFixedWidth( DEFAULT_SLIDER_WIDTH )
        self.setFixedHeight( 50 )  # Make the slider taller to accommodate the handle

        # Style the slider with a square handle
        self.setStyleSheet( """
            QSlider::handle:horizontal {
                background-color: #673232;
                border: 1px solid #373737;
                width: 26px;
                height: 24px;
                margin: -8px 0;/* Adjust margins to half the handle height */
                border-radius: 4px; /* This rounds the corners */
            }
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                height: 12px;       /* 2px smaller than handle height */
                background: #373737  ;
                margin: 2px 0;
                position: absolute;
                left: 4px;         /* Inset by half handle width */
                right: 4px;        /* Inset by half handle width */
                border-radius: 4px; /* This rounds the corners */
            }
        """ )

        self.label = QLabel( '0%' )
        self.label.setFixedWidth( DEFAULT_LABEL_WIDTH )

    def _connect_signals( self ):
        """Connect Qt signals to their handlers"""
        self.sliderPressed.connect( self.query_selection )
        self.valueChanged.connect( self.adjust_values )
        self.sliderReleased.connect( self.finalize_value )

    def reset_state( self ):
        """Reset all state variables to their default values"""
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = {}
        self.current_time = None
        self.selected_objects = []
        self.new_values = {}
        self.all_curves = []
        self.anim_layers = []
        self.blend_nodes = []  # mark as dirty for proper ui update

    def get_visible_curves( self ):
        """Get all curves visible in graph editor"""
        curves = cmds.keyframe( q = True, name = True, sl = True )
        if curves:
            # print( 'sel curves ', selected_curves )
            return curves

        ge = 'graphEditor1GraphEd'
        ge_exists = cmds.animCurveEditor( ge, exists = True )
        if ge_exists:
            curves = cmds.animCurveEditor( ge, q = True, curvesShown = True )
        # print( 'visible: ', curves )
        return curves

    def get_blend_nodes( self ):
        """Finds blend nodes associated with anim layers in scope"""
        for layer in self.anim_layers:
            # print( layer )
            blends = cmds.animLayer( layer, q = True, blendNodes = True )
            if blends:
                self.blend_nodes.extend( blends )
            else:
                # print( 'no blends' )
                pass
        # print( 'blends', self.blend_nodes )

    # ... [Rest of the CustomSlider class remains the same]
    def query_selection( self ):
        """Query and store the current animation state"""
        # open chunk
        cmds.undoInfo( openChunk = True, cn = UNDO_CHUNK_NAME )

        # get curves
        self.all_curves = self.get_visible_curves()

        if not self.all_curves:
            message( 'No animation curves found', warning = True )
            return

        # initialize
        self.selected_objects = cmds.ls( selection = True )
        self.anim_layers = cmds.ls( type = 'animLayer' )
        self.get_blend_nodes()
        self.current_time = cmds.currentTime( query = True )
        self._initialize_key_values()

        # Process curves and their objects
        # print( self.selected_objects )
        for obj in self.selected_objects:
            self._process_object_curves( obj )

    def _initialize_key_values( self ):
        """Initialize storage dictionaries for key values"""
        self.previous_key_values = {}
        self.next_key_values = {}
        self.initial_values = {}

    def _process_object_curves( self, obj ):
        """
        Process animation curves for a given object.
        Stores previous, current, and next key values.
        Questionable query
        """
        for curve in self.all_curves:
            # Verify curve belongs to current object
            connections = cmds.listHistory( curve, f = True )
            # print( obj, connections )
            if obj not in connections:
                # print( '________out' )
                continue

            current_val = self._get_current_value( curve )
            self._initialize_object_storage( obj )
            self._store_initial_value( obj, curve, current_val )
            self._process_surrounding_keys( obj, curve, current_val )

    def _get_current_value( self, curve ):
        """Get the current value for a given curve"""
        return cmds.keyframe( curve, q = True, eval = True,
                           time = ( self.current_time, self.current_time ) )[0]

    def _initialize_object_storage( self, obj ):
        """Initialize storage dictionaries for an object if needed"""
        if obj not in self.initial_values:
            self.initial_values[obj] = {}
            self.previous_key_values[obj] = {}
            self.next_key_values[obj] = {}

    def _store_initial_value( self, obj, curve, current_val ):
        """Store the initial value for a curve"""
        self.initial_values[obj][curve] = current_val

    def _process_surrounding_keys( self, obj, curve, current_val ):
        """Process and store values for surrounding keyframes"""
        keyframes = cmds.keyframe( curve, query = True, timeChange = True )
        if not keyframes:
            self._store_default_key_values( obj, curve, current_val )
            return

        prev_keys = [key for key in keyframes if key < self.current_time]
        next_keys = [key for key in keyframes if key > self.current_time]

        self._store_prev_key_value( obj, curve, prev_keys, current_val )
        self._store_next_key_value( obj, curve, next_keys, current_val )

    def _store_default_key_values( self, obj, curve, current_val ):
        """Store current value as both previous and next key values"""
        self.previous_key_values[obj][curve] = current_val
        self.next_key_values[obj][curve] = current_val

    def _store_prev_key_value( self, obj, curve, prev_keys, current_val ):
        """Store the value of the previous keyframe"""
        if prev_keys:
            prev_val = cmds.keyframe( curve, q = True,
                                   time = ( prev_keys[-1], prev_keys[-1] ), vc = True )[0]
            self.previous_key_values[obj][curve] = prev_val
        else:
            self.previous_key_values[obj][curve] = current_val

    def _store_next_key_value( self, obj, curve, next_keys, current_val ):
        """Store the value of the next keyframe"""
        if next_keys:
            next_val = cmds.keyframe( curve, q = True,
                                   time = ( next_keys[0], next_keys[0] ), vc = True )[0]
            self.next_key_values[obj][curve] = next_val
        else:
            self.next_key_values[obj][curve] = current_val

    def adjust_values( self, value ):
        """
        Adjust animation values based on slider position.
        Interpolates between previous and next key values.
        """
        # print( 'adjust' )
        if not self.all_curves:
            return

        self.new_values = {}
        for obj in self.selected_objects:
            self._process_object_values( obj, value )

        if self.blend_nodes:
            # print( self.blend_nodes )
            cmds.dgdirty( self.blend_nodes )
            mel.eval( 'dgdirty;' )
        else:
            # print( 'dg' )
            mel.eval( 'dgdirty;' )
        self.label.setText( str( abs( value ) ) + '%' )

    def _process_object_values( self, obj, value ):
        """Process value adjustments for a single object"""
        self.new_values[obj] = {}
        for curve in self.all_curves:
            if curve not in self.initial_values.get( obj, {} ):
                continue

            initial_val = self.initial_values[obj][curve]
            blended_val = self._calculate_blended_value( obj, curve, value, initial_val )

            self.new_values[obj][curve] = blended_val
            cmds.setKeyframe( curve, time = self.current_time, value = blended_val )

    def _calculate_blended_value( self, obj, curve, value, initial_val ):
        """Calculate the blended value based on slider position"""
        # Convert slider value directly to percentage (no normalization needed)
        percentage = value / 100.0  # Direct percentage conversion

        if value >= 0:
            target_val = self.next_key_values.get( obj, {} ).get( curve, initial_val )
            ratio = percentage
        else:
            target_val = self.previous_key_values.get( obj, {} ).get( curve, initial_val )
            ratio = abs( percentage )

        return initial_val * ( 1 - ratio ) + target_val * ratio

    def finalize_value( self ):
        """Reset the slider and clean up the operation"""
        try:
            self._reset_slider()
            self.reset_state()
        finally:
            cmds.undoInfo( closeChunk = True, cn = UNDO_CHUNK_NAME )

    def _reset_slider( self ):
        """Reset slider to initial position"""
        self.valueChanged.disconnect( self.adjust_values )
        self.setValue( 0 )
        self.label.setText( '0%' )
        self.valueChanged.connect( self.adjust_values )


class CustomDialog( QDialog ):
    """Main dialog window for the Blend Pose Tool"""

    def __init__( self, parent = None ):
        super( CustomDialog, self ).__init__( parent )
        self._setup_ui()

    def _setup_ui( self ):
        """Setup the UI layout and widgets"""
        self.setWindowTitle( "Blend Pose Tool" )
        self.setFixedHeight( 70 )

        # Create layout
        layout = QHBoxLayout()
        self.label = QLabel( "Blend Pose" )
        self.slider = CustomSlider()

        # Add widgets to layout
        layout.addWidget( self.label )
        layout.addWidget( self.slider, 0, QtCore.Qt.AlignCenter )
        layout.addWidget( self.slider.label )

        self.setLayout( layout )
        self.adjustSize()


def get_maya_main_window():
    """
    Get Maya's main window as a QWidget.
    Returns the main Maya window wrapped as a QWidget.
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( int( main_window_ptr ), QtWidgets.QWidget )


if __name__ == '__main__':
    pass
else:
    custom_dialog = CustomDialog( get_maya_main_window() )
    custom_dialog.show()
