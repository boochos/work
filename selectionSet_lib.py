import os
import shutil
import maya.cmds as cmds
import maya.mel as mel

tell = ''

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
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
    '''
    #pose sub path
    pose = defaultPosePath()
    if not os.path.isdir(pose):
        os.mkdir(pose)
        message( "path:   '" + pose + "'   created")
    else:
        pass
        #message("path:   '" + pose + "'   exists")
    #key sub path
    key  = defaultKeyPath()
    if not os.path.isdir(key):
        os.mkdir(key)
        message( "path:   '" + key + "'   created")
    else:
        pass
        #message("path:   '" + key + "'   exists")
    '''
    return path

def defaultPath():
    user = os.path.expanduser('~')
    mainDir = user + '/maya/selectionSets/'
    return mainDir
'''
def defaultPosePath():
    mainDir = defaultPath()
    poseDir = mainDir + 'selectionPoseSets'
    return poseDir
    
def defaultKeyPath():
    mainDir = defaultPath()
    keyDir = mainDir + 'selectionKeySets'
    return keyDir
'''
def loadFile(path):
    loaded = []
    for line in open(path):
        # load the file, look for reference naming in the file
        # add to a dictionary
        loaded.append(line.strip('\n'))
    return loaded

def printLines(path=''):
    loaded = loadFile(path)
    for line in loaded:
        print line

def deletePath():
    if os.name == 'linux':
        user = os.path.expanduser('~')
        deleteDir = os.path.join(user, '.Trash\\')
        return deleteDir
    elif os.name == 'nt':
        user = os.getenv('USER')
        deleteDir = 'C:\\$Recycle.Bin'
        return deleteDir

def deleteFlushed():
    path = shotPath()
    delPath = deletePath()
    # this 'if' prevents deletion of files from main(default) character set directory
    if path != defaultPath():
        chars = os.listdir(path)
        for set in chars:
            file = os.path.join(path, set)
            # shutil.copy2(file, delPath) doesnt work on windows
            os.remove(file)
    else:
        message('Name your scene before proceeding')

def nameSpace(ns=''):
    return ns.split(':')[0]

def exportFile(filePath, sel=None):
    # Exports the given character set to a file.
    # test the path for type, want a full file path
    import os
    if not sel:
        sel = cmds.ls(sl=True, fl=True)
    if len(sel) > 0:
        if os.path.isdir(filePath) == True:
            message('No file name specified.')
        else:
            # add extension if not present
            if '.sel' not in filePath:
                filePath = filePath + '.sel'
            # create file, write, close
            outFile = open(filePath, 'w')
            writeFile(sel, outFile=outFile)
            outFile.close()
            # print ''
            message(" file:   '" + filePath + "'   saved")
    else:
        message('Select an object', maya=True)

def writeFile(sel=None, outFile=''):
    # Arguments   :<char>   : attribute of a character set
    #            :<parent> : character nodes parent
    #            :<outFile>: filepath of the output file
    # Description :Recursive function that seperates characters nodes children and
    #             attributes and writes them to the specified file.
    #
    # list all attributes of the character)
    # sel = cmds.ls(sl=True)
    createDefaultPath()
    if sel:
        # write out the parent line
        for s in sel:
            if ':' in s:
                s = stripNs(s)[1]
                # s = s.split(':')[1]
            # if attr
            outFile.write(s + '\n')
    else:
        # empty character set, write info
        pass
        # outFile.write( 'ParentInfo=' + parent + '|' + char + '\n')

def selectSet(path=defaultPath()):
    plus = []
    selection = cmds.ls(sl=True, fl=True)
    # path = defaultPath()
    files = os.listdir(str(path))
    msg = 'Sets selected:  '
    if len(selection) > 0:
        for sel in selection:
            for file in files:
                objects = getObjects(os.path.join(path, file))
                stripped = stripNs(sel)[1]
                ns = stripNs(sel)[0]
                if stripped in objects:
                    fl = file.split('.sel')[0]
                    if fl not in msg:
                        msg = msg + ' ' + fl
                    objects.remove(stripped)
                    for obj in objects:
                        obj = ns + obj
                        if obj not in selection:
                            plus.append(obj)
        if len(plus) > 0:
            cmds.select(plus, add=True)
            message(msg, maya=True)
        else:
            message('No set found', maya=True)
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

def getObjects(filePath):
    result = []
    objects = open(filePath).readlines()
    for obj in objects:
        result.append(obj.strip('\n'))
    return result

def updateNS(old='', new=''):
    '''
    takes full attr path namespace and all.
    replaces namespace found in 'old' with namespace found in 'new'
    '''
    if new != '':
        return old.replace(nameSpace(old), nameSpace(new))
    else:
        return old

def updateCS(string, old='', new=''):
    '''
    takes old string replaces with new from given string
    '''
    if type(string) == tuple:
        return updateCSlist(string, old, new)
    else:
        if new != 'new':
            return string.replace(old, new)
        else:
            return string

def updateCSlist(lst, old='', new=''):
    newLst = []
    for string in lst:
        newLst.append(updateCS(string, old, new))
    return newLst

def replaceInString(string, dic):
    '''
    string = 'string'
    dic    = dictionary
    '''
    for key in dic.keys():
        string = string.replace(key, dic[key])
    return string

def importFile(path='', prefix='', ns='', cs=['old', 'new'], rp={None:None}):
    '''
    prefix = adds prefix string with underscore after
    ns     = namespace string to replace
    cs     = character set string to replace, is obsolete with "rp" attribute
    rplc   = per line in file replace string, could change to dictionary for clarity
    '''
    if os.path.isfile(path) == True:
        if prefix != '':
            prefix = prefix + '_'
        addNode = ''
        for line in open(path).readlines():
            if rp.keys() != [None]:
                line = replaceInString(line, rp)
            # character and sub-character set line
            if line.find('ParentInfo=') > -1:
                # print line, '--'
                line = line.split('=')[1].strip('\n').partition('|')
                # line = updateCS(string=line, old=cs[0], new=cs[1])
                if line[0] == 'none':
                    # top character
                    charName = prefix + line[2]
                    charName = cmds.character(name=charName, em=True)
                    addNode = charName
                else:
                    # sub-character set
                    charName = prefix + line[2]
                    charTmp = cmds.character(name=charName, em=True)
                    # automatic rename of duplicate, splitting extra string
                    dup = charTmp.split(charName)[1]
                    charName = charTmp
                    cmds.character(charName, fe=prefix + line[0] + dup)
                    addNode = charName
            # character set members line
            else:
                if ':' in line:
                    line = updateNS(line, ns)
                try:
                    cmds.character(line.strip('\n'), fe=addNode)
                except:
                    loadWarning = 'no attribute found, %s, skipping...' % (line.strip('\n'))
                    mel.eval("warning\"" + loadWarning + "\";")
                else:
                    cmds.character(line.strip('\n'), fe=addNode)
    else:
        message('Path not found: ' + path)
