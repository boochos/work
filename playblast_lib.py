import os
import maya.cmds as cmds
import maya.mel as mel

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def getRange():
    min = cmds.playbackOptions(q=True, minTime=True)
    max = cmds.playbackOptions(q=True, maxTime=True)
    current = cmds.currentTime(q=True)
    return min, max, current

def selRange():
    selRange = cmds.timeControl('timeControl1', q=True, ra=True)
    min = selRange[0]
    max = selRange[1]
    range = max - min
    if range > 1:
        return min, max
    else:
        return False

def sound():
    gPlayBackSlider = mel.eval( '$tmpVar=$gPlayBackSlider' )
    fileName = cmds.timeControl( gPlayBackSlider, q=True, sound=True )
    if fileName:
        return fileName
    else:
        return None
        
def blastRange():
    blast = selRange()
    min = 0
    max = 0
    if blast == False:
        min, max, current = getRange()
    else:
        min = blast[0]
        max = blast[1]
    return min, max

def sceneName(full=False):
    sceneName = cmds.file(q=True, sn=True)
    if full:
        return sceneName
    sceneName = sceneName.split('.')[0]
    slash = sceneName.rfind('/')
    sceneName = sceneName[slash+1:]
    return sceneName

def shotDir():
    shotDir = sceneName()
    shotDir = shotDir[0:shotDir.rfind('-')+5] + '/'
    return shotDir

def createPath(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        print "-- path:   '" + path + "'   already exists --"
        
def blastDir():
    if os.name == 'nt':
        project = cmds.workspace( q=True, rd=True )
        scene = sceneName(full=True)
        if project in scene:
            return project + 'movies/'
        else:
            message('Project likely not set', maya=True)
            return None
            #print project
            #print scene
    elif os.name == 'posix':
        project = cmds.workspace( q=True, rd=True ).split('scenes/')[0]
        scene = sceneName(full=True)
        if project in scene:
            return project + 'movies/'
        else:
            message('Project likely not set', maya=True)
            return None
            #print project
            #print scene
    else:
        mainDir = '/usr/tmp/___A___PLAYBLAST___A___/'
        return mainDir

def blast(w=1280, h=720, x=1, format='qt', qlt=100, compression='H.264', offScreen=True):
    min, max = blastRange()
    w = w*x
    h = h*x
    #max = max + 1 #compensating for maya clipping last frame
    if os.name == 'nt':
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            pbName = blastDir()+sceneName()
            if os.path.exists(pbName):
                print True
            path = cmds.playblast(format=format, filename=blastDir()+sceneName(), sound=sound(), showOrnaments=False, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
    elif os.name == 'posix':
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            pbName = blastDir()+sceneName()
            if os.path.exists(pbName):
                print True
            path = cmds.playblast(format=format, filename=blastDir()+sceneName(), sound=sound(), showOrnaments=False, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
    else:
        createPath(path = blastDir())
        createPath(path = blastDir() + shotDir())
        playLo, playHi, current = getRange()
        w = w * x
        h = h * x
        path = cmds.playblast(format='image', filename=blastDir()+shotDir()+sceneName(), showOrnaments=False, st=min, et=max, viewer=False, fp=4, fo=True, offScreen=offScreen, percent=100, compression='png', width=w, height=h)
        rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
        print rvString
        os.system(rvString)
        cmds.currentTime(current)

def openLast():
    import os
    path = blastDir() + shotDir() + sceneName() + '.####.png'
    print path
    playLo, playHi, current = getRange()
    rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
    os.system(rvString)
