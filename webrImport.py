import imp
import os
import platform

import maya.cmds as cmds
import maya.mel as mel
# import urllib.request

ver = platform.python_version()
# print( ver )
if '2.' in ver:
    import urllib2
else:
    import urllib.request
    pass


# import urllib2
# import urllib.request
def mod( modulename = '', f = False ):
    '''
    Which source, build module, piggy back functions.
    code doubles up to keep variables hidden
    '''
    # print( '___import', modulename )
    #
    # vars
    # source file, net or local variable
    varFile = 'webrSource.py'
    # decipher main scripts, use dir in maya version if fails
    varPath = cmds.internalVar( userAppDir = True )
    varPathTest = os.path.join( varPath, 'scripts' )
    if os.path.isdir( varPathTest ):
        varPath = varPathTest
    else:
        varPath = cmds.internalVar( userScriptDir = True )
    # more vars
    webPath = 'https://raw.githubusercontent.com/boochos/work/master/'
    piggy = 'webrPiggyBack'
    local = False

    #
    # check if mel, download, else build python in ram
    if '.mel' in modulename:
        # download to scripts directory

        melF = urllib.URLopener()  # doesnt like this in py 3
        if os.path.isdir( varPath ):
            melF.retrieve( webPath + modulename, os.path.join( varPath, modulename ) )
            # urllib.request.urlretrieve( webPath + modulename, os.path.join( varPath, modulename ) )
            mel.eval( 'rehash' )
        else:
            pass
            # print '___not a path', varPath + modulename
    else:
        #
        # check for local variable
        try:
            import webrSource as frm
            local = frm.local
            # print frm.local , '____local'
        except:
            print ( 'no local variable found' )
        # removed below, as its trying to find specific file and doesnt account for shared sys path
        # perform regular import instead
        # also need to find path to local file if in shared directory, check and parse sys path
        '''
        if os.path.isfile(os.path.join(varPath, varFile)):
            import webrSource as frm
            reload(frm)
            local = frm.local
        '''

        '''
        #
        # piggy back function
        # paths
        urlPath = webPath + piggy + '.py'
        localPath = os.path.join(varPath, piggy + '.py')
        if local:
            infile = open(localPath, 'r')
            contents = infile.read()
        else:
            req = urllib2.Request(urlPath)
            response = urllib2.urlopen(req)
            contents = response.read()
        # create module
        # must be exec mode
        codeobj = compile(contents, '', 'exec')
        module = imp.new_module(piggy)
        exec(codeobj, module.__dict__)
        module.run(modulename=modulename)
        '''

        #
        # actual function
        # paths
        urlPath = webPath + modulename + '.py'
        localPath = os.path.join( varPath, modulename + '.py' )
        if local:
            localPath = os.path.join( varPath, modulename + '.py' )
            if os.path.isfile( localPath ):
                infile = open( localPath, 'r' )
                contents = infile.read()
            else:
                pth = os.sys.path
                for p in pth:
                    localPath = os.path.join( p, modulename + '.py' )
                    if os.path.isfile( localPath ):
                        infile = open( localPath, 'r' )
                        contents = infile.read()
        else:
            req = urllib2.Request( urlPath )
            response = urllib2.urlopen( req )
            # req = urllib.request( urlPath )
            # response = urllib.request.urlopen( req )
            contents = response.read()
        # create module
        # must be exec mode
        if contents:
            codeobj = compile( contents, '', 'exec' )
            module = imp.new_module( modulename )
            exec( codeobj, module.__dict__ )
            # print '___end'
            return module
        else:
            print ( "Couldn't find module" )
            return None
