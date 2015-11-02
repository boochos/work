import maya.cmds as cmds
import atom_placement_lib as place
import atom_miscellaneous_lib as misc
import atom_joint_lib as find


def cleanUp(obj, deformer=False, maskAnim=False, maskClone=False,
            muzzleAnim=False, muzzleClone=False,
            upperMuzzleAnim=False, upperMuzzleClone=False,
            lowerMuzzleAnim=False, lowerMuzzleClone=False,
            sculptAnim=False, sculptClone=False, sculptGeo=False,
            splineAnim=False, splineClone=False):
    '''\n

    '''
    # Deformer
    if deformer == True:
        deformer = nameMaster(deformer=True)
        cmds.parent(obj, deformer)
    # Mask
    if maskAnim == True:
        maskAnim = nameMaster(mask=True)[1]
        cmds.parent(obj, maskAnim)
    if maskClone == True:
        maskClone = nameMaster(mask=True)[2]
        cmds.parent(obj, maskClone)
    # Muzzle
    if muzzleAnim == True:
        muzzleAnim = nameMaster(muzzle=True)[1]
        cmds.parent(obj, muzzleAnim)
    if muzzleClone == True:
        muzzleClone = nameMaster(muzzle=True)[2]
        cmds.parent(obj, muzzleClone)
    # upperMuzzle
    if upperMuzzleAnim == True:
        upperMuzzleAnim = nameMaster(upperMuzzle=True)[1]
        cmds.parent(obj, upperMuzzleAnim)
    if upperMuzzleClone == True:
        upperMuzzleClone = nameMaster(upperMuzzle=True)[2]
        cmds.parent(obj, upperMuzzleClone)
    # lowerMuzzle
    if lowerMuzzleAnim == True:
        lowerMuzzleAnim = nameMaster(lowerMuzzle=True)[1]
        cmds.parent(obj, lowerMuzzleAnim)
    if lowerMuzzleClone == True:
        lowerMuzzleClone = nameMaster(lowerMuzzle=True)[2]
        cmds.parent(obj, lowerMuzzleClone)
    # Sculpt
    if sculptAnim == True:
        sculptAnim = nameMaster(sculpt=True)[1]
        cmds.parent(obj, sculptAnim)
    if sculptClone == True:
        sculptClone = nameMaster(sculpt=True)[2]
        cmds.parent(obj, sculptClone)
    if sculptGeo == True:
        sculptGeo = nameMaster(sculpt=True)[3]
        cmds.parent(obj, sculptGeo)
    # Spline
    if splineAnim == True:
        splineAnim = nameMaster(spline=True)[1]
        cmds.parent(obj, splineAnim)
    if splineClone == True:
        splineClone = nameMaster(spline=True)[2]
        cmds.parent(obj, splineClone)


def makeClone(obj, maskClone=False, muzzleClone=False, orient=False):
    '''\n

    '''
    parent = place.null2(obj + '_CloneTopGrp', obj, orient)[0]
    child = place.null2(obj + '_CloneCtGrp', obj, orient)[0]
    offset = place.null2(obj + '_CloneOffstGrp', obj, orient)[0]
    cmds.parent(offset, child)
    cmds.parent(child, parent)
    if maskClone == True:
        cleanUp(parent, maskClone=True)
    if muzzleClone == True:
        cleanUp(parent, muzzleClone=True)
    return offset, child, parent


def makeJointClone(root, name='_clone', pad=2, suffix=None):
    '''\n
    root   = object at top of hierarchy\n
    *cloned root       = cloned root should later get parent constrained to an animated control(ie. head control)
    *cloned children   = children under cloned root drive via direct connects to original joints
    name   = new name\n
    pad    = number padding, 2 is default\n
    suffix = string (ie. 'L' or 'R')\n
    '''
    # original joints
    cmds.select(root, hi=True)
    original = cmds.ls(sl=True, l=True)
    # cloned joints
    dup = cmds.duplicate(root, rc=True)
    clones = misc.renameHierarchy(dup[0], name, pad, suffix)
    # connect joints
    for i in range(1, len(clones), 1):
        misc.hijack(original[i], clones[i])
    return clones


def fullConstraint(obj1, obj2):
    '''\n

    '''
    cmds.parentConstraint(obj1, obj2, mo=True)
    cmds.scaleConstraint(obj1, obj2, mo=True)


def nameMaster(deformer=False, mask=False, muzzle=False, upperMuzzle=False, lowerMuzzle=False, sculpt=False, spline=False):
    '''\n
    Default names of master groups\n
    Only use one at a time. All other should remain as 'False'\n
    '''
    if deformer == True:
        result = 'deformerGrp'
    if mask == True:
        result = ['maskGrp', 'mask_AnimGrp', 'mask_CloneGrp']
    if muzzle == True:
        result = ['muzzleGrp', 'muzzle_AnimGrp', 'muzzle_CloneGrp']
    if upperMuzzle == True:
        result = ['upperMuzzleGrp', 'upperMuzzle_AnimGrp', 'upperMuzzle_CloneGrp']
    if lowerMuzzle == True:
        result = ['lowerMuzzleGrp', 'lowerMuzzle_AnimGrp', 'lowerMuzzle_CloneGrp']
    if sculpt == True:
        result = ['sculptGrp', 'sculpt_AnimGrp', 'sculpt_CloneGrp', 'sculpt_GeoGrp']
    if spline == True:
        result = ['splineGrp', 'spline_AnimGrp', 'spline_CloneGrp']
    return result


def master(deformer=False, mask=False, muzzle=False, upperMuzzle=False, lowerMuzzle=False, sculpt=False, spline=False, cleanUp=True):
    '''\n

    '''
    dfrmr = nameMaster(deformer=True)
    msk = nameMaster(mask=True)
    mzzle = nameMaster(muzzle=True)
    Umzzle = nameMaster(upperMuzzle=True)
    Lmzzle = nameMaster(lowerMuzzle=True)
    sclpt = nameMaster(sculpt=True)
    spln = nameMaster(spline=True)
    if deformer == True:
        dfrmr = nameMaster(deformer=True)
        null = cmds.group(em=True, n=dfrmr)
        if cleanUp == True:
            misc.cleanUp(null, Ctrl=True)
    if mask == True:
        null = cmds.group(em=True, n=msk[0])
        nullAnim = cmds.group(em=True, n=msk[1])
        nullClone = cmds.group(em=True, n=msk[2])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if muzzle == True:
        null = cmds.group(em=True, n=mzzle[0])
        nullAnim = cmds.group(em=True, n=mzzle[1])
        nullClone = cmds.group(em=True, n=mzzle[2])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if upperMuzzle == True:
        null = cmds.group(em=True, n=Umzzle[0])
        nullAnim = cmds.group(em=True, n=Umzzle[1])
        nullClone = cmds.group(em=True, n=Umzzle[2])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if lowerMuzzle == True:
        null = cmds.group(em=True, n=Lmzzle[0])
        nullAnim = cmds.group(em=True, n=Lmzzle[1])
        nullClone = cmds.group(em=True, n=Lmzzle[2])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if sculpt == True:
        null = cmds.group(em=True, n=sclpt[0])
        nullAnim = cmds.group(em=True, n=sclpt[1])
        nullClone = cmds.group(em=True, n=sclpt[2])
        nullGeo = cmds.group(em=True, n=sclpt[3])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(nullGeo, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullGeo, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if spline == True:
        null = cmds.group(em=True, n=spln[0])
        nullAnim = cmds.group(em=True, n=spln[1])
        nullClone = cmds.group(em=True, n=spln[2])
        cmds.parent(nullAnim, null)
        cmds.parent(nullClone, null)
        cmds.parent(null, dfrmr)
        misc.setChannels(null, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullAnim, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False])
        misc.setChannels(nullClone, translate=[True, False], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
    if sculpt == True:
        return null, nullAnim, nullClone, nullGeo
    elif deformer == True:
        return null
    else:
        return null, nullAnim, nullClone


def childrenOf(obj, root=False):
    '''\n

    '''
    cmds.select(obj, hi=True)
    if root == False:
        sel = cmds.ls(sl=True, fl=True)[1:]
    else:
        sel = cmds.ls(sl=True, fl=True)
    return sel


def muzzle(root='muzzle_jnt_001', name='muzzle', cleanUp=False, size=9.5, m=True, uM=False, lM=False, shape='ballRoll_ctrl'):
    '''\n
    root = joint from which to start placing controllers down chain
    name = prefix
    size = size of controllers
    '''
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    import atom_deformer_lib as dfrmr
    Master = None
    if cleanUp == True:
        rootJnt = find.root(root)
        misc.cleanUp(rootJnt, SknJnts=True)
    if 'upperMuzzle' in root:
        masterNames = dfrmr.nameMaster(upperMuzzle=True)
    elif 'lowerMuzzle' in root:
        masterNames = dfrmr.nameMaster(lowerMuzzle=True)
    elif 'muzzle' in root:
        masterNames = dfrmr.nameMaster(muzzle=True)
    if cmds.objExists(masterNames[0]) == 0:
        if 'upperMuzzle' in root:
            Master = dfrmr.master(upperMuzzle=True)
        elif 'lowerMuzzle' in root:
            Master = dfrmr.master(lowerMuzzle=True)
        elif 'muzzle' in root:
            Master = dfrmr.master(muzzle=True)
    else:
        print '--------THIS IS BROKEN---------\n'
    controls, clones = place.controllerDownChain(root, name, pad=3, base=None, parent=None, shape=shape, color=31, size=X * size, groups=True, orient=True, suffix=None, scale=True, setChannel=True, clone=True, fk=True)
    if 'upperMuzzle' in root:
        dfrmr.cleanUp(controls[0][0], upperMuzzleAnim=True)
        dfrmr.cleanUp(clones[0][0], upperMuzzleClone=True)
    if 'lowerMuzzle' in root:
        dfrmr.cleanUp(controls[0][0], lowerMuzzleAnim=True)
        dfrmr.cleanUp(clones[0][0], lowerMuzzleClone=True)
    if 'muzzle' in root:
        dfrmr.cleanUp(controls[0][0], muzzleAnim=True)
        dfrmr.cleanUp(clones[0][0], muzzleClone=True)
    # return controls[0][0], Master[1]
    return Master[1]


def nameSculpt():
    name = ['crown', 'brow', 'muzzle', 'nose', 'chin', 'neck', 'brow_L', 'cheek_L', 'jaw_L', 'temple_L', 'nostril_L', 'brow_R', 'cheek_R', 'jaw_R', 'temple_R', 'nostril_R']
    return name


def sculptSpheres():
    '''
    currently not used anywhere
    sculpt deformer is too heavy
    '''
    i = 0
    name = nameSculpt()
    deformerSculpt = None
    while i <= 4:
        deformerTool = cmds.sphere(name='deformer_' + name[i], p=(0, 0, 0), ax=(0, 1, 0), ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=12, nsp=6, ch=1)
        if i > 1:
            deformerTool[1] = cmds.rename(deformerTool[1], name[i][:len(name[i]) - 1] + 'shapeUtl_' + name[i][len(name[i]) - 1:])
        else:
            deformerTool[1] = cmds.rename(deformerTool[1], name[i] + '_shapeUtl')
        i = i + 1


def sculptMirror(objL, group=False):
    '''\n
    mirrors nurbSphere across X axis, with group above\n
    '''
    # new name for history node
    newHis = None
    history = cmds.listHistory(objL)
    '''
	for item in history:
		if 'shapeUtl' in item:
			newHis =  item.replace('_L', '_R')
			break
	'''
    # new name for sphere
    objR = objL.replace('_L', '_R')
    # mirror items
    mirrorGrp = place.null2(objR[:len(objR) - 1] + 'Grp_' + objR[len(objR) - 1:], objL, orient=True)
    mirrorObj = cmds.duplicate(objL, rr=True, un=True, n=objR)
    # duplicate history node
    #mirrorHis = cmds.listHistory(mirrorObj)
    # rename history node on mirror
    '''
	for item in mirrorHis:
		if 'shapeUtl' in item:
			cmds.rename(item, newHis)
	'''
    # mirror group
    tmp = cmds.group(em=True, n='tmp')
    cmds.parent(mirrorObj[0], mirrorGrp)
    cmds.parent(mirrorGrp, tmp)
    # mirror
    cmds.scale(-1, 1, 1, tmp)
    # delete mirror group
    cmds.parent(mirrorGrp, w=True)
    cmds.delete(tmp)
    if group == False:
        cmds.parent(mirrorObj, w=True)
        cmds.delete(mirrorGrp)
        return mirrorObj[0]
    else:
        return mirrorGrp, mirrorObj[0]


def sculpt(geo, deformer=False, name='sculptTool', size=2, orient=False):
    '''\n
    geo       = geo to be deformed\n
    deformer  = object to be used as deformation tool of 'geo'. If 'False', a generic sphere will be created at origin\n
    size      = size of controllers\n
    '''
    color = 15
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    import atom_deformer_lib as dfrmr

    def hijackSculpt(node, obj, name=name, envelope=True, outsideFalloffDist=True):
        '''\n
        node = sculpt node\n
        obj  = object hijacking 'nodes' attrs\n
        name = prefix tag for attrs\n
        '''
        if envelope == True:
            misc.hijackAttrs(node, obj, 'envelope', name + '_Envelope')
            cmds.setAttr(obj + '.' + name + '_Envelope', 0.5)
        if outsideFalloffDist == True:
            misc.hijackAttrs(node, obj, 'outsideFalloffDist', name + '_Dropoff')
            cmds.setAttr(obj + '.' + name + '_Dropoff', k=True)

    defObj = None
    Master = None
    # master
    masterNames = dfrmr.nameMaster(sculpt=True)
    if cmds.objExists(masterNames[0]) == 0:
        Master = dfrmr.master(sculpt=True)
    else:
        Master = masterNames
    # deformer
    if deformer == False:
        # NO SPHERES ARE BEING USED. THIS IS OBSOLETE
        print '----------WHY IS THIS BEING RUN---------\n', '----------CHECK DEFORMER MODULE----------'
        # make sphere as deformer
        deformerTool = cmds.sphere(name=name + '_Geo', p=(0, 0, 0), ax=(0, 1, 0), ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=12, nsp=6, ch=1)
        deformerTool[1] = cmds.rename(deformerTool[1], name + '_shapeUtl')
        defObj = deformerTool[0]
    else:
        defObj = deformer
    # controls
    controls, clones = place.controllerDownChain(defObj, name, pad=0, shape='diamond_ctrl', color=color, size=X * size, groups=True, orient=orient, suffix=None, scale=True, setChannel=True, clone=True, fk=False)
    i = 0
    for item in controls:
        cmds.setAttr(item[2] + '.Offset_Vis', 1)
        misc.hijackScale(clones[i][2], item[3])
        cmds.setAttr(item[3] + '.scaleX', k=True, l=False)
        cmds.setAttr(item[3] + '.scaleY', k=True, l=False)
        cmds.setAttr(item[3] + '.scaleZ', k=True, l=False)
        i = i + 1
    cmds.select(geo)
    sculpt = cmds.lattice(name=name, divisions=(2, 2, 2), outsideLattice=2, objectCentered=False, ofd=0.5, ldv=(2, 2, 2), exclusive="Create new partition#")
    sculpt[1] = cmds.rename(sculpt[1], name + '_Lattice')
    sculpt[2] = cmds.rename(sculpt[2], name + '_Base')
    cmds.setAttr(sculpt[2] + '.overrideEnabled', 1)
    cmds.setAttr(sculpt[2] + '.overrideColor', color)
    misc.optEnum(controls[0][3])
    ##misc.hijackVis(sculpt[1], controls[0][2], name='Def', default=0)
    hijackSculpt(sculpt[0], controls[0][3], name='Def')
    # structure
    cmds.parent(controls[0][0], Master[1])
    cmds.parent(clones[0][0], Master[2])
    ##cmds.parent(defObj, Master[3])
    cmds.delete(defObj)
    cmds.parent(sculpt[2], clones[0][1])
    cmds.parent(sculpt[1], clones[0][2])
    misc.zero(sculpt[2])
    misc.zero(sculpt[1])
    cmds.setAttr(clones[0][0] + '.visibility', 0)
    return Master[1]


def mask(root='maskEdge_jnt_root', top='maskEdge_jnt_top', bottom='maskEdge_jnt_bottom', root_L='maskEdge_jnt_root_L', root_R='maskEdge_jnt_root_R', cleanUp=False, size=2):
    '''\n
    ***All variables should be skinned joints\n
    root    = root joint\n
    top     = middle top of mask\n
    bottom  = middle bottom of mask\n
    root_L  = root joint for left side\n
    root_R  = root joint for right side\n
    '''
    import atom_deformer_lib as dfrmr
    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    Master = None
    masterNames = nameMaster(mask=True)
    if cmds.objExists(masterNames[0]) == 0:
        Master = dfrmr.master(mask=True)
    else:
        Master = masterNames
    if cleanUp == True:
        misc.cleanUp(root, SknJnts=True)
    mask_L = childrenOf(root_L)
    mask_L.sort()
    mask_R = childrenOf(root_R)
    mask_R.sort()
    # change to groups instead of controller
    maskRoot = place.Controller('Mask_Root', root, False, 'loc_ctrl', X * size, 31, 8, 1, (0, 0, 1), True, True)
    MaskRootCt = maskRoot.createController()
    dfrmr.cleanUp(MaskRootCt[0], maskAnim=True)

    maskTop = place.Controller('Mask_Top', top, False, 'diamond_ctrl', X * size, 31, 8, 1, (0, 0, 1), True, True)
    MaskTopCt = maskTop.createController()
    dfrmr.cleanUp(MaskTopCt[0], maskAnim=True)
    clone = dfrmr.makeClone(MaskTopCt[2], maskClone=True)
    misc.hijack(clone[1], MaskTopCt[2], visibility=False)
    misc.hijack(clone[0], MaskTopCt[3], visibility=False, scale=False)
    misc.hijack(MaskTopCt[2], MaskRootCt[2], translate=False, rotate=False, scale=False)
    fullConstraint(clone[0], top)
    cmds.parentConstraint(MaskRootCt[4], MaskTopCt[0], mo=True)
    misc.scaleUnlock(MaskTopCt[2])

    maskBottom = place.Controller('Mask_Bottom', bottom, False, 'diamond_ctrl', X * size, 31, 8, 1, (0, 0, 1), True, True)
    MaskBottomCt = maskBottom.createController()
    dfrmr.cleanUp(MaskBottomCt[0], maskAnim=True)
    clone = dfrmr.makeClone(MaskBottomCt[2], maskClone=True)
    misc.hijack(clone[1], MaskBottomCt[2], visibility=False)
    misc.hijack(clone[0], MaskBottomCt[3], visibility=False, scale=False)
    misc.hijack(MaskBottomCt[2], MaskRootCt[2], translate=False, rotate=False, scale=False)
    fullConstraint(clone[0], bottom)
    cmds.parentConstraint(MaskRootCt[4], MaskBottomCt[0], mo=True)
    misc.scaleUnlock(MaskBottomCt[2])

    i = 0
    for item in mask_L:
        mask = place.Controller('Mask_' + str(('%0' + str(3) + 'd') % (i + 1)) + '_L', item, False, 'diamond_ctrl', X * size, 30, 8, 1, (0, 0, 1), True, True)
        MaskCt = mask.createController()
        dfrmr.cleanUp(MaskCt[0], maskAnim=True)
        clone = dfrmr.makeClone(MaskCt[2], maskClone=True)
        misc.hijack(clone[1], MaskCt[2], visibility=False)
        misc.hijack(clone[0], MaskCt[3], visibility=False, scale=False)
        misc.hijack(MaskCt[2], MaskRootCt[2], translate=False, rotate=False, scale=False)
        fullConstraint(clone[0], item)
        cmds.parentConstraint(MaskRootCt[4], MaskCt[0], mo=True)
        misc.scaleUnlock(MaskCt[2])
        i = i + 1

    i = 0
    for item in mask_R:
        mask = place.Controller('Mask_' + str(('%0' + str(3) + 'd') % (i + 1)) + '_R', item, False, 'diamond_ctrl', X * size, 30, 8, 1, (0, 0, 1), True, True)
        MaskCt = mask.createController()
        dfrmr.cleanUp(MaskCt[0], maskAnim=True)
        clone = dfrmr.makeClone(MaskCt[2], maskClone=True)
        misc.hijack(clone[1], MaskCt[2], visibility=False)
        misc.hijack(clone[0], MaskCt[3], visibility=False, scale=False)
        misc.hijack(MaskCt[2], MaskRootCt[2], translate=False, rotate=False, scale=False)
        fullConstraint(clone[0], item)
        cmds.parentConstraint(MaskRootCt[4], MaskCt[0], mo=True)
        misc.scaleUnlock(MaskCt[2])
        i = i + 1
    # return MaskRootCt[0], Master[1]
    return Master[1]


def spline(SPLN_Name='SPLN', SPLN_Size=0.5, SPLN_Dist=3.0, SPLN_Falloff=0, SPLN_Prnt=['start', 'mid', 'end'],
           SPLN_Attr='SPLN_L', SPLN=['startJNT', 'endJNT'],
           SPLN_Vis=['cntrlName', 'attrName'], mirror=False, cleanUp=False):
    '''\n
    Spline Deformer
    '''
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

    X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    import atom_deformer_lib as dfrmr
    from atom import atom_splineStage_lib as stage
    from atom import atom_spline_lib as posFrom

    # master groups
    Master = None
    masterNames = dfrmr.nameMaster(spline=True)
    if cmds.objExists(masterNames[0]) == 0:
        Master = dfrmr.master(spline=True)
    else:
        Master = masterNames

    def mirrorBhv(name, obj1, obj2, attrs=['tx', 'ry', 'rz']):
        # math node
        mltp = cmds.shadingNode('multiplyDivide', au=True, n=(name + '_rev'))
        # set operation: 2 = divide, 1 = multiply
        cmds.setAttr((mltp + '.operation'), 1)
        cmds.setAttr((mltp + '.i2x'), -1)
        cmds.setAttr((mltp + '.i2y'), -1)
        cmds.setAttr((mltp + '.i2z'), -1)
        # connect
        cmds.connectAttr(obj1 + '.' + attrs[0], mltp + '.i1x', f=True), cmds.connectAttr(mltp + '.ox', obj2 + '.' + attrs[0], f=True)
        cmds.connectAttr(obj1 + '.' + attrs[1], mltp + '.i1y', f=True), cmds.connectAttr(mltp + '.oy', obj2 + '.' + attrs[1], f=True)
        cmds.connectAttr(obj1 + '.' + attrs[2], mltp + '.i1z', f=True), cmds.connectAttr(mltp + '.oz', obj2 + '.' + attrs[2], f=True)
        # unlock parent scaleX, scale inverse
        parent = cmds.listRelatives(obj1, p=True)[0]
        cmds.setAttr(parent + '.sx', k=True, l=False)
        cmds.setAttr(parent + '.sx', -1)

    def lockXforms(obj, t=True, r=True):
        translateList = ['.tx', '.ty', '.tz']
        rotateList = ['.rx', '.ry', '.rz']
        if t == True:
            for attr in translateList:
                cmds.setAttr(obj + attr, l=True,)
                cmds.setAttr(obj + attr, k=False)
        if t == True:
            for attr in rotateList:
                cmds.setAttr(obj + attr, l=True,)
                cmds.setAttr(obj + attr, k=False)

    # joint info
    midCT = None
    strtCT = None
    endCT = None
    cmds.select(SPLN[0], hi=True)
    jntList = cmds.ls(sl=True)
    i = 0
    for jnt in jntList:
        mid = posFrom.posFromCenter(len(jntList), i)
        if mid == 0:
            midCT = jnt
            break
        i = i + 1
    strtCT = jntList[0]
    endCT = jntList[len(jntList) - 1]

    sufStart = '_start'
    sufMid = '_mid'
    sufEnd = '_end'

    # spline controllers
    strt = place.Controller(SPLN_Name + sufStart, strtCT, True, 'ballRoll_ctrl', SPLN_Size * 2, 17, 8, 1, (0, 0, 1), True, True)
    strt_Ct = strt.createController()
    lockXforms(strt_Ct[3])
    mid = place.Controller(SPLN_Name + sufMid, midCT, True, 'v_ctrl', SPLN_Size * 1, 17, 8, 1, (0, 0, 1), True, True)
    mid_Ct = mid.createController()
    lockXforms(mid_Ct[3])
    end = place.Controller(SPLN_Name + sufEnd, endCT, True, 'ballRollInv_ctrl', SPLN_Size * 2, 17, 8, 1, (0, 0, 1), True, True)
    end_Ct = end.createController()
    lockXforms(end_Ct[3])

    # constrain controllers to rig
    cmds.parentConstraint(SPLN_Prnt[0], strt_Ct[0], mo=True)
    cmds.parentConstraint(SPLN_Prnt[1], mid_Ct[0], mo=True)
    cmds.parentConstraint(SPLN_Prnt[2], end_Ct[0], mo=True)

    # spline clone
    if cmds.objExists(SPLN[0]):
        SPLN_Name = SPLN_Name + '_Clone'
        # build spline
        SplineOpts(SPLN_Name, SPLN_Size * 0.5, SPLN_Dist * 3.0, SPLN_Falloff)
        cmds.select(SPLN)
        stage.splineStage(4)
        # set options
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.' + SPLN_Name + 'Vis', 0)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.' + SPLN_Name + 'Root', 0)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.' + SPLN_Name + 'Stretch', 1)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.ClstrVis', 0)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.ClstrMidIkBlend', 1)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.VctrVis', 0)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.VctrMidIkBlend', 1)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0)
        cmds.setAttr(SPLN_Name + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5)
        cmds.setAttr(SPLN_Name + '_S_IK_Cntrl.LockOrientOffOn', 1)
        cmds.setAttr(SPLN_Name + '_E_IK_Cntrl.LockOrientOffOn', 1)
        # attrs
        OptAttr(strt_Ct[3], SPLN_Name + 'Spline')
        misc.hijackCustomAttrs(SPLN_Name + '_IK_CtrlGrp', strt_Ct[3])
        cmds.setAttr(strt_Ct[3] + '.' + SPLN_Name + 'Vis', l=True)
        cmds.setAttr(strt_Ct[3] + '.ClstrVis', l=True)
        cmds.setAttr(strt_Ct[3] + '.VctrVis', l=True)

    # connect/mirror controllers to clones
    midInt = str(int((float(len(jntList)) / 2 + 0.5)))
    # start
    misc.hijack(SPLN_Name + '_S_IK_Cntrl', strt_Ct[2], translate=True, rotate=True, scale=False, visibility=False)
    # mid
    misc.hijack(SPLN_Name + '_Clstr_M' + midInt + '_Ctrl', mid_Ct[2], translate=True, rotate=True, scale=False, visibility=False)
    misc.hijack(mid_Ct[1], SPLN_Name + '_Clstr_M' + midInt + '_PrntGrp', translate=True, rotate=True, scale=False, visibility=False)
    # end
    misc.hijack(SPLN_Name + '_E_IK_Cntrl', end_Ct[2], translate=True, rotate=True, scale=False, visibility=False)
    # mirror connections
    if mirror == True:
        mirrorBhv(SPLN_Name + sufStart, strt_Ct[2], SPLN_Name + '_S_IK_Cntrl')
        mirrorBhv(SPLN_Name + sufStart, mid_Ct[2], SPLN_Name + '_Clstr_M' + midInt + '_Ctrl')
        mirrorBhv(SPLN_Name + sufStart, end_Ct[2], SPLN_Name + '_E_IK_Cntrl')

    # cleanup
    if cleanUp == True:
        # joints
        rootJnt = find.root(SPLN[0])
        misc.cleanUp(rootJnt, SknJnts=True)
        # anim controls
        dfrmr.cleanUp(strt_Ct[0], splineAnim=True)
        dfrmr.cleanUp(mid_Ct[0], splineAnim=True)
        dfrmr.cleanUp(end_Ct[0], splineAnim=True)
        # clone controls
        dfrmr.cleanUp(SPLN_Name + '_SplineAllGrp', splineClone=True)

    # return controls[0][0], Master[1]
    # return Master[1]


def retain(geo, deformer, follow, name='sculptTool', size=5, orient=False):
    '''\n
    geo       = *has to be list, geo to be deformed\n
    deformer  = object to be used as deformation tool of 'geo'. If 'False', a generic sphere will be created at origin\n
    size      = size of cntrlCtlers\n
    '''
    color = 12
    import atom_deformer_lib as dfrmr

    def hijackSculpt(node, obj, name=name, envelope=True, dropoffDistance=True):
        '''\n
        node = sculpt node\n
        obj  = object hijacking nodes attrs\n
        name = prefix tag for attrs\n
        '''
        attrs = []
        if envelope == True:
            attrs.append(misc.hijackAttrs(node, obj, 'envelope', name + '_Envelope'))
        if dropoffDistance == True:
            attrs.append(misc.hijackAttrs(node, obj, 'dropoffDistance', name + '_Dropoff'))
        print attrs
        return attrs

    # cntrlCts
    cntrl = place.Controller(name, deformer, orient, 'ballRoll_ctrl', size, color, 8, 1, (0, 0, 1), True, True)
    cntrlCt = cntrl.createController()
    vis = None
    if type(geo) == list:
        i = 0
        for item in geo:
            sculpt = cmds.sculpt(geo, sculptTool=deformer, mode='stretch', insideMode='even', maxDisplacement=0, dropoffType='linear', dropoffDistance=1, groupWithLocator=0, objectCentered=1)
            # sculptNode
            sculpt[0] = cmds.rename(sculpt[0], item + name + '_Utl')
            # originLocator
            sculpt[2] = cmds.rename(sculpt[2], item + name + '_UtlOrigin')
            print sculpt[1]
            if i == 0:
                print 'here'
                misc.optEnum(cntrlCt[2])
                vis = misc.hijackVis(sculpt[1], cntrlCt[2], name='Def', default=0)
                attrs = hijackSculpt(sculpt[0], cntrlCt[2], name='Def')
            else:
                cmds.connectAttr(attrs[0], sculpt[0] + '.envelope')
                cmds.connectAttr(attrs[1], sculpt[0] + '.dropoffDistance')
            cmds.setAttr(sculpt[2] + '.overrideEnabled', 1)
            cmds.setAttr(sculpt[2] + '.overrideColor', color)
            #hijackSculpt(sculpt[0], cntrlCt[2], name=item + 'Def')
            cmds.parent(sculpt[2], deformer)
            misc.zero(sculpt[2])
            i = i + 1
    else:
        pass
    # structure
    cmds.parentConstraint(follow, cntrlCt[0], mo=True)
    cmds.parent(deformer, cntrlCt[4])
    #cmds.parent(sculpt[2], deformer)
    # misc.zero(sculpt[2])
    misc.cleanUp(cntrlCt[0], Ctrl=True)


def floatingControl(name='', parent='', joint='pin_jnt', size=4, shape='facetZup_ctrl'):
    # slave ct
    cntrl = place.Controller(name + '_slave', joint, True, shape, size, 17, 8, 1, (0, 0, 1), True, True)
    fl1 = cntrl.createController()
    cmds.parentConstraint(fl1[len(fl1) - 1], joint, mo=True)
    cmds.setAttr(fl1[0] + '.visibility', 0)
    # master ct
    cntrl = place.Controller(name, joint, True, shape, size, 17, 8, 1, (0, 0, 1), True, True)
    fl2 = cntrl.createController()
    cmds.parentConstraint(parent, fl2[0], mo=True)
    misc.hijack(fl1[1], fl2[1], translate=True, rotate=True, scale=False, visibility=False)
    misc.hijack(fl1[2], fl2[2], translate=True, rotate=True, scale=False, visibility=False)
    return fl1, fl2
