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


def create( spans = 1, sections = 8, degree = 3, axis = [ 0, 0, 1 ], X = 1, twist = True ):
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
    MasterCt = PreBuild[5]
    # place.cleanUp( obj, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    #
    if axis == [ 0, 1, 0 ]:
        cv_shape = 'diamondYup_ctrl'
        row_shape = 'facetYup_ctrl'
        row_direction = 1
    else:  # assume Z direction [ 0, 0, 1 ]
        cv_shape = 'diamondZup_ctrl'
        row_shape = 'facetZup_ctrl'
        row_direction = 2
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
        geo = cmds.cylinder( name = name, axis = axis, spans = spans, sections = sections, degree = degree )
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
                cmds.setAttr( cv_Ct[0] + '.rotateZ' , rotation )
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
        #
        scale()
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


def twist():
    '''
    add twist to mid rows, could use in place of twist joints
    min max weight
    ----
    add group under object to twist
    orient constraint to other twisting object
    connect weight to multDblLn node
    use other input as weight
    
    '''
    pass


def slideBulge( obj1 = '', obj2 = '' ):
    '''
    add sliding(translate along geo) based on distance from anchor cvs, or rotation of rows
    min max weight
    '''
    #
    name = 'distance'
    op1 = 'slide'
    attr1 = 'neutralize_distance_' + obj2
    attr2 = 'distance_' + obj2
    attr3 = op1 + '_distance_' + obj2
    attr4 = op1 + '_weight_' + obj2
    op2 = 'bulge'
    attr5 = op2 + '_distance_' + obj2
    attr6 = op2 + '_weight_' + obj2
    #
    misc.optEnum( obj1, attr = name, enum = 'FEEDBACK' )
    createAttr( obj = obj1, attr = attr2 )
    createAttr( obj = obj1, attr = attr1 )
    misc.optEnum( obj1, attr = op1, enum = 'CONTROL' )
    createAttr( obj = obj1, attr = attr3 )
    createAttr( obj = obj1, attr = attr4, k = 1, dv = 0.5 )
    misc.optEnum( obj1, attr = op2, enum = 'CONTROL' )
    createAttr( obj = obj1, attr = attr5 )
    createAttr( obj = obj1, attr = attr6, k = 1, dv = 0.5 )
    #
    obj1_CtGrp = cmds.listRelatives( obj1, p = True )[0]
    obj1_TopGrp = cmds.listRelatives( obj1_CtGrp, p = True )[0]
    obj2_CtGrp = cmds.listRelatives( obj2, p = True )[0]
    obj2_TopGrp = cmds.listRelatives( obj2_CtGrp, p = True )[0]
    distance( obj1 = obj1_TopGrp, obj2 = obj2_TopGrp, attrObj = obj1 + '.' + attr2 )
    #
    sub = cmds.shadingNode( 'plusMinusAverage' , au = True, n = name + '_' + obj1 + '_' + obj2 + '_sub' )
    cmds.setAttr( sub + '.operation', 2 )  # subtract
    cmds.connectAttr( obj1 + '.' + attr1, sub + '.input1D[0]' )
    cmds.connectAttr( obj1 + '.' + attr2, sub + '.input1D[1]' )
    # slide
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '_' + obj1 + '_' + obj2 + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( obj1 + '.' + attr4, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', obj1 + '.' + attr3 )
    #
    cmds.connectAttr( obj1 + '.' + attr3, obj1_CtGrp + '.translateZ' )  # final output
    # bulge
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '_' + obj1 + '_' + obj2 + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( obj1 + '.' + attr6, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', obj1 + '.' + attr5 )
    #
    cmds.connectAttr( obj1 + '.' + attr5, obj1_CtGrp + '.translateY' )  # final output
    # neutralize offset
    neutralize = cmds.getAttr( obj1 + '.' + attr2 )
    cmds.setAttr( obj1 + '.' + attr1, neutralize )


def dynamic():
    '''
    add dynamic jiggle to cv
    '''
    pass


def __________________UTIL():
    pass


def createAttr( obj = '', attr = '', k = False, dv = 0.0 ):
    '''
    creates attr and applies expression
    '''
    cmds.addAttr( obj, longName = attr, attributeType = 'float', k = k, dv = dv )
    cmds.setAttr( obj + "." + attr, cb = True )
    cmds.setAttr( obj + "." + attr, k = k )


def createDisNode( name = '' ):
    dis = cmds.createNode( 'distanceBetween', name = name + '_dis' )
    return dis


def distance( obj1 = '', obj2 = '', attrObj = '' ):
    '''
    assembles distance relationship
    attrObj should include attribute name
    '''
    # connect to distance node
    disNode = createDisNode( name = 'dstnc___' + obj1 + '___' + obj2 )
    cmds.connectAttr( obj1 + '.worldMatrix[0]', disNode + '.inMatrix1' )
    cmds.connectAttr( obj2 + '.worldMatrix[0]', disNode + '.inMatrix2' )
    # feed distance attrs
    cmds.connectAttr( disNode + '.distance', attrObj )

