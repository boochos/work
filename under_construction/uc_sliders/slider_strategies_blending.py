# -*- coding: utf-8 -*-
"""
Provides blending strategies for animation curve manipulation.
Handles interpolation of values and tangents between animation states.
"""

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np


def __BLENDING_STRATEGIES__():
    pass


class BlendStrategy( object ):
    """Base class for blending behaviors"""

    def __init__( self, core ):
        self.core = core
        self.uses_signed_blend = False  # Default behavior ((+ / -) or abs)
        self.PARALLEL_THRESHOLD_DEG = 0.0001  # if initial and target angle are less than this range, snap to target.
        self.VALUE_MATCH_THRESHOLD = 0.000001  # when value matches, only blend tangent
        self._sync_weight_settings()

    def _get_targeting_strategy( self ):
        """Get current targeting strategy from core"""
        return self.core.get_current_targeting_strategy()

    def _sync_weight_settings( self ):
        """Sync weight control settings from targeting strategy"""
        strategy = self.core.get_current_targeting_strategy()
        self.lock_weights_beyond_negative = strategy.lock_weights_beyond_negative
        self.lock_weights_beyond_positive = strategy.lock_weights_beyond_positive
        self.preserve_weights_positive = strategy.preserve_weights_positive
        self.preserve_weights_negative = strategy.preserve_weights_negative
        self.preserve_opposing_anchor = strategy.preserve_opposing_anchor

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

    def blend_anchors( self, curve, anchor_data, blend_factor ):
        """
        Handle blending of anchor tangent weights separately from main key blending.
        Meant to be consistent across all blend strategies.
        
        Args:
            curve: The animation curve being processed
            anchor_data: Dictionary containing 'time', 'weight', and 'tangent' info
            blend_factor: Current blend factor (0-1)
            
        Returns:
            dict: Updated anchor data with blended weight
        """
        try:
            if not anchor_data:
                return None

            curve_data = self.core.get_curve_data( curve )
            if not curve_data:
                return None

            # Get current key index and tangent data
            current_idx = curve_data.key_map[anchor_data['time']]
            current_weight = curve_data.tangents[anchor_data['tangent'] + '_weights'][current_idx]

            # Check direction
            is_positive = blend_factor > 0
            is_negative = blend_factor < 0
            beyond_negative = blend_factor <= -1.0
            beyond_positive = blend_factor >= 1.0
            abs_blend = abs( blend_factor )

            # Determine if we should preserve the current weight
            preserve_weight = False

            # Check directional anchor preservation
            if self.preserve_opposing_anchor:
                preserve_weight = ( anchor_data['tangent'] == 'out' and is_positive ) or \
                                ( anchor_data['tangent'] == 'in' and is_negative )

            # Check other preservation conditions if not already preserving
            if not preserve_weight:
                preserve_weight = ( self.preserve_weights_positive and is_positive ) or \
                                ( self.preserve_weights_negative and is_negative )

            # Calculate new weight
            if preserve_weight:
                new_weight = current_weight
            elif beyond_negative and self.lock_weights_beyond_negative:
                new_weight = anchor_data['weight']
            elif beyond_positive and self.lock_weights_beyond_positive:
                new_weight = anchor_data['weight']
            else:
                if self.lock_weights_beyond_negative:
                    abs_blend = min( abs_blend, 1.0 ) if blend_factor < 0 else abs_blend
                if self.lock_weights_beyond_positive:
                    abs_blend = min( abs_blend, 1.0 ) if blend_factor > 0 else abs_blend

                new_weight = current_weight * ( 1.0 - abs_blend ) + anchor_data['weight'] * abs_blend

            # Return updated anchor data
            updated_anchor = anchor_data.copy()
            updated_anchor['weight'] = new_weight
            return updated_anchor

        except Exception as e:
            print( "Error in anchor weight blending: {0}".format( e ) )
            return None


class TriangleBlendStrategy( BlendStrategy ):
    """Uses geometric relationships between points A, B, C for blending with intersection-based point B"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )
        self.debug = False
        self.uses_signed_blend = True
        self.lock_weights_beyond_negative = True  # Lock weights when going beyond -100%
        self.lock_weights_beyond_positive = True  # Lock weights when going beyond +100%

    def blend_values( self, curve, current_idx, initial_value, target_value, target_tangents, blend_factor ):
        """
        Blend using three key points:
        A: Target point (current_time, target_value)
        B: Intersection points of C's in/out angles and target's in/out angles
        C: Current point (current_time, initial_value)
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            point_c_time = curve_data.keys[current_idx]
            running_value = curve_data.get_running_value( current_idx )

            self._log_initial_state( blend_factor, point_c_time, initial_value, running_value, target_value )

            # Get initial tangents at C's position (both in and out)
            initial_in_tangent = curve_data.tangents['in_angles'][current_idx]
            initial_out_tangent = curve_data.tangents['out_angles'][current_idx]
            self._log_angle_info( initial_in_tangent, initial_out_tangent )
            initial_in_weight = curve_data.tangents['in_weights'][current_idx]
            initial_out_weight = curve_data.tangents['out_weights'][current_idx]

            # Get point B by finding intersection of angles for both in and out tangents
            point_b = self._find_point_b( 
                curve, curve_data, current_idx,
                point_c_time, initial_value,
                target_value, target_tangents,
                blend_factor
            )
            self._log_anchor_info( point_b )

            # Calculate new position for point C
            moving_c_value = self._calculate_point_c_position( initial_value, target_value, blend_factor )
            self._log_position_calculation( abs( blend_factor ), moving_c_value )

            # Calculate geometric relationships between A, B, C for both tangents
            triangle_abc_in = self._calculate_triangle_abc( 
                point_c_time, initial_value,
                point_b['in']['time'], point_b['in']['value'],
                moving_c_value, initial_in_tangent
            )
            triangle_abc_out = self._calculate_triangle_abc( 
                point_c_time, initial_value,
                point_b['out']['time'], point_b['out']['value'],
                moving_c_value, initial_out_tangent
            )
            self._log_geometry_data( triangle_abc_in, triangle_abc_out )

            # Calculate angles based on geometric relationships
            angles = self._calculate_abc_angles( 
                triangle_abc_in, triangle_abc_out,
                initial_in_tangent, initial_out_tangent,
                initial_value, moving_c_value,
                point_b, target_tangents, target_value,
                blend_factor,
                initial_in_weight, initial_out_weight
            )
            self._log_angle_calculation( angles )

            # Prepare final tangent result with separate in/out angles
            tangents = self._prepare_tangent_result( angles, target_tangents )

            # Update curve state
            self._update_curve_state( curve_data, current_idx, moving_c_value, tangents )
            self._log_final_result( moving_c_value, angles )

            return moving_c_value, tangents

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return initial_value, None

    def _find_point_b( self, curve, curve_data, current_idx, point_c_time, current_value, target_value, target_tangents, blend_factor ):
        """Find point B as intersection of two lines: one from C with angle_c, one from target with target angle"""
        # Calculate intersection for in tangent
        point_b_in = self._calculate_intersection( 
            curve_data.tangents['in_angles'][current_idx],
            target_tangents['in'][0],
            point_c_time,
            current_value,
            target_value
        )

        # Calculate intersection for out tangent
        point_b_out = self._calculate_intersection( 
            curve_data.tangents['out_angles'][current_idx],
            target_tangents['out'][0],
            point_c_time,
            current_value,
            target_value
        )

        return {
            'in': point_b_in,
            'out': point_b_out
        }

    def _calculate_intersection( self, angle_c, target_angle, point_c_time, current_value, target_value ):
        """Calculate intersection point for a single tangent"""
        angle_c = math.radians( angle_c )
        target_angle = math.radians( target_angle )

        # If angles are effectively parallel
        if abs( math.degrees( angle_c ) - math.degrees( target_angle ) ) < self.PARALLEL_THRESHOLD_DEG:
            return {
                'time': point_c_time,
                'value': target_value
            }

        # Convert angles to slopes
        slope_c = math.tan( angle_c )
        slope_target = math.tan( target_angle )

        # Calculate intersection
        point_b_time = ( 
            ( target_value - current_value + slope_c * point_c_time - slope_target * point_c_time )
            / ( slope_c - slope_target )
        )
        point_b_value = current_value + slope_c * ( point_b_time - point_c_time )

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

    def _calculate_abc_angles( self, triangle_abc_in, triangle_abc_out, initial_in_tangent, initial_out_tangent,
                             current_value, moving_c_value, value_b, target_tangents, target_value, blend_factor, initial_in_weight, initial_out_weight ):
        """Calculate angles based on geometric relationships"""
        # If values match within threshold, use direct angle interpolation
        if abs( moving_c_value - target_value ) < self.VALUE_MATCH_THRESHOLD:
            running_calculated_in = self._blend_angles( initial_in_tangent, target_tangents['in'][0], abs( blend_factor ) )
            running_calculated_out = self._blend_angles( initial_out_tangent, target_tangents['out'][0], abs( blend_factor ) )
        else:
            # Use geometric angle calculation when points are distinct
            if abs( initial_in_tangent - target_tangents['in'][0] ) < self.PARALLEL_THRESHOLD_DEG:
                running_calculated_in = target_tangents['in'][0]
            else:
                running_calculated_in = triangle_abc_in['running_calculated_tangent']

            if abs( initial_out_tangent - target_tangents['out'][0] ) < self.PARALLEL_THRESHOLD_DEG:
                running_calculated_out = target_tangents['out'][0]
            else:
                running_calculated_out = triangle_abc_out['running_calculated_tangent']

        # Handle weights with direction-specific preservation
        is_positive = blend_factor > 0
        is_negative = blend_factor < 0
        beyond_negative = blend_factor <= -1.0
        beyond_positive = blend_factor >= 1.0
        weight_blend = abs( blend_factor )

        # Handle in weight
        if self.preserve_weights_positive and is_positive:
            # Keep original weight in positive direction
            running_calculated_in_weight = initial_in_weight
        elif beyond_negative and self.lock_weights_beyond_negative:
            running_calculated_in_weight = target_tangents['in'][1]
        elif beyond_positive and self.lock_weights_beyond_positive:
            running_calculated_in_weight = target_tangents['in'][1]
        else:
            # Normal blending within range or when locking is disabled
            if self.lock_weights_beyond_negative:
                weight_blend = min( weight_blend, 1.0 ) if blend_factor < 0 else weight_blend
            if self.lock_weights_beyond_positive:
                weight_blend = min( weight_blend, 1.0 ) if blend_factor > 0 else weight_blend

            running_calculated_in_weight = ( initial_in_weight * ( 1.0 - weight_blend ) +
                                         target_tangents['in'][1] * weight_blend )

        # Handle out weight
        if ( self.preserve_weights_positive and is_positive ) or ( self.preserve_weights_negative and is_negative ):
            # Keep original weight in positive direction
            running_calculated_out_weight = initial_out_weight
        elif beyond_negative and self.lock_weights_beyond_negative:
            running_calculated_out_weight = target_tangents['out'][1]
        elif beyond_positive and self.lock_weights_beyond_positive:
            running_calculated_out_weight = target_tangents['out'][1]
        else:
            # Normal blending within range or when locking is disabled
            running_calculated_out_weight = ( initial_out_weight * ( 1.0 - weight_blend ) +
                                          target_tangents['out'][1] * weight_blend )

        # Clamp weights to Maya's valid range
        running_calculated_in_weight = min( max( running_calculated_in_weight, 0.1 ), 10.0 )
        running_calculated_out_weight = min( max( running_calculated_out_weight, 0.1 ), 10.0 )

        return {
            'running_calculated_in': running_calculated_in,
            'running_calculated_out': running_calculated_out,
            'running_calculated_in_weight': running_calculated_in_weight,
            'running_calculated_out_weight': running_calculated_out_weight
        }

    def _prepare_tangent_result( self, angles, target_tangents ):
        """Package calculated angles and weights into result format"""
        return {
            'in': ( angles['running_calculated_in'], angles['running_calculated_in_weight'] ),
            'out': ( angles['running_calculated_out'], angles['running_calculated_out_weight'] )
        }

    def _update_curve_state( self, curve_data, current_idx, moving_c_value, tangents ):
        """Update the running state of the curve"""
        curve_data.update_running_state( current_idx, moving_c_value, tangents )

    def __LOG__( self ):
        """  [Logging methods remain the same]"""

    def _log_initial_state( self, blend_factor, point_c_time, current_value,
                          running_value, target_value ):
        if self.debug:
            print( "\n=== Geometric4 Frame Start ===" )
            print( "Blend Factor: {0}".format( blend_factor ) )
            print( "Time C: {0}".format( point_c_time ) )
            print( "Value C (current): {0}".format( current_value ) )
            print( "Value C (running): {0}".format( running_value ) )
            print( "Value A (target): {0}".format( target_value ) )

    def _log_anchor_info( self, point_b ):  # Updated
        if self.debug:
            print( "\n=== Point B Info ===" )
            print( "B Time (in): {0}".format( point_b['in']['time'] ) )
            print( "B Value (in): {0}".format( point_b['in']['value'] ) )
            print( "B Time (out): {0}".format( point_b['out']['time'] ) )
            print( "B Value (out): {0}".format( point_b['out']['value'] ) )

    def _log_angle_info( self, initial_in_tangent, initial_out_tangent ):  # Updated
        if self.debug:
            print( "\n=== Start Angle Info ===" )
            print( "C's Start In Angle: {0}".format( initial_in_tangent ) )
            print( "C's Start Out Angle: {0}".format( initial_out_tangent ) )
            print( "Note: These variables will not be overwritten" )

    def _log_position_calculation( self, merge_mult, moving_c_value ):
        if self.debug:
            print( "\n=== C Position Update ===" )
            print( "Blend Multiplier: {0}".format( merge_mult ) )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Note: C moving towards A while projecting Tangent at point B" )

    def _log_geometry_data( self, triangle_abc_in, triangle_abc_out ):  # Updated
        if self.debug:
            print( "\n=== Triangle Geometry ===" )
            print( "In Tangent Triangle:" )
            print( "  Initial State:" )
            print( "    Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc_in['initial_opposite'] ) )
            print( "    Adjacent (B-C horizontal): {0}".format( 
                triangle_abc_in['initial_adjacent'] ) )
            print( "  Current State:" )
            print( "    Opposite (moving): {0}".format( triangle_abc_in['opposite'] ) )
            print( "    Adjacent: {0}".format( triangle_abc_in['adjacent'] ) )
            print( "    Scale Factor: {0}".format( triangle_abc_in['scale_factor'] ) )

            print( "\nOut Tangent Triangle:" )
            print( "  Initial State:" )
            print( "    Opposite (B-C vertical): {0} (should be near 0)".format( 
                triangle_abc_out['initial_opposite'] ) )
            print( "    Adjacent (B-C horizontal): {0}".format( 
                triangle_abc_out['initial_adjacent'] ) )
            print( "  Current State:" )
            print( "    Opposite (moving): {0}".format( triangle_abc_out['opposite'] ) )
            print( "    Adjacent: {0}".format( triangle_abc_out['adjacent'] ) )
            print( "    Scale Factor: {0}".format( triangle_abc_out['scale_factor'] ) )

    def _log_angle_calculation( self, angles ):  # Updated
        if self.debug:
            print( "\n=== Angle Calculations ===" )
            print( "Running calculated in tangent: {0}".format( 
                angles['running_calculated_in'] ) )
            print( "Running calculated out tangent: {0}".format( 
                angles['running_calculated_out'] ) )
            print( "Note: Maintaining angle relationships from A" )

    def _log_final_result( self, moving_c_value, angles ):  # Updated
        if self.debug:
            print( "\n=== Final Frame Result ===" )
            print( "New C Value: {0}".format( moving_c_value ) )
            print( "Running calculated in tangent: {0}".format( 
                angles['running_calculated_in'] ) )
            print( "Running calculated out tangent: {0}".format( 
                angles['running_calculated_out'] ) )
            print( "Note: Non-zero final angles, blending towards target tangents" )
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


class TriangleDirectBlendStrategy( TriangleBlendStrategy ):
    """Triangle blend strategy optimized for direct targeting"""

    def _calculate_point_c_position( self, current_value, target_value, blend_factor ):
        """Calculate new position for point C based on blend factor"""
        merge_mult = abs( blend_factor )
        return current_value * ( 1 - merge_mult ) + target_value * merge_mult


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


def __AUTO_TANGENT_STRATEGIES__():
    pass


class AutoTangentStrategy( object ):
    """Base class for auto tangent calculation behaviors"""

    def __init__( self, core ):
        # Common settings that could be adjusted
        self.debug = False
        self.core = core

    def calculate_tangents( self, curve, current_idx, new_value, curve_data ):
        """
        Calculate auto tangents using this behavior.
        
        Args:
            curve: The animation curve
            current_idx: Index of current key
            new_value: The new value being calculated
            curve_data: The curve data object
            
        Returns:
            tuple: (angle, weight) for the auto tangent
        """
        raise NotImplementedError

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


class AutoSmoothStrategy( AutoTangentStrategy ):
    """Maya-style auto smooth tangent behavior using weighted averaging of slopes"""

    def calculate_tangents( self, curve, current_idx, new_value, curve_data, cached_positions = None ):
        """Calculate angles based on weighted average of surrounding slopes"""
        try:
            all_keys = curve_data.keys
            selected_keys = self.core.get_selected_keys( curve )

            # Find anchor keys
            left_anchor_idx, right_anchor_idx = self._find_anchor_keys( curve, current_idx )
            if left_anchor_idx is None or right_anchor_idx is None:
                return 0.0, 1.0

            # Determine if this is first or last selected key
            is_first_selected = current_idx == min( i for i, t in enumerate( all_keys ) if t in selected_keys )
            is_last_selected = current_idx == max( i for i, t in enumerate( all_keys ) if t in selected_keys )

            # Get previous key/value
            if is_first_selected:
                prev_time = all_keys[left_anchor_idx]
                prev_value = curve_data.values[left_anchor_idx]
                # print( "Key {0}: using time {1} (anchor)".format( all_keys[current_idx], prev_time ) )
            else:
                prev_time = all_keys[max( 0, current_idx - 1 )]
                prev_value = ( cached_positions[current_idx - 1] if cached_positions and current_idx - 1 in cached_positions
                            else curve_data.values[max( 0, current_idx - 1 )] )
                # print( "Key {0}: using time {1}".format( all_keys[current_idx], prev_time ) )

            # Get next key/value
            if is_last_selected:
                next_time = all_keys[right_anchor_idx]
                next_value = curve_data.values[right_anchor_idx]
                # print( "and {0} (anchor)".format( next_time ) )
            else:
                next_time = all_keys[min( len( all_keys ) - 1, current_idx + 1 )]
                next_value = ( cached_positions[current_idx + 1] if cached_positions and current_idx + 1 in cached_positions
                            else curve_data.values[min( len( all_keys ) - 1, current_idx + 1 )] )
                # print( "and {0}".format( next_time ) )

            dt_prev = all_keys[current_idx] - prev_time
            dt_next = next_time - all_keys[current_idx]

            if dt_prev == 0 or dt_next == 0:
                return 0.0, 1.0

            # Weight based on time distance
            prev_weight = dt_next / ( dt_prev + dt_next )
            next_weight = dt_prev / ( dt_prev + dt_next )

            # Calculate slopes
            prev_slope = ( new_value - prev_value ) / dt_prev if dt_prev != 0 else 0
            next_slope = ( next_value - new_value ) / dt_next if dt_next != 0 else 0

            # Weighted average of slopes
            weighted_slope = prev_slope * prev_weight + next_slope * next_weight

            # Convert to angle
            uniform_angle = math.degrees( math.atan( weighted_slope ) )

            # Calculate uniform weight using 1/3 rule
            weight = min( dt_prev, dt_next ) / 3.0
            weight = min( max( weight, 0.1 ), 10.0 )  # Clamp to Maya's valid range

            return uniform_angle, weight

        except Exception as e:
            print( "Error calculating smooth tangents: {0}".format( e ) )
            return 0.0, 1.0

    def _calculate_tangent_angles( self, curve, current_idx, new_value, curve_data ):
        """Calculate angles based on weighted average of surrounding slopes"""
        keys = curve_data.keys

        prev_time = keys[max( 0, current_idx - 1 )]
        prev_value = curve_data.get_running_value( current_idx - 1 ) or curve_data.values[max( 0, current_idx - 1 )]

        next_time = keys[min( len( keys ) - 1, current_idx + 1 )]
        next_value = curve_data.get_running_value( current_idx + 1 ) or curve_data.values[min( len( keys ) - 1, current_idx + 1 )]

        current_time = keys[current_idx]

        dt_prev = current_time - prev_time
        dt_next = next_time - current_time

        # Weight based on time distance
        prev_weight = dt_next / ( dt_prev + dt_next )
        next_weight = dt_prev / ( dt_prev + dt_next )

        # Calculate slopes instead of raw angles
        prev_slope = ( new_value - prev_value ) / dt_prev if dt_prev != 0 else 0
        next_slope = ( next_value - new_value ) / dt_next if dt_next != 0 else 0

        # Weighted average of slopes
        weighted_slope = prev_slope * prev_weight + next_slope * next_weight

        # Convert to angle
        uniform_angle = math.degrees( math.atan( weighted_slope ) )

        return uniform_angle, dt_prev, dt_next, ( new_value - prev_value ), ( next_value - new_value )

    def _calculate_tangent_weights( self, dt_prev, dt_next, dv_prev, dv_next ):
        """Calculate weights based on time distances and value changes"""
        base_weight_prev = dt_prev / 3.0
        base_weight_next = dt_next / 3.0

        value_rate_prev = abs( dv_prev / dt_prev ) if dt_prev != 0 else 0
        value_rate_next = abs( dv_next / dt_next ) if dt_next != 0 else 0

        if value_rate_prev > 1.0:
            base_weight_prev *= 1.0 / math.sqrt( value_rate_prev )
        if value_rate_next > 1.0:
            base_weight_next *= 1.0 / math.sqrt( value_rate_next )

        weight_prev = min( max( base_weight_prev, 0.1 ), 10.0 )
        weight_next = min( max( base_weight_next, 0.1 ), 10.0 )

        uniform_weight = ( weight_prev + weight_next ) / 2.0

        return uniform_weight


class AutoCatmullRomStrategy( AutoTangentStrategy ):
    """
    Catmull-Rom spline tangent behavior. 
    Creates C1 continuous curves passing through keyframe points.
    Uses surrounding points to determine slopes with tension parameter.
    """

    def __init__( self, core ):
        super( AutoCatmullRomStrategy, self ).__init__( core )
        self.tension = 0.0  # 0.5 is standard Catmull-Rom, 0.0 is tighter curves, 1.0 is looser

    def calculate_tangents( self, curve, current_idx, new_value, curve_data, cached_positions = None ):
        """Calculate tangents using Catmull-Rom spline with proper anchor handling"""
        try:
            all_keys = curve_data.keys
            selected_keys = self.core.get_selected_keys( curve )
            is_positive = self.core.current_blending_strategy == 'positive'

            # Find anchor keys
            left_anchor_idx, right_anchor_idx = self._find_anchor_keys( curve, current_idx )
            if left_anchor_idx is None or right_anchor_idx is None:
                return 0.0, 1.0

            # Get the values for surrounding points based on blend direction
            if is_positive:  # Blending toward right anchor (A2)
                last_selected_idx = max( i for i, t in enumerate( all_keys ) if t in selected_keys )
                if current_idx == last_selected_idx:
                    # Last selected key (K3) - use A2 and K2
                    prev_time = all_keys[current_idx - 1]
                    prev_value = ( cached_positions[current_idx - 1] if cached_positions and current_idx - 1 in cached_positions
                                else curve_data.values[current_idx - 1] )
                    next_time = all_keys[right_anchor_idx]
                    next_value = curve_data.values[right_anchor_idx]
                    # print( "Key {0}: using time {1} and {2}".format( all_keys[current_idx], prev_time, next_time ) )
                else:
                    # Other keys (K1, K2) - use adjacent keys
                    prev_time = all_keys[max( 0, current_idx - 1 )]
                    prev_value = ( cached_positions[current_idx - 1] if cached_positions and current_idx - 1 in cached_positions
                                else curve_data.values[max( 0, current_idx - 1 )] )
                    next_time = all_keys[min( len( all_keys ) - 1, current_idx + 1 )]
                    next_value = ( cached_positions[current_idx + 1] if cached_positions and current_idx + 1 in cached_positions
                                else curve_data.values[min( len( all_keys ) - 1, current_idx + 1 )] )
                    # print( "Key {0}: using time {1} and {2}".format( all_keys[current_idx], prev_time, next_time ) )
            else:  # Blending toward left anchor (A1)
                first_selected_idx = min( i for i, t in enumerate( all_keys ) if t in selected_keys )
                if current_idx == first_selected_idx:
                    # First selected key (K1) - use A1 and K2
                    prev_time = all_keys[left_anchor_idx]
                    prev_value = curve_data.values[left_anchor_idx]
                    next_time = all_keys[current_idx + 1]
                    next_value = ( cached_positions[current_idx + 1] if cached_positions and current_idx + 1 in cached_positions
                                else curve_data.values[current_idx + 1] )
                    # print( "Key {0}: using time {1} and {2}".format( all_keys[current_idx], prev_time, next_time ) )
                else:
                    # Other keys (K2, K3) - use adjacent keys
                    prev_time = all_keys[max( 0, current_idx - 1 )]
                    prev_value = ( cached_positions[current_idx - 1] if cached_positions and current_idx - 1 in cached_positions
                                else curve_data.values[max( 0, current_idx - 1 )] )
                    next_time = all_keys[min( len( all_keys ) - 1, current_idx + 1 )]
                    next_value = ( cached_positions[current_idx + 1] if cached_positions and current_idx + 1 in cached_positions
                                else curve_data.values[min( len( all_keys ) - 1, current_idx + 1 )] )
                    # print( "Key {0}: using time {1} and {2}".format( all_keys[current_idx], prev_time, next_time ) )

            # Calculate time intervals
            dt_prev = all_keys[current_idx] - prev_time
            dt_next = next_time - all_keys[current_idx]

            if dt_prev == 0 or dt_next == 0:
                return 0.0, 1.0

            # Calculate Catmull-Rom slope with tension parameter
            slope = ( ( 1.0 - self.tension ) *
                    ( ( next_value - new_value ) / dt_next +
                     ( new_value - prev_value ) / dt_prev ) / 2.0 )

            # Convert slope to angle
            angle = math.degrees( math.atan( slope ) )

            # Calculate weight using standard 1/3 rule
            weight = min( dt_prev, dt_next ) / 3.0
            weight = min( max( weight, 0.1 ), 10.0 )  # Clamp to Maya's valid range

            return angle, weight

        except Exception as e:
            print( "Error calculating Catmull-Rom tangents: {0}".format( e ) )
            return 0.0, 1.0

    def set_tension( self, value ):
        """
        Set the tension parameter for the Catmull-Rom spline.
        
        Args:
            value (float): Tension value. 
                          0.0 gives tighter curves
                          0.5 is standard Catmull-Rom
                          1.0 gives looser curves
        """
        self.tension = max( 0.0, min( 1.0, value ) )


class AutoEaseStrategy( AutoTangentStrategy ):
    """
    Auto tangent behavior that creates ease-in/out curves
    with minimal overshoot by reducing tangent angles
    near value extremes.
    """
    # TODO: errors if whole curve is selected, core issue

    def __init__( self, core ):
        super( AutoEaseStrategy, self ).__init__( core )
        self.ease_strength = 0.5  # Controls how much to reduce angles
        self.debug = True
        self.in_weight = None
        self.out_weight = None

    def calculate_tangents( self, curve, current_idx, new_value, curve_data, cached_positions = None ):
        """Calculate ease-in/out tangents with reduced angles near value extremes"""
        try:
            # Get key values and times
            all_keys = curve_data.keys
            selected_keys = self.core.get_selected_keys( curve )

            # Find anchor keys
            left_anchor_idx, right_anchor_idx = self._find_anchor_keys( curve, current_idx )
            if left_anchor_idx is None or right_anchor_idx is None:
                return 0.0, 1.0

            # Get previous/next key info
            times_values = self._get_surrounding_keys_info( curve_data, current_idx,
                                                         left_anchor_idx, right_anchor_idx,
                                                         all_keys, selected_keys,
                                                         cached_positions, new_value )
            if not times_values:
                return 0.0, 1.0

            # Calculate separate in/out weights using helper method
            if curve_data.is_weighted:
                # print( 'weighted' )
                self.in_weight, self.out_weight = self._calculate_tangent_weights( times_values )

            # Calculate angle using helper method
            angle = self._calculate_tangent_angles( times_values, new_value )

            # Return angle and weights as tuple for both in and out tangents
            return angle, self.in_weight, self.out_weight

        except Exception as e:
            print( "Error calculating ease tangents: {0}".format( e ) )
            return 0.0, 1.0

    def _get_surrounding_keys_info( self, curve_data, current_idx, left_anchor_idx,
                                 right_anchor_idx, all_keys, selected_keys,
                                 cached_positions, new_value ):
        """Get information about surrounding keys needed for calculations"""
        try:
            # Determine if this is first or last selected key
            is_first_selected = current_idx == min( i for i, t in enumerate( all_keys ) if t in selected_keys )
            is_last_selected = current_idx == max( i for i, t in enumerate( all_keys ) if t in selected_keys )

            # Get previous key/value
            if is_first_selected:
                prev_time = all_keys[left_anchor_idx]
                prev_value = curve_data.values[left_anchor_idx]
            else:
                prev_time = all_keys[max( 0, current_idx - 1 )]
                prev_value = ( cached_positions[current_idx - 1] if cached_positions and current_idx - 1 in cached_positions
                            else curve_data.values[max( 0, current_idx - 1 )] )

            # Get next key/value
            if is_last_selected:
                next_time = all_keys[right_anchor_idx]
                next_value = curve_data.values[right_anchor_idx]
            else:
                next_time = all_keys[min( len( all_keys ) - 1, current_idx + 1 )]
                next_value = ( cached_positions[current_idx + 1] if cached_positions and current_idx + 1 in cached_positions
                            else curve_data.values[min( len( all_keys ) - 1, current_idx + 1 )] )

            return {
                'prev_time': prev_time,
                'prev_value': prev_value,
                'next_time': next_time,
                'next_value': next_value,
                'current_time': all_keys[current_idx],
                'current_value': new_value
            }
        except Exception as e:
            print( "Error getting surrounding keys info: {0}".format( e ) )
            return None

    def _calculate_tangent_angles( self, times_values, new_value ):
        """Calculate angle considering ease in/out near extremes"""
        dt_prev = times_values['current_time'] - times_values['prev_time']
        dt_next = times_values['next_time'] - times_values['current_time']

        if dt_prev == 0 or dt_next == 0:
            return 0.0

        # Calculate basic slopes
        prev_slope = ( new_value - times_values['prev_value'] ) / dt_prev
        next_slope = ( times_values['next_value'] - new_value ) / dt_next

        # Find if current point is at a local extreme
        is_peak = ( ( new_value > times_values['prev_value'] and new_value > times_values['next_value'] ) or
                   ( new_value >= times_values['prev_value'] and new_value >= times_values['next_value'] ) )
        is_valley = ( ( new_value < times_values['prev_value'] and new_value < times_values['next_value'] ) or
                     ( new_value <= times_values['prev_value'] and new_value <= times_values['next_value'] ) )

        # Reduce slopes near extremes using ease_strength
        if is_peak or is_valley:
            prev_slope *= ( 1.0 - self.ease_strength )
            next_slope *= ( 1.0 - self.ease_strength )

        # Weight based on time distance
        prev_weight = dt_next / ( dt_prev + dt_next )
        next_weight = dt_prev / ( dt_prev + dt_next )

        # Weighted average of slopes
        avg_slope = prev_slope * prev_weight + next_slope * next_weight

        base_auto_angle = math.degrees( math.atan( avg_slope ) )

        # Apply flattening behavior
        in_angle, out_angle = self._calculate_tangent_angle_flattening( 
            times_values, base_auto_angle
        )

        return in_angle  # only return one angle, they should match at this point, this after blending to full auto

    def _calculate_tangent_angle_flattening( self, times_values, base_auto_angle ):
        """
        Calculate flattened angles by detecting when control points cross neighbor y-values.
        Returns tuple of (in_angle, out_angle)
        """
        try:
            in_triggered = False
            out_triggered = False

            # Get key values and times
            current_y = times_values['current_value']  # correct

            prev_y = times_values['prev_value']  # correct
            next_y = times_values['next_value']  # correct

            # x distance, correct
            dt_prev = times_values['current_time'] - times_values['prev_time']  # correct
            dt_next = times_values['next_time'] - times_values['current_time']  # correct

            # control points, aka weights
            if self.in_weight:
                # weighted case, use weight as control point
                cp_in_x = self.in_weight * -1  # flip to negative for in, accomodates get_cp_y method
                cp_out_x = self.out_weight
            else:
                # non-weighted case, use 1/3 weight
                cp_in_x = dt_prev / 3.0 * -1  # flip to negative for in, accomodates get_cp_y method
                cp_out_x = dt_next / 3.0

            def get_cp_y( angle, cp_x ):
                """In tangent is assumed to flipped to negative"""
                rad = math.radians( angle )
                dy = math.tan( rad ) * cp_x
                return current_y + dy

            def get_angle_to_y( target_y, cp_x, current_y ):
                """Calculate angle needed to hit target y value"""
                dy = target_y - current_y
                return math.degrees( math.atan( dy / cp_x ) )

            # Check in tangent
            in_cp_y = get_cp_y( base_auto_angle, cp_in_x )
            in_angle = base_auto_angle

            # Test if control point crosses prev key's y value
            if ( ( current_y >= prev_y and in_cp_y < prev_y ) or
                ( current_y <= prev_y and in_cp_y > prev_y ) ):
                flat_in_angle = get_angle_to_y( prev_y, cp_in_x, current_y )
                #
                if abs( flat_in_angle ) < abs( base_auto_angle ):
                    in_angle = flat_in_angle
                    in_triggered = True
                else:
                    # print( 'no - in' )
                    pass

            # Check out tangent similarly
            out_cp_y = get_cp_y( base_auto_angle, cp_out_x )
            out_angle = base_auto_angle

            # Test if control point crosses next key's y value
            if ( ( current_y >= next_y and out_cp_y < next_y ) or
                ( current_y <= next_y and out_cp_y > next_y ) ):
                # print( 'qualified out' )
                flat_out_angle = get_angle_to_y( next_y, cp_out_x, current_y )
                #
                if abs( flat_out_angle ) < abs( base_auto_angle ):
                    out_angle = flat_out_angle
                    out_triggered = True
                    # print( 'yes' )
                else:
                    # print( 'no - out' )
                    pass

            #
            if in_triggered:
                return in_angle, in_angle
            if out_triggered:
                return out_angle, out_angle
            #
            return in_angle, out_angle

        except Exception as e:
            print( "Error calculating flattened angles: {0}".format( e ) )
            return base_auto_angle, base_auto_angle

    def _calculate_tangent_weights( self, times_values ):
        """
        Calculate in/out weights based on time distances and value differences to neighboring keys.
        Weights will not go below 1/3 of their respective distances.
        """
        dt_prev = times_values['current_time'] - times_values['prev_time']
        dt_next = times_values['next_time'] - times_values['current_time']

        # Calculate value differences
        dv_prev = abs( times_values['current_value'] - times_values['prev_value'] )
        dv_next = abs( times_values['next_value'] - times_values['current_value'] )

        # Base weights with 1/3 rule
        base_in_weight = dt_prev / 3.0
        base_out_weight = dt_next / 3.0

        # Calculate value change rates
        value_rate_prev = dv_prev / dt_prev if dt_prev != 0 else 0
        value_rate_next = dv_next / dt_next if dt_next != 0 else 0

        # Adjust weights based on value rates, but don't go below 1/3
        in_weight = base_in_weight
        out_weight = base_out_weight

        if value_rate_prev > 1.0:
            in_weight = max( base_in_weight * ( 1.0 / math.sqrt( value_rate_prev ) ), base_in_weight )
        if value_rate_next > 1.0:
            out_weight = max( base_out_weight * ( 1.0 / math.sqrt( value_rate_next ) ), base_out_weight )

        # Calculate proximity but don't let it reduce below 1/3
        value_range_prev = max( abs( times_values['next_value'] - times_values['prev_value'] ), 0.001 )
        value_range_next = value_range_prev

        proximity_prev = 1.0 - min( dv_prev / value_range_prev, 1.0 )
        proximity_next = 1.0 - min( dv_next / value_range_next, 1.0 )

        # Apply proximity scaling but ensure we don't go below base weights
        in_weight = max( in_weight * ( 0.5 + 0.5 * ( 1.0 - proximity_prev ) ), base_in_weight )
        out_weight = max( out_weight * ( 0.5 + 0.5 * ( 1.0 - proximity_next ) ), base_out_weight )

        # Final clamping to Maya's valid range
        in_weight = min( max( in_weight, 0.1 ), 10.0 )
        out_weight = min( max( out_weight, 0.1 ), 10.0 )

        return in_weight, out_weight

    def _calculate_tangent_weight_flattening( self ):
        # may not be necessaryu as an extra step
        pass


def __DEV_STRATEGIES__():
    pass


class TriangleStaggeredBlendStrategy( TriangleDirectBlendStrategy ):
    """
    Blend strategy that staggers key movement based on proximity to target anchor,
    with Maya-style auto ease tangents during motion.
    """

    def __init__( self, core ):
        super( TriangleStaggeredBlendStrategy, self ).__init__( core )
        self.base_ease = 1.0
        self.ease_scale = 0.0
        self.debug = False

        # Range portion parameters, possibly make this more automated, less ditance = higher value, more ditance = smaller value
        self.min_range_portion = 0.47
        self.max_range_portion = 0.47
        # Local overrides for dynamic range calculation
        self._local_min_range_portion = self.min_range_portion
        self._local_max_range_portion = self.max_range_portion

        self.distance_threshold_min = 3
        self.distance_threshold_max = 100

        # Cache for pre-calculated values
        self._last_blend_factor = None
        self._cached_positions = {}
        self._cached_timings = {}

        # Auto tangent parameters
        self.transition_to_auto_end = 0.025  # Point where we finish blending to auto tangents
        self.transition_to_target_start = 0.999  # Point where we start blending to target tangents, 1.0 means stay auto

        # Set auto tangent behavior
        # self.auto_tangent_behavior = AutoSmoothStrategy( core )
        # self.auto_tangent_behavior = AutoCatmullRomStrategy( core )
        self.auto_tangent_behavior = AutoEaseStrategy( core )

        # TODO: gloablly try to integrate buffer curve snapshot before editing
        # TODO: doesnt pick up non selected key
        # TODO: anchor should reach weight the same time as the first key hits its target, not at the end of the blend
        # TODO: work in tangent weight rules from target class, preserve tangents when sliding in opposite direction and so on

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        """
        Main blend method using pre-calculation for position and tangents.
        """
        try:
            # Skip pre-calculation if blend factor hasn't changed
            if self._last_blend_factor != blend_factor:
                self._precalculate_curve_positions( curve, blend_factor )
                self._last_blend_factor = blend_factor

            # Get pre-calculated position
            if current_idx not in self._cached_positions:
                return current_value, None

            new_value = self._cached_positions[current_idx]

            # Calculate tangents using pre-calculated positions
            curve_data = self.core.get_curve_data( curve )
            new_tangents = self._calculate_tangents_with_precalc( curve, current_idx, curve_data )

            # Handle edge case where tangent calculation fails
            if not new_tangents and target_tangents:
                new_tangents = target_tangents

            if self.debug:
                self._log_debug_info( current_idx, blend_factor )

            return new_value, new_tangents

        except Exception as e:
            print( "Error in blend values: {0}".format( e ) )
            return current_value, None

    def _precalculate_curve_positions( self, curve, blend_factor ):
        """Pre-calculate positions for all selected keys."""
        try:
            # Initialize and validate
            curve_data = self._initialize_precalculation( curve )
            if not curve_data:
                return

            selected_keys = self.core.get_selected_keys( curve )
            if not selected_keys:
                return

            # Calculate timing data first
            self._calculate_timing_data( curve, curve_data, selected_keys, blend_factor >= 0 )

            # Then calculate positions using timing data
            self._calculate_positions( curve, curve_data, selected_keys, blend_factor )

        except Exception as e:
            print( "Error in position pre-calculation: {0}".format( e ) )
            self._reset_caches()

    def _initialize_precalculation( self, curve ):
        """Initialize caches and get curve data."""
        self._cached_positions.clear()
        self._cached_timings.clear()
        return self.core.get_curve_data( curve )

    def _calculate_timing_data( self, curve, curve_data, selected_keys, is_positive ):
        """Calculate and store timing data for each selected key."""
        target_strategy = self.core.get_current_targeting_strategy()

        for time in selected_keys:
            current_idx = curve_data.key_map[time]

            # Calculate basic timing values
            normalized_distance, dynamic_ease, range_portion = self._calculate_stagger_timing( 
                curve_data, current_idx, time, selected_keys, is_positive
            )

            # Get target tangents
            _, target_tangents = target_strategy.calculate_target_tangents( curve, time )

            # Store timing data
            self._store_timing_data( current_idx, normalized_distance, dynamic_ease,
                                  range_portion, target_tangents )

    def _store_timing_data( self, current_idx, normalized_distance, dynamic_ease,
                          range_portion, target_tangents ):
        """Store calculated timing data in cache."""
        self._cached_timings[current_idx] = {
            'normalized_distance': normalized_distance,
            'dynamic_ease': dynamic_ease,
            'range_portion': range_portion,
            'start': normalized_distance * ( 1.0 - range_portion ),
            'range_end': normalized_distance * ( 1.0 - range_portion ) + range_portion,
            'target_tangents': target_tangents
        }

    def _calculate_positions( self, curve, curve_data, selected_keys, blend_factor ):
        """Calculate and store positions for each selected key."""
        target_strategy = self.core.get_current_targeting_strategy()

        for time in selected_keys:
            current_idx = curve_data.key_map[time]
            current_value = curve_data.values[current_idx]

            # Get target values
            prev_target, next_target = target_strategy.calculate_target_value( curve, time )
            if prev_target is None or next_target is None:
                continue

            # Calculate new position
            target = next_target if blend_factor >= 0 else prev_target
            new_position = self._calculate_new_position( current_idx, current_value,
                                                      target, blend_factor )

            # Update states
            self._update_position_states( curve_data, current_idx, new_position )

    def _calculate_new_position( self, current_idx, current_value, target_value, blend_factor ):
        """Calculate new position using timing data."""
        timing = self._cached_timings[current_idx]
        return self._calculate_staggered_position( 
            current_value,
            target_value,
            blend_factor,
            timing
        )

    def _update_position_states( self, curve_data, current_idx, new_position ):
        """Update cached position and curve running state."""
        self._cached_positions[current_idx] = new_position
        curve_data.update_running_state( current_idx, new_position, None )

    def _calculate_tangents_with_precalc( self, curve, current_idx, curve_data ):
        """Calculate tangents with transitions using cached data."""
        try:
            # Validate and get basic data
            if not self._validate_tangent_calculation( current_idx ):
                return None

            timing_data = self._cached_timings[current_idx]
            new_value = self._cached_positions[current_idx]
            local_progress = self._calculate_local_progress( timing_data )

            # Get initial tangent values
            initial_tangents = self._get_initial_tangents( curve_data, current_idx )

            # Calculate auto tangents - now returns angle and separate weights
            auto_tangents = self._calculate_auto_tangents( curve, current_idx, new_value, curve_data )
            if not auto_tangents:
                return None

            auto_angle, auto_in_weight, auto_out_weight = auto_tangents

            # Calculate final tangents based on progress
            return self._calculate_final_tangents( local_progress, initial_tangents,
                                               auto_angle, auto_in_weight, auto_out_weight,
                                               timing_data )

        except Exception as e:
            print( "Error calculating tangents: {0}".format( e ) )
            return None

    def _validate_tangent_calculation( self, current_idx ):
        """Validate cached data exists for tangent calculation."""
        return ( current_idx in self._cached_positions and
                current_idx in self._cached_timings )

    def _calculate_local_progress( self, timing_data ):
        """Calculate progress within key's motion range."""
        abs_blend = abs( self._last_blend_factor )

        # Before motion
        if abs_blend <= timing_data['start']:
            return 0.0

        # After motion
        if abs_blend >= timing_data['range_end']:
            return 1.0

        # Within motion - calculate and ease progress
        progress = ( abs_blend - timing_data['start'] ) / timing_data['range_portion']
        return self._ease_progress( progress )

    def _ease_progress( self, progress ):
        """Apply ease in/out curve to progress."""
        if progress < 0.5:
            return 4.0 * pow( progress, 3 )
        else:
            scaled = progress - 1.0
            return 1.0 + ( 4.0 * pow( scaled, 3 ) )

    def _get_initial_tangents( self, curve_data, current_idx ):
        """Get initial tangent values."""
        return {
            'in_angle': curve_data.tangents['in_angles'][current_idx],
            'in_weight': curve_data.tangents['in_weights'][current_idx],
            'out_angle': curve_data.tangents['out_angles'][current_idx],
            'out_weight': curve_data.tangents['out_weights'][current_idx]
        }

    def _calculate_auto_tangents( self, curve, current_idx, new_value, curve_data ):
        """Calculate auto tangents using current behavior."""
        try:
            return self.auto_tangent_behavior.calculate_tangents( 
                curve,
                current_idx,
                new_value,
                curve_data,
                self._cached_positions  # Pass cached positions for better accuracy
            )
        except Exception as e:
            print( "Error calculating auto tangents: {0}".format( e ) )
            return None

    def _calculate_final_tangents( self, local_progress, initial_tangents,
                                auto_angle, auto_in_weight, auto_out_weight, timing_data ):
        """Calculate final tangents based on transition phase."""
        # Phase 1: Initial to auto transition
        if local_progress <= self.transition_to_auto_end:
            return self._calculate_initial_to_auto_transition( 
                local_progress, initial_tangents,
                auto_angle, auto_in_weight, auto_out_weight )

        # Phase 2: Pure auto tangents
        if local_progress < self.transition_to_target_start:
            return {
                'in': ( auto_angle, auto_in_weight ),
                'out': ( auto_angle, auto_out_weight )
            }

        # Phase 3: Auto to target transition
        if ( self.transition_to_target_start < 1.0 and
            local_progress >= self.transition_to_target_start and
            'target_tangents' in timing_data ):
            return self._calculate_auto_to_target_transition( 
                local_progress, auto_angle, auto_in_weight, auto_out_weight,
                timing_data['target_tangents'] )

        # Fallback to auto tangents
        return {
            'in': ( auto_angle, auto_in_weight ),
            'out': ( auto_angle, auto_out_weight )
        }

    def _calculate_initial_to_auto_transition( self, progress, initial_tangents,
                                            auto_angle, auto_in_weight, auto_out_weight ):
        """Calculate transition from initial to auto tangents."""
        blend_factor = progress / self.transition_to_auto_end
        blend_factor = blend_factor * blend_factor * ( 3 - 2 * blend_factor )

        # Blend angles
        in_angle = self._blend_angles( initial_tangents['in_angle'], auto_angle, blend_factor )
        out_angle = self._blend_angles( initial_tangents['out_angle'], auto_angle, blend_factor )

        # Blend weights separately for in/out
        in_weight = ( initial_tangents['in_weight'] * ( 1 - blend_factor ) +
                    auto_in_weight * blend_factor )
        out_weight = ( initial_tangents['out_weight'] * ( 1 - blend_factor ) +
                     auto_out_weight * blend_factor )

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    def _calculate_auto_to_target_transition( self, progress, auto_angle, auto_in_weight,
                                           auto_out_weight, target_tangents ):
        """Calculate transition from auto to target tangents."""
        blend_factor = ( ( progress - self.transition_to_target_start ) /
                       ( 1.0 - self.transition_to_target_start ) )
        blend_factor = blend_factor * blend_factor * ( 3 - 2 * blend_factor )

        # Blend angles
        in_angle = self._blend_angles( auto_angle, target_tangents['in'][0], blend_factor )
        out_angle = self._blend_angles( auto_angle, target_tangents['out'][0], blend_factor )

        # Blend weights separately for in/out
        in_weight = auto_in_weight * ( 1 - blend_factor ) + target_tangents['in'][1] * blend_factor
        out_weight = auto_out_weight * ( 1 - blend_factor ) + target_tangents['out'][1] * blend_factor

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    def _calculate_dynamic_range_portion( self, key_distance, max_distance ):
        """
        Calculate range portion dynamically based on distance between keys.
        
        Args:
            max_distance (float): Maximum distance between keys in frames
            
        Returns:
            float: Calculated range portion between min_range_portion and max_range_portion
        """

        # print( max_distance )

        # Prevent division by zero
        if max_distance == 0:
            return self.min_range_portion

        # Calculate relative distance (0-1)
        # Keys closer to target = smaller ratio
        distance_ratio = key_distance / max_distance
        '''
        print( "\nDebug:" )
        print( "key_distance: {0}".format( key_distance ) )
        print( "max_distance: {0}".format( max_distance ) )
        print( "distance_ratio: {0}".format( distance_ratio ) )
        '''

        # Smooth step interpolation for natural easing
        smoothed_ratio = distance_ratio * distance_ratio * ( 3 - 2 * distance_ratio )
        # smoothed_ratio = distance_ratio

        # Closer keys get smaller range portions, distant keys get larger portions
        range_portion = ( self._local_min_range_portion +
                        ( self._local_max_range_portion - self._local_min_range_portion ) * smoothed_ratio )

        if self.debug:
            print( "\n=== Dynamic Range Portion ===" )
            print( "Max distance between keys: {0}".format( max_distance ) )
            print( "Distance ratio: {0}".format( distance_ratio ) )
            print( "Smoothed ratio: {0}".format( smoothed_ratio ) )
            print( "Calculated range portion: {0}".format( range_portion ) )

        # print( "Calculated range portion: {0}".format( range_portion ) )
        return range_portion

    def _calculate_staggered_position( self, current_value, target_value, blend_factor, timing ):
        """Helper function to calculate staggered position with proper easing"""
        abs_blend = abs( blend_factor )

        # Before motion range
        if abs_blend <= timing['start']:
            return current_value

        # After motion range
        if abs_blend >= timing['range_end']:
            return target_value

        # Within motion range - calculate local progress
        local_progress = ( abs_blend - timing['start'] ) / timing['range_portion']

        # Apply ease in/out curve
        if local_progress < 0.5:
            eased_progress = 4.0 * pow( local_progress, 3 )
        else:
            scaled = local_progress - 1.0
            eased_progress = 1.0 + ( 4.0 * pow( scaled, 3 ) )

        # Blend between current and target
        return current_value * ( 1 - eased_progress ) + target_value * eased_progress

    def _calculate_stagger_timing( self, curve_data, current_idx, current_time, selected_keys, is_positive ):
        """
        Calculate timing values and dynamic easing for staggered movement.
        Returns:
            tuple: (normalized_distance, dynamic_ease_power, range_portion)
        """
        # Override for single key case
        if len( selected_keys ) == 1:
            self._local_min_range_portion = 1.0
            self._local_max_range_portion = 1.0
        else:
            self._local_min_range_portion = self.min_range_portion
            self._local_max_range_portion = self.max_range_portion

        # Find the target anchor key
        target_anchor_idx = None
        for i in range( current_idx + ( 1 if is_positive else -1 ),
                      len( curve_data.keys ) if is_positive else -1,
                      1 if is_positive else -1 ):
            if curve_data.keys[i] not in selected_keys:
                target_anchor_idx = i
                break

        if target_anchor_idx is None:
            return 0.0, self.base_ease, self.max_range_portion

        target_time = curve_data.keys[target_anchor_idx]

        # Calculate distances from each selected key to its target
        key_distances = []
        for key_time in selected_keys:
            distance = abs( target_time - key_time )
            key_distances.append( distance )

        # Get max of actual distances
        max_distance = max( key_distances )

        # Calculate distance for current key
        distance_to_target = abs( target_time - current_time )

        # Normalize distance: 0 = closest to target, 1 = furthest from target
        normalized_distance = distance_to_target / max_distance

        # Calculate dynamic ease power that increases with distance
        dynamic_ease = self.base_ease + ( normalized_distance * self.ease_scale )

        # Calculate dynamic range portion using this key's actual distance
        range_portion = self._calculate_dynamic_range_portion( distance_to_target, max_distance )

        if self.debug:
            print( "\n=== Stagger Timing ===" )
            print( "Target time: {0}".format( target_time ) )
            print( "Current time: {0}".format( current_time ) )
            print( "Distance to target: {0}".format( distance_to_target ) )
            print( "Max distance: {0}".format( max_distance ) )
            print( "Normalized distance: {0}".format( normalized_distance ) )
            print( "Dynamic ease power: {0}".format( dynamic_ease ) )
            print( "Range portion: {0}".format( range_portion ) )

        return normalized_distance, dynamic_ease, range_portion

    def reset( self ):
        """Reset cached data"""
        self._last_blend_factor = None
        self._cached_positions.clear()
        self._cached_timings.clear()
        super( TriangleStaggeredBlendStrategy, self ).reset()

    def _log_debug_info( self, current_idx, blend_factor ):
        """Log debug information if debug mode is enabled"""
        if not self.debug:
            return

        print( "\n=== Staggered Blend Debug ===" )
        print( "Current Index: {0}".format( current_idx ) )
        print( "Blend Factor: {0}".format( blend_factor ) )

        if current_idx in self._cached_timings:
            timing = self._cached_timings[current_idx]
            print( "Timing Data:" )
            print( "  Normalized Distance: {0:.3f}".format( timing['normalized_distance'] ) )
            print( "  Dynamic Ease: {0:.3f}".format( timing['dynamic_ease'] ) )
            print( "  Range Portion: {0:.3f}".format( timing['range_portion'] ) )
            print( "  Start: {0:.3f}".format( timing['start'] ) )
            print( "  Range End: {0:.3f}".format( timing['range_end'] ) )

        if current_idx in self._cached_positions:
            print( "Cached Position: {0}".format( self._cached_positions[current_idx] ) )
