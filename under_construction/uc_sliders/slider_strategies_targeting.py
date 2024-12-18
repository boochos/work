# -*- coding: utf-8 -*-

import math

import maya.cmds as cmds
import maya.mel as mel
import numpy as np

# TODO: add strategy to blend into tangent angle of anchor keys(L/R), a mix of direct and linear
# TODO: add strategy to blend into tangent but easing out to next keys position, theoretical curve, control points meet.


def __UTIL__():
    pass


def calculate_angle_multiplier( point_a, point_c, angle ):
    """
    Calculate how much longer an angled line would be compared to a horizontal line.
    Returns the ratio of angled_length/horizontal_length.
    
    Args:
        horizontal_distance: The base horizontal distance
        angle: The angle in degrees to calculate for
    """
    # Calculate lengths of triangle sides
    ac_length = abs( point_a[0] - point_c[0] )  # horizontal distance

    # Convert input angle to radians
    angle_rad = math.radians( angle )

    # Calculate AB length using trigonometry
    # In a right triangle: tan(θ) = opposite/adjacent = BC/AC
    # Therefore: AB = AC/cos(θ)
    ab_length = ac_length / math.cos( angle_rad )
    # print( angle_rad, ab_length, angle )

    # Return multiplier ratio
    return ab_length / ac_length if ac_length != 0 else 1.0


def __TARGETING_STRATEGIES__():
    pass


class TargetStrategy:
    """Base class for targeting strategies"""

    def __init__( self, core ):
        self.core = core
        self.force_one_third = False  # force construction of a curve that uses 1/3 rule, changes anchor tangent weights to a dif shape
        self.force_one_third_anchor = False
        #
        self.lock_weights_beyond_negative = True
        self.lock_weights_beyond_positive = True
        self.preserve_weights_positive = False
        self.preserve_weights_negative = False
        self.preserve_opposing_anchor = False  # When True, preserve anchor weights not in blend direction

        self.preserve_anchor_auto_tangents = False  # used for blending strategies

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

    def calculate_anchor_weights( self, curve, time ):
        """
        Calculate proper weights for anchor key tangents using the 1/3 rule.
        Only affects the tangent weight pointing toward the selected keys:
        - Left anchor: out tangent weight
        - Right anchor: in tangent weight
        
        Args:
            curve: The animation curve being processed
            time: Current time being evaluated
        
        Returns:
            tuple: (prev_anchor_data, next_anchor_data) where each is a dict with:
                  'time': key time
                  'weight': calculated weight
                  'tangent': 'in' or 'out' indicating which tangent to affect
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            if curve_data.is_weighted and self.force_one_third_anchor:
                current_idx = curve_data.key_map[time]
                all_keys = curve_data.keys

                # Use existing method to find anchor keys
                prev_key, next_key = self._get_anchor_indices( curve, current_idx )

                if prev_key is None or next_key is None:
                    return None, None

                # Calculate weights based on gaps to nearest selected key
                left_anchor_time = all_keys[prev_key]
                right_anchor_time = all_keys[next_key]

                # For left anchor's out tangent, use distance to next key
                left_gap = all_keys[prev_key + 1] - left_anchor_time
                left_weight = left_gap / 3.0

                # For right anchor's in tangent, use distance to previous key
                right_gap = right_anchor_time - all_keys[next_key - 1]
                right_weight = right_gap / 3.0

                left_anchor_data = {
                    'time': left_anchor_time,
                    'weight': left_weight,
                    'tangent': 'out'  # We only adjust the out tangent of left anchor
                }

                right_anchor_data = {
                    'time': right_anchor_time,
                    'weight': right_weight,
                    'tangent': 'in'  # We only adjust the in tangent of right anchor
                }

                return left_anchor_data, right_anchor_data
            else:
                # TODO: Not implemented. anchor needs to adjust but not to 1/3 rule
                return None, None

        except Exception as e:
            print( "Error calculating anchor tangent weights: {0}".format( e ) )
            return None, None

    def _get_anchor_indices( self, curve, current_idx ):
        """Find surrounding non-selected keys to use as anchors, returns indices"""
        curve_data = self.core.get_curve_data( curve )
        all_keys = curve_data.keys
        selected_keys = self.core.get_selected_keys( curve )

        left_anchor_idx = next( ( i for i in range( current_idx - 1, -1, -1 )
                      if all_keys[i] not in selected_keys ), None )
        right_anchor_idx = next( ( i for i in range( current_idx + 1, len( all_keys ) )
                      if all_keys[i] not in selected_keys ), None )

        return left_anchor_idx, right_anchor_idx

    def _get_neighbouring_points( self, curve, current_idx ):
        """ returns 2 points (x,y), left and right of current index"""
        left_index = max( 0, current_idx - 1 )  # Ensures we don't go below 0
        left_time = self.core.curve_data[curve].keys[left_index]
        left_value = self.core.curve_data[curve].values[left_index]
        left_point = [left_time, left_value]

        right_index = max( 0, current_idx + 1 )  # Ensures we don't go below 0
        right_time = self.core.curve_data[curve].keys[right_index]
        right_value = self.core.curve_data[curve].values[right_index]
        right_point = [right_time, right_value]

        return left_point, right_point

    def _calculate_one_third( self, curve, current_idx ):
        """
        Calculate in and out weights based on the 1/3 rule using actual neighboring keys.
        
        Args:
            curve: The animation curve
            current_idx: Index of current key
            
        Returns:
            tuple: (in_length, out_length) representing the weights
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            all_keys = curve_data.keys
            current_time = all_keys[current_idx]

            in_length = out_length = 1.0 / 3.0  # Default fallback

            # Calculate in weight based on distance to previous key
            if current_idx > 0:
                time_gap = current_time - all_keys[current_idx - 1]
                in_length = time_gap / 3.0

            # Calculate out weight based on distance to next key
            if current_idx < len( all_keys ) - 1:
                time_gap = all_keys[current_idx + 1] - current_time
                out_length = time_gap / 3.0

            return in_length, out_length

        except Exception as e:
            print( "Error calculating one third weights: {0}".format( e ) )
            return 1.0 / 3.0, 1.0 / 3.0  # Fallback to default if calculation fails

    def _calculate_tangent_weights_scaled( self, left_anchor_point, current_key, right_anchor_point, angle ):
        """
        Calculates Maya-style auto tangent weights using right triangle solving.
        
        Args:
            left_anchor_point: Tuple of (time, value) for the previous key, or None if no previous key
            current_key: Tuple of (time, value) for the current key
            right_anchor_point: Tuple of (time, value) for the next key, or None if no next key
            angle: Angle in degrees to use for triangle calculation
            
        Returns:
            Tuple of (in_weight, out_weight) for the current key
        """

        in_weight = out_weight = 0

        if left_anchor_point and right_anchor_point:
            # Determine if current key is closer to prev or halfway between prev and next
            mid_y = left_anchor_point[1] + ( right_anchor_point[1] - left_anchor_point[1] ) / 2
            use_prev = current_key[1] <= mid_y

            if use_prev:
                # Use left_anchor_point and current_key for calculation
                point_a = left_anchor_point
                point_b = current_key
                point_c = ( current_key[0], left_anchor_point[1] )  # right angle point
            else:
                # Use current_key and right_anchor_point for calculation
                point_a = right_anchor_point
                point_b = current_key
                point_c = ( current_key[0], right_anchor_point[1] )  # right angle point

            multiplier = calculate_angle_multiplier( point_a, point_c, angle )
            # print( 'mlt:', multiplier, current_key )

            # Calculate in_weight and out_weight using multiplier
            dt_in = current_key[0] - left_anchor_point[0] if left_anchor_point else 0
            dt_out = right_anchor_point[0] - current_key[0] if right_anchor_point else 0

            # Base weights (similar to original 1/3 rule)
            base_in = dt_in / 3.0 if left_anchor_point else 0
            base_out = dt_out / 3.0 if right_anchor_point else 0

            in_weight = base_in * multiplier
            out_weight = base_out * multiplier

            # print( "Triangle multiplier: %s" % multiplier )

        # print( "Final weights: in = %s, out = %s\n" % ( in_weight, out_weight ) )
        return in_weight, out_weight

    def reset( self ):
        """Reset any stored state"""
        pass


class DirectTargetStrategy( TargetStrategy ):
    """Blend directly to prev/next non-selected keys"""

    def __init__( self, core ):
        TargetStrategy.__init__( self, core )  # Python 2.7 style
        self.force_one_third = True  # force construction of a curve that uses 1/3 rule, changes anchor tangent weights to a dif shape
        self.force_one_third_anchor = True
        # shouldnt change for the most part
        self.lock_weights_beyond_negative = True
        self.lock_weights_beyond_positive = True
        #
        self.preserve_weights_positive = False
        self.preserve_weights_negative = False
        self.preserve_opposing_anchor = True  # Enable directional preservation for direct targeting
        self.preserve_anchor_auto_tangents = True

    def calculate_target_value( self, curve, time ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )
            selected_keys = self.core.get_selected_keys( curve )

            # Start with current value as default targets
            current_value = curve_data.get_value( current_idx )
            left_target = right_target = current_value

            # Find previous non-selected key
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    left_target = curve_data.values[i]
                    break

            # Find next non-selected key
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    right_target = curve_data.values[i]
                    break

            return left_target, right_target

        except Exception as e:
            print( "Error in direct target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        """Use flat tangents (0 angle) as targets"""
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )

            if curve_data.is_weighted:
                if self.force_one_third:
                    # Calculate 1/3 rule weights for weighted curves
                    in_weight, out_weight = self._calculate_one_third( curve, current_idx )
                else:
                    pass
                    # TODO: NOT IMPLEMENTED
            else:
                # Use default weight for non-weighted curves
                in_weight = out_weight = 1.0

            # Keep angles flat (0) regardless of weighting
            flat_tangents = {
                'in': ( 0.0, in_weight ),
                'out': ( 0.0, out_weight )
            }

            return flat_tangents, flat_tangents

        except Exception as e:
            print( "Error calculating direct target tangents: {0}".format( e ) )
            return None, None


class LinearTargetStrategy( TargetStrategy ):
    """Blend towards or away from linear interpolation"""

    def __init__( self, core ):
        TargetStrategy.__init__( self, core )  # Python 2.7 style
        self.force_one_third = True  # force construction of a curve that uses 1/3 rule, changes anchor tangent weights to a dif shape
        self.force_one_third_anchor = True
        # shouldnt change for the most part
        self.lock_weights_beyond_negative = True
        self.lock_weights_beyond_positive = True
        #
        self.preserve_weights_positive = True
        self.preserve_weights_negative = False
        self.preserve_anchor_auto_tangents = True

    def calculate_target_value( self, curve, time ):
        try:
            curve_data = self.core.get_curve_data( curve )
            current_idx = curve_data.get_key_index( time )
            selected_keys = self.core.get_selected_keys( curve )

            current_value = curve_data.get_value( current_idx )

            # Find surrounding non-selected keys
            left_anchor_idx = right_anchor_idx = None
            left_anchor_time = left_anchor_value = None
            right_anchor_time = right_anchor_value = None

            # Find previous non-selected key
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    left_anchor_idx = i
                    left_anchor_time = curve_data.keys[i]
                    left_anchor_value = curve_data.values[i]
                    break

            # Find next non-selected key
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    right_anchor_idx = i
                    right_anchor_time = curve_data.keys[i]
                    right_anchor_value = curve_data.values[i]
                    break

            # Calculate targets if we found both surrounding keys
            if left_anchor_idx is not None and right_anchor_idx is not None:
                # Calculate linear interpolation
                time_ratio = ( time - left_anchor_time ) / ( right_anchor_time - left_anchor_time )
                linear_value = left_anchor_value + ( right_anchor_value - left_anchor_value ) * time_ratio

                # Calculate delta from linear
                delta = current_value - linear_value

                # For negative (towards linear), use linear value
                # For positive (away from linear), exaggerate from linear
                '''
                # this doesnt work for this strategy, in its current state, relic from direct methodology
                return linear_value, current_value + delta
                '''
                return linear_value, linear_value

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
            left_anchor_idx = right_anchor_idx = None
            for i in range( current_idx - 1, -1, -1 ):
                if curve_data.keys[i] not in selected_keys:
                    left_anchor_idx = i
                    break
            for i in range( current_idx + 1, len( curve_data.keys ) ):
                if curve_data.keys[i] not in selected_keys:
                    right_anchor_idx = i
                    break

            if left_anchor_idx is not None and right_anchor_idx is not None:
                # Calculate angle of linear path
                dx = curve_data.keys[right_anchor_idx] - curve_data.keys[left_anchor_idx]
                dy = curve_data.values[right_anchor_idx] - curve_data.values[left_anchor_idx]
                linear_angle = math.degrees( math.atan2( dy, dx ) )

                #
                #
                # Handle weighted tangents
                if curve_data.is_weighted:
                    if self.force_one_third:
                        # Calculate weights based on 1/3 rule
                        in_weight, out_weight = self._calculate_one_third( curve, current_idx )
                    else:
                        # Preserve existing weights
                        in_weight = curve_data.tangents['in_weights'][current_idx]
                        out_weight = curve_data.tangents['out_weights'][current_idx]
                else:
                    # Use default unit weight for non-weighted curves
                    in_weight = out_weight = 1.0

                # Create target tangents with calculated angle and weights
                target_tangents = {
                    'in': ( linear_angle, in_weight ),
                    'out': ( linear_angle, out_weight )
                }
                #
                #
                #

                # return negative_tangents, negative_tangents # removed, refactor from adding wegihted tangent support
                return target_tangents, target_tangents

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
        self.force_one_third = True  # force construction of a curve that uses 1/3 rule, changes anchor tangent weights to a dif shape
        self.force_one_third_anchor = True
        # shouldnt change for the most part
        self.lock_weights_beyond_negative = True
        self.lock_weights_beyond_positive = True
        #
        self.preserve_weights_positive = True
        self.preserve_weights_negative = False

    def calculate_target_value( self, curve, time ):
        """Calculate bezier-based value for blending"""
        try:
            current_idx = self.core.get_curve_data( curve ).key_map[time]

            left_anchor_idx, right_anchor_idx = self._get_anchor_indices( curve, current_idx )
            if left_anchor_idx is not None and right_anchor_idx is not None:
                curve_data, p0, p3 = self._get_curve_points( curve, left_anchor_idx, right_anchor_idx )
                p1, p2, gap = self._calculate_control_points( curve_data, p0, p3, left_anchor_idx, right_anchor_idx )

                '''
                print( "P0: time={0}, value={1}".format( p0[0], p0[1] ) )
                print( "P1: time={0}, value={1}".format( p1[0], p1[1] ) )
                print( "P2: time={0}, value={1}".format( p2[0], p2[1] ) )
                print( "P3: time={0}, value={1}".format( p3[0], p3[1] ) )

                print( "p0=({0}, {1})".format( p0[0], p0[1] ) )
                print( "p1=({0}, {1})".format( p1[0], p1[1] ) )
                print( "p2=({0},{1})".format( p2[0], p2[1] ) )
                print( "p3=({0}, {1})".format( p3[0], p3[1] ) )
                '''
                # Calculate t parameter and bezier value
                # t = ( time - p0[0] ) / gap
                # Calculate correct t parameter using Newton's method
                t = self._find_t_for_time( time, p0, p1, p2, p3 )
                mt = 1.0 - t
                mt2 = mt * mt
                mt3 = mt2 * mt
                t2 = t * t
                t3 = t2 * t

                bezier_value = ( p0[1] * mt3 +
                              3.0 * p1[1] * mt2 * t +
                              3.0 * p2[1] * mt * t2 +
                              p3[1] * t3 )

                return bezier_value, bezier_value

            return curve_data.values[current_idx], curve_data.values[current_idx]

        except Exception as e:
            print( "Error in spline target calculation: {0}".format( e ) )
            return None, None

    def calculate_target_tangents( self, curve, time ):
        """Calculate tangents for the bezier curve"""
        try:
            current_idx = self.core.get_curve_data( curve ).key_map[time]
            if not self.core.get_curve_data( curve ).tangents:
                return None, None

            left_anchor_idx, right_anchor_idx = self._get_anchor_indices( curve, current_idx )
            if left_anchor_idx is not None and right_anchor_idx is not None:
                curve_data, p0, p3 = self._get_curve_points( curve, left_anchor_idx, right_anchor_idx )
                p1, p2, gap = self._calculate_control_points( curve_data, p0, p3, left_anchor_idx, right_anchor_idx )

                # Calculate t for current time
                # t = ( time - p0[0] ) / gap
                # Calculate correct t parameter using Newton's method
                t = self._find_t_for_time( time, p0, p1, p2, p3 )
                mt = 1.0 - t

                # Calculate intermediate points
                AB_x = ( mt * p0[0] ) + ( t * p1[0] )
                AB_y = ( mt * p0[1] ) + ( t * p1[1] )

                BC_x = ( mt * p1[0] ) + ( t * p2[0] )
                BC_y = ( mt * p1[1] ) + ( t * p2[1] )

                CD_x = ( mt * p2[0] ) + ( t * p3[0] )
                CD_y = ( mt * p2[1] ) + ( t * p3[1] )

                # Calculate tangent points
                tan_in_x = ( mt * AB_x ) + ( t * BC_x )
                tan_in_y = ( mt * AB_y ) + ( t * BC_y )

                tan_out_x = ( mt * BC_x ) + ( t * CD_x )
                tan_out_y = ( mt * BC_y ) + ( t * CD_y )

                point_x = ( mt * tan_in_x ) + ( t * tan_out_x )
                point_y = ( mt * tan_in_y ) + ( t * tan_out_y )

                # Calculate x and y lengths once
                in_xlength = point_x - tan_in_x
                in_ylength = point_y - tan_in_y
                out_xlength = tan_out_x - point_x
                out_ylength = tan_out_y - point_y

                # Calculate angles
                in_tan = in_ylength / in_xlength
                in_angle = math.degrees( math.atan( in_tan ) )

                out_tan = out_ylength / out_xlength
                out_angle = math.degrees( math.atan( out_tan ) )

                # Calculate lengths based on scenario
                if curve_data.is_weighted:
                    if self.force_one_third:
                        in_length, out_length = self._calculate_one_third( curve, current_idx )
                        # left_point, right_point = self._get_neighbouring_points( curve, current_idx )
                        # in_length, out_length = self._calculate_tangent_weights_scaled( left_point, [ point_x, point_y ], right_point, in_angle )
                    else:
                        # TODO: this should use 1/3 rule on all but tangents facing the anchors. likely need a dif calculation
                        in_length, out_length = self._calculate_one_third( curve, current_idx )
                else:
                    # Calculate standard lengths using stored x/y values
                    in_length = math.sqrt( in_xlength * in_xlength + in_ylength * in_ylength )
                    out_length = math.sqrt( out_xlength * out_xlength + out_ylength * out_ylength )

                negative_tangents = {
                    'in': ( in_angle, in_length ),
                    'out': ( out_angle, out_length )
                }

                return negative_tangents, negative_tangents

            return None, None

        except Exception as e:
            print( "Error calculating tangents: {0}".format( e ) )
            return None, None

    def _calculate_one_third( self, curve, current_idx ):
        """
        Calculate in and out weights based on the 1/3 rule using actual neighboring keys.
        Returns tuple of (in_length, out_length) representing the weights.
        """
        try:
            curve_data = self.core.get_curve_data( curve )
            all_keys = curve_data.keys
            current_time = all_keys[current_idx]

            in_length = out_length = 1.0 / 3.0  # Default fallback

            # Calculate in weight based on distance to previous key
            if current_idx > 0:
                time_gap = current_time - all_keys[current_idx - 1]
                in_length = time_gap / 3.0

            # Calculate out weight based on distance to next key
            if current_idx < len( all_keys ) - 1:
                time_gap = all_keys[current_idx + 1] - current_time
                out_length = time_gap / 3.0

            return in_length, out_length

        except Exception as e:
            print( "Error calculating one third weights: {0}".format( e ) )
            return 1.0 / 3.0, 1.0 / 3.0  # Fallback to default if calculation fails

    def _get_curve_points( self, curve, prev_idx, next_idx ):
        """Get anchor points and curve data"""
        curve_data = self.core.get_curve_data( curve )
        p0 = [curve_data.keys[prev_idx], curve_data.values[prev_idx]]
        p3 = [curve_data.keys[next_idx], curve_data.values[next_idx]]

        return ( curve_data, p0, p3 )

    def _calculate_control_points( self, curve_data, p0, p3, left_anchor_idx, right_anchor_idx ):
        """Calculate bezier control points P1 and P2"""
        """
        # Alternate method. Below values relate to position of their associated key, x value is x*8, y value is y*(1/3.0)
        # use this to get control points
        print(cmds.getAttr(curve_node + ".keyTanInX[0]"))
        print(cmds.getAttr(curve_node + ".keyTanInY[0]"))
        print(cmds.getAttr(curve_node + ".keyTanOutX[0]"))
        print(cmds.getAttr(curve_node + ".keyTanOutY[0]"))
        # could use this to set them or reverse engineer the math for the raw weight value, 
        # will actually need to figure out the math to set the target weight value
        cmds.keyTangent(curve_node, ox= 0.0, t=(0.0,)) 
        cmds.keyTangent(curve_node, oy= -3.0, t=(0.0,))
        
        
        """
        gap = p3[0] - p0[0]
        tangent_data = curve_data.tangents

        # Get tangent data
        left_anchor_out_angle = math.radians( tangent_data['out_angles'][left_anchor_idx] )
        left_anchor_out_weight = tangent_data['out_weights'][left_anchor_idx]
        right_anchor_in_angle = math.radians( tangent_data['in_angles'][right_anchor_idx] )
        right_anchor_in_weight = tangent_data['in_weights'][right_anchor_idx]

        '''
        print( "\nTangent Values:" )
        print( "left_anchor_out_angle:", math.degrees( left_anchor_out_angle ) )
        print( "left_anchor_out_weight :", left_anchor_out_weight  )
        print( "right_anchor_in_angle:", math.degrees( right_anchor_in_angle ) )
        print( "right_anchor_in_weight :", right_anchor_in_weight  )
        '''

        # Calculate P1
        if curve_data.is_weighted and not self.force_one_third:
            # First calculate relative offsets
            time_offset = math.cos( left_anchor_out_angle ) * left_anchor_out_weight
            # print( '__time offset', time_offset )
            value_offset = math.sin( left_anchor_out_angle ) * left_anchor_out_weight
            # print( '__value offset', value_offset )

            x = p0[0] + time_offset
            y = p0[1] + value_offset
            p1 = [x, y]
        else:
            # Non-weighted uses standard 1/3 gap
            time_adj = gap / 3.0
            opo = math.tan( left_anchor_out_angle ) * time_adj
            p1 = [p0[0] + time_adj, p0[1] + opo]

        # Calculate P2
        if curve_data.is_weighted and not self.force_one_third:
            # First calculate relative offsets
            time_offset = math.cos( right_anchor_in_angle ) * right_anchor_in_weight
            # print( '__time offset', time_offset )
            value_offset = math.sin( right_anchor_in_angle ) * right_anchor_in_weight
            # print( '__value offset', value_offset )

            x = p3[0] - time_offset
            y = p3[1] - value_offset
            p2 = [x, y]
        else:
            # Non-weighted uses standard 1/3 gap
            time_adj = gap / 3.0
            opo = math.tan( right_anchor_in_angle ) * time_adj
            p2 = [p3[0] - time_adj, p3[1] - opo]

        '''
        print( "\nCalculated Points:" )
        print( "P0:", p0 )
        print( "P1:", p1 )
        print( "P2:", p2 )
        print( "P3:", p3 )
        '''

        return p1, p2, gap

    def _bezier_derivative( self, t, p0, p1, p2, p3 ):
        """Calculate derivative of Bezier curve at t (for x component only)"""
        mt = 1.0 - t
        mt2 = mt * mt
        t2 = t * t

        dx = 3.0 * ( 
            p1[0] * mt2 - p0[0] * mt2 +
            p2[0] * 2 * mt * t - p1[0] * 2 * mt * t +
            p3[0] * t2 - p2[0] * t2
        )
        return dx

    def _find_t_for_time( self, time, p0, p1, p2, p3, tolerance = 1e-7, max_iterations = 10 ):
        """Find t value for given time using Newton's method"""
        # Initial guess using linear interpolation
        t = ( time - p0[0] ) / ( p3[0] - p0[0] )

        for _ in range( max_iterations ):
            # Calculate current x value
            mt = 1.0 - t
            mt2 = mt * mt
            mt3 = mt2 * mt
            t2 = t * t
            t3 = t2 * t

            x = ( p0[0] * mt3 +
                 3.0 * p1[0] * mt2 * t +
                 3.0 * p2[0] * mt * t2 +
                 p3[0] * t3 )

            if abs( x - time ) < tolerance:
                return t

            dx = self._bezier_derivative( t, p0, p1, p2, p3 )
            if abs( dx ) < 1e-10:  # Avoid division by zero
                break

            t = t - ( x - time ) / dx
            t = max( 0.0, min( 1.0, t ) )  # Clamp to [0,1]

        return t


'''
curve_node = 'pCube1_translateX109'
#
cmds.keyTangent(curve_node, ox= 0.0, t=(0.0,)) 
cmds.keyTangent(curve_node, oy= -3.0, t=(0.0,))

# left anchor key
kxy = cmds.getAttr(curve_node + ".keyTimeValue[0]")[0]
x = kxy[0] + (cmds.getAttr(curve_node + ".keyTanOutX[0]") *8)
y = kxy[1] + (cmds.getAttr(curve_node + ".keyTanOutY[0]") *(1.0/3.0))
print(x,y)
# right anchor key
kxy = cmds.getAttr(curve_node + ".keyTimeValue[2]")[0]
x = kxy[0] - (cmds.getAttr(curve_node + ".keyTanInX[2]") *8)
y = kxy[1] - ( cmds.getAttr( curve_node + ".keyTanInY[2]" ) * ( 1.0 / 3.0 ) )
print( x, y )
'''
