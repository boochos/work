import urllib
import maya.cmds as cmds
import maya.mel as mel
import os
import webrImport as web
# web
wf = web.mod('webrFiles_lib')


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class Depend():

    def __init__(self):
        # shelf
        self.shelf = 'WebShelf'
        self.old = 'WebShelf_old'


def shelfRefresh():
    getIcons()
    shelfRename()
    shelfBuild()
    shelfDeleteWin()


def shelfDeleteWin():
    win = cmds.window('DELETE_OLD_SHELF', w=200, h=40)
    cmds.columnLayout(columnAttach=('both', 1), columnAlign=(
        'center'), adjustableColumn=True, rowSpacing=10, columnWidth=250)
    cmds.button('deleteButtonShelf', c="import maya.cmds as cmds\ncmds.deleteUI('WebShelf_old', control=True)\ncmds.deleteUI('DELETE_OLD_SHELF', control=True)",
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
                         command='import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.incrementalSave()')

        cmds.shelfButton(label='', annotation='set project from file name', w=wh, h=wh, image='PrjtSet.xpm',
                         command='import webrImport as web\nfm = web.mod("fileMan_lib"\nreload(fm)\nfm.setProjectFromFilename("scenes")')

        cmds.shelfButton(label='print selection', annotation='print selection',
                         w=wh, h=wh, image='PrntSel.xpm', command='sl.prnt()')

        cmds.shelfButton(label='temporarily save selection', annotation='temporarily save selection',
                         w=wh, h=wh, image='selStore.xpm', command='import webrImport as web\nsl = web.mod("selection")\nsl = sel.Sel()')

        cmds.shelfButton(label='select saved selection', annotation='select saved selection',
                         w=wh, h=wh, image='sel.xpm', command='sl.select()')

        cmds.shelfButton(label='select pair script job', annotation='select pair script job', w=wh,
                         h=wh, image='srv_mirSel_off_icon.xpm', command='import webrImport as web\nps = web.mod("pairSelect")\nps.toggleJob()')

        cmds.shelfButton(label='manage playblasts in temp folder', annotation='playblast Manager', w=wh, h=wh,
                         image='playBlastMan.xpm', command='import webrImport as web\npb = web.mod("playblast_lib")\npb.blastWin()')

        cmds.shelfButton(label='playblast', annotation='playblast', w=wh, h=wh, image='rvBlast.png',
                         command='import webrImport as web\npb = web.mod("playblast_lib")\npb.blast(x=1, format="image", qlt=100, compression="png", offScreen=True )')

        cmds.shelfButton(label='toggle image planes on selected camera', annotation='toggle image planes on selected camera',
                         w=wh, h=wh, image='camPlateToggle.xpm', command='import webrImport as web\ntp = web.mod("togglePlate")\ntp.togglePlate()')

        cmds.shelfButton(label='controller size +', annotation='controller size +', w=wh, h=wh,
                         image='CT+.xpm', command='import webrImport as web\nds = web.mod("display_lib")\nds.shapeSize(mltp=1.1)')

        cmds.shelfButton(label='controller size -', annotation='controller size -', w=wh, h=wh,
                         image='CT-.xpm', command='import webrImport as web\nds = web.mod("display_lib")\nds.shapeSize(mltp=0.9)')

        cmds.shelfButton(label='character set import ui', annotation='character set import ui', w=wh,
                         h=wh, image='csIm.png', command='import webrImport as web\ncsUI = web.mod("characterUI_macro_lib")\ncsUI.CSUI()')

        cmds.shelfButton(label='character set export ui', annotation='character set export ui', w=wh, h=wh,
                         image='csEx.png', command='import webrImport as web\ncsUI = web.mod("characterUI_macro_lib")\ncsUI.CSUI(export=True)')

        cmds.shelfButton(label='toggle membership', annotation='toggle membership of object from current character set', w=wh,
                         h=wh, image='csMbrTgl.png', command='import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.toggleMembershipToCurrentSet()')

        cmds.shelfButton(label='flush character sets temporarily', annotation='flush character sets temporarily',
                         w=wh, h=wh, image='flush.png', command='import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.flush()')

        cmds.shelfButton(label='unflush character sets ', annotation='unflush character sets ', w=wh,
                         h=wh, image='flushUn.png', command='import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.unflush()')

        cmds.shelfButton(label='graph editor buttons', annotation='graph editor buttons', w=wh,
                         h=wh, image='geBttns.png', command='import webrImport as web\nds = web.mod("display_lib")\nds.buttonsGE()')

        cmds.shelfButton(label='gather frame numbers', annotation='gather frame numbers of first selection\ninsert keys on same frames to all consecutive objects\nremove non matching frames',
                         w=wh, h=wh, image='matchKeys.png', command='import webrImport as web\ncn = web.mod("constraint_lib")\ncn.matchKeyedFramesLoop()')

        cmds.shelfButton(label='move first object to the location of second', annotation='move first object to the location of second',
                         w=wh, h=wh, image='MatchX.xpm', command='import webrImport as web\nanm = web.mod("anim_lib")\nanm.matchObj()')

        cmds.shelfButton(label='constraint tools', annotation='constraint tools', w=wh, h=wh,
                         image='constraintUI.png', command='import webrImport as web\ncnUI = web.mod("constraintUI_macro_lib")\ncnUI.CSUI()')

        cmds.shelfButton(label='select selection', annotation='select selection set\nread from text file\nobjects cannot be in multiple sets',
                         w=wh, h=wh, image='TagSel.xpm', command='import webrImport as web\nss = web.mod("selectionSet_lib")\nss.selectSet()')

        cmds.shelfButton(label='create selection set files', annotation='create selection set files', w=wh,
                         h=wh, image='TagUI.xpm', command='import webrImport as web\nsUI = web.mod("selectionUI_macro_lib")\nsUI.CSUI()')

        cmds.shelfButton(label='2 selected objects', annotation='2 selected objects\nanim from object 1 is pasted to object 2\ncurrent frame is used as the paste point', w=wh, h=wh, image='animCopyPaste.png',
                         command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nsel = cmds.ls(sl=True)\ncmds.select(sel[0])\nancop.animCopy()\ncmds.select(sel[1])\nancop.animPaste()')

        cmds.shelfButton(label='anim is copied from selected objects', annotation='anim is copied from selected objects', w=wh, h=wh,
                         image='AnimCopy.xpm', command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nancop.animCopy()')

        cmds.shelfButton(label='anim is pasted to selected objects', annotation='anim is pasted to selected objects', w=wh, h=wh,
                         image='AnimPaste.xpm', command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nancop.animPaste()')

        cmds.shelfButton(label='anim is imported from a file', annotation='anim is imported from a file', w=wh, h=wh,
                         image='AnimImport.xpm', command='import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipApply(ns=cmds.ls(sl=1)[0].split(":")[0])')

        cmds.shelfButton(label='anim is exported to a file', annotation='anim is exported to a file', w=wh,
                         h=wh, image='AnimExport.xpm', command='import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipSave()')

        cmds.shelfButton(label='speed attribute is added', annotation='speed attribute is added', w=wh,
                         h=wh, image='kmh.xpm', command='import webrImport as web\nds = web.mod("display_lib")\nds.speed(local=0)')

        cmds.shelfButton(label='select 2 objects', annotation='select 2 objects\ndistance attribue is added\nattr only updates on frame changes',
                         w=wh, h=wh, imageOverlayLabel='dst', image='pythonFamily.png', command='import webrImport as web\ndis = web.mod("display_lib")\ndis.distance()')
    else:
        # clean ui
        cmds.deleteUI(dp.shelf, control=True)


def getIcons():
    # online
    urlIcons = 'https://raw.github.com/boochos/shelfIcons/master'

    # local
    prefDir = cmds.internalVar(upd=1)
    iconDir = os.path.join(prefDir, 'icons')

    # get icons
    for icon in wf.icons:
        url = urlIcons + '/' + icon
        # print url
        home = os.path.join(iconDir, icon)
        print url
        print home
        message('downloading -- ' + home)
        cmds.refresh()
        # urllib.urlretrieve(url, home)
