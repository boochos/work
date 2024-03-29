import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
#

import webrImport as web
# web
place = web.mod( 'atom_place_lib' )


def convertFlipValue( flipVar ):
    flip = flipVar[:]
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

    if visibility[0] == True:
        try:
            cmds.setAttr( item + '.visibility', 1 )
        except:
            pass
            # #mel.eval('warning \"' + '////... visibility already connected ...////' + '\";')
    else:
        try:
            cmds.setAttr( item + '.visibility', 0 )
        except:
            pass
            # #mel.eval('warning \"' + '////... visibility already connected ...////' + '\";')

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


def buildName( prefix, suffix, name ):
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
    sel = cmds.ls( sl = True )
    if len( sel ) > 0:
        i = 0
        result = []
        relative = []
        exclusion = ['pointConstraint', 'orientConstraint', 'parentConstraint']
        obj = None
        if what == 'null':
            if order != None:
                obj = place.null( name, order )
            else:
                obj = place.null( name )
        elif what == 'loc':
            if order != None:
                obj = place.loc( name, order )[0]
            else:
                obj = place.loc( name )[0]

        else:
            mel.eval( 
                'warning \"' + '////...  -what-  has two options: \'loc\' or \'null\' ...////' + '\";' )
        if obj != None:
            for item in sel:
                cmds.select( sel[i] )
                # above
                if where == 1:
                    parent = cmds.listRelatives( 
                        item, parent = True, typ = 'transform' )
                    # if parent of item exists (middle of chain)
                    if parent != None:
                        for prnt in parent:
                            if cmds.nodeType( prnt ) in exclusion:
                                child.remove( prnt )
                        relative.append( parent )
                        # parent obj under parent of item
                        cmds.parent( obj, parent )
                        # parent item under obj
                        cmds.parent( item, obj )
                    # if item has no parents (top of chain)
                    else:
                        # parent item under obj
                        cmds.parent( item, obj )
                # below
                else:
                    child = cmds.listRelatives( 
                        item, children = True, typ = 'transform' )
                    # if item has children (middle of chain)
                    if child != None:
                        for chld in child:
                            if cmds.nodeType( chld ) in exclusion:
                                child.remove( chld )
                        relative.append( child )
                        # parent obj under item
                        cmds.parent( obj, item )
                        # parent child(s) under obj
                        for item in child:
                            cmds.parent( item, obj )
                    # if item has no children (bottom of chain)
                    else:
                        # parent obj under item
                        cmds.parent( obj, item )
                result.append( obj )
                i = i + 1
            return result
    else:
        mel.eval( 'warning \"' +
                 '////... select at least one object ...////' + '\";' )
        return None


def selectionList():
    sel = cmds.ls( sl = True )
    return sel


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
            cmds.addAttr( objList, ln = attrList, at = attrType,
                         min = minimum, max = maximum, h = False )
            cmds.setAttr( ( objList + '.' + attrList ), cb = True )
            cmds.setAttr( ( objList + '.' + attrList ), k = keyable )
        else:
            for attr in attrList:
                cmds.addAttr( objList, ln = attr, at = attrType,
                             min = minimum, max = maximum )
                cmds.setAttr( ( objList + '.' + attr ), cb = True )
                cmds.setAttr( ( objList + '.' + attr ), k = keyable )

    elif len( objList ) > 0:
        if len( attrList ) > 0:
            for obj in objList:
                if type( attrList ) != list:
                    cmds.addAttr( obj, ln = attrList, at = attrType,
                                 min = minimum, max = maximum )
                    cmds.setAttr( ( obj + '.' + attrList ), cb = True )
                    cmds.setAttr( ( obj + '.' + attrList ), k = keyable )
                else:
                    for attr in attrList:
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


def guideLine( obj1, obj2, Name ):
    """\n
    Connects 2 objects with curve\n
    Create curve with 2 points\n
    pointConstrain cv[0] to obj1, cv[1] to obj2\n
    """
    result = []
    curveTmp = cmds.curve( d = 1, p = [( 0, 0, 0 ), ( 0, 0, 0 )], k = [0, 1] )
    curve = cmds.rename( curveTmp, ( Name + '_crv#' ) )
    cmds.setAttr( curve + '.overrideEnabled', 1 )
    cmds.setAttr( curve + '.overrideDisplayType', 1 )
    clstr = place.clstrOnCV( curve, Name + '___' + obj1 + '___' + obj2 )
    cmds.setAttr( clstr[0] + '.visibility', 0 )
    cmds.setAttr( clstr[1] + '.visibility', 0 )
    cmds.pointConstraint( obj1, clstr[0], mo = False, w = 1.0 )
    cmds.pointConstraint( obj2, clstr[1], mo = False, w = 1.0 )
    result.append( curve )
    result.append( clstr )
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
    RO = 'False'
    # old
    '''
    if (cmds.getAttr(CtGp + '.rotateOrder')) == (cmds.getAttr(TopGp + '.rotateOrder')):
        if cmds.getAttr(CtGp + '.rotateOrder') == cmds.getAttr(ObjOff + '.rotateOrder'):
            if cmds.getAttr(CtGp + '.rotateOrder') == cmds.getAttr(ObjOn + '.rotateOrder'):
                RO = cmds.getAttr(CtGp + '.rotateOrder')
    '''
    # new
    if ( cmds.getAttr( CtGp + '.rotateOrder' ) ) == ( cmds.getAttr( ObjOff + '.rotateOrder' ) ):
        # print CtGp, ObjOff, 'Good'
        if cmds.getAttr( CtGp + '.rotateOrder' ) == cmds.getAttr( ObjOn + '.rotateOrder' ):
            # print CtGp, ObjOn, 'Good'
            RO = cmds.getAttr( CtGp + '.rotateOrder' )

    # attrs
    prefix = ''
    if attr != False:
        prefix = attr
    PosOffOn = prefix + 'PositionOffOn'  # attr to switch parent, on 'Obj'
    OrntOffOn = prefix + 'OrientOffOn'  # attr to switch parent, on 'Obj'
    PrntOffOn = prefix + 'ParentOffOn'  # attr to switch parent, on 'Obj'
    Parent = 'Parent'  # enum attr name

    # create 'OPTNS' enum
    if OPT == True:
        cmds.addAttr( Ct, ln = Parent, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( Ct + '.' + Parent, cb = True )

    # create point switch
    if Pos == True:
        # create and constrain matching Obj1Gp and Obj2Gp
        PosOffGp = place.null2( name + '_PosOffGp', Ct )[0]
        PosOnGp = place.null2( name + '_PosOnGp', Ct )[0]
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
    if Ornt == True:
        if RO == 'False':
            mel.eval( 'warning \"' + '////... Orient: Rotation Orders dont match. IM OUT!...////' +
                     CtGp + ObjOff + ObjOn + '\";' )
        else:
            # constrain matching Obj1Gp and Obj2Gp
            OrntOffGp = place.null2( name + '_OrntOffGp', Ct )[0]
            OrntOnGp = place.null2( name + '_OrntOnGp', Ct )[0]
            setRotOrder( OrntOffGp, RO )
            setRotOrder( OrntOnGp, RO )
            cmds.parent( OrntOffGp, TopGp )
            cmds.parent( OrntOnGp, TopGp )
            cmds.orientConstraint( ObjOff, OrntOffGp, w = 1.0, mo = True )
            cmds.orientConstraint( ObjOn, OrntOnGp, w = 1.0, mo = True )
            # contrain object with switch constraints
            cmds.addAttr( Ct, ln = OrntOffOn, attributeType = 'float',
                         k = True, dv = w, min = 0.0, max = 1.0 )
            SwitchCnst = cmds.orientConstraint( 
                OrntOffGp, CtGp, w = 1.0, mo = False )[0]
            cmds.orientConstraint( OrntOnGp, CtGp, w = 0.0, mo = False )
            # build switch
            wghtAttr = cmds.listAttr( SwitchCnst, k = True, ud = True )
            revrsOrnt = cmds.shadingNode( 
                'reverse', au = True, n = ( name + '_revrsOrnt' ) )
            cmds.connectAttr( Ct + '.' + OrntOffOn, revrsOrnt + '.inputX' )
            cmds.connectAttr( revrsOrnt + '.outputX',
                             SwitchCnst + '.' + wghtAttr[0] )
            cmds.connectAttr( Ct + '.' + OrntOffOn,
                             SwitchCnst + '.' + wghtAttr[1] )

    # create parent switch
    if Prnt == True:
        if RO == 'False':
            mel.eval( 'warning \"' + '////... Parent: Rotation Orders dont match. IM OUT!...////' +
                     CtGp + ObjOff + ObjOn + '\";' )
        else:
            # constrain matching Obj1Gp and Obj2Gp
            PrntOffGp = place.null2( name + '_PrntOffGp', CtGp )[0]
            PrntOnGp = place.null2( name + '_PrntOnGp', CtGp )[0]
            setRotOrder( PrntOffGp, RO )
            setRotOrder( PrntOnGp, RO )
            cmds.parent( PrntOffGp, TopGp )
            cmds.parent( PrntOnGp, TopGp )
            cmds.parentConstraint( ObjOff, PrntOffGp, w = 1.0, mo = True )
            cmds.parentConstraint( ObjOn, PrntOnGp, w = 1.0, mo = True )
            # contrain object with switch constraints
            cmds.addAttr( Ct, ln = PrntOffOn, attributeType = 'float',
                         k = True, dv = w, min = 0.0, max = 1.0 )
            SwitchCnst = cmds.parentConstraint( 
                PrntOffGp, CtGp, w = 1.0, mo = False )[0]
            cmds.parentConstraint( PrntOnGp, CtGp, w = 0.0, mo = False )
            # build switch
            wghtAttr = cmds.listAttr( SwitchCnst, k = True, ud = True )
            revrsPrnt = cmds.shadingNode( 
                'reverse', au = True, n = ( name + '_revrsPrnt' ) )
            cmds.connectAttr( Ct + '.' + PrntOffOn, revrsPrnt + '.inputX' )
            cmds.connectAttr( revrsPrnt + '.outputX',
                             SwitchCnst + '.' + wghtAttr[0] )
            cmds.connectAttr( Ct + '.' + PrntOffOn,
                             SwitchCnst + '.' + wghtAttr[1] )


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
    if hier == True:
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
    if hier == True:
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


def scaleUnlock( obj, sx = True, sy = True, sz = True, k = True ):
    scaleString = ['.scaleX', '.scaleY', '.scaleZ']
    scaleList = [sx, sy, sz]
    i = 0
    for item in scaleList:
        if item == True:
            cmds.setAttr( obj + scaleString[i], lock = False )
            if k:
                cmds.setAttr( obj + scaleString[i], cb = True )
                cmds.setAttr( obj + scaleString[i], k = True )
        i = i + 1


def hijack( obj1, obj2, translate = True, rotate = True, scale = True, visibility = True ):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    if translate == True:
        cmds.connectAttr( obj2 + '.translateX', obj1 + '.translateX' )
        cmds.connectAttr( obj2 + '.translateY', obj1 + '.translateY' )
        cmds.connectAttr( obj2 + '.translateZ', obj1 + '.translateZ' )
    if rotate == True:
        cmds.connectAttr( obj2 + '.rotateX', obj1 + '.rotateX' )
        cmds.connectAttr( obj2 + '.rotateY', obj1 + '.rotateY' )
        cmds.connectAttr( obj2 + '.rotateZ', obj1 + '.rotateZ' )
    if scale == True:
        cmds.connectAttr( obj2 + '.scaleX', obj1 + '.scaleX' )
        cmds.connectAttr( obj2 + '.scaleY', obj1 + '.scaleY' )
        cmds.connectAttr( obj2 + '.scaleZ', obj1 + '.scaleZ' )
    if visibility == True:
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
        if cmds.objExists( World ) == 1:
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
    Top  = (0 creates ___CHARACTER___ group) (1 creates ___PROP___ group)\n
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
        master = place.Controller( 
            Master, world, False, 'facetYup_ctrl', Size, 12, 8, 1, ( 0, 1, 0 ), True, True )
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


def optEnum( obj, attr = 'Deformer', enum = 'OPTNS', cb = True ):
    '''\n
    obj = object to recieve 'OPTNS' attr
    attr = attribute name(if options are for deformer, attr='Def')
    '''
    if not cmds.attributeQuery( attr, node = obj, ex = True ):
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = enum )
        cmds.setAttr( obj + '.' + attr, cb = cb )
        cmds.setAttr( obj + '.' + attr, lock = 1 )
    else:
        print( '___already exists', obj, attr )


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


def labelJoint( joint, hi = False ):
    '''\n

        '''
    sel = None
    if hi == True:
        cmds.select( joint, hi = True )
        sel = cmds.ls( sl = True )
        for jnt in sel:
            cmds.setAttr( jnt + '.drawLabel', 1 )
            cmds.setAttr( jnt + '.type', 18 )
            cmds.setAttr( jnt + '.otherType', jnt, type = 'string' )
    else:
        cmds.setAttr( joint + '.drawLabel', 1 )
        cmds.setAttr( joint + '.type', 18 )
        cmds.setAttr( joint + '.otherType', joint, type = 'string' )


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


class convertTrack():

    '''\n
    Converts boujou track to camera space.\n
    Needs 3 objects.
    -camera(shot camera with plate)
    -boujou Locator(motion track baked from boujou)
    -obj(character controller thats constrained to boujouNode)
    '''

    def __init__( self ):
        sel = cmds.ls( sl = True )
        if len( sel ) == 3:
            self.cam = sel[0]
            self.track = sel[1]
            self.obj = sel[2]
            self.trackCt = None
            self.start = None
            self.end = None
            self.trackController()
            self.frameRange()
            self.bakeMotion()
        else:
            OpenMaya.MGlobal.displayError( 
                '////... select three objects,   --CAMERA--,   --TRACK--,   --CONSTRAINED CONTROLLER--' )

    def trackController( self ):
        '''\n
        creates tracking controllers
        '''
        name = 'Track'
        i = 1
        if cmds.objExists( name ) == 1:
            while cmds.objExists( name ) == 1:
                if i > 1:
                    name = name.replace( str( i - 1 ), str( i ) )
                else:
                    name = name + str( 1 )
                i = i + 1
        '''
        if exists == 1:
            name = name + nameS 
        '''
        ct = place.Controller( 
            name, self.track, shape = 'loc_ctrl', size = 3, color = 7 )
        self.trackCt = ct.createController()
        cmds.parent( self.trackCt[0], self.cam )
        setRotOrder( self.trackCt[0], 2, True )

    def frameRange( self ):
        '''\n
        get frame range
        '''
        self.start = cmds.playbackOptions( q = True, min = True )
        self.end = cmds.playbackOptions( q = True, max = True )

    def bakeMotion( self ):
        '''\n
        Constrains trackCt[0] object to self.track object, bakes the constraint.
        '''
        constraint = cmds.parentConstraint( 
            self.track, self.trackCt[0], mo = True )
        # self.start = cmds.playbackOptions(q=True, min=True)
        # self.end   = cmds.playbackOptions(q=True, max=True)
        cmds.bakeResults( self.trackCt[0], t = ( self.start, self.end ), sb = 1, at = [
                         "tx", "ty", "tz", "rx", "ry", "rz"], hi = "none" )
        cmds.delete( constraint )
        constraint = cmds.parentConstraint( 
            self.trackCt[2], self.obj, mo = True )[0]
        UsrAttr = cmds.listAttr( constraint, ud = True )
        for attr in UsrAttr:
            if self.trackCt[2] not in attr:
                cmds.setAttr( constraint + '.' + attr, 0 )
        cmds.select( self.trackCt[0] )


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
