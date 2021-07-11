import os

import maya.cmds as cmds
import maya.mel as mel


class Get():

    def __init__( self, fromSelection = True ):
        self.min = cmds.playbackOptions( q = True, minTime = True )
        self.max = cmds.playbackOptions( q = True, maxTime = True )
        self.current = cmds.currentTime( q = True )
        self.selStart = self.current
        self.selEnd = self.current
        self.start = 0
        self.end = 0
        self.setStartEnd()
        self.keyStart = 0
        self.keyEnd = 0
        self.range = 0
        self.selection = False
        if fromSelection:
            self.keyedFrames()
        # Has to be last
        self.selRange()

    def selRange( self ):
        # overide range if selected range is detected
        sel = cmds.timeControl( 'timeControl1', q = True, ra = True )
        self.range = sel[1] - sel[0]
        # print range, '  range'
        if self.range > 1:
            # print self.range, '_____range'
            self.selStart = sel[0]
            self.selEnd = sel[1]
            self.keyStart = sel[0]
            self.keyEnd = sel[1]
            self.selection = True

    def setStartEnd( self ):
        if self.selStart != self.current and self.selEnd != self.current:
            self.start = self.selStart
            self.end = self.selEnd
        else:
            self.start = self.min
            self.end = self.max

    def keyedFrames( self ):
        selAll = cmds.ls( sl = True )
        # print 'X     ', selAll
        frames = []
        if selAll:
            for sel in selAll:
                animCurves = cmds.findKeyframe( sel, c = True )
                # print 'XX    ',
                if animCurves is not None:
                    for crv in animCurves:
                        framesTmp = cmds.keyframe( crv, q = True )
                        # print 'XXX    ', framesTmp
                        for frame in framesTmp:
                            frames.append( frame )
                    frames = list( set( frames ) )
                    # print 'XXXX    ', frames, selAll
                    self.keyStart = min( frames )
                    self.keyEnd = max( frames )
                else:
                    # print 'no anim curves', sel
                    pass
        else:
            print( '-- Select an object. --' )


def frameRangeFromMaFile( path = '', handles = 0 ):
    '''
    
    '''
    path = 'P:/XMAG/075/XMAG_075_035/anim/maya/scenes/XMAG_075_035_anim_v003.ma'
    play_start = 0
    play_end = 0
    all_start = 0
    all_end = 0
    # print path
    if os.path.isfile( path ):
        inFile = open( path, 'r' )
        for line in inFile.readlines():
            cvLine = line.strip( '\n' )
            if 'playbackOptions' in line:
                # print line
                line_parts = line.split( ' ' )
                i = 0
                for part in line_parts:
                    if part == '-min':
                        play_start = int( line_parts[i + 1] )
                    if part == '-max':
                        play_end = int( line_parts[i + 1] )
                    if part == '-ast':
                        all_start = int( line_parts[i + 1] )
                    if part == '-aet':
                        all_end = int( line_parts[i + 1] )
                    i = i + 1
                # print play_start
                # print play_end
                # print all_start
                # print all_end
                cmds.playbackOptions( animationStartTime = all_start )
                cmds.playbackOptions( animationEndTime = all_end )
                if handles:
                    cmds.playbackOptions( minTime = play_start + handles )
                    cmds.playbackOptions( maxTime = play_end - handles )
                else:
                    cmds.playbackOptions( minTime = play_start )
                    cmds.playbackOptions( maxTime = play_end )
        inFile.close()
        return None
    else:
        print( 'Not a file:  ' + path )
        # print 'not a directory'

