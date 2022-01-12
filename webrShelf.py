import os
import platform

pyVer = 2
ver = platform.python_version()
if '2.' in ver:
    import urllib2
    import urllib
else:
    pyVer = 3
    import urllib.request

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
#
# web
wf = web.mod( 'webrFiles_lib' )
# FUTURE: when new version is pushed, server lags about 5min. Short find a
# way to time the updates


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    what = what.replace( '\\', '/' )
    global tell
    tell = what
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


class Depend():

    def __init__( self ):
        # shelf
        self.shelf = 'Web'
        self.old = 'WebrShelf_old'


def shelfRefresh():
    getIcons( download = True )
    shelfBuild()
    message( 'Shelf Refreshed!' )


def shelfRefreshWin():
    win = cmds.window( 'REFRESH_SHELF', w = 200, h = 40 )
    cmds.columnLayout( columnAttach = ( 'both', 1 ), columnAlign = ( 
        'center' ), adjustableColumn = True, rowSpacing = 10, columnWidth = 250 )
    cmds.button( 'deleteButtonShelf', c = 'import webrImport as web\nws = web.mod("webrShelf")\nws.shelfRefresh()',
                l = 'REFRESH SHELF', w = 150, h = 100 )
    cmds.showWindow( win )


def shelfRename( *args ):
    dp = Depend()
    if cmds.control( dp.shelf, q = 1, ex = 1 ):
        cmds.renameUI( dp.shelf, dp.old )
        shelfRefreshWin()


def shelfBuild( *args ):
    # shelfPrnt = 'ShelfLayout'
    dp = Depend()
    if not cmds.control( dp.shelf, q = 1, ex = 1 ):
        # build ui
        message( 'build shelf' )
        '''
        # old method, causes error
        cmds.setParent(shelfPrnt)
        cmds.shelfLayout(dp.shelf)
        '''
        mel.eval( 'addNewShelfTab %s' % dp.shelf )
        # make sure its empty
        buttons = cmds.shelfLayout( dp.shelf, query = True, childArray = True )
        if buttons:
            print( buttons )
            cmds.deleteUI( buttons, control = True )
        #
        cmds.refresh()
        # add buttons
        shelfAddButtons()
    else:
        # clean ui
        message( 'clean shelf' )
        '''
        # old method
        cmds.deleteUI(dp.shelf, control=True)
        '''
        buttons = cmds.shelfLayout( dp.shelf, query = True, childArray = True )
        if buttons:
            print( buttons )
            cmds.deleteUI( buttons, control = True )
            cmds.refresh()
        shelfAddButtons()


def shelfAddButtons( *args ):
    wh = 35
    cmds.setParent( Depend().shelf )
    # build buttons
    cmds.shelfButton( label = 'FRSH', annotation = 'refresh web shelf', w = wh, h = wh,
                     image = 'reloadShelf.png', command = 'import webrImport as web\nws = web.mod("webrShelf")\nws.shelfRefreshWin()' )

    cmds.shelfButton( label = 'quick undo', annotation = 'viewport toggle', w = wh,
                     h = wh, image = 'toggleUI.png', command = 'import webrImport as web\ncn = web.mod("constraint_lib")\ncn.uiEnable()' )

    cmds.shelfButton( label = 'quick undo', annotation = 'quick undo, viewport hide while executing undo', w = wh,
                     h = wh, image = 'quickUndo.png', command = 'import webrImport as web\ncn = web.mod("constraint_lib")\ncn.quickUndo()' )

    cmds.shelfButton( label = 'save ++', annotation = 'save ++', w = wh, h = wh, image = 'savePlus.png',
                     command = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.incrementalSave()' )

    cmds.shelfButton( label = '', annotation = 'set project from file name', w = wh, h = wh, image = 'projectSet.png',
                     command = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.setProjectFromFilename("scenes")' )

    cmds.shelfButton( label = 'temporarily save selection', annotation = 'temporarily save selection',
                     w = wh, h = wh, image = 'selStore.png', command = 'import webrImport as web\nsel = web.mod("selection")\nsl = sel.Sel()' )

    cmds.shelfButton( label = 'select saved selection', annotation = 'select saved selection',
                     w = wh, h = wh, image = 'sel.png', command = 'sl.select()' )

    cmds.shelfButton( label = 'print selection', annotation = 'print selection',
                     w = wh, h = wh, image = 'selPrint.png', command = 'sl.prnt()' )

    cmds.shelfButton( label = 'select pair script job', annotation = 'select pair script job', w = wh,
                     h = wh, image = 'selMrrOff.png', command = 'import webrImport as web\nps = web.mod("pairSelect")\nps.toggleJob()' )

    cmds.shelfButton( label = 'playblast', annotation = 'playblast', w = wh, h = wh, image = 'blast.png',
                     command = 'import webrImport as web\npb = web.mod("playblast_lib")\npb.blast(x=1, format="image", qlt=100, compression="jpg", offScreen=True )' )

    cmds.shelfButton( label = 'manage playblasts in temp folder', annotation = 'playblast Manager', w = wh, h = wh,
                     image = 'blastUI.png', command = 'import webrImport as web\npb = web.mod("playblast_lib")\npb.blastWin()' )

    cmds.shelfButton( label = 'toggle image planes on selected camera', annotation = 'toggle image planes on selected camera',
                     w = wh, h = wh, image = 'plateToggle.png', command = 'import webrImport as web\ntp = web.mod("togglePlate")\ntp.togglePlate()' )

    cmds.shelfButton( label = 'frame range to image plane range', annotation = 'toggle image planes on selected camera',
                     w = wh, h = wh, image = 'plateRange.png', command = 'import webrImport as web\ntp = web.mod("togglePlate")\ntp.plateRange()' )

    cmds.shelfButton( label = 'controller size +', annotation = 'controller size +', w = wh, h = wh,
                     image = 'ctrPlus.png', command = 'import webrImport as web\nds = web.mod("display_lib")\nds.shapeSize(mltp=1.1)' )

    cmds.shelfButton( label = 'controller size -', annotation = 'controller size -', w = wh, h = wh,
                     image = 'ctrMinus.png', command = 'import webrImport as web\nds = web.mod("display_lib")\nds.shapeSize(mltp=0.9)' )

    cmds.shelfButton( label = 'character set import ui', annotation = 'character set import ui', w = wh,
                     h = wh, image = 'csIm.png', command = 'import webrImport as web\ncsUI = web.mod("characterUI_macro_lib")\ncsUI.CSUI()' )

    cmds.shelfButton( label = 'character set export ui', annotation = 'character set export ui', w = wh, h = wh,
                     image = 'csEx.png', command = 'import webrImport as web\ncsUI = web.mod("characterUI_macro_lib")\ncsUI.CSUI(export=True)' )

    cmds.shelfButton( label = 'toggle membership', annotation = 'toggle membership of object from current character set', w = wh,
                     h = wh, image = 'csMbrTgl.png', command = 'import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.toggleMembershipToCurrentSet()' )

    cmds.shelfButton( label = 'flush character sets temporarily', annotation = 'flush character sets temporarily',
                     w = wh, h = wh, image = 'flush.png', command = 'import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.flush()' )

    cmds.shelfButton( label = 'unflush character sets ', annotation = 'unflush character sets ', w = wh,
                     h = wh, image = 'flushUn.png', command = 'import webrImport as web\ncs = web.mod("characterSet_lib")\ncs.unflush()' )

    cmds.shelfButton( label = 'graph editor buttons', annotation = 'graph editor buttons', w = wh,
                     h = wh, image = 'geBttns.png', command = 'import webrImport as web\nds = web.mod("display_lib")\nds.graphEditorButtons()' )

    cmds.shelfButton( label = 'gather frame numbers', annotation = 'gather frame numbers of first selection\ninsert keys on same frames to all consecutive objects\nremove non matching frames',
                     w = wh, h = wh, image = 'matchKeys.png', command = 'import webrImport as web\ncn = web.mod("constraint_lib")\ncn.matchKeyedFramesLoop()' )

    cmds.shelfButton( label = 'move first object to the location of second', annotation = 'move first object to the location of second',
                     w = wh, h = wh, image = 'matchAll.png', command = 'import webrImport as web\nanm = web.mod("anim_lib")\nanm.matchObj()' )

    cmds.shelfButton( label = 'constraint tools', annotation = 'constraint tools', w = wh, h = wh,
                     image = 'helpersUI.png', command = 'import webrImport as web\ncnUI = web.mod("constraintUI_macro_lib")\ncnUI.CSUI()' )

    cmds.shelfButton( label = 'select selection', annotation = 'select selection set\nread from text file\nobjects cannot be in multiple sets',
                     w = wh, h = wh, image = 'selSet.png', command = 'import webrImport as web\nss = web.mod("selectionSet_lib")\nss.selectSet()' )

    cmds.shelfButton( label = 'create selection set files', annotation = 'create selection set files', w = wh,
                     h = wh, image = 'selSetUI.png', command = 'import webrImport as web\nsUI = web.mod("selectionUI_macro_lib")\nsUI.CSUI()' )

    cmds.shelfButton( label = 'anim is exported to a file', annotation = 'anim is exported to a file', w = wh,
                     h = wh, image = 'animOut.png', command = 'import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipSave(name="tempClip", temp=True)' )

    cmds.shelfButton( label = 'anim is imported from a file', annotation = 'anim is imported from a file', w = wh, h = wh,
                     image = 'animIn.png', command = 'import webrImport as web\ncp = web.mod("clipPickle_lib")\ncp.clipApply(path=cp.clipDefaultTempPath() + "tempClip.clip")' )

    cmds.shelfButton( label = 'clip library', annotation = 'Clip Library', w = wh,
                     h = wh, imageOverlayLabel = '', image = 'animUI.png', command = 'import webrImport as web\ncpui = web.mod("clipPickleUI_macro_lib")\ncpui.CPUI()' )

    cmds.shelfButton( label = 'warp time ui', annotation = 'warp time ui', w = wh, h = wh,
                     image = 'warpTimeUI.png', command = 'import webrImport as web\nar = web.mod("animRetime_lib")' )

    cmds.shelfButton( label = 'speed attribute is added', annotation = 'speed attribute is added', w = wh,
                     h = wh, image = 'kmh.png', command = 'import webrImport as web\nds = web.mod("display_lib")\nds.speed(local=0)' )

    cmds.shelfButton( label = 'select 2 objects', annotation = 'select 2 objects\ndistance attribute is added\nattr only updates on frame changes',
                     w = wh, h = wh, image = 'distance.png', command = 'import webrImport as web\ndis = web.mod("display_lib")\ndis.distance()' )

    cmds.shelfButton( label = 'select camera', annotation = 'select camera\ntoggles frustum',
                     w = wh, h = wh, image = 'frustum.png', command = 'import webrImport as web\nal = web.mod("anim_lib")\nal.toggleFrustum()' )

    cmds.shelfButton( label = 'select object', annotation = 'select object\nconstrains new camera to object',
                     w = wh, h = wh, image = 'followCam.png', command = 'import webrImport as web\ncam = web.mod("camera_lib")\ncam.follow_cam()' )

    # 'import display_lib as dis\nreload(dis)\ndis.distance()'
    # 'import webrImport as web\ndis = web.mod("display_lib")\ndis.distance()'

    # TODO: timewarp tool
    # TODO: timewarp with path anim, uisng some combo to sync path anim to, anim layer as time warp to keep object anim on same spot on curve
    # TODO: rivet
    # TODO: mirror


def getIcons( download = False ):
    # online
    urlIcons = 'https://raw.github.com/boochos/shelfIcons/master'

    # local
    prefDir = cmds.internalVar( upd = 1 )
    iconDir = os.path.join( prefDir, 'icons' )

    # get icons
    for icon in wf.icons:
        url = urlIcons + '/' + icon
        # print url
        local = os.path.join( iconDir, icon )
        # print local
        if download:
            message( 'downloading -- ' + local )
            print()  # adds new line
            cmds.refresh()
            #
            if pyVer == 2:
                urllib.urlretrieve( url, local )
            else:
                urllib.request.urlretrieve( url, local )
    message( 'Icons downloaded.' )


def createMyShelf():
    # sample code
    shelfName = 'My_Shelf'
    test = cmds.shelfLayout( shelfName, ex = True )
    if test:
        # If the shelf already exists, clear the contents and re-add the
        # buttons.
        newShelf = shelfName
        buttons = cmds.shelfLayout( newShelf, query = True, childArray = True )
        cmds.deleteUI( buttons, control = True )
    else:
        newShelf = mel.eval( 'addNewShelfTab %s' % shelfName )
        cmds.setParent( newShelf )
        # add buttons here


def removeShelf():
    # sample code
    shelfName = 'My_Shelf'
    test = cmds.shelfLayout( shelfName, ex = True )
    if test:
        mel.eval( 'deleteShelfTab %s' % shelfName )
        gShelfTopLevel = mel.eval( '$tmpVar=$gShelfTopLevel' )
        cmds.saveAllShelves( gShelfTopLevel )
    else:
        return
