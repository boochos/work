from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QDialog, QLabel, QSlider, QHBoxLayout
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QToolBar, QSlider, QHBoxLayout
from shiboken2 import getCppPointer
from shiboken2 import wrapInstance
from shiboken2 import wrapInstance
import shiboken2

from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as apiUI
import maya.OpenMayaUI as omui
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.cmds as cmds

# import maya as m
# import QtCompat
t_bar = None


def print_all_maya_ui():
    '''
    
    '''
    x = dict( ( w.objectName(), w ) for w in QtWidgets.QApplication.allWidgets() )
    y = [name for ( name, widget ) in x.items()]
    y.sort()
    for name in y:
        print( name )


def slider_bar():
    '''
    
    '''
    global t_bar
    # main window
    app = QtWidgets.QApplication.instance()  # get the qApp instance if it exists.
    mayaWin = next( w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow' )

    t_bar = QtWidgets.QToolBar( 'SlidersBar', parent = mayaWin )
    t_bar.setObjectName( 'MyLabel' )
    # t_bar.setWindowFlags( Qt.Window )  # Make this widget a parented standalone window

    t_bar.addWidget( QtWidgets.QLabel( "Hello" ) )
    #
    tggl_button = QtWidgets.QPushButton( 'TOGGLE VIEWPORTS 3' )
    t_bar.addWidget( tggl_button )

    #
    slider = QtWidgets.QSlider()
    slider.setOrientation( QtCore.Qt.Horizontal )
    t_bar.addWidget( slider )

    #
    t_bar.show()
    # t_bar = None  # widget is parented, so it will not be destroyed.


def slider_bar_close():
    '''
    
    '''
    global t_bar
    if t_bar:
        t_bar.close()


def mayaMainWindow():
    '''
    
    '''
    mainWindowPointer = MQtUtil.mainWindow()
    return shiboken2.wrapInstance( int( mainWindowPointer ), QtWidgets.QWidget )


class MyToolbar( MayaQWidgetDockableMixin, QtWidgets.QToolBar ):
    '''
    parent ui needs to be more specific
    '''

    # workspace_control_name will be populated only after Maya restart to recreate window
    def __init__( self, parent = mayaMainWindow() ):
        super( MyToolbar, self ).__init__( parent )

        self.setWindowTitle( "Toolbar" )
        self.myButton = QtWidgets.QPushButton( 'TOGGLE VIEWPORTS 4' )
        self.addWidget( self.myButton )

        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation( QtCore.Qt.Horizontal )
        self.addWidget( self.slider )

'''
if __name__ == '__main__':  # from script editor
    myToolbar = MyToolbar()
    myToolbar.show( dockable = True )
else:  # from module, like here
    print( '???', __name__ )
    myToolbar = MyToolbar()
    # myToolbar.setTabPosition( 'left' )
    myToolbar.show( dockable = True, area = 'bottom', floating = False, setTabPosition = 'left' )
'''

'''
# main window
app = QtWidgets.QApplication.instance()  # get the qApp instance if it exists.
mayaWin = next( w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow' )

t_bar = QtWidgets.QToolBar( 'SlidersBar', parent = mayaWin )
# hello.setObjectName( 'MyLabel' )
# hello.setWindowFlags( Qt.Window )  # Make this widget a parented standalone window

t_bar.addWidget( QtWidgets.QLabel( "Hello" ) )
#
tggl_button = QtWidgets.QPushButton( 'TOGGLE VIEWPORTS 3' )
t_bar.addWidget( tggl_button )

t_bar.show()
# t_bar = None  # widget is parented, so it will not be destroyed.
'''

'''
from PySide2 import QtWidgets
x = dict((w.objectName(), w) for w in QtWidgets.QApplication.allWidgets())
y = [name for (name, widget) in x.items()]
y.sort()
for name in y:
    print(name)

import QtCompat
import maya as m
ptr = m.OpenMayaUI.MQtUtil.findControl("graphEditor1OutlineEdSlave")
graphEd = QtCompat.wrapInstance(long(ptr ), QtWidgets.QWidget)

from PySide2 import QtCore, QtGui, QtWidgets
import maya.OpenMayaUI as apiUI
app = QtWidgets.QApplication.instance() #get the qApp instance if it exists.
mayaWin = next(w for w in app.topLevelWidgets() if w.objectName()=='MayaWindow')
hello = QtWidgets.QToolBar(parent=mayaWin) 
hello.setObjectName('MyLabel') 
hello.setWindowFlags(mayaWin) # Make this widget a parented standalone window
hello.show() 
hello = None # widget is parented, so it will not be destroyed. 
'''


class _MyWindow( MayaQWidgetDockableMixin, QtWidgets.QDialog ):

    # workspace_control_name will be populated only after Maya restart to recreate window
    def __init__( self, parent = mayaMainWindow() ):
        super( _MyWindow, self ).__init__( parent )

        self.setWindowTitle( "Dockable Window" )
        self.myButton = QtWidgets.QPushButton( 'My Button' )
        mainLayout = QtWidgets.QVBoxLayout( self )
        mainLayout.addWidget( self.myButton )

'''
if __name__ == '__main__':
    myWindow = MyWindow()
    myWindow.show( dockable = True )
else:
    print( '???', __name__ )
    myWindow = _MyWindow()
    myWindow.setTabPosition( 'left' )
    myWindow.show( dockable = True )
'''


# ai code
def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtWidgets.QWidget )


class DockableWindow( QtWidgets.QWidget ):

    def __init__( self, parent = None ):
        super( DockableWindow, self ).__init__( parent )

        self.setWindowTitle( "Dockable PySide2 Window" )
        self.setGeometry( 300, 300, 400, 200 )

        self.button = QtWidgets.QPushButton( "Click Me!" )
        self.button.clicked.connect( self.on_button_click )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget( self.button )
        self.setLayout( layout )

    def on_button_click( self ):
        print( "Button clicked!" )


dockable_window = None


def create_dockable_window():
    global dockable_window
    if cmds.workspaceControl( "DockableWindowWorkspaceControl", exists = True ):
        delete_dockable_window()

    dockable_window = DockableWindow( get_maya_main_window() )
    workspace_control_name = cmds.workspaceControl( "DockableWindowWorkspaceControl",
                                                   label = "Dockable Window",
                                                   tabToControl = ( "scriptEditorPanel1Window", -1 ),
                                                   uiScript = "DockableWindow().show()" )
    control_widget = omui.MQtUtil.findControl( workspace_control_name )
    control_wrap = wrapInstance( long( control_widget ), QtWidgets.QWidget )
    layout = QtWidgets.QVBoxLayout( control_wrap )
    layout.setContentsMargins( 0, 0, 0, 0 )
    layout.addWidget( dockable_window )


def delete_dockable_window():
    global dockable_window
    if cmds.workspaceControl( "DockableWindowWorkspaceControl", exists = True ):
        cmds.deleteUI( "DockableWindowWorkspaceControl", control = True )
        dockable_window = None


# create_dockable_window()
custom_widget = None

custom_toolbar = None


class CustomSlider( QSlider ):

    def __init__( self, parent = None ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )
        self.setRange( 0, 100 )
        self.setValue( 50 )
        self.valueChanged.connect( self.update_label )

        self.label = QLabel( str( self.value() ) )
        self.label.setFixedWidth( 30 )

    def update_label( self, value ):
        self.label.setText( str( value ) )


class CustomToolbar( QToolBar ):

    def __init__( self, parent = None ):
        super( CustomToolbar, self ).__init__( parent )

        self.setWindowTitle( "Custom Toolbar" )
        self.setGeometry( 300, 300, 400, 50 )

        self.label = QLabel( "Custom Toolbar Between Time Slider and Range Slider" )
        self.addWidget( self.label )

        self.slider = CustomSlider()
        slider_layout = QHBoxLayout()
        slider_layout.addWidget( self.slider )
        slider_layout.addWidget( self.slider.label )

        slider_widget = QWidget()
        slider_widget.setLayout( slider_layout )
        self.addWidget( slider_widget )


def delete_custom_toolbar():
    if cmds.workspaceControl( "customToolbarWorkspaceControl", exists = True ):
        cmds.deleteUI( "customToolbarWorkspaceControl", control = True )

    parent = get_maya_main_window()
    for child in parent.findChildren( QToolBar ):
        if child.windowTitle() == "Custom Toolbar":
            child.setParent( None )
            child.deleteLater()

# custom_toolbar = None  # Define the global variable


def create_custom_toolbar():
    global custom_toolbar
    delete_custom_toolbar()

    custom_toolbar = CustomToolbar( get_maya_main_window() )

    control_name = cmds.workspaceControl( "customToolbarWorkspaceControl",
                                         label = "Custom Toolbar",
                                         dockToMainWindow = ( "bottom", 1 ),  # Docking to the bottom
                                         uiScript = "import __main__; __main__.custom_toolbar.show()" )
    control_widget = omui.MQtUtil.findControl( control_name )
    control_wrap = wrapInstance( long( control_widget ), QWidget )

    layout = QVBoxLayout( control_wrap )
    layout.setContentsMargins( 0, 0, 0, 0 )
    layout.addWidget( custom_toolbar )
    custom_toolbar.setParent( control_wrap )
    custom_toolbar.show()


create_custom_toolbar()

# ## mostly working slider from ai

# Initialize the global variable
global custom_dialog


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtWidgets.QWidget )


class CustomSlider( QSlider ):

    def __init__( self, parent = None ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )
        self.setRange( -100, 100 )
        self.setValue( 0 )
        self.sliderPressed.connect( self.query_selection )
        self.valueChanged.connect( self.adjust_values )
        self.sliderReleased.connect( self.finalize_value )
        self.setFixedWidth( 200 )

        self.label = QLabel( str( self.value() ) )
        self.label.setFixedWidth( 30 )
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = None
        self.current_time = None
        self.attrs = None

    def query_selection( self ):
        self.initial_values = None
        print( "checking:", self.initial_values )
        selected_objects = cmds.ls( selection = True )
        if selected_objects:
            obj = selected_objects[0]
            self.current_time = cmds.currentTime( query = True )
            # print( "Current time:", self.current_time )
            keyframes = cmds.keyframe( obj, query = True, timeChange = True )
            # print( "Keyframes:", keyframes )
            if keyframes:
                prev_keys = [key for key in keyframes if key < self.current_time]
                next_keys = [key for key in keyframes if key > self.current_time]
                # print( "Previous keys:", prev_keys )
                # print( "Next keys:", next_keys )
                if prev_keys and next_keys:
                    prev_key_time = prev_keys[-1]
                    next_key_time = next_keys[0]
                    self.attrs = cmds.listAttr( obj, keyable = True, scalar = True )  # Get all keyable attributes
                    # print( "Attributes:", self.attrs )
                    self.previous_key_values = {}
                    self.next_key_values = {}
                    self.initial_values = {}

                    for attr in self.attrs:
                        prev_val = cmds.keyframe( obj, query = True, time = ( prev_key_time, prev_key_time ), valueChange = True, attribute = attr )
                        next_val = cmds.keyframe( obj, query = True, time = ( next_key_time, next_key_time ), valueChange = True, attribute = attr )
                        if prev_val and next_val:
                            self.previous_key_values[attr] = prev_val[0]
                            self.next_key_values[attr] = next_val[0]
                        self.initial_values[attr] = cmds.getAttr( "{0}.{1}".format( obj, attr ) )
                        print( "loop:", self.initial_values )

                    # print( "Previous key values:", self.previous_key_values )
                    # print( "Next key values:", self.next_key_values )
                    print( "Stored:", self.initial_values )

    def adjust_values( self, value ):
        if self.previous_key_values and self.next_key_values:
            new_values = {}
            if value >= 0:
                ratio = value / 100.0
                for attr in self.attrs:
                    if attr in self.initial_values and attr in self.next_key_values:
                        new_values[attr] = self.initial_values[attr] * ( 1 - ratio ) + self.next_key_values[attr] * ratio
            else:
                ratio = abs( value ) / 100.0
                for attr in self.attrs:
                    if attr in self.initial_values and attr in self.previous_key_values:
                        new_values[attr] = self.initial_values[attr] * ( 1 - ratio ) + self.previous_key_values[attr] * ratio

            selected_objects = cmds.ls( selection = True )
            if selected_objects:
                obj = selected_objects[0]
                for attr, new_value in new_values.items():
                    cmds.setKeyframe( obj, time = self.current_time, value = new_value, attribute = attr )
        self.label.setText( str( value ) )

    def finalize_value( self ):
        print( 'Released', self.initial_values )
        # Disconnect the valueChanged signal temporarily
        self.valueChanged.disconnect( self.adjust_values )
        # Commit the final value
        # self.adjust_values( self.value() )
        # Reset the slider to default value
        self.setValue( 0 )
        # Reconnect the valueChanged signal
        self.valueChanged.connect( self.adjust_values )
        # Disconnect from the attributes
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = None
        self.attrs = None
        print( 'Reset', self.initial_values )


class CustomDialog( QDialog ):

    def __init__( self, parent = None ):
        super( CustomDialog, self ).__init__( parent )
        self.setWindowTitle( "Custom Toolbar" )
        self.setFixedHeight( 40 )  # Limit the height to 40 pixels when floating

        # Main layout
        layout = QHBoxLayout()
        self.label = QLabel( "Custom Toolbar Between Time Slider and Range Slider" )
        layout.addWidget( self.label )
        self.slider = CustomSlider()
        layout.addWidget( self.slider )
        layout.addWidget( self.slider.label )

        self.setLayout( layout )
        self.adjustSize()


def delete_custom_dialog():
    global custom_dialog
    if custom_dialog and custom_dialog.isVisible():
        custom_dialog.close()
    else:
        print( 'no dialog' )


def create_custom_dialog():
    global custom_dialog
    delete_custom_dialog()
    custom_dialog = CustomDialog( get_maya_main_window() )
    custom_dialog.show()

# Initialize and create the custom dialog
# create_custom_dialog()


if __name__ == '__main__':
    pass
else:
    if custom_dialog and custom_dialog.isVisible():
        custom_dialog.close()
    else:
        print( 'no dialog' )
    custom_dialog = CustomDialog( get_maya_main_window() )  # returns class
    custom_dialog.show()
