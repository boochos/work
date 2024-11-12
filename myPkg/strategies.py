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
