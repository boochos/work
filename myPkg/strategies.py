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
    """Blend strategy using cubic bezier spline interpolation to match Maya's behavior"""

    def __init__( self ):
        self._cached_curves = {}
        self._cached_controls = {}

    def reset( self ):
        """Clear any cached data"""
        self._cached_curves.clear()
        self._cached_controls.clear()

    def calculate_target_value( self, current_time, current_value, curve_data, blend_info ):
        """Calculate bezier-based value for blending using direct solving"""
        current_idx = curve_data['key_map'].get( current_time )

        # Get selected keys
        selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

        # Get curve data
        all_keys = curve_data['keys']
        all_values = curve_data['values']
        tangent_data = curve_data['tangents']
        using_weighted_tangents = curve_data['is_weighted']

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

            print( "Debug - weights:" )
            print( "prev_out_weight:", prev_out_weight )
            print( "next_in_weight:", next_in_weight )

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
            t = ( current_time - p0[0] ) / gap

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

            # Print debug info
            print( "Debug - Control Points:" )
            print( "P0:", p0 )
            print( "P1:", p1 )
            print( "P2:", p2 )
            print( "P3:", p3 )
            print( "t value:", t )

            # Calculate blend targets
            delta = bezier_value - current_value
            return bezier_value, current_value - delta

        return current_value, current_value

    def calculate_target_value__( self, current_time, current_value, curve_data, blend_info ):
            """Calculate bezier-based value for blending with weighted tangent support"""
            current_idx = curve_data['key_map'].get( current_time )

            # Get selected keys
            selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

            # Get curve data
            all_keys = curve_data['keys']
            all_values = curve_data['values']
            tangent_data = curve_data['tangents']
            using_weighted_tangents = curve_data['is_weighted']

            # Find surrounding non-selected keys
            prev_key = next( ( i for i in range( current_idx - 1, -1, -1 )
                            if all_keys[i] not in selected_keys ), None )
            next_key = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                            if all_keys[i] not in selected_keys ), None )

            if prev_key is not None and next_key is not None:
                # Get points for bezier calculation
                p0 = np.array( [all_keys[prev_key], all_values[prev_key]] )
                p3 = np.array( [all_keys[next_key], all_values[next_key]] )

                # Calculate time and value scales
                time_scale = p3[0] - p0[0]
                value_scale = p3[1] - p0[1]

                # Store original values for denormalization
                normalize_scale = abs( value_scale )
                original_p0_val = p0[1]

                # Normalize the values for calculation
                norm_p0_val = 0.0
                norm_p3_val = 1.0 if value_scale > 0 else -1.0  # Preserve direction

                print( "Debug - Pre-normalization Values:" )
                print( "P0 original:", p0[1] )
                print( "P3 original:", p3[1] )
                print( "Value scale:", value_scale )
                print( "Normalize scale:", normalize_scale )

                # Get tangent data
                prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
                prev_out_weight = tangent_data['out_weights'][prev_key]
                next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
                next_in_weight = tangent_data['in_weights'][next_key]

                # Normalize both scales
                norm_time_scale = time_scale / abs( value_scale )  # This makes time scale relative to value scale
                x_scale = norm_time_scale / 3.0

                # Calculate normalized offsets
                # Calculate normalized offsets
                if using_weighted_tangents:
                    # Scale the tangent influence relative to normalized space
                    y1_offset = 2.0 * math.tan( prev_out_angle ) / 3.0 * abs( norm_p3_val )
                    y2_offset = 2.0 * math.tan( next_in_angle ) / 3.0 * abs( norm_p3_val )

                    # Apply weights
                    y1_offset *= prev_out_weight
                    y2_offset *= next_in_weight
                else:
                    y1_offset = 2.0 * math.tan( prev_out_angle ) / 3.0 * abs( norm_p3_val )
                    y2_offset = 2.0 * math.tan( next_in_angle ) / 3.0 * abs( norm_p3_val )

                # Calculate control points in normalized space
                p1 = np.array( [
                    p0[0] + x_scale,
                    norm_p0_val + y1_offset
                ] )

                p2 = np.array( [
                    p3[0] - x_scale,
                    norm_p3_val - y2_offset
                ] )

                print( "Debug - Normalized Control Points:" )
                print( "P0 norm:", norm_p0_val )
                print( "P1 norm:", p1[1] )
                print( "P2 norm:", p2[1] )
                print( "P3 norm:", norm_p3_val )

                # Calculate parameter t
                t = ( current_time - p0[0] ) / time_scale

                # Print debug info
                print( "Debug - Original Values: {0} -> {1}".format( p0[1], p3[1] ) )
                print( "Debug - Normalized Values: {0} -> {1}".format( norm_p0_val, norm_p3_val ) )
                print( "Debug - Scale: {0}".format( normalize_scale ) )
                print( "Debug - Control Points (Normalized):" )
                print( "P0: [{0}, {1}]".format( p0[0], norm_p0_val ) )
                print( "P1: {0}".format( p1 ) )
                print( "P2: {0}".format( p2 ) )
                print( "P3: [{0}, {1}]".format( p3[0], norm_p3_val ) )

                # Calculate bezier value using optimized Bernstein basis
                mt = 1.0 - t
                mt2 = mt * mt
                mt3 = mt2 * mt
                t2 = t * t
                t3 = t2 * t

                bezier_value = ( norm_p0_val * mt3 +
                               3.0 * p1[1] * mt2 * t +
                               3.0 * p2[1] * mt * t2 +
                               norm_p3_val * t3 )

                # Denormalize the result
                bezier_value = bezier_value * normalize_scale + original_p0_val

                # Calculate blend targets
                delta = bezier_value - current_value
                return bezier_value, current_value - delta

            return current_value, current_value

    def calculate_target_tangents( self, current_time, curve_data, blend_info ):
            """Calculate tangents matching reference implementation exactly"""
            current_idx = curve_data['key_map'].get( current_time )

            if not curve_data.get( 'tangents' ):
                return None, None

            # Get curve data
            all_keys = curve_data['keys']
            all_values = curve_data['values']
            tangent_data = curve_data['tangents']
            using_weighted_tangents = curve_data['is_weighted']

            # Get selected keys
            selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

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
                t = ( current_time - p0[0] ) / gap
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

                print( "Debug Control Points:" )
                print( "P0:", p0 )
                print( "P1:", p1 )
                print( "P2:", p2 )
                print( "P3:", p3 )

                print( "Debug Intermediate:" )
                print( "AB:", [AB_x, AB_y] )
                print( "BC:", [BC_x, BC_y] )
                print( "CD:", [CD_x, CD_y] )

                print( "Debug Final Points:" )
                print( "Tan In:", [tan_in_x, tan_in_y] )
                print( "Point:", [point_x, point_y] )
                print( "Tan Out:", [tan_out_x, tan_out_y] )

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

                print( "Debug Angles:" )
                print( "In angle:", in_angle )
                print( "Out angle:", out_angle )
                print( "In length:", in_length )
                print( "Out length:", out_length )

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

    def calculate_target_tangents__( self, current_time, curve_data, blend_info ):
            """Calculate bezier-based tangents matching Maya's behavior"""
            current_idx = curve_data['key_map'].get( current_time )

            if not curve_data.get( 'tangents' ):
                return None, None

            # Get curve data
            all_keys = curve_data['keys']
            all_values = curve_data['values']
            tangent_data = curve_data['tangents']
            using_weighted_tangents = curve_data['is_weighted']

            # Get current value from curve data
            current_value = curve_data['values'][current_idx]

            # Get current tangents
            curr_in_angle = tangent_data['in_angles'][current_idx]
            curr_out_angle = tangent_data['out_angles'][current_idx]
            curr_in_weight = tangent_data['in_weights'][current_idx]
            curr_out_weight = tangent_data['out_weights'][current_idx]

            # Get selected keys
            selected_keys = cmds.keyframe( blend_info['curve'], q = True, sl = True, tc = True ) or []

            # Find surrounding non-selected keys
            prev_key = next( ( i for i in range( current_idx - 1, -1, -1 )
                            if all_keys[i] not in selected_keys ), None )
            next_key = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                            if all_keys[i] not in selected_keys ), None )

            if prev_key is not None and next_key is not None:
                # Get points for bezier calculation
                p0 = np.array( [all_keys[prev_key], all_values[prev_key]] )
                p3 = np.array( [all_keys[next_key], all_values[next_key]] )

                # Calculate time and value scales
                time_scale = p3[0] - p0[0]
                value_scale = p3[1] - p0[1]

                # Get tangent data
                prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
                prev_out_weight = tangent_data['out_weights'][prev_key]
                next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
                next_in_weight = tangent_data['in_weights'][next_key]

                # Calculate control points using same logic as value calculation
                x_scale = time_scale / 3.0

                if using_weighted_tangents:
                    y1_offset = 2.0 * value_scale * math.tan( prev_out_angle ) / 3.0 * prev_out_weight
                    y2_offset = 2.0 * value_scale * math.tan( next_in_angle ) / 3.0 * next_in_weight
                else:
                    y1_offset = 2.0 * value_scale * math.tan( prev_out_angle ) / 3.0
                    y2_offset = 2.0 * value_scale * math.tan( next_in_angle ) / 3.0

                # Calculate control points
                p1 = np.array( [p0[0] + x_scale, p0[1] + y1_offset] )
                p2 = np.array( [p3[0] - x_scale, p3[1] - y2_offset] )

                # Calculate tangent at the modified key (t=0.5)
                t = 0.5  # Since we want the tangent at the middle key

                # Calculate tangent vector using derivative of bezier curve
                mt = 1.0 - t
                tangent_vector = np.array( [
                    3.0 * mt * mt * ( p1[0] - p0[0] ) +
                    6.0 * mt * t * ( p2[0] - p1[0] ) +
                    3.0 * t * t * ( p3[0] - p2[0] ),
                    3.0 * mt * mt * ( p1[1] - p0[1] ) +
                    6.0 * mt * t * ( p2[1] - p1[1] ) +
                    3.0 * t * t * ( p3[1] - p2[1] )
                ] )

                # Calculate angle from tangent vector
                spline_angle = math.degrees( math.atan2( tangent_vector[1], tangent_vector[0] ) )

                # Calculate weight based on angle
                weight = abs( value_scale ) * 2.0 / 3.0
                weight = min( max( weight, 0.1 ), 10.0 )

                '''
                print( "Debug Tangent - Input angle: {0}".format( math.degrees( prev_out_angle ) ) )
                print( "Debug Tangent - Calculated angle: {0}".format( spline_angle ) )
                print( "Debug Tangent - Control points:" )
                print( "P0:", p0 )
                print( "P1:", p1 )
                print( "P2:", p2 )
                print( "P3:", p3 )
                '''
                # Build tangent targets
                negative_tangents = {
                    'in': ( spline_angle, weight ),
                    'out': ( spline_angle, weight )
                }

                # For positive (exaggerate), calculate delta from current angles
                in_delta = spline_angle - curr_in_angle
                out_delta = spline_angle - curr_out_angle

                positive_tangents = {
                    'in': ( curr_in_angle - in_delta, weight ),
                    'out': ( curr_out_angle - out_delta, weight )
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


class SplineBlendStrategy___( BlendStrategy ):

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

        # Check if curve uses weighted tangents
        curve_name = blend_info['curve']
        using_weighted_tangents = curve_data['is_weighted']
        # print( "\nDebug Value Calculation - Using weighted tangents: {0}".format( using_weighted_tangents ) )

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
            x_scale = time_scale / 3.0
            y_scale = time_scale / 3.0

            # Previous key's out tangent
            prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
            prev_out_weight = tangent_data['out_weights'][prev_key]

            # Next key's in tangent
            next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
            next_in_weight = tangent_data['in_weights'][next_key]

            # print( "Debug Value - Prev out weight: {0}".format( prev_out_weight ) )
            # print( "Debug Value - Next in weight: {0}".format( next_in_weight ) )

            # Calculate control points differently based on curve type
            if using_weighted_tangents:
                # Try new weighted calculation
                x_scale = time_scale / 3.0
                y_scale = time_scale / 3.0

                p1 = np.array( [
                    p0[0] + x_scale * math.cos( prev_out_angle ),  # No weight on x
                    p0[1] + y_scale * math.sin( prev_out_angle ) * prev_out_weight  # Single weight
                ] )

                p2 = np.array( [
                    p3[0] - x_scale * math.cos( next_in_angle ),  # No weight on x
                    p3[1] - y_scale * math.sin( next_in_angle ) * next_in_weight  # Single weight
                ] )
            else:
                # Original calculation for non-weighted curves
                x_scale = time_scale / 3.0
                p1 = np.array( [
                    p0[0] + x_scale * math.cos( prev_out_angle ) * prev_out_weight,
                    p0[1] + x_scale * math.sin( prev_out_angle ) * prev_out_weight
                ] )

                p2 = np.array( [
                    p3[0] - x_scale * math.cos( next_in_angle ) * next_in_weight,
                    p3[1] - x_scale * math.sin( next_in_angle ) * next_in_weight
                ] )

            # Calculate parameter t
            t = ( current_time - p0[0] ) / time_scale

            # Calculate the bezier value
            bezier_value = self._rational_bezier_curve( t, p0, p1, p2, p3 )[1]  # for non weighted curves
            # bezier_value = self._rational_bezier_curve( t, p0, p1, p2, p3, 1.0, prev_out_weight, next_in_weight, 1.0 )[1]  # Added weights here

            # print( "Debug Value - t parameter: {0}".format( t ) )
            # print( "Debug Value - Current value: {0}".format( current_value ) )
            # print( "Debug Value - Calculated bezier value: {0}".format( bezier_value ) )

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

        # Check if curve uses weighted tangents
        curve_name = blend_info['curve']
        using_weighted_tangents = cmds.keyTangent( curve_name, q = True, weightedTangents = True )
        # print( "Debug - Using weighted tangents: {0}".format( using_weighted_tangents ) )

        # Get current tangent angles
        curr_in_angle = tangent_data['in_angles'][current_idx]
        curr_out_angle = tangent_data['out_angles'][current_idx]

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
            # Get points for bezier calculation - using the outer keys
            p0 = np.array( [all_keys[prev_key], all_values[prev_key]] )
            p3 = np.array( [all_keys[next_key], all_values[next_key]] )

            # Get the outer key tangents to define the overall curve shape
            time_scale = p3[0] - p0[0]
            x_scale = time_scale / 3.0

            # Use the outer keys' tangents
            prev_out_angle = math.radians( tangent_data['out_angles'][prev_key] )
            prev_out_weight = tangent_data['out_weights'][prev_key]
            next_in_angle = math.radians( tangent_data['in_angles'][next_key] )
            next_in_weight = tangent_data['in_weights'][next_key]

            # print( "Debug - Prev out weight: {0}".format( prev_out_weight ) )
            # print( "Debug - Next in weight: {0}".format( next_in_weight ) )

            # Calculate control points based on outer key tangents
            p1 = np.array( [
                p0[0] + x_scale * math.cos( prev_out_angle ) * prev_out_weight,
                p0[1] + x_scale * math.sin( prev_out_angle ) * prev_out_weight
            ] )

            p2 = np.array( [
                p3[0] - x_scale * math.cos( next_in_angle ) * next_in_weight,
                p3[1] - x_scale * math.sin( next_in_angle ) * next_in_weight
            ] )

            # Calculate parameter t for current key's position along the overall curve
            t = ( current_time - p0[0] ) / time_scale

            # Calculate tangent vector at this point on the curve
            tangent = self._weighted_bezier_tangent( t, p0, p1, p2, p3 )

            # Calculate spline-based angle and weight
            spline_angle = math.atan2( tangent[1], tangent[0] ) * 180.0 / math.pi
            if using_weighted_tangents:
                # print( "Debug - Calculating weighted tangent" )
                weight = np.linalg.norm( tangent ) / time_scale  # We'll modify this for weighted tangents
            else:
                weight = np.linalg.norm( tangent ) / time_scale

            # print( "Debug - Calculated weight: {0}".format( weight ) )

            # Calculate delta from current angles
            in_delta = spline_angle - curr_in_angle
            out_delta = spline_angle - curr_out_angle

            # For negative: use spline angles (towards curve)
            negative_tangents = {
                'in': ( spline_angle, weight ),
                'out': ( spline_angle, weight )
            }

            # For positive: exaggerate away from spline angles
            positive_tangents = {
                'in': ( curr_in_angle - in_delta, weight ),  # Opposite direction
                'out': ( curr_out_angle - out_delta, weight )  # Opposite direction
            }

            return negative_tangents, positive_tangents

        return None, None

    def _calculate_control_point( self, base_point, angle, weight, x_scale, y_scale, is_out = True ):
        """Calculate control point with balanced scaling and preserved direction"""
        direction = 1 if is_out else -1
        tangent_vector = np.array( [
            direction * x_scale * math.cos( angle ),
            direction * y_scale * math.sin( angle )
        ] )
        # Normalize and apply weight
        length = np.linalg.norm( tangent_vector )
        if length > 0:
            tangent_vector = ( tangent_vector / length ) * weight
        return base_point + tangent_vector

    def _rational_bezier_curve( self, t, p0, p1, p2, p3, w0 = 1.0, w1 = 1.0, w2 = 1.0, w3 = 1.0 ):
        """Compute point on rational bezier curve"""
        mltp = 1.0
        p0_w = p0 * w0
        p1_w = p1 * ( w1 * mltp )
        p2_w = p2 * ( w2 * mltp )
        p3_w = p3 * w3

        mt = 1 - t
        # denominator = ( ( 1 - t ) ** 3 * w0 + 3 * ( 1 - t ) ** 2 * t * w1 + 3 * ( 1 - t ) * t ** 2 * w2 + t ** 3 * w3 )
        # numerator = ( ( 1 - t ) ** 3 * p0_w + 3 * ( 1 - t ) ** 2 * t * p1_w + 3 * ( 1 - t ) * t ** 2 * p2_w + t ** 3 * p3_w )

        denominator = ( mt ** 3 * w0 + 3 * mt ** 2 * t * w1 + 3 * mt * t ** 2 * w2 + t ** 3 * w3 )
        numerator = ( mt ** 3 * p0_w + 3 * mt ** 2 * t * p1_w + 3 * mt * t ** 2 * p2_w + t ** 3 * p3_w )

        return numerator / denominator

    def _bezier_tangent( self, t, p0, p1, p2, p3 ):
        # More stable calculation using Horner's method
        mt = 1 - t

        # Calculate coefficients
        c3 = 3.0 * ( p1 - p0 )
        c2 = 3.0 * ( p2 - p1 ) - c3
        c1 = p3 - p0 - c3 - c2

        # Evaluate derivative
        return ( 3 * c1 * t * t +
                2 * c2 * t +
                c3 )

    def _weighted_bezier_tangent( self, t, p0, p1, p2, p3, w0 = 1.0, w1 = 1.0, w2 = 1.0, w3 = 1.0 ):
        """Compute tangent on weighted Bézier curve."""
        # Apply weights to control points
        p0_w = p0 * w0
        p1_w = p1 * w1
        p2_w = p2 * w2
        p3_w = p3 * w3

        mt = 1 - t

        # Calculate coefficients with weighted control points
        c3 = 3.0 * ( p1_w - p0_w )
        c2 = 3.0 * ( p2_w - p1_w ) - c3
        c1 = p3_w - p0_w - c3 - c2

        # Evaluate derivative (tangent)
        tangent = ( 3 * c1 * t * t +
                   2 * c2 * t +
                   c3 )

        # Normalize the tangent if needed
        tangent = tangent / np.linalg.norm( tangent )

        return tangent

    def _bezier_tangent___( self, t, p0, p1, p2, p3 ):
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
