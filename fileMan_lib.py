import os
import subprocess

import maya.cmds as cmds
import maya.mel as mel


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            print what


def setProjectFromFilename( dirVar ):
    path = cmds.file( query = True, sceneName = True )
    # print path
    if len( path ) > 0:
        idx = path.rfind( dirVar )
        # print idx
        if idx > -1:
            if os.name == 'nt':
                setPath = path[:idx - 1]
            else:
                setPath = path[:idx + len( dirVar )]
            print setPath
            mel.eval( 'setProject "' + setPath + '";' )
            message( 'Project set to: %s' % ( setPath ) )
        else:
            # print '\n'
            cmds.warning( '\\"3D\\" not found in path, setProject aborted.' )
    else:
        cmds.warning( 'No file path found, operation aborted.' )


def splitEndNumFromString( name ):
    num = ''
    rName = ''
    for i in name:
        try:
            int( i )
            num += i
        except:
            rName += num + i
            num = ''
    if num == '':
        extracted = '%04d' % ( 0000 )
    else:
        extracted = '%04d' % ( int( num ) )

    return rName, extracted


def parseSceneFilePath( path ):
    # return_list = []
    # if path is empty, the scene hasn't not been saved yet
    if not len( path ):
        print 'Save the scene first using the correct naming convention, name_#### ".ma" or ".mb"'
        return False
    else:
        # look for the furthest '.' to make sure there is an extension
        if path.rfind( '.' ) > -1:
            # split the scene file name appart
            basename = os.path.basename( path ).split( '.' )[0]
            extension = os.path.basename( path ).split( '.' )[1]
            basepath = os.path.dirname( path )
            return [basepath, basename, extension]
        else:
            return False


def incrementalSave( *args ):

    scene = cmds.file( query = True, sn = True )
    scene_info = parseSceneFilePath( scene )

    # make sure the correct file format is being used
    if scene_info is not False:
        # if no number was found, force it to 0000
        # find the highest version of the current scene name in the folder, then increment the current scene to one more than that then save
        files = os.listdir( scene_info[0] )
        num = 000
        string_info = splitEndNumFromString( scene_info[1] )

        for f in files:
            # make sure the current file is not a directory
            if os.path.isfile( os.path.join( scene_info[0], f ) ):
                # remove any file that has a '.' in the front of it
                if f[0] != '.':
                    phile = parseSceneFilePath( os.path.join( scene_info[0], f ) )
                    if phile is not False:
                        file_info = splitEndNumFromString( phile[1] )
                        if string_info[0] == file_info[0]:
                            if file_info[1] > num:
                                num = file_info[1]
        # increment the suffix
        version = '%03d' % ( int( num ) + 1 )
        name = os.path.join( scene_info[0], string_info[0] ) + str( version ) + '.' + scene_info[2]
        name = name.replace( '\\', '/' )
        # get the current file type
        fileType = cmds.file( query = True, typ = True )
        # add the file about to be saved to the recent files menu
        mel.eval( 'addRecentFile "' + name + '" ' + fileType[0] + ';' )
        # rename the current file
        cmds.file( name, rn = name )
        # save it
        cmds.file( save = True, typ = fileType[0] )


def openDirFromScenePath( inDir = 'maya', openDir = 'movies' ):
    path = cmds.file( query = True, sceneName = True )
    if len( path ) > 0:
        i = path.rfind( inDir )
        if i > -1:
            if os.name == 'nt':
                path = path[:i + len( inDir )]
                path = path + '/' + openDir
                path = path.replace( '/', '\\' )
                if os.path.isdir( path ):
                    subprocess.Popen( r'explorer /open, ' + path )
            else:
                path = path[:i + len( inDir )]
                app = "nautilus"
                call( [app, path] )
        else:
            print '\n'
            cmds.warning( inDir + '  --  not found in path' )
    else:
        cmds.warning( 'No file path found, operation aborted.' )


def makeRefWindow():
    # make obj a reference
    path = cmds.file( q = True, sceneName = True )
    win = 'Convert_to_ref'
    # ui
    try:
        cmds.deleteUI( win )
    except:
        pass
    if path:
        pth = path.split( '/' )
        pth = pth[len( pth ) - 1]
        path = path.split( pth )[0]
        cmds.window( win, title = 'Convert to Reference' )
        cmds.columnLayout( adj = True )
        pathFld = cmds.textFieldGrp( label = 'Path: ', text = path, cal = ( 1, 'left' ), adj = 2, cw = ( 1, 80 ), editable = False )
        fileField = cmds.textFieldGrp( label = 'Filename: ', text = '', cal = ( 1, 'left' ), adj = 2, cw = ( 1, 80 ) )
        nsField = cmds.textFieldGrp( label = 'NameSpace: ', text = '', cal = ( 1, 'left' ), adj = 2, cw = ( 1, 80 ) )
        # ns auto fill
        vars = 'fileField="%s", nsField="%s"' % ( fileField, nsField, )
        cmd = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.cmd_fillNs(%s)' % vars
        cmds.textFieldGrp( fileField, e = True, cc = cmd )
        # file export vars
        vars = 'pathField="%s", fileField="%s", nsField="%s"' % ( pathFld, fileField, nsField, )
        cmd = 'import webrImport as web\nfm = web.mod("fileMan_lib")\nfm.cmd_makeRefOfSelection(%s)' % vars
        cmds.button( label = 'Convert', c = cmd )
        cmds.showWindow()
    else:
        message( 'save current scene before exporting', warning = True )


def cmd_fillNs( fileField = '', nsField = '', *args ):
    ns = cmds.textFieldGrp( fileField, q = True, text = True )
    cmds.textFieldGrp( nsField, e = True, text = ns )


def cmd_makeRefOfSelection( pathField = '', fileField = '', nsField = '', *args ):
    path = cmds.textFieldGrp( pathField, q = True, text = True )
    fyle = cmds.textFieldGrp( fileField, q = True, text = True )
    ns = cmds.textFieldGrp( nsField, q = True, text = True )
    nsList = cmds.namespaceInfo( lon = True )
    sel = cmds.ls( sl = True )
    if sel:
        f = fyle
        if f:
            path = os.path.join( path, f )
        else:
            message( 'Provide a file name, excluding path.', warning = True )
            return None
        if ns:
            if ns not in nsList:
                try:
                    cmds.file( path, type = 'mayaAscii', er = True, namespace = ns )
                except:
                    message( 'Export Failed... In case your object is already a reference, make a duplicate or import it. Then try again.', warning = True )
            else:
                message( 'Namespace "' + ns + '" already exists. Choose another!', warning = True )
        else:
            message( 'Provide a namespace for the reference.', warning = True )
            return None
    else:
        message( 'Select and object', warning = True )
