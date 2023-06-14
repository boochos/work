from pymel.core import *

import atom_miscellaneous_lib as misc
import atom_placement_lib as place
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


def WORLD_SPACE():
    return '___WORLD_SPACE'


def attachObj( obj = '', upObj = '', crv = '', position = 1.0 ):
    '''
    attach object to motion path
    '''
    if upObj:
        mp = cmds.pathAnimation( obj, name = obj + '_motionPath' , c = crv, startU = position, follow = True, wut = 'object', wuo = upObj, fm = True )
    else:
        mp = cmds.pathAnimation( obj, name = obj + '_motionPath' , c = crv, startU = position, follow = True, fm = True )
    # print( mp )
    anmCrv = cmds.listConnections( mp + '.uValue' )[0]
    cmds.delete( anmCrv )
    # print( mp, position )
    cmds.setAttr( mp + '.uValue', position )
    # delete anim curve included by default
    return mp


def makeCurve( start = 'joint1', end = 'joint2', name = 'crvTest', points = 4 ):
    '''
    make simple 4 point curve from start to end
    '''
    # build curve
    point_A = cmds.xform( start, query = True, ws = True, rp = True )
    point_B = cmds.xform( end, query = True, ws = True, rp = True )
    lengthSeg = 1.0 / points
    i = 1
    p = '[( ' + str( point_A[0] ) + ', ' + str( point_A[1] ) + ',' + str( point_A[2] ) + ')'
    while i <= points:
        seg = place.positionBetween2Pts( point_A, point_B, position = lengthSeg * i )
        p = p + ',( ' + str( seg[0] ) + ', ' + str( seg[1] ) + ',' + str( seg[2] ) + ')'
        i = i + 1
    p = p + ']'
    crv = cmds.curve( n = name, d = 3, p = eval( p ) )
    return crv


def makeDynamic( parentObj = 'joint1', attrObj = 'joint2', mstrCrv = '', mstrCrvReparent = True, addBlendShape = True ):
    '''
    for vehicles these need to be True:
    mstrCrvReparent (reparent group of master curve)
    addBlendShape (drives master curve with blendshape)
    '''
    #
    mstrCrvObj = ls( mstrCrv )[0]
    mstrCrvObj.visibility.set( False )
    strtCurve = duplicate( mstrCrv, name = mstrCrv + '_dynamicStartCurve' )[0]  # attraction curve, will receive a blendshape from the master curve

    select( strtCurve )
    Mel.eval( 'makeCurvesDynamicHairs 0 0 1;' )
    hairSys = None
    dynCurve = None
    nuc = 'nucleus1'
    # rename output curve
    output_curves_grp = 'hairSystem1OutputCurves'
    child = cmds.listRelatives( output_curves_grp, children = True )
    if child:
        # print( child )
        cmds.rename( child[0], mstrCrv + '_dynamicOutputCurve' )
    #
    follicle = strtCurve.getParent()
    cmds.rename( follicle.name(), mstrCrv + '_follicle' )

    for i in follicle.getShape().connections( d = True, s = False ):
        if i.getShape().type() == 'nurbsCurve':
            dynCurve = i
            # print( dynCurve )

        elif i.getShape().type() == 'hairSystem':
            hairSys = i
    if addBlendShape:
        blendNode = blendShape( dynCurve, mstrCrv, n = mstrCrv + '_dynamic_blendshape' )[0]
        cmds.setAttr( str( blendNode ) + '.' + str( dynCurve ), 1 )
        # print( blendNode )
    else:
        # temp, separate to function
        blendNode = blendShape( mstrCrv, strtCurve, n = mstrCrv + '_startDriver_blendshape' )[0]
        # always full weight
        #
        blendNode = blendShape( [mstrCrv, dynCurve], mstrCrv + '_result', n = mstrCrv + '_result_blendshape' )[0]
        # add swap switch, one blends on, the other blends off
        pass
    hairSys.getShape().iterations.set( 5 )
    hairSys.getShape().drag.set( 0 )
    # hairSys.getShape().startCurveAttract.set( 5 )
    # hairSys.getShape().attractionDamp.set( 1.5 )

    # Set the follicle system properties
    folshape = follicle.getShape()
    folshape.pointLock.set( 1 )

    # cmds.parentConstraint( parentObj, str( follicle.getParent() ), mo = True )

    # attrs
    misc.optEnum( attrObj, attr = 'Dynamic', enum = 'CONTROL' )
    # dynamic enable attr connection
    en_attr = 'enable'
    # nucleus
    place.hijackAttrs( nuc, attrObj, en_attr, en_attr, set = False, default = 0, force = True )
    cmds.setAttr( attrObj + '.' + en_attr, cb = True )
    # dynamic enable hairSystem
    cndtn = cmds.shadingNode( 'condition', au = True, n = attrObj + '_cndtn_dynmc' )
    cmds.setAttr( cndtn + '.colorIfFalseR', 3 )
    cmds.connectAttr( attrObj + '.' + en_attr, cndtn + '.firstTerm' )
    cmds.connectAttr( cndtn + '.outColorR', str( hairSys.getShape() ) + '.simulationMethod' )

    s_attr = 'startFrame'
    cmds.addAttr( attrObj, ln = s_attr, at = 'long', h = False )
    cmds.setAttr( attrObj + '.' + s_attr, cb = True )
    cmds.setAttr( attrObj + '.' + s_attr, k = False )
    cmds.setAttr( attrObj + '.' + s_attr, 1 )
    # misc.addAttribute( [attrObj], ['startFrame'], -1000.0, 10000.0, True, 'float' )
    cmds.connectAttr( attrObj + '.' + s_attr, nuc + '.' + s_attr, force = True )
    #
    misc.addAttribute( [attrObj], ['startCurveAttract', 'attractionDamp'], 0.0, 100.0, True, 'float' )
    cmds.connectAttr( attrObj + '.startCurveAttract', str( hairSys.getShape() ) + '.startCurveAttract', force = True )
    cmds.connectAttr( attrObj + '.attractionDamp', str( hairSys.getShape() ) + '.attractionDamp', force = True )
    cmds.setAttr( attrObj + '.startCurveAttract', 5 )
    cmds.setAttr( attrObj + '.attractionDamp', 1.75 )

    #
    sharedDynGrp = 'dynamicWorldGrp'
    if not cmds.objExists( sharedDynGrp ):
        sharedDynGrp = cmds.group( name = sharedDynGrp, em = True )
        cmds.setAttr( sharedDynGrp + '.visibility', 0 )
    #
    dynGrp = None
    if mstrCrvReparent:
        # cleanup to local group
        dynGrp = cmds.group( em = True, name = mstrCrv + '_dynamicGrp' )
        cmds.setAttr( dynGrp + '.visibility', 0 )
        cmds.parent( mstrCrv, dynGrp )
        cmds.parent( str( follicle.getParent() ), dynGrp )
        cmds.parent( dynGrp, sharedDynGrp )
    else:
        cmds.parent( follicle.name(), sharedDynGrp )
    # clean to shared group
    cmds.parent( str( hairSys ), sharedDynGrp )
    cmds.parent( output_curves_grp, sharedDynGrp )
    cmds.parent( nuc, sharedDynGrp )

    try:
        cmds.parent( sharedDynGrp, WORLD_SPACE() )
    except:
        pass

    return [str( follicle.getParent() ), dynGrp, sharedDynGrp ]


def createAndConnectBlendNodesToAttr( ctrl, attr, nodes ):
    ctrlObj = ls( ctrl )[0]
    # create the driving attribute
    misc.optEnum( ctrlObj.name(), attr = 'Stretch' )
    ctrlObj.addAttr( attr, at = 'double', max = 1, min = 0, dv = 0, k = True )
    for node in nodes:
        # make the string then execute to make it so
        connectAttr( ctrl + '.' + attr, node + '.blender' )
        # exeStr = 'ls("%s")[0].%s.connect(ls("%s")[0].blender)'%(ctrl,attr,node)
        # exec(exeStr)


def renameDynJntChain( obj, prefix, num, suffix = None ):
    name = '%s_dynJnt_jnt_%02d' % ( prefix, num )
    if suffix != None:
        name += '_' + suffix
    obj.rename( name )
    return name

'''
#
import imp
import webrImport as web
imp.reload(web)
# vehicle rig
dnm = web.mod('atom_dynamicSpline_lib')
crv = dnm.makeCurve()
dnm.attachObj( obj = 'loc', upObj = 'up', crv = crv, position = 0.9 )
dnm.makeDynamic( parentOne = 'joint1', parentTwo = 'joint2', mstrCrv = crv)
'''
