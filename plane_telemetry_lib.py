from math import sqrt
import json
import os

import maya.OpenMaya as OpenMaya
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
        self.start = None
        self.end = None
        self.current = None
        # file name
        self.plane_to_cam = 'plane_to_cam'
        self.plane_speed = 'plane_speed'
        self.plane_height = 'plane_height'
        self.cam_speed = 'cam_speed'
        self.cam_height = 'cam_height'
        self.file_names = [
            self.plane_to_cam,
            self.plane_speed,
            self.plane_height,
            self.cam_speed,
            self.cam_height
            ]
        # dict
        self.plane_to_cam_dict = {}
        self.plane_speed_dict = {}
        self.plane_height_dict = {}
        self.cam_speed_dict = {}
        self.cam_height_dict = {}
        self.dicts = [
            self.plane_to_cam_dict,
            self.plane_speed_dict,
            self.plane_height_dict,
            self.cam_speed_dict,
            self.cam_height_dict
            ]

        self.range()
        self.get_path()
        self.run()
        self.output()

    def range( self ):
        self.start = cmds.playbackOptions( q = True, minTime = True )
        self.end = cmds.playbackOptions( q = True, maxTime = True )
        self.current = self.start

    def get_path( self ):
        self.path = cmds.file( q = True, sn = True )
        self.path = self.path.rsplit( '/', 1 )[0]
        print( self.path )

    def run( self ):
        current = cmds.currentTime( q = True )
        while self.current <= self.end:
            # print( self.current )
            cmds.currentTime( self.current )
            # measure distances
            self.plane_to_cam_dict[self.current] = distance2Objs( self.plane, self.cam )
            # plane to ground, build points, amalgamate ground
            p1 = cmds.xform( self.plane, q = True, ws = True, rp = True )
            p2 = cmds.xform( self.ground, q = True, ws = True, rp = True )
            p22 = [p1[0], p2[1], p1[2]]
            d = distance2Pts( p1, p22 )
            d = round( 0.01 * d, 1 )
            self.plane_height_dict[float( self.current )] = d

            # cam to ground
            p1 = cmds.xform( self.cam, q = True, ws = True, rp = True )
            p2 = cmds.xform( self.ground, q = True, ws = True, rp = True )
            p22 = [p1[0], p2[1], p1[2]]
            d = distance2Pts( p1, p22 )
            d = round( 0.01 * d, 1 )
            self.cam_height_dict[self.current] = d
            # print( self.current, self.plane_height_dict[self.current] )

            # measure speeds
            self.plane_speed_dict[self.current] = speed( self.plane )
            self.cam_speed_dict[self.current] = speed( self.cam )
            # print( self.current, self.plane_speed_dict[self.current] )
            #
            self.current += 1

        # restore frame
        cmds.currentTime( current )

    def output( self ):
        '''
        export json files
        '''
        i = 0
        for f in self.file_names:
            f_path = os.path.join( self.path, f + '.json' )
            print( f_path )
            fileObjectJSON = open( f_path, 'w' )
            json.dump( self.dicts[i], fileObjectJSON, indent = 1 )
            fileObjectJSON.close()
            i += 1


def distance2Pts( p1, p2 ):
    '''
    
    '''
    #
    error = 0
    if len( p1 ) != 3:
        OpenMaya.MGlobal.displayError( 
            'First argument list needs to have three elements...' )
        error = 1
    if len( p2 ) != 3:
        OpenMaya.MGlobal.displayError( 
            'Second argument list needs to have three elements...' )
        error = 1

    if error != 1:
        v = [0, 0, 0]
        v[0] = p1[0] - p2[0]
        v[1] = p1[1] - p2[1]
        v[2] = p1[2] - p2[2]
        distance = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
        distance = sqrt( distance )
        return distance
    else:
        return None


def distance2Objs( obj1 = '', obj2 = '' ):
    '''
    to meters
    '''
    #
    p1 = cmds.xform( obj1, q = True, ws = True, rp = True )
    p2 = cmds.xform( obj2, q = True, ws = True, rp = True )
    d = distance2Pts( p1, p2 )
    return round( 0.01 * d, 1 )


def speed( obj = '' ):
    '''
    to kmh
    '''
    now = cmds.currentTime( q = True )
    before = now - 1
    # matrix
    p1 = cmds.getAttr( obj + '.worldMatrix', t = ( before ) )
    p2 = cmds.getAttr( obj + '.worldMatrix' )
    # pos only
    p1 = p1[-3:]
    p2 = p2[-3:]
    #
    d = distance2Pts( p1, p2 )
    return round( d * 24 * 60 * 60 / 100000, 1 )
