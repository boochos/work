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
cp = web.mod( 'clipPickle_lib' )


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            # print( what)
            pass


def __________________BUILD():
    pass


def createPlane( patchesU = 1, patchesV = 8, length = 8, width = 4, degree = 3, axis = [ 0, 1, 0 ], X = 1, hideRows = False, mirrorControls = True ):
    '''
    degree = 1 or 3
    ---
    CANT USE DEGREE 1 (LINEAR) WITH MUSCLE, HAS SEAM, MUSCLE RIPS IT APART ... RETAINER HAS TO BE (CUBIC) IF INFLUENCED BY MUSCLE, 
    CANT MOVE 2ND AND 2ND LAST ROWS, MUSCLE SYSTEM DOESNT LIKE IT.
    ---
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
    logType( typ = 'plane' )
    MasterCt = PreBuild[5]
    # place.cleanUp( obj, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    #
    if axis == [ 0, 1, 0 ]:
        cv_shape = 'diamondYup_ctrl'
        row_shape = 'rectangleWideZup_ctrl'
        row_direction = 2  # y is up
        codeScale = X * 1.5
        cmds.select( MasterCt[2] )
        ui.importCurveShape( name = row_shape, codeScale = codeScale )
        cmds.select( MasterCt[3] )
        ui.importCurveShape( name = row_shape, codeScale = codeScale * 0.9 )
    else:  # assume Z direction [ 0, 0, 1 ]
        cv_shape = 'diamondZup_ctrl'
        row_shape = 'rectangleWideYup_ctrl'
        row_direction = 1  # z is up
        codeScale = X * 1.5
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
    length_ratio = length / width
    #
    if degree == 1 or degree == 3:
        geo = cmds.nurbsPlane( name = name, axis = axis, patchesU = patchesU, patchesV = patchesV, degree = degree, lengthRatio = length_ratio, width = width )
        print( geo )
        place.cleanUp( geo[0], Body = True )
        if degree == 3:
            if hideRows:
                rows = patchesV + 3
            else:
                rows = patchesV + 1
                cmds.setAttr( geo[1] + '.patchesV', patchesV - 2 )
        else:
            rows = patchesV + 1
        print( rows )
        # rows = spans + 1
        cvs = patchesU + 3
        print( cvs )
        '''
        rotation = -90
        rotation_inc = 360 / cvs  # each cv gets rotation to, for bulge effect
        if degree == 3:
            rotation = -90 + rotation_inc  # / cvs * -1
        '''

        # orient cv controls, figure out split
        mid_cv = 0
        h_cvs = cvs / 2
        r_cvs = ( round( h_cvs ) )
        print( h_cvs, r_cvs )
        if r_cvs == h_cvs:
            print( 'no mid cv' )
        else:
            print( 'mid cv' )
            mid_cv = r_cvs + 1
        # create parts

        clr = 0

        for r in range( rows ):
            #
            row_master = False
            cv_controls = []
            for c in range( cvs ):
                print( 'c ', c )
                # cv name
                cv = name + '.cv[' + str( c ) + '][' + str( r ) + ']'
                cv_name = cv.replace( '.', '_' ).replace( '][', '_' ).replace( '[', '_' ).replace( ']', '' ).split( name + '_' )[1]
                # cv control
                pos = cmds.xform( cv, t = True, ws = True, q = True )
                cv_Ct = place.Controller2( cv_name, geo[0], False, cv_shape, X * 0.3, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                place.cleanUp( cv_Ct[0], Ctrl = True )
                insertCvPivotControl( obj = cv_Ct, X = X * 0.2, colorName = colors[clr] )
                cmds.xform( cv_Ct[0], ws = True, t = pos )
                #
                if c <= r_cvs - 1:
                    cmds.setAttr( cv_Ct[0] + '.rotateZ' , 90 )
                    cmds.setAttr( cv_Ct[1] + '.rotateZ' , -90 )
                #
                if  mid_cv and c > mid_cv - 1:
                    cmds.setAttr( cv_Ct[0] + '.rotateZ' , -90 )
                    if mirrorControls:
                        cmds.setAttr( cv_Ct[1] + '.rotateZ' , -90 )
                        scaleInverse( cv_Ct[1], 'scaleY' )
                    else:
                        cmds.setAttr( cv_Ct[1] + '.rotateZ' , 90 )
                #
                if not mid_cv and c > r_cvs - 1:
                    cmds.setAttr( cv_Ct[0] + '.rotateZ' , -90 )
                    if mirrorControls:
                        cmds.setAttr( cv_Ct[1] + '.rotateZ' , -90 )
                        scaleInverse( cv_Ct[1], 'scaleY' )
                    else:
                        cmds.setAttr( cv_Ct[1] + '.rotateZ' , 90 )

                '''
                cmds.setAttr( cv_Ct[0] + '.rotateZ' , rotation )  # doesnt account for up axis
                '''
                cv_controls.append( cv_Ct )
                '''
                rotation = rotation - rotation_inc
                '''
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
                    row_Ct = place.Controller2( row_name, geo[0], False, row_shape, X * 2.8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                    place.scaleUnlock( row_Ct[2], sx = True, sy = True, sz = False )
                    place.cleanUp( row_Ct[0], Ctrl = True )
                    insertTwistPivotControl( obj = row_Ct, X = X * 2, colorName = colors[clr] )
                    if row_direction == 1:  # reverse of cylinder
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
        if degree == 3 and hideRows:  # could do this always to keep consistent if behaviour is bad even in linear(degree 1)
            degree3( row_controls, row_cv_controls )
            row_controls.pop( 1 )  # remove second
            row_controls.pop( -2 )  # remove second last
            row_cv_controls.pop( 1 )  # remove cv second
            row_cv_controls.pop( -2 )  # remove cv second last
        #
        # slideBulgeAll( row_cv_controls )
        slideBulgeAnchorsAll( row_cv_controls, plane = True )  # need better deafults for middle row
        twist( row_controls )
        # scale()
    else:
        print( 'degrees has to be 1 or 3' )


def create( spans = 1, sections = 8, degree = 3, axis = [ 0, 0, 1 ], X = 1, hideRows = False ):
    '''
    degree = 1 or 3
    ---
    CANT USE DEGREE 1 (LINEAR) WITH MUSCLE, HAS SEAM, MUSCLE RIPS IT APART ... RETAINER HAS TO BE (CUBIC) IF INFLUENCED BY MUSCLE, 
    CANT MOVE 2ND AND 2ND LAST ROWS, MUSCLE SYSTEM DOESNT LIKE IT.
    ---
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
    logType( typ = 'cylinder' )
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
        print( geo )
        place.cleanUp( geo[0], Body = True )
        if degree == 3:
            if hideRows:
                rows = spans + 3
            else:
                rows = spans + 1
                cmds.setAttr( geo[1] + '.spans', spans - 2 )
        else:
            rows = spans + 1
        # rows = spans + 1
        cvs = sections

        rotation = -90
        rotation_inc = 360 / cvs  # each cv gets rotation to, for bulge effect
        if degree == 3:
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
                cv_Ct = place.Controller2( cv_name, geo[0], False, cv_shape, X * 0.3, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
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
        if degree == 3 and hideRows:  # could do this always to keep consistent if behaviour is bad even in linear(degree 1)
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


def slideBulgeAnchors( master = '', slave = '', slide_weight = 0.5, bulge_weight = 0.5, feedbackAttrs = False ):
    '''
    add sliding(translate along geo) based on distance from anchor cvs, or rotation of rows
    min max distance
    '''
    #
    slave_CtGrp = cmds.listRelatives( slave, p = True )[0]
    slave_TopGrp = cmds.listRelatives( slave_CtGrp, p = True )[0]
    master_CtGrp = cmds.listRelatives( master, p = True )[0]
    # attr names
    suffix = anchorAttr1()  # test for pre-existing, iterate
    limits = True
    # qualify suffix
    if cmds.attributeQuery( anchorPrefix() + suffix, node = slave, ex = 1 ):
        suffix = anchorAttr2()
        limits = False
    # cv specific attrs
    attr_sfx = suffix
    attr_ntrlz_ds = 'neutralize_distance_' + suffix
    attr_ds_sfx = 'distance_' + suffix
    op1 = 'slide'
    attr_sld_ds_sfx = op1 + '_distance_' + suffix
    attr_sld_w_sfx = op1 + '_w_' + suffix
    op2 = 'bulge'
    attr_blg_ds_sfx = op2 + '_distance_' + suffix
    attr_blg_w_sfx = op2 + '_w_' + suffix
    attr_sld_sfx = op1 + '_onOff_' + suffix  # add math
    attr_blg_sfx = op2 + '_onOff_' + suffix  # add math
    # limits attrs
    mintzl = 'minTransZLimit'
    maxtzl = 'maxTransZLimit'
    mintyl = 'minTransYLimit'
    maxtyl = 'maxTransYLimit'
    attr_sld_min_sfx = op1 + '_min'
    attr_sld_max_sfx = op1 + '_max'
    attr_blg_min_sfx = op2 + '_min'
    attr_blg_max_sfx = op2 + '_max'
    slide_raw = 'slide_current'
    bulge_raw = 'bulge_current'
    # inverse
    force_bulge_direction = 'match'
    bulge_direction_qualifier = 'qualifier'  # hijack condition node, use min/max so only "greater than", "less than" are available

    # add attrs
    if limits:
        misc.optEnum( slave, attr = 'slide_soft', enum = 'LIMITS' )
        # min
        cmds.transformLimits( slave_CtGrp, tz = [-100, 100], etz = [1, 1] )
        place.hijackAttrs( slave_CtGrp, slave, mintzl, attr_sld_min_sfx, set = True, default = -0.5, force = True )
        # raw
        createAttr( obj = slave, attr = slide_raw )
        cmds.connectAttr( slave_CtGrp + '.translateZ', slave + '.' + slide_raw )
        cmds.setAttr( slave + '.' + slide_raw, lock = 1 )
        # max
        cmds.transformLimits( slave_CtGrp, tz = [-100, 100], etz = [1, 1] )
        place.hijackAttrs( slave_CtGrp, slave, maxtzl, attr_sld_max_sfx, set = True, default = 0.5, force = True )
        misc.optEnum( slave, attr = 'bulge_soft', enum = 'LIMITS' )
        # min
        cmds.transformLimits( slave_CtGrp, ty = [-100, 100], ety = [1, 1] )
        place.hijackAttrs( slave_CtGrp, slave, mintyl, attr_blg_min_sfx, set = True, default = -0.5, force = True )
        # raw
        createAttr( obj = slave, attr = bulge_raw )
        cmds.connectAttr( slave_CtGrp + '.translateY', slave + '.' + bulge_raw )
        cmds.setAttr( slave + '.' + bulge_raw, lock = 1 )
        # max
        cmds.transformLimits( slave_CtGrp, ty = [-100, 100], ety = [1, 1] )
        place.hijackAttrs( slave_CtGrp, slave, maxtyl, attr_blg_max_sfx, set = True, default = 0.5, force = True )
    #
    misc.optEnum( slave, attr = anchorPrefix() + attr_sfx, enum = 'CONTROL' )
    createAttr( obj = slave, attr = attr_ds_sfx, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr_ntrlz_ds, cb = feedbackAttrs )
    misc.optEnum( slave, attr = op1 + '_' + suffix, enum = master, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr_sld_sfx, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr_sld_ds_sfx, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr_sld_w_sfx, k = 1, dv = slide_weight )
    misc.optEnum( slave, attr = op2 + '_' + suffix, enum = master, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr_blg_sfx, dv = 1, typ = 'bool' )
    createAttr( obj = slave, attr = attr_blg_ds_sfx, cb = feedbackAttrs )
    createAttr( obj = slave, attr = attr_blg_w_sfx, k = 1, dv = bulge_weight )
    #
    distance( name = '', obj1 = master_CtGrp, obj2 = slave_TopGrp, attrObj = slave + '.' + attr_ds_sfx )  # (Ct --> Top)  <-- (causes cycle)

    # return
    #
    sub = cmds.shadingNode( 'plusMinusAverage' , au = True, n = slave + '___' + master + '_sub' )
    cmds.setAttr( sub + '.operation', 2 )  # subtract
    cmds.connectAttr( slave + '.' + attr_ntrlz_ds, sub + '.input1D[0]' )
    cmds.connectAttr( slave + '.' + attr_ds_sfx, sub + '.input1D[1]' )
    # return
    # slide
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '___' + slave + '___' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr_sld_w_sfx, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr_sld_ds_sfx )
    #
    mlt2 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op1 + '___' + slave + '___' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr_sld_ds_sfx, mlt2 + '.input1' )
    cmds.connectAttr( slave + '.' + attr_sld_sfx, mlt2 + '.input2' )
    # return
    if suffix != 'anchor1':
        place.smartAttrBlend( master = mlt2, slave = slave_CtGrp, masterAttr = 'output', slaveAttr = 'translateZ', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False )
        pass
    else:
        cmds.connectAttr( mlt2 + '.output', slave_CtGrp + '.translateZ' )  # final output
    # return
    # bulge
    mlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '___' + slave + '___' + master + '_mlt' )
    cmds.connectAttr( sub + '.output1D', mlt + '.input1' )
    cmds.connectAttr( slave + '.' + attr_blg_w_sfx, mlt + '.input2' )
    cmds.connectAttr( mlt + '.output', slave + '.' + attr_blg_ds_sfx )
    #
    mlt3 = cmds.shadingNode( 'multDoubleLinear', au = True, n = op2 + '___' + slave + '___' + master + '_enable_mlt' )
    cmds.connectAttr( slave + '.' + attr_blg_ds_sfx, mlt3 + '.input1' )
    cmds.connectAttr( slave + '.' + attr_blg_sfx, mlt3 + '.input2' )
    if suffix != 'anchor1':
        smart_nodes = place.smartAttrBlend( master = mlt3, slave = slave_CtGrp, masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False )
        pass
    else:
        cmds.connectAttr( mlt3 + '.output', slave_CtGrp + '.translateY' )  # final output
    # neutralize offset
    neutralize = cmds.getAttr( slave + '.' + attr_ds_sfx )
    cmds.setAttr( slave + '.' + attr_ntrlz_ds, neutralize )
    #
    cmds.setAttr( slave + '.' + attr_ds_sfx, lock = 1 )
    cmds.setAttr( slave + '.' + attr_sld_ds_sfx, lock = 1 )
    cmds.setAttr( slave + '.' + attr_blg_ds_sfx, lock = 1 )
    # ease limits
    if not limits:
        # slide
        name = op1
        masterAttr = None
        slaveAttr = slave_CtGrp + '.translateZ'
        con = cmds.listConnections( slaveAttr, s = 1, d = 0, skipConversionNodes = True, plugs = True )
        maxAttr = slave + '.' + attr_sld_max_sfx.replace( anchorAttr2(), anchorAttr1() )
        minAttr = slave + '.' + attr_sld_min_sfx.replace( anchorAttr2(), anchorAttr1() )
        if con:
            masterAttr = con[0]
            easeIntoLimits( name = name, masterAttr = masterAttr, slaveAttr = slaveAttr , maxAttr = maxAttr, minAttr = minAttr )
        # bulge
        name = op2
        masterAttr = None
        slaveAttr = slave_CtGrp + '.translateY'
        con = cmds.listConnections( slaveAttr, s = 1, d = 0, skipConversionNodes = True, plugs = True )
        maxAttr = slave + '.' + attr_blg_max_sfx.replace( anchorAttr2(), anchorAttr1() )
        minAttr = slave + '.' + attr_blg_min_sfx.replace( anchorAttr2(), anchorAttr1() )
        if con:
            masterAttr = con[0]
            easeIntoLimits( name = name, masterAttr = masterAttr, slaveAttr = slaveAttr , maxAttr = maxAttr, minAttr = minAttr )
    # force bulge direction
    if not limits:
        smart_blend_result_node = smart_nodes[-1]
        # make attr
        misc.optEnum( slave, attr = 'bulgeDirection', enum = 'CONTROL' )
        createAttr( obj = slave, attr = force_bulge_direction, typ = 'bool', cb = True )
        # createAttr( obj = slave, attr = bulge_direction_qualifier, typ = 'bool', cb = True )

        # make math nodes
        rawInvrs = cmds.shadingNode( 'multDoubleLinear', au = True, n = slave + '_matchDirectionMath' )
        cmds.connectAttr( smart_blend_result_node + '.output', rawInvrs + '.input1' )
        cmds.setAttr( rawInvrs + '.input2', -1 )
        #
        cndtnMath = cmds.shadingNode( 'condition', au = True, n = slave + '_matchDirectionCond' )
        cmds.connectAttr( smart_blend_result_node + '.output', cndtnMath + '.firstTerm' )  # raw, unforced value from smart blend node
        cmds.setAttr( cndtnMath + '.secondTerm', 0 )
        cmds.setAttr( cndtnMath + '.operation', 2 )  # greater than
        cmds.connectAttr( smart_blend_result_node + '.output', cndtnMath + '.colorIfFalseR' )
        cmds.connectAttr( rawInvrs + '.output', cndtnMath + '.colorIfTrueR' )
        place.hijackAttrs( cndtnMath, slave, 'operation', bulge_direction_qualifier, set = True, default = 2, force = True )

        # pipe through on / off
        cndtnOnOff = cmds.shadingNode( 'condition', au = True, n = slave + '_matchDirectionOnOff' )
        cmds.connectAttr( slave + '.' + force_bulge_direction, cndtnOnOff + '.firstTerm' )
        cmds.setAttr( cndtnOnOff + '.secondTerm', 1 )
        cmds.setAttr( cndtnOnOff + '.operation', 0 )  # equal
        cmds.connectAttr( smart_blend_result_node + '.output', cndtnOnOff + '.colorIfFalseR' )  # raw
        cmds.connectAttr( cndtnMath + '.outColorR', cndtnOnOff + '.colorIfTrueR' )  # raw, unforced value from smart blend node outColorR
        #
        cmds.connectAttr( cndtnOnOff + '.outColorR', slave_CtGrp + '.translateY', f = True )  # slave_CtGrp


def slideBulgeAnchorsAll( row_cv_controls = [], plane = False ):
    '''
    connect cv rows with slide Bulge effect
    '''
    # start
    for r in range( len( row_cv_controls ) - 2 ):  # r = row iterator
        anchor1_cvs = row_cv_controls[0]  # locking to start and end rows, to get around cycle
        slave_cvs = row_cv_controls[r + 1]
        anchor2_cvs = row_cv_controls[-1]
        for c in range( len( anchor1_cvs ) ):
            if plane:
                slideBulgeAnchors( master = anchor1_cvs[c][2], slave = slave_cvs[c][2], slide_weight = -0.5, bulge_weight = 0.5 )
                slideBulgeAnchors( master = anchor2_cvs[c][2], slave = slave_cvs[c][2], slide_weight = 0.5, bulge_weight = 0.5 )
            else:
                slideBulgeAnchors( master = anchor1_cvs[c][2], slave = slave_cvs[c][2], slide_weight = 0.5, bulge_weight = 0.5 )
                slideBulgeAnchors( master = anchor2_cvs[c][2], slave = slave_cvs[c][2], slide_weight = -0.5, bulge_weight = 0.5 )


def dynamic():
    '''
    turn on option in controller class
    '''
    pass


def muslce():
    '''
    make retainer a muscle
    '''
    pass


def __________________STRINGS():
    pass


def anchorAttr1():
    return '_1'


def anchorAttr2():
    return '_2'


def anchorPrefix():
    return 'CV'


def typeAttr():
    return 'type'


def defaultDir():
    return 'retainerPoses'


def rigTopNodeName():
    return '___UTIL___'


def __________________UTIL():
    pass


def scaleInverse( obj = '', axis = 'scaleY' ):
    '''
    assumes axis is locked
    unlock and set to -1.0
    lock
    '''
    cmds.setAttr( obj + '.' + axis, lock = False )
    cmds.setAttr( obj + '.' + axis, -1.0 )
    cmds.setAttr( obj + '.' + axis, lock = True )


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


def easeIntoLimits( name = '', masterAttr = '', slaveAttr = '', maxAttr = '', minAttr = '' ):
    '''
    "attr" variables assume "nodeName.attr" format
    assumes given node variables already exist
    '''
    place.attr_easeInto_Limits( name = name, masterAttr = masterAttr, slaveAttr = slaveAttr, maxAttr = maxAttr, minAttr = minAttr )


def createAttr( obj = '', attr = '', k = False, l = False, dv = 0.0, typ = 'float', cb = True ):
    '''
    creates attr
    '''
    # print( attr )
    cmds.addAttr( obj, longName = attr, attributeType = typ, k = k, dv = dv )
    cmds.setAttr( obj + "." + attr, cb = cb )
    cmds.setAttr( obj + "." + attr, k = k )
    cmds.setAttr( obj + "." + attr, lock = l )


def createDisNode( name = '' ):
    '''
    distance node
    '''
    dis = cmds.createNode( 'distanceBetween', name = name + '___dis' )
    return dis


def insertCvPivotControl( obj = [], X = 1, colorName = '' ):
    '''
    obj = expected to be full controller hierarchy
    creates a control, used to place a row control, so CtGrp twists from the correct position. 
    this control should be used to place the row
    '''
    #
    ctrl = place.circle( name = obj[2] + '_cvPvt', obj = obj[2], shape = 'loc_ctrl', size = X, colorName = colorName )[0]
    attr = 'Pivot_Vis'
    place.addAttribute( obj[2], attr, 1, 1, True, 'long' )
    cmds.connectAttr( obj[2] + '.' + attr, ctrl + 'Shape' + '.visibility' )
    place.scaleLock( ctrl, True )
    cmds.setAttr( ctrl + '.visibility', l = True, cb = False )
    #
    cmds.parent( ctrl, obj[0] )
    cmds.parent( obj[1], ctrl )


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


def findParent( obj = '', find = '___CONTROLS' ):
    '''
    find 1st parent in hierarchy
    '''
    limit = 50
    i = 0
    ns = ''
    if ':' in obj:
        find = obj.split( ':' )[0] + ':' + find

    if obj:
        while i < limit:
            parent = cmds.listRelatives( obj, p = True )
            if parent:
                print( parent , find )
                obj = parent[0]
                if obj == find:
                    return obj
            i = i + 1
        # print( 'nothing', obj )
        return None
    else:
        print( 'needs an object' )


def logType( typ = '' ):
    '''
    
    '''
    misc.optEnum( rigTopNodeName(), attr = typeAttr(), enum = typ )


def defaultPath():
    '''
    
    '''
    path = cmds.file( query = True, sn = True )
    if path:
        # print( path )
        path = path.rsplit( '/', 1 )[0]
        if 'scenes' in path:
            path = os.path.join( path, defaultDir() )
            if os.path.isdir( path ):
                return path
            else:
                os.mkdir( path )
                return path
        else:
            print( path )
            message( 'missing string in path: "scenes"' )
            return None
    message( 'save scene' )


def versionPath():
    '''
    create version for each export
    import should pickup latest
    '''
    pass


def getControls():
    '''
    should find every control in asset
    including offset control
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    if sel:
        s = sel[0]
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
                            if cmds.attributeQuery( 'Offset_Vis', node = c, ex = 1 ):
                                controls.append( c )
                            offset = cmds.listRelatives( item, c = True )
                            for o in offset:
                                if '_offset' in o:
                                    controls.append( o )
                            else:
                                # print( c )
                                pass
                    else:
                        # print( 'no ctGrp', item )
                        pass
        else:
            # print( 'no controls' )
            pass
    message( 'select a control' )
    return controls


def getRetainerShape():
    '''
    
    '''
    sel = cmds.ls( sl = 1 )
    if sel:
        sel = sel[0]
        parent = findParent( sel , find = rigTopNodeName() )
        if parent:
            result = cmds.getAttr( parent + '.' + typeAttr() )
            return result


def __________________MANAGE():
    pass


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
                            if cmds.attributeQuery( anchorPrefix() + anchorAttr1(), node = c, ex = 1 ):
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
            dis = cmds.getAttr( c + '.distance_' + anchorAttr1() )
            cmds.setAttr( c + '.neutralize_distance_' + anchorAttr1(), dis )
            dis = cmds.getAttr( c + '.distance_' + anchorAttr2() )
            cmds.setAttr( c + '.neutralize_distance_' + anchorAttr2(), dis )
    else:
        print( 'no controls' )


def neutralizeRows():
    '''
    find all row controls with proper attrs, run script to reset parent nodes (pivot offset above Ct group), 
    ie, match position of row control, reset row control to zero
    '''
    pass


def neutralizeCVs():
    '''
    neutralize cv positions, may need to add extra control, same as rows have, 'pivot'
    '''
    pass


def disable( state = False ):
    '''
    disable all slide / bulge translations
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


def setDrivenKey():
    '''
    add set driven key functionality, per cv
    '''
    pass


def geoAttach():
    '''
    temporary
    attach to geo for setup position
    geo constraint
    use normal or tangent constraint, one of these should keep control oriented to geo plane ?
    '''
    pass


def geoDetach():
    '''
    temporary
    detach from geo
    delete constraints (geo, normal, tangent)
    '''
    pass


def mirror():
    '''
    mirror controls, feed center cv for mirror plane
    '''
    pass


def mirrorAB():
    '''
    take one retainer shape, mirror position of all controls in world space to opposite side.
    '''
    pass


def __________________PORT():
    pass


def importDrivenKey():
    '''
    add set driven key functionality, per cv
    '''
    pass


def exportDrivenKey():
    '''
    add set driven key functionality, per cv
    '''
    pass


def exportPose():
    '''
    use scene path as default location to save,
    export retainer pose
    
    NEED TO CREATE VERSION FOR EACH EXPORT AND NAMING SYSTEM TO BYPASS MULTIPLE EXPORTS OF SAME SHAPE RIG
    TRACK CLASHING RIGS, WITH DIF AMOUNT OF CVS, ONLY IMPORT TO COMPATIBLE RIGS
    
    '''
    sel = cmds.ls( sl = 1 )
    # export
    name = ''
    if name:
        if sel:
            version = '.' + self.cmdCreateVersionNumber()
            cp.clipSave( name = name + version, poseOnly = True )
            message( 'Set   ' + name + '   exported to   ' + path )
        else:
            message( 'Select some objects. Export aborted.', maya = True, warning = True )
    else:
        message( 'Provided a name. Export aborted.', maya = True, warning = True )


def importPose():
    '''
    import pose, use scene path to find location
    '''
    pass


def importConstraints():
    '''
    only raw constraints, un-rigged
    '''
    pass


def exportConstraints():
    '''
    
    '''
    pass
