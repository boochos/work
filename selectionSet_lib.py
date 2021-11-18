import json
import os

import maya.cmds as cmds
import maya.mel as mel

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
            print( what )


def createDefaultPath():
    # main path
    path = defaultPath()
    if not os.path.isdir( path ):
        os.mkdir( path )
        message( "path:   '" + path + "'   created" )
    else:
        pass
        # message("path:   '" + path + "'   exists")
    return path


def defaultPath():
    # user = os.path.expanduser('~')
    # mainDir = user + '/maya/selectionSets/'
    # proper directory query
    varPath = cmds.internalVar( userAppDir = True )
    mainDir = os.path.join( varPath, 'selectionSets' )
    return mainDir


def deletePath():
    if os.name == 'linux':
        user = os.path.expanduser( '~' )
        deleteDir = os.path.join( user, '.Trash\\' )
        return deleteDir
    elif os.name == 'nt':
        user = os.getenv( 'USER' )
        deleteDir = 'C:\\$Recycle.Bin'
        return deleteDir


def exportFile( filePath, sel = None ):
    #
    createDefaultPath()
    #
    if os.path.isdir( filePath ):
        message( 'Path construction looks wrong, check script editor.' )
        print( filePath )
        return None
    else:
        # add extension if not present
        if '.sel' not in filePath:
            filePath = filePath + '.sel'
        # open
        outFile = open( filePath, 'wt' )
        if sel:
            # confirm type
            if type( sel ) != dict:
                sel = outputDict( sel )
            json.dump( sel, outFile, indent = 4 )
        else:
            json.dump( {}, outFile, indent = 4 )
            message( 'Empty set saved', maya = True )
    outFile.close()
    message( " file:   '" + filePath + "'   saved" )


def loadDict( filePath ):
    # print( filePath )
    # readFile = open( filePath, 'r' )
    # print( readFile )
    try:
        readFile = open( filePath, 'r' )
        dic = json.load( readFile )
        readFile.close()
        return dic
    except:
        return None


def outputDict( sel = [] ):
    dic = {}
    if sel:
        for s in sel:
            if ':' in s:
                val = s.split( ':' )[1]
            else:
                val = s
            dic[s] = val
    # print dic
    return dic


def stripPipe( selList = [] ):
    selection = []
    if selList:
        for sel in selList:
            # strip full path to object, if exists
            if '|' in sel:
                sel = sel.split( '|' )
                selection.append( sel[len( sel ) - 1] )
            else:
                selection.append( sel )
    return selection


def getSetNsList( setList = [] ):
    refs = []
    for obj in setList:
        if ':' in obj:
            ref = obj.split( ':' )[0]
            if ref not in refs:
                refs.append( ref )
    return len( refs )


def splitNs( obj, colon = True ):
    '''
    may need a version of this in the future for nested references
    '''
    if ':' in obj:
        i = obj.rfind( ':' )
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
            ns = item.split( ':' )[0]
            if ns not in ref:
                ref.append( ns )
    return ref


def listLiveContextualNs( setList = [] ):
    allRefs = listLiveNs()
    liveRefs = []
    for obj in setList:
        if ':' in obj:
            obj = obj.split( ':' )[1]
            for ref in allRefs:
                if cmds.objExists( ref + ':' + obj ):
                    if ref not in liveRefs:
                        liveRefs.append( ref )
    return liveRefs


def splitSetToAssets( setDict = {} ):
    '''
    compartmentalize dict into assets,
    split by namespaces and local objects
    '''
    refs = []
    assets = []
    objs = []
    assetDict = {}
    for key in setDict:
        if ':' in key:
            ns = key.split( ':' )[0]
            if ns not in refs:
                refs.append( ns )
        else:
            objs.append( key )
    if objs:
        assetDict['obj'] = objs
    i = 1
    if refs:
        for ref in refs:
            asset = []
            for key in setDict:
                if ref in key:
                    asset.append( key )
            assets.append( asset )
            assetDict[ref] = asset
            i = i + 1
    assets.append( objs )
    for asset in assets:
        pass
        # print 'ASSET:  ', asset
    return assetDict


def selectSet():
    remapped = findSet()
    if remapped:
        cmds.select( remapped, add = True )


def findSet():
    path = defaultPath()
    selection = cmds.ls( sl = True, fl = True )
    allFiles = os.listdir( str( defaultPath() ) )
    addSel = []
    #
    if selection:
        selection = stripPipe( selection )
        for sel in selection:
            # object name
            obj = splitNs( sel )[1]
            for f in allFiles:
                # load dict
                setDict = loadDict( os.path.join( path, f ) )
                #
                if setDict:
                    if obj in setDict.values():
                        # print f
                        # convert set to list of objects
                        remapped = remapSet( sel, setDict )
                        # print remapped
                        for con in remapped:
                            if con not in selection:
                                addSel.append( con )
    return addSel


def findNewNs( obj, liveNs ):
    '''
    obj = obj without ns
    liveNs = edited as solutions are found
    '''
    remapped = None
    availabeleNs = []
    for ref in liveNs:
        renamed = ref + ':' + obj
        if cmds.objExists( renamed ):
            availabeleNs.append( ref )
        else:
            renamed = None
    if len( availabeleNs ) == 1:
        remapped = availabeleNs[0] + ':' + obj
    else:
        obj = None
    return remapped


def remapSet( sel = '', setDict = {} ):
    '''
    convert saved set to contextual form, try and replace missing namespaces
    '''
    # figure out which asset the selection is in
    remappedSet = []
    assets = splitSetToAssets( setDict )
    setNsList = getSetNsList( setDict.keys() )  # int number of setNsList in set
    # obj asset
    objSet = ''
    for asset in assets:
        if 'obj' in asset:
            for obj in assets[asset]:
                if cmds.objExists( obj ):
                    remappedSet.append( obj )
            objSet = asset
    if objSet:
        del assets[objSet]
    # ref assets
    if setNsList == 1:
        # single ref
        for asset in assets:
            # try saved ns
            converted = remapExplicit( sel, assets[asset] )
            if converted:
                for obj in converted:
                    if cmds.objExists( obj ):
                        remappedSet.append( obj )
            else:
                # replace ns
                converted = remapSingleNs( sel, assets[asset] )
                # print converted
                if converted:
                    for obj in converted:
                        if cmds.objExists( obj ):
                            remappedSet.append( obj )
    elif setNsList > 1:
        # multi ref
        if ':' not in sel:
            sel = None
        converted = remapMultiNs( sel, assets )
        if converted:
            for obj in converted:
                if cmds.objExists( obj ):
                    remappedSet.append( obj )
    return remappedSet


def remapExplicit( sel = '', setList = [] ):
    '''
    try using saved selection
    '''
    # print '\n  explicit  \n'
    remapped = []
    if sel:
        if sel in setList:
            for obj in setList:
                if cmds.objExists( obj ):
                    remapped.append( obj )
    return remapped


def remapSingleNs( sel = '', setList = [] ):
    # print '\n  single  \n'
    remapped = []
    if sel:
        obj = sel.split( ':' )[1]
        ns = sel.split( ':' )[0]
        # iterate keys in dict
        for member in setList:
            obj = ns + ':' + member.split( ':' )[1]
            if cmds.objExists( obj ):
                remapped.append( obj )
    return remapped


def remapMultiNs( sel = None, assets = {} ):
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
            setList.append( member )
    #
    # contextual ref list
    liveNsList = listLiveContextualNs( setList )
    #
    # explicit, entire set list
    if sel:
        remappedExplicit = remapExplicit( sel, setList )
    #
    # explicit per asset
    solvedAssets = []
    if assets:
        for asset in assets:
            converted = remapExplicit( assets[asset][0], assets[asset] )
            if converted:
                solvedAssets.append( asset )
                for member in converted:
                    remappedSolve.append( member )
                ns = assets[asset][0].split( ':' )[0]
                if ns in liveNsList:
                    liveNsList.remove( ns )
        for asset in solvedAssets:
            for obj in assets[asset]:
                setList.remove( obj )
            del assets[asset]
    #
    # solve sel ns
    if sel:
        selObj = sel.split( ':' )[1]
        selRef = sel.split( ':' )[0]
        obj = findNewNs( selObj, liveNsList )
        if obj:
            liveNsList.remove( selRef )
            remappedSolve.append( obj )
            #
            for member in setList:
                if selObj in member:
                    asset = member.split( ':' )[0]
                    setList.remove( member )
                    remappedSolve.append( member )
            del assets[asset]
    #
    # cycle through asset members
    solvedAssets = []
    for asset in assets:
        if asset not in 'obj':
            for member in assets[asset]:
                # cycle through liveNsList
                # print member
                obj = member.split( ':' )[1]
                obj = findNewNs( obj, liveNsList )
                if obj:
                    if member in setList:
                        setList.remove( member )
                        remappedSolve.append( obj )
                    if asset not in solvedAssets:
                        solvedAssets.append( asset )
        else:
            # add to selection if exists
            pass
    if solvedAssets:
        for asset in solvedAssets:
            del assets[asset]
    #
    # remove solved ns from previous section
    if remappedSolve:
        for member in remappedSolve:
            ref = member.split( ':' )[0]
            if ref in liveNsList:
                liveNsList.remove( ref )
    #
    # check liveNsList
    if liveNsList:
        # check dupes
        setListNoNs = []
        solved = []
        for obj in setList:
            setListNoNs.append( obj.split( ':' )[1] )
        for obj in setListNoNs:
            num = setListNoNs.count( obj )
            ns = []
            refs = []
            if num > 1:
                # check number of ns options
                for ref in liveNsList:
                    renamed = ref + ':' + obj
                    if cmds.objExists( renamed ):
                        ns.append( renamed )
                        refs.append( ref )
            if len( ns ) == num:
                # add to cyclic solve
                for item in ns:
                    remappedSolve.append( item )
            for ref in refs:
                solved.append( ref )
            dupeList = setList
            for member in dupeList:
                if obj in member:
                    if member in setList:
                        setList.remove( member )
        for ref in solved:
            if ref in liveNsList:
                liveNsList.remove( ref )
    #
    # compare results
    converted = None
    if len( remappedSolve ) > len( remappedExplicit ):
        converted = remappedSolve
    elif len( remappedExplicit ) > len( remappedSolve ):
        converted = remappedExplicit
        liveNsList = None
    else:
        converted = remappedExplicit
        liveNsList = None
    #
    # Done
    if assets:
        ns = ''
        for n in assets:
            ns = ns + ' -- ' + n
        # BUG: fix for scarecrow, mid fingers, shouldve worked, only one ref with available objects
        message( 'WRONG MESSAGE -- Objects were not remapped for these namespaces: ' + ns, warning = True )
    return converted
