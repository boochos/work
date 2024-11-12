import imp

from under_construction.uc_sliders import slider_strategies_targeting
import maya.cmds as cmds
import maya.mel as mel

imp.reload( slider_strategies_targeting )


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
        self.strategies = {
            'direct': slider_strategies_targeting.DirectTargetStrategy(),
            'linear': slider_strategies_targeting.LinearTargetStrategy(),
            'spline': slider_strategies_targeting.SplineTargetStrategy()
        }
        self.current_strategy = 'linear'

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

    def set_blend_strategy( self, strategy_name ):
        """Change the current blend strategy"""
        if strategy_name in self.strategies:
            self.current_strategy = strategy_name
            return True
        return False

    def get_current_strategy( self ):
        """Get the current blend strategy"""
        return self.strategies[self.current_strategy]

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

    def clear_caches( self ):
        """Clear all caches"""
        self.curve_cache.clear()
        self.key_cache.clear()
        self.tangent_cache.clear()
        self.cache_key = None

        # Reset current strategy
        if self.current_strategy in self.strategies:
            self.strategies[self.current_strategy].reset()
