import datetime
import maya.cmds as cmds
import maya.mel as mm


def setProjectFromFilename( dirVar ):
    path = cmds.file( query = True, sceneName = True )
    if len( path ) > 0:
        idx = path.rfind( dirVar )
        if idx > -1:
            setPath = path[:idx + 2]
            m = mm.eval( 'setProject "' + setPath + '";' )
            print( '-- Project set to: %s' % ( setPath ) )
        else:
            print( '\n' )
            printMayaWarning( '\\"3D\\" not found in path, setProject aborted.' )
    else:
        printMayaWarning( 'No file path found, operation aborted.' )


#-------------
# Name        :getDate
# Arguments   :None
# Description :Returns the date in a year, month, day format as a string
#-------------
def getDate( *args ):
    date = datetime.date.today()  # get the current date
    year = str( date.year )  # convert the int to a string
    month = str( date.month )
    day = 'undefined'
    # day will only return one digit if less that 10, the variable
    # has to be checked before conversion so the extra digit can be
    # added
    if date.day < 10:
        day = '0' + str( date.day )
    else:
        day = str( date.day )
    return '%s, %s, %s' % ( year, month, day )


#-------------
# Name        :scanForSceneRefs
# Arguments   :None
# Description :Searches all the transforms in the scene for the
#             ':' that is the furthest to the right. This is to
#             detect referenced namespaces
#-------------
def scanForSceneRefs( *args ):
    import maya.cmds as cmds
    refDic = {}
    refList = []
    nodes = cmds.ls( rf = True )
    for node in nodes:
        try:
            cmds.referenceQuery( node, filename = True )
        except:
            print( '%s, not found skipping' % ( node ) )
        else:
            path = cmds.referenceQuery( node, filename = True )
            isRefLoaded = cmds.file( path, query = True, dr = True )
            if ( isRefLoaded == 0 ):
                if refDic.has_key( node ) != 1:
                    nameSpace = cmds.file( path, query = True, ns = True )
                    refDic[nameSpace] = nameSpace
    for ref in refDic:
        refList.append( ref )

    if ( len( refList ) == 0 ):
        refList.append( 'None' )
    return refList


#-------------
# Name        :scanNodeForNamespace
# Arguments   :None
# Description :Searches the node for it's namespace
#-------------
def scanNodeForNamespace( node ):
    import maya.cmds as cmds
    refList = []
    namespace = None
    node = node.strip( '\n' )
    try:
        cmds.referenceQuery( node, filename = True )
    except:
        print( '%s, not found skipping' % ( node ) )
    else:
        path = cmds.referenceQuery( node, filename = True )
        isRefLoaded = cmds.file( path, query = True, dr = True )
        if ( isRefLoaded == 0 ):
            namespace = cmds.file( path, query = True, ns = True )
    return namespace


#-------------
# Name        :printMayaWarning
# Arguments   :message<string>: String that will be printed
# Description :Print a warning message in Maya
#-------------
def printMayaWarning( message ):
    import maya.mel as mm
    mm.eval( 'warning \"' + message + '\";' )
