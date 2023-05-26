from maya import cmds


def aimConstraint( target = '', obj = '', aim = [0, 0, 0], up = [0, 0, 0], offset = True ):
    '''
    matrix based aim constraint
    should replace standard constraint with same options and features
    '''
    aimTar = cmds.spaceLocator( name = 'AimTarget' )[0]
    upTar = cmds.spaceLocator( name = 'UpTarget' )[0]
    pos = cmds.spaceLocator( name = 'Position' )[0]
    output = cmds.spaceLocator( name = 'AimedNode' )[0]
    aimMat = cmds.createNode( 'aimMatrix' )

    cmds.setAttr( aimMat + '.secondaryMode', 1 )
    cmds.connectAttr( pos + '.worldMatrix[0]', aimMat + '.inputMatrix' )
    cmds.connectAttr( aimTar + '.worldMatrix[0]', aimMat + '.primaryTargetMatrix' )
    cmds.connectAttr( upTar + '.worldMatrix[0]', aimMat + '.secondaryTargetMatrix' )
    cmds.connectAttr( aimMat + '.outputMatrix', output + '.offsetParentMatrix' )
