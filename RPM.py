import maya.cmds as cmds


class RPM():

    def __init__( self ):
        self.attr = None
        self.obj = None
        self.label = None
        self.hud = 'RPM'
        self.frames = []
        self.val = []
        self.rpm = []
        self.getObj()
        if self.attr is not None:
            self.display()

    def getObj( self ):
        try:
            self.attr = cmds.channelBox( 'mainChannelBox', q = True, sma = True )[0]
            self.obj = cmds.channelBox( 'mainChannelBox', q = True, mol = True )[0]
            self.label = self.hud + '__' + self.obj.split( ':' )[1] + '.' + self.attr
        except:
            cmds.warning( 'Select an attr in the ChannelBox to operate on.' )

    def avg( self ):
        '''
        3 frame average
        '''
        # 360/(fps * 60) = degrees
        # 360/(24  * 60) = 0.25
        self.frames = [cmds.currentTime( q = True ) - 1, cmds.currentTime( q = True ), cmds.currentTime( q = True ) + 1]
        self.val = []
        self.rpm = []
        for frame in self.frames:
            self.val.append( cmds.getAttr( self.obj + '.' + self.attr, t = frame ) )
        list( set( self.val ) )
        if len( self.val ) != 1:
            self.rpm.append( ( self.val[0] - self.val[1] ) / 0.25 )
            self.rpm.append( ( self.val[1] - self.val[2] ) / 0.25 )
            # average of 2 values
            return sum( self.rpm, 0.0 ) / len( self.rpm )
        else:
            return 0.0

    def remove( self ):
        if cmds.headsUpDisplay( self.hud, ex = True ):
            cmds.headsUpDisplay( self.hud, remove = True )

    def display( self ):
        self.remove()
        cmds.headsUpDisplay( self.hud, section = 1, block = 0, blockSize = 'small', label = self.label, labelFontSize = 'small', command = self.avg, event = 'idle' )  # nodeChanges='attributeChange'


def valueChangePerFrame( rpm = 360 ):
    '''
    x value change per frame
    '''
    return rpm * 0.25


def addSection( rpm = 100, startFrame = 1000, totalFrames = 110 ):
    '''
    used to setup rpm wedge
    '''
    # BUG: keys dont maintain tangent type when setting keyframe
    #
    sel = cmds.ls( sl = 1 )[0]
    attr = 'rotateY'
    crv = cmds.findKeyframe( sel + '.' + attr, c = True )
    #
    r = valueChangePerFrame( rpm )
    print( '________________' )
    print( '_____ for', rpm, 'rpm' )
    print( r, ' x value' )
    x = r * totalFrames
    print( x, ' on totalFrames' )
    cmds.setKeyframe( crv, time = ( startFrame, startFrame ), value = 0, shape = False )
    cmds.setKeyframe( crv, time = ( startFrame + totalFrames, startFrame + totalFrames ), value = x, shape = False )
    cmds.selectKey( crv )
    cmds.keyframe( animation = 'keys', relative = 1, timeChange = ( 0 - ( totalFrames + 1 ) ) )


def tireRotation():
    # TODO: tire rotation, figure it out, copied from net
    '''
    you'll want to link the tire's rotation (in example) in the z axis to the translation in the x axis...
    you'll need to get the diameter of that tire, so use a distance tool to find it...
    once you got that, open up your handy dandy calculator and the formula for the circumference is " 2*3.14*diameter ". 
    Once you get that number, divide 360 by that number.
    so say the diam of the tyre was 4 then the circumference would be 25.13, and 360 / 25.13 = 14.33. 
    So what this means is that for every unit travelled in the x axis, the tyre will rotate 14.33 degrees.
    So to get this to work using mel would look something like this..
    tyre.rotateZ = tyre.translateX * 14.33;
    so what this says is that for every 1 unit travelled in x, the rotate is equal to that times 14.33, so if it went 1 unite, 1 * 14.33 is 14.33 degrees....
    '''
    pass
