import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )


def CONTROLS():
    return '___CONTROLS'


def structure( name = 'panel' ):
    '''
    
    '''
    #
    PreBuild = place.rigPrebuild( Top = 4, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 10 )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    #
    place.rotationLock( MasterCt[2], lock = True )
    #
    sffx = 'Clstr'
    # cube
    cube = cmds.polyCube( name = name )
    # make unselectable
    cmds.setAttr( cube[0] + '.overrideEnabled', 1 )
    place.hijackAttrs( cube[0], MasterCt[2], 'overrideDisplayType', 'geoDisplay', set = False, default = 2, force = True )
    cmds.setAttr( MasterCt[2] + '.geoDisplay', cb = True )
    # print( cube, GEO )
    cmds.parent( cube[0], GEO[0] )
    # clusters
    clstr_grp = cmds.group( name = name + '_' + sffx + '_Grp', em = True )
    cmds.setAttr( clstr_grp + '.visibility', 0 )
    cmds.parentConstraint( MasterCt[4], clstr_grp, mo = True )
    clusters = place.clstrOnVrts( cube[0], clstrSuffix = name )
    # offset, reverse equivalent to pixel
    #
    cmds.select( clusters )
    cmds.parent( clusters, clstr_grp )
    cmds.parent( clstr_grp, WORLD_SPACE )

    front = [
    name + '00Handle',
    name + '01Handle',
    name + '03Handle',
    name + '02Handle'
    ]
    back = [
    name + '04Handle',
    name + '07Handle',
    name + '06Handle',
    name + '05Handle'
    ]
    left = [
    name + '07Handle',
    name + '01Handle',
    name + '03Handle',
    name + '05Handle'
    ]
    right = [
    name + '04Handle',
    name + '00Handle',
    name + '06Handle',
    name + '02Handle'
    ]
    top = [
    name + '04Handle',
    name + '03Handle',
    name + '02Handle',
    name + '05Handle'
    ]
    bottom = [
    name + '07Handle',
    name + '00Handle',
    name + '01Handle',
    name + '06Handle'
    ]
    size = 0.5
    controls = []
    defaultNodes = []
    #
    zone = front
    name = 'front'
    position = place.averagePosition( zone )
    front_Ct = place.Controller2( name + '_ct', MasterCt[0], False, 'squareZup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( front_Ct )
    #
    place.rotationLock( front_Ct[2], lock = True )
    place.translationLock( front_Ct[2], lock = True )
    place.translationZLock( front_Ct[2], lock = False )
    cmds.setAttr( front_Ct[2] + '.tz', 0.5 )  # add offset on control
    #
    cmds.xform( front_Ct[0], ws = True, t = position )
    cmds.setAttr( front_Ct[0] + '.tz', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], front_Ct[0], mo = True )
    cmds.parent( front_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = front_Ct[2], slave = c, masterAttr = 'translateZ', slaveAttr = 'translateZ', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', -0.5 )
    #
    zone = back
    name = 'back'
    position = place.averagePosition( zone )
    back_Ct = place.Controller2( name + '_ct', zone[0], False, 'squareZup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( back_Ct )
    #
    place.rotationLock( back_Ct[2], lock = True )
    place.translationLock( back_Ct[2], lock = True )
    place.translationZLock( back_Ct[2], lock = False )
    cmds.setAttr( back_Ct[2] + '.tz', -0.5 )  # add offset on control
    #
    cmds.xform( back_Ct[0], ws = True, t = position )
    cmds.setAttr( back_Ct[0] + '.tz', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], back_Ct[0], mo = True )
    cmds.parent( back_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = back_Ct[2], slave = c, masterAttr = 'translateZ', slaveAttr = 'translateZ', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', 0.5 )
    #
    zone = left
    name = 'left'
    position = place.averagePosition( zone )
    left_Ct = place.Controller2( name + '_ct', zone[0], False, 'squareXup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( left_Ct )
    #
    place.rotationLock( left_Ct[2], lock = True )
    place.translationLock( left_Ct[2], lock = True )
    place.translationXLock( left_Ct[2], lock = False )
    cmds.setAttr( left_Ct[2] + '.tx', 0.5 )  # add offset on control
    #
    cmds.xform( left_Ct[0], ws = True, t = position )
    cmds.setAttr( left_Ct[0] + '.tx', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], left_Ct[0], mo = True )
    cmds.parent( left_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = left_Ct[2], slave = c, masterAttr = 'translateX', slaveAttr = 'translateX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', -0.5 )
    #
    zone = right
    name = 'right'
    position = place.averagePosition( zone )
    right_Ct = place.Controller2( name + '_ct', zone[0], False, 'squareXup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( right_Ct )
    #
    place.rotationLock( right_Ct[2], lock = True )
    place.translationLock( right_Ct[2], lock = True )
    place.translationXLock( right_Ct[2], lock = False )
    cmds.setAttr( right_Ct[2] + '.tx', -0.5 )  # add offset on control
    #
    cmds.xform( right_Ct[0], ws = True, t = position )
    cmds.setAttr( right_Ct[0] + '.tx', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], right_Ct[0], mo = True )
    cmds.parent( right_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = right_Ct[2], slave = c, masterAttr = 'translateX', slaveAttr = 'translateX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', 0.5 )
    #
    zone = top
    name = 'top'
    position = place.averagePosition( zone )
    top_Ct = place.Controller2( name + '_ct', zone[0], False, 'squareYup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( top_Ct )
    #
    place.rotationLock( top_Ct[2], lock = True )
    place.translationLock( top_Ct[2], lock = True )
    place.translationYLock( top_Ct[2], lock = False )
    cmds.setAttr( top_Ct[2] + '.ty', 0.5 )  # add offset on control
    #
    cmds.xform( top_Ct[0], ws = True, t = position )
    cmds.setAttr( top_Ct[0] + '.ty', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], top_Ct[0], mo = True )
    cmds.parent( top_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = top_Ct[2], slave = c, masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', -0.5 )
    #
    zone = bottom
    name = 'bottom'
    position = place.averagePosition( zone )
    bottom_Ct = place.Controller2( name + '_ct', zone[0], False, 'squareYup_ctrl', size, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    controls.append( bottom_Ct )
    #
    place.rotationLock( bottom_Ct[2], lock = True )
    place.translationLock( bottom_Ct[2], lock = True )
    place.translationYLock( bottom_Ct[2], lock = False )
    cmds.setAttr( bottom_Ct[2] + '.ty', -0.5 )  # add offset on control
    #
    cmds.xform( bottom_Ct[0], ws = True, t = position )
    cmds.setAttr( bottom_Ct[0] + '.ty', 0.0 )  # remove offset on top group
    cmds.parentConstraint( MasterCt[4], bottom_Ct[0], mo = True )
    cmds.parent( bottom_Ct[0], CONTROLS )
    for c in zone:
        defaultNode = place.smartAttrBlend( master = bottom_Ct[2], slave = c, masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False, blendAttrExisting = False, preserveDefault = True )[-1]
        cmds.setAttr( defaultNode + '.input1', 0.5 )
    # connect shapes
    offset = 0.5
    # front
    vrts = cmds.ls( '{}.cv[:]'.format( front_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if x > 0.1:
            defaultNodes = place.smartAttrBlend( master = left_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if x < 0.1:
            defaultNodes = place.smartAttrBlend( master = right_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if y > 0.1:
            defaultNodes = place.smartAttrBlend( master = top_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if y < 0.1:
            defaultNodes = place.smartAttrBlend( master = bottom_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # back
    vrts = cmds.ls( '{}.cv[:]'.format( back_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if x > 0.1:
            defaultNodes = place.smartAttrBlend( master = left_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if x < 0.1:
            defaultNodes = place.smartAttrBlend( master = right_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if y > 0.1:
            defaultNodes = place.smartAttrBlend( master = top_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if y < 0.1:
            defaultNodes = place.smartAttrBlend( master = bottom_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # left
    vrts = cmds.ls( '{}.cv[:]'.format( left_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if z > 0.1:
            defaultNodes = place.smartAttrBlend( master = front_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if z < 0.1:
            defaultNodes = place.smartAttrBlend( master = back_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if y > 0.1:
            defaultNodes = place.smartAttrBlend( master = top_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if y < 0.1:
            defaultNodes = place.smartAttrBlend( master = bottom_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # right
    vrts = cmds.ls( '{}.cv[:]'.format( right_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if z > 0.1:
            defaultNodes = place.smartAttrBlend( master = front_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if z < 0.1:
            defaultNodes = place.smartAttrBlend( master = back_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if y > 0.1:
            defaultNodes = place.smartAttrBlend( master = top_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if y < 0.1:
            defaultNodes = place.smartAttrBlend( master = bottom_Ct[2], slave = v, masterAttr = 'translateY', slaveAttr = 'yValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # bottom
    vrts = cmds.ls( '{}.cv[:]'.format( bottom_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if z > 0.1:
            defaultNodes = place.smartAttrBlend( master = front_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if z < 0.1:
            defaultNodes = place.smartAttrBlend( master = back_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if x > 0.1:
            defaultNodes = place.smartAttrBlend( master = left_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if x < 0.1:
            defaultNodes = place.smartAttrBlend( master = right_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # top
    vrts = cmds.ls( '{}.cv[:]'.format( top_Ct[2] ), fl = True )
    for v in vrts:
        pos = cmds.xform( v, ws = True, q = True, t = True )
        x = pos[0]
        y = pos[1]
        z = pos[2]
        if z > 0.1:
            defaultNodes = place.smartAttrBlend( master = front_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if z < 0.1:
            defaultNodes = place.smartAttrBlend( master = back_Ct[2], slave = v, masterAttr = 'translateZ', slaveAttr = 'zValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
        if x > 0.1:
            defaultNodes = place.smartAttrBlend( master = left_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( -offset ) )
        if x < 0.1:
            defaultNodes = place.smartAttrBlend( master = right_Ct[2], slave = v, masterAttr = 'translateX', slaveAttr = 'xValue', preserveDefault = True )
            val = cmds.getAttr( defaultNodes[-1] + '.input1' )
            cmds.setAttr( defaultNodes[-1] + '.input1', val + ( offset ) )
    # center controls, connect rotatePivots
    #
    for control in controls:
        name = control[2].split( '_' )[0]
        loc = place.loc( name + '_center', control[0] )[0]
        cmds.setAttr( loc + '.v', 0 )
        cmds.parent( loc, WORLD_SPACE )
        #
        if name == 'front':
            for c in front:
                cmds.pointConstraint( c, loc )
        if name == 'back':
            for c in back:
                cmds.pointConstraint( c, loc )
        if name == 'left':
            for c in left:
                cmds.pointConstraint( c, loc )
        if name == 'right':
            for c in right:
                cmds.pointConstraint( c, loc )
        if name == 'top':
            for c in top:
                cmds.pointConstraint( c, loc )
        if name == 'bottom':
            for c in bottom:
                cmds.pointConstraint( c, loc )
        #
        if name == 'front' or name == 'back':
            cmds.connectAttr( loc + '.tx', control[2] + '.rotatePivot.rotatePivotX' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'tx', slaveAttr = 'rotatePivot.rotatePivotX', reverse = True, preserveDefault = True )
            cmds.connectAttr( loc + '.ty', control[2] + '.rotatePivot.rotatePivotY' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'ty', slaveAttr = 'rotatePivot.rotatePivotY', reverse = True, preserveDefault = True )
        if name == 'left' or name == 'right':
            cmds.connectAttr( loc + '.ty', control[2] + '.rotatePivot.rotatePivotY' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'ty', slaveAttr = 'rotatePivot.rotatePivotY', reverse = True, preserveDefault = True )
            cmds.connectAttr( loc + '.tz', control[2] + '.rotatePivot.rotatePivotZ' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'tz', slaveAttr = 'rotatePivot.rotatePivotZ', reverse = True, preserveDefault = True )
        if name == 'top' or name == 'bottom':
            cmds.connectAttr( loc + '.tx', control[2] + '.rotatePivot.rotatePivotX' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'tx', slaveAttr = 'rotatePivot.rotatePivotX', reverse = True, preserveDefault = True )
            cmds.connectAttr( loc + '.tz', control[2] + '.rotatePivot.rotatePivotZ' )
            place.smartAttrBlend( master = MasterCt[2], slave = control[2], masterAttr = 'tz', slaveAttr = 'rotatePivot.rotatePivotZ', reverse = True, preserveDefault = True )

    # pose, square foot from origin
    cmds.setAttr( left_Ct[2] + '.tx', 1 )
    cmds.setAttr( top_Ct[2] + '.ty', 1 )
    cmds.setAttr( front_Ct[2] + '.tz', 1 )

    cmds.setAttr( right_Ct[2] + '.tx', 0 )
    cmds.setAttr( bottom_Ct[2] + '.ty', 0 )
    cmds.setAttr( back_Ct[2] + '.tz', 0 )


def stairs( master = 'panel_rig:master', rise = 'panel_rig:top_ct.ty', run = 'panel_rig:front_ct.tz' ):
    '''
    
    '''
    minmax = [-10, 10]
    stairs = cmds.ls( sl = 1 )
    riseAttr = rise.split( '.' )[1]
    runAttr = run.split( '.' )[1]
    rise = rise.split( '.' )[0]
    run = run.split( '.' )[0]
    i = 1
    for s in stairs:
        cmds.setAttr( s + '.overrideEnabled', 1 )
        cmds.connectAttr( master + '.geoDisplay', s + '.overrideDisplayType' )
        place.smartAttrBlend( master = rise, slave = s, masterAttr = riseAttr, slaveAttr = riseAttr, blendAttrObj = s, blendAttrString = 'offsetY', blendWeight = i, reverse = False, minmax = minmax )
        place.smartAttrBlend( master = run, slave = s, masterAttr = runAttr, slaveAttr = runAttr, blendAttrObj = s, blendAttrString = 'offsetZ', blendWeight = i, reverse = False, minmax = minmax )
        i = i + 1


def spider( *args ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 12 )

    # lists for joints and controllers
    endJntL = [
    'legA_jnt_06_L',
    'legB_jnt_06_L',
    'legC_jnt_06_L',
    'legD_jnt_06_L'
    ]
    endJntR = [
    'legA_jnt_06_R',
    'legB_jnt_06_R',
    'legC_jnt_06_R',
    'legD_jnt_06_R'
    ]
    kneeJntL = [
    'legA_jnt_03_L',
    'legB_jnt_03_L',
    'legC_jnt_03_L',
    'legD_jnt_03_L'
    ]
    kneeJntR = [
    'legA_jnt_03_R',
    'legB_jnt_03_R',
    'legC_jnt_03_R',
    'legD_jnt_03_R'
    ]
    legJntL = [
    'legA_jnt_02_L',
    'legB_jnt_02_L',
    'legC_jnt_02_L',
    'legD_jnt_02_L'
    ]
    legJntR = [
    'legA_jnt_02_R',
    'legB_jnt_02_R',
    'legC_jnt_02_R',
    'legD_jnt_02_R'
    ]
    legParentsL = [
    'legA_jnt_01_L',
    'legB_jnt_01_L',
    'legC_jnt_01_L',
    'legD_jnt_01_L'
    ]
    legParentsR = [
    'legA_jnt_01_R',
    'legB_jnt_01_R',
    'legC_jnt_01_R',
    'legD_jnt_01_R'
    ]
    legAnklesL = [
    'legA_jnt_05_L',
    'legB_jnt_05_L',
    'legC_jnt_05_L',
    'legD_jnt_05_L'
    ]
    legAnklesR = [
    'legA_jnt_05_R',
    'legB_jnt_05_R',
    'legC_jnt_05_R',
    'legD_jnt_05_R'
    ]
    legJntL_flex = [
    'legA_jnt_03_L',
    'legB_jnt_03_L',
    'legC_jnt_03_L',
    'legD_jnt_03_L'
    ]
    legJntR_flex = [
    'legA_jnt_03_R',
    'legB_jnt_03_R',
    'legC_jnt_03_R',
    'legD_jnt_03_R'
    ]
    geo = 'geo_spider_body'
    cmds.deltaMush( geo, smoothingIterations = 4, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    # Create COG Controller and clean up
    cog = 'cog'
    cnt = place.Controller( cog, 'root_jnt', orient = False, shape = 'boxZup_ctrl', size = 2.0, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
    cmds.parentConstraint( cntCt[4], 'root_jnt', mo = True )

    # up vector for root legs
    up_Ct = place.Controller2( 'legRoot_up', 'root_jnt', True, 'diamond_ctrl', 0.5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.setAttr( up_Ct[0] + '.ty', 1 )
    cmds.setAttr( up_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( 'root_jnt', up_Ct[0], mo = True )
    cmds.parent( up_Ct[0], CONTROLS() )

    chest = 'thorax'
    chst = place.Controller( chest, 'thorax_jnt', orient = False, shape = 'facetZup_ctrl', size = 0.75, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    chstCt = chst.createController()
    place.translationLock( chstCt[2], True )
    place.cleanUp( chstCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( chstCt[4], 'thorax_jnt', mo = True )
    cmds.parentConstraint( cntCt[4], chstCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    pelvis = 'abdomen'
    plvs = place.Controller( pelvis, 'abdomen_jnt', orient = False, shape = 'squareZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    plvsCt = plvs.createController()
    place.translationLock( plvsCt[2], True )
    place.cleanUp( plvsCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( plvsCt[4], 'abdomen_jnt', mo = True )
    cmds.parentConstraint( cntCt[4], plvsCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    head = 'head'
    hd = place.Controller( head, 'head_jnt', orient = False, shape = 'facetZup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    hdCt = hd.createController()
    place.translationLock( hdCt[2], True )
    place.cleanUp( hdCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( hdCt[4], 'head_jnt', mo = True )
    cmds.parentConstraint( chstCt[4], hdCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    # return
    # LeftSide of Rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsL = []
    ankleAimL = []
    for jnt in endJntL:
        cnt = place.Controller( jnt.split( '_' )[0] + '_L', jnt, orient = False, shape = 'squareYup_ctrl', size = 0.5, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsL.append( cntCt[4] )
        # control for ankle aim
        name_Ct = place.Controller2( jnt.split( '_' )[0] + '_ankleAim_L', jnt, True, 'loc_ctrl', 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
        cmds.setAttr( name_Ct[0] + '.visibility', 0 )
        ankleAimL.append( name_Ct )
        cmds.orientConstraint( name_Ct[4], legAnklesL[i], mo = False )
        cmds.pointConstraint( cntCt[4], name_Ct[0], mo = False )
        place.cleanUp( name_Ct[0], Ctrl = True )
        #
        i = i + 1
    # print 'catch baseGrpsL:'
    # print baseGrpsL
    # return
    i = 0
    scktGrpsL = []
    baseUpL = []
    ankleUpL = []
    for jnt in legJntL:
        cnt = place.Controller( jnt.split( '_' )[0] + '_base_L', jnt, orient = False, shape = 'diamond_ctrl', size = 0.35, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        place.rotationLock( cntCt[2], True )
        # cmds.setAttr( cntCt[0] + '.rx', 0 )
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'root_jnt', cntCt[0], mo = True )
        # cmds.parentConstraint( cntCt[4], jnt, mo = True )
        # root leg aim
        cmds.aimConstraint( cntCt[4], legParentsL[i], wut = 'object', wuo = up_Ct[4], aim = ( 0, 0, 1 ), u = ( 0, 1, 0 ), mo = True )
        scktGrpsL.append( cntCt[4] )
        #
        # up vector for base legs
        upBase_Ct = place.Controller2( jnt.split( '_' )[0] + '_baseUp_L', jnt, True, 'diamond_ctrl', 0.1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
        cmds.setAttr( upBase_Ct[0] + '.ty', 1.25 )
        cmds.setAttr( upBase_Ct[0] + '.visibility', 0 )
        baseUpL.append( upBase_Ct )
        # cmds.parentConstraint( 'root_jnt', up_Ct[0], mo = True ) # constrains later
        cmds.parent( upBase_Ct[0], CONTROLS() )
        #
        # up vector for ankle
        upAnkle_Ct = place.Controller2( endJntL[i].split( '_' )[0] + '_ankleUp_L', endJntL[i], True, 'diamond_ctrl', 0.1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
        cmds.setAttr( upAnkle_Ct[0] + '.ty', 0.5 )
        cmds.setAttr( upAnkle_Ct[0] + '.visibility', 0 )
        ankleUpL.append( upAnkle_Ct )
        # cmds.parentConstraint( 'root_jnt', up_Ct[0], mo = True ) # constrains later
        cmds.parent( upAnkle_Ct[0], CONTROLS() )
        #
        i = i + 1
    # print 'catch scktGrpsL:'
    # print scktGrpsL
    # return
    # Rightside of rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsR = []
    ankleAimR = []
    for jnt in endJntR:
        cnt = place.Controller( jnt.split( '_' )[0] + '_R', jnt, orient = False, shape = 'squareYup_ctrl', size = 0.5, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsR.append( cntCt[4] )
        # control for ankle aim
        name_Ct = place.Controller2( jnt.split( '_' )[0] + '_ankleAim_R', jnt, True, 'loc_ctrl', 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
        cmds.setAttr( name_Ct[0] + '.visibility', 0 )
        ankleAimR.append( name_Ct )
        cmds.orientConstraint( name_Ct[4], legAnklesR[i], mo = False )
        cmds.pointConstraint( cntCt[4], name_Ct[0], mo = False )
        place.cleanUp( name_Ct[0], Ctrl = True )
        #
        i = i + 1
    # print 'catch baseGrpsR:'
    # print baseGrpsR

    i = 0
    scktGrpsR = []
    baseUpR = []
    ankleUpR = []
    for jnt in legJntR:
        cnt = place.Controller( jnt.split( '_' )[0] + '_base_R', jnt, orient = False, shape = 'diamond_ctrl', size = 0.35, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
        cntCt = cnt.createController()
        place.rotationLock( cntCt[2], True )
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'root_jnt', cntCt[0], mo = True )
        # cmds.parentConstraint( cntCt[4], jnt, mo = True )
        cmds.aimConstraint( cntCt[4], legParentsR[i], wut = 'object', wuo = up_Ct[4], aim = ( 0, 0, -1 ), u = ( 0, -1, 0 ), mo = True )
        scktGrpsR.append( cntCt[4] )
        #
        # up vector for base legs
        upBase_Ct = place.Controller2( jnt.split( '_' )[0] + '_baseUp_R', jnt, True, 'diamond_ctrl', 0.1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
        cmds.setAttr( upBase_Ct[0] + '.ty', 1.25 )
        cmds.setAttr( upBase_Ct[0] + '.visibility', 0 )
        baseUpR.append( upBase_Ct )
        # cmds.parentConstraint( 'root_jnt', up_Ct[0], mo = True ) # constrains later
        cmds.parent( upBase_Ct[0], CONTROLS() )
        #
        # up vector for ankle
        upAnkle_Ct = place.Controller2( endJntR[i].split( '_' )[0] + '_ankleUp_R', endJntR[i], True, 'diamond_ctrl', 0.1, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
        cmds.setAttr( upAnkle_Ct[0] + '.ty', 0.5 )
        cmds.setAttr( upAnkle_Ct[0] + '.visibility', 0 )
        ankleUpR.append( upAnkle_Ct )
        # cmds.parentConstraint( 'root_jnt', up_Ct[0], mo = True ) # constrains later
        cmds.parent( upAnkle_Ct[0], CONTROLS() )
        #
        i = i + 1
    # print 'catch scktGrpsR:'
    # print scktGrpsR

    # create PoleVectors, place and clean up into groups
    # return
    # LeftSide of Rig

    curveShapePath = 'C:\\Users\\sebas\\Documents\\maya\\controlShapes'

    i = 0
    pvLocListL = []
    for jnt in legJntL:
        # pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp', 'atom_bls_limbUp_radioButtonGrp', 1.0, 0.2, curveShapePath, True, flipVar = [0, 0, 0], X = 0.05 )
        pvLoc = appendage.create_3_joint_pv2( stJnt = jnt, endJnt = endJntL[i], prefix = jnt.split( '_jnt' )[0], suffix = 'L', distance_offset = 0.0, orient = True, color = 'blue', X = 0.1, midJnt = '' )
        pvLocListL.append( pvLoc )
        place.cleanUp( pvLoc[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # flex pv
    i = 0
    pvLocListL_flex = []
    for jnt in legJntL_flex:
        # pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp', 'atom_bls_limbUp_radioButtonGrp', 1.0, 0.2, curveShapePath, True, flipVar = [0, 0, 0], X = 0.05 )
        pvLoc = appendage.create_3_joint_pv2( stJnt = jnt, endJnt = legAnklesL[i], prefix = jnt.split( '_jnt' )[0] + '_flex', suffix = 'L', distance_offset = 0.0, orient = True, color = 'blue', X = 0.05, midJnt = '' )
        pvLocListL_flex.append( pvLoc )
        place.cleanUp( pvLoc[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # print 'catch pvLocListL:'
    # print pvLocListL
    # return
    # RightSide of Rig

    i = 0
    pvLocListR = []
    for jnt in legJntR:
        # pvLoc = appendage.create_3_joint_pv( jnt, endJntR[i], 'pv', 'R', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp', 'atom_bls_limbUp_radioButtonGrp', -1.0, 0.2, curveShapePath, True, flipVar = [0, 1, 1], X = 0.05 )
        pvLoc = appendage.create_3_joint_pv2( stJnt = jnt, endJnt = endJntR[i], prefix = jnt.split( '_jnt' )[0], suffix = 'R', distance_offset = 0.0, orient = True, color = 'red', X = 0.1, midJnt = '' )
        pvLocListR.append( pvLoc )
        place.cleanUp( pvLoc[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # flex pv
    i = 0
    pvLocListR_flex = []
    for jnt in legJntR_flex:
        # pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp', 'atom_bls_limbUp_radioButtonGrp', 1.0, 0.2, curveShapePath, True, flipVar = [0, 0, 0], X = 0.05 )
        pvLoc = appendage.create_3_joint_pv2( stJnt = jnt, endJnt = legAnklesR[i], prefix = jnt.split( '_jnt' )[0] + '_flex', suffix = 'R', distance_offset = 0.0, orient = True, color = 'red', X = 0.05, midJnt = '' )
        pvLocListR_flex.append( pvLoc )
        place.cleanUp( pvLoc[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # print 'catch pvLocListR:'
    # print pvLocListR
    # return
    # Creates poleVector Rig for appendages
    """
    creates pole vector rig
    \n*
    name      = name
    Master    = lowest master controller of char          --(not manipulated, 3 objs are constrained to it, for twist value calc)\n
    Top       = controller at top of ik                   --(not manipulated, pvRig group is parented under this object)\n
    Btm       = bottom of ik, controlling group or null   --(not manipulated, aim object for 'Top')\n
    Twist     = object from which twist is derived        --(not manipulated, axis is derived from 'aim' variable)\n
    pv        = pre-positioned pole vector object         --(object gets parented, turned off)\n
    midJnt    = connection joint for guideline            --(not manipulated)\n
    X         = size
    up        = [int, int, int]                           --(ie. [1,0,0], use controller space not joint space)\n
    aim       = [int, int, int]                           --(ie. [0,-1,0], use controller space not joint space)\n
    color     = int 1-31                                  --(ie. 17 is yellow)\n
    *\n
    Note      = Master, Top, Twist should all have the same rotation order.
    ie.       = Twist axis should be main axis. If 'y'is main axis, rotate order = 'zxy' or 'xzy'
    """
    i = 0
    for jnt in endJntL:
        #
        cmds.xform( pvLocListL[i][0], os = True, ro = ( 0, 0, 0 ) )
        cmds.parentConstraint( cntCt[4], pvLocListL[i][0], mo = True )
        #
        # cmds.pointConstraint( baseGrpsL[i], pvLocListL[i][0], mo = True )
        # cmds.pointConstraint( legJntL[i].split( '_' )[0] + '_base_L', pvLocListL[i][0], mo = True )
        # appendage.pvRig( jnt.split( '_' )[0] + '_pv_L', 'master_Grp', scktGrpsL[i], baseGrpsL[i], baseGrpsL[i], pvLocListL[i][4], kneeJntL[i], 0.1, jnt.split( '_' )[0] + '_L', setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
        i = i + 1

    i = 0
    for jnt in endJntR:
        #
        cmds.xform( pvLocListR[i][0], os = True, ro = ( 0, 0, 0 ) )
        cmds.parentConstraint( cntCt[4], pvLocListR[i][0], mo = True )
        #
        # cmds.pointConstraint( baseGrpsR[i], pvLocListR[i][0], mo = True )
        # cmds.pointConstraint( legJntR[i].split( '_' )[0] + '_base_R', pvLocListR[i][0], mo = True )
        # appendage.pvRig( jnt.split( '_' )[0] + '_pv_R', 'master_Grp', scktGrpsR[i], baseGrpsR[i], baseGrpsR[i], pvLocListR[i][4], kneeJntR[i], 0.1, jnt.split( '_' )[0] + '_R', setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 17 )
        i = i + 1

    place.cleanUp( 'GuideGp', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # Create an ik handle from TopJoint to end effector

    i = 0
    util_jointsL = []
    for jnt in legJntL:
        name = jnt.split( '_' )[0] + '_ik_L'
        #
        util_joints = place.jointChainAlign( name = jnt.split( '_' )[0] + '_jnt_utl', suffix = 'L', objs = [jnt, kneeJntL[i], endJntL[i]] )
        util_jointsL.append( util_joints )
        cmds.parentConstraint( legParentsL[i], util_joints[0], mo = True )
        # up vector for aim
        cmds.parentConstraint( util_joints[0], baseUpL[i][0], mo = True )
        cmds.parentConstraint( util_joints[1], ankleUpL[i][0], mo = True )
        place.cleanUp( util_joints[0], SknJnts = True )
        #
        cmds.ikHandle( n = name, sj = util_joints[0], ee = util_joints[-1], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListL[i], name )
        cmds.setAttr( name + '.visibility', 0 )
        cmds.parent( name, baseGrpsL[i] )
        #
        # ik for flex segment
        name = jnt.split( '_' )[0] + '_flex_ik_L'
        cmds.ikHandle( n = name, sj = kneeJntL[i], ee = legAnklesL[i], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListL_flex[i][4], name )
        cmds.parentConstraint( util_joints[1], pvLocListL_flex[i][0], mo = True )
        cmds.setAttr( name + '.visibility', 0 )
        cmds.parent( name, ankleAimL[i][0] )
        #
        i = i + 1
    # return
    i = 0
    util_jointsR = []
    for jnt in legJntR:
        name = jnt.split( '_' )[0] + '_ik_R'
        #
        util_joints = place.jointChainAlign( name = jnt.split( '_' )[0] + '_jnt_utl', suffix = 'R', objs = [jnt, kneeJntR[i], endJntR[i]] )
        util_jointsR.append( util_joints )
        cmds.parentConstraint( legParentsR[i], util_joints[0], mo = True )
        # up vector for aim
        cmds.parentConstraint( util_joints[0], baseUpR[i][0], mo = True )
        cmds.parentConstraint( util_joints[1], ankleUpR[i][0], mo = True )
        place.cleanUp( util_joints[0], SknJnts = True )
        #
        cmds.ikHandle( n = name, sj = util_joints[0], ee = util_joints[-1], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListR[i], name )
        cmds.setAttr( name + '.visibility', 0 )
        cmds.parent( name, baseGrpsR[i] )
        #
        # ik for flex segment
        name = jnt.split( '_' )[0] + '_flex_ik_R'
        cmds.ikHandle( n = name, sj = kneeJntR[i], ee = legAnklesR[i], sol = 'ikRPsolver', p = 2, w = .5, srp = True )
        cmds.poleVectorConstraint( pvLocListR_flex[i][4], name )
        cmds.parentConstraint( util_joints[1], pvLocListR_flex[i][0], mo = True )
        cmds.setAttr( name + '.visibility', 0 )
        cmds.parent( name, ankleAimR[i][0] )
        #
        i = i + 1

    # segment control
    # Left Side of Rig
    color = 'blue'
    shape = 'facetXup_ctrl'
    i = 0
    for knee in kneeJntL:
        # knee
        name_Ct = place.Controller2( knee.split( '_' )[0] + '_knee_L', knee, True, shape, 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        place.rotationLock( name_Ct[2], True )
        orn = cmds.orientConstraint( util_jointsL[i][0], name_Ct[0] )
        cmds.delete( orn )
        cmds.parentConstraint( util_jointsL[i][0], name_Ct[0], mo = True )
        # aim base leg at new control
        cmds.aimConstraint( name_Ct[4], legJntL[i], wut = 'object', wuo = baseUpL[i][4], aim = ( 0, 0, 1 ), u = ( 0, 1, 0 ), mo = True )
        cmds.parent( name_Ct[0], CONTROLS() )
        #
        # ankle
        name_Ct = place.Controller2( legAnklesL[i].split( '_' )[0] + '_ankle_L', legAnklesL[i], True, shape, 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        place.rotationLock( name_Ct[2], True )
        cmds.parentConstraint( util_jointsL[i][1], name_Ct[0], mo = True )
        cmds.parent( name_Ct[0], CONTROLS() )
        cmds.aimConstraint( name_Ct[4], ankleAimL[i][0], wut = 'object', wuo = ankleUpL[i][4], aim = ( 0, 0, 1 ), u = ( 0, 1, 0 ), mo = True )
        #
        i = i + 1

    # Right Side of Rig
    color = 'red'
    shape = 'facetXup_ctrl'
    i = 0
    for knee in kneeJntR:
        # knee
        name_Ct = place.Controller2( knee.split( '_' )[0] + '_knee_R', knee, True, shape, 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        place.rotationLock( name_Ct[2], True )
        orn = cmds.orientConstraint( util_jointsR[i][0], name_Ct[0] )
        cmds.delete( orn )
        cmds.parentConstraint( util_jointsR[i][0], name_Ct[0], mo = True )
        # aim base leg at new control
        cmds.aimConstraint( name_Ct[4], legJntR[i], wut = 'object', wuo = baseUpR[i][4], aim = ( 0, 0, -1 ), u = ( 0, -1, 0 ), mo = True )
        cmds.parent( name_Ct[0], CONTROLS() )
        #
        # ankle
        name_Ct = place.Controller2( legAnklesR[i].split( '_' )[0] + '_ankle_R', legAnklesR[i], True, shape, 0.4, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
        cmds.xform( name_Ct[0], r = True, os = True, ro = ( 0, 180, 180 ) )
        place.rotationLock( name_Ct[2], True )
        cmds.parentConstraint( util_jointsR[i][1], name_Ct[0], mo = True )
        cmds.parent( name_Ct[0], CONTROLS() )
        cmds.aimConstraint( name_Ct[4], ankleAimR[i][0], wut = 'object', wuo = ankleUpR[i][4], aim = ( 0, 0, -1 ), u = ( 0, -1, 0 ), mo = True )
        #
        i = i + 1

    # cleanup of root_jnt and body_Geo

    place.cleanUp( 'root_jnt', Ctrl = False, SknJnts = True, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    place.cleanUp( geo, Ctrl = False, SknJnts = False, Body = True, Accessory = False, Utility = False, World = False, olSkool = False )
    #

    # have to run last cuz consraint node parent under spine joint breaks spline build
    '''
    i = 0
    for jnt in legParents:
        cmds.parentConstraint( jnt, legJntL[i], mo = True )
        cmds.parentConstraint( jnt, legJntR[i], mo = True )
        i = i + 1'''

    # scale
    # geo = 'geo_spider_body'
    mstr = 'master'
    uni = 'uniformScale'
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    # misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def buildSplines( *args ):
    '''\n
    Build splines for quadraped character\n
    '''
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 0.15

    def SplineOpts( name, size, distance, falloff ):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField( 'atom_prefix_textField', e = True, tx = name )
        cmds.floatField( 'atom_spln_scaleFactor_floatField', e = True, v = size )
        cmds.floatField( 'atom_spln_vectorDistance_floatField', e = True, v = distance )
        cmds.floatField( 'atom_spln_falloff_floatField', e = True, v = falloff )

    def OptAttr( obj, attr ):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( obj + '.' + attr, cb = True )

    # SPINE
    spineName = 'spine'
    spineSize = X * 1
    spineDistance = X * 20
    spineFalloff = 0
    spinePrnt = 'Cog_Grp'
    spineStrt = 'Chest_Grp'
    spineEnd = 'Pelvis_Grp'
    spineAttr = 'Chest'
    spineRoot = 'spine_jnt_01'
    'spine_S_IK_Jnt'
    spine = ['spine_jnt_01', 'spine_jnt_07']
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # return None
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 1 )
    cmds.setAttr( spineAttr + '.ClstrVis', 0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', .25 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_E_IK_curve_scale.input2Z' )
    # add hack to move joint only at end of spline
    pelvis = 'spine_M6_IK_Cntrl'
    plvs = place.Controller( pelvis, 'spine_jnt_07', orient = True, shape = 'tacZ_ctrl', size = 1.0, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    plvsCt = plvs.createController()
    place.cleanUp( plvsCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parent( plvsCt[0], spineName + '_E_IK_Cntrl' )
    cmds.connectAttr( plvsCt[2] + '.translateX', spineName + '_jnt_07_pointConstraint1.offsetX' )
    cmds.connectAttr( plvsCt[2] + '.translateY', spineName + '_jnt_07_pointConstraint1.offsetY' )
    cmds.connectAttr( plvsCt[2] + '.translateZ', spineName + '_jnt_07_pointConstraint1.offsetZ' )

    # NECK
    neckName = 'Neck'
    neckSize = X * 1
    neckDistance = X * 20
    neckFalloff = 0
    neckPrnt = 'Neck_Grp'
    neckStrt = 'Neck_Grp'
    neckEnd = 'Head_Grp'
    neckAttr = 'Neck'
    neck = ['head_jnt_01', 'head_jnt_05']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # assemble
    OptAttr( neckAttr, 'NeckSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 1 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )
    # return False
    # TAIL
    neckName = 'Tail'
    neckSize = X * 1
    neckDistance = X * 20
    neckFalloff = 0
    neckPrnt = 'Pelvis_Grp'
    neckStrt = 'spine_jnt_07'
    neckEnd = 'Tail_Grp'
    neckAttr = 'Tail'
    neck = ['tail_jnt_01', 'tail_jnt_05']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( neckAttr, 'TailSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    # return None
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 1 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # scale
    '''
    # scale
    geo = 'caterpillar_c_geo_lod_0'
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    # misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush
    '''
