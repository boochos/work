def renameToCreation( path='C:\\Users\\Sebastian\\SkyDrive\\Google Drive\\Accounting\\Unfiled', prefix='' ):
    for filename in os.listdir( path1 ):
        oldName = os.path.join( path1, filename )
        ext = '.' + filename.split( '.' )[len( filename.split( '.' ) ) - 1]
        #print ext
        tm = datetime.datetime.fromtimestamp( os.path.getmtime( os.path.join( path1, filename ) ) )
        newName = os.path.join( path1, tm.strftime( '{0}%Y-%m-%d-%H-%M-%S'.format( prefix ) ) ) + ext
        if os.path.isfile( newName ):
            print 'already exists'
        else:
            print newName, 'doesnt exist'
            os.rename( oldName, newName )