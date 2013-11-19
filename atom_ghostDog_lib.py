from pymel.core import *
import maya.cmds as cmds
import atom_appendage_lib as aal
import atom_ui_lib as aul
import atom_placement_lib as place
import atom_miscellaneous_lib as misc
import atom_splineStage_lib as stage
import atom_joint_lib as ajl
import atom_earRig_lib as ael
import atom_splineFk_lib as splnFk
import atom_deformer_lib as adl
def deform(*args):
    '''\n
    Creates deformation splines for quad rig.\n
    paw pad\n
    neck\n
    belly\n
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

    ##deformation opt attr
    OptAttr('cog', 'DeformationVis')

    ##build defomers
    if face == False:
        #PADS
        parentIn = ['Front_limb_rot_grp_L', 'Front_limb_rot_grp_R']
        padAttach = ['front_paw_Fk_jnt_L', 'front_paw_Fk_jnt_R']
        prefix    = ['Front', 'Front']
        suffix    = ['L', 'R']
        X_roll    = ['Front_ball_roll_ctrl_L', 'Front_ball_roll_ctrl_R']
        X_fk      = ['Front_paw_fk_ctrl_L', 'Front_paw_fk_ctrl_R']
        padName   = ['frontPad_L', 'frontPad_R']
        padPrnt   = ['front_wrist_jnt_L', 'front_wrist_jnt_R']
        padStrt   = ['front_wrist_jnt_L', 'front_wrist_jnt_R']
        padJnt    = ['front_pad_jnt_02_L', 'front_pad_jnt_02_R']
        padSplineCnst   = ['front_splinePad_jnt_05_L', 'front_splinePad_jnt_05_R']
        padSplineJnt    = [['front_splinePad_jnt_01_L','front_splinePad_jnt_05_L'],
                           ['front_splinePad_jnt_01_R','front_splinePad_jnt_05_R']]
        padAttr   =  ['frontPad_L', 'frontPad_R']
        padVis    =  ['front_paw_L', 'front_paw_R']
        padSize     = X*4.0
        padDistance = X*3.0
        padFalloff  = 0
        i           = 0

        while i <= 1:
            ##create sudo-metacarpal groups
            parent    = place.null2(prefix[i] + '_pad_ctrl_grp_' + suffix[i], padAttach[i], False)[0]
            roll      = place.null2(prefix[i] + '_pad_roll_grp_' + suffix[i], padAttach[i], False)[0]
            pivot     = place.null2(prefix[i] + '_pad_base_pivot_grp_' + suffix[i], padAttach[i], False)[0]
            ctrlGp    = place.null2(prefix[i] + '_pad_ctrlGp_' + suffix[i], padJnt[i], True)[0]
            ctrl      = place.circle(prefix[i] + '_pad_ctrl_' + suffix[i], padJnt[i], 'loc_ctrl', padSize, 17)[0]
            cnst      = place.null2(prefix[i] + '_pad_cnst_grp_' + suffix[i], padAttach[i], False)[0]
            cmds.parent(cnst, ctrl)
            cmds.parent(ctrl, ctrlGp)
            cmds.parent(ctrlGp, pivot)
            cmds.parent(pivot, roll)
            cmds.parent(roll, parent)
            cmds.parent(parent, parentIn[i])
            cmds.pointConstraint(padAttach[i], parent, mo=True)
            cmds.connectAttr(X_roll[i] + '.rotateX', roll + '.rotateX')
            cmds.connectAttr(X_fk[i] + '.rotateX', pivot + '.rotateX')

            cmds.parentConstraint(ctrl, padJnt[i], mo=True)
            cmds.connectAttr(padVis[i] + '.Pad', ctrl + '.visibility')
            misc.setChannels(ctrl, [False, True], [False, True], [True, False], [True, True,False], [True,True] )
            i = i + 1

    #ABDOMEN
    abdomenName = 'abdomen'
    abdomenSize     = X*0.5
    abdomenDistance = X*3.0
    abdomenFalloff  = 0
    abdomenPrnt = 'spine_jnt_05'
    ##abdomenStrt = 'pelvis_jnt'
    abdomenEnd  = 'tail_jnt_02'
    abdomenAttr = 'abdomen'
    abdomen     = ['abdomen_jnt_01', 'abdomen_jnt_07']
    ##build controller
    ab      = place.Controller(abdomenName, abdomen[0], True, 'facetXup_ctrl', X*16, 12, 8, 1, (0,0,1), True, True)
    AbCt = ab.createController()
    cmds.parentConstraint(abdomenPrnt, AbCt[0], mo=True)
    ##build spline
    SplineOpts(abdomenName, abdomenSize, abdomenDistance, abdomenFalloff)
    cmds.select(abdomen)
    stage.splineStage(4)
    ##assemble
    cmds.parentConstraint(AbCt[4], abdomenName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(AbCt[4], abdomenName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(abdomenEnd, abdomenName + '_E_IK_PrntGrp', mo=True)
    ##set options
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Vis', 0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Root', 0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Stretch', 1)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrVis', 0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrMidIkBlend', .25)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrVis', 0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidIkBlend', .25)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
    cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(abdomenName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(abdomenName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    ##attrs
    OptAttr(abdomenAttr, 'AbdomenSpline')
    misc.hijackCustomAttrs(abdomenName + '_IK_CtrlGrp', AbCt[2])
    misc.hijackVis(AbCt[2], 'cog', name='abdomen', default=None, suffix=False)
    ##cleanup
    misc.cleanUp(AbCt[0], Ctrl=True)


    #SEMISPINALESTHORACIS
    SSTName = 'SST'
    SSTSize     = X*0.5
    SSTDistance = X*3.0
    SSTFalloff  = 0
    SSTPrnt = 'spine_jnt_06'
    ##SSTStrt = 'spine_jnt_06'
    SSTEnd  = 'neck_jnt_03'
    SSTAttr = 'SST'
    SST     = ['semispinalesThoracis_jnt_01', 'semispinalesThoracis_jnt_05']
    ##build controller
    sst      = place.Controller(SSTName, SST[0], True, 'facetXup_ctrl', X*12, 12, 8, 1, (0,0,1), True, True)
    sstCt = sst.createController()
    cmds.parentConstraint(SSTPrnt, sstCt[0], mo=True)
    ##build spline
    SplineOpts(SSTName, SSTSize, SSTDistance, SSTFalloff)
    cmds.select(SST)
    stage.splineStage(4)
    ##assemble
    cmds.parentConstraint(sstCt[4], SSTName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(sstCt[4], SSTName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(SSTEnd, SSTName + '_E_IK_PrntGrp', mo=True)
    ##set options
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Vis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Root', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Stretch', 1)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrVis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrVis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(SSTName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(SSTName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    ##attrs
    OptAttr(sstCt[2], 'SSTSpline')
    misc.hijackCustomAttrs(SSTName + '_IK_CtrlGrp', sstCt[2])
    misc.hijackVis(sstCt[2], 'cog', name='semispinalesThoracis', default=None, suffix=False)
    ##cleanup
    misc.cleanUp(sstCt[0], Ctrl=True)

    #LONGISSIMUSCAPITIS
    LCName = 'LC'
    LCSize     = X*0.5
    LCDistance = X*3.0
    LCFalloff  = 0
    LCPrnt = 'semispinalesThoracis_jnt_03'
    ##LCStrt = 'semispinalesThoracis_jnt_03'
    LCEnd  = 'neck_jnt_06'
    LCAttr = 'LC'
    LC     = ['longissimusCapitis_jnt_01', 'longissimusCapitis_jnt_05']
    ##build controller
    lc      = place.Controller(LCName, LC[0], True, 'facetXup_ctrl', X*12, 12, 8, 1, (0,0,1), True, True)
    lcCt = lc.createController()
    cmds.parentConstraint(LCPrnt, lcCt[0], mo=True)
    ##build spline
    SplineOpts(LCName, LCSize, LCDistance, LCFalloff)
    cmds.select(LC)
    stage.splineStage(4)
    ##assemble
    cmds.parentConstraint(lcCt[4], LCName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(lcCt[4], LCName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(LCEnd, LCName + '_E_IK_PrntGrp', mo=True)
    ##set options
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Vis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Root', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Stretch', 1)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrVis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrVis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(LCName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(LCName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    ##attrs
    OptAttr(lcCt[2], 'LCSpline')
    misc.hijackCustomAttrs(LCName + '_IK_CtrlGrp', lcCt[2])
    misc.hijackVis(lcCt[2], 'cog', name='longissimusCapitis', default=None, suffix=False)
    ##cleanup
    misc.cleanUp(lcCt[0], Ctrl=True)

    #STERNOCLEIDOMASTOID
    if cmds.objExists('sternocleidomastoid_jnt_01'):
        SCMName = 'SCM'
        SCMSize     = X*0.5
        SCMDistance = X*3.0
        SCMFalloff  = 0
        SCMPrnt = 'neck_jnt_02'
        ##SCMStrt = 'neck_jnt_02'
        SCMEnd  = 'neck_jnt_06'
        SCMAttr = 'SCM'
        SCM     = ['sternocleidomastoid_jnt_01', 'sternocleidomastoid_jnt_05']
        ##build controller
        scm      = place.Controller(SCMName, SCM[0], True, 'facetXup_ctrl', X*12, 12, 8, 1, (0,0,1), True, True)
        scmCt = scm.createController()
        cmds.parentConstraint(SCMPrnt, scmCt[0], mo=True)
        ##build spline
        SplineOpts(SCMName, SCMSize, SCMDistance, SCMFalloff)
        cmds.select(SCM)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(scmCt[4], SCMName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scmCt[4], SCMName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCMEnd, SCMName + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Vis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Root', 1)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Stretch', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCMName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCMName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##attrs
        OptAttr(scmCt[2], 'SCMSpline')
        misc.hijackCustomAttrs(SCMName + '_IK_CtrlGrp', scmCt[2])
        misc.hijackVis(scmCt[2], 'cog', name='sternocleidomastoid', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(scmCt[0], Ctrl=True)

    ###
        #STERNOCLEIDOMASTOID_L
    if cmds.objExists('sternocleidomastoid_jnt_01_L'):
        SCM_L_Name = 'SCM_L'
        SCM_L_Size     = X*0.5
        SCM_L_Distance = X*3.0
        SCM_L_Falloff  = 0
        SCM_L_Prnt = 'spine_jnt_06'
        ##SCM_L_Strt = 'neck_jnt_02'
        SCM_L_End  = 'neck_jnt_06'
        SCM_L_Attr = 'SCM_L'
        SCM_L      = ['sternocleidomastoid_jnt_01_L', 'sternocleidomastoid_jnt_05_L']
        ##build controller
        scm_L    = place.Controller(SCM_L_Name, SCM_L[0], True, 'facetXup_ctrl', X*12, 12, 8, 1, (0,0,1), True, True)
        scm_L_Ct = scm_L.createController()
        cmds.parentConstraint(SCM_L_Prnt, scm_L_Ct[0], mo=True)
        ##build spline
        SplineOpts(SCM_L_Name, SCM_L_Size, SCM_L_Distance, SCM_L_Falloff)
        cmds.select(SCM_L)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(scm_L_Ct[4], SCM_L_Name + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scm_L_Ct[4], SCM_L_Name + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCM_L_End, SCM_L_Name + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Vis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Root', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Stretch', 1)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCM_L_Name + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCM_L_Name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##attrs
        OptAttr(scm_L_Ct[2], 'SCM_L_Spline')
        misc.hijackCustomAttrs(SCM_L_Name + '_IK_CtrlGrp', scm_L_Ct[2])
        misc.hijackVis(scm_L_Ct[2], 'cog', name='sternocleidomastoid_L', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(scm_L_Ct[0], Ctrl=True)
    ###

    #STERNOCLEIDOMASTOID_R
    if cmds.objExists('sternocleidomastoid_jnt_01_R'):
        SCM_R_Name = 'SCM_R'
        SCM_R_Size     = X*0.5
        SCM_R_Distance = X*3.0
        SCM_R_Falloff  = 0
        SCM_R_Prnt = 'spine_jnt_06'
        ##SCM_R_Strt = 'neck_jnt_02'
        SCM_R_End  = 'neck_jnt_06'
        SCM_R_Attr = 'SCM_R'
        SCM_R      = ['sternocleidomastoid_jnt_01_R', 'sternocleidomastoid_jnt_05_R']
        ##build controller
        scm_R    = place.Controller(SCM_R_Name, SCM_R[0], True, 'facetXup_ctrl', X*12, 12, 8, 1, (0,0,1), True, True)
        scm_R_Ct = scm_R.createController()
        cmds.parentConstraint(SCM_R_Prnt, scm_R_Ct[0], mo=True)
        ##build spline
        SplineOpts(SCM_R_Name, SCM_R_Size, SCM_R_Distance, SCM_R_Falloff)
        cmds.select(SCM_R)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(scm_R_Ct[4], SCM_R_Name + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scm_R_Ct[4], SCM_R_Name + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCM_R_End, SCM_R_Name + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Vis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Root', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Stretch', 1)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCM_R_Name + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCM_R_Name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##attrs
        OptAttr(scm_R_Ct[2], 'SCM_R_Spline')
        misc.hijackCustomAttrs(SCM_R_Name + '_IK_CtrlGrp', scm_R_Ct[2])
        misc.hijackVis(scm_R_Ct[2], 'cog', name='sternocleidomastoid_R', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(scm_R_Ct[0], Ctrl=True)

    #STERNALTHYROID
    if cmds.objExists('sternalThyroid_jnt_01'):
        STName = 'ST'
        STSize     = X*0.5
        STDistance = X*3.0
        STFalloff  = 0
        STPrnt = 'spine_jnt_06'
        ##STStrt = 'spine_jnt_06'
        STEnd  = 'sternocleidomastoid_jnt_03'
        STAttr = 'ST'
        ST     = ['sternalThyroid_jnt_01', 'sternalThyroid_jnt_05']
        ##build controller
        st      = place.Controller(STName, ST[0], True, 'facetXup_ctrl', X*26, 12, 8, 1, (0,0,1), True, True)
        stCt = st.createController()
        cmds.parentConstraint(STPrnt, stCt[0], mo=True)
        ##build spline
        SplineOpts(STName, STSize, STDistance, STFalloff)
        cmds.select(ST)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(stCt[4], STName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(stCt[4], STName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(STEnd, STName + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Vis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Root', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Stretch', 1)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(STName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(STName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##attrs
        OptAttr(stCt[2], 'STSpline')
        misc.hijackCustomAttrs(STName + '_IK_CtrlGrp', stCt[2])
        misc.hijackVis(stCt[2], 'cog', name='sternalThyroid', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(stCt[0], Ctrl=True)

    #CLEIDOCERVICALIS_L
    if cmds.objExists('cleidocervicalis_jnt_01_L'):
        CC_LName = 'CC_L'
        CC_LSize     = X*0.5
        CC_LDistance = X*3.0
        CC_LFalloff  = 0
        if cmds.objExists('scapula_jnt_02_L'):
            CC_LPrnt = 'scapula_jnt_02_L'
        else:
            CC_LPrnt = 'spine_jnt_06'
        ##CC_LStrt = 'spine_jnt_06'
        CC_LEnd  = 'neck_jnt_06'
        CC_LAttr = 'CC_L'
        CC_L     = ['cleidocervicalis_jnt_01_L', 'cleidocervicalis_jnt_05_L']
        ##build controller
        cc_l   = place.Controller(CC_LName, CC_L[0], True, 'facetXup_ctrl', X*20, 12, 8, 1, (0,0,1), True, True)
        cc_lCt = cc_l.createController()
        cmds.parentConstraint(CC_LPrnt, cc_lCt[0], mo=True)
        ##build spline
        SplineOpts(CC_LName, CC_LSize, CC_LDistance, CC_LFalloff)
        cmds.select(CC_L)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(cc_lCt[4], CC_LName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(cc_lCt[4], CC_LName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(CC_LEnd, CC_LName + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Vis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Root', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Stretch', 1)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.25)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.25)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(CC_LName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(CC_LName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##attrs
        OptAttr(cc_lCt[2], 'CC_LSpline')
        misc.hijackCustomAttrs(CC_LName + '_IK_CtrlGrp', cc_lCt[2])
        misc.hijackVis(cc_lCt[2], 'cog', name='cleidocervicalisL', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(cc_lCt[0], Ctrl=True)

    #CLEIDOCERVICALIS_R
    if cmds.objExists('cleidocervicalis_jnt_01_R'):
        CC_RName = 'CC_R'
        CC_RSize     = X*0.5
        CC_RDistance = X*3.0
        CC_RFalloff  = 0
        if cmds.objExists('scapula_jnt_02_R'):
            CC_RPrnt = 'scapula_jnt_02_R'
        else:
            CC_RPrnt = 'spine_jnt_06'
        ##CC_RStrt = 'spine_jnt_06'
        CC_REnd  = 'neck_jnt_06'
        CC_RAttr = 'CC_R'
        CC_R     = ['cleidocervicalis_jnt_01_R', 'cleidocervicalis_jnt_05_R']
        ##build controller
        cc_r   = place.Controller(CC_RName, CC_R[0], True, 'facetXup_ctrl', X*20, 12, 8, 1, (0,0,1), True, True)
        cc_rCt = cc_r.createController()
        cmds.parentConstraint(CC_RPrnt, cc_rCt[0], mo=True)
        ##build spline
        SplineOpts(CC_RName, CC_RSize, CC_RDistance, CC_RFalloff)
        cmds.select(CC_R)
        stage.splineStage(4)
        ##assemble
        cmds.parentConstraint(cc_rCt[4], CC_RName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(cc_rCt[4], CC_RName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(CC_REnd, CC_RName + '_E_IK_PrntGrp', mo=True)
        ##set options
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Vis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Root', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Stretch', 1)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.25)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.25)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(CC_RName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(CC_RName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##
        OptAttr(cc_rCt[2], 'CC_RSpline')
        misc.hijackCustomAttrs(CC_RName + '_IK_CtrlGrp', cc_rCt[2])
        misc.hijackVis(cc_rCt[2], 'cog', name='cleidocervicalisR', default=None, suffix=False)
        ##cleanup
        misc.cleanUp(cc_rCt[0], Ctrl=True)

def buildGostDogAppendages(*args):
    origVal =  cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', query=True, v2=True)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5)
    
    #front left arm
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_L')
    cmds.select('shldr_L',      toggle=True)
    cmds.select('front_paw_L', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=3 )
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=5)
    aal.createReverseLeg(traversDepth=3)
    aal.createVerticalScapRig('front_shoulder_jnt_L','front_shoulder_dbl_jnt_L', 'shldr_L_Grp', 'scapula_jnt_01_L','shldr_L','spine_jnt_06','_L')
    aal.createClavicleRig('clavicle_01_jnt_L','front_shoulder_jnt_L','spine_jnt_07', '_L',[0,0,1],[0,1,0])
    misc.cleanUp('Front_knee_pv_grp_L', Ctrl=True)
    misc.cleanUp('Front_auto_ankle_parent_grp_L', Ctrl=True)
    misc.cleanUp('Front_limb_ctrl_grp_L', Ctrl=True)
    ajl.RigTwistJoint('front_paw_L',['forarm_twist_01_jnt_L','forarm_twist_02_jnt_L'],'forarm', '_L', 'Z','Z')
    ##setjoint attrs for front left
    ##finger ik limits
    cmds.transformLimits('front_mid_phal_jnt_01_L', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_02_L', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_03_L', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_04_L', rx=(-27, 37), erx=(1, 1))
    ##arm limit/dampening
    cmds.transformLimits('front_upper_elbow_jnt_L', rx=(-180, 180), erx=(1, 1))
    cmds.setAttr('front_upper_elbow_jnt_L.maxRotateDampRangeX', 45)
    cmds.setAttr('front_upper_elbow_jnt_L.minRotateDampStrengthX', 25)
    cmds.setAttr('front_upper_elbow_jnt_L.maxRotateDampStrengthX', 75)
    
    
    
    #front right arm
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_R')
    cmds.select('shldr_R',     toggle=True)
    cmds.select('front_paw_R', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=4 )
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    aal.createReverseLeg(traversDepth=3)    
    aal.createVerticalScapRig('front_shoulder_jnt_R', 'front_shoulder_dbl_jnt_R', 'shldr_R_Grp', 'scapula_jnt_01_R','shldr_R','spine_jnt_06','_R')
    aal.createClavicleRig('clavicle_01_jnt_R','front_shoulder_jnt_R','spine_jnt_07', '_R',[0,0,1],[0,1,0])
    ajl.RigTwistJoint('front_paw_R',['forarm_twist_01_jnt_R','forarm_twist_02_jnt_R'],'forarm', '_R', 'Z','Z',twistDirection=-1)
    misc.cleanUp('Front_knee_pv_grp_R', Ctrl=True)
    misc.cleanUp('Front_auto_ankle_parent_grp_R', Ctrl=True)
    misc.cleanUp('Front_limb_ctrl_grp_R', Ctrl=True)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=origVal)
    ##setjoint attrs for front left
    ##finger ik limits
    cmds.transformLimits('front_mid_phal_jnt_01_R', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_02_R', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_03_R', rx=(-27, 37), erx=(1, 1))
    cmds.transformLimits('front_mid_phal_jnt_04_R', rx=(-27, 37), erx=(1, 1))
    ##arm limit/dampening
    cmds.transformLimits('front_upper_elbow_jnt_R', rx=(-180, 180), erx=(1, 1))
    cmds.setAttr('front_upper_elbow_jnt_R.maxRotateDampRangeX', 45)
    cmds.setAttr('front_upper_elbow_jnt_R.minRotateDampStrengthX', 25)
    cmds.setAttr('front_upper_elbow_jnt_R.maxRotateDampStrengthX', 75)

     
def ghostDogPreBuild(
    COG_jnt= 'spine_jnt_01', PELVIS_jnt= 'tail_jnt_01', CHEST_jnt= 'spine_jnt_06', NECK_jnt= 'neck_jnt_01', HEAD_jnt= 'neck_jnt_06', 
    SHLDR_L_jnt= 'front_shoulder_jnt_L', SHLDR_R_jnt= 'front_shoulder_jnt_R', 
    FRONT_L_jnt= 'front_foot_ctrl_placement_jnt_L', FRONT_R_jnt= 'front_foot_ctrl_placement_jnt_R', 
    TAIL_jnt= 'tail_jnt_01', TAILTIP_jnt= 'tail_jnt_011', GEO_gp= 'buddy_GP', SKIN_jnt= 'root_jnt'):

    current_scale = cmds.floatField('atom_qrig_conScale',q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=1.0)
    
    face=None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X     = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    if check == 0:
        face   = False
    else:
        face=True

    PreBuild    = misc.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=110)
    CHARACTER   = PreBuild[0]
    CONTROLS    = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO         = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt    = PreBuild[5]

    cmds.parent(SKIN_jnt, SKIN_JOINTS)
    #cmds.parent(GEO_gp, GEO)

    # COG #
    Cog   = 'cog'
    cog   = place.Controller(Cog, COG_jnt, False, 'facetXup_ctrl', X*40, 12, 8, 1, (0,0,1), True, True)
    CogCt = cog.createController()
    misc.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # PELVIS/CHEST #
    ## PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, True, 'facetZup_ctrl', X*50, 17, 8, 1, (0,0,1), True, True)
    PelvisCt = pelvis.createController()
    misc.setRotOrder(PelvisCt[0], 2, True)
    if cmds.objExists(TAIL_jnt):
        PelvisAttch_Gp = place.null2('PelvisAttch_Gp', TAIL_jnt)[0]
        PelvisAttch_CnstGp = place.null2('PelvisAttch_CnstGp', TAIL_jnt)[0]
        cmds.parent(PelvisAttch_CnstGp, PelvisAttch_Gp)
        misc.setRotOrder(PelvisAttch_CnstGp, 2, False)
        cmds.parentConstraint(PELVIS_jnt,PelvisAttch_Gp, mo=True)
        cmds.parent(PelvisAttch_Gp, PelvisCt[0])


    ## CHEST ##
    Chest   = 'chest'
    chest   = place.Controller(Chest, CHEST_jnt, False, 'GDchest_ctrl', X*3.5, 17, 8, 1, (0,0,1), True, True)
    ChestCt = chest.createController()
    misc.setRotOrder(ChestCt[0], 2, True)
    ## GROUP for shoulder joints, neck ##
    ChestAttch_Gp = place.null2('ChestAttch_Gp', NECK_jnt)[0]
    ChestAttch_CnstGp = place.null2('ChestAttch_CnstGp', NECK_jnt)[0]
    cmds.parent(ChestAttch_CnstGp, ChestAttch_Gp)
    misc.setRotOrder(ChestAttch_CnstGp, 2, False)
    cmds.parentConstraint(CHEST_jnt,ChestAttch_Gp, mo=True)
    cmds.parent(ChestAttch_Gp, PelvisCt[0])
    ##constrain controllers, parent under Master group
    cmds.parentConstraint(CogCt[4], PelvisCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], ChestCt[0], mo=True)
    ##setChannels
    misc.setChannels(PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False])
    ##misc.setChannels(PelvisCt[3], [False, True], [False, True], [True, False], [False, False, False])
    misc.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
    misc.setChannels(ChestCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(ChestCt[1], [True, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(ChestCt[2], [False, True], [False, True], [True, False], [True, False, False])
    ##misc.setChannels(ChestCt[3], [False, True], [False, True], [True, False], [False, False, False])
    misc.setChannels(ChestCt[4], [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(PelvisCt[0], CONTROLS)
    cmds.parent(ChestCt[0], CONTROLS)

    # NECK #
    Neck   = 'neck'
    neck   = place.Controller(Neck, NECK_jnt, True, 'GDneck_ctrl', X*3.5, 12, 8, 1, (0,0,1), True, True)
    NeckCt = neck.createController()
    misc.setRotOrder(NeckCt[0], 2, True)
    ##parent switches
    misc.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], ChestAttch_CnstGp, False, True, False, True, 'Chest')
    cmds.parentConstraint(ChestAttch_CnstGp, NeckCt[0], mo=True)
    misc.setChannels(NeckCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[1], [True, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[2], [True, False], [False, True], [True, False], [True, False, False])
    misc.setChannels(NeckCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(NeckCt[3] + '.visibility', cb=False)
    misc.setChannels(NeckCt[4], [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(NeckCt[0], CONTROLS)

    # HEAD #
    Head   = 'head'
    head   = place.Controller(Head, HEAD_jnt, False, 'GDhead_ctrl', X*3.5, 12, 8, 1, (0,0,1), True, True)
    HeadCt = head.createController()
    misc.setRotOrder(HeadCt[0], 2, True)
    ##parent switch
    misc.parentSwitch(Head, HeadCt[2], HeadCt[1], HeadCt[0], CogCt[4], NeckCt[4], False, False, True, True, 'Neck')
    ## insert group under Head, in the same space as Head_offset, name: Head_CnstGp
    Head_CnstGp = place.null2(Head + '_CnstGp', HEAD_jnt)[0]
    misc.setRotOrder(Head_CnstGp, 2, True)
    cmds.parent(Head_CnstGp, HeadCt[2])
    ##tip of head constrain to offset
    cmds.orientConstraint(HeadCt[3], 'neck_jnt_06', mo=True)
    ##constrain head to neck
    cmds.parentConstraint(NeckCt[4], HeadCt[0], mo=True)
    ##set channels
    misc.setChannels(HeadCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(HeadCt[1], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(HeadCt[2], [False, True], [False, True], [True, False], [True, False, False])
    misc.setChannels(HeadCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(HeadCt[3] + '.visibility', cb=False)
    misc.setChannels(HeadCt[4], [True, False], [True, False], [True, False], [True, False, False])
    misc.setChannels(Head_CnstGp, [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(HeadCt[0], CONTROLS)
    ##add extra group to 'HeadCt'
    HeadCt += (Head_CnstGp,)

    if face == False:
        # SHOULDER L #
        shldrL   = 'shldr_L'
        shldrL   = place.Controller(shldrL, SHLDR_L_jnt, False, 'shldrL_ctrl', X*10, 17, 8, 1, (0,0,1), True, True)
        ShldrLCt = shldrL.createController()
        misc.setRotOrder(ShldrLCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrLCt[0], mo=True)
        scapStrtchL = cmds.parentConstraint( ShldrLCt[4], 'front_shoulder_dbl_jnt_L', mo=True)[0]
        UsrAttrL = cmds.listAttr(scapStrtchL, ud=True)[0]
        cmds.addAttr(scapStrtchL + '.' + UsrAttrL, e=True, max=1)
        misc.hijackAttrs(scapStrtchL, ShldrLCt[2], UsrAttrL, 'ScapulaStretch', default=0)
        cmds.parent(ShldrLCt[0], CONTROLS)
        misc.setChannels(ShldrLCt[0], [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(ShldrLCt[1], [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(ShldrLCt[2], [False, True], [True, False], [True, False], [True, False, False])
        misc.setChannels(ShldrLCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrLCt[3] + '.visibility', cb=False)
        misc.setChannels(ShldrLCt[4], [True, False], [True, False], [True, False], [True, False, False])
        cmds.setAttr(ShldrLCt[2] + '.tx', l=True, k=False)
        cmds.setAttr(ShldrLCt[3] + '.tx', l=True, k=False)

        # SHOULDER R #
        shldrR   = 'shldr_R'
        shldrR   = place.Controller(shldrR, SHLDR_R_jnt, False, 'shldrR_ctrl', X*10, 17, 8, 1, (0,0,1), True, True)
        ShldrRCt = shldrR.createController()
        misc.setRotOrder(ShldrRCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrRCt[0], mo=True)
        scapStrtchR = cmds.parentConstraint( ShldrRCt[4], 'front_shoulder_dbl_jnt_R', mo=True)[0]
        UsrAttrR = cmds.listAttr(scapStrtchR, ud=True)[0]
        cmds.addAttr(scapStrtchR + '.' + UsrAttrR, e=True, max=1)
        misc.hijackAttrs(scapStrtchR, ShldrRCt[2], UsrAttrR, 'ScapulaStretch', default=0)
        cmds.parent(ShldrRCt[0], CONTROLS)
        misc.setChannels(ShldrRCt[0], [False, False], [False, False], [True, False], [True, False, False])
        misc.setChannels(ShldrRCt[1], [True, False], [True, False], [True, False], [True, False, False])
        misc.setChannels(ShldrRCt[2], [False, True], [True, False], [True, False], [True, False, False])
        misc.setChannels(ShldrRCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrRCt[3] + '.visibility', cb=False)
        misc.setChannels(ShldrRCt[4], [True, False], [True, False], [True, False], [True, False, False])
        cmds.setAttr(ShldrRCt[2] + '.tx', l=True, k=False)
        cmds.setAttr(ShldrRCt[3] + '.tx', l=True, k=False)

        # Attrs for paws
        attrVis  = ['Pivot', 'Pad', 'Fk', 'AnkleUp', 'BaseDigit', 'MidDigit', 'PvDigit']
        attrCstm = ['ToeRoll', 'HeelRoll', 'KneeTwist']
        vis      = 'Vis'
        assist   = 'Assist'

        # FRONT L  #
        PawFrntL   = 'front_paw_L'
        pawFrntL   = place.Controller(PawFrntL, FRONT_L_jnt, False, 'facetZup_ctrl', X*10, 12, 8, 1, (0,0,1), True, True)
        PawFrntLCt = pawFrntL.createController()
        cmds.parent(PawFrntLCt[0], CONTROLS)
        ##More parent group Options
        cmds.select(PawFrntLCt[0])
        PawFrntL_TopGrp2 = misc.insert('null', 1, PawFrntL + '_TopGrp2')[0][0]
        PawFrntL_CtGrp2  = misc.insert('null', 1, PawFrntL + '_CtGrp2')[0][0]
        PawFrntL_TopGrp1 = misc.insert('null', 1, PawFrntL + '_TopGrp1')[0][0]
        PawFrntL_CtGrp1  = misc.insert('null', 1, PawFrntL + '_CtGrp1')[0][0]
        ##set RotateOrders for new groups
        misc.setRotOrder(PawFrntL_TopGrp2, 2, True)
        ##attr
        misc.optEnum(PawFrntLCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawFrntLCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawFrntLCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawFrntLCt[2] + '.' + item), k=True)
        ##parentConstrain top group, switches
        cmds.parentConstraint(MasterCt[4], PawFrntL_TopGrp2, mo=True)
        misc.parentSwitch('PRNT2_' + PawFrntL, PawFrntLCt[2], PawFrntL_CtGrp2, PawFrntL_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        misc.parentSwitch('PRNT1_' + PawFrntL, PawFrntLCt[2], PawFrntL_CtGrp1, PawFrntL_TopGrp1, PawFrntL_CtGrp2, ChestCt[4], False, False, True, False, 'Chest', 0.0)
        misc.parentSwitch('PNT_' + PawFrntL, PawFrntLCt[2], PawFrntLCt[1], PawFrntLCt[0], PawFrntL_CtGrp1, ChestCt[4], True, False, False, False, 'Chest', 0.0)
        ##attrVis
        misc.optEnum(PawFrntLCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            misc.addAttribute(PawFrntLCt[2], item, 0, 1, False, 'long')	

        # FRONT R  #
        PawFrntR   = 'front_paw_R'
        pawFrntR   = place.Controller(PawFrntR, FRONT_R_jnt, False, 'facetZup_ctrl', X*10, 12, 8, 1, (0,0,1), True, True)
        PawFrntRCt = pawFrntR.createController()
        cmds.parent(PawFrntRCt[0], CONTROLS)
        ##More parent group Options
        cmds.select(PawFrntRCt[0])
        PawFrntR_TopGrp2 = misc.insert('null', 1, PawFrntR + '_TopGrp2')[0][0]
        PawFrntR_CtGrp2  = misc.insert('null', 1, PawFrntR + '_CtGrp2')[0][0]
        PawFrntR_TopGrp1 = misc.insert('null', 1, PawFrntR + '_TopGrp1')[0][0]
        PawFrntR_CtGrp1  = misc.insert('null', 1, PawFrntR + '_CtGrp1')[0][0]
        ##set RotateOrders for new groups
        misc.setRotOrder(PawFrntR_TopGrp2, 2, True)
        ##attr
        misc.optEnum(PawFrntRCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawFrntRCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawFrntRCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawFrntRCt[2] + '.' + item), k=True)
        ##parentConstrain top group, switches
        cmds.parentConstraint(MasterCt[4], PawFrntR_TopGrp2, mo=True)
        misc.parentSwitch('PRNT2_' + PawFrntR, PawFrntRCt[2], PawFrntR_CtGrp2, PawFrntR_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        misc.parentSwitch('PRNT1_' + PawFrntR, PawFrntRCt[2], PawFrntR_CtGrp1, PawFrntR_TopGrp1, PawFrntR_CtGrp2, ChestCt[4], False, False, True, False, 'Chest', 0.0)
        misc.parentSwitch('PNT_' + PawFrntR, PawFrntRCt[2], PawFrntRCt[1], PawFrntRCt[0], PawFrntR_CtGrp1, ChestCt[4], True, False, False, False, 'Chest', 0.0)
        ##attrVis
        misc.optEnum(PawFrntRCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            misc.addAttribute(PawFrntRCt[2], item, 0, 1, False, 'long')	

    if face == False:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt, ShldrLCt, ShldrRCt, PawFrntLCt, PawFrntRCt#, TailCt, TailTipCt
    else:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt
    
def buildGhostDogEars():
    earBase = None
    if not cmds.objExists('earRig_Grp'):
	earBase = place.null2('earRig_Grp', 'neck_jnt_06')[0]
	misc.setRotOrderWithXform(earBase, 'zxy', False)
	cmds.parent(earBase, 'neck_jnt_06')
    
    ear_template = '/Volumes/VFX/Projects/Spooky_Buddies/Assets/Development/Artist/spatapoff/CharactersWork/GhostDog/RIG/ear_rig/GhostDog_ear_template.mb'
     
    if os.path.exists(ear_template):
	importFile(ear_template)
	
    mid_chain_L   = adl.makeJointClone('mid_ear_01_jnt_L'  , 'mid_ear_master_jnt'  , suffix = 'L')   
    front_chain_L = adl.makeJointClone('front_ear_01_jnt_L', 'front_ear_master_jnt', suffix = 'L')
    back_chain_L  = adl.makeJointClone('back_ear_01_jnt_L' , 'back_ear_master_jnt' , suffix = 'L')

    ael.EarRig('mid_ear'  , 'mid_ear_master_jnt_01_L'  , 'mid_ear_master_jnt_10_L'  , earBase, None,
               'front_ear', 'front_ear_master_jnt_01_L', 'front_ear_master_jnt_10_L', earBase, 'make_parent_list',
               'back_ear' , 'back_ear_master_jnt_01_L' , 'back_ear_master_jnt_10_L' , earBase, 'make_parent_list',
               'L')
    
    mid_chain_L   = adl.makeJointClone('mid_ear_01_jnt_R'  , 'mid_ear_master_jnt'  , suffix = 'R')   
    front_chain_L = adl.makeJointClone('front_ear_01_jnt_R', 'front_ear_master_jnt', suffix = 'R')
    back_chain_L  = adl.makeJointClone('back_ear_01_jnt_R' , 'back_ear_master_jnt' , suffix = 'R')
    
    ael.EarRig('mid_ear'  , 'mid_ear_master_jnt_01_R'  , 'mid_ear_master_jnt_10_R'  , earBase, None,
               'front_ear', 'front_ear_master_jnt_01_R', 'front_ear_master_jnt_10_R', earBase, 'make_parent_list',
               'back_ear' , 'back_ear_master_jnt_01_R' , 'back_ear_master_jnt_10_R' , earBase, 'make_parent_list',
               'R')
    
    
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
	    tailRig = splnFk.SplineFK('tail','tailDbl_jnt', 'tail_jnt_011', 'mid', 
		                          controllerSize=20, parent1= 'pelvis_Grp', parent2='master_Grp', parentDefault=[1,0], stretch=0, ik='ik')
	    #tailRig.placeIkJnts()
	    for i in tailRig.topGrp2:
		misc.cleanUp(i, World=True)
	    #misc.cleanUp('tail_mid_UpVctrGdGrp', Ctrl=True)
	
	#SPINE
	spineName = 'spine'
	spineSize     = X*5
	spineDistance = X*8
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
	cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 0.25)
	cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0)
	cmds.setAttr(spineAttr + '.VctrVis', 0)
	cmds.setAttr(spineAttr + '.VctrMidIkBlend', .25)
	cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
	cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
	cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
	cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
	cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)
		
	#NECK
	neckName = 'neck'
	neckSize     = X*5
	neckDistance = X*7
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
	cmds.parentConstraint(neckPrnt, neckName + '_IK_CtrlGrp')
	cmds.parentConstraint(neckStrt, neckName + '_S_IK_PrntGrp')
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
	   
