import maya.cmds as cmds
import maya.mel as mel
import time, getpass
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
    def __init__( self, obj, attr, frame, offset=0, weightedTangents=None ):
        #dont think this currently accounts for weighted tangents
        self.obj = obj
        self.attr = attr
        self.frame = frame
        self.value = None
        self.crv = None
        self.weightedTangents = weightedTangents
        self.weightLock = False
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
        index = cmds.keyframe( self.obj, q=True, time=( self.frame, self.frame ), at=self.attr, indexValue=True )[0]
        self.value = cmds.keyframe( self.obj, q=True, index=( index, index ), at=self.attr, valueChange=True )[0]
        self.inAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inAngle=True )[0]
        self.outAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outAngle=True )[0]
        self.inTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inTangentType=True )[0]
        self.outTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outTangentType=True )[0]
        self.lock = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, lock=True )[0]
        if self.weightedTangents:
            self.weightLock = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, weightLock=True )[0]
            self.inWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inWeight=True )[0]
            self.outWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outWeight=True )[0]

    def putKey( self ):
        #set key, creates curve node
        cmds.setKeyframe( self.obj, at=self.attr, time=( self.frame + self.offset, self.frame + self.offset ), value=self.value, shape=False )
        #update curve name, set curve type, set weights
        self.crv = cmds.findKeyframe( self.obj, at=self.attr, c=True )[0]
        cmds.setAttr( self.crv + '.weightedTangents', self.weightedTangents )
        if  self.weightedTangents:
            cmds.keyTangent( self.obj, edit=True, time=( self.frame + self.offset, self.frame + self.offset ), attribute=self.attr, weightLock=self.weightLock,
            inWeight=self.inWeight, outWeight=self.outWeight)
        #set rest of key attributes
        cmds.keyTangent( self.obj, edit=True, time=( self.frame + self.offset, self.frame + self.offset ), attribute=self.attr,
        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock )

class Attribute( Key ):
    def __init__( self, obj, attr, offset=0 ):
        '''
        add get/put keys from Key class to this one
        '''
        self.obj = obj
        self.name = attr
        self.crv = cmds.findKeyframe( self.obj, at=self.name, c=True )
        #print self.crv
        self.frames = []
        self.keys = []
        self.value = cmds.getAttr( self.obj + '.' + self.name )
        self.offset = offset
        self.preInfinity = None
        self.postInfinity = None
        self.weightedTangents = None
        self.getCurve()

    def getCurve( self ):
        if self.crv != None:
            if len( self.crv ) == 1:
                self.crv = self.crv[0]
                self.getCurveAttrs()
                self.getFrames()
                self.getKeys()

    def getCurveAttrs(self):
        self.preInfinity = cmds.getAttr( self.crv + '.preInfinity'  )
        self.postInfinity = cmds.getAttr( self.crv + '.postInfinity' )
        self.weightedTangents = cmds.getAttr(self.crv + '.weightedTangents')

    def getFrames( self ):
        if self.crv != None:
            self.getCurveAttrs()
            framesTmp = cmds.keyframe( self.crv, q=True )
            for frame in framesTmp:
                self.frames.append( frame )
            self.frames = list( set( self.frames ) )
            self.frames.sort()

    def getKeys( self ):
        for frame in self.frames:
            a = Key( self.obj, self.name, frame, weightedTangents=self.weightedTangents )
            self.keys.append( a )

    def putCurve(self):
        if self.keys:
            print len(self.keys)
            for k in self.keys:
                k.obj = self.obj
                k.offset = self.offset
                k.crv = self.crv
                k.putKey()
            self.putCurveAttrs()
        else:
            if not cmds.getAttr( self.obj + '.' + self.name, l=True ):
                cmds.setAttr( self.obj + '.' + self.name, self.value )

    def putCurveAttrs(self):
        #need to update curve name, isnt the same as stored, depends on how curves and layers are ceated
        self.crv = cmds.findKeyframe( self.obj, at=self.name, c=True )[0]
        cmds.setAttr( self.crv + '.preInfinity', self.preInfinity  )
        cmds.setAttr( self.crv + '.postInfinity', self.postInfinity )

class Obj( Attribute ):
    def __init__( self, obj, offset=0 ):
        self.name = obj
        self.offset = offset
        self.attributes = []
        self.getAttribute()

    def getAttribute( self ):
        #currently does not include enums
        keyable = cmds.listAttr( self.name, k=True, s=True )
        print keyable
        for k in keyable:
            a = Attribute( self.name, k )
            self.attributes.append( a )

    def putAttribute( self ):
        for attr in self.attributes:
            attr.obj = self.name
            attr.offset = self.offset
            attr.putCurve()


class Layer( Obj ):
    def __init__( self, sel=[], name=None, offset=0, ns=None, comment='' ):
        '''
        can use to copy and paste animation
        '''
        self.sel = sel
        self.start = None
        self.end = None
        self.length = None
        self.comment = comment
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
        self.weight = None    #can be animated, add Key class
        self.rotationAccumulationMode = None    #test if enums work
        self.scaleAccumulationMode = None
        #
        self.getObjects()
        self.getLayerAttrs()
        self.getStartEndLength()

    def getObjects( self ):
        for obj in self.sel:
            a = Obj( obj )
            self.objects.append( a )

    def getStartEndLength( self ):
        frames = []
        for obj in self.objects:
            for attr in obj.attributes:
                if len( attr.keys ) > 0:
                    for k in attr.keys:
                        frames.append( k.frame )
        frames = sorted( list( set( frames ) ) )
        if frames:
            self.start = frames[0]
            self.end = frames[len( frames ) - 1]
            self.length = self.end - self.start + 1

    def getLayerAttrs( self ):
        if self.name:
            self.mute = cmds.getAttr( self.name + '.mute' )
            self.solo = cmds.getAttr( self.name + '.solo' )
            self.lock = cmds.getAttr( self.name + '.lock' )
            self.ghost = cmds.getAttr( self.name + '.ghost' )
            self.ghostColor = cmds.getAttr( self.name + '.ghostColor' )
            self.override = cmds.getAttr( self.name + '.override' )
            self.passthrough = cmds.getAttr( self.name + '.passthrough' )
            self.weight = Attribute( self.name, 'weight' )
            self.rotationAccumulationMode = cmds.getAttr( self.name + '.rotationAccumulationMode' )
            self.scaleAccumulationMode = cmds.getAttr( self.name + '.scaleAccumulationMode' )

    def putObjects( self, atCurrentFrame=False ):
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

    def putLayerAttrs( self ):
        cmds.setAttr( self.name + '.mute', self.mute )
        cmds.setAttr( self.name + '.solo', self.solo )
        cmds.setAttr( self.name + '.lock' , self.lock )
        cmds.setAttr( self.name + '.ghost', self.ghost )
        cmds.setAttr( self.name + '.ghostColor', self.ghostColor )
        cmds.setAttr( self.name + '.override', self.override )
        cmds.setAttr( self.name + '.passthrough', self.passthrough )
        self.weight.putCurve()
        cmds.setAttr( self.name + '.rotationAccumulationMode', self.rotationAccumulationMode )
        cmds.setAttr( self.name + '.scaleAccumulationMode', self.scaleAccumulationMode )

class Clip( Layer ):
    def __init__( self, name='', offset=0, ns=None, comment='' ):
        self.sel = cmds.ls( sl=True )
        self.name = name
        self.comment = comment
        self.source = None
        self.user = getpass.getuser()
        self.date = time.strftime("%c")
        #
        self.start = None
        self.end = None
        self.length = None
        self.layers = []    #list of class objects
        self.layerNames = None
        self.rootLayer = None
        self.offset = offset
        self.ns = ns
        #
        self.getLayers()
        self.getClipAttrs()

    def getClipAttrs(self):
        #scene name
        sceneName = cmds.file( q=True, sn=True )
        self.source = sceneName[sceneName.rfind( '/' ) + 1:]

    def getLayers( self ):
        #get layers in scene
        self.layerNames = cmds.ls( type='animLayer' )    #should consider reversing order
        self.rootLayer = cmds.animLayer( q=True, root=True )
        layerMembers = []
        if self.layerNames:
            for layer in self.layerNames:
                #collect objects in layer
                currentlayer = []
                connected = cmds.listConnections( layer, s=1, d=0, t='transform' )
                if connected:
                    objects = list( set( connected ) )
                    for s in self.sel:
                        if s in objects:
                            currentlayer.append( s )
                            layerMembers.append( s )
                    if currentlayer:
                        self.setActiveLayer( layer )    #create clip
                        #build class
                        #print layer, '_________'
                        clp = Layer( name=layer, sel=currentlayer, comment=self.comment )
                        self.layers.append( clp )    #append to self.layers
                else:
                    print layer, '     no members'
            self.setActiveLayer( l=self.rootLayer )
            clp = Layer( sel=self.sel, comment=self.comment )    #build class
            self.layers.append( clp )
        else:
            #no anim layers, create single layer class
            clp = Layer( name=None,sel=self.sel, comment=self.comment )
            self.layers.append( clp )

    def setActiveLayer( self, l=None ):
        #maya 2014, this does not activate layer: cmds.animLayer( ex, e=True, sel=False )
        #need to source mel script, otherwise selectLayer command doesn't exist
        #source "C:/Program Files/Autodesk/Maya2014/scripts/startup/buildSetAnimLayerMenu.mel";
        mel.eval( 'source "buildSetAnimLayerMenu.mel";' )
        if l:
            mel.eval( 'selectLayer(\"' + l + '\");' )
        else:
            mel.eval( 'selectLayer(\"");' )

    def putLayers( self ):
        #restore layers from class
        clash = '__CLASH__'
        for layer in self.layers:
            sceneLayers = cmds.ls( type='animLayer' )
            sceneRootLayer = cmds.animLayer( q=True, root=True )
            #print layer.name
            if not layer.name:
                self.setActiveLayer( l=sceneRootLayer )
                layer.putObjects()
            else:
                if not cmds.animLayer( layer.name, q=True, ex=True ):
                    #create layer
                    cmds.animLayer( layer.name )
                else:
                    if not cmds.animLayer( clash + layer.name, q=True, ex=True ):
                        cmds.animLayer( clash + layer.name )
                        message( 'Layer ' + layer.name + ' already exists' )
                    else:
                        message( 'Layer ' + layer.name + ' already exists' )
                        break
                #set layer attrs
                layer.putLayerAttrs()
                #set layer to current
                self.setActiveLayer( l=layer.name )
                #add objects
                if layer.sel:
                    cmds.select( layer.sel )
                    cmds.animLayer( layer.name, e=True, aso=True )
                #add animation
                layer.putObjects()

def clipSave( name='clipTemp.clip', path='', comment='' ):
    '''
    save clip to file
    '''
    path = clipPath( name=name )
    clp = Clip( name=name.split( '.' )[0], comment=comment )
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
            clipApply( path=path, offset=offset )
    else:
        clipApply( path=path )

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