from PySide2.QtGui import QColor


class ThemeColorManager:
    """Manages themed color variants with simple dictionary access."""

    # TODO: think about adding a complimentary accent color, opposite side on the color wheel ie orange/blue

    def __init__( self, color_name = 'blue' ):
        # Define base colors dictionary
        self._base_colors = {
            'blue': ( 60, 112, 175 ),  # Original blue
            'blueLight': ( 60, 147, 176 ),  # Lighter blue
            'red': ( 175, 67, 67 ),  # Original red
            'teal': ( 83, 181, 178 ),  # Teal
            'purple': ( 101, 76, 228 ),  # Purple
            'green': ( 82, 171, 92 ),  # Original green
            'greenLight': ( 120, 176, 60 ),  # Lighter green
            'magenta': ( 149, 60, 176 ),  # Magenta
            'orange': ( 175, 120, 48 ),  # Orange
            'yellow': ( 175, 164, 60 ),  # Yellow
            'pink': ( 189, 115, 185 ),  # Pink
        }
        '''
        # Get base color tuple
        self._base = self._base_colors.get( color_name, self._base_colors['blue'] )

        # Generate and store all colors
        self.themed = self._generate_colors()
        '''
        self.set_theme( color_name )

    def _adjust_color( self, rgb_tuple, value_factor, desat_amount = 0.0 ):
        """Adjust rgb color values."""
        # Convert to QColor for HSV manipulation
        color = QColor( *rgb_tuple )
        h, s, v, a = color.getHsv()

        # Adjust value (brightness)
        new_v = min( 255, max( 0, int( v * value_factor ) ) )

        # Adjust saturation if needed
        if desat_amount > 0:
            new_s = min( 255, max( 0, int( s * ( 1.0 - desat_amount ) ) ) )
        else:
            new_s = s

        # Convert back to RGB
        color.setHsv( h, new_s, new_v, a )
        return ( color.red(), color.green(), color.blue() )

    def _generate_colors( self ):
        """Generate all theme colors as rgb strings."""
        colors = {
            # Theme color variants
            'base': 'rgb%s' % str( self._base ),
            #
            'white': 'rgb(255, 255, 255)',

            # Brighter
            'brighter_00': 'rgb%s' % str( self._adjust_color( self._base, 1.05 ) ),
            'brighter_01': 'rgb%s' % str( self._adjust_color( self._base, 1.1 ) ),  # 1
            'brighter_02': 'rgb%s' % str( self._adjust_color( self._base, 1.15 ) ),  # 2
            'brighter_03': 'rgb%s' % str( self._adjust_color( self._base, 1.2 ) ),  # 3
            'brighter_04': 'rgb%s' % str( self._adjust_color( self._base, 1.3 ) ),  # 4
            'brighter_05': 'rgb%s' % str( self._adjust_color( self._base, 1.4 ) ),  # 5
            'brighter_06': 'rgb%s' % str( self._adjust_color( self._base, 1.5 ) ),  # 6
            'brighter_07': 'rgb%s' % str( self._adjust_color( self._base, 1.6 ) ),  # 7 brightest

            # Darker
            'darker_00': 'rgb%s' % str( self._adjust_color( self._base, 0.9, 0.1 ) ),  # 1
            'darker_01': 'rgb%s' % str( self._adjust_color( self._base, 0.85, 0.4 ) ),  # 1
            'darker_02': 'rgb%s' % str( self._adjust_color( self._base, 0.7, 0.6 ) ),  # 2
            'darker_03': 'rgb%s' % str( self._adjust_color( self._base, 0.6, 0.6 ) ),  # 3
            'darker_04': 'rgb%s' % str( self._adjust_color( self._base, 0.55, 0.6 ) ),  # 4
            'darker_05': 'rgb%s' % str( self._adjust_color( self._base, 0.5, 0.7 ) ),  # 5
            'darker_06': 'rgb%s' % str( self._adjust_color( self._base, 0.4, 0.8 ) ),  # 6
            'darker_07': 'rgb%s' % str( self._adjust_color( self._base, 0.3, 0.9 ) ),  # 7 darkest

            # Greys from lightest to darkest
            'grey_00': 'rgb(240, 240, 240)',
            'grey_01': 'rgb(230, 230, 230)',
            'grey_02': 'rgb(200, 200, 200)',
            'grey_03': 'rgb(170, 170, 170)',
            'grey_04': 'rgb(147, 150, 150)',  #
            'grey_05': 'rgb(109, 110, 110)',  #
            'grey_06': 'rgb(75, 77, 77)',  #
            'grey_07': 'rgb(55, 55, 55)',  # 7
            'grey_08': 'rgb(43, 43, 43)',  # 8
            'grey_09': 'rgb(35, 37, 37)',  # 9
            'grey_10': 'rgb(26, 26, 26)',  # 10

            # bg
            'bg': 'rgb(56, 56, 56)',
            'bg_light': 'rgb(68, 68, 68)',
        }
        return colors

    def set_theme( self, color_name ):
        """set theme color, generate new colors"""
        # Get base color tuple
        self._base = self._base_colors.get( color_name, self._base_colors['blue'] )

        # Generate and store all colors
        self.themed = self._generate_colors()


class StylesheetManager:
    """Generates stylesheets using ThemeColorManager colors."""

    def __init__( self, color_name = 'blue' ):
        # Create theme manager internally if given a string
        if isinstance( color_name, str ):
            self.theme_manager = ThemeColorManager( color_name )
            self.colors = self.theme_manager.themed
        else:
            # Still support passing a theme manager directly
            self.colors = color_name.themed

    def get_stylesheet_colors( self, widget_type = 'QPushButton' ):
        """
        Get a complete stylesheet for specified widget type.
        Args:
            widget_type (str): Qt widget class name
        Returns:
            str: Complete stylesheet
        """
        if widget_type == 'QPushButton':
            return self.get_button_stylesheet()
        elif widget_type == 'QPushButton_text':
            return self.get_button_text_stylesheet()
        elif widget_type == 'QPushButton_pref':
            return self.get_button_pref_stylesheet()
        elif widget_type == 'QLineEdit':
            return self.get_line_edit_stylesheet()
        elif widget_type == 'QListWidget':
            return self.get_list_widget_stylesheet()
        elif widget_type == 'QTreeWidget':
            return self.get_tree_widget_stylesheet()
        elif widget_type == 'QRadioButton':
            return self.get_radio_button_stylesheet()
        elif widget_type == 'QComboBox':
            return self.get_combo_box_stylesheet()
        elif widget_type == 'QLabel_title':
            return self.get_label_title_stylesheet()
        elif widget_type == 'QLabel_subtitle':
            return self.get_label_subtitle_stylesheet()
        elif widget_type == 'QLabel_compact':
            return self.get_label_compact_stylesheet()
        elif widget_type == 'QLabel':
            return self.get_label_stylesheet()
        elif widget_type == 'QMenu':
            return self.get_menu_context_stylesheet()
        elif widget_type == 'QToolButton_collapse':
            return self.get_button_collapse_stylesheet()
        elif widget_type == 'QFrame':
            return self.get_separator_stylesheet()
        return ""

    def get_button_stylesheet( self ):
        return """
            QPushButton {
                background-color: %s;
                border: 1px solid %s;
                border-radius: 4px;
                padding: 5px 15px;
                color: white;
                font-size: 12px;
                letter-spacing: 3.0px;
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
            self.colors['base'],
            self.colors['grey_10'],
            self.colors['base'],
            self.colors['brighter_07'],
            self.colors['brighter_02'],
            self.colors['brighter_04'],
            self.colors['darker_02'],
            self.colors['darker_05'],
            self.colors['brighter_02']
            # letter-spacing: 1.5px;
        )

    def get_button_text_stylesheet( self ):
        return """
            QPushButton {
                background-color: transparent;
                color: %s;
                border-radius: 4px;
                border: none;
                font-size: 12px;
                letter-spacing: 3.0px;
            }
            QPushButton:hover {
                color: %s;
            }
        """ % ( 
            self.colors['grey_03'],
            self.colors['brighter_06']
        )

    def get_button_pref_stylesheet( self ):
        return """
            QPushButton {
                border: 1px solid %s;
                background-color: %s;
                border-radius: 2px;
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
            self.colors['bg'],
            self.colors['bg_light'],  # QColor( 42, 42, 42 ).name(),
            self.colors['grey_08'],  # QColor( 90, 90, 90 ).name(),
            self.colors['grey_04']  # QColor( 26, 26, 26 ).name()
        )

    def get_line_edit_stylesheet( self ):
        return """
            QLineEdit {
                border: 1px solid %s;
                border-radius: 4px;
                padding: 3px 5px;
                color: %s;
                font-size: 13px;
                letter-spacing: 1.0px;
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
            self.colors['darker_06'],
            self.colors['grey_03'],
            self.colors['darker_05'],
            self.colors['darker_02'],
            self.colors['grey_04'],
            self.colors['darker_05']
        )

    def get_list_widget_stylesheet( self ):
        return """
            QListWidget {
                border: 1px solid %s;
                color: %s;
                font-size: 13px;
            }
            QListWidget:hover {
                border: 1px solid %s;
            }
            QListWidget:focus {
                border: 1px solid %s;
            }
            QListWidget::item {
                border: none;  /* Remove item borders */
            }
            QListWidget::item:hover {
                background-color: %s;
            }
            QListWidget::item:selected {
                background-color: %s;
            }
        """ % ( 
            self.colors['darker_06'],
            self.colors['grey_03'],
            self.colors['darker_06'],
            self.colors['darker_06'],
            self.colors['darker_06'],
            self.colors['darker_02']
        )

    def get_tree_widget_stylesheet( self ):
        return """
            QTreeWidget {
                border: 1px solid %s;
                color: %s;
                font-size: 13px;
            }
            QTreeWidget:hover {
                border: 1px solid %s;
            }
            QTreeWidget:focus {
                border: 1px solid %s;
            }
            QTreeWidget::item {
                border: none;  /* Remove item borders */
            }
            QTreeWidget::item:hover {
                background-color: %s;
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
                font-size: 11px;
                letter-spacing: 3.0px;
            }
        """ % ( 
            self.colors['darker_06'],
            self.colors['grey_03'],
            self.colors['darker_06'],
            self.colors['darker_06'],
            self.colors['darker_06'],
            self.colors['darker_02'],
            self.colors['darker_02'],
            self.colors['darker_02'],
            self.colors['grey_09']
        )

    def get_radio_button_stylesheet( self ):
        return """
            QRadioButton {
                color: %s;
                letter-spacing: 1.5px;
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
            self.colors['grey_04'],
            self.colors['grey_09'],
            self.colors['darker_02'],
            self.colors['base']
        )

    def get_combo_box_stylesheet( self ):
        return """
            QComboBox {
                color: %s;
                background-color: %s;
                selection-color: %s;
                selection-background-color: %s;
                font-size: 13px;
                border: 1px solid %s;
                border-radius: 2px;
                padding: 3px 5px;
                padding-right: 20px;  /* Make room for the dropdown button */
                letter-spacing: 0.25px;
            }
            
            QComboBox:hover {
                border-color: %s;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                width: 8px;
                height: 8px;
                background: %s;
                border-radius: 4px;
            }
            
            QComboBox::down-arrow:hover {
                background: %s;
            }
            
            QComboBox::down-arrow:on {
                background: %s;
            }            

            QComboBox QAbstractItemView {
                color: %s;
                selection-color: %s;
                selection-background-color: %s;
                background-color: %s;
                font-size: 12px;
                border: 1px solid %s;
                border-radius: 4px;
                padding: 2px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 4px;
                border-radius: 2px;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: %s;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: %s;
            }
        """ % ( 
            self.colors['grey_03'],  # Main text color
            self.colors['grey_08'],  # Background color
            self.colors['grey_03'],  # Selected text color
            self.colors['darker_02'],  # Selected background color
            self.colors['darker_06'],  # Border color
            self.colors['darker_05'],  # Hover border color
            self.colors['grey_05'],  # Down arrow color
            self.colors['grey_03'],  # Down arrow hover color
            self.colors['base'],  # Down arrow when dropdown is open
            self.colors['grey_03'],  # Dropdown text color
            self.colors['grey_01'],  # Selected dropdown text color
            self.colors['darker_02'],  # Selected dropdown background color
            self.colors['grey_08'],  # Dropdown background color
            self.colors['grey_06'],  # Dropdown border color
            self.colors['darker_06'],  # Dropdown item hover color
            self.colors['darker_02']  # Dropdown item selected color
        )

    def get_label_title_stylesheet( self ):
        return """
            QLabel {
                color: %s;
                font-weight: normal;
                font-size: 13px;
                letter-spacing: 3.5px;
            }
        """ % ( 
            self.colors['brighter_02']
        )

    def get_label_subtitle_stylesheet( self ):
        return """
            QLabel {
                color: %s;
                font-weight: normal;
                ont-size: 13px;
                letter-spacing: 3.0px;
            }
        """ % ( 
            self.colors['darker_01']
        )

    def get_label_stylesheet( self ):
        return """
            QLabel {
                color: %s;
                font-size: 12px;
                letter-spacing: 1.5px;
            }
        """ % ( 
            self.colors['grey_04']
        )

    def get_label_compact_stylesheet( self ):
        return """
            QLabel {
                color: %s;
                font-size: 12px;
                letter-spacing: 0.0px;
            }
        """ % ( 
            self.colors['grey_04']
        )

    def get_menu_context_stylesheet( self ):
        return """
            QMenu {
                color: %s;
                background-color: %s;
                font-size: 13px;
                border: 1px solid %s;
            }
            QMenu::item {
                background-color: %s;
            }
            QMenu::item:selected {
                background-color: %s;
                color: %s;
            }
        """ % ( 
            self.colors['grey_04'],
            self.colors['grey_09'],
            self.colors['grey_06'],
            self.colors['grey_09'],
            self.colors['darker_07'],
            self.colors['white']
        )

    def get_button_collapse_stylesheet( self ):
        return """
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 2px;
                margin: 0;
                padding: 0;
            }
            
            QToolButton::right-arrow {
                image: none;
                width: 8px;
                height: 8px;
                background: %s;
                border-radius: 2px;
            }
            
            QToolButton::right-arrow:hover {
                background: %s;
            }
            
            QToolButton::down-arrow {
                image: none;
                width: 8px;
                height: 8px;
                background: %s;
                border-radius: 2px;
            }
            
            QToolButton::down-arrow:hover {
                background: %s;
            }
        """ % ( 
            self.colors['grey_05'],  # Arrow normal color - using theme color
            self.colors['grey_03'],  # Arrow hover color - using theme base color
            self.colors['base'],  # Arrow normal color (down state)
            self.colors['darker_02']  # Arrow hover color (down state)
        )

    def get_separator_stylesheet( self ):
        return """
            QFrame {
                background-color: %s;
                border: none;
                max-height: 2px;
            }
        """ % ( self.colors['grey_08'] )
