import os
import maya.cmds as cmds
import maya.mel as mel
# TODO: not working at all

def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def createDefaultPath():
    path = defaultPath()
    if not os.path.isdir(path):
        os.mkdir(path)
        message("path:   '" + path + "'   created")
    else:
        pass
        # message("path:   '" + path + "'   exists")
    return path


def getDefaultPath():
    user = os.path.expanduser('~')
    mainDir = user + '/maya/contorolShapes/'
    return mainDir


def exportShape(name=''):
    '''
    #Name        :exportCurveShape
    #Arguements  :N/A
    #Description :Exports the local transforms of the cvs on the selected curve.
    #Notes       :This is designed to only work with the Atom win 
    '''
    # get the selection
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        path = os.path.join(uiPath, uiName) + '.txt'
        # if the file exists, stop here
        if os.path.isfile(path) is False:
            # extract the curves shape node
            shapeNode = cmds.listRelatives(sel[0], shapes=True)[0]
            if cmds.nodeType(shapeNode) == 'nurbsCurve':
                cvInfo = cmds.getAttr(shapeNode + '.cv[*]')
                outFile = open(path, 'w')
                for i in range(0, len(cvInfo), 1):
                    info = cmds.getAttr(shapeNode + '.cv[' + str(i) + ']', query=True, os=True, t=True)
                    outFile.write('%s %s %s\n' % (info[0], info[1], info[2]))
                outFile.close()
    else:
        message('Select one curve to export')


def importShape(name, path, scale=1.0):
    '''
    #Name        :importCurveShape
    #Arguements  :<name>: str
    #            :<path>: str
    #Description :Imports a curve shape based on the path and name info
    #Notes       :Function expects a .txt file
    '''
    selection = cmds.ls(sl=True, tr=True)
    path = path + '/' + name + '.txt'
    # change the shape of multiple selected curves
    if len(selection) > 0:
        for sel in selection:
            # get the shape node
            shapeNode = cmds.listRelatives(sel, shapes=True)[0]
            # cvInfo is populated then interated through later
            cvInfo = []
            if cmds.nodeType(shapeNode) == 'nurbsCurve':
                inFile = open(path, 'r')
                for line in inFile.readlines():
                    # extract the position data stored in the file
                    cvLine = line.strip('\n')
                    cvLine = cvLine.split(' ')
                    tmp = float(cvLine[0]) * scale, float(cvLine[1]) * scale, float(cvLine[2]) * scale
                    cvInfo.append(tmp)
                inFile.close()
                # Shape the curve
                if overRide != False:
                    cmds.setAttr(shapeNode + '.overrideEnabled', 1)
                    cmds.setAttr(shapeNode + '.overrideColor', overRide)

                if len(cvInfo) == len(cmds.getAttr(shapeNode + '.cv[*]')):
                    for i in range(0, len(cvInfo), 1):
                        cmds.getAttr(shapeNode + '.cv[' + str(i) + ']', os=True, t=cvInfo[i])
                else:
                    # Curves with different CV counts are not compatible
                    message('CV count[' + str(len(cmds.getAttr(shapeNode + '.cv[*]'))) + '] from selected does not match import CV count[' + str(len(cvInfo)) + ']')
    else:
        message('Select a NURBS curve if you truly want to proceed...')
