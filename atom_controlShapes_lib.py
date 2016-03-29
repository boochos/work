import maya.cmds as cmds
import os


def shapeDir():
    # user shapes
    varPath = cmds.internalVar(userAppDir=True)
    shpPath = 'controlShapes'
    path = os.path.join(varPath, shpPath)
    # shared shapes
    pth = os.sys.path
    for p in pth:
        parentPath = os.path.abspath(os.path.join(p, os.pardir))
        sharedPath = os.path.join(parentPath, shpPath)
        if os.path.isdir(sharedPath):
            # print sharedPath, '  __path found through sys path'
            return sharedPath
    # make local version if non exist
    if not os.path.isdir(path):
        os.mkdir(path)
    return path
