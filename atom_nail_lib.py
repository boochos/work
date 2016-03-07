from pymel.core import *
import maya.cmds as cmds
import webrImport as web
# web
aal = web.mod('atom_appendage_lib')
aul = web.mod('atom_ui_lib')
place = web.mod('atom_place_lib')
stage = web.mod('atom_splineStage_lib')
ajl = web.mod('atom_joint_lib')
ael = web.mod('atom_earRig_lib')
splnFk = web.mod('atom_splineFk_lib')
adl = web.mod('atom_deformer_lib')
abl = web.mod('atom_body_lib')


def preBuild(COG_jnt='split_R_jnt', PELVIS_jnt='split_L_jnt'):

    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=0.3)

    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)

    CONTROLS = '___CONTROLS'
    cmds.parentConstraint('master_Grp', 'root', mo=True)
    cmds.scaleConstraint('master_Grp', 'root')

    ## nail_L ##
    Pelvis = 'nail_L'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'diamond_ctrl', X * 0.25, 17, 8, 1, (0, 0, 1), False, True)
    PelvisCt = pelvis.createController()
    place.setRotOrder(PelvisCt[0], 2, True)
    # parent switch
    place.parentSwitch('nail_L', PelvisCt[2], PelvisCt[1], PelvisCt[0], 'master_Grp', 'world', False, False, True, True, 'World', w=0)
    # constrain controllers, parent under Master group
    cmds.parentConstraint('master_Grp', PelvisCt[0], mo=True)
    cmds.scaleConstraint('master', PelvisCt[0])
    # setChannels
    place.setChannels(PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False])
    place.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(PelvisCt[0], CONTROLS)
    place.hijackVis(PelvisCt[2], 'master', name='nail_L', suffix=True, default=0, mode='visibility')

    ## nail_L ##
    Pelvis = 'nail_R'
    pelvis = place.Controller(Pelvis, COG_jnt, False, 'diamond_ctrl', X * 0.25, 17, 8, 1, (0, 0, 1), False, True)
    PelvisCt = pelvis.createController()
    place.setRotOrder(PelvisCt[0], 2, True)
    # parent switch
    place.parentSwitch('nail_R', PelvisCt[2], PelvisCt[1], PelvisCt[0], 'master_Grp', 'world', False, False, True, True, 'World', w=0)
    # constrain controllers, parent under Master group
    cmds.parentConstraint('master_Grp', PelvisCt[0], mo=True)
    cmds.scaleConstraint('master', PelvisCt[0])
    # setChannels
    place.setChannels(PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False])
    place.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(PelvisCt[0], CONTROLS)
    place.hijackVis(PelvisCt[2], 'master', name='nail_R', suffix=True, default=0, mode='visibility')

    # splines
    buildSplines()


def buildSplines(*args):
    '''\n
    Build splines for quadraped character\n
    '''
    face = None
    check = cmds.checkBox('atom_rat_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    if check == 0:
        face = False
    else:
        face = True

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

    # anchor r
    blRig = splnFk.SplineFK('anchor_R', 'anchor_00_R_jnt', 'anchor_05_R_jnt', 'mid',
                            controllerSize=X * 0.2, rootParent='nail_R_Grp', parent1='nail_R_Grp', parentDefault=[0, 1], segIteration=5, stretch=1, ik='splineIK')
    # print blRig.ctrlList, '____'
    for i in blRig.topGrp2:
        place.cleanUp(i, World=True)
    for i in blRig.ctrlList:
        pass
        cmds.setAttr(i[0] + '.scaleX', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleY', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleZ', e=True, cb=True, l=False)
        # print i[0]
        cmds.scaleConstraint('master', i[0])
        # return None
    place.hijackVis(blRig.ctrlList[0][2], 'master', name='anchor_R', suffix=True, default=0, mode='visibility')

    # anchor l
    blRig = splnFk.SplineFK('anchor_L', 'anchor_00_L_jnt', 'anchor_05_L_jnt', 'mid',
                            controllerSize=X * 0.2, rootParent='nail_L_Grp', parent1='nail_L_Grp', parentDefault=[0, 1], segIteration=5, stretch=1, ik='splineIK')
    for i in blRig.topGrp2:
        place.cleanUp(i, World=True)
    for i in blRig.ctrlList:
        pass
        cmds.setAttr(i[0] + '.scaleX', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleY', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleZ', e=True, cb=True, l=False)
        cmds.scaleConstraint('master', i[0])
    place.hijackVis(blRig.ctrlList[0][2], 'master', name='anchor_L', suffix=True, default=0, mode='visibility')

    # split r
    blRig = splnFk.SplineFK('split_R', 'split_00_R_jnt', 'split_05_R_jnt', 'mid',
                            controllerSize=X * 0.2, rootParent='nail_R_Grp', parent1='nail_R_Grp', parentDefault=[0, 1], segIteration=5, stretch=1, ik='splineIK')
    for i in blRig.topGrp2:
        place.cleanUp(i, World=True)
    for i in blRig.ctrlList:
        pass
        cmds.setAttr(i[0] + '.scaleX', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleY', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleZ', e=True, cb=True, l=False)
        cmds.scaleConstraint('master', i[0])
    place.hijackVis(blRig.ctrlList[0][2], 'master', name='split_R', suffix=True, default=0, mode='visibility')

    # split l
    blRig = splnFk.SplineFK('split_L', 'split_00_L_jnt', 'split_05_L_jnt', 'mid',
                            controllerSize=X * 0.2, rootParent='nail_L_Grp', parent1='nail_L_Grp', parentDefault=[0, 1], segIteration=5, stretch=1, ik='splineIK')
    for i in blRig.topGrp2:
        place.cleanUp(i, World=True)
    for i in blRig.ctrlList:
        pass
        cmds.setAttr(i[0] + '.scaleX', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleY', e=True, cb=True, l=False)
        cmds.setAttr(i[0] + '.scaleZ', e=True, cb=True, l=False)
        cmds.scaleConstraint('master', i[0])
    place.hijackVis(blRig.ctrlList[0][2], 'master', name='split_L', suffix=True, default=0, mode='visibility')
