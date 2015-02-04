import urllib2
import imp
import os


def mod(modulename=''):
    '''
    which source, build module
    '''
    local = False
    # path vars
    varFile = 'webrSource.py'
    varPath = os.path.expanduser('~') + '/maya/scripts/'
    webPath = 'https://raw.githubusercontent.com/boochos/work/master/'
    # paths
    urlPath = webPath + modulename + '.py'
    localPath = varPath + modulename + '.py'
    # check for local variable
    if os.path.isfile(varPath + varFile):
        import webrSource as frm
        reload(frm)
        local = frm.local
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
