import urllib2
import imp
import os


def makeModule(modulename=''):
    # file path
    path = 'https://raw.githubusercontent.com/boochos/work/master/' + modulename + '.py'
    req = urllib2.Request(path)
    response = urllib2.urlopen(req)
    # read file
    contents = response.read()
    # must be exec mode
    codeobj = compile(contents, '', 'exec')
    module = imp.new_module(modulename)
    exec(codeobj, module.__dict__)
    # done
    return module
