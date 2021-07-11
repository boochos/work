from pymel.core import *
import maya.cmds as cmds
import webrImport as web
# web
aal = web.mod( 'atom_appendage_lib' )
aul = web.mod( 'atom_ui_lib' )
place = web.mod( 'atom_place_lib' )
stage = web.mod( 'atom_splineStage_lib' )
ajl = web.mod( 'atom_joint_lib' )
ael = web.mod( 'atom_earRig_lib' )
splnFk = web.mod( 'atom_splineFk_lib' )
adl = web.mod( 'atom_deformer_lib' )
abl = web.mod( 'atom_body_lib' )


def preBuild( 
        COG_jnt = 'root_jnt', PELVIS_jnt = 'pelvis_jnt', CHEST_jnt = 'chest_jnt', NECK_jnt = 'neck_00_jnt', HEAD_jnt = 'head_00_jnt',
        HIP_L_jnt = 'back_fin_L_jnt', HIP_R_jnt = 'back_fin_R_jnt',
        SHLDR_L_jnt = 'front_shoulder_jnt_L', SHLDR_R_jnt = 'front_shoulder_jnt_R',
        BACK_L_jnt = 'back_foot_ctrl_placement_jnt_L', BACK_R_jnt = 'back_foot_ctrl_placement_jnt_R',
        FRONT_L_jnt = 'front_foot_ctrl_placement_jnt_L', FRONT_R_jnt = 'front_foot_ctrl_placement_jnt_R',
        TAIL_jnt = 'tail_00_jnt', TAILTIP_jnt = 'spine_20_jnt', GEO_gp = 'buddy_GP', SKIN_jnt = 'root_jnt' ):
    '''\n

    '''
    current_scale = cmds.floatField( 'atom_qrig_conScale', q = True, v = True )
    cmds.floatField( 'atom_qrig_conScale', edit = True, v = .3 )

    face = None
    check = cmds.checkBox( 'atom_qrig_faceCheck', query = True, v = True )
    X = cmds.floatField( 'atom_qrig_conScale', query = True, value = True )
    # print X
    if check == 0:
        face = False
    else:
        face = True

    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 40 )
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
    cog = place.Controller( Cog, COG_jnt, True, 'facetZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True )
    CogCt = cog.createController()
    place.setRotOrder( CogCt[0], 2, True )
    cmds.parent( CogCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], CogCt[0], mo = True )

    # PELVIS/CHEST #
    # # PELVIS ##
    Pelvis = 'pelvis'
    pelvis = place.Controller( Pelvis, PELVIS_jnt, True, 'pelvis_ctrl', X * 4.75, 17, 8, 1, ( 0, 0, 1 ), True, True )
    PelvisCt = pelvis.createController()
    place.setRotOrder( PelvisCt[0], 2, True )
    # # GROUP for hip joints, tail ##
    if cmds.objExists( TAIL_jnt ):
        PelvisAttch_Gp = place.null2( 'PelvisAttch_Gp', TAIL_jnt )[0]
        PelvisAttch_CnstGp = place.null2( 'PelvisAttch_CnstGp', TAIL_jnt )[0]
        cmds.parent( PelvisAttch_CnstGp, PelvisAttch_Gp )
        place.setRotOrder( PelvisAttch_CnstGp, 2, False )
        cmds.parentConstraint( PELVIS_jnt, PelvisAttch_Gp, mo = True )
        cmds.parent( PelvisAttch_Gp, PelvisCt[0] )

    # # CHEST ##
    Chest = 'chest'
    chest = place.Controller( Chest, CHEST_jnt, True, 'chest_ctrl', X * 4.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    ChestCt = chest.createController()
    place.setRotOrder( ChestCt[0], 2, True )
    # # GROUP for shoulder joints, neck ##
    ChestAttch_Gp = place.null2( 'ChestAttch_Gp', NECK_jnt )[0]
    ChestAttch_CnstGp = place.null2( 'ChestAttch_CnstGp', NECK_jnt )[0]
    cmds.parent( ChestAttch_CnstGp, ChestAttch_Gp )
    place.setRotOrder( ChestAttch_CnstGp, 2, False )
    cmds.parentConstraint( CHEST_jnt, ChestAttch_Gp, mo = True )
    cmds.parent( ChestAttch_Gp, PelvisCt[0] )
    # constrain controllers, parent under Master group
    cmds.parentConstraint( CogCt[4], PelvisCt[0], mo = True )
    cmds.parentConstraint( CogCt[4], ChestCt[0], mo = True )
    # setChannels
    place.setChannels( PelvisCt[0], [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( PelvisCt[1], [True, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( PelvisCt[2], [False, True], [False, True], [True, False], [True, False, False] )
    # #place.setChannels(PelvisCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels( PelvisCt[4], [True, False], [True, False], [True, False], [True, False, False] )
    place.setChannels( ChestCt[0], [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( ChestCt[1], [True, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( ChestCt[2], [False, True], [False, True], [True, False], [True, False, False] )
    # #place.setChannels(ChestCt[3], [False, True], [False, True], [True, False], [False, False, False])
    place.setChannels( ChestCt[4], [True, False], [True, False], [True, False], [True, False, False] )
    # parent topGp to master
    cmds.parent( PelvisCt[0], CONTROLS )
    cmds.parent( ChestCt[0], CONTROLS )

    # NECK #
    Neck = 'neck'
    neck = place.Controller( Neck, NECK_jnt, True, 'GDneck_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True )
    NeckCt = neck.createController()
    place.setRotOrder( NeckCt[0], 2, True )
    # parent switches
    place.parentSwitch( Neck, NeckCt[2], NeckCt[1], NeckCt[0], CogCt[4], ChestAttch_CnstGp, False, True, False, True, 'Chest' )
    cmds.parentConstraint( ChestAttch_CnstGp, NeckCt[0], mo = True )
    place.setChannels( NeckCt[0], [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( NeckCt[1], [True, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( NeckCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( NeckCt[3], [True, False], [False, True], [True, False], [False, False, False] )
    cmds.setAttr( NeckCt[3] + '.visibility', cb = False )
    place.setChannels( NeckCt[4], [True, False], [True, False], [True, False], [True, False, False] )
    # parent topGp to master
    cmds.parent( NeckCt[0], CONTROLS )

    # HEAD #
    Head = 'head'
    head = place.Controller( Head, HEAD_jnt, True, 'head_ctrl', X * 4, 12, 8, 1, ( 0, 0, 1 ), True, True )
    HeadCt = head.createController()
    place.setRotOrder( HeadCt[0], 2, True )
    # parent switch
    place.parentSwitch( Head, HeadCt[2], HeadCt[1], HeadCt[0], CogCt[4], NeckCt[4], False, False, True, True, 'Neck' )
    # insert group under Head, in the same space as Head_offset, name: Head_CnstGp
    Head_CnstGp = place.null2( Head + '_CnstGp', HEAD_jnt )[0]
    place.setRotOrder( Head_CnstGp, 2, True )
    cmds.parent( Head_CnstGp, HeadCt[2] )
    # tip of head constrain to offset
    # cmds.orientConstraint(HeadCt[3], NECK_jnt, mo=True)
    # constrain head to neck
    cmds.parentConstraint( NeckCt[4], HeadCt[0], mo = True )
    # set channels
    place.setChannels( HeadCt[0], [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( HeadCt[1], [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( HeadCt[2], [False, True], [False, True], [True, False], [True, False, False] )
    place.setChannels( HeadCt[3], [True, False], [False, True], [True, False], [False, False, False] )
    cmds.setAttr( HeadCt[3] + '.visibility', cb = False )
    place.setChannels( HeadCt[4], [True, False], [True, False], [True, False], [True, False, False] )
    place.setChannels( Head_CnstGp, [True, False], [True, False], [True, False], [True, False, False] )
    # parent topGp to master
    cmds.parent( HeadCt[0], CONTROLS )
    # add extra group to 'HeadCt'
    HeadCt += ( Head_CnstGp, )

    if not face:
        pass


def buildSplines( *args ):
    '''\n
    Build splines for quadraped character\n
    '''
    face = None
    check = cmds.checkBox( 'atom_rat_faceCheck', query = True, v = True )
    X = cmds.floatField( 'atom_qrig_conScale', query = True, value = True )
    if check == 0:
        face = False
    else:
        face = True

    def SplineOpts( name, size, distance, falloff ):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField( 'atom_prefix_textField', e = True, tx = name )
        cmds.floatField( 'atom_spln_scaleFactor_floatField', e = True, v = size )
        cmds.floatField( 'atom_spln_vectorDistance_floatField', e = True, v = distance )
        cmds.floatField( 'atom_spln_falloff_floatField', e = True, v = falloff )

    def OptAttr( obj, attr ):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( obj + '.' + attr, cb = True )

    # Tail
    tailRig = splnFk.SplineFK( 'tail', 'tail_00_jnt', 'spine_21_jnt', 'mid',
                              controllerSize = 6, rootParent = 'PelvisAttch_CnstGp', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in tailRig.topGrp2:
        place.cleanUp( i, World = True )

    # Tongue
    tngRig = splnFk.SplineFK( 'tongue', 'tongue_00_jnt', 'tongue_03_jnt', 'mid',
                             controllerSize = 1, rootParent = 'lower_jaw_00_jnt', parent1 = 'head_00_jnt', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in tngRig.topGrp2:
        place.cleanUp( i, World = True )

    # fl
    flRig = splnFk.SplineFK( 'fin_front_L', 'front_fin_00_L_jnt', 'front_fin_07_L_jnt', 'mid',
                            controllerSize = 6, rootParent = 'chest_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in flRig.topGrp2:
        place.cleanUp( i, World = True )

    # fr
    frRig = splnFk.SplineFK( 'fin_front_R', 'front_fin_00_R_jnt', 'front_fin_07_R_jnt', 'mid',
                            controllerSize = 6, rootParent = 'chest_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in frRig.topGrp2:
        place.cleanUp( i, World = True )

    # bl
    blRig = splnFk.SplineFK( 'fin_back_L', 'back_fin_L_jnt', 'back_fin_07_L_jnt', 'mid',
                            controllerSize = 6, rootParent = 'pelvis_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in blRig.topGrp2:
        place.cleanUp( i, World = True )

    # br
    brRig = splnFk.SplineFK( 'fin_back_R', 'back_fin_R_jnt', 'back_fin_07_R_jnt', 'mid',
                            controllerSize = 6, rootParent = 'pelvis_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = 4, stretch = 0, ik = 'splineIK' )
    for i in brRig.topGrp2:
        place.cleanUp( i, World = True )

    # SPINE
    spineName = 'spine'
    spineSize = X * 4
    spineDistance = X * 7
    spineFalloff = 0
    spinePrnt = 'cog_Grp'
    spineStrt = 'pelvis_Grp'
    spineEnd = 'chest_Grp'
    spineAttr = 'cog'
    spineRoot = 'pelvis_jnt'
    'spine_S_IK_Jnt'
    spine = ['spine_05_jnt', 'spine_01_jnt']
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 1 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 0 )
    cmds.setAttr( spineAttr + '.ClstrVis', 1 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', .75 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 1 )

    # NECK
    neckName = 'neck'
    neckSize = X * 4
    neckDistance = X * 7
    neckFalloff = 0
    neckPrnt = 'neck_Grp'
    neckStrt = 'neck_Grp'
    neckEnd = 'head_CnstGp'
    neckAttr = 'neck'
    neck = ['neck_00_jnt', 'neck_02_jnt']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    stage.splineStage( 4 )
    # assemble
    OptAttr( neckAttr, 'NeckSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp' )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp' )
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
    cmds.setAttr( neckAttr + '.ClstrVis', 1 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )

    # belly
    deform()

    # constrain jiggles
    parentJiggleJoints()


def parentJiggleJoints():
    prnt = 'neck_01_jnt'
    chld = [
        'muscle_spine00_R_jnt',
        'muscle_spine00_L_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )
    prnt = 'spine_01_jnt'
    chld = [
        'muscle_spine01_R_jnt',
        'muscle_spine01_L_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )
    prnt = 'spine_02_jnt'
    chld = [
        'muscle_spine02_L_jnt',
        'muscle_spine02_R_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )
    prnt = 'spine_03_jnt'
    chld = [
        'muscle_spine03_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )
    prnt = 'spine_04_jnt'
    chld = [
        'muscle_spine04_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )
    prnt = 'spine_05_jnt'
    chld = [
        'muscle_spine05_jnt'
    ]
    for ch in chld:
        cmds.parentConstraint( prnt, ch, mo = True )


def deform( *args ):
    '''\n
    Creates deformation splines for rat rig.\n
    neck\n
    belly\n
    '''
    face = None
    check = cmds.checkBox( 'atom_qrig_faceCheck', query = True, v = True )
    X = cmds.floatField( 'atom_qrig_conScale', query = True, value = True )
    if check == 0:
        face = False
    else:
        face = True

    def SplineOpts( name, size, distance, falloff ):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField( 'atom_prefix_textField', e = True, tx = name )
        cmds.floatField( 'atom_spln_scaleFactor_floatField', e = True, v = size )
        cmds.floatField( 'atom_spln_vectorDistance_floatField', e = True, v = distance )
        cmds.floatField( 'atom_spln_falloff_floatField', e = True, v = falloff )

    def OptAttr( obj, attr ):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( obj + '.' + attr, cb = True )

    # deformation opt attr
    OptAttr( 'cog', 'DeformationVis' )

    # belly
    SSTName = 'belly'
    SSTSize = X * 0.1
    SSTDistance = X * 5
    SSTFalloff = 0
    SSTPrnt = 'chest_jnt'
    # #SSTStrt = 'spine_jnt_06'
    SSTEnd = 'pelvis_jnt'
    SSTAttr = 'belly'
    SST = ['belly_00_jnt', 'belly_04_jnt']
    # build controller
    sst = place.Controller( SSTName, SST[0], True, 'facetZup_ctrl', X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True )
    sstCt = sst.createController()
    cmds.parentConstraint( SSTPrnt, sstCt[0], mo = True )
    # build spline
    SplineOpts( SSTName, SSTSize, SSTDistance, SSTFalloff )
    cmds.select( SST )
    stage.splineStage( 4 )
    # assemble
    cmds.parentConstraint( sstCt[4], SSTName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( sstCt[4], SSTName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( SSTEnd, SSTName + '_E_IK_PrntGrp', mo = True )
    # set options
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Vis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Root', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Stretch', 1 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrVis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 1 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrVis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidIkBlend', 1 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( SSTName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( SSTName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # attrs
    OptAttr( sstCt[2], 'BellySpline' )
    place.hijackCustomAttrs( SSTName + '_IK_CtrlGrp', sstCt[2] )
    place.hijackVis( sstCt[2], 'cog', name = 'belly', default = None, suffix = False )
    # cleanup
    place.cleanUp( sstCt[0], Ctrl = True )

    # throat
    SSTName = 'throat'
    SSTSize = X * 0.1
    SSTDistance = X * 5
    SSTFalloff = 0
    SSTPrnt = 'chest_jnt'
    # #SSTStrt = 'spine_jnt_06'
    SSTEnd = 'lower_jaw_00_jnt'
    SSTAttr = 'throat'
    SST = ['throat_00_jnt', 'throat_04_jnt']
    # build controller
    sst = place.Controller( SSTName, SST[0], True, 'facetZup_ctrl', X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True )
    sstCt = sst.createController()
    cmds.parentConstraint( SSTPrnt, sstCt[0], mo = True )
    # build spline
    SplineOpts( SSTName, SSTSize, SSTDistance, SSTFalloff )
    cmds.select( SST )
    stage.splineStage( 4 )
    # assemble
    cmds.parentConstraint( sstCt[4], SSTName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( sstCt[4], SSTName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( SSTEnd, SSTName + '_E_IK_PrntGrp', mo = True )
    # set options
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Vis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Root', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.' + SSTName + 'Stretch', 1 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrVis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrMidIkBlend', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrVis', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidIkBlend', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( SSTAttr + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( SSTName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( SSTName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # attrs
    OptAttr( sstCt[2], 'ThroatSpline' )
    place.hijackCustomAttrs( SSTName + '_IK_CtrlGrp', sstCt[2] )
    place.hijackVis( sstCt[2], 'cog', name = 'throat', default = None, suffix = False )
    # cleanup
    place.cleanUp( sstCt[0], Ctrl = True )
