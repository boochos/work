import urllib
import maya.cmds as cmds
import maya.mel as mel
import os
import compileall as ca
import py_compile as pc

# updated

####################################################################
# commented chunk of code should download this module and run it
'''
import urllib
import os
import compileall as ca
import maya.cmds as cmds
url = 'https://raw.github.com/boochos/work/master/download_lib.py'
dir = cmds.internalVar(usd=1)
dir = dir.partition('maya')
dir = os.path.join(dir[0], dir[1])
dir = os.path.join(dir, 'scripts')
urllib.urlretrieve(url, os.path.join(dir, 'download_lib.py'))
ca.compile_dir(dir, force=True)
import download_lib as dl
reload(dl)
dl.shelfRefresh(getAll=True)
'''
####################################################################


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def pathDepth(path='', depth='maya'):
    stf = path.partition(depth)
    result = os.path.join(stf[0], stf[1])
    return result


class Depend():

    def __init__(self):
        # shelf
        self.shelf = 'AnimGit'
        self.old = 'AnimGit_old'


def shelfRefresh(getAll=False):
    if getAll:
        get(getScripts=1, getButtons=1, compileAll=1)
    shelfRename()
    shelfBuild()
    shelfDeleteWin()


def shelfDeleteWin():
    win = cmds.window('DELETE_OLD_SHELF', w=200, h=40)
    cmds.columnLayout(columnAttach=('both', 1), columnAlign=(
        'center'), adjustableColumn=True, rowSpacing=10, columnWidth=250)
    cmds.button('deleteButtonShelf', c="import maya.cmds as cmds\ncmds.deleteUI('AnimGit_old', control=True)\ncmds.deleteUI('DELETE_OLD_SHELF', control=True)",
                l='DELETE OLD SHELF', w=150, h=100)
    cmds.showWindow(win)


def shelfRename(*args):
    dp = Depend()
    if cmds.control(dp.shelf, q=1, ex=1):
        cmds.renameUI(dp.shelf, dp.old)


def shelfBuild(*args):
    shelfDir = cmds.internalVar(ush=1)
    shelfPrnt = 'ShelfLayout'
    dp = Depend()
    if not cmds.control(dp.shelf, q=1, ex=1):
        # build ui
        cmds.setParent(shelfPrnt)
        cmds.shelfLayout(dp.shelf)
        cmds.setParent(dp.shelf)
        wh = 35
        # build buttons
        cmds.shelfButton(label='FRSH', annotation='refresh AnimGit shelf', w=wh, h=wh,
                         image='dwnArrow.xpm', command='import download_lib as dl\nreload(dl)\ndl.shelfRefresh(getAll=1)')
        cmds.shelfButton(label='save ++', annotation='save ++', w=wh, h=wh, image='save++_icon.xpm',
                         command='import fileMan_lib as fm\nreload(fm)\nfm.incrementalSave()')
        cmds.shelfButton(label='', annotation='set project from file name', w=wh, h=wh, image='PrjtSet.xpm',
                         command='import fileMan_lib as fm\nreload(fm)\nfm.setProjectFromFilename("scenes")')
        cmds.shelfButton(label='print selection', annotation='print selection',
                         w=wh, h=wh, image='PrntSel.xpm', command='sl.prnt()')
        cmds.shelfButton(label='temporarily save selection', annotation='temporarily save selection',
                         w=wh, h=wh, image='selStore.xpm', command='import selection as sel\nsl = sel.Sel()')
        cmds.shelfButton(label='select saved selection', annotation='select saved selection',
                         w=wh, h=wh, image='sel.xpm', command='sl.select()')
        cmds.shelfButton(label='select pair script job', annotation='select pair script job', w=wh,
                         h=wh, image='srv_mirSel_off_icon.xpm', command='import pairSelect as ps\nps.toggleJob()')
        cmds.shelfButton(label='manage playblasts in temp folder', annotation='playblast Manager', w=wh, h=wh,
                         image='playBlastMan.xpm', command='import playblast_lib\nreload(playblast_lib)\nplayblast_lib.blastWin()')
        cmds.shelfButton(label='playblast', annotation='playblast', w=wh, h=wh, image='rvBlast.png',
                         command="import playblast_lib as pb\nreload(pb)\npb.blast(x=1, format='image', qlt=100, compression='png', offScreen=True )")
        cmds.shelfButton(label='toggle image planes on selected camera', annotation='toggle image planes on selected camera',
                         w=wh, h=wh, image='camPlateToggle.xpm', command='import togglePlate\nreload(togglePlate)\ntogglePlate.togglePlate()')
        cmds.shelfButton(label='controller size +', annotation='controller size +', w=wh, h=wh,
                         image='CT+.xpm', command='import display_lib as ds\nreload(ds)\nds.shapeSize(mltp=1.1)')
        cmds.shelfButton(label='controller size -', annotation='controller size -', w=wh, h=wh,
                         image='CT-.xpm', command='import display_lib as ds\nreload(ds)\nds.shapeSize(mltp=0.9)')
        cmds.shelfButton(label='character set import ui', annotation='character set import ui', w=wh,
                         h=wh, image='csIm.png', command='import characterUI_macro_lib as csUI\nreload(csUI)\ncsUI.CSUI()')
        cmds.shelfButton(label='character set export ui', annotation='character set export ui', w=wh, h=wh,
                         image='csEx.png', command='import characterUI_macro_lib as csUI\nreload(csUI)\ncsUI.CSUI(export=True)')
        cmds.shelfButton(label='toggle membership', annotation='toggle membership of object from current character set', w=wh,
                         h=wh, image='csMbrTgl.png', command='import characterSet_lib as cs\nreload(cs)\ncs.toggleMembershipToCurrentSet()')
        cmds.shelfButton(label='flush character sets temporarily', annotation='flush character sets temporarily',
                         w=wh, h=wh, image='flush.png', command='import characterSet_lib as cs\nreload(cs)\ncs.flush()')
        cmds.shelfButton(label='unflush character sets ', annotation='unflush character sets ', w=wh,
                         h=wh, image='flushUn.png', command='import characterSet_lib as cs\nreload(cs)\ncs.unflush()')
        cmds.shelfButton(label='graph editor buttons', annotation='graph editor buttons', w=wh,
                         h=wh, image='geBttns.png', command='import display_lib as ds\nreload(ds)\nds.buttonsGE()')
        cmds.shelfButton(label='gather frame numbers', annotation='gather frame numbers of first selection\ninsert keys on same frames to all consecutive objects\nremove non matching frames',
                         w=wh, h=wh, image='matchKeys.png', command='import constraint_lib as cn\nreload(cn)\ncn.matchKeyedFramesLoop()')
        cmds.shelfButton(label='move first object to the location of second', annotation='move first object to the location of second',
                         w=wh, h=wh, image='MatchX.xpm', command='import anim_lib as anm\nreload(anm)\nanm.matchObj()')
        cmds.shelfButton(label='constraint tools', annotation='constraint tools', w=wh, h=wh,
                         image='constraintUI.png', command='import constraintUI_macro_lib as cnUI\nreload(cnUI)\ncnUI.CSUI()')
        cmds.shelfButton(label='select selection', annotation='select selection set\nread from text file\nobjects cannot be in multiple sets',
                         w=wh, h=wh, image='TagSel.xpm', command='import selectionSet_lib as ss\nreload(ss)\nss.selectSet()')
        cmds.shelfButton(label='create selection set files', annotation='create selection set files', w=wh,
                         h=wh, image='TagUI.xpm', command='import selectionUI_macro_lib as sUI\nreload(sUI)\nsUI.CSUI()')
        cmds.shelfButton(label='2 selected objects', annotation='2 selected objects\nanim from object 1 is pasted to object 2\ncurrent frame is used as the paste point', w=wh, h=wh, image='animCopyPaste.png',
                         command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nsel = cmds.ls(sl=True)\ncmds.select(sel[0])\nancop.animCopy()\ncmds.select(sel[1])\nancop.animPaste()')
        cmds.shelfButton(label='anim is copied from selected objects', annotation='anim is copied from selected objects', w=wh, h=wh,
                         image='AnimCopy.xpm', command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nancop.animCopy()')
        cmds.shelfButton(label='anim is pasted to selected objects', annotation='anim is pasted to selected objects', w=wh, h=wh,
                         image='AnimPaste.xpm', command='import animation_library_manager as alm\nreload(alm)\nancop = alm.AnimationToolbox()\nancop.animPaste()')
        cmds.shelfButton(label='anim is imported from a file', annotation='anim is imported from a file', w=wh, h=wh,
                         image='AnimImport.xpm', command='import clipPickle_lib as cp\nreload(cp)\ncp.clipApply(ns=cmds.ls(sl=1)[0].split(":")[0])')
        cmds.shelfButton(label='anim is exported to a file', annotation='anim is exported to a file', w=wh,
                         h=wh, image='AnimExport.xpm', command='import clipPickle_lib as cp\nreload(cp)\ncp.clipSave()')
        cmds.shelfButton(label='speed attribute is added', annotation='speed attribute is added', w=wh,
                         h=wh, image='kmh.xpm', command='import display_lib as ds\nreload(ds)\nds.speed(local=0)')
        cmds.shelfButton(label='select 2 objects', annotation='select 2 objects\ndistance attribue is added\nattr only updates on frame changes',
                         w=wh, h=wh, imageOverlayLabel='dst', image='pythonFamily.png', command='import display_lib as dis\nreload(dis)\ndis.distance()')
    else:
        # clean ui
        cmds.deleteUI(dp.shelf, control=True)


def get(getScripts=False, getButtons=False, compileAll=False):
    # ONLINE_____

    # online repos
    urlScripts = 'https://raw.github.com/boochos/work/master'
    urlIcons = 'https://raw.github.com/boochos/shelfIcons/master'

    # libs
    '''
    libs = ['download_lib.py', 'fileMan_lib', 'characterSet_lib.py', 'characterUI_macro_lib.py', 'constraint_lib.py',
    'constraintUI_macro_lib.py', 'constraintUI_micro_lib.py', 'display_lib.py',
    'key_anim_lib.py', 'lists_lib.py', 'selection.py', 'selectionSet_lib.py',
    'selectionUI_macro_lib.py', 'zero.py', 'autoTangent.mel', 'pairSelect.py',
    'animCurve_lib.py', 'animCopyPaste_lib.py', 'animation_library_manager.py',
    'anim_lib.py', 'ui_micro_lib.py', 'sys_lib.py', 'playblast_lib.py', 'togglePlate.py',
    'graphFilter.py', 'curveSoftSelect.py', 'pairSelectList.txt', 'animRig_lib.py', 'clipPickle_lib.py', 'clipPickleUI_micro_lib___BETA.py', 'clipPickleUI_macro_lib___BETA.py' ]'''

    # icons
    '''
    icons = ['constraintUI.png', 'csAdd.png', 'csEx.png',
    'csIm.png', 'csMbrTgl.png', 'csMinus.png', 'flush.png', 'flushUn.png', 'geBttns.png',
    'matchKeys.png', 'CT-.xpm', 'CT+.xpm', 'PrntSel.xpm', 'selStore.xpm', 'sel.xpm', 'TagSel.xpm',
    'TagUI.xpm', 'upArrow.xpm', 'MatchX.xpm', 'dwnArrow.xpm', 'AnimPaste.xpm', 'AnimStore.xpm',
    'AnimImport.xpm', 'AnimExport.xpm', 'animCopyPaste.xpm', 'AnimCopy.xpm', 'rvBlast.png', 'sel.png',
    'srv_mirSel_off_icon.xpm', 'srv_mirSel_on_icon.xpm', 'save++_icon.xpm', 'kmh.xpm', 'camPlateToggle.xpm',
    'playBlastMan.xpm', 'PrjtSet.xpm']'''

    # LOCAL_____

    # scripts
    scriptDir = cmds.internalVar(usd=1)
    scriptDir = pathDepth(path=scriptDir, depth='maya')
    scriptDir = os.path.join(scriptDir, 'scripts')
    # icons
    prefDir = cmds.internalVar(upd=1)
    iconDir = os.path.join(prefDir, 'icons')

    # instead
    # download downloadFiles lib, always before update
    dnLib = 'downloadFiles_lib'
    url = urlScripts + '/' + dnLib
    home = os.path.join(scriptDir, dnLib)
    if os.path.isdir(home):
        # os.remove(home)
        print 'remove   ', home
    #urllib.urlretrieve(url, home)
    pc.compile(file)
    import downloadFiles_lib as df

    # get scripts
    for lib in df.downloadlibs:
        url = urlScripts + '/' + lib
        # print url
        home = os.path.join(scriptDir, lib)
        if getScripts:
            print url
            print home
            if os.path.isdir(home):
                os.remove(home)
            message('downloading -- ' + home)
            cmds.refresh()
            #urllib.urlretrieve(url, home)
    # compile modules
    if compileAll:
        ca.compile_dir(scriptDir, force=True)
        message('compile_______________________')
    # get icons
    for icon in df.downloadIcons:
        url = urlIcons + '/' + icon
        # print url
        home = os.path.join(iconDir, icon)
        if getButtons:
            print url
            print home
            message('downloading -- ' + home)
            cmds.refresh()
            #urllib.urlretrieve(url, home)
