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
    """Base class for blending behaviors"""

    def __init__( self, core ):
        self.core = core

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


class GeometricBlendStrategy( BlendStrategy ):
    """Uses geometric relationships for blending"""

    def __init__( self, core ):
        BlendStrategy.__init__( self, core )  # Python 2.7 style
        self.debug = True

    def blend_values( self, curve, current_idx, current_value, target_value, target_tangents, blend_factor ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_time = curve_data.keys[current_idx]

            # Point C - current position
            # Point A is at current time but target value
            target_time = current_time  # A and C share same x position

            # Get anchor key (B) from blend_data
            if blend_factor >= 0:
                anchor_idx = curve_data.next_indices[current_time]
            else:
                anchor_idx = curve_data.prev_indices[current_time]

            # Get B position from anchor
            ref_time = curve_data.keys[anchor_idx]
            ref_value = curve_data.values[anchor_idx]

            if self.debug:
                print( "Triangle: A(right angle)=({0}, {1}), B(anchor)=({2}, {3}), C(current)=({4}, {5}), ratio={6}".format( 
                    current_time, target_value,  # Point A
                    ref_time, ref_value,  # Point B (anchor)
                    current_time, current_value,  # Point C
                    blend_factor
                ) )

            # Calculate angle at B
            opposite = abs( current_value - target_value )  # Vertical distance C to A
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

            # Linear blend for value while maintaining geometric tangents
            new_value = current_value * ( 1 - merge_mult ) + target_value * merge_mult

            return new_value, {
                'in': ( in_angle, target_tangents['in'][1] ),
                'out': ( out_angle, target_tangents['out'][1] )
            }

        except Exception as e:
            print( "Error in geometric blending: {0}".format( e ) )
            return current_value, None
