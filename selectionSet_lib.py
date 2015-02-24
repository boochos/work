import os
import maya.cmds as cmds
import maya.mel as mel
import json

tell = ''


def message(what='', maya=True, warning=False):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace('\\', '/')
    if warning:
        cmds.warning(what)
    else:
        if maya:
            mel.eval('print \"' + what + '\";')
        else:
            print what


def createDefaultPath():
    # main path
    path = defaultPath()
    if not os.path.isdir(path):
        os.mkdir(path)
        message("path:   '" + path + "'   created")
    else:
        pass
        # message("path:   '" + path + "'   exists")
    return path


def defaultPath():
    user = os.path.expanduser('~')
    mainDir = user + '/maya/selectionSets/'
    return mainDir


def deletePath():
    if os.name == 'linux':
        user = os.path.expanduser('~')
        deleteDir = os.path.join(user, '.Trash\\')
        return deleteDir
    elif os.name == 'nt':
        user = os.getenv('USER')
        deleteDir = 'C:\\$Recycle.Bin'
        return deleteDir


def exportFile(filePath, sel=None):
    #
    createDefaultPath()
    #
    if os.path.isdir(filePath):
        message('Path construction looks wrong, check script editor.')
        print filePath
        return None
    else:
        # add extension if not present
        if '.sel' not in filePath:
            filePath = filePath + '.sel'
        # open
        outFile = open(filePath, 'wb')
        if sel:
            # confirm type
            if type(sel) != dict:
                sel = outputDict(sel)
            json.dump(sel, outFile, indent=4)
        else:
            json.dump({}, outFile, indent=4)
            message('Empty set saved', maya=True)
    outFile.close()
    message(" file:   '" + filePath + "'   saved")


def loadFile(filePath):
    readFile = open(filePath, 'r')
    dic = json.load(readFile)
    readFile.close()
    return dic


def outputDict(sel=[]):
    # make out put format, update ui
    dic = {}
    if sel:
        for s in sel:
            if ':' in s:
                val = s.split(':')[1]
            else:
                val = s
            dic[val] = s
    return dic


def selectSet(path=defaultPath()):
    # TODO: add explicit mode, select exactly saved objects
    plus = []
    selection = cmds.ls(sl=True, fl=True)
    files = os.listdir(str(path))
    msg = 'Sets selected:  '
    warn = 'Some objects could not be selected. No namespace provided by selection:  --  '
    foundSet = False
    ex = '  '
    if selection:
        for sel in selection:
            for file in files:
                # load dict
                objects = loadFile(os.path.join(path, file))
                # strip ns
                findObj = stripNs(sel)[1]
                # new ns
                ns = stripNs(sel)[0]
                if findObj in objects.keys():
                    foundSet = True
                    # build message
                    f = file.split('.sel')[0]
                    if f not in msg:
                        msg = msg + ' ' + f
                    # remove already selected from dict
                    del objects[findObj]
                    # iterate values in dict
                    for value in objects.values():
                        # if orig obj had ns, apply new ns
                        if ':' in value:
                            # current selection may not have ns, use original ns
                            if ns:
                                obj = ns + value.split(':')[1]
                            else:
                                # use original ns if new one is not supplied
                                obj = value
                        else:
                            obj = value
                        if obj not in selection:
                            if cmds.objExists(obj):
                                plus.append(obj)
                            else:
                                ex = ex + obj + '  --  '
        if plus:
            cmds.select(plus, add=True)
            message(msg, maya=True)
        else:
            if foundSet:
                message(warn + ex, maya=True, warning=True)
            else:
                message('No suitable objects found.', maya=True)
    else:
        message('Select an object', maya=True)


def stripNs(obj):
    if ':' in obj:
        i = obj.rfind(':')
        ref = obj[:i]
        base = obj[i + 1:]
        return ref + ':', base
    else:
        return '', obj
