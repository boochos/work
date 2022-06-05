import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

cn = web.mod( 'constraint_lib' )
ds = web.mod( 'display_lib' )
ac = web.mod( 'animCurve_lib' )
plc = web.mod( 'atom_place_lib' )


def pose( obj = '', attr = '', startFrame = 1001, rotR = 90, posR = 2.0, sclR = 1.0, transitionDuration = 10, framesToNeutral = 10 ):
    '''
    create range of motion animation
    sclR needs to be between 0.1 - 1.
    '''
    #
    cmds.currentTime( startFrame )
    currentPose = cmds.getAttr( obj + '.' + attr )
    #
    rot_mlt = 1.0
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
    if rot in attr:
        # print( rotR )
        if rotR > 0:
            min = ( currentPose - rotR ) * rot_mlt
            max = ( currentPose + rotR ) * rot_mlt
        else:
            return startFrame
    if pos in attr:
        if posR > 0:
            min = ( currentPose - posR ) * pos_mlt
            max = ( currentPose + posR ) * pos_mlt
        else:
            return startFrame
    if scl in attr:
        if sclR > 0 and sclR < 1.0:
            min = ( currentPose * sclR ) * scl_mlt
            max = ( currentPose * ( 1.0 + sclR ) ) * scl_mlt
        else:
            return startFrame
    #
    frameStart = startFrame
    frameMin = startFrame + transitionDuration
    frameMax = frameMin + ( transitionDuration * 2 )
    frameEnd = frameMax + framesToNeutral
    #
    # print( attr, min, max )
    cmds.setKeyframe( obj + '.' + attr, t = frameStart, v = currentPose )
    cmds.setKeyframe( obj + '.' + attr, t = frameMin, v = min )
    cmds.setKeyframe( obj + '.' + attr, t = frameMax, v = max )
    cmds.setKeyframe( obj + '.' + attr, t = frameEnd, v = currentPose )

    return frameEnd


def poseLoop( startFrame = 1001, rotR = 90, posR = 1.00, sclR = 0.0, transitionDuration = 10, framesToNeutral = 10 ):
    '''
    get selection
    loop through objects
    loop through object axis
    create range of motion animation
    '''
    #
    sel = cmds.ls( sl = 1 )
    current = cmds.currentTime( startFrame )
    #
    for obj in sel:
        attrs = listAttrs( obj )
        if attrs:
            for attr in attrs:
                deleteAnim( obj, attr )
                current = pose( obj = obj, attr = attr, startFrame = current, rotR = rotR, posR = posR, sclR = sclR, transitionDuration = transitionDuration, framesToNeutral = framesToNeutral )
                # print(current)
    setFrameRange( start = startFrame, end = current )


def simplePose( obj = '', attr = '', startFrame = 1001, min = -1.0, max = 1.0, transitionDuration = 10 ):
    '''
    create range of motion animation
    '''
    #
    cmds.currentTime( startFrame )
    currentPose = cmds.getAttr( obj + '.' + attr )
    #
    frameStart = startFrame
    frameMin = startFrame + transitionDuration
    frameMax = frameMin + ( transitionDuration * 2 )
    frameEnd = frameMax + transitionDuration
    #
    # print( attr, min, max )
    cmds.setKeyframe( obj + '.' + attr, t = frameStart, v = currentPose )
    cmds.setKeyframe( obj + '.' + attr, t = frameMin, v = min )
    cmds.setKeyframe( obj + '.' + attr, t = frameMax, v = max )
    cmds.setKeyframe( obj + '.' + attr, t = frameEnd, v = currentPose )

    return frameEnd


def simplePoseLoop( startFrame = 1001, rotR = 90, posR = 1.00, sclR = 0.0, transitionDuration = 10 ):
    '''
    get selection
    loop through objects
    loop through object axis
    create range of motion animation
    '''
    #
    sel = cmds.ls( sl = 1 )
    current = cmds.currentTime( startFrame )
    #
    for obj in sel:
        attrs = listAttrs( obj )
        if attrs:
            for attr in attrs:
                #
                deleteAnim( obj, attr )
                currentPose = cmds.getAttr( obj + '.' + attr )
                #
                rot_mlt = 1.0
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
                    # print( rotR )
                    if rotR > 0:
                        min = ( currentPose - rotR ) * rot_mlt
                        max = ( currentPose + rotR ) * rot_mlt
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
    setFrameRange( start = startFrame, end = current )


def compoundRollPose( obj = '', startFrame = 1, rotR = 60, posR = 2.0, transitionDuration = 10, sideUpFront = ['x', 'y', 'z'], rotFlip = [1, 1, 1], posFlip = [1, 1, 1], deletePrevious = True, torque = False ):
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
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose )

    # pose 2 forward
    frame = startFrame + transitionDuration
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( rotR * rotFlip[2] ) )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( posR * posFlip[2] ) )

    if torque:
        # create torque function
        pass

    # pose 3 side
    frame = startFrame + ( transitionDuration * 2 )
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose + ( rotR * rotFlip[0] ) )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose + ( posR * posFlip[0] ) )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose )

    # pose 4 back
    frame = startFrame + ( transitionDuration * 3 )
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( ( rotR * -1 ) * rotFlip[2] ) )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( ( posR * -1 ) * posFlip[2] ) )

    # pose 5 other side
    frame = startFrame + ( transitionDuration * 4 )
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose + ( ( rotR * -1 ) * rotFlip[0] ) )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose + ( ( posR * -1 ) * posFlip[0] ) )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose )

    # pose 6 forward
    frame = startFrame + ( transitionDuration * 5 )
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose + ( rotR * rotFlip[2] ) )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose + ( posR * posFlip[2] ) )

    # pose 7 neutral
    frame = startFrame + ( transitionDuration * 6 )
    # rot
    cmds.setKeyframe( obj + '.rotate' + rot_side, t = frame, v = rot_side_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_up, t = frame, v = rot_up_pose )
    cmds.setKeyframe( obj + '.rotate' + rot_front, t = frame, v = rot_front_pose )
    # pos
    cmds.setKeyframe( obj + '.translate' + pos_side, t = frame, v = pos_side_pose )
    cmds.setKeyframe( obj + '.translate' + pos_up, t = frame, v = pos_up_pose )
    cmds.setKeyframe( obj + '.translate' + pos_front, t = frame, v = pos_front_pose )

    # print( '____________', frame )
    return frame


def compoundTorquePose():
    '''
    create torque function
    neutral to xfrom object space rotation, similar to simplePose() or pose()
    '''
    pass


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

