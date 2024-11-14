import imp

from under_construction.uc_sliders import slider_strategies_blending
from under_construction.uc_sliders import slider_strategies_targeting
import maya.cmds as cmds
import maya.mel as mel

imp.reload( slider_strategies_targeting )
imp.reload( slider_strategies_blending )


class SliderCore( object ):
    """Core class for data management"""

    def __init__( self ):
        """Initialize core data structures"""
        # Storage
        self.curve_cache = {}
        self.key_cache = {}
        self.tangent_cache = {}

        # State tracking
        self.current_time = None
        self.cache_key = None
        self.last_update_time = 0

        # Performance settings
        self.batch_size = 50
        self.cache_timeout = 5.0  # seconds

        # Initialize strategies
        self.targeting_strategies = {
            'direct': slider_strategies_targeting.DirectTargetStrategy(),
            'linear': slider_strategies_targeting.LinearTargetStrategy(),
            'spline': slider_strategies_targeting.SplineTargetStrategy()
        }
        self.current_targeting_strategy = 'linear'

        # Initialize blending strategies
        self.blending_strategies = {
            'rate': slider_strategies_blending.RateBasedBlendStrategy(),
            'linear': slider_strategies_blending.LinearBlendStrategy()
        }
        self.current_blending_strategy = 'rate'  # Default to rate-based blending

    def get_curves( self ):
        """Get and cache visible/selected curves"""

        # Get curves
        curves = cmds.keyframe( q = True, name = True, sl = True ) or []
        if not curves:
            ge = 'graphEditor1GraphEd'
            if cmds.animCurveEditor( ge, exists = True ):
                curves = cmds.animCurveEditor( ge, q = True, curvesShown = True ) or []

        # print( '___', curves )
        return curves

    def collect_curve_data( self, curve ):
        """Batch collect all data for a curve"""

        # Collect all curve data in one go
        data = {
            'keys': cmds.keyframe( curve, q = True, tc = True ) or [],
            'values': cmds.keyframe( curve, q = True, vc = True ) or [],
            'is_weighted': cmds.keyTangent( curve, q = True, weightedTangents = True )[0],
            'tangents': self._batch_get_tangents( curve )
        }

        # Create key map for quick lookups
        data['key_map'] = {time: i for i, time in enumerate( data['keys'] )}

        self.key_cache[curve] = data
        return data

    def _batch_get_tangents( self, curve ):
        """Batch collect all tangent data for a curve"""
        return {
            'in_angles': cmds.keyTangent( curve, q = True, ia = True ) or [],
            'in_weights': cmds.keyTangent( curve, q = True, iw = True ) or [],
            'out_angles': cmds.keyTangent( curve, q = True, oa = True ) or [],
            'out_weights': cmds.keyTangent( curve, q = True, ow = True ) or [],
            'in_types': cmds.keyTangent( curve, q = True, itt = True ) or [],
            'out_types': cmds.keyTangent( curve, q = True, ott = True ) or []
        }

    # Rename existing strategy methods to be more specific
    def set_targeting_strategy( self, strategy_name ):
        """Change the current targeting strategy"""
        if strategy_name in self.targeting_strategies:
            self.current_targeting_strategy = strategy_name
            return True
        return False

    def get_current_targeting_strategy( self ):
        """Get the current targeting strategy"""
        return self.targeting_strategies[self.current_targeting_strategy]

    def _set_blending_strategy( self, strategy_name ):
        """Change the current blend strategy"""
        if strategy_name in self.blending_strategies:
            self.current_blending_strategy = strategy_name
            return True
        return False

    def _get_current_blending_strategy( self ):
        """Get the current blend strategy"""
        return self.blending_strategies[self.current_blending_strategy]

    def calculate_prev_indices( self, times ):
        """Calculate previous key indices for all times"""
        indices = {}
        for i, time in enumerate( times ):
            indices[time] = i - 1 if i > 0 else i
        return indices

    def calculate_next_indices( self, times ):
        """Calculate next key indices for all times"""
        indices = {}
        for i, time in enumerate( times[:-1] ):
            indices[time] = i + 1
        # Handle last key
        indices[times[-1]] = len( times ) - 1
        return indices

    def _blend_tangents( self, curve_data, current_idx, target_value, target_tangents, ratio, curve ):
        """
        Blend tangents using current strategy
        
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
        strategy = self._get_current_blending_strategy()
        return strategy.blend_tangents( curve_data, current_idx, target_value,
                                     target_tangents, ratio, curve )

    def clear_caches( self ):
        """Clear all caches"""
        self.curve_cache.clear()
        self.key_cache.clear()
        self.tangent_cache.clear()
        self.cache_key = None

        # Reset current strategies
        if self.current_targeting_strategy in self.targeting_strategies:
            self.targeting_strategies[self.current_targeting_strategy].reset()
        if self.current_blending_strategy in self.blending_strategies:
            self.blending_strategies[self.current_blending_strategy].reset()
