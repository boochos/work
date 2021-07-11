from ctypes import *
import functools
import os
import random
import string
import subprocess
import sys
import tempfile
import threading
import time
import traceback

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import clips_lib as clp


# reload( clp )
# from key_base.python.quicktime import ffmpegtool
# from key_tools_playblast import key_tools_playblast_lib as ktpl
# HACK: get a paradigm, build clips, proper list built
def getTempDir( *args ):
    return tempfile.gettempdir()


class struct_timespec( Structure ):
    _fields_ = [( 'tv_sec', c_long ), ( 'tv_nsec', c_long )]


class struct_stat64( Structure ):
    _fields_ = [
        ( 'st_dev', c_int32 ),
        ( 'st_mode', c_uint16 ),
        ( 'st_nlink', c_uint16 ),
        ( 'st_ino', c_uint64 ),
        ( 'st_uid', c_uint32 ),
        ( 'st_gid', c_uint32 ),
        ( 'st_rdev', c_int32 ),
        ( 'st_atimespec', struct_timespec ),
        ( 'st_mtimespec', struct_timespec ),
        ( 'st_ctimespec', struct_timespec ),
        ( 'st_birthtimespec', struct_timespec ),
        ( 'dont_care', c_uint64 * 8 )
    ]


def get_creation_time( path ):
    libc = CDLL( 'libc.dylib' )
    stat64 = libc.stat64
    stat64.argtypes = [c_char_p, POINTER( struct_stat64 )]

    buf = struct_stat64()
    rv = stat64( path, pointer( buf ) )
    if rv != 0:
        raise OSError( "Couldn't stat file %r" % path )
    return buf.st_birthtimespec.tv_sec


class FolderWatcher( threading.Thread ):

    '''
    Description: Class that starts a thread to watch the specified path for changes\n
    Arguments:\n
    imagePath<string>:Path to the folder to watch the contents of
    Notes: This class is created and started when the key_tools_playblast_ui is started. This Class
    is used to update the UI with any folder changes.
    return:N/A\n
    '''
    # Set the env to False incase it isn't
    os.environ['UPDATE_FOLDER'] = 'FALSE'

    def __init__( self, path ):
        threading.Thread.__init__( self )
        self.path = path

    def run( self ):
        before = dict( [( f, None ) for f in os.listdir( self.path )] )
        status = os.getenv( 'THREAD_STATUS' )
        while status == 'True':
            time.sleep( 1 )
            # To communicate with the thread, just before Maya starts playblasting a writing.txt is created
            # This will cause the thread to not see any changes in the folder until the writing.txt is removed/deleted
            writing = os.path.isfile( os.path.join( self.path, 'writing.txt' ) )
            if not writing:
                after = dict( [( f, None ) for f in os.listdir( self.path )] )
                changed = [f for f in after if not f in before]
                if changed:
                    os.environ['UPDATE_FOLDER'] = 'TRUE'
                else:
                    changed = [f for f in before if not f in after]
                    if changed:
                        os.environ['UPDATE_FOLDER'] = 'TRUE'
                before = after
            # When the window closes the thread status is false, and is stopped
            status = os.getenv( 'THREAD_STATUS' )


class KeyToolsPlayblastManagerWindow( QWidget ):

    def __init__( self, path, ext, leaf, parent = None ):
        super( KeyToolsPlayblastManagerWindow, self ).__init__( parent )
        self.path = path
        self.ext = ext
        self.procs = []
        os.environ['THREAD_STATUS'] = 'True'
        self.user = os.getenv( 'USER' )
        self.statName = 'approval_status_'
        self.sts = '__status.sts'
        self.st1 = 'None'
        self.st2 = 'Playblasts'
        self.st3 = 'Animation Dailies'
        self.st4 = 'Supervisor Dailies'
        self.st5 = 'Trash'
        self.tables = []
        self.leaf = leaf
        self.scroll = 28
        self.height = 75
        self.col = [135, 200, 60, 60, 135, 60, 130]
        self.somcol = self.scroll
        for i in range( 0, len( self.col ), 1 ):
            if i != 1:
                self.somcol = self.somcol + self.col[i]
        self.allcol = self.scroll
        for i in range( 0, len( self.col ), 1 ):
            self.allcol = self.allcol + self.col[i]
        # Get the file location then move up 3 levels to the root path

        # self.rootPath = os.path.dirname(os.path.abspath(__file__))
        for i in range( 3 ):
            # self.rootPath = os.path.split(self.rootPath)[0]
            pass
        self.rootPath = 'C:\Program Files\Python27\Lib\site-packages\key_base'

        self.createControls()
        self.playblast_dir = clp.getClips( self.path, self.leaf )
        self.redrawAllTables()
        self.setTables()
        # Create FolderWatcher
        if os.path.isdir( self.path ):
            watch = FolderWatcher( self.path )
            watch.start()
        # Create a time to check for changes in the folder provided in path, if there are changes
        # and nothing is being written to the folder, the table will update
        timer = QTimer( self )
        self.connect( timer, SIGNAL( 'timeout()' ), self.updateTable )
        timer.start( 250 )

    def approvalAss( self, path ):
        if '.' in path:
            path = path.split( '.' )[0]
            # print path, 'old'
            result = path + self.sts
            # print result, ' result'
            return result
        else:
            # print '  here'
            return path

    def approvalCMD( self, arg ):
        '''
        0 = None unapprove
        1 = approve
        2 = morgan
        3 = nuke
        '''
        table = self.tabLayout.currentWidget()
        selectedIndexes = table.selectedIndexes()
        selectedItems = table.selectedItems()
        # print arg
        # none
        if arg == 0:
            for i in range( 0, len( selectedIndexes ), 1 ):
                if selectedIndexes[i].column() == 1:
                    self.statName = selectedItems[i].text()
                    # print selectedItems[i].data, self.statName
                    selPath = self.approvalAss( selectedItems[i].data )
                    self.setApprovalStatus( selPath, 'None' )
        # anim
        elif arg == 1:
            for i in range( 0, len( selectedIndexes ), 1 ):
                if selectedIndexes[i].column() == 1:
                    self.statName = selectedItems[i].text()
                    # print selectedItems[i].data, self.statName
                    selPath = self.approvalAss( selectedItems[i].data )
                    self.setApprovalStatus( selPath, 'anim' )
        # anim
        elif arg == 2:
            for i in range( 0, len( selectedIndexes ), 1 ):
                if selectedIndexes[i].column() == 1:
                    self.statName = selectedItems[i].text()
                    # print selectedItems[i].data, self.statName
                    selPath = self.approvalAss( selectedItems[i].data )
                    self.setApprovalStatus( selPath, 'nuke' )
        # final
        else:
            for i in range( 0, len( selectedIndexes ), 1 ):
                if selectedIndexes[i].column() == 1:
                    self.statName = selectedItems[i].text()
                    # print selectedItems[i].data, self.statName
                    selPath = self.approvalAss( selectedItems[i].data )
                    self.setApprovalStatus( selPath, 'morgan' )

        self.redrawAllTables()

    def redrawAllTables( self ):
        # get a list of all the tables then redraw them
        for i in self.tabLayout.children()[0].children():
            if type( i ).__name__ == 'QTableWidget':
                self.drawTable( i )

    def setApprovalStatus( self, path, status ):
        # if os.path.exists( path ):
        # filePath = os.path.join( path, str( self.statName ) )
        filePath = path
        # print path, 'iiinnnnnnn'
        _file = open( filePath, 'w' )
        _file.write( status )
        _file.close()
        # else:
        #    print 'oooouuuuuuttttt', path

    def setTables( self ):
        for i in self.tabLayout.children()[0].children():
            if type( i ).__name__ == 'QTableWidget':
                self.tables.append( i )

    def resizeColumn( self ):
        # get all the tables
        uiWidth = self.width()
        for i in self.tables:
            width = i.width()
            header = i.horizontalHeader()
            header.resizeSection( 1, width - self.somcol )

    def resizeEvent( self, event ):
        self.resizeColumn()

    def drawTable( self, table ):
        '''
        Description: Draw the table 
        Arguments:\n
        return:columnWidth<int>\n
        '''
        # clear the contents of the table
        table.clear()
        clipContainer = []
        status = 'None'
        columnWidth = 10
        # Create the containers to populate the table with
        for i in range( 0, len( self.playblast_dir ), 1 ):
            clip = self.playblast_dir[i]
            path = clip.path
            # path = self.approvalAss( clip.movPath )
            # print clip.__dict__
            if os.path.isdir( path ):
                # get the status, if there is no status file or its set to none that's unapproved
                self.statName = clip.name
                apprPath = os.path.join( clip.path, clip.name + self.sts )
                # print apprPath
                if os.path.exists( apprPath ):
                    _file = open( apprPath, 'r' )
                    status = _file.readlines()[0].strip( '\n' )
                    _file.close()
                else:
                    status = 'None'
                    self.setApprovalStatus( apprPath, 'None' )
                # print status
                if status == table.status_type:
                    # print table.status_type
                    qpath = QFont( path )
                    qmetric = QFontMetrics( qpath )
                    qwidth = qmetric.width( str( path ) )
                    # print path, '-----path-----'
                    clipContainer.append( clip )
                    # find the longest name
                    if qwidth > columnWidth:
                        columnWidth = qwidth
                else:
                    pass
                    # print '   ========= table didnt match   -', table.status_type, clip.name, '- \n'
            else:
                # print 'nnnnn00000000000000'
                pass

        # Set the header labels
        table.setHorizontalHeaderLabels( ['Thumbnail', 'Name:', 'Start:', 'End:', 'Dimensions:', 'Ext:', 'Date:'] )
        # Qheaderview.resizemode
        table.horizontalHeader().setResizeMode( QHeaderView.ResizeMode( 2 ) )
        table.horizontalHeader().setResizeMode( 1, QHeaderView.Stretch )

        # Set the row count
        table.setRowCount( len( clipContainer ) )

        # Create a table entry for each container
        for i in range( 0, len( clipContainer ), 1 ):
            # print i
            # create a QTableWidgetItem
            thm = QTableWidgetItem()
            # Set some of the visible attributes
            table.setRowHeight( i, self.height )
            thm.setBackgroundColor( QColor( "black" ) )

            # print clipContainer[i].name
            # Thumbnail
            # if there is a folder, with no frames icon will stay None
            icon = None
            if clipContainer[i].thumbnail != None:
                icon = QIcon( QIcon( clipContainer[i].thumbnail ) )
                thm.setIcon( icon )
                table.setIconSize( QSize( 125, 125 ) )
            else:
                thm.setText( 'None' )
            table.setColumnWidth( 0, self.col[0] )
            table.setItem( i, 0, thm )
            thm.setTextAlignment( Qt.AlignCenter )

            # Name
            item = QTableWidgetItem( clipContainer[i].name )
            item.data = clipContainer[i].movPath
            table.setItem( i, 1, item )
            item.setTextAlignment( Qt.AlignCenter )

            # Start
            item = QTableWidgetItem( clipContainer[i].start )
            table.setItem( i, 2, item )
            table.setColumnWidth( 2, self.col[2] )
            item.setTextAlignment( Qt.AlignCenter )

            # End
            item = QTableWidgetItem( clipContainer[i].end )
            table.setItem( i, 3, item )
            table.setColumnWidth( 3, self.col[3] )
            item.setTextAlignment( Qt.AlignCenter )

            # Dimension
            # print clipContainer[i].width + ' x ' + clipContainer[i].height
            dim = QTableWidgetItem( clipContainer[i].width + ' x ' + clipContainer[i].height )
            table.setItem( i, 4, dim )
            table.setColumnWidth( 4, self.col[4] )
            dim.setTextAlignment( Qt.AlignCenter )

            # Extension
            # print clipContainer[i].ext, '\n'
            item = QTableWidgetItem( clipContainer[i].ext )
            table.setItem( i, 5, item )
            table.setColumnWidth( 5, self.col[5] )
            item.setTextAlignment( Qt.AlignCenter )

            # Date
            item = QTableWidgetItem( clipContainer[i].date )
            table.setItem( i, 6, item )
            table.setColumnWidth( 6, self.col[6] )
            item.setTextAlignment( Qt.AlignCenter )
        table.sortItems( 6, Qt.DescendingOrder )

    def createButton( self, path, width, height, pos = None, parent = None, setFlat = True, tooltip = None ):
        size = QSize( width, height )
        button = QPushButton( QIcon( path ), '', self )
        button.setFlat( setFlat )
        button.setFixedSize( size )
        button.setIconSize( size )
        # button.move( 0, 0 )
        if tooltip is not None:
            button.setToolTip( QString( tooltip ) )
        if pos is not None:
            button.move( pos[0], pos[1] )
        if parent is not None:
            parent.addWidget( button )
        return button

    def createTable( self, status_type = 'None' ):
        table = QTableWidget()
        table.status_type = status_type
        table.setSelectionBehavior( QTableWidget.SelectRows )
        table.setEditTriggers( QTableWidget.NoEditTriggers )
        table.setAlternatingRowColors( True )
        table.verticalHeader().setVisible( False )
        table.setSortingEnabled( True )
        table.setColumnCount( 7 )
        table.setMinimumHeight( ( self.height * 3 ) + 32 )
        return table

    def createControls( self ):
        widthT = 150
        heightT = 60
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins( 0, 0, 0, 0 )
        self.mainLayout.setSpacing( 0 )
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins( 0, 0, 0, 0 )
        self.buttonLayout.setSpacing( 0 )
        self.controlWidget = QWidget()
        self.controlWidget.setMinimumWidth( self.allcol )
        self.controlWidget.setLayout( self.buttonLayout )
        '''
                                           '''
        self.unApBut = self.createButton( self.rootPath + '/art/icons/submitLightGrey.png', widthT, heightT,
                                         parent = self.buttonLayout, tooltip = 'You have failed me for the last time %s!<vader voice>\nUNAPPROVE!' % self.user )
        self.apBut = self.createButton( self.rootPath + '/art/icons/submitGrey.png', widthT, heightT,
                                       parent = self.buttonLayout, tooltip = 'Good job %s, one more phase to go!' % self.user )
        self.morgBut = self.createButton( self.rootPath + '/art/icons/morganSubmit.png', widthT, heightT,
                                         parent = self.buttonLayout, tooltip = '%s,the final approval, may the glorious Morgan smile favorably upon your work.' % self.user )
        self.delBut = self.createButton( self.rootPath + '/art/icons/trash.png', widthT, heightT,
                                        parent = self.buttonLayout, tooltip = '%s,you will prepare selected files for total destruction!' % self.user )
        # right side
        self.buttonLayout.addStretch()
        self.pbBut = self.createButton( self.rootPath + '/art/icons/playGreen.png', 50, heightT,
                                       parent = self.buttonLayout, setFlat = True, tooltip = '%s...\nPlay That Clip!!' % self.user )
        self.qtBut = self.createButton( self.rootPath + '/art/icons/qBlue.png', 50, heightT,
                                       parent = self.buttonLayout, tooltip = 'Hey, %s...\nThis is the Time the Quick' % ( self.user ) )
        self.nukeBut = self.createButton( self.rootPath + '/art/icons/deleteRed.png', 50, heightT,
                                         parent = self.buttonLayout, tooltip = 'PERMANENTLY DESTROY SELECTED.\n T H E R E  I S  N O  G O I N G  B A C K!!!' )
        # Set up the button connections
        self.connect( self.qtBut, SIGNAL( 'clicked()' ), self.quickTheTime )
        self.connect( self.pbBut, SIGNAL( 'clicked()' ), self.playTheBast )
        self.connect( self.nukeBut, SIGNAL( 'clicked()' ), self.deleteFolders )

        cmd = functools.partial( self.approvalCMD, 0 )
        self.connect( self.unApBut, SIGNAL( 'clicked()' ), cmd )

        cmd = functools.partial( self.approvalCMD, 1 )
        self.connect( self.apBut, SIGNAL( 'clicked()' ), cmd )

        cmd = functools.partial( self.approvalCMD, 4 )
        self.connect( self.morgBut, SIGNAL( 'clicked()' ), cmd )

        cmd = functools.partial( self.approvalCMD, 2 )
        self.connect( self.delBut, SIGNAL( 'clicked()' ), cmd )

        self.split = QSplitter( Qt.Vertical )
        self.tabLayout = QTabWidget()
        self.tabLayout.setTabBar( TabBar() )  # QTabWidget()
        self.connect( self.tabLayout, SIGNAL( 'currentChanged(int)' ), self.resizeColumn )
        # Add the tables
        self.tabLayout.addTab( self.createTable( 'None' ), 'Dailies   1' )
        self.tabLayout.addTab( self.createTable( 'anim' ), 'Dailies   2' )
        self.tabLayout.addTab( self.createTable( 'morgan' ), 'Dailies   3' )
        self.tabLayout.addTab( self.createTable( 'nuke' ), 'TRASH' )

        # Add icons to the tabs
        self.tabLayout.setTabIcon( 0, QIcon( self.rootPath + '/art/icons/submitLightGrey.png' ) )
        self.tabLayout.setTabIcon( 1, QIcon( self.rootPath + '/art/icons/submitGrey.png' ) )
        self.tabLayout.setTabIcon( 2, QIcon( self.rootPath + '/art/icons/morganSubmit.png' ) )
        self.tabLayout.setTabIcon( 3, QIcon( self.rootPath + '/art/icons/trash.png' ) )
        self.tabLayout.setIconSize( QSize( 32, 32 ) )

        # self.console = console.window()
        # self.output  = self.console.output

        self.split.addWidget( self.tabLayout )
        # self.split.addWidget(self.console)
        self.split.setSizes( [100, 0] )

        self.mainLayout.addWidget( self.controlWidget )
        self.mainLayout.addWidget( self.split )
        self.setLayout( self.mainLayout )

        # self.output = self.console.output

    def quickTheTime( self ):
        '''
        Description: Create a quicktime based off of the first select item in the QTable
        Arguments:\n
        return:N/A\n
        '''
        # Get the selected items
        table = self.tabLayout.currentWidget()
        selected = table.selectedItems()

        if len( selected ) != 0:
            if len( selected ) / 5 == 1:
                if selected[0].text() != 'None':
                    for sel in selected:
                        if sel.column() == 1:
                            path = sel.data
                            # self.audioInfo = ktpl.getAudioInfo( path )
                            auto_output = sel.data

                            mov = clp.makeMov( filein = clp.buildSeqName( auto_output ), fileout = auto_output.split( '.' )[0] + '.mov', quality = 15, scrub = True )
                            # self.playTheBast()
                            return mov

                            try:
                                print( self.audioInfo[-1] )
                                project_name, seq, shot = project.guess_shot( self.audioInfo[-1] )
                                # print project_name,seq,shot
                                self.output( 'PROJECT = %s' % project_name )
                                self.output( 'SEQ = %s' % seq )
                                self.output( 'SHOT = %s' % shot )

                                if shot:
                                    output = os.path.join( project.get_project_base(), project_name, 'SEQ', seq, shot, '3D', 'dailies' )
                                    self.output( output )
                                    if os.path.exists( output ):
                                        auto_output = output

                            except:
                                print( traceback.format_exc() )

                            if not auto_output:
                                output = QFileDialog.getExistingDirectory( self, 'Export Directory', os.getenv( 'HOME' ), QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks )
                            else:
                                output = auto_output
                            if len( output ) != 0:

                                # Set the path
                                self.tmp_audio = None

                                # Check for audio

                                audio_proc = ''

                                has_audio = False
                                '''
                                if self.audioInfo:
                                    if len( self.audioInfo ) > 2:
                                        print self.audioInfo
                                        has_audio = True
                                '''
                                if has_audio:

                                    chars = string.letters + string.digits
                                    randname = ''.join( [random.choice( chars ) for i in xrange( 10 )] )

                                    self.tmp_audio = '/var/tmp/sox_tmp_%s.aif' % randname
                                    args = [get_sox(), self.audioInfo[0], self.tmp_audio, 'trim', self.audioInfo[1], self.audioInfo[2]]
                                    self.output( subprocess.list2cmdline( args ) )
                                    audio_proc = console.process( args, console = self.output )
                                    self.procs.append( audio_proc )
                                    audio_proc.start()
                                    audio_proc.process.waitForFinished()

                                first_image = auto_output
                                q_proc = ''
                                if first_image is not None:
                                    final_output = os.path.join( str( output ), os.path.basename( path[:-5] ) ) + '.mov'

                                    arg = ''
                                    ffmpegtool_exec = os.path.join( environment.get_base(), '2d', 'bin', 'ffmpegtool' )
                                    if self.tmp_audio is not None:
                                        arg = [ffmpegtool_exec, '-a', self.tmp_audio, first_image, final_output]
                                    else:
                                        arg = [ffmpegtool_exec, first_image, final_output]

                                    reload( ffmpegtool )
                                    try:
                                        ffmpegtool.makeQuicktime( first_image,
                                                                 dest = final_output,
                                                                 audio = self.tmp_audio,
                                                                 resize = None,
                                                                 preset = None )
                                    except:

                                        error = traceback.format_exc()

                                        print( error )
                                        self.console.textBrowser.append( error )

                                    # self.console.textBrowser.clear()
                                    # q_proc = console.process(arg, console=self.output)
                                    # self.connect(q_proc.process ,SIGNAL('finished(int)'),self.finishedQToutput)
                                    # self.procs.append(q_proc)
                                    # q_proc.start()

                            else:
                                self.statusBar().showMessage( 'Operation Cancelled' )
                else:
                    self.statusBar().showMessage( 'Empty directory selected....you fail.' )
            else:
                self.statusBar().showMessage( 'Select only one playblast to convert' )

    def finishedQToutput( self ):
        if self.audioInfo is not None:
            pass
            # os.remove(self.tmp_audio)

    def playTheBast( self ):
        '''
        Description: Run Mplay\n
        Arguments:\n
        return:N/A\n
        '''
        table = self.tabLayout.currentWidget()
        # print table
        selected = table.selectedItems()
        # print selected
        for sel in selected:
            if sel.column() == 1:
                # print sel.data
                if '.mov' in sel.data:
                    cmd = ['C:\\Program Files\\Windows Media Player\\wmplayer.exe', sel.data]
                    subprocess.Popen( cmd )
                else:
                    args = ktpl.runMplay( sel.data, 'jpg', os.environ )
                    proc = console.process( args, console = self.output )
                    self.procs.append( proc )
                    proc.start()

    def updateTable( self ):
        '''
        Description: Update/Redraw the table
        return:N/A\n
        '''
        state = os.getenv( 'UPDATE_FOLDER' )
        if state == 'TRUE':
            self.redrawAllTables()
            os.environ['UPDATE_FOLDER'] = 'FALSE'

    def deleteFolders( self ):
        '''
        Description: deleted the selected folders\n
        Arguments:\n
        return:N/A\n
        '''
        user_os = os.name
        table = self.tabLayout.currentWidget()
        selectedIndexes = table.selectedIndexes()
        selectedItems = table.selectedItems()
        if table.status_type == 'nuke':
            import shutil
            for i in range( 0, len( selectedIndexes ), 1 ):
                if selectedIndexes[i].column() == 1:
                    clip = selectedItems[i].data
                    q = clp.qualify( [clip] )
                    if q == 'movie':
                        # delete movie
                        os.remove( clip )
                        # delete status file
                        os.remove( self.approvalAss( clip ) )
                    elif q == 'image':
                        # this is case specific, be careful
                        dir = clip.split( selectedItems[i].text() )[0] + selectedItems[i].text()
                        name = selectedItems[i].text()
                        # list contents
                        contents = os.listdir( dir )
                        for i in range( 0, len( contents ), 1 ):
                            c = contents[i]
                            if name in c:
                                # should delete status file and sequence,
                                # not accounting for empty directory
                                os.remove( c )
                    self.redrawAllTables()
                    self.pbBut.setDisabled( False )
        else:
            msgBox = QMessageBox()
            msgBox.setText( 'You can only NUKE files from the Nuke tab, try again.' )
            msgBox.exec_()

    def closeEvent( self, event ):
        os.environ['THREAD_STATUS'] = 'False'


def get_sox():
    if os.name() == 'Darwin':
        return os.path.join( environment.get_macports_base(), 'bin', 'sox' )

    else:
        return 'sox'


def run():
    # path       = '/var/tmp/srv_playblast'
    path1 = 'C:\\VFX\\projects\\Cop_Dog_Promo'
    leaf1 = '*\\images\\*'
    path2 = 'C:\\VFX\\projects\\Scarecrow\\Work'
    leaf2 = '*\\Maya\\movies'
    path3 = 'C:\\Users\\Sebastian\\Dropbox (Personal)\\share'
    leaf3 = ''
    path4 = '/VFX/projects/NBH/Dropbox(VFX Animation)/VFXAnimationTeam/Dmitry_Format/NBH/shots'
    leaf4 = '*/maya/movies'
    path = path4
    leaf = leaf4
    # if the folder isn't created, make it, this shouldn't happen, but just t
    if not os.path.isdir( path ):
        os.mkdir( path, 0777 )

    app = QApplication( sys.argv )
    app.setWindowIcon( ( QIcon( '/home/sebastianw/maya/2015-x64/prefs/icons/rvBlast.png' ) ) )
    controlWin = KeyToolsPlayblastManagerWindow( path, 'mov', leaf )
    controlWin.show()
    controlWin.redrawAllTables()
    controlWin.raise_()
    app.exec_()


class TabBar( QTabBar ):

    def tabSizeHint( self, index ):
        # width = QTabBar.tabSizeHint( self, index ).width()
        return QSize( 150, 50 )


if __name__ == '__main__':
    run()
