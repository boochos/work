import os
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import atom_miscellaneous_lib as misc

def exportCurveShape(*args):
    '''
    #-------------
    #Name        :exportCurveShape
    #Arguements  :N/A
    #Description :Exports the local transforms of the cvs on the selected curve.
    #Notes       :This is designed to only work with the Atom win 
    #-------------
    '''
    #get the selection
    sel = cmds.ls(selection=True)
    if len(sel) == 1:
        #assemble the variables to build the path name later on
        uiPath = cmds.textField('atom_csst_exportPath_textField',query=True, tx=True )
        uiName = cmds.textField('atom_csst_exportName_textField', query=True, tx=True)
        if uiName != 'None':
            path = os.path.join(uiPath, uiName) + '.txt'
            #if the file exists, stop here
            if os.path.isfile(path) == False:
                #extract the curves shape node
                shapeNode = cmds.listRelatives(sel[0], shapes =True)[0]
                if cmds.nodeType(shapeNode) == 'nurbsCurve':
                    cvInfo = cmds.getAttr(shapeNode + '.cv[*]')
                    outFile   = open(path, 'w')
                    for i in range(0, len(cvInfo),1):
                        info =  cmds.xform(shapeNode + '.cv['+ str(i) +']', query=True, os=True, t=True)
                        outFile.write('%s %s %s\n' %(info[0], info[1], info[2]))
                    outFile.close()
                    #add the butto
                    cmds.button(label=uiName, c='import atom_ui_lib\natom_ui_lib.importCurveShape("'+uiName+'","'+uiPath +'")',p='atom_ccst_main_columnLayout')
                    refreshWindow('atom_win')
    else:
        print 'Select one curve to export'


def importCurveShape(name,path, codeScale = False, overRide = False):
    '''
    #-------------
    #Name        :importCurveShape
    #Arguements  :<name>: str
    #            :<path>: str
    #Description :Imports a curve shape based on the path and name info
    #Notes       :Function expects a .txt file
    #-------------
    '''
    selection  = cmds.ls(selection=True, tr=True)
    path = path + '/' + name + '.txt' 
    #change the shape of multiple selected curves
    if len(selection) > 0:
        for sel in selection:
            #get the shape node
            shapeNode = cmds.listRelatives(sel, shapes =True)[0]
            #cvInfo is populated then interated through later
            cvInfo = []
            curveScale = None
            if codeScale == False:
                curveScale = cmds.floatField('atom_csst_curveScale_floatField', query=True, value=True)
            else:
                curveScale = codeScale
                
            if cmds.nodeType(shapeNode) == 'nurbsCurve':
                inFile = open(path, 'r')
                for line in inFile.readlines():
                    #extract the position data stored in the file
                    cvLine = line.strip('\n')
                    cvLine = cvLine.split(' ')
                    tmp = float(cvLine[0])*curveScale, float(cvLine[1])*curveScale,float(cvLine[2])*curveScale
                    cvInfo.append(tmp)
                inFile.close()
                #Shape the curve
                if overRide != False:
                    cmds.setAttr(shapeNode + '.overrideEnabled', 1)
                    cmds.setAttr(shapeNode + '.overrideColor', overRide)
                    
                if len(cvInfo) == len(cmds.getAttr(shapeNode + '.cv[*]')):
                    for i in range(0,len(cvInfo),1):    
                        cmds.xform(shapeNode + '.cv[' + str(i) +']',os = True, t = cvInfo[i])
                else:
                    #Curves with different CV counts are not compatible
                    OpenMaya.MGlobal.displayError('CV count['+str(len(cmds.getAttr(shapeNode + '.cv[*]')))+'] from selected does not match import CV count['+str(len(cvInfo))+']')
    else:
        OpenMaya.MGlobal.displayError('Select a NURBS curve if you truly want to proceed...')
