import os
import urllib  # need this for downloading icons, line is sometimes commented out

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
# web
wf = web.mod( 'webrFiles_lib' )
# FUTURE: when new version is pushed, server lags about 5min. Short find a way to time the updates


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


class Depend():

    def __init__( self ):
        # shelf
        self.shelf = 'WebRig'
        self.old = 'WebRigShelf_old'
        self.ref = 'REFRESH_RIG_SHELF'


def shelfRefresh():
    getIcons( download = False )
    shelfBuild()
    cmds.deleteUI( Depend().ref )


def shelfRefreshWin():
    win = cmds.window( 'REFRESH_RIG_SHELF', w = 200, h = 40 )
    cmds.columnLayout( columnAttach = ( 'both', 1 ), columnAlign = ( 
        'center' ), adjustableColumn = True, rowSpacing = 10, columnWidth = 250 )
    cmds.button( 'deleteButtonRigShelf', c = 'import webrImport as web\nwrs = web.mod("webrRigShelf")\nwrs.shelfRefresh()',
                l = 'REFRESH RIG SHELF', w = 150, h = 100 )
    cmds.showWindow( win )


def shelfBuild( *args ):
    # shelfPrnt = 'ShelfLayout'
    dp = Depend()
    if not cmds.control( dp.shelf, q = 1, ex = 1 ):
        # build ui
        mel.eval( 'addNewShelfTab %s' % dp.shelf )
        cmds.refresh()
        shelfAddButtons()
    else:
        # clean ui
        buttons = cmds.shelfLayout( dp.shelf, query = True, childArray = True )
        if buttons:
            cmds.deleteUI( buttons, control = True )
            cmds.refresh()
            # print 'deleting_____________\n', buttons
        shelfAddButtons()


def shelfAddButtons( *args ):
    wh = 35
    cmds.setParent( Depend().shelf )
    # build buttons
    cmds.shelfButton( label = 'FRSH', annotation = 'refresh rig shelf', w = wh, h = wh,
                     image = 'refreshWeb.png', command = 'import webrImport as web\nwrs = web.mod("webrRigShelf")\nwrs.shelfRefreshWin()' )

    cmds.shelfButton( label = 'save ++', annotation = 'save ++', w = wh, h = wh, image = 'save++_icon.xpm',
                     command = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.incrementalSave()' )

    cmds.shelfButton( label = '', annotation = 'set project from file name', w = wh, h = wh, image = 'PrjtSet.xpm',
                     command = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.setProjectFromFilename("scenes")' )

    cmds.shelfButton( label = 'temporarily save selection', annotation = 'temporarily save selection',
                     w = wh, h = wh, image = 'selStore.xpm', command = 'import webrImport as web\nsel = web.mod("selection")\nsl = sel.Sel()' )

    cmds.shelfButton( label = 'select saved selection', annotation = 'select saved selection',
                     w = wh, h = wh, image = 'sel.xpm', command = 'sl.select()' )

    cmds.shelfButton( label = 'print selection', annotation = 'print selection',
                     w = wh, h = wh, image = 'PrntSel.xpm', command = 'sl.prnt()' )

    cmds.shelfButton( label = 'ATOM', annotation = 'ATOM UI', w = wh, h = wh,
                     image = 'Atom.xpm', command = 'import webrImport as web\natom = web.mod("atom_lib")\natom.win()' )

    cmds.shelfButton( label = 'Atom Weight Util', annotation = 'Atom Weight Util', w = wh, h = wh, image = 'AtmWghtUtl.xpm',
                     command = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.weightingUtilWinv02()' )

    cmds.shelfButton( label = 'Joint Orient Util', annotation = 'Joint Orient Util',
                     w = wh, h = wh, image = 'AtomUtl.xpm', command = 'import webrImport as web\nweb.mod("cometJointOrient.mel")\nimport maya.mel as mel\nmel.eval("cometJointOrient()")' )

    cmds.shelfButton( label = 'Atom Influence Match', annotation = 'Atom Influence Match', w = wh, h = wh,
                     image = 'AtmTrnsfrInflnc.xpm', command = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.transferInfWin()' )

    cmds.shelfButton( label = 'Atom Surface Rig', annotation = 'Atom Surface Rig', w = wh, h = wh,
                     image = 'AtmSrfcRg.xpm', command = 'import webrImport as web\nasr = web.mod("atom_surfaceRig_lib")\nasr.win()' )

    cmds.shelfButton( label = 'Atom Lock Attr UI', annotation = 'Atom Lock Attr UI', w = wh,
                     h = wh, image = 'AtomLck.xpm', command = 'import webrImport as web\naul = web.mod("atom_utilities_lib")\naul.atomLockWin()' )

    cmds.shelfButton( label = 'Atom Update Mesh', annotation = 'Atom Update Mesh', w = wh, h = wh,
                     image = 'AtmMshUpdt.xpm', command = 'import webrImport as web\naum = web.mod("atom_updateMesh_lib")\naum.win()' )

    cmds.shelfButton( label = 'Atom Tag UI', annotation = 'Atom Tag UI', w = wh, h = wh,
                     image = 'TagUI.xpm', command = 'import webrImport as web\ntg = web.mod("atom_tag_lib")\ntg.Atom_Tag_Win().win()' )

    cmds.shelfButton( label = 'Atom Zero Joint Orient', annotation = 'Atom Zero Joint Orient', w = wh, h = wh,
                     image = 'Zero.xpm', command = 'import webrImport as web\njnt = web.mod("atom_joint_lib")\njnt.zeroJntSelection()' )

    cmds.shelfButton( label = 'save scene ui', annotation = 'save scene ui', w = wh,
                     h = wh, image = 'saveFileUI.xpm', command = 'import webrImport as web\nkui = web.mod("key_ui")\nkui.saveSceneWin()' )


def getIcons( download = False ):
    # online
    urlIcons = 'https://raw.github.com/boochos/shelfIcons/master'

    # local
    prefDir = cmds.internalVar( upd = 1 )
    iconDir = os.path.join( prefDir, 'icons' )

    # get icons
    for icon in wf.iconsRig:
        url = urlIcons + '/' + icon
        # print url
        local = os.path.join( iconDir, icon )
        # print local
        if download:
            message( 'downloading -- ' + local )
            cmds.refresh()
            urllib.urlretrieve( url, local )
