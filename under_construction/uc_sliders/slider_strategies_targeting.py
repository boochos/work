# -*- coding: utf-8 -*-

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np

# TODO: add support for weighted tangents, investigate tangent weight issues when targeting


class TargetStrategy:
    """Base class for targeting strategies"""

    def __init__( self, core ):
        self.core = core

    def calculate_target_value( self, curve, time ):
        """
        Calculate target values for a curve at given time
        Returns:
        tuple: (previous_target, next_target)
        """
        raise NotImplementedError

    def calculate_target_tangents( self, curve, time ):
        """
        Calculate target tangents for a curve at given time
        Returns:
        tuple: (previous_tangents, next_tangents)
        """
        raise NotImplementedError

    def reset( self ):
        """Reset any stored state"""
        pass


class DirectTargetStrategy( TargetStrategy ):
    """Blend directly to prev/next non-selected keys"""

    def calculate_target_value( self, curve, time ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )
            selected_keys = self.core.get_selected_keys( curve )

            # Start with current value as default targets
            current_value = curve_data.get_value( current_idx )
            prev_target = next_target = current_value

            # Find previous non-selected key
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    prev_target = curve_data.values[i]
                    break

            # Find next non-selected key
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    next_target = curve_data.values[i]
                    break

            return prev_target, next_target

        except Exception as e:
            print( "Error in direct target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        """Use flat tangents (0 angle) as targets"""
        flat_tangents = {
            'in': ( 0.0, 1.0 ),
            'out': ( 0.0, 1.0 )
        }
        return flat_tangents, flat_tangents


class LinearTargetStrategy( TargetStrategy ):
    """Blend towards or away from linear interpolation"""

    def calculate_target_value( self, curve, time ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )
            selected_keys = self.core.get_selected_keys( curve )

            current_value = curve_data.get_value( current_idx )

            # Find surrounding non-selected keys
            prev_idx = next_idx = None
            prev_time = prev_value = None
            next_time = next_value = None

            # Find previous non-selected key
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    prev_idx = i
                    prev_time = curve_data.keys[i]
                    prev_value = curve_data.values[i]
                    break

            # Find next non-selected key
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    next_idx = i
                    next_time = curve_data.keys[i]
                    next_value = curve_data.values[i]
                    break

            # Calculate targets if we found both surrounding keys
            if prev_idx is not None and next_idx is not None:
                # Calculate linear interpolation
                time_ratio = ( time - prev_time ) / ( next_time - prev_time )
                linear_value = prev_value + ( next_value - prev_value ) * time_ratio

                # Calculate delta from linear
                delta = current_value - linear_value

                # For negative (towards linear), use linear value
                # For positive (away from linear), exaggerate from linear
                '''
                # this doesnt work for this strategy, in its current state, relic from direct methodology
                return linear_value, current_value + delta
                '''
                return linear_value, linear_value

            return current_value, current_value

        except Exception as e:
            print( "Error in linear target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )
            selected_keys = self.core.get_selected_keys( curve )

            # Find surrounding non-selected keys
            prev_idx = next_idx = None
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    prev_idx = i
                    break
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    next_idx = i
                    break

            if prev_idx is not None and next_idx is not None:
                # Calculate angle of linear path
                dx = curve_data.keys[next_idx] - curve_data.keys[prev_idx]
                dy = curve_data.values[next_idx] - curve_data.values[prev_idx]
                linear_angle = math.degrees( math.atan2( dy, dx ) )

                # Get current tangent angles
                curr_in_angle = curve_data.tangents['in_angles'][current_idx]
                curr_out_angle = curve_data.tangents['out_angles'][current_idx]

                # Calculate angle differences from linear
                in_diff = curr_in_angle - linear_angle
                out_diff = curr_out_angle - linear_angle

                # Calculate targets
                negative_tangents = {
                    'in': ( linear_angle, 1.0 ),
                    'out': ( linear_angle, 1.0 )
                }

                positive_tangents = {
                    'in': ( curr_in_angle + in_diff, 1.0 ),
                    'out': ( curr_out_angle + out_diff, 1.0 )
                }
                # TODO: relic from direct methodology, both should be the same, likely only one should be returned, its causing issues in blending
                # return negative_tangents, positive_tangents
                return negative_tangents, negative_tangents

            # Fallback to current tangents
            current_tangents = {
                'in': ( curve_data.tangents['in_angles'][current_idx],
                      curve_data.tangents['in_weights'][current_idx] ),
                'out': ( curve_data.tangents['out_angles'][current_idx],
                       curve_data.tangents['out_weights'][current_idx] )
            }

            return current_tangents, current_tangents

        except Exception as e:
            print( "Error in linear tangent calculation: {0}".format( e ) )
            return None, None


class SplineTargetStrategy( TargetStrategy ):
    """Uses cubic bezier spline interpolation"""

    def __init__( self, core ):
        TargetStrategy.__init__( self, core )  # Python 2.7 style
        self._cached_curves = {}
        self._cached_controls = {}

    def calculate_target_value( self, curve, time ):
        """Calculate bezier-based value for blending"""
        try:
            current_idx = self.core.get_curve_data( curve ).key_map[time]

            prev_key, next_key = self._find_anchor_keys( curve, current_idx )
            if prev_key is not None and next_key is not None:
                curve_data, p0, p3 = self._get_curve_points( curve, prev_key, next_key )
                p1, p2, gap = self._calculate_control_points( curve_data, p0, p3, prev_key, next_key )

                '''
                print( "P0: time={0}, value={1}".format( p0[0], p0[1] ) )
                print( "P1: time={0}, value={1}".format( p1[0], p1[1] ) )
                print( "P2: time={0}, value={1}".format( p2[0], p2[1] ) )
                print( "P3: time={0}, value={1}".format( p3[0], p3[1] ) )

                print( "p0=({0}, {1})".format( p0[0], p0[1] ) )
                print( "p1=({0}, {1})".format( p1[0], p1[1] ) )
                print( "p2=({0},{1})".format( p2[0], p2[1] ) )
                print( "p3=({0}, {1})".format( p3[0], p3[1] ) )
                '''
                # Calculate t parameter and bezier value
                t = ( time - p0[0] ) / gap
                mt = 1.0 - t
                mt2 = mt * mt
                mt3 = mt2 * mt
                t2 = t * t
                t3 = t2 * t

                bezier_value = ( p0[1] * mt3 +
                              3.0 * p1[1] * mt2 * t +
                              3.0 * p2[1] * mt * t2 +
                              p3[1] * t3 )

                return bezier_value, bezier_value

            return curve_data.values[current_idx], curve_data.values[current_idx]

        except Exception as e:
            print( "Error in spline target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        """Calculate tangents for the bezier curve"""
        try:
            current_idx = self.core.get_curve_data( curve ).key_map[time]
            if not self.core.get_curve_data( curve ).tangents:
                return None, None

            prev_key, next_key = self._find_anchor_keys( curve, current_idx )
            if prev_key is not None and next_key is not None:
                curve_data, p0, p3 = self._get_curve_points( curve, prev_key, next_key )
                p1, p2, gap = self._calculate_control_points( curve_data, p0, p3, prev_key, next_key )

                # Calculate t for current time
                t = ( time - p0[0] ) / gap
                mt = 1.0 - t

                # Calculate intermediate points
                AB_x = ( mt * p0[0] ) + ( t * p1[0] )
                AB_y = ( mt * p0[1] ) + ( t * p1[1] )

                BC_x = ( mt * p1[0] ) + ( t * p2[0] )
                BC_y = ( mt * p1[1] ) + ( t * p2[1] )

                CD_x = ( mt * p2[0] ) + ( t * p3[0] )
                CD_y = ( mt * p2[1] ) + ( t * p3[1] )

                # Calculate tangent points
                tan_in_x = ( mt * AB_x ) + ( t * BC_x )
                tan_in_y = ( mt * AB_y ) + ( t * BC_y )

                tan_out_x = ( mt * BC_x ) + ( t * CD_x )
                tan_out_y = ( mt * BC_y ) + ( t * CD_y )

                point_x = ( mt * tan_in_x ) + ( t * tan_out_x )
                point_y = ( mt * tan_in_y ) + ( t * tan_out_y )

                # Calculate angles and lengths
                xlength = point_x - tan_in_x
                ylength = point_y - tan_in_y
                tan = ylength / xlength
                in_angle = math.degrees( math.atan( tan ) )
                in_length = math.sqrt( xlength * xlength + ylength * ylength )

                xlength = tan_out_x - point_x
                ylength = tan_out_y - point_y
                tan = ylength / xlength
                out_angle = math.degrees( math.atan( tan ) )
                out_length = math.sqrt( xlength * xlength + ylength * ylength )

                # Clamp weights
                in_length = min( max( in_length, 0.1 ), 10.0 )
                out_length = min( max( out_length, 0.1 ), 10.0 )
                '''
                print( "\nTarget Tangent Calculation:" )
                print( "In Angle: {:.3f}".format( in_angle ) )
                print( "Out Angle: {:.3f}".format( out_angle ) )
                print( "In Weight: {:.3f}".format( in_length ) )
                print( "Out Weight: {:.3f}".format( out_length ) )
                '''
                negative_tangents = {
                    'in': ( in_angle, in_length ),
                    'out': ( out_angle, out_length )
                }

                return negative_tangents, negative_tangents

            return None, None

        except Exception as e:
            print( "Error calculating tangents: {0}".format( e ) )
            return None, None

    def _find_anchor_keys( self, curve, current_idx ):
        """Find surrounding non-selected keys to use as anchors"""
        curve_data = self.core.get_curve_data( curve )
        all_keys = curve_data.keys
        selected_keys = self.core.get_selected_keys( curve )

        prev_key = next( ( i for i in range( current_idx - 1, -1, -1 )
                      if all_keys[i] not in selected_keys ), None )
        next_key = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                      if all_keys[i] not in selected_keys ), None )

        return prev_key, next_key

    def _get_curve_points( self, curve, prev_key, next_key ):
        """Get anchor points and curve data"""
        curve_data = self.core.get_curve_data( curve )
        p0 = [curve_data.keys[prev_key], curve_data.values[prev_key]]
        p3 = [curve_data.keys[next_key], curve_data.values[next_key]]

        return ( curve_data, p0, p3 )

    def _calculate_control_points( self, curve_data, p0, p3, prev_key, next_key ):
        """Calculate bezier control points P1 and P2"""
        """
        # TODO: below values relate to position of their associated key, x value is x*8, y value is y*(1/3.0)
        # use this to get control points
        print(cmds.getAttr(curve_node + ".keyTanInX[0]"))
        print(cmds.getAttr(curve_node + ".keyTanInY[0]"))
        print(cmds.getAttr(curve_node + ".keyTanOutX[0]"))
        print(cmds.getAttr(curve_node + ".keyTanOutY[0]"))
        # could use this to set them or reverse engineer the math for the raw weight value, 
        # will actually need to figure out the math to set the target weight value
        cmds.keyTangent(curve_node, ox= 0.0, t=(0.0,)) 
        cmds.keyTangent(curve_node, oy= -3.0, t=(0.0,))
        
        
        """
        gap = p3[0] - p0[0]
        mltp = 1.0 / 3.0
        tangent_data = curve_data.tangents
        using_weighted_tangents = curve_data.is_weighted

        # Get tangent data
        prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
        prev_out_weight = tangent_data['out_weights'][prev_key]
        next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
        next_in_weight = tangent_data['in_weights'][next_key]

        print( "\nTangent Values:" )
        print( "prev_out_angle:", math.degrees( prev_out_angle ) )
        print( "prev_out_weight:", prev_out_weight )
        print( "next_in_angle:", math.degrees( next_in_angle ) )
        print( "next_in_weight:", next_in_weight )

        # Calculate P1
        if using_weighted_tangents:
            adj = prev_out_weight
        else:
            adj = gap * mltp
        opo = math.tan( prev_out_angle ) * adj
        p1 = [p0[0] + adj, p0[1] + opo]

        # Calculate P2
        if using_weighted_tangents:
            adj = next_in_weight
        else:
            adj = gap * mltp
        opo = math.tan( next_in_angle ) * adj
        p2 = [p3[0] - adj, p3[1] - opo]

        return p1, p2, gap
