import imp

import maya.cmds as cmds
import maya.mel as mel

import strategies
imp.reload( strategies )


class BlendToolCore( object ):
    """Core singleton for centralized data management"""
    _instance = None

    def __init__( self ):
        """Initialize called automatically when instance is created"""
        self._initialize()

    def __new__( cls ):
        if cls._instance is None:
            cls._instance = super( BlendToolCore, cls ).__new__( cls )
            cls._instance._initialize()
        return cls._instance

    def _initialize( self ):
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
            'direct': strategies.DirectKeyBlendStrategy(),
            'linear': strategies.LinearBlendStrategy(),
            'spline': strategies.SplineBlendStrategy()
        }
        self.current_strategy = 'spline'

    def get_curves( self ):
        """Get and cache visible/selected curves"""
        cache_key = ( 
            cmds.currentTime( q = True ),
            tuple( cmds.ls( selection = True ) )
        )

        # Return cached if valid
        if self.cache_key == cache_key:
            return self.curve_cache.get( 'curves', [] )

        # Get curves
        curves = cmds.keyframe( q = True, name = True, sl = True ) or []
        if not curves:
            ge = 'graphEditor1GraphEd'
            if cmds.animCurveEditor( ge, exists = True ):
                curves = cmds.animCurveEditor( ge, q = True, curvesShown = True ) or []

        # Cache results
        self.cache_key = cache_key
        self.curve_cache['curves'] = curves
        return curves

    def collect_curve_data( self, curve ):
        """Batch collect all data for a curve"""
        if curve in self.key_cache:
            return self.key_cache[curve]

        # Collect all curve data in one go
        data = {
            'keys': cmds.keyframe( curve, q = True, tc = True ) or [],
            'values': cmds.keyframe( curve, q = True, vc = True ) or [],
            'tangents': self._batch_get_tangents( curve )
        }

        # Create key map for quick lookups
        data['key_map'] = {time: i for i, time in enumerate( data['keys'] )}
        '''
        for k in data:
            print( '____' )
            print( data[k] )
        '''
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
