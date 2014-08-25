import maya.cmds as cmds
import maya.mel as mel


def message( what='', maya=True ):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print what

def togglePlate():
    sel = cmds.ls( sl=True )
    #make sure 1 object selected
    if len( sel ) == 1:
        #conditions, try, exception, else(no exception)
        try:
            #select shape node
            try:
                shape = cmds.listRelatives( shapes=True )[0]    #first item only
            except:
                if cmds.nodeType( sel ) == 'camera':
                    shape = sel
        except:
            #if no shape node exists in selection
            message( 'Selection is not of camera type' )
        else:
            #is shape node a camera
            if cmds.nodeType( shape ) == 'camera':
                connections = cmds.listConnections( shape, sh=True, t='imagePlane' )
                print connections
                if connections:
                #loop through connections
                    for item in connections:
                        #if imagePlane exists...
                        if cmds.nodeType( item ) == 'imagePlane':
                            print item
                            #find what message is connected too, connect to opposite
                            node = cmds.listConnections( ( item + '.message' ), p=True )
                            for connection in node:
                                if 'imagePlane[' in connection:
                                    #check for 'imagePlane' string in node
                                    connectionNode = connection.rpartition( '.' )[0]
                                    connectionAttr = connection.rpartition( '.' )[2]
                                    connectionAttr = connectionAttr.replace( '[', 'XXX' ).replace( ']', 'ZZZ' )
                                    attr = 'plateOff_' + connectionAttr
                                    cmds.addAttr( connectionNode, ln=attr, at='message' )
                                    cmds.connectAttr( ( item + '.message' ), ( connectionNode + '.' + attr ), f=True )
                                    cmds.disconnectAttr( ( item + '.message' ), connection )
                                    message( 'Image sequence OFF' )
                                elif 'plateOff' in connection:
                                    #check for 'plateOff' string in node
                                    connectionNode = connection.rpartition( '.' )[0]
                                    connectionAttr = connection.rpartition( '.' )[2]
                                    cmds.deleteAttr( connectionNode, at=connectionAttr )
                                    reConnectAttr = connectionAttr.replace( 'XXX', '[' ).replace( 'ZZZ', ']' )
                                    reConnectAttr = reConnectAttr.rpartition( '_' )[2]
                                    cmds.connectAttr( item + '.message', connectionNode + '.' + reConnectAttr, f=True )
                                    message( 'Image sequence ON' )
                        else:
                            pass
                            #mel.eval('warning \"' + '////...imagePlane node not present on ' + sel[0] + '...////' + '\";')
                else:
                    pass
                    #message('No connections found on ' + sel[0])
            else:
                message( 'Selection is not of camera type' )
    else:
        message( 'Select a camera with an imagePlane node' )
