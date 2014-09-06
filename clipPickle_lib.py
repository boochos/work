import maya.cmds as cmds
import maya.mel as mel
import pickle, os

def message( what='', maya=True ):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print what

class Key():
    def __init__( self, obj, attr, frame, offset=0 ):
        self.obj = obj
        self.attr = attr
        self.frame = frame
        self.value = None
        self.inTangentType = None
        self.inWeight = None
        self.inAngle = None
        self.outTangentType = None
        self.outWeight = None
        self.outAngle = None
        self.lock = None
        self.offset = offset
        self.getKey()

    #pretty sure these defs should be in the Attribute class

    def getKey( self ):
        print self.obj, self.attr, self.frame, self.value
        index = cmds.keyframe( self.obj, q=True, time=( self.frame, self.frame ), at=self.attr, indexValue=True )[0]
        self.value = cmds.keyframe( self.obj, q=True, index=( index, index ), at=self.attr, valueChange=True )[0]
        self.inAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inAngle=True )[0]
        self.outAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outAngle=True )[0]
        self.inTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inTangentType=True )[0]
        self.outTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outTangentType=True )[0]
        self.inWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inWeight=True )[0]
        self.outWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outWeight=True )[0]
        self.lock = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, lock=True )[0]

    def putKey( self ):
        cmds.setKeyframe( self.obj, at=self.attr, time=( self.frame + self.offset, self.frame + self.offset ), value=self.value )
        cmds.keyTangent( self.obj, edit=True, time=( self.frame + self.offset, self.frame + self.offset ), attribute=self.attr,
        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inWeight=self.inWeight,
        outWeight=self.outWeight, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock )

class Attribute( Key ):
    def __init__( self, obj, attr, offset=0 ):
        '''
        add get/put keys from Key class to this one
        '''
        self.obj = obj
        self.name = attr
        self.crv = cmds.findKeyframe( self.obj, at=self.name, c=True )
        self.frames = []
        self.key = []
        self.value = cmds.getAttr( self.obj + '.' + self.name )
        self.offset = offset
        self.preInfinity = None
        self.postInfinity = None
        self.qualify()

    def qualify( self ):
        if self.crv != None:
            if len( self.crv ) == 1:
                self.crv = self.crv[0]
                self.getFrames()
                self.getKeys()

    def getFrames( self ):
        if self.crv != None:
            framesTmp = cmds.keyframe( self.crv, q=True )
            for frame in framesTmp:
                self.frames.append( frame )
            self.frames = list( set( self.frames ) )
            self.frames.sort()

    def getKeys( self ):
        for frame in self.frames:
            a = Key( self.obj, self.name, frame )
            self.key.append( a )


class Obj( Attribute ):
    def __init__( self, obj, offset=0 ):
        self.name = obj
        self.offset = offset
        self.attributes = []
        self.getAttribute()

    def getAttribute( self ):
        keyable = cmds.listAttr( self.name, k=True, s=True )
        for k in keyable:
            a = Attribute( self.name, k )
            self.attributes.append( a )

    def putAttribute( self ):
        '''
        need to incorporate infinity status
        '''
        for attr in self.attributes:
            if len( attr.key ) > 0:
                for k in attr.key:
                    k.obj = self.name
                    k.offset = self.offset
                    k.putKey()
            else:
                if not cmds.getAttr(self.name + '.' + attr.name, l=True):
                    cmds.setAttr( self.name + '.' + attr.name, attr.value )

class ClipLayer( Obj ):
    def __init__( self, sel=[], name=None, offset=0, ns=None, comment='' ):
        '''
        can use to copy and paste animation
        '''
        self.sel = sel
        self.user = os.path.expanduser( '~' )
        self.start = None
        self.end = None
        self.length = None
        self.comment = comment
        self.date = ''
        #self.name = name
        self.objects = []
        self.offset = offset
        self.ns = ns
        #layer attrs
        self.name = name
        self.mute = None
        self.solo = None
        self.lock = None
        self.ghost = None
        self.ghostColor = None
        self.override = None
        self.passthrough = None
        self.weight = None #can be animated
        self.rotationAccumulationMode = None
        self.scaleAccumulationMode = None
        #
        self.getObject()
        self.getLayerAttrs()
        self.getStartEndLength()

    def getObject( self ):
        for obj in self.sel:
            a = Obj( obj )
            self.objects.append( a )

    def getStartEndLength( self ):
        frames = []
        for obj in self.objects:
            for attr in obj.attributes:
                if len( attr.key ) > 0:
                    for k in attr.key:
                        frames.append( k.frame )
        frames = sorted( list( set( frames ) ) )
        if frames:
            self.start = frames[0]
            self.end = frames[len( frames ) - 1]
            self.length = self.end - self.start + 1

    def getLayerAttrs(self):
        if self.name:
            self.mute =  cmds.getAttr(self.name + '.mute')
            self.solo = cmds.getAttr(self.name + '.solo')
            self.lock = cmds.getAttr(self.name + '.lock')
            self.ghost = cmds.getAttr(self.name + '.ghost')
            self.ghostColor = cmds.getAttr(self.name + '.ghostColor')
            self.override = cmds.getAttr(self.name + '.override')
            self.passthrough = cmds.getAttr(self.name + '.passthrough')
            self.weight = cmds.getAttr(self.name + '.weight')
            self.rotationAccumulationMode = cmds.getAttr(self.name + '.rotationAccumulationMode')
            self.scaleAccumulationMode = cmds.getAttr(self.name + '.scaleAccumulationMode')

    def putObjects( self, atCurrentFrame=True ):
        #doesnt work if either no anim curves or object has no namespace
        autoKey = cmds.autoKeyframe( q=True, state=True )
        cmds.autoKeyframe( state=False )
        #current
        if atCurrentFrame:
            current = cmds.currentTime( q=True )
            if self.start > current:
                self.offset = current - self.start
            else:
                self.offset = ( ( self.start - current ) * -1.0 ) + 0.0
            print self.offset
        #put
        for obj in self.objects:
            if self.ns:
                obj.name = self.ns + ':' + obj.name.split( ':' )[1]
            obj.offset = self.offset
            obj.putAttribute()
        cmds.autoKeyframe( state=autoKey )

    def putLayerAttrs(self):
        self.mute =  cmds.setAttr(self.name + '.mute', self.mute )
        self.solo = cmds.setAttr(self.name + '.solo', self.solo)
        self.lock = cmds.setAttr(self.name + '.lock' , self.lock)
        self.ghost = cmds.setAttr(self.name + '.ghost', self.ghost)
        self.ghostColor = cmds.setAttr(self.name + '.ghostColor', self.ghostColor)
        self.override = cmds.setAttr(self.name + '.override', self.override)
        self.passthrough = cmds.setAttr(self.name + '.passthrough', self.passthrough)
        self.weight = cmds.setAttr(self.name + '.weight', self.weight)
        self.rotationAccumulationMode = cmds.setAttr(self.name + '.rotationAccumulationMode', self.rotationAccumulationMode)
        self.scaleAccumulationMode = cmds.setAttr(self.name + '.scaleAccumulationMode', self.scaleAccumulationMode)

class Clip( ClipLayer ):
    def __init__( self, name='', offset=0, ns=None, comment='' ):
        self.sel = cmds.ls( sl=True )
        self.user = os.path.expanduser( '~' )
        self.start = None
        self.end = None
        self.length = None
        self.comment = comment
        self.date = ''
        self.name = name
        self.layers = []
        self.existingLayers = None
        self.offset = offset
        self.ns = ns
        self.getLayers()

    def getLayers(self):
        self.existingLayers = cmds.ls(type='animLayer') #should consider reversing order
        layerMembers = []
        if self.existingLayers:
            for layer in self.existingLayers:
                #collect objects in layer
                currentlayer = []
                connected = cmds.listConnections(layer, s=1, d=0, t='transform')
                if connected:
                    print layer, '    has members', connected
                    objects = list(set(connected))
                    if objects:
                        for s in self.sel:
                            if s in objects:
                                currentlayer.append(s)
                                layerMembers.append(s)
                    #create clip
                    self.setLayer(layer)
                    print currentlayer, '    current'
                    clp = ClipLayer( name=layer, sel=currentlayer, comment=self.comment )
                    #append to self.layers
                    self.layers.append(clp)
                else:
                    print layer, '     no members'
            #build object list for objects not in anim layer
            nonLayerMemebers = list(set(self.sel). difference(layerMembers))
            if nonLayerMemebers:
                clp = ClipLayer( sel=nonLayerMemebers, comment=self.comment )
                #append to self.layers
                self.layers.append(clp)
        else:
            #no anim layers, create clip
            clp = ClipLayer( sel=self.sel, comment=self.comment )
            self.layers.append(clp)

    def setLayer(self, l=None):
        #all off
        existingLayers = cmds.ls(type='animLayer')
        if existingLayers:
            for ex in existingLayers:
                cmds.animLayer(ex, e=True, sel=False)
            #set 'l' as active layer
            if l:
                cmds.animLayer(l, e=True, sel=True)

    def putLayers(self):
        clash = '__CLASH__'
        existingLayers = cmds.ls(type='animLayer')
        for layer in self.layers:
            if not layer.name:
                layer.putObjects()
            else:
                if not cmds.animLayer(layer.name, q=True, ex=True):
                    #create layer
                    cmds.animLayer(layer.name)
                else:
                    if not cmds.animLayer(clash + layer.name, q=True, ex=True):
                        cmds.animLayer(clash + layer.name)
                    else:
                        message('Layer ' + layer.name + ' already exists')
                        break
                #set layer attrs
                layer.putLayerAttrs()
                #set layer to current
                self.setLayer(l=layer.name)
                #add objects
                #print layer.sel, '000000000000000'
                cmds.select(layer.sel)
                cmds.animLayer(layer.name, e=True, aso=True)
                #add animation
                layer.putObjects()

def clipSave( name='clipTemp.clip', path='', comment='' ):
    '''
    save clip to file
    '''
    path = clipPath( name=name )
    clp = Clip( name=name.split('.')[0], comment=comment )
    print clp.name
    fileObject = open( path, 'wb' )
    pickle.dump( clp, fileObject )
    fileObject.close()

def clipOpen( path='' ):
    '''
    open clip form file
    '''
    fileObject = open( path, 'r' )
    clp = pickle.load( fileObject )
    return clp

def clipApply( path='', offset=0, ns=None ):
    '''
    apply animation from file
    '''
    clp = clipOpen( path=path )
    clp.ns = ns
    #clp.offset = offset
    clp.putLayers()

def clipRemap( path='', offset=0 ):
    '''
    apply animation with new namespace from selection
    '''
    sel = cmds.ls( sl=True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
            clipApply( path=path, offset=offset, ns=ns )
    else:
        clipApply(path=path)

def clipPath( name='' ):
    path = clipTempPath()
    if os.path.isdir( path ):
        return os.path.join( path, name )
    else:
        os.mkdir( path, 0777 )
        return os.path.join( path, name )

def clipTempPath():
    user = os.path.expanduser( '~' )
    path = user + '/maya/clipLibrary/'
    return path
