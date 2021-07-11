import os
import maya.cmds as cmds
import maya.mel as mel


def message( what = '' ):
    mel.eval( 'print \"' + what + '\";' )


def animPlugin():
    # load plugin
    print( 'asking for plugin state' )
    state = cmds.pluginInfo( 'animImportExport', q = True, loaded = True )
    print( 'dealing with plugin' )
    if state == 0:
        platform = os.name
        print( platform )
        if platform == 'Linux':
            cmds.pluginInfo( '/software/apps/maya/2012.sp1/cent5.x86_64/bin/plug-ins/' + 'animImportExport', e = True, a = True )
            cmds.loadPlugin( 'animImportExport' )
        elif platform == 'nt':
            path = "C:\Program Files\Autodesk\Maya2013" + "\\" + "bin\plug-ins" + "\\" + "animImportExport.mll"
            print( path )
            cmds.pluginInfo( 'C:\Program Files\Autodesk\Maya2013\\bin\plug-ins\\' + 'animImportExport.mll', e = True, a = True )
            cmds.loadPlugin( 'animImportExport' )
        else:
            print( 'mac os' )
            pass
            cmds.pluginInfo( '/Applications/Autodesk/maya2009/Maya.app/Contents/MacOS/plug-ins/' + 'animImportExport.bundle', e = True, a = True )
            cmds.loadPlugin( 'animImportExport' )
    else:
        message( 'Plugin Loaded, good to go' )


def animSelList():
    # make sure something is selected
    sel = cmds.ls( sl = True )
    return sel


def frameRange():
    # get current frame, and last playback frame
    start = cmds.currentTime( q = True )
    end = cmds.playbackOptions( q = True, max = True )
    return start, end


def animExport():
    # export anim to file
    print( 'getting sel' )
    sel = animSelList()
    if len( sel ) > 0:
        print( 'asking for plugin' )
        animPlugin()
        print( 'getting frame range' )
        frame = frameRange()
        print( 'getting path' )
        path = animPath()
        print( 'making string' )
        ops = "precision=8;intValue=17;nodeNames=0;verboseUnits=0;whichRange=1;range=" + str( frame[0] ) + ":" + str( frame[1] ) + ";options=keys;hierarchy=none;controlPoints=0;shapes=0;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -time >" + str( frame[0] ) + ":" + str( frame[1] ) + "> -float >" + str( frame[0] ) + ":" + str( frame[1] ) + "> -option keys -hierarchy none -controlPoints 0 -shape 0 "
        # ops   = "precision=8;intValue=17;nodeNames=1;verboseUnits=0;whichRange=2;range=" + str(1)         + ":" + str(24)       + ";options=keys;hierarchy=none;controlPoints=0;shapes=0;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -time >" + str(1)        + ":" +       str(24) + "> -float >" + str(1)        + ":" +      str(24)  + "> -option keys -hierarchy none -controlPoints 0 -shape 0 "
        # ops    = "precision=8;intValue=17;nodeNames=0;verboseUnits=0;whichRange=1;range=0:10;options=keys;hierarchy=none;controlPoints=0;shapes=0;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0 -shape 0 " -typ "animExport" -es "C:/Users/Sebastian/Documents/maya/testanim.anim";
        print( 'exporting file' )
        cmds.file( path, es = True, typ = "animExport", f = True, op = ops )
        print( 'print message' )
        message( 'Keys between --- ' + str( frame[0] ) + '---  and --- ' + str( frame[1] ) + '--- have been exported!' )
        print( 'after message' )
    else:
        cmds.warning( '////... Select at least one object with animation...////' )


def animImport():
    # import anim from file
    sel = animSelList()
    if len( sel ) > 0:
        animPlugin()
        frame = frameRange()
        path = animPath()
        ops = "targetTime=1;time=" + str( frame[0] ) + ";copies=1;option=merge;connect=0"
        cmds.file( path, i = True, typ = "animImport", ra = True, namespace = "animTemp", options = ops )
        cmds.select( sel )
        mel.eval( 'print \"' + 'Animation imported at  ---' + str( frame[0] ) + '---\";' )
    else:
        cmds.warning( '////... Select at least one object with animation...////' )


def animPath():
    # create directory for animation file
    path = os.path.join( os.getenv( 'HOME' ), 'maya/animationTemporary' )
    path = path.replace( '\\', '/' )
    print( 'making path' )
    if os.path.isdir( path ):
        # print 'exists'
        path = os.path.join( path, 'animTemp.anim' )
        path = path.replace( '\\', '/' )
        return path
    else:
        # print 'doesnt exists'
        os.mkdir( path )
        path = os.path.join( path, 'animTemp.anim' )
        path = path.replace( '\\', '/' )
        return path


def animCopy():
    # copy anim
    sel = animSelList()
    if len( sel ) > 0:
        frame = frameRange()
        cmds.copyKey( sel, time = ( frame[0], frame[1] ), option = 'keys', hierarchy = 'none', controlPoints = 0, shape = 1 )
        mel.eval( 'print \"' + 'Animation copied form  -' + str( frame[0] ) + '-  to  -' + str( frame[1] ) + '-\";' )
    else:
        cmds.warning( '////... Select at least one object with animation...////' )


def animPaste():
    # paste anim
    sel = animSelList()
    if len( sel ) > 0:
        frame = frameRange()
        cmds.pasteKey( sel, time = ( frame[0], ), f = ( frame[0], ), option = 'merge', copies = 1, connect = 0, timeOffset = 0, floatOffset = 0, valueOffset = 0 )
        mel.eval( 'print \"' + 'Animation pasted at  -' + str( frame[0] ) + '-\";' )
    else:
        cmds.warning( '////... Select at least one object with animation...////' )


def animCopyPaste():
    sel = cmds.ls( sl = True )
    if len( sel ) == 2:
        frame = frameRange()
        cmds.copyKey( sel[0], time = ( frame[0], frame[1] ), option = 'keys', hierarchy = 'none', controlPoints = 0, shape = 1 )
        cmds.pasteKey( sel[1], time = ( frame[0], ), f = ( frame[0], ), option = 'merge', copies = 1, connect = 0, timeOffset = 0, floatOffset = 0, valueOffset = 0 )
    else:
        cmds.warning( '////... Select 2 objects. The first should have keys...////' )
