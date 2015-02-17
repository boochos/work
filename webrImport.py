import urllib2
import imp
import os


def mod(modulename=''):
    '''
    Which source, build module, piggy back functions.
    code doubles up to keep variables hidden
    '''
    # path vars
    varFile = 'webrSource.py'
    varPath = os.path.expanduser('~') + '/maya/scripts/'
    webPath = 'https://raw.githubusercontent.com/boochos/work/master/'
    piggy = 'webrPiggyBack'
    local = False
    # check for local variable
    if os.path.isfile(varPath + varFile):
        import webrSource as frm
        reload(frm)
        local = frm.local

    # piggy back function
    # paths
    urlPath = webPath + piggy + '.py'
    localPath = varPath + piggy + '.py'
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
    module.run()

    # actual function
    # paths
    print modulename, '&&&&&&&&&&&&&&&&&&&&&&'
    urlPath = webPath + modulename + '.py'
    localPath = varPath + modulename + '.py'
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
    return module
