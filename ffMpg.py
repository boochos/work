import subprocess
import os


def movToMp4(dir='', fl=''):
    filein = os.path.join(dir, fl)
    fileout = os.path.join(dir, fl).replace('.mov', '.mp4')
    print filein
    print fileout
    # All
    # cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png', fileout]
    cmd = ['ffmpeg', '-i', filein, '-c', 'copy', fileout]
    cmd = ['ffmpeg', '-i', filein, '-strict', '-2', '-c:v', 'libx264', fileout]
    cmd = ['ffmpeg', '-i', filein, '-strict', '-2', '-an', fileout]
    # -c:v libx264
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print out


def renderFrames(*args):
    filein = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002.mp4'
    fileout = 'X:/_image/_projects/SI/HOL/shots/026_004/maya/sourceimages/26_4ref1_002.%05d.png'
    # All
    cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png', fileout]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print out
    # Start/End
    # hh:mm:ss[.xxx]
    start = '00:00:05'
    end = '00:00:07'
    cmd = ['ffmpeg', '-ss', start, '-i', filein, '-to', end, '-vcodec', 'png', fileout]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print out

def go():
    dir = '/jobs/SITE/DOC/breakdowns/SARC/SpiderRef/new'
    for fl in os.listdir(dir):
        if '.mov' in fl:
            print fl
            movToMp4(dir, fl)
        # break

'''
import ffMpg
reload(ffMpg)
ffMpg.go()
'''
