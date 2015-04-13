import maya.cmds as cmds
import maya.mel as mel

# OFF
off = ['head_low_cut_geo', 'body_low_cut_geo', 'body_lo', 'roots_lo', 'body_cut_geo', 'head_cut_geo', 'head_chop_geo',
       'sym_geo',
       'curve19',
       'curve20',
       'curve21',
       'curve22',
       'curve23',
       'curve24',
       'curve25',
       'curve26',
       'curve27',
       'curve28',
       'curve8',
       'curve7',
       'curve6',
       'curve5',
       'curve4',
       'curve3',
       'curve2',
       'curve1',
       'curve29',
       'curve30',
       'curve31',
       'curve32',
       'curve33',
       'curve34',
       'curve35',
       'curve36',
       'curve37',
       'curve38',
       'curve39',
       'polyToCurve1',
       'polyToCurve2',
       'polyToCurve3',
       'polyToCurve4',
       'polyToCurve5',
       'polyToCurve6',
       'polyToCurve7',
       'polyToCurve8',
       'polyToCurve9'
       ]

# LOW
loGeo = ['head_cut_geo']
# nurbs
loVis = 'ct_main_hdl.geo_influencesVis'

# MID
midGeo = ['deform_body_geo', 'deform_roots_geo']

# HIGH
hiGeo = ['body', 'roots', 'vines_02', 'vines_01', 'headVines', 'twigs_a_geo', 'twigs_b_geo', 'twigs1_lower', 'twigs2_lower', 'twigs1_upper', 'twigs2_upper', 'cutheadVines_upper', 'cutvines_02_upper', 'cutvines_02_lower', 'cutvines_01', 'cutheadVines_lower',
         'body1', 'roots1', 'vines_01', 'vines_02', 'headVines', 'twigs1', 'twigs2', 'head', 'head_chop_geo']


# ATTR
attr = '.visibility'


def ns():
    ns = ''
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        ns = sel[0].split(':')[0]
        ns = ns + ':'
        return ns
    else:
        return ns


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def state():
    if cmds.objExists(ns() + loGeo[0]):
        shapes = cmds.listRelatives(ns() + loGeo[0], type='shape')
        state = cmds.getAttr(shapes[0] + attr)
        return state
    else:
        return False


def toggle():
    if state():
        all(v=0)
        # change to mid
        for geo in midGeo:
            if cmds.objExists(ns() + geo):
                shapes = cmds.listRelatives(ns() + geo, type='shape')
                for shape in shapes:
                    cmds.setAttr(shape + attr, 1)
        cmds.setAttr(ns() + loVis, 0)
        message('mid res', maya=True)
    else:
        all(v=0)
        # change to lo
        for geo in loGeo:
            if cmds.objExists(ns() + geo):
                shapes = cmds.listRelatives(ns() + geo, type='shape')
                for shape in shapes:
                    cmds.setAttr(shape + attr, 1)
        cmds.setAttr(ns() + loVis, 1)
        message('low res', maya=True)


def all(v=0):
    tip = 'Does not change vis attrs on master control'
    allStates = [loGeo, midGeo, hiGeo, off]
    for state in allStates:
        for geo in state:
            if cmds.objExists(ns() + geo):
                shapes = cmds.listRelatives(ns() + geo, type='shape')
                for shape in shapes:
                    cmds.setAttr(shape + attr, v)
            else:
                print 'here\n'
        cmds.setAttr(ns() + loVis, v)
        if v == 0:
            message('all OFF --  ' + tip, maya=True)
        else:
            message('all ON --  ' + tip, maya=True)


def hi():
    all(v=0)
    for geo in hiGeo:
        if cmds.objExists(ns() + geo):
            shapes = cmds.listRelatives(ns() + geo, type='shape')
            for shape in shapes:
                cmds.setAttr(shape + attr, 1)
    message('high res', maya=True)
