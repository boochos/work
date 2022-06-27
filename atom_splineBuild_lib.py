from __future__ import division
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )
spln = web.mod( 'atom_spline_lib' )
joint = web.mod( 'atom_joint_lib' )


def getColors( colorScheme = '' ):
    # colorSchemes
    if colorScheme == 'red':
        return [20, 13]
    elif colorScheme == 'blue':
        return [18, 6]
    else:
        return [22, 17]


###############################################################################
# ############################## STAGE 1 ######################################
def clusterGroup( prefix, X, skinJnts, aim, up, rotate, colorScheme = 'yellow' ):
    colors = getColors( colorScheme )
    if len( skinJnts ) > 2:
        # return
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp = []
        clusterGrps = []

        # Master groups
        cmds.select( skinJnts[0] )
        # #
        MstrPrfx = place.null( ( prefix + '_SplineAllGrp' ) )[0]
        S_MstrSplnGrp = place.null( ( prefix + '_StrtSplnGrp' ) )[0]
        E_MstrSplnGrp = place.null( ( prefix + '_EndSplnGrp' ) )[0]
        SplnCtrlGrp = place.null( ( prefix + '_SplnCtrlGrp' ) )[0]
        ClstrGrp = place.null( ( prefix + '_ClstrGrp' ) )[0]
        cmds.parent( S_MstrSplnGrp, E_MstrSplnGrp, SplnCtrlGrp, MstrPrfx )
        cmds.parent( ClstrGrp, SplnCtrlGrp )
        place.cleanUp( MstrPrfx, Ctrl = True )
        cmds.setAttr( ( S_MstrSplnGrp + '.visibility' ), 0 )
        cmds.setAttr( ( E_MstrSplnGrp + '.visibility' ), 0 )
        cmds.setAttr( ( ClstrGrp + '.visibility' ), 0 )
        # setChannels
        place.setChannels( MstrPrfx, [True, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( S_MstrSplnGrp, [True, False], [True, False], [True, False], [False, False, False] )
        place.setChannels( E_MstrSplnGrp, [True, False], [True, False], [True, False], [False, False, False] )
        place.setChannels( SplnCtrlGrp, [True, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( ClstrGrp, [False, False], [False, False], [True, False], [False, False, False] )

        # #
        cmds.select( skinJnts )

        # place start ik joints
        # #aim = 'X', 'Y' or 'Z'
        # #up = 'X', 'Y' or 'Z'
        # #rotate = 'X', 'Y' or 'Z'
        # #sao = xup, xdown, yup, ydown, zup, zdown
        Sjnt = place.joint( 0, ( prefix + '_S_jnt' ) )
        # orient joints
        # hardcoding 'oj' value. Shouldn't be any different. Otherwise spline up vector breaks.
        cmds.joint( Sjnt[0], e = True, oj = 'xyz', sao = 'yup', ch = True )
        for item in Sjnt:
            joint.ZeroJointOrient( item )
        cmds.setAttr( Sjnt[len( Sjnt ) - 1] + '.jointOrientX', 0 )
        cmds.setAttr( Sjnt[len( Sjnt ) - 1] + '.jointOrientY', 0 )
        cmds.setAttr( Sjnt[len( Sjnt ) - 1] + '.jointOrientZ', 0 )

        # make splineIk
        Sitems = spln.splineIK( ( prefix + '_S_IK' ), Sjnt[0], ( Sjnt[len( Sjnt ) - 1] ) )  # Sitems contains ik, effector, curve respectively.
        # make clusters from start ik curve
        Sc = place.clstrOnCV( Sitems[2], ( prefix + '_S_Clstr_' ) )

        # Start Stretch
        # needs curve from Sitems
        Sblnd = spln.StretchNodes( ( prefix + '_S_M' ), Sitems[2], Sjnt )

        # reselect selection
        cmds.select( skinJnts )
        # place end ik joints
        # #aim = 'X', 'Y' or 'Z'
        # #up = 'X', 'Y' or 'Z'
        # #rotate = 'X', 'Y' or 'Z'
        # #sao = xup, xdown, yup, ydown, zup, zdown
        Ejnt = place.joint( 1, ( prefix + '_E_jnt' ) )
        # #cmds.delete(Ejnt[len(Ejnt) -1])
        # orient joints
        # hardcoding 'oj' value. Shouldn't be any different. Otherwise spline up vector breaks.
        cmds.joint( Ejnt[0], e = True, oj = 'xyz', sao = 'yup', ch = True )
        for item in Ejnt:
            joint.ZeroJointOrient( item )
        # cmds.setAttr(Ejnt[len(Ejnt)-1] + '.jointOrientX', 0)
        # cmds.setAttr(Ejnt[len(Ejnt)-1] + '.jointOrientY', 0)
        # cmds.setAttr(Ejnt[len(Ejnt)-1] + '.jointOrientZ', 0)

        # make splineIk
        Eitems = spln.splineIK( ( prefix + '_E_IK' ), Ejnt[0], ( Ejnt[len( Ejnt ) - 1] ) )
        # create clusters from end ik curve
        Ec = place.clstrOnCV( Eitems[2], ( prefix + '_E_Clstr_' ) )

        # End Stretch
        # needs curve from Sitems
        Eblnd = spln.StretchNodes( ( prefix + '_E_M' ), Eitems[2], Ejnt )

        # Parent items
        cmds.parent( Sc, Ec, ClstrGrp )
        cmds.parent( Sjnt[0], Sitems[0], Sitems[2], S_MstrSplnGrp )
        cmds.parent( Ejnt[0], Eitems[0], Eitems[2], E_MstrSplnGrp )
        place.cleanUp( Sitems[2], World = True )
        place.cleanUp( Eitems[2], World = True )

        # place joints on CVs, point z down y up
        # for pointing down z... will be deleted
        cmds.select( skinJnts )
        Xjnt = cmds.duplicate( rc = True )
        par = cmds.select( Xjnt[0] ), cmds.pickWalk( d = 'up' )
        if par[1][0] != Xjnt[0]:
            cmds.parent( Xjnt[0], w = True )
        child = cmds.select( Xjnt[len( skinJnts ) - 1] ), cmds.pickWalk( d = 'down' )
        if child[1][0] != Xjnt[len( Xjnt ) - 1]:
            cmds.delete( Xjnt[len( skinJnts ):] )
        cmds.select( Xjnt[0], hi = True )
        Xjnt = cmds.ls( sl = True )
        F = cmds.insertJoint( Xjnt[0] )
        L = cmds.insertJoint( Xjnt[len( Xjnt ) - 2] )
        Fpos = cmds.xform( Sc[1], q = True, rp = True, ws = True )
        Frot = cmds.xform( Xjnt[0], q = True, ro = True, ws = True )
        Lpos = cmds.xform( Sc[len( Sc ) - 2], q = True, rp = True, ws = True )
        Lrot = cmds.xform( Xjnt[len( Xjnt ) - 1], q = True, ro = True, ws = True )
        cmds.joint( F, e = True, co = True, p = Fpos )
        # cmds.joint(F, e=True, co=True, o=Frot )
        cmds.joint( L, e = True, co = True, p = Lpos )
        # cmds.joint(L, e=True, co=True, o=Lrot )

        Xjnt.insert( int( len( Xjnt ) - 1 ), L )
        Xjnt.insert( 1, F )

        # create cluster constrain groups
        # mid positions
        jj = 1
        for i in range( 0, len( Sc ), 1 ):
            if i == 0:
                # Start
                cmds.select( Xjnt[0] )
                ScnsG = place.null( ( prefix + '_S_ClstrGrp' ) )
                clusterGrps.append( ScnsG[0] )
                cmds.pointConstraint( ScnsG, Sc[0], mo = True, w = 1.0 )
                cmds.pointConstraint( ScnsG, Ec[( len( Ec ) - 1 )], mo = True, w = 1.0 )
            elif i == ( len( Sc ) - 1 ):
                # End
                cmds.select( Xjnt[len( Xjnt ) - 1] )
                EcnsG = place.null( ( prefix + '_E_ClstrGrp' ) )
                clusterGrps.append( EcnsG[0] )
                cmds.pointConstraint( EcnsG, ( Sc[( len( Sc ) - 1 )] ), mo = True, w = 1.0 )
                cmds.pointConstraint( EcnsG, Ec[0], mo = True, w = 1.0 )
            else:
                # Mid
                cmds.select( Xjnt[i] )
                McnsG = place.null( ( prefix + '_M' + str( jj ) + '_ClstrGrp' ) )
                clusterGrps.append( McnsG[0] )
                cmds.pointConstraint( McnsG, Sc[i], mo = True, w = 1.0 )
                cmds.pointConstraint( McnsG, ( Ec[( len( Sc ) - ( i + 1 ) )] ), mo = True, w = 1.0 )
                jj = jj + 1

        # Delete XJnts
        cmds.delete( Xjnt )

        # Create full List
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( clusterGrps )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Sjnt )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Ejnt )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Sblnd )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Eblnd )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Sitems[2] )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Sitems[0] )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( Eitems[0] )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( SplnCtrlGrp )
        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp.append( ClstrGrp )
        return BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp
    else:
        mel.eval( 'warning \"' + '////... Select odd number of objects. Minimum is 3 ...////' + '\";' )
        return None


###############################################################################
# ############################## STAGE 2 ######################################
def clusterControlGroup( prefix, suffix, X, aim, buildControls, skinJnts, rotOrder, function, F,
                        BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp, colorScheme = 'yellow' ):
    colors = getColors( colorScheme )
    # sel = cmds.ls(sl=True)
    if len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) > 2:
        # cluster control parent group
        cmds.select( skinJnts[0] )
        # ClstrCtrlGrp = place.null((prefix + suffix + '_CtrlGrp'))[0]
        # print ClstrCtrlGrp
        ClstrCtrlGrp = place.null2( prefix + suffix + '_CtrlGrp', skinJnts[0] )[0]

        # cluster group attrs
        place.setChannels( ClstrCtrlGrp, [False, False], [False, False], [True, False], [True, False, False] )
        place.addAttribute( ClstrCtrlGrp, suffix[1:] + 'Vis', 0, 1, 0, 'long' )
        attrList = [suffix[1:] + 'MidSEPosWeight', suffix[1:] + 'MidIkBlend', suffix[1:] + 'MidIkSE_W', suffix[1:] + 'TangentVis', suffix[1:] + 'Vis']
        place.addAttribute( ClstrCtrlGrp, attrList[3], 0, 1, 0, 'long' )
        place.addAttribute( ClstrCtrlGrp, attrList[:3], 0, 1, 1, 'double' )
        cmds.setAttr( ( ClstrCtrlGrp + '.' + attrList[0] ), 0.5 )
        cmds.setAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), 1.0 )
        cmds.setAttr( ( ClstrCtrlGrp + '.' + attrList[2] ), 0.5 )
        cmds.connectAttr( ClstrCtrlGrp + '.' + attrList[4], ClstrCtrlGrp + '.visibility', f = True )
        cmds.setAttr( ClstrCtrlGrp + '.visibility', cb = False )
        # hide pos weight attr, tangent weight attr... Unless needed
        cmds.setAttr( ClstrCtrlGrp + '.' + attrList[0], k = False, cb = False )
        cmds.setAttr( ClstrCtrlGrp + '.' + attrList[3], k = False, cb = False )
        # parent cluster group
        cmds.parent( ClstrCtrlGrp, BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[8] )

        #
        jj = 1
        ClusterCntrls = []
        SMidClusterCntrls = []
        EMidClusterCntrls = []
        ClusterCntrlGrps = []
        XtraP = []
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP = []
        Sloc = None
        Sfun = int
        Efun = int

        if function == 0:
            Sfun = 0
            Efun = 1
        else:
            Sfun = 1
            Efun = 0

        # Create start/end/middle group structure
        # Start Position Groups
        cmds.select( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][0] )
        if buildControls == 0:
            Sloc = BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][0]
        else:
            Sloc = place.circle( prefix + suffix + '_S_Ctrl', BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][0], 'diamond_ctrl', X * ( 1.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            cmds.parent( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][0], Sloc )
        cmds.select( Sloc )
        ClusterCntrls.append( Sloc )
        Spr = place.insert( 'null', 1, ( ( prefix + suffix + '_S_PrntGrp' ) ) )[0]
        cmds.select( Spr )
        Sps = place.insert( 'null', 1, ( ( prefix + suffix + '_S_PosGrp' ) ) )[0]
        # cmds.setAttr(Sps[0] + '.rotateOrder', rotOrder)
        place.setChannels( Sps[0], [False, False], [False, False], [True, False], [True, False, False] )
        ClusterCntrlGrps.append( Sps[0] )
        cmds.parent( Sps, ClstrCtrlGrp )
        cmds.select( Sloc )
        SMps = place.insert( 'null', 0, ( ( prefix + suffix + '_S_M_PosGrp' ) ) )[0]

        # End Position Groups
        cmds.select( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 )] )
        if buildControls == 0:
            Eloc = BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 )]
        else:
            Eloc = place.circle( prefix + suffix + '_E_Ctrl', BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 )], 'diamond_ctrl', X * ( 1.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            cmds.parent( ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 )] ), Eloc )
        cmds.select( Eloc )
        Epr = place.insert( 'null', 1, ( ( prefix + suffix + '_E_PrntGrp' ) ) )[0]
        cmds.select( Epr )
        Eps = place.insert( 'null', 1, ( ( prefix + suffix + '_E_PosGrp' ) ) )[0]
        # cmds.setAttr(Eps[0] + '.rotateOrder', rotOrder)
        place.setChannels( Eps[0], [False, False], [False, False], [True, False], [True, False, False] )
        # clusterCntrlGrps.append(Eps[0]) added at the end for order consistency
        cmds.parent( Eps, ClstrCtrlGrp )
        cmds.select( Eloc )
        EMps = place.insert( 'null', 0, ( ( prefix + suffix + '_E_M_PosGrp' ) ) )[0]

        # Middle Position Groups
        num = str( int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 ) )
        cmds.select( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 )] )
        if buildControls == 0:
            MMloc = BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 )]
        else:
            MMloc = place.circle( prefix + suffix + '_M' + num + '_Ctrl', BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 )], 'v_ctrl', X * ( 1.6 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            cmds.parent( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 )], MMloc )
        cmds.select( MMloc )
        ClusterCntrls.append( MMloc )
        MMpr = place.insert( 'null', 1, ( prefix + suffix + '_M' + num + '_PrntGrp' ) )[0][0]
        cmds.select( MMpr )
        MMps = place.insert( 'null', 1, ( prefix + suffix + '_M' + num + '_PosGrp' ) )[0]
        XPrntCnstrnt = cmds.pointConstraint( MMps, MMpr, mo = True, w = 0 )[0]
        # ClusterCntrlGrps.append(MMps[0]) ...command moved to first iteration of second for loop
        cmds.parent( MMps, ClstrCtrlGrp )
        cmds.select( MMloc )
        MMMps = place.insert( 'null', 0, ( prefix + suffix + 'M_M' + num + '_PosGrp' ) )[0]
        # Corresponding groups under 'S' and 'E'
        Sprn = place.circle( prefix + suffix + '_S_M' + num + '_PrntGrp', MMloc, 'diamond_ctrl', X * ( 0.4 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[3] ), ( Sprn + '.visibility' ), f = True )
        cmds.parent( Sprn, Sloc )
        PrntCnstrnt = cmds.pointConstraint( Sprn, MMpr, mo = True, w = 0.5 )[0]
        Eprn = place.circle( prefix + suffix + '_E_M' + num + '_PrntGrp', MMloc, 'diamond_ctrl', X * ( 0.4 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[3] ), ( Eprn + '.visibility' ), f = True )
        cmds.parent( Eprn, Eloc )
        cmds.pointConstraint( Eprn, MMpr, mo = True, w = 0.5 )
        cmds.setAttr( XPrntCnstrnt + '.restTranslateX', 0 )
        cmds.setAttr( XPrntCnstrnt + '.restTranslateY', 0 )
        cmds.setAttr( XPrntCnstrnt + '.restTranslateZ', 0 )
        PosCnstrnt = cmds.pointConstraint( SMps, MMps, mo = True, w = 0.5 )[0]
        cmds.pointConstraint( EMps, MMps, mo = True, w = 0.5 )
        # Set Channels
        place.setChannels( MMps[0], [False, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( MMpr, [False, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( Spr[0], [False, False], [False, False], [True, False], [True, False, False] )
        place.setChannels( Epr[0], [False, False], [False, False], [True, False], [True, False, False] )

        # Weight options for middle cluster
        # Parent group
        MidIK_PrntBlnd = cmds.shadingNode( 'blendColors', name = ( prefix + suffix + '_MidIK_WghtBlend' ), asUtility = True )
        # on blend, 0 = second input, 1 = first input
        # connect 'MidIkOnOff' to blender
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( MidIK_PrntBlnd + '.blender' ), f = True )
        # create reverse
        Bool_MidIK_PrntRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_MidIK_OnOff_Reverse' ), asUtility = True )
        Wght_MidIK_PrntRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_MidIK_Weight_Reverse' ), asUtility = True )
        # connect 'MidIkWeight' to reverse
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( Bool_MidIK_PrntRvrs + '.inputX' ), f = True )
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[2] ), ( Wght_MidIK_PrntRvrs + '.inputX' ), f = True )
        # connect ''MidIkWeight' to blends first input
        # cmds.connectAttr((ClstrCtrlGrp + '.' + attrList[2]), (MidIK_PrntBlnd + '.color1G'), f=True)
        # connect 'MidR' to blends first input
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[2] ), ( MidIK_PrntBlnd + '.color1R' ), f = True )
        cmds.connectAttr( ( Wght_MidIK_PrntRvrs + '.outputX' ), ( MidIK_PrntBlnd + '.color1G' ), f = True )
        cmds.connectAttr( ( Bool_MidIK_PrntRvrs + '.outputX' ), ( MidIK_PrntBlnd + '.color1B' ), f = True )

        # constraint connect
        attrs = cmds.listAttr( PrntCnstrnt, k = True )
        weightAttrs = attrs[-3:]
        cmds.connectAttr( ( MidIK_PrntBlnd + '.outputR' ), ( PrntCnstrnt + '.' + weightAttrs[2] ), f = True )
        cmds.connectAttr( ( MidIK_PrntBlnd + '.outputG' ), ( PrntCnstrnt + '.' + weightAttrs[1] ), f = True )
        cmds.connectAttr( ( MidIK_PrntBlnd + '.outputB' ), ( PrntCnstrnt + '.' + weightAttrs[0] ), f = True )

        # Position group
        # create reverse
        MidIK_PosRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_MidIK_Reverse' ), asUtility = True )
        # connect 'MidIkWeight' to reverse
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[0] ), ( MidIK_PosRvrs + '.inputX' ), f = True )
        # constraint connect
        attrs = cmds.listAttr( PosCnstrnt, k = True )
        weightAttrs = attrs[-2:]
        cmds.connectAttr( ( MidIK_PosRvrs + '.outputX' ), ( PosCnstrnt + '.' + weightAttrs[0] ), f = True )
        cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[0] ), ( PosCnstrnt + '.' + weightAttrs[1] ), f = True )

        # Split list in two ##
        # division point -int-
        centerOfList = int( ( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0] ) - 1 ) / 2 )
        # START to MIDDLE -list-
        S_M = BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][:( centerOfList + 1 )]
        # MIDDLE to END -list-
        M_E = BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[0][centerOfList:]

        # Create 'mid' group structure
        # #Start - Middle
        for i in range( 0, len( S_M ), 1 ):
            if i == 0:
                pass
                # print '-skip start-'
            elif i == ( len( S_M ) - 1 ):
                pass
                # print '-skip end-'
            else:
                cc = spln.blendWeight2( S_M, i, Sfun, F )
                # print cc
                # Hierarchy
                # Mid Left-Over Position Groups
                cmds.select( S_M[i] )
                if buildControls == 0:
                    Mloc = S_M[i]
                else:
                    Mloc = place.circle( prefix + suffix + '_M' + str( jj ) + '_Ctrl', S_M[i], 'diamond_ctrl', X * ( 0.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
                    cmds.parent( S_M[i], Mloc )
                cmds.select( Mloc )
                SMidClusterCntrls.append( Mloc )
                Mpr = place.insert( 'null', 1, ( prefix + suffix + '_M' + str( jj ) + '_PrntGrp' ) )[0]
                # Corresponding groups under 'S' and 'M'
                Sprn = place.null( ( prefix + suffix + '_S_M' + str( jj ) + '_PrntGrp' ) )[0]
                cmds.parent( Sprn, Sloc )
                SPrntCnstrnt = cmds.pointConstraint( Sprn, Mpr, mo = False, w = cc[0] )[0]
                MMprn = place.null( ( prefix + suffix + '_MM_M' + str( jj ) + '_PrntGrp' ) )[0]
                cmds.parent( MMprn, MMloc )
                EPrntCnstrnt = cmds.pointConstraint( MMprn, Mpr, mo = False, w = cc[1] )[0]
                cmds.select( Mpr )
                Mps = place.insert( 'null', 1, ( prefix + suffix + '_M' + str( jj ) + '_PosGrp' ) )[0]
                XPrntCnstrnt = cmds.pointConstraint( Mps, Mpr, mo = True, w = 0 )[0]
                cmds.setAttr( XPrntCnstrnt + '.restTranslateX', 0 )
                cmds.setAttr( XPrntCnstrnt + '.restTranslateY', 0 )
                cmds.setAttr( XPrntCnstrnt + '.restTranslateZ', 0 )
                ClusterCntrlGrps.append( Mps[0] )
                cmds.parent( Mps, ClstrCtrlGrp )
                cmds.pointConstraint( SMps, Mps, mo = True, w = cc[0] )
                cmds.pointConstraint( MMMps, Mps, mo = True, w = cc[1] )
                # #
                # Weight options for middle cluster
                # Parent group
                SMidIK_PrntBlnd = cmds.shadingNode( 'blendColors', name = ( prefix + suffix + '_MidIK' + str( jj ) + '_WghtBlend' ), asUtility = True )
                # on blend, 0 = second input, 1 = first input
                # connect 'MidIkOnOff' to blender
                cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( SMidIK_PrntBlnd + '.blender' ), f = True )
                # create reverse
                SMidIK_PrntRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_MidIK' + str( jj ) + '_Reverse' ), asUtility = True )
                # connect 'MidIkWeight' to reverse
                cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( SMidIK_PrntRvrs + '.inputX' ), f = True )
                cmds.connectAttr( ( SMidIK_PrntRvrs + '.outputX' ), ( SMidIK_PrntBlnd + '.color1B' ), f = True )
                # connect ''MidIkWeight' to blends first input
                cmds.setAttr( SMidIK_PrntBlnd + '.color1R', cc[0] )
                cmds.setAttr( SMidIK_PrntBlnd + '.color1G', cc[1] )
                # constraint connect
                attrs = cmds.listAttr( SPrntCnstrnt, k = True )
                weightAttrs = attrs[-3:]
                cmds.connectAttr( ( SMidIK_PrntBlnd + '.outputR' ), ( SPrntCnstrnt + '.' + weightAttrs[0] ), f = True )
                cmds.connectAttr( ( SMidIK_PrntBlnd + '.outputG' ), ( SPrntCnstrnt + '.' + weightAttrs[1] ), f = True )
                cmds.connectAttr( ( SMidIK_PrntBlnd + '.outputB' ), ( SPrntCnstrnt + '.' + weightAttrs[2] ), f = True )
                # Set Channels
                place.setChannels( Mloc, [False, True], [False, False], [True, False], [True, False, False] )
                place.setChannels( Mpr[0], [False, False], [True, False], [True, False], [True, False, False] )
                place.setChannels( Sprn, [False, False], [True, False], [True, False], [True, False, False] )
                place.setChannels( MMprn, [False, False], [True, False], [True, False], [True, False, False] )
                # #
                jj = jj + 1
        jj = jj + 1

        # #Middle - End
        for i in range( 0, len( M_E ), 1 ):
            if i == 0:
                pass
                # print '-skip start-'
                ClusterCntrlGrps.append( MMps[0] )
            elif i == ( len( M_E ) - 1 ):
                pass
                # print '-skip end-'
            else:
                cc = spln.blendWeight2( M_E, i, Efun, F )
                # print cc
                # Hierarchy
                # Mid Left-Over Position Groups
                cmds.select( M_E[i] )
                if buildControls == 0:
                    Mloc = M_E[i]
                else:
                    Mloc = place.circle( prefix + suffix + '_M' + str( jj ) + '_Ctrl', M_E[i], 'diamond_ctrl', X * ( 0.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
                    cmds.parent( M_E[i], Mloc )
                cmds.select( Mloc )
                EMidClusterCntrls.append( Mloc )
                Mpr = place.insert( 'null', 1, ( prefix + suffix + '_M' + str( jj ) + '_PrntGrp' ) )[0]
                # Corresponding groups under 'M' and 'E'
                MMprn = place.null( ( prefix + suffix + '_MM_M' + str( jj ) + '_PrntGrp' ) )[0]
                cmds.parent( MMprn, MMloc )
                SPrntCnstrnt = cmds.pointConstraint( MMprn, Mpr, mo = True, w = cc[0] )[0]
                Eprn = place.null( ( prefix + suffix + '_E_M' + str( jj ) + '_PrntGrp' ) )[0]
                cmds.parent( Eprn, Eloc )
                EPrntCnstrnt = cmds.pointConstraint( Eprn, Mpr, mo = True, w = cc[1] )[0]
                cmds.select( Mpr )
                Mps = place.insert( 'null', 1, ( prefix + suffix + '_M' + str( jj ) + '_PosGrp' ) )[0]
                XPrntCnstrnt = cmds.pointConstraint( Mps, Mpr, mo = True, w = 0 )[0]
                cmds.setAttr( XPrntCnstrnt + '.restTranslateX', 0 )
                cmds.setAttr( XPrntCnstrnt + '.restTranslateY', 0 )
                cmds.setAttr( XPrntCnstrnt + '.restTranslateZ', 0 )
                ClusterCntrlGrps.append( Mps[0] )
                cmds.parent( Mps, ClstrCtrlGrp )
                cmds.pointConstraint( MMMps, Mps, mo = True, w = cc[0] )
                cmds.pointConstraint( EMps, Mps, mo = True, w = cc[1] )
                # #
                # Weight options for middle cluster
                # Parent group
                EMidIK_PrntBlnd = cmds.shadingNode( 'blendColors', name = ( prefix + suffix + '_MidIK' + str( jj ) + '_WghtBlend' ), asUtility = True )
                # on blend, 0 = second input, 1 = first input
                # connect 'MidIkOnOff' to blender
                cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( EMidIK_PrntBlnd + '.blender' ), f = True )
                # create reverse
                EMidIK_PrntRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_MidIK' + str( jj ) + '_Reverse' ), asUtility = True )
                # connect 'MidIkWeight' to reverse
                cmds.connectAttr( ( ClstrCtrlGrp + '.' + attrList[1] ), ( EMidIK_PrntRvrs + '.inputX' ), f = True )
                cmds.connectAttr( ( EMidIK_PrntRvrs + '.outputX' ), ( EMidIK_PrntBlnd + '.color1B' ), f = True )
                # #
                cmds.setAttr( EMidIK_PrntBlnd + '.color1R', cc[0] )
                cmds.setAttr( EMidIK_PrntBlnd + '.color1G', cc[1] )
                # constraint connect
                attrs = cmds.listAttr( SPrntCnstrnt, k = True )
                weightAttrs = attrs[-3:]
                cmds.connectAttr( ( EMidIK_PrntBlnd + '.outputR' ), ( SPrntCnstrnt + '.' + weightAttrs[0] ), f = True )
                cmds.connectAttr( ( EMidIK_PrntBlnd + '.outputG' ), ( SPrntCnstrnt + '.' + weightAttrs[1] ), f = True )
                cmds.connectAttr( ( EMidIK_PrntBlnd + '.outputB' ), ( SPrntCnstrnt + '.' + weightAttrs[2] ), f = True )
                # Set Channels
                place.setChannels( Mloc, [False, True], [False, False], [True, False], [True, False, False] )
                place.setChannels( Mpr[0], [False, False], [True, False], [True, False], [True, False, False] )
                place.setChannels( Eprn, [False, False], [True, False], [True, False], [True, False, False] )
                place.setChannels( MMprn, [False, False], [True, False], [True, False], [True, False, False] )
                # #

                jj = jj + 1
        # moved to when objects are created
        # #cmds.setAttr(Sps[0] + '.rotateOrder', rotOrder)
        # #cmds.setAttr(Eps[0] + '.rotateOrder', rotOrder)
        ClusterCntrlGrps.append( Eps[0] )
        ClusterCntrls.append( Eloc )
        XtraP.append( MMpr )

        #
        # Guides
        # guide grp
        guideGp = 'GuideGp'
        if cmds.objExists( guideGp ) == 0:
            cmds.group( em = True, name = guideGp )
            try:
                cmds.parent( guideGp, '___WORLD_SPACE' )
            except:
                pass
            place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )

        Controls = []
        Controls.append( ClusterCntrls[0] )
        for item in SMidClusterCntrls:
            Controls.append( item )
        Controls.append( ClusterCntrls[1] )
        for item in EMidClusterCntrls:
            Controls.append( item )
        Controls.append( ClusterCntrls[2] )
        # create guide groups
        cmds.select( skinJnts[0] )
        guideGrp = cmds.group( em = True, name = prefix + suffix + '_Ctrl_GuideGrp' )
        guideClstr = cmds.group( em = True, name = prefix + suffix + '_Ctrl_GuideClstrGrp' )
        guideCrv = cmds.group( em = True, name = prefix + suffix + '_Ctrl_GuideCrvGrp' )
        cmds.parent( guideClstr, guideCrv, guideGrp )
        cmds.parent( guideGrp, guideGp )
        cmds.connectAttr( ClstrCtrlGrp + '.visibility', guideCrv + '.visibility' )
        place.setChannels( guideGrp, [True, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( guideClstr, [True, False], [True, False], [True, False], [True, False, False] )
        place.setChannels( guideCrv, [True, False], [True, False], [True, False], [False, False, False] )
        # create guides
        for i in range( 0, len( Controls ) - 1, 1 ):
            CrvCls = place.guideLine( Controls[i], Controls[i + 1], prefix + suffix + '_Guide' )
            cmds.parent( CrvCls[0], guideCrv )
            cmds.parent( CrvCls[1], guideClstr )
            place.setChannels( CrvCls[0], [False, False], [False, False], [False, False], [True, False, False] )
            place.setChannels( CrvCls[1][0], [False, False], [False, False], [False, False], [False, False, False] )
            place.setChannels( CrvCls[1][1], [False, False], [False, False], [False, False], [False, False, False] )
        #

        # Set Control Channels
        for i in range( 0, len( ClusterCntrls ), 1 ):
            # Start
            if i == 0:
                place.setChannels( ClusterCntrls[i], [False, True], [False, True], [True, False], [True, False, False] )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), l = False, cb = True )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), k = True )
            # Middle
            elif i == ( len( ClusterCntrls ) - 1 ) / 2:
                place.setChannels( ClusterCntrls[i], [False, True], [False, True], [True, False], [True, False, False] )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), l = False, cb = True )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), k = True )
            # Last
            elif i == len( ClusterCntrls ) - 1:
                place.setChannels( ClusterCntrls[i], [False, True], [False, True], [True, False], [True, False, False] )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), l = False, cb = True )
                cmds.setAttr( ClusterCntrls[i] + '.scale' + str( aim.upper() ), k = True )
            # All other positions
            else:
                place.setChannels( ClusterCntrls[i], [False, True], [False, True], [True, False], [True, False, False] )
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP.append( ClusterCntrlGrps )
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP.append( ClstrCtrlGrp )
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP.append( attrList )
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP.append( ClusterCntrls )
        BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP.append( XtraP )

        return BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP
    else:
        mel.eval( 'warning \"' + '////... Select odd number of objects. Minimum is 3 ...////' + '\";' )
        return None
###############################################################################
# ############################## STAGE 3 ######################################


def ikGroup( prefix, X, skinJnts, rotOrder, BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp,
            BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP, colorScheme = 'yellow' ):
    # print '?'
    colors = getColors( colorScheme )
    # Variables
    # print 'ikg start'
    # point constrained to start/end ik joints
    # aim constrained at 'M_IK_AimCnst' under next controller position in next stage
    # ('M' +  str(jj) + '_IK_PrntGrp')
    xprnt = []

    # worldUpObjects' parent gets pointConstrained to this position in next stage
    # ('M' +  str(jj) + '_IK_UpVtr')
    xvtr = []

    # prnt group is aimed att this group in next position
    # ('E_IK_AimCnst')
    xaim = []

    # start ik controllers
    # ('S_IK_Cntrl'),('S_IK_Cntrl_Offst')
    xScnrl = []

    # end ik controllers
    # ('E_IK_Cntrl'),('E_IK_Cntrl_Offst')
    xEcnrl = []

    # number(int) of postions for ik controllers and joints
    # used in calculating twist weighting in mid ik controller positions
    xik = len( skinJnts )

    # matrix test
    # #not used
    xjnt = []

    # up vector object is created in stage 4, needs constraint name
    xcnstrnt = []

    # start/end prnt goups
    SEprnt = [None, None]

    # returned list
    # culmination of above
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt = []

    # Ik parent group
    cmds.select( skinJnts[0] )
    grp = place.null( ( prefix + '_IK_CtrlGrp' ) )[0]

    # add attributes to grp
    # prefixPlus = prefix + 'Vis'
    prefixPlus = 'Vis'  # removed prefix
    place.addAttribute( grp, prefixPlus, 0, 1, 0, 'long' )
    cmds.connectAttr( ( grp + '.' + prefixPlus ), ( grp + '.visibility' ), f = True )
    cmds.setAttr( grp + '.' + prefixPlus, 1 )
    # attrList = [prefix + 'Root', prefix + 'Stretch']
    attrList = [ 'Root', 'Stretch']  # removed prefix
    place.addAttribute( grp, attrList, 0, 1, 1, 'double' )
    # add attrs from cluster group
    place.hijackCustomAttrs( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], grp )
    # Hierarchy
    # parent ClusterControl and ClusterGroup group under Ik group
    cmds.parentConstraint( grp, BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], mo = True )
    cmds.parentConstraint( grp, BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[9], mo = True )
    # parent Ik group under Spline Control group
    cmds.parent( grp, BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[8] )
    # setChannels
    # place.setChannels(BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], [False, False], [False, False], [True, False], [True, False, False])

    # connect stretch blends(BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp - form stage 1) to 'grp'
    for i in range( 0, len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[3] ), 1 ):
        cmds.connectAttr( ( grp + '.' + attrList[1] ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[3][i] + '.blender' ), f = True )
        cmds.connectAttr( ( grp + '.' + attrList[1] ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[4][i] + '.blender' ), f = True )

    #
    # Root switch for -middle- only needs 2 values. One through reverse node
    # Root value drives constraint of middle groups
    # create blend
    MidB = cmds.shadingNode( 'blendColors', name = ( prefix + '_M_rootBlend' ), asUtility = True )
    # on blend, 0 = second input, 1 = first input
    cmds.setAttr( MidB + '.blender', 0 )
    # create reverse. Also used in 'SRblnd' and 'ERblnd' blends
    MidR = cmds.shadingNode( 'reverse', name = ( prefix + '_M_rootReverse' ), asUtility = True )
    # connect 'Root' to reverse
    cmds.connectAttr( ( grp + '.' + attrList[0] ), ( MidR + '.inputX' ), f = True )
    # connect 'Root' to blends second input
    cmds.connectAttr( ( grp + '.' + attrList[0] ), ( MidB + '.color2G' ), f = True )
    # connect 'MidR' to blends second input
    cmds.connectAttr( ( MidR + '.outputX' ), ( MidB + '.color2R' ), f = True )
    #

    #
    # Root switch for -start- needs 4 values.
    # Stretch value drives constraint of middle groups
    # Paradigm = if root is switched but stretch is on, start joint has to stay on controls position
    # create blend
    SRblnd = cmds.shadingNode( 'blendColors', name = ( prefix + '_S_rootBlend' ), asUtility = True )
    # on blend, 0 = second input, 1 = first input
    cmds.setAttr( SRblnd + '.blender', 0 )
    # create reverse
    StrtR = cmds.shadingNode( 'reverse', name = ( prefix + '_S_rootReverse' ), asUtility = True )
    # connect 'Stretch' attr to reverse
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( StrtR + '.inputX' ), f = True )
    # Blend First Pair of Inputs
    # connect 'Stretch' attr to blends first input
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( SRblnd + '.color1R' ), f = True )
    # connect  'MidR' to blends second input
    cmds.connectAttr( ( StrtR + '.outputX' ), ( SRblnd + '.color1G' ), f = True )
    # Blend Second Pair of Inputs
    # connect 'RootSwitch' attr to blends first input
    cmds.connectAttr( ( grp + '.' + attrList[0] ), ( SRblnd + '.color2G' ), f = True )
    # connect 'StrtR' to blends first input
    cmds.connectAttr( ( MidR + '.outputX' ), ( SRblnd + '.color2R' ), f = True )
    # Blend 'Blender' Input
    # connect 'Stretch' attr to blends 'Blender' input
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( SRblnd + '.blender' ), f = True )
    #

    #
    # Root switch for -end- needs 4 values.
    # Stretch value drives constraint of middle groups
    # Paradigm = if root is switched but stretch is on, end joint has to stay on controls position
    # create blend
    ERblnd = cmds.shadingNode( 'blendColors', name = ( prefix + '_E_rootBlend' ), asUtility = True )
    # on blend, 0 = second input, 1 = first input
    cmds.setAttr( ERblnd + '.blender', 0 )
    # create reverse
    EndR = cmds.shadingNode( 'reverse', name = ( prefix + '_E_rootReverse' ), asUtility = True )
    # connect 'Stretch' attr to reverse
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( EndR + '.inputX' ), f = True )
    # Blend First Pair of Inputs
    # connect 'RootSwitch' attr to blends second input
    cmds.connectAttr( ( grp + '.' + attrList[0] ), ( ERblnd + '.color2G' ), f = True )
    # connect  'MidR' to blends second input
    cmds.connectAttr( ( MidR + '.outputX' ), ( ERblnd + '.color2R' ), f = True )
    # Blend Second Pair of Inputs
    # connect 'Stretch' attr to blends first input
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( ERblnd + '.color1G' ), f = True )
    # connect 'EndR' to blends first input
    cmds.connectAttr( ( EndR + '.outputX' ), ( ERblnd + '.color1R' ), f = True )
    # Blend 'Blender' Input
    # connect 'Stretch' attr to blends 'Blender' input
    cmds.connectAttr( ( grp + '.' + attrList[1] ), ( ERblnd + '.blender' ), f = True )
    #
    # Ik controls/groups
    # Tanget Attrs are connected in Stage 4... This order has to stay consistent else update Stage 4. Vis attr is added last.
    OptAttrs = ['LockOrientOffOn', 'SplineTangent', 'VectorTangent']
    vis = 'Offset_Vis'
    jj = 1
    for i in range( 0, len( skinJnts ), 1 ):
        if i == 0:
            # first, no aim groups, no vector groups
            # create nulls
            cmds.select( skinJnts[i] )
            prnt = place.null( prefix + '_S_IK_PrntGrp' )
            SEprnt[0] = prnt[0]
            place.setChannels( prnt[0], [False, True], [False, True], [True, False], [True, False, False] )
            ctrl = place.circle( prefix + '_S_IK_Cntrl', skinJnts[i], 'splineStart_ctrl', X * ( 2.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            ctrlOfst = place.circle( prefix + '_S_IK_Cntrl_Offst', skinJnts[i], 'splineStart_ctrl', X * ( 2.2 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            place.setChannels( ctrl, [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( ctrlOfst, [False, True], [False, True], [True, False], [True, False, False] )
            # intermediate nulls for orientation option
            cmds.select( skinJnts[i] )
            Sjnt_Strt = place.null2( prefix + '_Sjnt_StrtIntrNll', skinJnts[i] )[0]
            Ejnt_Strt = place.null2( prefix + '_Ejnt_StrtIntrNll', skinJnts[i] )[0]
            jnt_Strt = place.null2( prefix + '_jnt_StrtIntrNll', skinJnts[i] )[0]
            Sctl_Strt = place.null2( prefix + '_Sctl_StrtIntrNll', skinJnts[i] )[0]
            # #
            # option attrs
            place.addAttribute( ctrl, OptAttrs[0], 0, 1, True, 'float' )
            # offset vis attr
            place.addAttribute( ctrl, vis, 0, 1, 0, 'long' )
            cmds.setAttr( ctrl + '.' + vis, 0 )
            cmds.connectAttr( ( ctrl + '.' + vis ), ( ctrlOfst + '.visibility' ), f = True )
            # #
            xScnrl.append( ctrl )
            xScnrl.append( ctrlOfst )
            cmds.select( skinJnts[i] )
            clstr = place.null2( prefix + '_S_IK_ClstrGrp', skinJnts[i] )
            jnt = place.null2( prefix + '_S_IK_Jnt', skinJnts[i] )
            xjnt.append( jnt[0] )
            # create hierarchy
            cmds.parent( jnt, ctrlOfst )
            cmds.parent( clstr, ctrlOfst )
            cmds.parent( jnt_Strt, ctrlOfst )
            cmds.parent( Sjnt_Strt, ctrlOfst )
            cmds.parent( Ejnt_Strt, ctrlOfst )
            cmds.parent( Sctl_Strt, ctrlOfst )
            cmds.parent( ctrlOfst, ctrl )
            cmds.parent( ctrl, prnt )
            cmds.parent( prnt, grp )
            # rotate Orders
            cmds.setAttr( ( ctrl + '.rotateOrder' ), rotOrder )
            cmds.setAttr( ( ctrlOfst + '.rotateOrder' ), rotOrder )
            # constrain elements
            # joint
            cmds.pointConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            cmds.orientConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            # cluster group
            cmds.pointConstraint( clstr, BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][i], mo = True, w = 1 )[0]
            cmds.orientConstraint( clstr, BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][i], mo = True, w = 1 )
            # startIK to spline joints
            cnstrnt = cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i], jnt, mo = True, w = 0.5 )[0]
            xcnstrnt.append( cnstrnt )
            cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ) - i ) - 1], jnt, mo = True, w = 0.5 )
            # connect blend to constraint weights
            #
            attrs = cmds.listAttr( cnstrnt, k = True )
            weightAttrs = attrs[-2:]
            cmds.connectAttr( ( SRblnd + '.outputR' ), ( cnstrnt + '.' + weightAttrs[0] ), f = True )
            cmds.connectAttr( ( SRblnd + '.outputG' ), ( cnstrnt + '.' + weightAttrs[1] ), f = True )
            # Connect Start Offset Control to spline
            cmds.connectAttr( ( ctrlOfst + '.worldMatrix[0]' ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[6] + '.dWorldUpMatrix' ), f = True )
            cmds.connectAttr( ( ctrlOfst + '.worldMatrix[0]' ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[7] + '.dWorldUpMatrixEnd' ), f = True )

            # connect OrientationAttr/Rig
            for i in range( 0, len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1] ), 1 ):
                joint.ZeroJointOrient( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i] )
                joint.ZeroJointOrient( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][i] )
            cmds.orientConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][0], Sjnt_Strt, mo = True, w = 1 )
            cmds.orientConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ) - 1], Ejnt_Strt, mo = True, w = 1 )
            J_orient = cmds.orientConstraint( Sjnt_Strt, jnt_Strt, mo = False, w = 1 )[0]
            cmds.orientConstraint( Ejnt_Strt, jnt_Strt, mo = False, w = 1 )
            J_orient_attrs = cmds.listAttr( J_orient, k = True )
            J_orient_weightAttrs = J_orient_attrs[-2:]
            cmds.connectAttr( SRblnd + '.outputR', J_orient + '.' + J_orient_weightAttrs[0] )
            cmds.connectAttr( SRblnd + '.outputG', J_orient + '.' + J_orient_weightAttrs[1] )
            Orient_cnstrnt = cmds.orientConstraint( jnt_Strt, jnt, mo = False, w = 1 )[0]
            cmds.orientConstraint( Sctl_Strt, jnt, mo = False, w = 1 )
            Orient_cnstrnt_attrs = cmds.listAttr( Orient_cnstrnt, k = True )
            Orient_cnstrnt_weightAttrs = Orient_cnstrnt_attrs[-2:]
            S_OrientRvrs = cmds.shadingNode( 'reverse', name = ( prefix + '_StartOrientation' ), asUtility = True )
            cmds.connectAttr( ctrl + '.' + OptAttrs[0], S_OrientRvrs + '.inputX' )
            cmds.connectAttr( ctrl + '.' + OptAttrs[0], Orient_cnstrnt + '.' + Orient_cnstrnt_weightAttrs[1] )
            cmds.connectAttr( S_OrientRvrs + '.outputX', Orient_cnstrnt + '.' + Orient_cnstrnt_weightAttrs[0] )
        elif i == 1:
            # second, no aim groups
            # create nulls
            cmds.select( skinJnts[i] )
            # point constrained to start/end ik joints
            # aim constrained at 'M_IK_AimCnst' under next controller position in next stage
            prnt = place.null( prefix + '_M' + str( jj ) + '_IK_PrntGrp' )
            place.setChannels( prnt[0], [False, True], [False, True], [True, False], [True, False, False] )
            xprnt.append( prnt[0] )
            ctrl = place.circle( prefix + '_M' + str( jj ) + '_IK_Cntrl', skinJnts[i], 'tacZ_Ctrl', X * ( 3 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            ctrlOfst = place.circle( prefix + '_M' + str( jj ) + '_IK_Cntrl_Offst', skinJnts[i], 'tacZ_Ctrl', X * ( 2.7 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            place.setChannels( ctrl, [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( ctrlOfst, [False, True], [False, True], [True, False], [True, False, False] )
            # offset vis attr
            place.addAttribute( ctrl, vis, 0, 1, 0, 'long' )
            cmds.setAttr( ctrl + '.' + vis, 0 )
            cmds.connectAttr( ( ctrl + '.' + vis ), ( ctrlOfst + '.visibility' ), f = True )
            # #
            clstr = place.null( prefix + '_M' + str( jj ) + '_IK_ClstrGrp' )
            jnt = place.null( prefix + '_M' + str( jj ) + '_IK_Jnt' )
            xjnt.append( jnt[0] )
            # worldUpObjects' parent gets pointConstrained to this position in next stage
            vtr = place.null( prefix + '_M' + str( jj ) + '_IK_UpVtr' )
            xvtr.append( vtr[0] )
            # create hierarchy
            cmds.parent( jnt, ctrlOfst )
            cmds.parent( clstr, ctrlOfst )
            cmds.parent( vtr, ctrlOfst )
            cmds.parent( ctrlOfst, ctrl )
            cmds.parent( ctrl, prnt )
            cmds.parent( prnt, grp )
            # constrain elements
            # joint
            cmds.pointConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            cmds.orientConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            # midIK to spline joints
            cnstrnt = cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i], prnt, mo = True, w = 0.5 )[0]
            xcnstrnt.append( cnstrnt )
            cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ) - i ) - 1], prnt, mo = True, w = 0.5 )
            # connect blend to constraint weights
            #
            attrs = cmds.listAttr( cnstrnt, k = True )
            weightAttrs = attrs[-2:]
            cmds.connectAttr( ( MidB + '.outputR' ), ( cnstrnt + '.' + weightAttrs[0] ), f = True )
            cmds.connectAttr( ( MidB + '.outputG' ), ( cnstrnt + '.' + weightAttrs[1] ), f = True )
            #
            # increment 'M...' name
            jj = jj + 1
        elif i == ( len( skinJnts ) - 1 ):
            # end, no vector groups
            # create nulls
            cmds.select( skinJnts[i] )
            prnt = place.null( prefix + '_E_IK_PrntGrp' )
            SEprnt[1] = prnt[0]
            place.setChannels( prnt[0], [False, True], [False, True], [True, False], [True, False, False] )
            ctrl = place.circle( prefix + '_E_IK_Cntrl', skinJnts[i], 'splineEnd_ctrl', X * ( 2.5 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            ctrlOfst = place.circle( prefix + '_E_IK_Cntrl_Offst', skinJnts[i], 'splineEnd_ctrl', X * ( 2.2 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            place.setChannels( ctrl, [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( ctrlOfst, [False, True], [False, True], [True, False], [True, False, False] )
            # intermediate nulls for orientation option
            Ejnt_End = place.null( prefix + '_Ejnt_EndIntrNll' )[0]
            Sjnt_End = place.null( prefix + '_Sjnt_EndIntrNll' )[0]
            jnt_End = place.null( prefix + '_jnt_EndIntrNll' )[0]
            Ectl_Strt = place.null( prefix + '_Ectl_EndIntrNll' )[0]
            # #
            # orient attr
            place.addAttribute( ctrl, OptAttrs[0], 0, 1, True, 'float' )
            # offset vis attr
            place.addAttribute( ctrl, vis, 0, 1, 0, 'long' )
            cmds.setAttr( ctrl + '.' + vis, 0 )
            cmds.connectAttr( ( ctrl + '.' + vis ), ( ctrlOfst + '.visibility' ), f = True )
            # #
            xEcnrl.append( ctrl )
            xEcnrl.append( ctrlOfst )
            clstr = place.null( prefix + '_E_IK_ClstrGrp' )
            jnt = place.null( prefix + '_E_IK_Jnt' )
            xjnt.append( jnt[0] )
            aim = place.null( prefix + '_E_IK_AimCnst' )
            xaim.append( aim[0] )
            # create hierarchy
            cmds.parent( aim, jnt )
            cmds.parent( jnt, ctrlOfst )
            cmds.parent( clstr, ctrlOfst )
            cmds.parent( jnt_End, ctrlOfst )
            cmds.parent( Sjnt_End, ctrlOfst )
            cmds.parent( Ejnt_End, ctrlOfst )
            cmds.parent( Ectl_Strt, ctrlOfst )
            cmds.parent( ctrlOfst, ctrl )
            cmds.parent( ctrl, prnt )
            cmds.parent( prnt, grp )
            # rotate Orders
            cmds.setAttr( ( ctrl + '.rotateOrder' ), rotOrder )
            cmds.setAttr( ( ctrlOfst + '.rotateOrder' ), rotOrder )
            # constrain joint to jnt group
            # joint
            cmds.pointConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            cmds.orientConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            # cluster groups
            cmds.pointConstraint( clstr, BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][len( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0] ) - 1], mo = True, w = 1 )
            cmds.orientConstraint( clstr, BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][len( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0] ) - 1], mo = True, w = 1 )
            # endIK to spline joints
            cnstrnt = cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i], jnt, mo = True, w = 0.5 )[0]
            xcnstrnt.append( cnstrnt )
            cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ) - i ) - 1], jnt, mo = True, w = 0.5 )
            # connect blend to constraint weights
            #
            attrs = cmds.listAttr( cnstrnt, k = True )
            weightAttrs = attrs[-2:]
            cmds.connectAttr( ( ERblnd + '.outputR' ), ( cnstrnt + '.' + weightAttrs[0] ), f = True )
            cmds.connectAttr( ( ERblnd + '.outputG' ), ( cnstrnt + '.' + weightAttrs[1] ), f = True )
            # Connect End Offset Control to spline
            cmds.connectAttr( ( ctrlOfst + '.worldMatrix[0]' ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[7] + '.dWorldUpMatrix' ), f = True )
            cmds.connectAttr( ( ctrlOfst + '.worldMatrix[0]' ), ( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[6] + '.dWorldUpMatrixEnd' ), f = True )

            # connect OrientationAttr/Rig
            for i in range( 0, len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ), 1 ):
                joint.ZeroJointOrient( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][i] )
                joint.ZeroJointOrient( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i] )
            cmds.orientConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][0], Ejnt_End, mo = True, w = 1 )
            cmds.orientConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1] ) - 1], Sjnt_End, mo = True, w = 1 )
            J_orient = cmds.orientConstraint( Sjnt_End, jnt_End, mo = True, w = 1 )[0]
            cmds.orientConstraint( Ejnt_End, jnt_End, mo = True, w = 1 )
            J_orient_attrs = cmds.listAttr( J_orient, k = True )
            J_orient_weightAttrs = J_orient_attrs[-2:]
            cmds.connectAttr( ERblnd + '.outputR', J_orient + '.' + J_orient_weightAttrs[0] )
            cmds.connectAttr( ERblnd + '.outputG', J_orient + '.' + J_orient_weightAttrs[1] )
            Orient_cnstrnt = cmds.orientConstraint( jnt_End, jnt, mo = True, w = 1 )[0]
            cmds.orientConstraint( Ectl_Strt, jnt, mo = True, w = 0 )
            Orient_cnstrnt_attrs = cmds.listAttr( Orient_cnstrnt, k = True )
            Orient_cnstrnt_weightAttrs = Orient_cnstrnt_attrs[-2:]
            E_OrientRvrs = cmds.shadingNode( 'reverse', name = ( prefix + '_EndOrientation' ), asUtility = True )
            cmds.connectAttr( ctrl + '.' + OptAttrs[0], E_OrientRvrs + '.inputX' )
            cmds.connectAttr( ctrl + '.' + OptAttrs[0], Orient_cnstrnt + '.' + Orient_cnstrnt_weightAttrs[1] )
            cmds.connectAttr( E_OrientRvrs + '.outputX', Orient_cnstrnt + '.' + Orient_cnstrnt_weightAttrs[0] )
            #
        else:
            # middle
            # create nulls
            cmds.select( skinJnts[i] )
            # point constrained to start/end ik joints, aim constrained at 'M_IK_AimCnst' under next controller position
            prnt = place.null( prefix + '_M' + str( jj ) + '_IK_PrntGrp' )
            place.setChannels( prnt[0], [False, True], [False, True], [True, False], [True, False, False] )
            xprnt.append( prnt[0] )
            ctrl = place.circle( prefix + '_M' + str( jj ) + '_IK_Cntrl', skinJnts[i], 'tacZ_Ctrl', X * ( 3 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            ctrlOfst = place.circle( prefix + '_M' + str( jj ) + '_IK_Cntrl_Offst', skinJnts[i], 'tacZ_Ctrl', X * ( 2.7 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
            place.setChannels( ctrl, [False, True], [False, True], [True, False], [True, False, False] )
            place.setChannels( ctrlOfst, [False, True], [False, True], [True, False], [True, False, False] )
            # offset vis attr
            place.addAttribute( ctrl, vis, 0, 1, 0, 'long' )
            cmds.setAttr( ctrl + '.' + vis, 0 )
            cmds.connectAttr( ( ctrl + '.' + vis ), ( ctrlOfst + '.visibility' ), f = True )
            # #
            clstr = place.null( prefix + '_M' + str( jj ) + '_IK_ClstrGrp' )
            jnt = place.null( prefix + '_M' + str( jj ) + '_IK_Jnt' )
            xjnt.append( jnt[0] )
            vtr = place.null( prefix + '_M' + str( jj ) + '_IK_UpVtr' )
            xvtr.append( vtr[0] )
            # prnt group is aimed att this group
            aim = place.null( prefix + '_M' + str( jj ) + '_IK_AimCnst' )
            xaim.append( aim[0] )
            # create hierarchy
            cmds.parent( aim, jnt )
            cmds.parent( jnt, ctrlOfst )
            cmds.parent( clstr, ctrlOfst )
            cmds.parent( vtr, ctrlOfst )
            cmds.parent( ctrlOfst, ctrl )
            cmds.parent( ctrl, prnt )
            cmds.parent( prnt, grp )
            # constrain joint to jnt group
            # joint
            cmds.pointConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            cmds.orientConstraint( jnt, skinJnts[i], mo = True, w = 1 )
            # midIK to spline joints
            cnstrnt = cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[1][i], prnt, mo = True, w = 0.5 )[0]
            xcnstrnt.append( cnstrnt )
            cmds.pointConstraint( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2][( len( BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp[2] ) - i ) - 1], prnt, mo = True, w = 0.5 )
            #
            # connect blend to constraint weights
            attrs = cmds.listAttr( cnstrnt, k = True )
            weightAttrs = attrs[-2:]
            cmds.connectAttr( ( MidB + '.outputR' ), ( cnstrnt + '.' + weightAttrs[0] ), f = True )
            cmds.connectAttr( ( MidB + '.outputG' ), ( cnstrnt + '.' + weightAttrs[1] ), f = True )
            #
            # increment 'M...' name
            jj = jj + 1
        i = i + 1
    # print 'ikg end'
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xprnt )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xvtr )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xaim )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xScnrl )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xEcnrl )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xik )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xjnt )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( xcnstrnt )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( SRblnd )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( ERblnd )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( MidB )
    BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt.append( SEprnt )
    return BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt

###############################################################################
# ############################## STAGE 4 ######################################


def upVectorGroup( prefix, X, Y, F, skinJnts, aim, up, aimFloat, upFloat, rotOrder, Constrain,
                  BUS_clusterGrps_Sjnt_Ejnt_Sblnd_Eblnd_Crv_Sik_Eik_SplnCtrlGrp_ClstrGrp,
                  BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt,
                  BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP, colorScheme = 'yellow' ):

    colors = getColors( colorScheme )
    # lists
    xprntPos = []
    xprntRot = []
    xctrl = []
    xtan = []
    BUS_prntPos_ctrl_tan = []
    suffix = '_Vctr'
    # Vector parent groups
    # parent constrain to ik_ctrlGrp
    cmds.select( skinJnts[0] )
    DELETE_VctrGrp = place.null( prefix + '_DELETEME_VctrGrp' )[0]
    # constrain main to ikGrp
    cmds.select( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[0][0] )
    # pass group from stage 3 instead of pick walking...
    ikGrp = cmds.pickWalk( d = 'up' )[0]
    SplnCntrlGrp = cmds.pickWalk( d = 'up' )[0]

    # calculate y position of up vector by measuring distance from first to second joint
    p1 = cmds.xform( skinJnts[0], q = True, ws = True, t = True )
    p2 = cmds.xform( skinJnts[1], q = True, ws = True, t = True )
    locTY = place.distance2Pts( p1, p2 )
    # Start UP Vector controls
    BUS_VctrCntrls_BUS = [[], [None], [None], [None], [None], [None], [None], [None], [None]]
    BUS_VctrCntrls_BUS[8] = SplnCntrlGrp
    sTan = place.circle( prefix + suffix + '_S_Ctrl', skinJnts[0], 'vctrArrow_ctrl', X * ( 0.3 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
    sTmp = place.circle( prefix + '_S_DELETEME', skinJnts[0], 'vctrArrow_ctrl', X * ( 0.6 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
    # create hierarchy
    cmds.parent( sTan, sTmp )
    cmds.setAttr( sTan + '.translate' + up.upper(), Y * ( locTY ) )
    cmds.parent( sTan, DELETE_VctrGrp )
    cmds.delete( sTmp )
    BUS_VctrCntrls_BUS[0].append( sTan )

    # Mid UP Vector controls
    jj = 1
    i = 0
    for item in BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[1]:
        # up vector control
        if item == BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[1][int( ( len( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[1] ) - 1 ) / 2 )]:
            mTan = place.circle( prefix + suffix + '_M' + str( jj ) + '_Ctrl', item, 'diamond_ctrl', X * ( 0.3 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
        else:
            mTan = place.circle( prefix + suffix + '_M' + str( jj ) + '_Ctrl', item, 'diamond_ctrl', X * ( 0.15 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
        mTmp = place.circle( prefix + suffix + '_M' + str( jj ) + '_DELETEME', item, 'diamond_ctrl', X * ( 0.6 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
        # create hierarchy
        cmds.parent( mTan, mTmp )
        cmds.setAttr( mTan + '.translate' + up.upper(), Y * ( locTY ) )
        cmds.parent( mTan, DELETE_VctrGrp )
        cmds.delete( mTmp )
        BUS_VctrCntrls_BUS[0].append( mTan )
        # constrain aim up vector group to aim group of next controller
        cmds.aimConstraint( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[2][i], BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[0][i], mo = True, aimVector = aimFloat, upVector = upFloat, worldUpType = 'object', worldUpObject = mTan )  # , worldUpType='object', worldUpObject=ctrl
        # increment 'M...' name
        jj = jj + 1
        i = i + 1

    # End UP Vector controls
    eTan = place.circle( prefix + suffix + '_E_Ctrl', skinJnts[len( skinJnts ) - 1], 'vctrArrowInv_ctrl', X * ( 0.3 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]
    eTmp = place.circle( prefix + '_E_DELETEME', skinJnts[len( skinJnts ) - 1], 'vctrArrowInv_ctrl', X * ( 0.6 ), colors[0], 8, 1, ( 0, 0, 1 ) )[0]

    # create hierarchy
    cmds.parent( eTan, eTmp )
    cmds.setAttr( eTan + '.translate' + up.upper(), Y * ( locTY ) )
    cmds.parent( eTan, DELETE_VctrGrp )
    cmds.delete( eTmp )
    BUS_VctrCntrls_BUS[0].append( eTan )

    # Up Vector Weight Groups
    suffix = '_Vctr'
    BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP = clusterControlGroup( prefix, suffix, X, aim, 0, skinJnts, rotOrder, 0, F, BUS_VctrCntrls_BUS )
    MidCnstrnt = ['VctrMidTwstCstrnt', 'VctrMidTwstCstrntSE_W']
    VectorMaster = BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[1]
    place.addAttribute( VectorMaster, MidCnstrnt, 0, 1, True, 'float' )
    cmds.setAttr( VectorMaster + '.' + MidCnstrnt[0], 1 )
    cmds.setAttr( VectorMaster + '.' + MidCnstrnt[1], 0.5 )

    # constrain Start Up Vector
    cmds.parentConstraint( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][0], BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][0], mo = True, w = 1.0 )
    # constrain Mid Up Vector
    # insert compensation groups for mid up vector constraint
    cmds.select( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[4][0] )
    stringNum = len( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[4][0] )
    name = BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[4][0]
    # X1 places X2. X1 constrains X2 to itself
    X1 = place.insert( 'null', 0, name[:stringNum - 8] + '_X' + name[-8:] )[0][0]
    cmds.select( X1 )
    # X2 gets constrained to X1 and mid luster group
    X2 = place.insert( 'null', 0, name[:stringNum - 8] + '_XX' + name[-8:] )[0][0]
    cmds.select( X2 )
    # X3 puts Up vector controller back to correct position
    X3 = place.insert( 'null', 0, name[:stringNum - 8] + '_XXX' + name[-8:] )[0][0]
    # place X1 X3 groups
    cmds.setAttr( X2 + '.rotateOrder', rotOrder )
    cmds.setAttr( X1 + '.translate' + up.upper(), Y * ( locTY ) * -1 )
    cmds.setAttr( X3 + '.translate' + up.upper(), Y * ( locTY ) )
    # add constraints
    pointMidCnstrnt = cmds.pointConstraint( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][1], X2, mo = True, w = 1.0 )[0]
    cmds.pointConstraint( X1, X2, mo = True, w = 0.0 )
    # mid upVector network for constraint switch/weight to mid cluster
    # switch network for pointConstraint
    MidVctr_PntRvrs = cmds.shadingNode( 'reverse', name = ( prefix + suffix + '_' + MidCnstrnt[0] ), asUtility = True )
    attrs = cmds.listAttr( pointMidCnstrnt, k = True )
    weightAttrs = attrs[-2:]
    cmds.connectAttr( VectorMaster + '.' + MidCnstrnt[0], pointMidCnstrnt + '.' + weightAttrs[0] )
    cmds.connectAttr( VectorMaster + '.' + MidCnstrnt[0], MidVctr_PntRvrs + '.inputX' )
    cmds.connectAttr( MidVctr_PntRvrs + '.outputX', pointMidCnstrnt + '.' + weightAttrs[1] )
    # switch network for twist blend and weight
    blends = spln.twistBlend( prefix + suffix, BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[3], BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[4], X2, 'rotate' + str( aim.upper() ) )
    cmds.connectAttr( VectorMaster + '.' + MidCnstrnt[0], blends[0] + '.blender' )
    cmds.connectAttr( VectorMaster + '.' + MidCnstrnt[1], blends[1] + '.blender' )
    # #

    # constrain End Up Vector
    cmds.parentConstraint( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][2], BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][int( len( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[0] ) - 1 )], mo = True, w = 1.0 )

    # constrain Vector Master group to Ik Master group, setChannels
    if Constrain[0] == True:
        cmds.parentConstraint( Constrain[1], ikGrp, mo = True, w = 1.0 )
        if Constrain[2] != None:
            cmds.parentConstraint( Constrain[2], BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[11][0], mo = True, w = 1.0 )
            if Constrain[3] != None:
                cmds.parentConstraint( Constrain[3], BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[11][1], mo = True, w = 1.0 )

    # constrain Vector Master group to Ik Master group, setChannels
    cmds.parentConstraint( ikGrp, BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], mo = True, w = 1.0 )
    place.setChannels( ikGrp, [False, False], [False, False], [False, False], [False, False, False] )
    cmds.setAttr( ikGrp + '.visibility', cb = False )
    place.setChannels( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], [False, False], [False, False], [False, False], [False, False, False] )
    place.setChannels( X1, [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( X2, [False, False], [False, False], [True, False], [True, False, False] )
    place.setChannels( X3, [False, False], [False, False], [True, False], [True, False, False] )
    cmds.setAttr( X2 + '.rotateX', cb = True )
    cmds.setAttr( X2 + '.rotateY', cb = True )
    cmds.setAttr( X2 + '.rotateZ', cb = True )
    # finished with temp group...delete
    cmds.delete( DELETE_VctrGrp )

    # connect weight options to cluster group weight options
    place.hijackCustomAttrs( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[1], ikGrp )

    # connect Tangent scale for UpVectors and SplineClusters
    # Vars
    ClstrStartCtrl = BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][0]
    ClstrEndCtrl = BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][len( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[3] ) - 1]
    VctrStartCtrl = BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][0]
    VctrEndCtrl = BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[3][len( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[3] ) - 1]
    attrs = cmds.listAttr( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[3][0], k = True )
    tangntAttrs = attrs[-2:]
    # cluster controls
    '''
	cmds.connectAttr(BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[3][0] + '.' + tangntAttrs[0], ClstrStartCtrl + '.scale' + aim.upper())
	cmds.connectAttr(BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[4][0] + '.' + tangntAttrs[0], ClstrEndCtrl + '.scale' + aim.upper())
	'''
    # vector controls
    '''
	cmds.connectAttr(BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[3][0] + '.' + tangntAttrs[1], VctrStartCtrl + '.scale' + aim.upper())
	cmds.connectAttr(BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[4][0] + '.' + tangntAttrs[1], VctrEndCtrl + '.scale' + aim.upper())
	'''

    # set channels for clusterControlGroups and vectorControlGroups
    # clusterControlGroups
    for i in range( 1, len( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0] ) - 1, 1 ):
        place.setChannels( BUS_clusterCntrlGrps_ClstrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][i], [False, False], [True, False], [True, False], [True, False, False] )
    # vectorControlGroups
    for i in range( 1, len( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[0] ) - 1, 1 ):
        place.setChannels( BUS_VectorCntrlGrps_VctrCtrlGrp_AttrList_ClusterCntrls_XtraP[0][i], [False, False], [True, False], [True, False], [True, False, False] )

    # Up vector guides
    # create guide groups
    guideGp = 'GuideGp'
    cmds.select( skinJnts[0] )
    guideGrp = cmds.group( em = True, name = prefix + '_Vctr_Cnnct_GuideGrp' )
    guideClstr = cmds.group( em = True, name = prefix + '_GuideClstrGrp' )
    guideCrv = cmds.group( em = True, name = prefix + '_GuideCrvGrp' )
    cmds.parent( guideClstr, guideCrv, guideGrp )
    cmds.parent( guideGrp, guideGp )
    cmds.connectAttr( VectorMaster + '.visibility', guideCrv + '.visibility' )
    place.setChannels( guideGrp, [True, False], [True, False], [True, False], [True, False, False] )
    place.setChannels( guideClstr, [True, False], [True, False], [True, False], [True, False, False] )
    place.setChannels( guideCrv, [True, False], [True, False], [True, False], [False, False, False] )
    # create guides
    for i in range( 0, len( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[0] ), 1 ):
        CrvCls = place.guideLine( BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[0][i], BUS_VctrCntrls_BUS[0][i + 1], prefix + '_Guide' )
        cmds.parent( CrvCls[0], guideCrv )
        cmds.parent( CrvCls[1], guideClstr )
        place.setChannels( CrvCls[0], [False, False], [False, False], [False, False], [True, False, False] )
        place.setChannels( CrvCls[1][0], [False, False], [False, False], [False, False], [False, False, False] )
        place.setChannels( CrvCls[1][1], [False, False], [False, False], [False, False], [False, False, False] )

    # add attrs to spline parent
    if Constrain[0]:
        Spline = 'Spline'
        cmds.addAttr( Constrain[1], ln = Spline, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( Constrain[1] + '.' + Spline, cb = True )
        place.hijackCustomAttrs( ikGrp, Constrain[1] )

    # Done
    BUS_prntPos_ctrl_tan.append( xtan )
    return ikGrp, BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[11][0], BUS_prnt_vtr_aim_Scnr_Ecnrl_ik_xjnt_cnstrnt_SRblnd_ERblnd_MidB_SEprnt[11][1]
