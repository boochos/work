import maya.cmds as cmds
import maya.mel as mel

def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')

class GetRange():
    def __init__(self):
        self.min = cmds.playbackOptions(q=True, minTime=True)
        self.max = cmds.playbackOptions(q=True, maxTime=True)
        self.current = cmds.currentTime(q=True)

'''
import animCurve_lib as ac
reload(ac)
objects = cmds.ls(sl=1)
start = cmds.playbackOptions(q=1,min=1)
end = cmds.playbackOptions(q=1,max=1)
bakeTimeWarp(objects,start,end,killWarp=True)
'''

def bakeTimeWarp(objects,start,end,killWarp=True):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe
    for i in objects:
        dupe = cmds.duplicate(i,po=1)[0]
        dupe = cmds.rename(dupe, dupe + '__warped')
        if not cmds.attributeQuery('bakeTimeWarpConnection',node=i,ex=1):
            cmds.addAttr(i,ln='bakeTimeWarpConnection',at='message')
        cmds.connectAttr(dupe+'.message',i+'.bakeTimeWarpConnection')
    for x in range(start,end+1):
        cmds.currentTime(x)
        outTime = cmds.getAttr('time1.outTime')
        unwarpedTime = cmds.getAttr('time1.unwarpedTime')
        for i in objects:
            # build a list of all keyed channels.
            keyables = cmds.listAttr(i,k=1)
            keyedChans = []
            for f in keyables:
                if cmds.keyframe(i+'.'+f,q=1,n=1):
                    try:
                        keyedChans.append(f)
                    except:
                        print f, '  skipped\n'
            dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
            for chan in keyedChans:
                val = cmds.getAttr(i+'.'+chan,t=outTime)
                cmds.setAttr(dupe+'.'+chan,val)
                cmds.setKeyframe(dupe+'.'+chan,t=unwarpedTime)
    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
        chans = [f for f in cmds.listAttr(dupe,k=1) if cmds.keyframe(dupe+'.'+f,q=1,n=1)]
        for chan in chans:
            animCurve = cmds.keyframe(dupe+'.'+chan,q=1,n=1)[0]
            oldCurve = cmds.keyframe(i+'.'+chan,q=1,n=1)
            cmds.connectAttr(animCurve+'.output',i+'.'+chan,f=1)
            cmds.delete(oldCurve)
        cmds.delete(dupe)
        cmds.deleteAttr(i+'.bakeTimeWarpConnection')
    if killWarp:
        timeWarp = cmds.listConnections('time1.timewarpIn_Raw')[0]
        cmds.delete(timeWarp)

def animScale():
    scale_factor = 4.0389
    scale_pivot  = cmds.playbackOptions(q=True, min=True)
    cmds.scaleKey(ts=scale_factor, tp=scale_pivot)


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
