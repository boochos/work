import maya.cmds as cmds
import pairSelect as ms
import display_lib as ds

ms.toggleIcon(off=True)

def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')

