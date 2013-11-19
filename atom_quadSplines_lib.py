import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc
from atom import atom_splineStage_lib as stage
import atom_splineFk_lib as splnFk

def quadSplines(*args):
    '''\n
    Build splines for quadraped character\n
    '''
    face=None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    if check == 0:
        face = False
    else:
        face=True

    def SplineOpts(name, size, distance, falloff):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField('atom_prefix_textField', e=True, tx=name)
        cmds.floatField('atom_spln_scaleFactor_floatField', e=True, v=size)
        cmds.floatField('atom_spln_vectorDistance_floatField', e=True, v=distance)
        cmds.floatField('atom_spln_falloff_floatField', e=True, v=falloff)

    def OptAttr(obj, attr):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr(obj, ln=attr, attributeType='enum', en='OPTNS' )
        cmds.setAttr(obj + '.' + attr, cb=True)
    if face == False:
        #TAIL
        tailName = 'tail'
        tailSize     = X*1.2
        tailDistance = X*3.0
        tailFalloff  = 0
        tailPrnt = 'tail_Grp'
        tailStrt = 'tail_Grp'
        tailEnd  = 'tailTip_Grp'
        tailAttr = 'tail'
        tail     = ['tail_jnt_01', 'tail_jnt_011']
        ##build spline
        SplineOpts(tailName, tailSize, tailDistance, tailFalloff)
        cmds.select(tail)
        stage.splineStage(4)
        ##assemble
        OptAttr(tailAttr, 'TailSpline')
        cmds.parentConstraint(tailPrnt, tailName + '_IK_CtrlGrp')
        cmds.parentConstraint(tailStrt, tailName + '_S_IK_PrntGrp')
        cmds.parentConstraint(tailEnd, tailName + '_E_IK_PrntGrp')
        misc.hijackCustomAttrs(tailName + '_IK_CtrlGrp', tailAttr)
        ##set options
        cmds.setAttr(tailAttr + '.' + tailName + 'Vis', 0)
        cmds.setAttr(tailAttr + '.' + tailName + 'Root', 0)
        cmds.setAttr(tailAttr + '.' + tailName + 'Stretch', 0)
        cmds.setAttr(tailAttr + '.ClstrVis', 0)
        cmds.setAttr(tailAttr + '.ClstrMidIkBlend', 1)
        cmds.setAttr(tailAttr + '.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(tailAttr + '.VctrVis', 0)
        cmds.setAttr(tailAttr + '.VctrMidIkBlend', 1)
        cmds.setAttr(tailAttr + '.VctrMidIkSE_W', 0.5)
        cmds.setAttr(tailAttr + '.VctrMidTwstCstrnt', 0)
        cmds.setAttr(tailAttr + '.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(tailName + '_S_IK_Cntrl.LockOrientOffOn', 0)
        cmds.setAttr(tailName + '_E_IK_Cntrl.LockOrientOffOn', 0)

    #SPINE
    spineName = 'spine'
    spineSize     = X*2.5
    spineDistance = X*4.0
    spineFalloff  = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'pelvis_Grp'
    spineEnd  = 'chest_Grp'
    spineAttr = 'cog'
    spineRoot = 'root_jnt'
    'spine_S_IK_Jnt'
    spine     = ['pelvis_jnt','spine_jnt_06']
    ##build spline
    SplineOpts(spineName, spineSize, spineDistance, spineFalloff)
    cmds.select(spine)
    stage.splineStage(4)
    ##assemble
    OptAttr(spineAttr, 'SpineSpline')
    cmds.parentConstraint(spinePrnt, spineName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(spineStrt, spineName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(spineEnd, spineName + '_E_IK_PrntGrp', mo=True)
    cmds.parentConstraint(spineName + '_S_IK_Jnt', spineRoot, mo=True)
    misc.hijackCustomAttrs(spineName + '_IK_CtrlGrp', spineAttr)
    ##set options
    cmds.setAttr(spineAttr + '.' + spineName + 'Vis', 0)
    cmds.setAttr(spineAttr + '.' + spineName + 'Root', 0)
    cmds.setAttr(spineAttr + '.' + spineName + 'Stretch', 0)
    cmds.setAttr(spineAttr + '.ClstrVis', 0)
    cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 1)
    cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0.1)
    cmds.setAttr(spineAttr + '.VctrVis', 0)
    cmds.setAttr(spineAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    #NECK
    neckName = 'neck'
    neckSize     = X*2.5
    neckDistance = X*3.5
    neckFalloff  = 0
    neckPrnt = 'neck_Grp'
    neckStrt = 'neck_Grp'
    neckEnd  = 'head_CnstGp'
    neckAttr = 'neck'
    neck     = ['neck_jnt_01','neck_jnt_05']
    ##build spline
    SplineOpts(neckName, neckSize, neckDistance, neckFalloff)
    cmds.select(neck)
    stage.splineStage(4)
    ##assemble
    OptAttr(neckAttr, 'NeckSpline')
    cmds.parentConstraint(neckPrnt, neckName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(neckStrt, neckName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(neckEnd, neckName + '_E_IK_PrntGrp')
    misc.hijackCustomAttrs(neckName + '_IK_CtrlGrp', neckAttr)
    ##set options
    cmds.setAttr(neckAttr + '.' + neckName + 'Vis', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Root', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Stretch', 0)
    cmds.setAttr(neckAttr + '.ClstrVis', 0)
    cmds.setAttr(neckAttr + '.ClstrMidIkBlend', 1)
    cmds.setAttr(neckAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrVis', 0)
    cmds.setAttr(neckAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(neckAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(neckAttr+ '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(neckName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(neckName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    
    #EARS
    if cmds.objExists('root_ear_jnt_L') == True:
        spine = splnFk.SplineFK('ear_rig_L','root_ear_jnt_L','ear_04_jnt_L', 'L', rootParent='neck_jnt_06', parent1='neck_jnt_06', controllerSize=X*8)
        spine = splnFk.SplineFK('ear_rig_R','root_ear_jnt_R','ear_04_jnt_R', 'R', rootParent='neck_jnt_06', parent1='neck_jnt_06', controllerSize=X*8)
