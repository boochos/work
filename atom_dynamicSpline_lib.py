from pymel.core import *
import atom_placement_lib as place
import atom_miscellaneous_lib as misc
import atom_joint_lib as jnt
import atom_spline_lib as spln
import atom_splineFk_lib as splnFk
import atom_deformer_lib as adl

def makeDynamic(parentOne, parentTwo, mstrCrv):
    mstrCrvObj = ls(mstrCrv)[0]
    mstrCrvObj.visibility.set(False)
    dup        = duplicate(mstrCrv, name=mstrCrv + '_dynamicDuplicate')[0]
    
    select(dup)    
    Mel.eval('makeCurvesDynamicHairs 0 0 1;')
    hairSys  = None
    dynCurve = None
    folSys   = dup.getParent()

    for i in folSys.getShape().connections(d=True, s=False):
        if i.getShape().type() == 'nurbsCurve':
            dynCurve = i
        
        elif i.getShape().type() == 'hairSystem':
            hairSys = i
    blendNode = blendShape(dynCurve,mstrCrv, n='face_blendshape')
    hairSys.getShape().iterations.set(10)
    
    #Set the follicle system properties
    folshape = folSys.getShape()
    folshape.pointLock.set(1)
    folshape.overrideDynamics.set(1)
    folshape.lengthFlex.set(.1)
    folshape.damp.set(.1)
    folshape.stiffness.set(1)
    folshape.stiffnessScale[1].stiffnessScale_Position.set(1)
    folshape.stiffnessScale[1].stiffnessScale_FloatValue.set(0)
    #parentConstraint(masterObj,dynCurve, mo=True)
    parent(folSys.getParent(), parentOne)
    
def createAndConnectBlendNodesToAttr(ctrl,attr,nodes):
    ctrlObj = ls(ctrl)[0]
    #create the driving attribute
    misc.optEnum(ctrlObj.name(), attr='Stretch')
    ctrlObj.addAttr(attr, at='double', max=1, min=0, dv=0,k=True)
    for node in nodes:
        #make the string then execute to make it so
        connectAttr(ctrl + '.'+ attr, node + '.blender')
        #exeStr = 'ls("%s")[0].%s.connect(ls("%s")[0].blender)'%(ctrl,attr,node)
        #exec(exeStr)

def renameDynJntChain(obj, prefix, num, suffix=None):
    name = '%s_dynJnt_jnt_%02d' %(prefix, num)
    if suffix != None:
        name += '_' + suffix
    obj.rename(name)
    return name