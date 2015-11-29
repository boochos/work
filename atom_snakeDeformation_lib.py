import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')
stage = web.mod('atom_splineStage_lib')


def snakeDeform(*args):
    '''\n
    Creates deformation splines for quad rig.\n
    paw pad\n
    neck\n
    belly\n
    '''
    face = None
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
        cmds.addAttr(obj, ln=attr, attributeType='enum', en='OPTNS')
        cmds.setAttr(obj + '.' + attr, cb=True)

    # deformation opt attr
    OptAttr('head', 'DeformationVis')

    # DIGASTRIC
    if cmds.objExists('digastric_jnt_01'):
        DGCName = 'DGC'
        DGCSize = X * 0.5
        DGCDistance = X * 3.0
        DGCFalloff = 0
        DGCPrnt = 'upperD_jnt_02'
        ##DGCStrt = 'neck_jnt_02'
        DGCEnd = 'head_jnt'
        DGCAttr = 'DGC'
        DGC = ['digastric_jnt_01', 'digastric_jnt_07']
        # build controller
        dgc = place.Controller(DGCName, DGC[0], True, 'facetXup_ctrl', X * 5, 12, 8, 1, (0, 0, 1), True, True)
        dgcCt = dgc.createController()
        cmds.parentConstraint(DGCPrnt, dgcCt[0], mo=True)
        # build spline
        SplineOpts(DGCName, DGCSize, DGCDistance, DGCFalloff)
        cmds.select(DGC)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(dgcCt[4], DGCName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(dgcCt[4], DGCName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(DGCEnd, DGCName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.' + DGCName + 'Vis', 0)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.' + DGCName + 'Root', 0)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.' + DGCName + 'Stretch', 1)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.ClstrMidIkBlend', .4)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.5)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(DGCAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(DGCName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(DGCName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(dgcCt[2], 'DGCSpline')
        place.hijackCustomAttrs(DGCName + '_IK_CtrlGrp', dgcCt[2])
        place.hijackVis(dgcCt[2], 'head', name='digastric', default=None, suffix=False)
        # cleanup
        place.cleanUp(dgcCt[0], Ctrl=True)
