import os
import maya.cmds as cmds
import maya.mel as mel
import math

#global job id
idV    = None
idS    = None
#global vars
glVal  = []
glFrm  = []
glCrv  = []
glPlg  = None

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def jobValue(*args):
    #local curves
    lcCrv   = cmds.keyframe(q=True, name=True, sl=True)
    lcVal   = []
    #set
    global glCrv
    if not glCrv or glCrv != lcCrv: #set globals
        #set local
        glCrv = lcCrv
    if glCrv == lcCrv: #continue
        c = 0
        for crv in lcCrv:
            frames     = cmds.keyframe(crv, q=True, sl=True)
            startFrame = frames[0]
            endFrame   = frames[len(frames)-1]
            frames     = [startFrame, endFrame]
            print '__________________________________________________________________'
            print frames, '___frames'
            #iterators for correct list positions in global vars
            v = 0
            side = ['l', 'r']
            for frame in frames:
                print frame, '__ left right frame ittr'
                lcVal  = cmds.keyframe(crv, q=True, vc=True, time=(frame, frame))[0]
                glval  = glVal[c][v]
                if glval != lcVal:
                    print glval, '__global ', lcVal, '__local '
                    offset = glval - lcVal
                    if offset < 0:
                        offset = offset*-1
                    framesBlend = neibors(crv=crv, splitFrame=frame, drop=5, direction=side[v])
                    #needs to be start at 1, 0 is the first position, full weight
                    b = 1
                    for f in framesBlend:
                        print f, '__blend frame ittr'
                        if f != frame:
                            if v == 0:
                                blnd = blendWeight2(framesBlend, b)[1]
                                print blnd, '____start'
                            else:
                                blnd = blendWeight2(framesBlend, b)[0]
                                print blnd, '____end'
                            val  = cmds.keyframe(crv, q=True, vc=True, time=(f, f))[0]
                            if glval < lcVal:
                                cmds.keyframe(crv, vc=val+(offset*blnd), time=(f, f))
                            elif glval > lcVal:
                                cmds.keyframe(crv, vc=val-(offset*blnd), time=(f, f))
                        b=b+1
                    #reset global, stops loop from running!!!
                    glVal[c][v] = lcVal
                    message('did math')
                    message('\n\n')
                else:
                    print '________________________value variable is the same'
                v=v+1
            c=c+1
    else:
        message('_____________________________________________________nothing to act on')

def killValueJob():
    global idV
    print idV, '___killing value job'
    getJobs = cmds.scriptJob(lj=True)
    #print getJobs
    jobs = []
    for job in getJobs:
        if "jobValue()" in job:
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)
    global idV
    idV = None
    globalReset()
    message('Value script OFF', maya=True)

def activateValueJob():
    global idV
    print idV, '___activate'
    #print idV
    if plug():
        idV = cmds.scriptJob( ac= [plug(), "import curveSoftSelect as css\ncss.jobValue()"])
        #toggleIcon()
        globalInitiate()
        message('Value script ON', maya=True)
    else:
        print 'nothing selected ____coudn\'t activate'

def jobSel(*args):
    #local curves
    globalReset()
    lcCrv   = cmds.keyframe(q=True, name=True, sl=True)
    if lcCrv:
        killValueJob()
        activateValueJob()
        print 'activate value'
    else:
        killValueJob()
        print 'killed value'

def killSelJob():
    getJobs = cmds.scriptJob(lj=True)
    #print getJobs
    jobs = []
    for job in getJobs:
        if "jobSel()" in job:
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)

def toggleSelJob():
    global idS
    if idS:
        killSelJob()
        killValueJob()
        cmds.scriptJob( kill=idS, force=True)
        idS = None
        #toggleIcon()
        message('Soft key Selection OFF', maya=True)
        globalReset()
    else:
        #print idS
        killSelJob()
        idS = cmds.scriptJob( e= ["SelectionChanged", "import curveSoftSelect as css\ncss.jobSel()"])
        jobSel()
        #toggleIcon()
        message('Soft key Selection ON', maya=True)

def globalReset():
    global glFrm
    glFrm = []
    global glVal
    glVal = []
    global glCrv
    glCrv = []
    global glPlg
    glPlg = None
    print '___reset globals'

def globalInitiate():
    global glCrv
    global glVal
    global glFrm
    frmTmp = []
    valTmp = []
    glCrv   = cmds.keyframe(q=True, name=True, sl=True)
    for crv in glCrv:
        frames = cmds.keyframe(crv, q=True, sl=True)
        startFrame = frames[0]
        endFrame   = frames[len(frames)-1]
        frames     = [startFrame, endFrame]
        for frame in frames:
            frmTmp.append(frame)
            valTmp.append(cmds.keyframe(crv, q=True, vc=True, time=(frame, frame))[0])
        glFrm.append(frmTmp)
        glVal.append(valTmp)
        frmTmp = []
        valTmp = []
    print glCrv
    print glVal
    print glFrm
    print '___initiate globals'

def plug():
    crvs   = cmds.keyframe(q=True, name=True, sl=True)
    if crvs:
        global glPlg
        glPlg = cmds.listConnections(crvs[0], s=0,d=1, p=1)[0]
        return glPlg
    else:
        pass

def neibors(crv='', splitFrame=0.0, drop=1, direction='l'):
    '''
    drop should consider frame bounderies and find keys within, not keyframes on either side
    '''
    frames = cmds.keyframe(crv, q=True)
    start  = []
    end    = []
    result = []
    i = 0
    for frame in frames:
        if frame == splitFrame:
            if direction == 'l':
                start = frames[i-drop:i]
                for f in start:
                    result.append(f)
                return result
            else:
                end   = frames[i+1:i+drop+1]
                for f in end:
                    result.append(f)
                print result
                return result
            #result.append(splitFrame)
        else:
            i = i + 1

def blendWeight2(List, i, function=2, falloff=0.0):
    '''
    Arguments:\n
        List = list of objects
        i = object
        function 0 = (ease in)
        function 1 = (ease out)
        function 2 = (ease in ease out)
        function 3 = (ease out ease in)\n
        falloff
        part of decay... not scripted yet
        <1 = (slower falloff)
        1< = (quicker falloff)        
        \r#decay 0 = default value
        \r#decay 1 = full decayed value
        \r#divide decay(1) by same number as angles then progressively add it through loop
        \r#division makes the falloff weighted towards  end (tall egg shape)
        \r#multiplication makes falloff weighted towards start (wide egg shape)
    '''
    weight = [None,None]
    decay = 0
    #orig
    #numOfPoints = len(List)-1
    #new
    numOfPoints = len(List)+1


    if function == 0:
        #Ease Out
        iDegree = 90/numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff/numOfPoints
        else:
            decay = 0
        ##weight[0] = math.cos(math.radians(iDegree*i))
        weight[0] = math.cos(math.radians(iDegree*i))
        weight[1] = 1 - weight[0]
        weight[1] =  weight[1]/math.exp(decay*(len(List) -(i)))
        weight[0] = 1 - weight[1]
        return weight
    elif function == 1:
        #Ease In
        iDegree = 90/numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff/numOfPoints
        else:
            decay = 0
        ##weight[1] = math.sin(math.radians(iDegree*i))
        weight[1] = math.sin(math.radians(iDegree*i))
        weight[0] = 1 - weight[1]
        weight[0] = weight[0]/math.exp(decay*(i+1))
        weight[1] = 1 - weight[0]
        return weight
    elif function == 2:
        #Ease Out Ease In
        iDegree = 180/numOfPoints
        weight[0] = (math.cos(math.radians(iDegree*i)) * 0.5) + 0.5
        weight[1] = 1 - weight[0]
        return weight
    elif function == 3:
        #Ease In Ease Out
        iDegree = 180/numOfPoints
        weight[1] = (math.sin(math.radians(iDegree*i)) * 0.5) + 0.5
        weight[0] = 1 - weight[1]
        return weight
    else:
        mel.eval('warning \"' + '////... function variable needs a value between 0 and 3...////' + '\";')
