import os
import maya.cmds as cmds
import maya.mel as mel
import math
import json
import tempfile
import urllib
import imp
import shutil
#
# import display_lib as ds
import webrImport as web
# web
ds = web.mod('display_lib')

# FUTURE: use Castejeau method to draw nicer curve
# TODO: too many module imports for cloud usage... fix
# globals
idB = None
glPlg = None


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def jobValue(*args):
    que = cmds.undoInfo(q=1, un=1)
    # only run if undo que has a keyframe -edit entry
    if 'keyframe -edit' in que:
        # local curves
        lcCrv = cmds.keyframe(q=True, name=True, sl=True)
        lcVal = []
        # set
        G = globalLoad()
        glVal = G['glVal']
        glCrv = G['glCrv']
        if not glCrv or glCrv != lcCrv:  # set globals
            # set local
            glCrv = lcCrv
        if glCrv == lcCrv:  # continue
            c = 0
            for crv in lcCrv:
                frames = cmds.keyframe(crv, q=True, sl=True)
                # drop = len(frames)
                drop = 5
                if drop == 1:
                    func = [0, 1]
                else:
                    func = [2, 2]
                startFrame = frames[0]
                endFrame = frames[len(frames) - 1]
                frames = [startFrame, endFrame]
                # print '__________________________________________________________________'
                # print frames, '___frames'
                # iterators for correct list positions in global vars
                v = 0
                side = ['l', 'r']
                for frame in frames:
                    # print frame, '__ left right frame ittr'
                    lcVal = cmds.keyframe(crv, q=True, vc=True, time=(frame, frame))[0]
                    # print glVal, '    glVal'
                    glval = glVal[c][v]
                    if glval != lcVal:
                        # print glval, '__global ', lcVal, '__local '
                        offset = glval - lcVal
                        if offset < 0:
                            offset = offset * -1
                        framesBlend = neibors(crv=crv, splitFrame=frame, drop=drop, direction=side[v])
                        # needs to be start at 1, 0 is the first position, full weight
                        b = 1
                        for f in framesBlend:
                            # print f, '__blend frame ittr'
                            if f != frame:
                                if v == 0:
                                    # left side of plsit frame
                                    # do math to figure out frame position in drop range
                                    pos = frame - f
                                    # flip value so blendweight gets correct input
                                    pos = drop - pos + 1
                                    # print pos
                                    # get blend weight value with position number
                                    # blnd = blendWeight2(drop, b)[1]
                                    blnd = blendWeight2(drop, pos, func[0])[1]
                                    # print blnd, '____start'
                                else:
                                    # do math to figure out frame position in drop range
                                    pos = f - frame
                                    # print pos
                                    # get blend weight value with position number
                                    # right side of plsit frame
                                    # blnd = blendWeight2(drop, b)[0]
                                    blnd = blendWeight2(drop, pos, func[1])[0]
                                    # print blnd, '____end'
                                val = cmds.keyframe(crv, q=True, vc=True, time=(f, f))[0]
                                if glval < lcVal:
                                    cmds.keyframe(crv, vc=val + (offset * blnd), time=(f, f))
                                    # cmds.keyTangent( crv, edit=True, itt='auto', ott='auto', time=(f, f))
                                elif glval > lcVal:
                                    cmds.keyframe(crv, vc=val - (offset * blnd), time=(f, f))
                                    # cmds.keyTangent( crv, edit=True, itt='auto', ott='auto', time=(f, f))
                            b = b + 1
                        # reset global, stops loop from running!!!
                        glVal[c][v] = lcVal
                        # message('did math')
                        # message('\n\n')
                    else:
                        pass
                        # print '________________________value variable is the same'
                    v = v + 1
                c = c + 1
            globalInitiate()
        else:
            # message('nothing to act on')
            pass


def jobUndo(*args):
    # need to reset globals if an undo is detected
    que = cmds.undoInfo(q=1, rn=1)
    if 'import curveSoftSelect as css' in que or 'jobValue' in que:
        cmds.undo()
    killValueJob()
    activateValueJob()


def killUndoJob(*args):
    # print '___killing undo job'
    getJobs = cmds.scriptJob(lj=True)
    # print getJobs
    jobs = []
    for job in getJobs:
        if "jobUndo" in job:
            # print job, '______________ undo job'
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)
    # message('Undo script OFF', maya=True)


def activateUndoJob(*args):
    cmds.scriptJob(e=["Undo", "import webrImport as web\ncss = web.mod('curveSoftSelect')\ncss.jobUndo()"])
    # cmds.scriptJob(e=["Undo", "import curveSoftSelect as css\ncss.jobUndo()"])
    # message('Undo script ON', maya=True)


def killValueJob(*args):
    getJobs = cmds.scriptJob(lj=True)
    # print getJobs
    jobs = []
    for job in getJobs:
        if "jobValue" in job:
            # print job, '______________ value job'
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)
    globalReset()
    # message('Value script OFF', maya=True)


def activateValueJob(*args):
    if plug():
        globalInitiate()
        cmds.scriptJob(ac=[plug(), "import webrImport as web\ncss = web.mod('curveSoftSelect')\ncss.jobValue()"])
        # cmds.scriptJob(ac=[plug(), "import curveSoftSelect as css\ncss.jobValue()"])
        message('Value script ON', maya=True)
    else:
        # message('nothing selected ____coudn\'t activate')
        pass


def jobSel(*args):
    # local curves
    lcCrv = cmds.keyframe(q=True, name=True, sl=True)
    if lcCrv:
        killValueJob()
        activateValueJob()
        # print 'activate value'
    else:
        killValueJob()
        # print 'killed value'


def killSelJob(*args):
    getJobs = cmds.scriptJob(lj=True)
    # print getJobs
    jobs = []
    for job in getJobs:
        if "jobSel" in job:
            jobs.append(job.split(':')[0])
    if len(jobs) > 0:
        for job in jobs:
            cmds.scriptJob(kill=int(job), force=True)
        # message('Sel script OFF', maya=True)
        return True
    else:
        return False


def toggleSelJob(*args):
    global idB
    idS = killSelJob()
    if idS:
        idB = True
        killValueJob()
        killUndoJob()
        toggleButton()
        if os.path.isfile(globalPath()):
            os.remove(globalPath())
            '''
        if os.path.isdir(dir):'''

        message('Soft key Selection OFF', maya=True)
    else:
        idB = False
        killUndoJob()
        cmds.scriptJob(e=["SelectionChanged", "import webrImport as web\ncss = web.mod('curveSoftSelect')\ncss.jobSel()"])
        # cmds.scriptJob(e=["SelectionChanged", "import curveSoftSelect as css\ncss.jobSel()"])
        jobSel()
        activateUndoJob()
        toggleButton()
        message('Soft key Selection ON', maya=True)


def makeLocal(*args):
    # download module
    modulename = 'curveSoftSelect'
    url = 'https://raw.github.com/boochos/work/master/' + modulename + '.py'
    dir = tempfile.gettempdir() + '/' + modulename
    if not os.path.isdir(dir):
        os.mkdir(dir)
    urllib.urlretrieve(url, os.path.join(dir, modulename + '.py'))


def removeLocal(*args):
    path = ''
    shutil.rmtree(path)


def importLocal(*args):
    # var
    modulename = 'curveSoftSelect'
    varPath = os.path.expanduser('~') + '/maya/scripts/'
    webPath = 'https://raw.githubusercontent.com/boochos/work/master/'

    # create module
    urlPath = webPath + modulename + '.py'
    localPath = varPath + modulename + '.py'
    infile = open(localPath, 'r')
    contents = infile.read()

    # create module
    # must be exec mode
    codeobj = compile(contents, '', 'exec')
    module = imp.new_module(modulename)
    exec(codeobj, module.__dict__)
    return module


def globalReset(*args):
    global glPlg
    glPlg = None
    #
    G = globs()
    globalDump(G)
    # print '___reset globals'


def globalInitiate(*args):
    glVal = []
    frmTmp = []
    valTmp = []
    glCrv = cmds.keyframe(q=True, name=True, sl=True)
    for crv in glCrv:
        frames = cmds.keyframe(crv, q=True, sl=True)
        startFrame = frames[0]
        endFrame = frames[len(frames) - 1]
        frames = [startFrame, endFrame]
        for frame in frames:
            frmTmp.append(frame)
            valTmp.append(cmds.keyframe(crv, q=True, vc=True, time=(frame, frame))[0])
        glVal.append(valTmp)
        frmTmp = []
        valTmp = []
    G = globs()
    G['glCrv'] = glCrv
    G['glVal'] = glVal
    globalDump(G)
    # print '___initiate globals'


def globalLoad(*args):
    path = globalPath()
    fileObj = open(path, 'r')
    G = json.load(fileObj)
    return G


def globalDump(G, *args):
    path = globalPath()
    fileObj = open(path, 'wb')
    json.dump(G, fileObj, indent=2)


def globalPath(*args):
    # return os.path.expanduser('~') + '/softSelect_Temp.json'
    return tempfile.gettempdir() + '/softSelect_Temp.json'


def globalTempPath(*arg):
    pass


def globs():
    # needed for jobValue()
    return {'glCrv': None, 'glVal': None}


def plug(*args):
    crvs = cmds.keyframe(q=True, name=True, sl=True)
    if crvs:
        global glPlg
        glPlg = cmds.listConnections(crvs[0], s=0, d=1, p=1)[0]
        return glPlg
    else:
        message('no curves')


def toggleButton(*args):
    ds = web.mod('display_lib')
    ui = ds.GraphEditorButtonNames()
    # sftSel
    global idB
    # List shelf buttons
    buttons = cmds.lsUI(type='button')
    # iterate through buttons to find one using appropriate images
    for btn in buttons:
        if ui.sftSel in btn:
            if idB:
                # turn off
                cmds.button(btn, edit=True, bgc=[0.38, 0.38, 0.38])
                idB = False
            else:
                # turn on
                cmds.button(btn, edit=True, bgc=[0.3, 0.35, 0.5])
                idB = True


def neibors(crv='', splitFrame=0.0, drop=1, direction='l'):
    '''
    drop should consider frame boundaries and find keys within, not keyframes on either side
    '''
    frames = cmds.keyframe(crv, q=True)
    result = []
    if direction == 'l':
        dropoff = splitFrame - drop
    else:
        dropoff = splitFrame + drop
    for frame in frames:
        if direction == 'l':
            if frame >= dropoff and frame < splitFrame:
                result.append(frame)
        else:
            if frame <= dropoff and frame > splitFrame:
                result.append(frame)
    return result


def blendWeight2(numOfPoints=1, i=1, function=2, falloff=0.0):
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
    weight = [None, None]
    decay = 0
    # orig
    # numOfPoints = len(List)-1
    # new
    numOfPoints = numOfPoints + 1

    if function == 0:
        # Ease Out
        iDegree = 90 / numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff / numOfPoints
        else:
            decay = 0
        # weight[0] = math.cos(math.radians(iDegree*i))
        weight[0] = math.cos(math.radians(iDegree * i))
        weight[1] = 1 - weight[0]
        # weight[1] =  weight[1]/math.exp(decay*(len(List) -(i)))
        # weight[0] = 1 - weight[1]
        return weight
    elif function == 1:
        # Ease In
        iDegree = 90 / numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff / numOfPoints
        else:
            decay = 0
        # weight[1] = math.sin(math.radians(iDegree*i))
        weight[1] = math.sin(math.radians(iDegree * i))
        weight[0] = 1 - weight[1]
        # weight[0] = weight[0]/math.exp(decay*(i+1))
        # weight[1] = 1 - weight[0]
        return weight
    elif function == 2:
        # Ease Out Ease In
        iDegree = 180 / numOfPoints
        weight[0] = (math.cos(math.radians(iDegree * i)) * 0.5) + 0.5
        weight[1] = 1 - weight[0]
        return weight
    elif function == 3:
        # Ease In Ease Out
        iDegree = 180 / numOfPoints
        weight[1] = (math.sin(math.radians(iDegree * i)) * 0.5) + 0.5
        weight[0] = 1 - weight[1]
        return weight
    else:
        mel.eval('warning \"' + '////... function variable needs a value between 0 and 3...////' + '\";')
