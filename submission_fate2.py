import os, shutil

import maya.cmds as cmds
import webrImport as web

pb = web.mod( "playblast_lib" )
ffm = web.mod( "ffMpg" )


def fate_daily( X = 0.5, layers = {}, layersOnly = False ):
    '''
    "layers" expects dict(name of render layer to create) with value as list(objects to place in render layer)
    {layer_name, [objs,etc.]}
    
    '''
    # check for wrong suffix
    path_temp = ''
    path = cmds.file( query = True, exn = True )
    revert = False
    if 'Publish' in path:
        path_temp = path.replace( 'Publish', '' )
        cmds.file( path_temp, rn = path_temp )  # rename file
        revert = True

    start = 1001
    pnl = cmds.getPanel( withFocus = True )
    cmds.editRenderLayerGlobals( crl = 'defaultRenderLayer' )
    cmds.setFocus( pnl )
    subDir = 'precomp'
    cmds.select( clear = 1 )
    #
    if not layersOnly:
        #
        result = pb.blast( x = X, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = 'precomp', play = False )  # blastPath, blastName
        # to mp4
        pathOut = result[0].replace( result[1], '' )
        pathOutName = result[1].replace( '_precomp', '____cam' )  # added cam string, burnin expects cam suffix
        mp4 = ffm.imgToMp4( pathIn = result[0], image = result[1], start = start, pathOut = pathOut, pathOutName = pathOutName )
        # copy mp4 to image seq directory, matching name
        shutil.copyfile( mp4, os.path.join( result[0], result[1] + '.mp4' ) )
        # add burn in
        ffm.burn_in( filein = mp4, startFrame = start, size = 35, rndrFrames = False )
        #
        pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_precomp' )
    #
    if layers:
        # loop through layers, create blast of each layer
        for key in layers:
            subDir = key
            sel = layers[key]
            # # if cmds.objExists(sel) loop through remove objects that dont exist, only use existing objects
            # render layer
            lyr = cmds.createRenderLayer( sel, noRecurse = True, name = subDir, makeCurrent = True )

            cmds.setFocus( pnl )
            result = pb.blast( x = X, format = "image", qlt = 100, compression = "png", offScreen = True, useGlobals = True, forceTemp = True, camStr = False, strp_r = True, subDir = subDir, play = False )
            pb.blastRenameSeq( result = result, splitStr = '_v', moveStr = '_' + subDir )
            # render layer, delete
            cmds.editRenderLayerGlobals( currentRenderLayer = 'defaultRenderLayer' )
            cmds.delete( lyr )
            # move root directory to G drive
            # shutil.copytree( src, dest )

    if revert:
        cmds.file( path, rn = path )  # rename file

'''
# statue_man
import webrImport as web
ft = web.mod('submission_fate2')
ft.fate_daily( X = 0.5, layers={'statueManBty':['rig:statue_man_model:Statue_man_High']} )

# statue_man
import webrImport as web
ft = web.mod('submission_fate2')
ft.fate_daily( X = 0.5, layers={'statueManBty':['rig:statue_man_model:Statue_man_Low']} )
'''
