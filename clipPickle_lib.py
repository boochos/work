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
        self.getKeys()

    def getKeys( self ):
        index = cmds.keyframe( self.obj, q=True, time=( self.frame, self.frame ), at=self.attr, indexValue=True )[0]
        self.value = cmds.keyframe( self.obj, q=True, index=( index, index ), at=self.attr, valueChange=True )[0]
        self.inAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inAngle=True )[0]
        self.outAngle = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outAngle=True )[0]
        self.inTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inTangentType=True )[0]
        self.outTangentType = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outTangentType=True )[0]
        self.inWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, inWeight=True )[0]
        self.outWeight = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, outWeight=True )[0]
        self.lock = cmds.keyTangent( self.obj, q=True, time=( self.frame, self.frame ), attribute=self.attr, lock=True )[0]

    def putKeys( self ):
        cmds.setKeyframe( self.obj, at=self.attr, time=( self.frame + self.offset, self.frame + self.offset ), value=self.value )
        cmds.keyTangent( self.obj, edit=True, time=( self.frame + self.offset, self.frame + self.offset ), attribute=self.attr,
        inTangentType=self.inTangentType, outTangentType=self.outTangentType, inWeight=self.inWeight,
        outWeight=self.outWeight, inAngle=self.inAngle, outAngle=self.outAngle, lock=self.lock )

class Attribute( Key ):
    def __init__( self, obj, attr, offset=0 ):
        self.obj = obj
        self.name = attr
        self.crv = cmds.findKeyframe( self.obj, at=self.name, c=True )
        self.frames = []
        self.key = []
        self.value = cmds.getAttr( self.obj + '.' + self.name )
        self.offset = offset
        self.qualify()

    def qualify( self ):
        if self.crv != None:
            if len( self.crv ) == 1:
                self.crv = self.crv[0]
                self.getKeyedFrames()
                self.getKeyAttributes()

    def getKeyedFrames( self ):
        if self.crv != None:
            framesTmp = cmds.keyframe( self.crv, q=True )
            for frame in framesTmp:
                self.frames.append( frame )
            self.frames = list( set( self.frames ) )
            self.frames.sort()

    def getKeyAttributes( self ):
        for frame in self.frames:
            a = Key( self.obj, self.name, frame )
            self.key.append( a )
    '''
    def build( self, replace=True ):
        if replace == True:
            self.crv = cmds.findKeyframe( self.obj, at=self.name, c=True )
            if self.crv:
                cmds.delete( self.crv )
        for key in self.key:
            key.obj = self.obj
            key.put()'''

class Obj( Attribute ):
    def __init__( self, obj, offset=0 ):
        self.name = obj
        self.offset = offset
        self.attribute = []
        self.getCurve()

    def getCurve( self ):
        keyable = cmds.listAttr( self.name, k=True )
        for k in keyable:
            a = Attribute( self.name, k )
            self.attribute.append( a )

    def putCurve( self ):
        for attr in self.attribute:
            if len( attr.key ) > 0:
                for k in attr.key:
                    k.offset = self.offset
                    k.putKeys()
            else:
                cmds.setAttr( self.name + '.' + attr.name, attr.value )

class Clip( Obj ):
    def __init__( self, offset=0 ):
        self.sel = cmds.ls( sl=True )
        self.object = []
        self.offset = offset
        self.getClip()

    def getClip( self ):
        for obj in self.sel:
            a = Obj( obj )
            self.object.append( a )

    def putClip( self ):
        for obj in self.object:
            obj.offset = self.offset
            obj.putCurve()

def clipSave( name='', path='' ):
    '''
    save clip to file
    '''
    path = clipPath( name='clipTemp.clip' )
    clp = Clip()
    fileObject = open( path, 'wb' )
    pickle.dump( clp, fileObject )
    fileObject.close()

def clipOpen():
    '''
    open clip form file
    '''
    path = clipPath( name='clipTemp.clip' )
    fileObject = open( path, 'r' )
    clp = pickle.load( fileObject )
    return clp

def clipApply( offset=0 ):
    '''
    apply animation
    '''
    clp = clipOpen()
    clp.offset = offset
    clp.putClip()

def clipPath( name='' ):
    path = clipTempPath()
    if os.path.isdir( path ):
        return os.path.join( path, name )
    else:
        os.mkdir( path, 0777 )
        return os.path.join( path, name )

def clipTempPath():
    user = os.path.expanduser( '~' )
    path = user + '/maya/clipExport/'
    return path
