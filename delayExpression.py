import maya.cmds as cmds
import maya.mel as mel


def deleteExpression(con='', attr=''):
    '''
    #
    '''
    # find exp
    cnn = cmds.listConnections(con + '.' + attr, s=True, d=False)
    if cnn:
        if cmds.nodeType(cnn[0]) == 'unitConversion':
            cnn_uc = cmds.listConnections(cnn, s=True, d=False, type='expression')
            if cnn_uc:
                if cmds.nodeType(cnn_uc[0]) == 'expression':
                    exp = cnn_uc[0]
        elif cmds.nodeType(cnn[0]) == 'expression':
            exp = cnn[0]
        # delete exp
        if exp:
            st1 = cmds.expression(exp, q=True, s=True)
            st2 = 'frame'
            if st2 in st1:
                cmds.delete(exp)
                print 'deleted___  ', con, '  ___  ', exp
            else:
                print '    nope     '
        else:
            print 'no expression  ', attr


def delayAnimation(f=5, removeOnly=False):
    '''
    f = delay by frames
    '''
    controls = [
        'hexa_1:HexapedeRig_r_legfront_KneeIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_LowerLegIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_BallIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_ToeIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_HeelIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_FootIk_Ctrl',
        'hexa_1:HexapedeRig_r_legfront_Switch_Ctrl'
    ]
    r = True
    for con in controls:
        # setup ccontrol names
        con1 = con
        con2 = con.replace('legfront', 'legmid')
        con3 = con1.replace('_r_', '_l_')
        con4 = con2.replace('_r_', '_l_')
        # list attrs
        dos = cmds.listAttr(con1, k=True, s=True)
        donts = cmds.listAttr(con1, k=True, s=True, l=True)
        # expression
        for attr in dos:
            if attr not in donts:
                offset = 0
                # clean up old expression
                deleteExpression(con=con2, attr=attr)
                deleteExpression(con=con4, attr=attr)
                if not removeOnly:
                    if 'HexapedeRig_r_legfront_FootIk_Ctrl' in con:
                        if attr == 'translateX':
                            offset = 0.4
                    # add new expression
                    s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con2, attr, str(f), con1, attr, offset * -1,)
                    print s
                    cmds.expression(s=s)
                    s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con4, attr, str(f), con3, attr, offset,)
                    print s
                    cmds.expression(s=s)
                    offset = 0
            else:
                pass
                # print attr, '    nooooo_____'


def delayAnimation_tapirus(f=5, removeOnly=False):
    '''
    f = delay by frames
    '''
    controls = [
        'tap:r_front_leg_KneeIk_Ctrl',
        'tap:r_front_leg_LowerLegIk_Ctrl',
        'tap:r_front_leg_BallIk_Ctrl',
        'tap:r_front_leg_ToeIk_Ctrl',
        'tap:r_front_leg_HeelIk_Ctrl',
        'tap:r_front_leg_FootIk_Ctrl',
        'tap:r_front_leg_Switch_Ctrl',
        'tap:r_front_leg_ToePivotIk_Ctrl'
    ]
    r = True
    for con in controls:
        if cmds.objExists(con):
            # setup control names
            con1 = con
            con2 = con.replace('front_leg', 'mid_leg')
            con3 = con1.replace('r_', 'l_')
            con4 = con2.replace('r_', 'l_')
            # list attrs
            dos = cmds.listAttr(con1, k=True, s=True)
            donts = cmds.listAttr(con1, k=True, s=True, l=True)
            # expression
            for attr in dos:
                if attr not in donts and 'blendParent1' not in attr:
                    offset = 0
                    # clean up old expression
                    deleteExpression(con=con2, attr=attr)
                    deleteExpression(con=con4, attr=attr)
                    if not removeOnly:
                        if 'r_front_leg_FootIk_Ctrl' in con:
                            if attr == 'translateX':
                                offset = 0.0
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con2, attr, str(f), con1, attr, offset * -1,)
                        print s
                        cmds.expression(s=s)
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con4, attr, str(f), con3, attr, offset,)
                        print s
                        cmds.expression(s=s)
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo_____'


def delayAnimation_sturm(f=3, removeOnly=False):
    '''
    f = delay by frames
    '''
    controls = [
        'strmb:sturmbeast_r_front_leg_KneeIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_LowerLegIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_BallIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_ToeIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_HeelIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_FootIk_Ctrl',
        'strmb:sturmbeast_r_front_leg_Switch_Ctrl'
    ]
    r = True
    for con in controls:
        if cmds.objExists(con):
            # setup control names
            con1 = con
            con2 = con.replace('front_leg', 'mid_leg')
            con3 = con1.replace('r_', 'l_')
            con4 = con2.replace('r_', 'l_')
            # list attrs
            dos = cmds.listAttr(con1, k=True, s=True)
            donts = cmds.listAttr(con1, k=True, s=True, l=True)
            # expression
            for attr in dos:
                if attr not in donts:
                    offset = 0
                    # clean up old expression
                    deleteExpression(con=con2, attr=attr)
                    deleteExpression(con=con4, attr=attr)
                    if not removeOnly:
                        if 'r_front_leg_FootIk_Ctrl' in con:
                            if attr == 'translateX':
                                offset = 0.0
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con2, attr, str(f), con1, attr, offset * -1,)
                        print s
                        cmds.expression(s=s)
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con4, attr, str(f), con3, attr, offset,)
                        print s
                        cmds.expression(s=s)
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo_____'


def delayAnimation_hh(f=3, removeOnly=False):
    '''
    f = delay by frames
    '''
    controls = [
        'hh:r_legsfrond_KneeIk_Ctrl',
        'hh:r_legsfrond_LowerLegIk_Ctrl',
        'hh:r_legsfrond_BallIk_Ctrl',
        'hh:r_legsfrond_ToeIk_Ctrl',
        'hh:r_legsfrond_HeelIk_Ctrl',
        'hh:r_legsfrond_FootIk_Ctrl',
        'hh:r_legsfrond_Switch_Ctrl',
        'hh:r_legsfrond_ToePivotIk_Ctrl'
    ]
    r = True
    for con in controls:
        if cmds.objExists(con):
            # setup control names
            con1 = con
            con2 = con.replace('legsfrond', 'legsmid')
            con3 = con1.replace('r_', 'l_')
            con4 = con2.replace('r_', 'l_')
            # list attrs
            dos = cmds.listAttr(con1, k=True, s=True)
            donts = cmds.listAttr(con1, k=True, s=True, l=True)
            # expression
            for attr in dos:
                if attr not in donts and 'blendParent1' not in attr:
                    offset = 0
                    # clean up old expression
                    deleteExpression(con=con2, attr=attr)
                    deleteExpression(con=con4, attr=attr)
                    if not removeOnly:
                        if 'r_legsfrond_FootIk_Ctrl' in con or 'l_legsfrond_FootIk_Ctrl' in con:
                            if attr == 'translateZ':
                                offset = 4.5
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con2, attr, str(f), con1, attr, offset * -1,)
                        print s
                        cmds.expression(s=s)
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % (con4, attr, str(f), con3, attr, offset * -1,)
                        print s
                        cmds.expression(s=s)
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo____