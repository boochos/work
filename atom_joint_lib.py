from pymel.core import *
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
#
import webrImport as web
# web
place = web.mod( 'atom_place_lib' )


class CreateTwistJoints( object ):

    '''
    Used when creating the stardard character template
    '''

    def __init__( self, baseJnt, num, name, suffix, axis ):
        self.baseJnt = ls( baseJnt )[0]
        self.endJnt = ls( jointTravers( self.baseJnt.name(), 1 ) )[0]
        self.numJnt = num
        self.name = name
        self.suffix = suffix
        self.axis = axis

        # Get the distance inbetween the two joints for placement
        self.masterDis = place.distance2Pts( self.baseJnt.getTranslation( space = 'world' ), self.endJnt.getTranslation( space = 'world' ) )
        self.disOffset = float( self.masterDis ) / ( float( self.numJnt ) + 1 )
        self.jntTwistList = []

    def placeJoints( self ):
        currentDis = 0
        for i in range( 0, self.numJnt, 1 ):
            currentDis += self.disOffset

            name = '%s_twist_%02d_jnt_%s' % ( self.name, i + 1, self.suffix )
            jnt = createNode( 'joint', name = name, ss = True )
            jnt.setParent( self.baseJnt )

            jnt.setTranslation( [self.axis[0] * currentDis, self.axis[1] * currentDis, self.axis[2] * currentDis], space = 'object' )
            jnt.jointOrientX.set( 0 ), jnt.jointOrientY.set( 0 ), jnt.jointOrientZ.set( 0 )

            self.jntTwistList.append( jnt )


class RigTwistJoint( object ):

    def __init__( self, driver, driven, name, suffix, driverAxis, twistAxis, twistDirection = 1 ):
        self.driver = driver
        self.driven = driven
        self.name = name
        self.suffix = suffix
        self.driverAxis = driverAxis.upper()
        self.twistAxis = twistAxis.upper()
        self.twistDirection = twistDirection

        self.driverDict = {}
        self.buildRig()

    def buildRig( self ):
        fallOffFactor = 0
        cnt = 1
        for j in self.driven:

            twistJoint = j
            mdName = '%s_MDN_%02d%s' % ( self.name, cnt, self.suffix )
            mdn = createNode( 'multiplyDivide', name = mdName )
            fallOffFactor += 1 / float( len( self.driven ) + 1 )

            execStr = 'ls("' + mdn + '")[0].input2' + self.twistAxis + '.set(' + str( self.twistDirection * fallOffFactor ) + ')'
            exec( execStr )

            execStr = 'ls("' + self.driver + '")[0].rotate' + self.driverAxis + '.connect("'
            execStr += mdn + '.input1' + self.twistAxis + '", f=True)'
            exec( execStr )

            execStr = 'ls("' + mdn + '")[0].output' + self.twistAxis + '.connect("'
            execStr += twistJoint + '.rotate' + self.twistAxis + '",f=True)'
            exec( execStr )
            cnt += 1


def findEndJoint( parent, childCnt = 1 ):
    # list the children of the parent
    child = cmds.listRelatives( parent, children = True )
    if child != None:
        # test the child count
        if len( child ) == childCnt:
            return findEndJoint( child[0] )
        else:
            return parent
    else:
        return None


def getJointChainHier( fstJnt, sndJnt, chain = None ):
    # list the children of the parent
    if chain == None:
        chain = []
        chain.append( fstJnt )
    child = cmds.listRelatives( fstJnt, children = True )
    if child != None:
        # test the child count
        if child[0] != sndJnt:
            chain.append( child[0] )
            return getJointChainHier( child[0], sndJnt, chain )
        else:
            chain.append( child[0] )
            return chain
    else:
        return None


def jointTravers( startJnt, travCnt, cnt = 1 ):
    child = cmds.listRelatives( startJnt, children = True )
    if child != None:
        if travCnt != cnt:
            if len( child ) == 1:
                cnt += 1
                return jointTravers( child, travCnt, cnt )
            else:
                return None
        elif travCnt == cnt:
            return child[0]
        else:
            return None
    else:
        return None


def ZeroJointOrient( obj ):
    '''
    requires joint name\n
    adds any rotation value in axis(X,Y,Z) to related jointOrient value\n
    '''
    Jo = ['jointOrientX', 'jointOrientY', 'jointOrientZ']
    Ro = ['rotateX', 'rotateY', 'rotateZ']
    for i in range( 0, len( Jo ), 1 ):
        attrJo = cmds.getAttr( obj + '.' + Jo[i] )
        attrRo = cmds.getAttr( obj + '.' + Ro[i] )
        cmds.setAttr( obj + '.' + Jo[i], ( attrJo + attrRo ) )
        cmds.setAttr( obj + '.' + Ro[i], 0 )


def zeroJntSelection():
    sel = cmds.ls( sl = True )
    for item in sel:
        ZeroJointOrient( item )


def root( joint ):
    '''\n
    finds root joint of given joint\n
    '''
    parent = cmds.listRelatives( joint, ap = True, typ = 'joint' )
    if parent == None:
        return joint
    else:
        while parent != None:
            newParent = cmds.listRelatives( parent[0], p = True, typ = 'joint' )
            if newParent == None:
                return parent[0]
            else:
                parent = newParent


def mirror( jnt = '', mirrorBehavior = True ):
    '''
    
    mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "_L" "_R";
    '''
    sel = cmds.ls( sl = True )
    cmds.select( jnt )
    cmds.mirrorJoint( mirrorYZ = True, mirrorBehavior = mirrorBehavior, searchReplace = ( '_L', '_R' ) )
    cmds.select( sel )


def labelJoint( joint, hi = False ):
    '''\n
    Labels joint from name
    joint = joint to label
    hi    = label all hierarchy
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


def scaleCompensate( joint, hi = False, v = 0 ):
    '''\n
    Sets scale compensate on joints\n
    joint = joint to setAttr on\n
    hi    = setAttr all hierarchy\n
    v     = int value to set 0 or 1\n
        '''
    sel = None
    if hi == True:
        cmds.select( joint, hi = True )
        sel = cmds.ls( sl = True )
        for jnt in sel:
            cmds.setAttr( jnt + '.segmentScaleCompensate', v )
    else:
        cmds.setAttr( joint + '.segmentScaleCompensate', v )


def orientJntAt( obj, aim, up, aimVec = ( 0, 0, 1 ), upVec = ( 0, 1, 0 ) ):
    '''
        -orient a joint at an object with aim constraint,
    then zero rotates by adding values to joint orient.\n
    -jointOrients have to be set to zero in order for this to work, for some reason
        '''
    cmds.setAttr( '%s.jointOrient' % obj, 0, 0, 0 )
    cnst = cmds.aimConstraint( aim, obj,
                              mo = False,
                              aimVector = aimVec,
                              upVector = upVec,
                              worldUpType = 'object',
                              worldUpObject = up )
    cmds.delete( cnst )
    axis = ['X', 'Y', 'Z']
    for item in axis:
        cmds.setAttr( obj + '.jointOrient' + item, cmds.getAttr( obj + '.rotate' + item ) + cmds.getAttr( obj + '.jointOrient' + item ) )
        cmds.setAttr( obj + '.rotate' + item, 0 )


def ikJntRange( jnt, percent = 70 ):
    '''
        assumptions:\n
    jnt has 0 rotational values\n
    jnt is(will be) middle joint of 3 joint ik chain\n
    jnt is planar\n
    process:\n
    look at jointOrient values find value above 0 or below 0... 
    there should only be one attr, otherwise joint is not planar\n
    percent = range of movement (ie. 100= fully extends, 0= locks up at current position)
        '''
    result = 0
    q = []
    m = -1
    mn = [-360.0, 0]
    mx = [360.0, 0]
    X = cmds.getAttr( jnt + '.jointOrientX' )
    Y = cmds.getAttr( jnt + '.jointOrientY' )
    Z = cmds.getAttr( jnt + '.jointOrientZ' )
    axis = [X, Y, Z]
    for val in axis:
        if val != 0:
            q.append( val )
    if len( q ) == 1:
        if q[0] < 0:
            mx[1] = 1
            mx[0] = m * ( q[0] / ( 100.0 / percent ) )
            result = mx[0]
        else:
            mn[1] = 1
            mn[0] = m * ( q[0] / ( 100.0 / percent ) )
            result = mn[0]
        cmds.transformLimits( jnt, rx = [mn[0], mx[0]], erx = [mn[1], mx[1]] )
        return result
    elif len( q ) > 1:
        OpenMaya.MGlobal.displayWarning( '---  ' + jnt + ' joint is not planar  ---' )
        return result


def insertJoint( jnt = '', axis = 'tz' ):
    '''
    
    '''
    children = cmds.listRelatives( jnt, children = True )
    if children:
        if len( children ) == 1:
            children = children[0]
        else:
            print( 'more than one parent', children )
            children[0]
    else:
        return
    rds = cmds.getAttr( jnt + '.radius' )
    # print( parent )
    tz = cmds.getAttr( children + '.' + axis )
    dis = tz / 2
    j = cmds.insertJoint( jnt )
    cmds.setAttr( j + '.radius', rds )
    cmds.move( 0, 0, dis, j + '.scalePivot', j + '.rotatePivot', r = True, ls = True, wd = True )


def insertJoints( jnts = [] ):
    '''
    
    '''
    for jnt in jnts:
        insertJoint( jnt )
