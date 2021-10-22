import os

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web
#
# web
ui = web.mod( 'atom_ui_lib' )

# place Clusters on CV derived from 'curve' variable
# curve
# curve from which to make clusters
# clstrSuffix
# suffix for cluster


def pad_number( i = 1, pad = 2 ):
    '''
    given i and pad, return padded string
    '''
    return str( ( '%0' + str( pad ) + 'd' ) % ( i ) )


def clstrOnCV( curve, clstrSuffix ):
    clstr = []
    i = 0
    num = cmds.getAttr( ( curve + '.cv[*]' ) )
    for item in num:
        c = cmds.cluster( 
            ( curve + '.cv[' + str( i ) + ']' ), n = ( clstrSuffix + pad_number( i ) ), envelope = True )[1]
        i = i + 1
        clstr.append( c )
    return clstr

# places curve on points derived from selection


def curve( name, points, d = 2 ):
    '''\n
    name = name...
    points = list of objects from which xfrom can be derived
    '''
    pos = []
    if len( points ) > 2:
        for item in points:
            x = cmds.xform( item, q = True, t = True, ws = True )
            pos.append( x )
        curve = cmds.curve( p = pos, name = ( name ), d = d )
        return curve
    else:
        mel.eval( 'warning \"' + '////... select 3 objects ...////' + '\";' )
        return None

# place joints on positions derived from selection
# order(boolean) = placement order
# 0 = first to last selected object
# 1 = last to first selected object
# jntSuffix
# suffix for joints


def jointChain( suffix = 'chain', pad = 2, length = 1, amount = 30, radius = 0.4, dbl = 0 ):
    '''
    creates joint chain down Z axis
    dbl = make a double joint every nth joint
    '''
    jnt = []
    cmds.select( cl = True )
    i = 0
    d = 1  # double trigger
    l = 0  # letter label
    while i <= amount:
        letter = chr( ord( 'a' ) + l ).upper()
        pos = [0, 0, length * i]

        if dbl and dbl == d and i != amount:
            plc = cmds.joint( name = ( suffix + letter + '_jnt_' + str( ( '%0' + str( pad ) + 'd' ) % ( d ) ) ), p = pos )
            jnt.append( plc )
            cmds.setAttr( plc + '.radius', radius * 3 )
            d = 1
            l = l + 1
            letter = chr( ord( 'a' ) + l ).upper()
        #
        if dbl:
            plc = cmds.joint( name = ( suffix + letter + '_jnt_' + str( ( '%0' + str( pad ) + 'd' ) % ( d ) ) ), p = pos )
            jnt.append( plc )
        else:
            plc = cmds.joint( name = ( suffix + '_jnt_' + str( ( '%0' + str( pad ) + 'd' ) % ( i ) ) ), p = pos )
            jnt.append( plc )
        cmds.setAttr( plc + '.radius', radius )
        # jnt.append( plc )
        i = i + 1
        if dbl and dbl != d:
            d = d + 1
    return jnt


def joint( order, jntSuffix, pad = 2, rpQuery = True, radius = 0.4 ):
    sel = cmds.ls( sl = True, fl = True, l = True )
    if len( sel ) > 0:
        if order == 0:
            jnt = []
            cmds.select( cl = True )
            i = 1
            for item in sel:
                if rpQuery == True:
                    pos = cmds.xform( item, q = True, rp = True, ws = True )
                else:
                    pos = cmds.xform( item, q = True, t = True, ws = True )
                plc = cmds.joint( 
                    name = ( jntSuffix + '_' + str( ( '%0' + str( pad ) + 'd' ) % ( i ) ) ), p = pos )
                cmds.setAttr( plc + '.radius', radius )
                jnt.append( plc )
                i = i + 1
            cmds.select( sel )
            return jnt
        elif order == 1:
            rvrsSel = []
            # (reverse order loop - range(size of(array),stop@,increment by)
            for i in range( len( sel ), 0, -1 ):
                rvrsSel.append( sel[i - 1] )
            sel = list( rvrsSel )
            jnt = []
            cmds.select( cl = True )
            for item in sel:
                if rpQuery == True:
                    pos = cmds.xform( item, q = True, rp = True, ws = True )
                else:
                    pos = cmds.xform( item, q = True, t = True, ws = True )
                plc = cmds.joint( name = ( jntSuffix + '#' ), p = pos )
                cmds.setAttr( plc + '.radius', radius )
                jnt.append( plc )
            cmds.select( sel )
            return jnt
    else:
        plc = cmds.joint( name = jntSuffix, p = [0, 0, 0] )
        cmds.setAttr( plc + '.radius', radius * 3 )
        # mel.eval( 'warning \"' + '////... select at least one object ...////' + '\";' )
        return [plc]

# place locators on positions derived from selection
# locSuffix
# suffix for spaceLocators


def loc( locSuffix, obj = None ):
    sel = []
    if obj == None:
        sel = cmds.ls( sl = True, fl = True, l = True )
    else:
        sel.append( obj )
    if len( sel ) > 0:
        loc = []
        cmds.select( cl = True )
        for item in sel:
            pos = cmds.xform( item, q = True, t = True, ws = True )
            rot = cmds.xform( item, q = True, ro = True, ws = True )
            n = cmds.spaceLocator( name = locSuffix )[0]
            cmds.xform( n, t = ( pos ), ro = ( rot ) )
            loc.append( n )
        cmds.select( sel )
        # returns list
        return loc
    else:
        mel.eval( 'warning \"' +
                 '////... select at least one object ...////' + '\";' )
        return None

# place nulls on positions derived from selection
# nllSuffix
# suffix for null


def null( nllSuffix, order = None ):
    sel = cmds.ls( sl = True, fl = True, l = True )
    if len( sel ) > 0:
        null = []
        cmds.select( cl = True )
        for item in sel:
            pos = cmds.xform( item, q = True, rp = True, ws = True )
            rot = cmds.xform( item, q = True, ro = True, ws = True )
            n = cmds.group( name = nllSuffix, em = True )
            if order != None:
                cmds.xform( n, roo = order )
            cmds.xform( n, t = pos, ro = rot )
            null.append( n )
        cmds.select( sel )
        return null

    else:
        mel.eval( 'warning \"' +
                 '////... select at least one object ...////' + '\";' )
        return None


def circle( name = '', obj = '', shape = '', size = 1.0, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), orient = True, colorName = None , radius = 1.0 ):
    '''
    place circle
    name     = name of circle
    obj      = object whose position to match
    shape    = shape of circle to import(name of text file)
    sections = number of CVs
    degree   = Linear(1) or Cubic(3) ,has to be int
    normal   = plane on which to build circle
    '''
    if colorName:
        color = colorDict()[colorName]
    # path = os.path.expanduser('~') + '/GitHub/controlShapes/'
    path = None
    Circle = []
    if type( obj ) != list:
        pos = cmds.xform( obj, q = True, rp = True, ws = True )
        rot = cmds.xform( obj, q = True, ro = True, ws = True )
        n = cmds.circle( name = name, center = ( 0, 0, 0 ), normal = normal, sweep = 360,
                        radius = radius, degree = degree, sections = sections, constructionHistory = 1 )[0]
        cmds.xform( n, t = pos )
        if orient:
            cmds.xform( n, ro = rot )
        else:
            print( 'no orient' )
        Circle.append( n )
        # import shape
        if shape:
            cmds.select( n )
            ui.importCurveShape( shape, path, size, color )
        return Circle
    elif len( obj ) > 0:
        for item in obj:
            pos = cmds.xform( item, q = True, rp = True, ws = True )
            rot = cmds.xform( item, q = True, ro = True, ws = True )
            n = cmds.circle( name = name, center = ( 0, 0, 0 ), normal = normal, sweep = 360,
                            radius = radius, degree = degree, sections = sections, constructionHistory = 1 )[0]
            cmds.xform( n, t = pos, ro = rot )
            Circle.append( n )
            if shape:
                cmds.select( n )
                ui.importCurveShape( shape, path, size, color )
        return Circle

    else:
        mel.eval( 
            'warning \"' + '////... No object specified under \'obj\' variable ...////' + '\";' )
        return None

# Version 2 (no selection required, state object(s) to match as variable "obj")
# place nulls on positions derived from selection
# nllSuffix
# suffix for null


def null2( nllSuffix, obj, orient = True ):
    null = []
    defRoo = 'xyz'
    if type( obj ) != list:
        pos = cmds.xform( obj, q = True, rp = True, ws = True )
        rot = cmds.xform( obj, q = True, ro = True, ws = True )
        n = cmds.group( name = nllSuffix, em = True )
        objRoo = cmds.xform( obj, q = True, roo = True )
        setRotOrderWithXform( n, objRoo )
        cmds.xform( n, t = pos, ro = rot, ws = True )
        setRotOrderWithXform( n, defRoo )
        if orient == False:
            cmds.xform( n, ro = ( 0, 0, 0 ) )
        null.append( n )
        return null
    elif type( obj ) == list:
        for item in obj:
            n = null2( nllSuffix, item, orient )[0]
            null.append( n )
        return null
    else:
        mel.eval( 
            'warning \"' + '////... \"obj\" variable must be a single object or list type ...////' + '\";' )
        return None


def colorDict():
    colors = {'darkRed': 4, 'blue': 6, 'brown': 10, 'red': 13, 'yellow': 17,
              'lightBlue': 18, 'pink': 20, 'lightYellow': 22, 'green': 23,
              'lightBrown': 24, 'purple': 30, 'burgundy': 31}
    return colors


def vector( v = [] ):
    '''
    list to translate direction
    '''
    if v == [1, 0, 0]:
        return '.translateX'
    if v == [0, 1, 0]:
        return '.translateY'
    if v == [0, 0, 1]:
        return '.translateZ'


class Controller():
    # initialize

    def __init__( self, name, obj, orient = True, shape = 'diamond_ctrl',
                 size = 1, color = 8, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True,
                 groups = False, orientCt = False, colorName = None ):
        self.name = name
        self.obj = obj
        self.orient = orient
        self.shape = shape
        self.size = size
        self.color = color
        self.colorName = colorName
        self.sections = sections
        self.degree = degree
        self.normal = normal
        self.setChannels = setChannels
        self.groups = groups
        self.orientCt = orientCt
        self.colors = colorDict()

    # conditions

    def condition( self ):
        if type( self.obj ) == list:
            if len( self.obj ) == 1:
                self.createController()
            else:
                mel.eval( 
                    'warning \"' + '////... \'obj\' variable has to be only item in list ...////' + '\";' )
        elif len( self.obj ) > 0:
            self.createController()
        else:
            mel.eval( 
                'warning \"' + '////... \'obj\' variable can only be one object...////' + '\";' )

    def whatColor( self ):
        if self.colorName:
            self.color = self.colors[self.colorName]

    # create
    def createController( self ):
        self.whatColor()
        ct = circle( self.name, self.obj, self.shape, self.size * ( 0.3 ),
                    self.color, self.sections, self.degree, self.normal )[0]
        ctO = circle( self.name + '_Offset', self.obj, self.shape, self.size *
                     ( 0.25 ), self.color, self.sections, self.degree, self.normal )[0]
        gp = null2( self.name + '_Grp', self.obj )[0]
        if self.groups:
            ctgp = null2( self.name + '_CtGrp', self.obj )[0]
            topgp = null2( self.name + '_TopGrp', self.obj )[0]
            cmds.parent( ct, ctgp )
            cmds.parent( ctgp, topgp )
            if self.setChannels:
                setChannels( ctgp, translate = [False, True], rotate = [False, True], scale = [
                            True, False], visibility = [True, False, False], other = [False, True] )
                setChannels( topgp, translate = [False, True], rotate = [False, True], scale = [
                            True, False], visibility = [True, False, False], other = [False, True] )

        # parent
        cmds.parent( gp, ctO )
        cmds.parent( ctO, ct )
        # align orient query
        if self.orient == False:
            if self.groups == True:
                cmds.setAttr( topgp + '.rotate', 0, 0, 0 )
            else:
                cmds.setAttr( ct + '.rotate', 0, 0, 0 )
        elif self.orient != False and self.orient != True:
            rot = cmds.xform( self.orient, query = True, ws = True, ro = True )
            if self.groups == True:
                cmds.setAttr( topgp + '.rotate', rot[0], rot[1], rot[2] )
            else:
                cmds.setAttr( ct + '.rotate', rot[0], rot[1], rot[2] )
        # align control separately if requested
        if self.orientCt:
            rot = cmds.xform( self.obj, query = True, ws = True, ro = True )
            cmds.xform( ct, ws = True, ro = rot )
        # attrs
        # ct
        attr = 'Offset_Vis'
        addAttribute( ct, 'Offset_Vis', 0, 1, False, 'long' )
        # ctO
        cmds.connectAttr( ct + '.' + attr, ctO + '.visibility' )
        # gp
        # Done
        cmds.select( cl = True )
        if self.setChannels == True:
            setChannels( ct, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [True, False, False], other = [False, True] )
            setChannels( ctO, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [False, False, False], other = [False, True] )
            setChannels( gp, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [True, False, False], other = [False, True] )
            cmds.setAttr( ctO + '.visibility', cb = False )
            i = cmds.getAttr( ctO + '.visibility', cb = True )

        # print( topgp, ctgp, ct, ctO, gp )
        if self.groups == True:
            return topgp, ctgp, ct, ctO, gp
        else:
            return ct, ctO, gp


class Controller2():
    # initialize

    def __init__( self, name, obj, orient = True, shape = 'diamond_ctrl',
                 size = 1, color = 8, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True,
                 groups = False, orientCt = False, colorName = None ):
        #
        self.name = name
        self.obj = obj
        self.orient = orient
        self.shape = shape
        self.size = size
        self.color = color
        self.colorName = colorName
        self.sections = sections
        self.degree = degree
        self.normal = normal
        self.setChannels = setChannels
        self.groups = groups
        self.orientCt = orientCt
        self.result = None
        #
        self.colors = colorDict()
        self.createController()

    # conditions

    def condition( self ):
        if type( self.obj ) == list:
            if len( self.obj ) == 1:
                self.createController()
            else:
                mel.eval( 
                    'warning \"' + '////... \'obj\' variable has to be only item in list ...////' + '\";' )
        elif len( self.obj ) > 0:
            self.createController()
        else:
            mel.eval( 
                'warning \"' + '////... \'obj\' variable can only be one object...////' + '\";' )

    def whatColor( self ):
        if self.colorName:
            self.color = self.colors[self.colorName]

    # create
    def createController( self ):
        self.whatColor()
        ct = circle( self.name, self.obj, self.shape, self.size * ( 0.3 ),
                    self.color, self.sections, self.degree, self.normal )[0]
        ctO = circle( self.name + '_Offset', self.obj, self.shape, self.size *
                     ( 0.25 ), self.color, self.sections, self.degree, self.normal )[0]
        gp = null2( self.name + '_Grp', self.obj )[0]
        if self.groups:
            ctgp = null2( self.name + '_CtGrp', self.obj )[0]
            topgp = null2( self.name + '_TopGrp', self.obj )[0]
            cmds.parent( ct, ctgp )
            cmds.parent( ctgp, topgp )
            if self.setChannels:
                setChannels( ctgp, translate = [False, True], rotate = [False, True], scale = [
                            True, False], visibility = [True, False, False], other = [False, True] )
                setChannels( topgp, translate = [False, True], rotate = [False, True], scale = [
                            True, False], visibility = [True, False, False], other = [False, True] )

        # parent
        cmds.parent( gp, ctO )
        cmds.parent( ctO, ct )
        # align orient query
        if self.orient == False:
            if self.groups == True:
                cmds.setAttr( topgp + '.rotate', 0, 0, 0 )
            else:
                cmds.setAttr( ct + '.rotate', 0, 0, 0 )
        elif self.orient != False and self.orient != True:
            rot = cmds.xform( self.orient, query = True, ws = True, ro = True )
            if self.groups == True:
                cmds.setAttr( topgp + '.rotate', rot[0], rot[1], rot[2] )
            else:
                cmds.setAttr( ct + '.rotate', rot[0], rot[1], rot[2] )
        # align control separately if requested
        if self.orientCt:
            rot = cmds.xform( self.obj, query = True, ws = True, ro = True )
            cmds.xform( ct, ws = True, ro = rot )
        # attrs
        # ct
        attr = 'Offset_Vis'
        addAttribute( ct, 'Offset_Vis', 0, 1, False, 'long' )
        # ctO
        cmds.connectAttr( ct + '.' + attr, ctO + '.visibility' )
        # gp
        # Done
        cmds.select( cl = True )
        if self.setChannels == True:
            setChannels( ct, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [True, False, False], other = [False, True] )
            setChannels( ctO, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [False, False, False], other = [False, True] )
            setChannels( gp, translate = [False, True], rotate = [False, True], scale = [
                        True, False], visibility = [True, False, False], other = [False, True] )
            cmds.setAttr( ctO + '.visibility', cb = False )
            i = cmds.getAttr( ctO + '.visibility', cb = True )

        if self.groups == True:
            self.result = [ topgp, ctgp, ct, ctO, gp]
            return topgp, ctgp, ct, ctO, gp
        else:
            self.result = [ ct, ctO, gp]
            return ct, ctO, gp


def twoJointPV( name, ik, distance = 1, constrain = True, size = 1 ):
    sj = cmds.ikHandle( ik, q = True, sj = True )
    Gp = null2( name + '_PvGrp', sj, False )[0]
    Pv = circle( name + '_PV', sj, 'diamond_ctrl',
                size * 1, 17, 8, 1, ( 0, 0, 1 ) )[0]
    cmds.parent( Pv, Gp )
    X = cmds.getAttr( ik + '.poleVectorX' )
    Y = cmds.getAttr( ik + '.poleVectorY' )
    Z = cmds.getAttr( ik + '.poleVectorZ' )
    cmds.setAttr( Pv + '.translateX', distance * X )
    cmds.setAttr( Pv + '.translateY', distance * Y )
    cmds.setAttr( Pv + '.translateZ', distance * Z )
    if constrain == True:
        cmds.poleVectorConstraint( Pv, ik )
    return Gp, Pv


def controllerDownChain( root, name, pad = 2, base = None, parent = None, shape = 'loc_ctrl',
                        color = 17, size = 10, groups = True, orient = False, suffix = None,
                        scale = True, setChannel = True, clone = False, fk = False ):
    '''\n

    '''
    result = []
    control_chain = []
    clone_chain = []
    cmds.select( root, hi = True )
    sel = cmds.ls( sl = True, typ = 'transform' )
    i = 1
    for obj in sel:
        if pad > 0:
            num = '_' + str( ( '%0' + str( pad ) + 'd' ) % ( i ) )
        else:
            num = ''
        # SUFFIX
        if suffix != None:
            ctrl = Controller( name + num + '_' + suffix, obj, shape = shape,
                              color = color, size = size, groups = groups, orient = orient )
        else:
            ctrl = Controller( name + num, obj, shape = shape,
                              color = color, size = size, groups = groups, orient = orient )
        Control = ctrl.createController()
        control_chain.append( Control )
        # CLONE
        if clone == False:
            cmds.parentConstraint( Control[4], obj, mo = True )
        else:
            clone_parent = null2( Control[2] + '_CloneTopGrp', obj, orient )[0]
            clone_child = null2( Control[2] + '_CloneCtGrp', obj, orient )[0]
            clone_offset = null2( Control[2] + '_CloneOffstGrp', obj, orient )[0]
            cmds.parentConstraint( clone_offset, obj, mo = True )
            clone_set = [clone_parent, clone_child, clone_offset]
            clone_chain.append( clone_set )
            cmds.parent( clone_offset, clone_child )
            cmds.parent( clone_child, clone_parent )
            hijack( clone_offset, Control[3], scale = False, visibility = False )
            hijack( clone_child, Control[2], scale = False, visibility = False )
        # BASE
        if base != None:
            cmds.parentConstraint( base, Control[0], mo = True )
        # PARENT
        if parent != None:
            cmds.parent( Control[0], parent )
        # SETCHANNEL
        if setChannel != True:
            for item in Control:
                setChannels( item, translate = [False, True], rotate = [False, True], scale = [
                            False, True], visibility = [True, False, False] )
        # SCALE
        if scale == True:
            if clone == False:
                hijackScale( obj, Control[2] )
            else:
                hijackScale( obj, clone_child )
                hijackScale( clone_child, Control[2] )
                scaleUnlock( Control[2] )
        i = i + 1
    # FK
    if fk == True:
        num = len( control_chain )
        j = 1
        for item in control_chain:
            if num > j:
                cmds.parent( control_chain[j][0], item[2] )
                cmds.parentConstraint( item[3], control_chain[j][0], mo = True )
                if clone == True:
                    cmds.parent( clone_chain[j][0], clone_chain[j - 1][2] )
            j = j + 1
    return control_chain, clone_chain


def convertFlipValue( flipVar ):
    '''
    
    '''
    flip = flipVar[:]  # duplicate list
    # print( flip, flipVar )
    for i in range( 0, 3, 1 ):
        if flip[i] == 1:
            flip[i] = -1
        else:
            flip[i] = 1
    return flip

# transform[lock, keyable], visibility[set, lock, keyable]


def setChannels( item, translate = [True, True], rotate = [True, True], scale = [True, True], visibility = [True, False, True], other = [False, True] ):
    '''
    Set that state of the items channels\n.
    translate, rotate, scale: [lock, keyable], lock = bool, keyable = bool
    visibility :[set, lock, keyable], set= bool, lock = bool, keyable = bool
    '''
    # translate
    nodeType = cmds.nodeType( item )
    translateList = ['.tx', '.ty', '.tz']
    rotateList = ['.rx', '.ry', '.rz']
    scaleList = ['.sx', '.sy', '.sz']

    if visibility[0]:
        try:
            cmds.setAttr( item + '.visibility', 1 )
        except:
            pass
            # mel.eval('warning \"' + '////... visibility already connected ...////' + '\";')
    else:
        try:
            cmds.setAttr( item + '.visibility', 0 )
        except:
            pass
            # mel.eval('warning \"' + '////... visibility already connected ...////' + '\";')

    if visibility[1] == True:
        cmds.setAttr( item + '.visibility', lock = True )
    else:
        cmds.setAttr( item + '.visibility', lock = False )
    if visibility[2] == True:
        cmds.setAttr( item + '.visibility', k = True )
    else:
        cmds.setAttr( item + '.visibility', k = False, cb = True )

    if nodeType == 'transform':
        if translate[0] == True:
            for attr in translateList:
                cmds.setAttr( item + attr, lock = True )
        else:
            for attr in translateList:
                cmds.setAttr( item + attr, lock = False )

        if translate[1] == True:
            for attr in translateList:
                cmds.setAttr( item + attr, k = True )
        else:
            for attr in translateList:
                cmds.setAttr( item + attr, k = False )

        if scale[0] == True:
            for attr in scaleList:
                cmds.setAttr( item + attr, lock = True )
        else:
            for attr in scaleList:
                cmds.setAttr( item + attr, lock = False )

        if scale[1] == True:
            for attr in scaleList:
                cmds.setAttr( item + attr, k = True )
        else:
            for attr in scaleList:
                cmds.setAttr( item + attr, k = False )

        if rotate[0] == True:
            for attr in rotateList:
                cmds.setAttr( item + attr, lock = True )
        else:
            for attr in rotateList:
                cmds.setAttr( item + attr, lock = False )

        if rotate[1] == True:
            for attr in rotateList:
                cmds.setAttr( item + attr, k = True )
        else:
            for attr in rotateList:
                cmds.setAttr( item + attr, k = False )

    elif nodeType == 'ikHandle':
        standardAttrList = translateList + scaleList + rotateList
        ikAttrList = ['.pvx', '.pvy', '.pvz', '.off', '.rol', '.twi', '.ikb']
        if other[0] == True:
            for attr in standardAttrList:
                cmds.setAttr( item + attr, lock = False )
            for attr in ikAttrList:
                cmds.setAttr( item + attr, lock = False )

        if other[1] == True:
            for attr in standardAttrList:
                cmds.setAttr( item + attr, k = False )
            for attr in ikAttrList:
                cmds.setAttr( item + attr, k = False )


def distance2Pts( p1, p2 ):
    error = 0
    if len( p1 ) != 3:
        OpenMaya.MGlobal.displayError( 
            'First argument list needs to have three elements...' )
        error = 1
    if len( p2 ) != 3:
        OpenMaya.MGlobal.displayError( 
            'Second argument list needs to have three elements...' )
        error = 1

    if error != 1:
        v = [0, 0, 0]
        v[0] = p1[0] - p2[0]
        v[1] = p1[1] - p2[1]
        v[2] = p1[2] - p2[2]
        distance = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
        from math import sqrt
        distance = sqrt( distance )
        return distance
    else:
        return None


def axisMulti( axis, dis ):

    mvPos = [0, 0, 0]
    mvPos[0] = axis[0] * dis
    mvPos[1] = axis[1] * dis
    mvPos[2] = axis[2] * dis
    return mvPos


def stripUnderscore( name ):
    # check for underscores
    if name[0] == '_':
        name = name[1:]
    if name[-1] == '_':
        name = name[:-1]

    return name


def buildName( prefix = '', suffix = '', name = '' ):
    if prefix.find( ' ' ) > -1:
        prefix = ''
    if suffix.find( ' ' ) > -1:
        suffix = ''

    if len( prefix ) != 0:
        if len( suffix ) != 0:
            name = stripUnderscore( name )
            name = prefix + '_' + name + '_' + suffix
        else:
            name = stripUnderscore( name )
            name = prefix + '_' + name
    else:
        if len( suffix ) != 0:
            name = stripUnderscore( name )
            name = name + '_' + suffix
        else:
            name = stripUnderscore( name )

    return name


def insert( what, where, name, order = None ):
    """Inserts item in selected object(s) hierarchy
    \n
    where:\n
    0 = parent below selected, parent selection children under item\n
    1 = parent above selected, parent selection under item\n
    what:\n
    'null' = null\n
    'loc' = spaceLocator\n
    return = list\n
    """
    # print '____insert'
    sel = cmds.ls( sl = True )
    if sel:
        if len( sel ) == 1:
            sel = sel[0]
            result = []
            relative = []
            exclusion = ['pointConstraint',
                         'orientConstraint', 'parentConstraint']
            obj = None
            if what == 'null':
                if order != None:
                    obj = null( name, order )
                else:
                    obj = null( name )
            elif what == 'loc':
                if order != None:
                    obj = loc( name, order )[0]
                else:
                    obj = loc( name )[0]

            else:
                mel.eval( 
                    'warning \"' + '////...  -what-  has two options: \'loc\' or \'null\' ...////' + '\";' )
            if obj:
                # above
                if where == 1:
                    prnt = cmds.listRelatives( 
                        sel, parent = True, typ = 'transform' )
                    # if parent of item exists (middle of chain)
                    if prnt:
                        prnt = prnt[0]
                        relative.append( prnt )
                        # parent obj under parent of item
                        cmds.parent( obj, prnt )
                        # parent item under obj
                        cmds.parent( sel, obj )
                    # if item has no parents (top of chain)
                    else:
                        # parent item under obj
                        cmds.parent( sel, obj )
                # below
                else:
                    child = cmds.listRelatives( 
                        sel, children = True, typ = 'transform' )
                    # if sel has children (middle of chain)
                    if child:
                        for chld in child:
                            if cmds.nodeType( chld ) in exclusion:
                                child.remove( chld )
                        relative.append( child )
                        # parent obj under item
                        cmds.parent( obj, sel )
                        # parent child(s) under obj
                        for item in child:
                            cmds.parent( item, obj )
                    # if item has no children (bottom of chain)
                    else:
                        # parent obj under item
                        cmds.parent( obj, sel )
                result.append( obj )
                return result
            else:
                print( ' NO OBJ______' )
    else:
        mel.eval( 'warning \"' +
                 '////... select at least one object ...////' + '\";' )
        return None


def addAttribute( objList, attrList, minimum, maximum, keyable, attrType ):
    """
    #\n
    objList = object
    attrList = list of attributes to add
    minimum = minimum value to set
    maximum = maximum value to set
    keyable = True or False
    attrType = type of value (int, float, long, enum, bool...)
    """
    if type( objList ) != list:
        if type( attrList ) != list:
            if not cmds.attributeQuery( attrList, node = objList, exists = True ):
                cmds.addAttr( objList, ln = attrList, at = attrType,
                             min = minimum, max = maximum, h = False )
                cmds.setAttr( ( objList + '.' + attrList ), cb = True )
                cmds.setAttr( ( objList + '.' + attrList ), k = keyable )
        else:
            for attr in attrList:
                if not cmds.attributeQuery( attr, node = objList, exists = True ):
                    cmds.addAttr( objList, ln = attr, at = attrType,
                                 min = minimum, max = maximum )
                    cmds.setAttr( ( objList + '.' + attr ), cb = True )
                    cmds.setAttr( ( objList + '.' + attr ), k = keyable )

    elif len( objList ) > 0:
        if len( attrList ) > 0:
            for obj in objList:
                if type( attrList ) != list:
                    if not cmds.attributeQuery( attrList, node = obj, exists = True ):
                        cmds.addAttr( obj, ln = attrList, at = attrType,
                                     min = minimum, max = maximum )
                        cmds.setAttr( ( obj + '.' + attrList ), cb = True )
                        cmds.setAttr( ( obj + '.' + attrList ), k = keyable )
                else:
                    for attr in attrList:
                        if not cmds.attributeQuery( attr, node = obj, exists = True ):
                            cmds.addAttr( obj, ln = attr, at = attrType,
                                         min = minimum, max = maximum )
                            cmds.setAttr( ( obj + '.' + attr ), cb = True )
                            cmds.setAttr( ( obj + '.' + attr ), k = keyable )

        else:
            mel.eval( 
                'warning \"' + '////... Second argument -attrList- is empty...////' + '\";' )
    else:
        mel.eval( 'warning \"' + '////... First argument -objList- is of the wrong type. List or String is expected...////' + '\";' )


def hijackVis( obj1, obj2, name = '', suffix = True, default = None, mode = 'visibility' ):
    '''\n
    Hijacks and converts visibility attribute from boolean to 0-1 base
    obj1     = slave\n
    obj2     = master\n
    name     = new name of attribute being hijacked
    suffix   = suffix string of name
    default  = value, 0(hidden) or 1(visible)
    suffix   = suffix string to new attr
    mode     = 'visibility', 'dispGeometry'
    '''
    # create suffix
    if suffix == True:
        suffix = name + '_Vis'
        addAttribute( obj2, suffix, 0, 1, False, 'long' )
        cmds.connectAttr( obj2 + '.' + suffix, obj1 + '.' + mode )
    else:
        # OLD elif suffix == False:
        suffix = name
        if cmds.attributeQuery( suffix, node = obj2, ex = True ) == True:
            cmds.connectAttr( obj2 + '.' + suffix, obj1 + '.' + mode )
        else:
            addAttribute( obj2, suffix, 0, 1, False, 'long' )
            cmds.connectAttr( obj2 + '.' + suffix, obj1 + '.' + mode )
    if default != None:
        cmds.setAttr( obj2 + '.' + suffix, default )
    vis = obj2 + '.' + suffix
    return vis


def hijackAttrs( obj1, obj2, attrOrig, attrNew, set = False, default = None, force = True ):
    """\n
    obj1     = slave\n
    obj2     = master\n
    attrOrig = name of attr getting hijacked on obj1\n
    attrNew  = name of attr hijacking on obj2\n
    """
    ENM = None
    SMIN = None
    SMAX = None
    MIN = None
    MAX = None
    # collect custom attrs from obj1
    K = cmds.getAttr( obj1 + '.' + attrOrig, k = True )
    TYP = cmds.getAttr( obj1 + '.' + attrOrig, typ = True )
    if TYP == 'enum':
        ENM = cmds.attributeQuery( attrOrig, node = obj1, le = True )[0]
    if cmds.attributeQuery( attrOrig, node = obj1, sme = True ) == 1:
        SMIN = cmds.attributeQuery( attrOrig, node = obj1, smn = True )[0]
        # print SMIN
    if cmds.attributeQuery( attrOrig, node = obj1, sme = True ) == 1:
        SMAX = cmds.attributeQuery( attrOrig, node = obj1, smx = True )[0]
        # print SMAX
    if cmds.attributeQuery( attrOrig, node = obj1, mne = True ) == 1:
        MIN = cmds.attributeQuery( attrOrig, node = obj1, min = True )[0]
        # print MIN
    if cmds.attributeQuery( attrOrig, node = obj1, mxe = True ) == 1:
        MAX = cmds.attributeQuery( attrOrig, node = obj1, max = True )[0]
        # print MAX
    L = cmds.getAttr( obj1 + '.' + attrOrig, l = True )
    CB = cmds.getAttr( obj1 + '.' + attrOrig, cb = True )
    V = cmds.getAttr( obj1 + '.' + attrOrig )
    attrState = attrOrig, K, TYP, MIN, MAX, L, CB, V, ENM

    # recreate attrs on obj2 from obj1, connect attrs
    if TYP == 'enum':
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2, ln = attrNew, k = K, at = TYP, en = ENM )
            cmds.setAttr( obj2 + '.' + attrNew, V )
    else:
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2, ln = attrNew, k = K, at = TYP )
    if SMIN != None:
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2 + '.' + attrNew, e = True, smn = SMIN )
    if SMAX != None:
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2 + '.' + attrNew, e = True, smx = SMAX )
    if MIN != None:
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2 + '.' + attrNew, e = True, min = MIN )
    if MAX != None:
        if not cmds.attributeQuery( attrNew, node = obj2, exists = True ):
            cmds.addAttr( obj2 + '.' + attrNew, e = True, max = MAX )
    cmds.setAttr( obj2 + '.' + attrNew, l = L )
    if K == False:
        cmds.setAttr( obj2 + '.' + attrNew, cb = CB )
    cmds.setAttr( obj2 + '.' + attrNew, V )

    # connect attr
    if not force:
        cmds.connectAttr( obj2 + '.' + attrNew, obj1 + '.' + attrOrig )
    else:
        hijackForceAttr( name = attrOrig, objAttr1 = ( 
            obj1 + '.' + attrOrig ), objAttr2 = ( obj2 + '.' + attrNew ) )

    # override keyable
    if set != False:
        cmds.setAttr( obj2 + '.' + attrNew, k = False )
        cmds.setAttr( obj2 + '.' + attrNew, cb = True )
    if default != None:
        cmds.setAttr( obj2 + '.' + attrNew, default )
    attr = obj2 + '.' + attrNew
    return attr


def hijackCustomAttrs( obj1, obj2 ):
    """\n
    obj1 = slave\n
    obj2 = master\n
    format = list [object] [attr, keyable, type, min, max, lock, channelBox, [enums]]\n
    """
    UsrAttr = cmds.listAttr( obj1, ud = True )
    hAttrs = []
    ENM = []
    # collect custom attrs from obj1
    for attr in UsrAttr:
        K = cmds.getAttr( obj1 + '.' + attr, k = True )
        TYP = cmds.getAttr( obj1 + '.' + attr, typ = True )
        if TYP == 'enum':
            ENM = cmds.attributeQuery( attr, node = obj1, le = True )[0]
        if cmds.attributeQuery( attr, node = obj1, mne = True ) == 1:
            MIN = cmds.attributeQuery( attr, node = obj1, min = True )[0]
        else:
            MIN = None
        if cmds.attributeQuery( attr, node = obj1, mxe = True ) == 1:
            MAX = cmds.attributeQuery( attr, node = obj1, max = True )[0]
        else:
            MAX = None
        L = cmds.getAttr( obj1 + '.' + attr, l = True )
        CB = cmds.getAttr( obj1 + '.' + attr, cb = True )
        V = cmds.getAttr( obj1 + '.' + attr )
        attrState = attr, K, TYP, MIN, MAX, L, CB, V, ENM
        hAttrs.append( attrState )
    # recreate attrs on obj2 from obj1, connect attrs
    for i in range( 0, len( hAttrs ), 1 ):
        if hAttrs[i][2] == 'enum':
            cmds.addAttr( obj2, ln = hAttrs[i][0], k = hAttrs[i]
                         [1], at = hAttrs[i][2], en = hAttrs[i][8] )
            cmds.setAttr( obj2 + '.' + hAttrs[i][0], hAttrs[i][7] )
        else:
            cmds.addAttr( obj2, ln = hAttrs[i][0],
                         k = hAttrs[i][1], at = hAttrs[i][2] )
        if hAttrs[i][3] != None:
            cmds.addAttr( obj2 + '.' + hAttrs[i][0], e = True, min = hAttrs[i][3] )
        if hAttrs[i][4] != None:
            cmds.addAttr( obj2 + '.' + hAttrs[i][0], e = True, max = hAttrs[i][4] )
        cmds.setAttr( obj2 + '.' + hAttrs[i][0], l = hAttrs[i][5] )
        if hAttrs[i][1] == False:
            cmds.setAttr( obj2 + '.' + hAttrs[i][0], cb = hAttrs[i][6] )
        cmds.setAttr( obj2 + '.' + hAttrs[i][0], hAttrs[i][7] )

    for attr in UsrAttr:
        cmds.connectAttr( obj2 + '.' + attr, obj1 + '.' + attr )


def hijackForceAttr( name = '', objAttr1 = '', objAttr2 = '', objAttr3 = '' ):
    '''
    objAttr1 = slave
    objAttr2 = master
    if slave has pre-exisitng incoming connection, insert add node and pipe in master value
    '''
    if not objAttr3:
        cnct = cmds.listConnections( 
            objAttr1, source = True, destination = False, plugs = True )
        # print cnct, '__________'
        if cnct:
            if len( cnct ) == 1:
                objAttr3 = cnct[0]
            else:
                return None
        else:
            cmds.connectAttr( objAttr2, objAttr1 )
            return None
    add = cmds.createNode( 'addDoubleLinear', n = name + '_MergeAttrs' )
    cmds.connectAttr( objAttr3, add + '.input1', f = True )
    cmds.connectAttr( objAttr2, add + '.input2' )
    #
    # cmds.connectAttr(add + '.output', objAttr1, f=True)
    # necessary for scale type attr, need to start at a value of 1
    addScale = cmds.createNode( 'addDoubleLinear', n = name + '_MergeScaleAttrs' )
    cmds.setAttr( addScale + '.input2', -1.0 )
    cmds.connectAttr( add + '.output', addScale + '.input1', f = True )
    cmds.connectAttr( addScale + '.output', objAttr1, f = True )


def hijackHybridScale( obj1 = '', obj2 = '', lengthAttr = 'scaleZ', attrPrefix = '', attrSuffix = '', connectExisting = False ):
    '''
    obj1 = slave
    obj2 = master
    lengthAttr = given attr is used as length scale
    remaining scales are combined to control girth of object
    '''
    # find girth attrs
    girthAttrs = []
    if lengthAttr == 'scaleX':
        girthAttrs = ['scaleY', 'scaleZ']
    elif lengthAttr == 'scaleY':
        girthAttrs = ['scaleX', 'scaleZ']
    else:
        girthAttrs = ['scaleX', 'scaleY']
    # connects
    length = attrPrefix + 'Length' + attrSuffix
    girth = attrPrefix + 'Girth' + attrSuffix
    if not cmds.attributeQuery( length, node = obj2, exists = True ):
        hijackAttrs( obj1, obj2, attrOrig = lengthAttr,
                    attrNew = length, set = False, default = None )
    else:
        if connectExisting is True:
            cmds.connectAttr( obj2 + '.' + length, obj1 + '.' + lengthAttr )
    if not cmds.attributeQuery( girth, node = obj2, exists = True ):
        hijackAttrs( 
            obj1, obj2, attrOrig = girthAttrs[0], attrNew = girth, set = False, default = None )
        # cmds.connectAttr(obj2 + '.' + girth, obj1 + '.' + girthAttrs[1])
        #
        hijackForceAttr( name = girthAttrs[1], objAttr1 = ( 
            obj1 + '.' + girthAttrs[1] ), objAttr2 = ( obj2 + '.' + girth ) )
    else:
        if connectExisting is True:
            # cmds.connectAttr(obj2 + '.' + girth, obj1 + '.' + girthAttrs[0])
            # cmds.connectAttr(obj2 + '.' + girth, obj1 + '.' + girthAttrs[1])
            #
            hijackForceAttr( name = girthAttrs[0], objAttr1 = ( 
                obj1 + '.' + girthAttrs[0] ), objAttr2 = ( obj2 + '.' + girth ) )
            hijackForceAttr( name = girthAttrs[1], objAttr1 = ( 
                obj1 + '.' + girthAttrs[1] ), objAttr2 = ( obj2 + '.' + girth ) )


def guideLine( obj1, obj2, Name = 'guide' ):
    """\n
    Connects 2 objects with curve\n
    Create curve with 2 points\n
    pointConstrain cv[0] to obj1, cv[1] to obj2\n
    """
    # clusters dont seem to track well
    # USE THIS METHOD: connectAttr locator1.translateZ
    # curveShape1.controlPoints[0].zValue

    result = []
    curveTmp = cmds.curve( d = 1, p = [( 0, 0, 0 ), ( 0, 0, 0 )], k = [0, 1] )
    curve = cmds.rename( curveTmp, ( Name + '_crv#' ) )
    shape = cmds.listRelatives( curve, typ = 'shape' )[0]
    cmds.setAttr( curve + '.overrideEnabled', 1 )
    cmds.setAttr( curve + '.overrideDisplayType', 1 )
    '''
    clstr = clstrOnCV(curve, Name + '___' + obj1 + '___' + obj2)
    cmds.setAttr(clstr[0] + '.visibility', 0)
    cmds.setAttr(clstr[1] + '.visibility', 0)
    cmds.pointConstraint(obj1, clstr[0], mo=False, w=1.0)
    cmds.pointConstraint(obj2, clstr[1], mo=False, w=1.0)
    result.append(curve)
    result.append(clstr)
    '''
    # 1
    loc1 = cmds.spaceLocator( name = Name + '_loc1___' + obj1 + '___' + obj2 )[0]
    cmds.setAttr( loc1 + '.visibility', 0 )
    cmds.connectAttr( loc1 + '.translateX', shape + '.controlPoints[0].xValue' )
    cmds.connectAttr( loc1 + '.translateY', shape + '.controlPoints[0].yValue' )
    cmds.connectAttr( loc1 + '.translateZ', shape + '.controlPoints[0].zValue' )
    cmds.pointConstraint( obj1, loc1, mo = False, w = 1.0 )
    # 2
    loc2 = cmds.spaceLocator( name = Name + '_loc2___' + obj1 + '___' + obj2 )[0]
    cmds.setAttr( loc2 + '.visibility', 0 )
    cmds.connectAttr( loc2 + '.translateX', shape + '.controlPoints[1].xValue' )
    cmds.connectAttr( loc2 + '.translateY', shape + '.controlPoints[1].yValue' )
    cmds.connectAttr( loc2 + '.translateZ', shape + '.controlPoints[1].zValue' )
    cmds.pointConstraint( obj2, loc2, mo = False, w = 1.0 )
    #
    result.append( curve )
    result.append( [loc1, loc2] )
    return result


def parentSwitch( name, Ct, CtGp, TopGp, ObjOff, ObjOn, Pos = True, Ornt = True, Prnt = True, OPT = True, attr = False, w = 1.0 ):
    """creates auto ankle twist rig with on/off switch
    \n*
    ***Note: Two dedicated groups must be above Ct variable in the same position\n
    ***Dont freeze any associated groups or controllers (ie. Ct, CtGp,TopGp,ObjOff,ObjOn)\n
    ***Make sure rotation orders are the same between objects being constrained (ie. CtGp,TopGp,ObjOff,ObjOn. New groups will inherit order, unless only 'Pos'=True)\n
    name      = prefix to objects created (ie. reverse node)\n
    Ct        = controller to recieve attribute for switch of char\n
    CtGp      = constrained object, typically group above Ct, unless there are multiple switches\n
    TopGp     = group under which parent switching will occur, CtGp is parented under this group\n
    ObjOff    = constraint object for off/0 value, **use a group not controller\n
    ObjOn     = constraint object for on/1 value, **use a group not controller\n
    Pos       = create point switch,  True or False\n
    Ornt      = create orient switch, True or False\n
    Prnt      = create parent switch,  True or False\n
    OPT       = create 'OPTNS' enum attr as separator\n
    attr      = prefix to switch attr, if False no prefix is added, otherwise a string is expected\n
    w         = default weight value of parent\n
    *
    """

    def setRotOrder( obj, rotOrder ):
        cmds.setAttr( obj + '.rotateOrder', rotOrder )

    # make sure rotation orders are the same
    RO = False
    if ( cmds.getAttr( CtGp + '.rotateOrder' ) ) == ( cmds.getAttr( ObjOff + '.rotateOrder' ) ):
        # print CtGp, ObjOff, 'Good'
        if cmds.getAttr( CtGp + '.rotateOrder' ) == cmds.getAttr( ObjOn + '.rotateOrder' ):
            # print CtGp, ObjOn, 'Good'
            RO = cmds.getAttr( CtGp + '.rotateOrder' )
            roD = {0: 'xyz', 1: 'yzx', 2: 'zxy', 3: 'xzy', 4: 'yxz', 5: 'zyx'}
            RO = roD[RO]
            # print RO

    # attrs
    prefix = ''
    if attr != False:
        prefix = attr
    PosOffOn = prefix + 'PositionOffOn'  # attr to switch parent, on 'Obj'
    OrntOffOn = prefix + 'OrientOffOn'  # attr to switch parent, on 'Obj'
    PrntOffOn = prefix + 'ParentOffOn'  # attr to switch parent, on 'Obj'
    Parent = 'Parent'  # enum attr name

    # create 'OPTNS' enum
    if OPT:
        cmds.addAttr( Ct, ln = Parent, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( Ct + '.' + Parent, cb = True )

    # create point switch
    if Pos:
        # create and constrain matching Obj1Gp and Obj2Gp
        PosOffGp = null2( name + '_PosOffGp', Ct )[0]
        PosOnGp = null2( name + '_PosOnGp', Ct )[0]
        cmds.parent( PosOffGp, TopGp )
        cmds.parent( PosOnGp, TopGp )
        cmds.pointConstraint( ObjOff, PosOffGp, w = 1.0, mo = True )
        cmds.pointConstraint( ObjOn, PosOnGp, w = 1.0, mo = True )
        # contrain object with switch constraints
        cmds.addAttr( Ct, ln = PosOffOn, attributeType = 'float',
                     k = True, dv = w, min = 0.0, max = 1.0 )
        SwitchCnst = cmds.pointConstraint( PosOffGp, CtGp, w = 1.0, mo = False )[0]
        cmds.pointConstraint( PosOnGp, CtGp, w = 0.0, mo = False )
        # build switch
        wghtAttr = cmds.listAttr( SwitchCnst, k = True, ud = True )
        revrsPos = cmds.shadingNode( 'reverse', au = True, n = ( name + '_revrsPos' ) )
        cmds.connectAttr( Ct + '.' + PosOffOn, revrsPos + '.inputX' )
        cmds.connectAttr( revrsPos + '.outputX', SwitchCnst + '.' + wghtAttr[0] )
        cmds.connectAttr( Ct + '.' + PosOffOn, SwitchCnst + '.' + wghtAttr[1] )

    # create orient switch
    if Ornt:
        if not RO:
            pass
            # mel.eval('warning \"' + '////... Orient: Rotation Orders dont match. IM OUT!...////' + ' -- ' + CtGp + ' -- ' + ObjOff + ' -- ' + ObjOn + '\";')
            # return None
        # constrain matching Obj1Gp and Obj2Gp
        OrntOffGp = null2( name + '_OrntOffGp', Ct )[0]
        OrntOnGp = null2( name + '_OrntOnGp', Ct )[0]
        setRotOrderWithXform( OrntOffGp, RO )
        setRotOrderWithXform( OrntOnGp, RO )
        cmds.parent( OrntOffGp, TopGp )
        cmds.parent( OrntOnGp, TopGp )
        cmds.orientConstraint( ObjOff, OrntOffGp, w = 1.0, mo = True )
        cmds.orientConstraint( ObjOn, OrntOnGp, w = 1.0, mo = True )
        # contrain object with switch constraints
        cmds.addAttr( Ct, ln = OrntOffOn, attributeType = 'float',
                     k = True, dv = w, min = 0.0, max = 1.0 )
        SwitchCnst = cmds.orientConstraint( OrntOffGp, CtGp, w = 1.0, mo = False )[0]
        cmds.orientConstraint( OrntOnGp, CtGp, w = 0.0, mo = False )
        # build switch
        wghtAttr = cmds.listAttr( SwitchCnst, k = True, ud = True )
        revrsOrnt = cmds.shadingNode( 
            'reverse', au = True, n = ( name + '_revrsOrnt' ) )
        cmds.connectAttr( Ct + '.' + OrntOffOn, revrsOrnt + '.inputX' )
        cmds.connectAttr( revrsOrnt + '.outputX',
                         SwitchCnst + '.' + wghtAttr[0] )
        cmds.connectAttr( Ct + '.' + OrntOffOn, SwitchCnst + '.' + wghtAttr[1] )

    # create parent switch
    if Prnt:
        if not RO:
            pass
            # mel.eval('warning \"' + '////... Parent: Rotation Orders dont match. IM OUT!...////' + ' -- ' + CtGp + ' -- ' + ObjOff + ' -- ' + ObjOn + '\";')
            # return None
        # constrain matching Obj1Gp and Obj2Gp
        PrntOffGp = null2( name + '_PrntOffGp', CtGp )[0]
        PrntOnGp = null2( name + '_PrntOnGp', CtGp )[0]
        setRotOrderWithXform( PrntOffGp, RO )
        setRotOrderWithXform( PrntOnGp, RO )
        cmds.parent( PrntOffGp, TopGp )
        cmds.parent( PrntOnGp, TopGp )
        cmds.parentConstraint( ObjOff, PrntOffGp, w = 1.0, mo = True )
        cmds.parentConstraint( ObjOn, PrntOnGp, w = 1.0, mo = True )
        # contrain object with switch constraints
        cmds.addAttr( Ct, ln = PrntOffOn, attributeType = 'float',
                     k = True, dv = w, min = 0.0, max = 1.0 )
        SwitchCnst = cmds.parentConstraint( PrntOffGp, CtGp, w = 1.0, mo = False )[0]
        cmds.parentConstraint( PrntOnGp, CtGp, w = 0.0, mo = False )
        # build switch
        wghtAttr = cmds.listAttr( SwitchCnst, k = True, ud = True )
        revrsPrnt = cmds.shadingNode( 
            'reverse', au = True, n = ( name + '_revrsPrnt' ) )
        cmds.connectAttr( Ct + '.' + PrntOffOn, revrsPrnt + '.inputX' )
        cmds.connectAttr( revrsPrnt + '.outputX',
                         SwitchCnst + '.' + wghtAttr[0] )
        cmds.connectAttr( Ct + '.' + PrntOffOn, SwitchCnst + '.' + wghtAttr[1] )


def setRotOrder( obj, rotOrder = 2, hier = False ):
    '''\n
    ## Rotate Order = aim vector should be last in rotate hierarchy\n
    ## obj          = object to change rotate order of\n
    ## rotOrder     = rotation order to use, (value range: 0=5)\n
    ## 0 = xyz\n
    ## 1 = yzx\n
    ## 2 = zxy\n
    ## 3 = xzy\n
    ## 4 = yxz\n
    ## 5 = zyx\n
    '''
    if hier:
        transforms = []
        cmds.select( obj, hierarchy = True )
        sel = cmds.ls( sl = True )
        cmds.select( cl = True )
        for item in sel:
            if cmds.nodeType( item ) == 'transform':
                transforms.append( item )
        for item in transforms:
            cmds.setAttr( item + '.rotateOrder', rotOrder )
    else:
        cmds.setAttr( obj + '.rotateOrder', rotOrder )


def setRotOrderWithXform( obj, rotOrder = 'xyz', hier = False ):
    '''\n
    ## Rotate Order = aim vector should be last in rotate hierarchy\n
    ## obj          = object to change rotate order of\n
    ## rotOrder     = String expected of the 6 order types
    '''
    if rotOrder:
        if isinstance( rotOrder, int ):
            roD = {0: 'xyz', 1: 'yzx', 2: 'zxy', 3: 'xzy', 4: 'yxz', 5: 'zyx'}
            rotOrder = roD[rotOrder]
        if hier:
            transforms = []
            cmds.select( obj, hierarchy = True )
            sel = cmds.ls( sl = True )
            cmds.select( cl = True )
            for item in sel:
                if cmds.nodeType( item ) == 'transform':
                    transforms.append( item )
            for item in transforms:
                cmds.xform( item, p = True, roo = rotOrder )
        else:
            cmds.xform( obj, p = True, roo = rotOrder )


def hijackScale( obj1, obj2 ):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    for s in scl:
        cnct = cmds.listConnections( 
            obj1 + s, source = True, destination = False, plugs = True )
        if cnct:
            if len( cnct ) == 1:
                hijackForceAttr( name = 'scale', objAttr1 = obj1,
                                objAttr2 = obj2, objAttr3 = cnct[0] )
        else:
            # print cnct, '_____cnct'
            cmds.connectAttr( obj2 + s, obj1 + s )


def hijackScaleMerge( obj1, obj2, mergeAttr = 'Scale' ):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    addAttribute( objList = [obj2], attrList = [mergeAttr], minimum = 0.0,
                 maximum = 1000.0, keyable = True, attrType = 'float' )
    cmds.setAttr( obj2 + '.' + mergeAttr, cmds.getAttr( obj1 + scl[0] ) )
    for s in scl:
        cmds.connectAttr( obj2 + '.' + mergeAttr, obj1 + s )


def scaleUnlock( obj, sx = True, sy = True, sz = True ):
    scaleString = ['.sx', '.sy', '.sz']
    scaleList = [sx, sy, sz]
    i = 0
    for item in scaleList:
        if item == True:
            cmds.setAttr( obj + scaleString[i], lock = False )
            cmds.setAttr( obj + scaleString[i], cb = True )
            cmds.setAttr( obj + scaleString[i], k = True )
        i = i + 1


def translationLock( obj, lock = False ):
    '''
    toggle state of translation
    '''
    tString = ['.tx', '.ty', '.tz']
    for item in tString:
        cmds.setAttr( obj + item, lock = lock )
        cmds.setAttr( obj + item, k = not lock )
        # cmds.setAttr( obj + item, cb = not lock )


def translationX( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.tx'
    cmds.setAttr( obj + item, lock = lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def translationY( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.ty'
    # cmds.setAttr( obj + item, cb = not lock )
    cmds.setAttr( obj + item, lock = lock )
    # cmds.setAttr( obj + item, cb = not lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def translationZ( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.tz'
    cmds.setAttr( obj + item, lock = lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def rotationLock( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    tString = ['.rx', '.ry', '.rz']
    for item in tString:
        cmds.setAttr( obj + item, lock = lock )
        cmds.setAttr( obj + item, k = not lock )
        # cmds.setAttr( obj + item, cb = not lock )


def rotationX( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.rx'
    cmds.setAttr( obj + item, lock = lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def rotationY( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.ry'
    cmds.setAttr( obj + item, lock = lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def rotationZ( obj, lock = False ):
    '''
    toggle state of rotation
    '''
    item = '.rz'
    cmds.setAttr( obj + item, lock = lock )
    cmds.setAttr( obj + item, k = not lock )
    # cmds.setAttr( obj + item, cb = not lock )


def hijack( obj1, obj2, translate = True, rotate = True, scale = True, visibility = True ):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    if translate:
        cmds.connectAttr( obj2 + '.translateX', obj1 + '.translateX' )
        cmds.connectAttr( obj2 + '.translateY', obj1 + '.translateY' )
        cmds.connectAttr( obj2 + '.translateZ', obj1 + '.translateZ' )
    if rotate:
        cmds.connectAttr( obj2 + '.rotateX', obj1 + '.rotateX' )
        cmds.connectAttr( obj2 + '.rotateY', obj1 + '.rotateY' )
        cmds.connectAttr( obj2 + '.rotateZ', obj1 + '.rotateZ' )
    if scale:
        cmds.connectAttr( obj2 + '.scaleX', obj1 + '.scaleX' )
        cmds.connectAttr( obj2 + '.scaleY', obj1 + '.scaleY' )
        cmds.connectAttr( obj2 + '.scaleZ', obj1 + '.scaleZ' )
    if visibility:
        cmds.connectAttr( obj2 + '.visibility', obj1 + '.visibility' )


def renameHierarchy( root, name, pad = 2, suffix = None ):
    '''\n
    root   = object at top of hierarchy\n
    name   = new name\n
    pad    = number padding, 2 is default\n
    suffix = string (ie. 'L' or 'R')\n
    '''
    cmds.select( root, hi = True )
    sel = cmds.ls( sl = True, l = True )
    newName = ''
    j = 1  # start count is 1 not zero, avoid 00 pad
    for i in range( 0, len( sel ), 1 ):
        if suffix == None:
            sel[i] = cmds.rename( sel[i], name + '_' +
                                 str( ( '%0' + str( pad ) + 'd' ) % ( j ) ) )
        else:
            sel[i] = cmds.rename( 
                sel[i], name + '_' + str( ( '%0' + str( pad ) + 'd' ) % ( j ) ) + '_' + suffix )
        if i == 0:
            root = sel[i]
        cmds.select( root, hi = True )
        sel = cmds.ls( sl = True )
        if i + 1 == len( sel ):
            return sel
        i = i + 1
        j = j + 1


def cleanUp( obj, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False ):
    '''\n
    Ctrl  =  parent 'obj' to '___CONTROLS'    group of prebuild script\n
    SknJnts  =  parent 'obj' to '___SKIN_JOINTS' group of prebuild script\n
    Body       =  parent 'obj' to '___BODY'         group of prebuild script\n
    Accessory       =  parent 'obj' to '___ACCESSORY'         group of prebuild script\n
    Utility       =  parent 'obj' to '___UTILITY'         group of prebuild script\n
    World     =  parent 'obj' to '___WORLD_SPACE' group of prebuild script\n
    olSkool   =  parent 'obj' to '___OL_SKOOL'    group of prebuild script\n
    '''
    if Ctrl == True:
        Ctrl = namePrebuild( Ctrl = True )
        if cmds.objExists( Ctrl ) == 1:
            try:
                cmds.parent( obj, Ctrl )
            except:
                print( obj, 'clean up to', Ctrl, 'failed.' )
    if SknJnts == True:
        SknJnts = namePrebuild( SknJnts = True )
        if cmds.objExists( SknJnts ) == 1:
            try:
                cmds.parent( obj, SknJnts )
            except:
                print( obj, 'clean up to', SknJnts, 'failed.' )
    if Body == True:
        Body = namePrebuild( Geo = True )[3]
        if cmds.objExists( Body ) == 1:
            try:
                cmds.parent( obj, Body )
            except:
                print( obj, 'clean up to', Body, 'failed.' )
    if Accessory == True:
        Accessory = namePrebuild( Geo = True )[2]
        if cmds.objExists( Accessory ) == 1:
            try:
                cmds.parent( obj, Accessory )
            except:
                print( obj, 'clean up to', Accessory, 'failed.' )
    if Utility == True:
        Utility = namePrebuild( Geo = True )[1]
        if cmds.objExists( Utility ) == 1:
            try:
                cmds.parent( obj, Utility )
            except:
                print( obj, 'clean up to', Utility, 'failed.' )
    if World == True:
        World = namePrebuild( World = True )
        if cmds.objExists( World ):
            try:
                cmds.parent( obj, World )
            except:
                print( obj, 'clean up to', World, 'failed.' )
    if olSkool == True:
        olSkool = namePrebuild( olSkool = True )
        if cmds.objExists( olSkool ) == 1:
            try:
                cmds.parent( obj, olSkool )
            except:
                print( obj, 'clean up to', olSkool, 'failed.' )


def namePrebuild( Top = 0, Ctrl = False, SknJnts = False, Geo = False, World = False, Master = False, olSkool = False ):
    '''\n
    Default names of master groups\n
    Only use one at a time. All other should remain as 'False'\n
    Top   (0 = creates ___CHARACTER___ group),  (1 = creates ___PROP___ group)\n
    Ctrl     =  return name\n
    SknJnts  =  return name\n
    Geo      =  return name, name, name, name\n
    World    =  return name\n
    Master   =  return name\n
    '''
    if Top == 0:
        result = '___CHARACTER___'
    elif Top == 1:
        result = '___PROP___'
    elif Top == 2:
        result = '___VEHICLE___'
    elif Top == 3:
        result = '___ACCSS___'
    if Ctrl == True:
        result = '___CONTROLS'
    if SknJnts == True:
        result = '___SKIN_JOINTS'
    if Geo == True:
        result = ['___GEO', '___UTILITY', '___ACCESSORY', '___BODY']
    if World == True:
        result = '___WORLD_SPACE'
    if Master == True:
        result = 'master'
    if olSkool == True:
        result = '___OL_SKOOL'
    return result


def rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 110 ):
    '''\n
    Top  = (0 creates ___CHARACTER___ group) (1 creates ___PROP___ group) (2 creates ___VEHICLE___ group)\n
    '''
    TOP = None
    CONTROLS = None
    SKIN_JOINTS = None
    GEO = None
    WORLD = None
    MASTER = None
    result = []

    # TOP #
    if Top == 0:
        Top = namePrebuild( Top = 0 )
        TOP = cmds.group( em = True, n = Top )
        setChannels( TOP, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( TOP )
    elif Top == 1:
        Top = namePrebuild( Top = 1 )
        TOP = cmds.group( em = True, n = Top )
        setChannels( TOP, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( TOP )
    elif Top == 2:
        Top = namePrebuild( Top = 2 )
        TOP = cmds.group( em = True, n = Top )
        setChannels( TOP, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( TOP )
    elif Top == 3:
        Top = namePrebuild( Top = 3 )
        TOP = cmds.group( em = True, n = Top )
        setChannels( TOP, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( TOP )
    else:
        mel.eval( 'warning \"' + '////... Top variable is out of range. 0=CHARACTER, 1=PROP, 2=VEHICLE, 3=ACCSS...////' + '\";' )

    # CONTROLS #
    if Ctrl == True:
        Ctrl = namePrebuild( Ctrl = True )
        CONTROLS = cmds.group( em = True, n = Ctrl )
        cmds.parent( CONTROLS, TOP )
        setChannels( CONTROLS, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( CONTROLS )

    # SKIN_JOINTS #
    if SknJnts == True:
        SknJnts = namePrebuild( SknJnts = True )
        SKIN_JOINTS = cmds.group( em = True, n = SknJnts )
        cmds.parent( SKIN_JOINTS, TOP )
        setChannels( SKIN_JOINTS, [True, False], [True, False], [
                    True, False], [False, False, False] )
        # #cmds.parent(SKIN_jnt, SKIN_JOINTS)
        result.append( SKIN_JOINTS )

    # GEO #
    if Geo == True:
        GEO = ['', '', '', '']
        Geo = namePrebuild( Geo = True )
        GEO[0] = cmds.group( em = True, n = Geo[0] )
        GEO[1] = cmds.group( em = True, n = Geo[1] )
        GEO[2] = cmds.group( em = True, n = Geo[2] )
        GEO[3] = cmds.group( em = True, n = Geo[3] )
        cmds.parent( GEO[3], GEO[0] )
        cmds.parent( GEO[2], GEO[0] )
        cmds.parent( GEO[1], GEO[0] )
        cmds.parent( GEO[0], TOP )
        i = 0
        for item in GEO:
            setChannels( item, [True, False], [True, False],
                        [True, False], [True, False, False] )
            if i == 1:
                cmds.setAttr( item + '.visibility', False )
            i = i + 1
        # #cmds.parent(GEO_gp, GEO)
        result.append( GEO )

    # WORLD #
    if World == True:
        World = namePrebuild( World = True )
        WORLD_SPACE = cmds.group( em = True, n = World )
        cmds.parent( WORLD_SPACE, TOP )
        setChannels( WORLD_SPACE, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( WORLD_SPACE )

    # MASTER #
    if Master == True:
        Master = namePrebuild( Master = True )
        world = cmds.group( em = True )
        master = Controller( Master, world, False, 'facetYup_ctrl', Size,
                            12, 8, 1, ( 0, 1, 0 ), True, True, False, colorName = 'yellow' )
        MasterCt = master.createController()
        setRotOrder( MasterCt[0], 2, True )
        cmds.delete( world )
        cmds.parent( MasterCt[0], CONTROLS )
        result.append( MasterCt )

    # OLSKOOL #
    if OlSkool == True:
        olSkool = namePrebuild( olSkool = True )
        OL_SKOOL = cmds.group( em = True, n = olSkool )
        cmds.parent( OL_SKOOL, TOP )
        setChannels( OL_SKOOL, [True, False], [True, False], [
                    True, False], [True, False, False] )
        result.append( OL_SKOOL )

    return result


def zero( obj, t = True, r = True, s = True ):
    translate = ['.tx', '.ty', '.tz']
    rotate = ['.rx', '.ry', '.rz']
    scale = ['.sx', '.sy', '.sz']
    if t == True:
        for item in translate:
            cmds.setAttr( obj + item, 0 )
    if r == True:
        for item in rotate:
            cmds.setAttr( obj + item, 0 )
    if s == True:
        for item in scale:
            cmds.setAttr( obj + item, 1 )


def optEnum( obj, attr = 'Deformer', enum = 'OPTNS' ):
    '''\n
    obj = object to recieve 'OPTNS' attr
    attr = attribute name(if options are for deformer, attr='Def')
    '''
    if not cmds.attributeQuery( attr, node = obj, ex = True ):
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = enum )
        cmds.setAttr( obj + '.' + attr, cb = True )
    else:
        pass
        # print '___already exists', obj, attr


def stripSufx( obj, string = False ):
    '''\n
    removes suffix (_L, _R)\n
    string == False    - default strings are stripped (_L, _R)
    string == 'string' - supplied string will be stripped from obj
    '''
    name = None
    if string == False:
        if '_L' in obj:
            name = obj.replace( '_L', '' )
            return name
        elif '_R' in obj:
            name = obj.replace( '_R', '' )
            return name
        else:
            print( 'nothing stripped' )
    else:
        if string in obj:
            name = obj.replace( string, '' )
            return name
        else:
            print( 'nothing stripped' )


def shapeSize( obj = None, mltp = 1 ):
    '''\n
    mltp = size multiplier of shape nodes
    '''

    if obj == None:
        # make a list from selection
        obj = cmds.ls( sl = True, l = True )
    elif type( obj ) == list:
        # no need to accomodate
        pass
    else:
        # obj must be a single item, make a list
        obj = [obj]
    # run the loop on list
    for item in obj:
        shape = cmds.listRelatives( item, s = True, f = True )
        if shape != None:
            for node in shape:
                if 'SharedAttr' not in node:
                    cmds.scale( mltp, mltp, mltp, node + '.cv[*]' )


def addText( obj, t = 'A', f = 'Arial-Bold', c = 12, rotOffset = [0, 0, 0], posOffset = [-1, 10, 0] ):
    '''\n
    obj = transform to recieve text
    t   = text
    f   = font
    c   = color
    '''
    shapes = []
    text = cmds.textCurves( ch = 0, f = f, t = t )
    # xform text
    pos = cmds.xform( obj, q = True, rp = True, ws = True )
    rot = cmds.xform( obj, q = True, ro = True, ws = True )
    cmds.xform( text, t = pos, ro = rot )
    # get selection
    cmds.select( text, hi = True )
    sel = cmds.ls( sl = True )
    # find shapes
    for item in sel:
        if cmds.objectType( item ) != 'transform':
            # offset
            cmds.rotate( rotOffset[0], rotOffset[1], rotOffset[2],
                        item + '.cv[*]', r = True, eu = True, p = pos )
            cmds.move( posOffset[0], posOffset[1], posOffset[2],
                      item + '.cv[*]', r = True, ls = True, wd = True )
            # assemble
            cmds.setAttr( item + '.overrideEnabled', 1 )
            cmds.setAttr( item + '.overrideColor', c )
            cmds.parent( item, obj, r = True, s = True )
            cmds.rename( item, obj + 'Shape' )
    # delete left overs
    cmds.delete( text )


def breakConnection( obj = '', attr = '' ):
    '''
    break connection whatever is driving given attr on given object
    '''
    con = cmds.listConnections( obj + '.' + attr, s = 1, d = 0, skipConversionNodes = True, plugs = True )
    if con:
        cmds.disconnectAttr( con[0], obj + '.' + attr )


def smartAttrBlend( master = '', slave = '', masterAttr = '', slaveAttr = '', blendAttrObj = '', blendAttrString = '', blendWeight = 1.0, reverse = False ):
    '''\n
    hijacks attribute with weight effect\n
    obj1   = master
    obj2   = slave
    objOpt = object to recieve blend attribute(typically parent of object 2 if using controller hierarchy)
    specific = ['slave attribiute', 'master attribute'], pre-existing
    #
    slave queried if existing connection, add addDoubleLin if true, break existing connection, pipe through addDoubleLin
    new master gets multDoubleLin for weight and reverse after if needed
    
        '''
    #
    name = 'smartBlend'
    rev = None
    addDL = None

    # reverse node
    if reverse:
        # rev = cmds.shadingNode( 'reverse', name = master + '_' + name + '_rvrs', asUtility = True )
        # cmds.connectAttr( master + '.' + masterAttr, rev + '.inputX' )
        # mltp node instead
        rev = cmds.shadingNode( 'multDoubleLinear', name = master + '_' + name + '_mltpNeg', asUtility = True )
        cmds.setAttr( rev + '.input2', -1 )
        cmds.connectAttr( master + '.' + masterAttr, rev + '.input1' )

    # weight node
    blendN = cmds.shadingNode( 'multDoubleLinear', name = master + '_' + name + '_mltp', asUtility = True )

    # connect master/rev attr to weight node
    if reverse:
        cmds.connectAttr( rev + '.output', blendN + '.input1' )
    else:
        cmds.connectAttr( master + '.' + masterAttr, blendN + '.input1' )

    # create user weight attr
    # hijackAttrs( obj1, obj2, attrOrig, attrNew, set = False, default = None, force = True )
    if blendAttrObj:
        optEnum( blendAttrObj, 'additive' )
        hijackAttrs( blendN, blendAttrObj, 'input2', blendAttrString + 'Weight', set = True, default = blendWeight )
    else:
        cmds.setAttr( blendN + '.input2', blendWeight )

    # find existing incoming masterAttr connections, if any
    existingMaster = None
    con = cmds.listConnections( slave + '.' + slaveAttr, s = 1, d = 0, skipConversionNodes = True, plugs = True )
    # print( con )
    if con:
        # add addition node
        existingMaster = con[0]
        addDL = cmds.shadingNode( 'addDoubleLinear', name = master + '_' + name + '_add', asUtility = True )
        cmds.connectAttr( existingMaster, addDL + '.input1' )
        cmds.connectAttr( blendN + '.output', addDL + '.input2' )
        # connect out blend
        cmds.connectAttr( addDL + '.output', slave + '.' + slaveAttr, force = True )  # force
    else:
        # connect out blend
        cmds.connectAttr( blendN + '.output', slave + '.' + slaveAttr )


def attrBlend( obj1, obj2, objOpt, pos = False, rot = False, scale = False, specific = [[None], None], skip = 2, default = 1 ):
    '''\n
    hijacks attribute with weight effect\n
    obj1   = master
    obj2   = slave
    pos    = position blend
    rot    = rotation blend
    scale  = scale blend
    objOpt = object to recieve blend attribute(typically parent of object 2 if using controller hierarchy)
    specific = ['slave attribiute', 'master attribute'], pre-existing
        '''
    # attrs
    attr = [['rx', 'ry', 'rz'], ['tx', 'ty', 'tz'], ['sx', 'sy', 'sz'], [
        'color1R', 'color1G', 'color1B'], ['outputR', 'outputG', 'outputB']]
    optEnum( objOpt, 'additive' )
    # pos
    if pos == True:
        # blend
        rotB = cmds.shadingNode( 'blendColors', name = ( 
            obj1 + '_positionBlend' ), asUtility = True )
        cmds.setAttr( rotB + '.color1R', 0 )
        cmds.setAttr( rotB + '.color2B', 0 )
        hijackAttrs( rotB, objOpt, 'blender', 'posWeight', default = default )
        # #connect in blend
        i = 0
        for item in attr[1]:
            cmds.connectAttr( obj1 + '.' + item, rotB + '.' + attr[3][i] )
            i = i + 1
        # connect out blend
        j = 0
        for item in attr[4]:
            cmds.connectAttr( rotB + '.' + item, obj2 + '.' + attr[1][j] )
            j = j + 1
    # rotate
    if rot == True:
        # blend
        rotB = cmds.shadingNode( 'blendColors', name = ( 
            obj1 + '_rotateBlend' ), asUtility = True )
        cmds.setAttr( rotB + '.color1R', 0 )
        cmds.setAttr( rotB + '.color2B', 0 )
        hijackAttrs( rotB, objOpt, 'blender', 'rotWeight', default = default )
        # #connect in blend
        i = 0
        for item in attr[0]:
            cmds.connectAttr( obj1 + '.' + item, rotB + '.' + attr[3][i] )
            i = i + 1
        # connect out blend
        j = 0
        for item in attr[4]:
            if j == skip:
                pass
            else:
                # print rotB + '.' + item, obj2 + '.' + attr[0][j]
                cmds.connectAttr( rotB + '.' + item, obj2 + '.' + attr[0][j] )
                j = j + 1
    # scale
    if scale == True:
        # blend
        rotB = cmds.shadingNode( 'blendColors', name = ( 
            obj1 + '_scaleBlend' ), asUtility = True )
        # cmds.setAttr(rotB + '.color2R', 1)
        # cmds.setAttr(rotB + '.color2B', 1)
        # cmds.setAttr(rotB + '.color2B', 1)
        for item in attr[3]:
            cmds.setAttr( rotB + '.' + item[:5] + str( 2 ) + item[6], 1 )
        hijackAttrs( rotB, objOpt, 'blender', 'sclWeight', default = default )
        # #connect in blend
        i = 0
        for item in attr[2]:
            cmds.connectAttr( obj1 + '.' + item, rotB + '.' + attr[3][i] )
            i = i + 1
        # connect out blend
        j = 0
        for item in attr[4]:
            cmds.connectAttr( rotB + '.' + item, obj2 + '.' + attr[2][j] )
            j = j + 1
    # specific
    if specific != [[None], None]:
        # blend
        rotB = cmds.shadingNode( 'blendColors', name = ( 
            obj1 + '_specificBlend' ), asUtility = True )
        # hijack blend attribute
        hijackAttrs( rotB, objOpt, 'blender',
                    specific[1] + 'Weight', default = default )
        # #connect in blend
        cmds.setAttr( rotB + '.color2R', default )
        cmds.connectAttr( obj1 + '.' + specific[0], rotB + '.color1R' )
        # connect out blend
        for attr in specific[0]:
            cmds.connectAttr( rotB + '.outputR', obj2 + '.' + attr )


def hijackConstraints( master = '', attr = '', value = 0.5, constraint = '' ):
    '''
    assume weight = 0-1
    master = object
    attr = attr to create on master object, if doesnt exist
    value = value to assign new attr
    constraint = connect and connect reverse
    '''
    # add attr
    # cmds.addAttr( master, ln = attr, attributeType = 'float', k = True, dv = value, min = 0.0, max = 1.0 )
    # weight
    weightAttr = cmds.listAttr( constraint, k = True, ud = True )
    # direct connect
    cmds.connectAttr( master + '.' + attr, constraint + '.' + weightAttr[0] )
    # reverse node connect
    revrsPos = cmds.shadingNode( 'reverse', au = True, n = ( constraint + '_' + attr + '_revrs' ) )
    cmds.connectAttr( master + '.' + attr, revrsPos + '.inputX' )
    cmds.connectAttr( revrsPos + '.outputX', constraint + '.' + weightAttr[1] )


def sortObj( objs ):
    '''\n
    Sort objects alphabetically and reposition in hierarchy.
    Objects must be under the same parent.
    '''
    # convert list to string objects
    i = 0
    for item in objs:
        objs[i] = str( item )
        i = i + 1
    # sort string objects
    objs.sort( key = str.lower )
    # reorder in scene
    for item in objs:
        cmds.reorder( item, b = True )


def flatten( obj ):
    '''
    rudamentary function to remove world orientations in x and z axis\n
    can be adapted to 'flatten' other axis by exposing a variable...
    '''
    ro = cmds.getAttr( obj + '.ro' )
    cmds.setAttr( obj + '.ro', 3 )
    x = cmds.xform( obj, q = True, ws = True, ro = True )
    cmds.xform( obj, ws = True, ro = ( 0, x[1], 0 ) )
    cmds.setAttr( obj + '.ro', ro )


def getUniqueName( name = '' ):
    if not cmds.objExists( name ):
        return name
    else:
        i = 1
        while cmds.objExists( name + str( i ) ):
            i = i + 1
        return name + str( i )


def assetParent( obj = '', query = False ):
    prefix = '__HELP__'
    suffix = 'local'
    if ':' in obj:
        asset = obj.split( ':' )[0]
    else:
        asset = suffix
    asset = prefix + asset
    if not query:
        if not cmds.objExists( asset ):
            asset = cmds.group( name = asset, em = True )
            setChannels( asset, [True, False], [True, False], [
                        True, False], [True, False, False] )
            # asset = assetGrp
        return asset
    else:
        return asset
