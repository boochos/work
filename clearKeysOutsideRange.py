import time

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            print( what )


def clear( startBuffer = 2, endBuffer = 2 ):
    # selection and curves
    sel = cmds.ls( sl = 1 )

    # range
    fmin = cmds.playbackOptions( q = True, minTime = True ) - startBuffer
    fmax = cmds.playbackOptions( q = True, maxTime = True ) + endBuffer

    # curves
    crvs = cmds.findKeyframe( sel, c = True )
    if crvs:
        # gather keys to remove
        for crv in crvs:
            startFrame = 0
            endFrame = 0
            startClear = False
            endClear = False
            # sort temp frames, and key insert
            framesTmp = cmds.keyframe( crv, q = True )
            framesTmp = list( set( framesTmp ) )
            framesTmp.sort()
            if framesTmp[0] < fmin:
                # print 'insert to min'
                cmds.setKeyframe( crv, i = True, t = ( fmin + startBuffer, fmin + startBuffer ) )
                cmds.setKeyframe( crv, i = True, t = ( fmin, fmin ) )
                startClear = True
                startFrame = framesTmp[0]
            if framesTmp[len( framesTmp ) - 1] > fmax:
                # print 'insert to max'
                cmds.setKeyframe( crv, i = True, t = ( fmax - endBuffer, fmax - endBuffer ) )
                cmds.setKeyframe( crv, i = True, t = ( fmax, fmax ) )
                endClear = True
                endFrame = framesTmp[len( framesTmp ) - 1]
            # sort keys
            frames = []
            for frame in framesTmp:
                if frame > fmax or frame < fmin:
                    frames.append( frame )
            frames = list( set( frames ) )
            frames.sort()
            # clear keys
            if startClear:
                cmds.cutKey( crv, t = ( startFrame, fmin - 1 ), clear = True )
                startClear = False
            if endClear:
                cmds.cutKey( crv, t = ( fmax + 1 , endFrame ), clear = True )
                endClear = False
            # print frames


def addKeyOnMaster( ns = '' ):
    fmin = cmds.playbackOptions( q = True, minTime = True )
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    for attr in attrs:
        crv = cmds.findKeyframe( ns + ':base_startPivot_ctrl.' + attr, c = True )
        if crv:
            cmds.setKeyframe( crv, i = True, t = ( fmin, fmin ) )
        else:
            cmds.setKeyframe( ns + ':base_startPivot_ctrl.' + attr, t = ( fmin, fmin ) )


def cleaCrowdKeys( startBuffer = 2, endBuffer = 2, selectionOnly = False ):
    '''
    operates only if "base_startPivot_ctrl" control exists
    '''
    start = time.time()
    refs = cmds.ls( typ = 'reference', long = True )
    selectionNS = inclusionNS()
    # print refs
    i = 1
    for ref in refs:
        message( str( i ) + ' of ' + str( len( refs ) ), maya = True )
        ud = cmds.listAttr( ref, ud = True )
        if ud:
            if 'apkgNode' in ud:
                crowdQualify = cmds.getAttr( ref + '.apkgNode' )
                if crowdQualify:
                    # print crowdQualify
                    if 'crowd_vignette_a' in crowdQualify:
                        ns = cmds.referenceQuery( ref, ns = True )
                        # print ns, '__'
                        if selectionOnly:
                            if ns.split( ':' )[1] not in selectionNS:
                                print 'exclude  ', ns
                                ns = None
                        if ns:
                            if cmds.objExists( ns + ':base_startPivot_ctrl' ):
                                print 'include  ', ns
                                addKeyOnMaster( ns = ns )
                                cmds.select( ns + ':base_startPivot_ctrl' )
                                import animation.util; animation.util.selectAllCtrlsSelected()
                                clear( startBuffer = startBuffer, endBuffer = endBuffer )
        i = i + 1
    end = time.time()
    message( 'Elapsed: ' + str( round( end - start, 2 ) ) + ' seconds' )


def inclusionNS():
    sel = cmds.ls( sl = True )
    include = []
    for s in sel:
        if ':' in s:
            ns = s.split( ':' )[0]
            include.append( ns )
    return include

