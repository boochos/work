import os, subprocess


def crop( dirIn = 'C:\Users\Sebastian\Desktop\in', dirOut = 'C:\Users\Sebastian\Desktop\out', w = 2550, h = 4200, c = 3300 ):
    '''
    apparently crops images,
    need ffmpeg
    '''
    images = os.listdir( dirIn )
    for image in images:
        img = os.path.join( dirIn, image )
        imgOut = os.path.join( dirOut, image )
        cmd = ['ffmpeg', '-i', img, '-filter:v', 'crop=' + str( w ) + ':' + str( c ) + ':0:0', '-y', imgOut]
        p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        out, err = p.communicate()
        print( "==========output==========" )
        print( out )
        if err:
            print( "========= error ========" )
            print( err )
    # return filein
