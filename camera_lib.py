import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

plc = web.mod( 'atom_place_lib' )
cn = web.mod( 'constraint_lib' )
cs = web.mod( 'characterSet_lib' )
anm = web.mod( "anim_lib" )


def message( what = '', maya = False ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def lockIt( objs = [] ):
    if type( objs ) == 'list':
        for item in objs:
            plc.setChannels( objs, [True, False], [True, False], [True, False], [True, False, False] )
    else:
        plc.setChannels( objs, [True, False], [True, False], [True, False], [True, False, False] )


def getName():
    # string find...
    a = 'anim'
    # string replace...
    c = 'camera'
    # get current file
    path = cmds.file( q = 1, sn = 1 )
    # replace
    if a in path:
        path = path.replace( a, c )
        print( path )
        return path


def camTag( tag = 'shotCam' ):
    sel = cmds.ls( sl = True )
    if len( sel ) == 1:
        sel = sel[0]
        # conditions, try, exception, else(no exception)
        try:
            # select shape node
            try:
                shape = cmds.listRelatives( shapes = True )[0]  # first item only
            except:
                if cmds.nodeType( sel ) == 'camera':
                    shape = sel
        except:
            # if no shape node exists in selection
            message( 'Selection is not of camera type' )
        else:
            # is shape node a camera
            if cmds.nodeType( shape ) == 'camera':
                cmds.addAttr( ln = tag, at = 'bool', )
    else:
        message( 'Select 1 camera.' )


def camEx():
    path = getName()
    # get camera to export
    cmds.file( path, force = True, options = 'v=0', es = True, type = 'mayaAscii' )


def follow_cam( bake = False, worldOrient = True, *args ):
    '''
    sometimes adds 2 pairblends, needs to be fixed as it breaks active char set key ticks.
    '''
    # store selection
    color = 24  # brown
    color = 30  # purple
    sel = cmds.ls( sl = True )
    if len( sel ) == 1:
        # place rig nodes
        # offset = cn.locator( obj = sel[0], constrain = False, X = 2, color = color, suffix = '__OFFSET__', matchSet = False, shape = 'diamond_ctrl' )[0]
        offset = plc.circle( name = plc.getUniqueName( '__OFFSET__' ), obj = sel[0], shape = 'diamond_ctrl', size = 2.0, color = color, orient = False, colorName = None )
        cam = cmds.camera( n = plc.getUniqueName( 'cam_follow' ) )
        cmds.select( cam[0], offset )
        anm.matchObj()
        # print( cam )
        cmds.setAttr( cam[1] + '.focalLength', 55 )
        cmds.parent( cam[0], offset )
        root = plc.null2( nllSuffix = plc.getUniqueName( '__ROOT__' ), obj = sel[0], orient = True )
        parent = root
        # group
        g = cmds.group( n = plc.getUniqueName( sel[0] + '__CAM_FOLLOW__' ), em = True )
        lockIt( g )
        # place orient object
        if worldOrient:
            ornt = plc.null2( nllSuffix = plc.getUniqueName( '__WORLD_ORIENT__' ), obj = root, orient = False )[0]
            cmds.orientConstraint( g, ornt )
            cmds.parent( ornt, root )
            plc.setChannels( ornt, [True, False], [False, True], [True, False], [True, False, False] )
            parent = ornt
            spin = cn.locator( obj = ornt, constrain = False, X = 0.75, color = color, suffix = '__ORIGIN__', matchSet = False )[0]
            cn.putControlSize( spin, cn.getControlSize( sel[0] ) )
        else:
            spin = cn.locator( obj = sel[0], constrain = False, X = 1, color = color, suffix = '__ORIGIN__', matchSet = False )[0]
        # unlock scale, good for parenting to camera, controlling z-depth
        plc.scaleUnlock( spin )
        # return None
        # heirarchy
        cmds.parent( offset, spin )
        # return None
        cmds.parent( spin, parent )
        # add full path name to object
        # return None
        cmds.parentConstraint( sel[0], root, mo = True )
        # bake anim to offset loc
        cmds.parentConstraint( sel[0], offset, mo = True )
        #
        con = cn.getConstraint( offset )
        if con:
            cmds.delete( con )
        # return None
        # create final rig constraints
        # parent, rig to group
        cmds.parent( root, g )
        # match char set
        cs.matchCharSet( sel[0], [offset, spin] )
        # return None
        # clean up
        p = plc.assetParent( sel[0] )
        cmds.parent( g, p )
        # select new control
        cmds.select( offset )
        message( 'Parent rig built. -- New control Selected ', maya = True )
    else:
        cmds.warning( '-- Select 1 objects. --' )
