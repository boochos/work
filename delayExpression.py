import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
place = web.mod( "atom_place_lib" )
cn = web.mod( 'constraint_lib' )


def deleteExpression( con = '', attr = '' ):
    '''
    #
    '''
    # find exp
    cnn = cmds.listConnections( con + '.' + attr, s = True, d = False )
    if cnn:
        if cmds.nodeType( cnn[0] ) == 'unitConversion':
            cnn_uc = cmds.listConnections( cnn, s = True, d = False, type = 'expression' )
            if cnn_uc:
                if cmds.nodeType( cnn_uc[0] ) == 'expression':
                    exp = cnn_uc[0]
        elif cmds.nodeType( cnn[0] ) == 'expression':
            exp = cnn[0]
        # delete exp
        if exp:
            st1 = cmds.expression( exp, q = True, s = True )
            st2 = 'frame'
            if st2 in st1:
                cmds.delete( exp )
                print( 'deleted___  ', con, '  ___  ', exp )
            else:
                print( '    nope     ' )
        else:
            print( 'no expression  ', attr )


def delayAnimation( f = 5, removeOnly = False ):
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
        con2 = con.replace( 'legfront', 'legmid' )
        con3 = con1.replace( '_r_', '_l_' )
        con4 = con2.replace( '_r_', '_l_' )
        # list attrs
        dos = cmds.listAttr( con1, k = True, s = True )
        donts = cmds.listAttr( con1, k = True, s = True, l = True )
        # expression
        for attr in dos:
            if attr not in donts:
                offset = 0
                # clean up old expression
                deleteExpression( con = con2, attr = attr )
                deleteExpression( con = con4, attr = attr )
                if not removeOnly:
                    if 'HexapedeRig_r_legfront_FootIk_Ctrl' in con:
                        if attr == 'translateX':
                            offset = 0.4
                    # add new expression
                    s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con2, attr, str( f ), con1, attr, offset * -1, )
                    print( s )
                    cmds.expression( s = s )
                    s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con4, attr, str( f ), con3, attr, offset, )
                    print( s )
                    cmds.expression( s = s )
                    offset = 0
            else:
                pass
                # print attr, '    nooooo_____'


def delayAnimation_tapirus( f = 5, removeOnly = False ):
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
        if cmds.objExists( con ):
            # setup control names
            con1 = con
            con2 = con.replace( 'front_leg', 'mid_leg' )
            con3 = con1.replace( 'r_', 'l_' )
            con4 = con2.replace( 'r_', 'l_' )
            # list attrs
            dos = cmds.listAttr( con1, k = True, s = True )
            donts = cmds.listAttr( con1, k = True, s = True, l = True )
            # expression
            for attr in dos:
                if attr not in donts and 'blendParent1' not in attr:
                    offset = 0
                    # clean up old expression
                    deleteExpression( con = con2, attr = attr )
                    deleteExpression( con = con4, attr = attr )
                    if not removeOnly:
                        if 'r_front_leg_FootIk_Ctrl' in con:
                            if attr == 'translateX':
                                offset = 0.0
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con2, attr, str( f ), con1, attr, offset * -1, )
                        print( s )
                        cmds.expression( s = s )
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con4, attr, str( f ), con3, attr, offset, )
                        print( s )
                        cmds.expression( s = s )
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo_____'


def delayAnimation_sturm( f = 3, removeOnly = False ):
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
        if cmds.objExists( con ):
            # setup control names
            con1 = con
            con2 = con.replace( 'front_leg', 'mid_leg' )
            con3 = con1.replace( 'r_', 'l_' )
            con4 = con2.replace( 'r_', 'l_' )
            # list attrs
            dos = cmds.listAttr( con1, k = True, s = True )
            donts = cmds.listAttr( con1, k = True, s = True, l = True )
            # expression
            for attr in dos:
                if attr not in donts:
                    offset = 0
                    # clean up old expression
                    deleteExpression( con = con2, attr = attr )
                    deleteExpression( con = con4, attr = attr )
                    if not removeOnly:
                        if 'r_front_leg_FootIk_Ctrl' in con:
                            if attr == 'translateX':
                                offset = 0.0
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con2, attr, str( f ), con1, attr, offset * -1, )
                        print( s )
                        cmds.expression( s = s )
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con4, attr, str( f ), con3, attr, offset, )
                        print( s )
                        cmds.expression( s = s )
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo_____'


def delayAnimation_hh( f = 3, removeOnly = False ):
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
        if cmds.objExists( con ):
            # setup control names
            con1 = con
            con2 = con.replace( 'legsfrond', 'legsmid' )
            con3 = con1.replace( 'r_', 'l_' )
            con4 = con2.replace( 'r_', 'l_' )
            # list attrs
            dos = cmds.listAttr( con1, k = True, s = True )
            donts = cmds.listAttr( con1, k = True, s = True, l = True )
            # expression
            for attr in dos:
                if attr not in donts and 'blendParent1' not in attr:
                    offset = 0
                    # clean up old expression
                    deleteExpression( con = con2, attr = attr )
                    deleteExpression( con = con4, attr = attr )
                    if not removeOnly:
                        if 'r_legsfrond_FootIk_Ctrl' in con or 'l_legsfrond_FootIk_Ctrl' in con:
                            if attr == 'translateZ':
                                offset = 4.5
                        # add new expression
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con2, attr, str( f ), con1, attr, offset * -1, )
                        print( s )
                        cmds.expression( s = s )
                        s = '%s.%s = `getAttr -t (frame-%s) %s.%s` + %s;' % ( con4, attr, str( f ), con3, attr, offset * -1, )
                        print( s )
                        cmds.expression( s = s )
                        offset = 0
                else:
                    pass
                    # print attr, '    nooooo____


def globalWeightAttrStr():
    return 'globalWeight'


def statusAttrStr():
    return 'status'


def weightRotAttrStr():
    return 'delayWeightRot'


def delayRotAttrStr():
    return 'delayByFramesRot'


def weightPosAttrStr():
    return 'delayWeightPos'


def delayPosAttrStr():
    return 'delayByFramesPos'


def delayNodeStr():
    return '___delayNode___'


def getUniqueName( name = '' ):
    # print( name )
    if '|' in name:
        name = name.split( '|' )[-1]
    if not cmds.objExists( name ):
        return name
    else:
        i = 1
        while cmds.objExists( name + str( i ) + '___' ):
            i = i + 1
        return name + str( i ) + '___'


def create_delay_rotation_constraint():
    '''
    "My name is %s and I'm %d" % ('john', 12) #My name is john and I'm 12
    float $offset = `getAttr pCylinder5_orientConstraint1.delayByFrames`;
    pCylinder5_orientConstraint1.delayedRotateX = `getAttr -t (frame-$offset) pCylinder5_orientConstraint1.constraintRotateX`;
    '''
    #
    print( 'create' )
    #
    '''
    name = getUniqueName( name )
    '''
    #
    attr_suffix = 'Rotate'
    attr_type = 'doubleAngle'

    loc = ''
    sel = cmds.ls( sl = True )
    # if not cmds.objExists( name ):
    if len( sel ) == 2:
        # loc = cmds.spaceLocator( n = name )[0]
        # loc = ''
        # sel = cmds.ls( sl = True )
        # if len( sel ) == 2:
        loc = cmds.orientConstraint( sel[0], sel[1], mo = True )[0]

        # attr
        attr = 'delaySettings'
        cmds.addAttr( loc, ln = attr, h = False, at = 'enum', en = '________' )
        cmds.setAttr( ( loc + '.' + attr ), cb = True )
        cmds.setAttr( ( loc + '.' + attr ), k = False )
        # attr
        weight = weightRotAttrStr()
        cmds.addAttr( loc, ln = weight, h = False, at = 'float', min = 0, max = 2, dv = 1 )
        cmds.setAttr( ( loc + '.' + weight ), cb = True )
        cmds.setAttr( ( loc + '.' + weight ), k = True )
        # attr
        delayByFrames = delayRotAttrStr()
        cmds.addAttr( loc, ln = delayByFrames, h = False, at = 'float', dv = 2 )
        cmds.setAttr( ( loc + '.' + delayByFrames ), cb = True )
        cmds.setAttr( ( loc + '.' + delayByFrames ), k = True )
        #
        vis = False
        attr = 'outputRot'
        cmds.addAttr( loc, ln = attr, h = False, at = 'enum', en = '________' )
        cmds.setAttr( ( loc + '.' + attr ), cb = vis )
        cmds.setAttr( ( loc + '.' + attr ), k = False )
        # attr
        delayedRotateX = 'delayedRotateX'
        cmds.addAttr( loc, ln = delayedRotateX, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedRotateX ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedRotateX ), k = False )
        # attr
        delayedRotateY = 'delayedRotateY'
        cmds.addAttr( loc, ln = delayedRotateY, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedRotateY ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedRotateY ), k = False )
        # attr
        delayedRotateZ = 'delayedRotateZ'
        cmds.addAttr( loc, ln = delayedRotateZ, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedRotateZ ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedRotateZ ), k = False )
        #
        # check if constraint has pairBlendConnection
        con = cmds.listConnections( loc + '.constraintRotateX', s = 0, d = 1, plugs = True )
        print( con )
        # attr
        weightedRotateX = 'weightedRotateX'
        cmds.addAttr( loc, ln = weightedRotateX, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraintRotateX', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedRotateX, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedRotateX ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedRotateX ), k = False )
        # attr
        weightedRotateY = 'weightedRotateY'
        cmds.addAttr( loc, ln = weightedRotateY, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraintRotateY', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedRotateY, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedRotateY ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedRotateY ), k = False )
        # attr
        weightedRotateZ = 'weightedRotateZ'
        cmds.addAttr( loc, ln = weightedRotateZ, h = False, at = 'doubleAngle', min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraintRotateZ', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedRotateZ, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedRotateZ ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedRotateZ ), k = False )
        #
        s = 'float $offset = `getAttr %s.%s`;\n' % ( loc, delayByFrames )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedRotateX, loc, 'constraintRotateX' )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedRotateY, loc, 'constraintRotateY' )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedRotateZ, loc, 'constraintRotateZ' )
        print( s )
        cmds.expression( s = s, n = 'delayRotExpression' )
        #
        blnd = cmds.createNode( "animBlendNodeAdditiveRotation", n = 'blendDelayRotWeight' )  # blend between constraint and offset value ## animBlendNodeAdditiveRotation
        #
        cmds.connectAttr( loc + '.offsetX', blnd + '.inputAX', f = True )  # offsets to blend in
        cmds.connectAttr( loc + '.offsetY', blnd + '.inputAY', f = True )
        cmds.connectAttr( loc + '.offsetZ', blnd + '.inputAZ', f = True )
        #
        cmds.connectAttr( loc + '.' + delayedRotateX, blnd + '.inputBX', f = True )  # delayed contraint value to blend in
        cmds.connectAttr( loc + '.' + delayedRotateY, blnd + '.inputBY', f = True )
        cmds.connectAttr( loc + '.' + delayedRotateZ, blnd + '.inputBZ', f = True )
        #
        cmds.connectAttr( loc + '.' + weight, blnd + '.weightB', f = True )  # constraint custom weight to blend weightB
        #
        rev = cmds.shadingNode( 'reverse', asUtility = True, n = 'reverseRotW' )  # reverse
        cmds.connectAttr( loc + '.' + weight, rev + '.inputX', f = True )  # constraint custom weight to rev in
        cmds.connectAttr( rev + '.outputX', blnd + '.weightA', f = True )  # rev out to blend weightA
        #
        cmds.connectAttr( blnd + '.outputX', loc + '.' + weightedRotateX, f = True )  # blended out to weighted customs in, outs are already connected
        cmds.connectAttr( blnd + '.outputY', loc + '.' + weightedRotateY, f = True )
        cmds.connectAttr( blnd + '.outputZ', loc + '.' + weightedRotateZ, f = True )
        #
        # this breaks auto creation of blend attr in constraints, maybe... think constraint cant find its destination fo rthe pairBlend
        place.hijackAttrs( loc, sel[1], weightRotAttrStr(), weightRotAttrStr(), set = False, default = None, force = True )  # hijack to slave object for easier rebuild / (export/import)
        place.hijackAttrs( loc, sel[1], delayRotAttrStr(), delayRotAttrStr(), set = False, default = None, force = True )
        #
        return loc
    else:
        print( 'select 2 objects, like you would to create a constraint' )


def create_delay_position_constraint():
    '''
    "My name is %s and I'm %d" % ('john', 12) #My name is john and I'm 12
    float $offset = `getAttr pCylinder5_orientConstraint1.delayByFrames`;
    pCylinder5_orientConstraint1.delayedRotateX = `getAttr -t (frame-$offset) pCylinder5_orientConstraint1.constraintRotateX`;
    
    EXISTING ANIM CURVES GET DISCONNECTED , fix
    '''
    #
    print( 'create' )
    #
    '''
    name = getUniqueName( name )
    '''
    #
    attr_suffix = 'Translate'
    attr_type = 'doubleLinear'

    loc = ''
    sel = cmds.ls( sl = True )
    #
    if len( sel ) == 2:
        #
        loc = cmds.pointConstraint( sel[0], sel[1], mo = True )[0]
        # attr
        attr = 'delaySettings'
        cmds.addAttr( loc, ln = attr, h = False, at = 'enum', en = '________' )
        cmds.setAttr( ( loc + '.' + attr ), cb = True )
        cmds.setAttr( ( loc + '.' + attr ), k = False )
        # attr
        weight = weightPosAttrStr()
        cmds.addAttr( loc, ln = weight, h = False, at = 'float', min = 0, max = 2, dv = 1 )
        cmds.setAttr( ( loc + '.' + weight ), cb = True )
        cmds.setAttr( ( loc + '.' + weight ), k = True )
        # attr
        delayByFrames = delayPosAttrStr()
        cmds.addAttr( loc, ln = delayByFrames, h = False, at = 'float', dv = 2 )
        cmds.setAttr( ( loc + '.' + delayByFrames ), cb = True )
        cmds.setAttr( ( loc + '.' + delayByFrames ), k = True )
        #
        vis = False
        attr = 'output' + attr_suffix
        cmds.addAttr( loc, ln = attr, h = False, at = 'enum', en = '________' )
        cmds.setAttr( ( loc + '.' + attr ), cb = vis )
        cmds.setAttr( ( loc + '.' + attr ), k = False )
        # attr
        delayedX = 'delayed' + attr_suffix + 'X'
        cmds.addAttr( loc, ln = delayedX, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedX ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedX ), k = False )
        # attr
        delayedY = 'delayed' + attr_suffix + 'Y'
        cmds.addAttr( loc, ln = delayedY, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedY ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedY ), k = False )
        # attr
        delayedZ = 'delayed' + attr_suffix + 'Z'
        cmds.addAttr( loc, ln = delayedZ, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        cmds.setAttr( ( loc + '.' + delayedZ ), cb = vis )
        cmds.setAttr( ( loc + '.' + delayedZ ), k = False )
        #
        # attr
        weightedX = 'weighted' + attr_suffix + 'X'
        cmds.addAttr( loc, ln = weightedX, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraint' + attr_suffix + 'X', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedX, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedX ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedX ), k = False )
        # attr
        weightedY = 'weighted' + attr_suffix + 'Y'
        cmds.addAttr( loc, ln = weightedY, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraint' + attr_suffix + 'Y', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedY, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedY ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedY ), k = False )
        # attr
        weightedZ = 'weighted' + attr_suffix + 'Z'
        cmds.addAttr( loc, ln = weightedZ, h = False, at = attr_type, min = 0, max = 1, dv = 0 )
        plugs = cmds.listConnections( loc + '.constraint' + attr_suffix + 'Z', s = 0, d = 1, plugs = True )
        cmds.connectAttr( loc + '.' + weightedZ, plugs[0], f = True )
        cmds.setAttr( ( loc + '.' + weightedZ ), cb = vis )
        cmds.setAttr( ( loc + '.' + weightedZ ), k = False )
        #
        s = 'float $offset = `getAttr %s.%s`;\n' % ( loc, delayByFrames )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedX, loc, 'constraint' + attr_suffix + 'X' )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedY, loc, 'constraint' + attr_suffix + 'Y' )
        s = s + '%s.%s = `getAttr -t (frame-$offset) %s.%s`;\n' % ( loc, delayedZ, loc, 'constraint' + attr_suffix + 'Z' )
        print( s )
        cmds.expression( s = s, n = 'delayPosExpression' )
        #
        blndX = cmds.createNode( "animBlendNodeAdditiveDL", n = 'blendDelay' + attr_suffix + 'XWeight' )  # blend between constraint and offset value ## animBlendNodeAdditiveRotation
        blndY = cmds.createNode( "animBlendNodeAdditiveDL", n = 'blendDelay' + attr_suffix + 'YWeight' )  # blend between constraint and offset value ## animBlendNodeAdditiveRotation
        blndZ = cmds.createNode( "animBlendNodeAdditiveDL", n = 'blendDelay' + attr_suffix + 'ZWeight' )  # blend between constraint and offset value ## animBlendNodeAdditiveRotation
        #
        cmds.connectAttr( loc + '.restTranslateX', blndX + '.inputA', f = True )  # offsets to blend in
        cmds.connectAttr( loc + '.restTranslateY', blndY + '.inputA', f = True )
        cmds.connectAttr( loc + '.restTranslateZ', blndZ + '.inputA', f = True )
        #
        cmds.connectAttr( loc + '.' + delayedX, blndX + '.inputB', f = True )  # delayed contraint value to blend in
        cmds.connectAttr( loc + '.' + delayedY, blndY + '.inputB', f = True )
        cmds.connectAttr( loc + '.' + delayedZ, blndZ + '.inputB', f = True )
        #
        cmds.connectAttr( loc + '.' + weight, blndX + '.weightB', f = True )  # constraint custom weight to blend weightB
        cmds.connectAttr( loc + '.' + weight, blndY + '.weightB', f = True )  # constraint custom weight to blend weightB
        cmds.connectAttr( loc + '.' + weight, blndZ + '.weightB', f = True )  # constraint custom weight to blend weightB
        #
        rev = cmds.shadingNode( 'reverse', asUtility = True, n = 'reverse' + attr_suffix + 'W' )  # reverse
        cmds.connectAttr( loc + '.' + weight, rev + '.inputX', f = True )  # constraint custom weight to rev in
        cmds.connectAttr( rev + '.outputX', blndX + '.weightA', f = True )  # rev out to blend weightA
        cmds.connectAttr( rev + '.outputX', blndY + '.weightA', f = True )  # rev out to blend weightA
        cmds.connectAttr( rev + '.outputX', blndZ + '.weightA', f = True )  # rev out to blend weightA
        #
        cmds.connectAttr( blndX + '.output', loc + '.' + weightedX, f = True )  # blended out to weighted customs in, outs are already connected
        cmds.connectAttr( blndY + '.output', loc + '.' + weightedY, f = True )
        cmds.connectAttr( blndZ + '.output', loc + '.' + weightedZ, f = True )
        #
        # this breaks auto creation of blend attr in constraints, maybe... think constraint cant find its destination fo rthe pairBlend
        place.hijackAttrs( loc, sel[1], weightPosAttrStr(), weightPosAttrStr(), set = False, default = None, force = True )  # hijack to slave object for easier rebuild / (export/import)
        place.hijackAttrs( loc, sel[1], delayPosAttrStr(), delayPosAttrStr(), set = False, default = None, force = True )
        #
        return loc
    else:
        print( 'select 2 objects, like you would to create a constraint' )


def delayGrpStr():
    return  '___delay___grp'


def charybdis_tentacles_delayRotations( side = 'L' ):
    '''
    
    '''
    #
    constraints = []
    ns = ''
    sel = cmds.ls( sl = True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
        #
        _p = delayGrpStr()
        if not cmds.objExists( delayGrpStr() ):
            _p = cmds.group( n = delayGrpStr(), em = True )  # cleanup group
        #
        _t_main = ':' + side + '_tentacle4_globalOffset_ctrl'
        master = ns + _t_main
        #
        '''
        # tentacle number ref
        1 = back
        2 = inside
        3 = outside
        5 = front
        6 = small - outside
        7 = small - between
        8 = small - inside
        '''
        _t = [
        ':' + side + '_tentacle1_global_ctrl',
        ':' + side + '_tentacle2_global_ctrl',
        ':' + side + '_tentacle3_global_ctrl',
        ':' + side + '_tentacle5_global_ctrl',
        ':' + side + '_tentacle6_global_ctrl',
        ':' + side + '_tentacle7_global_ctrl',
        ':' + side + '_tentacle8_global_ctrl'
        ]
        # [weight, delay]
        _settings = [
            [0.2, 20],  # back
            [0.4, 14],  # inside
            [0.5, 16],  # outside
            [0.6, 12],  # front
            [0.2, 13],  # small - outside
            [0.18, 10],  # small - between
            [0.16, 16]  # small - inside
            ]
        # pseudo target
        _pseudo_master = cmds.group( n = place.getUniqueName( master + '__delay__' ), em = True )
        _up = ns + ':' + side + '_tentacle4_global_ctrl_aimUp_loc'
        #
        cmds.pointConstraint( master, _pseudo_master, mo = False )
        cmds.aimConstraint( ns + ':' + side + '_tentacle4_5_ctrl', _pseudo_master, wut = 'object', wuo = _up, aim = [1, 0, 0], u = [0, 1, 0], mo = False )
        cmds.parent( _pseudo_master, _p )
        # delay constraints
        i = 0
        for t in _t:
            slave = ns + t
            cmds.select( [_pseudo_master, slave] )
            c = create_delay_rotation_constraint()
            constraints.append( c )
            #
            cmds.setAttr( slave + '.' + weightRotAttrStr(), _settings[i][0] )
            cmds.setAttr( slave + '.' + delayRotAttrStr(), _settings[i][1] )

            i += 1
    else:
        print( 'Select an objet from the rig' )


def charybdis_tentacles_main_delayPositions( side = 'L' ):
    '''
    point contraints with delay for main tentacles
    '''
    constraints = []
    ns = ''
    sel = cmds.ls( sl = True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
        # delay group
        _p = delayGrpStr()
        if not cmds.objExists( delayGrpStr() ):
            _p = cmds.group( n = delayGrpStr(), em = True )  # cleanup parent group
        # master tentacle control
        master = ns + ':' + side + '_tentacle4_globalOffset_ctrl'
        # group for main tentacle controls
        _m = cmds.group( n = delayGrpStr() + '_' + side + '_main', em = True )  # main pos
        cmds.parent( _m, _p )
        # tip new driver
        _tip = ns + ':' + side + '_tentacle4_5_ctrl'
        cmds.select( _tip )
        _tip_pseudo = cn.locatorOnSelection( ro = 'zxy', X = 1.3, constrain = True, toSelection = False, group = True )
        _tip_pseudo.append( cmds.listRelatives( _tip_pseudo[0], parent = True )[0] )
        cmds.parentConstraint( master, _tip_pseudo[1], mo = True )  # grp
        cmds.parentConstraint( _tip_pseudo[0], _tip, mo = True )  # control
        cmds.parent( _tip_pseudo[1], _m )
        # return
        #
        _t = [
        ns + ':' + side + '_tentacle4_4_ctrl',
        ns + ':' + side + '_tentacle4_3_ctrl',
        ns + ':' + side + '_tentacle4_2_ctrl',
        ns + ':' + side + '_tentacle4_1_ctrl'
        ]
        # [weight, delay]
        _settings = [
            [0.75, 6],
            [0.5, 10],
            [0.2, 14],
            [0.1, 18]
            ]
        i = 0
        for t in _t:
            cmds.select( t )
            t_pseudo = cn.locatorOnSelection( ro = 'zxy', X = 1.3, constrain = True, toSelection = False, group = True )
            t_pseudo.append( cmds.listRelatives( t_pseudo[0], parent = True )[0] )
            cmds.parent( t_pseudo[1], _m )
            cmds.parentConstraint( master, t_pseudo[1], mo = True )  # grp
            cmds.parentConstraint( t_pseudo[0], t, mo = True )  # control
            #
            cmds.select( [_tip_pseudo[0], t_pseudo[0]] )
            c = create_delay_position_constraint()
            constraints.append( c )
            #
            cmds.setAttr( t_pseudo[0] + '.' + weightPosAttrStr(), _settings[i][0] )
            cmds.setAttr( t_pseudo[0] + '.' + delayPosAttrStr(), _settings[i][1] )

            i += 1
    else:
        print( 'Select an objet from the rig' )


def charybdis_tentacles_neighbors_delayPositions( side = 'L' ):
    '''
    point contraints with delay for main tentacles
    '''
    constraints = []
    ns = ''
    sel = cmds.ls( sl = True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
        #
        '''
        _p = delayGrpStr()
        if not cmds.objExists( delayGrpStr() ):
            _p = cmds.group( n = delayGrpStr(), em = True )  # cleanup group
            '''
        #
        _pairs = [
            [
            ns + ':' + side + '_tentacle4_4_ctrl',
            ns + ':' + side + '_tentacle5_4_ctrl'  # front
            ],
            [
            ns + ':' + side + '_tentacle4_4_ctrl',
            ns + ':' + side + '_tentacle3_4_ctrl'  # outside
            ],
            [
            ns + ':' + side + '_tentacle4_3_ctrl',
            ns + ':' + side + '_tentacle2_4_ctrl'  # inside
            ],
            [
            ns + ':' + side + '_tentacle3_3_ctrl',
            ns + ':' + side + '_tentacle1_4_ctrl'  # back
            ]
            ]
        # [weight, delay]
        _settings = [
            [0.75, 2],
            [0.75, 2],
            [0.75, 2],
            [0.75, 2]
            ]
        i = 0
        for p in _pairs:
            slave = p[1]
            cmds.select( [p[0], slave] )
            c = create_delay_position_constraint()
            constraints.append( c )
            #
            cmds.setAttr( slave + '.' + weightPosAttrStr(), _settings[i][0] )
            cmds.setAttr( slave + '.' + delayPosAttrStr(), _settings[i][1] )

            i += 1

'''
import webrImport as web
dly = web.mod("delayExpression")
dly.charybdis_tentacles_delayRotations()
        
import webrImport as web
dly = web.mod("delayExpression")
dly.charybdis_tentacles_main_delayPositions()

import webrImport as web
dly = web.mod("delayExpression")
dly.charybdis_tentacles_neighbors_delayPositions()

import webrImport as web
dly = web.mod("delayExpression")
dly.create_delay_position_constraint()


import webrImport as web
dly = web.mod("delayExpression")
dly.create_delay_rotation_constraint()

#
'''
