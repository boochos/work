import os

path = 'C:\Users\Sebas\Documents\xpm_to_png\\'
print( path )
files = os.listdir( path )
print( files )
for pic in files:
    if 'png' in pic:
        isPng = pic.partition( '.xpm' )
        if len( isPng[1] ) > 0:
            origName = os.path.join( path, pic )
            newName = os.path.join( path, isPng[0] + '.png' )
            print origName
            print newName
            os.system( 'convert ' + origName + ' ' + newName )

'''
path = 'C:\\Users\\Sebastian\\Documents\\GitHub\\shelfIcons'
for pic in os.listdir(path):
    if 'xpm' in pic:
        isXpm = pic.partition('.xpm')
        if len(isXpm[1]) > 0:
            origName = os.path.join(path, pic)
            newName  = os.path.join(path, isXpm[0] + '.png')
            print origName
            print newName
            os.system('convert ' + origName + ' ' + newName)
'''
