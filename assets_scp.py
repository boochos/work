import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
atl = web.mod( "atom_path_lib" )
place = web.mod( "atom_place_lib" )
stage = web.mod( 'atom_splineStage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
anm = web.mod( "anim_lib" )
# atl.path(segments=5, size=0.05, length=10)


def amulet_string( segments = 9, joints_in_seg = 9 ):
    '''
    # segments = 13  # choose odd number
    # joints_in_seg = 5  # choose odd number
    '''
    X = 2
    splines = True
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 33 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    # print GEO
    # return None
    #
    '''
    geo_grp = 'Amulet_grp'
    geo_root = [
    'AMULET_GOLDEN1',
    'AMULET_BODY',
    'AMULET_BLUE',
    'AMULET_RED',
    'AMULET_CYAN',
    ]
    geo_hinge_l = [     'DETAIL_L', 'AMULET_CYLINDER_L']
    geo_hinge_r = [     'DETAIL_R', 'AMULET_CYLINDER_R']'''

    geo_string = 'cord'
    #
    cmds.parent( geo_string, GEO[0] )
    cmds.parent( 'TextureFBXASC032Group', WORLD_SPACE )
    cmds.parent( 'DirectionalFBXASC032Light', WORLD_SPACE )
    cmds.setAttr( 'TextureFBXASC032Group.visibility', 0 )
    cmds.setAttr( 'DirectionalFBXASC032Light.visibility', 0 )
    # model v012
    cmds.setAttr( geo_string + '.rotateX', 90 )
    # cmds.setAttr( geo_string + '.rotateY', 180 )
    # cmds.setAttr( geo_string + '.translateY', -0.213 )
    cmds.setAttr( geo_string + '.translateZ', -3.5 )

    #
    # cmds.deltaMush( 'AMULET_CHAIN', smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    '''
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )'''
    #
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # lock geo - [lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'cord_Base'
    amulet = place.Controller( Amulet, MasterCt[4], False, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    # cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # root
    cmds.select( cl = True )
    rt_jnt = place.joint( 0, 'stringRoot_jnt', pad = 2, rpQuery = True )[0]
    cmds.parentConstraint( AmuletCt[4], rt_jnt, mo = True )
    cmds.parent( rt_jnt, SKIN_JOINTS )

    # return None

    # stringA #
    StringA = 'stringA'
    stringA = place.Controller( StringA, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    StringACt = stringA.createController()
    '''
    cmds.setAttr( StringACt[0] + '.translateX', 4.168 )
    cmds.setAttr( StringACt[0] + '.translateY', 0.32 )
    cmds.setAttr( StringACt[0] + '.translateZ', 6.6 )'''
    place.setRotOrder( StringACt[0], 2, True )
    cmds.parent( StringACt[0], CONTROLS )
    # cmds.parentConstraint( Hinge_LCt[4], StringACt[0], mo = True )
    place.setChannels( StringACt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( StringACt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # string_Tip #
    String_Tip = 'string_Tip'
    string_Tip = place.Controller( String_Tip, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    String_TipCt = string_Tip.createController()
    '''
    cmds.setAttr( String_TipCt[0] + '.translateX', -4.168 )
    cmds.setAttr( String_TipCt[0] + '.translateY', 0.32 )'''
    cmds.setAttr( String_TipCt[0] + '.translateZ', 180 )
    place.setRotOrder( String_TipCt[0], 2, True )
    cmds.parent( String_TipCt[0], CONTROLS )
    # cmds.parentConstraint( Hinge_RCt[4], String_TipCt[0], mo = True )
    place.setChannels( String_TipCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( String_TipCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # STRING CHAIN
    # string variables
    gap = 180 / segments  # gap between hinges, correct segment to this length
    full_length = 180.0  # string length
    # math
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    # print seg_length, length
    # correct length for connection to base
    over_length = seg_length - gap  # will need to shorten segment
    reduce_length = over_length / lengths_in_seg  # each joint needs to be this much shorter
    new_length = length - reduce_length
    # chain
    suffix = 'string'
    pad = 2
    jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    cmds.parent( jnts[0], SKIN_JOINTS )

    # TUBE
    # temp joint for more geo length
    cmds.select( jnts[-1] )
    tmp_jnt = place.joint( 0, 'tmp_jnt', pad = 2, rpQuery = True, radius = 0.4 )[0]
    cmds.parent( tmp_jnt, jnts[-1] )
    cmds.setAttr( tmp_jnt + '.translateZ', length )
    jnts.append( tmp_jnt )
    crv = place.curve( 'crv', jnts, d = 2 )
    # clean up temp jnt
    cmds.delete( tmp_jnt )
    jnts.pop( -1 )
    # tube radius
    crcl = place.circle( 'radius', obj = jnts[0], radius = 0.55, degree = 5 )[0]
    cmds.select( [crv, crcl] )
    tube = cmds.extrude( ch = True, rn = False, po = 0, et = 2, ucp = 1, fpt = 1, upn = 1, rotation = 0, scale = 1, rsp = 1 )[0]
    cmds.reverseSurface( tube, rpo = True )
    tube_poly = cmds.nurbsToPoly( tube, format = 3, uType = 3, vType = 3, cht = 0.2, chr = 0.1 )[0]
    tube_poly = cmds.rename( tube_poly, suffix + '_Deformer' )
    cmds.polyNormal( tube_poly, nm = 0 )
    cmds.delete( tube_poly, constructionHistory = True )
    cmds.delete( tube, crv, crcl )
    cmds.parent( tube_poly, jnts[0] )
    '''
    cmds.setAttr( jnts[0] + '.translateX', 4.168 )
    cmds.setAttr( jnts[0] + '.translateY', 0.32 )
    cmds.setAttr( jnts[0] + '.translateZ', 6.6 )'''
    cmds.setAttr( tube_poly + '.translateZ', ( length * 0.7 ) * -1 )  # move so default weights distribute properly, loop cant lay directly on joint
    cmds.parent( tube_poly, world = True )  # unparent
    cmds.select( jnts[0], hi = True )
    cmds.select( tube_poly, add = True )
    # python or mel binSkin didnt work, created too many skinClusters
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    # wrap
    # return None
    dfrmr = createWrap( tube_poly, geo_string )
    # clean up
    cmds.parent( tube_poly, GEO[1] )
    cmds.parent( tube_poly + 'Base', GEO[1] )

    # return None

    # place segment controls
    seg = []
    # seg.append( jnts[0] )
    cmds.select( jnts[0], hi = True )
    sel = cmds.ls( sl = True )
    for jnt in sel:
        if '_01' in jnt and jnt != sel[0]:
            seg.append( jnt )
    # print seg
    # return None

    # fk chain
    suffix_fk = suffix + 'Macro'
    # fkjnts = place.jointChain( suffix = suffix_fk, pad = pad, length = new_length * lengths_in_seg, amount = ( segments - 1 ) / 2, radius = 0.4, dbl = 0 )
    # fkjnts = place.jointChain( suffix = suffix_fk, pad = pad, length = new_length * lengths_in_seg, amount = ( segments ), radius = 0.4, dbl = 0 )
    fkjnts = place.jointChain( suffix = suffix_fk, pad = pad, length = length * lengths_in_seg, amount = ( segments ), radius = 0.4, dbl = 0 )
    cmds.parent( fkjnts[0], SKIN_JOINTS )
    # should match string location, but center, no tx
    '''
    cmds.setAttr( fkjnts[0] + '.translateY', 0.32 )
    cmds.setAttr( fkjnts[0] + '.translateZ', 6.6 )'''
    # fk controls
    i = 0
    for joint in fkjnts:
        # print i
        if i == 0:
            parent = AmuletCt[4]
        else:
            parent = fkjnts[i - 1]
            # print 'parent', parent
        # Upper = joint[:7]
        Upper = suffix_fk + '_' + str( i )
        # print Upper
        upperMaster = place.Controller( Upper, joint, False, 'facetZup_ctrl', X * 3.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
        UpperCt = upperMaster.createController()
        # offset
        ofst = 10
        '''
        pos = cmds.getAttr( UpperCt[0] + '.tz' )
        cmds.setAttr( UpperCt[0] + '.tz', pos - ofst )'''
        #
        cmds.parentConstraint( UpperCt[4], joint )
        cmds.parent( UpperCt[0], CONTROLS )
        cmds.select( UpperCt[0] )
        UpperCt_TopGrp1 = place.insert( 'null', 1, Upper + '_TopGrp1' )[0][0]
        UpperCt_CtGrp1 = place.insert( 'null', 1, Upper + '_CtGrp1' )[0][0]
        place.setRotOrder( UpperCt_TopGrp1, 2, True )
        place.setRotOrder( UpperCt[2], 3, False )
        #
        place.parentSwitch( Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '', 1.0 )
        place.parentSwitch( Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '', 1.0 )
        #
        cmds.parentConstraint( parent, UpperCt_TopGrp1, mo = True )
        place.setChannels( UpperCt[0], [False, False], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[1], [False, True], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[2], [False, True], [False, True], [True, False], [True, False, False] )
        place.setChannels( UpperCt[3], [False, True], [False, True], [True, False], [False, False, False] )
        cmds.setAttr( UpperCt[3] + '.visibility', cb = False )
        place.setChannels( UpperCt[4], [True, False], [False, True], [True, False], [True, False, False] )
        #
        i = i + 1

    # string segment controls #
    i = 0
    iMax_letter = 'A'
    al = len( seg )
    # print seg
    for joint in seg:
        if cmds.objExists( joint ):
            if i == 0:
                parent = fkjnts[i + 1]
                # parent = 'stringA_Grp'
            else:
                if i <= 3:
                    parent = fkjnts[i + 1]
                else:
                    parent = fkjnts[i + 1]
                    # parent = fkjnts[ al - i]
                # parent = joint[:6] + chr( ord( 'a' ) + i ).upper() + '_Grp'
            #
            Upper = joint[:7]
            # print Upper
            upperMaster = place.Controller( Upper, joint, False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
            UpperCt = upperMaster.createController()
            # place.addText( UpperCt[2], t = joint[5], c = 17, rotOffset = [0, 0, 0], posOffset = [-1.5, 8, 0] )
            cmds.parent( UpperCt[0], CONTROLS )
            cmds.select( UpperCt[0] )
            UpperCt_TopGrp1 = place.insert( 'null', 1, Upper + '_TopGrp1' )[0][0]
            UpperCt_CtGrp1 = place.insert( 'null', 1, Upper + '_CtGrp1' )[0][0]
            place.setRotOrder( UpperCt_TopGrp1, 2, True )
            place.setRotOrder( UpperCt[2], 3, False )
            # switch these for fk chain down middle
            place.parentSwitch( Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '', 1.0 )
            place.parentSwitch( Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '', 1.0 )
            #
            cmds.parentConstraint( parent, UpperCt_TopGrp1, mo = True )
            place.setChannels( UpperCt[0], [False, False], [False, False], [True, False], [True, False, False] )
            place.setChannels( UpperCt[1], [False, True], [False, False], [True, False], [True, False, False] )
            place.setChannels( UpperCt[2], [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( UpperCt[3], [False, True], [False, True], [True, False], [False, False, False] )
            cmds.setAttr( UpperCt[3] + '.visibility', cb = False )
            place.setChannels( UpperCt[4], [True, False], [False, True], [True, False], [True, False, False] )
            #
            i = i + 1
            iMax_letter = chr( ord( 'a' ) + i ).lower()
            # print iMax_letter

    # return None
    # need to parent macros start/tip
    cmds.parentConstraint( fkjnts[0], StringACt[0], mo = True )
    cmds.parentConstraint( fkjnts[-1], String_TipCt[0], mo = True )

    # necklace base hinge aim vectors
    iMax = ord( iMax_letter ) - 96
    end = str( ( '%0' + str( pad ) + 'd' ) % ( joints_in_seg ) )
    # print iMax
    if splines:
        amuletSplines( iMax, end = end )


def amuletSplines( iMax = 1, end = 1 ):
    '''\n
    Build splines for amulet\n
    iMax = number of iterations
    end = last joint number in spline, in proper format pad, for name building
    '''
    face = None
    # X = cmds.floatField( 'atom_srig_conScale', query = True, value = True )
    X = 0.25  # cmds.floatField( 'atom_srig_conScale', query = True, value = True )

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

    def chain( prefix = 'upper', iMax = 4, endPrefix = 'neck', EOrient = 0 ):
        '''\n

        '''
        i = 0
        while i < iMax:
            letter = chr( ord( 'a' ) + i ).upper()
            letterPrev = chr( ord( 'a' ) + ( i - 1 ) ).upper()
            letterNext = chr( ord( 'a' ) + ( i + 1 ) ).upper()
            splineName = prefix + letter
            splineSize = X * 1
            splineDistance = X * 16.0
            splineFalloff = 0
            if i == 0:
                # splinePrnt = 'A_Grp'
                # splineStrt = 'A_Grp'
                splinePrnt = prefix + 'A_Grp'
                splineStrt = prefix + 'A_Grp'
                newPrefix = prefix[0].upper() + prefix[1:]
                # splineAttr = 'A_' + newPrefix
                splineAttr = prefix + 'A'
            else:
                splinePrnt = prefix + letter + '_Grp'
                splineStrt = prefix + letterPrev + '_jnt_' + end
                splineAttr = prefix + letter + '_Offset'
            if i == iMax - 1:
                splineEnd = endPrefix + '_Grp'
            else:
                splineEnd = prefix + letterNext + '_Grp'
            # splineRoot = 'root_jnt'
            spline = [prefix + letter + '_jnt_01', prefix + letter + '_jnt_' + end]
            # build spline
            SplineOpts( splineName, splineSize, splineDistance, splineFalloff )
            cmds.select( spline )
            stage.splineStage( 4 )
            # assemble
            OptAttr( splineAttr, prefix + letter )
            # insert group above _IK_CtrlGrp # fixes mid ik orientation and position
            hack = False
            if hack:
                splinePrnt_s = place.null2( splineName + '_PARENT_S', splineName + '_IK_CtrlGrp', orient = True )[0]
                cmds.parent( splinePrnt_s, splineName + '_SplnCtrlGrp' )
                splinePrnt_e = place.null2( splineName + '_PARENT_E', splineName + '_IK_CtrlGrp', orient = True )[0]
                cmds.parent( splinePrnt_e, splineName + '_SplnCtrlGrp' )
                p = cmds.parentConstraint( splinePrnt, splinePrnt_s, mo = True )[0]
                cmds.setAttr( p + '.interpType', 0 )
                p = cmds.parentConstraint( splineEnd, splinePrnt_e, mo = True )[0]
                cmds.setAttr( p + '.interpType', 0 )
                p = cmds.parentConstraint( splinePrnt_s, splineName + '_IK_CtrlGrp', mo = True )[0]
                p = cmds.parentConstraint( splinePrnt_e, splineName + '_IK_CtrlGrp', mo = True )[0]
                cmds.setAttr( p + '.interpType', 0 )
            #
            else:
                cmds.parentConstraint( splinePrnt, splineName + '_IK_CtrlGrp', mo = True )  # no(unstable for string): above constraints are taking over
            cmds.parentConstraint( splineStrt, splineName + '_S_IK_PrntGrp', mo = True )
            cmds.parentConstraint( splineEnd, splineName + '_E_IK_PrntGrp', mo = True )
            # # cmds.parentConstraint(splineName + '_S_IK_Jnt', splineRoot, mo=True)
            # set options
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Vis', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Root', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.' + splineName + 'Stretch', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrVis', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrMidIkBlend', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.ClstrMidIkSE_W', 0.5 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrVis', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidIkBlend', 1 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidIkSE_W', 0.5 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrnt', 0 )
            cmds.setAttr( prefix + letter + '_IK_CtrlGrp.VctrMidTwstCstrntSE_W', 0.5 )
            cmds.setAttr( splineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
            cmds.setAttr( splineName + '_E_IK_Cntrl.LockOrientOffOn', EOrient )
            place.hijackCustomAttrs( splineName + '_IK_CtrlGrp', splineAttr )

            # connect multi/div node of spline curves(S/E) to Control group scale
            misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
            cmds.connectAttr( '___CONTROLS.scaleZ', prefix + letter + '_S_IK_curve_scale.input2Z' )
            cmds.connectAttr( '___CONTROLS.scaleZ', prefix + letter + '_E_IK_curve_scale.input2Z' )

            i = i + 1

    chain( prefix = 'string', iMax = iMax, endPrefix = 'string_Tip', EOrient = 1 )
    # chain(prefix='lower', iMax=18, endPrefix='lowerTip', EOrient=0)


def fk_chain( segments = 9, joints_in_seg = 9 ):
    '''
    # segments = 13  # choose odd number
    # joints_in_seg = 5  # choose odd number
    '''
    X = 2
    splines = False
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 33 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    # print GEO
    # return None
    #
    #
    # cmds.deltaMush( 'AMULET_CHAIN', smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    geo_string = 'cord'
    #
    cmds.parent( geo_string, GEO[0] )
    cmds.parent( 'TextureFBXASC032Group', WORLD_SPACE )
    cmds.parent( 'DirectionalFBXASC032Light', WORLD_SPACE )
    cmds.setAttr( 'TextureFBXASC032Group.visibility', 0 )
    cmds.setAttr( 'DirectionalFBXASC032Light.visibility', 0 )
    # model v012
    cmds.setAttr( geo_string + '.rotateX', 90 )
    # cmds.setAttr( geo_string + '.rotateY', 180 )
    # cmds.setAttr( geo_string + '.translateY', -0.213 )
    cmds.setAttr( geo_string + '.translateZ', -3.5 )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    '''
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )'''
    #
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # lock geo - [lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'Cord'
    amulet = place.Controller( Amulet, MasterCt[4], False, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    misc.addAttribute( [AmuletCt[2]], ['Travel'], 0.0, 10.0, True, 'float' )
    # cmds.setAttr( AmuletCt[2] + '.' + 'Travel', 0.0 )
    # cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # root
    cmds.select( cl = True )
    rt_jnt = place.joint( 0, 'stringRoot_jnt', pad = 2, rpQuery = True )[0]
    # cmds.parentConstraint( AmuletCt[4], rt_jnt, mo = True )
    cmds.parent( rt_jnt, SKIN_JOINTS )

    # return None

    # STRING CHAIN
    # string variables
    gap = 180 / segments  # gap between hinges, correct segment to this length
    full_length = 180.0  # string length
    # math
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    # correct length for connection to base
    over_length = seg_length - gap  # will need to shorten segment
    reduce_length = over_length / lengths_in_seg  # each joint needs to be this much shorter
    new_length = length - reduce_length
    # chain
    suffix = 'string'
    pad = 2
    # jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = 0 )
    # cmds.parent( jnts[0], SKIN_JOINTS )
    cmds.parent( jnts[0], rt_jnt )

    # TUBE
    # temp joint for more geo length
    cmds.select( jnts[-1] )
    tmp_jnt = place.joint( 0, 'tmp_jnt', pad = 2, rpQuery = True, radius = 0.4 )[0]
    cmds.parent( tmp_jnt, jnts[-1] )
    cmds.setAttr( tmp_jnt + '.translateZ', length )
    jnts.append( tmp_jnt )
    crv = place.curve( 'crv', jnts, d = 2 )
    # clean up temp jnt
    cmds.delete( tmp_jnt )
    jnts.pop( -1 )
    # tube radius
    crcl = place.circle( 'radius', obj = jnts[0], radius = 0.55, degree = 5 )[0]
    cmds.select( [crv, crcl] )
    tube = cmds.extrude( ch = True, rn = False, po = 0, et = 2, ucp = 1, fpt = 1, upn = 1, rotation = 0, scale = 1, rsp = 1 )[0]
    cmds.reverseSurface( tube, rpo = True )
    tube_poly = cmds.nurbsToPoly( tube, format = 3, uType = 3, vType = 3, cht = 0.2, chr = 0.1 )[0]
    tube_poly = cmds.rename( tube_poly, suffix + '_Deformer' )
    cmds.polyNormal( tube_poly, nm = 0 )
    cmds.delete( tube_poly, constructionHistory = True )
    cmds.delete( tube, crv, crcl )
    cmds.parent( tube_poly, jnts[0] )
    cmds.setAttr( tube_poly + '.translateZ', ( length * 0.7 ) * -1 )  # move so default weights distribute properly, loop cant lay directly on joint
    cmds.parent( tube_poly, world = True )  # unparent
    cmds.select( jnts[0], hi = True )
    cmds.select( tube_poly, add = True )
    # python or mel binSkin didnt work, created too many skinClusters
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    # wrap
    dfrmr = createWrap( tube_poly, geo_string )
    # clean up
    cmds.parent( tube_poly, GEO[1] )
    cmds.parent( tube_poly + 'Base', GEO[1] )

    # return None

    # place segment controls
    seg = []
    # seg.append( jnts[0] )
    cmds.select( jnts[0], hi = True )
    sel = cmds.ls( sl = True )
    for jnt in sel:
        if '_01' in jnt and jnt != sel[0]:
            seg.append( jnt )
    # print seg
    # return None

    # fk chain
    suffix_fk = suffix + 'Macro'
    # name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    tailRig = sfk.SplineFK( suffix_fk, rt_jnt, jnts[-1], None,
                              controllerSize = 3, rootParent = AmuletCt[4], parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = joints_in_seg, stretch = 0, ik = 'splineIK' )

    # print 'tailRig', tailRig
    # tailRig.placeIkJnts()
    for i in tailRig.topGrp2:
        place.cleanUp( i, World = True )
    cmds.parentConstraint( suffix_fk + '_002_Grp', rt_jnt, mo = True )
    return None
    # fk controls
    i = 0
    # for joint in fkjnts:
    for joint in jnts:
        # print i
        if i == 0:
            parent = AmuletCt[4]
        else:
            parent = jnts[i - 1]
            # print 'parent', parent
        # Upper = joint[:7]
        # Upper = suffix_fk + '_' + str( i ) # str( ( '%0' + str( pad ) + 'd' ) % ( i ) )
        Upper = suffix_fk + '_' + str( ( '%0' + str( 3 ) + 'd' ) % ( i ) )
        # print Upper
        upperMaster = place.Controller( Upper, joint, False, 'facetZup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
        UpperCt = upperMaster.createController()
        # offset
        ofst = 10
        #
        cmds.parentConstraint( UpperCt[4], joint )
        cmds.parent( UpperCt[0], CONTROLS )
        cmds.select( UpperCt[0] )
        UpperCt_TopGrp1 = place.insert( 'null', 1, Upper + '_TopGrp1' )[0][0]
        UpperCt_CtGrp1 = place.insert( 'null', 1, Upper + '_CtGrp1' )[0][0]
        place.setRotOrder( UpperCt_TopGrp1, 2, True )
        place.setRotOrder( UpperCt[2], 3, False )
        #
        place.parentSwitch( Upper, UpperCt[2], UpperCt_CtGrp1, UpperCt_TopGrp1, MasterCt[4], parent, False, False, True, True, '', 1.0 )
        place.parentSwitch( Upper, UpperCt[2], UpperCt[1], UpperCt[0], MasterCt[4], parent, False, True, False, False, '', 1.0 )
        #
        cmds.parentConstraint( parent, UpperCt_TopGrp1, mo = True )
        place.setChannels( UpperCt[0], [False, False], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[1], [False, True], [False, False], [True, False], [True, False, False] )
        place.setChannels( UpperCt[2], [False, True], [False, True], [True, False], [True, False, False] )
        place.setChannels( UpperCt[3], [False, True], [False, True], [True, False], [False, False, False] )
        cmds.setAttr( UpperCt[3] + '.visibility', cb = False )
        place.setChannels( UpperCt[4], [True, False], [False, True], [True, False], [True, False, False] )
        #
        i = i + 1


def fuse_string( segments = 9, joints_in_seg = 9 ):
    '''
    # segments = 13  # choose odd number
    # joints_in_seg = 5  # choose odd number
    '''
    X = 2
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 33 )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]
    # print GEO
    # return None
    #
    geo_grp = 'Amulet_grp'
    geo_root = [
    'AMULET_GOLDEN1',
    'AMULET_BODY',
    'AMULET_BLUE',
    'AMULET_RED',
    'AMULET_CYAN',
    ]
    geo_hinge_l = [     'DETAIL_L', 'AMULET_CYLINDER_L']
    geo_hinge_r = [     'DETAIL_R', 'AMULET_CYLINDER_R']

    geo_string = 'AMULET_CHAIN'
    #
    cmds.parent( geo_grp, GEO[0] )
    # model v004
    '''
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -8.661 )
    cmds.setAttr( geo_grp + '.translateZ', 1.623 )'''
    # model v012
    cmds.setAttr( geo_grp + '.rotateX', -90 )
    cmds.setAttr( geo_grp + '.rotateY', 180 )
    cmds.setAttr( geo_grp + '.translateY', -0.213 )
    cmds.setAttr( geo_grp + '.translateZ', -6.84 )

    #
    # cmds.deltaMush( 'AMULET_CHAIN', smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    '''
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )'''
    #
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    # lock geo - [lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [True, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    # amulet #
    Amulet = 'amulet'
    amulet = place.Controller( Amulet, MasterCt[4], False, 'diamond_ctrl', X * 8, 17, 8, 1, ( 0, 0, 1 ), True, True )
    AmuletCt = amulet.createController()
    place.setRotOrder( AmuletCt[0], 2, True )
    cmds.parent( AmuletCt[0], CONTROLS )
    cmds.parentConstraint( MasterCt[4], AmuletCt[0], mo = True )
    # cmds.parentConstraint( AmuletCt[4], geo_grp, mo = True )

    # root
    cmds.select( cl = True )
    rt_jnt = place.joint( 0, 'stringRoot_jnt', pad = 2, rpQuery = True )[0]
    cmds.parentConstraint( AmuletCt[4], rt_jnt, mo = True )
    cmds.parent( rt_jnt, SKIN_JOINTS )
    # bind root geo
    for geo in geo_root:
        # cmds.bindSkin( 'am', 'stringRoot_jnt' ) # doesnt work cuz gay, trying mel
        cmds.select( [geo, rt_jnt] )
        mel.eval( 'SmoothBindSkin;' )

    # l/R hinge
    cmds.select( cl = True )
    hingeL_jnt = place.joint( 0, 'string_jnt_L', pad = 2, rpQuery = True )[0]
    cmds.setAttr( hingeL_jnt + '.translateX', 5.645 )
    cmds.setAttr( hingeL_jnt + '.translateY', 0.379 )
    cmds.setAttr( hingeL_jnt + '.translateZ', 4.918 )
    cmds.setAttr( hingeL_jnt + '.rotateY', -3.683 )
    cmds.parent( hingeL_jnt, rt_jnt )
    hingeR_jnt = cmds.mirrorJoint( mirrorYZ = True, mirrorBehavior = True, searchReplace = ( '_L', '_R' ) )[0]
    # bind l
    for geo in geo_hinge_l:
        cmds.select( [geo, hingeL_jnt] )
        # print cmds.ls( sl = 1 )
        mel.eval( 'SmoothBindSkin -tsb;' )
    # bind r
    for geo in geo_hinge_r:
        cmds.select( [geo, hingeR_jnt] )
        mel.eval( 'SmoothBindSkin -tsb;' )

    # return None
    # hinge_L #
    Hinge_L = 'hinge_L'
    hinge_L = place.Controller( Hinge_L, hingeL_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_LCt = hinge_L.createController()
    place.setRotOrder( Hinge_LCt[0], 2, True )
    cmds.parent( Hinge_LCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_LCt[0], mo = True )
    cmds.parentConstraint( Hinge_LCt[4], hingeL_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_LCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_LCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # hinge_R #
    Hinge_R = 'hinge_R'
    hinge_R = place.Controller( Hinge_R, hingeR_jnt, True, 'facetXup_ctrl', X * 1.5, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Hinge_RCt = hinge_R.createController()
    place.setRotOrder( Hinge_RCt[0], 2, True )
    cmds.parent( Hinge_RCt[0], CONTROLS )
    cmds.parentConstraint( AmuletCt[4], Hinge_RCt[0], mo = True )
    cmds.parentConstraint( Hinge_RCt[4], hingeR_jnt, mo = True )
    # lock control - [lock, keyable]
    place.setChannels( Hinge_RCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( Hinge_RCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # stringA #
    StringA = 'stringA'
    stringA = place.Controller( StringA, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    StringACt = stringA.createController()
    cmds.setAttr( StringACt[0] + '.translateX', 4.168 )
    cmds.setAttr( StringACt[0] + '.translateY', 0.32 )
    cmds.setAttr( StringACt[0] + '.translateZ', 6.6 )
    place.setRotOrder( StringACt[0], 2, True )
    cmds.parent( StringACt[0], CONTROLS )
    cmds.parentConstraint( Hinge_LCt[4], StringACt[0], mo = True )
    place.setChannels( StringACt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( StringACt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # string_Tip #
    String_Tip = 'string_Tip'
    string_Tip = place.Controller( String_Tip, MasterCt[4], False, 'facetZup_ctrl', X * 2, 12, 8, 1, ( 0, 0, 1 ), True, True )
    String_TipCt = string_Tip.createController()
    cmds.setAttr( String_TipCt[0] + '.translateX', -4.168 )
    cmds.setAttr( String_TipCt[0] + '.translateY', 0.32 )
    cmds.setAttr( String_TipCt[0] + '.translateZ', 6.6 )
    place.setRotOrder( String_TipCt[0], 2, True )
    cmds.parent( String_TipCt[0], CONTROLS )
    cmds.parentConstraint( Hinge_RCt[4], String_TipCt[0], mo = True )
    place.setChannels( String_TipCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( String_TipCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # STRING CHAIN
    # string variables
    gap = 8.336  # gap between hinges, correct segment to this length
    full_length = 111.44  # string length
    # math
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    # correct length for connection to base
    over_length = seg_length - gap  # will need to shorten segment
    reduce_length = over_length / lengths_in_seg  # each joint needs to be this much shorter
    new_length = length - reduce_length
    # chain
    suffix = 'string'
    pad = 2
    # jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = '' )
    cmds.parent( jnts[0], SKIN_JOINTS )

    # TUBE
    # temp joint for more geo length
    cmds.select( jnts[-1] )
    tmp_jnt = place.joint( 0, 'tmp_jnt', pad = 2, rpQuery = True, radius = 0.4 )[0]
    cmds.parent( tmp_jnt, jnts[-1] )
    cmds.setAttr( tmp_jnt + '.translateZ', length )
    jnts.append( tmp_jnt )
    crv = place.curve( 'crv', jnts, d = 2 )
    # clean up temp jnt
    cmds.delete( tmp_jnt )
    jnts.pop( -1 )
    # tube radius
    crcl = place.circle( 'radius', obj = jnts[0], radius = 0.36, degree = 5 )[0]
    cmds.select( [crv, crcl] )
    tube = cmds.extrude( ch = True, rn = False, po = 0, et = 2, ucp = 1, fpt = 1, upn = 1, rotation = 0, scale = 1, rsp = 1 )[0]
    cmds.reverseSurface( tube, rpo = True )
    tube_poly = cmds.nurbsToPoly( tube, format = 3, uType = 3, vType = 3, cht = 0.2, chr = 0.1 )[0]
    tube_poly = cmds.rename( tube_poly, suffix + '_Deformer' )
    cmds.polyNormal( tube_poly, nm = 0 )
    cmds.delete( tube_poly, constructionHistory = True )
    cmds.delete( tube, crv, crcl )
    cmds.parent( tube_poly, jnts[0] )
    cmds.setAttr( jnts[0] + '.translateX', 4.168 )
    cmds.setAttr( jnts[0] + '.translateY', 0.32 )
    cmds.setAttr( jnts[0] + '.translateZ', 6.6 )
    # return None
    cmds.setAttr( tube_poly + '.translateZ', ( length * 0.7 ) * -1 )  # move so default weights distribute properly, loop cant lay directly on joint
    cmds.parent( tube_poly, world = True )  # unparent
    cmds.select( jnts[0], hi = True )
    cmds.select( tube_poly, add = True )
    # python or mel binSkin didnt work, created too many skinClusters
    sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    # wrap
    dfrmr = createWrap( tube_poly, geo_string )
    # clean up
    cmds.parent( tube_poly, GEO[1] )
    cmds.parent( tube_poly + 'Base', GEO[1] )

    # return None
    # correct joint length, for bend and connect to other side
    for jnt in jnts:
        if '_00' not in jnt:
            pass
            cmds.setAttr( jnt + '.translateZ', new_length )

    '''
    # bend into place, connect tip to opposite end of amulet
    bend_seg = int( ( segments / 2 ) + 0.5 )  # double joint, first joint in segment
    bend_letter = chr( ord( 'a' ) + bend_seg ).upper()  # number to letter
    bend_letter_next = chr( ord( 'a' ) + bend_seg + 1 ).upper()  # number to letter
    jnt_num = str( ( '%0' + str( pad ) + 'd' ) % ( 1 ) )  # pad jnt number
    cmds.setAttr( suffix + bend_letter + '_jnt_' + jnt_num + '.rotateY', -90 )
    cmds.setAttr( suffix + bend_letter_next + '_jnt_' + jnt_num + '.rotateY', -90 )'''

    # place segment controls
    seg = []
    # seg.append( jnts[0] )
    cmds.select( jnts[0], hi = True )
    sel = cmds.ls( sl = True )
    for jnt in sel:
        if '_01' in jnt and jnt != sel[0]:
            seg.append( jnt )
    # print seg
    # return None

    fuseSplines( jnts[0], jnts[-1], X = 0.5 )


def fuseSplines( root_jnt = '', tip_jnt = '', X = 2, upDis = 12 ):
    '''\n
    Build splines\n
    '''
    face = None
    check = cmds.checkBox( 'atom_rat_faceCheck', query = True, v = True )
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)

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
    spineName = 'fuse'
    spineSize = X * 1
    spineDistance = X * upDis
    spineFalloff = 0
    spinePrnt = 'fuseBase_Grp'
    spineStrt = 'fuseBase_Grp'
    spineEnd = 'fuseTip_Grp'
    spineAttr = 'fuseBase'
    spineRoot = root_jnt

    spine = [root_jnt, tip_jnt]
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # assemble
    OptAttr( spineAttr, 'SpineSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 0 )
    cmds.setAttr( spineAttr + '.ClstrVis', 1 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', 1.0 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 1 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # connect multi/div node of spline curves(S/E) to Control group scale
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_E_IK_curve_scale.input2Z' )
    # special case
    '''
    cmds.setAttr( spineName + '_E_IK_Cntrl.rotateY', -180 )
    cmds.setAttr( spineName + '_Vctr_M36_Ctrl.rotateY', -90 )
    cmds.setAttr( spineName + '_Clstr_M37_Ctrl.rotateY', -90 )'''


def dynamite():
    '''
    
    '''
    X = 5
    # main rig groups/controllers
    PreBuild = place.rigPrebuild( Top = 1, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = False, Size = 10 * X )
    cmds.select( cl = True )
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    SKIN_JOINTS = PreBuild[2]
    GEO = PreBuild[3]
    WORLD_SPACE = PreBuild[4]
    MasterCt = PreBuild[5]

    #
    geo_grp = 'Prop_DynamiteStick_lod0_grp'
    geo = [
    'c_dynamite_lod0_geo_0002',
    'c_dynamite_lod0_geo_0001',
    'c_ring_lod0_geo_0001'
    ]
    fuse_geo = 'c_fuse_lod0_geo_0001'
    #
    cmds.parent( geo_grp, GEO[0] )
    # cmds.setAttr( geo_grp + '.translateY', -11.3 )
    # cmds.setAttr( geo_grp + '.translateZ', -9 )
    # cmds.setAttr( geo_grp + '.rotateX', 0.735 )
    # cmds.setAttr( geo_grp + '.rotateY', -2.965 )

    # lock geo - [lock, keyable], [visible, lock, keyable]
    # place.setChannels( geo[0], [True, False], [True, False], [True, False], [False, False, False] )
    # place.setChannels( geo[1], [True, False], [True, False], [True, False], [True, False, False] )

    rt_jnt = cmds.joint( name = 'root_jnt' )
    cmds.parent( rt_jnt, SKIN_JOINTS )
    for g in geo:
        cmds.select( g, rt_jnt )
        mel.eval( 'SmoothBindSkin -tsb;' )

    dstnc = 16
    sz = 3
    # lid_2 #
    Dyn = 'dynamite'
    Dyn = place.Controller( Dyn, MasterCt[0], False, 'facetYup_ctrl', X * sz, 17, 8, 1, ( 0, 0, 1 ), True, True )
    DynCt = Dyn.createController()
    place.setRotOrder( DynCt[0], 2, True )
    cmds.parent( DynCt[0], CONTROLS )
    cmds.setAttr( DynCt[0] + '.translateY', -10.15 )
    cmds.parentConstraint( MasterCt[4], DynCt[0], mo = True )
    cmds.parentConstraint( DynCt[4], rt_jnt, mo = True )

    sz = 2
    # fuse base #
    Fuse = 'fuseBase'
    Fuse = place.Controller( Fuse, MasterCt[0], False, 'facetYup_ctrl', X * sz, 17, 8, 1, ( 0, 0, 1 ), True, True )
    FuseCt = Fuse.createController()
    place.setRotOrder( FuseCt[0], 2, True )
    cmds.parent( FuseCt[0], CONTROLS )
    cmds.setAttr( FuseCt[0] + '.translateY', 10.005 )
    cmds.parentConstraint( DynCt[4], FuseCt[0], mo = True )
    # lock translations [lock, keyable], [visible, lock, keyable]
    place.setChannels( FuseCt[2], [True, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( FuseCt[3], [True, False], [False, True], [True, False], [True, False, False] )

    # fuse tip #
    FuseT = 'fuseTip'
    FuseT = place.Controller( FuseT, MasterCt[0], False, 'facetYup_ctrl', X * sz, 17, 8, 1, ( 0, 0, 1 ), True, True )
    FuseTCt = FuseT.createController()
    place.setRotOrder( FuseTCt[0], 2, True )
    cmds.parent( FuseTCt[0], CONTROLS )
    cmds.setAttr( FuseTCt[0] + '.translateY', 29.204 )
    cmds.parentConstraint( FuseCt[4], FuseTCt[0], mo = True )

    # lid_2 up #
    Lid_2_u = 'tip'
    lid_2_u = place.Controller( Lid_2_u, MasterCt[0], False, 'loc_ctrl', X * sz, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_u_Ct = lid_2_u.createController()
    place.setRotOrder( Lid_2_u_Ct[0], 2, True )
    cmds.parent( Lid_2_u_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_u_Ct[0] + '.translateZ', dstnc / 2 )
    cmds.parentConstraint( MasterCt[4], Lid_2_u_Ct[0], mo = True )

    # lid_2 tip #
    Lid_2_t = 'up'
    lid_2_t = place.Controller( Lid_2_t, MasterCt[0], False, 'loc_ctrl', X * sz, 17, 8, 1, ( 0, 0, 1 ), True, True )
    Lid_2_t_Ct = lid_2_t.createController()
    place.setRotOrder( Lid_2_t_Ct[0], 2, True )
    cmds.parent( Lid_2_t_Ct[0], CONTROLS )
    cmds.setAttr( Lid_2_t_Ct[0] + '.translateY', dstnc )
    cmds.parentConstraint( MasterCt[4], Lid_2_t_Ct[0], mo = True )
    cmds.aimConstraint( Lid_2_t_Ct[4], DynCt[2], wut = 'object', wuo = Lid_2_u_Ct[4], aim = [0, 1, 0], u = [0, 0, 1], mo = False )
    place.setChannels( DynCt[2], [False, True], [True, False], [True, False], [True, False, False] )

    # fuse joints
    full_length = 19.2  # string length
    j_length = 0.252
    # math
    '''
    lengths_in_seg = joints_in_seg - 1  # correct math, need amount of gaps between joints, which is one less than requested
    seg_length = full_length / segments
    length = seg_length / lengths_in_seg
    amount = segments * lengths_in_seg
    '''
    amount = full_length / j_length
    # chain
    suffix = 'fuse'
    pad = 2
    # jnts = place.jointChain( suffix = suffix, pad = pad, length = length, amount = amount, radius = 0.4, dbl = joints_in_seg )
    jnts = place.jointChain( suffix = suffix, pad = pad, length = j_length, amount = amount, radius = 0.1, dbl = '' )
    #
    cmds.setAttr( jnts[0] + '.translateY', 10.005 )
    cmds.setAttr( jnts[0] + '.rotateX', -90 )
    cmds.select( fuse_geo, jnts )
    # print cmds.ls( sl = 1 )
    mel.eval( 'SmoothBindSkin -tsb;' )
    cmds.parent( jnts[0], SKIN_JOINTS )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 20.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    #
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    '''
    #
    misc.scaleUnlock( '___GEO', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___GEO' + s )'''
    #
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )

    fuseSplines( root_jnt = jnts[0], tip_jnt = jnts[-1], X = 0.1, upDis = 30 )

    # clean up
    cmds.parent( 'DYN_CONTROL', WORLD_SPACE )
