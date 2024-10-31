# Version 1.5
import json
import os
import platform

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, QPoint
from PySide2.QtWidgets import ( QDialog, QLabel, QSlider, QHBoxLayout, QVBoxLayout,
                              QPushButton, QRadioButton, QButtonGroup, QGroupBox )
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

# Initialize the global variable
global custom_dialog


def get_default_width_txt():
    return 'XL'


def get_default_range_txt():
    return '150'


# Constants
TOOL_NAME = 'Blend_N'
DEFAULT_RANGE_WIDTH_TXT = get_default_width_txt()
DEFAULT_SLIDER_WIDTH = {
    'S': 100,
    'M': 200,
    'L': 300,
    DEFAULT_RANGE_WIDTH_TXT: 400  # default
}

DEFAULT_RANGE = {
    '100': 100,
    '150': 150,  # default
    '200': 200
}


def get_default_width():
    return DEFAULT_SLIDER_WIDTH['XL']


def get_default_range():
    return DEFAULT_RANGE['150']


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


class HandleLabel( QLabel ):
    """Custom label that follows the slider handle"""

    def __init__( self, parent = None ):
        super( HandleLabel, self ).__init__( parent )
        self.setAlignment( Qt.AlignCenter )
        self.setFixedWidth( 40 )
        self.setStyleSheet( """
            QLabel {
                color: white;
                background-color: transparent;
                padding: 2px;
                font-weight: bold;
                font-size: 12px;
                border: 0px solid #333333;
                border-radius: 2px;
            }
        """ )


class CustomSlider( QSlider ):
    """
    Custom slider widget for blending between animation poses.
    Handles the core functionality of the blend pose tool.
    """
    # Class variables for color transition points and colors
    NEGATIVE_THRESHOLD = -101  # Point where negative red zone starts
    POSITIVE_THRESHOLD = 101  # Point where positive red zone starts
    LOCK_RELEASE_MARGIN = 15  # Percentage beyond threshold needed to release lock

    # groove
    COLOR_GROOVE_NEUTRAL = "#373737"  # Gray middle zone 373737
    COLOR_GROOVE_WARNING = "#453939"  # Red outer zones 673232 8B4343
    # handle
    COLOR_HANDLE_NORMAL = "#8B4343"  # Handle color within threshold
    COLOR_HANDLE_WARNING = "#E54C4C"  # Handle color beyond threshold E54C4C FF4444
    COLOR_HANDLE_BORDER_HOVER = "#B24949"  # handle
    COLOR_HANDLE_DISABLED = '#444444'  # Maya grey for disabled state
    # border
    COLOR_BORDER_NEUTRAL = '#1a1a1a'
    COLOR_BORDER_DISABLED = '#1a1a1a'  # Darker grey for disabled border

    def __init__( self, parent = None, theme = 'green' ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )
        self._is_disabled = False  # Add state tracking
        # self.theme = theme
        self.set_theme( theme )
        self._setup_ui()
        self._connect_signals()
        self.reset_state()

        # Lock state tracking
        self._positive_locked = False
        self._negative_locked = False
        self._lock_released = False
        self._soft_release = False

        # Create and setup the handle label
        self.handle_label = HandleLabel( self )
        self.handle_label.setText( '0' )
        self.handle_label.hide()  # Initially hide the label

        # Update handle label position whenever the slider value changes
        self.valueChanged.connect( self._update_handle_label_position )

        # Add mouse tracking to handle groove clicks
        self.setMouseTracking( True )

        # Initialize click timer
        self._click_timer = QtCore.QTimer( self )
        self._click_timer.timeout.connect( self._handle_repeat_click )
        self._click_direction = 0  # Store click direction (1 for right, -1 for left)
        self._is_groove_click = False
        # print( self.COLOR_HANDLE_DISABLED )

    def __UI__( self ):
        pass

    def set_threshold( self, negative, positive ):
        """Set new threshold values and update the slider"""
        self.NEGATIVE_THRESHOLD = negative
        self.POSITIVE_THRESHOLD = positive
        self._update_stylesheet()

    def setRange( self, minimum, maximum ):
        """Override setRange to update gradient when range changes"""
        super( CustomSlider, self ).setRange( minimum, maximum )
        self._update_stylesheet()

    def _update_handle_label_position( self ):
        """Update the position of the handle label to follow the slider handle"""
        if not self.handle_label.isVisible():
            self.handle_label.show()

        # Calculate handle position
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption( opt )
        handle_rect = self.style().subControlRect( QtWidgets.QStyle.CC_Slider, opt,
                                                QtWidgets.QStyle.SC_SliderHandle, self )

        # Position label centered over handle
        label_x = handle_rect.center().x() - self.handle_label.width() // 2
        label_y = handle_rect.center().y() - self.handle_label.height() // 2  # Center on handle

        # Update label position
        self.handle_label.move( label_x, label_y )
        self.handle_label.setText( '{0}'.format( abs( self.value() ) ) )

    def _connect_signals( self ):
        """Connect Qt signals to their handlers"""
        self.sliderPressed.connect( self.on_handle_press )
        self.valueChanged.connect( self.on_handle_move )
        self.sliderReleased.connect( self.on_handle_release )

    def _setup_ui( self ):
        """Initialize UI elements and their properties"""
        self.r = DEFAULT_RANGE['150']
        self.setRange( int( self.r * -1 ), int( self.r ) )
        self.setValue( 0 )
        self.setFixedWidth( DEFAULT_SLIDER_WIDTH[DEFAULT_RANGE_WIDTH_TXT] )  # Updated to use simple dict access
        self.setFixedHeight( 50 )

        self._update_stylesheet()

        # Connect valueChanged to update handle color
        self.valueChanged.connect( self._handle_value_change )
        self.valueChanged.connect( self._check_threshold_locks )

    def _check_threshold_locks( self, value ):
        """
        Handle threshold locking behavior
        """
        if self._lock_released:
            # print( 'released' )
            return

        # Check positive threshold
        if value >= self.POSITIVE_THRESHOLD - 1:
            if not self._positive_locked:
                # Engage lock at threshold
                self._positive_locked = True
                self.setValue( self.POSITIVE_THRESHOLD - 1 )
            elif value >= self.POSITIVE_THRESHOLD + self.LOCK_RELEASE_MARGIN:
                # Release lock if we've moved past release point
                self._positive_locked = False
                self._lock_released = True
            elif self._positive_locked:
                # Keep value at threshold while locked
                self.setValue( self.POSITIVE_THRESHOLD - 1 )
        # Check negative threshold
        elif value <= self.NEGATIVE_THRESHOLD + 1:
            if not self._negative_locked:
                # Engage lock at threshold
                self._negative_locked = True
                self.setValue( self.NEGATIVE_THRESHOLD + 1 )
            elif value <= self.NEGATIVE_THRESHOLD - self.LOCK_RELEASE_MARGIN:
                # Release lock if we've moved past release point
                self._negative_locked = False
                self._lock_released = True
            elif self._negative_locked:
                # Keep value at threshold while locked
                self.setValue( self.NEGATIVE_THRESHOLD + 1 )
        # print( 'check: ', self.value() )

    def _handle_value_change( self, value ):
        """Update handle color when value changes"""
        self._update_stylesheet( value )
        self.handle_label.setText( '{0}'.format( abs( value ) ) )

    def _calculate_gradient_stops( self ):
        """Calculate gradient stops based on current range"""
        total_range = self.maximum() - self.minimum()
        if total_range == 0:
            return "stop:0 {0}, stop:1 {0}".format( self.COLOR_GROOVE_NEUTRAL )

        # Convert the threshold points to percentages of the total range
        min_red_stop = ( self.NEGATIVE_THRESHOLD - self.minimum() ) / float( total_range )
        max_red_start = ( self.POSITIVE_THRESHOLD - self.minimum() ) / float( total_range )

        # Ensure stops are within 0-1 range
        min_red_stop = max( 0, min( min_red_stop, 1 ) )
        max_red_start = max( 0, min( max_red_start, 1 ) )

        # Build gradient stops
        stops = []

        # Add red zone for negative values if in range
        if self.minimum() <= self.NEGATIVE_THRESHOLD:
            stops.extend( [
                "stop:0 {0}".format( self.COLOR_GROOVE_WARNING ),
                "stop:{0} {1}".format( min_red_stop, self.COLOR_GROOVE_WARNING ),
                "stop:{0} {1}".format( min_red_stop + 0.001, self.COLOR_GROOVE_NEUTRAL )
            ] )
        else:
            stops.append( "stop:0 {0}".format( self.COLOR_GROOVE_NEUTRAL ) )

        # Add red zone for positive values if in range
        if self.maximum() >= self.POSITIVE_THRESHOLD:
            stops.extend( [
                "stop:{0} {1}".format( max_red_start - 0.001, self.COLOR_GROOVE_NEUTRAL ),
                "stop:{0} {1}".format( max_red_start, self.COLOR_GROOVE_WARNING ),
                "stop:1 {0}".format( self.COLOR_GROOVE_WARNING )
            ] )
        else:
            stops.append( "stop:1 {0}".format( self.COLOR_GROOVE_NEUTRAL ) )

        return ", ".join( stops )

    def __COLOUR__( self ):
        pass

    def set_theme( self, theme = '' ):
        """Update the slider's theme and refresh the UI"""
        self._setup_theme( theme )
        self._update_stylesheet()

    def set_colors( self, neutral = "#343434", warning = "#8B4343", handle_normal = "#673232", handle_warning = "#FF4444", handle_hover = "#B24949", border = '#1a1a1a' ):
        """Set new colors and update the slider"""
        self.COLOR_GROOVE_NEUTRAL = neutral
        self.COLOR_GROOVE_WARNING = warning
        self.COLOR_HANDLE_NORMAL = handle_normal
        self.COLOR_HANDLE_WARNING = handle_warning
        self.COLOR_HANDLE_BORDER_HOVER = handle_hover
        self.COLOR_BORDER_NEUTRAL = border
        self._update_stylesheet()

    def _setup_theme( self, theme = 'blue' ):
        """Set up color theme for the slider"""
        # Base themes dictionary
        themes = {
            'red': {
                'neutral': "#373737",  # Gray middle zone
                'warning': "#453939",  # Outer warning zones
                'handle_normal': "#8B4343",  # Handle normal state
                'handle_warning': "#E54C4C",  # Handle warning state
                'handle_hover': "#B24949",  # Handle hover state
                'border': '#1a1a1a',  # Normal border
                'disabled': '#444444',  # Disabled handle
                'disabled_border': '#333333'  # Disabled border
            },
            'teal': {
                'neutral': "#373737",
                'warning': "#394545",
                'handle_normal': "#438B8B",
                'handle_warning': "#4CE5E5",
                'handle_hover': "#49B2B2",
                'border': '#1a1a1a',
                'disabled': '#444444',
                'disabled_border': '#333333'
            },
            'purple': {
                'neutral': "#373737",
                'warning': "#3d3945",
                'handle_normal': "#8263c0",
                'handle_warning': "#8549ff",
                'handle_hover': "#a082db",
                'border': '#1a1a1a',
                'disabled': '#444444',
                'disabled_border': '#333333'
            },
            'blue': {
                'neutral': "#373737",
                'warning': "#394555",
                'handle_normal': "#438B99",
                'handle_warning': "#4CE5FF",
                'handle_hover': "#49B2D2",
                'border': '#1a1a1a',
                'disabled': '#444444',
                'disabled_border': '#333333'
            },
            'green': {
                'neutral': "#373737",
                'warning': "#3D4539",
                'handle_normal': "#4A8B43",
                'handle_warning': "#6DE54C",
                'handle_hover': "#49B249",
                'border': '#1a1a1a',
                'disabled': '#444444',
                'disabled_border': '#333333'
            }
        }

        # Get the selected theme or default to red if theme not found
        selected_theme = themes.get( theme, themes['red'] )

        # Set the color constants
        self.COLOR_GROOVE_NEUTRAL = selected_theme['neutral']
        self.COLOR_GROOVE_WARNING = selected_theme['warning']
        self.COLOR_HANDLE_NORMAL = selected_theme['handle_normal']
        self.COLOR_HANDLE_WARNING = selected_theme['handle_warning']
        self.COLOR_HANDLE_BORDER_HOVER = selected_theme['handle_hover']
        self.COLOR_BORDER_NEUTRAL = selected_theme['border']
        self.COLOR_HANDLE_DISABLED = selected_theme['disabled']
        self.COLOR_BORDER_DISABLED = selected_theme['disabled_border']

    def _update_stylesheet( self, value = None ):
        """Update the stylesheet with current gradient stops and handle color"""
        gradient = self._calculate_gradient_stops()

        # Use current value if provided, otherwise use slider's value
        current_value = value if value is not None else self.value()

        # Set handle color based on disabled state
        if self._is_disabled:
            handle_color = self.COLOR_HANDLE_DISABLED
            border_hover_color = self.COLOR_BORDER_DISABLED
        else:
            handle_color = self._get_handle_color( current_value )
            border_hover_color = self.COLOR_HANDLE_BORDER_HOVER

        stylesheet = """
            QSlider::handle:horizontal {
                background-color: %s;
                border: 1px solid %s;
                width: 24px;
                height: 24px;
                margin: -10px 0;
                border-radius: 4px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, %s);
                margin: 2px 0;
                position: absolute;
                left: 4px;
                right: 4px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
                border: 1px solid %s;
            }
            QSlider::sub-page:horizontal {
                background: transparent;
            }
            QSlider::add-page:horizontal {
                background: transparent;
            }
        """ % ( handle_color, self.COLOR_BORDER_NEUTRAL, gradient, border_hover_color )

        self.setStyleSheet( stylesheet )

    def _get_handle_color( self, value ):
        """Determine handle color based on current value"""
        if value <= self.NEGATIVE_THRESHOLD or value >= self.POSITIVE_THRESHOLD:
            return self.COLOR_HANDLE_WARNING
        return self.COLOR_HANDLE_NORMAL

    def __MOUSE__( self ):
        pass

    def mousePressEvent( self, event ):
        """Handle mouse press events for both handle and groove"""
        self.on_handle_press()

        # If disabled, don't process the event
        if self._is_disabled:
            # return
            pass

        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption( opt )

        # Get the handle and groove rectangles
        handle_rect = self.style().subControlRect( 
            QtWidgets.QStyle.CC_Slider,
            opt,
            QtWidgets.QStyle.SC_SliderHandle,
            self
        )
        groove_rect = self.style().subControlRect( 
            QtWidgets.QStyle.CC_Slider,
            opt,
            QtWidgets.QStyle.SC_SliderGroove,
            self
        )

        # Check if click is on handle
        if handle_rect.contains( event.pos() ):
            self._is_groove_click = False
            self._last_mouse_pos = event.pos().x()
            super( CustomSlider, self ).mousePressEvent( event )
            return

        # Check if click is on groove
        if groove_rect.contains( event.pos() ):
            self._is_groove_click = True
            # Calculate the click position relative to the groove
            pos = event.pos().x()
            center = self.width() / 2

            # Trigger the selection query if not already done
            if not self.all_curves:
                self.on_handle_press()

            # Store click direction
            self._click_direction = 1 if pos >= center else -1

            # Perform initial click
            self._handle_repeat_click()

            # Start repeating timer - adjust intervals as needed
            self._click_timer.start( 50 )  # Repeat every 50ms
            return

        self._is_groove_click = False
        super( CustomSlider, self ).mousePressEvent( event )

    def mouseMoveEvent( self, event ):
        """
        Handle mouse movement and threshold locking
        """
        if not self._is_groove_click:
            if self._last_mouse_pos is None:
                # print( 'last mouse pos: ', None )
                super( CustomSlider, self ).mouseMoveEvent( event )
                return

            current_pos = event.pos().x()
            width = self.width() - self.style().pixelMetric( QtWidgets.QStyle.PM_SliderLength )
            value_position = ( current_pos / float( width ) ) * ( self.maximum() - self.minimum() ) + self.minimum()
            current_value = self.value()
            # print( 'normlized', value_position )

            # Check if mouse has moved beyond threshold + margin
            if value_position >= ( self.POSITIVE_THRESHOLD + self.LOCK_RELEASE_MARGIN ) or \
               value_position <= ( self.NEGATIVE_THRESHOLD - self.LOCK_RELEASE_MARGIN ):
                self._mouse_beyond_threshold = True
                self._lock_released = True

            # check if the lock has been properly released, dont reset it if it has, this section unlocks the handle if the direction is reversed
            if not self._lock_released:
                if value_position >= self.NEGATIVE_THRESHOLD + self.LOCK_RELEASE_MARGIN and self._negative_locked or \
                    value_position <= self.POSITIVE_THRESHOLD - self.LOCK_RELEASE_MARGIN and self._positive_locked:
                    self._mouse_beyond_threshold = True
                    self._lock_released = True
                    self._soft_release = True
                    # print( 'mouse', current_value )

            # Handle positive threshold
            if current_value >= ( self.POSITIVE_THRESHOLD - 1 ) and not self._lock_released:
                if not self._mouse_beyond_threshold:
                    self.setValue( self.POSITIVE_THRESHOLD - 1 )
                    return

            # Handle negative threshold
            if current_value <= ( self.NEGATIVE_THRESHOLD + 1 ) and not self._lock_released:
                if not self._mouse_beyond_threshold:
                    self.setValue( self.NEGATIVE_THRESHOLD + 1 )
                    return

            if self._soft_release:
                self._mouse_beyond_threshold = False
                self._lock_released = False
                # self._last_mouse_pos = None
                self._soft_release = False
                self._negative_locked = False
                self._positive_locked = False
            # print( 'neg: ', self._negative_locked, 'pos: ', self._positive_locked )

            # reset, didnt move beyond threshold but back between threshold ranges

            super( CustomSlider, self ).mouseMoveEvent( event )

    def mouseReleaseEvent( self, event ):
        """Handle mouse release events"""
        # Reset handle color to normal state
        self._is_disabled = False  # Reset disabled state
        self._update_stylesheet( self.value() )

        if self._is_groove_click:
            # Stop the timer and reset
            self._click_timer.stop()
            self._click_direction = 0
            self._is_groove_click = False
            # Reset the slider
            QtCore.QTimer.singleShot( 100, self._reset_after_click )
        else:
            self._last_mouse_pos = None
            super( CustomSlider, self ).mouseReleaseEvent( event )

    def _reset_after_click( self ):
        """Reset slider after a groove click"""
        # Make sure we properly close the undo chunk and reset state
        self.on_handle_release()

    def _handle_repeat_click( self ):
        """Handle a single click iteration"""
        if self._click_direction == 0:
            return

        # Calculate new value
        current = self.value()
        new_value = current + self._click_direction

        # Ensure we stay within bounds
        new_value = max( min( new_value, self.maximum() ), self.minimum() )

        # Only update if value actually changed
        if new_value != current:
            self.setValue( new_value )
            self._handle_value_change( new_value )

    def __PRESS__( self ):
        pass

    def on_handle_press( self ):
        """Query and store the current animation state"""
        # open chunk
        cmds.undoInfo( openChunk = True, cn = TOOL_NAME )

        # get curves
        self.all_curves = self._get_visible_curves()

        if not self.all_curves:
            message( 'No animation curves found', warning = True )
            self._is_disabled = True  # Set disabled state
            self._update_stylesheet( self.value() )
            return

        # initialize
        self.selected_objects = cmds.ls( selection = True )
        self.anim_layers = cmds.ls( type = 'animLayer' )
        self._get_blend_nodes()
        self.current_time = cmds.currentTime( query = True )
        self._initialize_key_values()

        # Process curves and their objects
        # print( self.selected_objects )
        for obj in self.selected_objects:
            self._process_object_curves( obj )

    def _get_visible_curves( self ):
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

    def _get_blend_nodes( self ):
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
        """
        Get the current value for a given curve.
        If keys are selected, uses the selected key value.
        Otherwise, evaluates at current time.
        """
        # Check if we have selected keys on this curve
        selected_keys = cmds.keyframe( curve, q = True, sl = True, tc = True )

        if selected_keys:
            # Get the value of the first selected key
            key_time = selected_keys[0]
            return cmds.keyframe( curve, q = True, time = ( key_time, key_time ), vc = True )[0]

        # Fallback to current time evaluation
        return cmds.keyframe( curve, q = True, eval = True,
                            time = ( self.current_time, self.current_time ) )[0]

    def _process_surrounding_keys( self, obj, curve, current_val ):
        """
        Process and store values for surrounding keyframes.
        Handles multiple groups of selected keys with gaps.
        """
        # Get all keyframes on the curve
        keyframes = cmds.keyframe( curve, query = True, timeChange = True )
        if not keyframes:
            self._store_default_key_values( obj, curve, current_val )
            return

        # Check if we're working with selected keys
        selected_keys = cmds.keyframe( curve, q = True, sl = True, tc = True )

        if selected_keys:
            # Group selected keys
            key_groups = self._group_selected_keys( keyframes, selected_keys )
            all_keys = sorted( keyframes )

            # Process each group separately
            for group in key_groups:
                # Find surrounding unselected keys for this group
                prev_key = None
                next_key = None

                # Find previous unselected key for this group
                for key in reversed( all_keys ):
                    if key < group[0] and key not in selected_keys:
                        prev_key = key
                        break

                # Find next unselected key for this group
                for key in all_keys:
                    if key > group[-1] and key not in selected_keys:
                        next_key = key
                        break

                # Get values for surrounding keys
                prev_val = None
                next_val = None

                if prev_key is not None:
                    prev_val = cmds.keyframe( curve, q = True, time = ( prev_key, prev_key ), vc = True )[0]
                if next_key is not None:
                    next_val = cmds.keyframe( curve, q = True, time = ( next_key, next_key ), vc = True )[0]

                # Process each key in the group
                for sel_key in group:
                    if obj not in self.previous_key_values:
                        self.previous_key_values[obj] = {}
                    if obj not in self.next_key_values:
                        self.next_key_values[obj] = {}

                    # Get current value at this key
                    current_key_val = cmds.keyframe( curve, q = True, time = ( sel_key, sel_key ), vc = True )[0]
                    curve_key = '{0}_{1}'.format( curve, sel_key )

                    # Store values for this key
                    if prev_val is not None:
                        self.previous_key_values[obj][curve_key] = prev_val
                    else:
                        self.previous_key_values[obj][curve_key] = current_key_val

                    if next_val is not None:
                        self.next_key_values[obj][curve_key] = next_val
                    else:
                        self.next_key_values[obj][curve_key] = current_key_val

                    # Store initial value for this key
                    self.initial_values[obj][curve_key] = current_key_val
        else:
            # Handle current time case (no selection)
            reference_time = self.current_time
            prev_keys = [key for key in keyframes if key < reference_time]
            next_keys = [key for key in keyframes if key > reference_time]

            self._store_prev_key_value( obj, curve, prev_keys, current_val )
            self._store_next_key_value( obj, curve, next_keys, current_val )

    def _initialize_object_storage( self, obj ):
        """Initialize storage dictionaries for an object if needed"""
        if obj not in self.initial_values:
            self.initial_values[obj] = {}
            self.previous_key_values[obj] = {}
            self.next_key_values[obj] = {}

    def _store_initial_value( self, obj, curve, current_val ):
        """Store the initial value for a curve"""
        self.initial_values[obj][curve] = current_val

    def _store_default_key_values( self, obj, curve, current_val ):
        """Store current value as both previous and next key values"""
        self.previous_key_values[obj][curve] = current_val
        self.next_key_values[obj][curve] = current_val

    def _store_prev_key_value( self, obj, curve, prev_keys, current_val ):
        """
        Store the value of the previous keyframe.
        Takes into account whether we're working with selected keys.
        """
        if prev_keys:
            prev_time = prev_keys[-1]
            prev_val = cmds.keyframe( curve, q = True,
                                    time = ( prev_time, prev_time ), vc = True )[0]
            self.previous_key_values[obj][curve] = prev_val
        else:
            self.previous_key_values[obj][curve] = current_val

    def _store_next_key_value( self, obj, curve, next_keys, current_val ):
        """
        Store the value of the next keyframe.
        Takes into account whether we're working with selected keys.
        """
        if next_keys:
            next_time = next_keys[0]
            next_val = cmds.keyframe( curve, q = True,
                                    time = ( next_time, next_time ), vc = True )[0]
            self.next_key_values[obj][curve] = next_val
        else:
            self.next_key_values[obj][curve] = current_val

    def _group_selected_keys( self, keyframes, selected_keys ):
        """
        Group selected keys into continuous sequences.
        Returns list of groups, where each group is a list of selected keys.
        """
        if not selected_keys:
            return []

        # Sort keys
        selected_keys = sorted( selected_keys )
        groups = []
        current_group = [selected_keys[0]]

        # Group consecutive keys
        for i in range( 1, len( selected_keys ) ):
            # Find the minimum time difference between any two keys on the curve
            all_times = sorted( keyframes )
            min_time_diff = float( 'inf' )
            for j in range( 1, len( all_times ) ):
                diff = all_times[j] - all_times[j - 1]
                if diff < min_time_diff:
                    min_time_diff = diff

            # Allow for small floating point differences by multiplying min_time_diff by 1.1
            if selected_keys[i] - selected_keys[i - 1] <= min_time_diff * 1.1:
                current_group.append( selected_keys[i] )
            else:
                groups.append( current_group )
                current_group = [selected_keys[i]]

        groups.append( current_group )
        return groups

    def __MOVE__( self ):
        pass

    def on_handle_move( self, value ):
        """
        Adjust animation values based on slider position.
        Now handles both selected key and current time scenarios.
        """
        if not self.all_curves:
            return

        self.moved = True
        self.new_values = {}
        for obj in self.selected_objects:
            self._process_object_values( obj, value )

        if self.blend_nodes:
            cmds.dgdirty( self.blend_nodes )
            mel.eval( 'dgdirty;' )
        else:
            mel.eval( 'dgdirty;' )

    def _process_object_values( self, obj, value ):
        """
        Process value adjustments for a single object.
        Now handles multiple groups of selected keys.
        """
        self.new_values[obj] = {}
        for curve in self.all_curves:
            # Check if we're working with selected keys
            selected_keys = cmds.keyframe( curve, q = True, sl = True, tc = True )

            if selected_keys:
                # Process each selected key
                for key_time in selected_keys:
                    curve_key = '{0}_{1}'.format( curve, key_time )
                    if curve_key not in self.initial_values.get( obj, {} ):
                        continue

                    initial_val = self.initial_values[obj][curve_key]
                    blended_val = self._calculate_blended_value( obj, curve_key, value, initial_val )

                    self.new_values[obj][curve_key] = blended_val
                    cmds.setKeyframe( curve, time = key_time, value = blended_val )
            else:
                # Handle current time case
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

    def __RELEASE__( self ):
        pass

    def on_handle_release( self ):
        """Reset the slider and clean up the operation"""
        try:
            self._reset_slider()
            self.reset_state()
        finally:
            cmds.undoInfo( closeChunk = True, cn = TOOL_NAME )

    def _reset_slider( self ):
        """Reset slider to initial position"""
        self.valueChanged.disconnect( self.on_handle_move )
        self.setValue( 0 )
        # self.label.setText( '0%' )
        self.handle_label.hide()  # Initially hide the label
        self.valueChanged.connect( self.on_handle_move )

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
        self.moved = False

        # Reset lock states
        self._positive_locked = False
        self._negative_locked = False
        self._lock_released = False
        self._mouse_beyond_threshold = False
        self._last_mouse_pos = None

    def __MISC__( self ):
        pass


class CustomDialog( QDialog ):
    """Main dialog window for the Blend Pose Tool"""

    def __init__( self, parent = None ):
        super( CustomDialog, self ).__init__( parent )
        self.prefs = WebrToolsPrefs()
        self._setup_ui()

    def _setup_ui( self ):
        """Setup the UI layout and widgets"""
        self.setWindowTitle( "Blend Pose Tool" )
        self.setFixedHeight( 70 )

        # Create layout
        layout = QHBoxLayout()

        # Create toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize( 14, 14 )
        self.toggle_button.setToolTip( TOOL_NAME )
        self.toggle_button.setContextMenuPolicy( Qt.CustomContextMenu )  # Enable right-click menu
        self.toggle_button.customContextMenuRequested.connect( self._show_context_menu )  # Connect right-click signal
        self.toggle_button.setStyleSheet( """
            QPushButton {
                background-color: #2a2a2a;
                border: none;
                border-radius: 4px;
                margin-bottom: 4px;
                margin-right: 4px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """ )
        self.toggle_button.clicked.connect( self._toggle_slider_visibility )

        # Get default values
        default_width = DEFAULT_SLIDER_WIDTH[DEFAULT_RANGE_WIDTH_TXT]  # Updated to use simple dict access
        default_range = DEFAULT_RANGE['150']  # Updated to use simple dict access

        # Create slider with saved preferences
        slider_width = self.prefs.get_tool_pref( 'blend_pose_tool', 'slider_width', default_width )
        slider_range = self.prefs.get_tool_pref( 'blend_pose_tool', 'slider_range', default_range )

        self.slider = CustomSlider()
        self.slider.setFixedWidth( slider_width )
        self.slider.setRange( -slider_range, slider_range )

        # Add widgets to layout with alignment
        layout.addWidget( self.toggle_button, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft )
        layout.addWidget( self.slider, 0, QtCore.Qt.AlignCenter )

        self.setLayout( layout )
        self.adjustSize()

        # Load and apply saved slider visibility
        slider_visible = self.prefs.get_tool_pref( 'blend_pose_tool', 'slider_visible', True )
        self.slider.setVisible( slider_visible )

    def _show_context_menu( self, position ):
        """Show the context menu for preferences"""
        # Create preferences dialog
        prefs_dialog = PreferencesDialog( self )

        # Get the global position of the toggle button
        global_pos = self.toggle_button.mapToGlobal( position )

        # Move dialog below the tool
        dialog_x = global_pos.x() - 20
        dialog_y = global_pos.y() + self.height() / 3  # Add small gap

        prefs_dialog.move( dialog_x, dialog_y )
        prefs_dialog.show()

    def _toggle_slider_visibility( self ):
        """Toggle the slider's visibility and save the state"""
        current_visible = self.slider.isVisible()
        self.slider.setVisible( not current_visible )
        # Save the new visibility state
        self.prefs.set_tool_pref( 'blend_pose_tool', 'slider_visible', not current_visible )


class PreferencesDialog( QDialog ):
    """Dialog for managing Blend Pose Tool preferences"""

    def __init__( self, parent = None ):
        super( PreferencesDialog, self ).__init__( parent )
        self.prefs = WebrToolsPrefs()
        self._setup_ui()
        self._load_current_values()

        # Enable mouse tracking
        self.setMouseTracking( True )

        # Remove the window frame
        self.setWindowFlags( Qt.Popup | Qt.FramelessWindowHint )

        # Set darker background
        self.setStyleSheet( "QDialog { background-color: #383838; }" )

        # Track if mouse is inside dialog
        self._mouse_inside = False

    def _get_stylesheet( self ):
        """Return the stylesheet for the preferences dialog"""
        return """
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #404040;
            }
            QGroupBox {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-weight: bold;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            QRadioButton {
                color: #cccccc;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator::unchecked {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 7px;
            }
            QRadioButton::indicator::checked {
                background-color: #4b4b4b;
                border: 2px solid #666666;
                border-radius: 7px;
            }
            QRadioButton:checked {
                color: #ffffff;
            }
            QRadioButton:hover {
                color: #ffffff;
            }
        """

    def leaveEvent( self, event ):
        """Handle mouse leaving the dialog window"""
        self._mouse_inside = False
        # Use a short timer to verify mouse hasn't re-entered before closing
        QtCore.QTimer.singleShot( 100, self._check_close )
        super( PreferencesDialog, self ).leaveEvent( event )

    def enterEvent( self, event ):
        """Handle mouse entering the dialog window"""
        self._mouse_inside = True
        super( PreferencesDialog, self ).enterEvent( event )

    def _check_close( self ):
        """Check if we should close the dialog"""
        if not self._mouse_inside:
            self.close()

    def _setup_ui( self ):
        """Set up the preferences dialog UI with horizontal radio buttons"""
        self.setWindowTitle( "Slider Preferences" )

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins( 12, 8, 12, 8 )

        # Add title label
        title_label = QLabel( "{0} Prefs".format( TOOL_NAME ) )
        title_label.setStyleSheet( """
            QLabel {
                color: #cccccc;
                font-weight: bold;
                font-size: 13px;
            }
        """ )
        main_layout.addWidget( title_label )

        # Width section
        width_label = QLabel( "WIDTH" )
        width_label.setStyleSheet( """
            QLabel {
                color: #8c8c8c;
                font-weight: bold;
                font-size: 13px;
                padding: 2px 10px 2px 10px;
                background-color: #2b2b2b;
                border-radius: 6px;
            }
        """ )
        main_layout.addWidget( width_label )

        # Width radio buttons frame
        width_frame = QtWidgets.QFrame()
        width_layout = QHBoxLayout( width_frame )
        width_layout.setSpacing( 10 )
        width_layout.setContentsMargins( 8, 4, 8, 4 )
        self.width_button_group = QButtonGroup( self )

        # Create radio buttons for width options
        for i, ( size_name, value ) in enumerate( DEFAULT_SLIDER_WIDTH.items() ):
            radio = QRadioButton( size_name.title() )
            radio.setStyleSheet( """
                QRadioButton {
                    font-size: 13px;
                    spacing: 8px;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
                QRadioButton::indicator::unchecked {
                    background-color: #2b2b2b;
                    border: 2px solid #404040;
                    border-radius: 9px;
                }
                QRadioButton::indicator::checked {
                    background-color: #4b4b4b;
                    border: 2px solid #666666;
                    border-radius: 9px;
                }
            """ )
            radio.width_value = value
            radio.size_name = size_name
            self.width_button_group.addButton( radio, i )
            width_layout.addWidget( radio )

        main_layout.addWidget( width_frame )

        # Range section
        range_label = QLabel( "RANGE" )
        range_label.setStyleSheet( width_label.styleSheet() )  # Use same style as width label
        main_layout.addWidget( range_label )

        # Range radio buttons frame
        range_frame = QtWidgets.QFrame()
        range_layout = QHBoxLayout( range_frame )
        range_layout.setSpacing( 10 )
        range_layout.setContentsMargins( 8, 4, 8, 4 )
        self.range_button_group = QButtonGroup( self )

        # Create radio buttons for range options - sorted
        sorted_range = sorted( DEFAULT_RANGE.items(), key = lambda x: int( x[0] ) )
        for i, ( range_name, value ) in enumerate( sorted_range ):
            radio = QRadioButton( range_name )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.range_value = value
            radio.range_name = range_name
            self.range_button_group.addButton( radio, i )
            range_layout.addWidget( radio )

        main_layout.addWidget( range_frame )

        # Connect signals
        self.width_button_group.buttonClicked.connect( self._on_width_changed )
        self.range_button_group.buttonClicked.connect( self._on_range_changed )

        self.setLayout( main_layout )
        self.setMinimumWidth( 200 )
        self.adjustSize()

    def _load_current_values( self ):
        """Load current preference values and select appropriate radio buttons"""
        # Get current values from preferences
        current_width = self.prefs.get_tool_pref( 'blend_pose_tool', 'slider_width',
                                                DEFAULT_SLIDER_WIDTH[DEFAULT_RANGE_WIDTH_TXT] )
        current_range = self.prefs.get_tool_pref( 'blend_pose_tool', 'slider_range',
                                                DEFAULT_RANGE['150'] )

        # Select appropriate width radio button
        for button in self.width_button_group.buttons():
            if button.width_value == current_width:
                button.setChecked( True )
                break

        # Select appropriate range radio button
        for button in self.range_button_group.buttons():
            if button.range_value == current_range:
                button.setChecked( True )
                break

    def _on_width_changed( self, radio_button ):
        """Handle width radio button selection"""
        width_value = radio_button.width_value
        size_name = radio_button.size_name

        # Save to preferences
        self.prefs.set_tool_pref( 'blend_pose_tool', 'slider_width', width_value )
        self.prefs.set_tool_pref( 'blend_pose_tool', 'slider_width_name', size_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.setFixedWidth( width_value )
            parent_dialog.adjustSize()

    def _on_range_changed( self, radio_button ):
        """Handle range radio button selection"""
        range_value = radio_button.range_value
        range_name = radio_button.range_name

        # Save to preferences
        self.prefs.set_tool_pref( 'blend_pose_tool', 'slider_range', range_value )
        self.prefs.set_tool_pref( 'blend_pose_tool', 'slider_range_name', range_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.setRange( -range_value, range_value )


class WebrToolsPrefs( object ):
    """
    Manages preferences for WebrTools across different platforms.
    Handles reading, writing, and default values for tool-specific preferences.
    """

    def __init__( self ):
        self.prefs_file = 'WebrToolsPrefs.json'
        self.prefs_path = self._get_prefs_path()
        self.default_prefs = {
            'blend_pose_tool': {
                'slider_visible': True,
                'slider_width': DEFAULT_SLIDER_WIDTH[DEFAULT_RANGE_WIDTH_TXT],
                'slider_width_name': 'XL',
                'slider_range': DEFAULT_RANGE['150'],
                'slider_range_name': '150'
            }
        }
        self.prefs = self._load_prefs()

    def _get_prefs_path( self ):
        """
        Get the appropriate preferences directory path based on OS.
        Returns full path to the preferences file.
        """
        system = platform.system().lower()

        if system == 'windows':
            maya_app_dir = os.environ.get( 'MAYA_APP_DIR' )
            if maya_app_dir:
                base_path = maya_app_dir
            else:
                base_path = os.path.join( os.environ.get( 'USERPROFILE', '' ), 'Documents', 'maya' )

        elif system == 'darwin':  # macOS
            base_path = os.path.expanduser( '~/Library/Preferences/Autodesk/maya' )

        elif system == 'linux':
            base_path = os.path.expanduser( '~/maya' )

        else:
            raise OSError( 'Unsupported operating system: {}'.format( system ) )

        # Create scripts directory if it doesn't exist
        scripts_path = os.path.join( base_path, 'scripts' )
        if not os.path.exists( scripts_path ):
            os.makedirs( scripts_path )

        return os.path.join( scripts_path, self.prefs_file )

    def _load_prefs( self ):
        """
        Load preferences from file or create with defaults if doesn't exist.
        """
        try:
            if os.path.exists( self.prefs_path ):
                with open( self.prefs_path, 'r' ) as f:
                    stored_prefs = json.load( f )

                # Merge with defaults to ensure all required keys exist
                merged_prefs = self.default_prefs.copy()
                for tool, settings in stored_prefs.items():
                    if tool in merged_prefs:
                        merged_prefs[tool].update( settings )
                    else:
                        merged_prefs[tool] = settings

                return merged_prefs
            else:
                self._save_prefs( self.default_prefs )
                return self.default_prefs

        except ( IOError, ValueError ) as e:
            print( 'Error loading preferences: {}'.format( e ) )
            return self.default_prefs

    def _save_prefs( self, prefs_data ):
        """
        Save preferences to file.
        """
        try:
            with open( self.prefs_path, 'w' ) as f:
                json.dump( prefs_data, f, indent = 4 )
        except IOError as e:
            print( 'Error saving preferences: {}'.format( e ) )

    def get_tool_pref( self, tool_name, pref_name, default = None ):
        """
        Get a specific tool preference.
        """
        tool_prefs = self.prefs.get( tool_name, {} )
        return tool_prefs.get( pref_name, default )

    def set_tool_pref( self, tool_name, pref_name, value ):
        """
        Set a specific tool preference and save to file.
        """
        if tool_name not in self.prefs:
            self.prefs[tool_name] = {}

        self.prefs[tool_name][pref_name] = value
        self._save_prefs( self.prefs )


def get_maya_main_window():
    """
    Get Maya's main window as a QWidget.
    Returns the main Maya window wrapped as a QWidget.
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( int( main_window_ptr ), QtWidgets.QWidget )


if __name__ == '__main__':
    # print( '?' )
    pass
else:
    # print( 'here' )
    custom_dialog = CustomDialog( get_maya_main_window() )
    # print( custom_dialog )
    custom_dialog.show()
