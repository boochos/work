from pymel.core import *
import os
import atom_surfaceRig_lib as asl
from atom import atom_placement_lib as place
from atom import atom_splineStage_lib as stage
from atom import atom_miscellaneous_lib as misc

def buildAccessories(*args):
    dirPath,baseName   = os.path.split(sceneName())
    #neckRigList = ['BDogChain','BuddhaNecklace','BDogShirt']
    #
    neckRigList = ['BDogShirt','BDogChain','BuddhaNecklace']
    if not objExists('surfaceRig_geo'):
	importFile(os.path.join(dirPath,'GenericBuddy_surfaceRigGeo.ma'))
	
    sg = ls('surfaceRig_geo')[0]
    sg.visibility.set(0)
    sg.setParent('___UTILITY')
    sRig    = None
    hasWrap = False
    
    #create the wrap deformer
    for node in sg.node().listHistory():
	if node.nodeType() == 'wrap':
	    hasWrap = True 
    
    if not hasWrap:
	select('surfaceRig_geo')
	select('neck_retainer_Geo',tgl=True)
	mel.CreateWrap()
    
    if os.path.basename(dirPath) == 'RIG':
	#check the accessory folder
	accPath = os.path.join(dirPath, 'Accessories')
	if os.path.isdir(accPath):
	    accDirs = os.listdir(accPath)
	    for a in accDirs:
		rigPath = os.path.join(accPath, a)
		if os.path.isdir(rigPath):
		    for rig in neckRigList:
			if os.path.basename(rigPath) == rig:
			    
			    if rig == 'BDogChain':
				asrVtxList= [6,41,138,131,145,374,363,308,297,313,81,3]
				nullGrp  = None
				sRigList = []
    
				#import the necklace geo for the wrap deformer			    
				importFile(os.path.join(rigPath,rig  + '_Rig.ma'))
				
				try:
				    PyNode (rig + '_CLUSTERGRP')
				except:
				    nullGrp = ls(createNode('transform', name=rig + '_CLUSTERGRP', ss=True))[0]
	    
				for i in range(0,12,1):
				    #stripe goes counter clockwise
				    sRig = asl.ASR(ls('surfaceRig_geo.vtx[' + str(asrVtxList[i]) + ']')[0],ctrlSize=3, name = 'ASR_bdogChain_accessory', buildJoint = False)
				    sRig.createRig()
				    sRig.cleanup()
				    if i == 0: 
					nullGrp.setParent(sRig.rigWGrp)
					ls(sRig.rigCtrlGrp)[0].setParent('___CONTROLS')
					ls(sRig.rigWGrp)[0].setParent('___WORLD_SPACE')
				    sRigList.append(sRig)
				
				for i in range(0,12,1):
				    rigCluster = cluster('loftedSurface1.cv['+ str(i) +'][0:2]', name = rig + '_cluster_' + str(asrVtxList[i]))
				    pc         = pointConstraint(rigCluster[1],sRigList[i].ctrlElement.ctGrp)
				    delete(ls(pc))
				    rigCluster[1].visibility.set(0)
				    rigCluster[1].setParent(nullGrp)
				    parentConstraint(sRigList[i].ctrlElement.ctrl,rigCluster, mo=True)
				
				utilGrp = ls('bDogNecklaceUtl_Gp')[0]
				utilGrp.setParent('___OL_SKOOL')
				utilGrp.visibility.set(0)
				
				geoGrp = ls('bDogNecklace_GeoGp')[0]
				geoGrp.setParent('___UTILITY')
				
				neckCtrl = ls('neck')[0]
				
				if not neckCtrl.hasAttr('Accessory'):
				    neckCtrl.addAttr('Accessory',at='enum', en='OPTNS')
				    neckCtrl.Accessory.set(cb=True)
				
				neckCtrl.addAttr('BDog_Chain_Ctrl_Vis', at='long', dv=0, min=0, max=1)
				neckCtrl.BDog_Chain_Ctrl_Vis.set(cb=True)
				neckCtrl.BDog_Chain_Ctrl_Vis.connect(ls(sRig.rigCtrlGrp)[0].visibility)
				neckCtrl.addAttr('BDog_Chain_Geo_Vis', at='long', dv=0, min=0, max=1)
				neckCtrl.BDog_Chain_Geo_Vis.set(cb=True)
					
				for child in geoGrp.getChildren():
				    if child.getShape() == None:
					for subChild in child.getChildren():
					    neckCtrl.BDog_Chain_Geo_Vis.connect(subChild.visibility)
			    
			    elif rig == 'BuddhaNecklace':
				asrVtxList= [6,41,138,131,142,192,291,90,82,3]
				nullGrp  = None
				sRigList = []
    
				#import the necklace geo for the wrap deformer			    
				importFile(os.path.join(rigPath,rig  + '_Rig.ma'))
				
				try:
				    PyNode (rig + '_CLUSTERGRP')
				except:
				    nullGrp = ls(createNode('transform', name=rig + '_CLUSTERGRP', ss=True))[0]
	    
				for i in range(0,10,1):
				    sRig = asl.ASR(ls('surfaceRig_geo.vtx[' + str(asrVtxList[i]) + ']')[0],ctrlSize=3, name = 'ASR_buddahNecklace_accessory', buildJoint = False)
				    sRig.createRig()
				    sRig.cleanup()
				    if i == 0:
					nullGrp.setParent(sRig.rigWGrp)
					ls(sRig.rigCtrlGrp)[0].setParent('___CONTROLS')
					ls(sRig.rigWGrp)[0].setParent('___WORLD_SPACE')
					
				    sRigList.append(sRig)

				for i in range(0,10,1):
				    rigCluster = cluster('buddhaBeads_Nbs.cv['+ str(i) +'][0:2]', name = rig + '_cluster_' + str(asrVtxList[i]))
				    pc         = pointConstraint(rigCluster[1],sRigList[i].ctrlElement.ctGrp)
				    delete(ls(pc))
				    rigCluster[1].visibility.set(0)
				    rigCluster[1].setParent(nullGrp)
				    parentConstraint(sRigList[i].ctrlElement.ctrl,rigCluster, mo=True)
				
				utilGrp = ls('buddhaNecklaceUtl_Gp')[0]
				utilGrp.setParent('___UTILITY')
				utilGrp.visibility.set(0)
				
				geoGrp = ls('buddhaNecklace_GeoGp')[0]
				geoGrp.setParent('___UTILITY')
				
				neckCtrl = ls('neck')[0]
				
				if not neckCtrl.hasAttr('Accessory'):
				    neckCtrl.addAttr('Accessory',at='enum', en='OPTNS')
				    neckCtrl.Accessory.set(cb=True)
				
				neckCtrl.addAttr('Buddah_Ncklce_Ctrl_Vis', at='long', dv=0, min=0, max=1)
				neckCtrl.Buddah_Ncklce_Ctrl_Vis.set(cb=True)
				neckCtrl.Buddah_Ncklce_Ctrl_Vis.connect(ls(sRig.rigCtrlGrp)[0].visibility)
				
				neckCtrl.addAttr('Buddah_Ncklce_Geo_Vis', at='long', dv=0, min=0, max=1)
				neckCtrl.Buddah_Ncklce_Geo_Vis.set(cb=True)
				
				for child in geoGrp.getChildren():
				    if child.getShape() == None:
					for subChild in child.getChildren():
					    neckCtrl.Buddah_Ncklce_Geo_Vis.connect(subChild.visibility)
				
					    

			    
			    elif rig == 'BDogShirt':
				neckCtrl = ls('neck')[0]
								
				importFile(os.path.join(rigPath,rig  + '.ma'))
				shirtGeo = ls('shirt_Geo')[0]
				select(shirtGeo)
				select('body_Geo',tgl=True)
				mel.CreateWrap()
				neckCtrl.addAttr('BDog_Shirt_Geo_Vis', at='long', dv=0, min=0, max=1)
				neckCtrl.BDog_Shirt_Geo_Vis.set(cb=True)
				neckCtrl.BDog_Shirt_Geo_Vis.connect(shirtGeo.visibility)
				shirtGeo.getParent().setParent('___ACCESSORY')
				
				
def catNecklace(*args):
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    
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
    
    def spline(name, joints, parentS, parentE):
	'''\n
	    name   = prefix name\n
	joints = first joint and last joint of spline
	    '''
	spline   = place.Controller(name + '_Start', joints[0], True, 'facetZup_ctrl', X*4, 12, 8, 1, (0,0,1), True, True)
	splineCt = spline.createController()
	cmds.parentConstraint(parentS, splineCt[0], mo=True)
	##build spline
	SplineOpts(name, necklaceSize, necklaceDistance, necklaceFalloff)
	cmds.select(joints)
	stage.splineStage(4)
	##assemble
	cmds.parentConstraint(splineCt[4], name + '_IK_CtrlGrp', mo=True)
	cmds.parentConstraint(splineCt[4], name + '_S_IK_PrntGrp', mo=True)
	cmds.parentConstraint(parentE, name + '_E_IK_PrntGrp', mo=True)
	##set options
	cmds.setAttr(name + '_IK_CtrlGrp.' + name + 'Vis', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.' + name + 'Root', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.' + name + 'Stretch', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.ClstrVis', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.ClstrMidIkBlend', 1)
	cmds.setAttr(name + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
	cmds.setAttr(name + '_IK_CtrlGrp.VctrVis', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.VctrMidIkBlend', .25)
	cmds.setAttr(name + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
	cmds.setAttr(name + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
	cmds.setAttr(name + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
	cmds.setAttr(name + '_S_IK_Cntrl.LockOrientOffOn', 1)
	cmds.setAttr(name + '_E_IK_Cntrl.LockOrientOffOn', 0)
	##attrs
	OptAttr(splineCt[2], name)
	misc.hijackCustomAttrs(name + '_IK_CtrlGrp', splineCt[2])    
	
	
    #necklace
    necklaceName = 'necklace'
    necklaceSize     = X*0.5
    necklaceDistance = X*8.0
    necklaceFalloff  = 0
    necklacePrnt = 'necklaceFront_jnt'
    ##necklaceStrt = 'pelvis_jnt'
    necklaceEnd  = 'necklaceBack_jnt'
    necklaceAttr = 'necklace'
    L     = ['necklace_jnt_01_L', 'necklace_jnt_15_L']
    R     = ['necklace_jnt_01_R', 'necklace_jnt_15_R']
    #build controllers
    ##root
    front   = place.Controller(necklaceName + '_Front', necklacePrnt, True, 'diamond_ctrl', X*4, 12, 8, 1, (0,0,1), True, True)
    frontCt = front.createController()
    cmds.parentConstraint(frontCt[4], necklacePrnt, mo=True)
    ##end
    back   = place.Controller(necklaceName + '_Back', necklaceEnd, True, 'diamond_ctrl', X*4, 12, 8, 1, (0,0,1), True, True)
    backCt = back.createController()
    cmds.parentConstraint(backCt[4], necklaceEnd, mo=True)
    ##spline
    spline('necklace_L', L, frontCt[4], necklaceEnd)
    spline('necklace_R', R, frontCt[4], necklaceEnd)
    ##cleanup
    #misc.cleanUp(AbCt[0], Ctrl=True)
