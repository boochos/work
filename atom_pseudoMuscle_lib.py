from pymel.core import *
import maya.cmds as cmds
from atom import atom_miscellaneous_lib as misc


class StretchJnt(object):
    def __init__(self, name, stretchJnt, suffix='', driveAxis='Z', scaleAxis=['X', 'Y']):
        self.name           = name 
        self.suffix         = suffix
        self.jnt            = stretchJnt
        self.driveAxis      = driveAxis.upper()
        self.scaleAxis      = scaleAxis
        self.bJnt           = None 

        if nodeType(stretchJnt) == 'joint':

            self.jnt            = ls(stretchJnt)[0]
            self.bJnt           = self.jnt.getParent() 
        
            self.createNodes()
            self.connectNodes()
            
    def createNodes(self):
        self.main_MD        = createNode('multiplyDivide',   name = self.name + '_main_MD'   + self.suffix)
        self.main_MD.operation.set(2)
        disAttr             = getAttr(self.jnt + '.translate' + self.driveAxis) 
        setAttr(self.main_MD + '.input2' + self.driveAxis,disAttr)
        
        self.diff_PMA       = createNode('plusMinusAverage', name = self.name + '_diff_PMA'  + self.suffix)
        self.diff_PMA.addAttr('normFactor', at='short', dv=1, r=True)
        self.diff_PMA.operation.set(2)
        
        self.rev_MD         = createNode('multiplyDivide',   name = self.name + '_rev_MD'    + self.suffix)        
        self.finalScale_ADL = createNode('addDoubleLinear',  name = self.name + '_finalScale_ADL' + self.suffix)
        self.finalScale_ADL.input2.set(1)
        
        #ADD BLEND NODE AT THE END OF NODE CHAIN. THE SQUASH/STRETCH NEEDS AN OFF/WEIGHTED EFFECT.
        
        
    def connectNodes(self):
        evalStr = 'ls("%s")[0].translate%s.connect(ls("%s")[0].input1%s)' %(self.jnt, self.driveAxis, self.main_MD, self.driveAxis)
        exec(evalStr)
        
        evalStr = 'ls("%s")[0].output%s.connect(ls("%s")[0].input1D[0])' %(self.main_MD,  self.driveAxis, self.diff_PMA)
        self.diff_PMA.normFactor.connect(self.diff_PMA.input1D[1])
        exec(evalStr)
        
        evalStr = 'ls("%s")[0].output1D.connect(ls("%s")[0].input1%s)' %(self.diff_PMA, self.rev_MD, self.driveAxis)
        exec(evalStr)
        
        evalStr = 'ls("%s")[0].input2%s.set(%s)' %(self.rev_MD, self.driveAxis, -1)
        exec(evalStr)
        
        evalStr = 'ls("%s")[0].output%s.connect(ls("%s")[0].input1)' %(self.rev_MD,self.driveAxis,self.finalScale_ADL )
        exec(evalStr)

        for i in self.scaleAxis:
            evalStr = 'ls("%s")[0].output.connect(ls("%s")[0].scale%s, f=True)' %(self.finalScale_ADL, self.bJnt, i.upper())
            exec(evalStr)
            

#PseudoMuscle('test','_L','joint2','X', ['Y', 'Z'])
'''
select(hi=True)
sel = ls(sl=True)

for jnt in sel:
    childList = jnt.getChildren()
    child = None
    if len(childList) > 0:
        child = childList[0]
        child.setParent(None)
        jnt.rotateAxis.set(-180, 0, 0)
        child.setParent(jnt)
    else:
        jnt.rotateAxis.set(-180, 0, 0)
'''             