import maya.cmds  as cmds


fingers = ['l_handFingerA0Fk_CTRL',
'l_handFingerB0Fk_CTRL',
'l_handFingerC0Fk_CTRL',
'l_handFingerD0Fk_CTRL',
'l_handFingerD1Fk_CTRL',
'l_handFingerD2Fk_CTRL',
'l_handFingerC1Fk_CTRL',
'l_handFingerB1Fk_CTRL',
'l_handFingerA1Fk_CTRL',
'l_handFingerC2Fk_CTRL',
'l_handFingerB2Fk_CTRL',
'l_handFingerA2Fk_CTRL',
'l_handThumb_CTRL',
'l_handThumb0_CTRL',
'l_handThumb1_CTRL',
'l_handThumb2_CTRL',
'l_thumbBase_CTRL',
'l_handCupBck_CTRL',
'l_handCupFrt_CTRL',
'l_handA_CTRL',
'l_handB_CTRL',
'l_handC_CTRL',
'l_handD_CTRL']

'l_handA_CTRL', 'l_handB_CTRL', 'l_handC_CTRL', 'l_handD_CTRL'

def selectFngrs(R=False):
    sel = cmds.ls(sl=True)
    ref = sel[0].split(':')[0]
    cmds.select(clear=True)
    for item in fingers:
        if R == True:
            item = item.replace('l_', 'r_')
        print item
        ctrl = ref + ':' + item
        if cmds.objExists(ctrl) == True:
        	cmds.select(ctrl, add=True)
