import os
path = '/home/sebastianw/Dev/animToolsUKB/trunk/icons'
for pic in os.listdir(path):
    isPng = pic.partition('.png')
    if len(isPng[1]) > 0:
        origName = os.path.join(path, pic)
        newName  = os.path.join(path, isPng[0] + '.xpm')
        os.system('convert ' + origName + ' ' + newName)
