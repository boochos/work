import maya.cmds as cmds


class FkIkSwitch( object ):

    def __init__( self, fkIkAttrName = "fkIk", setKeys = True ):
        # args
        self.fkIkAttrName = fkIkAttrName
        self.setKeys = setKeys

        # vars
        self.messageAttrsHolder = None
        self.ikCtl = None
        self.poleVectorCtl = None
        self.poleVectorHook = None
        self.attrHolder = None
        self.clavicleCtl = None
        self.tarsusCtl = None
        self.fkChain = []
        self.ikChain = []

    def __notFkIkElementLog( self, obj ):
        return "FkIkSwitch: " + obj + " is not part of an fkIk system"

    def checkIfFkIkElement( self, obj ):
        assert obj, "FkIkSwitch.checkIfFkIkElement: obj cannot be none"
        assert cmds.objExists( obj ), obj + " is invalid"

        conns = cmds.listConnections( obj + ".message", p = 1 )

        assert conns, self.__notFkIkElementLog( obj )

        self.messageAttrsHolder = None

        for c in conns:
            attrName = c.split( "." )
            if attrName[1].startswith( "fkIk" ):
                self.messageAttrsHolder = attrName[0]
                break

        assert self.messageAttrsHolder, self.__notFkIkElementLog( obj )

        return self.messageAttrsHolder

    def checkSelectedIfFkIkElement( self ):
        sels = cmds.ls( sl = 1, type = "transform" )
        assert sels, "FkIkSwitch.checkIfFkIkElement: nothing selected or invalid selection"

        if len( sels ) > 1:
            print( "FkIkSwitch.checkIfFkIkElement: more than one item selected, using the first one" )

        self.checkIfFkIkElement( sels[0] )

    def __getAttrConnection( self, a, errorIfNotFound = True ):
        # if a is a multi, return the list
        if not cmds.objExists( self.messageAttrsHolder + ".fkIk" + a ):
            return

        isMulti = cmds.addAttr( self.messageAttrsHolder + ".fkIk" + a, q = 1, multi = 1 )
        if isMulti:
            elements = []
            indices = cmds.getAttr( self.messageAttrsHolder + ".fkIk" + a, mi = 1 )
            for i in indices:
                conns = cmds.listConnections( self.messageAttrsHolder + ".fkIk" + a + "[" + str( i ) + "]" )

                if errorIfNotFound:
                    assert conns, "FkIkSwitch.__getAttrConnection: " + "fkIk" + a + "[" + str( i ) + "]" + " is not connected"

                if conns:
                    elements.append( conns[0] )

            return elements
        else:
            conns = cmds.listConnections( self.messageAttrsHolder + ".fkIk" + a )

            if errorIfNotFound:
                assert conns, "FkIkSwitch.__getAttrConnection: " + "fkIk" + a + " is not connected"

            if conns:
                return conns[0]

    def __gatherConnectedNodes( self ):
        self.ikCtl = self.__getAttrConnection( "IkCtl" )
        self.poleVectorCtl = self.__getAttrConnection( "PoleVectorCtl" )
        self.poleVectorHook = self.__getAttrConnection( "PoleVectorHook" )
        self.attrHolder = self.__getAttrConnection( "SwitchAttrHolder" )
        self.clavicleCtl = self.__getAttrConnection( "ClavCtl", errorIfNotFound = False )
        self.tarsusCtl = self.__getAttrConnection( "TarsusCtl", errorIfNotFound = False )
        self.ikCtlHook = self.__getAttrConnection( "IkCtlHook" )
        self.fkWristCtlHook = self.__getAttrConnection( "FkWristCtlHook" )

        # fkChain
        self.fkChain = self.__getAttrConnection( "FkChain" )
        self.ikChain = self.__getAttrConnection( "IkChain" )

    def __setKey( self, nd, a, timeOffset = 0 ):
        if self.setKeys:
            currTime = cmds.currentTime( q = True )

#            if timeOffset < 0:
#                cmds.setKeyframe(nd + "." + a, time = currTime + timeOffset, inTangentType = 'clamped', outTangentType = 'clamped')
#            else:
            cmds.setKeyframe( nd + "." + a, time = currTime + timeOffset, inTangentType = 'clamped', outTangentType = 'clamped' )

    def __match( self, this, that, t = True, r = True ):
        if t:
            for a in ["tx", "ty", "tz"]:
                self.__setKey( this, a, -1 )

            pos = cmds.xform( that, q = 1, ws = 1, t = 1 )
            cmds.xform( this, ws = 1, t = pos )

            for a in ["tx", "ty", "tz"]:
                self.__setKey( this, a, 0 )

        if r:
            for a in ["rx", "ry", "rz"]:
                self.__setKey( this, a, -1 )

            rot = cmds.xform( that, q = 1, ws = 1, ro = 1 )
            cmds.xform( this, ws = 1, ro = rot )

            for a in ["rx", "ry", "rz"]:
                self.__setKey( this, a, 0 )

    def __fkToIk( self ):
        # snap the ikCtl to the last fkChain and the poleVector to the poleVectorHook
        self.__match( self.ikCtl, self.fkWristCtlHook, t = 1, r = 1 )
        self.__match( self.poleVectorCtl, self.poleVectorHook, t = 1, r = 0 )

        for i in range( len( self.fkChain ) ):
            self.__match( self.fkChain[i], self.fkChain[i], t = 0, r = 1 )

        if self.tarsusCtl:
            self.__match( self.tarsusCtl, self.fkChain[-2], t = 1, r = 0 )

    def __ikToFk( self ):
        self.__match( self.ikCtl, self.ikCtl, t = 1, r = 1 )
        self.__match( self.poleVectorCtl, self.poleVectorCtl, t = 1, r = 0 )

        if self.clavicleCtl:
            self.__match( self.clavicleCtl, clavicleCtl.ikCtl, t = 1, r = 1 )

            # store the clav ori, turn off autoClav and set the ori back on the ctl
            clavOri = cmds.xform( self.clavicleCtl, q = 1, ws = 1, ro = 1 )
            self.__setKey( self.clavicleCtl, "autoClavicle", -1 )
            cmds.setAttr( self.clavicleCtl + ".autoClavicle", 0 )
            cmds.xform( self.clavicleCtl, ws = 1, ro = clavOri )

            self.__setKey( self.clavicleCtl, "autoClavicle", 0 )

        if self.tarsusCtl:
            for i in range( len( self.fkChain ) - 1 ):
                self.__match( self.fkChain[i], self.ikChain[i], t = 0, r = 1 )
                self.__match( self.fkChain[len( self.fkChain ) - 1], self.ikCtlHook, t = 0, r = 1 )
        else:
            for i in range( len( self.fkChain ) ):
                self.__match( self.fkChain[i], self.ikChain[i], t = 0, r = 1 )

    def switch( self, useSelection = True, obj = None ):
        if useSelection:
            self.checkSelectedIfFkIkElement()
        else:
            assert obj, "FkIkSwitch.switch: obj cannot be None"
            assert cmds.objExists( obj ), "FkIkSwitch.switch: " + obj + " is invalid"
            self.checkIfFkIkElement( obj )

        # at this point we should have everything we need, get all the nodes
        self.__gatherConnectedNodes()

        # find the switch attrHolder
        fkIkAttr = self.attrHolder + "." + self.fkIkAttrName
        assert cmds.objExists( fkIkAttr ), "FkIkSwitch.switch: cannot find " + fkIkAttr
        fkIkVal = cmds.getAttr( fkIkAttr )

        self.__setKey( self.attrHolder, self.fkIkAttrName, -1 )

        if fkIkVal < 0.5:  # we're in fk, switching to ik
            self.__fkToIk()
            cmds.setAttr( fkIkAttr, 1 )
        else:  # we're in ik, switching to fk
            self.__ikToFk()
            cmds.setAttr( fkIkAttr, 0 )

        self.__setKey( self.attrHolder, self.fkIkAttrName, 0 )

# sw = FkIkSwitch(setKeys = 1)
# sw.switch()
