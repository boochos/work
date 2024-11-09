# -*- coding: utf-8 -*-

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np
import numpy as np


class BlendStrategy:
    """Base class for different blending behaviors"""

    def calculate_target_value( self, current_time, current_value, curve_data, blend_info ):
        """Calculate target values for blending"""
        raise NotImplementedError

    def calculate_target_tangents( self, current_time, curve_data, blend_info ):
        """Calculate target tangents for blending"""
        raise NotImplementedError

    def reset( self ):
        """Reset any stored state"""
        pass


class DirectKeyBlendStrategy( BlendStrategy ):
    """Blend directly to prev/next keys"""

    def calculate_target_value( self, current_time, current_value, curve_data, blend_info ):
        current_idx = curve_data['key_map'].get( current_time )

        # Get all keys on curve
        all_keys = curve_data['keys']
        if not all_keys:
            return current_value, current_value

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        # Find first non-selected key in both directions
        prev_target = current_value
        next_target = current_value

        # Look for previous non-selected key
        for i in range( current_idx - 1, -1, -1 ):
            if all_keys[i] not in selected_keys:
                prev_target = curve_data['values'][i]
                break

        # Look for next non-selected key
        for i in range( current_idx + 1, len( all_keys ) ):
            if all_keys[i] not in selected_keys:
                next_target = curve_data['values'][i]
                break

        return prev_target, next_target

    def calculate_target_tangents( self, current_time, curve_data, blend_info ):
        """Calculate target tangents, using flat tangents as blend targets"""
        if not curve_data.get( 'tangents' ):
            return None, None

        # Target is flat tangents (0 angle) for both prev and next
        flat_tangents = {
            'in': ( 0.0, 1.0 ),  # Flat angle (0) with standard weight
            'out': ( 0.0, 1.0 )
        }

        # Use flat tangents for both directions
        return flat_tangents, flat_tangents


class LinearBlendStrategy( BlendStrategy ):

    def calculate_target_value( self, current_time, current_value, curve_data, blend_info ):
        """
        Calculate targets:
        - Negative: blend towards linear interpolation
        - Positive: exaggerate away from linear interpolation
        """
        current_idx = curve_data['key_map'].get( current_time )

        # Get all keys and values
        all_keys = curve_data['keys']
        all_values = curve_data['values']
        if not all_keys:
            return current_value, current_value

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        # Find surrounding non-selected keys and their values
        prev_time = None
        prev_value = current_value
        next_time = None
        next_value = current_value

        # Look for previous non-selected key
        for i in range( current_idx - 1, -1, -1 ):
            if all_keys[i] not in selected_keys:
                prev_time = all_keys[i]
                prev_value = all_values[i]
                break

        # Look for next non-selected key
        for i in range( current_idx + 1, len( all_keys ) ):
            if all_keys[i] not in selected_keys:
                next_time = all_keys[i]
                next_value = all_values[i]
                break

        # If we found both surrounding keys
        if prev_time is not None and next_time is not None:
            # Calculate linear interpolation
            time_ratio = ( current_time - prev_time ) / ( next_time - prev_time )
            linear_value = prev_value + ( next_value - prev_value ) * time_ratio

            # For negative (towards linear), use linear value
            negative_target = linear_value

            # For positive (away from linear), exaggerate from linear
            delta_from_linear = current_value - linear_value
            positive_target = current_value + delta_from_linear  # Double the offset

            return negative_target, positive_target

        # Handle edge cases
        if prev_time is None:
            return next_value, current_value
        if next_time is None:
            return prev_value, current_value

        return current_value, current_value

    def calculate_target_tangents( self, current_time, curve_data, blend_info ):
        """Calculate target tangents based on direction"""
        if not curve_data.get( 'tangents' ):
            return None, None

        current_idx = curve_data['key_map'].get( current_time )

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        # Get all keys and values
        all_keys = curve_data['keys']
        all_values = curve_data['values']

        # Find surrounding non-selected keys
        prev_time = None
        prev_value = None
        next_time = None
        next_value = None

        # Look for previous non-selected key
        for i in range( current_idx - 1, -1, -1 ):
            if all_keys[i] not in selected_keys:
                prev_time = all_keys[i]
                prev_value = all_values[i]
                break

        # Look for next non-selected key
        for i in range( current_idx + 1, len( all_keys ) ):
            if all_keys[i] not in selected_keys:
                next_time = all_keys[i]
                next_value = all_values[i]
                break

        # If we found both keys
        if prev_time is not None and next_time is not None:
            # Calculate angle of linear path
            dx = next_time - prev_time
            dy = next_value - prev_value
            linear_angle = math.atan2( dy, dx ) * 180.0 / math.pi

            # Get current tangent angles
            tangent_data = curve_data['tangents']
            curr_in_angle = tangent_data['in_angles'][current_idx]
            curr_out_angle = tangent_data['out_angles'][current_idx]

            # Calculate angle differences from linear
            in_diff = curr_in_angle - linear_angle
            out_diff = curr_out_angle - linear_angle

            # For negative (towards linear), use linear angle
            negative_tangents = {
                'in': ( linear_angle, 1.0 ),
                'out': ( linear_angle, 1.0 )
            }

            # For positive (away from linear), exaggerate current angles
            positive_tangents = {
                'in': ( curr_in_angle + in_diff, 1.0 ),  # Double the angle difference
                'out': ( curr_out_angle + out_diff, 1.0 )
            }

            return negative_tangents, positive_tangents

        # Fallback to current tangents
        tangent_data = curve_data['tangents']
        current_tangents = {
            'in': ( tangent_data['in_angles'][current_idx],
                  tangent_data['in_weights'][current_idx] ),
            'out': ( tangent_data['out_angles'][current_idx],
                   tangent_data['out_weights'][current_idx] )
        }

        return current_tangents, current_tangents


class SplineBlendStrategy( BlendStrategy ):

    def __init__( self ):
        self._cached_curves = {}
        self._cached_controls = {}

    def reset( self ):
        """Clear any cached data"""
        self._cached_curves.clear()
        self._cached_controls.clear()

    def calculate_target_value( self, current_time, current_value, curve_data, blend_info ):
        """Calculate bezier-based value for blending with weighted tangent support"""
        current_idx = curve_data['key_map'].get( current_time )

        # Find surrounding non-selected keys
        all_keys = curve_data['keys']
        all_values = curve_data['values']
        tangent_data = curve_data['tangents']

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        prev_key = None
        next_key = None

        # Find previous non-selected key
        for i in range( current_idx - 1, -1, -1 ):
            if all_keys[i] not in selected_keys:
                prev_key = i
                break

        # Find next non-selected key
        for i in range( current_idx + 1, len( all_keys ) ):
            if all_keys[i] not in selected_keys:
                next_key = i
                break

        if prev_key is not None and next_key is not None:
            # Get points for bezier calculation
            p0 = np.array( [all_keys[prev_key], all_values[prev_key]] )
            p3 = np.array( [all_keys[next_key], all_values[next_key]] )

            time_scale = p3[0] - p0[0]

            # Previous key's out tangent
            prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
            prev_out_weight = tangent_data['out_weights'][prev_key]

            # Next key's in tangent
            next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
            next_in_weight = tangent_data['in_weights'][next_key]

            # Calculate control points using 1/3 rule but respect tangent direction
            p1 = np.array( [
                p0[0] + ( time_scale / 3.0 ) * math.cos( prev_out_angle ),
                p0[1] + ( time_scale / 3.0 ) * prev_out_weight * math.sin( prev_out_angle )
            ] )

            p2 = np.array( [
                p3[0] - ( time_scale / 3.0 ) * math.cos( next_in_angle ),
                p3[1] - ( time_scale / 3.0 ) * next_in_weight * math.sin( next_in_angle )
            ] )

            # Calculate parameter t
            t = ( current_time - p0[0] ) / time_scale
            '''
            print( "\nValue Calculation Debug:" )
            print( "P0:", p0 )
            print( "P1:", p1 )
            print( "P2:", p2 )
            print( "P3:", p3 )
            print( "Current Value:", current_value )
            print( "Current Time:", current_time )
            print( "t parameter:", t )
            '''
            # Calculate the bezier value
            bezier_value = self._rational_bezier_curve( t, p0, p1, p2, p3 )[1]  # Get y component
            '''
            print( "Calculated Bezier Value:", bezier_value )
            print( "Maya Curve Value:", cmds.keyframe( blend_info['curve'],
                                                   time = ( current_time, ),
                                                   q = True,
                                                   eval = True )[0] )
            '''
            # For negative: blend towards bezier
            # For positive: push away from bezier in opposite direction
            delta = bezier_value - current_value  # Flip the delta calculation

            negative_value = bezier_value  # Same as before
            positive_value = current_value - delta  # Now pushes away correctly

            return negative_value, positive_value

        return current_value, current_value

    def calculate_target_tangents( self, current_time, curve_data, blend_info ):
        """Calculate bezier-based tangents"""
        current_idx = curve_data['key_map'].get( current_time )
        all_keys = curve_data['keys']
        all_values = curve_data['values']
        tangent_data = curve_data['tangents']

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        # Find surrounding non-selected keys
        prev_key = None
        next_key = None

        # Find previous non-selected key
        for i in range( current_idx - 1, -1, -1 ):
            if all_keys[i] not in selected_keys:
                prev_key = i
                break

        # Find next non-selected key
        for i in range( current_idx + 1, len( all_keys ) ):
            if all_keys[i] not in selected_keys:
                next_key = i
                break

        if prev_key is not None and next_key is not None:
            # Get points for bezier calculation
            p0 = np.array( [all_keys[prev_key], all_values[prev_key]] )
            p3 = np.array( [all_keys[next_key], all_values[next_key]] )

            # Separate scales for time and value components
            time_scale = p3[0] - p0[0]
            value_scale = abs( p3[1] - p0[1] )

            x_scale = time_scale / 3.0
            y_scale = value_scale

            # Previous key's out tangent
            prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
            prev_out_weight = tangent_data['out_weights'][prev_key]

            # Next key's in tangent
            next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
            next_in_weight = tangent_data['in_weights'][next_key]

            # Calculate control points with separate scales
            p1 = np.array( [
                p0[0] + x_scale * math.cos( prev_out_angle ) * prev_out_weight,
                p0[1] + y_scale * math.sin( prev_out_angle ) * prev_out_weight
            ] )

            p2 = np.array( [
                p3[0] - x_scale * math.cos( next_in_angle ) * next_in_weight,
                p3[1] - y_scale * math.sin( next_in_angle ) * next_in_weight
            ] )

            # Calculate parameter t
            t = ( current_time - p0[0] ) / time_scale

            # Calculate tangent vector using bezier derivative
            tangent = self._bezier_tangent( t, p0, p1, p2, p3 )

            # Convert to angle and weight
            angle = math.atan2( tangent[1], tangent[0] ) * 180.0 / math.pi
            # Calculate weight (normalized by time scale)
            weight = np.linalg.norm( tangent ) / time_scale

            # Create tangents
            new_tangents = {
                'in': ( angle, weight ),
                'out': ( angle, weight )
            }

            return new_tangents, new_tangents

        return None, None

    def _rational_bezier_curve( self, t, p0, p1, p2, p3, w0 = 1.0, w1 = 1.0, w2 = 1.0, w3 = 1.0 ):
        """Compute point on rational bezier curve"""
        p0_w = p0 * w0
        p1_w = p1 * w1
        p2_w = p2 * w2
        p3_w = p3 * w3

        denominator = ( ( 1 - t ) ** 3 * w0 +
                      3 * ( 1 - t ) ** 2 * t * w1 +
                      3 * ( 1 - t ) * t ** 2 * w2 +
                      t ** 3 * w3 )

        numerator = ( ( 1 - t ) ** 3 * p0_w +
                    3 * ( 1 - t ) ** 2 * t * p1_w +
                    3 * ( 1 - t ) * t ** 2 * p2_w +
                    t ** 3 * p3_w )

        return numerator / denominator

    def _bezier_tangent( self, t, p0, p1, p2, p3 ):
        """Compute tangent vector at point t"""
        # Print debug info
        # print( "\nBezier Derivative Calculation:" )
        # First term: 3(1-t)²(p1-p0)
        term1 = 3 * ( 1 - t ) ** 2 * ( p1 - p0 )
        # print( "Term 1:", term1 )

        # Second term: 6(1-t)(t)(p2-p1)
        term2 = 6 * ( 1 - t ) * t * ( p2 - p1 )
        # print( "Term 2:", term2 )

        # Third term: 3t²(p3-p2)
        term3 = 3 * t ** 2 * ( p3 - p2 )
        # print( "Term 3:", term3 )

        # Total derivative
        derivative = term1 + term2 + term3
        return derivative

        '''
        # Derivative of cubic bezier
        t2 = t * t
        mt = 1 - t
        mt2 = mt * mt

        # Calculate tangent vector
        tangent = 3 * mt2 * ( p1 - p0 ) + \
                 6 * mt * t * ( p2 - p1 ) + \
                 3 * t2 * ( p3 - p2 )

        return tangent
        '''
