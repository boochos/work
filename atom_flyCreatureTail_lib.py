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


def preBuild(
        COG_jnt='root_jnt', PELVIS_jnt='pelvis_jnt', CHEST_jnt='spine_06_jnt', NECK_jnt='neck_07_jnt', HEAD_jnt='head_00_jnt',
        HIP_L_jnt='back_fin_L_jnt', HIP_R_jnt='back_fin_R_jnt',
        SHLDR_L_jnt='front_shoulder_jnt_L', SHLDR_R_jnt='front_shoulder_jnt_R',
        BACK_L_jnt='back_foot_ctrl_placement_jnt_L', BACK_R_jnt='back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt='front_foot_ctrl_placement_jnt_L', FRONT_R_jnt='front_foot_ctrl_placement_jnt_R',
        TAIL_jnt='tail_00_jnt', TAILTIP_jnt='spine_20_jnt', GEO_gp='simTube_geo', SKIN_jnt='root_jnt'):
    '''\n

    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=.2)

    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 0.9
    print X
    if check == 0:
        face = False
    else:
        face = True

    PreBuild = place.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=False, Size=140)
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # scale support adjust
    cmds.parent(MasterCt[0], WORLD_SPACE)
    #
    scaleList = ['.sx', '.sy', '.sz']
    unlock = [MasterCt[2], SKIN_JOINTS, CONTROLS]
    for ct in unlock:
        for attr in scaleList:
            cmds.setAttr(ct + attr, lock=False)
            cmds.setAttr(ct + attr, k=True)
    #
    cmds.connectAttr(MasterCt[2] + '.scaleX', SKIN_JOINTS + '.scaleX')
    cmds.connectAttr(MasterCt[2] + '.scaleY', SKIN_JOINTS + '.scaleY')
    cmds.connectAttr(MasterCt[2] + '.scaleZ', SKIN_JOINTS + '.scaleZ')
    #
    cmds.connectAttr(MasterCt[2] + '.scaleX', CONTROLS + '.scaleX')
    cmds.connectAttr(MasterCt[2] + '.scaleY', CONTROLS + '.scaleY')
    cmds.connectAttr(MasterCt[2] + '.scaleZ', CONTROLS + '.scaleZ')

    # cleanup
    cmds.parent(COG_jnt, SKIN_JOINTS)
    cmds.parent(GEO_gp, GEO[3])

    # COG #
    Cog = 'cog'
    cog = place.Controller(Cog, COG_jnt, True, 'facetZup_ctrl', X * 40, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # PELVIS/CHEST #
    ## PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'facetZup_ctrl', X * 30, 17, 8, 1, (0, 0, 1), True, True)
    PelvisCt = pelvis.createController()
    place.setRotOrder(PelvisCt[0], 2, True)

    ## CHEST ##
    Chest = 'chest'
    chest = place.Controller(Chest, CHEST_jnt, False, 'facetZup_ctrl', X * 30, 17, 8, 1, (0, 0, 1), True, True)
    ChestCt = chest.createController()
    place.setRotOrder(ChestCt[0], 2, True)
    '''
    ## GROUP for shoulder joints, neck ##
    ChestAttch_Gp = place.null2('ChestAttch_Gp', NECK_jnt)[0]
    ChestAttch_CnstGp = place.null2('ChestAttch_CnstGp', NECK_jnt)[0]
    cmds.parent(ChestAttch_CnstGp, ChestAttch_Gp)
    place.setRotOrder(ChestAttch_CnstGp, 2, False)
    cmds.parentConstraint(CHEST_jnt, ChestAttch_Gp, mo=True)
    cmds.parent(ChestAttch_Gp, PelvisCt[0])
    '''
    # constrain controllers, parent under Master group
    cmds.parentConstraint(CogCt[4], PelvisCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], ChestCt[0], mo=True)
    # setChannels
    place.setChannels(PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False])
    ##place.setChannels(PelvisCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[2], [False, True], [False, True], [True, False], [True, False, False])
    ##place.setChannels(ChestCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels(ChestCt[4], [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(PelvisCt[0], CONTROLS)
    cmds.parent(ChestCt[0], CONTROLS)

    # MIDDLE #
    Neck = 'neck'
    neck = place.Controller(Neck, NECK_jnt, False, 'facetZup_ctrl', X * 30, 17, 8, 1, (0, 0, 1), True, True)
    NeckCt = neck.createController()
    cmds.parentConstraint(CogCt[4], NeckCt[0], mo=True)
    place.setRotOrder(NeckCt[0], 2, True)
    cmds.parent(NeckCt[0], CONTROLS)

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

    # SPINE 1
    spineName = 'spine'
    spineSize = X * 3
    spineDistance = X * 12
    spineFalloff = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'pelvis_Grp'
    spineEnd = 'chest_Grp'
    spineAttr = 'pelvis'
    spineRoot = 'pelvis_jnt'
    spine = ['spine_00_jnt', 'spine_06_jnt']
    # build spline
    SplineOpts(spineName, spineSize, spineDistance, spineFalloff)
    cmds.select(spine)

    stage.splineStage(4)
    # assemble
    OptAttr(spineAttr, 'SpineSpline')
    cmds.parentConstraint(spinePrnt, spineName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(spineStrt, spineName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(spineEnd, spineName + '_E_IK_PrntGrp', mo=True)
    cmds.parentConstraint(spineName + '_S_IK_Jnt', spineRoot, mo=True)
    place.hijackCustomAttrs(spineName + '_IK_CtrlGrp', spineAttr)
    # set options
    cmds.setAttr(spineAttr + '.' + spineName + 'Vis', 0)
    cmds.setAttr(spineAttr + '.' + spineName + 'Root', 1)
    cmds.setAttr(spineAttr + '.' + spineName + 'Stretch', 1)
    cmds.setAttr(spineAttr + '.ClstrVis', 1)
    cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 1.0)
    cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrVis', 0)
    cmds.setAttr(spineAttr + '.VctrMidIkBlend', .75)
    cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # add scale support to master control for stretching, hardcoded, fix later
    s = spineName + '_S_IK_curve_scale'
    cmds.connectAttr(('master' + '.scaleZ'), (s + '.input2Z'))
    e = spineName + '_E_IK_curve_scale'
    cmds.connectAttr(('master' + '.scaleZ'), (e + '.input2Z'))

    # SPINE 2
    spineName = 'neck'
    spineSize = X * 2
    spineDistance = X * 12
    spineFalloff = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'spine_06_jnt'
    spineEnd = 'neck_Grp'
    spineAttr = 'chest'
    spineRoot = 'spine_06_jnt'
    spine = ['neck_01_jnt', 'neck_07_jnt']
    # build spline
    SplineOpts(spineName, spineSize, spineDistance, spineFalloff)
    cmds.select(spine)

    stage.splineStage(4)
    # assemble
    OptAttr(spineAttr, 'NeckSpline')
    cmds.parentConstraint(spinePrnt, spineName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(spineStrt, spineName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(spineEnd, spineName + '_E_IK_PrntGrp', mo=True)
    # cmds.parentConstraint(spineName + '_S_IK_Jnt', spineRoot, mo=True)
    place.hijackCustomAttrs(spineName + '_IK_CtrlGrp', spineAttr)
    # set options
    cmds.setAttr(spineAttr + '.' + spineName + 'Vis', 0)
    cmds.setAttr(spineAttr + '.' + spineName + 'Root', 1)
    cmds.setAttr(spineAttr + '.' + spineName + 'Stretch', 1)
    cmds.setAttr(spineAttr + '.ClstrVis', 1)
    cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 1.0)
    cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrVis', 0)
    cmds.setAttr(spineAttr + '.VctrMidIkBlend', .75)
    cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # add scale support to master control for stretching, hardcoded, fix later
    s = spineName + '_S_IK_curve_scale'
    cmds.connectAttr(('master' + '.scaleZ'), (s + '.input2Z'))
    e = spineName + '_E_IK_curve_scale'
    cmds.connectAttr(('master' + '.scaleZ'), (e + '.input2Z'))


'''
# ref tail
path = '/VFX/projects/NBH/Dropbox (VFX Animation)/VFXAnimationTeam/Dmitry_Format/NBH/_library/_assets/flyCreatureTail/maya/scenes/flyCreatureTail_rig_v0001.ma'
cmds.file(path, r=True, type="mayaAscii", gl=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace="tail")

# select
cmds.select(['flyCreature_animRig_v07:C_master_CTL', 'tail:master'])
sel = cmds.ls(sl=1)
# get ns
nsC = sel[0].split(':')[0]
nsT = sel[1].split(':')[0]

# set scale
cmds.setAttr(nsT + ':master.scaleX', 23)
cmds.setAttr(nsT + ':master.scaleY', 23)
cmds.setAttr(nsT + ':master.scaleZ', 23)

# master attach
con = cmds.parentConstraint(nsC + ':C_master_CTL', nsT + ':master_TopGrp', mo=False)

# hip attach
con = cmds.parentConstraint(nsC + ':C_spineHipsIk_CTL', nsT + ':neck_CtGrp', mo=False)
cmds.setAttr(con[0] + '.target[0].targetOffsetRotateX', -90)
'''
