import os
import math
from math import sqrt
import maya.cmds  as cmds


def getControlPoints(crv='', p0=[1.0, 0.0], p3=[10.0, 10.0], time=0.0):
    # could use multiplier to adjust length of existing weights after key is inserted
    mltp = 0.3333333333333333  # multiplier to solve adjacent side, p[1] x coor, 33.333333333333%
    # gap between keys
    gap = p3[0] - p0[0]
    # print gap, ' gap'

    # p1
    outA = cmds.keyTangent(crv, q=True, time=(p0[0], p0[0]), outAngle=True)[0]
    # print outA, ' p1 hyp angle'
    adj = gap * mltp  # tangent coor in x
    # print adj, ' p1 adj length'
    opo = math.tan(math.radians(outA)) * (adj)
    # print opo, ' p1 opo height'
    p1 = [p0[0] + adj, p0[1] + opo]
    # print p1

    # p2
    outA = cmds.keyTangent(crv, q=True, time=(p3[0], p3[0]), inAngle=True)[0]
    # print outA, ' p2 hyp angle'
    adj = gap * mltp  # tangent coor in x
    # print adj, ' p2 adj length'
    opo = math.tan(math.radians(outA)) * adj
    # print opo, ' p2 opo height'
    p2 = [p3[0] - adj, p3[1] - opo ]  # adjusting, may need fixing for +/- angles
    # print p2
    # resort lists [x,x,x,x] [y,y,y,y]
    return [p0[0], p1[0], p2[0], p3[0]], [p0[1], p1[1], p2[1], p3[1]]


def getPoint(cor=[], t=0.0):
    '''
    returns 3 points of given weight(t) in given axis
    tangent1 = left tangent position in given axis
    point = point position on curve
    tangent2 = right tangent position in given axis    
    **works for weighted tangents
    **inserting into a weighted tangent means updating existing tangent weights
    '''
    AB = ((1 - t) * cor[0]) + (t * cor[1])
    BC = ((1 - t) * cor[1]) + (t * cor[2])
    CD = ((1 - t) * cor[2]) + (t * cor[3])

    tanIn = ((1 - t) * AB) + (t * BC)
    tanOut = ((1 - t) * BC) + (t * CD)

    point = ((1 - t) * tanIn) + (t * tanOut)
    return [tanIn, point, tanOut]


def getPointTangents(xList, yList):
    # dead simple, does not account for pos or neg values
    # does not account for non-weighted tangents
    # solves tangent weights and angles

    # in tangent angle
    xlength = xList[1] - xList[0]  # 'adjacent' side in trig speak
    ylength = yList[1] - yList[0]  # 'opposite' side in trig speak
    tan = ylength / xlength
    degIn = math.degrees(math.atan(tan))
    # print degIn
    # in weighted tangent, length
    hlength = xlength * xlength + ylength * ylength
    hlengthIn = sqrt(hlength)
    # print hlength

    # out tangent angle
    xlength = xList[2] - xList[1]  # 'adjacent' side in trig speak
    ylength = yList[2] - yList[1]  # 'opposite' side in trig speak
    tan = ylength / xlength
    degOut = math.degrees(math.atan(tan))
    # print degOut
    # in weighted tangent, length
    hlength = xlength * xlength + ylength * ylength
    hlengthOut = sqrt(hlength)
    # print hlength
    return degIn, hlengthIn, degOut, hlengthOut


def seekPoint(corX=[1, 4, 7, 10], corY=[0, 0, 10, 10], frame=3.25, errM=0.001, steps=1000):
    #####
    n = 4  # number of control points
    s = steps
    for k in range(s):
        # print k
        t = float(k) / (s - 1)
        # print t
        x = getPoint(corX, t)
        # print x, '   X'
        y = getPoint(corY, t)
        # print y, '  y'
        if x[1] > (frame - errM) and x[1] < (frame + errM):
            degIn, hlengthIn, degOut, hlengthOut = getPointTangents(x, y)
            # print y, 'here', x    #find tangents in B function maybe
            # print degIn, y[1], degOut
            return degIn, hlengthIn, y[1], degOut, hlengthOut
    # if loop fails due to high accuracy, keep trying
    # print 'seeking'
    s = s * 3
    # print s
    return seekPoint(corX, corY, frame, errM, s)


def feeder():
    smaller = []
    greater = []
    sel = cmds.ls(sl=1)[0]
    if sel:
        time = cmds.currentTime(q=1)
        crv = cmds.findKeyframe(sel, c=True)[0]
        # print crv
        frames = cmds.keyframe(crv, q=True)
        for frame in frames:
            if frame < time:
                smaller.append(frame)
            elif frame > time:
                greater.append(frame)
        #
        sm = smaller[len(smaller) - 1]
        y = cmds.keyframe(crv, q=True, time=(sm, sm), valueChange=True, a=True)[0]
        p0 = [sm, y]
        # print p0
        #
        gr = greater[0]
        y = cmds.keyframe(crv, q=True, time=(gr, gr), valueChange=True, a=True)[0]
        p3 = [gr, y]
        # print p3
        #
        # print time
        corX, corY = getControlPoints(crv, p0, p3, time)
        # print corX, corY
        degIn, hlengthIn, value, degOut, hlengthOut = seekPoint(corX, corY, time)
        # print degIn, value, degOut, crv
        cmds.setKeyframe(crv, time=(time, time), value=value)
        cmds.keyTangent(crv, edit=True, time=(time, time), inAngle=degIn, outAngle=degOut)
        if cmds.getAttr(crv + '.weightedTangents'):
            mltp = 0.3333333333333333
            cmds.keyTangent(crv, edit=True, time=(time, time), inWeight=hlengthIn)
            cmds.keyTangent(crv, edit=True, time=(time, time), outWeight=hlengthOut)
            # adjust existing tangent weights
            o = cmds.keyTangent(crv, q=True, time=(p0[0], p0[0]), outWeight=True)[0]
            i = cmds.keyTangent(crv, q=True, time=(p3[0], p3[0]), inWeight=True)[0]
            print o * mltp, o
            print i * mltp, i

            cmds.keyTangent(crv, edit=True, time=(p0[0], p0[0]), lock=False, outWeight=o * mltp)
            cmds.keyTangent(crv, edit=True, time=(p3[0], p3[0]), lock=False, inWeight=i * mltp)
            cmds.keyTangent(crv, edit=True, time=(p0[0], p0[0]), lock=True)
            cmds.keyTangent(crv, edit=True, time=(p3[0], p3[0]), lock=True)
    else:
        print 'Select something'

feeder()








