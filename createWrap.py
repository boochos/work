import maya.cmds as cmds
import pymel.core as pm


def createWrap( *args, **kwargs ):
    '''
    
    '''
    print( args )
    # driver
    influence = args[0]
    # driven
    surface = args[1]

    shapes = cmds.listRelatives( influence, shapes = True, f = True )
    influenceShape = shapes[0]

    shapes = cmds.listRelatives( surface, shapes = True, f = True )
    surfaceShape = shapes[0]

    weightThreshold = kwargs.get( 'weightThreshold', 0.0 )
    maxDistance = kwargs.get( 'maxDistance', 1.0 )
    exclusiveBind = kwargs.get( 'exclusiveBind', False )
    autoWeightThreshold = kwargs.get( 'autoWeightThreshold', True )
    falloffMode = kwargs.get( 'falloffMode', 0 )

    wrapData = cmds.deformer( surface, type = 'wrap' )
    wrapNode = wrapData[0]

    cmds.setAttr( wrapNode + '.weightThreshold', weightThreshold )
    cmds.setAttr( wrapNode + '.maxDistance', maxDistance )
    cmds.setAttr( wrapNode + '.exclusiveBind', exclusiveBind )
    cmds.setAttr( wrapNode + '.autoWeightThreshold', autoWeightThreshold )
    cmds.setAttr( wrapNode + '.falloffMode', falloffMode )

    cmds.connectAttr( surface + '.worldMatrix[0]', wrapNode + '.geomMatrix' )

    duplicateData = cmds.duplicate( influence, name = influence + 'Base' )
    base = duplicateData[0]
    shapes = cmds.listRelatives( base, shapes = True )
    baseShape = shapes[0]
    cmds.hide( base )

    if not cmds.attributeQuery( 'dropoff', n = influence, exists = True ):
        cmds.addAttr( influence, sn = 'dr', ln = 'dropoff', dv = 4.0, min = 0.0, max = 20.0 )
        cmds.setAttr( influence + '.dr', k = True )

    if cmds.nodeType( influenceShape ) == 'mesh':
        if not cmds.attributeQuery( 'smoothness', n = influence, exists = True ):
            cmds.addAttr( influence, sn = 'smt', ln = 'smoothness', dv = 0.0, min = 0.0 )
            cmds.setAttr( influence + '.smt', k = True )

        if not cmds.attributeQuery( 'inflType', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'ift', ln = 'inflType', dv = 2, min = 1, max = 2 )

        cmds.connectAttr( influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.worldMesh', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.inflType', wrapNode + '.inflType[0]' )
        cmds.connectAttr( influence + '.smoothness', wrapNode + '.smoothness[0]' )

    if cmds.nodeType( influenceShape ) == 'nurbsCurve' or cmds.nodeType( influenceShape ) == 'nurbsSurface':
        if not cmds.attributeQuery( 'wrapSamples', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'wsm', ln = 'wrapSamples', dv = 10, min = 1 )
            cmds.setAttr( influence + '.wsm', k = True )

        cmds.connectAttr( influenceShape + '.ws', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.ws', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.wsm', wrapNode + '.nurbsSamples[0]' )

    cmds.connectAttr( influence + '.dropoff', wrapNode + '.dropoff[0]' )
    return wrapNode


def wrapDeformer( master = '', slave = '' ):
    '''
    run createWrap()
    '''
    #
    node = createWrap( master, slave )
    return node


def createWrap2( *args, **kwargs ):

    influence = args[0]
    surface = args[1]

    shapes = cmds.listRelatives( influence, shapes = True, f = True )
    influenceShape = shapes[0]

    shapes = cmds.listRelatives( surface, shapes = True, f = True )
    surfaceShape = shapes[0]

    # create wrap deformer
    weightThreshold = kwargs.get( 'weightThreshold', 0.0 )
    maxDistance = kwargs.get( 'maxDistance', 1.0 )
    exclusiveBind = kwargs.get( 'exclusiveBind', False )
    autoWeightThreshold = kwargs.get( 'autoWeightThreshold', True )
    falloffMode = kwargs.get( 'falloffMode', 0 )

    wrapData = cmds.deformer( surface, type = 'wrap' )
    wrapNode = wrapData[0]

    cmds.setAttr( wrapNode + '.weightThreshold', weightThreshold )
    cmds.setAttr( wrapNode + '.maxDistance', maxDistance )
    cmds.setAttr( wrapNode + '.exclusiveBind', exclusiveBind )
    cmds.setAttr( wrapNode + '.autoWeightThreshold', autoWeightThreshold )
    cmds.setAttr( wrapNode + '.falloffMode', falloffMode )

    cmds.connectAttr( surface + '.worldMatrix[0]', wrapNode + '.geomMatrix' )

    # add influence
    duplicateData = cmds.duplicate( influence, name = influence + 'Base' )
    base = duplicateData[0]
    shapes = cmds.listRelatives( base, shapes = True )
    baseShape = shapes[0]
    cmds.hide( base )

    # create dropoff attr if it doesn't exist
    if not cmds.attributeQuery( 'dropoff', n = influence, exists = True ):
        cmds.addAttr( influence, sn = 'dr', ln = 'dropoff', dv = 4.0, min = 0.0, max = 20.0 )
        cmds.setAttr( influence + '.dr', k = True )

    # if type mesh
    if cmds.nodeType( influenceShape ) == 'mesh':
        # create smoothness attr if it doesn't exist
        if not cmds.attributeQuery( 'smoothness', n = influence, exists = True ):
            cmds.addAttr( influence, sn = 'smt', ln = 'smoothness', dv = 0.0, min = 0.0 )
            cmds.setAttr( influence + '.smt', k = True )

        # create the inflType attr if it doesn't exist
        if not cmds.attributeQuery( 'inflType', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'ift', ln = 'inflType', dv = 2, min = 1, max = 2 )

        cmds.connectAttr( influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.worldMesh', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.inflType', wrapNode + '.inflType[0]' )
        cmds.connectAttr( influence + '.smoothness', wrapNode + '.smoothness[0]' )

    # if type nurbsCurve or nurbsSurface
    if cmds.nodeType( influenceShape ) == 'nurbsCurve' or cmds.nodeType( influenceShape ) == 'nurbsSurface':
        # create the wrapSamples attr if it doesn't exist
        if not cmds.attributeQuery( 'wrapSamples', n = influence, exists = True ):
            cmds.addAttr( influence, at = 'short', sn = 'wsm', ln = 'wrapSamples', dv = 10, min = 1 )
            cmds.setAttr( influence + '.wsm', k = True )

        cmds.connectAttr( influenceShape + '.ws', wrapNode + '.driverPoints[0]' )
        cmds.connectAttr( baseShape + '.ws', wrapNode + '.basePoints[0]' )
        cmds.connectAttr( influence + '.wsm', wrapNode + '.nurbsSamples[0]' )

    cmds.connectAttr( influence + '.dropoff', wrapNode + '.dropoff[0]' )
    # I want to return a pyNode object for the wrap deformer.
    # I do not see the reason to rewrite the code here into pymel.
    # return wrapNode
    return pm.nt.Wrap( wrapNode )
