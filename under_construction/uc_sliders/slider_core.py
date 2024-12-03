import imp
import time

from under_construction.uc_sliders import slider_strategies_blending
from under_construction.uc_sliders import slider_strategies_targeting
import maya.cmds as cmds
import maya.mel as mel

imp.reload( slider_strategies_targeting )
imp.reload( slider_strategies_blending )

# TODO: Add anchor weights handling when weighted tangents are used, mainly for SplineTargetStrategy, will need for others.
# TODO: cleanup module, audit functions and data structures for usage
# TODO: refactor how curves are gathered, should have 3 options, via selected vurves, active layers, selected objects, active char sets


class SliderCore( object ):
    """Core class for data management"""

    def __init__( self ):
        # Data management
        self.curve_data = {}  # Map of curve to CurveData
        self.blend_data = BlendData()
        self.update_queue = []  # Add this line to initialize update_queue

        # State tracking
        self.selected_objects = []
        self.anim_layers = []
        self.blend_nodes = []
        self.current_time = None
        self.moved = False
        self.cache_timeout = 5.0
        self.batch_size = 50

        self.targeting_strategies = {
            'direct': slider_strategies_targeting.DirectTargetStrategy( self ),
            'linear': slider_strategies_targeting.LinearTargetStrategy( self ),
            'spline': slider_strategies_targeting.SplineTargetStrategy( self )
        }
        self.blending_strategies = {
            'rate': slider_strategies_blending.RateBasedBlendStrategy( self ),
            'linear': slider_strategies_blending.LinearBlendStrategy( self ),
            'tria': slider_strategies_blending.TriangleBlendStrategy( self ),
            'triad': slider_strategies_blending.TriangleDirectBlendStrategy( self )
        }
        self.current_targeting_strategy = 'linear'
        self.current_blending_strategy = 'linear'

    def get_curve_tangents( self, curve ):
        return self.curve_data[curve].tangents

    def get_curve_value( self, curve, idx ):
        return self.curve_data[curve].values[idx]

    def initialize_blend_session( self ):
        """Initialize data for a new blend operation"""
        # print( '___current blend strategy', self.current_blending_strategy )
        # Clear previous data
        self.curve_data.clear()
        self.blend_data.clear()

        # Get current state
        curves = self.get_curves()
        if not curves:
            return False

        self.selected_objects = cmds.ls( selection = True )
        self.anim_layers = cmds.ls( type = 'animLayer' )
        self.current_time = cmds.currentTime( query = True )
        self.blend_nodes = self._get_blend_nodes()
        # print(self.blend_nodes)

        # Process each curve
        for curve in curves:
            self._process_curve( curve )

        return bool( self.curve_data )

    def _process_curve( self, curve ):
        """Process and cache curve data"""
        try:
            curve_data = CurveData.from_curve( curve )
            if not curve_data.keys:
                return

            selected_keys = self.get_selected_keys( curve )
            # print( "Selected keys:", selected_keys )  # Add this debug

            # If we have no selected keys and need to insert at current time
            if not selected_keys and self.current_time not in curve_data.key_map:
                if not self.moved:  # Keep undo opening here since we're about to insert
                    self.moved = True
                    cmds.undoInfo( openChunk = True, cn = 'Blend_N' )
                self._insert_current_time_key( curve )
                curve_data = CurveData.from_curve( curve )

            self.curve_data[curve] = curve_data
            self.blend_data.add_curve( curve, curve_data )

        except Exception as e:
            print( "Error processing curve {0}: {1}".format( curve, e ) )

    def has_curve_data( self, curve ):
        """Check if curve data exists"""
        return curve in self.curve_data

    def _insert_current_time_key( self, curve ):
        """Insert a key at current time"""
        try:
            current_value = cmds.keyframe( 
                curve,
                time = ( self.current_time, ),
                q = True,
                eval = True
            )[0]
            cmds.setKeyframe( 
                curve,
                time = self.current_time,
                insert = True,
                value = current_value
            )
        except Exception as e:
            print( "Error inserting key: {0}".format( e ) )

    def _get_blend_nodes( self ):
        """Get blend nodes from animation layers"""
        blend_nodes = []
        for layer in self.anim_layers:
            blends = cmds.animLayer( layer, q = True, blendNodes = True )
            if blends:
                blend_nodes.extend( blends )
        return blend_nodes

    def calculate_blend( self, curve, time, blend_factor ):
        """Calculate blended values for a curve at given time"""
        try:
            curve_data = self.curve_data.get( curve )
            if not curve_data:
                return None, None

            current_idx = curve_data.get_key_index( time )
            if current_idx is None:
                return None, None

            # Get target values using targeting strategy
            strategy = self.get_current_targeting_strategy()
            prev_target, next_target = strategy.calculate_target_value( curve, time )
            prev_tangents, next_tangents = strategy.calculate_target_tangents( curve, time )
            prev_anchor, next_anchor = strategy.calculate_anchor_weights( curve, time )  # Get anchor weights if strategy provides them

            current_strategy = self.get_current_blending_strategy()

            #
            #
            #
            # Process anchor weights if they exist
            if prev_anchor:
                blended_prev = current_strategy.blend_anchors( curve, prev_anchor, blend_factor )
                if blended_prev:
                    self.update_queue.append( {
                        'curve': curve,
                        'time': blended_prev['time'],
                        'is_anchor': True,
                        'tangent': blended_prev['tangent'],
                        'weight': blended_prev['weight']
                    } )

            if next_anchor:
                blended_next = current_strategy.blend_anchors( curve, next_anchor, blend_factor )
                if blended_next:
                    self.update_queue.append( {
                        'curve': curve,
                        'time': blended_next['time'],
                        'is_anchor': True,
                        'tangent': blended_next['tangent'],
                        'weight': blended_next['weight']
                    } )
            #
            #
            #

            # Determine blend direction and target
            is_forward = blend_factor >= 0
            target_value = next_target if is_forward else prev_target
            target_tangents = next_tangents if is_forward else prev_tangents

            # Get current strategy to determine how to handle blend_factor
            current_strategy = self.get_current_blending_strategy()
            if current_strategy.uses_signed_blend:
                # Pass original signed value for geometric strategy
                abs_blend = blend_factor
            else:
                # Use absolute value for other strategies
                abs_blend = abs( blend_factor )

            # print( "___blend_factor:", blend_factor )
            # print( "___is_forward:", is_forward )

            # Calculate blend using appropriate blend factor
            return self._blend_values( 
                curve,
                current_idx,
                target_value = target_value,
                target_tangents = target_tangents,
                blend_factor = abs_blend
            )

        except Exception as e:
            print( "Error calculating blend: {0}".format( e ) )
            return None, None

    def _blend_values( self, curve, current_idx, target_value, target_tangents, blend_factor ):
        """Calculate blended values using current blend strategy"""
        curve_data = self.curve_data[curve]
        current_value = curve_data.values[current_idx]

        strategy = self.get_current_blending_strategy()
        return strategy.blend_values( curve, current_idx, current_value, target_value, target_tangents, blend_factor )

    # Strategy Management
    def get_current_targeting_strategy( self ):
        """Get current targeting strategy instance"""
        return self.targeting_strategies[self.current_targeting_strategy]

    def set_targeting_strategy( self, strategy_name ):
        """Set current targeting strategy"""
        if strategy_name in self.targeting_strategies:
            self.current_targeting_strategy = strategy_name
            return True
        return False

    def get_current_blending_strategy( self ):
        """Get current blending strategy instance"""
        return self.blending_strategies[self.current_blending_strategy]

    def set_blending_strategy( self, strategy_name ):
        """Set current blending strategy"""
        # print( '___', strategy_name )
        if strategy_name in self.blending_strategies:
            self.current_blending_strategy = strategy_name
            return True
        return False

    def get_curves( self ):
        """Get visible/selected animation curves"""
        curves = cmds.keyframe( q = True, name = True, sl = True ) or []
        if not curves:
            ge = 'graphEditor1GraphEd'
            if cmds.animCurveEditor( ge, exists = True ):
                curves = cmds.animCurveEditor( ge, q = True, curvesShown = True ) or []
        return curves

    # Data Access Methods
    def get_selected_keys( self, curve ):
        """Get selected keys as a list"""
        return list( cmds.keyframe( curve, q = True, sl = True, tc = True ) or [] )  # Convert to list

    def get_curve_data( self, curve ):
        """Get cached curve data"""
        return self.curve_data.get( curve )

    def clear_caches( self ):
        """Clear all cached data"""
        self.curve_data.clear()
        self.blend_data.clear()
        self.moved = False
        self.update_queue = []

    def prepare_handle_move( self ):
        """Prepare for handle movement"""
        if not self.curve_data:
            return False

        if not self.moved:
            self.moved = True
            cmds.undoInfo( openChunk = True, cn = 'Blend_N' )

        return True

    def finish_blend( self ):
        """Clean up after blend operation"""
        if self.moved:
            cmds.undoInfo( closeChunk = True, cn = 'Blend_N' )
            self.moved = False
        self.clear_caches()

    def _process_object_updates( self, obj, blend_factor ):
        """Process updates for a single object"""
        # print( '___', blend_factor )
        for curve in self.curve_data:
            if curve not in self.curve_data:
                continue

            # Get keys to update
            selected_keys = self.get_selected_keys( curve )  # Use core method
            times_to_update = selected_keys if selected_keys else [self.current_time]

            # Process in batches
            for i in range( 0, len( times_to_update ), self.batch_size ):
                batch = times_to_update[i:i + self.batch_size]
                for time in batch:
                    new_value, new_tangents = self.calculate_blend( # Use core calculation
                        curve,
                        time,
                        blend_factor
                    )
                    # print( '___', blend_factor, new_value )
                    if new_value is not None:
                        self.update_queue.append( {
                            'curve': curve,
                            'time': time,
                            'value': new_value,
                            'tangents': new_tangents
                        } )

    def _execute_batch_updates( self ):
        """Execute queued updates in optimized batches"""
        curve_updates = {}
        for update in self.update_queue:
            curve = update['curve']
            if curve not in curve_updates:
                curve_updates[curve] = []
            curve_updates[curve].append( update )

        for curve, updates in curve_updates.items():
            curve_data = self.curve_data[curve]
            for update in updates:
                if update.get( 'is_anchor' ):
                # Get current key index and weights
                    key_idx = curve_data.key_map[update['time']]
                    current_in_weight = curve_data.tangents['in_weights'][key_idx]
                    current_out_weight = curve_data.tangents['out_weights'][key_idx]

                    # Update only the specified tangent weight, preserve the other
                    if update['tangent'] == 'in':
                        cmds.keyTangent( 
                            curve,
                            time = ( update['time'], update['time'] ),
                            inWeight = update['weight'],
                            outWeight = current_out_weight
                        )
                    else:  # 'out'
                        cmds.keyTangent( 
                            curve,
                            time = ( update['time'], update['time'] ),
                            inWeight = current_in_weight,
                            outWeight = update['weight']
                        )
                else:
                    # Handle normal key updates
                    time = update['time']
                    key_idx = curve_data.key_map[time]
                    cmds.setKeyframe( 
                        curve,
                        time = update['time'],
                        value = update['value']
                    )

                    if update['tangents']:
                        in_angle, in_weight = update['tangents']['in']
                        out_angle, out_weight = update['tangents']['out']

                        cmds.keyTangent( 
                            curve,
                            time = ( update['time'], update['time'] ),
                            ia = in_angle,
                            iw = in_weight,
                            oa = out_angle,
                            ow = out_weight,
                            lock = curve_data.tangents['lock'][key_idx]
                        )

    def on_handle_move( self, blend_factor ):
        """Core movement handler"""
        if self.prepare_handle_move():
            # Process updates
            for obj in self.selected_objects:
                self._process_object_updates( obj, blend_factor )

            if self.update_queue:
                self._execute_batch_updates()

            if self.blend_nodes:
                cmds.dgeval( self.blend_nodes )

    def __NOT_SURE_THIS_ARE_STILL_NEEDED___start( self ):
        pass

    def __NOT_SURE_THIS_ARE_STILL_NEEDED___end( self ):
        pass


# data_structures.py
class CurveData:
    """
    Encapsulates all data for a single animation curve
    """

    def __init__( self ):
        self.keys = []
        self.values = []
        self.key_map = {}
        self.is_weighted = False
        self.tangents = {
            'in_angles': [],
            'in_weights': [],
            'out_angles': [],
            'out_weights': [],
            'in_types': [],
            'out_types': [],

            # Additional attributes
            'weight_lock': [],  # weightLock
            'weighted_tangents': [],  # weightedTangents
            'lock': [],  # lockTangents
            'unify': [],  # tangentLock
            'breakdown': []  # breakdown state
        }

        self.prev_indices = {}
        self.next_indices = {}
        self.cache_timestamp = None

        # Add running state tracking at curve level
        self.running_values = []  # Tracks current values during blending
        self.running_tangents = {  # Tracks current tangent state
            'in_angles': [],
            'in_weights': [],
            'out_angles': [],
            'out_weights': []
        }

    @classmethod
    def from_curve( cls, curve ):
        """Create a CurveData instance from a Maya animation curve"""
        instance = cls()
        instance.keys = cmds.keyframe( curve, q = True, tc = True ) or []
        instance.values = cmds.keyframe( curve, q = True, vc = True ) or []
        instance.is_weighted = cmds.keyTangent( curve, q = True, weightedTangents = True )[0]
        instance.key_map = {time: i for i, time in enumerate( instance.keys )}
        instance._collect_tangents( curve )
        instance._calculate_indices()
        instance.cache_timestamp = time.time()

        # Initialize running state for selected and anchor keys
        selected_keys = set( cmds.keyframe( curve, q = True, sl = True, tc = True ) or [] )
        instance._init_running_state( selected_keys )

        return instance

    def _init_running_state( self, selected_keys ):
        """Initialize running state including selected keys and their anchors"""
        # First, create full arrays initialized to None
        self.running_values = [None] * len( self.values )
        self.running_tangents = {
            'in_angles': [None] * len( self.tangents['in_angles'] ),
            'in_weights': [None] * len( self.tangents['in_weights'] ),
            'out_angles': [None] * len( self.tangents['out_angles'] ),
            'out_weights': [None] * len( self.tangents['out_weights'] )
        }

        # For each selected key, find its anchors and populate running values
        for time in selected_keys:
            idx = self.key_map[time]
            # Add selected key
            self._add_to_running_state( idx )

            # Find and add previous anchor
            for i in range( idx - 1, -1, -1 ):
                if self.keys[i] not in selected_keys:
                    self._add_to_running_state( i )
                    break

            # Find and add next anchor
            for i in range( idx + 1, len( self.keys ) ):
                if self.keys[i] not in selected_keys:
                    self._add_to_running_state( i )
                    break

        # print( "___init running state for keys:", selected_keys )

    def _add_to_running_state( self, idx ):
        """Add a key to the running state"""
        if self.running_values[idx] is None:  # Only add if not already added
            self.running_values[idx] = self.values[idx]
            self.running_tangents['in_angles'][idx] = self.tangents['in_angles'][idx]
            self.running_tangents['in_weights'][idx] = self.tangents['in_weights'][idx]
            self.running_tangents['out_angles'][idx] = self.tangents['out_angles'][idx]
            self.running_tangents['out_weights'][idx] = self.tangents['out_weights'][idx]

    def _init_running_tangents( self ):
        """Initialize running tangents with current tangent values"""
        self.running_tangents = {
            'in_angles': self.tangents['in_angles'][:],
            'in_weights': self.tangents['in_weights'][:],
            'out_angles': self.tangents['out_angles'][:],
            'out_weights': self.tangents['out_weights'][:]
        }

    def update_running_state( self, idx, value, tangents ):
        """Update running state only if the key is in our running state"""
        if 0 <= idx < len( self.running_values ) and self.running_values[idx] is not None:
            self.running_values[idx] = value
            if tangents:
                self.running_tangents['in_angles'][idx] = tangents['in'][0]
                self.running_tangents['in_weights'][idx] = tangents['in'][1]
                self.running_tangents['out_angles'][idx] = tangents['out'][0]
                self.running_tangents['out_weights'][idx] = tangents['out'][1]

    def get_running_value( self, idx ):
        """Get running value if it exists, otherwise return None"""
        if 0 <= idx < len( self.running_values ):
            return self.running_values[idx]
        return None

    def get_running_tangents( self, idx ):
        """Get current running tangents at index"""
        if 0 <= idx < len( self.running_values ):
            return {
                'in': ( 
                    self.running_tangents['in_angles'][idx],
                    self.running_tangents['in_weights'][idx]
                ),
                'out': ( 
                    self.running_tangents['out_angles'][idx],
                    self.running_tangents['out_weights'][idx]
                )
            }
        return None

    def _collect_tangents( self, curve ):
        """Collect all tangent data for the curve"""
        self.tangents = {
            # Current queries
            'in_angles': cmds.keyTangent( curve, q = True, ia = True ) or [],
            'in_weights': cmds.keyTangent( curve, q = True, iw = True ) or [],
            'out_angles': cmds.keyTangent( curve, q = True, oa = True ) or [],
            'out_weights': cmds.keyTangent( curve, q = True, ow = True ) or [],
            'in_types': cmds.keyTangent( curve, q = True, itt = True ) or [],
            'out_types': cmds.keyTangent( curve, q = True, ott = True ) or [],

            # Additional queries
            'weight_lock': cmds.keyTangent( curve, q = True, weightLock = True ) or [],
            'weighted_tangents': cmds.keyTangent( curve, q = True, weightedTangents = True ) or [],
            'lock': cmds.keyTangent( curve, q = True, lock = True ) or [],
            'unify': cmds.keyTangent( curve, q = True, unify = True ) or [],
            'breakdown': cmds.keyframe( curve, q = True, breakdown = True ) or []
        }

    def _calculate_indices( self ):
        """Calculate previous and next key indices"""
        # Previous indices
        self.prev_indices = {
            time: ( i - 1 if i > 0 else i )
            for i, time in enumerate( self.keys )
        }

        # Next indices
        self.next_indices = {
            time: min( i + 1, len( self.keys ) - 1 )
            for i, time in enumerate( self.keys[:-1] )
        }
        # Handle last key
        if self.keys:
            self.next_indices[self.keys[-1]] = len( self.keys ) - 1

    def get_key_index( self, time ):
        """Get index for a given time"""
        return self.key_map.get( time )

    def get_value( self, idx ):
        """Get value at index"""
        return self.values[idx] if 0 <= idx < len( self.values ) else None

    def get_tangent_data( self, idx ):
        """Get all tangent data for an index"""
        if 0 <= idx < len( self.keys ):
            return {
                'in': ( 
                    self.tangents['in_angles'][idx],
                    self.tangents['in_weights'][idx]
                ),
                'out': ( 
                    self.tangents['out_angles'][idx],
                    self.tangents['out_weights'][idx]
                )
            }
        return None

    def is_cache_valid( self, timeout ):
        """Check if cached data is still valid"""
        if self.cache_timestamp is None:
            return False
        return ( time.time() - self.cache_timestamp ) < timeout


class BlendData:
    """
    Manages data for current blend operation
    """

    def __init__( self ):
        self.curve_data = {}  # CurveData instances
        self.selected_keys = {}  # Selected keys per curve
        self.initial_values = {}  # Current values per curve/time
        self.target_values = {}  # Target values per curve/time
        self.target_tangents = {}  # Target tangents per curve/time
        self.update_queue = []  # Pending updates

    def add_curve( self, curve, curve_data ):
        """Add curve data to blend session"""
        self.curve_data[curve] = curve_data
        self.selected_keys[curve] = set()
        self.initial_values[curve] = {}
        self.target_values[curve] = {}
        self.target_tangents[curve] = {}

    def add_update( self, curve, time, value, tangents ):
        """Queue an update"""
        self.update_queue.append( {
            'curve': curve,
            'time': time,
            'value': value,
            'tangents': tangents
        } )

    def clear( self ):
        """Clear all blend data"""
        self.curve_data = {}
        self.selected_keys = {}
        self.initial_values = {}
        self.target_values = {}
        self.target_tangents = {}
        self.update_queue = []  # Reset to empty list instead of using clear()
