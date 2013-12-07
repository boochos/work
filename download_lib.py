import urllib
import maya.cmds as cmds
import os
import compileall as ca


####################################################################
#commented chunk of code should download this module and run it
'''
import urllib
import os
import compileall as ca
url  = 'https://raw.github.com/boochos/work/master/download_lib.py'
scriptDir = cmds.internalVar(usd=1)
scriptDir = pathDepth(path=scriptDir, depth='maya')
scriptDir = os.path.join(scriptDir, 'scripts')
urllib.urlretrieve(url, os.path.join(scriptDir, 'download_lib.py'))
ca.compile_dir(scriptDir, force=True)
import download_lib as dl
dl.get()
'''
####################################################################



def pathDepth(path='', depth='maya'):
    stf    = path.partition(depth)
    result = os.path.join(stf[0], stf[1])
    return result

class Depend():
    def __init__(self):
        #shelf
        self.shelf     = 'AnimGit'

def get():
    #ONLINE_____
    
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
    shelfBttns  = ['']
    
    #LOCAL_____
    
    #scripts
    scriptDir = cmds.internalVar(usd=1)
    scriptDir = pathDepth(path=scriptDir, depth='maya')
    scriptDir = os.path.join(scriptDir, 'scripts')
    #icons
    prefDir   = cmds.internalVar(upd=1)
    iconDir   = os.path.join(prefDir,'icons')
    #shelf
    shelfDir  = cmds.internalVar(ush=1)
    shelfPrnt = 'ShelfLayout'
    dp = Depend()
    shelf     = dp.shelf

    #BUILD_____

    #build shelf
    if not cmds.control(shelf, q=1, ex=1):
        #get scripts
        for lib in libs:
            url  = urlScripts + '/' + lib
            print url
            home = os.path.join(scriptDir, lib)
            print home
            urllib.urlretrieve(url, home)
        #compile modules
        ca.compile_dir(scriptDir, force=True)
        #get icons
        for icon in icons:
            url  = urlIcons + '/' + icon
            print url
            home = os.path.join(iconDir, icon)
            print home
            urllib.urlretrieve(url, home)
        #build ui
        cmds.setParent(shelfPrnt)
        cmds.shelfLayout(shelf)
        cmds.setParent(shelf)
        wh = 35
        #build buttons
        cmds.shelfButton(annotation='save ++', w=wh,h=wh, image='save++_icon.xpm', command='cmds.sphere()' )
        cmds.shelfButton(annotation='print selection', w=wh,h=wh, image='PrntSel.xpm', command='sl.prnt()' )
        cmds.shelfButton(annotation='temporarily save selection', w=wh,h=wh, image='selStore.xpm', command='import selection as sel\nsl = sel.Sel()' )
        cmds.shelfButton(annotation='select saved selection', w=wh,h=wh, image='sel.xpm', command='sl.select()' )
        cmds.shelfButton(annotation='select pair script job', w=wh,h=wh, image='srv_mirSel_off_icon.xpm', command='import pairSelect as ps\nps.toggleJob()' )
        cmds.shelfButton(annotation='playblast', w=wh,h=wh, image='rvBlast.png', command="import playblast_lib as pb\nreload(pb)\npb.blast(w=1072, h=804, x=1, format='image', qlt=100, compression='png', offScreen=True )" )
        cmds.shelfButton(annotation='controller size +', w=wh,h=wh, image='CT+.xpm', command='import display_lib as ds\nreload(ds)\nds.shapeSize(mltp=1.1)' )
        cmds.shelfButton(annotation='controller size -', w=wh,h=wh, image='CT-.xpm', command='import display_lib as ds\nreload(ds)\nds.shapeSize(mltp=0.9)' )
        cmds.shelfButton(annotation='character set import ui', w=wh,h=wh, image='csIm.png', command='import characterUI_macro_lib as csUI\nreload(csUI)\ncsUI.CSUI()' )
        cmds.shelfButton(annotation='character set export ui', w=wh,h=wh, image='csEx.png', command='import characterUI_macro_lib as csUI\nreload(csUI)\ncsUI.CSUI(export=True)' )
        cmds.shelfButton(annotation='toggle membership of object from current character set', w=wh,h=wh, image='csMbrTgl.png', command='import characterSet_lib as cs\nreload(cs)\ncs.toggleMembershipToCurrentSet()' )
        cmds.shelfButton(annotation='flush character sets temporarily', w=wh,h=wh, image='flush.png', command='import characterSet_lib as cs\nreload(cs)\ncs.flush()' )
        cmds.shelfButton(annotation='unflush character sets ', w=wh,h=wh, image='flushUn.png', command='import characterSet_lib as cs\nreload(cs)\ncs.unflush()' )
        cmds.shelfButton(annotation='graph editor buttons', w=wh,h=wh, image='geBttns.png', command='import display_lib as ds\nreload(ds)\nds.buttonsGE()' )
        cmds.shelfButton(annotation='gather frame numbers of first selection\ninsert keys on same frames to all consecutive objects\nremove non matching frames', w=wh,h=wh, image='matchKeys.png', command='import constraint_lib as cn\nreload(cn)\ncn.matchKeyedFramesLoop()' )
        cmds.shelfButton(annotation='move first object to the location of second', w=wh,h=wh, image='MatchX.xpm', command='import anim_lib as anm\nreload(anm)\nanm.matchObj()' )
        cmds.shelfButton(annotation='constraint tools', w=wh,h=wh, image='constraintUI.png', command='import constraintUI_macro_lib as cnUI\nreload(cnUI)\ncnUI.CSUI()' )
        cmds.shelfButton(annotation='select selection set\nread from text file\nobjects cannot be in multiple sets', w=wh,h=wh, image='TagSel.xpm', command='import selectionSet_lib as ss\nreload(ss)\nss.selectSet()' )
        cmds.shelfButton(annotation='create selection set files', w=wh,h=wh, image='TagUI.xpm', command='import selectionUI_macro_lib as sUI\nreload(sUI)\nsUI.CSUI()' )
        cmds.shelfButton(annotation='2 selected objects\nanim from object 1 is pasted to object 2\ncurrent frame is used as the paste point', w=wh,h=wh, image='animCopyPaste.png', command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nsel = cmds.ls(sl=True)\ncmds.select(sel[0])\nancop.animCopy()\ncmds.select(sel[1])\nancop.animPaste()' )
        cmds.shelfButton(annotation='anim is copied from selected objects', w=wh,h=wh, image='AnimCopy.xpm', command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nancop.animCopy()' )
        cmds.shelfButton(annotation='anim is pasted to selected objects', w=wh,h=wh, image='AnimPaste.xpm', command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nancop.animPaste()' )
        cmds.shelfButton(annotation='anim is imported from a file', w=wh,h=wh, image='AnimImport.xpm', command='import animation_library_manager as animMan\nreload(animMan)\nanimMan.animImport()' )
        cmds.shelfButton(annotation='anim is exported to a file', w=wh,h=wh, image='AnimExport.xpm', command='import animation_library_manager as animMan\nreload(animMan)\nanimMan.animExport()' )
        cmds.shelfButton(annotation='speed attribute is added', w=wh,h=wh, imageOverlayLabel='spd', image='pythonFamily.png', command='import display_lib as ds\nreload(ds)\nds.speed(local=0)' )
        cmds.shelfButton(annotation='select 2 objects\ndistance attribue is added\nattr only updates on frame changes', w=wh,h=wh, imageOverlayLabel='dst', image='pythonFamily.png', command='import display_lib as dis\nreload(dis)\ndis.distance()' )
    else:
        #clean ui
        cmds.deleteUI(shelf, control=True)
