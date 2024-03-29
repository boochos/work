import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

cn = web.mod( 'constraint_lib' )
ds = web.mod( 'display_lib' )
ac = web.mod( 'animCurve_lib' )
plc = web.mod( 'atom_place_lib' )


def simplePose( obj = '', attr = '', startFrame = 1001, min = -1.0, max = 1.0, transitionDuration = 10 ):
    '''
    create range of motion animation
    '''
    #
    cmds.currentTime( startFrame )
    currentPose = cmds.getAttr( obj + '.' + attr )
    #
    # print( attr, min, max )
    cmds.setKeyframe( obj + '.' + attr, t = startFrame, v = currentPose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.' + attr, t = startFrame + transitionDuration, v = min, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.' + attr, t = startFrame + ( transitionDuration * 3 ), v = max, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.' + attr, t = startFrame + ( transitionDuration * 4 ), v = currentPose, itt = 'linear', ott = 'linear' )

    # eulerFilter( obj, tangentFix = True )
    return startFrame + ( transitionDuration * 4 )


def simplePoseLoop( startFrame = 1001, rotR = 90, posR = 1.00, sclR = 0.0, transitionDuration = 10, hyperExtensionAxis = '', hyperExtensionNegative = True, deletePrevious = False ):
    '''
    get selection
    loop through objects
    loop through object axis
    create range of motion animation
    '''

    #
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    sel = cmds.ls( sl = 1 )
    current = cmds.currentTime( startFrame )
    #
    for obj in sel:
        attrs = listAttrs( obj )
        if attrs:
            for attr in attrs:
                # delete anim
                if deletePrevious:
                    for attr in attrs:
                        deleteAnim( obj = obj, attr = attr )
                #
                currentPose = cmds.getAttr( obj + '.' + attr )
                #
                rot_mlt = 0.35
                pos_mlt = 1.0
                scl_mlt = 1.0
                #
                min = 0.0
                max = 0.0
                #
                pos = 'translate'
                rot = 'rotate'
                scl = 'scale'
                #
                go = True
                #
                if rot in attr:
                    if rotR > 0:
                        if hyperExtensionAxis:
                            if hyperExtensionAxis.upper() in attr:
                                if hyperExtensionNegative:  # reduce negative
                                    min = ( currentPose - rotR ) * rot_mlt
                                    max = ( currentPose + rotR )
                                else:  # reduce positive
                                    min = ( currentPose - rotR )
                                    max = ( currentPose + rotR ) * rot_mlt
                            else:  # reduce if hyperextension and wrong axis
                                min = ( currentPose - rotR ) * rot_mlt
                                max = ( currentPose + rotR ) * rot_mlt
                        else:  # do the things without multiplier
                            min = ( currentPose - rotR )
                            max = ( currentPose + rotR )
                    else:
                        go = False
                if pos in attr:
                    if posR > 0:
                        min = ( currentPose - posR ) * pos_mlt
                        max = ( currentPose + posR ) * pos_mlt
                    else:
                        go = False
                if scl in attr:
                    if sclR > 0 and sclR < 1.0:
                        min = ( currentPose * sclR ) * scl_mlt
                        max = ( currentPose * ( 1.0 + sclR ) ) * scl_mlt
                    else:
                        go = False
                if go:
                    current = simplePose( obj = obj, attr = attr, startFrame = current, min = min, max = max, transitionDuration = transitionDuration )
                # print(current)
        eulerFilter( obj, tangentFix = True )
    setFrameRange( start = startFrame, end = current )
    return current


def compoundPose( obj = '', startFrame = 1, rotR = 60, posR = 2.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [1, 1, 1], deletePrevious = True, torque = True ):
    '''
    create roll pose
    rotFlip / posFlip correspond to sideUpFront, atts will be flipped to match axis
    '''

    # start frame
    cmds.currentTime( startFrame )
    # attrs
    # rot
    rot_side = sideUpFront[2].upper()
    rot_up = sideUpFront[1].upper()
    rot_front = sideUpFront[0].upper()
    # pos
    pos_side = sideUpFront[0].upper()
    pos_up = sideUpFront[1].upper()
    pos_front = sideUpFront[2].upper()

    # start pose
    rot_side_pose = cmds.getAttr( obj + '.rotate' + sideUpFront[2].upper() )
    rot_up_pose = cmds.getAttr( obj + '.rotate' + sideUpFront[1].upper() )
    rot_front_pose = cmds.getAttr( obj + '.rotate' + sideUpFront[0].upper() )
    pos_side_pose = cmds.getAttr( obj + '.translate' + sideUpFront[0].upper() )
    pos_up_pose = cmds.getAttr( obj + '.translate' + sideUpFront[1].upper() )
    pos_front_pose = cmds.getAttr( obj + '.translate' + sideUpFront[2].upper() )

    # delete anim
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    if deletePrevious:
        for attr in attrs:
            deleteAnim( obj = obj, attr = attr )

    # pose 1 neutral
    frame = startFrame
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose, itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose, itt = 'linear', ott = 'linear' )

    if torque and rotR > 0.0:
        # create torque function
        frame = compoundTorquePose( obj = obj, torqueAxis = rot_up, startFrame = frame, min = rotR * -1, max = rotR, transitionDuration = transitionDuration )

    # pose 2 forward
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( rotR * rotFlip[2] ), itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( posR * posFlip[2] ), itt = 'linear', ott = 'linear' )

    if torque and rotR > 0.0:
        # create torque function
        frame = compoundTorquePose( obj = obj, torqueAxis = rot_up, startFrame = frame, min = rotR * -1, max = rotR, transitionDuration = transitionDuration )

    # pose 3 side
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose + ( rotR * rotFlip[0] ), itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose, itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose + ( posR * posFlip[0] ), itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose, itt = 'linear', ott = 'linear' )

    if torque and rotR > 0.0:
        # create torque function
        frame = compoundTorquePose( obj = obj, torqueAxis = rot_up, startFrame = frame, min = rotR * -1, max = rotR, transitionDuration = transitionDuration )

    # pose 4 back
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( ( rotR * -1 ) * rotFlip[2] ), itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( ( posR * -1 ) * posFlip[2] ), itt = 'linear', ott = 'linear' )

    if torque and rotR > 0.0:
        # create torque function
        frame = compoundTorquePose( obj = obj, torqueAxis = rot_up, startFrame = frame, min = rotR * -1, max = rotR, transitionDuration = transitionDuration )

    # pose 5 other side
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose + ( ( rotR * -1 ) * rotFlip[0] ), itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose, itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose + ( ( posR * -1 ) * posFlip[0] ), itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose, itt = 'linear', ott = 'linear' )

    if torque and rotR > 0.0:
        # create torque function
        frame = compoundTorquePose( obj = obj, torqueAxis = rot_up, startFrame = frame, min = rotR * -1, max = rotR, transitionDuration = transitionDuration )

    '''
    # pose 6 forward
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( rotR * rotFlip[2] ) )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( posR * posFlip[2] ) )'''

    # pose 7 neutral
    frame = frame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose, itt = 'linear', ott = 'linear' )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose, itt = 'linear', ott = 'linear' )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose, itt = 'linear', ott = 'linear' )

    # print( '____________', frame )
    # eulerFilter( obj, tangentFix = True )
    return frame


def compoundTorquePose( obj = '', torqueAxis = 'y', startFrame = 1001, min = -1.0, max = 1.0, transitionDuration = 10, deletePrevious = False ):
    '''
    create torque function
    neutral to xfrom object space rotation, similar to simplePose() or pose()
    add baked transitions, interpolation is bad otherwise, unless rotate orders are perfect
    '''
    #
    frame = startFrame
    cmds.currentTime( frame )
    rotP = cmds.xform( obj, q = True, os = True, ro = True )
    transforms = [ 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']

    # delete anim
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    if deletePrevious:
        for attr in attrs:
            deleteAnim( obj = obj, attr = attr )

    # pose 1
    cmds.currentTime( frame )
    cmds.xform( obj, os = False, r = False, ro = rotP )
    cmds.setKeyframe( obj, at = transforms )
    # pose 2 & 3
    if torqueAxis.lower() == 'x':
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = min, transitionDuration = transitionDuration )
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = ( min * -1 ) + max, transitionDuration = transitionDuration * 2 )
    else:
        print( 'no x' )
    #
    if torqueAxis.lower() == 'y':
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = min, transitionDuration = transitionDuration )
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = ( min * -1 ) + max, transitionDuration = transitionDuration * 2 )
    else:
        print( 'no y' )
    #
    if torqueAxis.lower() == 'z':
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = min, transitionDuration = transitionDuration )
        frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = ( min * -1 ) + max, transitionDuration = transitionDuration * 2 )

    else:
        print( 'no z' )
    # pose 4
    frame = torqueTransition( obj = obj, torqueAxis = torqueAxis, startFrame = frame, amount = max * -1, transitionDuration = transitionDuration )

    # eulerFilter( obj, tangentFix = True )
    return frame


def torqueTransition( obj = '', torqueAxis = '', startFrame = 1, amount = 1.0, transitionDuration = 10 ):
    '''
    create frame by frame transition, to overcome rotate order problems
    '''
    #
    cmds.currentTime( startFrame )
    transforms = [ 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']
    rotP = cmds.xform( obj, q = True, os = True, ro = True )
    step = amount / transitionDuration
    # print( '___step', step )
    # print('___start', startFrame)
    #
    i = 1
    if torqueAxis.lower() == 'x':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [step * i, 0, 0] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            i = i + 1
    if torqueAxis.lower() == 'y':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [0, step * i, 0] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            print( step * i )
            i = i + 1
    if torqueAxis.lower() == 'z':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [0, 0, step * i] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            i = i + 1
    return startFrame + transitionDuration


def osRotation( obj = '', axis = '', startFrame = 1, amount = 1.0, transitionDuration = 10, deletePrevious = True ):
    '''
    create frame by frame transition, to overcome rotate order problems
    '''
    #
    cmds.currentTime( startFrame )
    transforms = [ 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']
    rotP = cmds.xform( obj, q = True, os = True, ro = True )
    step = amount / transitionDuration
    # print( '___step', step )
    # print('___start', startFrame)

    # delete anim
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    if deletePrevious:
        for attr in attrs:
            deleteAnim( obj = obj, attr = attr )

    cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
    #
    i = 1
    if axis.lower() == 'x':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [step * i, 0, 0] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            i = i + 1
    if axis.lower() == 'y':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [0, step * i, 0] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            print( step * i )
            i = i + 1
    if axis.lower() == 'z':
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            cmds.xform( obj, os = True, r = True, ro = [0, 0, step * i] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            i = i + 1
    #
    eulerFilter( obj, tangentFix = True )
    return startFrame + transitionDuration


def osMultiAxisRotation( obj = '', startFrame = 1, amount = [0.0, 0.0, 0.0], transitionDuration = 10, deletePrevious = True, relative = True ):
    '''
    create frame by frame transition, to overcome rotate order problems
    '''
    #
    cmds.currentTime( startFrame )
    transforms = [ 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']
    rotP = cmds.xform( obj, q = True, os = True, ro = True )
    #
    stepX = 0.0
    stepY = 0.0
    stepZ = 0.0
    #
    if relative:
        if amount[0]:
            stepX = amount[0] / transitionDuration
        if amount[1]:
            stepY = amount[1] / transitionDuration
        if amount[2]:
            stepZ = amount[2] / transitionDuration
    else:
        if amount[0]:
            stepX = ( amount[0] - rotP[0] ) / transitionDuration
        if amount[1]:
            stepY = ( amount[1] - rotP[1] ) / transitionDuration
        if amount[2]:
            stepZ = ( amount[2] - rotP[2] ) / transitionDuration
    # print( '___step', step )
    # print('___start', startFrame)

    # delete anim
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    if deletePrevious:
        for attr in attrs:
            deleteAnim( obj = obj, attr = attr )

    cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
    #
    i = 1
    if relative:
        while i < transitionDuration + 1:
            cmds.currentTime( startFrame + i )
            cmds.xform( obj, os = False, ro = rotP )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            if relative:
                cmds.xform( obj, os = True, r = relative, ro = [stepX * i, stepY * i, stepZ * i] )
            else:
                pass
                # cmds.xform( obj, os = True, a = True, ro = [rotP[0] - ( stepX * i ), rotP[0] - ( stepY * i ), rotP[0] - ( stepZ * i )] )
            cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
            i = i + 1
    else:
        cmds.currentTime( startFrame + transitionDuration )
        cmds.xform( obj, os = True, a = True, ro = amount )
        cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
    #
    eulerFilter( obj, tangentFix = True )
    return startFrame + transitionDuration


def osMultiAxisPosition( obj = '', startFrame = 1, amount = [0.0, 0.0, 0.0], transitionDuration = 10, deletePrevious = True ):
    '''
    create frame by frame transition
    '''
    #
    cmds.currentTime( startFrame )
    transforms = [ 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']
    transP = cmds.xform( obj, q = True, t = True )
    #
    stepX = 0.0
    stepY = 0.0
    stepZ = 0.0
    #
    if amount[0]:
        stepX = amount[0] / transitionDuration
    if amount[1]:
        stepY = amount[1] / transitionDuration
    if amount[2]:
        stepZ = amount[2] / transitionDuration
    # print( '___step', step )
    # print('___start', startFrame)

    # delete anim
    attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    if deletePrevious:
        for attr in attrs:
            deleteAnim( obj = obj, attr = attr )

    cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
    #
    i = 1
    while i < transitionDuration + 1:
        cmds.currentTime( startFrame + i )
        cmds.xform( obj, os = False, t = transP )
        cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
        cmds.xform( obj, os = True, r = True, t = [stepX * i, stepY * i, stepZ * i] )
        cmds.setKeyframe( obj, at = transforms, itt = 'linear', ott = 'linear' )
        i = i + 1
    #
    eulerFilter( obj, tangentFix = True )
    return startFrame + transitionDuration


def listAttrs( obj = '' ):
    '''
    returns unlocked attr list
    '''
    transforms = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
    unlocked = []
    attrs = cmds.listAttr( obj, k = 1 )
    if attrs:
        for attr in attrs:
            if attr in transforms:
                unlocked.append( attr )
        # print( unlocked )
        return unlocked
    return None


def qualifyType():
    '''
    tries to guess at body part type
    '''
    pass


def deleteAnim( obj = '', attr = '' ):
    '''
    deletes any existing keys
    '''
    ac.deleteAnim2( obj, attrs = [attr] )


def distance( a = '', b = '' ):
    '''
    returns distance between controls
    '''
    pass


def setFrameRange( start = 1001, end = 1101 ):
    '''
    sets range
    '''
    cmds.playbackOptions( minTime = start )
    cmds.playbackOptions( animationStartTime = start )
    cmds.playbackOptions( maxTime = end )
    cmds.playbackOptions( animationEndTime = end )


def eulerFilter( obj, tangentFix = False ):
    curves = cmds.keyframe( obj, q = True, name = True )
    euler = []
    if curves:
        for crv in curves:
            c = curveNodeFromName( crv )
            if c.animCurveType() == 0:  # angular
                euler.append( crv )
        if euler:
            cmds.filterCurve( euler )
        if tangentFix:
            fixTangents( obj )
        # print 'here'


def curveNodeFromName( crv = '' ):
    selectionList = OpenMaya.MSelectionList()
    selectionList.add( crv )
    dependNode = OpenMaya.MObject()
    selectionList.getDependNode( 0, dependNode )
    crvNode = OpenMayaAnim.MFnAnimCurve( dependNode )
    return crvNode


def fixTangents( obj, attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'] ):
    animCurves = cmds.findKeyframe( obj, c = True )
    for crv in animCurves:
        for attr in attrs:
            if attr in crv:
                if 'step' in cmds.keyTangent( crv, q = True, ott = True ):
                    frames = cmds.keyframe( crv, q = True )
                    ott = cmds.keyTangent( crv, q = True, ott = True )
                    ot = []
                    it = []
                    for o in ott:
                        if o == 'step':
                            ot.append( 'step' )
                            it.append( 'auto' )
                        else:
                            ot.append( 'auto' )
                            it.append( 'auto' )
                    for i in range( len( frames ) ):
                        cmds.keyTangent( crv, edit = True, t = ( frames[i], frames[i] ), itt = it[i], ott = ot[i] )
                else:
                    cmds.keyTangent( crv, edit = True, itt = 'auto', ott = 'auto' )

'''
import webrImport as web
rom = web.mod("rangeOfMotion")
rom.poseLoop(startFrame = 1001, rotR = 45, posR = 0.50, sclR = 0.0, transitionDuration = 10, framesToNeutral = 1)

import webrImport as web
rom = web.mod("rangeOfMotion")
rom.simplePoseLoop(startFrame = 1001, rotR = 90, posR = 5.00, sclR = 0.0, transitionDuration = 10)

import webrImport as web
rom = web.mod("rangeOfMotion")
sel = cmds.ls(sl=1)[0]
rom.compoundTorquePose( obj = sel, torqueAxis = 'y', startFrame = 1001, min = -56.0, max = 75.0, transitionDuration = 10 )

sel = cmds.ls(sl=1)[0]
cmds.xform( sel, os = True, r = True, ro = [0, -10, 0] )

import webrImport as web
rom = web.mod("rangeOfMotion")
startFrame = 1
current = startFrame
current = rom.compoundPose('head', startFrame = current, rotR = 0, posR = 5.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [-1, 1, 1], torque=0)
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('head', startFrame = current, rotR = 60, posR = 5.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [-1, 1, 1], torque=0, deletePrevious = False)
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('head', startFrame = current, rotR = 60, posR = 5.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [-1, 1, 1], deletePrevious = False)
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('neck', startFrame = current, rotR = 30, posR = 0.0, transitionDuration = 10, sideUpFront = ['x', 'z', 'y'], rotFlip = [-1, 1, 1], posFlip = [1, 1, 1])
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('chest', startFrame = current, rotR = 30, posR = 5.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [-1, 1, -1], posFlip = [-1, 1, 1])
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('chest', startFrame = current, rotR = 40, posR = 20.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [-1, 1, 1], deletePrevious = False)
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('pelvis', startFrame = current, rotR = 30, posR = 2.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [-1, 1, -1], posFlip = [-1, 1, 1])
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('cog', startFrame = current, rotR = 50, posR = 5.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [-1, 1, -1], posFlip = [-1, 1, 1])
rom.setFrameRange( start = startFrame, end = current )
current = rom.compoundPose('hand_L', startFrame = current, rotR = 70, posR = 0.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [-1, 1, 1])
rom.setFrameRange( start = startFrame, end = current )
'''
