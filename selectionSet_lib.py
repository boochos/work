import os
import maya.cmds as cmds
import maya.mel as mel
import json

tell = ''


'''
# absorb old file format
ss = web.mod('selectionSet_lib')
path = '/home/sebastianw/maya/selectionSets'
files = os.listdir(path)
for f in files:
    objL = []
    p = os.path.join(path, f)
    read = open(p, 'r')
    lines = read.readlines()
    for line in lines:
        if '{' not in line:
            objL.append('Ref:' + line.strip('\n'))
        else:
            break
    print ss.outputDict(objL)
    ss.exportFile(filePath=p, sel=objL)
    read.close()
'''


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


def loadDict(filePath):
    readFile = open(filePath, 'r')
    dic = json.load(readFile)
    readFile.close()
    return dic


def outputDict(sel=[]):
    dic = {}
    if sel:
        for s in sel:
            if ':' in s:
                val = s.split(':')[1]
            else:
                val = s
            dic[s] = val
    # print dic
    return dic


def selectSet(path=defaultPath()):
    # needs overhaul, split up function so it can be fed a specific select set
    #
    # split set into assets partitions (refed, unrefed)
    #
    selection = cmds.ls(sl=True, fl=True)
    selection = stripPipe(selection)
    files = os.listdir(str(path))
    foundSet = False
    selectionAdd = []
    #
    msg = 'Sets selected:  '
    warn = 'Some objects could not be selected. No namespace provided by selection:  --  '
    ex = '  '
    #
    if selection:
        for sel in selection:
            # loop files
            for file in files:
                # load dict
                setDict = loadDict(os.path.join(path, file))
                # selected object
                findObj = splitNs(sel)[1]
                # selected ns
                ns = splitNs(sel)[0]
                #
                if findObj in setDict.values():
                    foundSet = True
                    #
                    # build message for selected sets print
                    f = file.split('.sel')[0]
                    if f not in msg:
                        msg = msg + ' -- ' + f
                    #
                    # qualify route, explicit or dynamic ns
                    explicit = False
                    if sel in setDict.keys():  # explicit
                        # check if sel has ns, if not check if rest of set has ns members, if yes, check existance
                        explicitMembers = []
                        if ':' in sel:  # list should be appropriate
                            for key in setDict.keys():
                                if cmds.objExists(key):
                                    selectionAdd.append(key)
                                    explicitMembers.append(key)
                            if len(explicitMembers) == len(setDict.keys()):
                                message('explicit attempt -- success')
                            else:
                                message('explicit attempt -- missing objects')
                        else:  # list needs further investigation
                            ref = False
                            for key in setDict.keys():
                                if ':' in key and cmds.objExists(key):
                                    # likelyhood of set being correct is high
                                    explicit = True
                                    ref = True  # dont go in next if query
                                    break
                            if not ref:
                                # no ref exists, list should be good as is
                                for key in setDict.keys():
                                    if cmds.objExists(key):
                                        selectionAdd.append(key)
                                        explicitMembers.append(key)
                                if len(explicitMembers) == len(setDict.keys()):
                                    message('explicit attempt -- success')
                                else:
                                    message('explicit attempt -- missing objects')
                            if explicit:
                                for key in setDict.keys():
                                    if cmds.objExists(key):
                                        selectionAdd.append(key)
                                        explicitMembers.append(key)
                                if len(explicitMembers) == len(setDict.keys()):
                                    message('explicit attempt -- success')
                                else:
                                    message('explicit attempt -- missing objects')
                    if not explicit:  # dynamic
                        print '\n  dynamic  \n'
                        # qualify for single vs multi ns in set
                        refs = []
                        for key in setDict.keys():
                            if ':' in key:
                                ref = splitNs(key)[0]
                                if ref not in refs:
                                    refs.append(ref)
                        if len(refs) == 1:  # single ns in set
                            print '\n  single  \n'
                            # iterate keys in dict
                            for key in setDict.keys():
                                # print key, '______key'
                                # if orig obj had ns, apply new ns
                                if ':' in key:
                                    # current selection may not have ns, use original ns
                                    if ns:
                                        print 'here'
                                        obj = ns + key.split(':')[1]
                                    else:
                                        print 'there'
                                        # use original ns if new one is not supplied
                                        obj = key
                                else:
                                    obj = key
                                if obj not in selection:
                                    print obj, ' not in sel'
                                    if cmds.objExists(obj):
                                        selectionAdd.append(obj)
                                    else:
                                        ex = ex + obj + '  --  '
                        else:  # multi ns in set
                            print '\n  multi  \n'
                            # TODO: attempt to find objects in existing namespaces, if more than one solution is found SELECT NOTHING
                            liveRefs = listNs()
                            numOfMembers = len(setDict.keys())
                            renamedMembers = []
                            renamed = None
                            for key in setDict.keys():
                                if ':' in key:
                                    obj = setDict[key]
                                    availabeleNs = []
                                    for ref in liveRefs:
                                        renamed = ref + ':' + obj
                                        if cmds.objExists(renamed):
                                            availabeleNs.append(ref)
                                        else:
                                            renamed = None
                                    if len(availabeleNs) == 1:
                                        # print availabeleNs
                                        renamedMembers.append(availabeleNs[0] + ':' + obj)
                                else:
                                    if cmds.objExists(key):
                                        renamedMembers.append(key)
                            if renamedMembers:
                                for item in renamedMembers:
                                    selectionAdd.append(item)
                                if len(renamedMembers) == numOfMembers:
                                    message('dynamic attempt -- success')
                                else:
                                    message('dynamic attempt -- missing objects')

        if selectionAdd:
            # TODO: add selectionAdd - selection operation, result is objects that should be added to selection
            cmds.select(selectionAdd, add=True)
            message(msg, maya=True)
        else:
            if foundSet:
                pass
                # message(warn + ex, maya=True, warning=True)
            else:
                message('No suitable objects found.', maya=True)
    else:
        message('Select an object', maya=True)


def stripPipe(selList=[]):
    selection = []
    if selList:
        for sel in selList:
            # strip full path to object, if exists
            if '|' in sel:
                sel = sel.split('|')
                selection.append(sel[len(sel) - 1])
            else:
                selection.append(sel)
    return selection


def getNs(sel=''):
    if ':' in sel:
        return sel.split(':')[0]
    else:
        return ''


def splitNs(obj):
    if ':' in obj:
        i = obj.rfind(':')
        ref = obj[:i]
        base = obj[i + 1:]
        return ref + ':', base
    else:
        return '', obj


def listNs():
    ref = []
    all = cmds.ls()
    for item in all:
        if ':' in item:
            ns = item.split(':')[0]
            if ns not in ref:
                ref.append(ns)
    return ref


def splitSetToAssets(setDict={}):
    '''
    compartmentalize dict into assets,
    split by namespaces and local objects
    '''
    # keys should contain 'ref', 'objs'
    refs = []
    assets = []
    objs = []
    assetDict = {}
    for key in setDict:
        if ':' in key:
            ns = key.split(':')[0]
            if ns not in refs:
                refs.append(ns)
        else:
            objs.append(key)
    assetDict['obj'] = objs
    i = 1
    for ref in refs:
        asset = []
        for key in setDict:
            if ref in key:
                asset.append(key)
        assets.append(asset)
        assetDict['ref' + str(i)] = asset
        i = i + 1
    assets.append(objs)
    for asset in assets:
        print 'ASSET:  ', asset
    return assetDict


def convertSet(sel='', setDict={}):
    '''
    convert saved set to contextual form, try and replace missing namespaces
    '''
    convertedSet = []
    assets = splitSetToAssets(setDict)
    for key in assets:
        if 'ref' in key:
            # try explicit method
            converted = convertExplicit(sel, setDict[key])
            if converted:
                for obj in converted:
                    if cmds.objExists(obj):
                        convertedSet.append(obj)
            else:
                # single ns replacement
                converted = convertSingleNs(sel, setDict[key])
                if converted:
                    for obj in converted:
                        if cmds.objExists(obj):
                            convertedSet.append(obj)
                else:
                    converted = convertMultiNs(sel, setDict[key])
                    if converted:
                        for obj in converted:
                            if cmds.objExists(obj):
                                convertedSet.append(obj)
                    else:
                        pass
                        # converted = convertByComparing(sel, setDict[key])
                        # compare if a namespace has been found previously in loop and removing it as a possibility
                        # if 4 refs were in set with same object, 4 refs are available in scene, must be correct
        else:
            for obj in setDict[key]:
                if cmds.objExists(obj):
                    convertedSet.append(obj)


def convertExplicit(sel='', setList=[]):
    '''
    try explicit selection
    '''
    converted = []
    for obj in setList:
        if cmds.objExists(obj):
            converted.append(obj)
    return converted


def convertNonExplicit(sel='', setDict=[]):
    # qualify for single vs multi ns in set
    refs = []
    for key in setDict.keys():
        if ':' in key:
            ref = splitNs(key)[0]
            if ref not in refs:
                refs.append(ref)
    if len(refs) == 1:  # single ns in set
        print '\n  single  \n'
        # iterate keys in dict
        for key in setDict.keys():
            # print key, '______key'
            # if orig obj had ns, apply new ns
            if ':' in key:
                # current selection may not have ns, use original ns
                if ns:
                    print 'here'
                    obj = ns + key.split(':')[1]
                else:
                    print 'there'
                    # use original ns if new one is not supplied
                    obj = key
            else:
                obj = key
            if obj not in selection:
                print obj, ' not in sel'
                if cmds.objExists(obj):
                    selectionAdd.append(obj)
                else:
                    ex = ex + obj + '  --  '
    else:  # multi ns in set
        print '\n  multi  \n'
        # TODO: attempt to find objects in existing namespaces, if more than one solution is found SELECT NOTHING
        liveRefs = listNs()
        numOfMembers = len(setDict.keys())
        renamedMembers = []
        renamed = None
        for key in setDict.keys():
            if ':' in key:
                obj = setDict[key]
                availabeleNs = []
                for ref in liveRefs:
                    renamed = ref + ':' + obj
                    if cmds.objExists(renamed):
                        availabeleNs.append(ref)
                    else:
                        renamed = None
                if len(availabeleNs) == 1:
                    # print availabeleNs
                    renamedMembers.append(availabeleNs[0] + ':' + obj)
            else:
                if cmds.objExists(key):
                    renamedMembers.append(key)
        if renamedMembers:
            for item in renamedMembers:
                selectionAdd.append(item)
            if len(renamedMembers) == numOfMembers:
                message('dynamic attempt -- success')
            else:
                message('dynamic attempt -- missing objects')


def convertSingleNs(sel='', setList=[]):
    # for given asset try finding one solution
    # qualify for single vs multi ns in set
    refs = []
    selectionAdd = []
    for key in setDict.keys():
        if ':' in key:
            ref = splitNs(key)[0]
            if ref not in refs:
                refs.append(ref)
    if len(refs) == 1:  # single ns in set
        print '\n  single  \n'
        # iterate keys in dict
        for key in setDict.keys():
            # print key, '______key'
            # if orig obj had ns, apply new ns
            if ':' in key:
                # current selection may not have ns, use original ns
                if ns:
                    print 'here'
                    obj = ns + key.split(':')[1]
                else:
                    print 'there'
                    # use original ns if new one is not supplied
                    obj = key
            else:
                obj = key
            if obj not in selection:
                print obj, ' not in sel'
                if cmds.objExists(obj):
                    selectionAdd.append(obj)
                else:
                    ex = ex + obj + '  --  '


def convertMultiNs():
    print '\n  multi  \n'
    # TODO: attempt to find objects in existing namespaces, if more than one solution is found SELECT NOTHING
    liveRefs = listNs()
    numOfMembers = len(setDict.keys())
    renamedMembers = []
    renamed = None
    for key in setDict.keys():
        if ':' in key:
            obj = setDict[key]
            availabeleNs = []
            for ref in liveRefs:
                renamed = ref + ':' + obj
                if cmds.objExists(renamed):
                    availabeleNs.append(ref)
                else:
                    renamed = None
            if len(availabeleNs) == 1:
                # print availabeleNs
                renamedMembers.append(availabeleNs[0] + ':' + obj)
        else:
            if cmds.objExists(key):
                renamedMembers.append(key)
    if renamedMembers:
        for item in renamedMembers:
            selectionAdd.append(item)
        if len(renamedMembers) == numOfMembers:
            message('dynamic attempt -- success')
        else:
            message('dynamic attempt -- missing objects')


def convertByComparing():
    '''
    when too many solutions are found try converting by eliminating namespaces already used
    '''
    pass
