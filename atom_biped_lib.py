from pymel.core import *
import maya.cmds as cmds
#
import webrImport as web
# web
aal = web.mod('atom_appendage_lib')
aul = web.mod('atom_ui_lib')
place = web.mod('atom_place_lib')
# misc = web.mod('atom_miscellaneous_lib')
stage = web.mod('atom_splineStage_lib')
splnFk = web.mod('atom_splineFk_lib')
abl = web.mod('atom_body_lib')


def preBuild(
        COG_jnt='spine_jnt_01', PELVIS_jnt='pelvis_jnt', CHEST_jnt='spine_jnt_06', NECK_jnt='neck_jnt_01', HEAD_jnt='neck_jnt_06',
        HIP_L_jnt='back_hip_jnt_L', HIP_R_jnt='back_hip_jnt_R',
        SHLDR_L_jnt='front_shoulder_jnt_L', SHLDR_R_jnt='front_shoulder_jnt_R',
        BACK_L_jnt='back_foot_ctrl_placement_jnt_L', BACK_R_jnt='back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt='front_foot_ctrl_placement_jnt_L', FRONT_R_jnt='front_foot_ctrl_placement_jnt_R',
        TAIL_jnt='tail_jnt_01', TAILTIP_jnt='tail_jnt_011', GEO_gp='buddy_GP', SKIN_jnt='root_jnt'):
    '''\n
    tail_jnt_01 -->> pelvis_jnt
    '''
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=1)

    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    print X
    if check == 0:
        face = False
    else:
        face = True

    # delta mush
    # cmds.deltaMush('Plane002',smoothingIterations=2, smoothingStep=0.5, pinBorderVertices=1, envelope=1)
    cmds.deltaMush('Group60400', smoothingIterations=8, smoothingStep=0.5, pinBorderVertices=1, envelope=1)

    PreBuild = place.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=150)
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    cmds.parent(SKIN_jnt, SKIN_JOINTS)
    # cmds.parent(GEO_gp, GEO)

    # COG #
    Cog = 'cog'
    cog = place.Controller(Cog, COG_jnt, False, 'facetYup_ctrl', X * 75, 12, 8, 1, (0, 0, 1), True, True)
    CogCt = cog.createController()
    place.setRotOrder(CogCt[0], 2, True)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # PELVIS/CHEST #
    ## PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller(Pelvis, PELVIS_jnt, False, 'biped_hip', X * 3.5, 17, 8, 1, (0, 0, 1), True, True)
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

    ## CUSTOM CHEST PIVOT ##
    cstmCt = place.Controller(name='chest_bend', obj='chest_bend_jnt', orient=True, shape='facetYup_ctrl', size=X * 60, color=17, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
    cstm = cstmCt.createController()
    cmds.parentConstraint(CogCt[4], cstm[0], mo=True)
    cmds.parent(cstm[0], CONTROLS)
    # cmds.delete('chest_bend_jnt')

    ## CHEST ##
    Chest = 'chest'
    chest = place.Controller(Chest, CHEST_jnt, False, 'GDchest_ctrl', X * 7.5, 17, 8, 1, (0, 0, 1), True, True)
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
    cmds.parentConstraint(cstm[4], ChestCt[0], mo=True)
    # setChannels
    place.setChannels(PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False])
    # place.setChannels(PelvisCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels(PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[0], [False, False], [False, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[1], [True, False], [False, False], [True, False], [True, False, False])
    place.setChannels(ChestCt[2], [False, True], [False, True], [True, False], [True, False, False])
    # place.setChannels(ChestCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels(ChestCt[4], [True, False], [True, False], [True, False], [True, False, False])
    # parent topGp to master
    cmds.parent(PelvisCt[0], CONTROLS)
    cmds.parent(ChestCt[0], CONTROLS)

    # NECK #
    Neck = 'neck'
    neck = place.Controller(Neck, NECK_jnt, True, 'GDneck_ctrl', X * 4, 12, 8, 1, (0, 0, 1), True, True)
    NeckCt = neck.createController()
    place.setRotOrder(NeckCt[0], 2, True)
    # parent switches
    place.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], ChestAttch_CnstGp, False, True, False, True, 'Chest', 0.0)
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
    head = place.Controller(Head, HEAD_jnt, False, 'biped_head', X * 3.5, 12, 8, 1, (0, 0, 1), True, True)
    HeadCt = head.createController()
    place.setRotOrder(HeadCt[0], 2, True)
    # parent switch
    place.parentSwitch(Head, HeadCt[2], HeadCt[1], HeadCt[0], CogCt[4], NeckCt[4], False, False, True, True, 'Neck', 1.0)
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

    # BasicFace
    jw = 'jaw_jnt'
    if cmds.objExists(jw):
        jawCt = jaw(jw)
        cmds.parent(jawCt, CONTROLS)
    eye = 'eye_jnt_L'
    if cmds.objExists(eye):
        grps = lids()
        cmds.parent(grps, CONTROLS)

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

        # SHOULDER L #
        shldrL = 'shldr_L'
        shldrL = place.Controller(shldrL, SHLDR_L_jnt, False, 'shldrL_ctrl', X * 25, 17, 8, 1, (0, 0, 1), True, True)
        ShldrLCt = shldrL.createController()
        place.setRotOrder(ShldrLCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrLCt[0], mo=True)
        # scap stretch
        scapStrtchL = cmds.parentConstraint(ShldrLCt[4], 'front_shoulder_dbl_jnt_L', mo=True)[0]
        UsrAttrL = cmds.listAttr(scapStrtchL, ud=True)[0]
        cmds.addAttr(scapStrtchL + '.' + UsrAttrL, e=True, max=1)
        place.hijackAttrs(scapStrtchL, ShldrLCt[2], UsrAttrL, 'ScapulaStretch', default=1)
        # clav stretch
        clavStrtchL = cmds.parentConstraint(ShldrLCt[4], 'clavicle_jnt_03_L', mo=True)[0]
        UsrAttrL = cmds.listAttr(clavStrtchL, ud=True)[0]
        cmds.addAttr(clavStrtchL + '.' + UsrAttrL, e=True, max=1)
        place.hijackAttrs(clavStrtchL, ShldrLCt[2], UsrAttrL, 'ClavicleStretch', default=0)
        #
        cmds.parent(ShldrLCt[0], CONTROLS)
        place.setChannels(ShldrLCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[2], [False, True], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrLCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrLCt[3] + '.visibility', cb=False)
        place.setChannels(ShldrLCt[4], [True, False], [True, False], [True, False], [True, False, False])
        # cmds.setAttr(ShldrLCt[2] + '.tx', l=True, k=False)
        # cmds.setAttr(ShldrLCt[3] + '.tx', l=True, k=False)

        # SHOULDER R #
        shldrR = 'shldr_R'
        shldrR = place.Controller(shldrR, SHLDR_R_jnt, False, 'shldrR_ctrl', X * 25, 17, 8, 1, (0, 0, 1), True, True)
        ShldrRCt = shldrR.createController()
        place.setRotOrder(ShldrRCt[0], 2, True)
        cmds.parentConstraint(ChestAttch_CnstGp, ShldrRCt[0], mo=True)
        # scap stretch
        scapStrtchR = cmds.parentConstraint(ShldrRCt[4], 'front_shoulder_dbl_jnt_R', mo=True)[0]
        UsrAttrR = cmds.listAttr(scapStrtchR, ud=True)[0]
        cmds.addAttr(scapStrtchR + '.' + UsrAttrR, e=True, max=1)
        place.hijackAttrs(scapStrtchR, ShldrRCt[2], UsrAttrR, 'ScapulaStretch', default=1)
        # clav stretch
        clavStrtchR = cmds.parentConstraint(ShldrRCt[4], 'clavicle_jnt_03_R', mo=True)[0]
        UsrAttrL = cmds.listAttr(clavStrtchR, ud=True)[0]
        cmds.addAttr(clavStrtchR + '.' + UsrAttrR, e=True, max=1)
        place.hijackAttrs(clavStrtchR, ShldrRCt[2], UsrAttrR, 'ClavicleStretch', default=0)
        #
        cmds.parent(ShldrRCt[0], CONTROLS)
        place.setChannels(ShldrRCt[0], [False, False], [False, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[1], [True, False], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[2], [False, True], [True, False], [True, False], [True, False, False])
        place.setChannels(ShldrRCt[3], [False, True], [True, False], [True, False], [False, False, False])
        cmds.setAttr(ShldrRCt[3] + '.visibility', cb=False)
        place.setChannels(ShldrRCt[4], [True, False], [True, False], [True, False], [True, False, False])
        # cmds.setAttr(ShldrRCt[2] + '.tx', l=True, k=False)
        # cmds.setAttr(ShldrRCt[3] + '.tx', l=True, k=False)

        # Attrs for paws
        attrVis = ['Pivot', 'Pad', 'Fk', 'AnkleUp', 'BaseDigit', 'MidDigit', 'PvDigit']
        attrCstm = ['ToeRoll', 'HeelRoll', 'KneeTwist']
        vis = 'Vis'
        assist = 'Assist'

        # BACK L  #
        PawBckL = 'foot_L'
        pawBckL = place.Controller(PawBckL, BACK_L_jnt, False, 'pawMaster_ctrl', X * 30.0, 12, 8, 1, (0, 0, 1), True, True)
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
        PawBckR = 'foot_R'
        pawBckR = place.Controller(PawBckR, BACK_R_jnt, False, 'pawMaster_ctrl', X * 30.0, 12, 8, 1, (0, 0, 1), True, True)
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
        PawFrntL = 'hand_L'
        pawFrntL = place.Controller(PawFrntL, FRONT_L_jnt, False, 'facetXup_ctrl', X * 17.5, 12, 8, 1, (0, 0, 1), True, True)
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
        PawFrntR = 'hand_R'
        pawFrntR = place.Controller(PawFrntR, FRONT_R_jnt, False, 'facetXup_ctrl', X * 17.5, 12, 8, 1, (0, 0, 1), True, True)
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
    # print cmds.floatField('atom_qrig_conScale', q=True, v=True)
    # return None
    current_scale = cmds.floatField('atom_qrig_conScale', q=True, v=True)
    cmds.floatField('atom_qrig_conScale', edit=True, v=1.0)
    print 1
    # return None
    current_ldf_val = cmds.floatField('atom_qls_ldf_floatField', query=True, v=True)
    print current_ldf_val
    # return None
    current_paw_ldf_val = cmds.floatField('atom_paw_qls_ldf_floatField', query=True, v=True)
    print current_paw_ldf_val
    # return None
    print 2
    # back leg left
    cmds.select('back_hip_jnt_L')
    cmds.select('hip_L', toggle=True)
    cmds.select('foot_L', toggle=True)
    cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=1)
    cmds.textField('atom_prefix_textField', edit=True, tx='Back')
    # return None
    aul.setPreset()
    # return None
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=20.0)  # height
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=4.0)  # forward
    print 3
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=50.0)  # knee pv distance
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=8)  # digit pv distance
    # aal.createReverseLeg()
    # return None
    aal.createReverseLeg(traversDepth=3, ballRollOffset=0.3)
    # return None
    place.cleanUp('Back_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_L', Ctrl=True)
    cmds.setAttr('Back_leg_ankle_ctrl_L.AutoAnkle', 0)
    print 4
    # return None
    # back right leg
    cmds.select(cl=True)
    cmds.select('back_hip_jnt_R')
    cmds.select('hip_R', toggle=True)
    cmds.select('foot_R', toggle=True)
    cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=2)
    cmds.textField('atom_prefix_textField', edit=True, tx='Back')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-20.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=-4.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=-50.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=-8)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    place.cleanUp('Back_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Back_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Back_limb_ctrl_grp_R', Ctrl=True)
    cmds.setAttr('Back_leg_ankle_ctrl_R.AutoAnkle', 0)

    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-2)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5.5)

    # front left leg
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_L')
    cmds.select('shldr_L', toggle=True)
    cmds.select('hand_L', toggle=True)
    cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=3)
    cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=20.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=4.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=-50.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=8.0)
    aal.createReverseLeg(traversDepth=3)
    # return None
    aal.createVerticalScapRig('front_shoulder_jnt_L', 'front_shoulder_dbl_jnt_L', 'shldr_L_Grp', 'scapula_jnt_01_L', 'shldr_L', 'spine_jnt_06', '_L')
    # return None
    aal.createClavicleRig('clavicle_jnt_02_L', 'front_shoulder_jnt_L', 'spine_jnt_07', '_L', [0, 0, 1], [0, 1, 0])
    # return None
    # SCALE -- MORE NODES ATTACH IN THE APPENDAGE LIB
    # scale upper arm
    aal.createBoneScale(name='', joint='front_shoulder_jnt_L', control='shldr_L', lengthAttr='scaleZ')
    # scale lower arm
    aal.createBoneScale(name='', joint='front_lower_knee_jnt_L', control='Front_pv_ctrl_L_Twist', lengthAttr='scaleZ')
    place.hijackScale('front_twist_01_jnt_L', 'front_lower_knee_jnt_L')
    place.hijackScale('front_twist_02_jnt_L', 'front_lower_knee_jnt_L')
    place.hijackScale('front_twist_03_jnt_L', 'front_lower_knee_jnt_L')
    # return None
    # scale hand
    aal.createBoneScale(name='', joint='Front_limb_ctrl_grp_L', control='hand_L', newAttr='hand', unified=True)
    # return None
    # clean
    place.cleanUp('Front_knee_pv_grp_L', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_L', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_L', Ctrl=True)
    # return None
    cmds.setAttr('Front_leg_ankle_ctrl_L.AutoAnkle', 0)
    cmds.setAttr('Front_pv_ctrl_L_Twist.TwistOff_On', 0)
    # breaks on twist attr change
    # return None

    # front right leg
    cmds.select(cl=True)
    cmds.select('front_shoulder_jnt_R')
    cmds.select('shldr_R', toggle=True)
    cmds.select('hand_R', toggle=True)
    cmds.optionMenu('atom_qls_limb_preset_optionMenu', edit=True, sl=4)
    cmds.textField('atom_prefix_textField', edit=True, tx='Front')
    aul.setPreset()
    # set the position of the ankle PV
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-20.0)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=-4.0)

    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=50.0)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=-8.0)
    # aal.createReverseLeg()
    aal.createReverseLeg(traversDepth=3)
    #aal.createQuadScapulaRig('front_shoulder_jnt_R', 'shldr_R_Grp', 'scapula_jnt_01_R', 'shldr_R', 'spine_jnt_06', '_R')
    aal.createVerticalScapRig('front_shoulder_jnt_R', 'front_shoulder_dbl_jnt_R', 'shldr_R_Grp', 'scapula_jnt_01_R', 'shldr_R', 'spine_jnt_06', '_R')
    aal.createClavicleRig('clavicle_jnt_02_R', 'front_shoulder_jnt_R', 'spine_jnt_07', '_R', [0, 0, 1], [0, 1, 0])
    # SCALE -- MORE NODES ATTACH IN THE APPENDAGE LIB
    # scale upper arm
    aal.createBoneScale(name='', joint='front_shoulder_jnt_R', control='shldr_R', lengthAttr='scaleZ')
    # scale lower arm
    aal.createBoneScale(name='', joint='front_lower_knee_jnt_R', control='Front_pv_ctrl_R_Twist', lengthAttr='scaleZ')
    place.hijackScale('front_twist_01_jnt_R', 'front_lower_knee_jnt_R')
    place.hijackScale('front_twist_02_jnt_R', 'front_lower_knee_jnt_R')
    place.hijackScale('front_twist_03_jnt_R', 'front_lower_knee_jnt_R')
    # scale hand
    aal.createBoneScale(name='', joint='Front_limb_ctrl_grp_R', control='hand_R', newAttr='hand', unified=True)

    place.cleanUp('Front_knee_pv_grp_R', Ctrl=True)
    place.cleanUp('Front_auto_ankle_parent_grp_R', Ctrl=True)
    place.cleanUp('Front_limb_ctrl_grp_R', Ctrl=True)
    cmds.setAttr('Front_leg_ankle_ctrl_R.AutoAnkle', 0)
    cmds.setAttr('Front_pv_ctrl_R_Twist.TwistOff_On', 0)

    # reset some UI vals
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v2=-5)
    cmds.floatFieldGrp('atom_qls_anklePvFlip_floatFieldGrp', edit=True, v3=5)
    cmds.floatField('atom_qls_ldf_floatField', edit=True, v=current_ldf_val)
    cmds.floatField('atom_paw_qls_ldf_floatField', edit=True, v=current_paw_ldf_val)

    # build volume retention rigs
    aal.createForarmTwistRig(['L', 'R'], w=0.5)
    aal.createThighTwistRig(['L', 'R'], w=-0.75)
    aal.createDeltTwistRig(['L', 'R'], w=-0.75)
    aal.createButtVolumeRig(['L', 'R'], w=0.1)
    aal.createDeltVolumeRig(['L', 'R'], w=0.5)

    print '===== Quadriped Leg Build Complete ====='
    cmds.floatField('atom_qrig_conScale', edit=True, v=current_scale)

    quadLimits()


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


def buildSplines(*args):
    '''\n
    Build splines for quadraped character\n
    '''
    face = None
    check = cmds.checkBox('atom_rat_faceCheck', query=True, v=True)
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 3
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

    if not face:
        pass
        '''
        tailRig = splnFk.SplineFK('tail', 'tailDbl_jnt', 'tail_jnt_032', 'mid', controllerSize=5, rootParent='PelvisAttch_CnstGp', parent1='master_Grp', parentDefault=[1, 0], segIteration=6, stretch=0, ik='splineIK')

        # tailRig.placeIkJnts()
        for i in tailRig.topGrp2:
            place.cleanUp(i, World=True)
        #place.cleanUp('tail_mid_UpVctrGdGrp', Ctrl=True)
        '''

    # SPINE
    spineName = 'spine'
    spineSize = X * 1
    spineDistance = X * 4
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
    cmds.setAttr(spineAttr + '.ClstrMidIkBlend', 1.0)
    cmds.setAttr(spineAttr + '.ClstrMidIkSE_W', 0.85)
    cmds.setAttr(spineAttr + '.VctrVis', 0)
    cmds.setAttr(spineAttr + '.VctrMidIkBlend', .25)
    cmds.setAttr(spineAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(spineAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(spineName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(spineName + '_E_IK_Cntrl.LockOrientOffOn', 1)

    # NECK
    neckName = 'neck'
    neckSize = X * 1
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
    cmds.parentConstraint(neckPrnt, neckName + '_IK_CtrlGrp')
    cmds.parentConstraint(neckStrt, neckName + '_S_IK_PrntGrp')
    cmds.parentConstraint(neckEnd, neckName + '_E_IK_PrntGrp')
    place.hijackCustomAttrs(neckName + '_IK_CtrlGrp', neckAttr)
    # set options
    cmds.setAttr(neckAttr + '.' + neckName + 'Vis', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Root', 0)
    cmds.setAttr(neckAttr + '.' + neckName + 'Stretch', 0)
    cmds.setAttr(neckAttr + '.ClstrVis', 0)
    cmds.setAttr(neckAttr + '.ClstrMidIkBlend', 0.25)
    cmds.setAttr(neckAttr + '.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrVis', 0)
    cmds.setAttr(neckAttr + '.VctrMidIkBlend', 1)
    cmds.setAttr(neckAttr + '.VctrMidIkSE_W', 0.5)
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrnt', 0)
    cmds.setAttr(neckAttr + '.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(neckName + '_S_IK_Cntrl.LockOrientOffOn', 0)
    cmds.setAttr(neckName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    # buildRatEars()
    hairSplines(X=X)


def hairSplines(X=1):
    neckName = ['hairOne', 'hairTwo', 'hairThree', 'hairFour', 'hairFive', 'hairSix', 'hairSeven', 'hairEight', ]
    neckSize = X * 0.1
    neckDistance = X * 0.4
    neckFalloff = 0
    neckPrnt = 'hair_root'
    neckStrt = 'hair_root'  # ???
    neckEnd = 'neck_Grp'  # ???
    neckJntS = '_01_jnt'
    neckJntE = ['_19_jnt', '_15_jnt', '_17_jnt', '_15_jnt', '_17_jnt', '_17_jnt', '_13_jnt', '_13_jnt']
    # build spline
    i = 0
    for name in neckName:
        neckAttr = name + '_S_IK_Cntrl'
        SplineOpts(name, neckSize, neckDistance, neckFalloff)
        cmds.select([name + neckJntS, name + neckJntE[i]])
        stage.splineStage(4)
        # assemble
        OptAttr(neckAttr, 'Spline')
        cmds.parentConstraint(neckPrnt, name + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(neckStrt, name + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(neckEnd, name + '_E_IK_PrntGrp', mo=True)
        place.hijackCustomAttrs(name + '_IK_CtrlGrp', neckAttr)
        # set options
        cmds.setAttr(neckAttr + '.' + name + 'Vis', 1)
        cmds.setAttr(neckAttr + '.' + name + 'Root', 0)
        cmds.setAttr(neckAttr + '.' + name + 'Stretch', 1)
        cmds.setAttr(neckAttr + '.ClstrVis', 1)
        cmds.setAttr(neckAttr + '.ClstrMidIkBlend', 0.25)
        cmds.setAttr(neckAttr + '.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(neckAttr + '.VctrVis', 0)
        cmds.setAttr(neckAttr + '.VctrMidIkBlend', 1)
        cmds.setAttr(neckAttr + '.VctrMidIkSE_W', 0.5)
        cmds.setAttr(neckAttr + '.VctrMidTwstCstrnt', 1)
        cmds.setAttr(neckAttr + '.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(name + '_S_IK_Cntrl.LockOrientOffOn', 0)
        cmds.setAttr(name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        i = i + 1


def jaw(jnt='jaw_jnt'):
    #ctrl = place.Controller('jaw', jnt, orient=True, shape='jawZ_ctrl', size=25, color=17, groups=True)
    ctrl = place.Controller('jaw', jnt, orient=True, shape='arrow_ctrl', size=25, color=17, groups=True)
    ctrl_group = ctrl.createController()
    cmds.parentConstraint('neck_jnt_06', ctrl_group[0], mo=True)
    cmds.parentConstraint(ctrl_group[4], jnt, mo=True)
    return ctrl_group[0]


def lids(jnts=['bottomLid_jnt_R', 'topLid_jnt_R', 'bottomLid_jnt_L', 'topLid_jnt_L']):
    grps = []
    drct = ''
    lid = 'Lid'
    for jnt in jnts:
        if 'top' in jnt:
            #shape = 'lidTop_ctrl'
            shape = 'arrow_ctrl'

            drct = 'top'
        else:
            # shape = 'lidBottom_ctrl'
            shape = 'arrow_ctrl'
            drct = 'bottom'
        if '_L' in jnt:
            ctrl = place.Controller(drct + lid + '_L', jnt, orient=True, shape=shape, size=20, color=17, groups=True)
            ctrl_group = ctrl.createController()
            cmds.parentConstraint('eye_jnt_L', ctrl_group[0], mo=True)
            cmds.parentConstraint(ctrl_group[4], jnt, mo=True)
            grps.append(ctrl_group[0])
        else:
            ctrl = place.Controller(drct + lid + '_R', jnt, orient=True, shape=shape, size=20, color=17, groups=True)
            ctrl_group = ctrl.createController()
            cmds.parentConstraint('eye_jnt_R', ctrl_group[0], mo=True)
            cmds.parentConstraint(ctrl_group[4], jnt, mo=True)
            grps.append(ctrl_group[0])
    return grps


def deform(*args):
    '''\n
    Creates deformation splines for rat rig.\n
    paw pad\n
    neck\n
    belly\n
    '''
    face = None
    check = cmds.checkBox('atom_qrig_faceCheck', query=True, v=True)
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

    # deformation opt attr
    OptAttr('cog', 'DeformationVis')

    # build defomers
    if face == False:
        # ABDOMEN
        abdomenName = 'abdomen'
        abdomenSize = X * 0.25
        abdomenDistance = X * 1.5
        abdomenFalloff = 0
        abdomenPrnt = 'pelvis_jnt'
        ##abdomenStrt = 'pelvis_jnt'
        abdomenEnd = 'spine_jnt_06'
        abdomenAttr = 'abdomen'
        abdomen = ['abdomen_jnt_01', 'abdomen_jnt_05']
        # build controller
        ab = place.Controller(abdomenName, abdomen[0], True, 'facetXup_ctrl', X * 4, 12, 8, 1, (0, 0, 1), True, True)
        AbCt = ab.createController()
        cmds.parentConstraint(abdomenPrnt, AbCt[0], mo=True)
        # build spline
        SplineOpts(abdomenName, abdomenSize, abdomenDistance, abdomenFalloff)
        cmds.select(abdomen)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(AbCt[4], abdomenName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(AbCt[4], abdomenName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(abdomenEnd, abdomenName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Vis', 0)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Root', 0)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.' + abdomenName + 'Stretch', 1)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrMidIkBlend', .25)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidIkBlend', .25)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(abdomenAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(abdomenName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(abdomenName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(abdomenAttr, 'AbdomenSpline')
        place.hijackCustomAttrs(abdomenName + '_IK_CtrlGrp', AbCt[2])
        place.hijackVis(AbCt[2], 'cog', name='abdomen', default=None, suffix=False)
        # cleanup
        place.cleanUp(AbCt[0], Ctrl=True)

    # SEMISPINALESTHORACIS
    SSTName = 'SST'
    SSTSize = X * 0.1
    SSTDistance = X * 1.5
    SSTFalloff = 0
    SSTPrnt = 'spine_jnt_06'
    ##SSTStrt = 'spine_jnt_06'
    SSTEnd = 'neck_jnt_03'
    SSTAttr = 'SST'
    SST = ['semispinalesThoracis_jnt_01', 'semispinalesThoracis_jnt_05']
    # build controller
    sst = place.Controller(SSTName, SST[0], True, 'facetXup_ctrl', X * 3, 12, 8, 1, (0, 0, 1), True, True)
    sstCt = sst.createController()
    cmds.parentConstraint(SSTPrnt, sstCt[0], mo=True)
    # build spline
    SplineOpts(SSTName, SSTSize, SSTDistance, SSTFalloff)
    cmds.select(SST)
    stage.splineStage(4)
    # assemble
    cmds.parentConstraint(sstCt[4], SSTName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(sstCt[4], SSTName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(SSTEnd, SSTName + '_E_IK_PrntGrp', mo=True)
    # set options
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Vis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Root', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Stretch', 1)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrVis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrVis', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
    cmds.setAttr(SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(SSTName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(SSTName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    # attrs
    OptAttr(sstCt[2], 'SSTSpline')
    place.hijackCustomAttrs(SSTName + '_IK_CtrlGrp', sstCt[2])
    place.hijackVis(sstCt[2], 'cog', name='semispinalesThoracis', default=None, suffix=False)
    # cleanup
    place.cleanUp(sstCt[0], Ctrl=True)

    # LONGISSIMUSCAPITIS
    LCName = 'LC'
    LCSize = X * 0.1
    LCDistance = X * 1.5
    LCFalloff = 0
    LCPrnt = 'semispinalesThoracis_jnt_03'
    ##LCStrt = 'semispinalesThoracis_jnt_03'
    LCEnd = 'neck_jnt_06'
    LCAttr = 'LC'
    LC = ['longissimusCapitis_jnt_01', 'longissimusCapitis_jnt_05']
    # build controller
    lc = place.Controller(LCName, LC[0], True, 'facetXup_ctrl', X * 3, 12, 8, 1, (0, 0, 1), True, True)
    lcCt = lc.createController()
    cmds.parentConstraint(LCPrnt, lcCt[0], mo=True)
    # build spline
    SplineOpts(LCName, LCSize, LCDistance, LCFalloff)
    cmds.select(LC)
    stage.splineStage(4)
    # assemble
    cmds.parentConstraint(lcCt[4], LCName + '_IK_CtrlGrp', mo=True)
    cmds.parentConstraint(lcCt[4], LCName + '_S_IK_PrntGrp', mo=True)
    cmds.parentConstraint(LCEnd, LCName + '_E_IK_PrntGrp', mo=True)
    # set options
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Vis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Root', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.' + LCName + 'Stretch', 1)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrVis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrVis', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
    cmds.setAttr(LCAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
    cmds.setAttr(LCName + '_S_IK_Cntrl.LockOrientOffOn', 1)
    cmds.setAttr(LCName + '_E_IK_Cntrl.LockOrientOffOn', 1)
    # attrs
    OptAttr(lcCt[2], 'LCSpline')
    place.hijackCustomAttrs(LCName + '_IK_CtrlGrp', lcCt[2])
    place.hijackVis(lcCt[2], 'cog', name='longissimusCapitis', default=None, suffix=False)
    # cleanup
    place.cleanUp(lcCt[0], Ctrl=True)

    # STERNOCLEIDOMASTOID
    if cmds.objExists('sternocleidomastoid_jnt_01'):
        SCMName = 'SCM'
        SCMSize = X * 0.1
        SCMDistance = X * 1.5
        SCMFalloff = 0
        SCMPrnt = 'neck_jnt_02'
        ##SCMStrt = 'neck_jnt_02'
        SCMEnd = 'neck_jnt_06'
        SCMAttr = 'SCM'
        SCM = ['sternocleidomastoid_jnt_01', 'sternocleidomastoid_jnt_05']
        # build controller
        scm = place.Controller(SCMName, SCM[0], True, 'facetXup_ctrl', X * 3, 12, 8, 1, (0, 0, 1), True, True)
        scmCt = scm.createController()
        cmds.parentConstraint(SCMPrnt, scmCt[0], mo=True)
        # build spline
        SplineOpts(SCMName, SCMSize, SCMDistance, SCMFalloff)
        cmds.select(SCM)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(scmCt[4], SCMName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scmCt[4], SCMName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCMEnd, SCMName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Vis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Root', 1)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.' + SCMName + 'Stretch', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCMAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCMName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCMName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(scmCt[2], 'SCMSpline')
        place.hijackCustomAttrs(SCMName + '_IK_CtrlGrp', scmCt[2])
        place.hijackVis(scmCt[2], 'cog', name='sternocleidomastoid', default=None, suffix=False)
        # cleanup
        place.cleanUp(scmCt[0], Ctrl=True)

    ###
        # STERNOCLEIDOMASTOID_L
    if cmds.objExists('sternocleidomastoid_jnt_01_L'):
        SCM_L_Name = 'SCM_L'
        SCM_L_Size = X * 0.1
        SCM_L_Distance = X * 1.5
        SCM_L_Falloff = 0
        SCM_L_Prnt = 'spine_jnt_06'
        ##SCM_L_Strt = 'neck_jnt_02'
        SCM_L_End = 'neck_jnt_06'
        SCM_L_Attr = 'SCM_L'
        SCM_L = ['sternocleidomastoid_jnt_01_L', 'sternocleidomastoid_jnt_05_L']
        # build controller
        scm_L = place.Controller(SCM_L_Name, SCM_L[0], True, 'facetXup_ctrl', X * 3, 12, 8, 1, (0, 0, 1), True, True)
        scm_L_Ct = scm_L.createController()
        cmds.parentConstraint(SCM_L_Prnt, scm_L_Ct[0], mo=True)
        # build spline
        SplineOpts(SCM_L_Name, SCM_L_Size, SCM_L_Distance, SCM_L_Falloff)
        cmds.select(SCM_L)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(scm_L_Ct[4], SCM_L_Name + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scm_L_Ct[4], SCM_L_Name + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCM_L_End, SCM_L_Name + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Vis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Root', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.' + SCM_L_Name + 'Stretch', 1)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCM_L_Attr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCM_L_Name + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCM_L_Name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(scm_L_Ct[2], 'SCM_L_Spline')
        place.hijackCustomAttrs(SCM_L_Name + '_IK_CtrlGrp', scm_L_Ct[2])
        place.hijackVis(scm_L_Ct[2], 'cog', name='sternocleidomastoid_L', default=None, suffix=False)
        # cleanup
        place.cleanUp(scm_L_Ct[0], Ctrl=True)
    ###

    # STERNOCLEIDOMASTOID_R
    if cmds.objExists('sternocleidomastoid_jnt_01_R'):
        SCM_R_Name = 'SCM_R'
        SCM_R_Size = X * 0.1
        SCM_R_Distance = X * 1.5
        SCM_R_Falloff = 0
        SCM_R_Prnt = 'spine_jnt_06'
        ##SCM_R_Strt = 'neck_jnt_02'
        SCM_R_End = 'neck_jnt_06'
        SCM_R_Attr = 'SCM_R'
        SCM_R = ['sternocleidomastoid_jnt_01_R', 'sternocleidomastoid_jnt_05_R']
        # build controller
        scm_R = place.Controller(SCM_R_Name, SCM_R[0], True, 'facetXup_ctrl', X * 3, 12, 8, 1, (0, 0, 1), True, True)
        scm_R_Ct = scm_R.createController()
        cmds.parentConstraint(SCM_R_Prnt, scm_R_Ct[0], mo=True)
        # build spline
        SplineOpts(SCM_R_Name, SCM_R_Size, SCM_R_Distance, SCM_R_Falloff)
        cmds.select(SCM_R)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(scm_R_Ct[4], SCM_R_Name + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(scm_R_Ct[4], SCM_R_Name + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(SCM_R_End, SCM_R_Name + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Vis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Root', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.' + SCM_R_Name + 'Stretch', 1)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SCM_R_Attr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SCM_R_Name + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SCM_R_Name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(scm_R_Ct[2], 'SCM_R_Spline')
        place.hijackCustomAttrs(SCM_R_Name + '_IK_CtrlGrp', scm_R_Ct[2])
        place.hijackVis(scm_R_Ct[2], 'cog', name='sternocleidomastoid_R', default=None, suffix=False)
        # cleanup
        place.cleanUp(scm_R_Ct[0], Ctrl=True)

    # STERNALTHYROID
    if cmds.objExists('sternalThyroid_jnt_01'):
        STName = 'ST'
        STSize = X * 0.1
        STDistance = X * 1.5
        STFalloff = 0
        STPrnt = 'spine_jnt_06'
        ##STStrt = 'spine_jnt_06'
        STEnd = 'sternocleidomastoid_jnt_03'
        STAttr = 'ST'
        ST = ['sternalThyroid_jnt_01', 'sternalThyroid_jnt_05']
        # build controller
        st = place.Controller(STName, ST[0], True, 'facetXup_ctrl', X * 5, 12, 8, 1, (0, 0, 1), True, True)
        stCt = st.createController()
        cmds.parentConstraint(STPrnt, stCt[0], mo=True)
        # build spline
        SplineOpts(STName, STSize, STDistance, STFalloff)
        cmds.select(ST)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(stCt[4], STName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(stCt[4], STName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(STEnd, STName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Vis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Root', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.' + STName + 'Stretch', 1)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidIkBlend', .5)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(STAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(STName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(STName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(stCt[2], 'STSpline')
        place.hijackCustomAttrs(STName + '_IK_CtrlGrp', stCt[2])
        place.hijackVis(stCt[2], 'cog', name='sternalThyroid', default=None, suffix=False)
        # cleanup
        place.cleanUp(stCt[0], Ctrl=True)

    # CLEIDOCERVICALIS_L
    if cmds.objExists('cleidocervicalis_jnt_01_L'):
        CC_LName = 'CC_L'
        CC_LSize = X * 0.1
        CC_LDistance = X * 1.5
        CC_LFalloff = 0
        if cmds.objExists('scapula_jnt_02_L'):
            CC_LPrnt = 'scapula_jnt_02_L'
        else:
            CC_LPrnt = 'spine_jnt_06'
        ##CC_LStrt = 'spine_jnt_06'
        CC_LEnd = 'neck_jnt_06'
        CC_LAttr = 'CC_L'
        CC_L = ['cleidocervicalis_jnt_01_L', 'cleidocervicalis_jnt_05_L']
        # build controller
        cc_l = place.Controller(CC_LName, CC_L[0], True, 'facetXup_ctrl', X * 4, 12, 8, 1, (0, 0, 1), True, True)
        cc_lCt = cc_l.createController()
        cmds.parentConstraint(CC_LPrnt, cc_lCt[0], mo=True)
        # build spline
        SplineOpts(CC_LName, CC_LSize, CC_LDistance, CC_LFalloff)
        cmds.select(CC_L)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(cc_lCt[4], CC_LName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(cc_lCt[4], CC_LName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(CC_LEnd, CC_LName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Vis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Root', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.' + CC_LName + 'Stretch', 1)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.25)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.25)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(CC_LAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(CC_LName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(CC_LName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(cc_lCt[2], 'CC_LSpline')
        place.hijackCustomAttrs(CC_LName + '_IK_CtrlGrp', cc_lCt[2])
        place.hijackVis(cc_lCt[2], 'cog', name='cleidocervicalisL', default=None, suffix=False)
        # cleanup
        place.cleanUp(cc_lCt[0], Ctrl=True)

    # CLEIDOCERVICALIS_R
    if cmds.objExists('cleidocervicalis_jnt_01_R'):
        CC_RName = 'CC_R'
        CC_RSize = X * 0.1
        CC_RDistance = X * 1.5
        CC_RFalloff = 0
        if cmds.objExists('scapula_jnt_02_R'):
            CC_RPrnt = 'scapula_jnt_02_R'
        else:
            CC_RPrnt = 'spine_jnt_06'
        ##CC_RStrt = 'spine_jnt_06'
        CC_REnd = 'neck_jnt_06'
        CC_RAttr = 'CC_R'
        CC_R = ['cleidocervicalis_jnt_01_R', 'cleidocervicalis_jnt_05_R']
        # build controller
        cc_r = place.Controller(CC_RName, CC_R[0], True, 'facetXup_ctrl', X * 4, 12, 8, 1, (0, 0, 1), True, True)
        cc_rCt = cc_r.createController()
        cmds.parentConstraint(CC_RPrnt, cc_rCt[0], mo=True)
        # build spline
        SplineOpts(CC_RName, CC_RSize, CC_RDistance, CC_RFalloff)
        cmds.select(CC_R)
        stage.splineStage(4)
        # assemble
        cmds.parentConstraint(cc_rCt[4], CC_RName + '_IK_CtrlGrp', mo=True)
        cmds.parentConstraint(cc_rCt[4], CC_RName + '_S_IK_PrntGrp', mo=True)
        cmds.parentConstraint(CC_REnd, CC_RName + '_E_IK_PrntGrp', mo=True)
        # set options
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Vis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Root', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.' + CC_RName + 'Stretch', 1)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.25)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.25)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(CC_RAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(CC_RName + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(CC_RName + '_E_IK_Cntrl.LockOrientOffOn', 1)
        ##
        OptAttr(cc_rCt[2], 'CC_RSpline')
        place.hijackCustomAttrs(CC_RName + '_IK_CtrlGrp', cc_rCt[2])
        place.hijackVis(cc_rCt[2], 'cog', name='cleidocervicalisR', default=None, suffix=False)
        # cleanup
        place.cleanUp(cc_rCt[0], Ctrl=True)
    # Check for any corrective blendshapes
    abl.buildCorrectiveBody()


def quadLimits():
    # back
    cmds.transformLimits('back_upper_knee_jnt_L', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_lower_knee_jnt_L', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_05_L', rx=[-15, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_04_L', rx=[-8, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_03_L', rx=[-13, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_02_L', rx=[-13, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_01_L', rx=[-10, 360], erx=[1, 0])
    cmds.transformLimits('back_upper_knee_jnt_R', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_lower_knee_jnt_R', rx=[-18, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_05_R', rx=[-15, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_04_R', rx=[-8, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_03_R', rx=[-13, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_02_R', rx=[-13, 360], erx=[1, 0])
    cmds.transformLimits('back_mid_phal_jnt_01_R', rx=[-10, 360], erx=[1, 0])
    # front
    cmds.transformLimits('front_upper_knee_jnt_L', rx=[-360, 10], erx=[0, 1])
    cmds.transformLimits('front_lower_knee_jnt_L', rx=[-360, 10], erx=[0, 1])
    cmds.transformLimits('front_mid_phal_jnt_04_L', rx=[-1, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_03_L', rx=[-8.5, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_02_L', rx=[-16, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_01_L', rx=[-6.5, 360], erx=[1, 0])
    cmds.transformLimits('front_upper_knee_jnt_R', rx=[-360, 10], erx=[0, 1])
    cmds.transformLimits('front_lower_knee_jnt_R', rx=[-360, 10], erx=[0, 1])
    cmds.transformLimits('front_mid_phal_jnt_04_R', rx=[-1, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_03_R', rx=[-8.5, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_02_R', rx=[-16, 360], erx=[1, 0])
    cmds.transformLimits('front_mid_phal_jnt_01_R', rx=[-6.5, 360], erx=[1, 0])
