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
        COG_jnt='pelvis_jnt', PELVIS_jnt='pelvis_jnt', CHEST_jnt='spine_04_JNT', NECK_jnt='neck_00_JNT', HEAD_jnt='head_JNT',
        HIP_L_jnt='back_hip_jnt_L', HIP_R_jnt='back_hip_jnt_R',
        SHLDR_L_jnt='shoulder_L_JNT', SHLDR_R_jnt='shoulder_R_JNT',
        BACK_L_jnt='back_foot_ctrl_placement_jnt_L', BACK_R_jnt='back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt='front_foot_ctrl_placement_jnt_L', FRONT_R_jnt='front_foot_ctrl_placement_jnt_R',
        TAIL_jnt='tail_00_JNT', TAILTIP_jnt='tail19', GEO_gp='mesh', SKIN_jnt='pelvis_jnt'):
    '''\n

    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=.3)

    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    print X
    if check == 0:
        face = False
    else:
        face = True

    PreBuild = place.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=70)
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # cmds.parent(SKIN_jnt, SKIN_JOINTS)
    # cmds.parent(GEO_gp, GEO)

    # COG #
    Cog = 'cog'
    cog = place.Controller(Cog, COG_jnt, False, 'facetZup_ctrl', X * 40, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # PELVIS/CHEST #
    ## PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'pelvis_ctrl', X * 3.5, 17, 8, 1, (0, 0, 1), True, True)
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
    chest = place.Controller(Chest, CHEST_jnt, False, 'chest_ctrl', X * 4.25, 17, 8, 1, (0, 0, 1), True, True)
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
    neck = place.Controller(Neck, NECK_jnt, True, 'GDneck_ctrl', X * 5, 12, 8, 1, (0, 0, 1), True, True)
    NeckCt = neck.createController()
    place.setRotOrder(NeckCt[0], 2, True)
    # parent switches
    place.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], ChestAttch_CnstGp, False, True, False, True, 'Chest', w=0)
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
    cmds.orientConstraint(HeadCt[3], NECK_jnt, mo=True)
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

    if not face:
        pass
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

        # SHOULDER L #
        shldrL = 'shldr_L'
        shldrL = place.Controller(shldrL, SHLDR_L_jnt, False, 'facetXup_ctrl', X * 21, 17, 8, 1, (0, 0, 1), True, True)
        ShldrLCt = shldrL.createController()
        place.setRotOrder(ShldrLCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrLCt[0], mo=True)

        scapStrtchL = cmds.parentConstraint(ShldrLCt[4], 'shoulder_dbl_jnt_L', mo=True)[0]
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
        shldrR = place.Controller(shldrR, SHLDR_R_jnt, False, 'facetXup_ctrl', X * 21, 17, 8, 1, (0, 0, 1), True, True)
        ShldrRCt = shldrR.createController()
        place.setRotOrder(ShldrRCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrRCt[0], mo=True)

        scapStrtchR = cmds.parentConstraint(ShldrRCt[4], 'shoulder_dbl_jnt_R', mo=True)[0]
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
        pawBckL = place.Controller(PawBckL, BACK_L_jnt, False, 'diamond_ctrl', X * 20.5, 12, 8, 1, (0, 0, 1), True, True)
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
        pawBckR = place.Controller(PawBckR, BACK_R_jnt, False, 'diamond_ctrl', X * 20.5, 12, 8, 1, (0, 0, 1), True, True)
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
        PawFrntL = 'wing_L'
        pawFrntL = place.Controller(PawFrntL, FRONT_L_jnt, True, 'GDchest_ctrl', X * 2.5, 12, 8, 1, (0, 0, 1), True, True)
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
        # place.optEnum(PawFrntLCt[2], attr=assist, enum='OPTNS')
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
        PawFrntR = 'wing_R'
        pawFrntR = place.Controller(PawFrntR, FRONT_R_jnt, True, 'GDchest_ctrl', X * 2.5, 12, 8, 1, (0, 0, 1), True, True)
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
        # place.optEnum(PawFrntRCt[2], attr=assist, enum='OPTNS')
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

    buildAppendages()

    if face == False:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt, ShldrLCt, ShldrRCt, PawFrntLCt, PawFrntRCt, pawBckL, PawBckRCt, PawBckLCt
    else:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt


def buildAppendages(*args):
    '''\n

    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=.2)

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
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=1.25)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=3.5)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=1)
    aal.createReverseLeg(traversDepth=3)
    place.cleanUp('Back_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_L', Ctrl=True)

    # back right leg
    cmds.select(cl=True)
    cmds.select('back_hip_jnt_R')
    cmds.select('hip_R', toggle=True)
    cmds.select('back_paw_R', toggle=True)
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=2)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Back')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-1.25)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=-3.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=-3.5)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=-1)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    place.cleanUp('Back_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_R', Ctrl=True)

    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-2)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5.5)

    # front left wing
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=3)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=1.5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=1.5)
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=-8.5)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=1)
    # pv
    flipVal = []
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v1=True))
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v2=True))
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v3=True))
    ankle_pv_loc = aal.create_3_joint_pv('shoulder_L_JNT', 'hand_L_JNT', 'Front', 'L', 'wing', 'atom_qls_limbRot_radioButtonGrp', 'atom_qls_limbAim_radioButtonGrp',
                                         'atom_qls_limbUp_radioButtonGrp', -8.5, 12, None, True, flipVal)
    pvElbow_L = place.Controller('pvElbow_L', 'Front_uperarm_L_JNT_pv_loc_L', False, 'diamond_ctrl', 6, 17, 8, 1, (0, 0, 1), True, True)
    pvElbow_L_Ct = pvElbow_L.createController()
    cmds.parent(ankle_pv_loc, pvElbow_L_Ct[4])
    cmds.parentConstraint('cog_Grp', pvElbow_L_Ct[0], mo=True)
    cmds.setAttr(ankle_pv_loc + '.visibility', 0)
    # ik
    ankleIkh = aal.create_ik('shoulder_L_JNT', 'hand_L_JNT', 'Front', 'L', 'wing', None, False, True)
    # pv constraint
    ankle_pvc = cmds.poleVectorConstraint(ankle_pv_loc, ankleIkh[0][0])
    # wrist
    wrist_L = place.Controller('wrist_L', 'hand_L_JNT', True, 'diamond_ctrl', 6, 17, 8, 1, (0, 0, 1), True, True)
    wrist_L_Ct = wrist_L.createController()
    cmds.parentConstraint('wing_L_Grp', wrist_L_Ct[0], mo=True)
    # reverse aim
    null = place.null2('reverseWrist_L', 'front_foot_ctrl_placement_jnt_L')[0]
    cmds.aimConstraint(wrist_L_Ct[4], null, wut='object', wuo='wing_L_jnt', aim=[0, 0, -1], u=[1, 0, 0], mo=True)
    cmds.parent(null, 'wing_L_Grp')
    cmds.parent(ankleIkh[0][0], null)

    aal.createQuadScapulaRig('shoulder_L_JNT', 'shldr_L_Grp', 'scapula_jnt_01_L', 'shldr_L', 'spine_05_JNT', '_L')

    place.cleanUp('Front_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_L', Ctrl=True)

    # front right wing
    idx = cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=4)
    atom_prefix_textField = cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-1.5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=-1.5)
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=3.5)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=-1)
    # pv
    flipVal = []
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v1=True))
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v2=True))
    flipVal.append(cmds.checkBoxGrp('atom_qls_flip_checkBoxGrp', query=True, v3=True))
    ankle_pv_loc = aal.create_3_joint_pv('shoulder_R_JNT', 'hand_R_JNT', 'Front', 'R', 'wing', 'atom_qls_limbRot_radioButtonGrp', 'atom_qls_limbAim_radioButtonGrp',
                                         'atom_qls_limbUp_radioButtonGrp', 8.5, 12, None, True, flipVal)
    pvElbow_R = place.Controller('pvElbow_R', 'Front_uperarm_R_JNT_pv_loc_R', False, 'diamond_ctrl', 6, 17, 8, 1, (0, 0, 1), True, True)
    pvElbow_R_Ct = pvElbow_R.createController()
    cmds.parent(ankle_pv_loc, pvElbow_R_Ct[4])
    cmds.parentConstraint('cog_Grp', pvElbow_R_Ct[0], mo=True)
    cmds.setAttr(ankle_pv_loc + '.visibility', 0)
    # ik
    ankleIkh = aal.create_ik('shoulder_R_JNT', 'hand_R_JNT', 'Front', 'R', 'wing', None, False, True)
    # pv constraint
    ankle_pvc = cmds.poleVectorConstraint(ankle_pv_loc, ankleIkh[0][0])
    # wrist
    wrist_R = place.Controller('wrist_R', 'hand_R_JNT', True, 'diamond_ctrl', 6, 17, 8, 1, (0, 0, 1), True, True)
    wrist_R_Ct = wrist_R.createController()
    cmds.parentConstraint('wing_R_Grp', wrist_R_Ct[0], mo=True)
    # reverse aim
    null = place.null2('reverseWrist_R', 'front_foot_ctrl_placement_jnt_R')[0]
    cmds.aimConstraint(wrist_R_Ct[4], null, wut='object', wuo='wing_R_jnt', aim=[0, 0, 1], u=[-1, 0, 0], mo=True)
    cmds.parent(null, 'wing_R_Grp')
    cmds.parent(ankleIkh[0][0], null)

    aal.createQuadScapulaRig('shoulder_R_JNT', 'shldr_R_Grp', 'scapula_jnt_01_R', 'shldr_R', 'spine_05_JNT', '_R')

    place.cleanUp('Front_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_R', Ctrl=True)

    # reset some UI vals
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5)
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=current_ldf_val)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=current_paw_ldf_val)

    # quadLimits()


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

    # Tail
    tailRig = splnFk.SplineFK('tail', 'tailRoot_JNT', 'tail_03_JNT', 'mid',
                              controllerSize=3, rootParent='PelvisAttch_CnstGp', parent1='master_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # Tongue
    tailRig = splnFk.SplineFK('tongue', 'tongue_01_JNT', 'tongue_06_JNT', 'mid',
                              controllerSize=4, rootParent='lower_jaw_01_JNT', parent1='head_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # jaw
    tailRig = splnFk.SplineFK('jaw', 'lower_jaw_01_JNT', 'lower_jaw_03_JNT', 'mid',
                              controllerSize=5, rootParent='head_Grp', parent1='neck_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # make parent group, cog orient, hand position
    null = place.null2('digitParent_L', 'reverseWrist_L')[0]
    cmds.setAttr(null + '.rotateOrder', 2)
    cmds.parent(null, 'reverseWrist_L')
    cmds.orientConstraint('cog_Grp', null, mo=False)
    # hand_Carpal_01_L
    tailRig = splnFk.SplineFK('hand_Carpal_01_L', 'hand_Carpal_01_dbl_L_JNT', 'hand_finger1_04_L_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_L', parent1=null, parent2='wing_L_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_02_L
    tailRig = splnFk.SplineFK('hand_Carpal_02_L', 'hand_Carpal_02_dbl_L_JNT', 'hand_finger2_04_L_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_L', parent1=null, parent2='wing_L_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_03_L
    tailRig = splnFk.SplineFK('hand_Carpal_03_L', 'hand_Carpal_03_dbl_L_JNT', 'hand_finger3_04_L_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_L', parent1=null, parent2='wing_L_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_04_L
    tailRig = splnFk.SplineFK('hand_Carpal_04_L', 'hand_Carpal_04_dbl_L_JNT', 'hand_finger4_03_L_JNT', 'left',
                              controllerSize=5, rootParent='reverseWrist_L', parent1=null, parent2='wing_L_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_01_R
    tailRig = splnFk.SplineFK('hand_Carpal_01_R', 'hand_Carpal_01_dbl_R_JNT', 'hand_finger1_03_R_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_R', parent1='cog_Grp', parent2='wing_R_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_02_R
    tailRig = splnFk.SplineFK('hand_Carpal_02_R', 'hand_Carpal_02_dbl_R_JNT', 'hand_finger2_03_R_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_R', parent1='cog_Grp', parent2='wing_R_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_03_R
    tailRig = splnFk.SplineFK('hand_Carpal_03_R', 'hand_Carpal_03_dbl_R_JNT', 'hand_finger3_03_R_JNT', 'left',
                              controllerSize=1.5, rootParent='reverseWrist_R', parent1='cog_Grp', parent2='wing_R_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # hand_Carpal_04_R
    tailRig = splnFk.SplineFK('hand_Carpal_04_R', 'hand_Carpal_04_dbl_R_JNT', 'hand_finger4_03_R_JNT', 'left',
                              controllerSize=5, rootParent='reverseWrist_R', parent1='cog_Grp', parent2='wing_R_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='ik')
    for i in tailRig.topGrp2:
        place.cleanUp(i, World=True)

    # SPINE
    spineName = 'spine'
    spineSize = 1
    spineDistance = 7
    spineFalloff = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'pelvis_Grp'
    spineEnd = 'chest_Grp'
    spineAttr = 'cog'
    spineRoot = 'pelvis_jnt'
    # 'spine_S_IK_Jnt'
    spine = ['spine_00_JNT', 'spine_04_JNT']
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

    # NECK
    neckName = 'neck'
    neckSize = 1
    neckDistance = 7
    neckFalloff = 0
    neckPrnt = 'neck_Grp'
    neckStrt = 'neck_Grp'
    neckEnd = 'head_CnstGp'
    neckAttr = 'neck'
    neck = ['neck_00_JNT', 'neck_04_JNT']
    # build spline
    SplineOpts(neckName, neckSize, neckDistance, neckFalloff)
    cmds.select(neck)
    stage.splineStage(4)
    # assemble
    OptAttr(neckAttr, 'NeckSpline')
    cmds.parentConstraint(neckPrnt, neckName + '_IK_CtrlGrp')
    cmds.parentConstraint(neckStrt, neckName + '_S_IK_PrntGrp')
    cmds.parentConstraint(neckEnd, neckName + '_E_IK_PrntGrp')
    place.hijackCustomAttrs(neckName + '_IK_CtrlGrp', neckAttr)
    # set options
    cmds.setAttr(neckAttr + '.' + neckName + 'Vis', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Root', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Stretch', 0)
    cmds.setAttr(neckAttr + '.ClstrVis', 1)
    cmds.setAttr(neckAttr + '.ClstrMidIkBlend', 1)
    cmds.setAttr(neckAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrVis', 0)
    cmds.setAttr(neckAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(neckAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(neckName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(neckName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # WINGS
    wingSize = 0.75
    wingDistance = 3.5
    # In #
    wingIn = 'wingInFlap_L'
    cog = place.Controller(wingIn, 'wing_L_jnt', False, 'facetZup_ctrl', 9, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], '___CONTROLS')
    cmds.parentConstraint('wing_L_Grp', CogCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], 'wing_L_jnt', mo=True)

    # wingIn L
    wingInName = 'wingIn_L'
    wingInSize = wingSize
    wingInDistance = wingDistance
    wingInFalloff = 0
    wingInPrnt = 'wing_L_jnt'
    wingInStrt = 'wing_L_jnt'
    wingInEnd = 'spine_00_JNT'
    wingInAttr = wingIn
    wingIn = ['wingIn_L_jnt_01', 'wingIn_L_jnt_09']
    # build spline
    SplineOpts(wingInName, wingInSize, wingInDistance, wingInFalloff)
    cmds.select(wingIn)
    stage.splineStage(4)
    # assemble
    OptAttr(wingInAttr, 'WingInSpline')
    cmds.parentConstraint(wingInPrnt, wingInName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(wingInStrt, wingInName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(wingInEnd, wingInName + '_E_IK_PrntGrp', mo=True)
    place.hijackCustomAttrs(wingInName + '_IK_CtrlGrp', wingInAttr)
    # set options
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Vis', 0)
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Root', 0)
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Stretch', 1)
    cmds.setAttr(wingInAttr + '.ClstrVis', 1)
    cmds.setAttr(wingInAttr + '.ClstrMidIkBlend', 0)
    cmds.setAttr(wingInAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(wingInAttr + '.VctrVis', 0)
    cmds.setAttr(wingInAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(wingInAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(wingInAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(wingInAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(wingInName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(wingInName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # Out #
    wingIn = 'wingOutFlap_L'
    cog = place.Controller(wingIn, 'wing_L_jnt', False, 'facetZup_ctrl', 9.5, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], '___CONTROLS')
    cmds.parentConstraint('wing_L_Grp', CogCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], 'wing_L_jnt', mo=True)

    # wingOut L
    wingOutName = 'wingOut_L'
    wingOutSize = wingSize
    wingOutDistance = wingDistance
    wingOutFalloff = 0
    wingOutPrnt = 'wing_L_jnt'
    wingOutStrt = 'wing_L_jnt'
    wingOutEnd = 'hand_finger4_03_L_JNT'
    wingOutAttr = wingIn
    wingOut = ['wingOut_L_jnt_01', 'wingOut_L_jnt_09']
    # build spline
    SplineOpts(wingOutName, wingOutSize, wingOutDistance, wingOutFalloff)
    cmds.select(wingOut)
    stage.splineStage(4)
    # assemble
    OptAttr(wingOutAttr, 'WingInSpline')
    cmds.parentConstraint(wingOutPrnt, wingOutName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(wingOutStrt, wingOutName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(wingOutEnd, wingOutName + '_E_IK_PrntGrp', mo=True)
    place.hijackCustomAttrs(wingOutName + '_IK_CtrlGrp', wingOutAttr)
    # set options
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Vis', 0)
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Root', 0)
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Stretch', 1)
    cmds.setAttr(wingOutAttr + '.ClstrVis', 1)
    cmds.setAttr(wingOutAttr + '.ClstrMidIkBlend', 0)
    cmds.setAttr(wingOutAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(wingOutAttr + '.VctrVis', 0)
    cmds.setAttr(wingOutAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(wingOutAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(wingOutAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(wingOutAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(wingOutName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(wingOutName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    #

    # WINGS
    # In #
    wingIn = 'wingInFlap_R'
    cog = place.Controller(wingIn, 'wing_R_jnt', False, 'facetZup_ctrl', 9, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], '___CONTROLS')
    cmds.parentConstraint('wing_R_Grp', CogCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], 'wing_R_jnt', mo=True)

    # wingIn R
    wingInName = 'wingIn_R'
    wingInSize = wingSize
    wingInDistance = wingDistance
    wingInFalloff = 0
    wingInPrnt = 'wing_R_jnt'
    wingInStrt = 'wing_R_jnt'
    wingInEnd = 'spine_00_JNT'
    wingInAttr = wingIn
    wingIn = ['wingIn_R_jnt_01', 'wingIn_R_jnt_09']
    # build spline
    SplineOpts(wingInName, wingInSize, wingInDistance, wingInFalloff)
    cmds.select(wingIn)
    stage.splineStage(4)
    # assemble
    OptAttr(wingInAttr, 'WingInSpline')
    cmds.parentConstraint(wingInPrnt, wingInName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(wingInStrt, wingInName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(wingInEnd, wingInName + '_E_IK_PrntGrp', mo=True)
    place.hijackCustomAttrs(wingInName + '_IK_CtrlGrp', wingInAttr)
    # set options
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Vis', 0)
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Root', 0)
    cmds.setAttr(wingInAttr + '.' + wingInName + 'Stretch', 1)
    cmds.setAttr(wingInAttr + '.ClstrVis', 1)
    cmds.setAttr(wingInAttr + '.ClstrMidIkBlend', 0)
    cmds.setAttr(wingInAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(wingInAttr + '.VctrVis', 0)
    cmds.setAttr(wingInAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(wingInAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(wingInAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(wingInAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(wingInName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(wingInName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # Out #
    wingIn = 'wingOutFlap_R'
    cog = place.Controller(wingIn, 'wing_R_jnt', False, 'facetZup_ctrl', 9.5, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], '___CONTROLS')
    cmds.parentConstraint('wing_R_Grp', CogCt[0], mo=True)
    cmds.parentConstraint(CogCt[4], 'wing_R_jnt', mo=True)

    # wingOut R
    wingOutName = 'wingOut_R'
    wingOutSize = wingSize
    wingOutDistance = wingDistance
    wingOutFalloff = 0
    wingOutPrnt = 'wing_R_jnt'
    wingOutStrt = 'wing_R_jnt'
    wingOutEnd = 'hand_finger4_03_R_JNT'
    wingOutAttr = wingIn
    wingOut = ['wingOut_R_jnt_01', 'wingOut_R_jnt_09']
    # build spline
    SplineOpts(wingOutName, wingOutSize, wingOutDistance, wingOutFalloff)
    cmds.select(wingOut)
    stage.splineStage(4)
    # assemble
    OptAttr(wingOutAttr, 'WingInSpline')
    cmds.parentConstraint(wingOutPrnt, wingOutName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(wingOutStrt, wingOutName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(wingOutEnd, wingOutName + '_E_IK_PrntGrp', mo=True)
    place.hijackCustomAttrs(wingOutName + '_IK_CtrlGrp', wingOutAttr)
    # set options
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Vis', 0)
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Root', 0)
    cmds.setAttr(wingOutAttr + '.' + wingOutName + 'Stretch', 1)
    cmds.setAttr(wingOutAttr + '.ClstrVis', 1)
    cmds.setAttr(wingOutAttr + '.ClstrMidIkBlend', 0)
    cmds.setAttr(wingOutAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(wingOutAttr + '.VctrVis', 0)
    cmds.setAttr(wingOutAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(wingOutAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(wingOutAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(wingOutAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(wingOutName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(wingOutName + '_E_IK_Cntrl.LockOrientOffOn', 1)
