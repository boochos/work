# -*- coding: utf-8 -*-
"""
Provides blending strategies for animation curve manipulation.
Handles interpolation of values and tangents between animation states.
"""

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np


class BlendStrategy( object ):
    """
    Base class for blending behaviors.
    Defines interface for different blending approaches.
    """

    @staticmethod
    def blend_tangents( curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        """
        Abstract method for blending between current and target tangents.
        
        Args:
            curve_data (dict): Current curve data including keys and tangent information
            current_idx (int): Index of current key being modified
            target_value (float): Target value being blended towards
            target_tangents (dict): Target tangent angles and weights
            ratio (float): Blend ratio between current and target (0-1)
            curve (str): Name of curve being modified
            
        Returns:
            dict: Blended tangent values with 'in' and 'out' data
        """
        raise NotImplementedError

    def reset( self ):
        """Reset any stored state"""
        pass


class RateBasedBlendStrategy( BlendStrategy ):
    """
    Blends tangents using a rate curve based on distance from target.
    Provides smoother transitions for larger value changes.
    """

    @staticmethod
    def blend_tangents( curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        """
        Blend tangents using rate curve based on distance to target.
        
        Args:
            curve_data (dict): Current curve data including keys and tangent information
            current_idx (int): Index of current key being modified
            target_value (float): Target value being blended towards
            target_tangents (dict): Target tangent angles and weights
            ratio (float): Blend ratio between current and target (0-1)
            curve (str): Name of curve being modified
            
        Returns:
            dict: Blended tangent values with 'in' and 'out' data
        """
        if not curve_data or not target_tangents:
            return None

        # Get current tangent values
        curr_in_angle = curve_data['tangents']['in_angles'][current_idx]
        curr_in_weight = curve_data['tangents']['in_weights'][current_idx]
        curr_out_angle = curve_data['tangents']['out_angles'][current_idx]
        curr_out_weight = curve_data['tangents']['out_weights'][current_idx]

        try:
            # Get current value for distance calculation
            current_value = cmds.keyframe( curve, q = True, time = ( curve_data['keys'][current_idx], ), eval = True )[0]

            # Calculate distance from target for rate curve
            distance = abs( target_value - current_value )

            # Get blend rate based on distance
            blend_rate = RateBasedBlendStrategy.rate_curve( distance )

            # Apply rate curve to ratio
            if ratio == 1.0:
                eased_ratio = ratio
            else:
                eased_ratio = ratio * blend_rate / 89.5

        except Exception as e:
            print( "Error accessing values: {}".format( e ) )
            eased_ratio = ratio

        # Blend angles with rate adjustment
        in_angle = RateBasedBlendStrategy.blend_angles( 
            curr_in_angle, target_tangents['in'][0], eased_ratio )
        out_angle = RateBasedBlendStrategy.blend_angles( 
            curr_out_angle, target_tangents['out'][0], eased_ratio )

        # Linear blend for weights
        in_weight = curr_in_weight * ( 1 - ratio ) + target_tangents['in'][1] * ratio
        out_weight = curr_out_weight * ( 1 - ratio ) + target_tangents['out'][1] * ratio

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    def reset( self ):
        """Reset any stored state"""
        pass

    @staticmethod
    def blend_angles( start_angle, end_angle, ratio ):
        """
        Blend between angles taking the shortest path around the circle.
        
        Args:
            start_angle (float): Starting angle in degrees
            end_angle (float): Ending angle in degrees
            ratio (float): Blend ratio between 0 and 1
            
        Returns:
            float: Blended angle value
        """
        # Calculate angle difference handling wrap-around
        diff = end_angle - start_angle
        if abs( diff ) > 180:
            if diff > 0:
                end_angle -= 360
            else:
                end_angle += 360

        # Linear interpolation
        result = start_angle * ( 1 - ratio ) + end_angle * ratio

        # Normalize result to 0-360 range
        while result < 0:
            result += 360
        while result >= 360:
            result -= 360

        return result

    @staticmethod
    def rate_curve( distance, power = 50 ):
        """
        Calculate angle change rate based on distance from target.
        
        Args:
            distance (float): Distance from target value (0-6561)
            power (int): Power for curve steepness, higher values give sharper falloff
            
        Returns:
            float: Rate of angle change (0-89.5)
        """
        x = min( distance / 6561.0, 1.0 )  # Normalize distance to 0-1 range
        return np.power( 1 - x, power ) * 89.5


class LinearBlendStrategy( BlendStrategy ):
    """
    Simple linear interpolation between tangent values.
    Useful as a baseline or for simple animations.
    """

    @staticmethod
    def blend_tangents( curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        """
        Blend tangents using simple linear interpolation.
        
        Args:
            curve_data (dict): Current curve data including keys and tangent information
            current_idx (int): Index of current key being modified
            target_value (float): Target value being blended towards
            target_tangents (dict): Target tangent angles and weights
            ratio (float): Blend ratio between current and target (0-1)
            curve (str): Name of curve being modified
            
        Returns:
            dict: Blended tangent values with 'in' and 'out' data
        """
        if not curve_data or not target_tangents:
            return None

        # Get current tangent values
        curr_in_angle = curve_data['tangents']['in_angles'][current_idx]
        curr_in_weight = curve_data['tangents']['in_weights'][current_idx]
        curr_out_angle = curve_data['tangents']['out_angles'][current_idx]
        curr_out_weight = curve_data['tangents']['out_weights'][current_idx]

        # Simple linear blend for angles
        in_angle = LinearBlendStrategy.blend_angles( 
            curr_in_angle, target_tangents['in'][0], ratio )
        out_angle = LinearBlendStrategy.blend_angles( 
            curr_out_angle, target_tangents['out'][0], ratio )

        # Linear blend for weights
        in_weight = curr_in_weight * ( 1 - ratio ) + target_tangents['in'][1] * ratio
        out_weight = curr_out_weight * ( 1 - ratio ) + target_tangents['out'][1] * ratio

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    @staticmethod
    def blend_angles( start_angle, end_angle, ratio ):
        """
        Linear blend between angles taking the shortest path.
        
        Args:
            start_angle (float): Starting angle in degrees
            end_angle (float): Ending angle in degrees
            ratio (float): Blend ratio between 0 and 1
            
        Returns:
            float: Blended angle value
        """
        # Calculate angle difference handling wrap-around
        diff = end_angle - start_angle
        if abs( diff ) > 180:
            if diff > 0:
                end_angle -= 360
            else:
                end_angle += 360

        # Linear interpolation
        result = start_angle * ( 1 - ratio ) + end_angle * ratio

        # Normalize result to 0-360 range
        while result < 0:
            result += 360
        while result >= 360:
            result -= 360

        return result

    def reset( self ):
        """Reset any stored state"""
        pass


class GeometricBlendStrategy( BlendStrategy ):

    def __init__( self ):
        BlendStrategy.__init__( self )
        self.debug = True

    def blend_tangents( self, curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        try:
            # Point C - current position
            current_time = curve_data['keys'][current_idx]
            current_value = cmds.keyframe( curve, q = True,
                                        time = ( current_time, ), eval = True )[0]

            # Point A is at current time but target value
            target_time = current_time  # A and C share same x position

            # Get anchor key (B) from blend_data
            if ratio >= 0:
                anchor_idx = curve_data['next_indices'][current_time]
            else:
                anchor_idx = curve_data['prev_indices'][current_time]

            # Get B position from anchor
            ref_time = curve_data['keys'][anchor_idx]
            ref_value = curve_data['values'][anchor_idx]

            if self.debug:
                print( "Triangle: A(right angle)=({0}, {1}), B(anchor)=({2}, {3}), C(current)=({4}, {5}), ratio={6}".format( 
                    current_time, target_value,  # Point A
                    ref_time, ref_value,  # Point B (anchor)
                    current_time, current_value,  # Point C
                    ratio
                ) )

            # Calculate angle at B
            opposite = abs( current_value - target_value )  # Vertical distance C to A
            adjacent = abs( ref_time - current_time )  # Horizontal distance B to A
            raw_angle = math.degrees( math.atan( opposite / adjacent ) )

            # Get start angle
            start_angle = curve_data['tangents']['in_angles'][current_idx]
            angle_at_B = -raw_angle if start_angle < 0 else raw_angle

            # Query current angle
            current_angle = cmds.keyTangent( curve, q = True, time = ( current_time, ), inAngle = True )[0]

            merge_mult = abs( ratio )

            if merge_mult >= 1.0:
                in_angle = target_tangents['in'][0]
                out_angle = target_tangents['out'][0]
            else:
                in_angle = start_angle * ( 1.0 - merge_mult ) + angle_at_B * merge_mult
                out_angle = start_angle * ( 1.0 - merge_mult ) + angle_at_B * merge_mult

            if self.debug:
                print( "Angles: target={0:.2f}, reference={1:.2f}, current={2:.2f}, start={3:.2f}, diff={4:.2f}, merge_mult={5:.2f}, ratio={6:.2f}{7}".format( 
                    target_tangents['in'][0],
                    angle_at_B,
                    current_angle,
                    start_angle,
                    current_angle - angle_at_B,
                    merge_mult,
                    ratio,
                    " (OVERRIDE)" if merge_mult >= 1.0 else ""
                ) )

            return {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return None


class TrigBasedBlendStrategy( BlendStrategy ):
    """
    Blends tangents using trigonometric functions.
    Provides smooth acceleration/deceleration based on sine/cosine curves.
    """

    def __init__( self ):
        BlendStrategy.__init__( self )  # Python 2 style super()
        # Initialize parameters
        self.distance_scale = 100.0
        self.phase_shift = 0.0
        self.frequency = 1.0
        self.amplitude = 1.0

    def reset( self ):
        """Reset any stored state"""
        pass

    @staticmethod
    def blend_tangents( curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        """
        Blend tangents using trig functions for smooth transitions.
        
        Args:
            curve_data (dict): Current curve data including keys and tangent information
            current_idx (int): Index of current key being modified
            target_value (float): Target value being blended towards
            target_tangents (dict): Target tangent angles and weights
            ratio (float): Blend ratio between current and target (0-1)
            curve (str): Name of curve being modified
            
        Returns:
            dict: Blended tangent values with 'in' and 'out' data
        """
        if not curve_data or not target_tangents:
            return None

        # Get current tangent values
        curr_in_angle = curve_data['tangents']['in_angles'][current_idx]
        curr_in_weight = curve_data['tangents']['in_weights'][current_idx]
        curr_out_angle = curve_data['tangents']['out_angles'][current_idx]
        curr_out_weight = curve_data['tangents']['out_weights'][current_idx]

        try:
            # Get current value for distance calculation
            current_value = curve_data['values'][current_idx]

            # Calculate distance from target for influence
            distance = abs( target_value - current_value )

            # Use cosine function to create smooth falloff
            # cos goes from 1 to 0 in 0 to pi/2 range
            # This creates a smooth deceleration as we get closer to target
            blend_influence = math.cos( ratio * math.pi * 0.5 )

            # Use sine function for the approach to target
            # sin goes from 0 to 1 in 0 to pi/2 range
            # This creates smooth acceleration towards target
            target_influence = math.sin( ratio * math.pi * 0.5 )

            # Combine influences based on distance
            # For larger distances, use more of the cosine curve (smoother initial movement)
            # For smaller distances, use more of the sine curve (smoother approach)
            distance_factor = min( distance / 100.0, 1.0 )  # Normalize distance influence
            final_ratio = blend_influence * distance_factor + target_influence * ( 1.0 - distance_factor )

            # Apply easing to final ratio
            eased_ratio = final_ratio

        except Exception as e:
            print( "Error in trig blending: {}".format( e ) )
            eased_ratio = ratio

        # Blend angles using final eased ratio
        in_angle = TrigBasedBlendStrategy.blend_angles( 
            curr_in_angle, target_tangents['in'][0], eased_ratio )
        out_angle = TrigBasedBlendStrategy.blend_angles( 
            curr_out_angle, target_tangents['out'][0], eased_ratio )

        # Weight blending with additional trig smoothing
        weight_ratio = math.sin( ratio * math.pi * 0.5 )  # Smooth weight transition
        in_weight = curr_in_weight * ( 1 - weight_ratio ) + target_tangents['in'][1] * weight_ratio
        out_weight = curr_out_weight * ( 1 - weight_ratio ) + target_tangents['out'][1] * weight_ratio

        return {
            'in': ( in_angle, in_weight ),
            'out': ( out_angle, out_weight )
        }

    @staticmethod
    def blend_angles( start_angle, end_angle, ratio ):
        """
        Blend between angles taking the shortest path around the circle.
        Uses same logic as base class but inherited here for completeness.
        
        Args:
            start_angle (float): Starting angle in degrees
            end_angle (float): Ending angle in degrees
            ratio (float): Blend ratio between 0 and 1
            
        Returns:
            float: Blended angle value
        """
        # Calculate angle difference handling wrap-around
        diff = end_angle - start_angle
        if abs( diff ) > 180:
            if diff > 0:
                end_angle -= 360
            else:
                end_angle += 360

        # Linear interpolation
        result = start_angle * ( 1 - ratio ) + end_angle * ratio

        # Normalize result to 0-360 range
        while result < 0:
            result += 360
        while result >= 360:
            result -= 360

        return result


class ElasticTrigStrategy( TrigBasedBlendStrategy ):
    """Specialized for bouncy, energetic movement"""

    def __init__( self ):
        TrigBasedBlendStrategy.__init__( self )  # Python 2 style super()
        self.frequency = 2.0
        self.amplitude = 1.2

    def blend_tangents( self, curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        # Always use elastic blend
        try:
            final_ratio = self._elastic_blend( ratio )
        except Exception as e:
            final_ratio = ratio
        # Continue with normal blending using elastic ratio...


class SnappyTrigStrategy( TrigBasedBlendStrategy ):
    """Specialized for sharp, precise movement"""

    def __init__( self ):
        TrigBasedBlendStrategy.__init__( self )  # Python 2 style super()
        self.frequency = 1.5
        self.amplitude = 0.9

    def blend_tangents( self, curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        # Always use exponential blend
        try:
            final_ratio = self._exponential_blend( ratio )
        except Exception as e:
            final_ratio = ratio
        # Continue with normal blending using snappy ratio...
