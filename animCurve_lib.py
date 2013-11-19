import maya.cmds as cmds
import maya.mel as mel

def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')

class GetRange():
    def __init__(self):
        self.min = cmds.playbackOptions(q=True, minTime=True)
        self.max = cmds.playbackOptions(q=True, maxTime=True)
        self.current = cmds.currentTime(q=True)

def scaleCrv(val):
    '''
    -Scale selected Graph Editor curves with given value.
    -Pivot derived from selection - get selected keys of curves, if values are the same, the pivot is from that position, otherwise pivot defaults to 0.
    '''
    #get curves of selected keys
    crvs = cmds.keyframe(q=True, name=True, sl=True)
    pvt = 0.0
    if crvs != None:
        if len(crvs) == 1:
            #keys selected from one curve
            selKey_1 = cmds.keyframe(crvs, q=True, vc=True, sl=True)
            selKey_2 = list(set(cmds.keyframe(crvs, q=True, vc=True, sl=True)))
            if len(selKey_1) != len(selKey_2):
                message('1')
                #multiple keys selected, same value, pivot = 0
                cmds.scaleKey(crvs, vs=val, vp=pvt)
            elif len(selKey_1) == 1:
                pvt = selKey_1[0]
                cmds.scaleKey(crvs, vs=val, vp=pvt)
                message('Single key selected, pivot = ' + str(pvt))
            else:
                cmds.scaleKey(crvs, vs=val, vp=pvt)
                message('Multiple keys selected from one curve, pivot = ' + str(pvt))
        elif len(crvs) > 1:
            selKey = list(set(cmds.keyframe(crvs, q=True, vc=True, sl=True)))
            if len(selKey) == 1:
                pvt = selKey[0]
                message('Selected Keys from different curves have the same value, pivot = ' + str(pvt))
            else:
                message('Selected Keys have different values, pivot = ' + str(pvt))
            cmds.scaleKey(crvs, vs=val, vp=pvt)
    else:
        message('Select one or more keys in the graph editor. Pivots depend on selection.')

def holdCrv(postCurrent=True, preCurrent=True):
    crvs = cmds.keyframe(q=True, name=True, sl=True)
    if crvs != None:
        cur = GetRange()
        for crv in crvs:
            frames = cmds.keyframe(crv, q=True, tc=True)
            val = cmds.keyframe(crv, q=True, eval=True, t=(cur.current,cur.current))[0]
            for frame in frames:
                if postCurrent == True:
                    if frame >= cur.current:
                        cmds.keyframe(crv, vc=val, t=(frame,frame))
                        cmds.keyTangent( crv, inTangentType='auto', outTangentType='auto', time=(frame,frame) )
                if preCurrent == True:
                    if frame <= cur.current:
                        cmds.keyframe(crv, vc=val, t=(frame,frame))
                        cmds.keyTangent( crv, inTangentType='auto', outTangentType='auto', time=(frame,frame) )
    else:
        message( 'Select curve(s) in the Graph Editor. -- Current timeline value of selected curve will be held.')
        
def keyedFrames(obj):
    animCurves = cmds.findKeyframe(obj, c=True)
    if animCurves != None:
        frames = []
        for crv in animCurves:
            framesTmp = cmds.keyframe(crv, q=True)
            for frame in framesTmp:
                frames.append(frame)
        frames = list(set(frames))
        frames.sort()
        return frames
    else:
        message('-- Object given has no keys --')

def toggleTangentLock():
    state = cmds.keyTangent(q=True, lock=True)[0]
    if state == True:
        cmds.keyTangent(lock=False)
        message('Tangent Broken')
    else:
        cmds.keyTangent(lock=True)
        message('Tangent Unified')

def tangentStep(mltp=1.0001):
    angle = cmds.keyTangent( q=True, outAngle=True )[0]
    cmds.keyTangent( e=True, outAngle=angle + mltp )
