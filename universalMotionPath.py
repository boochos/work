import glob
import os

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
place = web.mod( "atom_place_lib" )
misc = web.mod( 'atom_miscellaneous_lib' )
cn = web.mod( 'constraint_lib' )
z = web.mod( 'zero' )
ac = web.mod( 'animCurve_lib' )


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


def CONTROLS():
    return '___CONTROLS'


def WORLD_SPACE():
    return '___WORLD_SPACE'


def MASTERCT():
    return [
    'master_TopGrp',
    'master_CtGrp',
    'master',
    'master_Offset',
    'master_Grp'
    ]


def __________________PATH():
    pass


def build_curve( length = 10, cvs = 2, layer = 0, reverse = False ):
    '''
    
    '''
    direction = 1
    if reverse:
        direction = -1
    # print( direction )
    # return
    pth = place.getUniqueName( 'path' )
    if cvs > 1:
        if cvs == 2:
            p = '[( 0, 0, 0 )'
            p = p + ',( 0, 0,' + str( length * direction ) + ')'
            p = p + ']'
            # print( p )
            crv = cmds.curve( n = pth + '_layer_' + pad_number( i = layer ), d = 1, p = eval( p ) )
            '''
            if reverse:
                cmds.setAttr( crv + '.scaleZ', -1 )'''
            return crv
        else:
            pnts = cvs
            # print( pnts )
            lengthSeg = length / ( cvs - 1 )
            # print( 'seg: ', lengthSeg )
            i = 0
            max = 200
            mlt = 0
            p = ''
            while i < pnts and i < max:
                # print( lengthSeg * i )
                if i == 0:
                    # print( 'first: ', i, mlt, lengthSeg * mlt )
                    p = '[( 0, 0, 0 )'
                    # mlt = mlt + 1
                else:
                    # print( 'the rest: ', i, mlt, lengthSeg * mlt )
                    p = p + ',( 0, 0,' + str( lengthSeg * mlt * direction ) + ')'
                mlt = mlt + 1
                i = i + 1
            p = p + ']'
            # print( p )
            crv = cmds.curve( n = pth + '_layer_' + pad_number( i = layer ), d = 2, p = eval( p ) )
            '''
            if reverse:
                cmds.setAttr( crv + '.scaleZ', -1 )'''
            return crv


def path2( length = 10, layers = 3, X = 2.0, prebuild = True, prebuild_type = 4, ctrl_shape = 'splineStart_ctrl', reverse = False, hijack_ctrl = '' ):
    '''
    path 2.0
    '''
    #
    '''
    if points < 4:
        message( 'Points variable should be higher than 3.' )
        return None'''
    #
    if prebuild:
        PreBuild = place.rigPrebuild( Top = prebuild_type, Ctrl = True, SknJnts = False, Geo = False, World = True, Master = True, OlSkool = False, Size = 10 * X )
        # return
        #
        CHARACTER = PreBuild[0]
        CONTROLS = PreBuild[1]
        WORLD_SPACE = PreBuild[2]
        MasterCt = PreBuild[3]
    #
    pathDeviate = 'pathDeviate'
    if hijack_ctrl:
        misc.optEnum( hijack_ctrl, attr = 'path', enum = 'OPTNS' )
        misc.addAttribute( [hijack_ctrl], [pathDeviate], 0, 0.5, False, 'float' )
    else:
        misc.optEnum( MASTERCT()[2], attr = 'path', enum = 'OPTNS' )
        misc.addAttribute( [MASTERCT()[2]], [pathDeviate], 0, 0.5, False, 'float' )
    cmds.setAttr( MASTERCT()[2] + '.' + pathDeviate , cb = False )
    # cmds.setAttr( MasterCt[2] + '.' + pathDeviate, 0.2 )
    # cmds.setAttr( MasterCt[2] + '.overrideColor', 23 )

    # up
    upCnt = place.Controller( place.getUniqueName( 'up' ), 'master', orient = True, shape = 'loc_ctrl', size = length * X, color = 17, setChannels = True, groups = True )
    upCntCt = upCnt.createController()
    place.cleanUp( upCntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCntCt[0] + '.ty', length * 100 )
    cmds.setAttr( upCntCt[0] + '.visibility', 0 )
    cmds.parentConstraint( 'master_Grp', upCntCt[0], mo = True )

    # layers
    layers_built = []
    colors = [ 'lightYellow', 'lightBlue', 'pink', 'hotPink', 'purple']
    cvs = 2  # cvs
    i = 0  # layer
    j = 0  # colors
    while i < layers:
        if i == 0:
            lyrs = layer( master = MASTERCT(), length = length, cvs = cvs, layer = i, attachToCurve = '', color = colors[j], up = upCntCt[4], X = X, ctrl_shape = ctrl_shape, reverse = reverse, hijack_ctrl = hijack_ctrl )
            layers_built.append( lyrs )
        else:
            lyrs = layer( master = MASTERCT(), length = length, cvs = cvs, layer = i, attachToCurve = layers_built[i - 1].curve, color = colors[j], up = upCntCt[4], X = X, ctrl_shape = ctrl_shape, reverse = reverse, hijack_ctrl = hijack_ctrl )
            layers_built.append( lyrs )
        # counters
        print( i, cvs )
        cvs = ( cvs * 2 ) - 1
        i = i + 1
        if j == 4:
            j = 0
        else:
            j = j + 1

    print( 'Below not setup for cars yet.' )
    return
    '''
    lyrs = layer( master = MasterCt, length = length, cvs = 2, layer = 0, attachToCurve = '', color = colors[0], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 3, layer = 1, attachToCurve = layers_built[0].curve, color = colors[1], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 5, layer = 2, attachToCurve = layers_built[1].curve, color = colors[2], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 9, layer = 3, attachToCurve = layers_built[2].curve, color = colors[3], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 17, layer = 4, attachToCurve = layers_built[3].curve, color = colors[4], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 33, layer = 5, attachToCurve = layers_built[4].curve, color = colors[0], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 65, layer = 6, attachToCurve = layers_built[5].curve, color = colors[1], up = upCntCt[4], X = X )
    layers_built.append( lyrs )
    lyrs = layer( master = MasterCt, length = length, cvs = 129, layer = 7, attachToCurve = layers_built[6].curve, color = colors[2], up = upCntCt[4], X = X )
    layers_built.append( lyrs )'''

    # path
    s = 0.0
    travel = 'travel'
    spacing = 'offset'
    frontTwist = 'frontTwist'
    upTwist = 'upTwist'
    sideTwist = 'sideTwist'
    wheelRadius = 'wheelRadius'
    pathLength = 'pathLength'
    pathTraveled = 'pathTraveled'
    wheelRoll = 'wheelRoll'
    wheelRollMod = 'wheelRollModulus'
    wheelBase = 'wheelBase'
    msgPths = 'paths'
    msgMp = 'motionPath'
    # vehicle on path, front of vehicle
    opf = 'onPath_front'
    opfCt = place.Controller2( opf, MasterCt[4], False, 'squareOriginZup_ctrl', X * 5, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opfCt[0], World = True )
    # cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True ) # causes double transform
    place.rotationLock( opfCt[2], True )
    place.translationLock( opfCt[2], True )
    misc.optEnum( opfCt[2], attr = 'path', enum = 'CONTROL' )
    misc.addAttribute( [opfCt[2]], [travel], 0.0, 100.0, True, 'float' )
    cmds.setAttr( opfCt[2] + '.' + travel, 0.1 )
    misc.addAttribute( [opfCt[2]], [frontTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + frontTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [upTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + upTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [sideTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + sideTwist , cb = False )
    misc.optEnum( opfCt[2], attr = 'wheelMath', enum = 'COMPUTE' )
    misc.addAttribute( [opfCt[2]], [wheelRadius], 0.001, 1000, False, 'float' )
    # cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.addAttr( opfCt[2], ln = pathLength, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathLength , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathLength , k = False )
    misc.hijackAttrs( opfCt[2], layers_built[-1].crv_info, pathLength, 'arcLength', set = False, default = None, force = True )
    cmds.addAttr( opfCt[2], ln = pathTraveled, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRoll, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRollMod, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , k = False )

    # vehicle on path, back of vehicle
    opb = 'onPath_back'
    opbCt = place.Controller2( opb, MasterCt[4], False, 'squareOriginZup_ctrl', X * 4.9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opbCt[0], World = True )
    cmds.addAttr( opbCt[2], ln = msgPths, at = 'message' )
    cmds.addAttr( opbCt[2], ln = msgMp, at = 'message' )
    # cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )  # causes double transform
    place.rotationLock( opbCt[2], True )
    misc.optEnum( opbCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    misc.addAttribute( [opbCt[2]], [pathDeviate], 0, 0.5, True, 'float' )
    cmds.connectAttr( opbCt[2] + '.' + pathDeviate, MasterCt[2] + '.' + pathDeviate, f = True )
    misc.addAttribute( [opbCt[2]], [wheelBase], 0, 1000, True, 'float' )
    misc.addAttribute( [opbCt[2]], [spacing], -100.0, 100.0, True, 'float' )
    cmds.setAttr( opbCt[2] + '.' + wheelBase, 10 )

    # vehicle on path, top of vehicle
    opu = 'onPath_up'
    opuCt = place.Controller2( opu, MasterCt[4], False, 'loc_ctrl', X * 50, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opuCt[0], World = True )
    cmds.setAttr( opuCt[0] + '.ty', X * 100 )
    cmds.setAttr( opuCt[0] + '.visibility', 0 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )
    # aim
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( opfCt[3], True )

    # front - attach to path
    motpth_f = cmds.pathAnimation( opfCt[1], name = 'front_motionPath' , c = layers_built[-1].curve, startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_f + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_f + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_f + '.' + sideTwist )
    cmds.setAttr( opfCt[2] + '.' + frontTwist, 180 )
    cmds.setAttr( opfCt[2] + '.' + sideTwist, 90 )


def layer( master = [], length = 10, cvs = 2, layer = 0, attachToCurve = '', color = '', up = '', X = 1, ctrl_shape = 'splineStart_ctrl', reverse = False, hijack_ctrl = '' ):
    '''
    # points are the uValue used in motionPath
    degree 1 (linear)
    1 spans = 2 points = 2 cvs (layer 0)
    2 spans = 3 points = 3 cvs
    3 spans = 4 points = 4 cvs
    
    degree 2 (uValues start at layer 1)
    1 spans = 2 points = 3 cvs = uValue step 0.5 (middle) (layer 1 ,...) 
    2 spans  = 3 points = 4 cvs = uValue step 0.5 ,... 
    3 spans  = 4 points = 5 cvs
    '''
    #
    xmlt = 0.1
    mo_path = ''
    # curve
    curve = build_curve( length = length, cvs = cvs, layer = layer, reverse = reverse )
    cmds.setAttr( curve + '.template', 1 )
    place.cleanUp( curve, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    crv_info = cmds.arclen( curve, ch = True, n = ( curve + '_arcLength' ) )
    # clusters
    clusters = place.clstrOnCV( curve, 'layer_' + pad_number( i = layer ) + '_Clstr' )
    cGrp = 'clstr_' + pad_number( i = layer ) + '_Grp'
    cmds.group( clusters, n = cGrp, w = True )
    cmds.setAttr( cGrp + '.visibility', 0 )
    place.cleanUp( cGrp, World = True )

    '''
    # curve up
    curve_up = cmds.duplicate( curve, name = curve + '_up' )[0]  # duplicate, try to use for up vectors
    cmds.setAttr( curve_up + '.translateY', 30 )
    place.cleanUp( curve_up, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
    # clusters up
    clusters_up = place.clstrOnCV( curve_up, 'layer_' + pad_number( i = layer ) + '_Clstr' )
    cGrp_up = 'clstrUp_' + pad_number( i = layer ) + '_Grp'
    cmds.group( clusters_up, n = cGrp_up, w = True )
    cmds.setAttr( cGrp_up + '.visibility', 0 )
    place.cleanUp( cGrp_up, World = True )
    '''

    # controls
    controls = []
    layerGp = cmds.group( em = True, name = 'layer_' + pad_number( i = layer ) + '_ctrlGrp' )
    place.cleanUp( layerGp, Ctrl = True )
    if layer == 0:
        cmds.parentConstraint( master[4], layerGp, mo = True )  # layer 0 needs to move with master
    place.setChannels( layerGp, [True, False], [True, False], [True, False], [True, False, False] )
    # vis
    if hijack_ctrl:
        place.hijackVis( layerGp, hijack_ctrl, name = 'ctrlLayer' + str( layer ), suffix = False, default = 0, mode = 'visibility' )
    else:
        place.hijackVis( layerGp, master[2], name = 'ctrlLayer' + str( layer ), suffix = False, default = 0, mode = 'visibility' )
    i = 0
    j = 0
    step = 0.0
    if layer == 1:
        step = 0.5
    if layer == 2:
        step = 0.25
    if layer > 2:
        step = 0.268  # odd math between point 0 and point 1, use this value for second position (step * i), when i == 1
    position = step * i
    lastPosition = 0
    lastPositionAnchor = 0
    #
    for handle in clusters:
        # print( 'pos: ', position, 'seg: ', seg )
        #
        name = 'layer_' + pad_number( i = layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) )
        cnt = place.Controller( name, handle, orient = False, shape = ctrl_shape, size = X * ( 1 - ( xmlt * ( layer + 1 ) ) ), sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
        cntCt = cnt.createController()
        cmds.setAttr( cntCt[2] + '.showManipDefault', 1 )
        place.rotationLock( cntCt[2], True )
        place.rotationLock( cntCt[3], True )
        cmds.parent( cntCt[0], layerGp )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        # cmds.parentConstraint( cntCt[4], clusters_up[i], mo = True )
        controls.append( cntCt )
        #
        if attachToCurve:
            z.zero( cntCt[0] )  #
            # startU in fm=False mode is index based, distance to each edit point is a whole number, no matter the length, ie, 3.5 gets you half way between point 3 and point 4 (account for double points on either end)
            # create u value position for each control, add limits.
            # follow False, frees up rotations
            # degree 2 == 4 cvs, 3 edit points
            #
            mo_path = cmds.pathAnimation( cntCt[0], name = 'layer ' + pad_number( i = layer ) + '_motionPath' , c = attachToCurve, startU = position, follow = True, wut = 'object', wuo = up, fm = False, fa = 'z', ua = 'y', inverseFront = reverse )
            # print( mo_path )
            # cmds.setAttr( mo_path + '.follow', False )
            deleteAnim( mo_path, 'uValue' )
            # cmds.orientConstraint( master[4], cntCt[0], mo = True )
            # misc.hijackAttrs( opfCt[2], crvInfo, pathLength, 'arcLength', set = False, default = None, force = True )
        # regular
        i = i + 1
        j = j + 1
        position = step * j

        # irregular
        if i == 2 and layer > 2:
            position = 0.586  # odd math between point 0 and point 1
        if i == 3 and layer > 2:
            step = 0.5
            j = 2
            position = 1.0
        # third last
        if i == len( clusters ) - 3 and layer > 2:
            # print( handle )
            lastPosition = position + 0.5  # only add half, already added above
            lastPositionAnchor = position - 0.5  # next iteration already added, need to correct by removing it with -0.5
            position = lastPositionAnchor + 0.414
        # second last
        if i == len( clusters ) - 2 and layer > 2:
            # print( handle )
            position = lastPositionAnchor + 0.741
        # last
        if i == len( clusters ) - 1  and layer > 2:
            # print( handle )
            position = lastPosition
    lyr = Layer( curve, clusters, controls, crv_info, mo_path )
    return lyr


class Layer():

    def __init__( self, curve = '', clusters = [], controls = [], crv_info = '', mo_path = '' ):
        self.curve = curve
        self.clusters = clusters
        self.controls = controls
        self.crv_info = crv_info
        self.mo_path = mo_path


def path( points = 5, X = 0.05, length = 10.0, deviationLayers = 2, layers = 3 ):
    '''
    # creates groups and master controller from arguments specified as 'True'
    segment = 4 points
    deviationLayers = deviating curve layers, for back wheels, n layers == n curves
    layers = control layers
    
    '''
    #
    if points < 4:
        message( 'Points variable should be higher than 3.' )
        return None
    #
    PreBuild = place.rigPrebuild( Top = 4, Ctrl = True, SknJnts = False, Geo = False, World = True, Master = True, OlSkool = False, Size = 150 * X )
    #
    CHARACTER = PreBuild[0]
    CONTROLS = PreBuild[1]
    WORLD_SPACE = PreBuild[2]
    MasterCt = PreBuild[3]
    #
    pathDeviate = 'pathDeviate'
    misc.optEnum( MasterCt[2], attr = 'path', enum = 'OPTNS' )
    misc.addAttribute( [MasterCt[2]], [pathDeviate], 0, 0.5, False, 'float' )
    cmds.setAttr( MasterCt[2] + '.' + pathDeviate , cb = False )
    # cmds.setAttr( MasterCt[2] + '.' + pathDeviate, 0.2 )
    # cmds.setAttr( MasterCt[2] + '.overrideColor', 23 )

    # up
    upCnt = place.Controller( place.getUniqueName( 'up' ), 'master', orient = True, shape = 'loc_ctrl', size = 60 * X, color = 17, setChannels = True, groups = True )
    upCntCt = upCnt.createController()
    place.cleanUp( upCntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCntCt[0] + '.ty', length * 100 )
    cmds.setAttr( upCntCt[0] + '.visibility', 0 )
    cmds.parentConstraint( 'master_Grp', upCntCt[0], mo = True )

    #
    path = place.getUniqueName( 'path' )

    # layers
    cluster_layers = []
    paths = []
    crvInfo = None
    layer = 0
    while layer < deviationLayers:
        # build curve
        lengthSeg = length / ( points + layer - 1.0 )
        i = 1
        p = '[( 0, 0, -1.128 )'
        while i < points + layer:
            p = p + ',( 0, 0,' + str( lengthSeg * i ) + ')'
            i = i + 1
        p = p + ']'
        # print( p )
        pth = cmds.curve( n = path + '_layer_' + pad_number( i = layer ), d = 3, p = eval( p ) )
        if layer == 0:
            crvInfo = cmds.arclen( pth, ch = True, n = ( pth + '_arcLength' ) )
            #
            # crvLength = cmds.getAttr(crvInfo + '.arcLength')
            # dvd = cmds.shadingNode('multiplyDivide', au=True, n=(curve + '_scale'))
            #
        # cmds.setAttr( pth + '.visibility', 0 )
        # print( pth )
        paths.append( pth )
        # return
        cmds.setAttr( pth + '.template', 1 )
        place.cleanUp( pth, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cl = place.clstrOnCV( pth, 'layer' + pad_number( i = layer ) + '_Clstr' )
        # cleanup clusters and controllers
        cGrp = 'clstr_' + pad_number( i = layer ) + '_Grp'
        cmds.group( cl, n = cGrp, w = True )
        cmds.setAttr( cGrp + '.visibility', 0 )
        place.cleanUp( cGrp, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        cluster_layers.append( cl )
        layer = layer + 1
        if layer != deviationLayers and layer != 1:
            cmds.setAttr( pth + '.visibility', 0 )
    # print( paths )
    for l in range( len( cluster_layers ) - 1 ):
        # constrain start, end
        c = 0
        for c in range( len( cluster_layers[l + 1] ) - 0 ):
            # print( '____', c )
            # first
            if c == 0:
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
            # last
            elif cluster_layers[l + 1][c] == cluster_layers[l + 1][-1]:
                cmds.parentConstraint( cluster_layers[l][-1], cluster_layers[l + 1][c], mo = False )
                break
            else:
                constraint = cmds.parentConstraint( cluster_layers[l][c - 1], cluster_layers[l + 1][c], mo = False )[0]
                cmds.parentConstraint( cluster_layers[l][c], cluster_layers[l + 1][c], mo = False )
                place.hijackConstraints( master = MasterCt[2], attr = pathDeviate, value = 0.5, constraint = constraint )
            c = c + 1

    Ctrls = path_control_layers( clusters = cluster_layers[0], layers = layers, parent = MasterCt, X = X )
    # return

    # path
    s = 0.0
    travel = 'travel'
    spacing = 'offset'
    frontTwist = 'frontTwist'
    upTwist = 'upTwist'
    sideTwist = 'sideTwist'
    wheelRadius = 'wheelRadius'
    pathLength = 'pathLength'
    pathTraveled = 'pathTraveled'
    wheelRoll = 'wheelRoll'
    wheelRollMod = 'wheelRollModulus'
    wheelBase = 'wheelBase'
    msgPths = 'paths'
    msgMp = 'motionPath'
    # vehicle on path, front of vehicle
    opf = 'onPath_front'
    opfCt = place.Controller2( opf, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opfCt[0], World = True )
    # cmds.parentConstraint( MasterCt[4], opfCt[0], mo = True ) # causes double transform
    place.rotationLock( opfCt[2], True )
    place.translationLock( opfCt[2], True )
    misc.optEnum( opfCt[2], attr = 'path', enum = 'CONTROL' )
    misc.addAttribute( [opfCt[2]], [travel], 0.0, 100.0, True, 'float' )
    cmds.setAttr( opfCt[2] + '.' + travel, 0.1 )
    misc.addAttribute( [opfCt[2]], [frontTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + frontTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [upTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + upTwist , cb = False )
    misc.addAttribute( [opfCt[2]], [sideTwist], -360, 360, False, 'float' )
    cmds.setAttr( opfCt[2] + '.' + sideTwist , cb = False )
    misc.optEnum( opfCt[2], attr = 'wheelMath', enum = 'COMPUTE' )
    misc.addAttribute( [opfCt[2]], [wheelRadius], 0.001, 1000, False, 'float' )
    # cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.addAttr( opfCt[2], ln = pathLength, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathLength , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathLength , k = False )
    misc.hijackAttrs( opfCt[2], crvInfo, pathLength, 'arcLength', set = False, default = None, force = True )
    cmds.addAttr( opfCt[2], ln = pathTraveled, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , cb = True )
    cmds.setAttr( opfCt[2] + '.' + pathTraveled , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRoll, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRoll , k = False )
    cmds.addAttr( opfCt[2], ln = wheelRollMod, at = 'float', h = False )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , cb = True )
    cmds.setAttr( opfCt[2] + '.' + wheelRollMod , k = False )
    # cmds.setAttr( opfCt[2] + '.' + spacing, -0.15 )
    # vehicle on path, back of vehicle
    opb = 'onPath_back'
    opbCt = place.Controller2( opb, MasterCt[4], False, 'squareOriginZup_ctrl', X * 60, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opbCt[0], World = True )
    cmds.addAttr( opbCt[2], ln = msgPths, at = 'message' )
    cmds.addAttr( opbCt[2], ln = msgMp, at = 'message' )
    # cmds.parentConstraint( MasterCt[4], opbCt[0], mo = True )  # causes double transform
    place.rotationLock( opbCt[2], True )
    misc.optEnum( opbCt[2], attr = travel + 'Control', enum = 'OPTNS' )
    misc.addAttribute( [opbCt[2]], [pathDeviate], 0, 0.5, True, 'float' )
    cmds.connectAttr( opbCt[2] + '.' + pathDeviate, MasterCt[2] + '.' + pathDeviate, f = True )
    misc.addAttribute( [opbCt[2]], [wheelBase], 0, 1000, True, 'float' )
    misc.addAttribute( [opbCt[2]], [spacing], -100.0, 100.0, True, 'float' )
    cmds.setAttr( opbCt[2] + '.' + wheelBase, 10 )
    # vehicle on path, top of vehicle
    opu = 'onPath_up'
    opuCt = place.Controller2( opu, MasterCt[4], False, 'loc_ctrl', X * 50, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = 'lightBlue' ).result
    place.cleanUp( opuCt[0], World = True )
    cmds.setAttr( opuCt[0] + '.ty', X * 100 )
    cmds.setAttr( opuCt[0] + '.visibility', 0 )
    cmds.parentConstraint( opbCt[4], opuCt[0], mo = True )
    # aim
    cmds.aimConstraint( opbCt[4], opfCt[3], wut = 'object', wuo = opuCt[4], aim = [0, 0, -1], u = [0, 1, 0], mo = True )
    place.rotationLock( opfCt[3], True )

    # front - attach to path
    motpth_f = cmds.pathAnimation( opfCt[1], name = 'front_motionPath' , c = paths[0], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_f + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_f + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_f + '.' + sideTwist )
    cmds.setAttr( opfCt[2] + '.' + frontTwist, 180 )
    cmds.setAttr( opfCt[2] + '.' + sideTwist, 90 )
    # back - attach to path
    motpth_b = cmds.pathAnimation( opbCt[1], name = 'back_motionPath' , c = paths[-1], startU = s, follow = True, wut = 'object', wuo = upCntCt[4], fm = True )
    cmds.addAttr( motpth_b, ln = msgMp, at = 'message' )
    cmds.connectAttr( opbCt[2] + '.' + msgMp, motpth_b + '.' + msgMp )
    cmds.connectAttr( opfCt[2] + '.' + frontTwist, motpth_b + '.' + frontTwist )
    cmds.connectAttr( opfCt[2] + '.' + upTwist, motpth_b + '.' + upTwist )
    cmds.connectAttr( opfCt[2] + '.' + sideTwist, motpth_b + '.' + sideTwist )
    # nodes
    mltNode = cmds.shadingNode( 'multiplyDivide', au = True, n = ( travel + '_MltDv' ) )  # increase travel from (0.0-1.0 to 0.0-10.0)
    cmds.setAttr( ( mltNode + '.operation' ), 1 )  # set operation: 2 = divide, 1 = multiply
    cmds.setAttr( mltNode + '.input2Z', 0.01 )
    # dblLnrNode = cmds.createNode( 'addDoubleLinear', name = ( spacing + '_DblLnr' ) )
    # travel
    cmds.connectAttr( opfCt[2] + '.' + travel, mltNode + '.input1Z' )
    cmds.connectAttr( mltNode + '.outputZ', motpth_f + '.uValue', f = True )
    # spacing
    '''
    cmds.connectAttr( mltNode + '.outputZ', dblLnrNode + '.input2' )
    cmds.connectAttr( opbCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )'''
    # distance traveled
    uvlen = cmds.shadingNode( 'multDoubleLinear', name = 'uValuePathLen_mult', asUtility = True )
    cmds.connectAttr( opfCt[2] + '.pathLength', uvlen + '.input1' )
    cmds.connectAttr( motpth_f + '.uValue', uvlen + '.input2' )
    cmds.connectAttr( uvlen + '.output', opfCt[2] + '.' + pathTraveled )
    # wheel roll
    wheel_roll_math( distanceObjAttr = opfCt[2] + '.' + pathTraveled, radiusObjAttr = opfCt[2] + '.' + wheelRadius, outputObjAttr = opfCt[2] + '.' + wheelRoll )

    # result = wheel base * -1
    whlbf = cmds.shadingNode( 'multDoubleLinear', name = 'whlBase_flip', asUtility = True )
    cmds.connectAttr( opbCt[2] + '.' + wheelBase, whlbf + '.input1' )
    cmds.setAttr( whlbf + '.input2', -1 )
    # result = path traveled + result (result should be negative)
    trvldWhlbs = cmds.createNode( 'addDoubleLinear', name = ( 'whlBase_DblLnr' ) )
    cmds.connectAttr( whlbf + '.output', trvldWhlbs + '.input2' )
    cmds.connectAttr( opfCt[2] + '.' + pathTraveled, trvldWhlbs + '.input1' )
    # result = result / path length
    trvlDv = cmds.shadingNode( 'multiplyDivide', au = True, n = ( 'whlBase_MltDv' ) )
    cmds.setAttr( ( trvlDv + '.operation' ), 2 )  # set operation: 2 = divide, 1 = multiply
    cmds.connectAttr( trvldWhlbs + '.output', trvlDv + '.input1X' )
    cmds.connectAttr( opfCt[2] + '.' + pathLength, trvlDv + '.input2X' )
    # result = result * uValue multiplier
    # whlbMlt = cmds.shadingNode( 'multDoubleLinear', name = 'whlBase_Mlt', asUtility = True )
    dblLnrNode = cmds.createNode( 'addDoubleLinear', name = ( spacing + '_DblLnr' ) )
    cmds.connectAttr( opbCt[2] + '.' + spacing, dblLnrNode + '.input1' )
    cmds.connectAttr( trvlDv + '.outputX', dblLnrNode + '.input2' )
    # cmds.connectAttr( mltNode + '.outputZ', whlbMlt + '.input2' )
    # uValue = result # connect
    # cmds.connectAttr( whlbMlt + '.output', motpth_b + '.uValue', f = True )
    cmds.connectAttr( dblLnrNode + '.output', motpth_b + '.uValue', f = True )

    # smooth display
    cmds.select( paths )
    cmds.displaySmoothness( pointsWire = 32 )

    # message, for switching path connection in script later
    for p in paths:
        shape = path_shape( p )
        cmds.addAttr( shape, ln = msgPths, at = 'message' )
        cmds.connectAttr( opbCt[2] + '.' + msgPths, shape + '.' + msgPths )

    # message for path controllers, meant to attach all controls with geo constraint to ground plane
    msg = 'control'
    cmds.addAttr( MasterCt[2], ln = msg, at = 'message' )
    for g in Ctrls:
        print( g )
        cmds.addAttr( g, ln = msg, at = 'message' )
        cmds.connectAttr( MasterCt[2] + '.' + msg, g + '.' + msg )

    # scale
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    #
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    misc.scaleUnlock( opfCt[1], sx = True, sy = True, sz = True )
    misc.scaleUnlock( opbCt[1], sx = True, sy = True, sz = True )
    misc.scaleUnlock( opuCt[1], sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
        cmds.connectAttr( mstr + '.' + uni, opfCt[1] + s )
        cmds.connectAttr( mstr + '.' + uni, opbCt[1] + s )
        cmds.connectAttr( mstr + '.' + uni, opuCt[1] + s )


def path_control_layers( clusters = [], layers = 2, parent = '', X = 1 ):
    '''
    clusters = cluster list to start
    layers = amount of layers in controls, 0 based, ie 2 == 3 layers, [0,1,2]
    segment = amount of controls between each higher layer control ie [6, 3, 2] , every 6 controls on (1st) layer adds a control on parent (2nd) layer 
    parent = top layer parent
    '''
    resultCtrls = []
    # scale
    X = X * 100
    scale_range = 0.25  # 1.0 being final top layer scale, 'X', layer 0 scale = 1.0 - scale_range
    scale_0 = 1.0 - scale_range
    scale_mlt = scale_range / layers
    colors = [ 'lightYellow', 'lightBlue', 'pink', 'hotPink', 'purple']
    # group
    layerGp = cmds.group( em = True, name = 'layer_0_ctrlGrp' )
    place.cleanUp( layerGp, Ctrl = True )
    place.setChannels( layerGp, [True, False], [True, False], [True, False], [True, False, False] )
    # vis
    place.hijackVis( layerGp, parent[2], name = 'ctrlLayer0', suffix = False, default = 0, mode = 'visibility' )
    # layer 0
    layer = 0
    # CtrlsFull_this = []
    # CtrlsFull_next = []
    Ctrls = []
    CtrlGrps = []
    CtrlTopGrps = []
    i = 0
    for handle in clusters:
        #
        name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) )
        cnt = place.Controller( name, handle, orient = False, shape = 'splineStart_ctrl', size = X * 0.25, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = colors[0] )
        cntCt = cnt.createController()
        cmds.parent( cntCt[0], layerGp )
        cmds.parentConstraint( cntCt[4], handle, mo = True )
        #
        # CtrlsFull_this.append( cntCt )
        Ctrls.append( cntCt[2] )
        CtrlGrps.append( cntCt[4] )
        CtrlTopGrps.append( cntCt[0] )
        resultCtrls.append( cntCt[2] )
        #
        i = i + 1
    clusters = CtrlTopGrps

    # layer 0 guides
    guideGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_path_guideGrp' )
    place.cleanUp( guideGp, World = True )
    place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
    place.hijackVis( guideGp, parent[2], name = 'ctrlLayer0', suffix = False, default = 1, mode = 'visibility' )
    for i in range( len( CtrlGrps ) - 1 ):
        gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
        #
        cmds.parent( gd[0], guideGp )
        cmds.parent( gd[1], guideGp )
    print( 'result amount, layer 0 ', len( resultCtrls ) )

    # prep for layer loop
    layer = layer + 1
    color = colors[1]
    clr = 1
    shapes = ['splineStart_ctrl', 'splineStart_ctrl']  # ['splineStart_ctrl', 'splineEnd_ctrl']
    shape = shapes[0]
    # add layers
    while layer <= layers:
        # group
        layerGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_ctrlGrp' )
        place.cleanUp( layerGp, Ctrl = True )
        place.setChannels( layerGp, [True, False], [True, False], [True, False], [True, False, False] )
        place.hijackVis( layerGp, parent[2], name = 'ctrlLayer' + str( layer ), suffix = False, default = 1, mode = 'visibility' )
        #
        scale_layer = scale_0 + ( scale_mlt * layer )
        # CtrlsFull_this = []
        # CtrlsFull_next = []
        CtrlGrps = []
        CtrlTopGrps = []
        w = 1.0
        n = 1
        j = 1
        i = 0

        #
        for handle in clusters:
            # next layer start control
            if j == 1:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                s_cntCt = cnt.createController()
                cmds.parent( s_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( s_cntCt )
                CtrlTopGrps.append( s_cntCt[0] )
                CtrlGrps.append( s_cntCt[4] )
                resultCtrls.append( s_cntCt[2] )
                #
                cmds.parentConstraint( s_cntCt[4], handle, mo = True )  # this handle
                if i == 0:
                    cmds.parentConstraint( s_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle, weight as well be 1.0 : weight is normalized to 1.0 between 2 wights
                else:
                    cmds.parentConstraint( s_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                j = j + 1
                n = n + 1
            # next layer end control
            elif j == 3:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                e_cntCt = cnt.createController()
                cmds.parent( e_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( e_cntCt )
                CtrlTopGrps.append( e_cntCt[0] )
                CtrlGrps.append( e_cntCt[4] )
                resultCtrls.append( e_cntCt[2] )
                # previous layer constrain
                cmds.parentConstraint( e_cntCt[4], handle, mo = True )  # this handle
                cmds.parentConstraint( e_cntCt[4], clusters[i - 1], w = w, mo = True )  # last handle
                if i != len( clusters ) - 1:
                    cmds.parentConstraint( e_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                #
                j = j + 1
                n = n + 1
                # return
            # next layer end control
            elif j == 5:
                name = 'layer_' + str( layer ) + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( n ) )
                cnt = place.Controller( name, handle, orient = False, shape = shape, size = X * scale_layer, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = color )
                e_cntCt = cnt.createController()
                cmds.parent( e_cntCt[0], layerGp )
                #
                # CtrlsFull_next.append( e_cntCt )
                CtrlTopGrps.append( e_cntCt[0] )
                CtrlGrps.append( e_cntCt[4] )
                resultCtrls.append( e_cntCt[2] )
                # previous layer constrain
                cmds.parentConstraint( e_cntCt[4], handle, mo = True )  # this handle
                cmds.parentConstraint( e_cntCt[4], clusters[i - 1], w = w, mo = True )  # last handle
                if i != len( clusters ) - 1:
                    cmds.parentConstraint( e_cntCt[4], clusters[i + 1], w = w, mo = True )  # next handle
                #
                j = 2
                n = n + 1
            else:
                j = j + 1
            # constrain top layer controls to parent
            if layer == layers:
                cmds.parentConstraint( parent[4], CtrlTopGrps[-1], mo = True )
            i = i + 1

        #
        clusters = CtrlTopGrps
        # guides
        guideGp = cmds.group( em = True, name = 'layer_' + str( layer ) + '_path_guideGrp' )
        place.cleanUp( guideGp, World = True )
        place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
        cmds.setAttr( guideGp + '.visibility', 0 )
        # place.hijackVis( guideGp, parent[2], name = 'layer' + str( layer ), suffix = True, default = 1, mode = 'visibility' )
        for i in range( len( CtrlGrps ) - 1 ):
            gd = place.guideLine( CtrlGrps[i], CtrlGrps[i + 1], CtrlGrps[i] + '_guide' )
            cmds.parent( gd[0], guideGp )
            cmds.parent( gd[1], guideGp )
        # prep for next loop
        layer = layer + 1
        if color == colors[-1]:
            color = colors[0]
            clr = 0
        else:
            color = colors[clr + 1]
            clr = clr + 1
        if shape == shapes[0]:
            shape = shapes[1]
        else:
            shape = shapes[0]
    #
    return resultCtrls


def path_shape( curve = '' ):
    '''
    return shape node
    '''
    shapes = cmds.listRelatives( curve, s = 1 )  # s = shapes
    if shapes:
        for s in shapes:
            if 'Orig' not in s:
                return s
    print( 'no shapes found' )
    return None


def path_switch():
    '''
    uses selection
    assumes selection has specific message connections
    '''
    # object on path
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 1:
        sel = sel[0]
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    if 'onPath_back' in sel:
        # motionPath node
        motionPathNode = cmds.listConnections( sel + '.motionPath' )
        if motionPathNode:
            motionPathNode = motionPathNode[0]
        else:
            motionPathNode = None
        # path shape nodes
        pathShapes = cmds.listConnections( sel + '.paths' )
        if pathShapes:
            pathShapes.sort()
        else:
            pathShapes = None
        # current path
        current_path = cmds.listConnections( motionPathNode + '.geometryPath' )
        if current_path:
            current_path = current_path[0]
        else:
            current_path = None
    else:
        message( 'Select 1 object. Expecting "onPath_back"', warning = True )
        return None
    # iterate to new
    if motionPathNode and pathShapes and current_path:
        i = 0
        for i in range( len( pathShapes ) ):
            if pathShapes[i] == current_path:
                if i + 1 <= len( pathShapes ) - 1:
                    cmds.connectAttr( pathShapes[i + 1] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[i + 1] )
                else:
                    cmds.connectAttr( pathShapes[0] + '.worldSpace[0]', motionPathNode + '.geometryPath', f = True )
                    message( pathShapes[0] )
            else:
                # print( 'no match', pathShapes[i], current_path )
                pass
    else:
        message( 'Connections missing, aborted', warning = True )


def car_to_ground():
    '''
    attach selected namespace(vehicle) to selected ground plane
    '''
    pivots = [
    'chassis_front_L_pivot',
    'chassis_front_R_pivot',
    'chassis_back_L_pivot',
    'chassis_back_R_pivot'
    ]
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        ground = sel[1]
        for p in pivots:
            cmds.pointConstraint( veh_ns + ':move', veh_ns + ':' + p, mo = True )
            cmds.geometryConstraint( ground, veh_ns + ':' + p )
    else:
        message( 'Select 2 objects: vehicle 1st, ground 2nd', warning = True )


def path_to_ground():
    '''
    master of path should be selected
    is assumed it has message connections to all path controls
    iterate and constrain each control
    '''
    controls = []
    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        controls = cmds.listConnections( sel[0] + '.control' )
        if controls:
            # namespaces
            veh_ns = sel[0].split( ':' )[0]
            ground = sel[1]
            for c in controls:
                cmds.geometryConstraint( ground, c )
        else:
            message( 'Couldnt find path controls on first object:' + sel[0], warning = True )
    else:
        message( 'Select 2 objects: expecting master control of path and ground geo as selection.', warning = True )


def car_to_path( wheels = ['wheel_front_spin_L', 'wheel_front_spin_R', 'wheel_back_spin_L', 'wheel_back_spin_R'], mod = True, easyBake = True ):
    '''
    select controls first and path object with namespace last
    assumes controls are sorted in proper order
    adds modulus node in between roll connection
    '''
    # objects
    path_obj = 'onPath_front_Grp'
    path_steer = 'onPath_front'
    path_radius = 'onPath_front.wheelRadius'
    path_roll = 'onPath_front.wheelRoll'
    path_rollMod = 'onPath_front.wheelRollModulus'
    if easyBake:
        veh_obj = 'move'  # better able to bake and export anim
        veh_steer = 'steer'  # better able to bake and export anim
    else:
        veh_obj = 'move_CtGrp'
        veh_steer = 'steer_CtGrp'
    veh_offset = 'move_Offset'
    # wheel base
    path_wheelBase = 'onPath_back.wheelBase'
    chassis_f = 'chassis_back_pivot'
    chassis_b = 'chassis_front_pivot'

    sel = cmds.ls( sl = 1 )
    if len( sel ) == 2:
        # namespaces
        veh_ns = sel[0].split( ':' )[0]
        path_ns = sel[1].split( ':' )[0]
        # objects
        path_obj = path_ns + ':' + path_obj
        path_steer = path_ns + ':' + path_steer
        veh_obj = veh_ns + ':' + veh_obj
        veh_steer = veh_ns + ':' + veh_steer
        veh_offset = veh_ns + ':' + veh_offset
        chassis_f = veh_ns + ':' + chassis_f
        chassis_b = veh_ns + ':' + chassis_b
        # attrs
        path_radius = path_ns + ':' + path_radius
        path_roll = path_ns + ':' + path_roll
        path_rollMod = path_ns + ':' + path_rollMod
        path_wheelBase = path_ns + ':' + path_wheelBase
        #
        if cmds.objExists( path_obj ) and cmds.objExists( veh_obj ):
            # wheel spin
            for wheel in wheels:
                veh_radius = veh_ns + ':' + wheel + '.radius'
                veh_roll = veh_ns + ':' + wheel + '.roll'
                veh_rx = veh_ns + ':' + wheel + '.rx'
                cmds.connectAttr( veh_radius, path_radius, f = True )  # should only connect once per radius change, this breaks previous connections, should add smarter logic
                if easyBake:
                    if mod:
                        cmds.connectAttr( path_rollMod, veh_roll )
                        cmds.connectAttr( path_rollMod, veh_rx )
                    else:
                        cmds.connectAttr( path_roll, veh_roll )
                        cmds.connectAttr( path_roll, veh_rx )
                else:
                    if mod:
                        cmds.connectAttr( path_rollMod, veh_roll )
                    else:
                        cmds.connectAttr( path_roll, veh_roll )
                # modulus_node( name = wheel, objectAttrDvdnd = path_roll, objectAttrRmndr = veh_roll, divisor = 360 )
            # amount to shift offset control
            point_A = cmds.xform( veh_obj, query = True, ws = True, rp = True )
            point_B = cmds.xform( veh_steer, query = True, ws = True, rp = True )
            distance_steer = place.distance2Pts( point_A, point_B )
            print( distance_steer )  # add value to wheelBase attr
            # cmds.setAttr( veh_offset + '.translateZ', distance_steer * -1 )  # skip, not necessary
            # wheel base
            point_A = cmds.xform( chassis_f, query = True, ws = True, rp = True )
            point_B = cmds.xform( chassis_b, query = True, ws = True, rp = True )
            distance_wheelBase = place.distance2Pts( point_A, point_B )
            cmds.setAttr( path_wheelBase, distance_wheelBase )
            # attach
            cmds.parentConstraint( path_obj, veh_obj, mo = False )
            # cmds.parentConstraint( path_steer, veh_steer, mo = False )
            cmds.orientConstraint( path_steer, veh_steer, skip = ( 'x', 'z' ) )  # cant use parentCons, axis locked if easyBake
            #
            # fix distance_steer offset
            t = cmds.xform( veh_obj, query = True, os = True, t = True )
            cmds.xform( veh_obj, os = True, t = [t[0], t[1], t[2] - distance_steer] )
            cn.updateConstraintOffset( veh_obj )
            #
        else:
            message( 'Expected objects dont exist', warning = True )
            print( path_obj, veh_obj )
    else:
        message( 'Select 2 objects: vehicle 1st, path 2nd', warning = True )


def __________________UTILS():
    pass


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def modulus_node( name = 'wheelRoll', objectAttrDvdnd = '', objectAttrRmndr = '', divisor = None ):
    '''
    create mod node
    create output mod value objAttrRmndr
    '''
    # attrs
    divdA = 'dividend'
    divsA = 'divisor'
    rsltA = 'result'
    rsltIntA = 'resultInteger'
    qtntA = 'quotient'
    rmndA = 'remainderRaw'
    rmndPosA = 'remainderProcessed'  # force positive
    rmndDgrsA = 'remainder'
    attrList = [divdA, divsA, rsltA, rsltIntA, qtntA, rmndA, rmndPosA, rmndDgrsA]
    mod = '__modulus'

    # mod object
    modNode = cmds.group( name = name + mod, em = True )
    place.translationLock( modNode, True )
    place.rotationLock( modNode, True )
    place.scaleLock( modNode, True )
    # add attrs
    for attr in attrList:
        if 'Integer' in attr:
            cmds.addAttr( modNode, ln = attr, at = 'long', h = False )
        else:
            cmds.addAttr( modNode, ln = attr, at = 'float', h = False )
        cmds.setAttr( modNode + '.' + attr , k = False )
        cmds.setAttr( modNode + '.' + attr , cb = False )
    #
    cmds.setAttr( modNode + '.' + divdA , cb = True )
    cmds.addAttr( modNode + '.' + divdA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + divsA , cb = True )
    cmds.addAttr( modNode + '.' + divsA, e = True, min = 0.001 )
    cmds.setAttr( modNode + '.' + qtntA , cb = True )
    cmds.setAttr( modNode + '.' + rmndDgrsA , cb = True )
    cmds.setAttr( modNode + '.visibility' , k = False )
    cmds.setAttr( modNode + '.visibility' , cb = False )

    # connect inputs
    if objectAttrDvdnd:
        cmds.connectAttr( objectAttrDvdnd, modNode + '.' + divdA )
    else:
        cmds.setAttr( modNode + '.' + divdA, 1 )
    if divisor:
        cmds.setAttr( modNode + '.' + divsA, divisor )
    else:
        cmds.setAttr( modNode + '.' + divsA, 1 )
    # connect output
    if objectAttrRmndr:
        cmds.connectAttr( modNode + '.' + rmndDgrsA, objectAttrRmndr )

    # div , wheel rotation / 360
    ddd = cmds.shadingNode( 'multiplyDivide', au = True, n = name + mod + '__dividendDivisor_div' )
    cmds.setAttr( ddd + '.operation', 2 )  # divide
    cmds.connectAttr( modNode + '.' + divdA, ddd + '.input1X' )
    cmds.connectAttr( modNode + '.' + divsA, ddd + '.input2X' )

    # result
    cmds.connectAttr( ddd + '.outputX', modNode + '.' + rsltA )
    # result integer
    cmds.connectAttr( modNode + '.' + rsltA, modNode + '.' + rsltIntA )

    # remainder part a
    rra = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderRaw_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rra + '.input1' )
    # remainder part b
    rinm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__remainderRaw_mult' )
    cmds.connectAttr( modNode + '.' + rsltIntA, rinm + '.input1' )
    cmds.setAttr( rinm + '.input2', -1 )
    cmds.connectAttr( rinm + '.output', rra + '.input2' )
    # remainder part c
    cmds.connectAttr( rra + '.output', modNode + '.' + rmndA )

    # condition, force remainder to positive part a
    cndtn = cmds.shadingNode( 'condition', au = True, n = name + mod + '__remainderProcess_cnd' )
    cmds.setAttr( cndtn + '.operation', 4 )  # less than
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.firstTerm' )
    cmds.connectAttr( modNode + '.' + rmndA, cndtn + '.colorIfFalseR' )
    # condition true, flip remainder, part b
    rfa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__remainderProcess_add' )
    cmds.setAttr( rfa + '.input2', 1 )
    cmds.connectAttr( modNode + '.' + rmndA, rfa + '.input1' )
    cmds.connectAttr( rfa + '.output', cndtn + '.colorIfTrueR' )
    # condition c, output positive remainder
    cmds.connectAttr( cndtn + '.outColorR', modNode + '.' + rmndPosA )

    # remainder to degrees
    rdm = cmds.createNode( 'multDoubleLinear', name = name + mod + '__remainder_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rdm + '.input1' )
    cmds.connectAttr( modNode + '.' + divsA, rdm + '.input2' )
    cmds.connectAttr( rdm + '.output', modNode + '.' + rmndDgrsA )

    # quotient result minus remainder
    rqa = cmds.createNode( 'addDoubleLinear', name = name + mod + '__quotient_add' )
    cmds.connectAttr( modNode + '.' + rsltA, rqa + '.input1' )
    # remainder part b
    rnm = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + mod + '__quotient_mult' )
    cmds.connectAttr( modNode + '.' + rmndPosA, rnm + '.input1' )
    cmds.setAttr( rnm + '.input2', -1 )
    cmds.connectAttr( rnm + '.output', rqa + '.input2' )
    # remainder part c
    cmds.connectAttr( rqa + '.output', modNode + '.' + qtntA )

    place.cleanUp( modNode, World = True )
    return modNode


def wheel_roll_math( name = 'pathRadius1', distanceObjAttr = 'onPath_front.pathTraveled', radiusObjAttr = 'onPath_front.wheelRadius', outputObjAttr = 'onPath_front.wheelRoll', outputObjModAttr = 'onPath_front.wheelRollModulus' ):
    '''
    create nodes to calculate wheel rotation
    # ( ( $distance / ( pi2 * base_TopGrp.Radius ) ) * 360.0 ) # ROLL FORMULA
    '''
    #
    pi2 = 6.283185
    radiusPi2 = cmds.shadingNode( 'multDoubleLinear', name = name + '__radiusPi2_mult', asUtility = True )
    cmds.setAttr( radiusPi2 + '.input2', pi2 )
    cmds.connectAttr( radiusObjAttr, radiusPi2 + '.input1' )
    #
    radis = cmds.shadingNode( 'multiplyDivide', au = True, n = name + '__distanceTraveled_radiusPi2_div' )
    cmds.setAttr( radis + '.operation', 2 )  # divide
    cmds.connectAttr( distanceObjAttr, radis + '.input1X' )
    cmds.connectAttr( radiusPi2 + '.output', radis + '.input2X' )
    #
    mlt360 = cmds.shadingNode( 'multDoubleLinear', au = True, n = name + '__mlt360_mult' )
    cmds.connectAttr( radis + '.outputX', mlt360 + '.input1' )
    cmds.setAttr( mlt360 + '.input2', 360 )
    # output
    cmds.connectAttr( mlt360 + '.output', outputObjAttr )
    if outputObjModAttr:
        modulus_node( name = name, objectAttrDvdnd = outputObjAttr, objectAttrRmndr = outputObjModAttr, divisor = 360 )

    return [radiusPi2, radis, mlt360]


def deleteAnim( obj = '', attr = '' ):
    '''
    deletes any existing keys
    '''
    ac.deleteAnim2( obj, attrs = [attr] )


def _____________RIBBONS():
    pass


def ribbon_path( name = '', layers = 3, length = 10, width = 1, X = 2.0, ctrl_shape = 'diamond_ctrl', reverse = False, prebuild = False, prebuild_type = 4, ):
    '''
    
    '''
    if prebuild:
        PreBuild = place.rigPrebuild( Top = prebuild_type, Ctrl = True, SknJnts = False, Geo = False, World = True, Master = True, OlSkool = False, Size = 20 * X )
        # return
        #
        '''
        CHARACTER = PreBuild[0]
        CONTROLS = PreBuild[1]
        WORLD_SPACE = PreBuild[2]
        MasterCt = PreBuild[3]
        '''

    # layers
    layers_built = []
    colors = [ 'lightYellow', 'lightBlue', 'pink', 'hotPink', 'purple']
    rows = 2
    i = 0  # layer
    j = 0  # colors
    while i < layers:
        _name = 'layer_' + pad_number( i = i )
        if i == 0:
            lyrs = ribbon_layer( name = _name, rows = rows, length = length, width = width, color = colors[j], X = X, ctrl_shape = ctrl_shape, reverse = reverse, parent_layer = None, master = MASTERCT(), layer = i )
            layers_built.append( lyrs )
        else:
            lyrs = ribbon_layer( name = _name, rows = rows, length = length, width = width, color = colors[j], X = X, ctrl_shape = ctrl_shape, reverse = reverse, parent_layer = layers_built[i - 1], master = MASTERCT(), layer = i )
            layers_built.append( lyrs )
        # counters
        print( i, rows )
        rows = ( rows * 2 ) - 1
        i = i + 1
        if j == 4:
            j = 0
        else:
            j = j + 1

    #
    path_grp = cmds.group( em = True, n = name + '_ribbon_path_rig_Grp' )
    cmds.parent( path_grp, WORLD_SPACE() )
    # path curve
    curve = build_curve( length = length, cvs = len( layers_built[-1].controls ), layer = layers, reverse = reverse )
    cmds.setAttr( curve + '.template', 1 )
    cmds.parent( curve, path_grp )
    #
    clusters = place.clstrOnCV( curve, 'layer_' + pad_number( i = layers ) + '_Clstr' )
    cGrp = 'clstr_' + pad_number( i = layers ) + '_Grp'
    cmds.group( clusters, n = cGrp, w = True )
    cmds.setAttr( cGrp + '.visibility', 0 )
    cmds.parent( cGrp, path_grp )
    # path curve_up, up vectors
    curve_up = cmds.duplicate( curve, name = curve + '_up' )[0]
    cmds.setAttr( curve_up + '.template', 1 )
    cmds.setAttr( curve_up + '.ty', width * 3 )
    #
    clusters_up = place.clstrOnCV( curve_up, 'layer_' + pad_number( i = layers ) + '_up_Clstr' )
    cGrpUp = 'clstrUp_' + pad_number( i = layers ) + '_Grp'
    cmds.group( clusters_up, n = cGrpUp, w = True )
    cmds.setAttr( cGrpUp + '.visibility', 0 )
    cmds.parent( cGrpUp, path_grp )

    f = 0
    for control in layers_built[-1].controls:
        cmds.parentConstraint( control[4], clusters[f], mo = True )
        cmds.parentConstraint( control[4], clusters_up[f], mo = True )
        f += 1

    ##### non functional control, need to remove from coral snake reference   ######
    # up
    upCnt = place.Controller( place.getUniqueName( 'up' ), 'master', orient = True, shape = 'loc_ctrl', size = length * X, color = 17, setChannels = True, groups = True )
    upCntCt = upCnt.createController()
    place.cleanUp( upCntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCntCt[0] + '.ty', length * 100 )
    cmds.setAttr( upCntCt[0] + '.visibility', 0 )
    cmds.parentConstraint( 'master_Grp', upCntCt[0], mo = True )
    #
    #####

    return curve, curve_up


def ribbon_layer( name = '', rows = 2, length = 120, width = 10, color = '', X = 1, ctrl_shape = 'diamond_ctrl', reverse = False, parent_layer = None, master = [], layer = 0, create_curve = False, create_up_curve = False ):
    '''
    follow formula for how control and follicles increase on layers. ie (controls * 2) -1 = follicles on the same layer. next layer controls match previous follicles
    '''
    xmlt = 0.1
    r_layer = None
    if not parent_layer:
        r_layer = ribbon( name = name, rows = rows, length = length, width = width, color = color, X = X * ( 1 - ( xmlt * ( layer + 1 ) ) ), ctrl_shape = ctrl_shape, reverse = reverse )
    else:
        r_layer = ribbon( name = name, rows = rows, length = length, width = width, color = color, X = X * ( 1 - ( xmlt * ( layer + 1 ) ) ), ctrl_shape = ctrl_shape, reverse = reverse )
        i = 0
        for control in r_layer.controls:
            cmds.parentConstraint( parent_layer.follicles[i], control[0], mo = True )

            #
            i += 1
    #
    place.hijackVis( r_layer.controls_grp, master[2], name = 'ctrlLayer' + str( layer ), suffix = False, default = 0, mode = 'visibility' )

    return r_layer


class Ribbon():
    '''
    
    '''

    def __init__( self, name, length, width, all_grp = '', controls_grp = '', follicles_grp = '', joints_grp = '', controls = [], follicles = [], follicle_shapes = [], joints = [], geo = '', X = 1, ctrl_shape = '', color = '', rows = 2 ):
        self.name = name
        self.length = length
        self.width = width
        self.all_grp = all_grp
        self.controls_grp = controls_grp
        self.follicles_grp = follicles_grp
        self.joints_grp = joints_grp
        self.controls = controls
        self.follicles = follicles
        self.follicle_shapes = follicle_shapes
        self.joints = joints
        self.geo = geo
        self.X = X
        self.ctrl_shape = ctrl_shape
        self.color = color
        self.rows = rows


def ribbon( name = '', rows = 2, length = 120, width = 10, color = '', X = 1, ctrl_shape = 'diamond_ctrl', reverse = False, create_curve = False, create_up_curve = False ):
    '''
    ribbon
    maybe add a curve to each layer for visual reference
    '''
    # TODO: if rows == 2 aim at each end
    #
    length_ratio = length / width
    ribn = cmds.nurbsPlane( p = [0, 0, length / -2], ax = [0, 1, 0], w = width, lr = length_ratio , d = 3, u = 1, v = rows - 1, n = name + '_ribbon' )[0]
    cmds.setAttr( ribn + '.v', 0 )
    cmds.setAttr( ribn + '.template', 1 )
    cmds.select( ribn )
    mel.eval( 'DeleteHistory;' )
    # print( ribn )
    ribn_shape = cmds.listRelatives( ribn, s = True )[0]
    cmds.rotate( 0, 0, 90, ribn )
    # return
    a_grp = cmds.group( em = True, n = name + '_ribbon_Grp' )
    f_grp = cmds.group( em = True, n = name + '_follicle_Grp' )
    j_grp = cmds.group( em = True, n = name + '_follicleJnt_Grp' )
    cmds.parent( f_grp, a_grp )
    cmds.parent( j_grp, a_grp )
    cmds.parent( ribn, a_grp )
    cmds.setAttr( a_grp + '.v', 0 )
    cmds.setAttr( f_grp + '.v', 0 )
    cmds.setAttr( j_grp + '.v', 0 )
    #
    c_grp = cmds.group( em = True, n = name + '_ribbonControl_Grp' )
    try:
        cmds.parent( c_grp, CONTROLS() )
        cmds.parent( a_grp, WORLD_SPACE() )
    except:
        pass
    #
    joints = []
    follicles = []
    follicle_shapes = []
    controls = []
    length_fraction = 0
    follicle_amount = ( rows * 2 ) - 1
    step = length / ( follicle_amount - 1 )
    step = step / length  # normalize to 0-1
    # print( step )
    follicle_only = False
    i = 0  # follicles
    j = 0  # joints / controls
    for i in range( follicle_amount ):
        #
        fol_shape = cmds.createNode( 'follicle', n = name + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( i ) ) + '_follicleShape' )
        follicle_shapes.append( fol_shape )
        fol = cmds.listRelatives( fol_shape, p = True )[0]
        follicles.append( fol )
        cmds.parent( fol, f_grp )
        cmds.setAttr( fol + '.simulationMethod', 0 )
        # cmds.makeIdentity( 'spineNurbsPlane', apply = True, t = 1, r = 1, s = 1, n = 0 )
        # return
        cmds.connectAttr( fol_shape + '.outRotate', fol + '.rotate', f = True )
        cmds.connectAttr( fol_shape + '.outTranslate', fol + '.translate' )
        cmds.connectAttr( ribn_shape + '.worldMatrix', fol_shape + '.inputWorldMatrix' )
        cmds.connectAttr( ribn_shape + '.local', fol_shape + '.inputSurface' )

        cmds.setAttr( fol_shape + '.parameterV', length_fraction )
        cmds.setAttr( fol_shape + '.parameterU', 0.5 )
        length_fraction = length_fraction + step

        if not follicle_only:
            # joints
            cmds.select( fol )
            jnt = place.joint( order = 0, jntSuffix = 'tmp', pad = 2, rpQuery = True, radius = 1.0 )[0]
            jnt = cmds.rename( jnt, name + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( j ) ) + '_follicleControlJnt' )
            cmds.parent( jnt , j_grp )
            joints.append( jnt )
            # print( j )

            # controls
            n = name + '_point_' + str( ( '%0' + str( 2 ) + 'd' ) % ( j ) )
            c_Ct = place.Controller2( n, jnt, True, ctrl_shape, X * 9, 12, 8, 1, ( 0, 0, 1 ), True, True, colorName = color ).result
            cmds.parent( c_Ct[0], c_grp )
            cmds.parentConstraint( c_Ct[4], jnt, mo = True )
            controls.append( c_Ct )
            #
            if cmds.objExists( MASTERCT()[4] ):
                if j > 0:
                    place.parentSwitch( 
                        name = c_Ct[2],
                        Ct = c_Ct[2],
                        CtGp = c_Ct[1],
                        TopGp = c_Ct[0],
                        ObjOff = c_Ct[0],
                        ObjOn = controls[j - 1][4],
                        Pos = False,
                        Ornt = False,
                        Prnt = True,
                        OPT = True,
                        attr = 'fk',
                        w = 0.0 )
                else:
                    cmds.parentConstraint( MASTERCT()[4], c_Ct[0], mo = True )
            #
            follicle_only = True
            j += 1
        else:
            follicle_only = False

        #
        i += 1

    #
    skin_ribbon( joints = joints, geo = ribn )

    #
    ribbon_class = Ribbon( name, length, width, a_grp, c_grp, f_grp, j_grp, controls, follicles, follicle_shapes, joints, ribn, X, ctrl_shape, color, rows )
    return ribbon_class


def skin_ribbon( joints = [], geo = '' ):
    '''
    skin object
    '''

    cmds.select( joints )
    cmds.select( geo, add = True )
    # sknClstr = mel.eval( 'newSkinCluster "-bindMethod 1 -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 0.1 -rui true,multipleBindPose,1";' )[0]
    sknClstr = mel.eval( 'newSkinCluster "-toSelectedBones -bindMethod 0  -normalizeWeights 1 -weightDistribution 0 -mi 1 -omi true -dr 6 -rui false  , multipleBindPose, 0";' )[0]
    cmds.setAttr( sknClstr + '.skinningMethod', 1 )
    return sknClstr

'''
# path rig
import webrImport as web
ump = web.mod('universalMotionPath')
ump.path2()

'''
