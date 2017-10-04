from functools import partial
from subprocess import call
import datetime
import operator
import os
import platform
import shutil
import subprocess
import sys
import tempfile

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
#
# web
cl = web.mod('clips_lib')


# rgb gl color guide ## http://prideout.net/archive/colors.php
# http://www.tweaksoftware.com/static/documentation/rv/current/html/rv_manual.html
# layers = inputs in square brackets are layers
# -wipe = wipe view items
# -layout 'row' = side by side


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def getTempPath():
    blastD = '___A___PLAYBLAST___A___'
    tempD = tempfile.gettempdir()
    # print tempD, '__temp'
    return os.path.join(tempD, blastD)


def getPath(name='', temp=False):
    if temp:
        path = getTempPath()
    else:
        path = getDefaultPath()
    if os.path.isdir(path):
        return os.path.join(path, name)
    else:
        os.mkdir(path)
        return os.path.join(path, name)


def getDefaultPath():
    # print os.name
    varPath = cmds.internalVar(userAppDir=True)
    path = os.path.join(varPath, '__PLAYBLASTS__')
    # print path
    return path


def getWipe():
    return 'wipe_PB'


def getDefaultHeight():
    '''
    relating to pb man row height
    '''
    return 100


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


def sound(path=True):
    gPlayBackSlider = mel.eval('$tmpVar=$gPlayBackSlider')
    node = cmds.timeControl(gPlayBackSlider, q=True, sound=True)
    if not path:
        return node
    else:
        if node:
            fileName = cmds.sound(node, q=True, f=True)
            if fileName:
                # print fileName
                return fileName
            else:
                return None
        else:
            return False


def copySound(toPath=''):
    '''
    copy sound to playblast dir
    '''
    sndPath = sound()
    # print sndPath
    if sndPath:
        sndFile = sndPath.split('/')[len(sndPath.split('/')) - 1]
        # print sndFile
        shutil.copyfile(sndPath, os.path.join(
            sndPath, os.path.join(toPath, sndFile)))
        return sndPath
    else:
        return None


def blastRange():
    blast = selRange()
    min = 0
    max = 0
    if blast is False:
        min, max, current = getRange()
    else:
        min = blast[0]
        max = blast[1]
    return min, max


def camName():
    pnl = cmds.getPanel(withFocus=True)
    typ = cmds.getPanel(typeOf=pnl)
    if typ == 'modelPanel':
        cam = cmds.modelPanel(pnl, q=True, cam=True)
        if cam:
            typ = cmds.objectType(cam)
            if typ == 'camera':
                p = cmds.listRelatives(cam, p=True)[0]
                if ':' in p:
                    p = p.split(':')[1]
                return p
            else:
                if ':' in cam:
                    cam = cam.split(':')[1]
                return cam
        else:
            print 'no model returned', cam
    else:
        print 'not model panel', pnl


def sceneName(full=False, suffix=None, bracket=False):
    sceneName = cmds.file(q=True, sn=True)
    if full:
        return sceneName
    if '.ma' in sceneName:
        sceneName = sceneName.split('.ma')[0]
    else:
        sceneName = sceneName.split('.mb')[0]
    slash = sceneName.rfind('/')
    sceneName = sceneName[slash + 1:]
    # print sceneName, '___'
    if bracket:
        if '(' in sceneName or ')' in sceneName:
            sceneName = sceneName.replace('(', '__')
            sceneName = sceneName.replace(')', '__')
    # print sceneName, '_______get name'
    if suffix:
        sceneName = sceneName + suffix
    print sceneName
    return sceneName


def shotDir2(idx=7):
    shotDir = sceneName(full=1)
    shotDir = shotDir.split('/')[idx]
    shotDir = shotDir + '/'
    return shotDir


def createPath(path):
    print path
    if not os.path.isdir(path):
        # print path
        os.mkdir(path)
    else:
        pass
        # print "-- path:   '" + path + "'   already exists --"
    return path


def createBlastPath(suffix=None, forceTemp=False):
    '''
    bla
    '''
    createPath(path=blastDir(forceTemp=forceTemp))
    path = os.path.join(blastDir(forceTemp=forceTemp), sceneName())
    path = createPath(path)
    if suffix:
        path = path + sceneName() + suffix
    return path


def blastDir(forceTemp=False, brackets=False):
    '''
    forceTemp = use get default function to force a specified location, otherwise standard maya locations are used
    '''
    if not forceTemp:
        if os.name == 'nt':
            project = cmds.workspace(q=True, rd=True)
            scene = sceneName(full=True)
            if project in scene:
                if brackets:
                    if '(' in project or ')' in project:
                        project = project.replace('(', '__')
                        project = project.replace(')', '__')
                    # print project
                return project + 'movies/'
            else:
                message('Project likely not set', maya=True)
                return None
                # print project
                # print scene
        elif os.name == 'posix':
            project = cmds.workspace(q=True, rd=True).split('scenes/')[0]
            scene = sceneName(full=True)
            if project in scene:
                return project + 'movies/'
            else:
                message('Project likely not set', maya=True)
                # print None, '____'
                return None
                # print project, 'here'
                # print scene, 'here'
        else:
            return getPath()
    else:
        return getPath()


def blast(w=1920, h=1080, x=1, format='qt', qlt=70, compression='H.264', offScreen=True, useGlobals=False, forceTemp=True):
    '''
    rv player is mostly used to play back the images or movie files, function has gotten sloppy over time, cant guarantee competence
    '''
    # camName()
    min, max = blastRange()
    if useGlobals:
        w = cmds.getAttr('defaultResolution.width')
        h = cmds.getAttr('defaultResolution.height')
        pa = cmds.getAttr('defaultResolution.pixelAspect')
        h = h / pa
    else:
        w = int(float(w) * float(x))
        h = int(float(h) * float(x))
    # print w, h
    blastName = sceneName(full=False, suffix=None,
                          bracket=False) + '____' + camName()
    blastPath = createBlastPath('', forceTemp=forceTemp)
    blastFullPAth = os.path.join(blastPath, blastName)
    if not blastDir(forceTemp=forceTemp):
        message('Set project', maya=True)
    else:
        if 'image' not in format:
            path = cmds.playblast(format=format, filename=blastFullPAth, sound=sound(path=False), showOrnaments=True, st=min, et=max,
                                  viewer=False, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h, quality=qlt)
            openSelected(path=blastPath, name=blastName, ext='mov')
        else:
            playLo, playHi, current = getRange()
            # sound
            snd = copySound(toPath=createBlastPath('', forceTemp=forceTemp))
            # blast
            path = cmds.playblast(format='image', filename=blastFullPAth, showOrnaments=False, st=min, et=max, viewer=False,
                                  fp=4, fo=True, offScreen=offScreen, percent=100, compression=compression, width=w, height=h, quality=qlt)
            # play
            openSelected(path=blastPath, name=blastName,
                         ext=compression, start=str(playLo), end=str(playHi))
            cmds.currentTime(current)
    if cmds.window('PB_Man', q=True, ex=True):
        blastWin()


def blastWin():
    rootDir = getPath()
    # print rootDir, ' here'
    suf = '_PB'
    winName = 'PB_Man'
    if not cmds.window(winName, q=1, ex=1):
        # window
        win = cmds.window(winName, rtf=1)
        f1 = cmds.formLayout('mainForm' + suf)
        cmds.showWindow()
        # text field
        # field        = cmds.textField('defaultPath1', text=rootDir)
        # field = cmds.button('defaultPath1', label=rootDir, align='left', h=24, c="from subprocess import call\ncall(['nautilus',\'%s\'])" % (rootDir))
        field = cmds.button('defaultPath1', label=rootDir, align='left', h=24,
                            c="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.cmdOpen(\'%s\')" % (rootDir.replace('\\', '\\\\')))
        cmds.formLayout(f1, e=1, af=(field, 'top', 5))
        cmds.formLayout(f1, e=1, af=(field, 'left', 5))
        cmds.formLayout(f1, e=1, af=(field, 'right', 5))
        cmds.refresh(f=1)
        # refresh button
        refBtn = cmds.button('refresh' + suf, l='REFRESH',
                             c="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.blastWin()", h=24)
        attachForm = [(refBtn, 'top', 2, field)]
        cmds.formLayout(f1, edit=True, attachControl=attachForm)
        cmds.formLayout(f1, e=1, af=(refBtn, 'left', 5))
        cmds.formLayout(f1, e=1, af=(refBtn, 'right', 5))
        # flush button
        '''
        flushBtn = cmds.button('flush' + suf, l='DELETE ALL', c='import playblast_lib as pb\nreload(pb)\npb.flushDefaultDir()', h=16, w=100, bgc=[0.804, 0.361, 0.361])
        attachForm = [(flushBtn,'top', 2, refBtn)]
        cmds.formLayout(f1, edit=True, attachControl=attachForm)
        #cmds.formLayout(f1, e=1, af=(flushBtn, 'left', 5))
        cmds.formLayout(f1, e=1, af=(flushBtn, 'right', 5))
        #wipe button
        #rvString = 'rv ' + '[ ___' + 'None' + '___ ]' ' &'
        rvString = 'rv ' + ' -wipe' ' &'
        #test proper format
        rvString = 'rv','-wipe','-eval',';'

        wipBtn = cmds.button(getWipe(), l='WIPE', c='import subprocess\nsubprocess.Popen(%s)' % (getString(strings=rvString)), h=16, w=100)
        attachForm = [(wipBtn,'top', 2, refBtn)]
        cmds.formLayout(f1, edit=True, attachControl=attachForm)
        cmds.formLayout(f1, e=1, af=(wipBtn, 'left', 5))
        #cmds.formLayout(f1, e=1, af=(wipBtn, 'right', 5))
        #compare button
        '''

        # scroll
        scrollBar = 16
        scrollBarOffset = 75
        scrollLayout = cmds.scrollLayout(
            'scroll' + suf, horizontalScrollBarThickness=scrollBar, verticalScrollBarThickness=scrollBar, cr=1)
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'bottom', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'top', scrollBarOffset))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'left', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'right', 0))
        cmds.refresh(f=1)
        # row setup
        height = getDefaultHeight()
        col0 = 20
        col1 = 200
        col2 = 250
        col3 = 50
        width = col0 + col1 + col2 + col3
        wAdd = scrollBar + 10
        # status
        print '__detect'
        detectCompatibleStructure(rootDir)
        blastDirs = getBlastDirs(rootDir)
        # print blastDirs, '++++++++++++++++'

        if blastDirs:
            f2 = cmds.columnLayout(
                'column' + suf, w=width, bgc=[0.17, 0.17, 0.17], adj=True)
            cmds.refresh(f=1)
            # print f2
            # build rows
            # print blastDirs
            allClips = []
            for blastDir in blastDirs:
                contents = os.listdir(os.path.join(getPath(), blastDir))
                if contents:
                    # print 'here'
                    clips = getClips(path=os.path.join(getPath(), blastDir))
                    # print clips, '___clips'
                    if clips:
                        for clip in clips:
                            allClips.append(clip)
                            # cmds.setParent(f2)
                            # print blastDir
                            # print clip.name
                            # print clip.path
                            # print clip.dir
                            # buildRow_new(clip, height=height, parent=f2, col=[col0, col1, col2, col3])
                    cmds.refresh(f=1)
                else:
                    # rebuild
                    shutil.rmtree(blastDir)
                    cmds.deleteUI(winName)
                    blastWin()
                    break
            # start experiment for reordering clips according to date
            allClips.sort(key=operator.attrgetter('date'))
            allClips.reverse()
            for clip in allClips:
                cmds.setParent(f2)
                buildRow_new(clip, height=height, parent=f2,
                             col=[col0, col1, col2, col3])
            # end experiment
            cmds.window(win, e=1, w=width + wAdd,
                        h=(height * 4) + scrollBarOffset)
            cmds.refresh(f=1)
        else:
            message('no playblasts found', maya=True)
    else:
        cmds.deleteUI(winName)
        blastWin()


def buildRow_new(blastDir='', height=1, parent='', col=[10, 10, 10, 10]):
    # FIXME: breaks if 2 periods are in file name
    # FIXME: breaks if file name starts with a number
    # stuff
    alignI = 'center'
    alignM = 'left'
    alignD = 'right'
    w = 0
    h = 0
    padW = 0
    padH = 0
    padBtns = 2
    path = blastDir.path
    # print blastDir.__dict__

    # iconSize
    if os.path.isfile(blastDir.thumbnail):
        icon = blastDir.thumbnail
    else:
        icon = None
    # print 'icon'

    # row form
    f = cmds.rowLayout('row__' + blastDir.name + '__' + blastDir.ext, numberOfColumns=4, columnWidth4=(col[0], col[1], col[2], col[3]), adjustableColumn=3,
                       columnAttach=[(1, 'both', 0), (2, 'left', 0),
                                     (3, 'left', 0), (4, 'both', 0)],
                       columnAlign=[(1, 'center'), (2, alignI),
                                    (3, alignM), (4, alignD)],
                       h=height, bgc=[0.2, 0.2, 0.2], ann=blastDir.path)
    # checkbox
    chkBx = cmds.checkBox('check__' + blastDir.name, l='', w=col[0],
                          onc="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.addChecked(%s)" % (
                              getString(strings=[path])),
                          ofc="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.removeChecked(%s)" % (getString(strings=[path])))

    # icon
    cmdI = 'partial( openSelected, path=blastDir.path, name=blastDir.name, ext=blastDir.ext, start=blastDir.start, end=blastDir.end)'
    if icon and blastDir.width:
        w = float(blastDir.width)
        h = float(blastDir.height)
        print icon
        iconH = col[1] * (h / w)
        iconW = col[1]
        if iconH > height:
            iconH = height
            iconW = iconH * (w / h)
            padW = int((col[1] - iconW) / 2)
        if iconW < col[0]:
            padW = int((col[1] - iconW) / 2)
        if iconH < height:
            padH = int((height - iconH) / 2)
        # print blastDir.files
        iconBtn = cmds.iconTextButton(blastDir.name + '_Icon', st='iconOnly', image=icon, al=alignI, c=eval(
            cmdI), l=blastDir.name, w=iconW, h=iconH, iol='PLAY', mw=padBtns, mh=padBtns, bgc=[0.13, 0.13, 0.13])
    else:
        iconBtn = cmds.iconTextButton(blastDir.name + '_Icon', st='textOnly', al=alignI, c=eval(
            cmdI), l='- NO THUMBNAIL - \nINSTALL FFMPEG', w=col[1], h=height - padBtns, iol='PLAY', bgc=[0.13, 0.13, 0.13])

    # meta
    pt = '...' + path.split(getPath())[1].split('/')[0] + '\n'
    # sc    = 'Scene Name:  ' + blastDir + '\n'
    im = blastDir.name + '\n'
    di = str(int(w)) + ' x ' + str(int(h)) + '\n'
    fr = str(int(blastDir.start)) + '  -  ' + str(int(blastDir.end)) + '\n'
    le = str(int(blastDir.length)) + '  frames' + \
        '   ---   ' + blastDir.ext.upper() + '\n'
    dt = blastDir.date
    label = pt + im + di + fr + le + dt
    #
    metaBtn = cmds.iconTextButton(blastDir.name + '_Meta', st='textOnly', al=alignM, c="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.cmdOpen(\'%s\')" %
                                  (path.replace('\\', '\\\\')), l=label, h=height - padBtns, align='left', bgc=[0.23, 0.23, 0.23])

    # delete
    st = getString(strings=[f])
    # print st
    # print f, '_____f'
    cmdD = 'partial( removeRow, f, blastDir.path, blastDir.files)'
    delBtn = cmds.button(blastDir.name + '_Delete', c=eval(cmdD), al=alignD,
                         l='DELETE', w=col[3], h=height - padBtns, bgc=[0.500, 0.361, 0.361])
    # delBtn = cmds.button(blastDir.name + '_Delete', c="import webrImport as web\nreload(web)\npb = web.mod('playblast_lib')\npb.removeRow(%s)" % (st), l='DELETE', w=col[3], h=height - padBtns, bgc=[0.500, 0.361, 0.361])

    return f


def flushDefaultDir(*args):
    path = getPath()
    shutil.rmtree(path)
    createPath(path)


def addChecked(chk=''):
    # print chk
    c = cmds.button(getWipe(), q=True, c=True)
    front1 = c.split(rvFront())[0]
    front2 = rvFront()
    front = front1 + front2
    print front, '----'
    back = rvBack()
    # print back, '----'
    mid = c.split(rvFront())[1].split(rvBack())[0]
    print mid, '----'
    if mid == ',':  # none are have been added
        c = front, rvOpn(), chk, rvCls(), back
        print c[0], c[1]
    else:
        pass  # parse
        current = mid.split(',')
        print current, 'current'
    # print c
    # cmds.button(getWipe(), e=True, c=c)


def removeChecked(chk=''):
    # try adding square brackets to both inputs
    c = cmds.button(getWipe(), q=True, c=True)
    print c
    front = c.split('-wipe')[0] + rvFront()
    print '========='
    print front, 'front'
    print '========='
    '''
    mid   = c.split('[')[1].split(']')[0]
    mid   = mid.replace(chk, '')
    print mid, 'mid'
    back  = c.split(']')[1]
    print back, 'back\n'
    c = front + "[ " + mid + " ]" + back
    print c
    cmds.button(getWipe(), e=True, c=c)
    '''


def rvChk(chk=''):
    return rvOpn(), chk, rvCls()


def rvOpn():
    return '['


def rvCls():
    return ']'


def rvFront():
    return "'rv','-wipe'"


def rvBack():
    return "'-eval',';'"


def removeDoubleSpace(string=''):
    while '  ' in string:
        string.replace('  ', ' ')


def getString(strings=[]):
    '''
    convert vars to hard coded strings for button commands
    '''
    s = ''
    i = 0
    mx = len(strings) - 1
    for string in strings:
        if i == 0:
            s = "\'%s\'" % string
            if len(strings) > 1:
                s = s + ','
        elif i < mx:
            s = s + "\'%s\'" % string
            s = s + ','
        else:
            s = s + "\'%s\'" % string
        i = i + 1
    return s


def removeRow(row, path, files, *arg):
    '''
    arg = partial fuckery, leave empty
    row =  ''
    path = ''
    files = []
    '''
    # command looses scope when executed from button, need to re import
    import maya.cmds as cmds
    import webrImport as web
    # web
    cl = web.mod('clips_lib')

    # check for thumbnail, delete
    mov = cl.movExt()
    dat = cl.getDataPath()
    name = files[0].split('.')[0]
    ext = files[0].split('.')[len(files[0].split('.')) - 1]
    if ext in mov:
        thumb = os.path.join(dat, name + cl.getThumbSuffix() + '.png')
        if os.path.isfile(thumb):
            # print thumb, 'yes'
            os.remove(thumb)
        else:
            pass
            # print thumb
    # delete UI row
    cmds.deleteUI(str(row))
    # delete image seq
    for f in files:
        p = os.path.join(path, f)
        if os.path.isfile(p):
            os.remove(os.path.join(path, f))
    # delete if path empty
    if not os.listdir(path):
        shutil.rmtree(path)


def cmdOpen(path=''):
    #path = getPath()
    if os.name == 'nt':
        # print path
        # path = path.replace('\'', '\\')
        # print path
        if os.path.isdir(path):
            subprocess.Popen(r'explorer /open, ' + path)
    elif platform.system() == 'Darwin':
        subprocess.call(["open", "-R", path])
    else:
        message('Close file window to regain control over MAYA.')
        app = "nautilus"
        call([app, path])


def confirmCmd():
    '''
    confrim cmd, default cmd for delete buttons
    '''
    pass


def detectCompatibleStructure(path='', destructive=True):
    '''
    structure hard coded for now:
    ie. defaultDir/shot/sceneName
    '''
    rebuild = False
    root = getContentsType(path, directory=1, destructive=True)
    if root:
        for r in root:
            # print r, '======'
            shot = getContentsType(r, directory=0, destructive=True)
            if shot:
                # print shot, '======'
                for s in shot:
                    scene = getContentsType(s, directory=0, destructive=True)
                    if scene:
                        message('Directory structure is good')
                        return None


def getContentsType(path='', directory=False, destructive=False):
    '''
    directory = True  (returns path if directory found in given path)
    directory = False (returns path if file found in given path)
    returns None if criteria is not met
    '''
    # print directory, '+++++++++++++++++++++++++'
    d = not directory
    fullPaths = []
    # print path, '____deleting paths'
    if os.path.isdir(path) and os.access(path, os.R_OK):
        # list contents
        pathContents = os.listdir(path)
        for c in pathContents:
            fp = os.path.join(path, c)
            fullPaths.append(fp)
            # query type
            if os.path.isdir(fp) == d:
                # wrong type found
                message('wrong type found:   ' + fp)
                if destructive:
                    # delete
                    if os.path.isdir(fp):
                        shutil.rmtree(fp)
                    else:
                        os.remove(fp)
                    message('DELETING:   ' + fp)
        return fullPaths


def getAudio(path='', format=['wav', 'aiff']):
    # print path, '_inside audio'
    images = os.listdir(str(path))
    audio = []
    for image in images:
        for f in format:
            if f in image:
                # audio.append(image)
                return os.path.join(path, image)
    return None


def getClips(path=''):
    # print '___getting'
    return cl.getClips(path=path)


def openSelected(path='', name='', ext='', start='', end=''):
    # sample code for wipe compare
    # rv P_139_sk_0490_anim_swe_0077____camera.####.png -wipe P_139_sk_0490_anim_swe_0077____lookCam.####.png
    # audio
    # print '-- open'
    # print path
    print name
    # print ext
    # print start
    # print end
    # print os.path.join(path, name)
    mov = ['mov', 'avi', 'mp4']
    if ext in mov:
        # os.startfile(os.path.join(path, name + '.' + ext))
        filename = os.path.join(path, name + '.' + ext)
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
    else:
        path = str(path)
        if path:
            snd = getAudio(path)
            # print '______'
        else:
            pass
            # print '  no path'
        # os
        if os.name is 'nt':
            rvString = ['C:\\Program Files\\djv-1.1.0-Windows-64\\bin\\djv_view.exe',
                        os.path.join(path.replace('\\', '\\'), name + '.' + str(start) + '.' + ext)]
            # print rvString
            # subprocess.call(rvString)
            subprocess.Popen(rvString)
        elif os.name is 'posix':
            try:
                if snd:
                    print '-- with audio'
                    # with audio
                    rvString = 'rv ' + \
                        os.path.join(path, name) + '.#.' + ext + ' -in ' + \
                        start + ' -out ' + end + ' ' + snd + ' &'
                else:
                    print '-- no audio'
                    rvString = 'rv ' + \
                        os.path.join(path, name) + '.#.' + ext + ' -in ' + \
                        start + ' -out ' + end + ' &'  # escaped
                message('Play:  ' + rvString, maya=True)
                # print rvString
                os.system(rvString)
            except:
                # print rvString
                message('Failed to play  ', maya=True)
                print os.path.join(path, name)
        else:
            message('OS: ' + os.name +
                    '  not configured to play image seq.', maya=True)


def getDirectoryDate(path=''):
    t = os.path.getmtime(path)
    return str(datetime.datetime.fromtimestamp(t))


def getShotDirs(path=''):
    shots = os.listdir(path)
    # print shots
    shotPaths = []
    for shot in shots:
        shotPaths.append(os.path.join(path, shot))
    return shots
    # return shotPaths


def getBlastDirs(path=''):
    # Make sure the path exists and access is permitted
    if os.path.isdir(path) and os.access(path, os.R_OK):
        # shot dirs
        shots = getShotDirs(path)
        # print shots, 'shots____________'
        if shots:
            # print shots, '  shots'
            # Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            sortedDir = []
            # list shots in the default path
            for shot in shots:
                shotPath = os.path.join(getPath(), shot)

                def mtime(f): return os.stat(os.path.join(shotPath, f)
                                             ).st_ctime  # this doesn't work, remove!
                if os.path.isdir(shotPath):
                    contents = list(sorted(os.listdir(shotPath), key=mtime))
                    # print contents
                else:
                    message('skipping ' + shotPath +
                            '  Expected directory! DELETING!')
                    # do this where inappropriate stuff is found
                    os.remove(shotPath)
                # print contents
                if len(contents) > 0:
                    # This will error if 'u' objects are fed into a list
                    # pick out the directories
                    for i in contents:
                        if i[0] != '.':
                            if os.path.isdir(os.path.join(shot, i)):
                                dirs.append(os.path.join(shot, i))
                            else:
                                nonDir.append(i)
                else:
                    shutil.rmtree(os.path.join(getPath(), shot))
                    # errors on next line if something is deleted here

            def mtime(f): return os.path.getmtime(f)
            '''
            dirs = sorted(dirs, key=mtime)
            for i in reversed(dirs):
                sortedDir.append(i)
            '''
            sortedShots = []
            shotsPaths = []
            for shot in shots:
                shotsPaths.append(os.path.join(getPath(), shot))
            shotsD = sorted(shotsPaths, key=mtime)
            for shot in shots:
                for sd in shotsD:
                    if shot in sd:
                        sortedShots.append(shot)
            for i in reversed(sortedShots):
                sortedDir.append(i)

            # return shots
            # turned off to get it working need to sort this list according to
            # creation time
            return sortedDir
        else:
            return None
    else:
        createPath(path)
        return None
