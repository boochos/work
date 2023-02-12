import maya.cmds as cmds
import maya.mel as mel
#
import webrImport as web
# web
fr = web.mod( 'frameRange_lib' )


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def moveTime( left = True ):
    try:
        if left:
            cmds.keyframe( animation = 'keys', relative = 1, timeChange = ( 0 - 1 ) )
            message( '1 frame left', maya = 1 )
        else:
            cmds.keyframe( animation = 'keys', relative = 1, timeChange = ( 0 + 1 ) )
            message( '1 frame right', maya = 1 )
    except:
        pass


def moveValue( up = True ):
    try:
        if up:
            cmds.keyframe( animation = 'keys', relative = 1, valueChange = ( 0 + .005 ) )
            message( 'up      ' + str( 0.005 ), maya = 1 )
        else:
            cmds.keyframe( animation = 'keys', relative = 1, valueChange = ( 0 - .005 ) )
            message( 'down ' + str( 0.005 ), maya = 1 )
    except:
        message( 'didnt work' )
        pass


def animScale( v ):
    try:
        v = float( v )
        # scale_pivot  = cmds.playbackOptions(q=True, min=True)
        scale_pivot = cmds.currentTime( q = True )
        cmds.scaleKey( ts = v, tp = scale_pivot )
    except:
        message( 'didnt work' )
        return None
    # scale_factor = 4.0389


def bakeTimeWarp( objects, start, end, killWarp = True ):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe
    for i in objects:
        dupe = cmds.duplicate( i, po = 1 )[0]
        dupe = cmds.rename( dupe, dupe + '__warped' )
        if not cmds.attributeQuery( 'bakeTimeWarpConnection', node = i, ex = 1 ):
            cmds.addAttr( i, ln = 'bakeTimeWarpConnection', at = 'message' )
        cmds.connectAttr( dupe + '.message', i + '.bakeTimeWarpConnection' )
    for x in range( start, end + 1 ):
        cmds.currentTime( x )
        outTime = cmds.getAttr( 'time1.outTime' )
        unwarpedTime = cmds.getAttr( 'time1.unwarpedTime' )
        for i in objects:
            # build a list of all keyed channels.
            keyables = cmds.listAttr( i, k = 1 )
            keyedChans = []
            for f in keyables:
                if cmds.keyframe( i + '.' + f, q = 1, n = 1 ):
                    try:
                        keyedChans.append( f )
                    except:
                        print( f, '  skipped\n' )
            dupe = cmds.listConnections( i + '.bakeTimeWarpConnection' )[0]
            for chan in keyedChans:
                val = cmds.getAttr( i + '.' + chan, t = outTime )
                cmds.setAttr( dupe + '.' + chan, val )
                cmds.setKeyframe( dupe + '.' + chan, t = unwarpedTime )
    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        dupe = cmds.listConnections( i + '.bakeTimeWarpConnection' )[0]
        chans = [f for f in cmds.listAttr( dupe, k = 1 ) if cmds.keyframe( dupe + '.' + f, q = 1, n = 1 )]
        for chan in chans:
            animCurve = cmds.keyframe( dupe + '.' + chan, q = 1, n = 1 )[0]
            oldCurve = cmds.keyframe( i + '.' + chan, q = 1, n = 1 )
            cmds.connectAttr( animCurve + '.output', i + '.' + chan, f = 1 )
            cmds.delete( oldCurve )
        cmds.delete( dupe )
        cmds.deleteAttr( i + '.bakeTimeWarpConnection' )
    if killWarp:
        timeWarp = cmds.listConnections( 'time1.timewarpIn_Raw' )[0]
        cmds.delete( timeWarp )


def scaleCrv( val ):
    '''
    -Scale selected Graph Editor curves with given value.
    -Pivot derived from selection - get selected keys of curves, if values are the same, the pivot is from that position, otherwise pivot defaults to 0.
    '''
    # print '___here'
    # get curves of selected keys
    crvs = cmds.keyframe( q = True, name = True, sl = True )
    pvt = 0.0
    if crvs is not None:
        if len( crvs ) == 1:
            # keys selected from one curve
            selKey_1 = cmds.keyframe( crvs, q = True, vc = True, sl = True )
            selKey_2 = list( set( cmds.keyframe( crvs, q = True, vc = True, sl = True ) ) )
            if len( selKey_1 ) != len( selKey_2 ):
                message( '1' )
                # multiple keys selected, same value, pivot = 0
                cmds.scaleKey( crvs, vs = val, vp = pvt )
            elif len( selKey_1 ) == 1:
                pvt = selKey_1[0]
                cmds.scaleKey( crvs, vs = val, vp = pvt )
                message( 'Single key selected, pivot = ' + str( pvt ) )
            else:
                cmds.scaleKey( crvs, vs = val, vp = pvt )
                message( 'Multiple keys selected from one curve, pivot = ' + str( pvt ) )
        elif len( crvs ) > 1:
            selKey = list( set( cmds.keyframe( crvs, q = True, vc = True, sl = True ) ) )
            if len( selKey ) == 1:
                message( 'More than one curve selected, pivot = ' + str( pvt ) )
                # feature turned off
                # pvt = selKey[0]
                # message('Selected Keys from different curves have the same value, pivot = ' + str(pvt))
            else:
                message( 'Selected Keys have different values, pivot = ' + str( pvt ) )
            cmds.scaleKey( crvs, vs = val, vp = pvt )
    else:
        message( 'Select one or more keys in the graph editor. Pivots depend on selection.' )


def holdCrv( postCurrent = True, preCurrent = True ):
    crvs = cmds.keyframe( q = True, name = True, sl = True )
    if crvs is not None:
        cur = fr.Get()
        for crv in crvs:
            frames = cmds.keyframe( crv, q = True, tc = True )
            val = cmds.keyframe( crv, q = True, eval = True, t = ( cur.current, cur.current ) )[0]
            for frame in frames:
                if postCurrent:
                    if frame >= cur.current:
                        cmds.keyframe( crv, vc = val, t = ( frame, frame ) )
                        cmds.keyTangent( crv, inTangentType = 'auto', outTangentType = 'auto', time = ( frame, frame ) )
                if preCurrent:
                    if frame <= cur.current:
                        cmds.keyframe( crv, vc = val, t = ( frame, frame ) )
                        cmds.keyTangent( crv, inTangentType = 'auto', outTangentType = 'auto', time = ( frame, frame ) )
    else:
        message( 'Select curve(s) in the Graph Editor. -- Current timeline value of selected curve will be held.' )


def getKeyedFrames( obj ):
    animCurves = cmds.findKeyframe( obj, c = True )
    frames = []
    if animCurves:
        for crv in animCurves:
            framesTmp = cmds.keyframe( crv, q = True )
            for frame in framesTmp:
                frames.append( frame )
        frames = list( set( frames ) )
        frames.sort()
        return frames
    else:
        message( '-- Object given has no keys --' )
        return frames


def deleteAnim( obj, attrs = ['rotateX', 'rotateY', 'rotateZ'], lock = False, keyable = True ):
    animCurves = cmds.findKeyframe( obj, c = True )
    if animCurves:
        # should actually do this through connections
        for crv in animCurves:
            for attr in attrs:
                if attr.lower() in crv.lower():
                    cmds.delete( crv )
                else:
                    # print attr.lower(), '  attr not in curve  ', crv.lower()
                    pass
    else:
        # print 'no curves'
        pass
    for attr in attrs:
        cmds.setAttr( obj + '.' + attr, lock = lock )
        cmds.setAttr( obj + '.' + attr, keyable = keyable )


def deleteAnim2( obj, attrs = ['rotateX', 'rotateY', 'rotateZ'] ):
    animCurves = cmds.findKeyframe( obj, c = True )
    if animCurves:
        # should actually do this through connections
        for crv in animCurves:
            for attr in attrs:
                if attr.lower() in crv.lower():
                    cmds.delete( crv )


def unifyKeys():
    sel = cmds.keyframe( q = True, name = True, sl = True )
    if sel:
        frames = sorted( list( set( cmds.keyframe( sel, q = True ) ) ) )
        i = len( frames )
        for frame in frames:
            for c in sel:
                if not cmds.keyframe( c, q = True, time = ( frame, frame ) ):
                    message( 'adding keys on frame -- ' + str( frame ) )
                    cmds.refresh( f = 1 )
                    cmds.setKeyframe( sel, i = True, t = frame )
            i = i - 1
        message( 'Done' )
    else:
        message( 'Select some curves in the graph editor.' )


def toggleTangentLock():
    state = cmds.keyTangent( q = True, lock = True )[0]
    if state:
        cmds.keyTangent( lock = False )
        message( 'Tangent Broken' )
    else:
        cmds.keyTangent( lock = True )
        message( 'Tangent Unified' )


def setInfinityLinear():
    '''
    
    '''
    #
    sel = cmds.keyframe( q = True, name = True, sl = True )
    if sel:
        # cmds.keyTangent( itt = 'spline', ott = 'spline' )
        cmds.setInfinity( pri = 'linear' )
        cmds.setInfinity( poi = 'linear' )
        '''
        frames = sorted( list( set( cmds.keyframe( sel, q = True ) ) ) )
        i = len( frames )
        for frame in frames:
            for c in sel:
                if not cmds.keyframe( c, q = True, time = ( frame, frame ) ):
                    message( 'adding keys on frame -- ' + str( frame ) )
                    cmds.refresh( f = 1 )
                    cmds.setKeyframe( sel, i = True, t = frame )
            i = i - 1'''
        message( 'Done' )
    else:
        message( 'Select some curves in the graph editor.' )


def setInfinityConstant():
    '''
    
    '''
    #
    sel = cmds.keyframe( q = True, name = True, sl = True )
    if sel:
        # cmds.keyTangent( itt = 'spline', ott = 'spline' )
        cmds.setInfinity( pri = 'constant' )
        cmds.setInfinity( poi = 'constant' )

        message( 'Done' )
    else:
        message( 'Select some curves in the graph editor.' )


def tangentStep( mltp = 1.0001 ):
    angle = cmds.keyTangent( q = True, outAngle = True )[0]
    cmds.keyTangent( e = True, outAngle = angle + mltp )


def tangentFlat():
    #
    sel = cmds.keyframe( q = True, name = True, sl = True )
    if sel:
        cmds.keyTangent( itt = 'flat', ott = 'flat' )
        # message( 'Done' )
    else:
        message( 'Select some curves in the graph editor.' )


def bakeInfinity( sparseKeys = True, smart = True, sim = False, sampleBy = 1 ):
    crvs = cmds.keyframe( q = True, name = True, sl = True )
    if crvs:
        start = cmds.playbackOptions( q = True, minTime = True )
        end = cmds.playbackOptions( q = True, maxTime = True )
        objs = cmds.listConnections( crvs, d = True, s = False, plugs = True )
        cmds.refresh( suspend = 1 )
        print( sim, '________' )
        # cmds.bakeResults( objs, t = ( start, end ), simulation = sim, pok = True, smart = smart, sac = sparseKeys, sampleBy = 1 )
        cmds.bakeResults( objs, t = ( start, end ), simulation = sim, pok = True, sac = sparseKeys, sampleBy = 1 )
        cmds.refresh( suspend = 0 )
        message( str( len( objs ) ) + ' curves baked --' + str( objs ), maya = 1 )
    else:
        message( 'no curves are selected', maya = 1 )


def smoothKeys( weight = 0.5 ):
    crvs = cmds.keyframe( q = True, name = True, sl = True )
    if crvs:
        for crv in crvs:
            frames = cmds.keyframe( crv, q = True, sl = True )
            size = len( frames )
            if size > 2:
                # first key val
                # x = cmds.keyframe(crvs, q=True, vc=True, time=(frames[0], frames[0]))[0]
                i = 0
                for frame in frames:
                    if frame == frames[0] or frame == frames[size - 1]:
                        pass
                    else:
                        # previous itter
                        x = cmds.keyframe( crv, q = True, vc = True, time = ( frames[i - 1], frames[i - 1] ) )[0]
                        # this itter
                        y = cmds.keyframe( crv, q = True, vc = True, time = ( frame, frame ) )[0]
                        # next itter
                        z = cmds.keyframe( crv, q = True, vc = True, time = ( frames[i + 1], frames[i + 1] ) )[0]
                        # frame range between keys
                        frameRange = int( ( frames[i - 1] - frames[i + 1] ) * -1 )
                        # value range between keys, account for negative
                        valueRange = x - z
                        # force positive
                        if valueRange < 0:
                            valueRange = valueRange * -1
                        # find increments
                        inc = valueRange / frameRange
                        # how many increments to add
                        mlt = int( ( frames[i - 1] - frame ) * -1 )
                        # add up increments
                        keyPos = inc * mlt
                        # final value to add/subtract from previous key
                        # operation depends on x relative to z value
                        if x < z:
                            # print 'above'
                            val = x + keyPos
                            # print y, '  current'
                            # print val, '  actual'
                            val = y - val
                            # print val, '  dif'
                            val = val * weight
                            # print val, '  multip'
                            val = y - val
                            # print val, '  final'
                        else:
                            # print 'below'
                            val = x - keyPos
                            # print y, '  current'
                            # print val, '  actual'
                            val = y - val
                            # print val, '  dif'
                            val = val * weight
                            # print val, '  multip'
                            val = y - val
                            # print val, '  final'
                        cmds.keyframe( crv, vc = val, time = ( frame, frame ) )
                        cmds.keyTangent( crv, edit = True, itt = 'auto', ott = 'auto', time = ( frame, frame ) )
                    i = i + 1


def subframe():
    frames = None
    animCurves = cmds.keyframe( q = True, name = True, sl = True )
    cmds.selectKey( clear = True )
    # print animCurves
    if animCurves:
        for crv in animCurves:
            frames = cmds.keyframe( crv, q = True )
            # print frames
            if frames:
                for frame in frames:
                    rnd = round( frame, 0 )
                    # print rnd, frame
                    if rnd != frame:
                        message( 'removing: ' + 'key' + ' -- ' + str( frame ) )
                        cmds.refresh( f = 1 )
                        if rnd not in frames:
                            cmds.keyframe( time = ( frame, frame ), absolute = True, timeChange = rnd )
                        else:
                            cmds.cutKey( animCurves, time = ( frame, frame ) )
                        '''
                        if cmds.setKeyframe( animCurves, time = ( rnd, rnd ), i = 1 ) == 0:
                            cmds.cutKey( animCurves, time = ( frame, frame ) )
                        else:
                            cmds.setKeyframe( animCurves, time = ( rnd, rnd ), i = 1 )
                            cmds.cutKey( animCurves, time = ( frame, frame ) )'''
            else:
                message( 'no keys' )
        cmds.selectKey( animCurves )
    else:
        message( 'no curves selected' )


def distributeKeys( step = 3.0, destructive = True, forceWholeFrames = True ):
    '''
    operates on selected curves
    '''
    s = GraphSelection()
    sel = cmds.ls( sl = 1, fl = True )
    rng = fr.Get()
    if s.crvs:
        # gather info
        autoK = cmds.autoKeyframe( q = True, state = True )
        frames = getKeyedFrames( s.crvs )
        # process start/end of loop
        framesNew = []
        if rng.selection:
            for f in frames:
                if f >= rng.keyStart and f <= rng.keyEnd:
                    framesNew.append( f )
            frames = framesNew
        #
        cut = []
        # print frames
        if forceWholeFrames:
            framesOrig = frames
            frames = [round( frame ) for frame in frames]
            framesPartial = list( set( framesOrig ) - set( frames ) )
            cut = [frame for frame in framesPartial]
            # print cut, '______cut'
        lastFrame = frames[len( frames ) - 1]
        count = frames[0]
        i = frames[0]
        # turn off autokey
        cmds.autoKeyframe( state = False )
        framesNew = []
        # process keys
        while i < lastFrame:
            if i == count:
                cmds.setKeyframe( s.crvs, i = True, t = count )
                framesNew.append( count )
                count = count + step
            else:
                if i in frames:
                    cut.append( i )
            i = i + 1
        # remove keys is destructive
        if destructive:
            framesDel = sorted( list( set( frames ) - set( framesNew ) ) )
            for frame in framesDel:
                cut.append( frame )
            # print framesOrig, '________orig'
            # print framesNew, '________new'
            # print cut, '_________cut'
            if cut:
                for frame in cut:
                    if frame >= rng.keyStart and frame <= rng.keyEnd:
                        cmds.cutKey( sel, clear = 1, time = ( frame, frame ) )
        # restore autokey
        cmds.autoKeyframe( state = autoK )
    else:
        message( 'Select one or more anima curves', maya = 1 )


class GraphSelection():

    def __init__( self ):
        self.selection = cmds.ls( sl = True )
        self.crvs = cmds.keyframe( q = True, name = True, sl = True )
        self.pack = []
        if self.crvs:
            for item in self.crvs:
                cr = []
                cr.append( item )
                cr.append( cmds.keyframe( item, q = True, sl = True ) )
                self.pack.append( cr )

    def reselect( self, objects = True ):
        if objects:
            if self.selection:
                sel = cmds.ls( sl = True )
                if sel != self.selection:
                    cmds.select( self.selection )
        if self.pack:
            for cr in self.pack:
                cmds.selectKey( cr[0], add = True, time = ( cr[1][0], cr[1][len( cr[1] ) - 1] ) )
