import maya.cmds as cmds
import os


def shapeDir():
    varPath = cmds.internalVar(userAppDir=True)
    path = os.path.join(varPath, 'controlShapes')
    if not os.path.isdir(path):
        os.mkdir(path)
    return path
