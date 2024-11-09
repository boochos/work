# Version 1.5
import imp
import json
import os
import platform
import time

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QColor
from PySide2.QtWidgets import ( QDialog, QLabel, QSlider, QHBoxLayout, QVBoxLayout,
                              QPushButton, QRadioButton, QButtonGroup, QGroupBox )
from shiboken2 import wrapInstance

import core
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

from .strategies import BlendStrategy, DirectKeyBlendStrategy, LinearBlendStrategy

# print( "Core module path:", core.__file__ )  # This will show where it's finding core.py
imp.reload( core )

# Initialize the global variable
global custom_dialog

# Constants
TOOL_NAME = 'Blend_N'


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
    _TOOL_NAME = {'Blend_N': 'Bn'}  # TOOL_NAME.split( '_' )[0] + TOOL_NAME.split( '_' )[1]

    # Class variables for color transition points and colors
    NEGATIVE_THRESHOLD = -101  # Point where negative red zone starts
    POSITIVE_THRESHOLD = 101  # Point where positive red zone starts

    # Default dictionaries for configurable values
    DEFAULT_SLIDER_WIDTH = {
        'S': 100,
        'M': 200,
        'L': 300,
        'XL': 500  # default
    }
    DEFAULT_RANGE = {
        '100': 100,
        '150': 150,  # default
        '200': 200
    }
    DEFAULT_TICK_WIDTH = {
        'thin': 0.01,
        'med': 0.02,
        'thick': 0.03  # default # ADD NONE AS AN OPTION
    }
    DEFAULT_TICK_INTERVAL = {
    '25': 25,
    '30': 30,
    '50': 50  # default
    }
    DEFAULT_LOCK_RELEASE_MARGIN = {
        '0': 0,
        '5': 5,
        '10': 10,
        '15': 15  # default
    }
    DEFAULT_GROOVE_CLICK_VALUE = {
        '1': 1,  # default
        '2': 2,
        '3': 3,
        '5': 5
    }
    TOOL_NAME = {'Blend_N': 'Bn'}  # TOOL_NAME.split( '_' )[0] + TOOL_NAME.split( '_' )[1]

    # Default text values
    DEFAULT_WIDTH_TXT = 'XL'
    DEFAULT_RANGE_TXT = '150'
    DEFAULT_TICK_WIDTH_TXT = 'thick'
    DEFAULT_TICK_INTERVAL_TXT = '50'
    DEFAULT_LOCK_RELEASE_MARGIN_TXT = '15'
    DEFAULT_GROOVE_CLICK_VALUE_TXT = '1'

    # Colors
    # Groove
    COLOR_GROOVE_NEUTRAL = QColor( 55, 55, 55 ).name()  # rgb(55, 55, 55)
    COLOR_GROOVE_WARNING = QColor( 69, 57, 57 ).name()  # rgb(69, 57, 57)
    # Handle
    COLOR_HANDLE_NEUTRAL = QColor( 139, 67, 67 ).name()  # rgb(139, 67, 67)
    COLOR_HANDLE_WARNING = QColor( 229, 76, 76 ).name()  # rgb(229, 76, 76)
    COLOR_HANDLE_BORDER_HOVER = QColor( 178, 73, 73 ).name()  # rgb(178, 73, 73)
    COLOR_HANDLE_DISABLED = QColor( 68, 68, 68 ).name()  # rgb(68, 68, 68)
    # Border
    COLOR_BORDER_NEUTRAL = QColor( 26, 26, 26 ).name()  # rgb(26, 26, 26)
    COLOR_BORDER_DISABLED = QColor( 51, 51, 51 ).name()  # rgb(51, 51, 51)
    # Tick
    COLOR_TICK_MARK = QColor( 61, 69, 57 ).name()  # rgb(61, 69, 57)

    def __init__( self, parent = None, theme = 'orange' ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )

        self.core = core.BlendToolCore()
        # print( "Core initialized with key_cache:", hasattr( self.core, 'key_cache' ) )  # Debug

        self.blend_data = {}
        self.update_queue = []
        self.moved = False
        self._is_disabled = False  # Add state tracking

        # Initialize preference-based values using class defaults
        self._tick_interval = self.DEFAULT_TICK_INTERVAL[self.DEFAULT_TICK_INTERVAL_TXT]
        self._tick_width = self.DEFAULT_TICK_WIDTH[self.DEFAULT_TICK_WIDTH_TXT]
        self._slider_width = self.DEFAULT_SLIDER_WIDTH[self.DEFAULT_WIDTH_TXT]
        self._slider_range = self.DEFAULT_RANGE[self.DEFAULT_RANGE_TXT]
        self._lock_release_margin = self.DEFAULT_LOCK_RELEASE_MARGIN[self.DEFAULT_LOCK_RELEASE_MARGIN_TXT]
        self._groove_click_value = self.DEFAULT_GROOVE_CLICK_VALUE[self.DEFAULT_GROOVE_CLICK_VALUE_TXT]

        # self.theme = theme
        self.set_theme( theme )
        self._setup_ui()
        self._connect_signals()
        self._reset_state()

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

    # Add property
    @property
    def slider_range( self ):
        """Get current slider range"""
        return self._slider_range

    @slider_range.setter
    def slider_range( self, value ):
        """Set slider range and update UI"""
        self._slider_range = value
        self.setRange( -value, value )  # Updates Qt slider range
        self._update_stylesheet()

    @property
    def tick_interval( self ):
        return self._tick_interval

    @tick_interval.setter
    def tick_interval( self, value ):
        self._tick_interval = value
        self._update_stylesheet()

    @property
    def tick_width( self ):
        return self._tick_width

    @tick_width.setter
    def tick_width( self, value ):
        self._tick_width = value
        self._update_stylesheet()

    @property
    def slider_width( self ):
        return self._slider_width

    @slider_width.setter
    def slider_width( self, value ):
        self._slider_width = value
        self.setFixedWidth( value )

    @property
    def lock_release_margin( self ):
        return self._lock_release_margin

    @lock_release_margin.setter
    def lock_release_margin( self, value ):
        self._lock_release_margin = value

    @property
    def groove_click_value( self ):
        return self._groove_click_value

    @groove_click_value.setter
    def groove_click_value( self, value ):
        self._groove_click_value = value

    @classmethod
    def get_default_width_txt( cls ):
        """Get default width text value"""
        return cls.DEFAULT_WIDTH_TXT

    @classmethod
    def get_default_range_txt( cls ):
        """Get default range text value"""
        return cls.DEFAULT_RANGE_TXT

    @classmethod
    def get_default_tick_width_txt( cls ):
        """Get default tick width text value"""
        return cls.DEFAULT_TICK_WIDTH_TXT

    @classmethod
    def get_default_width( cls ):
        """Get default width value"""
        return cls.DEFAULT_SLIDER_WIDTH[cls.DEFAULT_WIDTH_TXT]

    @classmethod
    def get_default_range( cls ):
        """Get default range value"""
        return cls.DEFAULT_RANGE[cls.DEFAULT_RANGE_TXT]

    @classmethod
    def get_default_tick_width( cls ):
        """Get default tick width value"""
        return cls.DEFAULT_TICK_WIDTH[cls.DEFAULT_TICK_WIDTH_TXT]

    @classmethod
    def get_default_tick_interval_txt( cls ):
        """Get default tick interval text value"""
        return cls.DEFAULT_TICK_INTERVAL_TXT

    @classmethod
    def get_default_tick_interval( cls ):
        """Get default tick interval value"""
        return cls.DEFAULT_TICK_INTERVAL[cls.DEFAULT_TICK_INTERVAL_TXT]

    @classmethod
    def get_default_lock_release_margin_txt( cls ):
        """Get default lock release margin text value"""
        return cls.DEFAULT_LOCK_RELEASE_MARGIN_TXT

    @classmethod
    def get_default_lock_release_margin( cls ):
        """Get default lock release margin value"""
        return cls.DEFAULT_LOCK_RELEASE_MARGIN[cls.DEFAULT_LOCK_RELEASE_MARGIN_TXT]

    @classmethod
    def get_default_groove_click_value_txt( cls ):
        """Get default groove click value text value"""
        return cls.DEFAULT_GROOVE_CLICK_VALUE_TXT

    @classmethod
    def get_default_groove_click_value( cls ):
        """Get default groove click value"""
        return cls.DEFAULT_GROOVE_CLICK_VALUE[cls.DEFAULT_GROOVE_CLICK_VALUE_TXT]

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
        self.sliderPressed.connect( self._before_handle_press )
        self.valueChanged.connect( self._before_handle_move )
        self.sliderReleased.connect( self._before_handle_release )

    def _setup_ui( self ):
        """Initialize UI elements and their properties"""
        # Use instance variables initialized from preferences
        # self.setRange( int( -self.slider_range ), int( self.slider_range ) )
        self.setValue( 0 )
        # self.setFixedWidth( self.slider_width )  # Use the property
        self.setFixedHeight( 50 )

        # self._update_stylesheet()

        # Connect valueChanged to update handle color
        self.valueChanged.connect( self._handle_value_change )
        self.valueChanged.connect( self._check_threshold_locks )

    def _check_threshold_locks( self, value ):
        """
        Handle threshold locking behavior
        """
        # print( '\nCheck Threshold Locks Debug:' )
        # print( 'Incoming value: {0}'.format( value ) )
        # print( 'Lock Released: {0}'.format( self._lock_released ) )

        if self._lock_released:
            # print( 'Lock already released, returning' )
            return

        # Check positive threshold
        if value >= self.POSITIVE_THRESHOLD - 1:
            # print( 'Hit positive threshold check:' )
            if not self._positive_locked:
                # Engage lock at threshold
                # print( '___Engaging positive lock' )
                self._positive_locked = True
                # print( 'Setting value to: {0}'.format( self.POSITIVE_THRESHOLD - 1 ) )
                self.setValue( self.POSITIVE_THRESHOLD - 1 )
            elif value >= self.POSITIVE_THRESHOLD + self.lock_release_margin:
                # Release lock if we've moved past release point
                # print( '_________Releasing positive lock - beyond margin' )
                self._positive_locked = False
                self._lock_released = True
            elif self._positive_locked:
                # Keep value at threshold while locked
                # print( '___Maintaining positive lock at: {0}'.format( self.POSITIVE_THRESHOLD - 1 ) )
                self.setValue( self.POSITIVE_THRESHOLD - 1 )

        # Check negative threshold
        elif value <= self.NEGATIVE_THRESHOLD + 1:
            # print( 'Hit negative threshold check:' )
            if not self._negative_locked:
                # Engage lock at threshold
                # print( 'Engaging negative lock' )
                self._negative_locked = True
                # print( 'Setting value to: {0}'.format( self.NEGATIVE_THRESHOLD + 1 ) )
                self.setValue( self.NEGATIVE_THRESHOLD + 1 )
            elif value <= self.NEGATIVE_THRESHOLD - self.lock_release_margin:
                # Release lock if we've moved past release point
                # print( 'Releasing negative lock - beyond margin' )
                self._negative_locked = False
                self._lock_released = True
            elif self._negative_locked:
                # Keep value at threshold while locked
                # print( 'Maintaining negative lock at: {0}'.format( self.NEGATIVE_THRESHOLD + 1 ) )
                self.setValue( self.NEGATIVE_THRESHOLD + 1 )
        # print( 'check: ', self.value() )
        # print( 'End state:' )
        # print( 'Value: {0}'.format( self.value() ) )
        # print( 'Positive Lock: {0}'.format( self._positive_locked ) )
        # print( 'Negative Lock: {0}'.format( self._negative_locked ) )
        # print( 'Lock Released: {0}'.format( self._lock_released ) )

    def _handle_value_change( self, value ):
        """Update handle color when value changes"""
        self._update_stylesheet( value )
        self.handle_label.setText( '{0}'.format( abs( value ) ) )

    def _calculate_position( self, value ):
        """Convert absolute value to relative position (0-1)"""
        total_range = self.maximum() - self.minimum()
        if total_range == 0:
            return 0
        return ( value - self.minimum() ) / float( total_range )

    def _calculate_value( self, position ):
        """Convert relative position (0-1) to slider value"""
        total_range = self.maximum() - self.minimum()
        return position * total_range + self.minimum()

    def _format_gradient_stop( self, position, color ):
        """Format a single gradient stop with both position and corresponding value"""
        # slider_value = self._calculate_value( position ) # need for print
        # print( "Position: {0:.4f} ({1}) [Value: {2:.4f}]".format( position, color, slider_value ) )
        return "stop:{0:.4f} {1}".format( position, color )

    def _calculate_gradient_stops( self ):
        """Calculate gradient stops for a slider with warning zones and tick marks."""
        # Early return for zero range case
        total_range = self.maximum() - self.minimum()
        if total_range == 0:
            return "stop:0 {0}, stop:1 {0}".format( self.COLOR_GROOVE_NEUTRAL )

        # print( "\nSlider Range: {0} to {1}".format( self.minimum(), self.maximum() ) )
        # print( "Warning Thresholds: {0} to {1}".format( self.NEGATIVE_THRESHOLD, self.POSITIVE_THRESHOLD ) )
        # print( "\nGradient Sequence:" )

        # Constants
        TINY_GAP = 0.0001
        PROXIMITY_THRESHOLD = 1

        # Check if warning zones are within range
        has_negative_warning = self.NEGATIVE_THRESHOLD >= self.minimum()
        has_positive_warning = self.POSITIVE_THRESHOLD <= self.maximum()

        # Calculate key positions only if warning zones are in range
        min_warning_stop = ( self._calculate_position( self.NEGATIVE_THRESHOLD )
                          if has_negative_warning else None )
        max_warning_start = ( self._calculate_position( self.POSITIVE_THRESHOLD )
                           if has_positive_warning else None )

        # Generate tick positions and their actual values
        start_tick = ( ( self.NEGATIVE_THRESHOLD + self.tick_interval ) // self.tick_interval ) * self.tick_interval
        end_tick = ( ( self.POSITIVE_THRESHOLD + self.tick_interval ) // self.tick_interval ) * self.tick_interval

        # Build tick data
        tick_data = []
        for tick in range( int( start_tick ), int( end_tick ), self.tick_interval ):
            if self.minimum() <= tick <= self.maximum() and tick != 0:
                # Add proximity check
                if ( abs( tick - self.NEGATIVE_THRESHOLD ) > PROXIMITY_THRESHOLD and
                    abs( tick - self.POSITIVE_THRESHOLD ) > PROXIMITY_THRESHOLD ):
                    pos = self._calculate_position( tick )
                    if 0 < pos < 1:
                        tick_data.append( ( pos, tick ) )

        # Build gradient stops
        stops = []

        # Add negative warning zone
        if has_negative_warning:
            # print( "\n# Negative Warning Zone:" )
            stops.extend( [
                self._format_gradient_stop( 0, self.COLOR_GROOVE_WARNING ),
                self._format_gradient_stop( min_warning_stop, self.COLOR_GROOVE_WARNING ),
                self._format_gradient_stop( min_warning_stop + TINY_GAP,
                                       self.COLOR_GROOVE_NEUTRAL )
            ] )
            prev_pos = min_warning_stop + ( TINY_GAP * 2 )
        else:
            stops.append( self._format_gradient_stop( 0, self.COLOR_GROOVE_NEUTRAL ) )
            prev_pos = TINY_GAP

        # Add ticks
        for pos, tick_value in tick_data:
            # Determine tick direction based on value
            if tick_value < 0:
                tick_start = pos
                tick_end = pos + self.tick_width
                # print( "\n# Negative Tick at value: {0}".format( tick_value ) )
            else:
                tick_start = pos - self.tick_width
                tick_end = pos
                # print( "\n# Positive Tick at value: {0}".format( tick_value ) )

            # Add background before tick if there's space
            if tick_start - prev_pos > TINY_GAP:
                # print( "\n# Neutral Background:" )
                stops.extend( [
                    self._format_gradient_stop( prev_pos, self.COLOR_GROOVE_NEUTRAL ),
                    self._format_gradient_stop( tick_start - TINY_GAP,
                                           self.COLOR_GROOVE_NEUTRAL )
                ] )

            # Add tick mark
            stops.extend( [
                self._format_gradient_stop( tick_start - TINY_GAP,
                                       self.COLOR_GROOVE_NEUTRAL ),
                self._format_gradient_stop( tick_start, self.COLOR_TICK_MARK ),
                self._format_gradient_stop( tick_end, self.COLOR_TICK_MARK ),
                self._format_gradient_stop( tick_end + TINY_GAP,
                                       self.COLOR_GROOVE_NEUTRAL )
            ] )

            prev_pos = tick_end + TINY_GAP

        # Add final sections
        if has_positive_warning:
            if max_warning_start - prev_pos > TINY_GAP * 2:
                # print( "\n# Final Neutral Background:" )
                stops.extend( [
                    self._format_gradient_stop( prev_pos, self.COLOR_GROOVE_NEUTRAL ),
                    self._format_gradient_stop( max_warning_start - TINY_GAP,
                                           self.COLOR_GROOVE_NEUTRAL )
                ] )

            # print( "\n# Positive Warning Zone:" )
            stops.extend( [
                self._format_gradient_stop( max_warning_start - TINY_GAP,
                                       self.COLOR_GROOVE_NEUTRAL ),
                self._format_gradient_stop( max_warning_start,
                                       self.COLOR_GROOVE_WARNING ),
                self._format_gradient_stop( 1, self.COLOR_GROOVE_WARNING )
            ] )
        else:
            if 1.0 - prev_pos > TINY_GAP:
                stops.extend( [
                    self._format_gradient_stop( prev_pos, self.COLOR_GROOVE_NEUTRAL ),
                    self._format_gradient_stop( 1, self.COLOR_GROOVE_NEUTRAL )
                ] )

        return ", ".join( stops )

    def __COLOUR__( self ):
        pass

    def set_theme( self, theme = '' ):
        """Update the slider's theme and refresh the UI"""
        self._setup_theme( theme )
        self._update_stylesheet()

    def _setup_theme( self, theme = 'blue' ):
        """Set up color theme for the slider"""
        base_colors = {
            'blue': QColor( 60, 112, 175 ),  # Original blue
            'blueLight': QColor( 60, 147, 176 ),  # Original blue !
            'red': QColor( 175, 67, 67 ),  # From original red theme
            'teal': QColor( 83, 181, 178 ),  # From original teal theme
            'purple': QColor( 89, 95, 179 ),  # From original purple theme
            'green': QColor( 82, 171, 92 ),  # From original green theme
            'greenLight': QColor( 120, 176, 60 ),  # From original green theme !
            'magenta': QColor( 149, 60, 176 ),  # From original green theme
            'orange': QColor( 175, 120, 48 ),  # From original green theme !
            'yellow': QColor( 175, 164, 60 ),  # From original green theme !
            'pink': QColor( 189, 115, 185 ),  # From original green theme !
            'grey': QColor( 147, 150, 150 ),  # From original green theme !
            'greyDark': QColor( 109, 110, 110 )  # From original green theme !
        }

        # Get base color or default to blue
        base = base_colors.get( theme, base_colors['blue'] )

        theme_colors = {
            'groove_neutral': QColor( 55, 55, 55 ).name(),
            'groove_warning': value_color( base, 0.6, 0.6 ).name(),  # Darker and desaturated
            'handle_neutral': base.name(),
            'handle_warning': value_color( base, 1.4 ).name(),
            'border_hover': value_color( base, 1.6 ).name(),
            'border_neutral': QColor( 26, 26, 26 ).name(),
            'handle_disabled': value_color( base, 0.5, 0.8 ).name(),
            'border_disabled': value_color( base, 1.3, 0.0 ).name(),
            'tick_mark': value_color( base, 0.6, 0.6 ).name(),  # Darker and desaturated
            'ui_background': QColor( 43, 43, 43 ).name(),
            'ui_control_bg': QColor( 80, 43, 43 ).name()
        }

        # Set the color constants
        self.COLOR_GROOVE_NEUTRAL = theme_colors['groove_neutral']
        self.COLOR_GROOVE_WARNING = theme_colors['groove_warning']
        self.COLOR_HANDLE_NEUTRAL = theme_colors['handle_neutral']
        self.COLOR_HANDLE_WARNING = theme_colors['handle_warning']
        self.COLOR_HANDLE_BORDER_HOVER = theme_colors['border_hover']
        self.COLOR_BORDER_NEUTRAL = theme_colors['border_neutral']
        self.COLOR_HANDLE_DISABLED = theme_colors['handle_disabled']
        self.COLOR_BORDER_DISABLED = theme_colors['border_disabled']
        self.COLOR_TICK_MARK = theme_colors['tick_mark']
        self._current_theme = theme_colors

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
        return self.COLOR_HANDLE_NEUTRAL

    def __MOUSE__( self ):
        pass

    def mousePressEvent( self, event ):
        """Handle mouse press events for both handle and groove"""
        self._before_handle_press()

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
                self._before_handle_press()

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

            # Get style option for proper handle positioning
            opt = QtWidgets.QStyleOptionSlider()
            self.initStyleOption( opt )

            # Get the slider regions
            groove_rect = self.style().subControlRect( 
                QtWidgets.QStyle.CC_Slider,
                opt,
                QtWidgets.QStyle.SC_SliderGroove,
                self
            )
            handle_rect = self.style().subControlRect( 
                QtWidgets.QStyle.CC_Slider,
                opt,
                QtWidgets.QStyle.SC_SliderHandle,
                self
            )

            # Calculate relative position and convert to value
            pos = event.pos().x()
            groove_center = groove_rect.center().x()
            available_width = groove_rect.width() - handle_rect.width()

            # Adjust position to be relative to groove
            pos_on_groove = pos - groove_rect.x() - ( handle_rect.width() / 2 )

            # Convert to normalized value (0-1)
            if available_width > 0:
                normalized = max( 0.0, min( 1.0, pos_on_groove / float( available_width ) ) )
                # Convert to actual slider value
                value_position = int( normalized * ( self.maximum() - self.minimum() ) + self.minimum() )
            else:
                value_position = self.minimum()

            current_value = self.value()

            '''
            print( '' )
            print( '\nMouse Move Debug:' )
            print( 'Mouse Position: {}'.format( pos ) )
            print( 'Groove Center: {}'.format( groove_center ) )
            print( 'Position on Groove: {}'.format( pos_on_groove ) )
            # print( 'Current Position: {0}'.format( current_pos ) )
            print( 'Value Position: {0}'.format( value_position ) )
            print( 'Current Value: {0}'.format( current_value ) )
            print( 'Positive Lock: {0}'.format( self._positive_locked ) )
            print( 'Negative Lock: {0}'.format( self._negative_locked ) )
            print( 'Lock Released: {0}'.format( self._lock_released ) )
            print( 'Mouse Beyond Threshold: {0}'.format( self._mouse_beyond_threshold ) )
            print( 'Soft Release: {0}'.format( self._soft_release ) )
            '''

            # Check if mouse has moved beyond threshold + margin
            if value_position >= ( self.POSITIVE_THRESHOLD + self.lock_release_margin ) or \
               value_position <= ( self.NEGATIVE_THRESHOLD - self.lock_release_margin ):
                # print( 'Beyond threshold + margin condition met' )
                self._mouse_beyond_threshold = True
                self._lock_released = True

            # check if the lock has been properly released, dont reset it if it has, this section unlocks the handle if the direction is reversed
            if not self._lock_released:
                if value_position > self.NEGATIVE_THRESHOLD + 1 and self._negative_locked or \
                    value_position < self.POSITIVE_THRESHOLD - 1 and self._positive_locked:
                    # print( 'Direction reversal condition met:' )
                    # print( 'Value Position vs Threshold: {0} vs {1}'.format( value_position, self.POSITIVE_THRESHOLD ) )
                    self._mouse_beyond_threshold = False
                    self._lock_released = False
                    self._soft_release = False
                    self._negative_locked = False
                    self._positive_locked = False
                    self.setValue( value_position )
                    # print( '___Before super call - Current Value: {}'.format( self.value() ) )
                    super( CustomSlider, self ).mouseMoveEvent( event )
                    # print( '___After super call - Current Value: {}'.format( self.value() ) )
                    return
                    # print( 'mouse', current_value )

            # Handle positive threshold
            if current_value >= ( self.POSITIVE_THRESHOLD - 1 ) and not self._lock_released:
                # print( 'pos try adjusting' )
                if not self._mouse_beyond_threshold:
                    # print( 'pos adjust' )
                    self.setValue( self.POSITIVE_THRESHOLD - 1 )
                    return

            # Handle negative threshold
            if current_value <= ( self.NEGATIVE_THRESHOLD + 1 ) and not self._lock_released:
                # print( 'try adjusting' )
                if not self._mouse_beyond_threshold:
                    # print( 'adjust' )
                    self.setValue( self.NEGATIVE_THRESHOLD + 1 )
                    return

            '''
            if self._soft_release:
                print( 'Soft release triggering reset' )
                self._mouse_beyond_threshold = False
                self._lock_released = False
                # self._last_mouse_pos = None
                self._soft_release = False
                self._negative_locked = False
                self._positive_locked = False
            '''
            # print( 'neg: ', self._negative_locked, 'pos: ', self._positive_locked )

            # reset, didnt move beyond threshold but back between threshold ranges
            # print( 'Before super call - Current Value: {0}'.format( self.value() ) )
            super( CustomSlider, self ).mouseMoveEvent( event )
            # print( 'After super call - Current Value: {0}'.format( self.value() ) )

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
        self._before_handle_release()

    def _handle_repeat_click( self ):
        """Handle a single click iteration"""
        if self._click_direction == 0:
            return

        # Calculate new value
        current = self.value()
        new_value = current + ( self._click_direction * self.groove_click_value )

        # Ensure we stay within bounds
        new_value = max( min( new_value, self.maximum() ), self.minimum() )

        # Only update if value actually changed
        if new_value != current:
            self.setValue( new_value )
            self._handle_value_change( new_value )

    def __PRESS__( self ):
        pass

    def _before_handle_press( self ):
        """Start"""
        self.on_handle_press()

    def on_handle_press( self ):
        """HOOK, Query and store the current animation state"""

        # get curves
        self.all_curves = self.core.get_curves()  # self._get_visible_curves()

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

        # Clear and initialize blend data
        self.blend_data = {}

        # Batch collect data for all curves
        for curve in self.all_curves:
            curve_data = self.core.collect_curve_data( curve )
            if curve_data['keys']:  # Only add if curve has keys
                self.blend_data[curve] = {
                    'data': curve_data,
                    'prev_indices': self.core.calculate_prev_indices( curve_data['keys'] ),
                    'next_indices': self.core.calculate_next_indices( curve_data['keys'] ),
                    'curve': curve  # Add curve name to info
                }
            else:
                print( 'no keys' )
                pass

        # Process curves and their objects
        for obj in self.selected_objects:
            self._process_object_curves( obj )

    '''
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
        print( 'visible: ', curves )
        return curves
    '''

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
        """Process curves for an object"""
        for curve in self.all_curves:
            if curve not in self.blend_data:
                continue

            # Get cached data
            curve_info = self.blend_data[curve]
            curve_data = curve_info['data']

            # Get keys to update
            selected_keys = cmds.keyframe( curve, q = True, sl = True, tc = True )
            times_to_update = selected_keys if selected_keys else [self.current_time]

            # Process in batches
            for i in range( 0, len( times_to_update ), self.core.batch_size ):
                batch = times_to_update[i:i + self.core.batch_size]

                for time in batch:
                    self._process_key_update( obj, curve, time, curve_data, curve_info )

    def _process_key_update( self, obj, curve, time, curve_data, curve_info ):
        """Process update for a single key"""
        strategy = self.core.get_current_strategy()

        # Get current value
        current_idx = curve_data['key_map'].get( time )
        if current_idx is None:
            return

        current_value = curve_data['values'][current_idx]
        # print( '___', current_value )

        # Calculate targets using strategy
        prev_target, next_target = strategy.calculate_target_value( 
            time, current_value, curve_data, curve_info )
        print( 'p___', prev_target )
        print( 'n___', next_target )
        prev_tangents, next_tangents = strategy.calculate_target_tangents( 
            time, curve_data, curve_info )

        # Store for blending
        if obj not in self.blend_data:
            self.blend_data[obj] = {}

        key_data = {
            'current_value': current_value,
            'prev_target': prev_target,
            'next_target': next_target,
            'prev_tangents': prev_tangents,
            'next_tangents': next_tangents
        }

        self.blend_data[obj]["{0}_{1}".format( curve, time )] = key_data

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

    def _before_handle_move( self, value ):
        """Start undo chunk and set move var, """

        # Calculate duration if we have a previous start time
        current_time = time.time()
        if hasattr( self, '_last_move_time' ):
            duration = ( current_time - self._last_move_time ) * 1000  # Convert to milliseconds
            num_curves = len( self.all_curves ) if self.all_curves else 0

            # Initialize or update running average
            if not hasattr( self, '_move_counts' ):
                self._move_counts = 1
                self._move_total_time = duration
            else:
                self._move_counts += 1
                self._move_total_time += duration

            avg_duration = self._move_total_time / self._move_counts
            '''
            print( 'Move duration: {:.2f}ms | Avg: {:.2f}ms | Count: {} | Curves: {}'.format( 
                duration, avg_duration, self._move_counts, num_curves ) )'''

        # Store new start time
        self._last_move_time = current_time

        #
        if not self.all_curves:
            return

        if not self.moved:
            # set moved
            self.moved = True
            # open chunk
            cmds.undoInfo( openChunk = True, cn = 'Blend_N' )
        # if qualified
        self.on_handle_move( value )

    def on_handle_move( self, value ):
        """
        HOOK
        Adjust animation values based on slider position.
        Now handles both selected key and current time scenarios.
        """
        # Convert to blend factor (-1 to 1)
        blend_factor = value / 100.0
        # Clear previous updates
        self.update_queue = []

        # Process each object
        for obj in self.selected_objects:
            self._process_object_updates( obj, blend_factor )

        # Execute batched updates
        if self.update_queue:
            self._execute_batch_updates()

        # should precombine selected objects and belnds nodes to list to explcicity only call dgdirty oncecombine
        cmds.dgdirty( self.blend_nodes if self.blend_nodes else [] )
        mel.eval( 'dgdirty;' )

    def _process_object_updates( self, obj, blend_factor ):
        """Process updates for a single object"""
        for curve in self.all_curves:
            if curve not in self.blend_data:
                continue

            # Get cached data
            curve_info = self.blend_data[curve]
            curve_data = curve_info['data']

            # Get keys to update
            selected_keys = cmds.keyframe( curve, q = True, sl = True, tc = True )
            times_to_update = selected_keys if selected_keys else [self.current_time]

            print( "\nProcess Object Updates:" )
            print( "Selected Keys:", selected_keys )
            print( "Times to Update:", times_to_update )
            print( "Current Time:", self.current_time )

            # If no keys selected, insert key first and update curve_data
            if not selected_keys:
                current_value = cmds.keyframe( curve,
                                            time = ( self.current_time, ),
                                            q = True,
                                            eval = True )[0]

                # Insert the key
                cmds.setKeyframe( curve, time = self.current_time, insert = True, value = current_value )

                # Update curve_data to include new key
                new_keys = cmds.keyframe( curve, q = True, tc = True ) or []
                new_values = cmds.keyframe( curve, q = True, vc = True ) or []

                # Update curve_data
                curve_data['keys'] = new_keys
                curve_data['values'] = new_values
                curve_data['key_map'] = {time: i for i, time in enumerate( new_keys )}

                # Update tangent data
                tangent_data = self._batch_get_tangents( curve )  # You'll need this method
                curve_data['tangents'] = tangent_data

            # Process in batches
            for i in range( 0, len( times_to_update ), self.core.batch_size ):
                batch = times_to_update[i:i + self.core.batch_size]
                for time in batch:
                    # Calculate new values using strategy
                    new_value, new_tangents = self._calculate_blend( 
                        curve_data, curve_info, time, blend_factor )

                    print( "New Value:", new_value )
                    print( "New Tangents:", new_tangents )

                    if new_value is not None:
                        self.update_queue.append( {
                            'curve': curve,
                            'time': time,
                            'value': new_value,
                            'tangents': new_tangents
                        } )
                        print( "Update Queued" )
                    else:
                        print( "No Update Queued - New Value was None" )

    def _batch_get_tangents( self, curve ):
        """Batch collect all tangent data for a curve"""
        return {
            'in_angles': cmds.keyTangent( curve, q = True, ia = True ) or [],
            'in_weights': cmds.keyTangent( curve, q = True, iw = True ) or [],
            'out_angles': cmds.keyTangent( curve, q = True, oa = True ) or [],
            'out_weights': cmds.keyTangent( curve, q = True, ow = True ) or [],
        }

    def _execute_batch_updates( self ):
        """Execute queued updates in optimized batches"""
        print( "\nExecute Batch Updates:" )
        print( "Update Queue:", self.update_queue )  # See all pending updates
        # Group updates by curve
        curve_updates = {}
        for update in self.update_queue:
            curve = update['curve']
            if curve not in curve_updates:
                curve_updates[curve] = []
            curve_updates[curve].append( update )

        print( "Curve Updates:", curve_updates )  # See how updates are grouped
        # Process each curve's updates
        for curve, updates in curve_updates.items():
            # Set keyframes and tangents one at a time
            for update in updates:
                print( "\nSetting Key:" )
                print( "Curve:", curve )
                print( "Time:", update['time'] )
                print( "Value:", update['value'] )
                # Set keyframe
                cmds.setKeyframe( curve,
                               time = update['time'],
                               value = update['value'] )

                # Set tangents if they exist
                if update['tangents']:
                    in_angle, in_weight = update['tangents']['in']
                    out_angle, out_weight = update['tangents']['out']

                    # Set tangents individually
                    cmds.keyTangent( curve,
                                  time = ( update['time'], update['time'] ),  # Time needs to be a tuple
                                  ia = in_angle,
                                  iw = in_weight )
                    cmds.keyTangent( curve,
                                  time = ( update['time'], update['time'] ),
                                  oa = out_angle,
                                  ow = out_weight )

    def _calculate_blend( self, curve_data, curve_info, time, blend_factor ):
        """Calculate blended values using current strategy"""
        print( "\nCalculate Blend:" )
        print( "Time:", time )
        print( "Blend Factor:", blend_factor )

        current_idx = curve_data['key_map'].get( time )
        print( "Current Index:", current_idx )

        # Get current value
        current_value = curve_data['values'][current_idx]

        # Get strategy
        strategy = self.core.get_current_strategy()
        curve_info['curve'] = curve_info.get( 'curve', '' )

        # Calculate target values using strategy
        prev_target, next_target = strategy.calculate_target_value( 
            time, current_value, curve_data, curve_info )

        # Calculate target tangents using strategy
        prev_tangents, next_tangents = strategy.calculate_target_tangents( 
            time, curve_data, curve_info )

        # Determine which target to use based on blend direction
        if blend_factor >= 0:
            target_value = next_target
            target_tangents = next_tangents
            ratio = blend_factor
        else:
            target_value = prev_target
            target_tangents = prev_tangents
            ratio = abs( blend_factor )

        # Calculate blended value
        new_value = current_value * ( 1 - ratio ) + target_value * ratio

        # Calculate blended tangents
        new_tangents = None
        if target_tangents:
            new_tangents = self._blend_tangents( 
                curve_data['tangents'],
                current_idx,
                target_tangents,
                ratio
            )

        return new_value, new_tangents

    def _blend_tangents( self, tangent_data, current_idx, target_tangents, ratio ):
        """Blend between current tangents and target tangents"""
        if not tangent_data:
            return None

        # Get current tangents
        curr_in_angle = tangent_data['in_angles'][current_idx]
        curr_in_weight = tangent_data['in_weights'][current_idx]
        curr_out_angle = tangent_data['out_angles'][current_idx]
        curr_out_weight = tangent_data['out_weights'][current_idx]

        # Blend with target tangents
        in_angle = self._blend_angles( curr_in_angle,
                                    target_tangents['in'][0], ratio )
        in_weight = curr_in_weight * ( 1 - ratio ) + \
                   target_tangents['in'][1] * ratio

        out_angle = self._blend_angles( curr_out_angle,
                                     target_tangents['out'][0], ratio )
        out_weight = curr_out_weight * ( 1 - ratio ) + \
                    target_tangents['out'][1] * ratio

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    def _blend_angles( self, start_angle, end_angle, ratio ):
        """Blend angles handling wrap-around"""
        # Handle angle wrap-around
        diff = end_angle - start_angle
        if abs( diff ) > 180:
            if diff > 0:
                end_angle -= 360
            else:
                end_angle += 360

        return start_angle * ( 1 - ratio ) + end_angle * ratio

    def __RELEASE__( self ):
        pass

    def _before_handle_release( self ):
        # if chunk, close
        #
        if self.moved:
            cmds.undoInfo( closeChunk = True, cn = 'Blend_N' )
        #
        self._reset_slider()
        self.on_handle_release()

    def on_handle_release( self ):
        """HOOK, Reset the state"""
        try:
            self._reset_state()
            self.core.clear_caches()
        finally:
            pass

    def _reset_slider( self ):
        """Reset slider to initial position"""
        self.valueChanged.disconnect( self._before_handle_move )
        self.setValue( 0 )
        # self.label.setText( '0%' )
        self.handle_label.hide()  # Initially hide the label
        self.valueChanged.connect( self._before_handle_move )

    def _reset_state( self ):
        """Reset all state variables to their default values"""
        self._selected_keys_cache = {}  # Clear the cache
        self._move_counts = 0  # Reset timing stats
        self._move_total_time = 0  # Reset timing stats
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = {}
        self.current_time = None
        self.selected_objects = []
        self.new_values = {}
        self.all_curves = []
        self.anim_layers = []
        self.blend_nodes = []  # mark as dirty for proper ui update
        self.blend_data = {}  # Reset blend data
        self.update_queue = []  # Clear update queue
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
                background-color: %s;
                border: none;
                border-radius: 4px;
                margin-bottom: 4px;
                margin-right: 4px;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
        """ % ( 
            QColor( 42, 42, 42 ).name(),
            QColor( 90, 90, 90 ).name(),
            QColor( 26, 26, 26 ).name()
        ) )
        self.toggle_button.clicked.connect( self._toggle_slider_visibility )

        # Get preference values with class defaults
        slider_width = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'slider_width',
            CustomSlider.get_default_width()
        )
        slider_range = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'slider_range',
            CustomSlider.get_default_range()
        )
        slider_tick_width = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'tick_width',
            CustomSlider.get_default_tick_width()
        )
        slider_tick_interval = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'tick_interval',
            CustomSlider.get_default_tick_interval()
        )
        slider_lock_margin = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'lock_release_margin',
            CustomSlider.get_default_lock_release_margin()
        )
        slider_click_value = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'groove_click_value',
            CustomSlider.get_default_groove_click_value()
        )
        self.slider = CustomSlider()
        self.slider.slider_width = slider_width
        self.slider.slider_range = slider_range
        self.slider.tick_width = slider_tick_width
        self.slider.tick_interval = slider_tick_interval
        self.slider.lock_release_margin = slider_lock_margin
        self.slider.groove_click_value = slider_click_value
        self.slider._update_stylesheet()  # Make sure to update the stylesheet after changing TICK_WIDTH

        # Add widgets to layout with alignment
        layout.addWidget( self.toggle_button, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft )
        layout.addWidget( self.slider, 0, QtCore.Qt.AlignCenter )

        self.setLayout( layout )
        self.adjustSize()

        # Load and apply saved slider visibility
        slider_visible = self.prefs.get_tool_pref( TOOL_NAME, 'slider_visible', True )
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
        self.prefs.set_tool_pref( TOOL_NAME, 'slider_visible', not current_visible )


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
                background-color: %s;
                border: 1px solid %s;
            }
            QGroupBox {
                background-color: transparent;
                border: none;
                color: %s;
                font-weight: bold;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            QRadioButton {
                color: %s;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator::unchecked {
                background-color: %s;
                border: 2px solid %s;
                border-radius: 7px;
            }
            QRadioButton::indicator::checked {
                background-color: %s;
                border: 2px solid %s;
                border-radius: 7px;
            }
            QRadioButton:checked {
                color: %s;
            }
            QRadioButton:hover {
                color: %s;
            }
        """ % ( 
            QColor( 43, 43, 43 ).name(),  # #2b2b2b
            QColor( 64, 64, 64 ).name(),  # #404040
            QColor( 204, 204, 204 ).name(),  # #cccccc
            QColor( 204, 204, 204 ).name(),  # #cccccc
            QColor( 43, 43, 43 ).name(),  # #2b2b2b
            QColor( 64, 64, 64 ).name(),  # #404040
            QColor( 75, 75, 75 ).name(),  # #4b4b4b
            QColor( 102, 102, 102 ).name(),  # #666666
            QColor( 255, 255, 255 ).name(),  # #ffffff
            QColor( 255, 255, 255 ).name()  # #ffffff
        )

    def leaveEvent( self, event ):
        """Handle mouse leaving the dialog window"""
        self._mouse_inside = False
        # Use a short timer to verify mouse hasn't re-entered before closing
        QtCore.QTimer.singleShot( 100, self._check_close )
        super( PreferencesDialog, self ).leaveEvent( event )
        # TODO: reset pref button to turn off hover color, set normal state.

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
                color: %s;
                font-weight: bold;
                font-size: 13px;
            }
        """ % QColor( 204, 204, 204 ).name() )

        main_layout.addWidget( title_label )

        # Width section
        width_label = QLabel( "SLIDER WIDTH" )
        width_label.setStyleSheet( """
            QLabel {
                color: %s;
                font-weight: bold;
                font-size: 13px;
                padding: 2px 10px 2px 10px;
                background-color: %s;
                border-radius: 6px;
            }
        """ % ( 
            QColor( 140, 140, 140 ).name(),
            QColor( 43, 43, 43 ).name()
        ) )
        main_layout.addWidget( width_label )

        # Width radio buttons frame
        width_frame = QtWidgets.QFrame()
        width_layout = QHBoxLayout( width_frame )
        width_layout.setSpacing( 10 )
        width_layout.setContentsMargins( 8, 4, 8, 4 )
        self.width_button_group = QButtonGroup( self )

        # Create radio buttons for width options
        width_items = list( CustomSlider.DEFAULT_SLIDER_WIDTH.items() )
        for i, item in enumerate( width_items ):
            size_name, value = item
            radio = QRadioButton( size_name )
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
                    background-color: %s;
                    border: 2px solid %s;
                    border-radius: 9px;
                }
                QRadioButton::indicator::checked {
                    background-color: %s;
                    border: 2px solid %s;
                    border-radius: 9px;
                }
            """ % ( 
                QColor( 43, 43, 43 ).name(),
                QColor( 64, 64, 64 ).name(),
                QColor( 75, 75, 75 ).name(),
                QColor( 102, 102, 102 ).name()
            ) )
            radio.width_value = value
            radio.size_name = size_name
            self.width_button_group.addButton( radio, i )
            width_layout.addWidget( radio )

        main_layout.addWidget( width_frame )

        # Range section
        range_label = QLabel( "SLIDER RANGE" )
        range_label.setStyleSheet( width_label.styleSheet() )  # Use same style as width label
        main_layout.addWidget( range_label )

        # Range radio buttons frame
        range_frame = QtWidgets.QFrame()
        range_layout = QHBoxLayout( range_frame )
        range_layout.setSpacing( 10 )
        range_layout.setContentsMargins( 8, 4, 8, 4 )
        self.range_button_group = QButtonGroup( self )

        # Create radio buttons for range options - sorted
        range_items = list( CustomSlider.DEFAULT_RANGE.items() )
        # Sort by converting key to int for comparison
        range_items.sort( key = lambda x: int( x[0] ) )
        for i, item in enumerate( range_items ):
            range_name, value = item
            radio = QRadioButton( range_name )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.range_value = value
            radio.range_name = range_name
            self.range_button_group.addButton( radio, i )
            range_layout.addWidget( radio )

        main_layout.addWidget( range_frame )

        # Tick Width section
        tick_width_label = QLabel( "TICK WIDTH" )
        tick_width_label.setStyleSheet( width_label.styleSheet() )  # Use same style as width label
        main_layout.addWidget( tick_width_label )

        # Tick width radio buttons frame
        tick_frame = QtWidgets.QFrame()
        tick_layout = QHBoxLayout( tick_frame )
        tick_layout.setSpacing( 10 )
        tick_layout.setContentsMargins( 8, 4, 8, 4 )
        self.tick_width_button_group = QButtonGroup( self )

        # Sort tick width options by their values (thin to thick)
        tick_items = list( CustomSlider.DEFAULT_TICK_WIDTH.items() )
        # Sort by value
        tick_items.sort( key = lambda x: x[1] )
        for i, item in enumerate( tick_items ):
            width_name, value = item
            radio = QRadioButton( width_name.title() )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.tick_width_value = value
            radio.tick_width_name = width_name
            self.tick_width_button_group.addButton( radio, i )
            tick_layout.addWidget( radio )

        main_layout.addWidget( tick_frame )

        # Tick Interval
        tick_interval_label = QLabel( "TICK INTERVAL" )
        tick_interval_label.setStyleSheet( width_label.styleSheet() )
        main_layout.addWidget( tick_interval_label )

        # Tick interval radio buttons frame
        interval_frame = QtWidgets.QFrame()
        interval_layout = QHBoxLayout( interval_frame )
        interval_layout.setSpacing( 10 )
        interval_layout.setContentsMargins( 8, 4, 8, 4 )
        self.tick_interval_button_group = QButtonGroup( self )

        # Create radio buttons for interval options
        interval_items = list( CustomSlider.DEFAULT_TICK_INTERVAL.items() )
        interval_items.sort( key = lambda x: int( x[0] ) )
        for i, item in enumerate( interval_items ):
            interval_name, value = item
            radio = QRadioButton( interval_name )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.interval_value = value
            radio.interval_name = interval_name
            self.tick_interval_button_group.addButton( radio, i )
            interval_layout.addWidget( radio )

        main_layout.addWidget( interval_frame )

        # After tick interval section
        lock_margin_label = QLabel( "LOCK MARGIN" )
        lock_margin_label.setStyleSheet( width_label.styleSheet() )
        main_layout.addWidget( lock_margin_label )

        # Lock margin radio buttons frame
        margin_frame = QtWidgets.QFrame()
        margin_layout = QHBoxLayout( margin_frame )
        margin_layout.setSpacing( 10 )
        margin_layout.setContentsMargins( 8, 4, 8, 4 )
        self.lock_margin_button_group = QButtonGroup( self )

        # Create radio buttons for margin options
        margin_items = list( CustomSlider.DEFAULT_LOCK_RELEASE_MARGIN.items() )
        margin_items.sort( key = lambda x: int( x[0] ) )
        for i, item in enumerate( margin_items ):
            margin_name, value = item
            radio = QRadioButton( margin_name )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.margin_value = value
            radio.margin_name = margin_name
            self.lock_margin_button_group.addButton( radio, i )
            margin_layout.addWidget( radio )

        main_layout.addWidget( margin_frame )

        # After lock margin section
        click_value_label = QLabel( "GROOVE CLICK VALUE" )
        click_value_label.setStyleSheet( width_label.styleSheet() )
        main_layout.addWidget( click_value_label )

        # Click value radio buttons frame
        click_value_frame = QtWidgets.QFrame()
        click_value_layout = QHBoxLayout( click_value_frame )
        click_value_layout.setSpacing( 10 )
        click_value_layout.setContentsMargins( 8, 4, 8, 4 )
        self.click_value_button_group = QButtonGroup( self )

        # Create radio buttons for click value options
        click_value_items = list( CustomSlider.DEFAULT_GROOVE_CLICK_VALUE.items() )
        click_value_items.sort( key = lambda x: int( x[0] ) )
        for i, item in enumerate( click_value_items ):
            value_name, value = item
            radio = QRadioButton( value_name )
            radio.setStyleSheet( self.width_button_group.buttons()[0].styleSheet() )
            radio.click_value = value
            radio.click_value_name = value_name
            self.click_value_button_group.addButton( radio, i )
            click_value_layout.addWidget( radio )

        main_layout.addWidget( click_value_frame )

        # Connect signals
        self.width_button_group.buttonClicked.connect( self._on_width_changed )
        self.range_button_group.buttonClicked.connect( self._on_range_changed )
        self.tick_width_button_group.buttonClicked.connect( self._on_tick_width_changed )
        self.tick_interval_button_group.buttonClicked.connect( self._on_tick_interval_changed )
        self.lock_margin_button_group.buttonClicked.connect( self._on_lock_margin_changed )
        self.click_value_button_group.buttonClicked.connect( self._on_click_value_changed )

        self.setLayout( main_layout )
        self.setMinimumWidth( 200 )
        self.adjustSize()

    def _load_current_values( self ):
        """Load current preference values and select appropriate radio buttons"""
        # Get current values from preferences with CustomSlider class defaults
        current_width = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'slider_width',
            CustomSlider.get_default_width()
        )
        current_range = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'slider_range',
            CustomSlider.get_default_range()
        )
        current_tick_width = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'tick_width_name',  # Note: getting name, not value
            CustomSlider.get_default_tick_width_txt()
        )
        current_tick_interval = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'tick_interval',
            CustomSlider.get_default_tick_interval()
        )
        current_lock_margin = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'lock_release_margin',
            CustomSlider.get_default_lock_release_margin()
        )
        current_click_value = self.prefs.get_tool_pref( 
            TOOL_NAME,
            'groove_click_value',
            CustomSlider.get_default_groove_click_value()
        )
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

        # Select appropriate tick width radio button
        for button in self.tick_width_button_group.buttons():
            if button.tick_width_name == current_tick_width:
                button.setChecked( True )
                break
        # Select appropriate tick interval radio button
        for button in self.tick_interval_button_group.buttons():
            if button.interval_value == current_tick_interval:
                button.setChecked( True )
                break
        # Select appropriate lock margin radio button
        for button in self.lock_margin_button_group.buttons():
            if button.margin_value == current_lock_margin:
                button.setChecked( True )
                break
        # Select appropriate click value radio button
        for button in self.click_value_button_group.buttons():
            if button.click_value == current_click_value:
                button.setChecked( True )
                break

    def _on_width_changed( self, radio_button ):
        """Handle width radio button selection"""
        width_value = radio_button.width_value
        size_name = radio_button.size_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'slider_width', width_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'slider_width_name', size_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.slider_width = width_value
            parent_dialog.adjustSize()

    def _on_range_changed( self, radio_button ):
        """Handle range radio button selection"""
        range_value = radio_button.range_value
        range_name = radio_button.range_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'slider_range', range_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'slider_range_name', range_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.slider_range = range_value

    def _on_tick_width_changed( self, radio_button ):
        """Handle tick width radio button selection"""
        width_value = radio_button.tick_width_value
        width_name = radio_button.tick_width_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'tick_width', width_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'tick_width_name', width_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog and parent_dialog.slider:
            parent_dialog.slider.tick_width = width_value
            parent_dialog.slider._update_stylesheet()

    def _on_tick_interval_changed( self, radio_button ):
        """Handle tick interval radio button selection"""
        interval_value = radio_button.interval_value
        interval_name = radio_button.interval_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'tick_interval', interval_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'tick_interval_name', interval_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.tick_interval = interval_value

    def _on_lock_margin_changed( self, radio_button ):
        """Handle lock release margin radio button selection"""
        margin_value = radio_button.margin_value
        margin_name = radio_button.margin_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'lock_release_margin', margin_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'lock_release_margin_name', margin_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.lock_release_margin = margin_value

    def _on_click_value_changed( self, radio_button ):
        """Handle groove click value radio button selection"""
        click_value = radio_button.click_value
        click_value_name = radio_button.click_value_name

        # Save to preferences
        self.prefs.set_tool_pref( TOOL_NAME, 'groove_click_value', click_value )
        self.prefs.set_tool_pref( TOOL_NAME, 'groove_click_value_name', click_value_name )

        # Update slider immediately
        parent_dialog = self.parent()
        if parent_dialog:
            parent_dialog.slider.groove_click_value = click_value


class WebrToolsPrefs( object ):
    """
    Manages preferences for WebrTools across different platforms.
    Handles reading, writing, and default values for tool-specific preferences.
    """

    def __init__( self ):
        self.prefs_file = 'WebrToolsPrefs.json'
        self.prefs_path = self._get_prefs_path()
        # Initialize default preferences using CustomSlider class defaults
        self.default_prefs = {
            TOOL_NAME: {
                # Visibility
                'slider_visible': True,

                # Width preferences
                'slider_width': CustomSlider.get_default_width(),
                'slider_width_name': CustomSlider.get_default_width_txt(),

                # Range preferences
                'slider_range': CustomSlider.get_default_range(),
                'slider_range_name': CustomSlider.get_default_range_txt(),

                # Tick width preferences
                'tick_width': CustomSlider.get_default_tick_width(),
                'tick_width_name': CustomSlider.get_default_tick_width_txt(),

                # Tick interval preferences
                'tick_interval': CustomSlider.get_default_tick_interval(),
                'tick_interval_name': CustomSlider.get_default_tick_interval_txt(),

                # Lock release margin preferences
                'lock_release_margin': CustomSlider.get_default_lock_release_margin(),
                'lock_release_margin_name': CustomSlider.get_default_lock_release_margin_txt(),

                # Groove click value preferences
                'groove_click_value': CustomSlider.get_default_groove_click_value(),
                'groove_click_value_name': CustomSlider.get_default_groove_click_value_txt()
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


def desaturate_color( color, amount = 0.5 ):
    """
    Desaturate a color by reducing its saturation
    Args:
        color (QColor): Original color
        amount (float): Amount to desaturate, 0.0 to 1.0 where 1.0 is fully desaturated
    Returns:
        QColor: New desaturated color
    """
    # Create a copy of the color to modify
    new_color = QColor( color )

    # Convert to HSV
    h, s, v, a = new_color.getHsv()

    # Reduce saturation by the specified amount
    # Original saturation is 0-255, so we multiply the reduction
    new_s = int( s * ( 1.0 - amount ) )

    # Keep saturation in valid range
    new_s = max( 0, min( 255, new_s ) )

    # Set new HSV values and return
    new_color.setHsv( h, new_s, v, a )
    return new_color


def saturate_color( color, amount = 0.5 ):
    """
    Increase saturation of a color
    Args:
        color (QColor): Original color
        amount (float): Amount to saturate, 0.0 to 1.0 where 1.0 is fully saturated
    Returns:
        QColor: New saturated color
    """
    # Create a copy of the color to modify
    new_color = QColor( color )

    # Convert to HSV
    h, s, v, a = new_color.getHsv()

    # Increase saturation by the specified amount
    # Calculate how much room we have to increase (255 is max)
    room_to_increase = 255 - s
    increase = int( room_to_increase * amount )
    new_s = s + increase

    # Keep saturation in valid range
    new_s = max( 0, min( 255, new_s ) )

    # Set new HSV values and return
    new_color.setHsv( h, new_s, v, a )
    return new_color


def value_color( color, value_factor, desat_amount = 0 ):
    """
    Adjust the value (brightness) and optionally desaturate a color
    Args:
        color (QColor): Original color
        value_factor (float): Value to multiply current value by (0.0 to 1.0 darkens, >1.0 brightens)
        desat_amount (float): Amount to desaturate, 0.0 to 1.0 where 1.0 is fully desaturated
    Returns:
        QColor: New color with adjusted value and saturation
    """
    new_color = QColor( color )
    h, s, v, a = new_color.getHsv()

    # Adjust value while keeping it in valid range (0-255)
    new_v = int( v * value_factor )
    new_v = max( 0, min( 255, new_v ) )

    # Adjust saturation if specified
    if desat_amount > 0:
        new_s = int( s * ( 1.0 - desat_amount ) )
        new_s = max( 0, min( 255, new_s ) )
    else:
        new_s = s

    new_color.setHsv( h, new_s, new_v, a )
    return new_color


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
