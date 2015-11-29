import maya.cmds as cmds
import maya.mel as mm
import os
# This is all dirty code, because is sure aint clean!


def writeDirtyInfInfo(*args):
    sel = cmds.ls(sl=True, fl=True)
    obj = sel[0].split('.')[0]
    shape = cmds.listRelatives(obj, shapes=True)[0]
    # going to assume this is being used for the ol skoo
    skinCluster = mm.eval('findRelatedSkinCluster("faceDriver_Crv")')
    filePath = os.path.join(os.getenv('HOME'), 'Desktop/tmpWgtExport.txt')
    f = open(filePath, 'w')
    for i in sel:
        infLst = cmds.skinCluster(skinCluster, query=True, inf=True)
        wgtLst = cmds.skinPercent(skinCluster, i, query=True, v=True)
        if len(infLst) == len(wgtLst):
            wList = []
            wList.append('[')
            for i in range(0, len(infLst), 1):
                if wgtLst[i] > 0:
                    aStr = '[\'%s\',%s],' % (infLst[i], wgtLst[i])
                    wList.append(aStr)
                    #line = '[\'%s\',%s]\n' %(infLst[i], wgtLst[i])
            wList[len(wList) - 1] = wList[len(wList) - 1][:-1]
            wList.append(']\n')
            print wList
            f.writelines(wList)
    f.close()


def readDirtyInfInfo(*args):
    sel = cmds.ls(sl=True, fl=True)
    obj = sel[0].split('.')[0]
    shape = cmds.listRelatives(obj, shapes=True)[0]
    skinCluster = mm.eval('findRelatedSkinCluster("' + shape + '")')
    infLst = cmds.skinCluster(skinCluster, query=True, inf=True)
    cmds.setAttr(skinCluster + '.normalizeWeights', 0)

    filePath = os.path.join(os.getenv('HOME'), 'Desktop/tmpWgtExport.txt')
    f = open(filePath, 'r')
    lines = f.readlines()

    cvCnt = 0
    if len(sel) == len(lines):
        for cv in sel:
            wgtLst = cmds.skinPercent(skinCluster, cv, query=True, v=True)
            # set turn off normalization and set all weights to zero
            for i in range(0, len(infLst), 1):
                cmds.skinPercent(skinCluster, cv, tv=(infLst[i], 0))

            rLine = eval(lines[cvCnt])
            for i in range(0, len(rLine), 1):
                cmds.skinPercent(skinCluster, cv, tv=(rLine[i][0], rLine[i][1]))
            f.close()
            cvCnt += 1
        cmds.setAttr(skinCluster + '.normalizeWeights', 1)
    else:
        print 'Maya selection count doesn\'t match exported file component count.'


def win(*args):
    if cmds.window('atom_dirtyLittleInfWin', ex=True):
        cmds.deleteUI('atom_dirtyLittleInfWin')
    cmds.window('atom_dirtyLittleInfWin', t='DIRTY LITTLE INF WINDOW')
    cmds.columnLayout(adj=True)
    cmds.button(l='WRITE DIRTY INFO', c=writeDirtyInfInfo)
    cmds.button(l='READ DIRTY INFO', c=readDirtyInfInfo)
    cmds.showWindow('atom_dirtyLittleInfWin')
