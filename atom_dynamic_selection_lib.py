import os
import maya.OpenMaya as OpenMaya
from pymel.core import *


class Atom_Connect_Attr(object):

    '''
    Class: <Atom_Connect_Attr>: Class that creates and connects attibutes

    Methods:

       __init__(outObj, inObj, attr)  -- Class initialization.
                                      -- outObj<pynode> : Outgoing attr connection
                                      -- inObj <pynode> : Incomming attr connection
                                      -- attr  <string> : Attribute to create on the outObj and inObj

       connect() -- Connects the outObj and inObj using the attr and the connecting attribute
    '''

    def __init__(self, outObj, inObj, attr):
        self.outObj = None
        self.inObj = None
        self.attr = attr

        # check for outObj's existance
        if objExists(outObj):
            self.outObj = ls(outObj)[0]
        else:
            errorStr = ('outObj, %s does not exist. Operation failed') % s(outObj)
            OpenMaya.MGlobal.displayError(errorStr)

        # check for inObj's existance
        if objExists(inObj):
            self.inObj = ls(inObj)[0]
        else:
            errorStr = ('inObj, %s does not exist. Operation failed') % (inObj)
            OpenMaya.MGlobal.displayError(errorStr)

    def connect(self):
        if self.outObj != None and self.inObj != None:
            # make sure the objects done all ready have the attr
            if not self.outObj.hasAttr(self.attr):
                self.outObj.addAttr(self.attr, at='message')

            if not self.inObj.hasAttr(self.attr):
                self.inObj.addAttr(self.attr, at='message')

            # create the connection
            exec('ls("' + str(self.outObj) + '")[0].' + self.attr + '.connect(ls("' + str(self.inObj) + '")[0].' + self.attr + ',force=True)')


def addSelectionConnections(*args):
    '''
    Description: Function uses the project path and looks for a selection list folder. Once this folder is found
                 it looks for all sub-folders, these folders names are used as "master" objects, the folder name
                 has to match a maya scene object name. Within the folder are text files. The names of these text 
                 files are used as the attribute to connect to the master. The contents of the files are read and
                 these once again have to be objects that exist is maya as they recieve the connection from the master.

                 folder name(outObj).file name(attribute) ---|connects|---> file content line(inObj).file name(attribute)
                 eg. myObj(folder)-
                           |
                           -someAttr(file)-
                                    |
                                    -myOtherObj(file line)
                connection would be, myObj.someaAttr -----> myOtherObj.someAttr
    '''
    # get the path to the selection lists
    list_path = os.path.join(os.getenv('KEY_PROJECT_PATH'), 'selection_lists')
    # confirm the path path exists
    if os.path.isdir(list_path):
        # list the files in the path
        files = os.listdir(list_path)
        # iterate
        for f in files:
            # cull out any file that starts with .
            if f[0] != '.':
                # build the masterPath
                masterPath = os.path.join(list_path, f)
                # confirm that masterPath is a directory
                if os.path.isdir(masterPath):
                    # masterName(folder name) is the outObj
                    masterName = os.path.basename(masterPath)
                    listFiles = os.listdir(masterPath)
                    # the file name is used as the attr to connect to the main
                    for lf in listFiles:
                        if lf[0] != '.':
                            # read in the file contents
                            readfile = open(os.path.join(masterPath, lf), 'r')
                            readlines = readfile.readlines()
                            for line in readlines:
                                # line is the inObj
                                conObj = Atom_Connect_Attr(masterName, line.strip('\n'), lf.strip('\n'))
                                conObj.connect()
                                del(conObj)


class Atom_Read_Dynamic_Connection(object):

    '''
    Class: <Atom_Read_Dynamic_Connection>: Class that searches an object for attributes of a named type. It's expected
                                           that the attribute to find is the first part of the name, eg. "Atom_myAttr", if 
                                           the searchVar was "Atom", "Atom_myAttr" and it's connections would be found.

    Methods:
       __init__(obj, searchVar) -- Class initialization.
                                -- obj<string>       : name of the object to search
                                -- searchVar<string> : name of the attribute to find

       getAttr                  -- Find the attributes that start with the searchVar
       getMaster                -- Find the object that holds all the connection of the searchVar
       buildConnectionList      -- Finds all the connections on the master of a specific attribute type and puts them into a list.

       Notes: The way the paradigm works, what ever object that is the master holds all the connections of various types. When
       an object is fed into the class it's connection to the master is found. The master then keeps track of this connectection and finds
       all other objects with the same connection.
    '''

    def __init__(self, obj, searchVar='Atom'):
        self.objStr = obj
        self.master = None
        self.searchVar = searchVar
        self.attrList = []
        self.conList = []

        if self.objStr != None:
            self.getAttr()

            if len(self.attrList) > 0:
                self.getMaster()
                self.buildConnectionList()
            else:
                errorStr = '%s, has no attribute starting with %s' % (self.objStr, self.searchVar)
                OpenMaya.MGlobal.displayError(errorStr)

    def getAttr(self):
        if self.objStr:
            for attr in listAttr(self.objStr):
                if attr[:len(self.searchVar)] == self.searchVar:
                    self.attrList.append(attr)

    def getMaster(self):
        if len(self.attrList) == 1:
            # test if there is only one attribute to find the master
            attrTest = self.master = listConnections(self.objStr + '.' + self.attrList[0])

            if len(attrTest) > 1:
                self.master = self.objStr
            else:
                self.master = attrTest[0]
        elif len(self.attrList) > 1:
            self.master = self.objStr
        else:
            self.master = None

    def buildConnectionList(self):
        if self.master != None:
            for attr in self.attrList:
                if self.objStr == self.master:
                    self.conList.append(self.master)
                mCon = listConnections(self.master + '.' + attr)
                for con in mCon:
                    self.conList.append(con.name())


def selectionCMD(*args):
    selection = ls(sl=True)
    selList = []
    for sel in selection:
        sCls = Atom_Read_Dynamic_Connection(sel.name())
        if len(sCls.conList) > 0:
            selList.append(sCls.conList)
    if len(selList) > 0:
        select(selList)
