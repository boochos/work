from PySide2.QtGui import QColor


class ThemeColorManager:
    """
    Manages color themes and variations for UI elements.
    Provides methods to generate different color states for UI components.
    """
    # TODO: gonna need icon module to use for buttons, make one, workout logic.

    # Default colors from the original code
    DEFAULT_COLORS = {
        'blue': QColor( 60, 112, 175 ),  # Original blue
        'blueLight': QColor( 60, 147, 176 ),  # Lighter blue
        'red': QColor( 175, 67, 67 ),  # Original red
        'teal': QColor( 83, 181, 178 ),  # Teal
        'purple': QColor( 89, 95, 179 ),  # Purple
        'green': QColor( 82, 171, 92 ),  # Original green
        'greenLight': QColor( 120, 176, 60 ),  # Lighter green
        'magenta': QColor( 149, 60, 176 ),  # Magenta
        'orange': QColor( 175, 120, 48 ),  # Orange
        'yellow': QColor( 175, 164, 60 ),  # Yellow
        'pink': QColor( 189, 115, 185 ),  # Pink
        'grey': QColor( 147, 150, 150 ),  # Grey
        'greyDark': QColor( 109, 110, 110 ),  # Dark grey
        'greyDarkr': QColor( 75, 77, 77 ),  # Dark grey
        'greyDarker': QColor( 45, 47, 47 ),  # Dark grey
        'greyDarkest': QColor( 35, 37, 37 ),  # Dark grey
        'greyMid': QColor( 150, 150, 150 ),  # New mid grey
        'greyDarkr1': QColor( 45, 45, 45 ),  # Dark grey
        'white': QColor( 255, 255, 255 ),  # Dark grey
        'greyDarkest1': QColor( 26, 26, 26 ),  # Dark grey
    }

    # Default UI colors
    DEFAULT_UI_COLORS = {
        'background': QColor( 43, 43, 43 ),  # Dark background
        'border': QColor( 26, 26, 26 ),  # Dark border
        'groove': QColor( 55, 55, 55 ),  # Groove color
        'control': QColor( 80, 43, 43 )  # Control background
    }

    # Default adjustment values for different states
    DEFAULT_ADJUSTMENTS = {
        'disabled': {'value': 0.7, 'desat': 0.6},  # Darkest (0.7)
        'pressed': {'value': 0.8, 'desat': 0.0},  # Dark (0.8)
        'focus': {'value': 1.1, 'desat': 0.0},  # Bright (1.1)
        'active': {'value': 1.15, 'desat': 0.0},  # Brighter (1.15)
        'hover': {'value': 1.2, 'desat': 0.0},  # Even brighter (1.2)
        'selected': {'value': 1.3, 'desat': 0.0},  # Very bright (1.3)
        'warning': {'value': 1.4, 'desat': 0.0},  # Extra bright (1.4)
        'error': {'value': 1.5, 'desat': 0.0},  # Brightest (1.5)
    }

    def __init__( self, color_name = 'blue' ):
        """
        Initialize with a base color.
        Args:
            color_name (str|QColor): Base color name from DEFAULT_COLORS or QColor object
        """
        # TODO: cleanup ui colors, the greys, should called same way as the rest of the base color variants are called
        # TODO: rename base color variant naming, should follow naming convention, lighter01, lighter02, increasing in brightness, reverse for darkner colors ie. darker01. 01 being closest to base
        # TODO: remove all individually called colors in the stylesheets, they should come from the predefined base color variants, or grey variants
        # TODO: rename DEFAULT_ADJUSTMENts, DEFAULT_VARIANTS
        # TODO: think about adding a complimentary accent color, opposite side on the color wheel ie orange/blue
        if isinstance( color_name, QColor ):
            self._base_color = color_name
        else:
            self._base_color = self.DEFAULT_COLORS.get( color_name, self.DEFAULT_COLORS['blue'] )
        self._adjustments = self.DEFAULT_ADJUSTMENTS.copy()

    @classmethod
    def get_color( cls, color_name ):
        """
        Get a color from the default colors.
        Args:
            color_name (str): Name of the color from DEFAULT_COLORS
        Returns:
            QColor: The requested color or blue if not found
        """
        return cls.DEFAULT_COLORS.get( color_name, cls.DEFAULT_COLORS['blue'] )

    @classmethod
    def get_ui_color( cls, color_name ):
        """
        Get a UI color from the default UI colors.
        Args:
            color_name (str): Name of the color from DEFAULT_UI_COLORS
        Returns:
            QColor: The requested color or background if not found
        """
        return cls.DEFAULT_UI_COLORS.get( color_name, cls.DEFAULT_UI_COLORS['background'] )

    @classmethod
    def list_colors( cls ):
        """
        Get a list of available color names.
        Returns:
            list: Names of all available default colors
        """
        return list( cls.DEFAULT_COLORS.keys() )

    @property
    def base_color( self ):
        """Get the base color"""
        return self._base_color

    @base_color.setter
    def base_color( self, color ):
        """Set the base color from name or QColor"""
        if isinstance( color, str ):
            self._base_color = self.DEFAULT_COLORS.get( color, self._base_color )
        else:
            self._base_color = QColor( color )

    def set_state_adjustment( self, state, value_factor, desat_amount = 0.0 ):
        """
        Set custom adjustment values for a state.
        Args:
            state (str): State name ('hover', 'pressed', etc.)
            value_factor (float): Brightness adjustment (0.0-2.0)
            desat_amount (float): Desaturation amount (0.0-1.0)
        """
        self._adjustments[state] = {
            'value': value_factor,
            'desat': desat_amount
        }

    def get_color_for_state( self, state ):
        """
        Get the adjusted color for a specific state.
        Args:
            state (str): State name ('hover', 'pressed', etc.)
        Returns:
            QColor: Adjusted color for the state
        """
        if state not in self._adjustments:
            return self._base_color

        adj = self._adjustments[state]
        return self._adjust_color( 
            self._base_color,
            adj['value'],
            adj['desat']
        )

    def get_stylesheet_colors( self, widget_type = 'QPushButton' ):
        """
        Get a complete stylesheet with all state colors.
        Args:
            widget_type (str): Qt widget class name
        Returns:
            str: Complete stylesheet with all states
        """
        colors = {
            state: self.get_color_for_state( state ).name()
            for state in self._adjustments.keys()
        }

        if widget_type == 'QPushButton':
            return self._get_button_stylesheet( colors )
        elif widget_type == 'QPushButton_alt1':  # Add this new condition
            return self._get_button_alt1_stylesheet( colors )
        elif widget_type == 'QLineEdit':
            return self._get_line_edit_stylesheet( colors )
        elif widget_type == 'QListWidget':  # Add this new condition
            return self._get_list_widget_stylesheet( colors )
        elif widget_type == 'QTreeWidget':  # Add this new condition
            return self._get_tree_widget_stylesheet( colors )
        elif widget_type == 'QRadioButton':  # Add this new condition
            return self._get_radio_button_stylesheet( colors )
        elif widget_type == 'QComboBox':  # Add this new condition
            return self._get_combo_box_stylesheet( colors )
        elif widget_type == 'QLabel_title':  # Add this new condition
            return self._get_label_title_stylesheet( colors )
        elif widget_type == 'QLabel_subtitle':  # Add this new condition
            return self._get_label_title_stylesheet( colors )
        elif widget_type == 'QLabel':  # Add this new condition
            return self._get_label_stylesheet( colors )
        elif widget_type == 'QMenu':  # Add this new condition
            return self._get_menu_stylesheet( colors )
        # Add more widget types as needed
        return ""

    def get_all_colors( self ):
        """
        Get all color variations as a dictionary.
        Returns:
            dict: State names mapped to their QColors
        """
        return {
            state: self.get_color_for_state( state )
            for state in self._adjustments.keys()
        }

    def _adjust_color( self, color, value_factor, desat_amount ):
        """
        Adjust a color's brightness and saturation.
        Args:
            color (QColor): Color to adjust
            value_factor (float): Brightness multiplier
            desat_amount (float): Desaturation amount
        Returns:
            QColor: Adjusted color
        """
        new_color = QColor( color )
        h, s, v, a = new_color.getHsv()

        # Adjust value (brightness)
        new_v = int( v * value_factor )
        new_v = max( 0, min( 255, new_v ) )

        # Adjust saturation
        if desat_amount > 0:
            new_s = int( s * ( 1.0 - desat_amount ) )
            new_s = max( 0, min( 255, new_s ) )
        else:
            new_s = s

        new_color.setHsv( h, new_s, new_v, a )
        return new_color

    def _get_button_stylesheet( self, colors ):
        """Generate stylesheet for QPushButton"""
        return """
            QPushButton {
                background-color: %s;
                border: 1px solid %s;
                border-radius: 4px;
                padding: 5px 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: %s;
                border: 1px solid %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
            QPushButton:checked {
                background-color: %s;
            }
            QPushButton:disabled {
                background-color: %s;
                border-color: %s;
            }
            QPushButton:focus {
                border-color: %s;
                border-width: 2px;
            }
        """ % ( 
            self.base_color.name(),
            colors['disabled'],
            self.base_color.name(),
            colors['hover'],
            colors['pressed'],
            colors['selected'],
            colors['disabled'],
            self._adjust_color( self.base_color, 0.5, 0.8 ).name(),
            colors['focus']
        )

    def _get_button_alt1_stylesheet( self, colors ):
        """Generate stylesheet for alternate button style"""
        return """
            QPushButton {
                background-color: transparent;
                color: %s;
                border-radius: 4px;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: %s;
            }
        """ % ( 
            self.get_color( 'greyDark' ).name(),
            colors['error']
        )

    def _get_line_edit_stylesheet( self, colors ):
        """Generate stylesheet for QLineEdit"""
        return """
            QLineEdit {
                border: 1px solid %s;
                border-radius: 4px;
                padding: 3px 5px;
                color: white;
            }
            QLineEdit:hover {
                border-color: %s;
            }
            QLineEdit:focus {
                border-color: %s;
                border-width: 1px;
            }
            QLineEdit:disabled {
                background-color: %s;
                border-color: %s;
            }
        """ % ( 
            self._adjust_color( self.base_color, 0.4, 0.3 ).name(),  # Changed from 0.6 to 0.4 for darker border
            self.get_color( 'greyDarkr' ).name(),
            colors['disabled'],
            self.get_color( 'grey' ).name(),
            self._adjust_color( self.base_color, 0.4, 0.8 ).name()
        )

    def _get_list_widget_stylesheet( self, colors ):
        """Generate stylesheet for QListWidget"""
        return """
            QListWidget {
                color: %s;
                font-size: 13px;
            }
            QListWidget:focus {
                border: 1px solid %s;
            }
            QListWidget::item:hover {
                background-color: rgb(65, 65, 65);  /* Slightly lighter than base for hover */
            }
            QListWidget::item:selected {
                background-color: %s;
            }
        """ % ( 
            self.get_color( 'greyMid' ).name(),  # for list item text
            colors['disabled'],  # for focus border
            colors['disabled']  # for selected item
        )

    def _get_tree_widget_stylesheet( self, colors ):
        """Generate stylesheet for QTreeWidget"""
        return """
            QTreeWidget {
                color: %s;
                font-size: 13px;
            }
            QTreeWidget:focus {
                border: 1px solid %s;
            }
            QTreeWidget::item:hover {
                background-color: rgb(65, 65, 65);  /* Slightly lighter than base for hover */
            }
            QTreeWidget::item:selected {
                background-color: %s;
            }
            QTreeWidget::branch:selected {
                background-color: %s;
            }
            QTreeWidget QHeaderView::section {
                color: %s;
                background-color: %s;
                padding: 4px;
                font-size: 11px;  /* Added for header too */
            }
        """ % ( 
            self.get_color( 'greyMid' ).name(),  # for tree item text
            colors['disabled'],  # for focus border
            colors['disabled'],  # for selected item
            colors['disabled'],  # for selected branch
            colors['disabled'],
            self.get_color( 'greyDarkr1' ).name()  # for header background
        )

    def _get_radio_button_stylesheet( self, colors ):
        """Generate stylesheet for QRadioButton"""
        return """
            QRadioButton {
                color: %s;
            }
            QRadioButton::indicator {
                width: 9px;
                height: 9px;
                border-radius: 4px;
                background-color: %s;
            }
            QRadioButton::indicator:hover {
                border-radius: 4px;
                background-color: %s;
            }
            QRadioButton::indicator:checked {
                border-radius: 4px;
                background-color: %s;
            }
        """ % ( 
            self.get_color( 'grey' ).name(),
            self.get_color( 'greyDarkest' ).name(),
            self.get_color_for_state( 'disabled' ).name(),
            self.base_color.name()
        )

    def _get_combo_box_stylesheet( self, colors ):
        """Generate stylesheet for QComboBox"""
        return """
            QComboBox {
                color: %s;
                background-color: %s;
                selection-color: %s;
                selection-background-color: %s;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                color: %s;
                selection-color: %s;
                selection-background-color: %s;
                background-color: rgb(45, 45, 45);
                font-size: 12px;
            }
        """ % ( 
            self.get_color( 'grey' ).name(),  # Main text color
            self.get_color( 'greyDarkr1' ).name(),  # Background color
            self.get_color( 'grey' ).name(),  # Selected text color
            colors['disabled'],  # Selected background color
            self.get_color( 'grey' ).name(),  # Dropdown text color
            self.get_color( 'white' ).name(),  # Selected dropdown text color
            colors['disabled']  # Selected dropdown background color
        )

    def _get_label_title_stylesheet( self, colors ):
        """Generate stylesheet for title label"""
        return """
            QLabel {
                color: %s;
                font-weight: normal;
            }
        """ % ( 
            colors['hover']
        )

    def _get_label_subtitle_stylesheet( self, colors ):
        """Generate stylesheet for title label"""
        return """
            QLabel {
                color: %s;
                font-weight: normal;
            }
        """ % ( 
            colors['pressed']
        )

    def _get_label_stylesheet( self, colors ):
        """Generate stylesheet for standard QLabel"""
        return """
            QLabel {
                color: %s;
                font-size: 12px;
            }
        """ % ( 
            self.get_color( 'greyMid' ).name()
        )

    def _get_menu_stylesheet( self, colors ):
        """Generate stylesheet for context menu"""
        return """
            QMenu::item:selected {
                background-color: %s;
            }
        """ % ( 
            colors['disabled']  # Selection background color
        )
