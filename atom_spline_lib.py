from __future__ import division
import maya.cmds as cmds
import maya.mel as mel
import math
import webrImport as web
# web
place = web.mod('atom_place_lib')
jnt = web.mod('atom_joint_lib')

# List of joints
# confirms two joints are selected
# finds joints between the two selected joints
# confirms number of joints is odd
# returns all joints involved


def startEndJntList():
    jntList = []
    sel = cmds.ls(sl=True)
    if len(sel) == 2:
        x = 0
        for item in sel:
            if cmds.objectType(item) != 'joint':
                mel.eval('warning \"' + '////... Objects must be joints...////' + '\";')
                break
            else:
                x = 1
        if x == 1:
            jntList = jnt.getJointChainHier(sel[0], sel[1])
            # print jntList
            if len(jntList) % 2 == 1:
                return jntList
            else:
                mel.eval('warning \"' + '////... Number of joints must be odd...////' + '\";')
                return None
    else:
        mel.eval('warning \"' + '////... Select 2 objects: -start- & -end- joint of spline...////' + '\";')

# Creates splineIK
# ikName = prefix for all three object (iksolver, effector, curve)
# start = root joint of ik solver
# end = end joint of ik solver
# Returns ik, effector, curve


def splineIK(ikSuffix, start, end, upType=4, worldUpAxis=0, curve=False):
    '''\n
    makes ik spline
    start    = starting joint for ik
    end      = ending joint for ik
    fixCurve = fix number of cvs in curve to match the number joints
    '''
    # Not False means dont use default curve
    #__________

    # make this arguement make sense___________________________

    #__________
    if curve != False:
        chain = jnt.getJointChainHier(start, end, chain=None)
        crv = place.curve(ikSuffix + '_crv', chain)
        # print crv
        result = cmds.ikHandle(sj=start, ee=end, sol='ikSplineSolver', n=ikSuffix, c=crv, scv=False, ccv=False, pcv=False)
        result.append(crv)
    else:
        result = cmds.ikHandle(sj=start, ee=end, sol='ikSplineSolver', n=ikSuffix, scv=False, ccv=True, pcv=False)
    # rename curve and effector
    result[2] = cmds.rename(result[2], (ikSuffix + '_curve'))
    cmds.setAttr(result[2] + '.template', 1)
    result[1] = cmds.rename(result[1], (ikSuffix + '_effector'))
    # ##### ADD TO FUNCTION VARIABLES ##### #
    # Stickyness
    cmds.setAttr(ikSuffix + '.stickiness', 1)
    # Advanced Twist
    cmds.setAttr(ikSuffix + '.dTwistControlEnable', 1)
    # world Up Type
    cmds.setAttr(ikSuffix + '.dWorldUpType', upType)
    # Up Axis
    cmds.setAttr(ikSuffix + '.dWorldUpAxis', worldUpAxis)
    # Up Vector Start
    cmds.setAttr(ikSuffix + '.dWorldUpVectorX', 0)
    cmds.setAttr(ikSuffix + '.dWorldUpVectorY', 1)
    cmds.setAttr(ikSuffix + '.dWorldUpVectorZ', 0)
    # Up Vector End
    cmds.setAttr(ikSuffix + '.dWorldUpVectorEndX', 0)
    cmds.setAttr(ikSuffix + '.dWorldUpVectorEndY', 1)
    cmds.setAttr(ikSuffix + '.dWorldUpVectorEndZ', 0)
    # ##################################### #
    return result


# Position from center of list
# requires int as variables
##totalObjects = len(totalObjects)
# obj = 3, as in totalObjects[3]
# Returns list
# positive number = towards beginning of list, from center
# negative number = towards end of list, from center
##ie. beginning, 3, 2, 1, 0(center), -1, -2, -3, end
def posFromCenter(totalObjects, obj):
    centerOfList = (totalObjects - 1) / 2
    position = centerOfList - obj
    return position


# Calculates gradual weighting between two points with infinte objects between
# Multiplier is type of calculation
# 0 = linear weighting
# 1 = quadratic weighting
# Position
# position is derived from posFromCenter() in this module
# Returns
# 2 floats which add to 1.0
# use with on blend node or constraint with two incoming objects
def blendWeight(totalPositions, position, multiplier):
    weight = []
    falloff = 1

    # if totalPositions is zero, its likely there are only three joints involved
    # its assumed that the weight involved is for the center/middle position, append a weight of 0.5
    if totalPositions == 0:
        weight.append(0.5)
    else:
        # check multiplier state
        if multiplier == 1:
            falloff = 1 / ((0.5 / totalPositions) + 0.5)

        # check position of object from center and return weight(weight)
        if position > 0:
            # infront of middle position
            math = (0.5 / totalPositions) * (position * falloff)
            weight.append(0.5 + math)
            weight.append(1 - weight[0])
        elif position == 0:
            # middle position
            weight.append(0.5)
            weight.append(0.5)
        else:
            # behind middle position
            position = position * -1
            math = (0.5 / totalPositions) * (position * falloff)
            weight.append(1 - (0.5 + math))
            weight.append(0.5 + math)
    return weight


# Uses splineIK curve, joints involved and builds a node network for stretching
# curve = curve to use for stretch (ie. splineIK curve)
# jnts = spline joints
# blndSuffix = blend node suffix
# aim = axis that points down chain
# Return
# blendColor
def StretchNodes(blndSuffix, curve, jnts):
    # create math nodes
    # math
    crvInfo = cmds.arclen(curve, ch=True, n=(curve + '_arcLength'))
    crvLength = cmds.getAttr(crvInfo + '.arcLength')
    dvd = cmds.shadingNode('multiplyDivide', au=True, n=(curve + '_scale'))

    # set math nodes
    # set operation: 2 = divide, 1 = multiply
    cmds.setAttr((dvd + '.operation'), 2)

    # connect math nodes
    cmds.connectAttr((crvInfo + '.arcLength'), (dvd + '.input1Z'))
    # To Scale spline - figure out which groups scale will control dvdNodes value
    ##cmds.connectAttr(('?scaleGroup?' + '.scaleZ'), (dvd + '.input2Z'))

    # create and connect blends
    # assumes 'aimValue' point down chain
    blnd = []
    jj = 1
    for i in range(1, len(jnts), 1):
        # measure length, get translate(aimValue) value
        aimValue = cmds.getAttr(jnts[i] + '.translateX')
        # create stretch node
        ##
        mltpl = cmds.shadingNode('multiplyDivide', au=True, n=(curve + str(jj) + '_stretch'))
        cmds.setAttr((mltpl + '.operation'), 1)
        # multiplier = length of joint/default crv length
        cmds.setAttr((mltpl + '.input2Z'), (aimValue / crvLength))
        cmds.connectAttr((dvd + '.outputZ'), (mltpl + '.input1Z'))
        ##
        # create blend
        MidB = cmds.shadingNode('blendColors', name=(blndSuffix + str(jj) + '_Stretch'), asUtility=True)
        # set blend 'blender attr to 1'
        cmds.setAttr(MidB + '.blender', 1)
        # set color2B to 'aimValue'
        cmds.setAttr(MidB + '.color2B', aimValue)
        # connect mltpl output to blend color1B
        cmds.connectAttr((mltpl + '.outputZ'), (MidB + '.color1B'))
        # connect blend outputB to joint translateZ
        cmds.connectAttr((MidB + '.outputB'), (jnts[i] + '.translateX'))
        # store blend for return
        blnd.append(MidB)
        jj = jj + 1
    return blnd


def blendWeight2(List, i, function, falloff):
    '''
    Arguments:\n
        List = list of objects
        i = object
        function 0 = (ease in)
        function 1 = (ease out)
        function 2 = (ease in ease out)
        function 3 = (ease out ease in)\n
        falloff
        part of decay... not scripted yet
        <1 = (slower falloff)
        1< = (quicker falloff)        
        \r#decay 0 = default value
        \r#decay 1 = full decayed value
        \r#divide decay(1) by same number as angles then progressively add it through loop
        \r#division makes the falloff weighted towards  end (tall egg shape)
        \r#multiplication makes falloff weighted towards start (wide egg shape)
    '''
    weight = [None, None]
    decay = 0

    if function == 0:
        # Ease Out
        numOfPoints = len(List) - 1
        iDegree = 90 / numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff / numOfPoints
        else:
            decay = 0
        ##weight[0] = math.cos(math.radians(iDegree*i))
        weight[0] = math.cos(math.radians(iDegree * i))
        weight[1] = 1 - weight[0]
        weight[1] = weight[1] / math.exp(decay * (len(List) - (i)))
        weight[0] = 1 - weight[1]
        return weight
    elif function == 1:
        # Ease In
        numOfPoints = len(List) - 1
        iDegree = 90 / numOfPoints
        if falloff > 0.0 and falloff <= 1.0:
            decay = falloff / numOfPoints
        else:
            decay = 0
        ##weight[1] = math.sin(math.radians(iDegree*i))
        weight[1] = math.sin(math.radians(iDegree * i))
        weight[0] = 1 - weight[1]
        weight[0] = weight[0] / math.exp(decay * (i + 1))
        weight[1] = 1 - weight[0]
        return weight
    elif function == 2:
        # Ease Out Ease In
        numOfPoints = len(List) - 1
        iDegree = 180 / numOfPoints
        weight[0] = (math.cos(math.radians(iDegree * i)) * 0.5) + 0.5
        weight[1] = 1 - weight[0]
        return weight
    elif function == 3:
        # Ease In Ease Out
        numOfPoints = len(List) - 1
        iDegree = 180 / numOfPoints
        weight[1] = (math.sin(math.radians(iDegree * i)) * 0.5) + 0.5
        weight[0] = 1 - weight[1]
        return weight
    else:
        mel.eval('warning \"' + '////... Function needs a value between 0 and 3...////' + '\";')


def twistBlend(Name, obj1, obj2, obj3, attr):
    # Blends
    blends = []
    # blend for turning blend on/off
    onOff_Blnd = cmds.shadingNode('blendColors', name=(Name + '_onOffBlnd'), asUtility=True)
    cmds.setAttr(onOff_Blnd + '.blender', 1)
    # blend for weighting between obj1/obj2
    weight_Blnd = cmds.shadingNode('blendColors', name=(Name + '_weightBlnd'), asUtility=True)
    cmds.setAttr(weight_Blnd + '.blender', 0.5)

    # Nodes for blended value
    # blended values get added...
    DblLnr = cmds.createNode('addDoubleLinear', name=(Name + '_DblLnr'))
    # ...then divided by 2 to arrive at at a halfway point
    div = cmds.shadingNode('multiplyDivide', au=True, n=(Name + '_Div'))
    cmds.setAttr((div + '.operation'), 2)
    cmds.setAttr((div + '.input2X'), 2)

    # Connections
    # values to weight_Blnd
    if type(obj1) != list:
        cmds.connectAttr(obj1 + '.' + attr, weight_Blnd + '.color1R')
    else:
        # add values from items in obj1, maximum is 2.
        obj1_DblLnr = cmds.createNode('addDoubleLinear', name=(Name + '_Frst' + '_DblLnr'))
        cmds.connectAttr(obj1[0] + '.' + attr, obj1_DblLnr + '.input1')
        cmds.connectAttr(obj1[1] + '.' + attr, obj1_DblLnr + '.input2')
        cmds.connectAttr(obj1_DblLnr + '.output', weight_Blnd + '.color1R')

    if type(obj2) != list:
        cmds.connectAttr(obj2 + '.' + attr, weight_Blnd + '.color2R')
    else:
        # add values from items in obj2, maximum is 2.
        obj2_DblLnr = cmds.createNode('addDoubleLinear', name=(Name + '_Scnd' + '_DblLnr'))
        cmds.connectAttr(obj2[0] + '.' + attr, obj2_DblLnr + '.input1')
        cmds.connectAttr(obj2[1] + '.' + attr, obj2_DblLnr + '.input2')
        cmds.connectAttr(obj2_DblLnr + '.output', weight_Blnd + '.color2R')

    # weight_Blnd to onOff_Blnd
    cmds.connectAttr(weight_Blnd + '.outputR', onOff_Blnd + '.color1R')
    cmds.connectAttr(weight_Blnd + '.outputR', onOff_Blnd + '.color1G')
    # onOff_Blnd to DblLnr
    cmds.connectAttr(onOff_Blnd + '.outputR', DblLnr + '.input1')
    cmds.connectAttr(onOff_Blnd + '.outputG', DblLnr + '.input2')
    # DblLnr to div
    cmds.connectAttr(DblLnr + '.output', div + '.input1X')
    # div to obj3
    cmds.connectAttr(div + '.outputX', obj3 + '.' + attr)
    blends.append(onOff_Blnd)
    blends.append(weight_Blnd)
    return blends
