import maya.cmds as cmds
import webrImport as web
reload(web)
# pt = web.mod("atom_path_lib")
anm = web.mod("anim_lib")
cn = web.mod("constraint_lib")


def nsPaths():
    nsList = cmds.namespaceInfo(lon=True)
    nsPathsList = []
    for ns in nsList:
        if 'Path_' in ns:
            nsPathsList.append(ns)
    return nsPathsList


def nsHollow(roots, reverse=True):
    nsList = cmds.namespaceInfo(lon=True)
    newRoots = []
    newRoot = []
    ns = None
    for ns in nsList:
        if 'Scarecrow_' in ns:
            for root in roots:
                for ct in rev(root, reverse=reverse):
                    newRoot.append(ns + ':' + ct.split(':')[1])
                newRoots.append(newRoot)
                newRoot = []
            return newRoots


def rev(root=[], reverse=True):
    if reverse:
        return reversed(root)
    else:
        return root


def segmentsOff(ns=''):
    seg = segments()
    for item in seg:
        cmds.setAttr(ns + item + '.visibility', False)


def rootsOnPath(path='X:/_image/_projects/SI/HOL/_Assets/ScareCrow/scenes/Anim_Asset/Path_v01.ma', reverse=False):
    allLocs = []
    roots = rootList()
    if not nsPaths():
        cn.uiEnable(controls='modelPanel')
        roots = nsHollow(roots)
        for root in roots:
            nsA = nsPaths()
            cmds.file(path, r=True, type="mayaAscii", gl=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace="Path_v01")
            nsB = nsPaths()
            ns = list(set(nsB) - set(nsA))[0]
            # segments off
            segmentsOff(ns=ns)
            cmds.select(root)
            cmds.select(ns + ':path', add=True)
            # pose the path
            pathPose(root=root, ns=ns)
            # attach
            allLocs.append(attach(up=ns + ':up', reverse=reverse))
            # break
        cn.uiEnable(controls='modelPanel')
        for locs in allLocs:
            cmds.select(locs, add=True)
    else:
        cmds.warning('--  remove all path rigs before starting  --')


def pathPose(root=[], ns=''):
    # time
    min = cmds.playbackOptions(q=True, minTime=True)
    max = cmds.playbackOptions(q=True, maxTime=True)
    length = int(max - min)
    current = cmds.currentTime(q=True)
    cmds.currentTime(min)
    # move master path control to first root control
    t = cmds.xform(root[0], q=True, ws=True, t=True)
    cmds.xform(ns + ':master', ws=True, t=t)
    # vars
    point = 'Point'
    i = 0
    # loop start pose
    for control in root:
        t = cmds.xform(control, q=True, ws=True, t=True)
        n = pad(i)
        cmds.xform(ns + ':' + point + n, ws=True, t=t)
        i = i + 1
    # loop animated pose
    pathAnimPose(root=root[len(root) - 1], i=i, length=length, ns=ns, point=point)
    cmds.currentTime(current)


def pathAnimPose(root='', i=0, length=0, ns='', point=''):
    # point number
    # i = i + 1
    # number of point controls
    pathControls = 47
    # number of points left
    numOfCt = pathControls - i
    # advance every nframe
    nframe = 1
    # if frame length is larger than points left, skip frames
    if length > numOfCt:
        nframe = int(length / numOfCt)
    print nframe, '__________'
    while i <= 47:
        current = cmds.currentTime(q=True)
        cmds.currentTime(current + nframe)
        t = cmds.xform(root, q=True, ws=True, t=True)
        n = pad(i)
        cmds.xform(ns + ':' + point + n, ws=True, t=t)
        i = i + 1


def pad(i=0):
    if len(str(i)) == 1:
        return str(i).zfill(2)
    else:
        return str(i)


def attach(up='', reverse=False):
    # select control and path namespace
    sel = cmds.ls(sl=True)
    path = sel[len(sel) - 1]
    path = path.split(':')[0] + ':path'
    # remove path from list
    sel.remove(sel[len(sel) - 1])
    i = 0
    mlt = 1.0 / len(sel)
    s = 0.01
    e = 0.3
    locs = []
    for ct in sel:
        cmds.select(ct)
        loc = cn.locatorOnSelection(constrain=False, X=8)
        locs.append(loc[0])
        min = cmds.playbackOptions(q=True, minTime=True)
        max = cmds.playbackOptions(q=True, maxTime=True)
        cmds.parentConstraint(loc, ct, mo=True)
        # add world up object to path
        if not reverse:
            m = cmds.pathAnimation(loc, c=path, startTimeU=min, endTimeU=max, startU=s, endU=e, follow=True, wut='object', wuo=up)
        else:
            m = cmds.pathAnimation(loc, c=path, startTimeU=min, endTimeU=max, startU=e, endU=s, follow=True, wut='object', wuo=up)
        # parametric off
        cmds.setAttr(m + '.fractionMode', True)
        # fix value for parametric off option
        crv = cmds.findKeyframe(m, c=True)[0]
        frm = cmds.keyframe(crv, q=True)
        cmds.keyframe(crv, vc=s, time=(frm[0], frm[0]))
        cmds.keyframe(crv, vc=e, time=(frm[1], frm[1]))
        #
        i = i + 1
        s = s + mlt
        e = e + mlt
    cmds.select(clear=True)
    grp = cmds.group(name='__PATH_GRP__#', em=True)
    cmds.parent(locs, grp)
    cmds.select(locs)
    return locs


def rootList():
    # root list
    roots = [[
        'Scarecrow_BodyRig_v35:ct_root_a_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_13_hdl',
        'Scarecrow_BodyRig_v35:ct_root_a_14_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_b_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_13_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_14_hdl',
        'Scarecrow_BodyRig_v35:ct_root_b_15_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_c_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_13_hdl',
        'Scarecrow_BodyRig_v35:ct_root_c_14_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_d_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_13_hdl',
        'Scarecrow_BodyRig_v35:ct_root_d_14_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_e_3_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_e_12_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_f_2_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_3_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_f_12_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_g_2_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_3_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_g_12_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_h_2_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_3_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_h_12_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_i_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_i_13_hdl'
    ],
        [
        'Scarecrow_BodyRig_v35:ct_root_j_3_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_4_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_5_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_6_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_7_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_8_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_9_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_10_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_11_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_12_hdl',
        'Scarecrow_BodyRig_v35:ct_root_j_13_hdl'
    ]]
    return roots


def segments():
    return [
        ':Segment00',
        ':Segment01',
        ':Segment02',
        ':Segment03',
        ':Segment04',
        ':Segment05',
        ':Segment06',
        ':Segment07',
        ':Segment08',
        ':Segment09',
        ':Segment10',
        ':Segment11'
    ]
