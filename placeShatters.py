from random import randint

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

# web
cp = web.mod( 'clipPickle_lib' )


def message( what = '', maya = True, warning = False ):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace( '\\', '/' )
    if warning:
        cmds.warning( what )
    else:
        if maya:
            mel.eval( 'print \"' + what + '\";' )
        else:
            print( what )


def place():
    ns = 'LOC'
    locFile = '/jobs/SARC/ldev_sandstorm/maya//scenes/lob/LocatorsForSeb.mb'
    locG = ns + ':locGroup'
    # select locs
    sel = cmds.ls( sl = True )
    if sel:
        locs = sel
        print ' -- Using selection list -- '
    else:
        # ref locs
        cmds.file( locFile, reference = True, ns = ns )
        # get locs in group
        locs = cmds.listRelatives( locG, children = True )
        print ' -- Using loc file list -- '
    # shatter variables
    puff = '/jobs/SARC/ldev_sandstorm/maya/scenes/lob/GlassPuffCombined_referencer.ma'
    puffNs = 'shatter__'
    puffG = 'GlassPuffCombined_01'
    puffEl = 'Puffs'
    # hard coded camera name
    cam = 'camera'
    # setup shatter per loc
    for i in range( len( locs ) ):
        # if only one loc in list, 'if' will account
        if i < len( locs ):
            # ref shatter
            # pfns = puffNs + str(i)
            pfns = getUniqueNs( ns = puffNs )
            print pfns
            cmds.file( puff, reference = True, ns = pfns )
            # get loc location
            roo = cmds.xform( locs[i], q = True, roo = True )
            pos = cmds.xform( locs[i], q = True, ws = True, rp = True )
            rot = cmds.xform( locs[i], q = True, ws = True, ro = True )
            # set shatter location
            rooO = cmds.xform( pfns + ':' + puffG, q = True, roo = True )
            cmds.xform( pfns + ':' + puffG, roo = roo )
            cmds.xform( pfns + ':' + puffG, ws = True, t = pos, ro = rot )
            cmds.xform( pfns + ':' + puffG, roo = rooO )
            # aim puff texture at camera, use world up
            '''
            con = cmds.aimConstraint(cam, pfns + ':' + puffEl, mo=False, sk=('x', 'z'), wut='scene', u=(0.0, 0.0, -1.0),  aim=(0.0, 1.0, 0.0))
            cmds.delete(con)
            '''


def retime():
    # create window
    shatter = 'Shatter'
    try:
        cmds.deleteUI( shatter )
    except:
        pass
    window = cmds.window( shatter, title = 'Shatter Retime' )
    # cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, cr=True)
    cmds.columnLayout( adjustableColumn = True )
    sliders = []
    # asset references row
    cmds.rowLayout( numberOfColumns = 14, columnAlign = ( 1, 'center' ), adj = 6, columnAttach = [( 1, 'left', 0 ), ( 2, 'right', 0 )] )
    w = 70
    ww = w - 20
    cmds.text( l = 'REFERENCE:', al = 'left', w = 80 )
    cmds.text( l = 'Sim    ', al = 'left', w = 50 )
    cmds.button( label = ' Shatters ', c = 'import placeShatters as ps\nps.place()', w = ww )
    cmds.button( label = ' Cloud ', c = 'import placeShatters as ps\nps.refCloud()', w = ww )
    cmds.button( label = ' Wind ', c = 'import placeShatters as ps\nps.refWind()', w = ww )
    cmds.text( l = '  Geo    ', al = 'right' )
    cmds.button( label = ' Vl Cornhill ', c = 'import placeShatters as ps\nps.refValeCornhill()', w = w )
    cmds.button( label = ' Tm Cornhill ', c = 'import placeShatters as ps\nps.refTomCornhill()', w = w )
    cmds.button( label = ' Bengal ', c = 'import placeShatters as ps\nps.refBengal()', w = w )
    cmds.button( label = ' Birchin ', c = 'import placeShatters as ps\nps.refBirchin()', w = w )
    cmds.text( l = '  Full Setup    ', al = 'right' )
    cmds.button( label = ' Vale Setup ', c = 'import placeShatters as ps\nps.refValeSetup()', w = w, ann = 'setup from 137_snd_2200' )
    cmds.button( label = ' Tom Setup ', c = 'import placeShatters as ps\nps.refTomSetup()', w = w, ann = 'setup from 137_snd_7300' )
    cmds.setParent( '..' )
    cmds.separator( height = 10, style = 'in' )
    # vis settings
    cmds.rowLayout( numberOfColumns = 8, columnAlign = ( 1, 'center' ), adj = 8, columnAttach = [( 1, 'left', 0 ), ( 2, 'right', 0 )] )
    w = 70
    cmds.text( l = 'VISIBILITY:', al = 'left', w = 80 )
    cmds.text( l = 'Toggle    ', al = 'left', w = 50 )
    cmds.button( label = ' Puffs ', c = 'import placeShatters as ps\nps.togglePuffs()', w = ww )
    cmds.button( label = ' Glass ', c = 'import placeShatters as ps\nps.toggleGlass()', w = ww )
    cmds.button( label = ' Grains ', c = 'import placeShatters as ps\nps.toggleGrains()', w = ww )
    cmds.button( label = ' Grains + ', c = 'import placeShatters as ps\nps.toggleDenseGrains()', w = ww )
    cmds.button( label = ' Cracks ', c = 'import placeShatters as ps\nps.toggleCracks()', w = ww )
    cmds.setParent( '..' )
    cmds.separator( height = 10, style = 'in' )
    # selection offset
    cmds.rowLayout( numberOfColumns = 13, columnAlign = ( 1, 'center' ), adj = 9, columnAttach = [( 1, 'left', 0 ), ( 2, 'right', 0 )] )
    w = 70
    cmds.text( l = 'TIMING:', al = 'left', w = 80 )
    cmds.text( l = 'Shift cache of selected glass    ', al = 'left', w = 150 )
    cmds.button( label = ' <<<  10 ', c = 'import placeShatters as ps\nps.shiftSelected(v=-10)', w = w )
    cmds.button( label = ' <<  5 ', c = 'import placeShatters as ps\nps.shiftSelected(v=-5)', w = w )
    cmds.button( label = ' <  1  ', c = 'import placeShatters as ps\nps.shiftSelected(v=-1)', w = w )
    cmds.button( label = '  1  > ', c = 'import placeShatters as ps\nps.shiftSelected(v=1)', w = w )
    cmds.button( label = ' 5  >> ', c = 'import placeShatters as ps\nps.shiftSelected(v=5)', w = w )
    cmds.button( label = ' 10  >>> ', c = 'import placeShatters as ps\nps.shiftSelected(v=10)', w = w )
    cmds.text( l = '  Randomize    ', al = 'right' )
    cmds.button( label = ' +/- ', c = 'import placeShatters as ps\nps.offsetRandom(rng=3)', w = w )
    cmds.text( l = '  Glass Cracks Anim    ', al = 'right' )
    cmds.button( label = ' Import ', c = 'import placeShatters as ps\nps.crackVisAnim(shift=10)', w = w )
    cmds.setParent( '..' )
    cmds.separator( height = 10, style = 'in' )
    cmds.scrollLayout( horizontalScrollBarThickness = 16, verticalScrollBarThickness = 16, cr = True, h = 700 )
    cmds.columnLayout( adjustableColumn = True )
    grey = [0.24, 0.24, 0.24]
    greyD = [0.23, 0.23, 0.23]
    bg = [grey, greyD]
    tgl = 0
    # alembic section
    # get alembics from refs
    minV = cmds.playbackOptions( q = True, minTime = True ) - 80
    maxV = cmds.playbackOptions( q = True, maxTime = True ) + 80
    almb = cmds.ls( type = 'AlembicNode' )
    almbShtr = []
    for a in almb:
        if 'shatter__' in a:
            almbShtr.append( a )
    if almbShtr:
        for a in almbShtr:
            # row
            cmds.rowLayout( numberOfColumns = 3, adjustableColumn = 3, columnAlign = ( 1, 'left' ), columnAttach = [( 1, 'left', 0 ), ( 2, 'left', 0 )] )
            # button
            conn = cmds.listConnections( a, s = 0, d = 1 )
            cmd = None
            for c in conn:
                if cmds.nodeType( c ) == 'transform':
                    cmd = 'import maya.cmds as cmds\ncmds.select("%s")' % c
                    cmdTgl = 'import maya.cmds as cmds\ncmds.select("%s", tgl=True)' % c
            if cmd:
                bgc = [0.32, 0.32, 0.32]
            	cmds.button( label = 'select', c = cmd )
                cmds.button( label = 'toggle', c = cmdTgl )
            else:
            	cmds.button( label = 'None' )
            # slider group
            v = cmds.getAttr( a + '.offset' )
            # print v
            attr = '%s.offset' % a
            sl = cmds.attrFieldSliderGrp( at = attr, label = a.split( ':' )[0], smn = minV, smx = maxV, fieldMinValue = 0, fieldMaxValue = 2000, ann = a,
            pre = 3, s = 1.0, adj = 3, columnWidth3 = ( 75, 75, 100 ), columnAlign = ( 1, 'left' ), columnAttach = [( 1, 'left', 0 ), ( 2, 'left', 0 ), ( 3, 'both', 0 )] )
            # print sl
            sliders.append( sl )
            cmds.setParent( '..' )
            if tgl == 0:
                tgl = 1
            else:
                tgl = 0
    else:
        message( 'No shatter alembics found', warning = True )
    # show window
    cmds.showWindow( window )


def shiftSelected( v = 1 ):
    sel = cmds.ls( sl = True )
    for a in sel:
        shp = cmds.listRelatives( a, s = True )
        alm = cmds.listConnections( shp, t = 'AlembicNode' )
        if alm:
            offset = cmds.getAttr( alm[0] + '.offset' )
            try:
                offset = cmds.getAttr( alm[0] + '.offset' )
                print offset
                cmds.setAttr( alm[0] + '.offset', offset + v )
            except:
                print 'no'


def listShatters():
    rfs = cmds.ls( typ = 'reference' )
    shatters = []
    for ref in rfs:
        # print ref
        try:
            ns = cmds.referenceQuery( ref, ns = True, shn = True )
            # print ns, '++++++'
            if 'shatter__' in ns:
                shatters.append( ns )
        except:
            pass
    # print shatters
    return shatters


def togglePuffs():
    shatters = listShatters()
    if shatters:
        v = cmds.getAttr( shatters[0] + ':Puffs.visibility' )
        for s in shatters:
            cmds.setAttr( s + ':Puffs.visibility', not( v ) )
        message( 'Puffs set to: ' + str( not( v ) ) )
    else:
        message( 'No Shatter references found' )


def toggleGlass():
    shatters = listShatters()
    if shatters:
        v = cmds.getAttr( shatters[0] + ':Glass.visibility' )
        for s in shatters:
            cmds.setAttr( s + ':Glass.visibility', not( v ) )
        message( 'Glass set to: ' + str( not( v ) ) )
    else:
        message( 'No Shatter references found' )


def toggleGrains():
    shatters = listShatters()
    if shatters:
        v = cmds.getAttr( shatters[0] + ':GrainyGlass.visibility' )
        for s in shatters:
            cmds.setAttr( s + ':GrainyGlass.visibility', not( v ) )
        message( 'GrainyGlass set to: ' + str( not( v ) ) )
    else:
        message( 'No Shatter references found' )


def toggleDenseGrains():
    shatters = listShatters()
    dense = []
    v = None
    if shatters:
        for shtr in shatters:
            try:
                v = cmds.getAttr( shtr + ':Denser:GrainyGlass.visibility' )
                if v != None:
                    dense.append( shtr )
            except:
                pass
        if v != None:
            for s in dense:
                try:
                    cmds.setAttr( s + ':Denser:GrainyGlass.visibility', not( v ) )
                except:
                    print 'here'
                    pass
            message( 'Denser:GrainyGlass set to: ' + str( not( v ) ) )
    else:
        message( 'No Shatter references found' )


def toggleCracks():
    shatters = listShatters()
    if shatters:
        v = cmds.getAttr( shatters[0] + ':CrackedGlass.visibility' )
        for s in shatters:
            cmds.setAttr( s + ':CrackedGlass.visibility', not( v ) )
        message( 'CrackedGlass set to: ' + str( not( v ) ) )
    else:
        message( 'No Shatter references found' )


def refCloud():
    # dust cloud
    f = '/jobs/SARC/137_snd_1700/maya/scenes/lob/DustCloudElement.ma'
    ns = getUniqueNs( ns = 'cloud' )
    print ns
    cmds.file( f, reference = True, ns = ns )


def refWind():
    # dust blowing sideways
    f = '/jobs/SARC/ldev_sandstorm/maya/scenes/tcha/Abstractdust_v005.mb'
    ns = getUniqueNs( ns = 'wind' )
    cmds.file( f, reference = True, ns = ns )


def refValeCornhill():
    # cornhill vale env geo
    f = '/jobs/SARC/137_snd_2200/maya/scenes/swe/cornhill_vale.ma'
    ns = getUniqueNs( ns = 'valeEnv' )
    cmds.file( f, reference = True, ns = ns )


def refTomCornhill():
    # corhill tom env geo
    f = '/jobs/SARC/137_snd_7300/maya/scenes/swe/cornhill_tom.ma'
    ns = getUniqueNs( ns = 'tomEnv' )
    cmds.file( f, reference = True, ns = ns )


def refValeSetup():
    f = '/jobs/SARC/137_snd_2200/maya/scenes/swe/cornhill_vale_stripped.ma'
    ns = getUniqueNs( ns = 'valeSetup_2200' )
    cmds.file( f, reference = True, ns = ns )


def refTomSetup():
    f = '/jobs/SARC/137_snd_7300/maya/scenes/swe/cornhill_tom_stripped.ma'
    ns = getUniqueNs( ns = 'tomSetup_7300' )
    cmds.file( f, reference = True, ns = ns )


def refBirchin():
    # cornhill vale env geo
    f = '/jobs/SARC/137_snd_1660/maya/scenes/lob/BirchinLane_reduced_03.ma'
    ns = getUniqueNs( ns = 'BrchnEnv' )
    cmds.file( f, reference = True, ns = ns )


def refBengal():
    # cornhill vale env geo
    f = '/jobs/SARC/137_snd_2200/maya/scenes/swe/BengalCourt.ma'
    ns = getUniqueNs( ns = 'bengalEnv' )
    cmds.file( f, reference = True, ns = ns )


def crackVisAnim( shift = 10 ):
    path = '/u/swe/Public/clipLibrary/crackVis.0002.clip'
    almb = cmds.ls( type = 'AlembicNode' )
    almbShtr = []
    for a in almb:
        if 'shatter__' in a:
            ns = a.split( ':' )[0]
            print ns
            offset = cmds.getAttr( a + '.offset' )
            print offset
            cmds.select( ns + ':crackedGlass_geo' )
            try:
                cmds.currentTime( offset - shift )
                cmds.select( ns + ':crackedGlass_geo' )
                cp.clipApply( path = path, ns = True, onCurrentFrame = True )
            except:
                print 'no'
        else:
            message( 'No Shatter references found' )


def offsetRandom( rng = 3 ):
    almb = cmds.ls( type = 'AlembicNode' )
    almbShtr = []
    i = True
    j = 0
    for a in almb:
        print a
        if 'shatter__' in a:
            if j == 3:
                j = 0
            if j != 1:
                ns = a.split( ':' )[0]
                offset = cmds.getAttr( a + '.offset' )
                print offset
                r = randint( 0, rng )
                if not i:
                    r = r * -1
                print offset + r
                cmds.setAttr( a + '.offset', offset + r )
                i = not( i )
            j = j + 1


def getUniqueNs( ns = '' ):
    nsList = cmds.namespaceInfo( lon = True )
    if ns not in nsList:
        return ns
    else:
        i = 1
        while ns + str( i ) in nsList:
            i = i + 1
        return ns + str( i )
