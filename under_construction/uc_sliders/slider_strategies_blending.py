# -*- coding: utf-8 -*-
"""
Provides blending strategies for animation curve manipulation.
Handles interpolation of values and tangents between animation states.
"""
# TODO: add support to blend broken tangents individually
# TODO: add support for weighted tangents, investigate issues when blending
import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np


class BlendStrategy( object ):
    """Base class for blending behaviors"""

    def __init__( self, core ):
        self.core = core
        self.uses_signed_blend = False  # Default behavior

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """
        Calculate blended values and tangents
        Returns:
        tuple: (blended_value, blended_tangents)
        """
        raise NotImplementedError

    def reset( self ):
        """Reset any stored state"""
        pass

    def _blend_angles( self, start, end, ratio ):
        """
        Blend between angles taking shortest path
        Args:
            start (float): Starting angle in degrees
            end (float): Ending angle in degrees
            ratio (float): Blend ratio (0-1)
        Returns:
            float: Blended angle value
        """
        # Calculate angle difference handling wrap-around
        diff = end - start
        if abs( diff ) > 180:
            if diff > 0:
                end -= 360
            else:
                end += 360

        # Linear interpolation
        result = start * ( 1 - ratio ) + end * ratio

        # Normalize result to 0-360 range
        while result < 0:
            result += 360
        while result >= 360:
            result -= 360

        return result


class RateBasedBlendStrategy( BlendStrategy ):
    """Blends using rate curve based on distance from target"""

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            # Calculate rate based on distance
            distance = abs( target_value - current_value )
            rate = self._rate_curve( distance )

            # Apply rate to blend
            if blend_factor == 1.0:
                eased_ratio = blend_factor
            else:
                eased_ratio = blend_factor * rate / 89.5

            # Calculate blended value
            new_value = current_value * ( 1 - eased_ratio ) + target_value * eased_ratio

            # Calculate blended tangents
            new_tangents = None
            if target_tangents:
                new_tangents = self._blend_tangents( curve, current_idx, target_tangents, eased_ratio )

            return new_value, new_tangents

        except Exception as e:
            print( "Error in rate-based blending: {0}".format( e ) )
            return current_value, None

    def _rate_curve( self, distance, power = 50 ):
        """Calculate rate based on distance from target"""
        x = min( distance / 6561.0, 1.0 )  # Normalize distance
        return np.power( 1 - x, power ) * 89.5

    def _blend_tangents( self, curve, current_idx, target_tangents, ratio ):
        try:
            curve_data = self.core.get_curve_data( curve )
            curr_tangents = curve_data.tangents

            # Blend angles
            in_angle = self._blend_angles( 
                curr_tangents['in_angles'][current_idx],
                target_tangents['in'][0],
                ratio
            )
            out_angle = self._blend_angles( 
                curr_tangents['out_angles'][current_idx],
                target_tangents['out'][0],
                ratio
            )

            # Blend weights
            in_weight = curr_tangents['in_weights'][current_idx] * ( 1 - ratio ) + target_tangents['in'][1] * ratio
            out_weight = curr_tangents['out_weights'][current_idx] * ( 1 - ratio ) + target_tangents['out'][1] * ratio

            return {
                'in': ( in_angle, in_weight ),
                'out': ( out_angle, out_weight )
            }

        except Exception as e:
            print( "Error blending tangents: {0}".format( e ) )
            return None


class LinearBlendStrategy( BlendStrategy ):
    """Simple linear interpolation between values"""

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            # Linear value blend
            new_value = current_value * ( 1 - blend_factor ) + target_value * blend_factor

            # Linear tangent blend if available
            new_tangents = None
            if target_tangents:
                new_tangents = self._blend_tangents( curve, current_idx, target_tangents, blend_factor )

            return new_value, new_tangents

        except Exception as e:
            print( "Error in linear blending: {0}", format( e ) )
            return current_value, None

    def _blend_tangents( self, curve, current_idx, target_tangents, ratio ):
        try:
            curve_data = self.core.get_curve_data( curve )
            curr_tangents = curve_data.tangents

            # Simple linear interpolation for angles and weights
            in_angle = self._blend_angles( 
                curr_tangents['in_angles'][current_idx],
                target_tangents['in'][0],
                ratio
            )
            out_angle = self._blend_angles( 
                curr_tangents['out_angles'][current_idx],
                target_tangents['out'][0],
                ratio
            )

            in_weight = curr_tangents['in_weights'][current_idx] * ( 1 - ratio ) + target_tangents['in'][1] * ratio
            out_weight = curr_tangents['out_weights'][current_idx] * ( 1 - ratio ) + target_tangents['out'][1] * ratio

            return {
                'in': ( in_angle, in_weight ),
                'out': ( out_angle, out_weight )
            }

        except Exception as e:
            print( "Error blending tangents: {0}".format( e ) )
            return None

'''
class GeometricBlendStrategy__( BlendStrategy ):
    """Uses geometric relationships for blending"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = False
        self.uses_signed_blend = True  # Uses signed blend factor

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]

            # Get running value instead of using passed in current_value
            running_value = curve_data.get_running_value( current_idx )

            # Point C - current position
            # Point A is at current time but target value
            target_time = current_time  # A and C share same x position

            # Get anchor key (B) based on blend direction
            selected_keys = self.core.get_selected_keys( curve )
            anchor_idx = None

            if blend_factor >= 0:
                # Find next unselected key
                for i in range( current_idx + 1, len( curve_data.keys ) ):
                    if curve_data.keys[i] not in selected_keys:
                        anchor_idx = i
                        break
            else:
                # Find previous unselected key
                for i in range( current_idx - 1, -1, -1 ):
                    if curve_data.keys[i] not in selected_keys:
                        anchor_idx = i
                        break

            # If we can't find an unselected key, fallback to next/prev
            if anchor_idx is None:
                if blend_factor >= 0:
                    anchor_idx = curve_data.next_indices[current_time]
                else:
                    anchor_idx = curve_data.prev_indices[current_time]

            # Get B position from anchor
            ref_time = curve_data.keys[anchor_idx]
            ref_value = curve_data.values[anchor_idx]

            if self.debug:
                print( "Triangle: A(right angle)=({0}, {1}), B(anchor)=({2}, {3}), C(running)=({4}, {5}), ratio={6}".format( 
                    current_time, target_value,  # Point A
                    ref_time, ref_value,  # Point B (anchor)
                    current_time, running_value,  # Point C
                    blend_factor
                ) )

            # Calculate angle at B
            opposite = abs( running_value - target_value )  # Vertical distance C to A
            adjacent = abs( ref_time - current_time )  # Horizontal distance B to A
            raw_angle = math.degrees( math.atan( opposite / adjacent ) )

            # Get start angle and determine angle direction
            start_angle = curve_data.tangents['in_angles'][current_idx]
            angle_at_B = -raw_angle if start_angle < 0 else raw_angle

            # Query current angle for blending
            current_angle = curve_data.tangents['in_angles'][current_idx]

            merge_mult = abs( blend_factor )

            # Override angles if at full blend
            if merge_mult >= 1.0:
                in_angle = target_tangents['in'][0]
                out_angle = target_tangents['out'][0]
            else:
                # Blend between start angle and calculated angle
                in_angle = start_angle * ( 1.0 - merge_mult ) + angle_at_B * merge_mult
                out_angle = start_angle * ( 1.0 - merge_mult ) + angle_at_B * merge_mult

            if self.debug:
                print( "Angles: target={0:.2f}, reference={1:.2f}, current={2:.2f}, start={3:.2f}, diff={4:.2f}, merge_mult={5:.2f}, ratio={6:.2f}{7}".format( 
                    target_tangents['in'][0],  # Target angle
                    angle_at_B,  # Calculated reference angle
                    current_angle,  # Current angle
                    start_angle,  # Original angle
                    current_angle - angle_at_B,  # Difference from reference
                    merge_mult,  # Blend multiplier
                    blend_factor,  # Original ratio
                    " (OVERRIDE)" if merge_mult >= 1.0 else ""
                ) )

            # Linear blend now using running value instead of current_value
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult
            print( "Point B x/y: ({0}, {1}), in_angle: {2}, Start Angle: {3}, Current Angle: {4}, new value: {5}".format( ref_time, ref_value, in_angle, start_angle, current_angle, new_value ) )

            # Update running state
            curve_data.update_running_state( current_idx, new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            } )

            # Return the new values
            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None
            '''


class ContractingBlendStrategy( BlendStrategy ):
    """Uses geometric relationships between points A, B, C for blending"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (current_time, target_value)
        B: Anchor point (projected from C's angle)
        C: Current point (current_time, current_value)
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, current_value, running_value, target_value )

            # Get point B by projecting C's angle to A's y-value
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time, current_value, target_value, blend_factor )
            self._log_anchor_info( point_b )

            # Get angle at C and calculate new position
            angle_c = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( angle_c )

            moving_c_value = self._calculate_point_c_position( current_value, target_value, blend_factor )
            print( moving_c_value, running_value )
            # moving_c_value = running_value
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, current_value,
                point_b['time'], point_b['value'],
                moving_c_value, angle_c
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, angle_c, current_value, moving_c_value, point_b['value'] )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['final_angle'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value, target_value, blend_factor ):
        """Project from C using start_angle to find intersection with A's y-value"""
        MIN_DELTA = 0.001

        # Get angle at point C
        angle_c = math.radians( curve_data.tangents['in_angles'][current_idx] )

        # Calculate delta_y from C to A's y-value
        vertical_distance_c_to_a = abs( target_value - current_value )
        if vertical_distance_c_to_a < MIN_DELTA:
            vertical_distance_c_to_a = MIN_DELTA

        if abs( angle_c ) < math.radians( 0.1 ):
            angle_c = math.radians( 0.1 ) * ( 1 if angle_c >= 0 else -1 )

        horizontal_distance_c_to_b = vertical_distance_c_to_a / math.tan( abs( angle_c ) )
        point_b_time = point_c_time - horizontal_distance_c_to_b
        point_b_value = target_value  # B shares same y-value as A

        if self.debug:
            print( "\n=== Point B Projection ===" )
            print( "Point C - Time: {0}, Value: {1}".format( point_c_time, current_value ) )
            print( "Target Value (A,B y-value): {0}".format( target_value ) )
            print( "Angle C: {0}".format( math.degrees( angle_c ) ) )
            print( "C to A Vertical Distance: {0}".format( vertical_distance_c_to_a ) )
            print( "C to B Horizontal Distance: {0}".format( horizontal_distance_c_to_b ) )
            print( "Point B - Time: {0}, Value: {1}".format( point_b_time, point_b_value ) )

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_c ):
        """Calculate geometric relationships between points A, B, and C"""
        # Initial triangle calculations
        initial_opposite = abs( value_c - value_b )
        initial_adjacent = abs( time_c - time_b )
        initial_raw = math.degrees( math.atan( initial_opposite / initial_adjacent ) )

        # Scale factor calculation
        scale_factor = abs( angle_c / initial_raw ) if initial_raw != 0 else 1.0

        # New triangle calculations
        opposite = abs( moving_c_value - value_b )
        adjacent = abs( time_c - time_b )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': scale_factor,
            'opposite': opposite,
            'adjacent': adjacent
        }

    def _calculate_abc_angles( self, triangle_abc, angle_c, value_c, moving_c_value, value_b ):
        """Calculate angles based on geometric relationships between A, B, and C"""
        raw_angle = math.degrees( math.atan( 
            triangle_abc['opposite'] / triangle_abc['adjacent']
        ) ) if triangle_abc['adjacent'] != 0 else 90.0

        scaled_angle = raw_angle * triangle_abc['scale_factor']

        # Check if we crossed point B's value
        started_above_b = value_c >= value_b
        ended_above_b = moving_c_value >= value_b

        if started_above_b != ended_above_b:
            scaled_angle = -scaled_angle

        final_angle = -scaled_angle if angle_c < 0 else scaled_angle

        return {
            'raw_angle': raw_angle,
            'scaled_angle': scaled_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    # Logging methods
    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( point_c_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Anchor Point Info ===" )
            print( "Time: {0}".format( point_b['time'] ) )
            print( "Value: {0}".format( point_b['value'] ) )

    def _log_angle_info( self, angle_c ):
        if self.debug:
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( angle_c ) )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( moving_c_value ) )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( triangle_abc['opposite'] ) )
            print( "Adjacent (horizontal): {0}".format( triangle_abc['adjacent'] ) )
            print( "Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle (before scale/sign): {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final In/Out Angle: {0}".format( angles['final_angle'] ) )

    def _log_final_result( self, moving_c_value, final_angle ):
        if self.debug:
            print( "\n=== Result ===" )
            print( "New Value: {0}".format( moving_c_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "================\n" )


class ExpandingBlendStrategy( BlendStrategy ):
    """
    Blend strategy using geometric relationships between points A, B, C where:
    A: Target point (target_time, target_value)
    B: Intersection point of A's angle with C's y-value
    C: Current point (current_time, current_value)
    
    Unlike ContractingBlendStrategy, this maintains the target angle rather than 
    flattening to zero by constructing B at C's height using A's angle.
    """

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, current_value, running_value, target_value )

            # Get initial angle from curve data
            current_angle = curve_data.tangents['in_angles'][current_idx]
            target_angle = target_tangents['in'][0]

            # Get point B by projecting A's angle to C's y-value
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time,
                                       current_value, target_value, target_tangents )
            self._log_anchor_info( point_b )

            self._log_angle_info( target_angle )

            # Calculate new position for C based on blend factor
            moving_c_value = self._calculate_point_c_position( current_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Blend between current and target angle
            blend_factor_abs = abs( blend_factor )
            blended_angle = current_angle * ( 1.0 - blend_factor_abs ) + target_angle * blend_factor_abs

            tangents = {
                'in': ( blended_angle, target_tangents['in'][1] ),
                'out': ( blended_angle, target_tangents['out'][1] )
            }

            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, blended_angle )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric4 blending: {0}".format( str( e ) ) )
            return current_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value,
                     target_value, target_tangents ):
        """Project from A using target angle to find intersection with C's y-value"""
        try:
            MIN_DELTA = 0.001

            # Get angle from target/point A
            angle_a = math.radians( target_tangents['in'][0] )

            # Calculate delta_y from A down to C's y-value
            vertical_distance_a_to_c = abs( target_value - current_value )
            if vertical_distance_a_to_c < MIN_DELTA:
                vertical_distance_a_to_c = MIN_DELTA

            # Ensure we have a valid angle to work with
            if abs( angle_a ) < math.radians( 0.1 ):
                angle_a = math.radians( 0.1 ) * ( 1 if angle_a >= 0 else -1 )

            # Project from A to find B at C's height using angle_a
            horizontal_distance_a_to_b = vertical_distance_a_to_c / math.tan( abs( angle_a ) )

            # Determine direction based on angle sign
            if angle_a < 0:
                horizontal_distance_a_to_b = -horizontal_distance_a_to_b

            # B shares C's y-value but is offset horizontally
            point_b_time = point_c_time - horizontal_distance_a_to_b  # Changed to subtract
            point_b_value = current_value  # B matches C's value

            if self.debug:
                print( "\n=== Point B Projection ===" )
                print( "Starting Configuration:" )
                print( "  C - Time: {0}, Value: {1}".format( point_c_time, current_value ) )
                print( "  A - Target Value: {0}".format( target_value ) )
                print( "  A's Angle: {0}".format( math.degrees( angle_a ) ) )
                print( "Projection Calculations:" )
                print( "  Vertical Distance (A to C): {0}".format( vertical_distance_a_to_c ) )
                print( "  Horizontal Distance (A to B): {0}".format( horizontal_distance_a_to_b ) )
                print( "Resulting Point B:" )
                print( "  Time: {0}".format( point_b_time ) )
                print( "  Value: {0}".format( point_b_value ) )

            return {
                'time': point_b_time,
                'value': point_b_value
            }

        except Exception as e:
            print( "Error in _find_point_b: {0}".format( str( e ) ) )
            raise

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_a ):
        """Calculate geometric relationships based on A's angle projection"""
        # Initial triangle calculations using A's angle
        initial_opposite = abs( value_c - value_b )  # Should be 0 as they share y-value
        initial_adjacent = abs( time_c - time_b )
        initial_raw = math.degrees( math.atan( initial_opposite / initial_adjacent ) ) if initial_adjacent != 0 else 90.0

        # Scale factor based on A's angle
        scale_factor = abs( angle_a / initial_raw ) if initial_raw != 0 else 1.0

        # New triangle calculations as C moves towards A
        opposite = abs( moving_c_value - value_b )
        adjacent = abs( time_c - time_b )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': scale_factor,
            'opposite': opposite,
            'adjacent': adjacent
        }

    def _calculate_abc_angles( self, triangle_abc, angle_a, value_c, moving_c_value, value_b ):
        """Calculate angles maintaining A's angle relationship"""
        raw_angle = math.degrees( math.atan( 
            triangle_abc['opposite'] / triangle_abc['adjacent']
        ) ) if triangle_abc['adjacent'] != 0 else 90.0

        scaled_angle = raw_angle * triangle_abc['scale_factor']

        # Since B and C share y-value initially, we mainly care about direction relative to A
        started_below_a = value_c <= value_b
        ended_below_a = moving_c_value <= value_b

        if started_below_a != ended_below_a:
            scaled_angle = -scaled_angle

        final_angle = -scaled_angle if angle_a < 0 else scaled_angle

        return {
            'raw_angle': raw_angle,
            'scaled_angle': scaled_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time: {0}".format( point_b['time'] ) )
            print( "B Value: {0}".format( point_b['value'] ) )
            print( "Note: B shares y-value with C" )

    def _log_angle_info( self, angle_a ):
        if self.debug:
            print( "\n=== Target Angle Info ===" )
            print( "A's Angle: {0}".format( angle_a ) )
            print( "Note: This angle will be maintained through blend" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while maintaining angle relationship" )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Initial State:" )
            print( "  Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc['initial_opposite'] ) )
            print( "  Adjacent (B-C horizontal): {0}".format( 
                triangle_abc['initial_adjacent'] ) )
            print( "Current State:" )
            print( "  Opposite (moving): {0}".format( triangle_abc['opposite'] ) )
            print( "  Adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Note: Triangle formed by B at C's level" )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Raw Angle: {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final Angle: {0}".format( angles['final_angle'] ) )
            print( "Note: Maintaining angle relationship from A" )

    def _log_final_result( self, moving_c_value, final_angle ):
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "Note: Non-zero final angle preserved from A's angle" )
            print( "================\n" )

    def _log_point_b_projection( self, point_c_time, current_value, target_value,
                              angle_a_deg, vert_dist, horz_dist, point_b_time, point_b_value ):
        if self.debug:
            print( "\n=== Point B Projection Details ===" )
            print( "Starting Point C:" )
            print( "  Time: {0}".format( point_c_time ) )
            print( "  Value: {0}".format( current_value ) )
            print( "Target Point A:" )
            print( "  Value: {0}".format( target_value ) )
            print( "Projection:" )
            print( "  A's Angle (degrees): {0}".format( angle_a_deg ) )
            print( "  Vertical Distance (A to C): {0}".format( vert_dist ) )
            print( "  Horizontal Distance (A to B): {0}".format( horz_dist ) )
            print( "Resulting Point B:" )
            print( "  Time: {0}".format( point_b_time ) )
            print( "  Value: {0}".format( point_b_value ) )
            print( "  Note: B created at C's height using A's angle" )


def __DEV_STRATEGIES__():
    pass


class GeometricBlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = True
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( current_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

            # Get anchor key (B) based on blend direction
            selected_keys = self.core.get_selected_keys( curve )
            anchor_idx = None

            if blend_factor >= 0:
                # Find next unselected key
                for i in range( current_idx + 1, len( curve_data.keys ) ):
                    if curve_data.keys[i] not in selected_keys:
                        anchor_idx = i
                        break
            else:
                # Find previous unselected key
                for i in range( current_idx - 1, -1, -1 ):
                    if curve_data.keys[i] not in selected_keys:
                        anchor_idx = i
                        break

            # If we can't find an unselected key, fallback to next/prev
            if anchor_idx is None:
                if blend_factor >= 0:
                    anchor_idx = curve_data.next_indices[current_time]
                else:
                    anchor_idx = curve_data.prev_indices[current_time]

            # Get B position from anchor
            ref_time = curve_data.keys[anchor_idx]
            ref_value = curve_data.values[anchor_idx]

            print( "\n=== Anchor Point Info ===" )
            print( "Anchor Index: {0}".format( anchor_idx ) )
            print( "Reference Time: {0}".format( ref_time ) )
            print( "Reference Value: {0}".format( ref_value ) )

            # Get start angle for direction
            start_angle = curve_data.tangents['in_angles'][current_idx]
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( start_angle ) )

            # Calculate new position based on blend factor
            merge_mult = abs( blend_factor )
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult

            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( new_value ) )

            # Calculate initial triangle to get our scale factor
            initial_opposite = abs( current_value - ref_value )
            initial_adjacent = abs( ref_time - current_time )
            initial_raw = math.degrees( math.atan( initial_opposite / initial_adjacent ) )

            # Scale factor to maintain relationship with start angle
            scale_factor = abs( start_angle / initial_raw )

            # Calculate current triangle
            opposite = abs( new_value - ref_value )
            adjacent = abs( ref_time - current_time )

            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( opposite ) )
            print( "Adjacent (horizontal): {0}".format( adjacent ) )
            print( "Scale Factor: {0}".format( scale_factor ) )

            # Calculate raw angle and scale it
            raw_angle = math.degrees( math.atan( opposite / adjacent ) )
            scaled_angle = raw_angle * scale_factor

            # Preserve sign from start angle
            in_angle = -scaled_angle if start_angle < 0 else scaled_angle
            out_angle = in_angle

            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle (before scale/sign): {0}".format( raw_angle ) )
            print( "Scaled Angle: {0}".format( scaled_angle ) )
            print( "Final In/Out Angle: {0}".format( in_angle ) )

            # Update running state
            curve_data.update_running_state( current_idx, new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            } )

            print( "\n=== Result ===" )
            print( "New Value: {0}".format( new_value ) )
            print( "Final Angle: {0}".format( in_angle ) )
            print( "================\n" )

            # Return the new values
            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

'''
class ___ContractingBlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending with projected point B"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = True
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( current_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

            # Get start angle for direction
            start_angle = curve_data.tangents['in_angles'][current_idx]
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( start_angle ) )

            # Get reference value (where horizontal line is)
            if blend_factor >= 0:
                next_idx = curve_data.next_indices[current_time]
                ref_value = curve_data.values[next_idx]
            else:
                prev_idx = curve_data.prev_indices[current_time]
                ref_value = curve_data.values[prev_idx]

            # Calculate where point B should be:
            # Given angle and vertical distance, calculate horizontal distance
            angle_rad = math.radians( abs( start_angle ) )
            vertical_dist = abs( running_value - ref_value )
            horizontal_dist = vertical_dist / math.tan( angle_rad )

            # Calculate ref_time based on direction
            if start_angle < 0:
                ref_time = current_time - horizontal_dist
            else:
                ref_time = current_time + horizontal_dist

            print( "\n=== Projected Point B Info ===" )
            print( "Reference Time: {0}".format( ref_time ) )
            print( "Reference Value: {0}".format( ref_value ) )

            # Calculate new position based on blend factor
            merge_mult = abs( blend_factor )
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult

            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( new_value ) )

            # Calculate geometric angle between points
            opposite = abs( new_value - ref_value )
            adjacent = abs( ref_time - current_time )

            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( opposite ) )
            print( "Adjacent (horizontal): {0}".format( adjacent ) )

            # Calculate raw angle and preserve sign
            raw_angle = math.degrees( math.atan( opposite / adjacent ) )
            in_angle = -raw_angle if start_angle < 0 else raw_angle
            out_angle = in_angle

            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle (before sign): {0}".format( raw_angle ) )
            print( "Final In/Out Angle: {0}".format( in_angle ) )

            # Update running state
            curve_data.update_running_state( current_idx, new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            } )

            print( "\n=== Result ===" )
            print( "New Value: {0}".format( new_value ) )
            print( "Final Angle: {0}".format( in_angle ) )
            print( "================\n" )

            # Return the new values
            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None
            '''

'''
class ExpandingBlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending, expanding from point A"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = True
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( current_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

            # Point A is at (current_time, current_value)
            # Final C position will be at (current_time, target_value)
            # Need to find Point B using target tangent projection

            # Convert target tangent angle to radians
            target_angle = target_tangents['in'][0]
            target_angle_rad = math.radians( target_angle )
            print( "\n=== Target Angle Info ===" )
            print( "Target Angle: {0}".format( target_angle ) )

            # Calculate where point B should be:
            # Project from final C position (current_time, target_value) down to current_value
            vertical_dist = abs( target_value - current_value )
            horizontal_dist = vertical_dist / math.tan( abs( target_angle_rad ) )

            # Calculate ref_time (B's x position) based on target angle direction
            if target_angle < 0:
                ref_time = current_time - horizontal_dist
            else:
                ref_time = current_time + horizontal_dist

            # B is at (ref_time, current_value)
            print( "\n=== Point B Info ===" )
            print( "B Position - Time: {0}, Value: {1}".format( ref_time, current_value ) )

            # Calculate new position for C
            merge_mult = abs( blend_factor )
            # C moves from A's position (current_value) to target_value
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult

            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( new_value ) )

            # Calculate current triangle geometry
            opposite = abs( new_value - current_value )  # Height from A to current C position
            adjacent = abs( ref_time - current_time )  # Width from A to B

            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( opposite ) )
            print( "Adjacent (horizontal): {0}".format( adjacent ) )

            # Calculate current angle
            if adjacent != 0:
                raw_angle = math.degrees( math.atan( opposite / adjacent ) )
                # Preserve target angle sign
                in_angle = -raw_angle if target_angle < 0 else raw_angle
            else:
                in_angle = 0
            out_angle = in_angle

            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle: {0}".format( raw_angle ) )
            print( "Final In/Out Angle: {0}".format( in_angle ) )

            # Update running state
            curve_data.update_running_state( current_idx, new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            } )

            print( "\n=== Result ===" )
            print( "New Value: {0}".format( new_value ) )
            print( "Final Angle: {0}".format( in_angle ) )
            print( "================\n" )

            # Return the new values
            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

'''

'''
class ___ExpandingBlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending, expanding from point A"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = True
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( current_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

            # Get start angle
            start_angle = curve_data.tangents['in_angles'][current_idx]

            # Convert target tangent angle to radians
            target_angle = target_tangents['in'][0]
            target_angle_rad = math.radians( target_angle )
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( start_angle ) )
            print( "Target Angle: {0}".format( target_angle ) )

            # Calculate where point B should be based on target tangent projection
            vertical_dist = abs( target_value - current_value )
            horizontal_dist = vertical_dist / math.tan( abs( target_angle_rad ) )

            # Calculate ref_time based on target angle direction
            if target_angle < 0:
                ref_time = current_time - horizontal_dist
            else:
                ref_time = current_time + horizontal_dist

            print( "\n=== Point B Info ===" )
            print( "B Position - Time: {0}, Value: {1}".format( ref_time, current_value ) )

            # Calculate new position for C
            merge_mult = abs( blend_factor )
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult

            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( new_value ) )

            # Calculate current triangle geometry
            opposite = abs( new_value - current_value )
            adjacent = abs( ref_time - current_time )

            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( opposite ) )
            print( "Adjacent (horizontal): {0}".format( adjacent ) )

            # For angle blending:
            # If start_angle and target_angle have same sign or start_angle is 0,
            # blend directly between them
            if ( start_angle * target_angle >= 0 ) or start_angle == 0:
                in_angle = start_angle * ( 1 - merge_mult ) + target_angle * merge_mult
            else:
                # If they have opposite signs, gradually reduce start_angle to 0 first,
                # then grow towards target
                if merge_mult < 0.5:
                    # First half: reduce to zero
                    in_angle = start_angle * ( 1 - merge_mult * 2 )
                else:
                    # Second half: grow to target
                    scaled_mult = ( merge_mult - 0.5 ) * 2
                    in_angle = target_angle * scaled_mult

            out_angle = in_angle

            print( "\n=== Final Angle Calculation ===" )
            print( "In/Out Angle: {0}".format( in_angle ) )

            # Update running state
            curve_data.update_running_state( current_idx, new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            } )

            print( "\n=== Result ===" )
            print( "New Value: {0}".format( new_value ) )
            print( "Final Angle: {0}".format( in_angle ) )
            print( "================\n" )

            # Return the new values
            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None
            '''


class Geometric2BlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending with flexible point B selection"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """Main entry point for blending values"""
        try:
            # Get curve data and initial state
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )
            self._log_initial_state( blend_factor, current_time, current_value, running_value, target_value )

            # Get point B directly as time/value pair
            # In blend_values method, change:
            anchor_data = self._get_projected_point_b( curve, curve_data, current_idx, current_time, current_value, target_value, blend_factor )
            self._log_anchor_info( anchor_data )

            # Get start angle and calculate new position
            start_angle = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( start_angle )

            new_value = self._calculate_blended_position( current_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), new_value )

            # Calculate geometric relationships and angles
            geometry_data = self._calculate_geometric_relationships( 
                current_time, current_value,
                anchor_data['time'], anchor_data['value'],
                new_value, start_angle
            )
            self._log_geometry_data( geometry_data )

            angles = self._calculate_final_angles( geometry_data, start_angle, current_value, new_value, anchor_data['value'] )
            self._log_angle_calculation( angles )

            # Update state and prepare result
            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, new_value, tangents )
            self._log_final_result( new_value, angles['final_angle'] )

            return new_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

    def _get_projected_point_b( self, curve, curve_data, current_idx, current_time, current_value, target_value, blend_factor ):
        """Project from C using start_angle to find intersection with A's y-value"""
        MIN_DELTA = 0.001

        # Point C's angle (start_angle)
        angle_c = math.radians( curve_data.tangents['in_angles'][current_idx] )

        # Starting at Point C (current_time, running_value)
        # Need to intersect with y = target_value
        # Using angle_c to project

        # Calculate delta_y from C to the target value line
        delta_y = abs( target_value - current_value )
        if delta_y < MIN_DELTA:
            delta_y = MIN_DELTA

        # Using the angle, calculate how far along x we need to go
        # tan(angle) = opposite/adjacent
        # adjacent = opposite/tan(angle)
        if abs( angle_c ) < math.radians( 0.1 ):
            angle_c = math.radians( 0.1 ) * ( 1 if angle_c >= 0 else -1 )

        delta_x = delta_y / math.tan( abs( angle_c ) )

        # Set B's x position based on the intersection
        ref_time = current_time - delta_x  # Default placement to the left

        if self.debug:
            print( "\n=== Point B Projection ===" )
            print( "Point C - Current Time: {0}".format( current_time ) )
            print( "Point C - Current Value: {0}".format( current_value ) )
            print( "Point A - Target Value: {0}".format( target_value ) )
            print( "Projection Angle: {0}".format( math.degrees( angle_c ) ) )
            print( "Delta Y to target: {0}".format( delta_y ) )
            print( "Delta X to intersection: {0}".format( delta_x ) )
            print( "B Reference Time: {0}".format( ref_time ) )

        return {
            'time': ref_time,
            'value': target_value  # B shares y-value with A
        }

    def _get_point_b( self, curve, curve_data, current_idx, current_time, current_value, target_value, blend_factor ):
        """Find anchor point B and return its time and value directly"""
        selected_keys = self.core.get_selected_keys( curve )
        anchor_idx = None

        if blend_factor >= 0:
            # Find next unselected key
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    anchor_idx = i
                    break
        else:
            # Find previous unselected key
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    anchor_idx = i
                    break

        # If we can't find an unselected key, fallback to next/prev
        if anchor_idx is None:
            if blend_factor >= 0:
                anchor_idx = curve_data.next_indices[curve_data.keys[current_idx]]
            else:
                anchor_idx = curve_data.prev_indices[curve_data.keys[current_idx]]

        # Return time/value directly instead of index
        return {
            'time': curve_data.keys[anchor_idx],
            'value': curve_data.values[anchor_idx]
        }

    def _calculate_blended_position( self, current_value, target_value, blend_factor ):
        """Calculate new position based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_geometric_relationships( self, current_time, current_value,
                                        ref_time, ref_value, new_value, start_angle ):
        """Calculate all geometric relationships between points"""
        # Initial triangle calculations
        initial_opposite = abs( current_value - ref_value )
        initial_adjacent = abs( ref_time - current_time )
        initial_raw = math.degrees( math.atan( initial_opposite / initial_adjacent ) )

        # Scale factor calculation
        scale_factor = abs( start_angle / initial_raw ) if initial_raw != 0 else 1.0

        # New triangle calculations
        opposite = abs( new_value - ref_value )
        adjacent = abs( ref_time - current_time )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': scale_factor,
            'opposite': opposite,
            'adjacent': adjacent
        }

    def _calculate_final_angles( self, geometry_data, start_angle, current_value, new_value, anchor_value ):
        """Calculate final angles based on geometric relationships"""
        raw_angle = math.degrees( math.atan( 
            geometry_data['opposite'] / geometry_data['adjacent']
        ) ) if geometry_data['adjacent'] != 0 else 90.0

        scaled_angle = raw_angle * geometry_data['scale_factor']

        # Simple check if we crossed the anchor
        started_above = current_value >= anchor_value
        ended_above = new_value >= anchor_value

        # If we crossed sides, flip the sign
        if started_above != ended_above:
            scaled_angle = -scaled_angle

        # Then apply the original angle's sign
        final_angle = -scaled_angle if start_angle < 0 else scaled_angle

        return {
            'raw_angle': raw_angle,
            'scaled_angle': scaled_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, new_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, new_value, tangents )

    # Logging methods
    def _log_initial_state( self, blend_factor, current_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Current Time: {0}".format( current_time ) )
            print( "Current Value: {0}".format( current_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value: {0}".format( target_value ) )

    def _log_anchor_info( self, anchor_data ):
        if self.debug:
            print( "\n=== Anchor Point Info ===" )
            print( "Time: {0}".format( anchor_data['time'] ) )
            print( "Value: {0}".format( anchor_data['value'] ) )

    def _log_angle_info( self, start_angle ):
        if self.debug:
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( start_angle ) )

    def _log_position_calculation( self, merge_mult, new_value ):
        if self.debug:
            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( new_value ) )

    def _log_geometry_data( self, geometry_data ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( geometry_data['opposite'] ) )
            print( "Adjacent (horizontal): {0}".format( geometry_data['adjacent'] ) )
            print( "Scale Factor: {0}".format( geometry_data['scale_factor'] ) )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle (before scale/sign): {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final In/Out Angle: {0}".format( angles['final_angle'] ) )

    def _log_final_result( self, new_value, final_angle ):
        if self.debug:
            print( "\n=== Result ===" )
            print( "New Value: {0}".format( new_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "================\n" )


class Geometric3BlendStrategy( BlendStrategy ):
    """
    Uses geometric relationships between points A, B, C for blending.
    C starts at A and moves to target position while blending tangents.
    
    Points:
    A: Starting position at target_value
    B: Projection point found by projecting from target C
    C: Moving from A towards target position
    """

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (target_value)
        B: Anchor point (projected from C's angle)
        C: Starting at current_value and moving towards target
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            # Start from current position and move towards target
            self._log_initial_state( blend_factor, point_c_time, current_value, running_value, target_value )

            # Project from current position to find B
            point_b = self._get_projected_point_b( curve, curve_data, current_idx, point_c_time,
                                                current_value, target_value, target_tangents, blend_factor )
            self._log_anchor_info( point_b )

            # Starting angle is at current position
            angle_c = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( angle_c )

            # Move from current towards target
            moving_c_value = self._calculate_point_c_position( current_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, current_value,  # Starting at current
                point_b['time'], point_b['value'],
                moving_c_value, target_tangents['in'][0]
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, angle_c, current_value, moving_c_value,
                                            point_b['value'], target_tangents, blend_factor )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['final_angle'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

    def _get_projected_point_b( self, curve, curve_data, current_idx, time_c, start_value,
                             target_value, target_tangents, blend_factor ):
        """Project from target position to find B"""
        MIN_DELTA = 0.001

        # Use target tangent angle for projection
        target_angle = math.radians( target_tangents['in'][0] )

        # Calculate vertical distance from A to target
        vertical_distance_a_to_target = abs( target_value - start_value )
        if vertical_distance_a_to_target < MIN_DELTA:
            vertical_distance_a_to_target = MIN_DELTA

        # Protect against zero tangent
        if abs( target_angle ) < math.radians( 0.1 ):
            target_angle = math.radians( 0.1 ) * ( 1 if target_angle >= 0 else -1 )

        # Protect against zero tangent in division
        tan_value = math.tan( abs( target_angle ) )
        if abs( tan_value ) < MIN_DELTA:
            tan_value = MIN_DELTA if tan_value >= 0 else -MIN_DELTA

        # Project to find B
        horizontal_distance_to_b = vertical_distance_a_to_target / tan_value
        point_b_time = time_c - horizontal_distance_to_b
        point_b_value = start_value  # B shares y-value with starting point (A)

        if self.debug:
            print( "\n=== Point B Projection ===" )
            print( "Start at A - Time: {0}, Value: {1}".format( time_c, start_value ) )
            print( "Target Value: {0}".format( target_value ) )
            print( "Target Angle: {0}".format( math.degrees( target_angle ) ) )
            print( "Tan Value: {0}".format( tan_value ) )
            print( "A to Target Vertical Distance: {0}".format( vertical_distance_a_to_target ) )
            print( "Distance to B: {0}".format( horizontal_distance_to_b ) )
            print( "Point B - Time: {0}, Value: {1}".format( point_b_time, point_b_value ) )

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_point_c_position( self, start_value, target_value, blend_factor ):
        """Calculate C position as it moves from A to target"""
        merge_mult = abs( blend_factor )
        return start_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_triangle_abc( self, time_c, value_a, time_b, value_b, moving_c_value, target_angle ):
        """Calculate geometric relationships using A as start point"""
        MIN_DELTA = 0.001

        # Initial triangle from A
        initial_opposite = abs( value_a - value_b )
        initial_adjacent = abs( time_c - time_b )

        # Protect against zero division
        if initial_adjacent < MIN_DELTA:
            initial_adjacent = MIN_DELTA

        initial_raw = math.degrees( math.atan( initial_opposite / initial_adjacent ) )

        # Scale factor using target angle
        scale_factor = abs( target_angle / initial_raw ) if initial_raw != 0 else 1.0

        # Current triangle with same protection
        opposite = abs( moving_c_value - value_b )
        adjacent = abs( time_c - time_b )
        if adjacent < MIN_DELTA:
            adjacent = MIN_DELTA

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': scale_factor,
            'opposite': opposite,
            'adjacent': adjacent
        }

    def _calculate_abc_angles( self, triangle_abc, start_angle, value_a, moving_c_value,
                            value_b, target_tangents, blend_factor ):  # Added blend_factor parameter
        """Calculate angles, blending from start to target tangents"""
        if self.debug:
            print( "\n=== ABC Angle Calculation Debug ===" )
            print( "Triangle Data:" )
            print( "  opposite: {0}".format( triangle_abc['opposite'] ) )
            print( "  adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  scale_factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "\nValues:" )
            print( "  value_a: {0}".format( value_a ) )
            print( "  value_b: {0}".format( value_b ) )
            print( "  moving_c_value: {0}".format( moving_c_value ) )
            print( "  start_angle: {0}".format( start_angle ) )
            print( "  target_angle: {0}".format( target_tangents['in'][0] ) )

        raw_angle = math.degrees( math.atan( 
            triangle_abc['opposite'] / triangle_abc['adjacent']
        ) ) if triangle_abc['adjacent'] != 0 else 90.0

        if self.debug:
            print( "\nCalculations:" )
            print( "  raw_angle: {0}".format( raw_angle ) )

        scaled_angle = raw_angle * triangle_abc['scale_factor']

        if self.debug:
            print( "  scaled_angle: {0}".format( scaled_angle ) )

        # Check if we crossed point B
        started_above_b = value_a >= value_b
        ended_above_b = moving_c_value >= value_b

        if self.debug:
            print( "\nCrossing Check:" )
            print( "  started_above_b: {0}".format( started_above_b ) )
            print( "  ended_above_b: {0}".format( ended_above_b ) )

        if started_above_b != ended_above_b:
            scaled_angle = -scaled_angle
            if self.debug:
                print( "  Flipped scaled_angle: {0}".format( scaled_angle ) )

        # Use blend_factor directly for angle interpolation
        target_angle = target_tangents['in'][0]
        blend_mult = abs( blend_factor )

        if self.debug:
            print( "\nBlend Calculation:" )
            print( "  blend_mult: {0}".format( blend_mult ) )

        final_angle = start_angle * ( 1 - blend_mult ) + target_angle * blend_mult

        if self.debug:
            print( "  final_angle: {0}".format( final_angle ) )

        return {
            'raw_angle': raw_angle,
            'scaled_angle': scaled_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    def _log_initial_state( self, blend_factor, time_c, start_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time: {0}".format( time_c ) )
            print( "Starting Value (A): {0}".format( start_value ) )
            print( "Running Value: {0}".format( running_value ) )
            print( "Target Value (C): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Anchor Point Info ===" )
            print( "Time: {0}".format( point_b['time'] ) )
            print( "Value: {0}".format( point_b['value'] ) )

    def _log_angle_info( self, angle_c ):
        if self.debug:
            print( "\n=== Angle Info ===" )
            print( "Start Angle: {0}".format( angle_c ) )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== Position Calculation ===" )
            print( "Merge Multiplier: {0}".format( merge_mult ) )
            print( "New Value: {0}".format( moving_c_value ) )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Opposite (vertical): {0}".format( triangle_abc['opposite'] ) )
            print( "Adjacent (horizontal): {0}".format( triangle_abc['adjacent'] ) )
            print( "Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Final Angle Calculation ===" )
            print( "Raw Angle (before scale/sign): {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final In/Out Angle: {0}".format( angles['final_angle'] ) )

    def _log_final_result( self, moving_c_value, final_angle ):
        if self.debug:
            print( "\n=== Result ===" )
            print( "New Value: {0}".format( moving_c_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "================\n" )


class Geometric4BlendStrategy( BlendStrategy ):

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, current_value, running_value, target_value )

            # Get angle at C and A
            angle_c = curve_data.tangents['in_angles'][current_idx]
            angle_a = target_tangents['in'][0]

            # Get point B by projecting A's angle to C's y-value
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time,
                                       current_value, target_value, angle_a )
            self._log_anchor_info( point_b )
            self._log_angle_info( angle_c )

            moving_c_value = self._calculate_point_c_position( current_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, current_value,
                point_b['time'], point_b['value'],
                moving_c_value, angle_c, target_value
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, angle_c, current_value, moving_c_value,
                                             point_b['time'], point_c_time, angle_a )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['final_angle'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric4 blending: {0}".format( str( e ) ) )
            return current_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value,
                     target_value, angle_a ):
        """Project from A using target angle to find intersection with C's y-value"""
        MIN_DELTA = 0.001

        # Calculate delta_y from A to C's y-value
        vertical_distance_a_to_c = abs( target_value - current_value )
        if vertical_distance_a_to_c < MIN_DELTA:
            vertical_distance_a_to_c = MIN_DELTA

        # Get angle from target/point A
        angle_a_rad = math.radians( angle_a )
        if abs( angle_a_rad ) < math.radians( 0.1 ):
            angle_a_rad = math.radians( 0.1 ) * ( 1 if angle_a_rad >= 0 else -1 )

        # Project from A to find B at C's height
        horizontal_distance_a_to_b = vertical_distance_a_to_c / math.tan( abs( angle_a_rad ) )

        # Determine B position relative to C based on angle and blend direction
        moving_up = target_value > current_value

        # For positive target angle:
        #   moving up -> B left of C
        #   moving down -> B right of C
        # For negative target angle:
        #   moving up -> B right of C
        #   moving down -> B left of C
        if ( angle_a > 0 and moving_up ) or ( angle_a < 0 and not moving_up ):
            point_b_time = point_c_time - horizontal_distance_a_to_b  # B left of C
        else:
            point_b_time = point_c_time + horizontal_distance_a_to_b  # B right of C

        point_b_value = current_value  # B matches C's value

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_c, target_value ):
        """Calculate geometric relationships with sign preservation"""
        # Initial triangle measurements
        initial_opposite = abs( value_b - target_value )
        initial_adjacent = abs( time_c - time_b )
        initial_raw = math.degrees( math.atan( 
            initial_opposite / initial_adjacent
        ) ) if initial_adjacent != 0 else 90.0

        # Match the sign of initial_raw to angle_c for scale factor calculation
        initial_raw = abs( initial_raw ) * ( -1 if angle_c < 0 else 1 )

        # Calculate scale factor using absolute values to preserve sign relationships
        scale_factor = abs( angle_c / initial_raw ) if initial_raw != 0 else 1.0

        # Current triangle measurements
        opposite = abs( moving_c_value - target_value )
        adjacent = abs( time_c - time_b )

        if self.debug:
            print( "Triangle ABC Analysis:" )
            print( "Initial opposite: {0}".format( initial_opposite ) )
            print( "Initial adjacent: {0}".format( initial_adjacent ) )
            print( "Initial raw angle: {0}".format( initial_raw ) )
            print( "Incoming angle_c: {0}".format( angle_c ) )
            print( "Scale factor: {0}".format( scale_factor ) )
            print( "Current opposite: {0}".format( opposite ) )
            print( "Current adjacent: {0}".format( adjacent ) )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': scale_factor,
            'opposite': opposite,
            'adjacent': adjacent
        }

    def _calculate_abc_angles( self, triangle_abc, angle_c, current_value, moving_c_value,
                           time_b, time_c, angle_a ):
        # Get current triangle angle
        raw_angle = math.degrees( math.atan( 
            triangle_abc['opposite'] / triangle_abc['adjacent']
        ) ) if triangle_abc['adjacent'] != 0 else 90.0

        # Match sign of raw angle to incoming angle_c
        raw_angle = abs( raw_angle ) * ( -1 if angle_c < 0 else 1 )

        # Apply scale factor while preserving sign
        scaled_angle = raw_angle * abs( triangle_abc['scale_factor'] )

        # Simply add target angle to what's being reduced
        final_angle = scaled_angle + angle_a

        if self.debug:
            print( "=== Angle Calculation Details ===" )
            print( "Raw Triangle Angle: {0}".format( raw_angle ) )
            print( "Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Scaled Angle: {0}".format( scaled_angle ) )
            print( "Target Angle: {0}".format( angle_a ) )
            print( "Final Angle: {0}".format( final_angle ) )

        return {
            'raw_angle': raw_angle,
            'scaled_angle': scaled_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    # [Logging methods remain the same]

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time: {0}".format( point_b['time'] ) )
            print( "B Value: {0}".format( point_b['value'] ) )
            print( "Note: B shares y-value with C" )

    def _log_angle_info( self, angle_a ):
        if self.debug:
            print( "\n=== Target Angle Info ===" )
            print( "A's Angle: {0}".format( angle_a ) )
            print( "Note: This angle will be maintained through blend" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while maintaining angle relationship" )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Initial State:" )
            print( "  Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc['initial_opposite'] ) )
            print( "  Adjacent (B-C horizontal): {0}".format( 
                triangle_abc['initial_adjacent'] ) )
            print( "Current State:" )
            print( "  Opposite (moving): {0}".format( triangle_abc['opposite'] ) )
            print( "  Adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Note: Triangle formed by B at C's level" )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Raw Angle: {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final Angle: {0}".format( angles['final_angle'] ) )
            print( "Note: Maintaining angle relationship from A" )

    def _log_final_result( self, moving_c_value, final_angle ):
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "Note: Non-zero final angle preserved from A's angle" )
            print( "================\n" )

    def _log_point_b_projection( self, point_c_time, current_value, target_value,
                              angle_a_deg, vert_dist, horz_dist, point_b_time, point_b_value ):
        if self.debug:
            print( "\n=== Point B Projection Details ===" )
            print( "Starting Point C:" )
            print( "  Time: {0}".format( point_c_time ) )
            print( "  Value: {0}".format( current_value ) )
            print( "Target Point A:" )
            print( "  Value: {0}".format( target_value ) )
            print( "Projection:" )
            print( "  A's Angle (degrees): {0}".format( angle_a_deg ) )
            print( "  Vertical Distance (A to C): {0}".format( vert_dist ) )
            print( "  Horizontal Distance (A to B): {0}".format( horz_dist ) )
            print( "Resulting Point B:" )
            print( "  Time: {0}".format( point_b_time ) )
            print( "  Value: {0}".format( point_b_value ) )
            print( "  Note: B created at C's height using A's angle" )


class Geometric6BlendStrategy( BlendStrategy ):
    """variation on geom5 for direct blend"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (current_time, target_value)
        B: Intersection point of C's angle and target's angle
        C: Current point (current_time, current_value)
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, current_value, running_value, target_value )

            # Get point B by finding intersection of angles
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time, current_value, target_value, target_tangents, blend_factor )
            self._log_anchor_info( point_b )

            # Get angle at C and calculate new position
            angle_c = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( angle_c )

            moving_c_value = self._calculate_point_c_position( current_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, current_value,
                point_b['time'], point_b['value'],
                moving_c_value, angle_c
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, angle_c, current_value, moving_c_value, point_b['value'], target_tangents, target_value )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['final_angle'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value, target_value, target_tangents, blend_factor ):
        """Find point B as intersection of two lines: one from C with angle_c, one from target with target angle"""
        MIN_DELTA = 0.001

        # Get angles for both lines
        angle_c = math.radians( curve_data.tangents['in_angles'][current_idx] )
        target_angle = math.radians( target_tangents['in'][0] )

        # If angles are effectively parallel, we're already at the right angle
        if abs( angle_c - target_angle ) < math.radians( 0.1 ):
            # Angles match - no intersection needed
            point_b_time = point_c_time
            point_b_value = target_value
        else:
            # Convert angles to slopes
            slope_c = math.tan( angle_c )
            slope_target = math.tan( target_angle )

            # Calculate intersection
            point_b_time = ( 
                ( target_value - current_value + slope_c * point_c_time - slope_target * point_c_time )
                / ( slope_c - slope_target )
            )
            point_b_value = current_value + slope_c * ( point_b_time - point_c_time )

        if self.debug:
            print( "\n=== Point B Intersection ===" )
            print( "Point C - Time: {0}, Value: {1}".format( point_c_time, current_value ) )
            print( "Target - Value: {0}".format( target_value ) )
            print( "Point B - Time: {0}, Value: {1}".format( point_b_time, point_b_value ) )

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_c ):
        """Calculate geometric relationships between points A, B, and C for any triangle"""

        def normalize_angle( angle ):
            while angle > 90:
                angle = angle - 180
            while angle < -90:
                angle = angle + 180
            return angle

        # Calculate vector from C to B
        dx = time_b - time_c
        dy = value_b - moving_c_value

        # Calculate raw angle from C to B
        # This should remain constant regardless of C's movement
        raw_angle = normalize_angle( math.degrees( math.atan2( dy, dx ) ) )

        # Store initial relationship for reference
        initial_opposite = abs( value_c - value_b )
        initial_adjacent = abs( time_c - time_b )
        initial_raw = normalize_angle( math.degrees( math.atan2( value_b - value_c, dx ) ) )

        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Vector C->B: dx={0}, dy={1}".format( dx, dy ) )
            print( "Moving C value: {0}".format( moving_c_value ) )
            print( "B value: {0}".format( value_b ) )
            print( "Raw angle C->B: {0}".format( raw_angle ) )
            print( "Initial raw angle: {0}".format( initial_raw ) )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_raw': initial_raw,
            'scale_factor': 1.0,
            'opposite': abs( dy ),
            'adjacent': abs( dx ),
            'raw_angle': raw_angle  # This angle should remain consistent as C moves
        }

    def _calculate_abc_angles( self, triangle_abc, angle_c, current_value, moving_c_value, value_b, target_tangents, target_value ):
        """Calculate angles based on geometric relationships for any triangle"""
        # Use the raw angle directly - it's already what we want
        MIN_DELTA = 0.1  # Same threshold as in _find_point_b

        # If original angles were parallel, just use the target angle
        if abs( angle_c - target_tangents['in'][0] ) < MIN_DELTA:
            final_angle = target_tangents['in'][0]
        else:
            final_angle = triangle_abc['raw_angle']

        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Raw angle C->B: {0}".format( final_angle ) )
            print( "Current value: {0}".format( current_value ) )
            print( "Moving value: {0}".format( moving_c_value ) )
            print( "Target value: {0}".format( target_value ) )

        return {
            'raw_angle': final_angle,
            'scaled_angle': final_angle,
            'final_angle': final_angle
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        return {
            'in': ( angles['final_angle'], target_tangents['in'][1] ),
            'out': ( angles['final_angle'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    # [Logging methods remain the same]

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time: {0}".format( point_b['time'] ) )
            print( "B Value: {0}".format( point_b['value'] ) )
            print( "Note: B shares y-value with C" )

    def _log_angle_info( self, angle_a ):
        if self.debug:
            print( "\n=== Target Angle Info ===" )
            print( "A's Angle: {0}".format( angle_a ) )
            print( "Note: This angle will be maintained through blend" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while maintaining angle relationship" )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Initial State:" )
            print( "  Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc['initial_opposite'] ) )
            print( "  Adjacent (B-C horizontal): {0}".format( 
                triangle_abc['initial_adjacent'] ) )
            print( "Current State:" )
            print( "  Opposite (moving): {0}".format( triangle_abc['opposite'] ) )
            print( "  Adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Note: Triangle formed by B at C's level" )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Raw Angle: {0}".format( angles['raw_angle'] ) )
            print( "Scaled Angle: {0}".format( angles['scaled_angle'] ) )
            print( "Final Angle: {0}".format( angles['final_angle'] ) )
            print( "Note: Maintaining angle relationship from A" )

    def _log_final_result( self, moving_c_value, final_angle ):
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Final Angle: {0}".format( final_angle ) )
            print( "Note: Non-zero final angle preserved from A's angle" )
            print( "================\n" )

    def _log_point_b_projection( self, point_c_time, current_value, target_value,
                              angle_a_deg, vert_dist, horz_dist, point_b_time, point_b_value ):
        if self.debug:
            print( "\n=== Point B Projection Details ===" )
            print( "Starting Point C:" )
            print( "  Time: {0}".format( point_c_time ) )
            print( "  Value: {0}".format( current_value ) )
            print( "Target Point A:" )
            print( "  Value: {0}".format( target_value ) )
            print( "Projection:" )
            print( "  A's Angle (degrees): {0}".format( angle_a_deg ) )
            print( "  Vertical Distance (A to C): {0}".format( vert_dist ) )
            print( "  Horizontal Distance (A to B): {0}".format( horz_dist ) )
            print( "Resulting Point B:" )
            print( "  Time: {0}".format( point_b_time ) )
            print( "  Value: {0}".format( point_b_value ) )
            print( "  Note: B created at C's height using A's angle" )


class Geometric5BlendStrategy( BlendStrategy ):
    """Uses geometric relationships between points A, B, C for blending with intersection-based point B"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, initial_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (current_time, target_value)
        B: Intersection point of C's angle and target's angle
        C: Current point (current_time, initial_value)
        """
        # print( target_tangents )
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, initial_value, running_value, target_value )

            # Get initial tangent at C's position
            initial_tangent = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( initial_tangent )

            # Get point B by finding intersection of angles
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time, initial_value, target_value, target_tangents, blend_factor )
            self._log_anchor_info( point_b )

            moving_c_value = self._calculate_point_c_position( initial_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, initial_value,
                point_b['time'], point_b['value'],
                moving_c_value, initial_tangent
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, initial_tangent, initial_value, moving_c_value, point_b['value'], target_tangents, target_value )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['running_calculated_tangent'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return initial_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value, target_value, target_tangents, blend_factor ):
        """Find point B as intersection of two lines: one from C with angle_c, one from target with target angle"""
        MIN_DELTA = 0.001

        # Get angles for both lines
        angle_c = math.radians( curve_data.tangents['in_angles'][current_idx] )
        target_angle = math.radians( target_tangents['in'][0] )
        # print( target_angle, angle_c )

        # If angles are effectively parallel, we're already at the right angle
        if abs( angle_c - target_angle ) < math.radians( 0.1 ):
            # Angles match - no intersection needed
            point_b_time = point_c_time
            point_b_value = target_value
        else:
            # Convert angles to slopes
            slope_c = math.tan( angle_c )
            slope_target = math.tan( target_angle )

            # Calculate intersection
            point_b_time = ( 
                ( target_value - current_value + slope_c * point_c_time - slope_target * point_c_time )
                / ( slope_c - slope_target )
            )
            point_b_value = current_value + slope_c * ( point_b_time - point_c_time )

        if self.debug:
            print( "\n=== Point B Intersection ===" )
            print( "Point C - Time: {0}, Value: {1}".format( point_c_time, current_value ) )
            print( "Target - Value: {0}".format( target_value ) )
            print( "Point B - Time: {0}, Value: {1}".format( point_b_time, point_b_value ) )

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor. 
        Negative blend: pull towards target
        Positive blend: push away from target by the same amount"""

        # Calculate the distance from current to target
        delta = target_value - current_value

        # For negative blend: move toward target by blend_factor * delta
        # For positive blend: move away from target by blend_factor * delta
        return current_value - blend_factor * delta

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_c ):
        """Calculate geometric relationships between points A, B, and C for any triangle"""

        def normalize_angle( angle ):
            while angle > 90:
                angle = angle - 180
            while angle < -90:
                angle = angle + 180
            return angle

        # Calculate vector from C to B
        dx = time_b - time_c
        dy = value_b - moving_c_value

        # Calculate raw angle from C to B
        # This should remain constant regardless of C's movement
        running_calculated_tangent = normalize_angle( math.degrees( math.atan2( dy, dx ) ) )

        # Store initial relationship for reference
        initial_opposite = abs( value_c - value_b )
        initial_adjacent = abs( time_c - time_b )
        initial_calculated_tangent = normalize_angle( math.degrees( math.atan2( value_b - value_c, dx ) ) )

        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Vector C->B: dx={0}, dy={1}".format( dx, dy ) )
            print( "Moving C value: {0}".format( moving_c_value ) )
            print( "B value: {0}".format( value_b ) )
            print( "Running calculated tangent C->B: {0}".format( running_calculated_tangent ) )
            print( "Initial calculated tangent: {0}".format( initial_calculated_tangent ) )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_calculated_tangent ': initial_calculated_tangent ,
            'scale_factor': 1.0,
            'opposite': abs( dy ),
            'adjacent': abs( dx ),
            'running_calculated_tangent': running_calculated_tangent  # This angle should remain consistent as C moves
        }

    def _calculate_abc_angles( self, triangle_abc, angle_c, current_value, moving_c_value, value_b, target_tangents, target_value ):
        """Calculate angles based on geometric relationships for any triangle"""
        MIN_DELTA = 0.1  # Same threshold as in _find_point_b

        # If original angles were parallel, just use the target angle
        if abs( angle_c - target_tangents['in'][0] ) < MIN_DELTA:
            running_calculated_tangent = target_tangents['in'][0]
        else:
            running_calculated_tangent = triangle_abc['running_calculated_tangent']

        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Running calculated tangent C->B: {0}".format( running_calculated_tangent ) )
            print( "Current value: {0}".format( current_value ) )
            print( "Moving value: {0}".format( moving_c_value ) )
            print( "Target value: {0}".format( target_value ) )

        return {
            'running_calculated_tangent': running_calculated_tangent
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        # print( '___target t', target_tangents )

        return {
            'in': ( angles['running_calculated_tangent'], target_tangents['in'][1] ),
            'out': ( angles['running_calculated_tangent'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    # [Logging methods remain the same]

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time: {0}".format( point_b['time'] ) )
            print( "B Value: {0}".format( point_b['value'] ) )

    def _log_angle_info( self, initial_tangent ):
        if self.debug:
            print( "\n=== Start Angle Info ===" )
            print( "C's Start Angle: {0}".format( initial_tangent ) )
            print( "Note: This variable will not be overwritten" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while projecting Tangent at point B" )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Initial State:" )
            print( "  Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc['initial_opposite'] ) )
            print( "  Adjacent (B-C horizontal): {0}".format( 
                triangle_abc['initial_adjacent'] ) )
            print( "Current State:" )
            print( "  Opposite (moving): {0}".format( triangle_abc['opposite'] ) )
            print( "  Adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Note: Triangle" )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Running calculated tangent: {0}".format( angles['running_calculated_tangent'] ) )
            print( "Note: Maintaining angle relationship from A" )

    def _log_final_result( self, moving_c_value, running_calculated_tangent ):
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Running calculated tangent: {0}".format( running_calculated_tangent ) )
            print( "Note: Non-zero final angle, blending towards target tangent" )
            print( "================\n" )

    def _log_point_b_projection( self, point_c_time, current_value, target_value,
                              angle_a_deg, vert_dist, horz_dist, point_b_time, point_b_value ):
        if self.debug:
            print( "\n=== Point B Projection Details ===" )
            print( "Starting Point C:" )
            print( "  Time: {0}".format( point_c_time ) )
            print( "  Value: {0}".format( current_value ) )
            print( "Target Point A:" )
            print( "  Value: {0}".format( target_value ) )
            print( "Projection:" )
            print( "  A's Angle (degrees): {0}".format( angle_a_deg ) )
            print( "  Vertical Distance (A to C): {0}".format( vert_dist ) )
            print( "  Horizontal Distance (A to B): {0}".format( horz_dist ) )
            print( "Resulting Point B:" )
            print( "  Time: {0}".format( point_b_time ) )
            print( "  Value: {0}".format( point_b_value ) )


class Geometric7BlendStrategy( BlendStrategy ):
    """same as the other geom5, only changed _calculate_point_c_position to make it compatible with direct targeting strategy"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True

    def blend_values( self, curve, current_idx, initial_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (current_time, target_value)
        B: Intersection point of C's angle and target's angle
        C: Current point (current_time, initial_value)
        """
        # print( target_tangents )
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, initial_value, running_value, target_value )

            # Get initial tangent at C's position
            initial_tangent = curve_data.tangents['in_angles'][current_idx]
            self._log_angle_info( initial_tangent )

            # Get point B by finding intersection of angles
            point_b = self._find_point_b( curve, curve_data, current_idx, point_c_time, initial_value, target_value, target_tangents, blend_factor )
            self._log_anchor_info( point_b )

            moving_c_value = self._calculate_point_c_position( initial_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C
            triangle_abc = self._calculate_triangle_abc( 
                point_c_time, initial_value,
                point_b['time'], point_b['value'],
                moving_c_value, initial_tangent
            )
            self._log_geometry_data( triangle_abc )

            angles = self._calculate_abc_angles( triangle_abc, initial_tangent, initial_value, moving_c_value, point_b['value'], target_tangents, target_value )
            self._log_angle_calculation( angles )

            tangents = self._prepare_tangent_result( angles, target_tangents )
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles['running_calculated_tangent'] )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return initial_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value, target_value, target_tangents, blend_factor ):
        """Find point B as intersection of two lines: one from C with angle_c, one from target with target angle"""
        MIN_DELTA = 0.001

        # Get angles for both lines
        angle_c = math.radians( curve_data.tangents['in_angles'][current_idx] )
        target_angle = math.radians( target_tangents['in'][0] )
        # print( target_angle, angle_c )

        # If angles are effectively parallel, we're already at the right angle
        if abs( angle_c - target_angle ) < math.radians( 0.1 ):
            # Angles match - no intersection needed
            point_b_time = point_c_time
            point_b_value = target_value
        else:
            # Convert angles to slopes
            slope_c = math.tan( angle_c )
            slope_target = math.tan( target_angle )

            # Calculate intersection
            point_b_time = ( 
                ( target_value - current_value + slope_c * point_c_time - slope_target * point_c_time )
                / ( slope_c - slope_target )
            )
            point_b_value = current_value + slope_c * ( point_b_time - point_c_time )

        if self.debug:
            print( "\n=== Point B Intersection ===" )
            print( "Point C - Time: {0}, Value: {1}".format( point_c_time, current_value ) )
            print( "Target - Value: {0}".format( target_value ) )
            print( "Point B - Time: {0}, Value: {1}".format( point_b_time, point_b_value ) )

        return {
            'time': point_b_time,
            'value': point_b_value
        }

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult

    def _calculate_triangle_abc( self, time_c, value_c, time_b, value_b, moving_c_value, angle_c ):
        """Calculate geometric relationships between points A, B, and C for any triangle"""

        def normalize_angle( angle ):
            while angle > 90:
                angle = angle - 180
            while angle < -90:
                angle = angle + 180
            return angle

        # Calculate vector from C to B
        dx = time_b - time_c
        dy = value_b - moving_c_value

        # Calculate raw angle from C to B
        # This should remain constant regardless of C's movement
        running_calculated_tangent = normalize_angle( math.degrees( math.atan2( dy, dx ) ) )

        # Store initial relationship for reference
        initial_opposite = abs( value_c - value_b )
        initial_adjacent = abs( time_c - time_b )
        initial_calculated_tangent = normalize_angle( math.degrees( math.atan2( value_b - value_c, dx ) ) )

        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Vector C->B: dx={0}, dy={1}".format( dx, dy ) )
            print( "Moving C value: {0}".format( moving_c_value ) )
            print( "B value: {0}".format( value_b ) )
            print( "Running calculated tangent C->B: {0}".format( running_calculated_tangent ) )
            print( "Initial calculated tangent: {0}".format( initial_calculated_tangent ) )

        return {
            'initial_opposite': initial_opposite,
            'initial_adjacent': initial_adjacent,
            'initial_calculated_tangent ': initial_calculated_tangent ,
            'scale_factor': 1.0,
            'opposite': abs( dy ),
            'adjacent': abs( dx ),
            'running_calculated_tangent': running_calculated_tangent  # This angle should remain consistent as C moves
        }

    def _calculate_abc_angles( self, triangle_abc, angle_c, current_value, moving_c_value, value_b, target_tangents, target_value ):
        """Calculate angles based on geometric relationships for any triangle"""
        MIN_DELTA = 0.1  # Same threshold as in _find_point_b

        # If original angles were parallel, just use the target angle
        if abs( angle_c - target_tangents['in'][0] ) < MIN_DELTA:
            running_calculated_tangent = target_tangents['in'][0]
        else:
            running_calculated_tangent = triangle_abc['running_calculated_tangent']

        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Running calculated tangent C->B: {0}".format( running_calculated_tangent ) )
            print( "Current value: {0}".format( current_value ) )
            print( "Moving value: {0}".format( moving_c_value ) )
            print( "Target value: {0}".format( target_value ) )

        return {
            'running_calculated_tangent': running_calculated_tangent
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Prepare tangent result structure"""
        # print( '___target t', target_tangents )

        return {
            'in': ( angles['running_calculated_tangent'], target_tangents['in'][1] ),
            'out': ( angles['running_calculated_tangent'], target_tangents['out'][1] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    # [Logging methods remain the same]

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time: {0}".format( point_b['time'] ) )
            print( "B Value: {0}".format( point_b['value'] ) )

    def _log_angle_info( self, initial_tangent ):
        if self.debug:
            print( "\n=== Start Angle Info ===" )
            print( "C's Start Angle: {0}".format( initial_tangent ) )
            print( "Note: This variable will not be overwritten" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while projecting Tangent at point B" )

    def _log_geometry_data( self, triangle_abc ):
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "Initial State:" )
            print( "  Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc['initial_opposite'] ) )
            print( "  Adjacent (B-C horizontal): {0}".format( 
                triangle_abc['initial_adjacent'] ) )
            print( "Current State:" )
            print( "  Opposite (moving): {0}".format( triangle_abc['opposite'] ) )
            print( "  Adjacent: {0}".format( triangle_abc['adjacent'] ) )
            print( "  Scale Factor: {0}".format( triangle_abc['scale_factor'] ) )
            print( "Note: Triangle" )

    def _log_angle_calculation( self, angles ):
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Running calculated tangent: {0}".format( angles['running_calculated_tangent'] ) )
            print( "Note: Maintaining angle relationship from A" )

    def _log_final_result( self, moving_c_value, running_calculated_tangent ):
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Running calculated tangent: {0}".format( running_calculated_tangent ) )
            print( "Note: Non-zero final angle, blending towards target tangent" )
            print( "================\n" )

    def _log_point_b_projection( self, point_c_time, current_value, target_value,
                              angle_a_deg, vert_dist, horz_dist, point_b_time, point_b_value ):
        if self.debug:
            print( "\n=== Point B Projection Details ===" )
            print( "Starting Point C:" )
            print( "  Time: {0}".format( point_c_time ) )
            print( "  Value: {0}".format( current_value ) )
            print( "Target Point A:" )
            print( "  Value: {0}".format( target_value ) )
            print( "Projection:" )
            print( "  A's Angle (degrees): {0}".format( angle_a_deg ) )
            print( "  Vertical Distance (A to C): {0}".format( vert_dist ) )
            print( "  Horizontal Distance (A to B): {0}".format( horz_dist ) )
            print( "Resulting Point B:" )
            print( "  Time: {0}".format( point_b_time ) )
            print( "  Value: {0}".format( point_b_value ) )

