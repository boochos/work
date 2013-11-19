## Nov 20, 2011. Add function to support scene folder naming for cache files as oppose to simple versioning to solve negative imotions between artists.##
## Nov 19, 2011.Made change to add plate_01 handling for new plate naming:  ".../FD_005_01/images/FD_009_01_plate_01/"##
## Cache all tagged Geometry - Make sure you have the project set to shot/maya like  ".../FD_005_01/maya/##
## make sure there is only one plate directory in the shot/images/ folder like -> ".../FD_005_01/images/FD_005_01_plate/" <-  ##
## make sure there is only one set of images in the plate directory padded by four like  -> "FD_005_01_plate.0001.jpg" <-  ##


import maya.cmds as m
import os

os.name 
os.curdir

def createGeoCache(*args):
    project = m.workspace(rd=True, q=True)
    dataDir = project+'data/'
    index = project[:-1].rindex('/')
    shotDir = project[:index]+'/'
    index = shotDir[:-1].rindex('/')
    #parse scene path to derrive scene name to be used in folder
    s_string = m.file(sn=True, q=True)
    s_splitString = s_string.split('/')
    i_splitStringLength = len(s_splitString)
    s_filename = s_splitString[(i_splitStringLength - 1)]
    #parse scene name to derrive name 
    s_splitFolder = s_filename.split('.')
    i_splitStringLengthFolder = len(s_splitFolder)
    s_foldername = s_splitFolder[(i_splitStringLengthFolder - 2)]
    #specify the plate name here
    plate = shotDir[index+1:-1]+ '_plate_01'
    imageDir = shotDir + 'images/' + plate + '/'
    imageList  = []
    #images = os.listdir(imageDir)
    #for i in images:
       # if 'plate' in i:
           # imageList.append(i)
   
    start = m.playbackOptions (ast=True, q=True)
    end = m.playbackOptions (aet=True, q=True)

    #set timeline to images
    m.playbackOptions( ast = start, aet = end, min = start, max = end)

    #make geo caache directory
    geoCacheDir = dataDir + 'geoCache/'
    if not 'geoCache' in os.listdir(dataDir):
        os.mkdir(geoCacheDir)
    #make cache version directory
    versions = os.listdir(geoCacheDir)
    if versions:
        nextVersion = s_foldername
        cacheVersionDir = geoCacheDir+s_foldername #modified this line to use scene name as folder name
        if not os.path.exists(cacheVersionDir):
            os.mkdir(cacheVersionDir)
    else:
        cacheVersionDir = geoCacheDir+s_foldername #modified this line to use scene name as folder name
        os.mkdir(cacheVersionDir)

    # cache selected objects
    list = m.ls(type = 'transform' )
    for obj in list:
        if m.attributeQuery( 'cache', node= obj, exists=True ):
            try:
                m.setAttr(obj+'.cache', False)
            except:
                if m.getAttr(obj+'.cache'):
                    print m.getAttr(obj+'.cache'), obj
                    shape = m.listRelatives( obj, s=True)[0]
                    if ':' in shape:
                        cacheName = shape[ shape.rindex(':')+1 : ]
                    else:
                        cacheName = shape
                    print 'caching shape:', shape, 'as:', cacheName
                    m.cacheFile( dir = cacheVersionDir, f=cacheName, points = shape, st=start-10, et=end+10 )
        else:
            print 'no attr'
