import os
import subprocess

def renderFrames(*args):
    filein = '/data/jobs/CHP/reference/onSetData/witnessCams/6J_take1_A.MP4'
    fileout = '/home/sebastianw/Desktop/witcam/6J_take1_A.%05d.png'
    #All
    cmd = ['ffmpeg', '-i', filein, '-vcodec', 'png' ,fileout ]
    p =  subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print out
    #Start/End
    #hh:mm:ss[.xxx]
    start = '00:00:05'
    end = '00:00:07'
    cmd = ['ffmpeg', '-ss', start, '-i', filein, '-to', end, '-vcodec', 'png' ,fileout ]
    p =  subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print out