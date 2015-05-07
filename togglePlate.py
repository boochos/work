import maya.cmds as cmds
import maya.mel as mel


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def camName():
    pnl = cmds.getPanel(withFocus=True)
    typ = cmds.getPanel(typeOf=pnl)
    if typ == 'modelPanel':
        cam = cmds.modelPanel(pnl, q=True, cam=True)
        if cam:
            typ = cmds.objectType(cam)
            if typ == 'camera':
                return cam
            else:
                return cam
        else:
            # print 'no model returned', cam
            pass
    else:
        # print 'not model panel', pnl
        pass


def togglePlate():
    # TODO: add proper UI for plate management
    cam = camName()
    # print cam
    if cam:
        connections = cmds.listConnections(cam, sh=True, t='imagePlane')
        if connections:
            connections = list(set(connections))
            plates = platesOnly(connections)
            # print plates
            # check state of one plate
            st = plateState(plates[0])
            for plate in plates:
                if st:
                    # off
                    # print plate, '\n'
                    plateState(plate, toggle=True)
                else:
                    # on
                    # print plate, '\n'
                    plateState(plate, toggle=True)
        else:
            message('No plates')
    else:
        message('Not a camera')


def plateState(plate, toggle=False):
    node = list(set(cmds.listConnections((plate + '.message'), p=True)))
    # print node
    for connection in node:
        # print '\n', connection, '\n'
        if 'imagePlane[' in connection:
            if toggle:
                plateOff(plate, connection)
            else:
                return True
        elif 'plateOff' in connection:
            if toggle:
                plateOn(plate, connection)
            else:
                return False


def platesOnly(connections):
    plates = []
    for item in connections:
        if cmds.nodeType(item) == 'imagePlane':
            plates.append(item)
    return plates


def plateOff(plate, connection):
    # check for 'imagePlane' string in node
    connectionNode = connection.rpartition('.')[0]
    connectionAttr = connection.rpartition('.')[2]
    connectionAttr = connectionAttr.replace('[', 'XXX').replace(']', 'ZZZ')
    attr = 'plateOff_' + connectionAttr
    cmds.addAttr(connectionNode, ln=attr, at='message')
    cmds.connectAttr((plate + '.message'), (connectionNode + '.' + attr), f=True)
    cmds.disconnectAttr((plate + '.message'), connection)
    message('plates OFF')


def plateOn(plate, connection):
    # check for 'plateOff' string in node
    connectionNode = connection.rpartition('.')[0]
    connectionAttr = connection.rpartition('.')[2]
    cmds.deleteAttr(connectionNode, at=connectionAttr)
    reConnectAttr = connectionAttr.replace('XXX', '[').replace('ZZZ', ']')
    reConnectAttr = reConnectAttr.rpartition('_')[2]
    cmds.connectAttr(plate + '.message', connectionNode + '.' + reConnectAttr, f=True)
    message('plates ON')
