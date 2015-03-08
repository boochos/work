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


def selectSet_old(path=defaultPath()):
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
                                ref = splitNs(key, colon=False)[0]
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
                            liveRefs = listLiveNs()
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


def getSetNsList(setList=[]):
    refs = []
    for obj in setList:
        if ':' in obj:
            ref = obj.split(':')[0]
            if ref not in refs:
                refs.append(ref)
    return len(refs)


def splitNs(obj, colon=True):
    if ':' in obj:
        i = obj.rfind(':')
        ref = obj[:i]
        base = obj[i + 1:]
        if colon:
            return ref + ':', base
        else:
            return ref, base
    else:
        return '', obj


def listLiveNs():
    ref = []
    all = cmds.ls()
    for item in all:
        if ':' in item:
            ns = item.split(':')[0]
            if ns not in ref:
                ref.append(ns)
    return ref


def listLiveContextualNs(setList=[]):
    allRefs = listLiveNs()
    liveRefs = []
    for obj in setList:
        if ':' in obj:
            obj = obj.split(':')[1]
            for ref in allRefs:
                if cmds.objExists(ref + ':' + obj):
                    if ref not in liveRefs:
                        liveRefs.append(ref)
    return liveRefs


def splitSetToAssets(setDict={}):
    '''
    compartmentalize dict into assets,
    split by namespaces and local objects
    '''
    # TODO: keys should contain 'ref', 'objs', use actual ns name for key unless object belongs to objs'
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
    if refs:
        for ref in refs:
            asset = []
            for key in setDict:
                if ref in key:
                    asset.append(key)
            assets.append(asset)
            assetDict[ref] = asset
            i = i + 1
    assets.append(objs)
    for asset in assets:
        pass
        # print 'ASSET:  ', asset
    return assetDict


def selectSet():
    remapped = findSet()
    if remapped:
        cmds.select(remapped, add=True)


def findSet():
    path = defaultPath()
    selection = cmds.ls(sl=True, fl=True)
    allFiles = os.listdir(str(defaultPath()))
    addSel = []
    #
    if selection:
        selection = stripPipe(selection)
        for sel in selection:
            # object name
            obj = splitNs(sel)[1]
            for f in allFiles:
                # load dict
                setDict = loadDict(os.path.join(path, f))
                #
                if obj in setDict.values():
                    # print f
                    # convert set to list of objects
                    converted = remapSet(sel, setDict)
                    for con in converted:
                        if con not in selection:
                            addSel.append(con)
    return addSel


def findNewRef(obj, liveRefs):
    '''
    obj = obj without ns
    liveRefs = edited as solutions are found
    '''
    remapped = None
    availabeleNs = []
    removeRef = []
    for ref in liveRefs:
        renamed = ref + ':' + obj
        if cmds.objExists(renamed):
            availabeleNs.append(ref)
            removeRef.append(ref)
        else:
            renamed = None
    if len(availabeleNs) == 1:
        remapped = availabeleNs[0] + ':' + obj
    else:
        obj = None
    return remapped


def remapSet(sel='', setDict={}):
    '''
    convert saved set to contextual form, try and replace missing namespaces
    '''
    # figure out which asset the selection is in
    remappedSet = []
    assets = splitSetToAssets(setDict)
    setNsList = getSetNsList(setDict.keys())  # int number of setNsList in set
    # obj asset
    objSet = ''
    for key in assets:
        if 'obj' in key:
            for obj in assets[key]:
                if cmds.objExists(obj):
                    remappedSet.append(obj)
            objSet = key
    del assets[objSet]

    # ref assets
    if setNsList == 1:
        # single ref
        for key in assets:
            if ':' in key:
                # try saved ns
                converted = remapExplicit(sel, assets[key])
                if converted:
                    for obj in converted:
                        if cmds.objExists(obj):
                            remappedSet.append(obj)
                else:
                    # replace ns
                    converted = remapSingleNs(sel, assets[key])
                    if converted:
                        for obj in converted:
                            if cmds.objExists(obj):
                                remappedSet.append(obj)
    elif setNsList > 1:
        # multi ref
        if ':' not in sel:
            sel = None
        converted = remapMultiNs(sel, assets)
        if converted:
            for obj in converted:
                if cmds.objExists(obj):
                    remappedSet.append(obj)
    return remappedSet


def remapExplicit(sel='', setList=[]):
    '''
    try using saved selection
    '''
    # print '\n  explicit  \n'
    remapped = []
    if sel in setList:
        for obj in setList:
            if cmds.objExists(obj):
                remapped.append(obj)
    return remapped


def remapSingleNs(sel='', setList=[]):
    # print '\n  single  \n'
    remapped = []
    obj = sel.split(':')[1]
    ns = sel.split(':')[0]
    # iterate keys in dict
    for member in setList:
        obj = ns + member.split(':')[1]
        if cmds.objExists(obj):
            remapped.append(obj)
    return remapped


def remapMultiNs(sel=None, assets={}):
    '''
    find new namespaces if saved ones dont apply
    '''
    #
    remappedExplicit = []
    remappedSolve = []
    setList = []
    #
    # convert assets to object list
    for key in assets:
        for member in assets[key]:
            setList.append(member)
    #
    # contextual ref list
    liveNsList = listLiveContextualNs(setList)
    #
    print 'explicit_______'
    print liveNsList
    print setList
    # explicit, entire set list
    if sel:
        remappedExplicit = remapExplicit(sel, setList)
    #
    # explicit per asset
    solved = []
    for asset in assets:
        converted = remapExplicit(assets[asset][0], assets[asset])
        if converted:
            solved.append(asset)
            for member in converted:
                remappedSolve.append(member)
            ns = assets[asset][0].split(':')[0]
            if ns in liveNsList:
                liveNsList.remove(ns)
    for asset in solved:
        for obj in assets[asset]:
            setList.remove(obj)
        del assets[asset]
    #
    print 'explicit per asset_______'
    print liveNsList
    print setList
    #
    # solve sel ns
    if sel:
        obj = findNewRef(sel, liveNsList)
        if obj:
            setList.remove(obj)
            remappedSolve.append(obj)
            ref = obj.split(':')[0]
            selRef = sel.split(':')[0]
            del assets[selRef]
            for member in setList:
                if selRef in member:
                    member = member.replace(selRef, ref)
                    setList.remove(member)
                    remappedSolve.append(member)
    #
    print 'sel ns_______'
    print liveNsList
    print setList
    #
    # cycle through asset members
    for asset in assets:
        for member in assets[asset]:
            # cycle through liveNsList
            obj = member.split(':')[1]
            obj = findNewRef(obj, liveNsList)
            print obj, '   *************'
            if obj:
                if member in setList:
                    setList.remove(member)
                    remappedSolve.append(obj)
    #
    # remove solved ns
    if remappedSolve:
        for member in remappedSolve:
            ref = member.split(':')[0]
            if ref in liveNsList:
                liveNsList.remove(ref)
    #
    print 'cycle assets_______'
    print liveNsList
    print setList
    #
    # check liveNsList
    if liveNsList:
        # check dupes
        setListNoNs = []
        solved = []
        for obj in setList:
            setListNoNs.append(obj.split(':')[1])
        for obj in setListNoNs:
            num = setListNoNs.count(obj)
            ns = []
            refs = []
            if num > 1:
                # check number of ns options
                for ref in liveNsList:
                    renamed = ref + ':' + obj
                    if cmds.objExists(renamed):
                        ns.append(renamed)
                        refs.append(ref)
            if len(ns) == num:
                # add to cyclic solve
                for item in ns:
                    remappedSolve.append(item)
            for ref in refs:
                solved.append(ref)
            dupeList = setList
            for member in dupeList:
                if obj in member:
                    if member in setList:
                        setList.remove(member)
        for ref in solved:
            if ref in liveNsList:
                liveNsList.remove(ref)
    #
    print 'check dupes_______'
    print liveNsList
    print setList
    #
    # compare results
    converted = None
    if len(remappedSolve) > len(remappedExplicit):
        converted = remappedSolve
    elif len(remappedExplicit) > len(remappedSolve):
        converted = remappedExplicit
        liveNsList = None
    else:
        converted = remappedExplicit
        liveNsList = None
    #
    if liveNsList:
        ns = ''
        for n in liveNsList:
            ns = ns + ' -- ' + n
        message('Objects were not resolved for these namespaces: ' + ns, warning=True)
    return converted
