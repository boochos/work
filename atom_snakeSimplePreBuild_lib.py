import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc

def snakePreBuild(
    COG_jnt= 'upperA_jnt_01', 
    LOWER_jnt= ['lowerB_jnt_01', 'lowerC_jnt_01', 'lowerD_jnt_01', 'lowerE_jnt_01', 'lowerF_jnt_01', 'lowerG_jnt_01', 'lowerH_jnt_01',
                'lowerI_jnt_01', 'lowerJ_jnt_01', 'lowerK_jnt_01', 'lowerL_jnt_01', 'lowerM_jnt_01', 'lowerN_jnt_01', 'lowerO_jnt_01', 'lowerP_jnt_01',
                'lowerQ_jnt_01', 'lowerR_jnt_01'],
    UPPER_jnt= ['upperB_jnt_01','upperC_jnt_01','upperD_jnt_01'],
    NECK_jnt= 'neck_jnt_01', 
    HEAD_jnt= 'head_jnt', 
    LOWERTIP_jnt= 'lowerR_jnt_05', 
    GEO_gp= 'buddy_GP', 
    SKIN_jnt= 'root_jnt'):

    face=None
    X = cmds.floatField('atom_srig_conScale', query=True, value=True)
    '''
    if check == 0:
	face   = False
    else:
	face=True
    '''

    PreBuild    = misc.rigPrebuild(Top=0, Ctrl=True, SknJnts=True, Geo=True, World=True, Master=True, OlSkool=True, Size=110)
    CHARACTER   = PreBuild[0]
    CONTROLS    = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO         = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt    = PreBuild[5]

    cmds.parent(SKIN_jnt, SKIN_JOINTS)
    #cmds.parent(GEO_gp, GEO)

    # COG #
    Cog   = 'A'
    cog   = place.Controller(Cog, COG_jnt, False, 'facetZup_ctrl', X*32, 12, 8, 1, (0,0,1), True, True)
    CogCt = cog.createController()
    misc.addText(CogCt[2], t=Cog, c= 12, rotOffset=[0,0,0], posOffset=[-1.5,10,0])
    Up  = place.circle(Cog +'_Upper', CogCt[3], 'splineStart_ctrl', X*4.5, 12, 8, 1, (0,0,1))[0]
    cmds.parent(Up,CogCt[3])
    misc.setChannels(Up, [True, False], [True, False], [True, False], [True, False, False])
    misc.setRotOrder(CogCt[0], 2, True)
    misc.setRotOrder(CogCt[2], 3, False)
    cmds.parent(CogCt[0], CONTROLS)
    cmds.parentConstraint(CogCt[4], SKIN_jnt, mo=True)
    cmds.parentConstraint(MasterCt[4], CogCt[0], mo=True)

    # UPPER #
    i = 0
    for joint in UPPER_jnt:
        if cmds.objExists(joint):
            if i == 0:
                parent = 'A_Grp'
            else:
                parent = joint[:5] + chr(ord('a') + i).upper() + '_Grp'
            Upper       = joint[:6]
            upperMaster = place.Controller(Upper, joint, True, 'facetZup_ctrl', X*25, 17, 8, 1, (0,0,1), True, True)
            UpperCt     = upperMaster.createController()
            misc.addText(UpperCt[2], t=joint[5], c= 17, rotOffset=[0,0,0], posOffset=[-1.5,8,0])
            cmds.parent(UpperCt[0], CONTROLS)
            cmds.select(UpperCt[0])
            UpperCt_TopGrp1 = misc.insert('null', 1, Upper + '_TopGrp1')[0][0]
            UpperCt_CtGrp1  = misc.insert('null', 1, Upper + '_CtGrp1')[0][0]
            misc.setRotOrder(UpperCt_TopGrp1, 2, True)
            misc.setRotOrder(UpperCt[2], 3, False)
            misc.parentSwitch(Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '')
            misc.parentSwitch(Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '')
            cmds.parentConstraint(parent, UpperCt_TopGrp1, mo=True)
            misc.setChannels(UpperCt[0], [False, False], [False, False], [True, False], [True, False, False])
            misc.setChannels(UpperCt[1], [False, True], [False, False], [True, False], [True, False, False])
            misc.setChannels(UpperCt[2], [False, True], [False, True], [True, False], [True, False, False])
            misc.setChannels(UpperCt[3], [False, True], [False, True], [True, False], [False, False, False])
            cmds.setAttr(UpperCt[3] + '.visibility', cb=False)
            misc.setChannels(UpperCt[4], [True, False], [False, True], [True, False], [True, False, False])
            i = i+1

    # NECK/HEAD
    Neck   = 'neck'
    neck   = place.Controller(Neck, NECK_jnt, True, 'facetZup_ctrl', X*25, 12, 8, 1, (0,0,1), True, True)
    NeckCt = neck.createController()
    misc.setRotOrder(NeckCt[0], 2, True)
    misc.setRotOrder(NeckCt[2], 2, False)
    ##parent switches
    parent =  'upperD_jnt_05'
    D_Attch_Gp = place.null2('ChestAttch_Gp', parent)[0]
    D_Attch_CnstGp = place.null2('ChestAttch_CnstGp', parent)[0]
    cmds.parent(D_Attch_CnstGp, D_Attch_Gp)
    misc.setRotOrder(D_Attch_CnstGp, 2, False)
    cmds.parentConstraint(parent,D_Attch_Gp, mo=True)
    cmds.parent(D_Attch_Gp, NeckCt[0])
    misc.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], MasterCt[4], D_Attch_CnstGp, False, True, False, True, '')
    cmds.parentConstraint('upperD_jnt_05', NeckCt[0], mo=True)
    misc.setChannels(NeckCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[1], [True, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[2], [True, False], [False, True], [True, False], [True, False, False])
    misc.setChannels(NeckCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(NeckCt[3] + '.visibility', cb=False)
    misc.setChannels(NeckCt[4], [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(NeckCt[0], CONTROLS)

    # HEAD #
    Head   = 'head'
    head   = place.Controller(Head, HEAD_jnt, False, 'facetZup_ctrl', X*25, 12, 8, 1, (0,0,1), True, True)
    HeadCt = head.createController()
    misc.setRotOrder(HeadCt[0], 2, True)
    misc.setRotOrder(HeadCt[2], 2, False)
    ##parent switch
    misc.parentSwitch(Head, HeadCt[2], HeadCt[1], HeadCt[0], MasterCt[4], NeckCt[4], False, True, False, True, '')
    ## insert group under Head, in the same space as Head_offset, name: Head_CnstGp
    Head_CnstGp = place.null2(Head + '_CnstGp', HEAD_jnt)[0]
    misc.setRotOrder(Head_CnstGp, 2, True)
    cmds.parent(Head_CnstGp, HeadCt[2])
    ##tip of head constrain to offset
    cmds.orientConstraint(HeadCt[3], 'head_jnt', mo=True)
    ##constrain head to neck
    cmds.parentConstraint(NeckCt[4], HeadCt[0], mo=True)
    ##set channels
    misc.setChannels(HeadCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(HeadCt[1], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(HeadCt[2], [False, True], [False, True], [True, False], [True, False, False])
    misc.setChannels(HeadCt[3], [True, False], [False, True], [True, False], [False, False, False])
    cmds.setAttr(HeadCt[3] + '.visibility', cb=False)
    misc.setChannels(HeadCt[4], [True, False], [True, False], [True, False], [True, False, False])
    misc.setChannels(Head_CnstGp, [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(HeadCt[0], CONTROLS)
    ##add extra group to 'HeadCt'
    HeadCt += (Head_CnstGp,)

    # NECK/SPINE
    Neck   = 'upperE'
    neck   = place.Controller(Neck, NECK_jnt, True, 'facetZup_ctrl', X*35, 17, 8, 1, (0,0,1), True, True)
    NeckCt = neck.createController()
    misc.addText(NeckCt[2], t=Neck[5], c= 17, rotOffset=[0,0,0], posOffset=[-1,12,0])
    cmds.select(NeckCt[0])
    NeckCt_TopGrp1 = misc.insert('null', 1, Neck + '_TopGrp1')[0][0]
    NeckCt_CtGrp1  = misc.insert('null', 1, Neck + '_CtGrp1')[0][0]
    misc.setRotOrder(NeckCt_TopGrp1, 2, True)
    misc.setRotOrder(NeckCt[2], 3, False)
    ##parent switches
    parent =  UPPER_jnt[len(UPPER_jnt) -1][:6] + '_Grp'
    misc.parentSwitch(Neck, NeckCt[2], NeckCt_CtGrp1, NeckCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '')
    misc.parentSwitch(Neck, NeckCt[2], NeckCt[1], NeckCt[0], MasterCt[4], parent, False, True, False, False, '')
    cmds.parentConstraint(parent, NeckCt_TopGrp1, mo=True)
    misc.setChannels(NeckCt[0], [False, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[1], [True, False], [False, False], [True, False], [True, False, False])
    misc.setChannels(NeckCt[2], [False, True], [False, True], [True, False], [True, False, False])
    misc.setChannels(NeckCt[3], [False, True], [False, True], [True, False], [False, False, False])
    cmds.setAttr(NeckCt[3] + '.visibility', cb=False)
    misc.setChannels(NeckCt[4], [True, False], [True, False], [True, False], [True, False, False])
    ##parent topGp to master
    cmds.parent(NeckCt_TopGrp1, CONTROLS) 

    if face == False:
        pass
        #return MasterCt, CogCt, PelvisCt, ChestCt, HeadCt, TailCt, TailTipCt
    else:
        pass
        #return MasterCt, CogCt, PelvisCt, ChestCt, HeadCt