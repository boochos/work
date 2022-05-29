import os
import maya.cmds as cmds
import maya.mel as mel
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
cw = web.mod( 'createWrap' )
zero = web.mod( 'zero' )
krl = web.mod( "key_rig_lib" )
ui = web.mod( "atom_ui_lib" )
cn = web.mod( "constraint_lib" )


def __________________BUILD():
    pass


def create( spans = 1, sections = 8, degree = 3, axis = [ 0, 0, 1 ], X = 1 ):
    '''
    degree = 1 or 3
    create rigged nurbs object
    row options to expand with end rows
    cv options for twist
    cv options for sliding based distance
    cv options for bulge
    '''
    # things to add

    #
    PreBuild = place.rigPrebuild( Top = 4, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = X * 10 )
    scale()
    MasterCt = PreBuild[5]
    # place.cleanUp( obj, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    #
    if axis == [ 0, 1, 0 ]:
        cv_shape = 'diamondYup_ctrl'
        row_shape = 'facetYup_ctrl'
        row_direction = 1  # y is up
    else:  # assume Z direction [ 0, 0, 1 ]
        cv_shape = 'diamondZup_ctrl'
        row_shape = 'facetZup_ctrl'
        row_direction = 2  # z is up
        codeScale = X * 2.5
        cmds.select( MasterCt[2] )
        ui.importCurveShape( name = row_shape, codeScale = codeScale )
        cmds.select( MasterCt[3] )
        ui.importCurveShape( name = row_shape, codeScale = codeScale * 0.9 )
    #
    name = 'retainer'
    geo = None
    colors = [ 'lightBlue', 'pink', 'hotPink', 'purple']
    row_cv_controls = []
    row_controls = []
    joints = []
    #
    if degree == 1 or degree == 3:
        geo = cmds.cylinder( name = name, axis = axis, spans = spans, sections = sections, degree = degree, heightRatio = 6 )
        place.cleanUp( geo[0], Body = True )
        rows = spans + 1
        cvs = sections

        rotation = -90
        rotation_inc = 360 / cvs  # each cv gets rotation to, for bulge effect
        if degree == 3:
            rows = rows + 2
            rotation = -90 + rotation_inc  # / cvs * -1

        # create parts

        clr = 0
        for r in range( rows ):
            #
            row_master = False
            cv_controls = []
            for c in range( cvs ):
                # cv name
                cv = name + '.cv[' + str( r ) + '][' + str( c ) + ']'
                cv_name = cv.replace( '.', '_' ).replace( '][', '_' ).replace( '[', '_' ).replace( ']', '' ).split( name + '_' )[1]
                # cv control
                pos = cmds.xform( cv, t = True, ws = True, q = True )
                cv_Ct = place.Controller2( cv_name, geo[0], False, cv_shape, X * 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                place.cleanUp( cv_Ct[0], Ctrl = True )
                cmds.xform( cv_Ct[0], ws = True, t = pos )
                cmds.setAttr( cv_Ct[0] + '.rotateZ' , rotation )  # doesnt account for up axis
                cv_controls.append( cv_Ct )
                rotation = rotation - rotation_inc
                # joint
                cmds.select( cv_Ct[2] )
                j = place.joint()
                j = cmds.rename( j, cv_Ct[2] + '_jnt' )
                place.cleanUp( j, SknJnts = True )
                cmds.parentConstraint( cv_Ct[4], j, mo = True )
                joints.append( j )
                # row master control
                if not row_master:
                    row_name = 'row_' + str( r )
                    row_Ct = place.Controller2( row_name, geo[0], False, row_shape, X * 5.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                    place.scaleUnlock( row_Ct[2], sx = True, sy = True, sz = False )
                    place.cleanUp( row_Ct[0], Ctrl = True )
                    insertTwistPivotControl( obj = row_Ct, X = X * 2, colorName = colors[clr] )
                    if row_direction == 1:
                        cmds.xform( row_Ct[0], ws = True, t = [ 0, pos[row_direction], 0 ] )
                    else:
                        cmds.xform( row_Ct[0], ws = True, t = [ 0, 0, pos[row_direction] ] )
                    cmds.parentConstraint( MasterCt[4], row_Ct[0], mo = True )
                    row_controls.append( row_Ct )
                    row_master = True
            # constrain cvs to row
            for cv_control in cv_controls:
                cmds.parentConstraint( row_Ct[4], cv_control[0], mo = True )
            row_cv_controls.append( cv_controls )
            # update color
            if degree == 3 and r == 0:  # next is 2nd, keep color
                # print( '2nd', r )
                pass
            elif degree == 3 and r == range( rows )[-3]:  # next is 2nd last, skip a color to match last iteration
                # print( '2nd last', r, range( rows )[-3] )
                clr = clr + 1
                if clr > len( colors ) - 1:
                    clr = 0
            elif degree == 3 and r == range( rows )[-2]:  # next is last, keep color from previous iteration
                # print( 'last', r, range( rows )[-2] )
                pass
            else:
                # print( 'nth', r )
                clr = clr + 1
                if clr > len( colors ) - 1:
                    clr = 0

        # skin before moving stuff around
        skin( joints, geo = geo[0] )
        #
        if degree == 3:  # could do this always to keep consistent if behaviour is bad even in linear(degree 1)
            degree3( row_controls, row_cv_controls )
            row_controls.pop( 1 )  # remove second
            row_controls.pop( -2 )  # remove second last
            row_cv_controls.pop( 1 )  # remove cv second
            row_cv_controls.pop( -2 )  # remove cv second last
        #
        # slideBulgeAll( row_cv_controls )
        slideBulgeAnchorsAll( row_cv_controls )
        twist( row_controls )
        # scale()
    else:
        print( 'degrees has to be 1 or 3' )


def scale():
    '''
    add scaling to rig on master control
    '''
    #
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.01, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )


def skin( joints = [], geo = '' ):
    '''
    skin object
    '''
    cmds.select( joints )
    cmds.select( geo, add = True )
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )


def degree3( row_controls, row_cv_controls ):
    '''
    make changes for degree 3 based nurbs object
    '''
    # rows to disappear
    #
    con = cn.getConstraint( row_controls[1][0] )
    cmds.delete( con )
    cmds.parentConstraint( row_controls[0][4], row_controls[1][0], mo = False )  # second, row_1
    cmds.setAttr( row_controls[1][0] + '.visibility', 0 )
    #
    con = cn.getConstraint( row_controls[-2][0] )
    cmds.delete( con )
    cmds.parentConstraint( row_controls[-1][4], row_controls[-2][0], mo = False )  # second last, row_4
    cmds.setAttr( row_controls[-2][0] + '.visibility', 0 )
    # row cvs to disappear
    for cv in range( len( row_cv_controls[1] ) ):  # second
        con = cn.getConstraint( row_cv_controls[1][cv][0] )
        cmds.delete( con )
        cmds.parentConstraint( row_cv_controls[0][cv][4], row_cv_controls[1][cv][0], mo = False )
        cmds.setAttr( row_cv_controls[1][cv][0] + '.visibility', 0 )
    for cv in range( len( row_cv_controls[-2] ) ):  # second last
        con = cn.getConstraint( row_cv_controls[-2][cv][0] )
        cmds.delete( con )
        cmds.parentConstraint( row_cv_controls[-1][cv][4], row_cv_controls[-2][cv][0], mo = False )
        cmds.setAttr( row_cv_controls[-2][cv][0] + '.visibility', 0 )


def twist( row_controls = [] ):
    '''
    add twist to mid rows, could use in place of twist joints
    min max weight
    ----
    add group under object to twist
    orient constraint to other twisting object
    connect weight to multDblLn node
    use other input as weight
    
    '''

    # weight increments
    rows = len( row_controls ) - 1
    weight_inc = 1.0 / rows
    w = weight_inc
    for row in row_controls:
        if row[0] != row_controls[0][0] and row[0] != row_controls[-1][0]:  # skip first and last row
            # attrs
            op = 'twist'
            attr1 = 'enable'
            attr2 = 'offset'
            attr3 = 'amount'
            attr4 = 'weight_start_end'
            misc.optEnum( row[2], attr = op, enum = 'CONTROL' )
            createAttr( obj = row[2], attr = attr1, dv = 1, typ = 'bool' )
            cmds.addAttr( row[2] + '.' + attr1, e = 1, min = 0, max = 1 )
            createAttr( obj = row[2], attr = attr2 )
            createAttr( obj = row[2], attr = attr3 )
            createAttr( obj = row[2], attr = attr4, k = 1, dv = w )
            cmds.addAttr( row[2] + '.' + attr4, e = 1, min = 0, max = 1 )
            # constraint
            con = cmds.orientConstraint( row_controls[0][4], row[1], mo = 1, skip = ( 'x', 'y' ) )[0]  # doesnt account for up axis or cylinder
            cmds.orientConstraint( row_controls[-1][4], row[1], mo = 1, skip = ( 'x', 'y' ) )  # doesnt account for up axis or cylinder
            con_weight_attrs = cmds.listAttr( con, ud = 1 )
            # connect
            rev = cmds.shadingNode( 'reverse', au = True, n = op + '_' + row[2] + '_rev' )
            cmds.connectAttr( row[2] + '.' + attr4, rev + '.inputX' )
            # enable target 1
            mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op + '_' + row[2] + '_enable1_mlt' )
            cmds.connectAttr( rev + '.outputX', mlt + '.input1' )
            cmds.connectAttr( row[2] + '.' + attr1, mlt + '.input2' )
            cmds.connectAttr( mlt + '.output', con + '.' + con_weight_attrs[0] )
            # enable target 2
            mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op + '_' + row[2] + '_enable2_mlt' )
            cmds.connectAttr( row[2] + '.' + attr4, mlt + '.input1' )
            cmds.connectAttr( row[2] + '.' + attr1, mlt + '.input2' )
            cmds.connectAttr( mlt + '.output', con + '.' + con_weight_attrs[1] )
            #
            cmds.connectAttr( row[1] + '.rotateZ', row[2] + '.' + attr3 )
            cmds.setAttr( row[2] + '.' + attr3, lock = 1 )
            cmds.connectAttr( row[2] + '.' + attr2, con + '.offsetZ' )  # doesnt account for up axis or cylinder
            #
            #
            w = w + weight_inc


def slideBulgeAll( row_cv_controls = [] ):
    '''
    connect cv rows with slide Bulge effect
    '''
    # start
    master_cvs = row_cv_controls[0]
    slave_cvs = row_cv_controls[1]
    for c in range( len( master_cvs ) ):
        slideBulge( master = master_cvs[c][2], slave = slave_cvs[c][2], slide_weight = 0.5, bulge_weight = 0.5 )
    # end
    master_cvs = row_cv_controls[-1]
    slave_cvs = row_cv_controls[-2]
    for c in range( len( master_cvs ) ):
        slideBulge( master = master_cvs[c][2], slave = slave_cvs[c][2], slide_weight = -0.5, bulge_weight = 0.5 )


def slideBulge( master = '', slave = '', slide_weight = 0.5, bulge_weight = 0.5 ):
    '''
    add sliding(translate along geo) based on distance from anchor cvs, or rotation of rows
    min max distance
    '''
    # attr names
    name = 'distance'
    suffix = 'root'
    op1 = 'slide'
    attr1 = 'neutralize_distance_' + suffix
    attr2 = 'distance_' + suffix
    attr3 = op1 + '_distance_' + suffix
    attr4 = op1 + '_weight_' + suffix
    op2 = 'bulge'
    attr5 = op2 + '_distance_' + suffix
    attr6 = op2 + '_weight_' + suffix
    #
    attr7 = op1 + '_enable'  # add math
    attr8 = op2 + '_enable'  # add math
    # add attrs
    misc.optEnum( slave, attr = name, enum = 'CONTROL' )
    createAttr( obj = slave, attr = attr2 )
    createAttr( obj = slave, attr = attr1 )
    misc.optEnum( slave, attr = op1, enum = 'CONTROL' )
    createAttr( obj = slave, attr = attr7, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr3 )
    createAttr( obj = slave, attr = attr4, k = 1, dv = slide_weight )
    misc.optEnum( slave, attr = op2, enum = 'CONTROL' )
    createAttr( obj = slave, attr = attr8, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr5 )
    createAttr( obj = slave, attr = attr6, k = 1, dv = bulge_weight )
    #
    slave_CtGrp = cmds.listRelatives( slave, p = True )[0]
    slave_TopGrp = cmds.listRelatives( slave_CtGrp, p = True )[0]
    master_CtGrp = cmds.listRelatives( master, p = True )[0]
    master_TopGrp = cmds.listRelatives( master_CtGrp, p = True )[0]
    distance( obj1 = slave_TopGrp, obj2 = master_TopGrp, attrObj = slave + '.' + attr2 )
    #
    sub = cmds.shadingNode( 'plusMinusAverage' , au = True, n = name + '_' + slave + '_' + master + '_sub' )
    cmds.setAttr( sub + '.operation', 2 )  # subtract
    cmds.connectAttr( slave + '.' + attr1, sub + '.input1D[0]' )
    cmds.connectAttr( slave + '.' + attr2, sub + '.input1D[1]' )
    # slide
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '_' + slave + '_' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr4, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr3 )
    #
    mlt2 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '_' + slave + '_' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr3, mlt2 + '.input1' )
    cmds.connectAttr( slave + '.' + attr7, mlt2 + '.input2' )
    cmds.connectAttr( mlt2 + '.output', slave_CtGrp + '.translateZ' )  # final output
    # bulge
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '_' + slave + '_' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr6, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr5 )
    #
    mlt3 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '_' + slave + '_' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr5, mlt3 + '.input1' )
    cmds.connectAttr( slave + '.' + attr8, mlt3 + '.input2' )
    cmds.connectAttr( mlt3 + '.output', slave_CtGrp + '.translateY' )  # final output
    # neutralize offset
    neutralize = cmds.getAttr( slave + '.' + attr2 )
    cmds.setAttr( slave + '.' + attr1, neutralize )
    #
    cmds.setAttr( slave + '.' + attr2, lock = 1 )
    cmds.setAttr( slave + '.' + attr3, lock = 1 )
    cmds.setAttr( slave + '.' + attr5, lock = 1 )


def slideBulgeAnchorsAll( row_cv_controls = [] ):
    '''
    connect cv rows with slide Bulge effect
    '''
    # start
    for r in range( len( row_cv_controls ) - 2 ):  # r = row iterator
        anchor1_cvs = row_cv_controls[0]  # locking to start and end rows, to get around cycle
        slave_cvs = row_cv_controls[r + 1]
        anchor2_cvs = row_cv_controls[-1]
        for c in range( len( anchor1_cvs ) ):
            slideBulgeAnchors( master = anchor1_cvs[c][2], slave = slave_cvs[c][2], slide_weight = 0.5, bulge_weight = 0.5 )
            slideBulgeAnchors( master = anchor2_cvs[c][2], slave = slave_cvs[c][2], slide_weight = 0.5, bulge_weight = 0.5 )


def slideBulgeAnchors( master = '', slave = '', slide_weight = 0.5, bulge_weight = 0.5, feedbackAttrs = False ):
    '''
    add sliding(translate along geo) based on distance from anchor cvs, or rotation of rows
    min max distance
    '''
    # attr names
    suffix = anchorAttr1()  # test for pre-existing, iterate
    # qualify suffix
    if cmds.attributeQuery( suffix, node = slave, ex = 1 ):
        suffix = anchorAttr2()

    attr0 = suffix
    attr1 = 'neutralize_distance_' + suffix
    attr2 = 'distance_' + suffix
    op1 = 'slide'
    attr3 = op1 + '_distance_' + suffix
    attr4 = op1 + '_w_' + suffix
    op2 = 'bulge'
    attr5 = op2 + '_distance_' + suffix
    attr6 = op2 + '_w_' + suffix
    attr7 = op1 + '_' + suffix  # add math
    attr8 = op2 + '_' + suffix  # add math
    # add attrs
    misc.optEnum( slave, attr = attr0, enum = 'CONTROL' )
    createAttr( obj = slave, attr = attr2, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr1, cb = feedbackAttrs )
    if feedbackAttrs:
        misc.optEnum( slave, attr = op1 + '_' + suffix, enum = master )
    createAttr( obj = slave, attr = attr7, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr3, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr4, k = 1, dv = slide_weight )
    if feedbackAttrs:
        misc.optEnum( slave, attr = op2 + '_' + suffix, enum = master )
    createAttr( obj = slave, attr = attr8, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr5, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr6, k = 1, dv = bulge_weight )
    #
    slave_CtGrp = cmds.listRelatives( slave, p = True )[0]
    slave_TopGrp = cmds.listRelatives( slave_CtGrp, p = True )[0]
    master_CtGrp = cmds.listRelatives( master, p = True )[0]
    master_TopGrp = cmds.listRelatives( master_CtGrp, p = True )[0]
    disNode = distance( name = '', obj1 = master_CtGrp, obj2 = slave_TopGrp, attrObj = slave + '.' + attr2 )  # (Ct --> Top)  <-- (causes cycle)

    # return
    #
    sub = cmds.shadingNode( 'plusMinusAverage' , au = True, n = slave + '___' + master + '_sub' )
    cmds.setAttr( sub + '.operation', 2 )  # subtract
    cmds.connectAttr( slave + '.' + attr1, sub + '.input1D[0]' )
    cmds.connectAttr( slave + '.' + attr2, sub + '.input1D[1]' )
    # return
    # slide
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '___' + slave + '___' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr4, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr3 )
    #
    mlt2 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '___' + slave + '___' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr3, mlt2 + '.input1' )
    cmds.connectAttr( slave + '.' + attr7, mlt2 + '.input2' )
    # return
    if suffix != 'anchor1':
        place.smartAttrBlend( master = mlt2, slave = slave_CtGrp, masterAttr = 'output', slaveAttr = 'translateZ', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True, blendAttrExisting = False )
        pass
    else:
        cmds.connectAttr( mlt2 + '.output', slave_CtGrp + '.translateZ' )  # final output
    # return
    # bulge
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '___' + slave + '___' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr6, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr5 )
    #
    mlt3 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '___' + slave + '___' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr5, mlt3 + '.input1' )
    cmds.connectAttr( slave + '.' + attr8, mlt3 + '.input2' )
    if suffix != 'anchor1':
        place.smartAttrBlend( master = mlt3, slave = slave_CtGrp, masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False )
        pass
    else:
        cmds.connectAttr( mlt3 + '.output', slave_CtGrp + '.translateY' )  # final output
    # neutralize offset
    neutralize = cmds.getAttr( slave + '.' + attr2 )
    cmds.setAttr( slave + '.' + attr1, neutralize )
    #
    cmds.setAttr( slave + '.' + attr2, lock = 1 )
    cmds.setAttr( slave + '.' + attr3, lock = 1 )
    cmds.setAttr( slave + '.' + attr5, lock = 1 )


def dynamic():
    '''
    add dynamic jiggle to cv
    '''
    pass


def __________________UTIL():
    pass


def anchorAttr1():
    '''
    string for anchor
    '''
    return '_1'


def anchorAttr2():
    '''
    string for anchor
    '''
    return '_2'


def createAttr( obj = '', attr = '', k = False, l = False, dv = 0.0, typ = 'float', cb = True ):
    '''
    creates attr and applies expression
    '''
    cmds.addAttr( obj, longName = attr, attributeType = typ, k = k, dv = dv )
    cmds.setAttr( obj + "." + attr, cb = cb )
    cmds.setAttr( obj + "." + attr, k = k )
    cmds.setAttr( obj + "." + attr, lock = l )


def createDisNode( name = '' ):
    dis = cmds.createNode( 'distanceBetween', name = name + '___dis' )
    return dis


def insertTwistPivotControl( obj = [], X = 1, colorName = '' ):
    '''
    obj = expected to be full controller hierarchy
    creates a control, used to place a row control, so CtGrp twists from the correct position. 
    this control should be used to place the row
    '''
    #
    ctrl = place.circle( name = obj[2] + '_twistPvt', obj = obj[2], shape = 'loc_ctrl', size = X, colorName = colorName )[0]
    attr = 'Pivot_Vis'
    place.addAttribute( obj[2], attr, 0, 1, False, 'long' )
    cmds.connectAttr( obj[2] + '.' + attr, ctrl + 'Shape' + '.visibility' )
    #
    cmds.parent( ctrl, obj[0] )
    cmds.parent( obj[1], ctrl )


def slideLimits():
    '''
    add attr limits to slide Ct_Grp
    scale with rig
    '''
    pass


def bulgeLimits():
    '''
    add attr limits to bulge Ct_Grp
    scale with rig
    '''
    pass


def distance( name = '', obj1 = '', obj2 = '', attrObj = '' ):
    '''
    assembles distance relationship
    attrObj should include attribute name
    '''
    # connect to distance node
    if name:
        name = name + '___'
    #
    disNode = createDisNode( name = name + obj1 + '___' + obj2 )
    cmds.connectAttr( obj1 + '.worldMatrix[0]', disNode + '.inMatrix1' )
    cmds.connectAttr( obj2 + '.worldMatrix[0]', disNode + '.inMatrix2' )
    # add scale connection, create div node
    mltNode = cmds.shadingNode( 'multiplyDivide', au = True, n = ( name + 'ScaleDiv' ) )  # increase travel from (0.0-1.0 to 0.0-10.0)
    cmds.setAttr( ( mltNode + '.operation' ), 2 )  # set operation: 2 = divide, 1 = multiply
    cmds.connectAttr( disNode + '.distance', mltNode + '.input1X' )
    cmds.connectAttr( 'master.uniformScale', mltNode + '.input2X' )
    # feed distance attrs
    cmds.connectAttr( mltNode + '.outputX', attrObj )  # scaled output
    return


def neutralizeDistances():
    '''
    find all controls with proper attrs, run script to neutralize offset
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    for s in sel:
        # find control group
        parent = findParent( s )
        if parent:
            topGrps = cmds.listRelatives( parent, c = True )
            for topGrp in topGrps:
                ctGrp = cmds.listRelatives( topGrp, c = True )
                for item in ctGrp:
                    if '_CtGrp' in item:
                        control = cmds.listRelatives( item, c = True )
                        for c in control:
                            if cmds.attributeQuery( anchorAttr1(), node = c, ex = 1 ):
                                controls.append( c )
                            else:
                                print( c )
                    else:
                        # print( 'no ctGrp', item )
                        pass
        else:
            # print( 'no controls' )
            pass
    if controls:
        for c in controls:
            dis = cmds.getAttr( c + '.distance_' + anchorAttr1() )
            cmds.setAttr( c + '.neutralize_distance_' + anchorAttr1(), dis )
            dis = cmds.getAttr( c + '.distance_' + anchorAttr2() )
            cmds.setAttr( c + '.neutralize_distance_' + anchorAttr2(), dis )


def neutralizeRows():
    '''
    find all row controls with proper attrs, run script to reset parent nodes (pivot offset above Ct group), 
    ie, match position of row control, reset row control to zero
    '''
    pass


def disable( state = False ):
    '''
    disable all deformation effects
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    for s in sel:
        # find control group
        parent = findParent( s )
        if parent:
            topGrps = cmds.listRelatives( parent, c = True )
            for topGrp in topGrps:
                ctGrp = cmds.listRelatives( topGrp, c = True )
                for item in ctGrp:
                    if '_CtGrp' in item:
                        control = cmds.listRelatives( item, c = True )
                        for c in control:
                            if cmds.attributeQuery( anchorAttr1(), node = c, ex = 1 ):
                                controls.append( c )
                            else:
                                # print( c )
                                pass
                    else:
                        # print( 'no ctGrp', item )
                        pass
        else:
            # print( 'no controls' )
            pass
    if controls:
        for c in controls:
            cmds.setAttr( c + '.slide_enable_' + anchorAttr1(), state )
            cmds.setAttr( c + '.slide_enable_' + anchorAttr2(), state )
            cmds.setAttr( c + '.bulge_enable_' + anchorAttr1(), state )
            cmds.setAttr( c + '.bulge_enable_' + anchorAttr2(), state )


def findParent( obj = '', find = '___CONTROLS' ):
    '''
    find 1st parent in hierarchy
    '''
    limit = 50
    i = 0
    if obj:
        while i < limit:
            parent = cmds.listRelatives( obj, p = True )
            if parent:
                obj = parent[0]
                if obj == find:
                    return obj
            i = i + 1
        print( 'nothing' )
        return None
    else:
        print( 'needs an object' )


def mirror():
    '''
    take one retainer shape, mirror position of all controls in world space to opposite side.
    '''
    pass
