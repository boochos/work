from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QDialog, QLabel, QSlider, QHBoxLayout
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds

# Initialize the global variable
global custom_dialog

try:
    # close window if open
    if custom_dialog:
        if not custom_dialog.isHidden():
            # custom_dialog.store_session()
            custom_dialog.close()
        else:
            print( 'check on import, not: custom_dialog' )
            custom_dialog = None
except:
    print( 'check on import, error: custom_dialog' )
    # custom_dialog = None


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtWidgets.QWidget )


class CustomSlider( QSlider ):

    def __init__( self, parent = None ):
        super( CustomSlider, self ).__init__( QtCore.Qt.Horizontal, parent )
        self.r = 150.0
        self.setRange( self.r * -1, self.r )
        self.setValue( 0 )
        self.sliderPressed.connect( self.query_selection )
        self.valueChanged.connect( self.adjust_values )
        self.sliderReleased.connect( self.finalize_value )
        self.setFixedWidth( 400 )
        self.label = QLabel( str( self.value() ) )
        self.label.setFixedWidth( 30 )
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = {}
        self.current_time = None
        self.attrs = None
        self.selected_objects = []  # Store the selected objects
        self.new_values = {}  # Store new values
        self.auto_k_restore = None

    def query_selection( self ):
        cmds.undoInfo( openChunk = True, cn = 'BlendPose' )  # Open an undo chunk
        #
        self.auto_k_restore = cmds.autoKeyframe( q = True, state = True )
        cmds.autoKeyframe( state = True )
        #
        self.selected_objects = cmds.ls( selection = True )
        if self.selected_objects:
            self.current_time = cmds.currentTime( query = True )
            self.previous_key_values = {}
            self.next_key_values = {}
            self.initial_values = {}
            for obj in self.selected_objects:
                self.attrs = cmds.listAttr( obj, keyable = True, scalar = True )  # Get all keyable attributes
                self.previous_key_values[obj] = {}
                self.next_key_values[obj] = {}
                self.initial_values[obj] = {}
                for attr in self.attrs:
                    keyframes = cmds.keyframe( obj, query = True, timeChange = True, attribute = attr )
                    print( 'Keyframes for {}: {}'.format( attr, keyframes ) )
                    if keyframes:
                        prev_keys = [key for key in keyframes if key < self.current_time]
                        next_keys = [key for key in keyframes if key > self.current_time]
                        print( 'Previous for {}: {}'.format( attr, prev_keys ) )
                        print( 'Previous for {}: {}'.format( attr, next_keys ) )
                        if prev_keys and next_keys:
                            prev_key_time = prev_keys[-1]
                            next_key_time = next_keys[0]
                            prev_val = cmds.keyframe( obj, query = True, time = ( prev_key_time, prev_key_time ), valueChange = True, attribute = attr )
                            next_val = cmds.keyframe( obj, query = True, time = ( next_key_time, next_key_time ), valueChange = True, attribute = attr )
                            if prev_val and next_val:
                                self.previous_key_values[obj][attr] = prev_val[0]
                                self.next_key_values[obj][attr] = next_val[0]
                            else:
                                print( 'Previous for {}'.format( attr ) )
                                pass
                            self.initial_values[obj][attr] = cmds.getAttr( obj + '.' + attr )
                        else:
                            self.previous_key_values[obj][attr] = None
                            self.next_key_values[obj][attr] = None
                            self.initial_values[obj][attr] = cmds.getAttr( obj + '.' + attr )
                    else:
                        self.previous_key_values[obj][attr] = None
                        self.next_key_values[obj][attr] = None
                        self.initial_values[obj][attr] = cmds.getAttr( obj + '.' + attr )

    def adjust_values( self, value ):
        if self.previous_key_values and self.next_key_values:
            self.new_values = {}
            for obj in self.selected_objects:
                self.new_values[obj] = {}
                for attr in self.attrs:
                    if value >= 0:
                        ratio = value / self.r
                        if attr in self.initial_values[obj] and attr in self.next_key_values[obj] and self.next_key_values[obj][attr] is not None:
                            self.new_values[obj][attr] = self.initial_values[obj][attr] * ( 1 - ratio ) + self.next_key_values[obj][attr] * ratio
                    else:
                        ratio = abs( value ) / self.r
                        if attr in self.initial_values[obj] and attr in self.previous_key_values[obj] and self.previous_key_values[obj][attr] is not None:
                            self.new_values[obj][attr] = self.initial_values[obj][attr] * ( 1 - ratio ) + self.previous_key_values[obj][attr] * ratio
                for attr, new_value in self.new_values[obj].items():
                    # cmds.setKeyframe( obj, time = self.current_time, value = new_value, attribute = attr )
                    cmds.setAttr( obj + '.' + attr, new_value )
        else:
            pass
        self.label.setText( str( value ) )

    def finalize_value( self ):
        # Disconnect the valueChanged signal temporarily
        self.valueChanged.disconnect( self.adjust_values )
        # Reset the slider to default value
        self.setValue( 0 )
        self.label.setText( str( 0 ) )
        # Reconnect the valueChanged signal
        self.valueChanged.connect( self.adjust_values )
        # Reset the stored data
        self.previous_key_values = None
        self.next_key_values = None
        self.initial_values = None
        self.new_values = {}  # Reset new values
        self.attrs = None
        self.selected_objects = None  # Reset the stored objects
        cmds.autoKeyframe( state = self.auto_k_restore )
        cmds.undoInfo( closeChunk = True )  # Close the undo chunk


class CustomDialog( QDialog ):

    def __init__( self, parent = None ):
        super( CustomDialog, self ).__init__( parent )
        self.setWindowTitle( "Custom Toolbar" )
        self.setFixedHeight( 40 )  # Limit the height to 40 pixels when floating
        # Main layout
        layout = QHBoxLayout()
        self.label = QLabel( "Blend Pose" )
        layout.addWidget( self.label )
        self.slider = CustomSlider()
        layout.addWidget( self.slider )
        layout.addWidget( self.slider.label )
        self.setLayout( layout )
        self.adjustSize()


def delete_custom_dialog():
    if custom_dialog and custom_dialog.isVisible():
        custom_dialog.close()


def create_custom_dialog():
    delete_custom_dialog()
    custom_dialog = CustomDialog( get_maya_main_window() )
    custom_dialog.show()


if __name__ == '__main__':
    pass
else:
    custom_dialog = CustomDialog( get_maya_main_window() )  # returns class
    custom_dialog.show()

# TODO: add operation priorities: selected curves > in context of anim layers > selected objects / selected charSets > active char sets

# TODO: if no key exists to either side assume the values should be the current initial values
# TODO: check handling of anim layers... big fail, values need to be queried from anim curves not getAttr()
# TODO: add feature to push past 100%

'''
import time
# speed test
start = time.time()
sel = cmds.ls(sl=1)
max = 20
start = time.time()
while i < max:
    cmds.setKerframe(sel[0], time=[1010, 1010], value=3, attribute = 'tx')
    i = i+1
end = time.time()
elapsed = end - start
print('setKeyframe elapsed: ', elapsed)
#
start = time.time()
while i < max:
    cmds.setAttr(sel[0] '.translateX', 3)
    i = i+1
end = time.time()
elapsed = end - start
print('setKeyframe elapsed: ', elapsed)   
'''
