import os
import maya.cmds as cmds
import maya.mel as mel
import subprocess
from functools import partial
from subprocess import call
import datetime
import shutil

#rgb gl color guide ## http://prideout.net/archive/colors.php
#http://www.tweaksoftware.com/static/documentation/rv/current/html/rv_manual.html
#layers = inputs in square brackets are layers
# -wipe = wipe view items
# -layout 'row' = side by side


def message(what='', maya=False):
    what = '-- ' + what + ' --'
    global tell
    tell = what
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

def getDefaultPath():
    return '/var/tmp/rv_playblasts/'
    #return '/var/tmp/___A___PLAYBLAST___A___/'

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

def sceneName(full=False, suffix=None):
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
    if suffix:
        sceneName = sceneName + suffix
    return sceneName

def shotDir():
    shotDir = sceneName()
    shotDir = shotDir + '/'
    return shotDir

def shotDir2(idx=7):
    shotDir = sceneName(full=1)
    shotDir = shotDir.split('/')[idx]
    shotDir = shotDir + '/'
    return shotDir

def createPath(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        pass
        #print "-- path:   '" + path + "'   already exists --"
    return path

def createBlastPath(suffix=''):
    '''
    tie in with Bates blast module
    '''
    createPath(path = blastDir())
    createPath(path = blastDir() + shotDir2())
    path = createPath(blastDir() + shotDir2()+ sceneName() + suffix + '/') + sceneName() + suffix
    return path

def blastDir(forceTemp=True):
    '''
    forceTemp = use get default function to force a specified location, otherwise standard maya locations are used
    '''
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
                #print None, '____'
                return None
                #print project, 'here'
                #print scene, 'here'
        else:
            return getDefaultPath()
    else:
        return getDefaultPath()

def blast(w=1920, h=789, x=1, format='qt', qlt=100, compression='H.264', offScreen=True, useGlobals=True):
    '''
    rv player is mostly used to play back the images or movie files, function has gotten sloppy over time, cant guarantee competence
    '''
    min, max = blastRange()
    if useGlobals:
        w = cmds.getAttr( 'defaultResolution.width' )
        h = cmds.getAttr( 'defaultResolution.height' )
    w = w*x
    h = h*x
    if os.name == 'nt':
        #windows os
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            #print blastDir(), '   blastdir'
            pbName = blastDir()+sceneName()
            if os.path.exists(pbName):
                #print True
                pass
            if 'image' not in format:
                path = cmds.playblast(format=format, filename=blastDir()+sceneName(), sound=sound(), showOrnaments=True, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
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
        # could be linux or mac os
        i = 1
        if not blastDir():
            message('Set project', maya=True)
        else:
            pbName = shotDir2()+sceneName()
            if os.path.exists(pbName):
                #print True
                pass
            if 'image' not in format:
                path = cmds.playblast(format=format, filename=shotDir2()+sceneName(), sound=sound(), showOrnaments=False, st=min, et=max, viewer=True, fp=4, fo=True, qlt=qlt, offScreen=offScreen, percent=100, compression=compression, width=w, height=h)
            else:
                playLo, playHi, current = getRange()
                w = w * x
                h = h * x
                path = cmds.playblast(format='image', filename=createBlastPath(''), showOrnaments=False, st=min, et=max, viewer=False, fp=4, fo=True, offScreen=offScreen, percent=100, compression='png', width=w, height=h)
                if path:
                    rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &' #not escaped
                else:
                    rvString = 'rv ' + '[ ' + createBlastPath('') + '.#.png' + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &' #escaped
                print rvString
                os.system(rvString)
                cmds.currentTime(current)
    else:
        #? whatever else, doesnt get used much and will likely break...
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
        #window
        win = cmds.window(winName, rtf=1)
        f1 = cmds.formLayout('mainForm' + suf)
        cmds.showWindow()
        #text field
        #field        = cmds.textField('defaultPath1', text=rootDir)
        field        = cmds.button('defaultPath1', label=rootDir, align='left', h=24, c="from subprocess import call\ncall(['nautilus',\'%s\'])" % (rootDir))
        cmds.formLayout(f1, e=1, af=(field, 'top', 5))
        cmds.formLayout(f1, e=1, af=(field, 'left', 5))
        cmds.formLayout(f1, e=1, af=(field, 'right', 5))
        cmds.refresh(f=1)
        #refresh button
        refBtn = cmds.button('refresh' + suf, l='REFRESH', c='import playblast_lib as pb\nreload(pb)\npb.blastWin()', h=24)
        attachForm = [(refBtn,'top', 2, field)]
        cmds.formLayout(f1, edit=True, attachControl=attachForm)
        cmds.formLayout(f1, e=1, af=(refBtn, 'left', 5))
        cmds.formLayout(f1, e=1, af=(refBtn, 'right', 5))
        #flush button
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

        #scroll
        scrollBar       = 16
        scrollBarOffset = 75
        scrollLayout = cmds.scrollLayout('scroll' + suf, horizontalScrollBarThickness=scrollBar, verticalScrollBarThickness=scrollBar, cr=1)
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'bottom', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'top', scrollBarOffset))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'left', 0))
        cmds.formLayout(f1, e=1, af=(scrollLayout, 'right', 0))
        cmds.refresh(f=1)
        #row setup
        offset    = 0
        height    = getDefaultHeight()
        col0      = 20
        col1      = 200
        col2      = 250
        col3      = 50
        width     = col0+col1+col2+col3
        wAdd      = scrollBar+10
        #status
        detectCompatibleStructure(rootDir)
        blastDirs = getBlastDirs(rootDir)
        print blastDirs
        if blastDirs:
            f2 = cmds.formLayout('subForm' + suf, h=height*len(blastDirs), w=width, bgc=[0.17,0.17,0.17])
            cmds.refresh(f=1)
            #print f2

            #build rows
            j=0
            num = len(blastDirs)-1
            #print blastDirs
            for blastDir in blastDirs:
                contents = os.listdir(blastDir)
                if contents:
                    cmds.setParent(f2)
                    if j == 0:
                        attach = ''
                    else:
                        attach = blastDirs[j-1]
                    if j >= num:
                        below = ''
                    else:
                        below = blastDirs[j+1]
                    #print blastDir
                    buildRow(blastDir, offset=offset, height=height, parent=f2, col=[col0,col1,col2,col3], attachRow=attach, belowRow=below)
                    j=j+1
                    cmds.refresh(f=1)
                    print j
                else:
                    #rebuild
                    shutil.rmtree(blastDir)
                    cmds.deleteUI(winName)
                    blastWin()
                    break
            cmds.window(win, e=1, w=width+wAdd, h=(height*4)+scrollBarOffset)
            cmds.refresh(f=1)
    else:
        cmds.deleteUI(winName)
        blastWin()

def convertPathToRow(row, path):
    r = row.split('|')
    r = r[len(r)-1]
    p = path.split('/')
    p = p[len(p)-1]
    newRow = row.replace(r,p).replace('-','_')
    return newRow

def buildRow(blastDir='', offset=1,  height=1,  parent='', col=[10, 10, 10, 10], attachRow='', belowRow=''):

    #stuff
    allCols = col[0] + col[1] + col[2] + col[3]
    path = blastDir
    #print path

    #parse row name from directory path
    blastDir = blastDir.split('/')
    shot = blastDir[len(blastDir)-2]
    blastDir = blastDir[len(blastDir)-1]
    suf = '_RowForm__'
    blastDir = blastDir + suf + shot

    imageRange = getImageRange(path)
    imageName  = getImageName(path)

    #iconSize
    icon = getIcon(path)
    w, h = getIconSize(icon)

    #row form
    f    = cmds.formLayout(blastDir, h=height, bgc = [0.2,0.2,0.2], ann=path)
    if attachRow:
        #create above row name from path
        shot = attachRow.split('/')
        shot = suf + shot[len(shot)-2].replace('-','_')
        attachRow = convertPathToRow(f, attachRow) + shot
    if belowRow:
        #create below row name from path
        shot = belowRow.split('/')
        shot = suf + shot[len(shot)-2].replace('-','_')
        belowRow  = convertPathToRow(f, belowRow) + shot
    cmds.formLayout(parent, e=1, af=(f, 'top', offset))
    cmds.formLayout(parent, e=1, af=(f, 'left', 0))
    cmds.formLayout(parent, e=1, af=(f, 'right', 0))
    if attachRow:
        attachForm = [(f,'top',offset, attachRow)]
        #print parent
        cmds.formLayout(parent, edit=True, attachControl=attachForm)

    #checkbox
    chkBx = cmds.checkBox(blastDir + '_Check', l='', w=col[0],
        onc="import playblast_lib as pb\nreload(pb)\npb.addChecked(%s)" % (getString(strings=[path])),
        ofc="import playblast_lib as pb\nreload(pb)\npb.removeChecked(%s)" % (getString(strings=[path])))
    cmds.formLayout(f, e=1, af=(chkBx, 'top', height/2-8))
    cmds.formLayout(f, e=1, af=(chkBx, 'left', 4))

    #icon
    padW = 0
    padH = 0
    padBtns = 4
    cmdI = 'partial( openSelected, path = path )'
    iconH = col[1]*(h/w)
    iconW = col[1]
    if iconH > height:
        iconH = height
        iconW = iconH*(w/h)
        padW = int((col[1] - iconW)/2)
    if iconW < col[0]:
        padW = int((col[1] - iconW)/2)
    if iconH < height:
        padH = int((height - iconH)/2)
    iconBtn = cmds.iconTextButton(blastDir + '_Icon', st='iconOnly', image=icon, c=eval(cmdI), l=blastDir, w=iconW, h=iconH, iol='PLAY', mw=padBtns, mh=padBtns, bgc = [0.13,0.13,0.13],)
    #cmds.formLayout(f, e=1, af=(iconBtn, 'bottom', padH))
    cmds.formLayout(f, e=1, af=(iconBtn, 'top', padH))
    cmds.formLayout(f, e=1, af=(iconBtn, 'left', col[0] + padW))

    #delete
    cmds.setParent(f)
    st = getString(strings=[f, attachRow, belowRow])
    delBtn  = cmds.button(blastDir + '_Delete', c= "import playblast_lib as pb\nreload(pb)\npb.removeRow(%s)" % (st), l='DELETE', w=col[3], h=height-padBtns, bgc=[0.500, 0.361, 0.361])
    cmds.formLayout(f, e=1, af=(delBtn, 'bottom', padBtns/2))
    cmds.formLayout(f, e=1, af=(delBtn, 'top', padBtns/2))
    cmds.formLayout(f, e=1, af=(delBtn, 'right', 0))

    #meta
    pt    = path.split(getDefaultPath())[1].split('/')[0] + '\n'
    #sc    = 'Scene Name:  ' + blastDir + '\n'
    im    = imageName + '\n'
    di    = str(int(w)) + ' x ' + str(int(h)) + '\n'
    fr    = str(int(imageRange[0])) + 'f  -  ' + str(int(imageRange[1])) + 'f\n'
    le    = str(int(imageRange[1]-imageRange[0]+1)) + ' frames\n'
    dt    = getDirectoryDate(path)
    label = pt+im+di+fr+le+dt
    #
    #metaBtn = cmds.button(blastDir + '_Meta', c="from subprocess import call\ncall(['nautilus',\'%s\'])" % (path), l=label, h=height, w=col[2], align='left')
    metaBtn = cmds.iconTextButton(blastDir + '_Meta', st='textOnly', c="from subprocess import call\ncall(['nautilus',\'%s\'])" % (path), l=label, h=height-padBtns, align='center', fn='boldLabelFont', bgc = [0.23,0.23,0.23], w=col[2])
    cmds.formLayout(f, e=1, af=(metaBtn, 'bottom', padBtns/2))
    cmds.formLayout(f, e=1, af=(metaBtn, 'top', padBtns/2))
    cmds.formLayout(f, e=1, af=(metaBtn, 'left',col[1]+col[0]))
    #cmds.formLayout(f, e=1, af=(metaBtn, 'right', col[3]))
    #
    attachForm = [(metaBtn,'right', 0, delBtn)]
    cmds.formLayout(f, edit=True, attachControl=attachForm)

    return f

def flushDefaultDir(*args):
    path = getDefaultPath()
    shutil.rmtree(path)
    createPath(path)

def addChecked(chk=''):
    #print chk
    c = cmds.button(getWipe(), q=True, c=True)
    front1 = c.split(rvFront())[0]
    front2 = rvFront()
    front = front1 + front2
    print front, '----'
    back = rvBack()
    #print back, '----'
    mid = c.split(rvFront())[1].split(rvBack())[0]
    print mid, '----'
    if mid == ',': #none are have been added
        c = front, rvOpn(), chk, rvCls(), back
        print c[0],c[1]
    else:
        pass #parse
        current = mid.split(',')
        print current, 'current'
    #print c
    #cmds.button(getWipe(), e=True, c=c)

def removeChecked(chk=''):
    #try adding square brackets to both inputs
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
    mx = len(strings)-1
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
        i=i+1
    return s

def removeRow(row='', attachRow='', belowRow='', deleteDir=True):
    path = cmds.formLayout(row, q=1, ann=1)
    cmds.deleteUI(row)
    if deleteDir:
        #remove scene dir
        shutil.rmtree(path)
        #check if shot dir is empty, delete if it is
        shot = path.split('/' + path.split('/')[len(path.split('/'))-1])[0]
        contents = os.listdir(shot)
        if not contents:
            shutil.rmtree(shot)
    #shift lower rows
    updateRows(row, attachRow, belowRow)

def updateRows(row='', attachRow='', belowRow=''):
    parent = row.split('|')[3]
    if attachRow:
        #parent = attachRow.split('|')[3]
        if belowRow:
            attachForm = [(belowRow,'top',0, attachRow)]
            cmds.formLayout(parent, edit=True, attachControl=attachForm)
        #print parent
    updateRowCmd(row, attachRow, belowRow)
    #update height scroll, form
    num = getBlastDirs(getDefaultPath())
    if num:
        num = len(num)
        num = getDefaultHeight() * num
        if num:
            cmds.formLayout(parent, e=1, h=num)
        else:
            cmds.formLayout(parent, e=1, h=1)
    else:
        cmds.formLayout(parent, e=1, h=1)

def updateRowCmd(row='', attachRow='', belowRow=''):
    #attach
    if attachRow:
        attachDel = findDeleteControl(attachRow)
        cmdA = cmds.button(attachDel, q=1, c=1)
        #from attachRow cmd replace 'row' with belowRow
        cmdA = cmdA.replace(row, belowRow)
        cmds.button(attachDel, e=1, c=cmdA)
    #below
    if belowRow:
        belowDel = findDeleteControl(belowRow)
        cmdB = cmds.button(belowDel, q=1, c=1)
        #from belowRow cmd replace 'row' with attachRow
        cmdB = cmdB.replace(row, attachRow)
        cmds.button(belowDel, e=1, c=cmdB)

def updateDelCmd(*args):
    '''
    use to change delete cmd from confirm to delete
    '''
    pass

def deleteCmd():
    '''
    delete command, confrim command for deleting rows
    '''
    pass

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
            #print r, '======'
            shot = getContentsType(r, directory=1, destructive=True)
            if shot:
                #print shot, '======'
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
    d = not directory
    fullPaths = []
    if os.path.isdir(path) and os.access(path, os.R_OK):
        #list contents
        pathContents = os.listdir(path)
        for c in pathContents:
            fp = os.path.join(path,c)
            fullPaths.append(fp)
            #query type
            if  os.path.isdir(fp) == d:
                #wrong type found
                message('wrong type found:   ' + fp)
                if destructive:
                    #delete
                    if  os.path.isdir(fp):
                        shutil.rmtree(fp)
                    else:
                        os.remove(fp)
                    message('DELETING:   ' + fp)
        return fullPaths

def findDeleteControl(row=''):
    childs = cmds.formLayout(row, q=1, ca=1)
    for child in childs:
        if 'Delete' in child:
            return child

def getIcon(path=''):
    images = os.listdir(str(path))
    if images:
        icon = os.path.join(path, images[0])
        #print icon
        return icon
    else:
        return None

def getIconSize(path=''):
    if path:
        dim = subprocess.Popen(["identify","-format","\"%w,%h\"",path], stdout=subprocess.PIPE).communicate()[0]
        s = dim.split(',')
        w = float(s[0].split('"')[1])
        h = float(s[1].split('"')[0])
        return w, h
    else:
        return 0, 0

def getImageRange(path=''):
    images = os.listdir(str(path))
    if images:
        i = 0
        for image in images:
            if os.path.isdir(os.path.join(path, image)):
                images.pop(i)
            i = i + 1
        images =  sorted(images)
        start  = float(images[0].split('.')[1])
        end    = float(images[len(images)-1].split('.')[1])
        return start, end
    else:
        return None

def getImageName(path=''):
    images = os.listdir(str(path))
    if images:
        im = images[0].split('.')
        name = im[0] + '.*.' + im[2]
        return name
    else:
        return None

def openSelected(path=''):
    if os.name is 'nt':
        rvString = "\"C:/Program Files/Tweak/RV-3.12.12-64/bin/rv.exe\" " + "[ " + path + " -in " + str(playLo) + " -out " + str(playHi) + " ]"
        #print rvString
        pass
        subprocess.Popen(rvString)
    elif os.name is 'posix':
        try:
            rvString = 'rv ' + '[ ' + path + ' ]' ' &'
            #print rvString, '  here'
            message('Play:  ' + rvString, maya=True)
            os.system(rvString)
        except:
            #print rvString
            message('Failed:  ' + rvString, maya=True)
    else:
        path = path + sceneName() + '.####.png'
        #print path
        pass
        rvString = 'rv ' + '[ ' + path + ' -in ' + str(playLo) + ' -out ' + str(playHi) + ' ]' ' &'
        os.system.Popen(rvString)

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
        if shots:
            #print shots, '  shots'
            #Populate the directories and non-directories for organization
            dirs      = []
            nonDir    = []
            sortedDir = []
            #list shots in the default path
            for shot in shots:
                mtime = lambda f: os.stat(os.path.join(shot, f)).st_ctime #this doesnt work, remove!
                if os.path.isdir(shot):
                    contents  = list(sorted(os.listdir(shot), key=mtime))
                else:
                    message('skipping ' + shot + '  Expected directory! DELETING!')
                    os.remove(shot)  ####do this where inappropriate stuff is found
                #print contents
                if len(contents) > 0:
                    #This will error if 'u' objects are fed into a list
                    #pick out the directories
                    for i in contents:
                        if i[0] != '.':
                            if os.path.isdir(os.path.join(shot, i)):
                                dirs.append(os.path.join(shot,i))
                            else:
                                nonDir.append(i)
                else:
                    shutil.rmtree(shot)
            mtime = lambda f: os.path.getmtime(f)
            dirs = sorted(dirs, key=mtime)
            for i in reversed(dirs):
                sortedDir.append(i)

            return sortedDir
        else:
            return None
    else:
        createPath(path)
        return None
