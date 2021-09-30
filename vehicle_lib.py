import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
atl = web.mod( "atom_path_lib" )
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
anm = web.mod( "anim_lib" )
dsp = web.mod( "display_lib" )


def vehicle_master( masterX = 10, moveX = 10 ):
    '''
    default group structure
    master and move controls
    '''
    # temp for dev, remove when building actual vehicle
    PreBuild = place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = masterX * 20 )

    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # contact #
    Move = 'Move'
    move = place.Controller( Move, MasterCt[0], False, 'splineStart_ctrl', moveX * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    MoveCt = move.createController()
    cmds.parent( MoveCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], MoveCt[0], mo = True )

    return [MasterCt[4], MoveCt[4]]


def wheel( master_move_controls = [], axle = '', steer = '', center = '', bottom = '', top = '', spin = '', tire_geo = [], rim_geo = [], caliper_geo = [], name = '', suffix = '', X = 1.0 ):
    '''
    create wheel rig
    - translation based rotation
    - inflattion / deflation
    - steering
    inputs
    - 2 pre-existing controls = master_move_controls -- vehicle_master()
    - jnts                    = axle, steer, center, bottom, top, spin
    - geo                     = tire_geo, rim_geo, caliper_geo
    - naming strings          = name, suffix
    - controller size         = X
    
    '''
    colorName = ''
    # side
    if 'L' in suffix:
        colorName = 'red'
    elif 'R' in suffix:
        colorName = 'blue'

    CONTROLS = '___CONTROLS'
    master = master_move_controls[0]
    move = master_move_controls[1]

    # tire has to be facing forward in Z
    clstr = tire_pressure( obj = tire_geo, center = center, name = name, suffix = suffix )

    # geo cleanup
    cmds.parent( tire_geo, '___WORLD_SPACE' )
    if tire_geo:
        for i in tire_geo:
            print( i )
            cmds.connectAttr( spin + '.rotateX', i + '.rotateX' )
    else:
        print( 'no' )
    # return
    # rim, change to skin
    if rim_geo:
        for i in rim_geo:
            cmds.parent( i, spin )
    # caliper, skin if exists
    if caliper_geo:
        for i in caliper_geo:
            cmds.parent( i, center )

    # root
    cmds.parentConstraint( move, axle, mo = True )

    # wheels shouldnt sping when master is moved, use drive / move control
    WHEEL_SPACE = 'WHEEL_SPACE'
    if not cmds.objExists( WHEEL_SPACE ):
        WHEEL_SPACE = cmds.group( name = WHEEL_SPACE, em = True )
        cmds.parent( WHEEL_SPACE, CONTROLS )
        cmds.parentConstraint( master, WHEEL_SPACE, mo = True )

    # contact #
    Contact_F_L = name + '_contact_' + suffix
    contact_F_L = place.Controller( Contact_F_L, bottom, False, 'facetYup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Contact_F_LCt = contact_F_L.createController()
    cmds.parent( Contact_F_LCt[0], WHEEL_SPACE )
    cmds.parentConstraint( steer, Contact_F_LCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( Contact_F_LCt[2], [True, False], [True, False], [True, False], [True, False, False] )
    cmds.setAttr( Contact_F_LCt[2] + '.translateY', keyable = True, lock = False )
    #
    place.optEnum( Contact_F_LCt[2], attr = 'Wheel', enum = 'OPTNS' )
    place.addAttribute( [Contact_F_LCt[2]], ['autoRoll'], 0, 1, True, attrType = 'float' )
    #
    place.optEnum( Contact_F_LCt[0], attr = 'Roll', enum = 'INPUTS' )
    #
    cmds.addAttr( Contact_F_LCt[0], ln = 'Radius' )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Radius' ), cb = True )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Radius' ), keyable = True )
    #
    cmds.addAttr( Contact_F_LCt[0], ln = 'Drive' )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Drive' ), cb = True )
    cmds.setAttr( ( Contact_F_LCt[0] + '.Drive' ), keyable = True )

    # live radius
    g = cmds.group( name = name + '_grp_' + suffix, em = True )
    cmds.parent( g, CONTROLS )
    cmds.setAttr( g + '.visibility', 0 )
    #
    r1 = place.loc( name + '_radius1_' + suffix )[0]
    cmds.select( r1, spin )
    anm.matchObj()
    cmds.parent( r1, g )
    #
    r2 = place.loc( name + '_radius2_' + suffix )[0]
    cmds.select( r2, top )
    anm.matchObj()
    cmds.parent( r2, g )
    #
    dsp.distance( obj1 = r1, obj2 = r2 )
    cmds.connectAttr( r1 + '.distance', Contact_F_LCt[0] + '.Radius' )

    # center
    Center_front_L = name + '_pressure_' + suffix
    center_front_L = place.Controller( Center_front_L, center, False, 'diamond_ctrl', X * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Center_front_LCt = center_front_L.createController()
    cmds.parent( Center_front_LCt[0], CONTROLS )
    cmds.parentConstraint( Center_front_LCt[4], center, mo = True )
    cmds.parentConstraint( Contact_F_LCt[4], Center_front_LCt[0], mo = True )
    # math node
    mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = Center_front_LCt[2] + '_mltp_ty' )
    cmds.setAttr( mltp + '.operation', 1 )  # multiply
    cmds.setAttr( mltp + '.input2Y', -1 )
    # connect
    cmds.connectAttr( Center_front_LCt[2] + '.translateY', mltp + '.input1Y' )
    cmds.connectAttr( mltp + '.outputY', clstr + '.translateY' )
    # sidewall
    place.optEnum( Center_front_LCt[2], attr = 'Tire', enum = 'OPTNS' )
    place.addAttribute( [Center_front_LCt[2]], ['sidewallFlex'], -1, 1, True, attrType = 'float' )
    cmds.connectAttr( Center_front_LCt[2] + '.sidewallFlex', clstr + '.translateX' )

    # spin
    Spin_front_L = name + '_spin_' + suffix
    spin_front_L = place.Controller( Spin_front_L, spin, False, 'shldrL_ctrl', X * 7, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Spin_front_LCt = spin_front_L.createController()
    cmds.parent( Spin_front_LCt[0], CONTROLS )
    cmds.parentConstraint( Spin_front_LCt[4], spin, mo = True )
    cmds.parentConstraint( Center_front_LCt[4], Spin_front_LCt[0], mo = True )
    #
    cmds.connectAttr( Contact_F_LCt[0] + '.Drive', Spin_front_LCt[1] + '.rotateX' )
    #
    wheel_exp( ctrl = Contact_F_LCt[0] )

    # steer #
    Steer_F_L = name + '_steer_' + suffix
    steer_F_L = place.Controller( Steer_F_L, steer, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    Steer_F_LCt = steer_F_L.createController()
    cmds.parent( Steer_F_LCt[0], CONTROLS )
    cmds.xform( Steer_F_LCt[0], relative = True, t = ( 0, 0, 20 ) )
    cmds.parentConstraint( move, Steer_F_LCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( Steer_F_LCt[2], [True, False], [True, False], [True, False], [True, False, False] )
    cmds.setAttr( Steer_F_LCt[2] + '.translateX', keyable = True, lock = False )
    # steer up
    SteerUp_F_L = name + '_steerUp_' + suffix
    steerUp_F_L = place.Controller( SteerUp_F_L, steer, False, 'loc_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    SteerUp_F_LCt = steerUp_F_L.createController()
    cmds.parent( SteerUp_F_LCt[0], CONTROLS )
    cmds.xform( SteerUp_F_LCt[0], relative = True, t = ( 0, 10, 0 ) )
    cmds.parentConstraint( move, SteerUp_F_LCt[0], mo = True )
    cmds.setAttr( SteerUp_F_LCt[0] + '.visibility', 0 )

    cmds.aimConstraint( Steer_F_LCt[4], steer, wut = 'object', wuo = SteerUp_F_LCt[4], aim = [0, 0, 1], u = [0, 1, 0], mo = True )
    # cmds.aimConstraint( locAim, obj, wut = 'object', wuo = locUp, aim = aim, u = u, mo = mo )


def tire_pressure( obj = '', center = '', name = '', suffix = '', lattice = ( 2, 29, 5 ) ):
    '''
    add tire pressure behaviour
    lattice = object local space (X, Y, Z)
    '''
    # group
    g = cmds.group( name = name + '_clusterGrp_' + suffix, em = True )
    cmds.parent( g, '___WORLD_SPACE' )
    cmds.setAttr( g + '.visibility', 0 )

    # store selection
    sel = cmds.ls( sl = 1 )
    # lattice
    cmds.select( obj )
    # [u'wheel_front_lattice_L_', u'wheel_front_lattice_L_Lattice', u'wheel_front_lattice_L_Base']
    result = cmds.lattice( name = name + '_ltc_' + suffix + '_', dv = lattice, oc = True, outsideLattice = 1 )
    cmds.parent( result, '___WORLD_SPACE' )
    cmds.setAttr( result[1] + '.visibility', 0 )
    cmds.setAttr( result[2] + '.visibility', 0 )
    # print( result )
    # clusters
    clusters = []
    ltc = result[1]
    depth = lattice[0]  # X
    row = ( lattice[1] - 1 ) / 2  # Y
    column = lattice[2]  # Z
    for i in range( row ):  # depth
        sl = ltc + '.pt[' + str( i ) + '][0:' + str( depth - 1 ) + '][0:' + str( column - 1 ) + ']'
        sl = ltc + '.pt[0:' + str( depth - 1 ) + '][' + str( i ) + '][0:' + str( column - 1 ) + ']'
        # print( sl )
        cmds.select( sl )
        c = cmds.cluster( name = name + '_clstr_' + str( i ) + '_' + suffix + '_' )[1]
        clusters.append( c )

    # top cluster (lattice[row])
    sl = ltc + '.pt[' + str( row ) + ':' + str( lattice[1] ) + '][0:' + str( depth - 1 ) + '][0:' + str( column - 1 ) + ']'
    sl = ltc + '.pt[0:' + str( depth - 1 ) + '][' + str( row ) + ':' + str( lattice[1] ) + '][0:' + str( column - 1 ) + ']'
    # print( sl )
    cmds.select( sl )
    c = cmds.cluster( name = name + '_clstrTop_' + suffix + '_' )[1]
    # clusters.append( c )

    # parent clusters
    cmds.parent( clusters, g )
    cmds.parent( c, g )
    # connect to rig
    cmds.parentConstraint( center, g, mo = True )

    # translate y math nodes
    lattice_row_gap = 0.3  # guess, should find a way to measure it
    for i in range( len( clusters ) - 1 ):
        # create nodes for translation
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_ty' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_ty' )
        # set node attrs
        cmds.setAttr( cndtn + '.colorIfFalseR', 0 )
        cmds.setAttr( cndtn + '.colorIfFalseG', 0 )
        cmds.setAttr( cndtn + '.colorIfFalseB', 0 )
        cmds.setAttr( cndtn + '.secondTerm', lattice_row_gap )
        cmds.setAttr( cndtn + '.operation', 3 )  # greater or equal
        cmds.setAttr( addDL + '.input2', lattice_row_gap * -1 )
        # connect math in
        cmds.connectAttr( clusters[i] + '.translateY', addDL + '.input1' )
        cmds.connectAttr( clusters[i] + '.translateY', cndtn + '.firstTerm' )
        # connect math out
        cmds.connectAttr( addDL + '.output', cndtn + '.colorIfTrueG' )
        cmds.connectAttr( cndtn + '.outColorG', clusters[i + 1] + '.translateY' )

    # tire bulge scale X
    weight = 0.3
    weight_add = 0.1
    cls = int( len( clusters ) / 2 ) - 3
    for i in range( cls ):
        # create nodes for scale bulge
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_sclx' )
        mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = clusters[i] + '_mltDv_sclx' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_sclx' )
        # set node attrs
        cmds.setAttr( mltp + '.operation', 1 )  # multiply
        cmds.setAttr( mltp + '.input2X', weight )
        cmds.setAttr( addDL + '.input2', 1 )
        # connect mltp in
        cmds.connectAttr( clusters[0] + '.translateY', mltp + '.input1X' )
        # connect addDL in
        cmds.connectAttr( mltp + '.outputX', addDL + '.input1' )
        # connect next cluster in
        cmds.connectAttr( addDL + '.output', clusters[i + 1] + '.scaleX' )
        #
        if i <= 1:
            # weight_add = weight_add * 2
            weight = weight + weight_add
        else:
            # weight_add = weight_add * 2
            weight = weight - ( weight_add * 2 )

    # tx sidewall, direct copy of above loop, altered names, couple connections
    weight = 0.3
    weight_add = 0.1
    cls = int( len( clusters ) / 2 ) - 3
    for i in range( cls ):
        # create nodes for scale bulge
        cndtn = cmds.shadingNode( 'condition', au = True, n = clusters[i] + '_cndtn_tx' )
        mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = clusters[i] + '_mltDv_tx' )
        addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_tx' )
        # set node attrs
        cmds.setAttr( mltp + '.operation', 1 )  # multiply
        cmds.setAttr( mltp + '.input2X', weight )
        cmds.setAttr( addDL + '.input2', 0 )
        # connect mltp in
        cmds.connectAttr( clusters[0] + '.translateX', mltp + '.input1X' )
        # connect addDL in
        cmds.connectAttr( mltp + '.outputX', addDL + '.input1' )
        # connect next cluster in
        cmds.connectAttr( addDL + '.output', clusters[i + 1] + '.translateX' )
        #
        if i <= 1:
            # weight_add = weight_add * 2
            weight = weight + weight_add
        else:
            # weight_add = weight_add * 2
            weight = weight - ( weight_add * 2 )

    # limits
    cmds.select( clusters[0] )
    cmds.transformLimits( ety = [1, 0], ty = ( 0, 100 ) )

    cmds.select( sel )

    return clusters[0]


def wheel_exp( ctrl = '' ):
    '''
    add expression to control, connect drive attr to wheel rotation
    '''
    ln1 = "global vector $" + ctrl + "vPos = << 0, 0, 0 >>;\n"
    ln2 = "float $" + ctrl + "distance = 0.0;\n"
    ln3 = "int $" + ctrl + "direction = 1;\n"
    ln4 = "vector $" + ctrl + "vPosChange = `getAttr " + ctrl + ".translate`;\n"
    ln5 = "float $" + ctrl + "cx = $" + ctrl + "vPosChange.x - $" + ctrl + "vPos.x;\n"
    ln6 = "float $" + ctrl + "cy = $" + ctrl + "vPosChange.y - $" + ctrl + "vPos.y;\n"
    ln7 = "float $" + ctrl + "cz = $" + ctrl + "vPosChange.z - $" + ctrl + "vPos.z;\n"
    ln8 = "float $" + ctrl + "distance = sqrt( `pow $" + ctrl + "cx 2` + `pow $" + ctrl + "cy 2` + `pow $" + ctrl + "cz 2` );\n"
    ln9 = "if ( ( $" + ctrl + "vPosChange.x == $" + ctrl + "vPos.x ) && ( $" + ctrl + "vPosChange.y != $" + ctrl + "vPos.y ) && ( $" + ctrl + "vPosChange.z == $" + ctrl + "vPos.z ) ){}\n"
    ln10 = "else {\n"
    ln11 = "    float $" + ctrl + "angle = " + ctrl + ".rotateY%360;\n"
    ln12 = "    if ( $" + ctrl + "angle == 0 ){ \n"
    ln13 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = 1;\n"
    ln14 = "        else $" + ctrl + "direction=-1;}\n"
    ln15 = "    if ( ( $" + ctrl + "angle > 0 && $" + ctrl + "angle <= 90 ) || ( $" + ctrl + "angle <- 180 && $" + ctrl + "angle >= -270 ) ){ \n"
    ln16 = "        if ( $" + ctrl + "vPosChange.x > $" + ctrl + "vPos.x ) $" + ctrl + "direction = 1 * $" + ctrl + "direction;\n"
    ln17 = "        else $" + ctrl + "direction = -1 * $" + ctrl + "direction; }\n"
    ln18 = "    if ( ( $" + ctrl + "angle > 90 && $" + ctrl + "angle <= 180 ) || ( $" + ctrl + "angle < -90 && $" + ctrl + "angle >= -180 ) ){\n"
    ln19 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = -1 * $" + ctrl + "direction;\n"
    ln20 = "        else $" + ctrl + "direction = 1 * $" + ctrl + "direction; }\n"
    ln21 = "    if ( ( $" + ctrl + "angle > 180 && $" + ctrl + "angle <= 270 ) || ( $" + ctrl + "angle < 0 && $" + ctrl + "angle >= -90 ) ){\n"
    ln22 = "        if ( $" + ctrl + "vPosChange.x > $" + ctrl + "vPos.x ) $" + ctrl + "direction = -1 * $" + ctrl + "direction;\n"
    ln23 = "        else $" + ctrl + "direction = 1 * $" + ctrl + "direction; }\n"
    ln24 = "    if ( ( $" + ctrl + "angle > 270 && $" + ctrl + "angle <= 360 ) || ( $" + ctrl + "angle < -270 && $" + ctrl + "angle >= -360 ) ) {\n"
    ln25 = "        if ( $" + ctrl + "vPosChange.z > $" + ctrl + "vPos.z ) $" + ctrl + "direction = 1 * $" + ctrl + "direction;\n"
    ln26 = "        else $" + ctrl + "direction = -1 * $" + ctrl + "direction; }\n"
    ln27 = "    " + ctrl + ".Drive = " + ctrl + ".Drive + ( ( $" + ctrl + "direction * ( ( $" + ctrl + "distance / ( 6.283185 * " + ctrl + ".Radius ) ) * 360.0 ) ) ); }\n"
    ln28 = "$" + ctrl + "vPos = << " + ctrl + ".translateX, " + ctrl + ".translateY, " + ctrl + ".translateZ >>;\n"

    exp = ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7 + ln8 + ln9 + ln10 + ln11 + ln12 + ln13 + ln14 + ln15 + ln16 + ln17 + ln18 + ln19 + ln20 + ln21 + ln22 + ln23 + ln24 + ln25 + ln26 + ln27 + ln28
    cmds.expression( o = ctrl, s = exp )

'''
#
import imp
import webrImport as web
imp.reload(web)

sel = [
'axle_front_jnt',
'wheel_front_steer_L_jnt',
'wheel_front_center_L_jnt',
'wheel_front_bottom_L_jnt',
'wheel_front_top_L_jnt',
'wheel_front_spin_L_jnt'
]

# main
vhl = web.mod('vehicle_lib')
ctrls = vhl.vehicle_master()
vhl.wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'L', X = 1.0 )
#
'''
