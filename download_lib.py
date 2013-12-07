import urllib
import maya.cmds as cmds
import os

def pathDepth(path='', depth='maya'):
    stf    = path.partition(depth)
    result = os.path.join(stf[0], stf[1])
    return result

def get():
    #ONLINE
    
    #online repos
    urlScripts  = 'https://raw.github.com/boochos/work/master'
    urlIcons    = 'https://raw.github.com/boochos/shelfIcons/master'
    
    #libs
    libs        = ['characterSet_lib.py', 'characterUI_macro_lib.py', 'constraint_lib.py',
    'constraintUI_macro_lib.py', 'constraintUI_micro_lib.py', 'display_lib.py',
    'key_anim_lib.py', 'lists_lib.py', 'selection.py', 'selectionSet_lib.py',
    'selectionUI_macro_lib.py', 'zero.py', 'autoTangent.mel', 'oaSmoothKeys.mel',
    'pairSelect.py', 'animCurve_lib.py', 'animCopyPaste_lib.py', 'animation_library_manager.py',
    'anim_lib.py', 'ui_micro_lib.py', 'sys_lib.py', 'faceRig_selection_pair.txt',
    'playblast_lib.py', 'spaceSwap.py', 'togglePlate.py', 'graphFilter.py']
    
    #icons
    icons       = ['AnimCopy.png', 'animCopyPaste.png', 'constraintUI.png', 'csAdd.png', 'csEx.png',
    'csIm.png', 'csMbrTgl.png', 'csMinus.png', 'flush.png', 'flushUn.png', 'geBttns.png',
    'matchKeys.png', 'CT-.xpm', 'CT+.xpm', 'PrntSel.xpm', 'selStore.xpm', 'sel.xpm', 'TagSel.xpm',
    'TagUI.xpm', 'upArrow.xpm', 'MatchX.xpm', 'dwnArrow.xpm', 'AnimPaste.xpm', 'AnimStore.xpm',
    'AnimImport.xpm', 'AnimExport.xpm', 'animCopyPaste.xpm', 'AnimCopy.xpm', 'rvBlast.png', 'sel.png',
    'srv_mirSel_off_icon.xpm', 'srv_mirSel_on_icon.xpm', 'save++_icon.xpm']
    
    #shelf
    shelf   = 'shelf_Custom.mel'
    
    #LOCAL
    
    #scripts
    scriptDir = cmds.internalVar(usd=1)
    scriptDir = pathDepth(path=scriptDir, depth='maya')
    scriptDir = os.path.join(scriptDir, 'scripts')
    #icons
    prefDir   = cmds.internalVar(upd=1)
    iconDir   = os.path.join(prefDir,'icons')
    #shelf
    shelfDir  = cmds.internalVar(ush=1)
    
    
    #get scripts
    for lib in libs:
        url  = urlScripts + '/' + lib
        print url
        home = os.path.join(scriptDir, 'DELETEME____' + lib)
        print home
        #urllib.urlretrieve(url, home)
    #get icons
    for icon in icons:
        url  = urlIcons + '/' + icon
        print url
        home = os.path.join(scriptDir, 'DELETEME____' + icon)
        print home
        #urllib.urlretrieve(url, home)
    #get shelf
