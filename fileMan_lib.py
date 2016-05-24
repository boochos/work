import maya.cmds as cmds
import maya.mel as mel
import os
import subprocess


def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')


def setProjectFromFilename(dirVar):
    path = cmds.file(query=True, sceneName=True)
    # print path
    if len(path) > 0:
        idx = path.rfind(dirVar)
        # print idx
        if idx > -1:
            if os.name == 'nt':
                setPath = path[:idx - 1]
            else:
                setPath = path[:idx + len(dirVar)]
            print setPath
            mel.eval('setProject "' + setPath + '";')
            message('Project set to: %s' % (setPath))
        else:
            # print '\n'
            cmds.warning('\\"3D\\" not found in path, setProject aborted.')
    else:
        cmds.warning('No file path found, operation aborted.')


def splitEndNumFromString(name):
    num = ''
    rName = ''
    for i in name:
        try:
            int(i)
            num += i
        except:
            rName += num + i
            num = ''
    if num == '':
        extracted = '%04d' % (0000)
    else:
        extracted = '%04d' % (int(num))

    return rName, extracted


def parseSceneFilePath(path):
    #return_list = []
    # if path is empty, the scene hasn't not been saved yet
    if not len(path):
        print 'Save the scene first using the correct naming convention, name_#### ".ma" or ".mb"'
        return False
    else:
        # look for the furthest '.' to make sure there is an extension
        if path.rfind('.') > -1:
            # split the scene file name appart
            basename = os.path.basename(path).split('.')[0]
            extension = os.path.basename(path).split('.')[1]
            basepath = os.path.dirname(path)
            return [basepath, basename, extension]
        else:
            return False


def incrementalSave(*args):

    scene = cmds.file(query=True, sn=True)
    scene_info = parseSceneFilePath(scene)

    # make sure the correct file format is being used
    if scene_info is not False:
        # if no number was found, force it to 0000
        # find the highest version of the current scene name in the folder, then increment the current scene to one more than that then save
        files = os.listdir(scene_info[0])
        num = 0000
        string_info = splitEndNumFromString(scene_info[1])

        for f in files:
            # make sure the current file is not a directory
            if os.path.isfile(os.path.join(scene_info[0], f)):
                # remove any file that has a '.' in the front of it
                if f[0] != '.':
                    phile = parseSceneFilePath(os.path.join(scene_info[0], f))
                    if phile is not False:
                        file_info = splitEndNumFromString(phile[1])
                        if string_info[0] == file_info[0]:
                            if file_info[1] > num:
                                num = file_info[1]
        # increment the suffix
        version = '%04d' % (int(num) + 1)
        name = os.path.join(scene_info[0], string_info[0]) + str(version) + '.' + scene_info[2]
        name = name.replace('\\', '/')
        # get the current file type
        fileType = cmds.file(query=True, typ=True)
        # add the file about to be saved to the recent files menu
        mel.eval('addRecentFile "' + name + '" ' + fileType[0] + ';')
        # rename the current file
        cmds.file(name, rn=name)
        # save it
        cmds.file(save=True, typ=fileType[0])


def openDirFromScenePath(inDir='maya', openDir='movies'):
    path = cmds.file(query=True, sceneName=True)
    if len(path) > 0:
        i = path.rfind(inDir)
        if i > -1:
            if os.name == 'nt':
                path = path[:i + len(inDir)]
                path = path + '/' + openDir
                path = path.replace('/', '\\')
                if os.path.isdir(path):
                    subprocess.Popen(r'explorer /open, ' + path)
            else:
                path = path[:i + len(inDir)]
                app = "nautilus"
                call([app, path])
        else:
            print '\n'
            cmds.warning(inDir + '  --  not found in path')
    else:
        cmds.warning('No file path found, operation aborted.')
