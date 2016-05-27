import subprocess
import json
import time
import re
import glob
import itertools
import datetime
import os
import tempfile
from pymel.core import *


class Clip():

    def __init__(self):
        self.name = ''
        self.dir = ''
        self.start = 0
        self.end = 0
        self.ext = ''
        self.thumbnail = ''  # sometimes wrong icon is used
        self.length = 0
        self.date = ''
        self.width = 0
        self.height = 0
        self.path = ''
        self.movPath = ''
        self.files = []


def getDataPath():
    blastD = '___A___DATA___A___'
    tempD = tempfile.gettempdir()
    createPath(path=os.path.join(tempD, blastD))
    return os.path.join(tempD, blastD)


def movExt():
    return ['mov', 'avi', 'mp4']


def imgExt():
    return ['jpg', 'png', 'tif', 'exr', 'dpx']


def createPath(path=''):
    # print path
    if not os.path.isdir(path):
        # print path
        os.mkdir(path)
    else:
        pass
        # print "-- path:   '" + path + "'   already exists --"
    return path


def getClips(path='', leaf=''):
    '''
    will look for contents in given path + leaf sub dir
    path = base path
    leaf = sub directories, use * for path wildcards
    '''
    contents = glob.glob(os.path.join(path, leaf))
    # print contents, '__con'
    bucket = []
    for con in contents:
        # print con
        c = os.listdir(con)
        # print c
        seqFrames = []
        seqNames = []
        # needs to be sorted to group correctly
        data = sorted(c, key=lambda x: x.split('.')[0])
        # print data, '___data'
        for nm, frm in itertools.groupby(data, lambda x: x.split('.')[0]):
            seqFrames.append(list(frm))    # Store group iterator as a list
            seqNames.append(nm)
        # print seqNames, '____name'
        # print seqFrames, '____frames'
        for frames in seqFrames:
            # print frames
            exts = []
            # anything with same name but different extension returns as part of same sequence, sort for it
            for item in frames:
                # print item, ' one'
                if '.' in item:
                    exts.append(item.split('.')[len(item.split('.')) - 1])
                else:
                    pass
                    # print '___no confirm'
            exts = list(set(exts))
            # print confirmSeq, '___seq'
            if len(exts) == 1:
                b = buildClip(frames, con)
                if b:
                    # print '___have b'
                    bucket.append(b)
                else:
                    pass
                    # print '___no bucket'
            else:
                # more than one extension with same filename present, decipher
                extGroups = []
                for ext in exts:
                    grp = []
                    for frame in frames:
                        if ext in frame:
                            grp.append(frame)
                    extGroups.append(grp)
                    grp = []
                # print '___here'
                for grp in extGroups:
                    b = buildClip(grp, con)
                    if b:
                        bucket.append(b)
    return bucket


def buildClip(frames=[], path=''):
    q = qualify(frames)
    if q:
        # print frames
        if q == 'movie':
            return buildMov(frames, path)
        else:  # assume image
            return buildImg(frames, path)
    else:
        pass
        # print 'pass', frames


def getMeta(filename):
    pf = '-print_format'
    js = 'json'
    try:
        cmnd = ['ffprobe', pf, js, '-show_streams', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print filename
        out, err = p.communicate()
        # print "==========output=========="
        # print out
        js = json.loads(out)
        # print js
        if err:
            print "========= error ========"
            print err
        try:
            p.kill()
        except:
            pass
            # print 'couldnt kill ffprobe'
        return js
    except:
        print 'Failed getMeta: ', filename
    return None


def getThumbSuffix():
    return '__Thumb'


def getThumb(filein, fileout, delete=False, scale=1.0):
    create = False
    outdate = None
    indate = None
    if delete:
        if os.path.isfile(fileout):
            os.remove(fileout)
            # print 'deleted', fileout
        return None
    else:
        if os.path.isfile(fileout):
            outdate = os.path.getmtime(fileout)
            indate = os.path.getmtime(filein)
            if indate > outdate:
                create = True
            else:
                # print 'thumbnail is newer than source'
                pass
        else:
            create = True
        # add new directory in tmp for thumbs, deleting clip in pb man will need to delete thumbnail as well
        if create:
            # cmnd = ['ffmpeg', '-ss', '00:00:00', '-i', filein, '-vframes', '1', fileout]
            try:
                cmnd = ['ffmpeg', '-ss', '00:00:00', '-i', filein, '-y', '-frames:v', '1', fileout]
                p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # print filein
                out, err = p.communicate()
                print "==========output=========="
                # print out
                if out:
                    js = json.loads(out)
                # print js
                if err:
                    print "========= error ========"
                    print err
            except:
                pass
    return fileout


def getImageSize(path=''):
    if os.path.isfile(path):
        # print path
        dim = subprocess.Popen(["identify", "-format", "\"%w,%h\"", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = dim.communicate()
        if err:
            print err
        # print out
        # print dim
        s = dim.split(',')
        w = float(s[0].split('"')[1])
        h = float(s[1].split('"')[0])
        return w, h
        '''
        except:
            print '    except==========================='
            return 0, 0
            '''
    else:
        print '   nuthin========================='
        return 0, 0


def qualify(content):
    mov = movExt()
    img = imgExt()
    ext = content[0].split('.')
    ext = ext[len(ext) - 1]
    if getThumbSuffix() not in content[0]:
        if ext in mov:
            return 'movie'
        elif ext in img:
            return 'image'
        else:
            return None
    return None


def buildSeqName(path=''):
    path = re.sub('\..*?\.', '.%04d.', path, flags=re.DOTALL)
    # print path
    return path


def buildMov(content, path='', createThumb=True):
    meta = getMeta(os.path.join(path, content[0]))
    clip = Clip()
    clip.name = content[0].split('.')[0]
    clip.path = path
    clip.files = content
    clip.ext = content[0].split('.')[1]
    clip.movPath = os.path.join(path, content[0])
    clip.date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(clip.movPath)))
    if os.name == 'nt':
        clip.dir = clip.path.split('\\')[len(clip.path.split('\\')) - 2]
    else:
        clip.dir = clip.path.split('/')[len(clip.path.split('/')) - 1]
    if meta:
        # print content, ' ____content'
        # print clip.movPath
        clip.start = str(0)
        clip.end = str(int(meta['streams'][0]['nb_frames']) - 1)
        clip.length = meta['streams'][0]['nb_frames']
        clip.height = str(meta['streams'][0]['height'])
        clip.width = str(meta['streams'][0]['width'])
        if createThumb:
            path = clip.movPath
            f = getThumb(path, os.path.join(getDataPath(), clip.name + getThumbSuffix() + '.png'), delete=False)
            clip.thumbnail = f
    return clip


def buildImg(content=[], path=''):
    content = sorted(content)
    meta = getMeta(os.path.join(path, content[0]))
    clip = Clip()
    clip.movPath = os.path.join(path, content[0])
    clip.path = path
    clip.name = content[0].split('.')[0]
    if os.name == 'nt':
        clip.dir = clip.path.split('\\')[len(clip.path.split('\\')) - 2]
    else:
        clip.dir = clip.path.split('/')[len(clip.path.split('/')) - 1]
    clip.ext = content[0].split('.')[2]
    clip.start = content[0].split('.')[1]
    clip.end = content[len(content) - 1].split('.')[1]
    clip.length = len(content)
    clip.date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path)))
    clip.thumbnail = clip.movPath
    clip.files = content
    # print clip.thumbnail
    if meta:
        clip.height = str(meta['streams'][0]['height'])
        clip.width = str(meta['streams'][0]['width'])
    return clip


def makeMov(filein='', fileout='', quality=15, scrub=True):
    '''
    creates h264 movie from images\n
    forces overwrite\n
    image format 801_SC_v06.%04d.dpx\n
    '''
    # num = filein.split('.')
    # filein =
    # quality check
    if quality < 1:
        qual = str(1)
    else:
        qual = str(quality)
    # make movie
    if scrub:
        # scrubbing
        cmd = ['ffmpeg', '-y', '-probesize', '5000000', '-f', 'image2', '-r', '24', '-i', filein,
               '-c:v', 'libx264', '-profile:v', 'main', '-g', '1', '-tune', 'stillimage', '-crf', qual, '-bf',
               '0', '-vendor', 'ap10', '-pix_fmt', 'yuv420p', fileout]
    else:
        # non scrubbing
        cmd = ['ffmpeg', '-y', '-probesize', '5000000', '-f', 'image2', '-r', '24', '-i', filein,
               '-c:v', 'libx264', '-profile:v', 'main', '-vendor', 'ap10', '-pix_fmt', 'yuv420p', '-crf', qual, fileout]
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p1.communicate()
    print "==========output=========="
    print out
    if err:
        print "========= error ========"
        print err, '))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))'
    return filein


path1 = 'C:\\VFX\\projects\\Cop_Dog_Promo'
leaf1 = '*\\images\\*'
path2 = 'C:\\VFX\\projects\\Scarecrow\\Work'
leaf2 = '*\\Maya\\movies'
'''
bla = getClips( path1, leaf1 )
for b in bla:
    print b.__dict__
'''
# print bla[0].width
filein = 'C:\\VFX\\projects\\Scarecrow\\IO\\_Output\\805_SC_v05\\805_SC_v05.0001.dpx'
fileout = 'C:\\VFX\\projects\\Scarecrow\\IO\\_Output\\805_SC_v05\\805_SC_v05.mov'
# makeMov( filein, fileout, 1 )
# buildSeqName( filein )


def getFiles(path='', leaf=''):
    '''
    will look for contents in given path + leaf sub dir
    path = base path
    leaf = sub directories, use * for path wildcards
    '''
    contents = glob.glob(os.path.join(path, leaf))
    bucket = []
    for con in contents:
        # print con
        c = os.listdir(con)
        # print c
        seqFrames = []
        seqNames = []
        data = sorted(c, key=lambda x: x.split('.')[0])
        for nm, frm in itertools.groupby(data, lambda x: x.split('.')[len(x.split('.')) - 1]):
            seqFrames.append(list(frm))    # Store group iterator as a list
            seqNames.append(nm)
        print seqNames
        print seqFrames
