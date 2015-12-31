import urllib  # need this for downloading icons, line is sometimes commented out
import maya.cmds as cmds
import maya.mel as mel
import os
#
import webrImport as web
# web
wf = web.mod('webrFiles_lib')
# FUTURE: when new version is pushed, server lags about 5min. Short find a way to time the updates


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


class Depend():

    def __init__(self):
        # shelf
        self.shelf = 'Web'
        self.old = 'WebrShelf_old'


def shelfRefresh():
    getIcons(download=True)
    shelfBuild()
    message('Shelf Refreshed!')


def shelfRefreshWin():
    win = cmds.window('REFRESH_SHELF', w=200, h=40)
    cmds.columnLayout(columnAttach=('both', 1), columnAlign=(
        'center'), adjustableColumn=True, rowSpacing=10, columnWidth=250)
    cmds.button('deleteButtonShelf', c='import webrImport as web\nws = web.mod("webrShelf")\nws.shelfRefresh()',
                l='REFRESH SHELF', w=150, h=100)
    cmds.showWindow(win)


def shelfRename(*args):
    dp = Depend()
    if cmds.control(dp.shelf, q=1, ex=1):
        cmds.renameUI(dp.shelf, dp.old)
        shelfRefreshWin()


def shelfBuild(*args):
    # shelfPrnt = 'ShelfLayout'
    dp = Depend()
    if not cmds.control(dp.shelf, q=1, ex=1):
        # build ui
        '''
        # old method, causes error
        cmds.setParent(shelfPrnt)
        cmds.shelfLayout(dp.shelf)
        '''
        mel.eval('addNewShelfTab %s' % dp.shelf)
        cmds.refresh()
        shelfAddButtons()
    else:
        # clean ui
        '''
        # old method
        cmds.deleteUI(dp.shelf, control=True)
        '''
        buttons = cmds.shelfLayout(dp.shelf, query=True, childArray=True)
        if buttons:
            cmds.deleteUI(buttons, control=True)
            cmds.refresh()
        shelfAddButtons()


def shelfAddButtons(*args):
    wh = 35
    cmds.setParent(Depend().shelf)
    # build buttons
    cmds.shelfButton(label='FRSH', annotation='refresh web shelf', w=wh, h=wh,
                     image='refreshWeb.png', command='import webrImport as web\nws = web.mod("webrShelf")\nws.shelfRefreshWin()')

    cmds.shelfButton(label='quick undo', annotation='viewport toggle', w=wh,
                     h=wh, image='tgglUI.png', command='import webrImport as web\ncn = web.mod("constraint_lib")\ncn.uiEnable()')

    cmds.shelfButton(label='quick undo', annotation='quick undo, viewport hide while executing undo', w=wh,
                     h=wh, image='undoFast.png', command='import webrImport as web\ncn = web.mod("constraint_lib")\ncn.quickUndo()')

    cmds.shelfButton(label='save ++', annotation='save ++', w=wh, h=wh, image='save++_icon.xpm',
                     command='import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.incrementalSave()')

    cmds.shelfButton(label='', annotation='set project from file name', w=wh, h=wh, image='PrjtSet.xpm',
                     command='import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.setProjectFromFilename("scenes")')

    cmds.shelfButton(label='print selection', annotation='print selection',
                     w=wh, h=wh, image='PrntSel.png', command='sl.prnt()')

    cmds.shelfButton(label='temporarily save selection', annotation='temporarily save selection',
                     w=wh, h=wh, image='selStore.xpm', command='import webrImport as web\nsel = web.mod("selection")\nsl = sel.Sel()')

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
                     h=wh, image='geBttns.png', command='import webrImport as web\nds = web.mod("display_lib")\nds.graphEditorButtons()')

    cmds.shelfButton(label='gather frame numbers', annotation='gather frame numbers of first selection\ninsert keys on same frames to all consecutive objects\nremove non matching frames',
                     w=wh, h=wh, image='matchKeys.png', command='import webrImport as web\ncn = web.mod("constraint_lib")\ncn.matchKeyedFramesLoop()')

    cmds.shelfButton(label='move first object to the location of second', annotation='move first object to the location of second',
                     w=wh, h=wh, image='MatchX.xpm', command='import webrImport as web\nanm = web.mod("anim_lib")\nanm.matchObj()')

    cmds.shelfButton(label='constraint tools', annotation='constraint tools', w=wh, h=wh,
                     image='constraintUI.png', command='import webrImport as web\ncnUI = web.mod("constraintUI_macro_lib")\ncnUI.CSUI()')

    cmds.shelfButton(label='select selection', annotation='select selection set\nread from text file\nobjects cannot be in multiple sets',
                     w=wh, h=wh, image='TagSel.png', command='import webrImport as web\nss = web.mod("selectionSet_lib")\nss.selectSet()')

    cmds.shelfButton(label='create selection set files', annotation='create selection set files', w=wh,
                     h=wh, image='TagUI.png', command='import webrImport as web\nsUI = web.mod("selectionUI_macro_lib")\nsUI.CSUI()')

    cmds.shelfButton(label='2 selected objects', annotation='2 selected objects\nanim from object 1 is pasted to object 2\ncurrent frame is used as the paste point', w=wh, h=wh, image='animCopyPaste.png',
                     command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nsel = cmds.ls(sl=True)\ncmds.select(sel[0])\nancop.animCopy()\ncmds.select(sel[1])\nancop.animPaste()')

    cmds.shelfButton(label='anim is copied from selected objects', annotation='anim is copied from selected objects', w=wh, h=wh,
                     image='AnimCopy.xpm', command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nancop.animCopy()')

    cmds.shelfButton(label='anim is pasted to selected objects', annotation='anim is pasted to selected objects', w=wh, h=wh,
                     image='AnimPaste.xpm', command='import webrImport as web\nalm = web.mod("animation_library_manager")\nancop = alm.AnimationToolbox()\nancop.animPaste()')

    cmds.shelfButton(label='anim is exported to a file', annotation='anim is exported to a file', w=wh,
                     h=wh, image='AnimExport.xpm', command='import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipSave(name="tempClip", temp=True)')

    cmds.shelfButton(label='anim is imported from a file', annotation='anim is imported from a file', w=wh, h=wh,
                     image='AnimImport.xpm', command='import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipApply(path=cp.clipDefaultTempPath() + "tempClip.clip")')

    cmds.shelfButton(label='speed attribute is added', annotation='speed attribute is added', w=wh,
                     h=wh, image='kmh.xpm', command='import webrImport as web\nds = web.mod("display_lib")\nds.speed(local=0)')

    cmds.shelfButton(label='select 2 objects', annotation='select 2 objects\ndistance attribute is added\nattr only updates on frame changes',
                     w=wh, h=wh, imageOverlayLabel='dst', image='pythonFamily.png', command='import webrImport as web\ndis = web.mod("display_lib")\ndis.distance()')

    # 'import display_lib as dis\nreload(dis)\ndis.distance()'
    # 'import webrImport as web\ndis = web.mod("display_lib")\ndis.distance()'

    cmds.shelfButton(label='clip library', annotation='Clip Library', w=wh,
                     h=wh, imageOverlayLabel='', image='AnimStore.xpm', command='import webrImport as web\ncpui = web.mod("clipPickleUI_macro_lib")\ncpui.CPUI()')
    # TODO: timewarp tool
    # TODO: timewarp with path anim, uisng some combo to sync path anim to, anim layer as time warp to keep object anim on same spot on curve
    # TODO: rivet
    # TODO: mirror


def getIcons(download=False):
    # online
    urlIcons = 'https://raw.github.com/boochos/shelfIcons/master'

    # local
    prefDir = cmds.internalVar(upd=1)
    iconDir = os.path.join(prefDir, 'icons')

    # get icons
    for icon in wf.icons:
        url = urlIcons + '/' + icon
        # print url
        local = os.path.join(iconDir, icon)
        # print local
        if download:
            message('downloading -- ' + local)
            cmds.refresh()
            urllib.urlretrieve(url, local)
    message('Icons downloaded.')


def createMyShelf():
    # sample code
    shelfName = 'My_Shelf'
    test = cmds.shelfLayout(shelfName, ex=True)
    if test:
        # If the shelf already exists, clear the contents and re-add the buttons.
        newShelf = shelfName
        buttons = cmds.shelfLayout(newShelf, query=True, childArray=True)
        cmds.deleteUI(buttons, control=True)
    else:
        newShelf = mel.eval('addNewShelfTab %s' % shelfName)
        cmds.setParent(newShelf)
        # add buttons here


def removeShelf():
    # sample code
    shelfName = 'My_Shelf'
    test = cmds.shelfLayout(shelfName, ex=True)
    if test:
        mel.eval('deleteShelfTab %s' % shelfName)
        gShelfTopLevel = mel.eval('$tmpVar=$gShelfTopLevel')
        cmds.saveAllShelves(gShelfTopLevel)
    else:
        return
