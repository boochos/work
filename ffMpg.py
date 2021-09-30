import os
import subprocess
import time
# from cacheAbc import outDataExp


def movToMp4( dir = '', fl = '' ):
    filein = os.path.join( dir, fl )
    fileout = os.path.join( dir, fl ).replace( '.mov', '.mp4' )
    print( filein )
    print( fileout )
    # All
    # cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png', fileout]
    cmd = ['ffmpeg', '-i', filein, '-c', 'copy', fileout]
    cmd = ['ffmpeg', '-i', filein, '-strict', '-2', '-c:v', 'libx264', fileout]
    cmd = ['ffmpeg', '-i', filein, '-strict', '-2', '-an', fileout]
    # -c:v libx264
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )


def renderFrames( filein = '', fileout = '', pad = '4', format = 'png', startFrame = 1001 ):
    '''
    filein = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002.mp4'
    fileout = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002'
    '''
    fileout = fileout + '.%0' + pad + 'd.' + format
    print( fileout )
    # All
    cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png', '-start_number', str( startFrame ), fileout]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )
    '''
    # Start/End
    # hh:mm:ss[.xxx]
    start = '00:00:05'
    end = '00:00:07'
    cmd = ['ffmpeg', '-ss', start, '-i', filein, '-to', end, '-vcodec', 'png', fileout]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print out
    '''


def imgToMp4( *args ):
    '''
    os.system('ffmpeg -r 24 -b 5000k -y -i '+ soundPath + ' -i ' + saveDir + fileName +'.%04d.png -f mov ' +  fieldPath + '/' + fileName + '.mov')
    '''
    filein = 'C:/Users/sebas/Documents/maya/__PLAYBLASTS__/dba200_001_010_anm_v032/dba200_001_010_anm_v032____Camera01.0000.png'
    # filein = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002.mp4'
    fileout = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002.%05d.png'
    # All
    cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png', fileout]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )
    # Start/End
    # hh:mm:ss[.xxx]
    start = '00:00:05'
    end = '00:00:07'
    cmd = ['ffmpeg', '-ss', start, '-i', filein, '-to', end, '-vcodec', 'png', fileout]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )


def img_To_img():
    '''
    os.system('ffmpeg -r 24 -b 5000k -y -i '+ soundPath + ' -i ' + saveDir + fileName +'.%04d.png -f mov ' +  fieldPath + '/' + fileName + '.mov')
    '''
    filein = 'P:/uw/_Input/UWRP - Leaf Plates - 20210424/UWRP_011_030/UWRP_011_030_P01_V001/3200x1800/UWRP_011_030_P01_V001.%04d.dpx'
    fileout = 'P:/uw/_Input/UWRP - Leaf Plates - 20210424/UWRP_011_030/UWRP_011_030_P01_V001/3200x1800/UWRP_011_030_P01_V001.%04d.png'
    # imags = listdir(filein)
    # All
    cmd = ['ffmpeg', '-i', filein, '-start_number', '1001', fileout]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )
    #
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    print( out )


def go():
    dir = '/jobs/SITE/DOC/breakdowns/SARC/SpiderRef/new'
    for fl in os.listdir( dir ):
        if '.mov' in fl:
            print( fl )
        # break


def burn_in( filein = "", task = "", startFrame = 1001, topRight = "", size = 15, wMargin = 20, hMargin = 20 ):
    '''
    bigger margin number pushes text to edges of screen
    ffmpeg -i input -vf "drawtext=fontfile=Arial.ttf: text='%{frame_num}': start_number=1: x=(w-tw)/2: y=h-(2*lh): fontcolor=black: fontsize=20: box=1: boxcolor=white: boxborderw=5" -c:a copy output
    '''
    #
    # print( filein )
    filein = filein.replace( '/', '\\' )
    # print( filein )
    path_no_ext, ext = filein.split( "." )
    source = "file\: "
    path = ""
    #
    if not task:
        file_name = path_no_ext.split( "\\" )[-1]
        task = file_name
        path = path_no_ext.replace( task, "" )
        source = source + task
        if "_r" in task:
            task = task.split( "_r" )[0]  # split from revision
        else:
            task = task.split( "____" )[0]  # split from camera
        # task = "" + task.replace( "_r0", "_v0" )
    #
    burn1 = "_tmp__burn_in_1"
    burn2 = "_tmp__burn_in_2"
    burn3 = "__burn_in"
    #
    path1 = path_no_ext + burn1 + "." + ext
    path2 = path_no_ext + burn2 + "." + ext
    # path3 = path_no_ext + burn3 + "." + ext
    path_clientName = path_no_ext.replace( file_name, task + "." + ext )
    print ( path1 )
    print( path2 )
    print( path_clientName )
    # margin

    wm = "w/" + str( wMargin )  # divide image width to n number of pieces = margin
    hm = "h/" + str( hMargin )  # line height * margin = margin

    startFrame = str( startFrame )
    size = str( size )
    # print startFrame

    # render frames
    framesName = task + '_precomp'
    framesPath = os.path.join( path, framesName )
    if not os.path.isdir( framesPath ):
        # print path
        os.mkdir( framesPath )
    renderFrames( filein, os.path.join( framesPath, framesName ), startFrame = startFrame )
    # print( 'start burn-in 1 -----------' )
    # print( 'filein', filein )
    # print( 'path1', path1 )
    # task left upper corner
    # drawtext='fontfile=FreeSans.ttf:text=%{localtime\:%a %b %d %Y}'
    cmd = ["ffmpeg", "-i", filein, "-vf", "drawtext=fontfile=C\:\\Windows\\Fonts\\Arial.ttf: text='" + task + "': x=(" + wm + " ): y=(" + hm + "): fontcolor=white: fontsize=" + size + ": box=1: boxcolor=black: boxborderw=5", "-y", path1]
    cmd = ["ffmpeg", "-i", filein, "-vf", "drawtext=text='" + task + "': x=(" + wm + " ): y=(" + hm + "): fontcolor=white: fontsize=" + size + ": box=1: boxcolor=black: boxborderw=5", "-y", path1]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    # print( 'err ---------', err )
    # print( 'out ---------', out )
    # return

    # frames right upper corner
    cmd = ["ffmpeg", "-i", path1, "-vf", "drawtext=fontfile=C\:\\Windows\\Fonts\\Arial.ttf: text='%{frame_num}': start_number=" + startFrame + ": x=(w-tw - (" + wm + " )): y=(" + hm + "): fontcolor=white: fontsize=" + size + ": box=1: boxcolor=black: boxborderw=5", "-y", path2]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    # print( err )
    # print( out )
    os.remove( path1 )

    # frames right upper corner
    cmd = ["ffmpeg", "-i", path2, "-vf", "drawtext=fontfile=C\:\\Windows\\Fonts\\Arial.ttf: text='" + source + "': x=(" + wm + " ): y=(h-lh-" + hm + "): fontcolor=white: fontsize=" + size + ": box=1: boxcolor=black: boxborderw=5", "-y", path_clientName]
    p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    out, err = p.communicate()
    # print( err )
    # print( out )
    os.remove( path2 )
    os.remove( filein )

    # render frames path, frames name, burning qt path with name
    return [framesPath, framesName]

# burn_in()
'''
import ffMpg
reload( ffMpg )
ffMpg.img_To_img()
'''
