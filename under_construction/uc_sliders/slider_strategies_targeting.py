# -*- coding: utf-8 -*-

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np


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
                return linear_value, current_value + delta

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

                return negative_tangents, positive_tangents

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
        """Calculate bezier-based value for blending using direct solving"""
        try:
            current_idx = self.core.get_curve_data( curve ).key_map[time]

            # Get selected keys
            selected_keys = self.core.get_selected_keys( curve )

            # Get curve data
            curve_data = self.core.get_curve_data( curve )
            all_keys = curve_data.keys
            all_values = curve_data.values
            tangent_data = curve_data.tangents
            using_weighted_tangents = curve_data.is_weighted

            # Find surrounding non-selected keys
            prev_key = next( ( i for i in range( current_idx - 1, -1, -1 )
                           if all_keys[i] not in selected_keys ), None )
            next_key = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                           if all_keys[i] not in selected_keys ), None )

            if prev_key is not None and next_key is not None:
                # Get points
                p0 = [all_keys[prev_key], all_values[prev_key]]
                p3 = [all_keys[next_key], all_values[next_key]]

                # Get time gap
                gap = p3[0] - p0[0]
                mltp = 1.0 / 3.0  # Same as original code

                # Get tangent data
                prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
                prev_out_weight = tangent_data['out_weights'][prev_key]
                next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
                next_in_weight = tangent_data['in_weights'][next_key]

                # Calculate control points using trig
                # P1
                adj = gap * mltp
                opo = math.tan( prev_out_angle ) * adj
                if using_weighted_tangents:
                    opo *= prev_out_weight
                p1 = [p0[0] + adj, p0[1] + opo]

                # P2
                opo = math.tan( next_in_angle ) * adj
                if using_weighted_tangents:
                    opo *= next_in_weight
                p2 = [p3[0] - adj, p3[1] - opo]

                # Calculate t directly from x (current_time)
                # x = (1-t)³p0x + 3(1-t)²tp1x + 3(1-t)t²p2x + t³p3x
                # Normalize t to 0-1 range
                t = ( time - p0[0] ) / gap

                # Calculate y value using t
                mt = 1.0 - t
                mt2 = mt * mt
                mt3 = mt2 * mt
                t2 = t * t
                t3 = t2 * t

                bezier_value = ( p0[1] * mt3 +
                              3.0 * p1[1] * mt2 * t +
                              3.0 * p2[1] * mt * t2 +
                              p3[1] * t3 )

                # Calculate blend targets
                current_value = all_values[current_idx]
                delta = bezier_value - current_value
                return bezier_value, current_value - delta

            return all_values[current_idx], all_values[current_idx]

        except Exception as e:
            print( "Error in spline target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        """Calculate tangents matching reference implementation exactly"""
        current_idx = self.core.get_curve_data( curve ).key_map[time]

        if not self.core.get_curve_data( curve ).tangents:
            return None, None

        # Get curve data
        curve_data = self.core.get_curve_data( curve )
        all_keys = curve_data.keys
        all_values = curve_data.values
        tangent_data = curve_data.tangents
        using_weighted_tangents = curve_data.is_weighted

        # Get selected keys
        selected_keys = self.core.get_selected_keys( curve )

        # Find surrounding non-selected keys
        prev_key = next( ( i for i in range( current_idx - 1, -1, -1 )
                       if all_keys[i] not in selected_keys ), None )
        next_key = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                       if all_keys[i] not in selected_keys ), None )

        if prev_key is not None and next_key is not None:
            # Get points
            p0 = [all_keys[prev_key], all_values[prev_key]]
            p3 = [all_keys[next_key], all_values[next_key]]

            # Get gap and multiplier
            gap = p3[0] - p0[0]
            mltp = 1.0 / 3.0

            # Get tangent data
            prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
            prev_out_weight = tangent_data['out_weights'][prev_key]
            next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
            next_in_weight = tangent_data['in_weights'][next_key]

            # Calculate control points just like getControlPoints
            adj = gap * mltp

            # P1 calculation
            opo = math.tan( prev_out_angle ) * adj
            if using_weighted_tangents:
                opo *= prev_out_weight
            p1 = [p0[0] + adj, p0[1] + opo]

            # P2 calculation
            opo = math.tan( next_in_angle ) * adj
            if using_weighted_tangents:
                opo *= next_in_weight
            p2 = [p3[0] - adj, p3[1] - opo]

            # Calculate t for current time
            t = ( time - p0[0] ) / gap
            mt = 1.0 - t

            # Get points exactly like getPoint function
            # First level
            AB_x = ( mt * p0[0] ) + ( t * p1[0] )
            AB_y = ( mt * p0[1] ) + ( t * p1[1] )

            BC_x = ( mt * p1[0] ) + ( t * p2[0] )
            BC_y = ( mt * p1[1] ) + ( t * p2[1] )

            CD_x = ( mt * p2[0] ) + ( t * p3[0] )
            CD_y = ( mt * p2[1] ) + ( t * p3[1] )

            # Second level - exactly like reference
            tan_in_x = ( mt * AB_x ) + ( t * BC_x )
            tan_in_y = ( mt * AB_y ) + ( t * BC_y )

            tan_out_x = ( mt * BC_x ) + ( t * CD_x )
            tan_out_y = ( mt * BC_y ) + ( t * CD_y )

            # Final point
            point_x = ( mt * tan_in_x ) + ( t * tan_out_x )
            point_y = ( mt * tan_in_y ) + ( t * tan_out_y )

            # Calculate tangent angles exactly like getPointTangents
            # In tangent
            xlength = point_x - tan_in_x
            ylength = point_y - tan_in_y
            tan = ylength / xlength
            in_angle = math.degrees( math.atan( tan ) )
            in_length = math.sqrt( xlength * xlength + ylength * ylength )

            # Out tangent
            xlength = tan_out_x - point_x
            ylength = tan_out_y - point_y
            tan = ylength / xlength
            out_angle = math.degrees( math.atan( tan ) )
            out_length = math.sqrt( xlength * xlength + ylength * ylength )

            # Clamp weights to Maya's range
            in_length = min( max( in_length, 0.1 ), 10.0 )
            out_length = min( max( out_length, 0.1 ), 10.0 )

            # Build tangent targets
            negative_tangents = {
                'in': ( in_angle, in_length ),
                'out': ( out_angle, out_length )
            }

            # For positive (exaggerate), calculate delta from current angles
            curr_in_angle = tangent_data['in_angles'][current_idx]
            curr_out_angle = tangent_data['out_angles'][current_idx]

            in_delta = in_angle - curr_in_angle
            out_delta = out_angle - curr_out_angle

            positive_tangents = {
                'in': ( curr_in_angle - in_delta, in_length ),
                'out': ( curr_out_angle - out_delta, out_length )
            }

            return negative_tangents, positive_tangents

        return None, None

    def _bezier_value( self, t, p0, p1, p2, p3 ):
        """Calculate point on standard bezier curve"""
        mt = 1.0 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t

        return ( mt3 * p0[1] +
                3.0 * mt2 * t * p1[1] +
                3.0 * mt * t2 * p2[1] +
                t3 * p3[1] )

    def _rational_bezier_value( self, t, p0, p1, p2, p3, w0, w1, w2, w3 ):
        """Calculate point on rational bezier curve"""
        mt = 1.0 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t

        num = ( mt3 * w0 * p0[1] +
               3.0 * mt2 * t * w1 * p1[1] +
               3.0 * mt * t2 * w2 * p2[1] +
               t3 * w3 * p3[1] )

        den = ( mt3 * w0 +
               3.0 * mt2 * t * w1 +
               3.0 * mt * t2 * w2 +
               t3 * w3 )

        return num / den if den != 0 else p0[1]

    def _calculate_weighted_tangent( self, t, p0, p_curr, p3, angle1, angle2, scale ):
        """Calculate tangent vector for weighted tangents"""
        # Calculate direction vectors
        dir1 = np.array( [math.cos( angle1 ), math.sin( angle1 )] )
        dir2 = np.array( [math.cos( angle2 ), math.sin( angle2 )] )

        # Blend directions based on parameter
        blend_dir = dir1 * ( 1.0 - t ) + dir2 * t
        blend_dir = blend_dir / np.linalg.norm( blend_dir )

        # Scale tangent
        return blend_dir * scale

    def _calculate_standard_tangent( self, t, p0, p_curr, p3, angle1, angle2, scale ):
        """Calculate tangent vector for standard tangents"""
        # Calculate directions
        dir1 = np.array( [math.cos( angle1 ), math.sin( angle1 )] )
        dir2 = np.array( [math.cos( angle2 ), math.sin( angle2 )] )

        # Calculate tangent
        tangent = dir1 * ( 1.0 - t ) + dir2 * t
        length = np.linalg.norm( tangent )

        if length > 0:
            tangent = tangent / length * scale

        return tangent
