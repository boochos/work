import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc
from atom import atom_splineStage_lib as stage

def snakeSplines(*args):
	'''\n
	Build splines for snake character\n
	'''
	face=None
	X = cmds.floatField('atom_srig_conScale', query=True, value=True)
	'''
	if check == 0:
		face = False
	else:
		face=True
	'''
		
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

	def chain(prefix='upper', iMax=4, endPrefix='neck', EOrient = 0):
		'''\n
		
		'''
		i    = 0
		while i < iMax:
			letter     = chr(ord('a') + i).upper()
			letterPrev = chr(ord('a') + (i-1)).upper()
			letterNext = chr(ord('a') + (i+1)).upper()
			splineName = prefix + letter
			splineSize     = X*2.2
			splineDistance = X*4.0
			splineFalloff  = 1
			if i == 0:
				splinePrnt = 'A_Grp'
				splineStrt = 'A_Grp'
				newPrefix = prefix[0].upper() + prefix[1:]
				splineAttr = 'A_' + newPrefix
			else:
				splinePrnt = prefix + letter + '_Grp'
				splineStrt = prefix + letterPrev + '_jnt_05'
				splineAttr = prefix + letter + '_Offset'
			if i == iMax -1:
				splineEnd  = endPrefix + '_Grp'
			else:
				splineEnd = prefix + letterNext + '_Grp'
			splineRoot = 'root_jnt'
			spline     = [prefix + letter + '_jnt_01',prefix + letter + '_jnt_05']
			##build spline
			SplineOpts(splineName, splineSize, splineDistance, splineFalloff)
			cmds.select(spline)
			stage.splineStage(4)
			##assemble
			OptAttr(splineAttr, prefix + letter)
			cmds.parentConstraint(splinePrnt, splineName + '_IK_CtrlGrp', mo=True)
			cmds.parentConstraint(splineStrt, splineName + '_S_IK_PrntGrp', mo=True)
			cmds.parentConstraint(splineEnd, splineName + '_E_IK_PrntGrp', mo=True)
			#cmds.parentConstraint(splineName + '_S_IK_Jnt', splineRoot, mo=True)
			##set options
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.' + splineName + 'Vis', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.' + splineName + 'Root', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.' + splineName + 'Stretch', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.ClstrVis', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.ClstrMidIkBlend', 1)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.VctrVis', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.VctrMidIkBlend', 1)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
			cmds.setAttr(prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
			cmds.setAttr(splineName + '_S_IK_Cntrl.LockOrientOffOn', 0)
			cmds.setAttr(splineName + '_E_IK_Cntrl.LockOrientOffOn', EOrient)
			misc.hijackCustomAttrs(splineName + '_IK_CtrlGrp', splineAttr)
			i = i + 1
	chain(prefix='upper', iMax=4, endPrefix='upperE', EOrient = 1)
	chain(prefix='lower', iMax=18, endPrefix='lowerTip', EOrient = 0)

	#NECK
	neckName = 'neck'
	neckSize     = X*1.8
	neckDistance = X*4.0
	neckFalloff  = 1
	neckPrnt = 'neck_Grp' ## old parent
	##neckPrnt = 'upper' + chr(ord('a') + 3).upper() + '_jnt_05'
	neckStrt = 'upper' + chr(ord('a') + 3).upper() + '_jnt_05'
	neckEnd  = 'head_CnstGp'
	neckAttr = 'neck_Offset'
	neck     = ['neck_jnt_01','neck_jnt_03']
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
	cmds.setAttr(neckAttr + '.ClstrMidIkSE_W', 0.2)
	cmds.setAttr(neckAttr + '.VctrVis', 0)
	cmds.setAttr(neckAttr + '.VctrMidIkBlend', 1)
	cmds.setAttr(neckAttr + '.VctrMidIkSE_W', 0.5)
	cmds.setAttr(neckAttr + '.VctrMidTwstCstrnt', 0)
	cmds.setAttr(neckAttr+ '.VctrMidTwstCstrntSE_W', 0.5)
	cmds.setAttr(neckName + '_S_IK_Cntrl.LockOrientOffOn', 1)
	cmds.setAttr(neckName + '_E_IK_Cntrl.LockOrientOffOn', 1)
	