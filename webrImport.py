import urllib2
import urllib
import imp
import os
import maya.cmds as cmds
import maya.mel as mel


def mod(modulename='', f=False):
    '''
    Which source, build module, piggy back functions.
    code doubles up to keep variables hidden
    '''
    # print '___start', modulename
    #
    # vars
    # source file, net or local variable
    varFile = 'webrSource.py'
    # decipher main scripts, use dir in maya version if fails
    varPath = cmds.internalVar(userAppDir=True)
    varPathTest = os.path.join(varPath, 'scripts')
    if os.path.isdir(varPathTest):
        varPath = varPathTest
    else:
        varPath = cmds.internalVar(userScriptDir=True)
    # more vars
    webPath = 'https://raw.githubusercontent.com/boochos/work/master/'
    piggy = 'webrPiggyBack'
    local = False

    #
    # check if mel, download, else build python in ram
    if '.mel' in modulename:
        # download to scripts directory
        melF = urllib.URLopener()
        if os.path.isdir(varPath):
            melF.retrieve(webPath + modulename, os.path.join(varPath, modulename))
            mel.eval('rehash')
        else:
            pass
            # print '___not a path', varPath + modulename
    else:
        #
        # check for local variable
        if os.path.isfile(os.path.join(varPath, varFile)):
            import webrSource as frm
            reload(frm)
            local = frm.local

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

        #
        # actual function
        # paths
        urlPath = webPath + modulename + '.py'
        localPath = os.path.join(varPath, modulename + '.py')
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
        module = imp.new_module(modulename)
        exec(codeobj, module.__dict__)
        # print '___end'
        return module
