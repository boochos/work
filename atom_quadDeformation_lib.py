import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc
from atom import atom_splineStage_lib as stage
import atom_body_lib as abl
def quadDeform(*args):
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
		parentIn = ['Back_limb_rot_grp_L', 'Back_limb_rot_grp_R', 'Front_limb_rot_grp_L', 'Front_limb_rot_grp_R']
		padAttach = ['back_paw_Fk_jnt_L', 'back_paw_Fk_jnt_R', 'front_paw_Fk_jnt_L', 'front_paw_Fk_jnt_R']
		prefix    = ['Back', 'Back', 'Front', 'Front']
		suffix    = ['L', 'R', 'L', 'R']
		X_roll    = ['Back_ball_roll_ctrl_L', 'Back_ball_roll_ctrl_R', 'Front_ball_roll_ctrl_L', 'Front_ball_roll_ctrl_R']
		X_fk      = ['Back_paw_fk_ctrl_L', 'Back_paw_fk_ctrl_R', 'Front_paw_fk_ctrl_L', 'Front_paw_fk_ctrl_R']
		padName   = ['backPad_L', 'backPad_R', 'frontPad_L', 'frontPad_R']
		padPrnt   = ['back_ankle_jnt_L', 'back_ankle_jnt_R', 'front_ankle_jnt_L', 'front_ankle_jnt_R']
		padStrt   = ['back_ankle_jnt_L', 'back_ankle_jnt_R', 'front_ankle_jnt_L', 'front_ankle_jnt_R']
		padJnt    = ['back_pad_jnt_02_L', 'back_pad_jnt_02_R', 'front_pad_jnt_02_L', 'front_pad_jnt_02_R']
		padSplineCnst   = ['back_splinePad_jnt_05_L', 'back_splinePad_jnt_05_R', 'front_splinePad_jnt_05_L', 'front_splinePad_jnt_05_R']
		padSplineJnt    = [['back_splinePad_jnt_01_L','back_splinePad_jnt_05_L'],
		                   ['back_splinePad_jnt_01_R','back_splinePad_jnt_05_R'],
		                   ['front_splinePad_jnt_01_L','front_splinePad_jnt_05_L'],
		                   ['front_splinePad_jnt_01_R','front_splinePad_jnt_05_R']]
		padAttr   =  ['backPad_L', 'backPad_R', 'frontPad_L', 'frontPad_R']
		padVis    =  ['back_paw_L', 'back_paw_R', 'front_paw_L', 'front_paw_R']
		padSize     = X*4.0
		padDistance = X*3.0
		padFalloff  = 0
		i           = 0

		'''
		###possibly connect translates of all these objects to "Front_ball_roll_ctrl_L" control
		#Front_digit_1_roll_grp_L
		#Front_digit_2_roll_grp_L
		#Front_digit_3_roll_grp_L
		#Front_digit_4_roll_grp_L
		#Front_ankleIkParent_grp_L
		#Front_ankle_aim_loc_L
		'''

		while i <= 3:
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
		abdomenPrnt = 'pelvis_jnt'
		##abdomenStrt = 'pelvis_jnt'
		abdomenEnd  = 'spine_jnt_06'
		abdomenAttr = 'abdomen'
		abdomen     = ['abdomen_jnt_01', 'abdomen_jnt_05']
		##build controller
		ab      = place.Controller(abdomenName, abdomen[0], True, 'facetXup_ctrl', X*8, 12, 8, 1, (0,0,1), True, True)
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
		cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
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
	sst      = place.Controller(SSTName, SST[0], True, 'facetXup_ctrl', X*6, 12, 8, 1, (0,0,1), True, True)
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
	lc      = place.Controller(LCName, LC[0], True, 'facetXup_ctrl', X*6, 12, 8, 1, (0,0,1), True, True)
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
		scm      = place.Controller(SCMName, SCM[0], True, 'facetXup_ctrl', X*6, 12, 8, 1, (0,0,1), True, True)
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
		scm_L    = place.Controller(SCM_L_Name, SCM_L[0], True, 'facetXup_ctrl', X*6, 12, 8, 1, (0,0,1), True, True)
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
		scm_R    = place.Controller(SCM_R_Name, SCM_R[0], True, 'facetXup_ctrl', X*6, 12, 8, 1, (0,0,1), True, True)
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
		st      = place.Controller(STName, ST[0], True, 'facetXup_ctrl', X*13, 12, 8, 1, (0,0,1), True, True)
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
		cc_l   = place.Controller(CC_LName, CC_L[0], True, 'facetXup_ctrl', X*10, 12, 8, 1, (0,0,1), True, True)
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
		cc_r   = place.Controller(CC_RName, CC_R[0], True, 'facetXup_ctrl', X*10, 12, 8, 1, (0,0,1), True, True)
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
	#Check for any corrective blendshapes
	abl.buildCorrectiveBody()