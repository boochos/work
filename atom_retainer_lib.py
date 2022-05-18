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


def create( spans = 1, sections = 8, degree = 3, axis = [ 0, 0, 1 ], X = 1, twist = True ):
    '''
    degree = 1 or 3
    create rigged nurbs object
    options for twist
    options for sliding based distance 
    '''
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
    cyl = None
    colors = [ 'lightBlue', 'pink', 'hotPink', 'purple']
    cv_controls = []
    row_controls = []
    joints = []
    #
    if degree == 1 or degree == 3:
        cyl = cmds.cylinder( name = name, axis = axis, spans = spans, sections = sections, degree = degree )
        place.cleanUp( cyl[0], Body = True )
        rows = spans + 1
        if degree == 3:
            rows = rows * 2
        cvs = sections + 1  # last cv matches first cv location
        # create parts
        clr = 0
        for r in range( rows ):
            #
            row_master = False
            row_cv_controls = []
            for c in range( cvs ):
                # cv name
                cv = name + '.cv[' + str( r ) + '][' + str( c ) + ']'
                cv_name = cv.replace( '.', '_' ).replace( '][', '_' ).replace( '[', '_' ).replace( ']', '' ).split( name + '_' )[1]
                # cv control
                pos = cmds.xform( cv, t = True, ws = True, q = True )
                cv_Ct = place.Controller2( cv_name, cyl[0], False, cv_shape, X * 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                place.cleanUp( cv_Ct[0], Ctrl = True )
                cmds.xform( cv_Ct[0], ws = True, t = pos )
                cv_controls.append( cv_Ct )
                row_cv_controls.append( cv_Ct )
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
                    row_Ct = place.Controller2( row_name, cyl[0], False, row_shape, X * 5.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colors[clr] ).result
                    place.cleanUp( row_Ct[0], Ctrl = True )
                    if row_direction == 1:
                        cmds.xform( row_Ct[0], ws = True, t = [ 0, pos[row_direction], 0 ] )
                    else:
                        cmds.xform( row_Ct[0], ws = True, t = [ 0, 0, pos[row_direction] ] )
                    cmds.parentConstraint( MasterCt[4], row_Ct[0], mo = True )
                    row_controls.append( row_Ct )
                    row_master = True
            for cv_control in row_cv_controls:
                cmds.parentConstraint( row_Ct[4], cv_control[0], mo = True )
            # color loop
            clr = clr + 1
            if clr > len( colors ) - 1:
                clr = 0
        # skin nurbs object
        cmds.select( joints )
        cmds.select( cyl[0], add = True )
        sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
        cmds.setAttr( sknClstr + '.skinningMethod', 1 )
        # twist
        if twist:
            print( 'add twist' )

        # scale
        mstr = 'master'
        uni = 'uniformScale'
        scl = ['.scaleX', '.scaleY', '.scaleZ']
        #
        misc.addAttribute( [mstr], [uni], 0.01, 100.0, True, 'float' )
        cmds.setAttr( mstr + '.' + uni, 1.0 )
        # misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
        scl = ['.scaleX', '.scaleY', '.scaleZ']
        misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
        for s in scl:
            cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
        misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
        for s in scl:
            cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
            # cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush

    else:
        print( 'degrees has to be 1 or 3' )

