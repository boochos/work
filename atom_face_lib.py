import maya.cmds as cmds
import maya.mel as mm
import os
import atom_deformer_lib as dfrm
import atom_miscellaneous_lib as misc
import atom_faceRig_lib as faceRig
import atom_placement_lib as place
import atom_olSkoolFix_lib as ol
import atom_ghostDog_lib as agd
import key_util_lib
import key_rig_lib as skn
import atom_splineFk_lib as splnFk
reload(dfrm)
reload(misc)
reload(faceRig)
reload(place)
reload(ol)
reload(agd)
reload(key_util_lib)
reload(skn)
reload(splnFk)


def importFaceAssets(path, importList):
    print path
    files = os.listdir(path)
    importState = []
    # list to check if files exists, assuming false unless changed
    for state in importList:
        importState.append(False)
    idx = 0
    # interate through the importList
    for objFile in importList:
        # interate through all the files in the path directory
        for f in files:
            # check in the name is in the current file
            if objFile == f.split('.')[0]:
                # build import path
                importPath = os.path.join(path, f)
                # set the state, used later for user feedback
                importState[idx] = True
                idx += 1
                # import the file into the scene
                print 'importing: %s' % (importPath)
                cmds.file(importPath, i=True)

    # User feedback for files that were not imported
    for i in range(0, len(importList), 1):
        if importState[i] == False:
            print '===== %s, not found in path, skipping. =====' % (importList[i])


def extractShapeNode(name, orig=False):
    '''
    this can clearly have less 'if' and 'for' stupidity... fix
    '''
    objects = cmds.ls(type='transform')
    returnNode = None
    if cmds.objExists(name):
        for obj in objects:
            # find the 'name' in the object name
            if name == obj:
                shapeList = cmds.listRelatives(obj, shapes=True)
                if name == 'sculpt_Geo' or name == 'special_Geo':
                    return shapeList[0]

                elif shapeList != None:
                    for i in shapeList:
                        # if list connections returns None then the ShapeOrig has been found
                        con = cmds.listConnections(i, s=True, d=False)

                        if orig == True:
                            if con == None:
                                returnNode = i
                        else:
                            if con != None:
                                returnNode = i
    else:
        print '=====%s, does not exists, extraction failed.=====' % (name)
    return returnNode


def setFaceItemsVis(faceList):
    for item in faceList:
        if cmds.objExists(item) == True:
            cmds.setAttr(item + '.visibility', 0)
        else:
            print '===== %s, not found, skipping. =====' % (item)


def connectInToOutMesh(from_geoList, to_geoList):
    # check that the from and to geoLists are the same size
    if len(from_geoList) == len(to_geoList):
        # interate through the outList
        for i in range(0, len(from_geoList), 1):
            # interate through the sides
            sides = ['Lf_', 'Rt_']
            for side in sides:
                # Check that the from object exists
                if cmds.objExists(side + from_geoList[i]) == True:
                    fromShape = cmds.listRelatives(side + from_geoList[i], shapes=True)[0]
                    # check that the to object exists
                    if cmds.objExists(side + to_geoList[i]) == True:
                        toOrig = extractShapeNode(side + to_geoList[i], True)
                        if toOrig != None:
                            cmds.connectAttr(fromShape + '.outMesh', toOrig + '.inMesh', force=True)
                        else:
                            print 'Warning...' + side + to_geoList[i] + ' has no shapeOrig to connect.'
    else:
        print '=====List size miss match, from and to geo lists must have the same length.====='


def parentNonParentedMesh(*args):
    '''groupNode = node to group mesh's to
    '''
    # List all the transforms in the scene
    transforms = cmds.ls(type='transform')
    # interate through them
    for trans in transforms:
        # check if the current transform has a parent
        parentCheck = cmds.listRelatives(trans, parent=True)
        # if there is no parent it warrants further investigation
        if parentCheck == None:
            # get the shapNode
            shapeNode = cmds.listRelatives(trans, type='shape')
            # An unparented group node could throw an error
            # in that is case it wont have a shapeNode
            if shapeNode != None:
                # wanting mesh nodeTypes to group
                if cmds.nodeType(shapeNode[0]) == 'mesh':
                    if trans.rfind('mask') > -1 or trans.rfind('muzzle') > -1 or trans.rfind('sculpt') > -1 or trans.rfind('intermediate') > -1 or trans.rfind('hood') > -1:
                        misc.cleanUp(trans, Utility=True)
                    else:
                        misc.cleanUp(trans, Body=True)


def buildFace(*args):

    X = cmds.floatField('atom_srig_conScale', query=True, value=True)
    # Assume that the current open file has been opened from the correct directory and get the base path from that
    path = os.path.dirname(cmds.file(query=True, exn=True))

    # Files to import
    importList = ['Mask', 'Muzzle', 'FaceRig', 'Sculpt', 'Special']

    # Geo to connect outMesh
    from_geoList = ['eye_FrGeo', 'eyeouter_FrGeo', 'eyewater_FrGeo']

    # Geo to connect inMesh
    to_geoList = ['eye_Geo', 'eyeouter_Geo', 'eyewater_Geo']

    # import the face assets
    importFaceAssets(path, importList)

    # Connect the outMesh to the inMesh of the specific geo
    connectInToOutMesh(from_geoList, to_geoList)

    # Connect the tongue geo
    if cmds.objExists('tongue_FrGeo') == True:
        tongueShape = cmds.listRelatives('tongue_FrGeo', shapes=True)[0]
        if cmds.objExists('tongue_Geo') == True:
            tongueOrg = extractShapeNode('tongue_Geo', True)
            cmds.connectAttr(tongueShape + '.outMesh', tongueOrg + '.inMesh', force=True)
        else:
            print '=====tongue_Geo does not exist, skipping tongue connection.====='
    else:
        print '=====tongue_FrGeo does not exist, skipping tongue connection.====='

    # extract the shape and orig nodes from their transforms
    head = extractShapeNode('head_Geo', False)
    print head
    headOrig = extractShapeNode('head_Geo', True)
    print headOrig
    headFr = extractShapeNode('head_FrGeo', False)
    mask = extractShapeNode('mask_Geo', False)
    muzzle = extractShapeNode('muzzle_Geo', False)
    sculpt = extractShapeNode('sculpt_Geo', False)
    special = extractShapeNode('special_Geo', False)

    # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
    headInter = cmds.duplicate(head, name=head + '_intermediateGeo')[0]

    # setup the objects to connect
    connectionList = [headFr, mask, muzzle, sculpt, headInter]
    # create the blendShape
    blendNode = cmds.blendShape(headFr, mask, muzzle, sculpt, special, headInter, n='face_blendshape')
    # set the blendNode target weights
    trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
    trgs = cmds.blendShape(blendNode, query=True, t=True)
    for i in range(0, trgCnt, 1):
        if trgs[i] != 'special_Geo':
            cmds.blendShape(blendNode, edit=True, w=(i, 1))

    # Visibility list
    setVisList = ['muzzle_root_jnt', 'maskEdge_jnt_root', 'mask_Geo', 'sculpt_Geo', 'faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                  'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo', 'muzzle_Geo', 'special_Geo']

    # Connect the blendShape to the Orig node
    cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', headOrig + '.inMesh', force=True, )

    setFaceItemsVis(setVisList)

    # Sebastian made me add this --starting here
    # create deformer contorllers
    Attach = 'neck_jnt_06'  # constrain deformer anim groups to this object
    Vis = 'head'  # attach deformer anim group vis to this controller
    dfrm.master(deformer=True)
    # mask
    if cmds.objExists(setVisList[1]) == True:
        msk = dfrm.mask(cleanUp=True)
        cmds.parentConstraint(Attach, msk, mo=True)
        misc.optEnum(Vis)
        misc.hijackVis(msk, Vis, name='mask', default=0)
    # muzzle
    if cmds.objExists(setVisList[0]) == True:
        # single chain muzzle
        if cmds.objExists('muzzle_jnt_001') == True:
            mzzl = dfrm.muzzle(cleanUp=True)
            cmds.parentConstraint(Attach, mzzl, mo=True)
            misc.hijackVis(mzzl, Vis, name='muzzle', default=0)
        # double chain muzzle
        upper = 'upperMuzzle_jnt_001'
        nU = 'muzzleUpper'
        lower = 'lowerMuzzle_jnt_001'
        nL = 'muzzleLower'
        if cmds.objExists(upper) == True:
            # upper
            U_mzzl = dfrm.muzzle(root=upper, name=nU, cleanUp=True, shape='ballRoll_ctrl', size=X)
            cmds.parentConstraint(Attach, U_mzzl, mo=True)
            misc.hijackVis(U_mzzl, Vis, name=nU, default=0)
            # lower
            L_mzzl = dfrm.muzzle(root=lower, name=nL, cleanUp=True, shape='ballRoll_ctrl', size=X)
            cmds.parentConstraint(Attach, L_mzzl, mo=True)
            misc.hijackVis(L_mzzl, Vis, name=nL, default=0)
    # sculpt
    if cmds.objExists(setVisList[3]) == True:
        # _OLD_## mirrorList = dfrm.nameSculpt()[2:5:]
        mirrorList = dfrm.nameSculpt()[6:11:]
        for item in mirrorList:
            dfrm.sculptMirror('deformer_' + item, group=False)
        # sculpt controllers
        defTool = dfrm.nameSculpt()
        for item in defTool:
            sclpt = dfrm.sculpt('sculpt_Geo', deformer='deformer_' + item, name='sculpt_' + item)
        cmds.parentConstraint(Attach, sclpt, mo=True)
        misc.hijackVis(sclpt, Vis, name='sculpt', default=0)
    # tongue
    if cmds.objExists('root_tongue_jnt') == True:
        skin = skn.getSkinCluster('tongue_FrGeo')
        cmds.setAttr(skin + '.envelope', 0)
        grp = place.null2('jawAssist', 'jaw', orient=True)[0]
        cmds.setAttr(grp + '.rotateOrder', 2)
        misc.cleanUp(grp, World=True)
        cmds.parentConstraint('jaw', grp, mo=True)
        spine = splnFk.SplineFK('tongue_rig', 'root_tongue_jnt', 'tongue_08_jnt', None, rootParent=grp, parent1=grp, segIteration=3, controllerSize=X * 4, ik='splineIK', stretch=1)
        misc.shapeSize(spine.rootCt[2], 3)
        misc.shapeSize(spine.rootCt[3], 3)

    # clean up OL_SKOOL rig, add to Finalize later
    cmds.setAttr('Up_lip_2x|faceSharedAttr.macroVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.mainVisibility', 1)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.microVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.tongueVisibility', 0)
    cmds.select('LfUpBk_lipShape.cv[0:12]', 'LfUpBk_lipShape1.cv[0:12]', 'LfUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('RtUpBk_lipShape.cv[0:12]', 'RtUpBk_lipShape1.cv[0:12]', 'RtUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('Lf_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.select('Rt_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.delete('Lf_eyeFKAim_GpGp', 'Rt_eyeFKAim_GpGp ')
    ol.lockCT(*args)
    #--ending here

    # parent the face grp to the head
    cmds.parentConstraint('neck_jnt_06', 'faceCtrl_Gp', mo=True)
    # parent all the non parented mesh
    parentNonParentedMesh()
    # Parent the facerig groups to the proper group
    parentList = ['faceCtrl_Gp', 'faceJnt_Gp', 'faceUtil_Gp', 'faceGeo_Gp', 'Lf_eyeFKAim_Gp', 'Rt_eyeFKAim_Gp']

    for obj in parentList:
        if cmds.objExists(obj) == True:
            cmds.parent(obj, '___OL_SKOOL')


def buildGhostDogFace(*args):
    # Assume that the current open file has been opened from the correct directory and get the base path from that
    path = os.path.dirname(cmds.file(query=True, exn=True))
    # Files to import
    importList = ['FaceRig']

    # Geo to connect outMesh
    from_geoList = ['eye_FrGeo', 'eyeouter_FrGeo', 'eyewater_FrGeo']

    # Geo to connect inMesh
    to_geoList = ['eye_Geo', 'eyeouter_Geo', 'eyewater_Geo']

    # import the face assets
    importFaceAssets(path, importList)

    # Connect the outMesh to the inMesh of the specific geo
    connectInToOutMesh(from_geoList, to_geoList)

    # Connect the tongue geo
    if cmds.objExists('tongue_FrGeo') == True:
        tongueShape = cmds.listRelatives('tongue_FrGeo', shapes=True)[0]
        if cmds.objExists('tongue_Geo') == True:
            tongueOrg = extractShapeNode('tongue_Geo', True)
            cmds.connectAttr(tongueShape + '.outMesh', tongueOrg + '.inMesh', force=True)
        else:
            print '=====tongue_Geo does not exist, skipping tongue connection.====='
    else:
        print '=====tongue_FrGeo does not exist, skipping tongue connection.====='

    # extract the shape and orig nodes from their transforms
    head = extractShapeNode('head_Geo', False)
    headOrig = extractShapeNode('head_Geo', True)
    headFr = extractShapeNode('head_FrGeo', False)
    ear = None
    # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
    headInter = cmds.duplicate(head, name=head + '_intermediateGeo')[0]

    # setup the objects to connect
    connectionList = [headFr, headInter]
    # Build the ears
    if cmds.checkBox('atom_ghstDog_earCheck', q=True, v=True):
        agd.buildGhostDogEars()
        ear = extractShapeNode('earRig_head_Geo', False)
        cmds.setAttr('earRig_head_Geo.visibility', 0)

    # create the blendShape
    blendNode = cmds.blendShape(headFr, ear, headInter, n='face_blendshape')

    # set the blendNode target weights
    trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
    for i in range(0, trgCnt, 1):
        cmds.blendShape(blendNode, edit=True, w=(i, 1))

    # Connect the blendShape to the Orig node
    cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', headOrig + '.inMesh', force=True, )

    # Visibility list
    setVisList = ['faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                  'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo']
    setFaceItemsVis(setVisList)

    # parent the face grp to the head
    cmds.parentConstraint('neck_jnt_06', 'faceCtrl_Gp', mo=True)

    # Sebastian made me add this --starting here
    # create deformer contorllers
    dfrm.master(deformer=True)

    # sculpt
    '''
    ##_OLD_## mirrorList = dfrm.nameSculpt()[2:5:]
    mirrorList = dfrm.nameSculpt()[6:11:]
    for item in mirrorList:
        dfrm.sculptMirror('deformer_' + item, group=False)
    ##sculpt controllers
    defTool = dfrm.nameSculpt()
    for item in defTool:
        sclpt = dfrm.sculpt('sculpt_Geo', deformer='deformer_' + item, name='sculpt_' + item)
    #attach
    Attach = 'neck_jnt_06' ##constrain deformer anim groups to this object
    Vis    = 'head' ##attach deformer anim group vis to this controller
    ##constrain
    cmds.parentConstraint(Attach, sclpt, mo=True)
    ##connect vis attr
    misc.optEnum(Vis)
    misc.hijackVis(sclpt, Vis, name='sculpt', default=0)
    '''

    # clean up OL_SKOOL rig, add to Finalize later
    cmds.setAttr('Up_lip_2x|faceSharedAttr.macroVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.mainVisibility', 1)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.microVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.tongueVisibility', 0)
    cmds.select('LfUpBk_lipShape.cv[0:12]', 'LfUpBk_lipShape1.cv[0:12]', 'LfUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('RtUpBk_lipShape.cv[0:12]', 'RtUpBk_lipShape1.cv[0:12]', 'RtUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('Lf_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.select('Rt_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.delete('Lf_eyeFKAim_GpGp', 'Rt_eyeFKAim_GpGp ')
    #--ending here

    # parent the face grp to the head
    cmds.parentConstraint('neck_jnt_06', 'faceCtrl_Gp', mo=True)
    # parent all the non parented mesh
    parentNonParentedMesh()
    # Parent the facerig groups to the proper group
    parentList = ['faceCtrl_Gp', 'faceJnt_Gp', 'faceUtil_Gp', 'faceGeo_Gp', 'Lf_eyeFKAim_Gp', 'Rt_eyeFKAim_Gp']

    for obj in parentList:
        if cmds.objExists(obj) == True:
            # added this in case the
            try:
                cmds.parent(obj, '___OL_SKOOL')
            except:
                pass


def buildSnakeFace(*args):
    # Assume that the current open file has been opened from the correct directory and get the base path from that
    path = os.path.dirname(cmds.file(query=True, exn=True))
    # Files to import
    importList = ['FaceRig', 'hood', 'chest']

    # Geo to connect outMesh
    from_geoList = ['eye_FrGeo', 'eyeouter_FrGeo', 'eyewater_FrGeo']

    # Geo to connect inMesh
    to_geoList = ['eye_Geo', 'eyeouter_Geo', 'eyewater_Geo']

    # import the face assets
    importFaceAssets(path, importList)

    # Connect the outMesh to the inMesh of the specific geo
    connectInToOutMesh(from_geoList, to_geoList)

    # Connect the tongue geo
    if cmds.objExists('tongue_FrGeo') == True:
        tongueShape = cmds.listRelatives('tongue_FrGeo', shapes=True)[0]
        if cmds.objExists('tongue_Geo') == True:
            tongueOrg = extractShapeNode('tongue_Geo', True)
            cmds.connectAttr(tongueShape + '.outMesh', tongueOrg + '.inMesh', force=True)
        else:
            print '=====tongue_Geo does not exist, skipping tongue connection.====='
    else:
        print '=====tongue_FrGeo does not exist, skipping tongue connection.====='

    # extract the shape and orig nodes from their transforms
    head = extractShapeNode('head_Geo', False)
    headOrig = extractShapeNode('head_Geo', True)
    headFr = extractShapeNode('head_FrGeo', False)
    hood = extractShapeNode('hood_Geo', False)
    chest = extractShapeNode('chest_Geo', False)

    # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
    headInter = cmds.duplicate(head, name=head + '_intermediateGeo')[0]

    # setup the objects to connect
    connectionList = [headFr, hood, headInter]
    # create the blendShape
    blendNode = cmds.blendShape(headFr, hood, chest, headInter, n='face_blendshape')

    # set the blendNode target weights
    trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
    for i in range(0, trgCnt, 1):
        cmds.blendShape(blendNode, edit=True, w=(i, 1))

    # Visibility list
    setVisList = ['chest_Geo', 'hood_Geo', 'hood_root_jnt', 'sculpt_Geo', 'faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                  'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo']
    setFaceItemsVis(setVisList)

    # Connect the blendShape to the Orig node
    cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', headOrig + '.inMesh', force=True, )

    # parent the face grp to the head
    cmds.parentConstraint('head_jnt', 'faceCtrl_Gp', mo=True)
    # parent all the non parented mesh
    parentNonParentedMesh()
    # Parent the facerig groups to the proper group
    parentList = ['faceCtrl_Gp', 'faceJnt_Gp', 'faceUtil_Gp', 'faceGeo_Gp', 'Lf_eyeFKAim_Gp', 'Rt_eyeFKAim_Gp']
    for obj in parentList:
        if cmds.objExists(obj) == True:
            cmds.parent(obj, '___OL_SKOOL')

    # Sebastian added this section
    #--start--#
    # clean up OL_SKOOL rig, add to Finalize later
    cmds.setAttr('Up_lip_2x|faceSharedAttr.macroVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.mainVisibility', 1)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.microVisibility', 0)
    cmds.setAttr('Up_lip_2x|faceSharedAttr.tongueVisibility', 0)
    cmds.select('LfUpBk_lipShape.cv[0:12]', 'LfUpBk_lipShape1.cv[0:12]', 'LfUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('RtUpBk_lipShape.cv[0:12]', 'RtUpBk_lipShape1.cv[0:12]', 'RtUpBk_lipShape2.cv[0:12]')
    cmds.scale(0.5, 0.5, 0.5)
    cmds.select('Lf_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.select('Rt_eyeFK.cv[0:16]')
    cmds.scale(2.0, 1.0, 1.0)
    cmds.delete('Lf_eyeFKAim_GpGp', 'Rt_eyeFKAim_GpGp ')

    X = cmds.floatField('atom_srig_conScale', query=True, value=True)
    # hood
    dfrm.master(deformer=True)
    hood_l = dfrm.spline(SPLN_Name='hood_L', SPLN_Size=X * 4, SPLN_Dist=3.0, SPLN_Falloff=0,
                         SPLN_Prnt=['head_jnt', 'upperC_jnt_04', 'upperB_jnt_02'],
                         SPLN_Attr='hood_L', SPLN=['hood_root_jnt_L', 'hood_jnt_20_L'],
                         SPLN_Vis=['cntrlName', 'attrName'], mirror=False, cleanUp=True)
    hood_r = dfrm.spline(SPLN_Name='hood_R', SPLN_Size=X * 4, SPLN_Dist=3.0, SPLN_Falloff=0,
                         SPLN_Prnt=['head_jnt', 'upperC_jnt_04', 'upperB_jnt_02'],
                         SPLN_Attr='hood_R', SPLN=['hood_root_jnt_R', 'hood_jnt_20_R'],
                         SPLN_Vis=['cntrlName', 'attrName'], mirror=True, cleanUp=True)
    # chest
    chest = dfrm.spline(SPLN_Name='chest', SPLN_Size=X * 4, SPLN_Dist=3.0, SPLN_Falloff=0,
                        SPLN_Prnt=['head_jnt', 'upperC_jnt_04', 'upperB_jnt_02'],
                        SPLN_Attr='chest', SPLN=['chest_root_jnt_L', 'chest_jnt_20_L'],
                        SPLN_Vis=['cntrlName', 'attrName'], mirror=False, cleanUp=True)
    # tongue
    tongueMicro = faceRig.snakeTongue('tongue', 1.0)
    # break OL_SKOOL tongue
    cmds.disconnectAttr('tongue_FrGeoShape.outMesh', 'tongue_GeoShapeOrig.inMesh')
    # fangs
    fangL = place.Controller('fang_L', 'fang_jnt_L', orient=False, shape='facetYup_ctrl', size=2, color=17, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
    fangLCt = fangL.createController()
    fangR = place.Controller('fang_R', 'fang_jnt_R', orient=False, shape='facetYup_ctrl', size=2, color=17, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
    fangRCt = fangR.createController()
    cmds.parentConstraint(fangLCt[4], 'fang_jnt_L', mo=True)
    cmds.parentConstraint(fangRCt[4], 'fang_jnt_R', mo=True)
    cmds.parentConstraint('head_jnt', fangLCt[0], mo=True)
    cmds.parentConstraint('head_jnt', fangRCt[0], mo=True)
    misc.cleanUp(fangLCt[0], Ctrl=True)
    misc.cleanUp(fangRCt[0], Ctrl=True)
    #--end--#


def getGeoInputs(importList=['pin', 'breast'], *args):
    geoMap = {'ZBrush_defualt_group002': ['breast_Geo', 'pin_Geo'], '__CLASHCLASH___ZBrush_defualt_group002': ['breast_Geo_M', 'pin_Geo_M'], '__CLASHCLASH___ZBrush_defualt_group003': ['breast_Geo_H', 'pin_Geo_H']}

    # Assume that the current open file has been opened from the correct directory and get the base path from that
    path = os.path.dirname(cmds.file(query=True, exn=True))
    # import the face assets, items in list are actual file names
    importFaceAssets(path, importList=importList)

    for key in geoMap:
        resultGeo = extractShapeNode(key, False)
        resultOrig = extractShapeNode(key, True)
        # new
        # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
        resultInter = cmds.duplicate(resultGeo, name=resultGeo + '_intermediateGeo')[0]
        corr = []
        for geo in geoMap[key]:
            corr.append(extractShapeNode(geo, False))
        corr.append(resultInter)
        # new end

        # create the blendShape
        # blendNode = cmds.blendShape(hood, chest, headInter, n='face_blendshape') # old
        blendNode = cmds.blendShape(corr, n='face_blendshape')  # new

        # set the blendNode target weights
        trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
        for i in range(0, trgCnt, 1):
            cmds.blendShape(blendNode, edit=True, w=(i, 1))
        '''
        # Visibility list
        setVisList = ['chest_Geo', 'hood_Geo', 'hood_root_jnt', 'sculpt_Geo', 'faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                      'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo']
        setFaceItemsVis(setVisList)
        '''
        # Connect the blendShape to the Orig node
        cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', resultOrig + '.inMesh', force=True)
    #
    X = cmds.floatField('atom_srig_conScale', query=True, value=True)
    # clean up geo and joints
    for geo in corr:
        misc.cleanUp(geo, Utility=True)
    # floaters
    slave, master = dfrm.floatingControl(name='pin', parent='clavicle_jnt_02_L', joint='pin_jnt', size=X * 6, shape='arrow_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)
    slave, master = dfrm.floatingControl(name='breast_L', parent='spine_jnt_06', joint='breast_jnt_L', size=X * 15, shape='arrow_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)
    slave, master = dfrm.floatingControl(name='breast_R', parent='spine_jnt_06', joint='breast_jnt_R', size=X * 15, shape='arrowInv_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)


def getGeoInputsOld(resultGeo='ZBrush_defualt_group002', correctiveGeo=['breast_Geo', 'pin_Geo'], importList=['pin', 'breast'], *args):
    geoMap = {'ZBrush_defualt_group002': ['breast_Geo', 'pin_Geo'], '__CLASHCLASH___ZBrush_defualt_group002': ['breast_Geo_M', 'pin_Geo_M'], '__CLASHCLASH___ZBrush_defualt_group003': ['breast_Geo_H', 'pin_Geo_H']}

    # Assume that the current open file has been opened from the correct directory and get the base path from that
    path = os.path.dirname(cmds.file(query=True, exn=True))
    # import the face assets, items in list are actual file names
    importFaceAssets(path, importList=importList)

    head = extractShapeNode(resultGeo, False)
    headOrig = extractShapeNode(resultGeo, True)
    # hood = extractShapeNode('breast_Geo', False)
    # chest = extractShapeNode('pin_Geo', False)
    # new
    # Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
    headInter = cmds.duplicate(head, name=head + '_intermediateGeo')[0]
    corr = []
    for geo in correctiveGeo:
        corr.append(extractShapeNode(geo, False))
    corr.append(headInter)
    # new end

    # create the blendShape
    # blendNode = cmds.blendShape(hood, chest, headInter, n='face_blendshape') # old
    blendNode = cmds.blendShape(corr, n='face_blendshape')  # new

    # set the blendNode target weights
    trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
    for i in range(0, trgCnt, 1):
        cmds.blendShape(blendNode, edit=True, w=(i, 1))
    '''
    # Visibility list
    setVisList = ['chest_Geo', 'hood_Geo', 'hood_root_jnt', 'sculpt_Geo', 'faceUtil_Gp', 'faceJnt_Gp', headInter, 'head_FrGeo', 'Lf_eye_FrGeo', 'Lf_eyeouter_FrGeo',
                  'Lf_eyewater_FrGeo', 'Rt_eye_FrGeo', 'Rt_eyeouter_FrGeo', 'Rt_eyewater_FrGeo', 'tongue_FrGeo']
    setFaceItemsVis(setVisList)
    '''
    # Connect the blendShape to the Orig node
    cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', headOrig + '.inMesh', force=True)
    #
    X = cmds.floatField('atom_srig_conScale', query=True, value=True)
    # clean up geo and joints
    for geo in corr:
        misc.cleanUp(geo, Utility=True)
    # floaters
    slave, master = dfrm.floatingControl(name='pin', parent='clavicle_jnt_02_L', joint='pin_jnt', size=X * 6, shape='arrow_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)
    slave, master = dfrm.floatingControl(name='breast_L', parent='spine_jnt_06', joint='breast_jnt_L', size=X * 15, shape='arrow_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)
    slave, master = dfrm.floatingControl(name='breast_R', parent='spine_jnt_06', joint='breast_jnt_R', size=X * 15, shape='arrowInv_ctrl')
    misc.cleanUp(slave[0], World=True)
    misc.cleanUp(master[0], Ctrl=True)
