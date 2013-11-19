import maya.cmds as cmds
import anim_lib as anim
reload(anim)
#match

def toik():
    #ik
    ikUp = 'lf_arm_ik_1_hdl'
    ikDn = 'lf_arm_ik_2_hdl'
    ikWr = 'lf_arm_ik_wrist_hdl'
    ikPv = 'lf_arm_ik_elbow_hdl'
    #fk
    fkUp = 'lf_arm_fk_1_hdl'
    fkDn = 'lf_arm_fk_2_hdl'
    fkWr = 'lf_arm_fk_3_hdl'
    sel = cmds.ls(sl=True)[0]
    ns = sel.split(':')[0] + ':'
    if 'lf_' in sel:
        #fkUp to ik joint
        cmds.select(ns + fkUp, ns + ikUp)
        anim.matchObj()
        #fkDn to ik joint
        cmds.select(ns + fkDn, ns + ikDn)
        anim.matchObj()
    else:
        #fkUp to ik joint
        cmds.select(ns + fkUp.replace('lf_', 'rt_'), ns + ikUp.replace('lf_', 'rt_'))
        anim.matchObj()
        #fkDn to ik joint
        cmds.select(ns + fkDn.replace('lf_', 'rt_'), ns + ikDn.replace('lf_', 'rt_'))
        anim.matchObj()

def tofk():
    #ik
    ikUp = 'lf_arm_ik_1_hdl'
    ikDn = 'lf_arm_ik_2_hdl'
    ikWr = 'lf_arm_ik_wrist_hdl'
    ikPv = 'lf_arm_ik_elbow_hdl'
    #fk
    fkUp = 'lf_arm_fk_1_hdl'
    fkDn = 'lf_arm_fk_2_hdl'
    fkWr = 'lf_arm_fk_3_hdl'
    sel = cmds.ls(sl=True)[0]
    ns = sel.split(':')[0] + ':'
    if 'lf_' in sel:
        #ik wrist to fk wrist
        cmds.select(ns + ikWr, ns + fkWr)
        anim.matchObj()
        #pv to fk elbow
        cmds.select(ns + ikPv, ns + fkDn)
        anim.matchObj()
    else:
        #ik wrist to fk wrist
        cmds.select(ns + ikWr.replace('lf_', 'rt_'), ns + fkWr.replace('lf_', 'rt_'))
        anim.matchObj()
        #pv to fk elbow
        cmds.select(ns + ikPv.replace('lf_', 'rt_'), ns + fkDn.replace('lf_', 'rt_'))
        anim.matchObj()