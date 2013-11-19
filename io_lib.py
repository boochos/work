import maya.cmds as cmds
import maya.mel as mel
import os
import shutil

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def ingest(project='Scarecrow', compare=True):
    #Source
    audioFrom  = 'C:\Users\Slabster & Vicster\Documents\maya\IO\IN\Audio'
    plateFrom  = 'C:\Users\Slabster & Vicster\Documents\maya\IO\IN\Plates'
    mmFrom     = 'C:\Users\Slabster & Vicster\Documents\maya\IO\IN\Matchmoves'
    #Fetch files from source
    audioFiles = os.listdir(audioFrom)
    plateFiles = os.listdir(plateFrom)
    mmFiles    = os.listdir(mmFrom)
    #Shot names
    shots      = audioFiles
    #Ingest
    base          = 'C:\Users\Slabster & Vicster\Documents\maya\projects'
    template      = 'C:\Users\Slabster & Vicster\Documents\maya\projects\__ShotTemplate__'
    scenes        = 'maya/scenes'
    scene         = 'ShotTemplate.ma'
    plateTo       = 'maya/sourceimages'
    audioTo       = 'maya/sound'
    mmTo          = 'maya/assets'
    #messages
    front   = '_________SHOT:'
    back    = '_________'
    should  = '_________________________Should create above action_________________________' 
    already = ' exists  ----  '
    none    = '    none    ----   '
    line    = '\n'
    i       = 0
    j       = 0
    new     = []
    started = []
    
    for shot in shots:
        name     = shot.split('.')[0]
        print line
        print front + name  + back
        #shot dirs
        project   = os.path.join(base, name)
        sceneDir  = os.path.join(project, scenes)
        audioDir  = os.path.join(project, audioTo)
        plateDir  = os.path.join(project, plateTo)
        mmDir     = os.path.join(project, mmTo)
        #create project
        if not os.path.exists(project):
            if not compare:
                print 'project  =', project
                shutil.copytree(template, project, symlinks=True, ignore=None)
            else:
                print should
                i = i + 1
                new.append(name)
        else:
            print 'Project', already, project
        #rename scene
        if os.path.exists(sceneDir):
            oldScenes = os.listdir(sceneDir)
            if len(oldScenes) > 1:
                started.append(name)
                j = j + 1
            oldScene = os.path.join(sceneDir, os.listdir(sceneDir)[0])
            newScene = os.path.join(sceneDir, name + '_anim_0000.ma')
            if not os.path.exists(newScene):
                print 'File  =', newScene
                if not compare:
                    os.rename(oldScene, newScene)
                else:
                    print should
                    i = i + 1
                    new.append(name)
            else:
                print 'Scene  ', already, newScene
        else:
            print 'No scene =', sceneDir
        #copy audioFiles
        if not os.path.exists(os.path.join(audioDir, shot)):
            print 'Audio from  =', os.path.join(audioFrom, shot)
            print 'Audio to    =', os.path.join(audioDir, shot)
            if not compare:
                shutil.copy2( os.path.join(audioFrom, shot), os.path.join(audioDir, shot))
            else:
                print should
                i = i + 1
                new.append(name)
        else:
            print 'Audio  ', already, os.path.join(audioDir, shot)
        #copy plateFiles
        if name + '.rar' in plateFiles:
            plate = plateFiles[plateFiles.index(name + '.rar')]
            if not os.path.exists(os.path.join(plateDir, plate)):
                print 'Plate from  =', os.path.join(plateFrom, plate)
                print 'Plate to    =', os.path.join(plateDir, plate)
                if not compare:
                    shutil.copy2( os.path.join(plateFrom, plate), os.path.join(plateDir, plate))
                else:
                    print should
                    i = i + 1
                    new.append(name)
            else:
                print 'Plate  ', already, os.path.join(plateDir, plate)
        else:
            print 'Plate' + none + name + '.rar  --  in  --  ' + plateFrom
        #copy mmFiles, doesnt account for version numbers... fix with loop
        check = False
        for mm in mmFiles:
            if name in mm:
                check = True
                if not os.path.exists(os.path.join(mmDir, mm)):
                    print 'MM from  =', os.path.join(mmFrom, mm)
                    print 'MM to    =', os.path.join(mmDir, mm)
                    if not compare:
                        shutil.copy2( os.path.join(mmFrom, mm), os.path.join(mmDir, mm))
                    else:
                        print should
                        i = i + 1
                        new.append(name)
                else:
                    print 'MM     ', already, os.path.join(mmDir, mm)
            else:
                pass
                #print 'MM      ', name + '  --  no match in  -- ' + mm
        if not check:
            print 'MM   '+ none + name + '*  --  in  -- ' + mmDir
    print line, 'New:     ', i, ' ', new
    print 'Started: ', j, ' ', started
    return started, new

class IoDir():
    def __init__(self, project='', base='C:/Users/Slabster & Vicster/Documents/maya/projects', scene='scenes', cache='data/geoCache'):
        self.base         = base
        self.project      = os.path.join(self.base, project)
        self.scene        = os.path.join(self.project, scene)
        self.cache        = os.path.join(self.project, cache)
        self.shotNames    = os.listdir(self.base)
        self.shots        = None
        self.allShots()
        
    def allShots(self):
        #shot path
        allP = []
        #shot name
        allN = []
        for shot in self.shotNames:
            if not ('default' in shot or '__ShotTemplate__' in shot or os.path.isfile(os.path.join(self.base, shot))):
                allN.append(shot)
                allP.append(os.path.join(self.base, shot))
        #allP = filter(lambda x: os.path.isdir(x), allP)
        self.shotNames = allN
        self.shots     = allP
        

class IoLatest(IoDir):
    def __init__(self, project=''):
        self.dir            = IoDir(project)
        self.scenes         = []
        self.caches         = []
        self.scene          = None
        self.sceneName      = None
        self.cache          = None
        self.cacheName      = None
        self.sceneList()
        self.cacheList()
        self.getScene()
        self.getCache()
        #if not os.path.exists(newScene)
    def sceneList(self):
        for item in os.listdir(self.dir.scene):
            scene =  os.path.join(self.dir.scene, item)
            self.scenes.append(scene)

    def cacheList(self):
        if os.path.exists(self.dir.cache):
            for item in os.listdir(self.dir.cache):
                scene =  os.path.join(self.dir.cache, item)
                self.caches.append(scene)
        else:
            self.caches.append(None)

    def getScene(self):
        #filter files only
        filelist       = filter(lambda x: not os.path.isdir(x), self.scenes)
        if len(filelist) > 0:
            self.scene     = max(filelist, key=lambda x: os.stat(x).st_mtime)
            self.sceneName = self.scene[self.scene.rfind('\\')+1:]

    def getCache(self):
        #filter directories only
        if None not in self.caches:
            filelist       = filter(lambda x: os.path.isdir(x), self.caches)
            if len(filelist) > 0:
                self.cache     = max(filelist, key=lambda x: os.stat(x).st_mtime)
                self.cacheName = self.cache[self.cache.rfind('\\')+1:]

def publish(project='', compare=True, shot=True, cache=True, scene=False):
    dir     = 'C:\Users\Slabster & Vicster\Documents\maya\IO\OUT\maya'
    already = 'Publish exists:      '
    able    = 'Able to publish:  '
    copying = 'Copying directory:   '
    line    = '\n'
    latest  = IoLatest(project)
    print line, 'Shot:                ', project
    try:
        i       = latest.scene.rfind('_')+1
        iS      = latest.scene[i:]
    except:
        print 'No anim scene:  Exiting!', latest.scene
        return None
    try:
        i       = latest.cache.rfind('_')+1
        iC      = latest.cache[i:]
    except:
        print 'No cache directory:  Exiting!', latest.cache
        return None
    if iC in iS:
        #versions match, proceed
        dir = os.path.join(dir, latest.cacheName)
        #shot directory in 'OUT' for publish
        if not os.path.exists(dir):
            if not compare:
                print 'Creating directory:  ', latest.sceneName, latest.cacheName, dir
                os.mkdir(dir)
            else:
                print able, dir
        else:
            print already, dir
        #scene publish
        pubScene = os.path.join(dir, latest.sceneName)
        if not os.path.exists(pubScene):
            if not compare:
                print copying, pubScene
                shutil.copy2( latest.scene, pubScene)
            else:
                print able, pubScene
        else:
            print already, pubScene
        #cache publish
        pubCache = os.path.join(dir, latest.cacheName)
        if not os.path.exists(pubCache):
            if not compare:
                print copying, pubCache
                shutil.copytree(latest.cache, pubCache, symlinks=True, ignore=None)
            else:
                print able, pubCache
        else:
            print already, pubCache
    else:
        print 'Version match fail:'
        print '    Scene:  ', latest.sceneName
        print '    Cache:  ', latest.cacheName

def insertDir():
    base = 'C:/Users/Slabster & Vicster/Documents/maya/projects'
    dir  = IoDir(base)
    m    = 'maya'
    for shot in dir.shots:
        ins      = os.path.join(shot, m)
        contents = os.listdir(shot)
        #print ins
        if not os.path.exists(ins):
            os.mkdir(ins)
            for c in contents:
                shutil.move(os.path.join(shot, c), ins)
        else:
            message('exists')