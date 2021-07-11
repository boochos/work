import imp

import clipPickle_lib as cp

imp.reload( cp )

# sort out namespaces

# attr flip
'''
[
mirrorCurves = [
[obj, attr]
]
'''

# pose flip
sel = [
['skelLady01:L_leg_mainIk_ctrl',
'skelLady01:R_leg_mainIk_ctrl'],
['skelLady01:L_leg_mainIkPole_ctrl',
'skelLady01:R_leg_mainIkPole_ctrl'],
['skelLady01:L_arm_mainIk_ctrl',
'skelLady01:R_arm_mainIk_ctrl'],
['skelLady01:L_arm_mainIkPole_ctrl',
'skelLady01:R_arm_mainIkPole_ctrl'],
['skelLady01:L_arm_shoulderIk_ctrl',
'skelLady01:R_arm_shoulderIk_ctrl']
]


def swapAnim( pair = [] ):
    # Get
    cmds.select( pair[0] )
    pr_A = cp.Clip( name = 'tmp' )
    pr_A.get()
    # Swap
    cmds.select( pair[1] )
    pr_B = cp.Clip( name = 'tmp' )
    pr_B.get()
    #
    pr_A = cp.updateObjName( pr_A, names = [pair[1]] )
    pr_A.putLayers()
    pr_B = cp.updateObjName( pr_B, names = [pair[0]] )
    pr_B.putLayers()


def flipAttr( obj = '', attr = '' ):
    pass


def swap( sel = [] ):
    for pair in sel:
        swapAnim( pair = pair )


swap( sel = sel )
