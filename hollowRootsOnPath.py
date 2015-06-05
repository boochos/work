import maya.cmds as cmds
import webrImport as web
reload(web)
pt = web.mod("atom_path_lib")
anm = web.mod("anim_lib")


def nsPaths():
    nsList = cmds.namespaceInfo(lon=True)
    nsPathsList = []
    for ns in nsList:
        if 'Path_' in ns:
            nsPathsList.append(ns)
    return nsPathsList


def nsHollow(roots):
    nsList = cmds.namespaceInfo(lon=True)
    newRoots = []
    newRoot = []
    ns = None
    for ns in nsList:
        if 'Scarecrow_' in ns:
            for root in roots:
                for ct in root:
                    newRoot.append(ns + ':' + ct.split(':')[1])
                newRoots.append(newRoot)
                newRoot = []
            return newRoots


def rootsOnPath(path='X:/_image/_projects/SI/HOL/_Assets/ScareCrow/scenes/Anim_Asset/Path_v01.ma', reverse=False):
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
    if not nsPaths():
        roots = nsHollow(roots)
        for root in roots:
            nsA = nsPaths()
            f = cmds.file(path, r=True, type="mayaAscii", gl=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace="Path_v01")
            nsB = nsPaths()
            ns = list(set(nsB) - set(nsA))[0]
            # move master path control to first root control
            cmds.select(ns + ':master', root[0])
            anm.matchObj()
            cmds.select(root)
            cmds.select(ns + ':path', add=True)
            pt.attach(up=ns + ':up', reverse=reverse)
    else:
        cmds.warning('--  remove all path rigs before starting  --')
