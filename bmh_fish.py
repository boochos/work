import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
#

import webrImport as web
place = web.mod('atom_place_lib')
misc = web.mod('atom_miscellaneous_lib')


def add_scaling():
    # place group for master
    rt = 'Root_Grp'
    gp = place.null2('Master_Grp', rt, orient=True)[0]
    # lock up transforms
    misc.setChannels(gp, translate=[True, False], rotate=[
                     True, False], scale=[True, False])
    # parent group under 'Root_Grp'
    cmds.parent(gp, rt)

    # Add Scale attr to master
    mstr = 'Master_Con'
    misc.addAttribute(mstr, 'Scale', 0, 1000, True, 'float')
    cmds.setAttr(mstr + '.Scale', 1)
    # Parent Master under new group above
    cmds.parent(mstr, gp)

    # Unlock groups
    misc.scaleUnlock('Con_Grp', sx=True, sy=True, sz=True)
    misc.scaleUnlock('Jnt_Grp', sx=True, sy=True, sz=True)
    misc.scaleUnlock('Rig_Grp', sx=True, sy=True, sz=True)
    misc.scaleUnlock(mstr, sx=True, sy=True, sz=True)

    # hijack scale attrs from groups above to new attr on Master
    misc.hijackScale('Con_Grp', mstr)
    misc.hijackScale('Jnt_Grp', mstr)
    misc.hijackScale('Rig_Grp', mstr)
    #
    misc.setChannels('Con_Grp', translate=[True, False], rotate=[
                     True, False], scale=[True, False], visibility=[True, True, False])
    misc.setChannels('Jnt_Grp', translate=[True, False], rotate=[
                     True, False], scale=[True, False], visibility=[False, True, False])
    misc.setChannels('Rig_Grp', translate=[True, False], rotate=[
                     True, False], scale=[True, False], visibility=[False, True, False])
    #
    cmds.setAttr('Con_Grp.visibility', cb=False)
    cmds.setAttr('Jnt_Grp.visibility', cb=False)
    cmds.setAttr('Rig_Grp.visibility', cb=False)
    #
    cmds.connectAttr(mstr + '.Scale', mstr + '.scaleX')
    cmds.connectAttr(mstr + '.Scale', mstr + '.scaleY')
    cmds.connectAttr(mstr + '.Scale', mstr + '.scaleZ')
    cmds.setAttr(mstr + '.scaleX', lock=True)
    cmds.setAttr(mstr + '.scaleX', keyable=False)
    cmds.setAttr(mstr + '.scaleY', lock=True)
    cmds.setAttr(mstr + '.scaleY', keyable=False)
    cmds.setAttr(mstr + '.scaleZ', lock=True)
    cmds.setAttr(mstr + '.scaleZ', keyable=False)

    '''
    cmds.connectAttr(mstr + '.scaleY', mstr + '.scaleX')
    # cmds.setAttr(mstr + '.scaleX', lock=True)
    # cmds.setAttr(mstr + '.scaleX', keyable=False)
    cmds.connectAttr(mstr + '.scaleY', mstr + '.scaleZ')'''
