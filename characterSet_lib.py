import os
import maya.cmds as cmds
import maya.mel as mel
#
# import animCurve_lib as ac
import webrImport as web
# web
ac = web.mod( 'animCurve_lib' )

# var for UI
tell = ''


def message( what = '', maya = False ):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def sceneName():
    sceneName = cmds.file( q = True, sn = True )
    try:
        sceneName = sceneName.split( '.ma' )[0]
    except:
        sceneName = sceneName.split( '.mb' )[0]
    else:
        pass
    slash = sceneName.rfind( '/' )
    sceneName = sceneName[slash + 1:]
    return sceneName


def shotPath():
    shotDir = sceneName()
    # print shotDir, '___________________________'
    if sceneName() != '':
        shotDir = shotDir[0:shotDir.rfind( '_' )] + '/'
        print( shotDir )
    createDefaultPath()
    # path = defaultPath() + shotDir
    path = os.path.join( defaultPath(), shotDir )
    if not os.path.isdir( path ):
        os.mkdir( path )
        message( "path:   '" + path + "'   created" )
    else:
        pass
        # message("path:   '" + path + "'   exists")
    return path


def createDefaultPath():
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
    # mainDir = user + '/maya/characterSets/'
    # proper directory query
    varPath = cmds.internalVar( userAppDir = True )
    mainDir = os.path.join( varPath, 'characterSets' )
    return mainDir


def loadFile( path ):
    loaded = []
    for line in open( path ):
        # load the file, look for reference naming in the file
        # add to a dictionary
        loaded.append( line.strip( '\n' ) )
    return loaded


def printLines( path = '' ):
    loaded = loadFile( path )
    for line in loaded:
        print( line )


def listAll():
    return cmds.ls( type = 'character' )


def listTop():
    top = []
    all = listAll()
    if all:
        for chr in all:
            # print( chr )
            cnnct = cmds.listConnections( chr + '.message', d = True, s = False )
            # qualify
            tabInfo = 'MayaNodeEditorSavedTabsInfo'
            if cnnct:
                if tabInfo in cnnct:
                    cnnct.remove( tabInfo )
            #
            if cnnct:
                # case 1, partition node connection
                for node in cnnct:
                    if cmds.objExists( node ):
                        # connections are returned that are not objects
                        if cmds.nodeType( node ) == 'partition':
                            top.append( chr )
                            print( 'case1, no:', chr )
                            break
                # case 2, 'set' node connection
                if len( cnnct ) == 1:
                    if 'set' in cnnct[0]:
                        top.append( chr )
                    else:
                        print( 'case2, no:', chr )
                        print( cnnct )
            # case 1, no connection
            else:
                top.append( chr )
        return top
    else:
        message( 'No character sets exist' )
        return []


def deleteAll():
    chrs = listAll()
    for chr in chrs:
        # subcharacter sets raise error if top set is deleted, need exception
        try:
            cmds.delete( chr )
        except:
            pass


def parentSet():
    # forces first selection to be a member of second selection
    cmds.character( cmds.ls( sl = True )[0], fe = cmds.ls( sl = True )[1] )


def flush():
    all = listTop()
    # print 'top list'
    if all:
        deleteFlushed()
        # print 'deleted'
        tmp = []
        for char in all:
            if cmds.reference( char, inr = True ) is False:
                tmp.append( char )
        all = tmp
        if len( all ) > 0:
            path = shotPath()
            for set in all:
                exportFile( set, os.path.join( path , set ) )
                print( "-- flushed:   '" + set + "'  --" )
            deleteAll()
        else:
            pass
    else:
        message( 'No Character Sets in Scene' )


def unflush():
    path = shotPath()
    if path != defaultPath():
        chars = os.listdir( path )
        for set in chars:
            # importFile( path + set )
            importFile( os.path.join( path, set ) )
            print( "-- unflushed:   '" + set + "'  --" )
    else:
        message( 'Open a scene before proceeding' )


def deletePath():
    if os.name == 'linux':
        user = os.path.expanduser( '~' )
        deleteDir = os.path.join( user, '.Trash\\' )
        return deleteDir
    elif os.name == 'nt':
        user = os.getenv( 'USER' )
        deleteDir = 'C:\\$Recycle.Bin'
        return deleteDir


def deleteFlushed():
    path = shotPath()
    # this 'if' prevents deletion of files from main(default) character set
    # directory
    if path != defaultPath():
        chars = os.listdir( path )
        for set in chars:
            file = os.path.join( path, set )
            # shutil.copy2(file, delPath) doesnt work on windows
            if os.path.isfile( file ):
                os.remove( file )
    else:
        message( 'Name your scene before proceeding' )


def writeFile( char, parent, outFile = '' ):
    # Arguments   :<char>   : attribute of a character set
    #            :<parent> : character nodes parent
    #            :<outFile>: filepath of the output file
    # Description :Recursive function that seperates characters nodes children and
    #             attributes and writes them to the specified file.
    #
    # list all attributes of the character)
    characterMembers = cmds.character( char, query = True )
    if characterMembers is not None:
        # write out the parent line
        outFile.write( 'ParentInfo=' + parent + '|' + char + '\n' )
        parent = char
        charList = []
        # check members list for attrs or sub-characters
        for cMember in characterMembers:
            # if attr
            if cmds.nodeType( cMember ) != 'character':
                outFile.write( cMember + '\n' )
            # must be sub-character set, add to list
            else:
                charList.append( cMember )
        for char in charList:
            writeFile( char, parent, outFile )
    else:
        # empty character set, write info
        outFile.write( 'ParentInfo=' + parent + '|' + char + '\n' )


def exportFile( selChar, filePath ):
    # Exports the given character set to a file.
    # test the path for type, want a full file path
    import os
    if cmds.nodeType( selChar ) == 'character':
        if os.path.isdir( filePath ):
            message( 'No file name specified.' )
        else:
            # add extension if not present
            if '.chr' not in filePath:
                filePath = filePath + '.chr'
            # create file, write, close
            outFile = open( filePath, 'w' )
            writeFile( selChar, 'none', outFile = outFile )
            outFile.close()
            # print ''
            message( "file:   '" + filePath + "'   saved" )
    else:
        message( 'Object  ::' + selChar + '::  is not a characterSet.' )


def nameSpace( ns = '', base = False ):
    if ':' in ns:
        i = ns.rfind( ':' )
        ref = ns[:i]
        obj = ns[i + 1:]
        if base is False:
            return ref
        else:
            return ref, obj
    else:
        return ns


def updateNS( old = '', new = '' ):
    '''
    takes full attr path namespace and all.
    replaces namespace found in 'old' with namespace found in 'new'
    '''
    if new != '':
        return old.replace( nameSpace( old ), nameSpace( new ) )
    else:
        return old


def updateCS( string, old = '', new = '' ):
    '''
    takes old string replaces with new from given string
    '''
    if type( string ) == tuple:
        return updateCSlist( string, old, new )
    else:
        if new != 'new':
            return string.replace( old, new )
        else:
            return string


def updateCSlist( lst, old = '', new = '' ):
    newLst = []
    for string in lst:
        newLst.append( updateCS( string, old, new ) )
    return newLst


def replaceInString( string, dic ):
    '''
    string = 'string'
    dic    = dictionary
    '''
    for key in dic.keys():
        string = string.replace( key, dic[key] )
    return string


def importFile( path = '', prefix = '', ns = '', cs = ['old', 'new'], rp = {None: None} ):
    '''
    prefix = adds prefix string with underscore after
    ns     = namespace string to replace
    cs     = character set string to replace, is obsolete with "rp" attribute
    rplc   = per line in file replace string, could change to dictionary for clarity
    '''
    # nsCurrent = cmds.namespaceInfo(currentNamespace=True)
    # cmds.namespace(set=':')
    if os.path.isfile( path ):
        if prefix != '':
            prefix = prefix + '_'
        addNode = ''
        for line in open( path ).readlines():
            if rp != {None: None}:
                # print( '___', rp.keys() )
                # print( rp )
                line = replaceInString( line, rp )
            # character and sub-character set line
            if 'ParentInfo=' in line:
                # print line, '--'
                line = line.split( '=' )[1].strip( '\n' ).partition( '|' )
                # line = updateCS(string=line, old=cs[0], new=cs[1])
                if line[0] == 'none':
                    # top character
                    # print(prefix + line[2])
                    charName = prefix + line[2]
                    # print(charName)
                    charName = cmds.character( name = charName, em = True )
                    # print( charName )
                    addNode = charName
                else:
                    # sub-character set
                    charName = prefix + line[2]
                    # print(charName)
                    charTmp = cmds.character( name = charName, em = True )
                    # automatic rename of duplicate, splitting extra string
                    dup = ''
                    if charTmp != charName:
                        # print('charName:', charName)
                        # print('charTmp:', charTmp)
                        dup = charTmp.split( charName )[1]
                        charName = charTmp
                    cmds.character( charName, fe = prefix + line[0] + dup )
                    addNode = charName
            # character set members line
            else:
                # does not account for multiple refs in one set, like character
                # and prop
                if ':' in line:
                    line = updateNS( str( line ), str( ns ) )
                    if cmds.objExists( line ) is False:
                        sel = cmds.ls( sl = True )
                        if len( sel ) > 0:
                            sel = sel[0]
                            sel = nameSpace( sel, base = True )
                            line = updateNS( line, sel[0] + ':' + sel[1] )
                        else:
                            message( 
                                'Object ' + line + ' was not found. Select an object in desired namespace and try again.' )
                try:
                    cmds.character( line.strip( '\n' ), fe = addNode )
                except:
                    loadWarning = 'no attribute found, %s, skipping...' % ( 
                        line.strip( '\n' ) )
                    mel.eval( "warning\"" + loadWarning + "\";" )
                else:
                    cmds.character( line.strip( '\n' ), fe = addNode )
        # cmds.namespace(set=nsCurrent)
    else:
        message( 'Path not found: ' + path )


def activateSet( setList ):
    string = ''
    qts = "\""
    if type( setList ) != list:
        setList = [setList]
    max = len( setList )
    i = 0
    for item in setList:
        if item:
            item = qts + item + qts
            if i == 0:
                string = item
            elif i != max:
                string = string + ', ' + item
            else:
                string = string + item
            i = i + 1
        else:
            print( item )
            message( 'nothing found to activate' )
    cmd = "setCurrentCharacters({" + string + "});"
    mel.eval( cmd )


class GetSetOptions():

    def __init__( self ):
        # when 'multiple' is active as a set, active objects can be found if a connection exists to 'set1'
        # 'set1' cannot be queried....
        # cant toggle through char sets as a selection, selected set is skipped
        self.sel = cmds.ls( sl = True )
        self.current = currentSet()
        if self.sel:
            self.options = ['', self.sel[0]]
            self.charSet = self.sel[0]
            # create options list
            self.parentSet()
        else:
            self.options = [None]
        # print self.options

    def parentSet( self ):
        self.charSet = cmds.listConnections( 
            self.charSet, t = 'character', s = False, d = True )
        if self.charSet:
            self.charSet = list( set( self.charSet ) )[0]
            self.options.append( self.charSet )
            self.parentSet()
        else:
            pass


def currentSet():
    form = "MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|formLayout11"
    form = "RangeSlider|MainPlaybackRangeLayout|formLayout9|formLayout10|formLayout11"  # maya 2018
    form = 'RangeSlider|MainPlaybackRangeLayout|formLayout9|formLayout11|formLayout12'  # maya 2020
    txtFld = cmds.formLayout( form, q = True, ca = True )
    if len( txtFld ) != 0:
        txtFld = txtFld[1]
        val = cmds.textField( txtFld, q = True, tx = True )
        if 'No Character Set' not in val:
            return val
        else:
            return None


def currentSet2():
    ge = 'graphEditor1OutlineEd'
    sel = cmds.ls( sl = 1 )
    cmds.select( cl = 1 )
    # shows selectionConnection object, populates ge
    geL = cmds.outlinerEditor( ge, q = 1, mlc = 1 )
    # active sets
    result = cmds.selectionConnection( geL, q = 1, obj = 1 )
    if sel:
        cmds.select( sel )
    return result


def smartActivateSet( *args ):
    smarterActivateSet()


def smarterActivateSet( *args ):
    set = GetSetOptions()
    # print set.options, '_________'
    opt = str( len( set.options ) - 1 )
    if len( set.sel ) != 0:
        if len( set.sel ) > 1:  # multi object selection
            activateSet( set.sel )
            cmds.warning( '-- multiple objects set as character set --' )
            return set.sel
        if set.current:
            if set.current in set.options:
                idx = set.options.index( set.current )
                if idx != len( set.options ) - 1:
                    activateSet( set.options[idx + 1] )
                    message( 
                        'set --   ' + set.options[idx + 1] + '     -- ' + str( idx + 1 ) + ' of ' + opt, maya = True )
                else:
                    activateSet( set.options[0] )
                    message( 
                        'set --   ' + set.options[0] + '     -- ' + str( 0 ) + ' of ' + opt, maya = True )
            else:
                activateSet( set.options[1] )
                message( 
                    'set --   ' + set.options[1] + '     -- ' + str( 1 ) + ' of ' + opt, maya = True )
        else:
            activateSet( set.options[1] )
            message( 
                'set --   ' + set.options[1] + '     -- ' + str( 1 ) + ' of ' + opt, maya = True )
    else:
        activateSet( set.options[0] )


def toggleMembershipToCurrentSet( sel = [], attrs = [], shapeAttrs = [] ):
    current = GetSetOptions()
    # current.currentSet()  # add if current == None, return message and bail
    if not sel:
        sel = cmds.ls( sl = True )
        # collect object attrs
    if not attrs:
        attrs = cmds.channelBox( 'mainChannelBox', q = True, sma = True )
    # obj = cmds.channelBox('mainChannelBox', q=True, mol=True)[0]
    # collect shape attrs
    if not shapeAttrs:
        shapeAttrs = cmds.channelBox( 'mainChannelBox', q = True, ssa = True )
    # print sel
    output = None
    # change this to ask for selected channelBox attrs fist, if None, work
    # with entire object
    if len( sel ) == 1:
        sel = sel[0]
        try:
            shape = cmds.channelBox( 'mainChannelBox', q = True, sol = True )[0]
        except:
            pass
        # object attr toggle
        if attrs:
            # print '__1'
            for attr in attrs:
                if cmds.attributeQuery( attr, node = sel, ex = True ):
                    if cmds.character( sel + '.' + attr, im = currentSet() ) is False:
                        # print attr, sel
                        # BUG: sometimes throws error, only one set was in
                        # scene, no sub chars
                        cmds.character( sel + '.' + attr, fe = currentSet() )
                        # print attr, '  added'
                    else:
                        output = cmds.character( 
                            sel + '.' + attr, rm = currentSet() )
                        # print attr, '  removed'
                else:
                    pass
                    # print 'doesnt exist  ', sel + '.' + attr
        # shape attr toggle
        elif shapeAttrs:
            # print '__2'
            for attr in shapeAttrs:
                if cmds.character( shape + '.' + attr, im = currentSet() ) is False:
                    cmds.character( shape + '.' + attr, fe = current.currentSet() )
                    # print attr, '  added'
                else:
                    output = cmds.character( 
                        shape + '.' + attr, rm = currentSet() )
                    # print attr, '  removed'
        else:
            # print 'there'
            members = cmds.character( currentSet(), q = True )
            membersObj = []
            if members:
                for member in members:
                    membersObj.append( member.split( '.' )[0] )
            membersObj = list( set( membersObj ) )
            if sel not in membersObj:
                # print sel
                # print currentSet()
                try:
                    cmds.character( sel, fe = currentSet() )
                except:
                    cmds.warning( 
                        '--  ' + sel + '  -- Likely something wrong with the connected anim curve, Try deleting it. --' )
            else:
                for member in members:
                    if sel in member:
                        cmds.character( member, rm = currentSet() )
                    else:
                        pass
    else:
        for item in sel:
            toggleMembershipToCurrentSet( 
                sel = [item], attrs = attrs, shapeAttrs = shapeAttrs )
            # print 'wrong'
            # add toggle if / else
            # cmds.character(sel, include=currentSet())


def insertKey():
    '''
    #inserts key on active character set if no objects are selected
    '''
    sel = cmds.ls( sl = True )
    if len( sel ) == 0:
        if currentSet() != 'Multiple':
            cmds.setKeyframe( currentSet(), i = True )
            message( 'Key inserted to set:  ' + currentSet(), maya = True )
        else:
            cmds.setKeyframe()
    else:
        frames = ac.getKeyedFrames( sel )
        if frames:
            cmds.setKeyframe( i = True )
            message( 'Key inserted to selection', maya = True )
        else:
            cmds.setKeyframe()


def insertKeyToAnimLayer():
    '''
    inserts key to all animcurves in anim layer, wont key if objects has not been keyed but is in anim layer
    '''
    currentLayer = cmds.treeView( 
        'AnimLayerTabanimLayerEditor', q = True, selectItem = True )
    curves = cmds.animLayer( currentLayer[0], q = True, anc = True )
    cmds.setKeyframe( curves, i = True )


def parent( parent = True ):
    if parent:
        # make member of second selection
        cmds.character( cmds.ls( sl = True )[0], include = cmds.ls( sl = True )[1] )
    else:
        # remove membership from second selection
        cmds.character( cmds.ls( sl = True )[0], rm = cmds.ls( sl = True )[1] )


def matchCharSet( source = None, objs = [] ):
    '''
    source = get character set if connected
    objs = make members of list in same set as source
    '''
    char = cmds.listConnections( source, t = 'character', s = False, d = True )
    if char:
        char = list( set( char ) )
        if len( char ) == 1:
            for obj in objs:
                cmds.character( obj, include = char[0] )
        else:
            message( 'Object not added to Charecter set. More than one option found.' )
