import maya.cmds as cmds
import maya.mel as mm
import os
from key_libs import key_util_lib
import atom_deformer_lib as deformer
import atom_miscellaneous_lib as misc
import atom_splineStage_lib as stage
import atom_placement_lib as place


def SplineOpts(name, size, distance, falloff):
    '''\n
    Changes options in Atom rig window\n
    '''
    cmds.textField('atom_prefix_textField', e=True, tx=name)
    cmds.floatField('atom_spln_scaleFactor_floatField', e=True, v=size)
    cmds.floatField('atom_spln_vectorDistance_floatField', e=True, v=distance)
    cmds.floatField('atom_spln_falloff_floatField', e=True, v=falloff)

def splineSettings(prefix, Vis=1, Root=0, Stretch=0,
                   ClstrVis=0, ClstrBlnd=1, ClstrW=0.5,
                   VctrVis=0, VctrBlnd=1, VctrW=0.5, VctrCstrnt=0, VctrCstrntW=0.5,
                   StrtOrient=0, EndOrient=0):
    cmds.setAttr(prefix + '_IK_CtrlGrp.' + prefix + 'Vis', Vis)
    cmds.setAttr(prefix + '_IK_CtrlGrp.' + prefix + 'Root', Root)
    cmds.setAttr(prefix + '_IK_CtrlGrp.' + prefix + 'Stretch', Stretch)
    cmds.setAttr(prefix + '_IK_CtrlGrp.ClstrVis', ClstrVis)
    cmds.setAttr(prefix + '_IK_CtrlGrp.ClstrMidIkBlend', ClstrBlnd)
    cmds.setAttr(prefix + '_IK_CtrlGrp.ClstrMidIkSE_W', ClstrW)
    cmds.setAttr(prefix + '_IK_CtrlGrp.VctrVis', VctrVis)
    cmds.setAttr(prefix + '_IK_CtrlGrp.VctrMidIkBlend', VctrBlnd)
    cmds.setAttr(prefix + '_IK_CtrlGrp.VctrMidIkSE_W', VctrW)
    cmds.setAttr(prefix + '_IK_CtrlGrp.VctrMidTwstCstrnt', VctrCstrnt)
    cmds.setAttr(prefix + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', VctrCstrntW)
    cmds.setAttr(prefix + '_S_IK_Cntrl.LockOrientOffOn', StrtOrient)
    cmds.setAttr(prefix + '_E_IK_Cntrl.LockOrientOffOn', EndOrient)


def OptAttr(obj, attr):
    '''\n
    Creates separation attr to signify beginning of options for spline\n
    '''
    cmds.addAttr(obj, ln=attr, attributeType='enum', en='OPTNS' )
    cmds.setAttr(obj + '.' + attr, cb=True)

def spline(SPLN_Name='SPLN', SPLN_Size=0.5, SPLN_Dist=3.0, SPLN_Falloff=0, SPLN_Prnt=['splinePRNT', 'startPRNT', 'endJPRNT'],
           SPLN_Attr='SPLN_L', SPLN=['startJNT', 'endJNT', ],
           SPLN_Vis=['cntrlName', 'attrName'],  cleanUp=False):
    '''\n
    Build splines for snake character\n
    '''
    face=None
    X = cmds.floatField('atom_srig_conScale', query=True, value=True)

    #spline
    if cmds.objExists(SPLN[0]):
        SPLN_Name = SPLN_Name
        ##SPLN_Name = SPLN_Name + '_Base'
        #build spline
        SplineOpts(SPLN_Name, SPLN_Size*0.5, SPLN_Dist*3.0, SPLN_Falloff)
        cmds.select(SPLN)
        stage.splineStage(4)
    ##assemble
    cmds.parentConstraint(SPLN_Prnt[0], SPLN_Name + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(SPLN_Prnt[1], SPLN_Name + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(SPLN_Prnt[2], SPLN_Name + '_E_IK_PrntGrp', mo=True)

def snakeTongue(Name, X):
    '''\n
    X = size

    '''
    tng   = place.Controller(Name, 'tongueMicro_jnt_01', True, 'facetZup_ctrl', X*5, 13, 8, 1, (0,0,1), True, True)
    tngCt = tng.createController()
    cmds.parentConstraint('jaw', tngCt[0], mo=True)
    tngTip   = place.Controller(Name + 'Tip', 'tongueMicro_jnt_07', True, 'facetZup_ctrl', X*5, 13, 8, 1, (0,0,1), True, True)
    tngTipCt = tngTip.createController()
    cmds.parentConstraint(tngCt[4], tngTipCt[0], mo=True)
    ##OLD##
    '''
	#tongueMacro
	spline(SPLN_Name=Name + 'Macro', SPLN_Size=X*1.2, SPLN_Dist=0.4, SPLN_Falloff=0, 
		                     SPLN_Prnt=[tngCt[4], tngCt[4], tngCt[4]], SPLN_Attr='tongue', 
		                     SPLN=['tongueMacro_jnt_01', 'tongueMacro_jnt_03'],
		                     SPLN_Vis=['cntrlName', 'attrName'],  cleanUp=True)
	##macro spline Settings
	splineSettings(Name + 'Macro', Vis=1, Root=1, Stretch=0,
	               ClstrVis=0, ClstrBlnd=1, ClstrW=0.25,
                   VctrVis=0, VctrBlnd=1, VctrW=0.5, VctrCstrnt=0, VctrCstrntW=0.5,
                   StrtOrient=0, EndOrient=1)
	'''
    #tongue
    #_micro
    spline(SPLN_Name=Name + 'Base', SPLN_Size=X*.6, SPLN_Dist=2, SPLN_Falloff=1, 
           SPLN_Prnt=[tngCt[4], tngCt[4], tngTipCt[4]], SPLN_Attr='tongueBase', 
           SPLN=['tongueMicro_jnt_01', 'tongueMicro_jnt_07'],
           SPLN_Vis=['cntrlName', 'attrName'],  cleanUp=True)
    ##micro spline Settings
    splineSettings(Name + 'Base', Vis=0, Root=0, Stretch=1,
                   ClstrVis=0, ClstrBlnd=1, ClstrW=0,
                   VctrVis=0, VctrBlnd=1, VctrW=.5, VctrCstrnt=0, VctrCstrntW=0.5,
                   StrtOrient=1, EndOrient=1)

    #attrs
    OptAttr(tngTipCt[3], Name + 'Base' + 'Spline')
    misc.hijackCustomAttrs(Name + 'Base' + '_IK_CtrlGrp', tngTipCt[3])

    #_L
    #controls
    Ln = Name + 'Micro_L'
    chain = place.controllerDownChain('tongueMicro_jnt_01_L', Ln, pad=2, base=None, parent=None, shape='facetZup_ctrl', 
                                      color=17, size=1, groups=True, orient=True, suffix=None, 
                                      scale=True, setChannel=False, clone=False, fk=True)[0]
    misc.cleanUp(chain[0][0], Ctrl=True)
    cmds.parentConstraint('tongueMicro_jnt_07', chain[0][0], mo=True)
    #vars
    i = 0
    j = len(chain)
    #connects
    while i < j:
        misc.attrBlend(tngTipCt[2], chain[i][1], objOpt=chain[i][2], rot=True)
        i = i+1
    ##OLD##
    '''
	spline(SPLN_Name=Name + 'Micro_L', SPLN_Size=X*.4, SPLN_Dist=.85, SPLN_Falloff=0, 
		                         SPLN_Prnt=['tongueMicro_jnt_07', 'tongueMicro_jnt_07', 'tongueMicro_jnt_07'], SPLN_Attr='tongueMicro_L', 
		                         SPLN=['tongueMicro_jnt_01_L', 'tongueMicro_jnt_05_L'],
		                         SPLN_Vis=['cntrlName', 'attrName'],  cleanUp=True)
	##micro_L spline Settings
	splineSettings(Name + 'Micro_L', Vis=0, Root=1, Stretch=1,
               ClstrVis=1, ClstrBlnd=1, ClstrW=0.5,
               VctrVis=0, VctrBlnd=1, VctrW=0.5, VctrCstrnt=0, VctrCstrntW=0.5,
               StrtOrient=1, EndOrient=0)
	'''
    #_R
    #controls
    Ln = Name + 'Micro_R'
    chain = place.controllerDownChain('tongueMicro_jnt_01_R', Ln, pad=2, base=None, parent=None, shape='facetZup_ctrl', 
                                      color=17, size=1, groups=True, orient=True, suffix=None, 
                                      scale=True, setChannel=False, clone=False, fk=True)[0]
    misc.cleanUp(chain[0][0], Ctrl=True)
    cmds.parentConstraint('tongueMicro_jnt_07', chain[0][0], mo=True)
    #vars
    i = 0
    j = len(chain)
    #connects
    while i < j:
        misc.attrBlend(tngTipCt[2], chain[i][1], objOpt=chain[i][2], rot=True)
        i = i+1
    ##OLD##
    '''
	spline(SPLN_Name=Name + 'Micro_R', SPLN_Size=X*.4, SPLN_Dist=.85, SPLN_Falloff=0, 
		                         SPLN_Prnt=['tongueMicro_jnt_07', 'tongueMicro_jnt_07', 'tongueMicro_jnt_07'], SPLN_Attr='tongueMicro_R', 
		                         SPLN=['tongueMicro_jnt_01_R', 'tongueMicro_jnt_05_R'],
		                         SPLN_Vis=['cntrlName', 'attrName'],  cleanUp=True)
	##micro_R spline Settings
	splineSettings(Name + 'Micro_R', Vis=0, Root=1, Stretch=1,
               ClstrVis=1, ClstrBlnd=1, ClstrW=0.5,
               VctrVis=0, VctrBlnd=1, VctrW=0.5, VctrCstrnt=0, VctrCstrntW=0.5,
               StrtOrient=1, EndOrient=0)

	#attrs
	OptAttr(tngCt[2], Name + 'Macro' + 'Spline') 
	misc.hijackCustomAttrs(Name + 'Macro' + '_IK_CtrlGrp', tngCt[2])
	'''

    '''
	OptAttr(tngCt[2], Name + 'Micro' + 'Spline') 
	misc.hijackCustomAttrs(Name + 'Micro' + '_IK_CtrlGrp', tngCt[2])
	OptAttr(tngCt[2], Name + 'Micro_L' + 'Spline') 
	misc.hijackCustomAttrs(Name + 'Micro_L' + '_IK_CtrlGrp', tngCt[2])
	OptAttr(tngCt[2], Name + 'Micro_R' + 'Spline') 
	misc.hijackCustomAttrs(Name + 'Micro_R' + '_IK_CtrlGrp', tngCt[2])
	'''

    #cleanup
    misc.cleanUp(tngCt[0], Ctrl=True)
    misc.cleanUp(tngTipCt[0], Ctrl=True)