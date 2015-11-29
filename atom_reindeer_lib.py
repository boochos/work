from pymel.core import *
import maya.cmds as cmds
#
import webrImport as web
# web
aal = web.mod('atom_appendage_lib')
aul = web.mod('atom_ui_lib')
place = web.mod('atom_place_lib')
stage = web.mod('atom_splineStage_lib')
ael = web.mod('atom_earRig_lib')
splnFk = web.mod('atom_splineFk_lib')
adl = web.mod('atom_deformer_lib')
abl = web.mod('atom_body_lib')
jnt = web.mod('atom_joint_lib')


def preBuild(
        COG_jnt='spine_jnt_01', PELVIS_jnt='pelvis_jnt', CHEST_jnt='spine_jnt_06', NECK_jnt='neck_jnt_01', HEAD_jnt='neck_jnt_06',
        HIP_L_jnt='back_hip_jnt_L', HIP_R_jnt='back_hip_jnt_R',
        SHLDR_L_jnt='front_shoulder_jnt_L', SHLDR_R_jnt='front_shoulder_jnt_R',
        BACK_L_jnt='back_foot_ctrl_placement_jnt_L', BACK_R_jnt='back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt='front_foot_ctrl_placement_jnt_L', FRONT_R_jnt='front_foot_ctrl_placement_jnt_R',
        TAIL_jnt='tail_jnt_01', TAILTIP_jnt='tail_jnt_011', GEO_gp='buddy_GP', SKIN_jnt='root_jnt'):
    '''\n

    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=1.7)

    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)

    if check == 0:
        face = False
    else:
        face = True

    PreBuild = place.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=X * 180)
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    cmds.parent(SKIN_jnt, SKIN_JOINTS)
    #cmds.parent(GEO_gp, GEO)

    # COG #
    Cog = 'cog'
    cog = place.Controller(Cog, COG_jnt, False, 'cog_ctrl', X * 6, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # PELVIS/CHEST #
    ## PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'pelvis_ctrl', X * 5.25, 17, 8, 1, (0, 0, 1), True, True)
    PelvisCt = pelvis.createController()
    place.setRotOrder(PelvisCt[0], 2, True)
    ## GROUP for hip joints, tail ##
    if cmds.objExists(TAIL_jnt):
        PelvisAttch_Gp = place.null2('PelvisAttch_Gp', TAIL_jnt)[0]
        PelvisAttch_CnstGp = place.null2('PelvisAttch_CnstGp', TAIL_jnt)[0]
        cmds.parent(PelvisAttch_CnstGp, PelvisAttch_Gp)
        place.setRotOrder(PelvisAttch_CnstGp, 2, False)
        cmds.parentConstraint(PELVIS_jnt, PelvisAttch_Gp, mo=True)
        cmds.parent(PelvisAttch_Gp, PelvisCt[0])

    ## CHEST ##
    Chest = 'chest'
    chest = place.Controller(Chest, CHEST_jnt, False, 'chest_ctrl', X * 5.5, 17, 8, 1, (0, 0, 1), True, True)
    ChestCt = chest.createController()
    place.setRotOrder(ChestCt[0], 2, True)
    ## GROUP for shoulder joints, neck ##
    ChestAttch_Gp = place.null2('ChestAttch_Gp', NECK_jnt)[0]
    ChestAttch_CnstGp = place.null2('ChestAttch_CnstGp', NECK_jnt)[0]
    cmds.parent(ChestAttch_CnstGp, ChestAttch_Gp)
    place.setRotOrder(ChestAttch_CnstGp, 2, False)
    cmds.parentConstraint(CHEST_jnt, ChestAttch_Gp, mo=True)
    cmds.parent(ChestAttch_Gp, PelvisCt[0])
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

    # NECK #
    Neck = 'neck'
    neck = place.Controller(Neck, NECK_jnt, False, 'neckMaster_ctrl', X * 50, 12, 8, 1, (0, 0, 1), True, True)
    NeckCt = neck.createController()
    place.setRotOrder(NeckCt[0], 2, True)
    # parent switches
    place.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], ChestAttch_CnstGp, False, True, False, True, 'Chest')
    cmds.parentConstraint(ChestAttch_CnstGp, NeckCt[0], mo=True)
    place.setChannels(NeckCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(NeckCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(NeckCt[2], [True, False], [False, True], [True, False], [True, False, False])
    place.setChannels(NeckCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(NeckCt[3] + '.visibility', cb=False)
    place.setChannels(NeckCt[4], [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(NeckCt[0], CONTROLS)

    # HEAD #
    Head = 'head'
    head = place.Controller(Head, HEAD_jnt, False, 'head_ctrl', X * 5, 12, 8, 1, (0, 0, 1), True, True)
    HeadCt = head.createController()
    place.setRotOrder(HeadCt[0], 2, True)
    # parent switch
    place.parentSwitch(Head, HeadCt[2], HeadCt[1], HeadCt[0], CogCt[4], NeckCt[4], False, False, True, True, 'Neck')
    # insert group under Head, in the same space as Head_offset, name: Head_CnstGp
    Head_CnstGp = place.null2(Head + '_CnstGp', HEAD_jnt)[0]
    place.setRotOrder(Head_CnstGp, 2, True)
    cmds.parent(Head_CnstGp, HeadCt[2])
    # tip of head constrain to offset
    cmds.orientConstraint(HeadCt[3], 'neck_jnt_06', mo=True)
    # constrain head to neck
    cmds.parentConstraint(NeckCt[4], HeadCt[0], mo=True)
    # set channels
    place.setChannels(HeadCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(HeadCt[1], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(HeadCt[2], [False, True], [False, True], [True, False], [True, False, False])
    place.setChannels(HeadCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(HeadCt[3] + '.visibility', cb=False)
    place.setChannels(HeadCt[4], [True, False], [True, False], [True, False], [True, False, False])
    place.setChannels(Head_CnstGp, [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(HeadCt[0], CONTROLS)
    # add extra group to 'HeadCt'
    HeadCt += (Head_CnstGp,)

    if face == False:
        # HIP L #
        hipL = 'hip_L'
        hipL = place.Controller(hipL, HIP_L_jnt, False, 'diamond_ctrl', X * 15, 17, 8, 1, (0, 0, 1), True, True)
        HipLCt = hipL.createController()
        place.setRotOrder(HipLCt[0], 2, True)
        cmds.parentConstraint(PelvisAttch_CnstGp, HipLCt[0], mo=True)
        cmds.parentConstraint(HipLCt[4], 'back_hip_dbl_jnt_L', mo=True)
        cmds.parent(HipLCt[0], CONTROLS)

        place.setChannels(HipLCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(HipLCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(HipLCt[2], [True, False], [True, False], [True, False], [False, False, False])
        place.setChannels(HipLCt[3], [True, False], [True, False], [True, False], [False, False, False])
        cmds.setAttr(HipLCt[3] + '.visibility', cb=False)
        place.setChannels(HipLCt[4], [True, False], [True, False], [True, False], [True, False, False])

        # HIP R #
        hipR = 'hip_R'
        hipR = place.Controller(hipR, HIP_R_jnt, False, 'diamond_ctrl', X * 15, 17, 8, 1, (0, 0, 1), True, True)
        HipRCt = hipR.createController()
        place.setRotOrder(HipRCt[0], 2, True)
        cmds.parentConstraint(PelvisAttch_CnstGp, HipRCt[0], mo=True)
        cmds.parentConstraint(HipRCt[4], 'back_hip_dbl_jnt_R', mo=True)
        cmds.parent(HipRCt[0], CONTROLS)
        place.setChannels(HipRCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(HipRCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(HipRCt[2], [True, False], [True, False], [True, False], [False, False, False])
        place.setChannels(HipRCt[3], [True, False], [True, False], [True, False], [False, False, False])
        cmds.setAttr(HipRCt[3] + '.visibility', cb=False)
        place.setChannels(HipRCt[4], [True, False], [True, False], [True, False], [True, False, False])

        ribCageAngle = 15
        # SHOULDER L #
        shldrL = 'shldr_L'
        shldrL = place.Controller(shldrL, SHLDR_L_jnt, False, 'shldrL_ctrl', X * 18, 17, 8, 1, (0, 0, 1), True, True)
        ShldrLCt = shldrL.createController()
        place.setRotOrder(ShldrLCt[0], 2, True)
        cmds.setAttr(ShldrLCt[0] + '.ry', -1 * ribCageAngle)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrLCt[0], mo=True)
        scapStrtchL = cmds.parentConstraint(ShldrLCt[4], 'front_shoulder_dbl_jnt_L', mo=True)[0]
        UsrAttrL = cmds.listAttr(scapStrtchL, ud=True)[0]
        cmds.addAttr(scapStrtchL + '.' + UsrAttrL, e=True, max=1)
        place.hijackAttrs(scapStrtchL, ShldrLCt[2], UsrAttrL, 'ScapulaStretch', default=0)
        cmds.parent(ShldrLCt[0], CONTROLS)
        place.setChannels(ShldrLCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[2], [False, True], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrLCt[3] + '.visibility', cb=False)
        place.setChannels(ShldrLCt[4], [True, False], [True, False], [True, False], [True, False, False])
        cmds.setAttr(ShldrLCt[2] + '.tx', l=True, k=False)
        cmds.setAttr(ShldrLCt[3] + '.tx', l=True, k=False)

        # SHOULDER R #
        shldrR = 'shldr_R'
        shldrR = place.Controller(shldrR, SHLDR_R_jnt, False, 'shldrR_ctrl', X * 18, 17, 8, 1, (0, 0, 1), True, True)
        ShldrRCt = shldrR.createController()
        place.setRotOrder(ShldrRCt[0], 2, True)
        cmds.setAttr(ShldrRCt[0] + '.ry', 1 * ribCageAngle)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrRCt[0], mo=True)
        scapStrtchR = cmds.parentConstraint(ShldrRCt[4], 'front_shoulder_dbl_jnt_R', mo=True)[0]
        UsrAttrR = cmds.listAttr(scapStrtchR, ud=True)[0]
        cmds.addAttr(scapStrtchR + '.' + UsrAttrR, e=True, max=1)
        place.hijackAttrs(scapStrtchR, ShldrRCt[2], UsrAttrR, 'ScapulaStretch', default=0)
        cmds.parent(ShldrRCt[0], CONTROLS)
        place.setChannels(ShldrRCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[2], [False, True], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrRCt[3] + '.visibility', cb=False)
        place.setChannels(ShldrRCt[4], [True, False], [True, False], [True, False], [True, False, False])
        cmds.setAttr(ShldrRCt[2] + '.tx', l=True, k=False)
        cmds.setAttr(ShldrRCt[3] + '.tx', l=True, k=False)

        # Attrs for paws
        attrVis = ['Pivot', 'Pad', 'Fk', 'AnkleUp', 'BaseDigit', 'MidDigit', 'PvDigit']
        attrCstm = ['ToeRoll', 'HeelRoll', 'KneeTwist']
        vis = 'Vis'
        assist = 'Assist'

        # BACK L  #
        PawBckL = 'back_paw_L'
        pawBckL = place.Controller(PawBckL, BACK_L_jnt, False, 'pawMaster_ctrl', X * 20, 12, 8, 1, (0, 0, 1), True, True)
        PawBckLCt = pawBckL.createController()
        cmds.parent(PawBckLCt[0], CONTROLS)
        # More parent group Options
        cmds.select(PawBckLCt[0])
        PawBckL_TopGrp2 = place.insert('null', 1, PawBckL + '_TopGrp2')[0][0]
        PawBckL_CtGrp2 = place.insert('null', 1, PawBckL + '_CtGrp2')[0][0]
        PawBckL_TopGrp1 = place.insert('null', 1, PawBckL + '_TopGrp1')[0][0]
        PawBckL_CtGrp1 = place.insert('null', 1, PawBckL + '_CtGrp1')[0][0]
        # set RotateOrders for new groups
        place.setRotOrder(PawBckL_TopGrp2, 2, True)
        # attr
        place.optEnum(PawBckLCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawBckLCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawBckLCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawBckLCt[2] + '.' + item), k=True)
        # parentConstrain top group
        cmds.parentConstraint(MasterCt[4], PawBckL_TopGrp2, mo=True)
        place.parentSwitch('PRNT2_' + PawBckL, PawBckLCt[2], PawBckL_CtGrp2, PawBckL_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        place.parentSwitch('PRNT1_' + PawBckL, PawBckLCt[2], PawBckL_CtGrp1, PawBckL_TopGrp1, PawBckL_CtGrp2, PelvisCt[4], False, False, True, False, 'Pelvis', 0.0)
        place.parentSwitch('PNT_' + PawBckL, PawBckLCt[2], PawBckLCt[1], PawBckLCt[0], PawBckL_CtGrp1, PelvisCt[4], True, False, False, False, 'Pelvis', 0.0)
        # attrVis
        place.optEnum(PawBckLCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            place.addAttribute(PawBckLCt[2], item, 0, 1, False, 'long')

        # BACK R  #
        PawBckR = 'back_paw_R'
        pawBckR = place.Controller(PawBckR, BACK_R_jnt, False, 'pawMaster_ctrl', X * 20, 12, 8, 1, (0, 0, 1), True, True)
        PawBckRCt = pawBckR.createController()
        cmds.parent(PawBckRCt[0], CONTROLS)
        # More parent group Options
        cmds.select(PawBckRCt[0])
        PawBckR_TopGrp2 = place.insert('null', 1, PawBckR + '_TopGrp2')[0][0]
        PawBckR_CtGrp2 = place.insert('null', 1, PawBckR + '_CtGrp2')[0][0]
        PawBckR_TopGrp1 = place.insert('null', 1, PawBckR + '_TopGrp1')[0][0]
        PawBckR_CtGrp1 = place.insert('null', 1, PawBckR + '_CtGrp1')[0][0]
        # set RotateOrders for new groups
        place.setRotOrder(PawBckR_TopGrp2, 2, True)
        # attr
        place.optEnum(PawBckRCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawBckRCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawBckRCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawBckRCt[2] + '.' + item), k=True)
        # parentConstrain top group
        cmds.parentConstraint(MasterCt[4], PawBckR_TopGrp2, mo=True)
        place.parentSwitch('PRNT2_' + PawBckR, PawBckRCt[2], PawBckR_CtGrp2, PawBckR_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        place.parentSwitch('PRNT1_' + PawBckR, PawBckRCt[2], PawBckR_CtGrp1, PawBckR_TopGrp1, PawBckR_CtGrp2, PelvisCt[4], False, False, True, False, 'Pelvis', 0.0)
        place.parentSwitch('PNT_' + PawBckR, PawBckRCt[2], PawBckRCt[1], PawBckRCt[0], PawBckR_CtGrp1, PelvisCt[4], True, False, False, False, 'Pelvis', 0.0)
        # attrVis
        place.optEnum(PawBckRCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            place.addAttribute(PawBckRCt[2], item, 0, 1, False, 'long')

        # FRONT L  #
        PawFrntL = 'front_paw_L'
        pawFrntL = place.Controller(PawFrntL, FRONT_L_jnt, False, 'pawMaster_ctrl', X * 20, 12, 8, 1, (0, 0, 1), True, True)
        PawFrntLCt = pawFrntL.createController()
        cmds.parent(PawFrntLCt[0], CONTROLS)
        # More parent group Options
        cmds.select(PawFrntLCt[0])
        PawFrntL_TopGrp2 = place.insert('null', 1, PawFrntL + '_TopGrp2')[0][0]
        PawFrntL_CtGrp2 = place.insert('null', 1, PawFrntL + '_CtGrp2')[0][0]
        PawFrntL_TopGrp1 = place.insert('null', 1, PawFrntL + '_TopGrp1')[0][0]
        PawFrntL_CtGrp1 = place.insert('null', 1, PawFrntL + '_CtGrp1')[0][0]
        # set RotateOrders for new groups
        place.setRotOrder(PawFrntL_TopGrp2, 2, True)
        # attr
        place.optEnum(PawFrntLCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawFrntLCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawFrntLCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawFrntLCt[2] + '.' + item), k=True)
        # parentConstrain top group, switches
        cmds.parentConstraint(MasterCt[4], PawFrntL_TopGrp2, mo=True)
        place.parentSwitch('PRNT2_' + PawFrntL, PawFrntLCt[2], PawFrntL_CtGrp2, PawFrntL_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        place.parentSwitch('PRNT1_' + PawFrntL, PawFrntLCt[2], PawFrntL_CtGrp1, PawFrntL_TopGrp1, PawFrntL_CtGrp2, ChestCt[4], False, False, True, False, 'Chest', 0.0)
        place.parentSwitch('PNT_' + PawFrntL, PawFrntLCt[2], PawFrntLCt[1], PawFrntLCt[0], PawFrntL_CtGrp1, ChestCt[4], True, False, False, False, 'Chest', 0.0)
        # attrVis
        place.optEnum(PawFrntLCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            place.addAttribute(PawFrntLCt[2], item, 0, 1, False, 'long')

        # FRONT R  #
        PawFrntR = 'front_paw_R'
        pawFrntR = place.Controller(PawFrntR, FRONT_R_jnt, False, 'pawMaster_ctrl', X * 20, 12, 8, 1, (0, 0, 1), True, True)
        PawFrntRCt = pawFrntR.createController()
        cmds.parent(PawFrntRCt[0], CONTROLS)
        # More parent group Options
        cmds.select(PawFrntRCt[0])
        PawFrntR_TopGrp2 = place.insert('null', 1, PawFrntR + '_TopGrp2')[0][0]
        PawFrntR_CtGrp2 = place.insert('null', 1, PawFrntR + '_CtGrp2')[0][0]
        PawFrntR_TopGrp1 = place.insert('null', 1, PawFrntR + '_TopGrp1')[0][0]
        PawFrntR_CtGrp1 = place.insert('null', 1, PawFrntR + '_CtGrp1')[0][0]
        # set RotateOrders for new groups
        place.setRotOrder(PawFrntR_TopGrp2, 2, True)
        # attr
        place.optEnum(PawFrntRCt[2], attr=assist, enum='OPTNS')
        for item in attrCstm:
            cmds.addAttr(PawFrntRCt[2], ln=item, at='float', h=False)
            cmds.setAttr((PawFrntRCt[2] + '.' + item), cb=True)
            cmds.setAttr((PawFrntRCt[2] + '.' + item), k=True)
        # parentConstrain top group, switches
        cmds.parentConstraint(MasterCt[4], PawFrntR_TopGrp2, mo=True)
        place.parentSwitch('PRNT2_' + PawFrntR, PawFrntRCt[2], PawFrntR_CtGrp2, PawFrntR_TopGrp2, MasterCt[4], CogCt[4], False, False, True, True, 'Cog', 0.0)
        place.parentSwitch('PRNT1_' + PawFrntR, PawFrntRCt[2], PawFrntR_CtGrp1, PawFrntR_TopGrp1, PawFrntR_CtGrp2, ChestCt[4], False, False, True, False, 'Chest', 0.0)
        place.parentSwitch('PNT_' + PawFrntR, PawFrntRCt[2], PawFrntRCt[1], PawFrntRCt[0], PawFrntR_CtGrp1, ChestCt[4], True, False, False, False, 'Chest', 0.0)
        # attrVis
        place.optEnum(PawFrntRCt[2], attr=vis, enum='OPTNS')
        for item in attrVis:
            place.addAttribute(PawFrntRCt[2], item, 0, 1, False, 'long')
    cmds.floatField('atom_qrig_conScale', edit=True, v=current_scale)
    if face == False:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt, HipLCt, HipRCt, ShldrLCt, ShldrRCt, PawBckLCt, PawBckRCt, PawFrntLCt, PawFrntRCt,
    else:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt


def buildAppendages(*args):
    '''\n

    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    X = 2.5
    digX = 1.6
    cmds.floatField('atom_qrig_conScale', edit=True, v=X)

    current_ldf_val = cmds.floatField('atom_qls_ldf_floatField', query=True, v=True)
    current_paw_ldf_val = cmds.floatField('atom_paw_qls_ldf_floatField', query=True, v=True)

    # back leg left
    cmds.select('back_hip_jnt_L')
    cmds.select('hip_L', toggle=True)
    cmds.select('back_paw_L', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=1)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Back')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=X * 8.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=X * 3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=X * 20.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=X * 5)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    place.cleanUp('Back_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_L', Ctrl=True)

    place.shapeSize('Back_digit_1_ctrl_L', digX)
    place.shapeSize('Back_digit_2_ctrl_L', digX)

    # back right leg
    cmds.select(cl=True)
    cmds.select('back_hip_jnt_R')
    cmds.select('hip_R', toggle=True)
    cmds.select('back_paw_R', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=2)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Back')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=X * -8.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=X * -3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=X * -20.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=X * -5)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    place.cleanUp('Back_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_R', Ctrl=True)

    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-2)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5.5)

    place.shapeSize('Back_digit_1_ctrl_R', digX)
    place.shapeSize('Back_digit_2_ctrl_R', digX)

    # front left leg
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_L')
    cmds.select('shldr_L', toggle=True)
    cmds.select('front_paw_L', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=3)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=X * 8.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=X * 3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=X * -20.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=X * 5)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    aal.createQuadScapulaRig('front_shoulder_jnt_L', 'shldr_L_Grp', 'scapula_jnt_01_L', 'shldr_L', 'spine_jnt_06', '_L')

    # splitPivot left joint
    aal.splitPivot(pseudoRoot='front_pseudo_ankle_root_jnt_L',
                   attach='front_ankle_jnt_L', aimUp='front_lower_knee_jnt_L', aimDown='front_paw_Fk_jnt_L')

    place.cleanUp('Front_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_L', Ctrl=True)

    place.shapeSize('Front_digit_1_ctrl_L', digX)
    place.shapeSize('Front_digit_2_ctrl_L', digX)

    # front right leg
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_R')
    cmds.select('shldr_R', toggle=True)
    cmds.select('front_paw_R', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=4)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=X * -8.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=X * -3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=X * 20.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=X * -5)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    aal.createQuadScapulaRig('front_shoulder_jnt_R', 'shldr_R_Grp', 'scapula_jnt_01_R', 'shldr_R', 'spine_jnt_06', '_R')

    # splitPivot right joint
    aal.splitPivot(pseudoRoot='front_pseudo_ankle_root_jnt_R',
                   attach='front_ankle_jnt_R', aimUp='front_lower_knee_jnt_R', aimDown='front_paw_Fk_jnt_R')

    place.cleanUp('Front_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_R', Ctrl=True)

    place.shapeSize('Front_digit_1_ctrl_R', digX)
    place.shapeSize('Front_digit_2_ctrl_R', digX)

    # reset some UI vals
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5)
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=current_ldf_val)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=current_paw_ldf_val)

    print '===== Quadriped Leg Build Complete ====='
    cmds.floatField('atom_qrig_conScale', edit=True, v=current_scale)

    quadLimits()


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

    if face == False:
        # tailRig = splnFk.SplineFK('tail','tailDbl_jnt', 'tail_jnt_032', 'mid',
                                    # controllerSize=5, parent1= 'pelvis_Grp', parent2='master_Grp', parentDefault=[1,0], segIteration=6, stretch=0, ik='splineIK')
        tailRig = splnFk.SplineFK('tail', 'tailDbl_jnt', 'tail_jnt_08', 'mid',
                                  controllerSize=20, rootParent='PelvisAttch_CnstGp', parent1='master_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='splineIK')

        # tailRig.placeIkJnts()
        for i in tailRig.topGrp2:
            place.cleanUp(i, World=True)
        #place.cleanUp('tail_mid_UpVctrGdGrp', Ctrl=True)

    # SPINE
    spineName = 'spine'
    spineSize = X * 8
    spineDistance = X * 5
    spineFalloff = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'pelvis_Grp'
    spineEnd = 'chest_Grp'
    spineAttr = 'cog'
    spineRoot = 'root_jnt'
    'spine_S_IK_Jnt'
    spine = ['pelvis_jnt', 'spine_jnt_06']
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
    cmds.setAttr(spineAttr + '.' + spineName + 'Root', 0)
    cmds.setAttr(spineAttr + '.' + spineName + 'Stretch', 0)
    cmds.setAttr(spineAttr + '.ClstrVis', 0)
    cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 1)
    cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrVis', 0)
    cmds.setAttr(spineAttr + '.VctrMidIkBlend', .5)
    cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # NECK
    neckName = 'neck'
    neckSize = X * 6.5
    neckDistance = X * 4
    neckFalloff = 0
    neckPrnt = 'neck_Grp'
    neckStrt = 'neck_Grp'
    neckEnd = 'head_CnstGp'
    neckAttr = 'neck'
    neck = ['neck_jnt_01', 'neck_jnt_05']
    # build spline
    SplineOpts(neckName, neckSize, neckDistance, neckFalloff)
    cmds.select(neck)
    stage.splineStage(4)
    # assemble
    OptAttr(neckAttr, 'NeckSpline')
    cmds.parentConstraint(neckPrnt, neckName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(neckStrt, neckName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(neckEnd, neckName + '_E_IK_PrntGrp')
    place.hijackCustomAttrs(neckName + '_IK_CtrlGrp', neckAttr)
    # set options
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
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(neckName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(neckName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    buildRatEars()


def buildRatEars():
    spine = splnFk.SplineFK('ear_rig_L', 'root_ear_jnt_L', 'ear_04_jnt_L', 'L', rootParent='neck_jnt_06', parent1='neck_jnt_06', controllerSize=15)
    spine = splnFk.SplineFK('ear_rig_R', 'root_ear_jnt_R', 'ear_04_jnt_R', 'R', rootParent='neck_jnt_06', parent1='neck_jnt_06', controllerSize=15)


def harness():
    # surface constraint sets
    '''
    -listStructure = [vertexRoot, vertexAim, vertexUp, skinnedJoint]
    -controller gets placed on each vertex
    -controllers are constrained to vertices
    -rootController is aim constrained at...
    -"skinnedJoint" is constrained to controller sitting on "vertexRoot"
    '''
    bodyHarness = [
        ['harnessBody_Geo.vtx[191]', 'harnessBody_Geo.vtx[195]', 'harnessBody_Geo.vtx[186]', 'bodyHarness_mid_jnt'],
        ['harnessBody_Geo.vtx[60]', 'harnessBody_Geo.vtx[40]', 'harnessBody_Geo.vtx[89]', 'bodyHarness_01_jnt_L'],
        ['harnessBody_Geo.vtx[44]', 'harnessBody_Geo.vtx[153]', 'harnessBody_Geo.vtx[48]', 'bodyHarness_02_jnt_L'],
        ['harnessBody_Geo.vtx[93]', 'harnessBody_Geo.vtx[80]', 'harnessBody_Geo.vtx[118]', 'bodyHarness_03_jnt_L'],
        ['harnessBody_Geo.vtx[187]', 'harnessBody_Geo.vtx[184]', 'harnessBody_Geo.vtx[191]', 'bodyHarness_04_jnt_L'],
        ##['body_Geo.vtx[5308]', 'body_Geo.vtx[5417]', 'body_Geo.vtx[5372]', 'bodyHarness_04_jnt_R'],
        ['harnessBody_Geo.vtx[296]', 'harnessBody_Geo.vtx[283]', 'harnessBody_Geo.vtx[318]', 'bodyHarness_03_jnt_R'],
        ['harnessBody_Geo.vtx[247]', 'harnessBody_Geo.vtx[356]', 'harnessBody_Geo.vtx[251]', 'bodyHarness_02_jnt_R'],
        ['harnessBody_Geo.vtx[263]', 'harnessBody_Geo.vtx[243]', 'harnessBody_Geo.vtx[292]', 'bodyHarness_01_jnt_R']
    ]
    neckHarness = [
        ['harnessBody_Geo.vtx[12]', 'harnessBody_Geo.vtx[197]', 'harnessBody_Geo.vtx[179]', 'neckHarness_mid_jnt'],
        ['harnessHead_Geo.vtx[3]', 'harnessBody_Geo.vtx[141]', 'harnessBody_Geo.vtx[105]', 'neckHarness_01_jnt_L'],
        ##['head_Geo.vtx[47]', 'body_Geo.vtx[2099]', 'body_Geo.vtx[2221]', 'neckHarness_02_jnt_L'],
        ['harnessHead_Geo.vtx[313]', 'harnessBody_Geo.vtx[180]', 'harnessBody_Geo.vtx[196]', 'neckHarness_03_jnt_L'],
        ##['body_Geo.vtx[5889]', 'body_Geo.vtx[6034]', 'body_Geo.vtx[5892]', 'neckHarness_03_jnt_R'],
        ##['body_Geo.vtx[5896]', 'body_Geo.vtx[6027]', 'body_Geo.vtx[6022]', 'neckHarness_02_jnt_R'],
        ['harnessHead_Geo.vtx[317]', 'harnessBody_Geo.vtx[344]', 'harnessBody_Geo.vtx[308]', 'neckHarness_01_jnt_R']
    ]
    headHarness = [
        ['harnessHead_Geo.vtx[243]', 'harnessHead_Geo.vtx[238]', 'harnessHead_Geo.vtx[648]', 'headHarnessNeck_jnt'],
        ['harnessHead_Geo.vtx[291]', 'harnessHead_Geo.vtx[274]', 'harnessHead_Geo.vtx[45]', 'headHarnessNeck_01_jnt_L'],
        ['harnessHead_Geo.vtx[300]', 'harnessHead_Geo.vtx[211]', 'harnessHead_Geo.vtx[179]', 'headHarnessNeck_02_jnt_L'],
        ['harnessHead_Geo.vtx[305]', 'harnessHead_Geo.vtx[172]', 'harnessHead_Geo.vtx[220]', 'headHarnessNeck_03_jnt_L'],
        ##['head_Geo.vtx[3224]', 'head_Geo.vtx[2325]', 'head_Geo.vtx[3222]', 'headHarnessNeck_04_jnt_L'],
        ['harnessHead_Geo.vtx[308]', 'harnessHead_Geo.vtx[577]', 'harnessHead_Geo.vtx[30]', 'headHarnessNeckThroat_jnt'],
        ##['head_Geo.vtx[3227]', 'head_Geo.vtx[7488]', 'head_Geo.vtx[8147]', 'headHarnessNeck_04_jnt_R'],
        ['harnessHead_Geo.vtx[580]', 'harnessHead_Geo.vtx[475]', 'harnessHead_Geo.vtx[521]', 'headHarnessNeck_03_jnt_R'],
        ['harnessHead_Geo.vtx[478]', 'harnessHead_Geo.vtx[597]', 'harnessHead_Geo.vtx[359]', 'headHarnessNeck_02_jnt_R'],
        ['harnessHead_Geo.vtx[598]', 'harnessHead_Geo.vtx[570]', 'harnessHead_Geo.vtx[358]', 'headHarnessNeck_01_jnt_R'],
        ['harnessHead_Geo.vtx[701]', 'harnessHead_Geo.vtx[698]', 'harnessHead_Geo.vtx[643]', 'headHarnessMuzzle_jnt'],
        ##['head_Geo.vtx[3017]', 'head_Geo.vtx[3020]', 'head_Geo.vtx[3031]', 'headHarnessMuzzle_01_jnt_L'],
        ['harnessHead_Geo.vtx[201]', 'harnessHead_Geo.vtx[50]', 'harnessHead_Geo.vtx[100]', 'headHarnessMuzzle_02_jnt_L'],
        ##['head_Geo.vtx[1271]', 'head_Geo.vtx[1324]', 'head_Geo.vtx[1267]', 'headHarnessMuzzle_03_jnt_L'],
        ##['head_Geo.vtx[2217]', 'head_Geo.vtx[2302]', 'head_Geo.vtx[1271]', 'headHarnessMuzzle_04_jnt_L'],
        ##['head_Geo.vtx[2459]', 'head_Geo.vtx[2793]', 'head_Geo.vtx[1220]', 'headHarnessMuzzle_05_jnt_L'],
        ['harnessHead_Geo.vtx[138]', 'harnessHead_Geo.vtx[131]', 'harnessHead_Geo.vtx[737]', 'headHarnessMuzzleJaw_jnt'],
        ##['head_Geo.vtx[7390]', 'head_Geo.vtx[7468]', 'head_Geo.vtx[6172]', 'headHarnessMuzzle_04_jnt_R'],
        ##['head_Geo.vtx[6172]', 'head_Geo.vtx[6225]', 'head_Geo.vtx[6169]', 'headHarnessMuzzle_03_jnt_R'],
        ['harnessHead_Geo.vtx[502]', 'harnessHead_Geo.vtx[503]', 'harnessHead_Geo.vtx[411]', 'headHarnessMuzzle_02_jnt_R']
        ##['head_Geo.vtx[8205]', 'head_Geo.vtx[8208]', 'head_Geo.vtx[8220]', 'headHarnessMuzzle_01_jnt_R'],
        ##['head_Geo.vtx[7627]', 'head_Geo.vtx[7952]', 'head_Geo.vtx[6120]', 'headHarnessMuzzle_05_jnt_R'],
    ]
    accsBodyHarness = [
        ['bodyHarness2x_Geo.vtx[258]', 'bodyHarness2x_Geo.vtx[262]', 'bodyHarness2x_Geo.vtx[257]', 'bodyHarnessHook_jnt_L'],
        ['bodyHarness2x_Geo.vtx[123]', 'bodyHarness2x_Geo.vtx[278]', 'bodyHarness2x_Geo.vtx[124]', 'bodyHarnessPatch_jnt_L'],
        ['bodyHarness2x_Geo.vtx[329]', 'bodyHarness2x_Geo.vtx[326]', 'bodyHarness2x_Geo.vtx[126]', 'bodyHarnessPendant_jnt_L'],
        ['bodyHarness2x_Geo.vtx[741]', 'bodyHarness2x_Geo.vtx[737]', 'bodyHarness2x_Geo.vtx[643]', 'bodyHarnessPendant_jnt_R'],
        ['bodyHarness2x_Geo.vtx[639]', 'bodyHarness2x_Geo.vtx[693]', 'bodyHarness2x_Geo.vtx[640]', 'bodyHarnessPatch_jnt_R'],
        ['bodyHarness2x_Geo.vtx[472]', 'bodyHarness2x_Geo.vtx[709]', 'bodyHarness2x_Geo.vtx[473]', 'bodyHarnessHook_jnt_R']
    ]
    accsNeckHarness = [
        ['bodyHarness1x_Geo.vtx[66]', 'bodyHarness1x_Geo.vtx[71]', 'bodyHarness1x_Geo.vtx[173]', 'neckHarnessPatch_jnt_L'],
        ['bodyHarness1x_Geo.vtx[335]', 'bodyHarness1x_Geo.vtx[339]', 'bodyHarness1x_Geo.vtx[362]', 'neckHarnessPatch_jnt_R']
    ]
    accsHeadHarness = [
        ['headHarness_Geo.vtx[1323]', 'headHarness_Geo.vtx[1378]', 'headHarness_Geo.vtx[1049]', 'headHarnessHook_jnt_L'],
        ['headHarness_Geo.vtx[1341]', 'headHarness_Geo.vtx[1360]', 'headHarness_Geo.vtx[1057]', 'headHarnessHook_jnt_R']
    ]

    #['', '', '', '']

    # name string
    name = ['bodyHrnss', 'neckHrnss', 'headHrnss', 'accsBdyHrnss', 'accsNckHrnss', 'accsHdHrnss']

    # place joints on point pairs
    def surfJnts(name, pairL):
        jntPairs = []
        iks = []
        j = 0
        for pair in pairL:
            jnts = []
            i = 0
            suff = ['_root', '_aim', '_up']
            for point in pair:
                cmds.select(point)
                pos = cmds.xform(point, q=True, t=True, ws=True)
                jnts.append(place.joint(0, name + str(j) + suff[i] + '_jnt', pad=2, rpQuery=False)[0])
                i = i + 1
            j = j + 1
            # parent ik joints
            cmds.parent(jnts[1], jnts[0])
            # orient ik joints
            cmds.joint(jnts[0], e=True, oj='zyx', secondaryAxisOrient='yup')
            jnt.ZeroJointOrient(jnts[1])
            # orient up vector jnt
            cmds.parent(jnts[2], jnts[0])
            jnt.ZeroJointOrient(jnts[2])
            cmds.parent(jnts[2], w=True)
            # append pairs to list
            jntPairs.append(jnts)
            # ik
            ikhndl = cmds.ikHandle(sj=jnts[0], ee=jnts[1], sol='ikRPsolver', sticky='sticky')[0]
            cmds.setAttr(ikhndl + '.visibility', False)
            cmds.poleVectorConstraint(jnts[2], ikhndl)
            iks.append(ikhndl)
            # cleanup
            place.cleanUp(jnts[0], SknJnts=True)
            place.cleanUp(jnts[2], SknJnts=True)
            place.cleanUp(ikhndl, World=True)
        return jntPairs, iks

    def surfCts(name, vertSets):
        '''
        jntsIks[0] = lists of 3 joint sets
        jntsIks[1] = list of ik handles, one for each three joint set
        '''
        #controllers, constraints
        geoParent = []
        j = 0
        for vSet in vertSets:
            i = 0
            setName = ["", "_aim", "_up"]
            rootCtGp = None
            aimCt = None
            upCt = None
            for point in vSet:
                if i < 3:
                    # controller
                    diamond = place.Controller(name + '_' + str(('%0' + str(2) + 'd') % (j)) + setName[i], point, False, 'diamond_ctrl', 5, 12, 8, 1, (0, 0, 1), True, True)
                    DiamondCt = diamond.createController()
                    place.cleanUp(DiamondCt[0], Ctrl=True)
                    cnst = cmds.pointOnPolyConstraint(point, DiamondCt[0])[0]
                    # convert vertex to uv
                    uv = cmds.polyListComponentConversion(point, fv=True, tuv=True)
                    # get uv space
                    space = cmds.polyEditUV(uv, q=True)
                    # set uv attrs on constraint
                    cmds.setAttr(cnst + '.' + point.rsplit('.')[0] + 'U0', space[0])
                    cmds.setAttr(cnst + '.' + point.rsplit('.')[0] + 'V0', space[1])
                    # append geoParent
                    if i == 0:
                        geoParent.append(DiamondCt[4])
                        rootCtGp = DiamondCt[1]
                    elif i == 1:
                        aimCt = DiamondCt[4]
                        cmds.setAttr(DiamondCt[0] + '.visibility', False)
                    elif i == 2:
                        upCt = DiamondCt[4]
                        cmds.setAttr(DiamondCt[0] + '.visibility', False)
                    # constraint
                    '''
                    if i==1:
                        ##ik
                        cmds.pointConstraint(DiamondCt[4], jntsIks[1][j])
                    else:
                        ##joint
                        cmds.pointConstraint(DiamondCt[4], jntsIks[0][j][i])
                        '''
                else:
                    # constrain joint to first controller of vert set list
                    cmds.parentConstraint(geoParent[j], point, mo=True)
                i = i + 1
            # aim constraint
            cmds.aimConstraint(aimCt, rootCtGp, mo=True,
                               aimVector=(0, 0, 1), upVector=(0, 1, 0),
                               worldUpType='object', worldUpObject=upCt)
            j = j + 1
        return geoParent

    #jntsIks = surfJnts(name, vertSets)
    geoParent = surfCts(name[0], bodyHarness)
    geoParent = surfCts(name[1], neckHarness)
    geoParent = surfCts(name[2], headHarness)
    geoParent = surfCts(name[3], accsBodyHarness)
    geoParent = surfCts(name[4], accsNeckHarness)
    geoParent = surfCts(name[5], accsHeadHarness)
    # print jntsIks[0]
    # print jntsIks[1]


def quadLimits():
    # back
    cmds.transformLimits('back_upper_knee_jnt_L', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_lower_knee_jnt_L', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_02_L', rx=[-20, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_01_L', rx=[-20, 360], erx=[1, 0])
    cmds.transformLimits('back_upper_knee_jnt_R', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_lower_knee_jnt_R', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_02_R', rx=[-20, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_01_R', rx=[-20, 360], erx=[1, 0])
    # front
    cmds.transformLimits('front_upper_knee_jnt_L', rx=[-360, 8], erx=[0, 1])
    cmds.transformLimits('front_lower_knee_jnt_L', rx=[-360, 8], erx=[0, 1])
    cmds.transformLimits('front_mid_phal_jnt_02_L', rx=[-15, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_01_L', rx=[-15, 360], erx=[1, 0])
    cmds.transformLimits('front_upper_knee_jnt_R', rx=[-360, 8], erx=[0, 1])
    cmds.transformLimits('front_lower_knee_jnt_R', rx=[-360, 8], erx=[0, 1])
    cmds.transformLimits('front_mid_phal_jnt_02_R', rx=[-15, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_01_R', rx=[-15, 360], erx=[1, 0])
