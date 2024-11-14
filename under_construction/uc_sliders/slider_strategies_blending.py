# -*- coding: utf-8 -*-
"""
Provides blending strategies for animation curve manipulation.
Handles interpolation of values and tangents between animation states.
"""

import math
import numpy as np


class BlendStrategy:
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
            current_value = curve_data['values'][current_idx]

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
