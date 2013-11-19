import atom_splineBuild_lib as build
import atom_spline_lib as spln
import atom_ui_lib as ui
import maya.cmds as cmds
import maya.mel as mel

def splineStage(stage):
    """Arguments:
    stage = int 1-4
    \rDescription:
    Stage0 = Collect build options
    -rotateOrder
    -rotateAxis
    -AimAxis
    -UpAxis
    -ControllerScale
    -VectorDistance
    Stage1 = Build cluster control groups
    Stage2 = Build cluster groups
    Stage3 = Build IK groups
    Stage4 = Build vector groups
    """
    if stage > 0 and stage < 5:
        # ############################## Variables ###################################
        BUS_Stage1_BUS = [None]
        BUS_Stage2_BUS = [None]
        BUS_Stage3_BUS = [None]
        BUS_Stage4_BUS = [None]
        
        # STAGE 0 #
        ##print '----Stage 0 -starting-'
        #OPTIONS
        #Prefix
        prefix = cmds.textField('atom_prefix_textField', query=True, text=True)
        #Orient
        rotate = ui.convertAxisNum(cmds.radioButtonGrp('atom_spln_rot_radioButtonGrp', query=True, sl=True)).lower()
        aim    = ui.convertAxisNum(cmds.radioButtonGrp('atom_spln_aim_radioButtonGrp', query=True, sl=True)).lower()
        up     = ui.convertAxisNum(cmds.radioButtonGrp('atom_spln_up_radioButtonGrp' , query=True, sl=True)).lower()
        
        #Float version of rotate,aim,up. ie.(0.0, 1.0, 0.0)
        rotateFloat = ui.getRadioSelectionAsList('atom_spln_rot_radioButtonGrp')
        for i in range(0, len(rotateFloat), 1):
            rotateFloat[i] = float(rotateFloat[i])
        aimFloat = ui.getRadioSelectionAsList('atom_spln_aim_radioButtonGrp')
        for i in range(0, len(aimFloat), 1):
            aimFloat[i] = float(aimFloat[i])
        upFloat = ui.getRadioSelectionAsList('atom_spln_up_radioButtonGrp')
        for i in range(0, len(upFloat), 1):
            upFloat[i] = float(upFloat[i])

        #Scale  multipliers
        ##X = controller scale
        ##Y = vector distance
        X = cmds.floatField('atom_spln_scaleFactor_floatField', q=True, v=True)
        Y = cmds.floatField('atom_spln_vectorDistance_floatField', q=True, v=True)
        F = cmds.floatField('atom_spln_falloff_floatField', q=True, v=True)
        
        #Rotate Order - aim vector should be last in rotate hierarchy
        ## 0=xyz
        ## 1=yzx
        ## 2=zxy
        ## 3=xzy
        ## 4=yxz
        ## 5=zyx
        #rotOrder = 2
        rotOrder =    cmds.optionMenu('atom_spln_rotOrder_optionMenu', query=True, sl=True)-1
        #print '%s,%s,%s,%s,%s' %(str(prefix), str(rotate), str(aim), str(up), str(rotOrder))
        
        #Collect joints
        ##Three objects selected = Means third object parentConstrains spline Ik control group to itself
        Constrain = [False, None, None, None]
        sel = cmds.ls(sl=True)
        if len(sel) == 5:
            cmds.select(sel[:2])
            Constrain[0] = True
            Constrain[1] = sel[2]
            Constrain[2] = sel[3]
            Constrain[3] = sel[4]
            skinJnts = spln.startEndJntList()
            cmds.select(skinJnts)
        if len(sel) == 4:
            cmds.select(sel[:2])
            Constrain[0] = True
            Constrain[1] = sel[2]
            Constrain[2] = sel[3]
            skinJnts = spln.startEndJntList()
            cmds.select(skinJnts)
        elif len(sel) == 3:
            cmds.select(sel[:2])
            Constrain[0] = True
            Constrain[1] = sel[2]
            skinJnts = spln.startEndJntList()
            cmds.select(skinJnts)
        elif len(sel) == 2:    
            skinJnts = spln.startEndJntList()
            cmds.select(skinJnts)
        else:
            mel.eval('warning \"' + '////... Select 2 joints ... Select a 3rd if spline is to be constrained ...////' + '\";')
        ##print '----Stage 0 -variables collected-'
        ##############################################################################

        # ############################## STAGE 1 #####################################
        if stage > 0:
            ##print '----Stage 1 -starting-'
            #NEEDS:
            ## BUS_STAGE_0_BUS
            ##   (skinJnts)          - joint list on which spline is built
            ## OPTIONS
            ##   (aim)               - aim vector
            ##   (up)                - up vector
            ##   (rotOrder)          - rotate order
            ##   (prefix)            - body part
            BUS_Stage1_BUS = build.clusterGroup(prefix, X, skinJnts, aim, up, rotate)
            #RETURNS:
            ##   (clusterGrps)       - cluster groups
            ##   (Sjnt)              - spline start joints
            ##   (ejnt)              - spline end joints
            ##   (Sblnd)             - start blend nodes - stretch on/off
            ##   (Sblnd)             - end blend nodes - stretch on/off
            ##   (Crv)               - start spline curve - tangent constraint in STAGE 4
            ##print '----Stage 1 -cluster group-'
        ##############################################################################

        # ############################## STAGE 2 #####################################
        if stage > 1:
            ##print '----Stage 2 -starting-'
            #NEEDS:
            ## BUS_STAGE_1_BUS
            ##   (clusterGrps)       - cluster groups
            ##   (buildControls)     - boolean, build controls or parent objects in BUS_Stage1_BUS list into hiearchy
            BUS_Stage2_BUS = build.clusterControlGroup(prefix, '_Clstr', X, aim, 1, skinJnts, rotOrder, 0, F, BUS_Stage1_BUS)
            #RETURNS:
            ##   (clusterCntrlGrps)  - cluster control groups
            ##   (ClstrCntrlGrp)  - parent group for clusterCntrlGrps
            ##print '----Stage 2 -cluster control group-'
        else:
            return BUS_Stage1_BUS
        ##############################################################################

        # ############################## STAGE 3 #####################################
        if stage > 2:
            ##print '----Stage 3 -starting-'
            #NEEDS:
            ## BUS_STAGE_0_BUS
            ##   (skinJnts)         - joint list on which spline is built
            ##   (rotOrder)         - rotate order
            ## BUS_STAGE_1_BUS
            ##   (clusterGrps)      - cluster groups
            ##   (Sjnt)             - spline start joints
            ##   (ejnt)             - spline end joints
            ##   (Sblnd)            - start blend nodes - stretch on/off
            ##   (Sblnd)            - end blend nodes - stretch on/off
            ## BUS_STAGE_2_BUS
            ##   (clusterCntrlGrps) - cluster control groups
            BUS_Stage3_BUS = build.ikGroup(prefix, X, skinJnts, rotOrder, BUS_Stage1_BUS, BUS_Stage2_BUS)
            #RETURNS:
            ##   (prnt)             - top group of ik controls
            ##   (vtr)              - up vector group - second to secondlast positions only
            ##   (aim)              - aim vector group - third to last positions only
            ##   (Scnr)             - control objects at start of spline - main/offset
            ##   (Ecnrl)            - control objects at start of spline - main/offset
            ##   (ik)               - integer, returns total number ofcontrol positions, same as len(skinJnts)
            ##   (xjnt)             - matrix test, will be removed...
            ##   (cnstrnt)          - constraint that uses up vector in STAGE 4
            ##print '----Stage 3 -ik control group-'
        else:
            return BUS_Stage2_BUS
        ##############################################################################

        # ############################## STAGE 4 #####################################
        if stage > 3:
            ##print '----Stage 4 -starting-'
            #NEEDS:
            ## BUS_STAGE_0_BUS
            ##   (skinJnts)         - joint list on which spline is built
            ##   (rotOrder)         - rotate order
            ## BUS_STAGE_1_BUS
            ##   (Crv)              - start spline curve - tangent constraint in STAGE 4
            ## BUS_STAGE_3_BUS
            ##   (Scnr)             - control objects at start of spline - main/offset
            ##   (Ecnrl)            - control objects at start of spline - main/offset
            ##   (vtr)              - up vector group - second to secondlast positions only
            ##   (ik)               - integer, returns total number ofcontrol positions, same as len(skinJnts)
            ##   (cnstrnt)          - constraint that uses up vector created in STAGE 4
            ##   (aim)              - aim vector group - third to last positions only
            BUS_Stage4_BUS = build.upVectorGroup(prefix, X, Y, F, skinJnts, aim, up, aimFloat, upFloat, rotOrder, Constrain, BUS_Stage1_BUS, BUS_Stage3_BUS, BUS_Stage2_BUS)
            #RETURNS:
            ## BUS_Stage_4_BUS
            ##   ()
            ##print '----Stage 4 -up vector group-\n'
            return BUS_Stage4_BUS
        else:
            return BUS_Stage3_BUS
        ##############################################################################
        
    else:
        mel.eval('warning \"' + '////... \'stage\' variable must be an integer between -1- and -4- ...////' + '\";')