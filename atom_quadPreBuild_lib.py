import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')


def quadPreBuild(
        COG_jnt='spine_jnt_01', PELVIS_jnt='pelvis_jnt', CHEST_jnt='spine_jnt_06', NECK_jnt='neck_jnt_01', HEAD_jnt='neck_jnt_06',
        HIP_L_jnt='back_hip_jnt_L', HIP_R_jnt='back_hip_jnt_R',
        SHLDR_L_jnt='front_shoulder_jnt_L', SHLDR_R_jnt='front_shoulder_jnt_R',
        BACK_L_jnt='back_foot_ctrl_placement_jnt_L', BACK_R_jnt='back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt='front_foot_ctrl_placement_jnt_L', FRONT_R_jnt='front_foot_ctrl_placement_jnt_R',
        TAIL_jnt='tail_jnt_01', TAILTIP_jnt='tail_jnt_011', GEO_gp='buddy_GP', SKIN_jnt='root_jnt'):

    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    if check == 0:
        face = False
    else:
        face = True

    PreBuild = place.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=110)
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
    cog = place.Controller(Cog, COG_jnt, False, 'cog_ctrl', X * 3.5, 12, 8, 1, (0, 0, 1), True, True)
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
    chest = place.Controller(Chest, CHEST_jnt, False, 'chest_ctrl', X * 3.5, 17, 8, 1, (0, 0, 1), True, True)
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
    head = place.Controller(Head, HEAD_jnt, False, 'head_ctrl', X * 3.5, 12, 8, 1, (0, 0, 1), True, True)
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
        hipL = place.Controller(hipL, HIP_L_jnt, False, 'diamond_ctrl', X * 5, 17, 8, 1, (0, 0, 1), True, True)
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
        hipR = place.Controller(hipR, HIP_R_jnt, False, 'diamond_ctrl', X * 5, 17, 8, 1, (0, 0, 1), True, True)
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
        shldrL = place.Controller(shldrL, SHLDR_L_jnt, False, 'shldrL_ctrl', X * 15, 17, 8, 1, (0, 0, 1), True, True)
        ShldrLCt = shldrL.createController()
        place.setRotOrder(ShldrLCt[0], 2, True)
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
        shldrR = place.Controller(shldrR, SHLDR_R_jnt, False, 'shldrR_ctrl', X * 15, 17, 8, 1, (0, 0, 1), True, True)
        ShldrRCt = shldrR.createController()
        place.setRotOrder(ShldrRCt[0], 2, True)
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
        pawBckL = place.Controller(PawBckL, BACK_L_jnt, False, 'pawMaster_ctrl', X * 22, 12, 8, 1, (0, 0, 1), True, True)
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
        pawBckR = place.Controller(PawBckR, BACK_R_jnt, False, 'pawMaster_ctrl', X * 22, 12, 8, 1, (0, 0, 1), True, True)
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
        pawFrntL = place.Controller(PawFrntL, FRONT_L_jnt, False, 'pawMaster_ctrl', X * 22, 12, 8, 1, (0, 0, 1), True, True)
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
        pawFrntR = place.Controller(PawFrntR, FRONT_R_jnt, False, 'pawMaster_ctrl', X * 22, 12, 8, 1, (0, 0, 1), True, True)
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

        # TAIL #
        if cmds.objExists(TAIL_jnt):
            Tail = 'tail'
            tailMaster = place.Controller(Tail, TAIL_jnt, True, 'tailMaster_ctrl', X * 3.5, 12, 8, 1, (0, 0, 1), True, True)
            TailCt = tailMaster.createController()
            cmds.parent(TailCt[0], CONTROLS)
            place.setRotOrder(TailCt[0], 2, True)
            place.parentSwitch(Tail, TailCt[2], TailCt[1], TailCt[0], CogCt[4], PelvisAttch_CnstGp, False, True, False, True, 'Pelvis')
            cmds.parentConstraint(PelvisAttch_CnstGp, TailCt[0], mo=True)
            place.setChannels(TailCt[0], [False, False], [False, False], [True, False], [True, False, False])
            place.setChannels(TailCt[1], [True, False], [False, False], [True, False], [True, False, False])
            place.setChannels(TailCt[2], [True, False], [False, True], [True, False], [True, False, False])
            place.setChannels(TailCt[3], [True, False], [False, True], [True, False], [False, False, False])
            cmds.setAttr(TailCt[3] + '.visibility', cb=False)
            place.setChannels(TailCt[4], [True, False], [False, True], [True, False], [True, False, False])
        else:
            TailCt = None

        # TAIL TIP #
        if cmds.objExists(TAILTIP_jnt):
            TailTip = 'tailTip'
            tailTip = place.Controller(TailTip, TAILTIP_jnt, True, 'tailMaster_ctrl', X * 2.0, 17, 8, 1, (0, 0, 1), True, True)
            TailTipCt = tailTip.createController()
            cmds.parent(TailTipCt[0], CONTROLS)
            place.setRotOrder(TailTipCt[0], 2, True)
            place.parentSwitch(TailTip, TailTipCt[2], TailTipCt[1], TailTipCt[0], CogCt[4], TailCt[4], False, False, True, True, 'Tail', 0)
            cmds.parentConstraint(TailCt[4], TailTipCt[0], mo=True)
            place.setChannels(TailTipCt[0], [False, False], [False, False], [True, False], [True, False, False])
            place.setChannels(TailTipCt[1], [False, False], [False, False], [True, False], [True, False, False])
            place.setChannels(TailTipCt[2], [False, True], [False, True], [True, False], [True, False, False])
            place.setChannels(TailTipCt[3], [False, True], [False, True], [True, False], [False, False, False])
            cmds.setAttr(TailTipCt[3] + '.visibility', cb=False)
            place.setChannels(TailTipCt[4], [True, False], [False, True], [True, False], [True, False, False])
        else:
            TailTipCt = None

    if face == False:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt, HipLCt, HipRCt, ShldrLCt, ShldrRCt, PawBckLCt, PawBckRCt, PawFrntLCt, PawFrntRCt, TailCt, TailTipCt
    else:
        return MasterCt, CogCt, PelvisCt, ChestCt, NeckCt, HeadCt
