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
                cmds.setAttr( self.name + '.' + attr.name, attr.value )

class Clip( Obj ):
    def __init__( self, name='', offset=0, ns=None, comment='' ):
        '''
        can use to copy and paste animation
        '''
        self.sel = cmds.ls( sl=True )
        self.user = ''
        self.start = 0
        self.end = 0
        self.length = 0
        self.comment = comment
        self.date = ''
        self.name = ''
        self.objects = []
        self.offset = offset
        self.ns = ns
        self.getClip()

    def getClip( self ):
        for obj in self.sel:
            a = Obj( obj )
            self.objects.append( a )

    def getClipStats( self ):
        start = 0.0
        end = 0.0
        length = 0.0
        user = ''

    def putClip( self ):
        autoKey = cmds.autoKeyframe( q=True, state=True )
        cmds.autoKeyframe( state=False )
        for obj in self.objects:
            if self.ns:
                obj.name = self.ns + ':' + obj.name.split( ':' )[1]
            obj.offset = self.offset
            obj.putAttribute()
        cmds.autoKeyframe( state=autoKey )


def clipSave( name='', path='', comments='' ):
    '''
    save clip to file
    '''
    path = clipPath( name='clipTemp.clip' )
    clp = Clip()
    fileObject = open( path, 'wb' )
    pickle.dump( clp, fileObject )
    fileObject.close()

def clipOpen( path='' ):
    '''
    open clip form file
    '''
    path = clipPath( name='clipTemp.clip' )
    fileObject = open( path, 'r' )
    clp = pickle.load( fileObject )
    return clp

def clipApply( offset=0, ns=None ):
    '''
    apply animation from file
    '''
    clp = clipOpen()
    clp.ns = ns
    clp.offset = offset
    clp.putClip()

def clipRemap( offset=0 ):
    '''
    apply animation with new namespace from selection
    '''
    sel = cmds.ls( sl=True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
            clipApply( offset=offset, ns=ns )
    else:
        clipApply()

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
