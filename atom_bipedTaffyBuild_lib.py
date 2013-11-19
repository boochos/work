import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc
from atom import atom_appendage_lib as apg

def bipedTaffyBuild():
	'''\n
	still requires:
	-needs finger controls\n
	-geo\n
	-proper pole vectors\n
	-pivots for (heelRoll, toeRoll, FootMaster), current solution is sketchy
	
	'''
	# CORE
	SKIN_jnt         = 'jnt_COG'
	COG_jnt          = 'jnt_COG'
	PELVIS_jnt       = 'jnt_pelvis'
	CHEST1_jnt       = 'jnt_spine_02'
	CHEST2_jnt       = 'jnt_spine_03'
	CHEST3_jnt       = 'jnt_spine_04'
	NECK_jnt         = 'jnt_spine_07'
	HEAD_jnt         = 'jnt_head'
	GEO_gp           = 'Human_LowRez_humanCollider_Geo'
	# ARMS
	CLV_L_jnt        = 'jnt_clavicle_L'
	CLV_R_jnt        = 'jnt_clavicle_R'
	SHLDR_L_jnt      = 'jnt_shoulder_L'
	SHLDR_R_jnt      = 'jnt_shoulder_R'
	ELBOW_L_jnt      = 'jnt_elbow_L'
	ELBOW_R_jnt      = 'jnt_elbow_R'
	WRIST_L_jnt      = 'jnt_wrist_L'
	WRIST_R_jnt      = 'jnt_wrist_R'
	# LEG
	HIP_L_jnt        = 'jnt_femur_L'
	HIP_R_jnt        = 'jnt_femur_R'
	KNEE_L_jnt       = 'jnt_knee_L'
	KNEE_R_jnt       = 'jnt_knee_R'
	ANKLE_L_jnt      = 'jnt_ankle_L'
	ANKLE_R_jnt      = 'jnt_ankle_R'
	BALL_L_jnt       = 'jnt_ball_L'
	BALL_R_jnt       = 'jnt_ball_R'
	TOE_L_jnt        = 'jnt_end_L'
	TOE_R_jnt        = 'jnt_end_R'
	TOE_pivotL_jnt   = 'jnt_end_L'
	TOE_pivotR_jnt   = 'jnt_end_R'
	HEEL_pivotL_jnt  = ''
	HEEL_pivotR_jnt  = ''
	FOOT_pivotL_jnt  = 'jnt_ball_L'
	FOOT_pivotR_jnt  = 'jnt_ball_R'
	
	def atomOpts(name='leg', limbName=4, size=1.0, distance=20, suffix=1, flip=[0,0,0], rot=1, aim=2, up=3):
		cmds.textField('atom_prefix_textField', e=True, tx=name)
		cmds.floatField('atom_bls_scale_floatField', e=True, v=size)
		cmds.floatField('atom_bls_ldf_floatField', e=True, v=distance)
		cmds.optionMenu('atom_bls_limb_optionMenu', e=True, sl=limbName)
		cmds.optionMenu('atom_suffix_optionMenu', e=True, sl=suffix)
		cmds.checkBoxGrp('atom_bls_flip_checkBoxGrp', e=True, va3=flip)
		cmds.radioButtonGrp('atom_bls_limbRot_radioButtonGrp', e=True, sl=rot)
		cmds.radioButtonGrp('atom_bls_limbAim_radioButtonGrp', e=True, sl=aim)
		cmds.radioButtonGrp('atom_bls_limbUp_radioButtonGrp', e=True, sl=up)
	def placePV(femur):
		cmds.select(femur)
		pv = apg.create3jointIK('atom_bls_setChannel_checkBox')
		return pv
		

	# --- PREBUILD ---#
	#
	# CHARACTER #
	CHARACTER = cmds.group(em=True, n='___CHARACTER___')
	misc.setChannels(CHARACTER, [True, False], [True, False], [True, False], [True, False, False])
	
	# CONTROLS #
	CONTROLS = cmds.group(em=True, n='___CONTROLS')
	cmds.parent(CONTROLS, CHARACTER)
	misc.setChannels(CONTROLS, [True, False], [True, False], [True, False], [True, False, False])
	
	# SKIN_JOINTS #
	SKIN_JOINTS = cmds.group(em=True, n='___SKIN_JOINTS')
	cmds.parent(SKIN_JOINTS, CHARACTER)
	misc.setChannels(SKIN_JOINTS, [True, False], [True, False], [True, False], [True, False, False])
	cmds.parent(SKIN_jnt, SKIN_JOINTS)

	# GEO #
	GEO = cmds.group(em=True, n='___GEO')
	cmds.parent(GEO, CHARACTER)
	misc.setChannels(GEO, [True, False], [True, False], [True, False], [True, False, False])
	cmds.parent(GEO_gp, GEO)

	# WORLD #
	WORLD_SPACE = cmds.group(em=True, n='___WORLD_SPACE')
	cmds.parent(WORLD_SPACE, CHARACTER)
	misc.setChannels(WORLD_SPACE, [True, False], [True, False], [True, False], [True, False, False])
	
	# MASTER #
	Master    = 'master'
	ScaleGrp  = cmds.group(n='ScaleGrp', em=True)
	master    = place.Controller(Master, ScaleGrp, False, 'facetYup_ctrl', 170, 12, 8, 1, (0,1,0), True, True)
	MasterCt  = master.createController()
	misc.setRotOrder(MasterCt[2], 2, False)
	cmds.parent(ScaleGrp, CONTROLS)
	misc.hijackScale(COG_jnt, MasterCt[2])
	cmds.parent(MasterCt[0], CONTROLS)
	misc.setChannels(MasterCt[0], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(MasterCt[1], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(MasterCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(MasterCt[3], [False, True], [False, True], [True, False], [False, False, True])
	misc.setChannels(MasterCt[4], [False, True], [False, True], [True, False], [True, False, True])	
	
	# --- CORE ---#
	#
	# COG #
	Cog   = 'cog'
	cog   = place.Controller(Cog, COG_jnt, False, 'facetYup_ctrl', 110, 12, 8, 1, (0,0,1), True, True)
	CogCt = cog.createController()
	misc.setRotOrder(CogCt[2], 2, False)
	#cmds.parent(CogCt[0], ScaleGrp)
	cmds.parent(CogCt[0], MasterCt[2])
	cmds.parentConstraint(CogCt[4], COG_jnt, mo=True)
	cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)
	misc.setChannels(CogCt[0], [False, True], [False, True], [True, False], [True, False, True])
	misc.setChannels(CogCt[1], [False, True], [False, True], [True, False], [True, False, True])
	misc.setChannels(CogCt[2], [False, True], [False, True], [True, False], [True, False, True])
	misc.setChannels(CogCt[3], [False, True], [False, True], [True, False], [False, False, True])
	misc.setChannels(CogCt[4], [False, True], [False, True], [True, False], [True, False, True])
	
	# PELVIS/CHEST #
	## PELVIS ##
	Pelvis = 'pelvis'
	pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'facetYup_ctrl', 70, 17, 8, 1, (0,0,1), True, True)
	PelvisCt = pelvis.createController()
	misc.setRotOrder(PelvisCt[2], 2, False)
	cmds.parentConstraint(PelvisCt[4], PELVIS_jnt, mo=True)
	## CHEST ##
	Chest_1   = 'chest1'
	chest_1   = place.Controller(Chest_1, CHEST1_jnt, False, 'facetYup_ctrl', 65, 17, 8, 1, (0,0,1), True, True)
	Chest_1Ct = chest_1.createController()
	misc.setRotOrder(Chest_1Ct[2], 2, False)
	Chest_2   = 'chest2'
	chest_2   = place.Controller(Chest_2, CHEST2_jnt, False, 'facetYup_ctrl', 65, 17, 8, 1, (0,0,1), True, True)
	Chest_2Ct = chest_2.createController()
	misc.setRotOrder(Chest_2Ct[2], 2, False)
	Chest_3   = 'chest3'
	chest_3   = place.Controller(Chest_3, CHEST3_jnt, False, 'facetYup_ctrl', 65, 17, 8, 1, (0,0,1), True, True)
	Chest_3Ct = chest_3.createController()
	misc.setRotOrder(Chest_3Ct[2], 2, False)
	##constrain controllers, parent under Master group
	cmds.parentConstraint(CogCt[4], PelvisCt[0], mo=True)
	cmds.parentConstraint(CogCt[4], Chest_1Ct[0], mo=True)
	cmds.parentConstraint(Chest_1Ct[4], Chest_2Ct[0], mo=True)
	cmds.parentConstraint(Chest_2Ct[4], Chest_3Ct[0], mo=True)
	cmds.parentConstraint(Chest_1Ct[4], CHEST1_jnt, mo=True)
	cmds.parentConstraint(Chest_2Ct[4], CHEST2_jnt, mo=True)
	cmds.parentConstraint(Chest_3Ct[4], CHEST3_jnt, mo=True)
	##setChannels
	misc.setChannels(PelvisCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(PelvisCt[1], [True, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(PelvisCt[2], [True, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(PelvisCt[3], [True, False], [False, True], [False, True], [False, False, False])
	misc.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(PELVIS_jnt, PelvisCt[2])
	##chest1
	misc.setChannels(Chest_1Ct[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(Chest_1Ct[1], [True, False], [False, False], [False, False], [True, False, False])
	misc.setChannels(Chest_1Ct[2], [True, False], [False, True], [False, False], [True, False, False])
	misc.setChannels(Chest_1Ct[3], [True, False], [False, True], [True, False], [False, False, False])
	misc.setChannels(Chest_1Ct[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(CHEST1_jnt, Chest_1Ct[2])
	##chest2
	misc.setChannels(Chest_2Ct[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(Chest_2Ct[1], [True, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(Chest_2Ct[2], [True, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(Chest_2Ct[3], [True, False], [False, True], [True, False], [False, False, False])
	misc.setChannels(Chest_2Ct[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(CHEST2_jnt, Chest_2Ct[2])
	##chest1
	misc.setChannels(Chest_3Ct[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(Chest_3Ct[1], [True, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(Chest_3Ct[2], [True, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(Chest_3Ct[3], [True, False], [False, True], [True, False], [False, False, False])
	misc.setChannels(Chest_3Ct[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(CHEST3_jnt, Chest_3Ct[2])
	##parent topGp to master
	cmds.parent(PelvisCt[0], CogCt[2])
	cmds.parent(Chest_1Ct[0], CogCt[2])
	cmds.parent(Chest_2Ct[0], Chest_1Ct[2])
	cmds.parent(Chest_3Ct[0], Chest_2Ct[2])
	
	# NECK #
	Neck   = 'neck'
	neck   = place.Controller(Neck, NECK_jnt, False, 'facetYup_ctrl', 40, 12, 8, 1, (0,0,1), True, True)
	NeckCt = neck.createController()
	misc.setRotOrder(NeckCt[2], 2, False)
	##parent switches
	misc.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], Chest_3Ct[4], False, True, False, True, 'Chest')
	cmds.parentConstraint(Chest_3Ct[4], NeckCt[0], mo=True)
	cmds.parentConstraint(NeckCt[4], NECK_jnt, mo=True)
	misc.setChannels(NeckCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(NeckCt[1], [True, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(NeckCt[2], [True, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(NeckCt[3], [True, False], [False, True], [True, False], [False, False, False])
	cmds.setAttr(NeckCt[3] + '.visibility', cb=False)
	misc.setChannels(NeckCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(NECK_jnt, NeckCt[2])
	##parent topGp to master
	cmds.parent(NeckCt[0], Chest_3Ct[2])
	
	# HEAD #
	Head   = 'head'
	head   = place.Controller(Head, HEAD_jnt, False, 'facetYup_ctrl', 50, 12, 8, 1, (0,0,1), True, True)
	HeadCt = head.createController()
	misc.setRotOrder(HeadCt[2], 2, False)
	##parent switch
	misc.parentSwitch(Head, HeadCt[2], HeadCt[1], HeadCt[0], CogCt[4], NeckCt[4], False, True, False, True, 'Neck')
	## insert group under Head, in the same space as Head_offset, name: Head_CnstGp
	Head_CnstGp = place.null2(Head + '_CnstGp', HEAD_jnt)[0]
	misc.setRotOrder(Head_CnstGp, 2, True)
	cmds.parent(Head_CnstGp, HeadCt[2])
	##tip of head constrain to offset
	cmds.parentConstraint(HeadCt[4], HEAD_jnt, mo=True)
	##constrain head to neck
	cmds.parentConstraint(NeckCt[4], HeadCt[0], mo=True)
	##set channels
	misc.setChannels(HeadCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(HeadCt[1], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(HeadCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(HeadCt[3], [True, False], [False, True], [True, False], [False, False, False])
	cmds.setAttr(HeadCt[3] + '.visibility', cb=False)
	misc.setChannels(HeadCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.setChannels(Head_CnstGp, [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(HEAD_jnt, HeadCt[2])
	##parent topGp to master
	cmds.parent(HeadCt[0], NeckCt[2])
	##add extra group to 'HeadCt'
	HeadCt += (Head_CnstGp,)

	# --- ARMS --- #
	
	# SHOULDER L #
	ShldrL   = 'shldr_L'
	shldrL   = place.Controller(ShldrL, SHLDR_L_jnt, True, 'facetYup_ctrl', 35, 12, 8, 1, (0,0,1), True, True)
	ShldrLCt = shldrL.createController()
	misc.setRotOrder(ShldrLCt[1], 0, True)
	##parent switches
	misc.parentSwitch(ShldrL, ShldrLCt[2], ShldrLCt[1], ShldrLCt[0], CogCt[4], Chest_3Ct[4], False, True, False, True, 'Chest')
	##attach
	cmds.parentConstraint(Chest_3Ct[4], ShldrLCt[0], mo=True)
	cmds.parentConstraint( ShldrLCt[4], SHLDR_L_jnt, mo=True)
	cmds.parent(ShldrLCt[0], Chest_3Ct[2])
	#
	misc.setChannels(ShldrLCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(ShldrLCt[1], [False, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(ShldrLCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(ShldrLCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(ShldrLCt[3] + '.visibility', cb=False)
	misc.setChannels(ShldrLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(SHLDR_L_jnt, ShldrLCt[2])
	
	# SHOULDER R #
	ShldrR   = 'shldr_R'
	shldrR   = place.Controller(ShldrR, SHLDR_R_jnt, True, 'facetYup_ctrl', 35, 12, 8, 1, (0,0,1), True, True)
	ShldrRCt = shldrR.createController()
	misc.setRotOrder(ShldrRCt[1], 0, True)
	##parent switches
	misc.parentSwitch(ShldrR, ShldrRCt[2], ShldrRCt[1], ShldrRCt[0], CogCt[4], Chest_3Ct[4], False, True, False, True, 'Chest')
	##attach
	cmds.parentConstraint(Chest_3Ct[4], ShldrRCt[0], mo=True)
	cmds.parentConstraint( ShldrRCt[4], SHLDR_R_jnt, mo=True)
	cmds.parent(ShldrRCt[0], Chest_3Ct[2])
	misc.setChannels(ShldrRCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(ShldrRCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(ShldrRCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(ShldrRCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(ShldrRCt[3] + '.visibility', cb=False)
	misc.setChannels(ShldrRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(SHLDR_R_jnt, ShldrRCt[2])
	
	# CLAVICLE L #
	ClvL   = 'clv_L'
	clvL   = place.Controller(ClvL, CLV_L_jnt, True, 'diamond_ctrl', 10, 17, 8, 1, (0,0,1), True, True)
	ClvLCt = clvL.createController()
	upL    = place.circle('clv_L' + '_Up', ClvLCt[0], 'diamond_ctrl', 1, 17, 8, 1, (0,0,1))[0]
	##misc.setRotOrder(ClvLCt[1], 0, True)
	##misc.setRotOrder(upL, 0, True)
	cmds.setAttr(upL + '.visibility', False)
	cmds.parent(upL, Chest_3Ct[4])
	cmds.setAttr(upL + '.translateY', 1)
	cmds.aimConstraint(ShldrLCt[4], ClvLCt[0], aimVector=(0,-1,0), upVector=(0,0,-1), worldUpType='object', worldUpObject=upL)
	cmds.parentConstraint( ClvLCt[4], CLV_L_jnt, mo=True)
	cmds.parent(ClvLCt[0], Chest_3Ct[2])
	cmds.pointConstraint(Chest_3Ct[4], ClvLCt[0], mo=True)
	misc.setChannels(ClvLCt[0], [False, False], [False, False], [True, False], [True, False, False])
	misc.setChannels(ClvLCt[1], [True, False], [True, False], [True, False], [True, False, False])
	misc.setChannels(ClvLCt[2], [True, False], [True, False], [True, False], [True, False, False])
	misc.setChannels(ClvLCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(ClvLCt[3] + '.visibility', cb=False)
	misc.setChannels(ClvLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	
	# CLAVICLE R #
	ClvR   = 'clv_R'
	clvR   = place.Controller(ClvR, CLV_R_jnt, True, 'diamond_ctrl', 10, 17, 8, 1, (0,0,1), True, True)
	ClvRCt = clvR.createController()
	upR    = place.circle('clv_R' + '_Up', ClvRCt[0], 'diamond_ctrl', 1, 17, 8, 1, (0,0,1))[0]
	##misc.setRotOrder(ClvRCt[1], 0, True)
	##misc.setRotOrder(upR, 0, True)
	cmds.setAttr(upR + '.visibility', False)
	cmds.parent(upR, Chest_3Ct[4])
	cmds.setAttr(upR + '.translateY', 1)
	cmds.aimConstraint(ShldrRCt[4], ClvRCt[0], aimVector=(0,-1,0), upVector=(0,0,-1), worldUpType='object', worldUpObject=upR)
	cmds.parentConstraint( ClvRCt[4], CLV_R_jnt, mo=True)
	cmds.parent(ClvRCt[0], Chest_3Ct[2])
	cmds.pointConstraint(Chest_3Ct[4], ClvRCt[0], mo=True)
	misc.setChannels(ClvRCt[0], [False, False], [False, False], [True, False], [True, False, False])
	misc.setChannels(ClvRCt[1], [True, False], [True, False], [True, False], [True, False, False])
	misc.setChannels(ClvRCt[2], [True, False], [True, False], [True, False], [True, False, False])
	misc.setChannels(ClvRCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(ClvRCt[3] + '.visibility', cb=False)
	misc.setChannels(ClvRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	
	# ELBOW L #
	ElbowL   = 'elbow_L'
	elbowL   = place.Controller(ElbowL, ELBOW_L_jnt, True, 'facetYup_ctrl', 35, 17, 8, 1, (0,0,1), True, True)
	ElbowLCt = elbowL.createController()
	misc.setRotOrder(ElbowLCt[1], 0, True)
	cmds.parentConstraint(ShldrLCt[4], ElbowLCt[0], mo=True)
	cmds.parentConstraint( ElbowLCt[4], ELBOW_L_jnt, mo=True)
	cmds.parent(ElbowLCt[0], ShldrLCt[2])
	misc.setChannels(ElbowLCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(ElbowLCt[1], [False, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(ElbowLCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(ElbowLCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(ElbowLCt[3] + '.visibility', cb=False)
	misc.setChannels(ElbowLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(ELBOW_L_jnt, ElbowLCt[2])
	
	# ELBOW R #
	ElbowR   = 'elbow_R'
	elbowR   = place.Controller(ElbowR, ELBOW_R_jnt, True, 'facetYup_ctrl', 35, 17, 8, 1, (0,0,1), True, True)
	ElbowRCt = elbowR.createController()
	misc.setRotOrder(ElbowRCt[1], 0, True)
	cmds.parentConstraint(ShldrRCt[4], ElbowRCt[0], mo=True)
	cmds.parentConstraint( ElbowRCt[4], ELBOW_R_jnt, mo=True)
	cmds.parent(ElbowRCt[0], ShldrRCt[2])
	misc.setChannels(ElbowRCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(ElbowRCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(ElbowRCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(ElbowRCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(ElbowRCt[3] + '.visibility', cb=False)
	misc.setChannels(ElbowRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(ELBOW_R_jnt, ElbowRCt[2])
	
	# WRIST L #
	WristL   = 'wrist_L'
	wristL   = place.Controller(WristL, WRIST_L_jnt, True, 'facetYup_ctrl', 25, 12, 8, 1, (0,0,1), True, True)
	WristLCt = wristL.createController()
	misc.setRotOrder(WristLCt[1], 0, True)
	cmds.parentConstraint(ElbowLCt[4], WristLCt[0], mo=True)
	cmds.parentConstraint( WristLCt[4], WRIST_L_jnt, mo=True)
	cmds.parent(WristLCt[0], ElbowLCt[2])
	misc.setChannels(WristLCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(WristLCt[1], [False, False], [False, True], [False, True], [True, False, False])
	misc.setChannels(WristLCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(WristLCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(WristLCt[3] + '.visibility', cb=False)
	misc.setChannels(WristLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(WRIST_L_jnt, WristLCt[2])
	
	# WRIST R #
	WristR   = 'wrist_R'
	wristR   = place.Controller(WristR, WRIST_R_jnt, True, 'facetYup_ctrl', 25, 12, 8, 1, (0,0,1), True, True)
	WristRCt = wristR.createController()
	misc.setRotOrder(WristRCt[1], 0, True)
	cmds.parentConstraint(ElbowRCt[4], WristRCt[0], mo=True)
	cmds.parentConstraint( WristRCt[4], WRIST_R_jnt, mo=True)
	cmds.parent(WristRCt[0], ElbowRCt[2])
	misc.setChannels(WristRCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(WristRCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(WristRCt[2], [False, True], [False, True], [False, True], [True, False, False])
	misc.setChannels(WristRCt[3], [False, True], [False, True], [True, False], [False, False, False])
	cmds.setAttr(WristRCt[3] + '.visibility', cb=False)
	misc.setChannels(WristRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(WRIST_R_jnt, WristRCt[2])
	
	# --- LEGS --- #
	
	# HIP L #
	HipL   = 'hip_L'
	hipL   = place.Controller(HipL, HIP_L_jnt, False, 'diamond_ctrl', 5, 17, 8, 1, (0,0,1), True, True)
	HipLCt = hipL.createController()
	cmds.parentConstraint(PelvisCt[4], HipLCt[0], mo=True)
	cmds.parent(HipLCt[0], PelvisCt[2])
	misc.setChannels(HipLCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(HipLCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(HipLCt[2], [True, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(HipLCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(HipLCt[3] + '.visibility', cb=False)
	misc.setChannels(HipLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(HIP_L_jnt, HipLCt[2])

	# HIP R #
	HipR   = 'hip_R'
	hipR   = place.Controller(HipR, HIP_R_jnt, False, 'diamond_ctrl', 5, 17, 8, 1, (0,0,1), True, True)
	HipRCt = hipR.createController()
	cmds.parentConstraint(PelvisCt[4], HipRCt[0], mo=True)
	cmds.parent(HipRCt[0], PelvisCt[2])
	misc.setChannels(HipRCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(HipRCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(HipRCt[2], [True, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(HipRCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(HipRCt[3] + '.visibility', cb=False)
	misc.setChannels(HipRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(HIP_R_jnt, HipRCt[2])

	# KNEE L #
	KneeL   = 'knee_L'
	kneeL   = place.Controller(KneeL, KNEE_L_jnt, True, 'diamond_ctrl', 5, 17, 8, 1, (0,0,1), True, True)
	KneeLCt = kneeL.createController()
	cmds.parentConstraint(KNEE_L_jnt, KneeLCt[0], mo=True)
	cmds.parent(KneeLCt[0], CogCt[2])
	misc.setChannels(KneeLCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(KneeLCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(KneeLCt[2], [True, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(KneeLCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(KneeLCt[3] + '.visibility', cb=False)
	misc.setChannels(KneeLCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(KNEE_L_jnt, KneeLCt[2])
	
	# KNEE R #
	KneeR   = 'knee_R'
	kneeR   = place.Controller(KneeR, KNEE_R_jnt, True, 'diamond_ctrl', 5, 17, 8, 1, (0,0,1), True, True)
	KneeRCt = kneeR.createController()
	cmds.parentConstraint(KNEE_R_jnt, KneeRCt[0], mo=True)
	cmds.parent(KneeRCt[0], CogCt[2])
	misc.setChannels(KneeRCt[0], [False, False], [False, False], [False, True], [True, False, False])
	misc.setChannels(KneeRCt[1], [False, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(KneeRCt[2], [True, False], [True, False], [False, True], [True, False, False])
	misc.setChannels(KneeRCt[3], [True, False], [True, False], [True, False], [False, False, False])
	cmds.setAttr(KneeRCt[3] + '.visibility', cb=False)
	misc.setChannels(KneeRCt[4], [True, False], [True, False], [True, False], [True, False, False])
	misc.hijackScale(KNEE_R_jnt, KneeRCt[2])

	# LEG IK L #
	ik_leg_L = cmds.ikHandle(sj=HIP_L_jnt, ee=ANKLE_L_jnt, n='ik_leg_L', sol='ikRPsolver', s='sticky')
	atomOpts(name='leg', limbName=3, size=1.0, distance=20, suffix=1, flip=[1,0,0])
	pvL = placePV(HIP_L_jnt)
	cmds.poleVectorConstraint(pvL, ik_leg_L[0])
	cmds.parent(pvL, CogCt[2])
	cmds.setAttr(ik_leg_L[0] + '.visibility', False)
	
	# LEG IK R #
	ik_leg_R = cmds.ikHandle(sj=HIP_R_jnt, ee=ANKLE_R_jnt, n='ik_leg_R', sol='ikRPsolver', s='sticky')
	atomOpts(name='leg', limbName=3, size=1.0, distance=-20, suffix=2, flip=[1,1,0])
	pvR = placePV(HIP_R_jnt)
	cmds.poleVectorConstraint(pvR, ik_leg_R[0])
	cmds.parent(pvR, CogCt[2])
	cmds.setAttr(ik_leg_R[0] + '.visibility', False)
	
	# ANKLE L #
	AnkleL   = 'ankle_L'
	ankleL   = place.Controller(AnkleL, ANKLE_L_jnt, False, 'diamond_ctrl', 10, 17, 8, 1, (0,0,1), True, True)
	ankleLCt = ankleL.createController()
	cmds.parent(ik_leg_L[0], ankleLCt[4])
	cmds.parentConstraint( ankleLCt[4], ik_leg_L[0], mo=True)
	cmds.setAttr(ankleLCt[0] + '.visibility', False)
	
	# ANKLE R #
	AnkleR   = 'ankle_R'
	ankleR   = place.Controller(AnkleR, ANKLE_R_jnt, False, 'diamond_ctrl', 10, 17, 8, 1, (0,0,1), True, True)
	ankleRCt = ankleR.createController()
	cmds.parent(ik_leg_R[0], ankleRCt[4])
	cmds.parentConstraint( ankleRCt[4], ik_leg_R[0], mo=True)
	cmds.setAttr(ankleRCt[0] + '.visibility', False)
	
	# ANKLE IK L #
	ik_ankle_L = cmds.ikHandle(sj=ANKLE_L_jnt, ee=BALL_L_jnt, n='ik_ankle_L', sol='ikRPsolver', s='sticky')
	anklePv = place.twoJointPV(AnkleL, ik_ankle_L[0], 3)
	cmds.setAttr(ik_ankle_L[0] + '.visibility', False)
	cmds.setAttr(anklePv[1] + '.visibility', False)
	cmds.parent(anklePv[0], ankleLCt[3])
	
	# ANKLE IK R #
	ik_ankle_R = cmds.ikHandle(sj=ANKLE_R_jnt, ee=BALL_R_jnt, n='ik_ankle_R', sol='ikRPsolver', s='sticky')
	anklePv = place.twoJointPV(AnkleR, ik_ankle_R[0], 3)
	cmds.setAttr(ik_ankle_R[0] + '.visibility', False)
	cmds.setAttr(anklePv[1] + '.visibility', False)
	cmds.parent(anklePv[0], ankleRCt[3])
	
	# BALL L #
	BallL   = 'ball_L'
	ballL   = place.Controller(BallL, BALL_L_jnt, False, 'ballRoll_ctrl', 30, 17, 8, 1, (0,0,1), True, True)
	ballLCt = ballL.createController()
	cmds.parent(ankleLCt[0], ballLCt[2])
	cmds.parent(anklePv[0], ballLCt[4])
	cmds.parentConstraint(ballLCt[4], ankleLCt[0], mo=True)
	cmds.parent(ik_ankle_L[0], ballLCt[4])
	
	# BALL R #
	BallR   = 'ball_R'
	ballR   = place.Controller(BallR, BALL_R_jnt, False, 'ballRoll_ctrl', 30, 17, 8, 1, (0,0,1), True, True)
	ballRCt = ballR.createController()
	cmds.parent(ankleRCt[0], ballRCt[2])
	cmds.parent(anklePv[0], ballRCt[4])
	cmds.parentConstraint(ballRCt[4], ankleRCt[0], mo=True)
	cmds.parent(ik_ankle_R[0], ballRCt[4])
	
	# BALL IK L #
	ik_ball_L = cmds.ikHandle(sj=BALL_L_jnt, ee=TOE_L_jnt, n='ik_ball_L', sol='ikRPsolver', s='sticky')
	ballPv = place.twoJointPV(BallL , ik_ball_L[0])
	cmds.setAttr(ik_ball_L[0] + '.visibility', False)
	cmds.setAttr(anklePv[1] + '.visibility', False)
	cmds.parent(ballPv[0], ballLCt[3])
	
	# BALL IK R #
	ik_ball_R = cmds.ikHandle(sj=BALL_R_jnt, ee=TOE_R_jnt, n='ik_ball_R', sol='ikRPsolver', s='sticky')
	ballPv = place.twoJointPV(BallR , ik_ball_R[0])
	cmds.setAttr(ik_ball_R[0] + '.visibility', False)
	cmds.setAttr(anklePv[1] + '.visibility', False)
	cmds.parent(ballPv[0], ballRCt[3])
	
	# TOE L #
	ToeL   = 'toe_L'
	toeL   = place.Controller(ToeL, TOE_L_jnt, False, 'pawToeRoll_ctrl', 20, 17, 8, 1, (0,0,1), True, True)
	toeLCt = toeL.createController()
	misc.setRotOrder(toeLCt[2])
	cmds.parent( ballLCt[0], toeLCt[2])
	cmds.parent(ballPv[0], toeLCt[4])
	cmds.parentConstraint(toeLCt[4], ballLCt[0], mo=True)
	cmds.parent(ik_ball_L[0], toeLCt[4])
	
	# TOE R #
	ToeR   = 'toe_R'
	toeR   = place.Controller(ToeR, TOE_R_jnt, False, 'pawToeRoll_ctrl', 20, 17, 8, 1, (0,0,1), True, True)
	toeRCt = toeR.createController()
	misc.setRotOrder(toeRCt[2])
	cmds.parent( ballRCt[0], toeRCt[2])
	cmds.parent(ballPv[0], toeRCt[4])
	cmds.parentConstraint(toeRCt[4], ballRCt[0], mo=True)
	cmds.parent(ik_ball_R[0], toeRCt[4])
	
	# ANKLE FK L #
	AnkleFKL   = 'ankleFK_L'
	ankleFKL   = place.Controller(AnkleFKL, ANKLE_L_jnt, False, 'pawFK_ctrl', 30, 12, 8, 1, (0,0,1), True, True)
	ankleFKLCt = ankleFKL.createController()
	misc.setRotOrder(ankleFKLCt[2], 2, False)
	cmds.parent( toeLCt[0], ankleFKLCt[2])
	cmds.parentConstraint( ankleFKLCt[4], toeLCt[0], mo=True)
	
	# ANKLE FK R #
	AnkleFKR   = 'ankleFK_R'
	ankleFKR   = place.Controller(AnkleFKR, ANKLE_R_jnt, False, 'pawFK_ctrl', 30, 12, 8, 1, (0,0,1), True, True)
	ankleFKRCt = ankleFKR.createController()
	misc.setRotOrder(ankleFKRCt[2], 2, False)
	cmds.parent( toeRCt[0], ankleFKRCt[2])
	cmds.parentConstraint( ankleFKRCt[4], toeRCt[0], mo=True)

	# FOOT L  #
	FootL   = 'Foot_L'
	footL   = place.Controller(FootL, FOOT_pivotL_jnt, False, 'pawMaster_ctrl', 55, 12, 8, 1, (0,0,1), True, True)
	FootLCt = footL.createController()
	cmds.parent(FootLCt[0], MasterCt[2])
	##More parent group Options
	cmds.select(FootLCt[0])
	FootL_TopGrp2 = misc.insert('null', 1, FootL + '_TopGrp2')[0][0]
	FootL_CtGrp2  = misc.insert('null', 1, FootL + '_CtGrp2')[0][0]
	FootL_TopGrp1 = misc.insert('null', 1, FootL + '_TopGrp1')[0][0]
	FootL_CtGrp1  = misc.insert('null', 1, FootL + '_CtGrp1')[0][0]
	##set RotateOrders for new groups
	misc.setRotOrder(FootLCt[2])
	##parentConstraints
	cmds.parent(ankleFKLCt[0], FootLCt[2])
	cmds.parentConstraint( FootLCt[4], ankleFKLCt[0], mo=True)
	cmds.parentConstraint(MasterCt[4], FootL_TopGrp2, mo=True)
	misc.parentSwitch('PRNT2_' + FootL, FootLCt[2], FootL_CtGrp2, FootL_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
	misc.parentSwitch('PRNT1_' + FootL, FootLCt[2], FootL_CtGrp1, FootL_TopGrp1, FootL_CtGrp2, PelvisCt[4], False, False, True, False, 'Pelvis', 0.0)
	misc.parentSwitch('PNT_' + FootL, FootLCt[2], FootLCt[1], FootLCt[0], FootL_CtGrp1, PelvisCt[4], True, False, False, False, 'Pelvis', 0.0)
	misc.setChannels(FootLCt[0], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootLCt[1], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootLCt[2], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootLCt[3], [False, True], [False, True], [True, False], [False, False, True])
	misc.setChannels(FootLCt[4], [False, True], [False, True], [True, False], [False, False, True])
	misc.hijackScale(ANKLE_L_jnt, FootLCt[2])

	# FOOT R  #
	FootR   = 'Foot_R'
	footR   = place.Controller(FootR, FOOT_pivotR_jnt, False, 'pawMaster_ctrl', 55, 12, 8, 1, (0,0,1), True, True)
	FootRCt = footR.createController()
	cmds.parent(FootRCt[0], MasterCt[2])
	##More parent group Options
	cmds.select(FootRCt[0])
	FootR_TopGrp2 = misc.insert('null', 1, FootR + '_TopGrp2')[0][0]
	FootR_CtGrp2  = misc.insert('null', 1, FootR + '_CtGrp2')[0][0]
	FootR_TopGrp1 = misc.insert('null', 1, FootR + '_TopGrp1')[0][0]
	FootR_CtGrp1  = misc.insert('null', 1, FootR + '_CtGrp1')[0][0]
	##set RotateOrders for new groups
	misc.setRotOrder(FootRCt[2])
	##parentConstrain top group
	cmds.parent(ankleFKRCt[0], FootRCt[2])
	cmds.parentConstraint( FootRCt[4], ankleFKRCt[0], mo=True)
	cmds.parentConstraint(MasterCt[4], FootR_TopGrp2, mo=True)
	misc.parentSwitch('PRNT2_' + FootR, FootRCt[2], FootR_CtGrp2, FootR_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
	misc.parentSwitch('PRNT1_' + FootR, FootRCt[2], FootR_CtGrp1, FootR_TopGrp1, FootR_CtGrp2, PelvisCt[4], False, False, True, False, 'Pelvis', 0.0)
	misc.parentSwitch('PNT_' + FootR, FootRCt[2], FootRCt[1], FootRCt[0], FootR_CtGrp1, PelvisCt[4], True, False, False, False, 'Pelvis', 0.0)
	misc.setChannels(FootRCt[0], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootRCt[1], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootRCt[2], [False, True], [False, True], [False, True], [True, False, True])
	misc.setChannels(FootRCt[3], [False, True], [False, True], [True, False], [False, False, True])
	misc.setChannels(FootRCt[4], [False, True], [False, True], [True, False], [False, False, True])
	misc.hijackScale(ANKLE_R_jnt, FootRCt[2])

	# PV #
	pvL_Gp = apg.pvRig('pvLeg_L', MasterCt[4], HipLCt[4], ankleFKLCt[4], toeLCt[4], pvL, KNEE_L_jnt, 3, setChannels=True,up=[-1,0,0],aim=[0,-1,0], color=17)
	pvR_Gp = apg.pvRig('pvLeg_R', MasterCt[4], HipRCt[4], ankleFKRCt[4], toeRCt[4], pvR, KNEE_R_jnt, 3, setChannels=True,up=[1,0,0],aim=[0,-1,0], color=17)
	cmds.parent(pvL_Gp, MasterCt[2])
	cmds.parent(pvR_Gp, MasterCt[2])

