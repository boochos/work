from pymel.core import *
import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')
splnFk = web.mod('atom_splineFk_lib')
anm = web.mod('anim_lib')


def message(what='', maya=True, warning=False):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace('\\', '/')
    if warning:
        cmds.warning(what)
    else:
        if maya:
            mel.eval('print \"' + what + '\";')
        else:
            print what


def rename():
    # rename duplicate joints
    sel = cmds.ls(sl=1)[0]
    name = 'splineTentacle_'
    num = '5'
    side = 'R'
    suf = 'jnt'
    place.renameHierarchy(sel, name + side + num, pad=2, suffix=suf)


def tnt_constrain():
    jnt_pairs = [
        ['splineTentacle_L1_01_jnt', 'BN_reconorb_tentacle_L_01_01'],
        ['splineTentacle_L2_01_jnt', 'BN_reconorb_tentacle_L_02_02'],
        ['splineTentacle_L3_01_jnt', 'BN_reconorb_tentacle_L_03_01'],
        ['splineTentacle_L4_01_jnt', 'BN_reconorb_tentacle_L_04_01'],
        ['splineTentacle_L5_01_jnt', 'BN_reconorb_tentacle_L_05_01'],
        ['splineTentacle_R1_01_jnt', 'BN_reconorb_tentacle_R_01_01'],
        ['splineTentacle_R2_01_jnt', 'BN_reconorb_tentacle_R_02_02'],
        ['splineTentacle_R3_01_jnt', 'BN_reconorb_tentacle_R_03_01'],
        ['splineTentacle_R4_01_jnt', 'BN_reconorb_tentacle_R_04_01'],
        ['splineTentacle_R5_01_jnt', 'BN_reconorb_tentacle_R_05_01'],
    ]
    for pair in jnt_pairs:
        cmds.select(pair)
        constraint()


def constraint():
    # constrain skinne djoints to spline joints
    # select 2 roots, spline first
    roots = cmds.ls(sl=True)
    if roots:
        if len(roots) == 2:
            # driver joints
            cmds.select(roots[0], hi=True)
            drv_jnts = cmds.ls(sl=True)
            # slave joints
            cmds.select(roots[1], hi=True)
            slv_jnts = cmds.ls(sl=True)
            # constrain
            if drv_jnts:
                for i in range(len(drv_jnts)):
                    try:
                        cmds.parentConstraint(drv_jnts[i], slv_jnts[i], mo=True)
                    except:
                        print i
                        print drv_jnts[i]
            else:
                print 'No driver joints.'
        else:
            print 'Select 2 objects'


def tent():
    # Tentacle
    # tentacle_world_Parent
    # CNTRL_God
    # added branch, for testing
    all = [
        ['tentacle_L1', 'splineTentacle_L1_00_jnt', 'splineTentacle_L1_18_jnt', 'L', 'blue'],
        ['tentacle_L2', 'splineTentacle_L2_00_jnt', 'splineTentacle_L2_17_jnt', 'L', 'blue'],
        ['tentacle_L3', 'splineTentacle_L3_00_jnt', 'splineTentacle_L3_17_jnt', 'L', 'blue'],
        ['tentacle_L4', 'splineTentacle_L4_00_jnt', 'splineTentacle_L4_17_jnt', 'L', 'blue'],
        ['tentacle_L5', 'splineTentacle_L5_00_jnt', 'splineTentacle_L5_17_jnt', 'L', 'blue'],
        ['tentacle_R1', 'splineTentacle_R1_00_jnt', 'splineTentacle_R1_18_jnt', 'R', 'red'],
        ['tentacle_R2', 'splineTentacle_R2_00_jnt', 'splineTentacle_R2_17_jnt', 'R', 'red'],
        ['tentacle_R3', 'splineTentacle_R3_00_jnt', 'splineTentacle_R3_17_jnt', 'R', 'red'],
        ['tentacle_R4', 'splineTentacle_R4_00_jnt', 'splineTentacle_R4_17_jnt', 'R', 'red'],
        ['tentacle_R5', 'splineTentacle_R5_00_jnt', 'splineTentacle_R5_17_jnt', 'R', 'red']
    ]
    for tn in all:
        tailRig = splnFk.SplineFK(tn[0], tn[1], tn[2], tn[3], controllerSize=0.5, rootParent='CNTRL_God', parent1='tentacle_Gp',
                                  parentDefault=[1, 0], segIteration=4, stretch=0, ik='splineIK', colorScheme=tn[4])


def tent_secondary(delay=0.75):
    sel = cmds.ls(sl=True)
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split(':')[0]
            sels = [
                ':tentacle_L1_19_L',
                ':tentacle_L2_17_L',
                ':tentacle_L3_17_L',
                ':tentacle_L4_17_L',
                ':tentacle_L5_17_L',
                ':tentacle_R1_19_R',
                ':tentacle_R2_17_R',
                ':tentacle_R3_17_R',
                ':tentacle_R4_17_R',
                ':tentacle_R5_17_R'
            ]
            lsts = ['tentacle_L_1', 'tentacle_L_2', 'tentacle_L_3', 'tentacle_L_4', 'tentacle_L_5',
                    'tentacle_R_1', 'tentacle_R_2', 'tentacle_R_3', 'tentacle_R_4', 'tentacle_R_5', ]
            for i in range(len(sels)):
                cmds.select(ns + sels[i])
                anm.secondaryChain(offset=delay, lst=lsts[i])
        else:
            message('select a control with a namespace', warning=True)
    else:
        message('select a control with a namespace', warning=True)


def scaleConstrain():
    sel = [
        'splineFK_Ct__tentacle_L1',
        'splineFK_Ct__tentacle_L2',
        'splineFK_Ct__tentacle_L3',
        'splineFK_Ct__tentacle_L4',
        'splineFK_Ct__tentacle_L5',
        'splineFK_Ct__tentacle_R1',
        'splineFK_Ct__tentacle_R2',
        'splineFK_Ct__tentacle_R3',
        'splineFK_Ct__tentacle_R4',
        'splineFK_Ct__tentacle_R5'
    ]
    for s in sel:
        cmds.scaleConstraint('CNTRL_God', s, mo=True)


'''
#

# joints
import webrImport as web
tnt = web.mod('atom_tentacle_lib')
tnt.tnt_constrain()

# rig
import webrImport as web
tnt = web.mod('atom_tentacle_lib')
tnt.tent()

# secondary
import webrImport as web
# web
anm = web.mod('anim_lib')
anm.secondaryChain(offset=0.75, lst='tentacle_L_1')

'''
