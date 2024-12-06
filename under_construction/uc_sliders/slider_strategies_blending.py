# -*- coding: utf-8 -*-
"""
Provides blending strategies for animation curve manipulation.
Handles interpolation of values and tangents between animation states.
"""
# TODO: add strategy to perform a staggered blend, useful for when blending to left or right keys,
# TODO: cont. from above: should be able to designate a portion of the blend range to a key, portion would engage relative to the proximity in x of the anchor key
import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np


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


class TriangleStaggeredBlendStrategy__( TriangleDirectBlendStrategy ):
    """
    Blend strategy that staggers key movement based on proximity to targ
     et anchor.
    Keys closer to the target anchor begin blending sooner than those further away.
    """

    # TODO: create a blend to a theoretical curve the extends tangent to the x value of the opposing anchor,
    # TODO: cont. the opposing anchor points its tangent vertically to the position in y from the first anchor,
    # TODO: cont. the targets for the blending keys are positions along this curve.. may not be as useful as this one
    # TODO: create a dynamic tangent targets, ie auto behaviour, current behaviour has no relation to the curve shape
    def __init__( self, core ):
        super( TriangleStaggeredBlendStrategy, self ).__init__( core )
        self.base_ease = 0.0  # Base easing power
        self.ease_scale = 80.0  # How much distance affects easing power
        self.debug = False

        # Range portion parameters
        self.min_range_portion = 0.3  # Minimum range portion for large distances
        self.max_range_portion = 0.7  # Maximum range portion for small distances
        self.distance_threshold_min = 3  # Frame distance where we use max_range_portion
        self.distance_threshold_max = 100  # Frame distance where we use min_range_portion

    def _calculate_dynamic_range_portion( self, max_distance ):
        """
        Calculate range portion dynamically based on distance between keys.
        
        Args:
            max_distance (float): Maximum distance between keys in frames
            
        Returns:
            float: Calculated range portion between min_range_portion and max_range_portion
        """
        # Clamp distance to our threshold range
        clamped_distance = max( self.distance_threshold_min,
                             min( self.distance_threshold_max, max_distance ) )

        # Calculate how far we are between min and max thresholds (0-1)
        distance_ratio = ( clamped_distance - self.distance_threshold_min ) / \
                        float( self.distance_threshold_max - self.distance_threshold_min )

        # Invert ratio since we want higher values for smaller distances
        distance_ratio = 1.0 - distance_ratio

        # Smoothstep interpolation for a more natural transition
        smoothed_ratio = distance_ratio * distance_ratio * ( 3 - 2 * distance_ratio )

        # Lerp between min and max range portions
        range_portion = ( self.min_range_portion +
                        ( self.max_range_portion - self.min_range_portion ) * smoothed_ratio )

        if self.debug:
            print( "\n=== Dynamic Range Portion ===" )
            print( "Max distance between keys: {0}".format( max_distance ) )
            print( "Clamped distance: {0}".format( clamped_distance ) )
            print( "Distance ratio: {0}".format( distance_ratio ) )
            print( "Smoothed ratio: {0}".format( smoothed_ratio ) )
            print( "Calculated range portion: {0}".format( range_portion ) )

        return range_portion

    def _calculate_stagger_timing( self, curve_data, current_idx, current_time, selected_keys, is_positive ):
        """
        Calculate timing values and dynamic easing for staggered movement.
        Returns:
            tuple: (normalized_distance, dynamic_ease_power, range_portion)
        """
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
        max_distance = abs( max( selected_keys ) - min( selected_keys ) )

        if max_distance == 0:
            return 0.0, self.base_ease, self.max_range_portion

        # Calculate distance from this key to target anchor
        distance_to_target = abs( target_time - current_time )

        # Calculate dynamic range portion based on max distance
        range_portion = self._calculate_dynamic_range_portion( max_distance )

        # Normalize distance: 0 = closest to target, 1 = furthest from target
        normalized_distance = distance_to_target / max_distance

        # Calculate dynamic ease power that increases with distance
        dynamic_ease = self.base_ease + ( normalized_distance * self.ease_scale )

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

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            if not curve_data:
                return current_value, None

            selected_keys = self.core.get_selected_keys( curve )
            current_time = curve_data.keys[current_idx]
            is_positive = blend_factor >= 0

            if self.debug:
                print( "\n=== Key {0} ===".format( current_time ) )
                print( "Blend factor: {0}".format( blend_factor ) )

            # Get timing and easing values, now including dynamic range_portion
            normalized_distance, dynamic_ease, range_portion = self._calculate_stagger_timing( 
                curve_data, current_idx, current_time, selected_keys, is_positive
            )

            # Calculate when this key should start/end moving using dynamic range_portion
            start = normalized_distance * ( 1.0 - range_portion )
            range_end = start + range_portion

            abs_blend = abs( blend_factor )

            # Determine blend amount based on position in range
            if abs_blend <= start:
                adjusted_blend = 0.0
            elif abs_blend >= range_end:
                adjusted_blend = 1.0 if blend_factor > 0 else -1.0
            else:
                # Calculate local progress within this key's range
                local_progress = ( abs_blend - start ) / range_portion
                # Convert ease in/out circular
                if local_progress < 0.5:
                    eased_progress = 4.0 * pow( local_progress, 3 )
                else:
                    scaled = local_progress - 1.0
                    eased_progress = 1.0 + ( 4.0 * pow( scaled, 3 ) )
                adjusted_blend = eased_progress if blend_factor > 0 else -eased_progress

            if self.debug:
                print( "Normalized distance: {0:.3f}".format( normalized_distance ) )
                print( "Dynamic ease power: {0:.3f}".format( dynamic_ease ) )
                print( "Start: {0:.3f}".format( start ) )
                print( "Range end: {0:.3f}".format( range_end ) )
                print( "Local progress: {0:.3f}".format( 
                    local_progress if 'local_progress' in locals() else 0 ) )
                print( "Adjusted blend: {0:.3f}".format( adjusted_blend ) )

            return super( TriangleStaggeredBlendStrategy, self ).blend_values( 
                curve, current_idx, current_value, target_value, target_tangents, adjusted_blend
            )

        except Exception as e:
            print( "Error in staggered blend calculation: {0}".format( e ) )
            return current_value, None

    def set_range_portion_limits( self, min_val, max_val ):
        """Set the minimum and maximum range portion values"""
        self.min_range_portion = max( 0.1, min( 0.5, min_val ) )
        self.max_range_portion = max( 0.5, min( 1.0, max_val ) )

    def set_distance_thresholds( self, min_frames, max_frames ):
        """Set the frame distance thresholds for range portion calculation"""
        self.distance_threshold_min = max( 1, min_frames )
        self.distance_threshold_max = max( min_frames + 1, max_frames )


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


def __DEV_STRATEGIES__():
    pass


class TriangleStaggeredBlendStrategy( TriangleDirectBlendStrategy ):
    """
    Blend strategy that staggers key movement based on proximity to target anchor,
    with Maya-style auto ease tangents during motion.
    """

    def __init__( self, core ):
        super( TriangleStaggeredBlendStrategy, self ).__init__( core )
        self.base_ease = 0.0
        self.ease_scale = 80.0
        self.debug = False

        # Range portion parameters
        self.min_range_portion = 0.3
        self.max_range_portion = 0.7
        self.distance_threshold_min = 3
        self.distance_threshold_max = 100

        # Auto tangent parameters
        self.transition_to_auto_end = 0.05  # Point where we finish blending to auto tangents
        self.transition_to_target_start = 0.90  # Point where we start blending to target tangents

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            if not curve_data:
                return current_value, None

            selected_keys = self.core.get_selected_keys( curve )
            current_time = curve_data.keys[current_idx]
            is_positive = blend_factor >= 0

            if self.debug:
                print( "\n=== Key {0} ===".format( current_time ) )
                print( "Blend factor: {0}".format( blend_factor ) )

            # Get timing and easing values
            normalized_distance, dynamic_ease, range_portion = self._calculate_stagger_timing( 
                curve_data, current_idx, current_time, selected_keys, is_positive
            )

            # Calculate when this key should start/end moving using dynamic range_portion
            start = normalized_distance * ( 1.0 - range_portion )
            range_end = start + range_portion

            abs_blend = abs( blend_factor )

            # Calculate the adjusted blend factor for position
            if abs_blend <= start:
                adjusted_blend = 0.0
            elif abs_blend >= range_end:
                adjusted_blend = 1.0 if blend_factor > 0 else -1.0
            else:
                # Calculate local progress within this key's range
                local_progress = ( abs_blend - start ) / range_portion
                # Convert ease in/out circular
                if local_progress < 0.5:
                    eased_progress = 4.0 * pow( local_progress, 3 )
                else:
                    scaled = local_progress - 1.0
                    eased_progress = 1.0 + ( 4.0 * pow( scaled, 3 ) )
                adjusted_blend = eased_progress if blend_factor > 0 else -eased_progress

            # Calculate position using parent class
            new_value = super( TriangleStaggeredBlendStrategy, self ).blend_values( 
                curve, current_idx, current_value, target_value, target_tangents, adjusted_blend
            )[0]

            # Calculate tangents with auto ease
            new_tangents = self._blend_tangents_with_auto_ease( 
                curve, current_idx, current_value, new_value, target_tangents,
                abs( adjusted_blend )
            )

            if self.debug:
                print( "Normalized distance: {0:.3f}".format( normalized_distance ) )
                print( "Range portion: {0:.3f}".format( range_portion ) )
                print( "Adjusted blend: {0:.3f}".format( adjusted_blend ) )

            return new_value, new_tangents

        except Exception as e:
            print( "Error in staggered blend calculation: {0}".format( e ) )
            return current_value, None

    def _calculate_dynamic_range_portion( self, max_distance ):
        """
        Calculate range portion dynamically based on distance between keys.
        
        Args:
            max_distance (float): Maximum distance between keys in frames
            
        Returns:
            float: Calculated range portion between min_range_portion and max_range_portion
        """
        # Clamp distance to our threshold range
        clamped_distance = max( self.distance_threshold_min,
                             min( self.distance_threshold_max, max_distance ) )

        # Calculate how far we are between min and max thresholds (0-1)
        distance_ratio = ( clamped_distance - self.distance_threshold_min ) / \
                        float( self.distance_threshold_max - self.distance_threshold_min )

        # Invert ratio since we want higher values for smaller distances
        distance_ratio = 1.0 - distance_ratio

        # Smoothstep interpolation for a more natural transition
        smoothed_ratio = distance_ratio * distance_ratio * ( 3 - 2 * distance_ratio )

        # Lerp between min and max range portions
        range_portion = ( self.min_range_portion +
                        ( self.max_range_portion - self.min_range_portion ) * smoothed_ratio )

        if self.debug:
            print( "\n=== Dynamic Range Portion ===" )
            print( "Max distance between keys: {0}".format( max_distance ) )
            print( "Clamped distance: {0}".format( clamped_distance ) )
            print( "Distance ratio: {0}".format( distance_ratio ) )
            print( "Smoothed ratio: {0}".format( smoothed_ratio ) )
            print( "Calculated range portion: {0}".format( range_portion ) )

        return range_portion

    def _calculate_stagger_timing( self, curve_data, current_idx, current_time, selected_keys, is_positive ):
        """
        Calculate timing values and dynamic easing for staggered movement.
        Returns:
            tuple: (normalized_distance, dynamic_ease_power, range_portion)
        """
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
        max_distance = abs( max( selected_keys ) - min( selected_keys ) )

        if max_distance == 0:
            return 0.0, self.base_ease, self.max_range_portion

        # Calculate distance from this key to target anchor
        distance_to_target = abs( target_time - current_time )

        # Calculate dynamic range portion based on max distance
        range_portion = self._calculate_dynamic_range_portion( max_distance )

        # Normalize distance: 0 = closest to target, 1 = furthest from target
        normalized_distance = distance_to_target / max_distance

        # Calculate dynamic ease power that increases with distance
        dynamic_ease = self.base_ease + ( normalized_distance * self.ease_scale )

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

    def _blend_tangents_with_auto_ease( self, curve, current_idx, current_value, new_value, target_tangents, blend_factor ):
        """
        Calculate tangents with auto ease behavior, smoothly transitioning between:
        1. Initial tangents -> Auto tangents (first 10%)
        2. Auto tangents (10%-90%) 
        3. Auto tangents -> Target tangents (final 10%)
        """
        try:
            curve_data = self.core.get_curve_data( curve )

            # Get initial tangents
            initial_angle = curve_data.tangents['in_angles'][current_idx]
            initial_weight = curve_data.tangents['in_weights'][current_idx]

            # Calculate auto tangents
            uniform_angle, dt_prev, dt_next, dv_prev, dv_next = self._calculate_tangent_angles( 
                curve, current_idx, new_value )
            uniform_weight = self._calculate_tangent_weights( dt_prev, dt_next, dv_prev, dv_next )

            # Blend to auto tangents during first 10%
            if blend_factor <= self.transition_to_auto_end:
                local_blend = blend_factor / self.transition_to_auto_end
                # Smooth step interpolation
                local_blend = local_blend * local_blend * ( 3 - 2 * local_blend )

                final_angle = self._blend_angles( initial_angle, uniform_angle, local_blend )
                final_weight = initial_weight * ( 1 - local_blend ) + uniform_weight * local_blend

            # Use auto tangents between 10% and 90%
            elif blend_factor < self.transition_to_target_start:
                final_angle = uniform_angle
                final_weight = uniform_weight

            # Blend to target tangents in final 10%
            else:
                local_blend = ( blend_factor - self.transition_to_target_start ) / ( 1.0 - self.transition_to_target_start )
                local_blend = local_blend * local_blend * ( 3 - 2 * local_blend )

                final_angle = self._blend_angles( uniform_angle, target_tangents['in'][0], local_blend )
                final_weight = uniform_weight * ( 1 - local_blend ) + target_tangents['in'][1] * local_blend

            # Use same values for in/out tangents
            return {
                'in': ( final_angle, final_weight ),
                'out': ( final_angle, final_weight )
            }

        except Exception as e:
            print( "Error in auto ease tangent calculation: {0}".format( e ) )
            return None

    def _calculate_tangent_angles( self, curve, current_idx, new_value ):
        curve_data = self.core.get_curve_data( curve )
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
        # print( "\n=== Tangent Weight Calculation ===" )

        base_weight_prev = dt_prev / 3.0
        base_weight_next = dt_next / 3.0
        '''
        print( "Base weights (1/3 rule):" )
        print( "prev: {0:.3f}".format( base_weight_prev ) )
        print( "next: {0:.3f}".format( base_weight_next ) )
        '''
        value_rate_prev = abs( dv_prev / dt_prev ) if dt_prev != 0 else 0
        value_rate_next = abs( dv_next / dt_next ) if dt_next != 0 else 0
        '''
        print( "\nValue rates:" )
        print( "prev: {0:.3f}".format( value_rate_prev ) )
        print( "next: {0:.3f}".format( value_rate_next ) )
        '''
        if value_rate_prev > 1.0:
            base_weight_prev *= 1.0 / math.sqrt( value_rate_prev )
        if value_rate_next > 1.0:
            base_weight_next *= 1.0 / math.sqrt( value_rate_next )

        weight_prev = min( max( base_weight_prev, 0.1 ), 10.0 )
        weight_next = min( max( base_weight_next, 0.1 ), 10.0 )
        '''
        print( "\nAdjusted weights:" )
        print( "prev: {0:.3f}".format( weight_prev ) )
        print( "next: {0:.3f}".format( weight_next ) )
        '''
        uniform_weight = ( weight_prev + weight_next ) / 2.0
        # print( "Uniform weight: {0:.3f}".format( uniform_weight ) )

        return uniform_weight

    def _blend_to_targets( self, auto_angle, auto_weight, target_tangents, blend_progress ):
        """Blend from auto tangents to target tangents"""
        '''
        print( "\n=== Target Blending ===" )
        print( "Auto angle: {0:.3f} degrees".format( auto_angle ) )
        print( "Auto weight: {0:.3f}".format( auto_weight ) )
        print( "Target in angle: {0:.3f} degrees".format( target_tangents['in'][0] ) )
        print( "Target in weight: {0:.3f}".format( target_tangents['in'][1] ) )
        print( "Blend progress: {0:.3f}".format( blend_progress ) )
        '''

        if blend_progress >= self.tangent_transition_start:
            local_blend = ( blend_progress - self.tangent_transition_start ) / ( 1.0 - self.tangent_transition_start )
            local_blend = local_blend * local_blend * ( 3 - 2 * local_blend )

            final_angle = self._blend_angles( auto_angle, target_tangents['in'][0], local_blend )
            final_weight = auto_weight * ( 1 - local_blend ) + target_tangents['in'][1] * local_blend
            '''
            print( "\nBlending to targets:" )
            print( "Local blend: {0:.3f}".format( local_blend ) )
            print( "Final angle: {0:.3f} degrees".format( final_angle ) )
            print( "Final weight: {0:.3f}".format( final_weight ) )
            '''
            return final_angle, final_weight

        return auto_angle, auto_weight

    def _blend_to_auto_tangents( self, curve, curve_data, current_idx, new_value, blend_progress ):
        """
        Blend from initial tangents to auto-calculated tangents during the first portion of motion.
        
        Args:
            curve: The animation curve
            curve_data: Current curve data
            current_idx: Index of current key
            new_value: The new value being blended to
            blend_progress: Current blend progress (0-1)
            
        Returns:
            tuple: (blended_angle, blended_weight)
        """
        # Get initial tangents
        initial_angle = curve_data.tangents['in_angles'][current_idx]
        initial_weight = curve_data.tangents['in_weights'][current_idx]

        # Calculate auto tangents
        uniform_angle, dt_prev, dt_next, dv_prev, dv_next = self._calculate_tangent_angles( 
            curve, current_idx, new_value )
        uniform_weight = self._calculate_tangent_weights( dt_prev, dt_next, dv_prev, dv_next )

        # Blend during first portion
        if blend_progress <= self.transition_to_auto_end:
            local_blend = blend_progress / self.transition_to_auto_end
            # Smooth step interpolation
            local_blend = local_blend * local_blend * ( 3 - 2 * local_blend )

            final_angle = self._blend_angles( initial_angle, uniform_angle, local_blend )
            final_weight = initial_weight * ( 1 - local_blend ) + uniform_weight * local_blend
            return final_angle, final_weight

        return uniform_angle, uniform_weight
