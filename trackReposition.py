import maya.cmds as cmds


def trackReposition():
    # TODO: could alter to make camera space tool
    trans = cmds.ls(tr=True)
    locs = []
    cam = ''
    trk = 'track'
    for item in trans:
        if 'locator' in item:
            locs.append(item)
        elif 'Camera1' in item:
            cam = item
    cmds.select(locs)
    cmds.group(name='locators')
    cmds.group(name=trk)
    cmds.parent(cam, trk)
    m = cmds.xform(cam, q=True, m=True, ws=True)
    loc = cmds.spaceLocator(name='camPosition')
    cmds.xform(loc, m=m, ws=True)
    cmds.parentConstraint(loc, trk, mo=True)
    cmds.xform(loc, translation=(0, 0, 0), rotation=(0, 0, 0), ws=True)
