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
# FUTURE: when new version is pushed, server lags about 5min. Short find a way to time the updates


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
        self.shelf = 'WebRig'
        self.old = 'WebRigShelf_old'
        self.ref = 'REFRESH_RIG_SHELF'


def shelfRefresh():
    getIcons( download = True )
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
                     image = 'reloadShelf.png', command = 'import webrImport as web\nwrs = web.mod("webrRigShelf")\nwrs.shelfRefreshWin()' )

    cmds.shelfButton( label = 'save scene ui', annotation = 'save scene ui', w = wh,
                     h = wh, image = 'saveUi.png', command = 'import webrImport as web\nkui = web.mod("key_ui")\nkui.saveSceneWin()' )

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

    cmds.shelfButton( label = 'ATOM', annotation = 'ATOM UI', w = wh, h = wh,
                     image = 'atom.png', command = 'import webrImport as web\natom = web.mod("atom_lib")\natom.win()' )

    cmds.shelfButton( label = 'Atom Weight Util', annotation = 'Atom Weight Util', w = wh, h = wh, image = 'atomWgt.png',
                     command = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.weightingUtilWinv02()' )

    cmds.shelfButton( label = 'Joint Orient Util', annotation = 'Joint Orient Util',
                     w = wh, h = wh, image = 'atomJnt.png', command = 'import webrImport as web\nweb.mod("cometJointOrient.mel")\nimport maya.mel as mel\nmel.eval("cometJointOrient()")' )

    cmds.shelfButton( label = 'Atom Influence Match', annotation = 'Atom Influence Match', w = wh, h = wh,
                     image = 'atomInf.png', command = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.transferInfWin()' )

    cmds.shelfButton( label = 'Atom Surface Rig', annotation = 'Atom Surface Rig', w = wh, h = wh,
                     image = 'atomSrf.png', command = 'import webrImport as web\nasr = web.mod("atom_surfaceRig_lib")\nasr.win()' )

    cmds.shelfButton( label = 'Atom Lock Attr UI', annotation = 'Atom Lock Attr UI', w = wh,
                     h = wh, image = 'atomAtr.png', command = 'import webrImport as web\naul = web.mod("atom_utilities_lib")\naul.atomLockWin()' )

    cmds.shelfButton( label = 'Atom Update Mesh', annotation = 'Atom Update Mesh', w = wh, h = wh,
                     image = 'atomUM.png', command = 'import webrImport as web\naum = web.mod("atom_updateMesh_lib")\naum.win()' )

    cmds.shelfButton( label = 'Atom Tag UI', annotation = 'Atom Tag UI', w = wh, h = wh,
                     image = 'atomTag.png', command = 'import webrImport as web\ntg = web.mod("atom_tag_lib")\ntg.Atom_Tag_Win().win()' )

    cmds.shelfButton( label = 'Atom Zero Joint Orient', annotation = 'Atom Zero Joint Orient', w = wh, h = wh,
                     image = 'zeroJnt.png', command = 'import webrImport as web\njnt = web.mod("atom_joint_lib")\njnt.zeroJntSelection()' )


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
            print()  # adds new line
            cmds.refresh()
            #
            if pyVer == 2:
                urllib.urlretrieve( url, local )
            else:
                urllib.request.urlretrieve( url, local )
