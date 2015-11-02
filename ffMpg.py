import subprocess


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
