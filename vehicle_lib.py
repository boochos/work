import glob
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
cn = web.mod( 'constraint_lib' )
app = web.mod( "atom_appendage_lib" )
jnt = web.mod( 'atom_joint_lib' )
dnm = web.mod( 'atom_dynamicSpline_lib' )
ss = web.mod( "selectionSet_lib" )
wrp = web.mod( "createWrap" )


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
            print( what )


def CONTROLS():
    return '___CONTROLS'


def WORLD_SPACE():
    return '___WORLD_SPACE'


def __________________PARTS():
    pass


def vehicle_master( masterX = 10, moveX = 10, steerParent = '', geo_grp = '' ):
    '''
    default group structure
    master and move controls
    '''
    # temp for dev, remove when building actual vehicle
    PreBuild = place.rigPrebuild( Top = 2, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = masterX * 20 )

    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    # geo group
    if geo_grp:
        cmds.parent( geo_grp, '___GEO' )

    # root joint
    root = 'root_jnt'
    cmds.parent( root, SKIN_JOINTS )

    # move #
    Move = 'move'
    MoveCt = place.Controller2( Move, MasterCt[0], False, 'splineStart_ctrl', moveX * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( MoveCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], MoveCt[0], mo = True )
    cmds.parentConstraint( MoveCt[4], 'root_jnt', mo = True )
    # cmds.parentConstraint( opfCt[4], MoveCt[0], mo = True )

    # steer #
    Steer = 'steer'
    SteerCt = place.Controller2( Steer, 'front_jnt', False, 'splineStart_ctrl', moveX * 5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( SteerCt[0], CONTROLS )
    # cmds.setAttr( SteerCt[0] + '.tz', moveX * 5 )
    if steerParent:
        cmds.parentConstraint( steerParent, SteerCt[0], mo = True )
    else:
        cmds.parentConstraint( MoveCt[4], SteerCt[0], mo = True )
    place.translationLock( SteerCt[2], True )
    place.rotationXLock( SteerCt[2], True )
    place.rotationZLock( SteerCt[2], True )
    place.translationLock( SteerCt[3], True )
    place.rotationXLock( SteerCt[3], True )
    place.rotationZLock( SteerCt[3], True )

    if steerParent:
        return [MasterCt[4], steerParent, SteerCt[4]]
    else:
        return [MasterCt[4], MoveCt[4], SteerCt[4]]


def solid_axle( name = '', axle = '', axlL = '', axlR = '', parent1 = '', parent2 = '', parent3 = '', geo = [], aim = [0, 0, 1], up = [0, 1, 0], X = 1 ):
    '''
    axle = center axle jnt = front pivot / back pivot
    axlL = left axle
    axlR = right axle
    parent1 = pivot left wheel
    parent2 = pivot right wheel
    parent3 = chassis center pivot
    up object gets created at axle and moved in up vector direction and constrained to parent3
    
    * problem. top contact control group gets constrained to steer joint, when axle tilts and contact pivot control moves sideways, ty is added to wheel, cuz wheel space is no longer vertical...
    more uneven the axle more ty is added from sideways moving contact pivot
    could be problematic when pivot is constrainted to ground geo  
    
    '''
    # skin
    print( 'geo', geo )
    if geo:
        skin( axle, geo )

    # add rig group for cleanliness
    axle_grp = cmds.group( name = name + '_AxleGrp', em = True )
    cmds.setAttr( axle_grp + '.visibility', 0 )
    place.cleanUp( axle_grp, Ctrl = True )

    # axl
    name0 = name + '_axl'
    name0_Ct = place.Controller2( name0, axle, True, 'squareXup_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( name0_Ct[0], axle_grp )
    cmds.parentConstraint( name0_Ct[4], axle, mo = True )
    if parent3:
        cmds.parentConstraint( parent3, name0_Ct[0], mo = True )
    # place.rotationLock( name0_Ct[2], True )

    # axlL
    name1 = name + '_axlL'
    name1_Ct = place.Controller2( name1, axlL, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'blue' ).result
    cmds.parent( name1_Ct[0], axle_grp )
    cmds.pointConstraint( name1_Ct[4], name0_Ct[1], mo = True, sk = ['x', 'z'] )
    if parent3:
        cmds.parentConstraint( parent3, name1_Ct[0], mo = True )
    if parent1:
        cmds.pointConstraint( parent1, name1_Ct[1], mo = True, sk = ['x', 'z'] )
    # place.rotationLock( name1_Ct[2], True )

    # axlR
    name2 = name + '_axlR'
    name2_Ct = place.Controller2( name2, axlR, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'red' ).result
    cmds.parent( name2_Ct[0], axle_grp )
    cmds.pointConstraint( name2_Ct[4], name0_Ct[1], mo = True, sk = ['x', 'z'] )
    if parent3:
        cmds.parentConstraint( parent3, name2_Ct[0], mo = True )
    if parent2:
        cmds.pointConstraint( parent2, name2_Ct[1], mo = True, sk = ['x', 'z'] )
    # place.rotationLock( name2_Ct[2], True )
    # return

    # axle up
    nameUp = name + '_axlUp'
    nameUp_Ct = place.Controller2( nameUp, axle, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'yellow' ).result
    cmds.parent( nameUp_Ct[0], axle_grp )
    distance = dsp.measureDis( obj1 = axlL, obj2 = axlR )
    cmds.setAttr( nameUp_Ct[1] + place.vector( up ), distance )
    if parent3:
        cmds.parentConstraint( parent3, nameUp_Ct[0], mo = True )
    # place.rotationLock( nameUp_Ct[2], True )

    cmds.aimConstraint( name1_Ct[4], name0_Ct[1], wut = 'object', wuo = nameUp_Ct[4], aim = aim, u = up, mo = True, sk = ['x', 'y'] )

    return [name0_Ct]

    #


def piston( name = '', suffix = '', obj1 = '', obj2 = '', parent1 = '', parent2 = '', parentUp1 = '', parentUp2 = '', aim1 = [0, 0, 1], up1 = [0, 1, 0], aim2 = [0, 0, 1], up2 = [0, 1, 0], X = 1, color = 'yellow' ):
    '''
    obj objects should have proper pivot point for objects to place and constrain correctly
    '''
    #
    shape = 'squareZup_ctrl'
    if aim1 == [0, 1, 0] or aim1 == [0, -1, 0]:
        shape = 'squareYup_ctrl'
    attr = 'Up_Vis'
    #
    distance = dsp.measureDis( obj1 = obj1, obj2 = obj2 ) * 0.5
    if suffix:
        suffix = '_' + suffix
    upDir1 = 1
    for i in up1:
        if i == -1:
            upDir1 = -1
            break
    upDir2 = 1
    for i in up1:
        if i == -1:
            upDir2 = -1
            break
    # add rig group for cleanliness
    piston_grp = cmds.group( name = name + '_' + suffix + '_AllGrp', em = True )
    # cmds.parent( piston_grp, CONTROLS() )
    place.cleanUp( piston_grp, Ctrl = True )

    # obj1
    name1 = name + '_top' + suffix
    name1_Ct = place.Controller2( name1, obj1, True, shape, X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name1_Ct[0], piston_grp )
    cmds.pointConstraint( name1_Ct[4], obj1, mo = True )
    if parent1:
        cmds.parentConstraint( parent1, name1_Ct[0], mo = True )
    place.rotationLock( name1_Ct[2], True )

    # obj2
    name2 = name + '_bottom' + suffix
    name2_Ct = place.Controller2( name2, obj2, True, shape, X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    # return
    cmds.parent( name2_Ct[0], piston_grp )
    # rot = cmds.xform( name2_Ct[0], q = True, os = True, ro = True )
    # cmds.xform( name2_Ct[0], ws = True, ro = ( rot[0] + 180, 0, 0 ) )
    cmds.pointConstraint( name2_Ct[4], obj2, mo = True )
    if parent2:
        cmds.parentConstraint( parent2, name2_Ct[0], mo = True )
    place.rotationLock( name2_Ct[2], True )
    # return

    # obj1 up
    nameUp1 = name + '_topUp' + suffix
    nameUp1_Ct = place.Controller2( nameUp1, obj1, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp1_Ct[0], piston_grp )
    # print( nameUp1_Ct[1] , place.vector( up1 ), distance )
    cmds.setAttr( nameUp1_Ct[1] + place.vector( up1 ), distance * upDir1 )
    if parentUp1:
        cmds.parentConstraint( parentUp1, nameUp1_Ct[0], mo = True )
    else:
        cmds.parentConstraint( name1_Ct[4], nameUp1_Ct[0], mo = True )
    place.rotationLock( nameUp1_Ct[2], True )
    # vis
    place.addAttribute( name1_Ct[2], attr, 0, 1, False, 'long' )
    cmds.connectAttr( name1_Ct[2] + '.' + attr, nameUp1_Ct[0] + '.visibility' )

    # obj2 up
    nameUp2 = name + '_bottomUp' + suffix
    nameUp2_Ct = place.Controller2( nameUp2, obj2, True, 'loc_ctrl', X , 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( nameUp2_Ct[0], piston_grp )
    cmds.setAttr( nameUp2_Ct[1] + place.vector( up2 ), distance * upDir2 )
    if parentUp2:
        cmds.parentConstraint( parentUp2, nameUp2_Ct[0], mo = True )
    else:
        cmds.parentConstraint( name2_Ct[4], nameUp2_Ct[0], mo = True )
    place.rotationLock( nameUp2_Ct[2], True )
    # vis
    place.addAttribute( name2_Ct[2], attr, 0, 1, False, 'long' )
    cmds.connectAttr( name2_Ct[2] + '.' + attr, nameUp2_Ct[0] + '.visibility' )

    # aim
    cmds.aimConstraint( name2_Ct[4], obj1, wut = 'object', wuo = nameUp1_Ct[4], aim = aim1, u = up1, mo = True )
    cmds.aimConstraint( name1_Ct[4], obj2, wut = 'object', wuo = nameUp2_Ct[4], aim = aim2, u = up2, mo = True )

    return [name1_Ct, name2_Ct, nameUp1_Ct, nameUp2_Ct]


def spline( name = '', start_jnt = '', end_jnt = '', splinePrnt = '', splineStrt = '', splineEnd = '', startSkpR = False, endSkpR = False, color = 'yellow', X = 2 ):
    '''\n
    Build splines\n
    name      = 'chainA'         - name of chain
    root_jnt  = 'chainA_jnt_000' - provide first joint in chain
    tip_jnt   = 'chainA_jnt_016' - provide last joint in chain
    splinePrnt = 'master_Grp'     - parent of spline
    splineStrt = 'root_Grp'       - parent for start of spline
    splineEnd  = 'tip_Grp'        - parent for end of spline
    splineAttr = 'master'         - control to receive option attrs
    X         = 2                - controller scale
    '''

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

    # attr control
    attr_Ct = place.Controller2( name, start_jnt, True, 'squareZup_ctrl', X * 7, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( attr_Ct[0], CONTROLS() )
    cmds.parentConstraint( splineStrt, attr_Ct[0], mo = True )
    # lock translation
    place.rotationLock( attr_Ct[2], True )
    place.translationLock( attr_Ct[2], True )

    # SPINE
    splineName = name
    splineSize = X * 1
    splineDistance = X * 4
    splineFalloff = 0

    spline = [start_jnt, end_jnt]
    # build spline
    SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
    cmds.select( spline )

    stage.splineStage( 4, colorScheme = color )
    # assemble
    splineAttr = attr_Ct[2]
    OptAttr( splineAttr, name + 'Spline' )
    cmds.parentConstraint( splinePrnt, splineName + '_IK_CtrlGrp', mo = True )
    if startSkpR:
        cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True, sr = ( 'x', 'y', 'z' ) )
    else:
        cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True )
    if endSkpR:
        cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True, sr = ( 'x', 'y', 'z' ) )
    else:
        cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( splineName + '_IK_CtrlGrp', splineAttr )
    # set options
    cmds.setAttr( splineAttr + '.' + splineName + 'Vis', 0 )
    cmds.setAttr( splineAttr + '.' + splineName + 'Root', 0 )
    cmds.setAttr( splineAttr + '.' + splineName + 'Stretch', 1 )
    cmds.setAttr( splineAttr + '.ClstrVis', 1 )
    cmds.setAttr( splineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrVis', 0 )
    cmds.setAttr( splineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( splineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( splineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', splineName + '_E_IK_curve_scale.input2Z' )


def ik( name = '', start_jnt = '', end_jnt = '', start_parent = '', end_parent = '', pv_parent = '', X = 1.0, color = 'yellow' ):
    '''
    3 joint ik, for folding parts
    '''
    StartCt = place.Controller2( name, start_jnt, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parentConstraint( start_parent, StartCt[0], mo = True )
    cmds.pointConstraint( StartCt[4], start_jnt, mo = True )
    place.cleanUp( StartCt[0], Ctrl = True )
    #
    EndCt = place.Controller2( name, end_jnt, False, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parentConstraint( end_parent, EndCt[0], mo = True )
    place.cleanUp( EndCt[0], Ctrl = True )
    #
    PvCt = app.create_3_joint_pv2( stJnt = start_jnt, endJnt = end_jnt, prefix = name, suffix = '', distance_offset = 0.0, orient = True, color = color, X = X * 0.5, midJnt = '' )
    cmds.parentConstraint( pv_parent, PvCt[0], mo = True )
    place.cleanUp( PvCt[0], Ctrl = True )
    #
    ik = app.create_ik2( stJnt = start_jnt, endJnt = end_jnt, pv = PvCt[4], parent = EndCt[4], name = name, suffix = '', setChannels = True )


def four_point_pivot( name = 'vhcl', parent = '', skipParentUp = False, center = '', front = '', frontL = '', frontR = '', back = '', backL = '', backR = '', up = '', chassis_geo = [], X = 1, hide = False, shapes = 'boxZup_ctrl' ):
    '''
    - main control, with 4 point pivot control and up vector
    - will assume single pivot if either left or right not given
    - assume translateZ is forward
    '''
    pvt = 'pivot'
    vis_attr = 'pivots'
    #
    if name:
        name = name + '_'
    #
    color = 'yellow'
    colorc = 'yellow'
    colorL = 'blue'
    colorR = 'red'
    #
    single_front_pivot = False
    single_back_pivot = False

    # skin
    if chassis_geo:
        skin( center, chassis_geo )

    # body grp
    BODY_GRP = cmds.group( name = name + 'Pvt_AllGrp', em = True )
    cmds.parent( BODY_GRP, CONTROLS() )

    # ##########
    # body
    nameb = name + 'pivot'
    body_Ct = place.Controller2( nameb, center, False, 'rectangleTallYup_ctrl', X * 30, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( body_Ct[0], BODY_GRP )
    cmds.parentConstraint( parent, body_Ct[0], mo = True )
    place.translationLock( body_Ct[2], True )
    place.translationYLock( body_Ct[2], False )
    place.optEnum( body_Ct[2], attr = 'allPivots', enum = 'VIS' )
    place.addAttribute( body_Ct[2], vis_attr, 0, 1, False, 'long' )

    # ##########
    # front
    namef = name + 'front_' + pvt
    namef_Ct = place.Controller2( namef, front, False, 'L_ctrl', X * 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( namef_Ct[0], BODY_GRP )
    cmds.parentConstraint( namef_Ct[4], center, mo = True )
    cmds.parentConstraint( body_Ct[4], namef_Ct[0], mo = True )
    place.rotationLock( namef_Ct[2], True )
    place.translationZLock( namef_Ct[2], True )
    place.translationXLock( namef_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namef_Ct[0] + '.visibility' )

    # back
    nameb = name + 'back_' + pvt
    nameb_Ct = place.Controller2( nameb, back, False, 'invL_ctrl', X * 18, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameb_Ct[0], BODY_GRP )
    cmds.parentConstraint( body_Ct[4], nameb_Ct[0], mo = True )
    place.rotationLock( nameb_Ct[2], True )
    place.translationZLock( nameb_Ct[2], True )
    place.translationXLock( nameb_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, nameb_Ct[0] + '.visibility' )

    # up
    nameu = name + 'up_' + pvt
    nameu_Ct = place.Controller2( nameu, up, False, 'squareYup_ctrl', X * 10, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
    cmds.parent( nameu_Ct[0], BODY_GRP )
    if hide:
        cmds.setAttr( nameu_Ct[0] + '.visibility', 0 )
    # cmds.parentConstraint( nameu_Ct[4], up, mo = True )
    if not skipParentUp:
        cmds.parentConstraint( body_Ct[4], nameu_Ct[0], mo = True )
    place.rotationLock( nameu_Ct[2], True )
    place.translationZLock( nameu_Ct[2], True )
    cmds.connectAttr( body_Ct[2] + '.' + vis_attr, nameu_Ct[0] + '.visibility' )

    # ##########
    namefl_Ct = None
    namefr_Ct = None
    namefc_Ct = None  # center
    if frontL and frontR:  # dual front pivot
        # frontL
        namefl = name + 'front_L_' + pvt
        namefl_Ct = place.Controller2( namefl, frontL, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
        cmds.parent( namefl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefl_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefl_Ct[0], mo = True )
        place.rotationLock( namefl_Ct[2], True )
        # place.translationZLock( namefl_Ct[2], True )
        # place.translationXLock( namefl_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefl_Ct[0] + '.visibility' )

        # frontR
        namefr = name + 'front_R_' + pvt
        namefr_Ct = place.Controller2( namefr, frontR, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
        cmds.parent( namefr_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefr_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefr_Ct[0], mo = True )
        place.rotationLock( namefr_Ct[2], True )
        # place.translationZLock( namefr_Ct[2], True )
        # place.translationXLock( namefr_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefr_Ct[0] + '.visibility' )
    else:  # single front pivot
        single_front_pivot = True
        # front center
        namefc = name + 'front_C_' + pvt
        namefc_Ct = place.Controller2( namefc, front, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
        cmds.parent( namefc_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namefc_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namefc_Ct[0], mo = True )
        place.rotationLock( namefc_Ct[2], True )
        place.translationZLock( namefc_Ct[2], True )
        place.translationXLock( namefc_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namefc_Ct[0] + '.visibility' )

    # ##########
    namebl_Ct = None
    namebr_Ct = None
    namebc_Ct = None  # center
    if backL and backR:  # dual back pivot
        # backL
        namebl = name + 'back_L_' + pvt
        namebl_Ct = place.Controller2( namebl, backL, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorL ).result
        cmds.parent( namebl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebl_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebl_Ct[0], mo = True )
        place.rotationLock( namebl_Ct[2], True )
        # place.translationZLock( namebl_Ct[2], True )
        # place.translationXLock( namebl_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebl_Ct[0] + '.visibility' )

        # backR
        namebr = name + 'back_R_' + pvt
        namebr_Ct = place.Controller2( namebr, backR, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorR ).result
        cmds.parent( namebr_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebr_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebr_Ct[0], mo = True )
        place.rotationLock( namebr_Ct[2], True )
        # place.translationZLock( namebr_Ct[2], True )
        # place.translationXLock( namebr_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebr_Ct[0] + '.visibility' )
    else:  # single back pivot
        # back center
        single_back_pivot = True
        namebc = name + 'back_C_' + pvt
        namebc_Ct = place.Controller2( namebc, back, False, shapes, X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorc ).result
        cmds.parent( namebl_Ct[0], BODY_GRP )
        if hide:
            cmds.setAttr( namebc_Ct[0] + '.visibility', 0 )
        cmds.parentConstraint( body_Ct[4], namebc_Ct[0], mo = True )
        place.rotationLock( namebc_Ct[2], True )
        place.translationZLock( namebc_Ct[2], True )
        place.translationXLock( namebc_Ct[2], True )
        cmds.connectAttr( body_Ct[2] + '.' + vis_attr, namebc_Ct[0] + '.visibility' )

    # ##########
    # aim
    cmds.aimConstraint( nameb_Ct[4], namef_Ct[4], wut = 'object', wuo = nameu_Ct[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( namef_Ct[3], True )

    # ##########
    # pivot connections
    # 5 blend attr nodes
    # 2 multdiv nodes

    # front pivots ( left/ right ) ty blend
    if not single_front_pivot:
        frontBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_Blend' )
        cmds.setAttr( frontBlend + '.attributesBlender', 0.5 )
        # front left
        place.smartAttrBlend( master = namefl_Ct[2], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[3], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[4], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        # front right
        place.smartAttrBlend( master = namefr_Ct[2], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[3], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[4], slave = frontBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        cmds.connectAttr( frontBlend + '.output', namef_Ct[1] + '.translateY' )
        place.smartAttrBlend( master = frontBlend, slave = nameu_Ct[1], masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 0.5, reverse = False )  # add influence ty of up grp control
        # cmds.connectAttr( frontBlend + '.output', nameu_Ct[1] + '.translateY' )
    else:
        place.smartAttrBlend( master = namefc_Ct[2], slave = namef_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namefc_Ct[3], slave = namef_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namefc_Ct[4], slave = namef_Ct[4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )

    # back pivots ( left/ right ) ty blend
    if not single_back_pivot:
        backBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_Blend' )
        cmds.setAttr( backBlend + '.attributesBlender', 0.5 )
        # back left
        place.smartAttrBlend( master = namebl_Ct[2], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[3], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[4], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        # back right
        place.smartAttrBlend( master = namebr_Ct[2], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[3], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[4], slave = backBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection
        cmds.connectAttr( backBlend + '.output', nameb_Ct[1] + '.translateY' )
        place.smartAttrBlend( master = backBlend, slave = nameu_Ct[1], masterAttr = 'output', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 0.5, reverse = False )  # add influence ty of up grp control
        # cmds.connectAttr( backBlend + '.output', nameu_Ct[1] + '.translateY' )
    else:
        place.smartAttrBlend( master = namebc_Ct[2], slave = nameb_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namebc_Ct[3], slave = nameb_Ct[1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        place.smartAttrBlend( master = namebc_Ct[4], slave = nameb_Ct[4], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        # cmds.connectAttr( namebc_Ct[2] + '.translateY', nameb_Ct[1] + '.translateY' )

    # ###########
    # blend front up vector pivots (l/r) - prep nodes, ty to blend into tx of up vector control, left side converted to negative for neg tx
    frontUpBlend = None
    if not single_front_pivot:
        frontUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'front_up_txBlend' )  # recieves 2 ty inputs, one converted to negative
        cmds.setAttr( frontUpBlend + '.attributesBlender', 0.5 )  # each gets a weights of half
        # mltp only for left side, invert value
        # frontlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_front_l_mlt' )
        # cmds.setAttr( frontlmlt + '.operation', 1 )  # multiply
        # cmds.setAttr( frontlmlt + '.input2Y', -1 )
        # new
        place.smartAttrBlend( master = namefl_Ct[2], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[3], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namefl_Ct[4], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # insert second weighted connection
        #
        place.smartAttrBlend( master = namefr_Ct[2], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[3], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namefr_Ct[4], slave = frontUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection

        # old
        # cmds.connectAttr( namefr_Ct[2] + '.translateY', frontUpBlend + '.input[0]' )  # right to blend
        # cmds.connectAttr( namefl_Ct[2] + '.translateY', frontlmlt + '.input1Y' )  # left to negative node
        # cmds.connectAttr( frontlmlt + '.outputY', frontUpBlend + '.input[1]' )  # negative node to blend
    else:
        pass

    # blend back up vector pivots (l/r) - prep nodes, ty to blend into tx of up vector control, left side converted to negative for neg tx
    backUpBlend = None
    if not single_back_pivot:
        backUpBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'back_up_txBlend' )  # recieves 2 ty inputs, one converted to negative
        cmds.setAttr( backUpBlend + '.attributesBlender', 0.5 )  # each gets a weights of half
        # mltp only for left side, invert value
        # backlmlt = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '_back_l_mlt' )
        # cmds.setAttr( backlmlt + '.operation', 1 )  # multiply
        # cmds.setAttr( backlmlt + '.input2Y', -1 )
        # new
        place.smartAttrBlend( master = namebl_Ct[2], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[3], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # make first weighted connection
        place.smartAttrBlend( master = namebl_Ct[4], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[0]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )  # insert second weighted connection
        # back right
        place.smartAttrBlend( master = namebr_Ct[2], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[3], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # make first weighted connection
        place.smartAttrBlend( master = namebr_Ct[4], slave = backUpBlend, masterAttr = 'translateY', slaveAttr = 'input[1]', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )  # insert second weighted connection

        # old
        # cmds.connectAttr( namebr_Ct[2] + '.translateY', backUpBlend + '.input[0]' )  # right to blend
        # cmds.connectAttr( namebl_Ct[2] + '.translateY', backlmlt + '.input1Y' )  # left to negative node
        # cmds.connectAttr( backlmlt + '.outputY', backUpBlend + '.input[1]' )  # negative node to blend
    else:
        pass

    # blend result of front/back translateY values to upCt translateX
    result = []
    if not single_front_pivot  or not single_back_pivot:  # make sure at least one pivot is dual
        upBlend = cmds.shadingNode( 'blendTwoAttr' , au = True, n = name + 'up_txBlend' )
        cmds.setAttr( upBlend + '.attributesBlender', 0.5 )
        #
        if not single_front_pivot:
            cmds.connectAttr( frontUpBlend + '.output', upBlend + '.input[0]' )
            result.append( namefl_Ct )
            result.append( namefr_Ct )
        else:
            result.append( namefc_Ct )
        #
        if not single_back_pivot:
            cmds.connectAttr( backUpBlend + '.output', upBlend + '.input[1]' )
            result.append( namebl_Ct )
            result.append( namebr_Ct )
        else:
            result.append( namebc_Ct )
        #
        tx_attr = 'multiplier'
        place.optEnum( nameu_Ct[2], attr = 'chassisPivotRoll', enum = 'CONTROL' )
        place.addAttribute( [nameu_Ct[2]], [tx_attr], 0, 10, True, attrType = 'float' )
        cmds.setAttr( nameu_Ct[2] + '.' + tx_attr, 2 )
        txmlt = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + '_tx_mlt' )
        cmds.connectAttr( upBlend + '.output', txmlt + '.input1' )
        cmds.connectAttr( nameu_Ct[2] + '.' + tx_attr, txmlt + '.input2' )
        cmds.connectAttr( txmlt + '.output', nameu_Ct[1] + '.translateX' )

    else:
        return [namefc_Ct, namebc_Ct]

    result.append( namef_Ct )
    result.append( nameb_Ct )
    result.append( body_Ct )
    result.append( nameu_Ct )
    return result
    # return [namefl_Ct[2], namefr_Ct[2], namebl_Ct[2], namebr_Ct[2]]


def translate_part( name = '', suffix = '', obj = '', objConstrain = True, parent = '', translations = [0, 0, 1], X = 1, shape = 'facetYup_ctrl', color = 'yellow' ):
    '''
    doors and things
    rotations = [0, 0, 1] : ( x, y, z )
    '''
    #
    if suffix:
        suffix = '_' + suffix

    # obj
    name = name + suffix
    name_Ct = place.Controller2( name, obj, True, shape, X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name_Ct[0], CONTROLS() )
    if objConstrain:
        cmds.parentConstraint( name_Ct[4], obj, mo = True )
    if parent:
        cmds.parentConstraint( parent, name_Ct[0], mo = True )
    # lock translation
    place.rotationLock( name_Ct[2], True )
    if translations[0]:
        place.translationXLock( name_Ct[2], False )
    if translations[1]:
        place.translationYLock( name_Ct[2], False )
    if translations[2]:
        place.translationZLock( name_Ct[2], False )

    return name_Ct


def rotate_part( name = '', suffix = '', obj = '', objConstrain = True, parent = '', rotations = [0, 0, 1], X = 1, shape = 'facetYup_ctrl', color = 'yellow' ):
    '''
    doors and things
    rotations = [0, 0, 1] : ( x, y, z )
    '''
    #
    if suffix:
        suffix = '_' + suffix

    # obj
    name = name + suffix
    name_Ct = place.Controller2( name, obj, True, shape, X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
    cmds.parent( name_Ct[0], CONTROLS() )
    if objConstrain:
        cmds.parentConstraint( name_Ct[4], obj, mo = True )
    if parent:
        cmds.parentConstraint( parent, name_Ct[0], mo = True )
    # lock translation
    place.translationLock( name_Ct[2], True )
    # lock all rotations, unlock one at a time
    place.rotationLock( name_Ct[2], True )
    if rotations[0]:
        place.rotationXLock( name_Ct[2], False )
    if rotations[1]:
        place.rotationYLock( name_Ct[2], False )
    if rotations[2]:
        place.rotationZLock( name_Ct[2], False )

    return name_Ct


def blend_part( obj = '' ):
    '''
    given object create a duplicate and wrap original to dup
    '''
    # print( obj )
    if ':' in obj:
        obj_strip = obj.split( ':' )[0]
    dup = cmds.duplicate( obj, name = obj_strip + '_rigDup' )[0]
    blnd = cmds.blendShape( dup, obj, name = obj_strip + '_dupBlend' )
    # print( blnd )
    cmds.setAttr( blnd[0] + '.' + dup, 1 )
    cmds.setAttr( dup + '.visibility', 0 )
    return dup


def passengers( visObj = '', positions = [], X = 1.0 ):
    '''
    add 6 controls, 3 front, 3 back
    top group to chassis jnt
    add parent switch to each position
    '''
    place.optEnum( visObj, attr = 'passengerControls', enum = 'VIS' )
    #
    if not positions:
        positions = [
        'passenger_front_C_jnt',
        'passenger_back_C_jnt',
        'passenger_front_L_jnt',
        'passenger_back_L_jnt',
        'passenger_front_R_jnt',
        'passenger_back_R_jnt'
        ]
    # fix mirror, otherwise controller is upside down
    for p in positions:
        if '_R_' in p:
            cmds.setAttr( p + '.jointOrientX', 0 )
    # needs to be same order as positions
    attrsNew = [
    'front_C',
    'back_C',
    'front_L',
    'back_L',
    'front_R',
    'back_R'
    ]
    #
    sizeplus = 0.01
    j = 0
    for p in positions:
        if cmds.objExists( p ):
            color = 'yellow'
            if '_L' in p:
                color = 'blue'
            if '_R' in p:
                color = 'red'
            #
            name = p.replace( '_jnt', '' )
            p_Ct = place.Controller2( name, p, True, 'ballRoll_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
            place.cleanUp( p_Ct[0], Ctrl = True )
            place.hijackVis( p_Ct[0], visObj, name = attrsNew[j], suffix = False, default = None, mode = 'visibility' )
            # position switches
            place.optEnum( p_Ct[2], attr = 'positions', enum = 'CONTROL' )
            for jnt in positions:
                cmds.parentConstraint( jnt, p_Ct[0], mo = False )
            con = cn.getConstraint( p_Ct[0], nonKeyedRoute = False, keyedRoute = False, plugRoute = True )[0]
            attrs = cmds.listAttr( con, ud = True )
            i = 0
            for attr in attrs:
                attrNew = attrsNew[i]
                if j == i:
                    place.hijackAttrs( con, p_Ct[2], attr, attrNew, set = True, default = 1, force = True )
                else:
                    place.hijackAttrs( con, p_Ct[2], attr, attrNew, set = True, default = 0, force = True )
                cmds.addAttr( p_Ct[2] + '.' + attrNew, e = True, max = 1 )
                cmds.addAttr( p_Ct[2] + '.' + attrNew, e = True, min = 0 )
                i = i + 1
            # attrs = place.hijackCustomAttrs( con, p_Ct[2] )
            # place.addAttribute( p_Ct[2], vis_attr, 0, 1, False, 'long' )
            X = X + ( X * sizeplus )
        else:
            message( 'position doesnt exist: ' + p, warning = True )
        j = j + 1


def __________________WHEEL():
    pass


def wheel( master_move_controls = [], axle = '', steer = '', center = '', bottom = '', top = '', spin = '', tire_geo = [], rim_geo = [], caliper_geo = [], name = '', suffix = '', X = 1.0, exp = True, pressureMult = 0.3 ):
    '''
    create wheel rig
    - translation based rotation
    - inflattion / deflation
    - steering
    inputs
    - 2 pre-existing controls = master_move_controls -- vehicle_master(), list may have more, but only need the first 2
    - master                  = 'WHEEL_SPACE' group is constrained to this object, 'contact' control lives inside 
    - move                    = axle joint and steering controls get constrained to this object
    - jnts                    = axle, steer, center, bottom, top, spin
    - geo                     = tire_geo, rim_geo, caliper_geo
    - naming strings          = name, suffix
    - controller size         = X
    
    '''

    colorName = ''
    # side
    if 'L' in suffix:
        colorName = 'blue'
        ctrlShp = 'shldrL_ctrl'
    elif 'R' in suffix:
        colorName = 'red'
        ctrlShp = 'shldrR_ctrl'
    else:
        colorName = 'yellow'
        ctrlShp = 'shldrL_ctrl'

    if suffix:
        sffx = '_' + suffix
    else:
        sffx = suffix

    # position
    position = ''
    split_c = center.split( '_' )
    for c in split_c:
        if 'front' in c:
            position = c
        elif 'back' in c:
            position = c

    CONTROLS = '___CONTROLS'
    master = master_move_controls[0]
    move = master_move_controls[1]
    #
    WHEEL_GRP = cmds.group( name = name + sffx + '_AllGrp', em = True )
    # cmds.parentConstraint( move, WHEEL_GRP, mo = True )
    # cmds.parent( WHEEL_GRP, CONTROLS )
    place.cleanUp( WHEEL_GRP, Ctrl = True )
    # return
    # tire has to be facing forward in Z
    tire_p = tire_geo[0]  # test
    clstr = tire_pressure( obj = tire_p, center = center, name = name, suffix = suffix, pressureMult = pressureMult )
    # geo cleanup
    place.cleanUp( tire_p, World = True )

    if tire_p:
        cmds.connectAttr( spin + '.rotateX', tire_p + '.rotateX' )

    # rim, change to skin
    if rim_geo:
        skin( spin, rim_geo )
    # caliper, skin if exists
    if caliper_geo:
        skin( center, caliper_geo )

    # root
    if move:
        cmds.parentConstraint( move, axle, mo = True )

    # wheels shouldnt spin when master is moved, use drive / move control
    WHEEL_SPACE = 'WHEEL_SPACE'
    if not cmds.objExists( WHEEL_SPACE ):
        WHEEL_SPACE = cmds.group( name = WHEEL_SPACE, em = True )
        cmds.parent( WHEEL_SPACE, CONTROLS )
        cmds.parentConstraint( master, WHEEL_SPACE, mo = True )

    # contact # wheel spin derived from top group node of this control
    Contact = name + '_contact' + sffx
    contact = place.Controller( Contact, bottom, False, 'squareYup_ctrl', X * 6, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    ContactCt = contact.createController()
    # cmds.setAttr( ContactCt[0] + '.visibility', 0 )
    cmds.parent( ContactCt[0], WHEEL_SPACE )
    cmds.parentConstraint( steer, ContactCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( ContactCt[2], [True, False], [True, False], [True, False], [True, False, False] )

    # live radius
    g = cmds.group( name = name + '_Radius' + sffx + '_Grp', em = True )
    cmds.parent( g, WHEEL_GRP )
    cmds.setAttr( g + '.visibility', 0 )
    #
    r1 = place.loc( name + '_radius1' + sffx )[0]
    cmds.select( r1, spin )
    anm.matchObj()
    cmds.parent( r1, g )
    #
    r2 = place.loc( name + '_radius2' + sffx )[0]
    cmds.select( r2, top )
    anm.matchObj()
    cmds.parent( r2, g )
    #
    dsp.distance( obj1 = r1, obj2 = r2 )

    # center / pressure
    Pressure = name + '_pressure' + sffx
    pressure = place.Controller( Pressure, center, False, 'diamond_ctrl', X * 8, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    PressureCt = pressure.createController()
    cmds.parent( PressureCt[0], WHEEL_GRP )
    cmds.parentConstraint( PressureCt[4], center, mo = True )
    cmds.parentConstraint( ContactCt[4], PressureCt[0], mo = True )
    # math node
    mltp = cmds.shadingNode( 'multiplyDivide', au = True, n = PressureCt[2] + '_mltp_ty' )
    cmds.setAttr( mltp + '.operation', 1 )  # multiply
    cmds.setAttr( mltp + '.input2Y', -1 )
    # connect
    cmds.connectAttr( PressureCt[2] + '.translateY', mltp + '.input1Y' )
    cmds.connectAttr( mltp + '.outputY', clstr + '.translateY' )
    # sidewall
    place.optEnum( PressureCt[2], attr = 'Tire', enum = 'CONTROL' )
    place.addAttribute( [PressureCt[2]], ['sidewallFlex'], -1, 1, True, attrType = 'float' )
    cmds.connectAttr( PressureCt[2] + '.sidewallFlex', clstr + '.translateX' )

    # spin
    Spin = name + '_spin' + sffx
    spinct = place.Controller( Spin, spin, False, ctrlShp, X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = colorName )
    SpinCt = spinct.createController()
    cmds.parent( SpinCt[0], WHEEL_GRP )
    cmds.parentConstraint( SpinCt[4], spin, mo = True )
    cmds.parentConstraint( PressureCt[4], SpinCt[0], mo = True )
    place.translationLock( SpinCt[2], True )
    place.rotationLock( SpinCt[2], True )
    place.rotationXLock( SpinCt[2], False )
    place.translationLock( SpinCt[3], True )
    place.rotationLock( SpinCt[3], True )
    place.rotationXLock( SpinCt[3], False )
    #
    place.optEnum( SpinCt[2], attr = 'wheelRoll', enum = 'CONTROL' )
    #
    cmds.addAttr( SpinCt[2], ln = 'radius' )
    cmds.setAttr( ( SpinCt[2] + '.radius' ), cb = True )
    cmds.setAttr( ( SpinCt[2] + '.radius' ), keyable = False )
    #
    cmds.addAttr( SpinCt[2], ln = 'roll' )
    cmds.setAttr( ( SpinCt[2] + '.roll' ), cb = True )
    cmds.setAttr( ( SpinCt[2] + '.roll' ), keyable = False )
    #
    place.addAttribute( [SpinCt[2]], ['rollWeight'], 0, 1, True, attrType = 'float' )
    #
    cmds.connectAttr( r1 + '.distance', SpinCt[2] + '.radius' )
    # cmds.connectAttr( SpinCt[2] + '.roll', SpinCt[1] + '.rotateX' )
    place.smartAttrBlend( master = SpinCt[2], slave = SpinCt[1], masterAttr = 'roll', slaveAttr = 'rotateX', blendAttrObj = SpinCt[2], blendAttrString = 'rollWeight', blendWeight = 0.0, reverse = False, blendAttrExisting = True )
    #
    if exp:
        wheel_exp( ctrl = ContactCt[0] )

    return [steer, ContactCt, PressureCt]


def wheel_roll_math( name = 'pathRadius1', distanceObjAttr = 'onPath_front.pathTraveled', radiusObjAttr = 'onPath_front.wheelRadius', outputObjAttr = 'onPath_front.wheelRoll', outputObjModAttr = 'onPath_front.wheelRollModulus' ):
    '''
    create nodes to calculate wheel rotation
    # ( ( $distance / ( pi2 * base_TopGrp.Radius ) ) * 360.0 ) # ROLL FORMULA
    '''
    #
    pi2 = 6.283185
    radiusPi2 = cmds.shadingNode( 'multDoubleLinear', name = name + '__radiusPi2_mult', asUtility = True )
    cmds.setAttr( radiusPi2 + '.input2', pi2 )
    cmds.connectAttr( radiusObjAttr, radiusPi2 + '.input1' )
    #
    radis = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '__distanceTraveled_radiusPi2_div' )
    cmds.setAttr( radis + '.operation', 2 )  # divide
    cmds.connectAttr( distanceObjAttr, radis + '.input1X' )
    cmds.connectAttr( radiusPi2 + '.output', radis + '.input2X' )
    #
    mlt360 = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + '__mlt360_mult' )
    cmds.connectAttr( radis + '.outputX', mlt360 + '.input1' )
    cmds.setAttr( mlt360 + '.input2', 360 )
    # output
    cmds.connectAttr( mlt360 + '.output', outputObjAttr )
    if outputObjModAttr:
        modulus_node( name = name, objectAttrDvdnd = outputObjAttr, objectAttrRmndr = outputObjModAttr, divisor = 360 )

    return [radiusPi2, radis, mlt360]


def wheel_connect( name = '', suffix = '', axle_jnt = '', master_move_controls = [], pivot_grp = '', tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], pressureMult = 0.03, X = 1.0 ):
    '''
    # expected wheel joint order

    0 = 'axle_front_L_jnt'
    1 = 'wheel_front_steer_L_jnt'
    2 = 'wheel_front_center_L_jnt'
    3 = 'wheel_front_bottom_L_jnt'
    4 = 'tire_width_front_L_jnt'
    5 = 'wheel_front_top_L_jnt'
    6 = 'wheel_front_spin_L_jnt'
    7 = 'tire_wall_front_L_jnt'
    '''
    #
    cmds.select( axle_jnt, hi = True )
    j = cmds.ls( sl = True )

    # whl = [steer, ContactCt, CenterCt]
    whl = wheel( master_move_controls = master_move_controls, axle = j[0], steer = j[1], center = j[2], bottom = j[3], top = j[5], spin = j[6],
                     tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, name = name, suffix = suffix, X = X, exp = False, pressureMult = pressureMult )
    place.translationYLock( whl[1][2], False )
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( name + '_contactLock_' + suffix, whl[1][2], whl[1][1], whl[1][0], j[1], pivot_grp, True, False, False, True, 'pivot', 1.0 )
    place.breakConnection( whl[1][1], 'tx' )
    place.breakConnection( whl[1][1], 'tz' )
    # steer
    if 'front' in name:
        cmds.orientConstraint( master_move_controls[2], j[1], mo = True )
        place.breakConnection( j[1], 'rx' )
        place.breakConnection( j[1], 'rz' )
    # whl   = [steer, ContactCt, CenterCt]
    place.smartAttrBlend( master = whl[2][2], slave = pivot_grp, masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
    place.smartAttrBlend( master = whl[2][2], slave = whl[1][1], masterAttr = 'translateY', slaveAttr = 'translateY', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )


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


def __________________TIRE():
    pass


def tire_circle( obj = '', name = '', radius = 1.0, width = 1.0 ):
    '''
    # create circles
    # loft
    # nurbs to proxy
    # wrap deform tire objects
    # scale proxy tire, temp
    # create lattice
    # remove scale from proxy tire
    '''
    c = place.circle( name = name, obj = obj, sections = 8, degree = 3, normal = ( 1, 0, 0 ), orient = True, colorName = 'yellow' , radius = 1.0 )[0]
    c_shape = cmds.listRelatives( c )[0]
    c_input = cmds.listConnections( c_shape )[0]
    # print( c_input )
    place.hijackAttrs( c_input, c, 'radius', 'radius', set = True, default = radius, force = True )
    # print( c, c_shape )
    cmds.parent( c, obj )
    cmds.setAttr( c + '.tx', width )
    return c


def tire_curves( position = '', side = '', suffix = '', mirror = False ):
    '''
    create tire from joint info
    suffix = for additional tires on same position, ie, cement trucks have double tires in the back
    '''

    # print( position, side )
    # wheel joints
    wheel_center = 'wheel' + suffix + '_' + position + '_center_' + side + '_jnt'
    wheel_bottom = 'wheel' + suffix + '_' + position + '_bottom_' + side + '_jnt'
    tire_width = 'tire' + suffix + '_width_' + position + '_' + side + '_jnt'
    tire_wall = 'tire' + suffix + '_wall_' + position + '_' + side + '_jnt'

    # joint feedback

    r = cmds.getAttr( wheel_bottom + '.ty' ) * -1
    h = cmds.getAttr( tire_width + '.tx' )  # multiply by 4, shape requires it
    t = cmds.getAttr( tire_wall + '.ty' ) * -1

    if side == 'R':
        r = r * -1
        h = h * -1
        t = t * -1

    # names
    GRP = 'wheel' + suffix + '_' + position + '_' + side + '_CrvGrp'
    crvs = []
    c0 = 'tire' + suffix + '_crv0_' + position + '_' + side
    c1 = 'tire' + suffix + '_crv1_' + position + '_' + side
    c2 = 'tire' + suffix + '_crv2_' + position + '_' + side
    c3 = 'tire' + suffix + '_crv3_' + position + '_' + side
    c11 = 'tire' + suffix + '_crv11_' + position + '_' + side
    c22 = 'tire' + suffix + '_crv22_' + position + '_' + side
    c33 = 'tire' + suffix + '_crv33_' + position + '_' + side
    crvs_mirror = [c0, c1, c2, c3]
    # qualify
    if not cmds.objExists( c0 ):
        # curve group
        GRP = cmds.group( name = GRP, em = True )
        cmds.pointConstraint( wheel_center, GRP, mo = False )
        place.cleanUp( GRP, World = True )
        # curves
        c0 = tire_circle( obj = wheel_center, name = c0, radius = r, width = 0.0 )
        c1 = tire_circle( obj = wheel_center, name = c1, radius = r, width = h * 0.75 )
        c2 = tire_circle( obj = wheel_center, name = c2, radius = r, width = h )
        c3 = tire_circle( obj = wheel_center, name = c3, radius = t, width = h )
        # inside duplicates
        c11 = tire_circle( obj = wheel_center, name = c11, radius = r, width = h * 0.75 )
        cmds.setAttr( c11 + '.visibility', 0 )
        place.smartAttrBlend( master = c1, slave = c11, masterAttr = 'translateX', slaveAttr = 'translateX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
        place.smartAttrBlend( master = c1, slave = c11, masterAttr = 'radius', slaveAttr = 'radius', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        c22 = tire_circle( obj = wheel_center, name = c22, radius = r, width = h )
        cmds.setAttr( c22 + '.visibility', 0 )
        place.smartAttrBlend( master = c2, slave = c22, masterAttr = 'translateX', slaveAttr = 'translateX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
        place.smartAttrBlend( master = c2, slave = c22, masterAttr = 'radius', slaveAttr = 'radius', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        c33 = tire_circle( obj = wheel_center, name = c33, radius = t, width = h )
        cmds.setAttr( c33 + '.visibility', 0 )
        place.smartAttrBlend( master = c3, slave = c33, masterAttr = 'translateX', slaveAttr = 'translateX', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = True )
        place.smartAttrBlend( master = c3, slave = c33, masterAttr = 'radius', slaveAttr = 'radius', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False )
        #
        crvs = [c3, c2, c1, c0, c11, c22, c33]
        for crv in crvs:
            cmds.parent( crv, GRP )
        #
        if mirror:
            # return
            if side == 'R':
                tire_mirror_curves( get_side = 'L', crvs = crvs_mirror )
            else:
                tire_mirror_curves( get_side = 'R', crvs = crvs_mirror )
    else:
        # print( 'ALREADY EXISTS   ', c0 )
        place.cleanUp( GRP, World = True )
        crvs = [c3, c2, c1, c0, c11, c22, c33]  # return already existing curves
    return crvs


def tire_mirror_curves( get_side = 'L', crvs = [] ):
    '''
    
    '''
    radius = '.radius'
    tx = '.tx'
    side = ''
    if get_side == 'L':
        side = 'R'
    else:
        side = 'L'
    for crv in crvs:
        crv_other = crv.replace( side, get_side )
        x = cmds.getAttr( crv_other + tx )
        r = cmds.getAttr( crv_other + radius )
        cmds.setAttr( crv + tx, x )
        cmds.setAttr( crv + radius, r )


def tire_proxy2( position = '', side = '', suffix = '', crvs = [] ):
    '''
    create tire from joint info
    '''
    # loft
    lofted = cmds.loft( crvs, name = 'lofted' + suffix + '_' + position + '_' + side, degree = 1 )  # [u'lofted_front_L', u'loft1']
    place.cleanUp( lofted[0], World = True )
    cmds.select( lofted[0] )
    cmds.xform( cpc = True, p = True )  # center pivot doesnt work unless object is visible
    cmds.setAttr( lofted[0] + '.visibility', 0 )
    # convert to poly
    loftedPoly = cmds.nurbsToPoly( lofted[0], name = 'lofted' + suffix + '_poly_' + position + '_' + side, ch = True, polygonType = 1, polygonCount = 800, format = 0 )  # [u'lofted_poly_front_L', u'nurbsTessellate1']
    place.cleanUp( loftedPoly[0], World = True )
    cmds.select( loftedPoly[0] )
    cmds.xform( cpc = True, p = True )  # center pivot doesnt work unless object is visible
    cmds.setAttr( loftedPoly[0] + '.visibility', 0 )
    tire_proxy = loftedPoly[0]

    return [tire_proxy, lofted[0]]


def tire_wrap( master = '', slaves = [] ):
    '''
    wrap deform slaves with master
    '''
    wraps = []
    for slave in slaves:
        n = wrp.wrapDeformer( master = master, slave = slave )
        wraps.append( n )
    return wraps


def tire_proxy( position = '', side = '', tire_geo = [] ):
    '''
    create tire from joint info
    '''
    # print( position )
    # wheel joints
    wheel_center = 'wheel_' + position + '_center_' + side + '_jnt'
    wheel_bottom = 'wheel_' + position + '_bottom_' + side + '_jnt'
    tire_width = 'tire_width_' + position + '_' + side + '_jnt'
    tire_wall = 'tire_wall_' + position + '_' + side + '_jnt'
    # joint feedback
    r = cmds.getAttr( wheel_bottom + '.ty' ) * -1
    h = cmds.getAttr( tire_width + '.tx' )  # multiply by 4, shape requires it
    t = cmds.getAttr( tire_wall + '.ty' )
    if side == 'R':
        r = r * -1
        h = h * -1
        t = t * -1
    # tire proxy
    tire = cmds.polyPipe( name = 'tire_proxy_' + position + '_' + side, ax = [1, 0, 0], sa = 50, sc = 4, sh = 6, r = r, h = h * 4, t = t )
    cmds.setAttr( tire[0] + '.visibility', 0 )
    # return
    # print( tire )
    # position
    sel = cmds.ls( sl = 1 )
    cmds.select( tire[0], wheel_center )
    pos = cmds.xform( wheel_center, q = True, ws = True, rp = True )
    cmds.xform( tire[0], ws = True, t = pos )
    # anm.matchObj()
    # return
    cmds.select( sel )
    # wrap deformer
    wraps = []
    base = []
    i = 0
    for geo in tire_geo:
        n = wrp.wrapDeformer( master = tire[0], slave = geo )
        if i == 0:
            b = tire[0] + 'Base'
            cmds.setAttr( b + '.visibility', 0 )
            base.append( tire[0] + 'Base' )
        else:
            b = tire[0] + 'Base' + str( i )
            cmds.setAttr( b + '.visibility', 0 )
            base.append( tire[0] + 'Base' + str( i ) )
        wraps.append( n )
        i = i + 1

    return [tire[0], base, wraps]


def tire_pressure( obj = '', center = '', name = '', suffix = '', lattice = ( 2, 29, 5 ), pressureMult = 0.3, distortionRows = 6 ):
    '''
    add tire pressure behaviour
    lattice = object local space (X, Y, Z)
    distortion rows = hack, starting from center row, higher number removes more rows from calculation, higher number better for short tire wall
    '''
    # group
    g = cmds.group( name = name + '_clusterGrp_' + suffix, em = True )
    # g = place.null2( name + '_clusterGrp_' + suffix, center, orient = False )[0]
    cmds.parent( g, '___CONTROLS' )
    cmds.setAttr( g + '.visibility', 0 )
    # return
    # store selection
    sel = cmds.ls( sl = 1 )
    # lattice
    cmds.select( obj )
    # [u'wheel_front_lattice_L_', u'wheel_front_lattice_L_Lattice', u'wheel_front_lattice_L_Base']
    result = cmds.lattice( name = name + '_ltc_' + suffix + '_', dv = lattice, oc = True, outsideLattice = 1 )
    # return
    # result[0] is a component apparently, cant be parented
    cmds.parent( result[1], '___WORLD_SPACE' )
    cmds.parent( result[2], '___WORLD_SPACE' )
    # return
    cmds.setAttr( result[1] + '.visibility', 0 )
    cmds.setAttr( result[2] + '.visibility', 0 )
    # print( result )
    # clusters
    clusters = []
    ltc = result[1]
    depth = lattice[0]  # X
    row = ( lattice[1] - 1 ) / 2  # Y
    column = lattice[2]  # Z
    for i in range( int( row ) ):  # depth
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
    # return
    # parent clusters
    cmds.parent( clusters, g )
    cmds.parent( c, g )
    # connect to rig
    cmds.parentConstraint( center, g, mo = True )

    # translate y math nodes
    point_A = cmds.xform( clusters[0], query = True, ws = True, rp = True )
    point_B = cmds.xform( clusters[1], query = True, ws = True, rp = True )
    lattice_row_gap = place.distance2Pts( point_A, point_B )  # guess, should find a way to measure it
    # print( lattice_row_gap )
    cls = int( len( clusters ) / 2 ) - distortionRows  # len( clusters ) - 1
    # print( 'rows', cls )
    for i in range( cls ):
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
    weight = pressureMult
    weight_add = pressureMult * 0.5
    cls = int( len( clusters ) / 2 ) - distortionRows
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
    weight = lattice_row_gap
    weight_add = lattice_row_gap * 0.5
    cls = int( len( clusters ) / 2 ) - distortionRows
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


def __________________DYNAMIC():
    pass


def dynamic_target( name = 'chassis', root = 'root_jnt', target = 'up_jnt', front = 'front_jnt', constrainObj = 'chassis_jnt', parentObj = 'move_Grp', attrObj = 'move', aim = [0, 1, 0], up = [0, 0, 1], X = 10.0 ):
    '''
    name          = chassis      string
    root          = root_jnt,    crv start
    target        = up_jnt,      crv end, aim vector
    front         = front_jnt,   up vector
    constrainObj  = chassis_jnt, object to aim at target
    parentObj     = move_Grp,    parent of dynamics
    attrObj       = move,        objects receives dynamic attributes
    X             = 10.0         scale of controls
    '''
    # curve
    crv = dnm.makeCurve( start = root, end = target, name = name + '_crv', points = 4 )

    # aim control
    base = name + '_dynamicBase'
    base_Ct = place.Controller2( base, root, True, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( base_Ct[0], CONTROLS() )
    cmds.setAttr( base_Ct[0] + '.visibility', 0 )
    cmds.parentConstraint( base_Ct[4], constrainObj, mo = True )
    # limit enable
    cmds.transformLimits( base_Ct[1], rx = [-10, 10.0], erx = [1, 1] )
    cmds.transformLimits( base_Ct[1], rz = [-10, 10], erz = [1, 1] )
    # cmds.parentConstraint( parentObj, base_Ct[0], mo = True )
    # aim control
    a = name + '_dynamicTarget'  ###### control needs to be in world space
    aim_Ct = place.Controller2( a, target, True, 'diamondYup_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( aim_Ct[0], WORLD_SPACE() )  # to world, add scale constraint, is attached to motion path, needs to stay in world space
    place.rotationLock( aim_Ct[2], True )
    place.scaleUnlock( aim_Ct[0] )
    # add limit attrs for base # slave, master
    misc.optEnum( aim_Ct[2], attr = 'chassisDynamicRoll', enum = 'LIMIT' )
    minrxl = 'minRotXLimit'
    c_back = 'back'
    maxrxl = 'maxRotXLimit'
    c_front = 'front'
    minrzl = 'minRotZLimit'
    c_left = 'left'
    maxrzl = 'maxRotZLimit'
    c_right = 'right'
    m = 'Mstr'
    place.hijackAttrs( base_Ct[1], aim_Ct[2], minrxl, c_back, set = True, default = -3, force = True )
    place.hijackAttrs( base_Ct[1], aim_Ct[2], maxrxl, c_front, set = True, default = 3, force = True )
    place.hijackAttrs( base_Ct[1], aim_Ct[2], minrzl, c_left, set = True, default = -5, force = True )
    place.hijackAttrs( base_Ct[1], aim_Ct[2], maxrzl, c_right, set = True, default = 5, force = True )
    cmds.addAttr( aim_Ct[2] + '.' + c_back, e = True, max = 0 )
    cmds.addAttr( aim_Ct[2] + '.' + c_front, e = True, min = 0 )
    cmds.addAttr( aim_Ct[2] + '.' + c_left, e = True, max = 0 )
    cmds.addAttr( aim_Ct[2] + '.' + c_right, e = True, min = 0 )
    # up control
    u = name + '_dynamicUp'
    up_Ct = place.Controller2( u, front, True, 'loc_ctrl', X, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'hotPink' ).result
    cmds.parent( up_Ct[0], CONTROLS() )
    # cmds.parentConstraint( parentObj, up_Ct[0], mo = True )
    # move for stability
    point_A = cmds.xform( aim_Ct[0], query = True, ws = True, rp = True )
    point_B = cmds.xform( base_Ct[0], query = True, ws = True, rp = True )
    d = place.distance2Pts( point_A, point_B )
    cmds.setAttr( up_Ct[1] + '.translateZ', d * 10 )
    cmds.setAttr( up_Ct[0] + '.visibility', 0 )

    # constrain base to target
    aimCon = cmds.aimConstraint( aim_Ct[4], base_Ct[1], wut = 'object', wuo = up_Ct[4], aim = aim, u = up, mo = True )[0]
    place.attr_easeInto_Limits( name = 'dynamic', masterAttr = aimCon + '.constraintRotateX', slaveAttr = base_Ct[1] + '.rotateX', maxAttr = aim_Ct[2] + '.' + c_front, minAttr = aim_Ct[2] + '.' + c_back )  # front back
    place.attr_easeInto_Limits( name = 'dynamic', masterAttr = aimCon + '.constraintRotateZ', slaveAttr = base_Ct[1] + '.rotateZ', maxAttr = aim_Ct[2] + '.' + c_right, minAttr = aim_Ct[2] + '.' + c_left )  # left right

    # attach aim
    mp = dnm.attachObj( obj = aim_Ct[0], upObj = up_Ct[4], crv = crv, position = 1.0 )
    # return

    # make dynamic
    # [ follicle_Grp, dynGrp, sharedDynGrp ]
    grps = dnm.makeDynamic( parentObj = '', attrObj = aim_Ct[2], mstrCrv = crv )
    follicle_Grp = grps[0]
    # place.cleanUp( grps[1], World = True )
    place.cleanUp( grps[2], World = True )

    return [base_Ct, aim_Ct, up_Ct, follicle_Grp ]


def dynamic_tire_pressure():
    '''
    
    '''
    # main attr
    attrObj = 'chassis_dynamicTarget'
    attr = 'dynamicPressure'

    # chassis drives wheel
    chassis = 'chassis_dynamicBase_CtGrp'  # rx = front/back, rz = left/right
    # wheel drives next 3 groups
    wheel = 'wheel_front_pressure_L_CtGrp'
    place.smartAttrBlend( master = chassis, slave = wheel, masterAttr = 'rx', slaveAttr = 'ty', blendAttrObj = attrObj, blendAttrString = attr, blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = chassis, slave = wheel, masterAttr = 'rz', slaveAttr = 'ty', blendAttrObj = attrObj, blendAttrString = attr, blendWeight = 1.0, reverse = False )

    #
    pivot = 'chassis_front_L_pivot_Grp'
    cluster = 'wheel_front_clstr_0_L_Handle'  # reverse
    contact = 'wheel_front_contact_L_CtGrp'  # reverse
    place.smartAttrBlend( master = wheel, slave = pivot, masterAttr = 'ty', slaveAttr = 'ty', blendAttrObj = attrObj, blendAttrString = attr, blendWeight = 1.0, reverse = False )  # causes cycle
    place.smartAttrBlend( master = wheel, slave = cluster, masterAttr = 'ty', slaveAttr = 'ty', blendAttrObj = attrObj, blendAttrString = attr, blendWeight = 1.0, reverse = True )
    place.smartAttrBlend( master = wheel, slave = contact, masterAttr = 'ty', slaveAttr = 'ty', blendAttrObj = attrObj, blendAttrString = attr, blendWeight = 1.0, reverse = True )


def __________________PATH():
    pass


def path( points = 5, X = 0.05, length = 10.0, deviationLayers = 2, layers = 3 ):
    '''
    # creates groups and master controller from arguments specified as 'True'
    segment = 4 points
    deviationLayers = deviating curve layers, for back wheels, n layers == n curves
    layers = control layers
    
    '''
    #
    if points < 4:
        message( 'Points variable should be higher than 3.' )
        return None
    #
    PreBuild = place.rigPrebuild( Top = 4, Ctrl = True, SknJnts = False, Geo = False, World = True, Master = True, OlSkool = False, Size = 150 * X )
    #
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    WORLD_SPACE = PreBuild[2]
    MasterCt = PreBuild[3]
    #
    pathDeviate = 'pathDeviate'
    misc.optEnum( MasterCt[2], attr = 'path', enum = 'OPTNS' )
    misc.addAttribute( [MasterCt[2]], [pathDeviate], 0, 0.5, False, 'float' )
    cmds.setAttr( MasterCt[2] + '.' + pathDeviate , cb = False )
    # cmds.setAttr( MasterCt[2] + '.' + pathDeviate, 0.2 )
    # cmds.setAttr( MasterCt[2] + '.overrideColor', 23 )

    # up
    upCnt = place.Controller( place.getUniqueName( 'up' ), 'master', orient = True, shape = 'loc_ctrl', size = 60 * X, color = 17, setChannels = True, groups = True )
    upCntCt = upCnt.createController()
    place.cleanUp( upCntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCntCt[0] + '.ty', length * 100 )
    cmds.setAttr( upCntCt[0] + '.visibility', 0 )
    cmds.parentConstraint( 'master_Grp', upCntCt[0], mo = True )

    #
    path = place.getUniqueName( 'path' )

    # layers
    cluster_layers = []
    paths = []
    crvInfo = None
    layer = 0
    while layer < deviationLayers:
        # build curve
        lengthSeg = length / ( points + layer - 1.0 )
        i = 1
        p = '[( 0, 0, -1.128 )'
        while i < points + layer:
            p = p + ',( 0, 0,' + str( lengthSeg * i ) + ')'
            i = i + 1
        p = p + ']'
        # print( p )
        pth = cmds.curve( n = path + '_layer_' + pad_number( i = layer ), d = 3, p = eval( p ) )
        if layer == 0:
            crvInfo = cmds.arclen( pth, ch = True, n = ( pth + '_arcLength' ) )
            #
            # crvLength = cmds.getAttr(crvInfo + '.arcLength')
            # dvd = cmds.shadingNode('multiplyDivide', au=True, n=(curve + '_scale'))
            #
        # cmds.setAttr( pth + '.visibility', 0 )
        # print( pth )
        paths.append( pth )
        # return
        cmds.setAttr( pth + '.template', 1 )
        place.cleanUp( pth, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cl = place.clstrOnCV( pth, 'layer' + pad_number( i = layer ) + '_Clstr' )
        # cleanup clusters and controllers
        cGrp = 'clstr_' + pad_number( i = layer ) + '_Grp'
        cmds.group( cl, n = cGrp, w = True )
        cmds.setAttr( cGrp + '.visibility', 0 )
        place.cleanUp( cGrp, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cluster_layers.append( cl )
        layer = layer + 1
        if layer != deviationLayers and layer != 1:
            cmds.setAttr( pth + '.visibility', 0 )
    # print( paths )
    for l in range( len( cluster_layers ) - 1 ):
        # constrain start, end
        c = 0
        for c in range( len( cluster_layers[l + 1] ) - 0 ):
            # print( '____', c )
            # first
            if c == 0:
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
            # last
            elif cluster_layers[l + 1][c] == cluster_layers[l + 1][-1]:
                cmds.parentConstraint( cluster_layers[l][-1], cluster_layers[l + 1][c], mo = False )
                break
            else:
                constraint = cmds.parentConstraint( cluster_layers[l][c - 1], cluster_layers[l + 1][c], mo = False )[0]
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
                place.hijackConstraints( master = MasterCt[2], attr = pathDeviate, value = 0.5, constraint = constraint )
            c = c + 1
    '''
    # place Controls on Clusters and Constrain
    color = 9
    i = 1
    Ctrls = []
    CtrlsFull = []
    CtrlGrps = []
    for handle in cluster_layers[0]:
        #
        cnt = place.Controller( 'point' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ), handle, orient = False, shape = 'splineStart_ctrl', size = 60 * X, color = color, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'brown' )
        cntCt = cnt.createController()
        # cmds.setAttr( handle + '.visibility', 0 )
        cmds.parentConstraint( MasterCt[4], cntCt[0], mo = True )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        CtrlsFull.append( cntCt )
        Ctrls.append( cntCt[2] )
        CtrlGrps.append( cntCt[4] )
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1

    # guides
    guideGp = cmds.group( em = True, name = 'path_guideGrp' )
    for i in range( len( CtrlGrps ) - 1 ):
        gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
        place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
        cmds.parent( gd[0], guideGp )
        cmds.parent( gd[1], guideGp )
        place.cleanUp( guideGp, World = True )'''

    Ctrls = path_control_layers( clusters = cluster_layers[0], layers = layers, parent = MasterCt, X = X )
    # return

    # path
    s = 0.0
    travel = 'travel'
    spacing = 'offset'
    frontTwist = 'frontTwist'
    upTwist = 'upTwist'
    sideTwist = 'sideTwist'
    wheelRadius = 'wheelRadius'
    pathLength = 'pathLength'
    pathTraveled = 'pathTraveled'
    wheelRoll = 'wheelRoll'
    wheelRollMod = 'wheelRollModulus'
    wheelBase = 'wheelBase'
    msgPths = 'paths'
    msgMp = 'motionPath'
    # vehicle on path, front of vehicle
    opf = 'onPath_front'
    opfCt = place.Controller2( opf, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opfCt[0], World = True )
    # cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True ) # causes double transform
    place.rotationLock( opfCt[2], True )
    place.translationLock( opfCt[2], True )
    misc.optEnum( opfCt[2], attr = 'path', enum = 'CONTROL' )
    misc.addAttribute( [opfCt[2]], [travel], 0.0, 100.0, True, 'float' )
    cmds.setAttr( opfCt[2] + '.' + travel, 0.1 )
    misc.addAttribute( [opfCt[2]], [frontTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + frontTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [upTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + upTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [sideTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + sideTwist , cb = False )
    misc.optEnum( opfCt[2], attr = 'wheelMath', enum = 'COMPUTE' )
    misc.addAttribute( [opfCt[2]], [wheelRadius], 0.001, 1000, False, 'float' )
    # cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.addAttr( opfCt[2], ln = pathLength, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathLength , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathLength , k = False )
    misc.hijackAttrs( opfCt[2], crvInfo, pathLength, 'arcLength', set = False, default = None, force = True )
    cmds.addAttr( opfCt[2], ln = pathTraveled, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRoll, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRollMod, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , k = False )
    # cmds.setAttr( opfCt[2] + '.' + spacing, -0.15 )
    # vehicle on path, back of vehicle
    opb = 'onPath_back'
    opbCt = place.Controller2( opb, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opbCt[0], World = True )
    cmds.addAttr( opbCt[2], ln = msgPths, at = 'message' )
    cmds.addAttr( opbCt[2], ln = msgMp, at = 'message' )
    # cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )  # causes double transform
    place.rotationLock( opbCt[2], True )
    misc.optEnum( opbCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    misc.addAttribute( [opbCt[2]], [pathDeviate], 0, 0.5, True, 'float' )
    cmds.connectAttr( opbCt[2] + '.' + pathDeviate, MasterCt[2] + '.' + pathDeviate, f = True )
    misc.addAttribute( [opbCt[2]], [wheelBase], 0, 1000, True, 'float' )
    misc.addAttribute( [opbCt[2]], [spacing], -100.0, 100.0, True, 'float' )
    cmds.setAttr( opbCt[2] + '.' + wheelBase, 10 )
    # vehicle on path, top of vehicle
    opu = 'onPath_up'
    opuCt = place.Controller2( opu, MasterCt[4], False, 'loc_ctrl', X * 50, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opuCt[0], World = True )
    cmds.setAttr( opuCt[0] + '.ty', X * 100 )
    cmds.setAttr( opuCt[0] + '.visibility', 0 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )
    # aim
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( opfCt[3], True )

    # front - attach to path
    motpth_f = cmds.pathAnimation( opfCt[1], name = 'front_motionPath' , c = paths[0], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_f + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_f + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_f + '.' + sideTwist )
    cmds.setAttr( opfCt[2] + '.' + frontTwist, 180 )
    cmds.setAttr( opfCt[2] + '.' + sideTwist, 90 )
    # back - attach to path
    motpth_b = cmds.pathAnimation( opbCt[1], name = 'back_motionPath' , c = paths[-1], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.addAttr( motpth_b, ln = msgMp, at = 'message' )
    cmds.connectAttr( opbCt[2] + '.' + msgMp, motpth_b + '.' + msgMp )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_b + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_b + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_b + '.' + sideTwist )
    # nodes
    mltNode = cmds.shadingNode( 'multiplyDivide', au = True, n = ( travel + '_MltDv' ) )  # increase travel from (0.0-1.0 to 0.0-10.0)
    cmds.setAttr( ( mltNode + '.operation' ), 1 )  # set operation: 2 = divide, 1 = multiply
    cmds.setAttr( mltNode + '.input2Z', 0.01 )
    # dblLnrNode = cmds.createNode( 'addDoubleLinear', name = ( spacing + '_DblLnr' ) )
    # travel
    cmds.connectAttr( opfCt[2] + '.' + travel, mltNode + '.input1Z' )
    cmds.connectAttr( mltNode + '.outputZ', motpth_f + '.uValue', f = True )
    # spacing
    '''
    cmds.connectAttr( mltNode + '.outputZ', dblLnrNode + '.input2' )
    cmds.connectAttr( opbCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )'''
    # distance traveled
    uvlen = cmds.shadingNode( 'multDoubleLinear', name = 'uValuePathLen_mult', asUtility = True )
    cmds.connectAttr( opfCt[2] + '.pathLength', uvlen + '.input1' )
    cmds.connectAttr( motpth_f + '.uValue', uvlen + '.input2' )
    cmds.connectAttr( uvlen + '.output', opfCt[2] + '.' + pathTraveled )
    # wheel roll
    wheel_roll_math( distanceObjAttr = opfCt[2] + '.' + pathTraveled, radiusObjAttr = opfCt[2] + '.' + wheelRadius, outputObjAttr = opfCt[2] + '.' + wheelRoll )

    # result = wheel base * -1
    whlbf = cmds.shadingNode( 'multDoubleLinear', name = 'whlBase_flip', asUtility = True )
    cmds.connectAttr( opbCt[2] + '.' + wheelBase, whlbf + '.input1' )
    cmds.setAttr( whlbf + '.input2', -1 )
    # result = path traveled + result (result should be negative)
    trvldWhlbs = cmds.createNode( 'addDoubleLinear', name = ( 'whlBase_DblLnr' ) )
    cmds.connectAttr( whlbf + '.output', trvldWhlbs + '.input2' )
    cmds.connectAttr( opfCt[2] + '.' + pathTraveled, trvldWhlbs + '.input1' )
    # result = result / path length
    trvlDv = cmds.shadingNode( 'multiplyDivide', au = True, n = ( 'whlBase_MltDv' ) )
    cmds.setAttr( ( trvlDv + '.operation' ), 2 )  # set operation: 2 = divide, 1 = multiply
    cmds.connectAttr( trvldWhlbs + '.output', trvlDv + '.input1X' )
    cmds.connectAttr( opfCt[2] + '.' + pathLength, trvlDv + '.input2X' )
    # result = result * uValue multiplier
    # whlbMlt = cmds.shadingNode( 'multDoubleLinear', name = 'whlBase_Mlt', asUtility = True )
    dblLnrNode = cmds.createNode( 'addDoubleLinear', name = ( spacing + '_DblLnr' ) )
    cmds.connectAttr( opbCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( trvlDv + '.outputX', dblLnrNode + '.input2' )
    # cmds.connectAttr( mltNode + '.outputZ', whlbMlt + '.input2' )
    # uValue = result # connect
    # cmds.connectAttr( whlbMlt + '.output', motpth_b + '.uValue', f = True )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )

    # smooth display
    cmds.select( paths )
    cmds.displaySmoothness( pointsWire = 32 )

    # message, for switching path connection in script later
    for p in paths:
        shape = path_shape( p )
        cmds.addAttr( shape, ln = msgPths, at = 'message' )
        cmds.connectAttr( opbCt[2] + '.' + msgPths, shape + '.' + msgPths )

    # message for path controllers, meant to attach all controls with geo constraint to ground plane
    msg = 'control'
    cmds.addAttr( MasterCt[2], ln = msg, at = 'message' )
    for g in Ctrls:
        print( g )
        cmds.addAttr( g, ln = msg, at = 'message' )
        cmds.connectAttr( MasterCt[2] + '.' + msg, g + '.' + msg )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    misc.scaleUnlock( opfCt[1], sx = True, sy = True, sz = True )
    misc.scaleUnlock( opbCt[1], sx = True, sy = True, sz = True )
    misc.scaleUnlock( opuCt[1], sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
        cmds.connectAttr( mstr + '.' + uni, opfCt[1] + s )
        cmds.connectAttr( mstr + '.' + uni, opbCt[1] + s )
        cmds.connectAttr( mstr + '.' + uni, opuCt[1] + s )


def path_control_layers( clusters = [], layers = 2, parent = '', X = 1 ):
    '''
    clusters = cluster list to start
    layers = amount of layers in controls, 0 based, ie 2 == 3 layers, [0,1,2]
    segment = amount of controls between each higher layer control ie [6, 3, 2] , every 6 controls on (1st) layer adds a control on parent (2nd) layer 
    parent = top layer parent
    '''
    resultCtrls = []
    # scale
    X = X * 100
    scale_range = 0.25  # 1.0 being final top layer scale, 'X', layer 0 scale = 1.0 - scale_range
    scale_0 = 1.0 - scale_range
    scale_mlt = scale_range / layers
    colors = [ 'lightYellow', 'lightBlue', 'pink', 'hotPink', 'purple']
    # group
    layerGp = cmds.group( em = True, name = 'layer_0_ctrlGrp' )
    place.cleanUp( layerGp, Ctrl = True )
    place.setChannels( layerGp, [True, False], [True, False], [True, False], [True, False, False] )
    # vis
    place.hijackVis( layerGp, parent[2], name = 'ctrlLayer0', suffix = False, default = 0, mode = 'visibility' )
    # layer 0
    layer = 0
    # CtrlsFull_this = []
    # CtrlsFull_next = []
    Ctrls = []
    CtrlGrps = []
    CtrlTopGrps = []
    i = 0
    for handle in clusters:
        #
        name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) )
        cnt = place.Controller( name, handle, orient = False, shape = 'splineStart_ctrl', size = X * 0.25, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = colors[0] )
        cntCt = cnt.createController()
        cmds.parent( cntCt[0], layerGp )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        #
        # CtrlsFull_this.append( cntCt )
        Ctrls.append( cntCt[2] )
        CtrlGrps.append( cntCt[4] )
        CtrlTopGrps.append( cntCt[0] )
        resultCtrls.append( cntCt[2] )
        #
        i = i + 1
    clusters = CtrlTopGrps

    # layer 0 guides
    guideGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_path_guideGrp' )
    place.cleanUp( guideGp, World = True )
    place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
    place.hijackVis( guideGp, parent[2], name = 'ctrlLayer0', suffix = False, default = 1, mode = 'visibility' )
    for i in range( len( CtrlGrps ) - 1 ):
        gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
        #
        cmds.parent( gd[0], guideGp )
        cmds.parent( gd[1], guideGp )
    print( 'result amount, layer 0 ', len( resultCtrls ) )

    # prep for layer loop
    layer = layer + 1
    color = colors[1]
    clr = 1
    shapes = ['splineStart_ctrl', 'splineStart_ctrl']  # ['splineStart_ctrl', 'splineEnd_ctrl']
    shape = shapes[0]
    # add layers
    while layer <= layers:
        # group
        layerGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_ctrlGrp' )
        place.cleanUp( layerGp, Ctrl = True )
        place.setChannels( layerGp, [True, False], [True, False], [True, False], [True, False, False] )
        place.hijackVis( layerGp, parent[2], name = 'ctrlLayer' + str( layer ), suffix = False, default = 1, mode = 'visibility' )
        #
        scale_layer = scale_0 + ( scale_mlt * layer )
        # CtrlsFull_this = []
        # CtrlsFull_next = []
        CtrlGrps = []
        CtrlTopGrps = []
        w = 1.0
        n = 1
        j = 1
        i = 0

        #
        for handle in clusters:
            # next layer start control
            if j == 1:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                s_cntCt = cnt.createController()
                cmds.parent( s_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( s_cntCt )
                CtrlTopGrps.append( s_cntCt[0] )
                CtrlGrps.append( s_cntCt[4] )
                resultCtrls.append( s_cntCt[2] )
                #
                cmds.parentConstraint( s_cntCt[4], handle, mo = True )  # this handle
                if i == 0:
                    cmds.parentConstraint( s_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle, weight as well be 1.0 : weight is normalized to 1.0 between 2 wights
                else:
                    cmds.parentConstraint( s_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                j = j + 1
                n = n + 1
            # next layer end control
            elif j == 3:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                e_cntCt = cnt.createController()
                cmds.parent( e_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( e_cntCt )
                CtrlTopGrps.append( e_cntCt[0] )
                CtrlGrps.append( e_cntCt[4] )
                resultCtrls.append( e_cntCt[2] )
                # previous layer constrain
                cmds.parentConstraint( e_cntCt[4], handle, mo = True )  # this handle
                cmds.parentConstraint( e_cntCt[4], clusters[i - 1], w = w, mo = True )  # last handle
                if i != len( clusters ) - 1:
                    cmds.parentConstraint( e_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                #
                j = j + 1
                n = n + 1
                # return
            # next layer end control
            elif j == 5:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                e_cntCt = cnt.createController()
                cmds.parent( e_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( e_cntCt )
                CtrlTopGrps.append( e_cntCt[0] )
                CtrlGrps.append( e_cntCt[4] )
                resultCtrls.append( e_cntCt[2] )
                # previous layer constrain
                cmds.parentConstraint( e_cntCt[4], handle, mo = True )  # this handle
                cmds.parentConstraint( e_cntCt[4], clusters[i - 1], w = w, mo = True )  # last handle
                if i != len( clusters ) - 1:
                    cmds.parentConstraint( e_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                #
                j = 2
                n = n + 1
            else:
                j = j + 1
            # constrain top layer controls to parent
            if layer == layers:
                cmds.parentConstraint( parent[4], CtrlTopGrps[-1], mo = True )
            i = i + 1

        #
        clusters = CtrlTopGrps
        # guides
        guideGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_path_guideGrp' )
        place.cleanUp( guideGp, World = True )
        place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
        cmds.setAttr( guideGp + '.visibility', 0 )
        # place.hijackVis( guideGp, parent[2], name = 'layer' + str( layer ), suffix = True, default = 1, mode = 'visibility' )
        for i in range( len( CtrlGrps ) - 1 ):
            gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
            cmds.parent( gd[0], guideGp )
            cmds.parent( gd[1], guideGp )
        # prep for next loop
        layer = layer + 1
        if color == colors[-1]:
            color = colors[0]
            clr = 0
        else:
            color = colors[clr + 1]
            clr = clr + 1
        if shape == shapes[0]:
            shape = shapes[1]
        else:
            shape = shapes[0]
    #
    return resultCtrls


def path_shape( curve = '' ):
    '''
    return shape node
    '''
    shapes = cmds.listRelatives( curve, s = 1 )  # s = shapes
    if shapes:
        for s in shapes:
            if 'Orig' not in s:
                return s
    print( 'no shapes found' )
    return None


def path_switch():
    '''
    uses selection
    assumes selection has specific message connections
    '''
    # object on path
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 1:
        sel = sel[0]
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    if 'onPath_back' in sel:
        # motionPath node
        motionPathNode = cmds.listConnections( sel + '.motionPath' )
        if motionPathNode:
            motionPathNode = motionPathNode[0]
        else:
            motionPathNode = None
        # path shape nodes
        pathShapes = cmds.listConnections( sel + '.paths' )
        if pathShapes:
            pathShapes.sort()
        else:
            pathShapes = None
        # current path
        current_path = cmds.listConnections( motionPathNode + '.geometryPath' )
        if current_path:
            current_path = current_path[0]
        else:
            current_path = None
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    # iterate to new
    if motionPathNode and pathShapes and current_path:
        i = 0
        for i in range( len( pathShapes ) ):
            if pathShapes[i] == current_path:
                if i + 1 <= len( pathShapes ) - 1:
                    cmds.connectAttr( pathShapes[i + 1] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[i + 1] )
                else:
                    cmds.connectAttr( pathShapes[0] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[0] )
            else:
                # print( 'no match', pathShapes[i], current_path )
                pass
    else:
        message( 'Connections missing, aborted', warning = True )


def car_to_ground():
    '''
    attach selected namespace(vehicle) to selected ground plane
    '''
    pivots = [
    'chassis_front_L_pivot',
    'chassis_front_R_pivot',
    'chassis_back_L_pivot',
    'chassis_back_R_pivot'
    ]
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        ground = sel[1]
        for p in pivots:
            cmds.pointConstraint( veh_ns + ':move', veh_ns + ':' + p, mo = True )
            cmds.geometryConstraint( ground, veh_ns + ':' + p )
    else:
        message( 'Select 2 objects: vehicle 1st, ground 2nd', warning = True )


def path_to_ground():
    '''
    master of path should be selected
    is assumed it has message connections to all path controls
    iterate and constrain each control
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        controls = cmds.listConnections( sel[0] + '.control' )
        if controls:
            # namespaces
            veh_ns = sel[0].split( ':' )[0]
            ground = sel[1]
            for c in controls:
                cmds.geometryConstraint( ground, c )
        else:
            message( 'Couldnt find path controls on first object:' + sel[0], warning = True )
    else:
        message( 'Select 2 objects: expecting master control of path and ground geo as selection.', warning = True )


def car_to_path( wheels = ['wheel_front_spin_L', 'wheel_front_spin_R', 'wheel_back_spin_L', 'wheel_back_spin_R'], mod = True, easyBake = True ):
    '''
    select controls first and path object with namespace last
    assumes controls are sorted in proper order
    adds modulus node in between roll connection
    '''
    # objects
    path_obj = 'onPath_front_Grp'
    path_steer = 'onPath_front'
    path_radius = 'onPath_front.wheelRadius'
    path_roll = 'onPath_front.wheelRoll'
    path_rollMod = 'onPath_front.wheelRollModulus'
    if easyBake:
        veh_obj = 'move'  # better able to bake and export anim
        veh_steer = 'steer'  # better able to bake and export anim
    else:
        veh_obj = 'move_CtGrp'
        veh_steer = 'steer_CtGrp'
    veh_offset = 'move_Offset'
    # wheel base
    path_wheelBase = 'onPath_back.wheelBase'
    chassis_f = 'chassis_back_pivot'
    chassis_b = 'chassis_front_pivot'

    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        path_ns = sel[1].split( ':' )[0]
        # objects
        path_obj = path_ns + ':' + path_obj
        path_steer = path_ns + ':' + path_steer
        veh_obj = veh_ns + ':' + veh_obj
        veh_steer = veh_ns + ':' + veh_steer
        veh_offset = veh_ns + ':' + veh_offset
        chassis_f = veh_ns + ':' + chassis_f
        chassis_b = veh_ns + ':' + chassis_b
        # attrs
        path_radius = path_ns + ':' + path_radius
        path_roll = path_ns + ':' + path_roll
        path_rollMod = path_ns + ':' + path_rollMod
        path_wheelBase = path_ns + ':' + path_wheelBase
        #
        if cmds.objExists( path_obj ) and cmds.objExists( veh_obj ):
            # wheel spin
            for wheel in wheels:
                veh_radius = veh_ns + ':' + wheel + '.radius'
                veh_roll = veh_ns + ':' + wheel + '.roll'
                veh_rx = veh_ns + ':' + wheel + '.rx'
                cmds.connectAttr( veh_radius, path_radius, f = True )  # should only connect once per radius change, this breaks previous connections, should add smarter logic
                if easyBake:
                    if mod:
                        cmds.connectAttr( path_rollMod, veh_roll )
                        cmds.connectAttr( path_rollMod, veh_rx )
                    else:
                        cmds.connectAttr( path_roll, veh_roll )
                        cmds.connectAttr( path_roll, veh_rx )
                else:
                    if mod:
                        cmds.connectAttr( path_rollMod, veh_roll )
                    else:
                        cmds.connectAttr( path_roll, veh_roll )
                # modulus_node( name = wheel, objectAttrDvdnd = path_roll, objectAttrRmndr = veh_roll, divisor = 360 )
            # amount to shift offset control
            point_A = cmds.xform( veh_obj, query = True, ws = True, rp = True )
            point_B = cmds.xform( veh_steer, query = True, ws = True, rp = True )
            distance_steer = place.distance2Pts( point_A, point_B )
            print( distance_steer )  # add value to wheelBase attr
            # cmds.setAttr( veh_offset + '.translateZ', distance_steer * -1 )  # skip, not necessary
            # wheel base
            point_A = cmds.xform( chassis_f, query = True, ws = True, rp = True )
            point_B = cmds.xform( chassis_b, query = True, ws = True, rp = True )
            distance_wheelBase = place.distance2Pts( point_A, point_B )
            cmds.setAttr( path_wheelBase, distance_wheelBase )
            # attach
            cmds.parentConstraint( path_obj, veh_obj, mo = False )
            # cmds.parentConstraint( path_steer, veh_steer, mo = False )
            cmds.orientConstraint( path_steer, veh_steer, skip = ( 'x', 'z' ) )  # cant use parentCons, axis locked if easyBake
            #
            # fix distance_steer offset
            t = cmds.xform( veh_obj, query = True, os = True, t = True )
            cmds.xform( veh_obj, os = True, t = [t[0], t[1], t[2] - distance_steer] )
            cn.updateConstraintOffset( veh_obj )
            #
        else:
            message( 'Expected objects dont exist', warning = True )
            print( path_obj, veh_obj )
    else:
        message( 'Select 2 objects: vehicle 1st, path 2nd', warning = True )


def __________________CAR():
    pass


def car( name = '', geo_grp = '', frontSolidAxle = False, backSolidAxle = False, chassisAxleLock = False, X = 1.1, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setHundaiTuscon\\model\\maya\\scenes\\setHundaiTuscon_model_v001.ma' ):
    '''
    chassis
    4 wheels
    '''
    # ref geo
    if ns and ref_geo:
        reference_geo( ns = ns, path = ref_geo )
    #
    mirror_jnts()

    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    # SteerCt[4] = returned only if given as argument, otherwise this is returned: MasterCt[4], MoveCt[4]
    master_move_controls = vehicle_master( masterX = X * 8, moveX = X * 10, geo_grp = '' )
    # [base_Ct, aim_Ct, up_Ct, follicle_Grp]
    Ct = dynamic_target( name = 'chassis', root = 'root_jnt', target = 'up_jnt', front = 'front_jnt', constrainObj = 'chassis_jnt', parentObj = 'move_Grp', attrObj = 'move', aim = [0, 1, 0], up = [0, 0, 1], X = 100.0 )
    cmds.transformLimits( Ct[0][1], rx = [-1.7, 1.0], erx = [1, 1] )
    cmds.transformLimits( Ct[0][1], rz = [-4, 4], erz = [1, 1] )
    # return
    # place.cleanUp( 'Jeep_Wrangler', Body = True )

    # move
    move = 'move'

    # passenger positions
    passengers( visObj = move, X = X * 18 )

    # transport trucks have chassis / rear axle locked together, apart from vertical movement, ie ty
    skipParentUp = False
    if chassisAxleLock:
        skipParentUp = True

    # mass to pivot, body
    chassis_joint = 'chassis_jnt'
    chassis_geo = get_geo_list( name = name, ns = ns, chassis = True )
    skin( chassis_joint, chassis_geo )
    # pivot_controls = [frontl, frontr, backl, backr, front, back, center, up] # entire controller hierarchy [0-4]
    pivot_controls = four_point_pivot( name = 'chassis', parent = master_move_controls[1], skipParentUp = skipParentUp, center = Ct[0][0], front = 'front_jnt', frontL = 'wheel_front_bottom_L_jnt', frontR = 'wheel_front_bottom_R_jnt', back = 'back_jnt', backL = 'wheel_back_bottom_L_jnt', backR = 'wheel_back_bottom_R_jnt', up = 'up_jnt', chassis_geo = '', X = X * 2 )
    cmds.parentConstraint( pivot_controls[4][4], Ct[2][0], mo = True )  # front vector for dynamic rig
    cmds.parentConstraint( pivot_controls[4][4], Ct[3], mo = True )  # follicle_Grp
    # ( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 )
    place.parentSwitch( 'dynamic', Ct[1][2], Ct[1][1], Ct[1][0], pivot_controls[4][4], Ct[1][0], False, False, True, False, 'dynamic', 0.0 )

    # axle
    if frontSolidAxle:
        # front
        axl_f_geo = get_geo_list( name = name, ns = ns, axle_front = True )
        axle_controls = solid_axle( name = 'front', axle = 'front_jnt', axlL = 'wheel_front_center_L_jnt', axlR = 'wheel_front_center_R_jnt',
              parent1 = pivot_controls[0][4], parent2 = pivot_controls[1][4], parent3 = pivot_controls[6][4],
              geo = axl_f_geo, aim = [1, 0, 0], up = [0, 1, 0], X = X * 8 )
    if backSolidAxle:
        # back
        axl_b_geo = get_geo_list( name = name, ns = ns, axle_back = True )
        axle_controls = solid_axle( name = 'back', axle = 'back_jnt', axlL = 'wheel_back_center_L_jnt', axlR = 'wheel_back_center_R_jnt',
              parent1 = pivot_controls[2][4], parent2 = pivot_controls[3][4], parent3 = pivot_controls[6][4],
              geo = axl_b_geo, aim = [1, 0, 0], up = [0, 1, 0], X = X * 8 )
        # chassis lock
        cmds.parentConstraint( axle_controls[0][4], pivot_controls[7][0], mo = True )
        # assume front axle is independant, turn off front wheel influence to chassis upCt.tx influence
        cmds.setAttr( pivot_controls[7][2] + '.multiplier', 0 )

    # tire curves R, left should already exist
    crvs_f_l = tire_curves( position = 'front', side = 'L', mirror = False )
    crvs_b_l = tire_curves( position = 'back', side = 'L', mirror = False )
    crvs_f_r = tire_curves( position = 'front', side = 'R', mirror = True )
    crvs_b_r = tire_curves( position = 'back', side = 'R', mirror = True )
    # remove point constraint to joint
    crv_lists = [crvs_f_l, crvs_b_l, crvs_f_r, crvs_b_r]
    for lst in crv_lists:
        grp = cmds.listRelatives( lst[0], parent = True )[0]
        # print( grp )
        cmds.setAttr( grp + '.visibility', 0 )
        con = cn.getConstraint( grp, nonKeyedRoute = False, keyedRoute = False, plugRoute = True )
        cmds.delete( con )

    # proxy tires
    prxy_f_l = tire_proxy2( position = 'front', side = 'L', crvs = crvs_f_l )  # [tire_proxy, lofted[0]]
    prxy_f_r = tire_proxy2( position = 'front', side = 'R', crvs = crvs_f_r )
    prxy_b_l = tire_proxy2( position = 'back', side = 'L', crvs = crvs_b_l )
    prxy_b_r = tire_proxy2( position = 'back', side = 'R', crvs = crvs_b_r )
    tires_proxy = [prxy_f_l[0], prxy_f_r[0], prxy_b_l[0], prxy_b_r[0]]
    # tire geo
    tire_geo_f_l = get_geo_list( name = name, ns = ns, tire_front_l = True )
    tire_geo_f_r = get_geo_list( name = name, ns = ns, tire_front_r = True )
    tire_geo_b_l = get_geo_list( name = name, ns = ns, tire_back_l = True )
    tire_geo_b_r = get_geo_list( name = name, ns = ns, tire_back_r = True )
    tires_geo = [tire_geo_f_l, tire_geo_f_r, tire_geo_b_l, tire_geo_b_r]

    # wrap
    tire_wrap( master = prxy_f_l[0], slaves = tire_geo_f_l )
    tire_wrap( master = prxy_f_r[0], slaves = tire_geo_f_r )
    tire_wrap( master = prxy_b_l[0], slaves = tire_geo_b_l )
    tire_wrap( master = prxy_b_r[0], slaves = tire_geo_b_r )

    # add tire vis switch (tire geo / proxy geo)

    place.optEnum( move, attr = 'tires', enum = 'VIS' )
    for geos in tires_geo:
        for g in geos:
            try:
                place.hijackVis( g, move, name = 'tireGeo', suffix = False, default = None, mode = 'visibility' )
            except:
                pass
    for g in tires_proxy:
        place.hijackVis( g, move, name = 'tireProxy', suffix = False, default = None, mode = 'visibility' )
    cmds.setAttr( move + '.tireGeo', 1 )

    # master move controls
    if frontSolidAxle:
        master_move_controls_f = [master_move_controls[0], None, master_move_controls[2]]
    else:
        master_move_controls_f = [master_move_controls[0], chassis_joint, master_move_controls[2]]
    #
    if backSolidAxle:
        master_move_controls_b = [master_move_controls[0], None, master_move_controls[2]]
    else:
        master_move_controls_b = [master_move_controls[0], chassis_joint, master_move_controls[2]]

    # return
    # wheel front L
    tire_geo = [prxy_f_l[0]]
    rim_geo = get_geo_list( name = name, ns = ns, rim_front_l = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_front_l = True )
    wheel_connect( name = 'wheel_front', suffix = 'L', axle_jnt = 'axle_front_L_jnt', master_move_controls = master_move_controls_f, pivot_grp = pivot_controls[0][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # wheel front R
    tire_geo = [prxy_f_r[0]]
    rim_geo = get_geo_list( name = name, ns = ns, rim_front_r = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_front_r = True )
    wheel_connect( name = 'wheel_front', suffix = 'R', axle_jnt = 'axle_front_R_jnt', master_move_controls = master_move_controls_f, pivot_grp = pivot_controls[1][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # return
    # wheel back L
    tire_geo = [prxy_b_l[0]]
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_l = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_back_l = True )
    wheel_connect( name = 'wheel_back', suffix = 'L', axle_jnt = 'axle_back_L_jnt', master_move_controls = master_move_controls_b, pivot_grp = pivot_controls[2][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )
    # wheel back R
    tire_geo = [prxy_b_r[0]]
    rim_geo = get_geo_list( name = name, ns = ns, rim_back_r = True )
    caliper_geo = get_geo_list( name = name, ns = ns, caliper_back_r = True )
    wheel_connect( name = 'wheel_back', suffix = 'R', axle_jnt = 'axle_back_R_jnt', master_move_controls = master_move_controls_b, pivot_grp = pivot_controls[3][4], tire_geo = tire_geo, rim_geo = rim_geo, caliper_geo = caliper_geo, X = X * 1.1 )

    # scale
    # geo = 'caterpillar_c_geo_lod_0'
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
    '''
    misc.scaleUnlock( '___GEO', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___GEO' + s )
        # cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush
        '''
    # HACK :
    # REF MODEL GROUP, LEAVE ALL GEO HEIRARCHY AS IS
    # TIRES GEO MUST BE IN WORLD SPACE, THEY ARE BEING DEFORMED VIA BLENDSHAPE
    # INSTEAD OF SCALING ENTIRE GROUP WITH RIG, SCALE INDIVIDUAL OBJECTS...
    all_geo = get_geo_list( name = name, ns = ns, all = True )
    tires = []
    # print( get_geo_list( name = name, tire_front_l = True ) )
    tires.append( get_geo_list( name = name, ns = ns, tire_front_l = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_front_r = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_back_l = True )[0] )
    tires.append( get_geo_list( name = name, ns = ns, tire_back_r = True )[0] )
    # add dynamic parts
    all_geo.append( Ct[1][0] )  # target control
    all_geo.append( Ct[3] )  # follicle groupo
    #
    for geo in all_geo:
        if geo not in tires:
            for s in scl:
                cmds.connectAttr( mstr + '.' + uni, geo + s )

    fix_normals( name = name , ns = ns, tires = True, del_history = False )
    #
    if cmds.objExists( 'locator1' ):
        cmds.delete( 'locator1' )


def car_combined_asset( car = '', path = 'P:\\MDLN\\assets\\util\\path\\rig\\maya\\scenes\\path_rig_v006.ma', ppl_path = 'P:\\MDLN\\assets\\util\\driver\\rig\\maya\\scenes\\driver_rig_v003.ma', getPath = True ):
    '''
    new scene
    get project path
    ref car
    ref path
    attach car to path
    save scene
    '''
    # new
    cmds.file( newFile = True, force = True )
    # project
    prjct = cmds.workspace( act = True, q = True )

    #
    latest_file = ''
    if not car:
        if 'rig' in prjct:
            #
            scenes_path = os.path.join( prjct, 'scenes' )
            list_of_files = glob.glob( os.path.join( scenes_path, '*.ma' ) )  # * means all if need specific format then *.csv
            filtered_list = []
            for f in list_of_files:
                if 'rigSkel' not in f and '_rigCombined_' not in f and '_rigPassengers_' not in f:
                    filtered_list.append( f )
            latest_file = max( filtered_list, key = os.path.getctime )
            # print( latest_file )
            car = latest_file
        else:
            message( 'project not set to rig directory', warning = True )
    if not path:
        pass

    if car and path and ppl_path:
        # ref
        ns_v = 'vhcl'
        ns_ppl = 'ppl'
        cmds.file( car, reference = True, namespace = ns_v )
        cmds.file( ppl_path, reference = True, namespace = ns_ppl )

        if getPath:
            # ref
            ns_p = 'pth'
            cmds.file( path, reference = True, namespace = ns_p )
            # attach
            cmds.select( [ns_v + ':master', ns_p + ':master'] )
            car_to_path()

        # group
        cmds.select( ns_v + ':master' )
        mel.eval( 'InvertSelection;' )
        sel = cmds.ls( sl = 1 )
        sel.remove( ns_v + ':master' )
        cmds.select( sel )
        cmds.group( name = '___AllGrp___' )

        # people
        cmds.parentConstraint( ns_v + ':chassis_jnt', ns_ppl + ':master', mo = True )
        cmds.parentConstraint( ns_v + ':passenger_front_L_Grp', ns_ppl + ':Peter_CtGrp', mo = False )
        cmds.parentConstraint( ns_v + ':passenger_front_R_Grp', ns_ppl + ':Paula_CtGrp', mo = False )
        cmds.parentConstraint( ns_v + ':passenger_back_L_Grp', ns_ppl + ':Vojta_CtGrp', mo = False )
        cmds.parentConstraint( ns_v + ':passenger_back_R_Grp', ns_ppl + ':Filip_CtGrp', mo = False )
        # pose passengers
        if 'Corolla' in prjct:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -8 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -8 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -8 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -8 )
            # scale
            cmds.setAttr( ns_ppl + ':Peter.Scale', 0.8 )
            cmds.setAttr( ns_ppl + ':Paula.Scale', 0.8 )
            cmds.setAttr( ns_ppl + ':Vojta.Scale', 0.8 )
            cmds.setAttr( ns_ppl + ':Filip.Scale', 0.8 )
            # knee bend
            cmds.setAttr( ns_ppl + ':Peter.kneeBend', 70 )
            cmds.setAttr( ns_ppl + ':Paula.kneeBend', 70 )
            cmds.setAttr( ns_ppl + ':Vojta.kneeBend', 70 )
            cmds.setAttr( ns_ppl + ':Filip.kneeBend', 70 )
        elif 'Mazda3' in prjct:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -20 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -20 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -20 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -20 )
            # raise
            cmds.setAttr( ns_ppl + ':Vojta.ty', 6 )
            cmds.setAttr( ns_ppl + ':Filip.ty', 6 )
        elif 'C63' in prjct:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -23 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -23 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -23 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -23 )
        elif '2019' in prjct:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -24.5 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -24.5 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -24.5 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -24.5 )
        elif 'Mdx' in prjct:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -21 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -21 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -21 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -21 )
        else:
            # lean back
            cmds.setAttr( ns_ppl + ':Peter.rx', -17 )
            cmds.setAttr( ns_ppl + ':Paula.rx', -17 )
            cmds.setAttr( ns_ppl + ':Vojta.rx', -17 )
            cmds.setAttr( ns_ppl + ':Filip.rx', -17 )

        # save
        name = ''
        if getPath:
            name = latest_file.replace( '_rig_', '_rigCombined_' )
        else:
            name = latest_file.replace( '_rig_', '_rigPassengers_' )
        name = name.replace( '\\', '/' )
        fileType = ['mayaAscii']
        # add the file about to be saved to the recent files menu
        mel.eval( 'addRecentFile "' + name + '" ' + fileType[0] + ';' )
        # rename the current file
        cmds.file( name, rn = name )
        # save it
        # cmds.file( save = True, typ = fileType[0] )
        cmds.file( save = True )
    else:
        message( 'directory variables empty: car, path', warning = True )
        print( car )
        print( path )


def car_sandbox( name = 'car', X = 1 ):
    '''
    test build
    addDL = cmds.createNode( 'addDoubleLinear', name = clusters[i] + '_addDL_ty' )
    '''
    # mass to pivot, body
    center = 'body_jnt'
    # [MasterCt[4], MoveCt[4], SteerCt[4]]
    ctrls = vehicle_master( masterX = X * 10, moveX = X * 10 )

    # [frontl, frontr, backl, backr]
    bdy = four_point_pivot( name = 'body', parent = 'move_Grp', center = center, front = 'front_jnt', frontL = 'front_L_jnt', frontR = 'front_R_jnt', back = 'back_jnt', backL = 'back_L_jnt', backR = 'back_R_jnt', up = 'up_jnt', X = X * 2 )
    print( '_____body' )
    print( bdy )
    # wheels
    # front
    sel = [
    'axle_front_jnt',
    'wheel_front_steer_L_jnt',
    'wheel_front_center_L_jnt',
    'wheel_front_bottom_L_jnt',
    'wheel_front_top_L_jnt',
    'wheel_front_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_L_geo'], rim_geo = ['rim_front_L_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'L', X = X * 1.0 )
    print( 'done wheel' )
    cmds.parentConstraint( ctrls[2], whl[0], mo = True )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addfl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[0] + '.ty' )

    #
    sel = [
    'axle_front_jnt',
    'wheel_front_steer_R_jnt',
    'wheel_front_center_R_jnt',
    'wheel_front_bottom_R_jnt',
    'wheel_front_top_R_jnt',
    'wheel_front_spin_R_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_front_R_geo'], rim_geo = ['rim_front_R_geo'], caliper_geo = [], name = 'wheel_front', suffix = 'R', X = X * 1.0 )
    cmds.parentConstraint( ctrls[2], whl[0], mo = True )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addfr_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[1] + '.ty' )

    # back
    sel = [
    'axle_back_jnt',
    'wheel_back_steer_L_jnt',
    'wheel_back_center_L_jnt',
    'wheel_back_bottom_L_jnt',
    'wheel_back_top_L_jnt',
    'wheel_back_spin_L_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_L_geo'], rim_geo = ['rim_back_L_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'L', X = X * 1.0 )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addbl_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[2] + '.ty' )

    #
    sel = [
    'axle_back_jnt',
    'wheel_back_steer_R_jnt',
    'wheel_back_center_R_jnt',
    'wheel_back_bottom_R_jnt',
    'wheel_back_top_R_jnt',
    'wheel_back_spin_R_jnt'
    ]
    # [steer[1], contact[2], center[2], center[1]]
    whl = wheel( master_move_controls = ctrls, axle = sel[0], steer = sel[1], center = sel[2], bottom = sel[3], top = sel[4], spin = sel[5], tire_geo = ['tire_back_R_geo'], rim_geo = ['rim_back_R_geo'], caliper_geo = [], name = 'wheel_back', suffix = 'R', X = X * 1.0 )
    cmds.orientConstraint( center, whl[3], skip = ( 'x', 'y' ) )
    # pivots
    addfl = cmds.createNode( 'addDoubleLinear', name = name + '_addbr_ty' )
    cmds.connectAttr( whl[1] + '.ty', addfl + '.input1' )
    cmds.connectAttr( whl[2] + '.ty', addfl + '.input2' )
    cmds.connectAttr( addfl + '.output', bdy[3] + '.ty' )

    # bug, contact group in wheels dont update
    cmds.dgdirty( allPlugs = True )


def __________________UTILS():
    pass


def fix_normals( name = '', ns = '', tires = True, del_history = False ):
    '''
    after skinning geo gets weird normals
    '''
    geo = []
    #
    if tires:
        trs = get_geo_list( name = name, ns = ns, tire_front_l = True, tire_front_r = True, tire_back_l = True, tire_back_r = True )
        for t in trs:
            geo.append( t )
    else:
        geo = get_geo_list( name = name, ns = ns, all = True )
    cmds.select( geo )
    cmds.polyNormalPerVertex( unFreezeNormal = True )
    for g in geo:
        cmds.select( g )
        cmds.polySoftEdge( angle = 45 )
    if del_history:
        cmds.delete( geo, ch = True )


def mirror_jnts():
    '''
    
    '''
    # jnts - new joints for pivots
    mirrorj = [
    'axle_back_L_jnt',
    'axle_front_L_jnt',
    'passenger_back_L_jnt',
    'passenger_front_L_jnt'
    ]
    # mirror
    for j in mirrorj:
        jnt.mirror( j , mirrorBehavior = True )


def skin( joint = '', geos = [], constraint = True, selectedJoints = False ):
    '''
    skin geo list to joint
    '''
    #
    # alternate method
    # cmds.select( [geo_hub[1], jnt_hub[1]] )
    # mel.eval( 'SmoothBindSkin;' )
    #
    sel = cmds.ls( sl = 1 )
    # skin
    for g in geos:
        if constraint:
            cmds.parentConstraint( joint, g, mo = True )
        else:
            if selectedJoints:
                cmds.select( g, add = True )
                mel.eval( 'SmoothBindSkin;' )
            else:
                cmds.select( [g, joint] )
            mel.eval( 'SmoothBindSkin;' )
            # cmds.bindSkin( tsb = True )  # toSelectedBones
            # cmds.bindSkin( g, joint, tsb = True ) # toSelectedBones
            # cmds.bindSkin()
    cmds.select( sel )


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def modulus_node( name = 'wheelRoll', objectAttrDvdnd = '', objectAttrRmndr = '', divisor = None ):
    '''
    create mod node
    create output mod value objAttrRmndr
    '''
    # attrs
    divdA = 'dividend'
    divsA = 'divisor'
    rsltA = 'result'
    rsltIntA = 'resultInteger'
    qtntA = 'quotient'
    rmndA = 'remainderRaw'
    rmndPosA = 'remainderProcessed'  # force positive
    rmndDgrsA = 'remainder'
    attrList = [divdA, divsA, rsltA, rsltIntA, qtntA, rmndA, rmndPosA, rmndDgrsA]
    mod = '__modulus'

    # mod object
    modNode = cmds.group( name = name + mod, em = True )
    place.translationLock( modNode, True )
    place.rotationLock( modNode, True )
    place.scaleLock( modNode, True )
    # add attrs
    for attr in attrList:
        if 'Integer' in attr:
            cmds.addAttr( modNode, ln = attr, at = 'long', h = False )
        else:
            cmds.addAttr( modNode, ln = attr, at = 'float', h = False )
        cmds.setAttr( modNode + '.' + attr , k = False )
        cmds.setAttr( modNode + '.' + attr , cb = False )
    #
    cmds.setAttr( modNode + '.' + divdA , cb = True )
    cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + divsA , cb = True )
    cmds.addAttr( modNode + '.' + divsA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + qtntA , cb = True )
    cmds.setAttr( modNode + '.' + rmndDgrsA , cb = True )
    cmds.setAttr( modNode + '.visibility' , k = False )
    cmds.setAttr( modNode + '.visibility' , cb = False )

    # connect inputs
    if objectAttrDvdnd:
        cmds.connectAttr( objectAttrDvdnd, modNode + '.' + divdA )
    else:
        cmds.setAttr( modNode + '.' + divdA, 1 )
    if divisor:
        cmds.setAttr( modNode + '.' + divsA, divisor )
    else:
        cmds.setAttr( modNode + '.' + divsA, 1 )
    # connect output
    if objectAttrRmndr:
        cmds.connectAttr( modNode + '.' + rmndDgrsA, objectAttrRmndr )

    # div , wheel rotation / 360
    ddd = cmds.shadingNode( 'multiplyDivide', au = True, n = name + mod + '__dividendDivisor_div' )
    cmds.setAttr( ddd + '.operation', 2 )  # divide
    cmds.connectAttr( modNode + '.' + divdA, ddd + '.input1X' )
    cmds.connectAttr( modNode + '.' + divsA, ddd + '.input2X' )

    # result
    cmds.connectAttr( ddd + '.outputX', modNode + '.' + rsltA )
    # result integer
    cmds.connectAttr( modNode + '.' + rsltA, modNode + '.' + rsltIntA )

    # remainder part a
    rra = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderRaw_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rra + '.input1' )
    # remainder part b
    rinm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__remainderRaw_mult' )
    cmds.connectAttr( modNode + '.' + rsltIntA, rinm + '.input1' )
    cmds.setAttr( rinm + '.input2', -1 )
    cmds.connectAttr( rinm + '.output', rra + '.input2' )
    # remainder part c
    cmds.connectAttr( rra + '.output', modNode + '.' + rmndA )

    # condition, force remainder to positive part a
    cndtn = cmds.shadingNode( 'condition', au = True, n = name + mod + '__remainderProcess_cnd' )
    cmds.setAttr( cndtn + '.operation', 4 )  # less than
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.firstTerm' )
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.colorIfFalseR' )
    # condition true, flip remainder, part b
    rfa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderProcess_add' )
    cmds.setAttr( rfa + '.input2', 1 )
    cmds.connectAttr( modNode + '.' + rmndA, rfa + '.input1' )
    cmds.connectAttr( rfa + '.output', cndtn + '.colorIfTrueR' )
    # condition c, output positive remainder
    cmds.connectAttr( cndtn + '.outColorR', modNode + '.' + rmndPosA )

    # remainder to degrees
    rdm = cmds.createNode( 'multDoubleLinear', name = name + mod + '__remainder_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rdm + '.input1' )
    cmds.connectAttr( modNode + '.' + divsA, rdm + '.input2' )
    cmds.connectAttr( rdm + '.output', modNode + '.' + rmndDgrsA )

    # quotient result minus remainder
    rqa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__quotient_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rqa + '.input1' )
    # remainder part b
    rnm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__quotient_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rnm + '.input1' )
    cmds.setAttr( rnm + '.input2', -1 )
    cmds.connectAttr( rnm + '.output', rqa + '.input2' )
    # remainder part c
    cmds.connectAttr( rqa + '.output', modNode + '.' + qtntA )

    place.cleanUp( modNode, World = True )
    return modNode


def __________________GEO():
    pass


def reference_geo( ns = '', path = '' ):
    '''
    get geo from directory
    '''
    cmds.file( path, reference = True, ns = ns )


def get_geo_list( name = '', ns = '', chassis = False,
                  tire_front_l = False, rim_front_l = False, caliper_front_l = False,
                  tire_front_r = False, rim_front_r = False, caliper_front_r = False,
                  tire_back_l = False, rim_back_l = False, caliper_back_l = False,
                  tire_back_r = False, rim_back_r = False, caliper_back_r = False,
                  axle_front = False, axle_back = False,
                  drive_train = False,
                  all = False ):
    '''
    geo members via selection set
    '''
    geos = []
    geo_sets = []

    # chassis
    if chassis or all:
        geo_list = process_geo_list( name = name + '_' + 'chassis' )
        geo_sets.append( geo_list )

    # front l
    if tire_front_l or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_front_l' )
        geo_sets.append( geo_list )
    if rim_front_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_front_l' )
        geo_sets.append( geo_list )
    if caliper_front_l or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_front_l' )
        geo_sets.append( geo_list )

    # front r
    if tire_front_r or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_front_r' )
        geo_sets.append( geo_list )
    if rim_front_r or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_front_r' )
        geo_sets.append( geo_list )
    if caliper_front_r or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_front_r' )
        geo_sets.append( geo_list )

    # back l
    if tire_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_l' )
        geo_sets.append( geo_list )
    if rim_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_l' )
        geo_sets.append( geo_list )
    if caliper_back_l or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_back_l' )
        geo_sets.append( geo_list )

    # back r
    if tire_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'tire_back_r' )
        geo_sets.append( geo_list )
    if rim_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'rim_back_r' )
        geo_sets.append( geo_list )
    if caliper_back_r or all:
        geo_list = process_geo_list( name = name + '_' + 'caliper_back_r' )
        geo_sets.append( geo_list )

    # axle
    if axle_front or all:
        geo_list = process_geo_list( name = name + '_' + 'axle_front' )
        geo_sets.append( geo_list )
    if axle_back or all:
        geo_list = process_geo_list( name = name + '_' + 'axle_back' )
        geo_sets.append( geo_list )

    # drive shaft
    if drive_train or all:
        geo_list = process_geo_list( name = name + '_' + 'drive_train' )
        geo_sets.append( geo_list )

    # build list
    for geo_set in geo_sets:
        if geo_set:
            for geo in geo_set:
                if ns:
                    if cmds.objExists( ns + ':' + geo ):
                        geos.append( ns + ':' + geo )
                    else:
                        print( geo_set, geo )
                else:
                    geos.append( geo )

    return geos


def process_geo_list( name = '' ):
    '''
    
    '''
    s = []
    setDict = ss.loadDict( os.path.join( ss.defaultPath(), name + '.sel' ) )
    # print( setDict )
    if setDict:
        for obj in setDict.values():
            s.append( obj )
        # print( s )
        return s
    return None


def create_geo_set_files( name = '' ):
    '''
    
    '''
    files = ['chassis', 'tire_front_l', 'rim_front_l', 'caliper_front_l', 'tire_front_r', 'rim_front_r', 'caliper_front_r', 'tire_back_l', 'rim_back_l', 'caliper_back_l', 'tire_back_r', 'rim_back_r', 'caliper_back_r', 'axle_front', 'axle_back', 'drive_train' ]
    path = ss.defaultPath()
    for f in files:
        filePath = os.path.join( path, name + '_' + f + '.sel' )
        ss.exportFile( filePath, sel = ['persp'] )

'''
sel = cmds.ls( sl = 1 )
for s in sel:
    try:
        shp = cmds.listRelatives( s, shapes = 1 )[0]
        cmds.setAttr( s + '.normalX', 1 )
        cmds.setAttr( s + '.normalY', 0 )
        print( shp )
    except:
        print( 'fail' )'''

'''
import imp
import webrImport as web
imp.reload(web)
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Corolla', geo_grp='setCorolla_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setCorolla\\model\\maya\\scenes\\setCorolla_model_v004.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'HyundaiTucson', geo_grp='setHyundaiTuscon_grp', X = 9.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setHyundaiTucson\\\model\\maya\\scenes\\setHundaiTuscon_model_v012.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Mazda3', geo_grp='mazda3_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setMazda3\\model\\maya\\scenes\\setMazda3_model_v008.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'MazdaCX7', geo_grp='mazda_cx_7_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setMazdaCX7\\model\\maya\\scenes\\setMazdaCX7_model_v007.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'MercedesC63', geo_grp='merc_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setMercedesC63\\model\\maya\\scenes\\setMercedesC63_model_v008.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Rav4', geo_grp='toyotaRav4_grp', X = 10.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setToyotaRav4\\model\\maya\\scenes\\setToyotaRav4_model_v003.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'VolkswagenPassat', geo_grp='setVolkswagenPassat_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\set\\setVolkswagenPassat\\model\\maya\scenes\\setVolkswagenPassat_model_v010.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Rav4_2019', geo_grp='Toyota_RAV4', X = 9.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\2019ToyotaRav4\\model\\maya\\scenes\\2019ToyotaRav4_model_v004.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'AcuraMDX', geo_grp='acuraMdx_grp', X = 10.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\AcuraMdx\\model\\maya\\scenes\\AcuraMdx_model_v005.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'MazdaCX5', geo_grp='mazdaCx5_grp', X = 9.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\MazdaCx5\\model\\maya\\scenes\\MazdaCx5_model_v002.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'MercedesSprinter', geo_grp='mercedesSprinter_grp', X = 10.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\MercedesSprinter\\model\\maya\\scenes\\MercedesSprinter_model_v004.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Toyota4Runner', geo_grp='Toyota4Runner_grp', X = 8.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\Toyota4runner\\model\\maya\\scenes\\Toyota4runner_model_v002.ma' )
# vehicle rig
vhl = web.mod('vehicle_lib')
vhl.car( name = 'Truck', geo_grp='Truck_grp', frontSolidAxle = False, backSolidAxle = True, chassisAxleLock=True, X = 15.0, ns = 'geo', ref_geo = 'P:\\MDLN\\assets\\veh\\Truck\\model\\maya\\scenes\\Truck_model_v004.ma' )
# car to path
vhl = web.mod('vehicle_lib')
vhl.car_to_path()
# car to ground
vhl = web.mod('vehicle_lib')
vhl.car_to_ground()
# path to ground
vhl = web.mod('vehicle_lib')
vhl.path_to_ground()
# path to ground
vhl = web.mod('vehicle_lib')
vhl.path_switch()

# set files
vhl = web.mod('vehicle_lib')
vhl.create_geo_set_files(name='Rav4')

# vehicle path
vhl = web.mod('vehicle_lib')
vhl.path(  points = 10, X = 7, length = 20000, layers = 2 )

# vehicle path
vhl = web.mod('vehicle_lib')
vhl.path(  points = 100, X = 10, length = 200000, layers = 2 )

# TEST vehicle path
cmds.file( newFile = True, force = True )
vhl = web.mod('vehicle_lib')
multiple = 1
length = 50000*multiple # use multiples of 50k
pointGap = 500
points = length / pointGap
vhl.path(  points = points+1, X = 10, length = length, deviationLayers = 10, layers = 5 )


# combine car, path
vhl = web.mod('vehicle_lib')
vhl.car_combined_asset()
'''
