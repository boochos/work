import json
import os

import maya.cmds as cmds
import maya.mel as mel


class PlaneTelemetry():

    def __init__( self, plane = '', cam = '', ground = '' ):
        '''
        
        '''
        self.plane = plane
        self.cam = cam
        self.ground = ground
        #
        self.path = None
        self.min = None
        self.max = None
        #
        self.distance_to_cam = 'distance_to_cam'
        self.planes_speed = 'planes_speed'
        self.planes_height = 'planes_height'
        self.camera_speed = 'camera_speed'
        self.camera_height = 'camera_height'

    def range( self ):
        self.min = cmds.playbackOptions( q = True, minTime = True )
        self.max = cmds.playbackOptions( q = True, maxTime = True )

    def path( self ):
        self.path = cmds.file( q = True, sn = True )
        self.path = self.path.rsplit( '/', 1 )[0]
