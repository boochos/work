import os, shutil

import maya.cmds as cmds
import webrImport as web

pb = web.mod( "playblast_lib" )


def elos_daily():
    '''
    create daily package and move to G folder
    '''
    #
    project = 'ELOS'
    groot = 'G:/Shared drives'
    pnl = cmds.getPanel( withFocus = True )

    # daily burn-in / master render layer
    cmds.editRenderLayerGlobals( crl = 'defaultRenderLayer' )
    cmds.setFocus( pnl )
    # result = [u'C:/Users/sebas/Documents/maya/__PLAYBLASTS__\\154-080_anim_v001_r018\\154-080_anim_v001_dragonflySimBty', u'154-080_anim_v001_dragonflySimBty']
    result = pb.blast( x = 0.50, format = "qt", qlt = 100, compression = "H.264", offScreen = True, useGlobals = True, forceTemp = True, burnIn = True, burnInSize = 30, play = False )
    pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_precomp' )

    # source
    result[0] = result[0].replace( '\\', '/' )
    src = result[0].split( result[1] )[0]
    src = src[0:-1]
    version = src.split( '/' )[-1]
    # destination
    dest_partial1 = cmds.file( q = True, sn = True )  # P:/ELOS/154/154-080/anim/maya/scenes/154-080_anim_v001_r018.ma
    dest_partial1 = dest_partial1.replace( 'P:', groot )
    dest_partial1 = dest_partial1.split( 'maya' )[0]
    dest_partial2 = 'playblasts'  # G:\Shared drives\ELOS\154\154-080\anim\playblasts
    dest = os.path.join( dest_partial1, dest_partial2, version )

    # added few operations between deletion of old version to copy of new. Windows lags in acknowledging the path is gone. throws error
    print( dest, 'here' )  #

    if os.path.isdir( dest ):
        try:
            shutil.rmtree( dest )
        except:
            print( 'Couldnt delete directory. Perhaps Explorer window is open inside directory OR directory is syncing' )

    # daily hero render layer is exists
    go = True
    subDir = 'dragonflyBty'
    try:
        cmds.editRenderLayerGlobals( crl = subDir )
    except:
        go = False
    if go:
        cmds.setFocus( pnl )
        result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = subDir, play = False )
        pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_' + subDir )

    # daily sim render layer if exists
    go = True
    subDir = 'dragonflySimBty'
    try:
        cmds.editRenderLayerGlobals( crl = subDir )
    except:
        go = False
    if go:
        cmds.setFocus( pnl )
        result = pb.blast( x = 0.5, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = subDir, play = False )
        pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_' + subDir )

    # move root directory to G drive
    shutil.copytree( src, dest )
