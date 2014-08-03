import os, subprocess
import json, time, re
import glob, itertools
import re
import datetime


class Clip():
    def __init__( self ):
        self.name = ''
        self.start = 0
        self.end = 0
        self.ext = ''
        self.thumbnail = ''
        self.length = 0
        self.date = ''
        self.width = 0
        self.height = 0
        self.path = ''
        self.movPath = ''

def getClips( path='', leaf='' ):
    '''
    will look for contents in given path + leaf sub dir
    path = base path
    leaf = sub directories, use * for path wildcards
    '''
    contents = glob.glob( os.path.join( path, leaf ) )
    bucket = []
    for con in contents:
        #print con
        c = os.listdir( con )
        #print c
        seqFrames = []
        seqNames = []
        data = sorted( c, key=lambda x: x.split( '.' )[0] )
        for nm, frm in itertools.groupby( data, lambda x: x.split( '.' )[len( x.split( '.' ) ) - 1] ):
            seqFrames.append( list( frm ) )    # Store group iterator as a list
            seqNames.append( nm )
        #print seqNames
        #print seqFrames
        i = 0
        for frames in seqFrames:
            #print frames
            confirmSeq = []
            #anything with same name but different extension returns as part of same sequence, sort for it
            for item in frames:
                #print item, ' one'
                if '.' in item:
                    confirmSeq.append( item.split( '.' )[len( item.split( '.' ) ) - 1] )
            confirmSeq = list( set( confirmSeq ) )
            #print confirmSeq
            if len( confirmSeq ) == 1:
                b = buildClip( frames, con )
                if b:
                    bucket.append( b )
            else:
                for item in frames:
                    b = buildClip( [item], con )
                    if b:
                        bucket.append( b )
    return bucket

def buildClip( frames=[], path='' ):
    q = qualify( frames )
    if q:
        #print frames
        if q == 'movie':
            return buildMov( frames, path )
        else:    #assume image
            return buildImg( frames, path )
    else:
        pass
        #print 'pass', frames


def getMeta( filename ):
    pf = '-print_format'
    js = 'json'
    cmnd = ['ffprobe', pf, js, '-show_streams', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen( cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    #print filename
    out, err = p.communicate()
    #print "==========output=========="
    #print out
    js = json.loads( out )
    #print js
    if err:
        print "========= error ========"
        print err
    p.kill()
    return js

def getThumbSuffix():
    return '__Thumb'

def getThumb( filein, fileout, delete=False, scale=1.0 ):
    create = False
    outdate = None
    indate = None
    if delete:
        if os.path.isfile( fileout ):
            os.remove( fileout )
            print 'deleted', fileout
        return None
    else:
        if os.path.isfile( fileout ):
            outdate = os.path.getmtime( fileout )
            indate = os.path.getmtime( filein )
            if indate > outdate:
                create = True
            else:
                #print 'thumbnail is newer than source'
                pass
        else:
            create = True
        if create:
            #cmnd = ['ffmpeg', '-ss', '00:00:00', '-i', filein, '-vframes', '1', fileout]
            cmnd = ['ffmpeg', '-ss', '00:00:00', '-i', filein, '-y', '-frames:v', '1', fileout]
            p = subprocess.Popen( cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            #print filein
            out, err = p.communicate()
            print "==========output=========="
            #print out
            #js = json.loads( out )
            #print js
            if err:
                print "========= error ========"
                print err
    return fileout

def getImageSize( path='' ):
    if os.path.isfile( path ):
        #print path
        dim = subprocess.Popen( ["identify", "-format", "\"%w,%h\"", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        out, err = dim.communicate()
        if err:
            print err
        #print out
        #print dim
        s = dim.split( ',' )
        w = float( s[0].split( '"' )[1] )
        h = float( s[1].split( '"' )[0] )
        return w, h
        '''
        except:
            print '    except==========================='
            return 0, 0
            '''
    else:
        print '   nuthin========================='
        return 0, 0

def qualify( content ):
    mov = ['mov', 'avi', 'mp4']
    img = ['jpg', 'png', 'tif', 'exr', 'dpx']
    ext = content[0].split( '.' )
    ext = ext[len( ext ) - 1]
    if getThumbSuffix() not in content[0]:
        if ext in mov:
            return 'movie'
        elif ext in img:
            return 'image'
        else:
            return None
    return None

def buildSeqName( path='' ):
    path = re.sub( '\..*?\.', '.%04d.', path, flags=re.DOTALL )
    #print path
    return path

def buildMov( content, path='', createThumb=True ):
    meta = getMeta( os.path.join( path, content[0] ) )
    clip = Clip()
    clip.path = path
    #print meta, '\n-------------'
    if meta:
        clip.name = content[0].split( '.' )[0]
        clip.ext = content[0].split( '.' )[1]
        clip.movPath = os.path.join( path, content[0] )
        #print clip.movPath
        clip.start = str( 0 )
        clip.end = str( int( meta['streams'][0]['nb_frames'] ) - 1 )
        clip.length = meta['streams'][0]['nb_frames']
        clip.date = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( os.path.getmtime( clip.movPath ) ) )
        clip.height = str( meta['streams'][0]['height'] )
        clip.width = str( meta['streams'][0]['width'] )
        if createThumb:
            path = clip.movPath
            #print path, path.replace( '.' + clip.ext, '.png' ), clip.ext
            f = getThumb( path, path.replace( '.' + clip.ext, getThumbSuffix() + '.png' ), delete=False )
            clip.thumbnail = f
    return clip

def buildImg( content=[] , path='' ):
    #print content
    meta = getMeta( os.path.join( path, content[0] ) )
    clip = Clip()
    clip.movPath = os.path.join( path, content[0] )
    clip.path = path
    clip.name = content[0].split( '.' )[0]
    clip.ext = content[0].split( '.' )[2]
    clip.start = content[0].split( '.' )[1]
    clip.end = content[len( content ) - 1].split( '.' )[1]
    clip.length = len( content )
    clip.date = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( os.path.getmtime( path ) ) )
    clip.thumbnail = clip.movPath
    #print clip.thumbnail
    clip.height = str( meta['streams'][0]['height'] )
    clip.width = str( meta['streams'][0]['width'] )
    return clip


def makeMov( filein='', fileout='', quality=15, scrub=True ):
    '''
    creates h264 movie from images\n
    forces overwrite\n
    image format 801_SC_v06.%04d.dpx\n
    '''
    #num = filein.split('.')
    #filein =
    #quality check
    if quality < 1:
        qual = str( 1 )
    else:
        qual = str( quality )
    #make movie
    if scrub:
        #scrubbing
        cmd = ['ffmpeg', '-y', '-probesize', '5000000', '-f', 'image2', '-r', '24', '-i', filein,
                '-c:v', 'libx264', '-profile:v', 'main', '-g', '1', '-tune', 'stillimage', '-crf', qual, '-bf',
                 '0', '-vendor', 'ap10', '-pix_fmt', 'yuv420p', fileout]
    else:
        #non scrubbing
        cmd = ['ffmpeg', '-y', '-probesize', '5000000', '-f', 'image2', '-r', '24', '-i', filein,
                '-c:v', 'libx264', '-profile:v', 'main', '-vendor', 'ap10', '-pix_fmt', 'yuv420p', '-crf', qual, fileout]
    p1 = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
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
#print bla[0].width
filein = 'C:\\VFX\\projects\\Scarecrow\\IO\\_Output\\805_SC_v05\\805_SC_v05.0001.dpx'
fileout = 'C:\\VFX\\projects\\Scarecrow\\IO\\_Output\\805_SC_v05\\805_SC_v05.mov'
#makeMov( filein, fileout, 1 )
#buildSeqName( filein )

def getFiles( path='', leaf='' ):
    '''
    will look for contents in given path + leaf sub dir
    path = base path
    leaf = sub directories, use * for path wildcards
    '''
    contents = glob.glob( os.path.join( path, leaf ) )
    bucket = []
    for con in contents:
        #print con
        c = os.listdir( con )
        #print c
        seqFrames = []
        seqNames = []
        data = sorted( c, key=lambda x: x.split( '.' )[0] )
        for nm, frm in itertools.groupby( data, lambda x: x.split( '.' )[len( x.split( '.' ) ) - 1] ):
            seqFrames.append( list( frm ) )    # Store group iterator as a list
            seqNames.append( nm )
        print seqNames
        print seqFrames
