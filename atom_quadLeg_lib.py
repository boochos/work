import maya.cmds as cmds
import webrImport as web
# web
aal = web.mod( 'atom_appendage_lib' )
aul = web.mod( 'atom_ui_lib' )
place = web.mod( 'atom_place_lib' )


def buildQuadripedLegs( *args ):

    # back leg left
    cmds.select( 'back_hip_jnt_L' )
    cmds.select( 'hip_L', toggle = True )
    cmds.select( 'back_paw_L', toggle = True )
    idx = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 1 )
    atom_prefix_textField = cmds.textField( 'atom_prefix_textField', edit = True, tx = 'Back' )
    aul.setPreset()
    aal.createReverseLeg()

    place.cleanUp( 'Back_knee_pv_grp_L', Ctrl = True )
    place.cleanUp( 'Back_auto_ankle_parent_grp_L', Ctrl = True )
    place.cleanUp( 'Back_limb_ctrl_grp_L', Ctrl = True )

    # back right leg
    cmds.select( cl = True )
    cmds.select( 'back_hip_jnt_R' )
    cmds.select( 'hip_R', toggle = True )
    cmds.select( 'back_paw_R', toggle = True )
    idx = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 2 )
    atom_prefix_textField = cmds.textField( 'atom_prefix_textField', edit = True, tx = 'Back' )
    aul.setPreset()
    aal.createReverseLeg()

    place.cleanUp( 'Back_knee_pv_grp_R', Ctrl = True )
    place.cleanUp( 'Back_auto_ankle_parent_grp_R', Ctrl = True )
    place.cleanUp( 'Back_limb_ctrl_grp_R', Ctrl = True )

    cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v2 = -2 )
    cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v3 = 5.5 )

    # front left leg
    cmds.select( cl = True )
    cmds.select( 'front_shoulder_jnt_L' )
    cmds.select( 'shldr_L', toggle = True )
    cmds.select( 'front_paw_L', toggle = True )
    idx = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 3 )
    atom_prefix_textField = cmds.textField( 'atom_prefix_textField', edit = True, tx = 'Front' )
    aul.setPreset()
    aal.createReverseLeg()
    aal.createQuadScapulaRig( 'front_shoulder_jnt_L', 'shldr_L_Grp', 'scapula_jnt_01_L', 'shldr_L', 'spine_jnt_06', '_L' )

    place.cleanUp( 'Front_knee_pv_grp_L', Ctrl = True )
    place.cleanUp( 'Front_auto_ankle_parent_grp_L', Ctrl = True )
    place.cleanUp( 'Front_limb_ctrl_grp_L', Ctrl = True )

    # front right leg
    cmds.select( cl = True )
    cmds.select( 'front_shoulder_jnt_R' )
    cmds.select( 'shldr_R', toggle = True )
    cmds.select( 'front_paw_R', toggle = True )
    idx = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 4 )
    atom_prefix_textField = cmds.textField( 'atom_prefix_textField', edit = True, tx = 'Front' )
    aul.setPreset()
    aal.createReverseLeg()
    aal.createQuadScapulaRig( 'front_shoulder_jnt_R', 'shldr_R_Grp', 'scapula_jnt_01_R', 'shldr_R', 'spine_jnt_06', '_R' )

    place.cleanUp( 'Front_knee_pv_grp_R', Ctrl = True )
    place.cleanUp( 'Front_auto_ankle_parent_grp_R', Ctrl = True )
    place.cleanUp( 'Front_limb_ctrl_grp_R', Ctrl = True )

    cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v2 = -5 )
    cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v3 = 5 )
    print( '===== Quadriped Leg Build Complete =====' )
