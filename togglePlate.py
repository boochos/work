import os

from pymel.core import *

import maya.cmds as cmds
import maya.mel as mel


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def camName():
    pnl = cmds.getPanel( withFocus = True )
    typ = cmds.getPanel( typeOf = pnl )
    if typ == 'modelPanel':
        cam = cmds.modelPanel( pnl, q = True, cam = True )
        if cam:
            typ = cmds.objectType( cam )
            if typ == 'camera':
                return cam
            else:
                if typ == 'transform':
                    trans = PyNode( cam )
                    # get the transform's shape, aka the camera node
                    cam = trans.getShape()
                    return str( cam )
        else:
            # print 'no model returned', cam
            pass
    else:
        # print 'not model panel', pnl
        pass


def togglePlate():
    # TODO: add proper UI for plate management
    cam = camName()
    #
    if cam:
        #
        connections = cmds.listConnections( cam, sh = True, t = 'imagePlane' )
        #
        if connections:
            connections = list( set( connections ) )
            plates = platesOnly( connections )
            #
            # check state of one plate
            st = plateState( plates[0] )
            for plate in plates:
                if st:
                    # off
                    plateOff( plate )
                else:
                    # on
                    plateOn( plate )
        else:
            message( 'No plates' )
    else:
        message( 'Not a camera' )


def platesAllOn():
    '''
    
    '''
    cam = camName()
    #
    if cam:
        #
        connections = cmds.listConnections( cam, sh = True, t = 'imagePlane' )
        #
        if connections:
            connections = list( set( connections ) )
            plates = platesOnly( connections )
            #
            for plate in plates:
                plateOn( plate )
        else:
            message( 'No plates' )
    else:
        message( 'Not a camera' )


def platesAllOff():
    '''
    
    '''
    cam = camName()
    #
    if cam:
        #
        connections = cmds.listConnections( cam, sh = True, t = 'imagePlane' )
        #
        if connections:
            connections = list( set( connections ) )
            plates = platesOnly( connections )
            #
            for plate in plates:
                plateOff( plate )
        else:
            message( 'No plates' )
    else:
        message( 'Not a camera' )


def plateRange( handles = 0 ):
    '''
    
    '''
    cam = camName()
    #
    if cam:
        #
        connections = cmds.listConnections( cam, sh = True, t = 'imagePlane' )
        #
        if connections:
            connections = list( set( connections ) )
            plates = platesOnly( connections )
            print( plates )
            #
            for plate in plates:
                path = cmds.getAttr( plate + '.imageName' )
                # print path
                if os.path.isfile( path ):
                    # print 'file'
                    fl = path.split( '/' )[-1]
                    path = path[:-len( fl ) - 1]
                    # print path
                    fls = os.listdir( path )
                    # print fls.sort()
                    frst = fls[0]
                    lst = fls[-1]
                    frst = int( frst.rsplit( '.', 2 )[1] )
                    lst = int( lst.rsplit( '.', 2 )[1] )
                    cmds.playbackOptions( animationStartTime = frst )
                    cmds.playbackOptions( minTime = frst + handles )
                    cmds.playbackOptions( animationEndTime = lst )
                    cmds.playbackOptions( maxTime = lst - handles )
        else:
            message( 'No plates' )
    else:
        message( 'Not a camera' )


def plateState( plate, toggle = False ):
    '''
    node = list( set( cmds.listConnections( ( plate + '.message' ), p = True ) ) )
    # print node
    for connection in node:
        # print '\n', connection, '\n'
        if 'imagePlane[' in connection:
            if toggle:
                plateOff( plate, connection )
            else:
                return True
        elif 'plateOff' in connection:
            if toggle:
                plateOn( plate, connection )
            else:
                return False
    '''
    n = cmds.getAttr( plate + '.displayMode' )
    if n == 0:
        if toggle:
            # cmds.setAttr( plate + '.displayMode', 3 )
            plateOn( plate )
        else:
            return False
    else:
        if toggle:
            # cmds.setAttr( plate + '.displayMode', 0 )
            plateOff( plate )
        else:
            return True


def platesOnly( connections ):
    plates = []
    for item in connections:
        if cmds.nodeType( item ) == 'imagePlane':
            plates.append( item )
    return plates


def plateOff( plate = '' ):
    '''
    # check for 'imagePlane' string in node
    connectionNode = connection.rpartition( '.' )[0]
    connectionAttr = connection.rpartition( '.' )[2]
    connectionAttr = connectionAttr.replace( '[', 'XXX' ).replace( ']', 'ZZZ' )
    attr = 'plateOff_' + connectionAttr
    cmds.addAttr( connectionNode, ln = attr, at = 'message' )
    cmds.connectAttr( ( plate + '.message' ), ( connectionNode + '.' + attr ), f = True )
    cmds.disconnectAttr( ( plate + '.message' ), connection )
    '''
    cmds.setAttr( plate + '.displayMode', 0 )
    message( 'plates OFF' )


def plateOn( plate = '' ):
    '''
    # check for 'plateOff' string in node
    connectionNode = connection.rpartition( '.' )[0]
    connectionAttr = connection.rpartition( '.' )[2]
    cmds.deleteAttr( connectionNode, at = connectionAttr )
    reConnectAttr = connectionAttr.replace( 'XXX', '[' ).replace( 'ZZZ', ']' )
    reConnectAttr = reConnectAttr.rpartition( '_' )[2]
    cmds.connectAttr( plate + '.message', connectionNode + '.' + reConnectAttr, f = True )
    '''
    cmds.setAttr( plate + '.displayMode', 3 )
    message( 'plates ON' )

