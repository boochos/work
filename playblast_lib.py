import os
import maya.cmds as cmds
import maya.mel as mel
import subprocess
from functools import partial
from subprocess import call
import datetime

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def getDefaultPath():
    return '/usr/tmp/___A___PLAYBLAST___A___/'

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
    if '.ma' in sceneName:
        sceneName = sceneName.split('.ma')[0]
    else:
        sceneName = sceneName.split('.mb')[0]
    slash = sceneName.rfind('/')
    sceneName = sceneName[slash+1:]
    #print sceneName, '___'
    if '(' in sceneName or ')' in sceneName:
        sceneName = sceneName.replace('(','__')
        sceneName = sceneName.replace(')','__')
    return sceneName

def shotDir():
    shotDir = sceneName()
    #remove version number, will need to customize for every pipeline
    shotDir = shotDir + '/'
    #print shotDir, '======'
    return shotDir

def shotDir2(idx=7):
    shotDir = sceneName(full=1)
    shotDir = shotDir.split('/')[idx]
    #remove version number, will need to customize for every pipeline
    shotDir = shotDir + '/'
    #print shotDir, '======'
    return shotDir

def createPath(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        print "-- path:   '" + path + "'   already exists --"

def blastDir(forceTemp=True):
    if not forceTemp:
        if os.name == 'nt':
            project = cmds.workspace( q=True, rd=True )
            scene = sceneName(full=True)
            if project in scene:
                if '(' in project or ')' in project:
                    project = project.replace('(','__')
                    project = project.replace(')','__')
                #print project
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
                print None, '____'
                return None
                #print project, 'here'
                #print scene, 'here'
        else:
            return getDefaultPath()
    else:
        print '  temp'
        return getDefaultPath()

def blast(w=1920, h=789, x=1, format='qt', qlt=100, compression='H.264', offScreen=True):
    min, max = blastRange()
    w = w*x
    h = h*x
    #print '___'
    #max = max + 1 #compensating for maya clipping last frame
    if os.name == 'nt':
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            print blastDir(), '   blastdir'
            pbName = blastDir()+sceneName()
            if os.path.exists(pbName):
                print True
            if 'image' not in format:
                #path = cmds.playblast(format=format, filename=blastDir()+sceneName(), sound=sound(), showOrnaments=True, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
                path = cmds.playblast(format=format, filename=blastDir()+sceneName(), sound=sound(), showOrnaments=False, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
            else:
                createPath(blastDir())
                createPath(blastDir() + shotDir())
                path = cmds.playblast(format='image', filename=blastDir()+shotDir()+sceneName(), showOrnaments=False, st=min, et=max, viewer=False, fp=4, fo=True, offScreen=offScreen, percent=100, compression='png', width=w, height=h)
                rvString = "\"C:/Program Files/Tweak/RV-3.12.12-64/bin/rv.exe\" " + "[ " + path + " -in " + str(min) + " -out " + str(max) + " ]"
                print rvString
                subprocess.Popen(rvString)
                #cmds.currentTime(current)
    elif os.name == 'posix':
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            pbName = shotDir2()+sceneName()
            if os.path.exists(pbName):
                print True
            if 'image' not in format:
                path = cmds.playblast(format=format, filename=shotDir2()+sceneName(), sound=sound(), showOrnaments=False, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
            else:
                createPath(path = blastDir())
                createPath(path = blastDir() + shotDir2())
                createPath(path = blastDir() + shotDir2()+ sceneName())
                playLo, playHi, current = getRange()
                w = w * x
                h = h * x
                path = cmds.playblast(format='image', filename=blastDir()+shotDir2()+sceneName()+ '/' +sceneName(), showOrnaments=False, st=min, et=max, viewer=False, fp=4, fo=True, offScreen=offScreen, percent=100, compression='png', width=w, height=h)
                rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
                print rvString
                os.system(rvString)
                cmds.currentTime(current)
    else:
        createPath(path = blastDir())
        createPath(path = blastDir() + shotDir2())
        playLo, playHi, current = getRange()
        w = w * x
        h = h * x
        path = cmds.playblast(format='image', filename=blastDir()+shotDir2()+sceneName(), showOrnaments=False, st=min, et=max, viewer=False, fp=4, fo=True, offScreen=offScreen, percent=100, compression='png', width=w, height=h)
        rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
        print rvString
        os.system(rvString)
        cmds.currentTime(current)
    blastWin()

def blastWin():
    rootDir = getDefaultPath()
    suf = '_PB'
    winName = 'PB_Man'
    if not cmds.window(winName, q=1, ex=1):
        win = cmds.window(winName, rtf=1)
        f1 = cmds.formLayout('mainForm' + suf)
        field        = cmds.textField('defaultPath1', text=rootDir)
        cmds.formLayout(f1, e=1, af=(field, 'top', 10))
        cmds.formLayout(f1, e=1, af=(field, 'left', 5))
        cmds.formLayout(f1, e=1, af=(field, 'right', 5))

        scrollBar       = 16
        scrollBarOffset = 50
        scrollLayout = cmds.scrollLayout('scroll' + suf, horizontalScrollBarThickness=scrollBar, verticalScrollBarThickness=scrollBar, cr=1)
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'bottom', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'top', scrollBarOffset))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'left', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'right', 0))
        height    = 100
        col0      = 20
        col1      = 200
        col2      = 300
        col3      = 50
        width     = col1+col2+col3
        wAdd      = scrollBar+10
        blastDirs = getBlastDirs(rootDir)
        f2 = cmds.formLayout('subForm' + suf, h=height*len(blastDirs), w=width, bgc=[0.17,0.17,0.17])
        #print f2

        i=0
        ann = ''
        for blastDir in blastDirs:
            cmds.setParent(f2)
            annNew = buildRow(blastDir, offset=i, height=height, parent=f2, col=[col0,col1,col2,col3], ann=ann)
            ann = annNew
            i=i+height
        cmds.window(win, e=1, w=width+wAdd, h=(height*5)+scrollBarOffset)
        cmds.showWindow()
    else:
        cmds.deleteUI(winName)
        blastWin()

def buildRow(blastDir='', offset=1,  height=1,  parent='', col=[10, 10, 10, 10], ann=''):

    #stuff
    allCols = col[0] + col[1] + col[2] + col[3]
    #path = os.path.join(rootDir, blastDir)
    path = blastDir
    blastDir = blastDir.split('/')
    blastDir = blastDir[len(blastDir)-1]
    imageRange = getImageRange(path)
    imageName  = getImageName(path)

    #iconSize
    icon = getIcon(path)
    w, h = getIconSize(icon)

    #row form
    f   = cmds.formLayout(blastDir + '_RowForm', h=height, bgc = [0.2,0.2,0.2])
    newAnn = f + '__' + str(offset)
    cmds.formLayout(parent, e=1, af=(f, 'top', offset))
    cmds.formLayout(parent, e=1, af=(f, 'left', 0))
    cmds.formLayout(parent, e=1, af=(f, 'right', 0))

    #update previous ann
    #need name of this form in previous row iteration
    ann = ann.split('__')[0]
    if ann:
        cmds.formLayout(ann, e=1, ann=newAnn)

    #checkbox
    chkBx = cmds.checkBox(blastDir + '_Check', l='', w=col[0])
    cmds.formLayout(f, e=1, af=(chkBx, 'top', height))
    cmds.formLayout(f, e=1, af=(chkBx, 'left', 0))

    #icon
    cmdI = 'partial( openSelected, path = path )'
    iconH = col[1]*(h/w)
    iconW = col[1]
    if iconH > height:
        iconH = height
        iconW = iconH*(w/h)
    iconBtn = cmds.iconTextButton(blastDir + '_Icon', st='iconOnly', image=icon, c=eval(cmdI), l=blastDir, w=iconW, h=iconH)
    cmds.formLayout(f, e=1, af=(iconBtn, 'bottom', 0))
    cmds.formLayout(f, e=1, af=(iconBtn, 'top', 0))
    cmds.formLayout(f, e=1, af=(iconBtn, 'left', col[0]))

    #meta
    pt    = path + '\n'
    sc    = 'Scene Name:  ' + blastDir + '\n'
    im    = 'Image Name:  ' + imageName + '\n'
    di    = 'Dimensions:  ' + str(w) + ' x ' + str(h) + '\n'
    fr    = 'From: ' + str(imageRange[0]) + '  To:  ' + str(imageRange[1]) + '\n'
    le    = 'Length: ' + str(imageRange[1]-imageRange[0]+1) + '\n'
    dt    = 'Date:  ' + getDirectoryDate(path)
    label = pt+sc+im+di+fr+le+dt

    metaBtn = cmds.iconTextButton(blastDir + '_Meta', st='textOnly', c="from subprocess import call\ncall(['nautilus',\'%s\'])" % (path),
    l=label, h=height, align='left', bgc = [0.2,0.2,0.2])
    cmds.formLayout(f, e=1, af=(metaBtn, 'bottom', 0))
    cmds.formLayout(f, e=1, af=(metaBtn, 'top', 0))
    cmds.formLayout(f, e=1, af=(metaBtn, 'left',col[1]+col[0]))
    cmds.formLayout(f, e=1, af=(metaBtn, 'right', col[3]))

    #delete
    cmds.setParent(f)
    delBtn  = cmds.button(blastDir + '_Delete', c= "import playblast_lib as pb\nreload(pb)\npb.removeRow(\'%s\')" % (f), l='DELETE', w=col[3], h=height, bgc = [0.4,0.4,0.4], ann=ann)
    cmds.formLayout(f, e=1, af=(delBtn, 'bottom', 0))
    cmds.formLayout(f, e=1, af=(delBtn, 'top', 0))
    cmds.formLayout(f, e=1, af=(delBtn, 'right', 0))
    return f

def removeRow(rowForm=''):
    ann = cmds.formLayout(rowForm, q=1, ann=1)
    print ann
    ann = ann.split('__')[0]
    if len(ann.split('__')) > 1:
        offset = int(ann.split('__')[1])
    else:
        offset = 0
    parents = rowForm.split('|')
    row = parents[len(parents)-1]
    print row
    parent = rowForm.split('|' + row)[0]
    print parent
    cmds.setParent(parents[len(parents)-4])
    cmds.formLayout(ann, af=(parent, 'top', offset-100))
    cmds.deleteUI(rowForm)

def getIcon(path=''):
    images = os.listdir(str(path))
    icon = os.path.join(path, images[0])
    #print icon
    return icon

def getIconSize(path=''):
    dim = subprocess.Popen(["identify","-format","\"%w,%h\"",path], stdout=subprocess.PIPE).communicate()[0]
    s = dim.split(',')
    w = float(s[0].split('"')[1])
    h = float(s[1].split('"')[0])
    return w, h

def getImageRange(path=''):
    images = os.listdir(str(path))
    images =  sorted(images)
    start  = float(images[0].split('.')[1])
    end    = float(images[len(images)-1].split('.')[1])
    return start, end

def getImageName(path=''):
    images = os.listdir(str(path))
    im = images[0].split('.')
    name = im[0] + '.*.' + im[2]
    return name

def openSelected(path=''):
    #playLo, playHi, current = getRange()
    #path = os.path.join(rootDir, blastDir)
    print '___'
    if os.name is 'nt':
        #path = path + sceneName() + '.####.png'
        #print path
        #rvString = "\"C:/Program Files/Tweak/RV-3.12.12-64/bin/rv.exe\" " + "[ " + path + " -in " + str(playLo) + " -out " + str(playHi) + " ]"
        #print rvString
        pass
        subprocess.Popen(rvString)
    elif os.name is 'posix':
        try:
            #path = path + sceneName() + '.####.png'
            #print path
            #rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
            rvString = 'rv ' + '[ ' + path + ' ]' ' &'
            print rvString, '  here'
            os.system(rvString)
        except:
            #print rvString
            print 'no success'
    else:
        #path = path + sceneName() + '.####.png'
        #print path
        pass
        rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
        os.system(rvString)

def getDirectoryDate(path=''):
    t = os.path.getmtime(path)
    return str(datetime.datetime.fromtimestamp(t))

def getShotDirs(path=''):
    shots = os.listdir(path)
    shotPaths = []
    for shot in shots:
        shotPaths.append(os.path.join(path, shot))
    return shotPaths

def getBlastDirs(path=''):
    #Make sure the path exists and access is permitted
    if os.path.isdir(path) and os.access(path, os.R_OK):
        #shot dirs
        shots = getShotDirs(path)
        #Populate the directories and non-directories for organization
        dirs      = []
        nonDir    = []
        sortedDir = []
        #list shots in the default path
        for shot in shots:
            mtime = lambda f: os.stat(os.path.join(shot, f)).st_mtime
            contents  = list(sorted(os.listdir(shot), key=mtime))
            print contents
            if len(contents) > 0:
                #Sort the directory list based on the names in lowercase
                #This will error if 'u' objects are fed into a list
                #files.sort(key=str.lower)
                #pick out the directories
                for i in contents:
                    if i[0] != '.':
                        if os.path.isdir(os.path.join(shot, i)):
                            dirs.append(os.path.join(shot,i))
                        else:
                            nonDir.append(i)
                for d in reversed(dirs):
                    sortedDir.append(d)
        return sortedDir