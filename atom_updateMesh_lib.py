import os

import maya.cmds as cmds
import maya.mel as mm


def makeFileDict( path ):
    '''Open a file and read the contents into a dictionary
    path:<string>":path to file file to open
    return:<dictionary>
    Notes: expected format in file is as follows, variable=var contents, eg: mesh=someMesh
    '''
    # qualify the path
    if os.path.exists( path ):
        # open the file
        read_file = open( path, 'r' )
        # read the file contents
        file_info = read_file.readlines()
        # close the file
        read_file.close()
        # prepare the return dictionary
        out_dict = {}
        # populate the out_dict
        for info in file_info:
            # remove any whitespaces
            strip = info.strip()
            # split the line into a list using "=" as the splitter
            lineList = info.split( '=' )
            # clean the list
            var = lineList[0].strip()
            var_input = lineList[1].strip()
            # populate the dict
            out_dict[var] = var_input
        return out_dict
    else:
        print( '%s does not exist, action cancelled.' % ( path ) )


def updatePathCMD( window ):
    '''update the text field in the "window"
    window:<ELF window object>
    '''
    # get the current path
    path = cmds.textField( window + '_txtFld', tx = True, query = True )
    print( path )
    # 'mesh_update_info' is a hardcoded folder, make sure the path exists
    if os.path.exists( path ):
        cmds.textFieldButtonGrp( 'atom_meshUpdatePath_tfbg', edit = True, tx = path )
        cmds.button( 'atom_meshUpdate_button', edit = True, en = True )
    else:
        print( 'mesh_update_info folder not found. Browse to folder to continue.' )
        cmds.button( 'atom_meshUpdate_button', edit = True, en = False )
    cmds.deleteUI( window )


def updateMeshCMD( path = None ):
    '''This calls the actual upDateMesh function. It's set up this way incase the function ever needs to
    be called from command line.
    '''
    # if no path is given, this command isn't being called command line
    if path == None:
        # Query the gui for path information
        updateMesh( path = cmds.textFieldButtonGrp( 'atom_meshUpdatePath_tfbg', query = True, tx = True ) )
    # Command line
    else:
        updateMesh( path )


def backupCMD( path ):
    '''Create a backup folder in the "path"
    '''
    # check if the directory exists
    pathCheck = os.path.join( os.path.dirname( path ), 'mesh_update_scene_backup' )
    # if no directory exists, create it
    if os.path.exists( pathCheck ) != True:
        print( 'Backup directory does not exists, creating:\n\t %s' % ( pathCheck ) )
        os.mkdir( pathCheck, 0777 )


def updateMesh( path, backup = True ):
    '''
    Function that interates through all the .txt files in the path.This function creates a reference, then connects the outMesh to the inMesh and 
    removes the reference.
    '''
    print( '___ ' )
    if len( path ) > 0:
        # list the files in the "path"
        update_files = os.listdir( path )
        base_mesh = ''
        out_dict = ''
        # Build the full path
        outPath = os.path.join( path, 'outmesh.txt' )
        print( outPath )

        # test that outmesh.txt exists, this file is key and needs to be in the path directory
        if os.path.exists( outPath ) == True:
            out_dict = makeFileDict( outPath )
            print( out_dict )
            # read each file in the mesh_update_info path
            for i in update_files:
                # skip and files that start with '.' and skip the "outmesh.txt" file
                if i[0] != '.' and i != 'outmesh.txt':
                    # make sure that the outmesh.txt has been read in, in case that file doesn't exists
                    if len( out_dict ) != 0:
                        # read in the data from the current update file
                        in_dict = makeFileDict( os.path.join( path, i ) )
                        # open the file specified in "path"
                        print( 'file:  ', in_dict['path'] )
                        cmds.file( in_dict['path'], o = True, f = True )
                        print( in_dict['path'] )
                        if backup == True:
                            # make sure 'mesh_update_scene_backup' folder exists in the path
                            backupCMD( in_dict['path'] )
                            # This call to path will return unexpected results if there are more than one '.' in the name
                            name = os.path.basename( in_dict['path'].split( '.' )[0] )
                            # build the save path
                            savepath = os.path.join( os.path.dirname( in_dict['path'] ), 'mesh_update_scene_backup' )
                            # get the current name of the file
                            currentName = cmds.file( query = True, exn = True )
                            # get the file type
                            fileType = cmds.file( query = True, type = True )[0]
                            # name this file, save it into the backup folder then rename it back to its original name
                            cmds.file( rename = os.path.join( savepath, name + '_backup' ) )
                            cmds.file( save = True, type = fileType )
                            cmds.file( rename = currentName )

                        # reference in the outmesh file
                        ref_file = cmds.file( out_dict['path'], r = True , namespace = out_dict['ref'], type = 'mayaBinary' )
                        # interate through all the enteries in the update file
                        for geo in in_dict:
                            # skip path and ref entries
                            if geo != 'path' and geo != 'ref':
                                # None is specified when geo doesn't exist in the scene
                                if in_dict[geo] != 'None':
                                    # find the skinCluster on the specified geo
                                    skin = mm.eval( 'findRelatedSkinCluster("' + in_dict[geo] + '")' )
                                    # get the shapeNode
                                    inShape = cmds.listRelatives( in_dict[geo], shapes = True )[0]
                                    # if the object is skinned, the shapeOrig is required for connection
                                    if len( skin ) != 0:
                                        inShape = cmds.listRelatives( in_dict[geo], shapes = True )[1]
                                    # get the shapeNode for the .outMesh connection
                                    outShape = cmds.listRelatives( out_dict['ref'] + ':' + out_dict[geo], type = 'shape' )[0]

                                    # connect the "outShape.outMesh" to the "inShape.inMesh"
                                    cmds.connectAttr( outShape + '.outMesh', inShape + '.inMesh' )
                                    print( inShape )
                                    # bake the history into the inShape, if this isn't done everything reverts back to it's state post connection
                                    cmds.bakePartialHistory( inShape )
                        # remove the reference
                        cmds.file( ref_file , rr = True )
                        cmds.file( save = True, type = fileType )
                    else:
                        print( '!!!!! outmesh.txt file not found, update halted !!!!!' )
                else:
                    print( '3' )
        else:
            print( '1' )
    else:
        print( 'No valid path exists!' )


def  dirDialog( *args ):
    '''Creates a window to browse to the 'mesh_update_info' folder.
    '''
    import key_ui_lib
    winName = 'keyMeshdirDialogWin'
    if cmds.window( winName, ex = True ):
        cmds.deleteUI( winName )
    returnPath = key_ui_lib.DirDialog( winName, 'Set mesh update folder', cmds.workspace( query = True, o = True ),
                                      'Set mesh update folder', 'from atom import atom_updateMesh_lib\natom_updateMesh_lib.updatePathCMD("' + winName + '")' )
    returnPath.dirWin()


def deleteDirDialog( *args ):
    '''This function is called by a script job that's created when the updateMeshWin window is open
    This will delete the dirDialog window when the update mesh window is closed
    '''
    if cmds.window( 'keyMeshdirDialogWin', ex = True ):
        cmds.deleteUI( 'keyMeshdirDialogWin' )


def win( *args ):
    '''Window used to update the mesh
    '''
    # if any windows are open that deal with updating the mesh, close them
    winList = ['atom_meshUpdateWin', 'keyMeshdirDialogWin']
    for win in winList:
        if cmds.window( win, ex = True ):
            cmds.deleteUI( win )
    # create the window
    cmds.window( 'atom_meshUpdateWin', title = 'Atom Mesh Update' )
    cmds.columnLayout( co = ['both', 5], adj = True, rs = 5 )
    path = os.path.join( cmds.workspace( query = True, o = True ), 'scenes/anim/template_rig/CharactersWork/SantaPup/RIG/mesh_update_info' )
    button_state = True
    # Test if the mesh_update_folder is the current path, this will usually be false
    if os.path.exists( path ) != True:
        print( path )
        path = cmds.workspace( query = True, o = True )
        button_state = False
        print( 'mesh_update_info folder not found. Browse to folder to continue.' )

    cmds.textFieldButtonGrp( 'atom_meshUpdatePath_tfbg', label = 'Path:', tx = path, buttonLabel = 'Set Path', ct3 = ['left', 'both', 'left'],
                            co3 = [0, 0, 5], cl3 = ['left', 'center', 'center'], ad3 = 2, cw3 = [35, 100, 80], bc = 'from atom import atom_updateMesh_lib\natom_updateMesh_lib.dirDialog()' )
    cmds.button( 'atom_meshUpdate_button', l = 'Update Mesh', c = 'from atom import atom_updateMesh_lib\natom_updateMesh_lib.updateMeshCMD()', en = button_state )
    cmds.scriptJob( runOnce = True, uid = ['atom_meshUpdateWin', 'from atom import atom_updateMesh_lib\natom_updateMesh_lib.deleteDirDialog()'] )
    cmds.showWindow( 'atom_meshUpdateWin' )
