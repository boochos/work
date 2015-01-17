import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel


def addAttribute(objList, attrList, minimum, maximum, keyable, attrType):
    """
    #\n
    objList = object
    attrList = list of attributes to add
    minimum = minimum value to set
    maximum = maximum value to set
    keyable = True or False
    attrType = type of value (int, float, long, enum, bool...)
    """
    if type(objList) != list:
        if type(attrList) != list:
            cmds.addAttr(objList, ln=attrList, at=attrType, min=minimum, max=maximum, h=False)
            cmds.setAttr((objList + '.' + attrList), cb=True)
            cmds.setAttr((objList + '.' + attrList), k=keyable)
        else:
            for attr in attrList:
                cmds.addAttr(objList, ln=attr, at=attrType, min=minimum, max=maximum)
                cmds.setAttr((objList + '.' + attr), cb=True)
                cmds.setAttr((objList + '.' + attr), k=keyable)

    elif len(objList) > 0:
        if len(attrList) > 0:
            for obj in objList:
                if type(attrList) != list:
                    cmds.addAttr(obj, ln=attrList, at=attrType, min=minimum, max=maximum)
                    cmds.setAttr((obj + '.' + attrList), cb=True)
                    cmds.setAttr((obj + '.' + attrList), k=keyable)
                else:
                    for attr in attrList:
                        cmds.addAttr(obj, ln=attr, at=attrType, min=minimum, max=maximum)
                        cmds.setAttr((obj + '.' + attr), cb=True)
                        cmds.setAttr((obj + '.' + attr), k=keyable)

        else:
            mel.eval('warning \"' + '////... Second argument -attrList- is empty...////' + '\";')
    else:
        mel.eval('warning \"' + '////... First argument -objList- is of the wrong type. List or String is expected...////' + '\";')

def hijackVis(obj1, obj2, name='', suffix=True, default=None, mode='visibility'):
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
    # #create suffix
    if suffix == True:
        suffix = name + '_Vis'
        addAttribute(obj2, suffix, 0, 1, False, 'long')
        cmds.connectAttr(obj2 + '.' + suffix, obj1 + '.' + mode)
    else:
        # #OLD elif suffix == False:
        suffix = name
    if cmds.attributeQuery(suffix, node=obj2, ex=True) == True:
        cmds.connectAttr(obj2 + '.' + suffix, obj1 + '.' + mode)
    else:
        addAttribute(obj2, suffix, 0, 1, False, 'long')
        cmds.connectAttr(obj2 + '.' + suffix, obj1 + '.' + mode)
    if default != None:
        cmds.setAttr(obj2 + '.' + suffix, default)
        vis = obj2 + '.' + suffix
        return vis

def hijackAttrs(obj1, obj2, attrOrig, attrNew, set=False, default=None):
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
    K = cmds.getAttr(obj1 + '.' + attrOrig, k=True)
    TYP = cmds.getAttr(obj1 + '.' + attrOrig, typ=True)
    if TYP == 'enum':
        ENM = cmds.attributeQuery(attrOrig, node=obj1, le=True)[0]
    if cmds.attributeQuery(attrOrig, node=obj1 , sme=True) == 1:
        SMIN = cmds.attributeQuery(attrOrig, node=obj1 , smn=True)[0]
        # #print SMIN
    if cmds.attributeQuery(attrOrig, node=obj1 , sme=True) == 1:
        SMAX = cmds.attributeQuery(attrOrig, node=obj1 , smx=True)[0]
        # #print SMAX
    if cmds.attributeQuery(attrOrig, node=obj1 , mne=True) == 1:
        MIN = cmds.attributeQuery(attrOrig, node=obj1 , min=True)[0]
        # #print MIN
    if cmds.attributeQuery(attrOrig, node=obj1 , mxe=True) == 1:
        MAX = cmds.attributeQuery(attrOrig, node=obj1 , max=True)[0]
        # #print MAX
    L = cmds.getAttr(obj1 + '.' + attrOrig, l=True)
    CB = cmds.getAttr(obj1 + '.' + attrOrig, cb=True)
    V = cmds.getAttr(obj1 + '.' + attrOrig)
    attrState = attrOrig, K, TYP, MIN, MAX, L, CB, V, ENM

    # recreate attrs on obj2 from obj1, connect attrs
    if TYP == 'enum':
        cmds.addAttr(obj2, ln=attrNew, k=K, at=TYP, en=ENM)
        cmds.setAttr(obj2 + '.' + attrNew, V)
    else:
        cmds.addAttr(obj2, ln=attrNew, k=K, at=TYP)
    if SMIN != None:
        cmds.addAttr(obj2 + '.' + attrNew, e=True, smn=SMIN)
    if SMAX != None:
        cmds.addAttr(obj2 + '.' + attrNew, e=True, smx=SMAX)
    if MIN != None:
        cmds.addAttr(obj2 + '.' + attrNew, e=True, min=MIN)
    if MAX != None:
        cmds.addAttr(obj2 + '.' + attrNew, e=True, max=MAX)
    cmds.setAttr(obj2 + '.' + attrNew, l=L)
    if K == False:
        cmds.setAttr(obj2 + '.' + attrNew, cb=CB)
    cmds.setAttr(obj2 + '.' + attrNew, V)

    # connect attr
    cmds.connectAttr(obj2 + '.' + attrNew, obj1 + '.' + attrOrig)

    # override keyable
    if set != False:
        cmds.setAttr(obj2 + '.' + attrNew, k=False)
        cmds.setAttr(obj2 + '.' + attrNew, cb=True)
    if default != None:
        cmds.setAttr(obj2 + '.' + attrNew, default)
        attr = obj2 + '.' + attrNew
        return attr

def hijackCustomAttrs(obj1, obj2):
    """\n
    obj1 = slave\n
    obj2 = master\n
    format = list [object] [attr, keyable, type, min, max, lock, channelBox, [enums]]\n
    """
    UsrAttr = cmds.listAttr(obj1, ud=True)
    hAttrs = []
    ENM = []
    # collect custom attrs from obj1
    for attr in UsrAttr:
        K = cmds.getAttr(obj1 + '.' + attr, k=True)
        TYP = cmds.getAttr(obj1 + '.' + attr, typ=True)
        if TYP == 'enum':
            ENM = cmds.attributeQuery(attr, node=obj1, le=True)[0]
        if cmds.attributeQuery(attr, node=obj1 , mne=True) == 1:
            MIN = cmds.attributeQuery(attr, node=obj1 , min=True)[0]
        else:
            MIN = None
        if cmds.attributeQuery(attr, node=obj1 , mxe=True) == 1:
            MAX = cmds.attributeQuery(attr, node=obj1 , max=True)[0]
        else:
            MAX = None
        L = cmds.getAttr(obj1 + '.' + attr, l=True)
        CB = cmds.getAttr(obj1 + '.' + attr, cb=True)
        V = cmds.getAttr(obj1 + '.' + attr)
        attrState = attr, K, TYP, MIN, MAX, L, CB, V, ENM
        hAttrs.append(attrState)
    # recreate attrs on obj2 from obj1, connect attrs
    for i in range(0, len(hAttrs), 1):
        if hAttrs[i][2] == 'enum':
            cmds.addAttr(obj2, ln=hAttrs[i][0], k=hAttrs[i][1], at=hAttrs[i][2], en=hAttrs[i][8])
            cmds.setAttr(obj2 + '.' + hAttrs[i][0], hAttrs[i][7])
        else:
            cmds.addAttr(obj2, ln=hAttrs[i][0], k=hAttrs[i][1], at=hAttrs[i][2])
        if hAttrs[i][3] != None:
            cmds.addAttr(obj2 + '.' + hAttrs[i][0], e=True, min=hAttrs[i][3])
        if hAttrs[i][4] != None:
            cmds.addAttr(obj2 + '.' + hAttrs[i][0], e=True, max=hAttrs[i][4])
        cmds.setAttr(obj2 + '.' + hAttrs[i][0], l=hAttrs[i][5])
        if hAttrs[i][1] == False:
            cmds.setAttr(obj2 + '.' + hAttrs[i][0], cb=hAttrs[i][6])
        cmds.setAttr(obj2 + '.' + hAttrs[i][0], hAttrs[i][7])

    for attr in UsrAttr:
        cmds.connectAttr(obj2 + '.' + attr, obj1 + '.' + attr)

def hijackScale(obj1, obj2):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    cmds.connectAttr(obj2 + '.scaleX', obj1 + '.scaleX')
    cmds.connectAttr(obj2 + '.scaleY', obj1 + '.scaleY')
    cmds.connectAttr(obj2 + '.scaleZ', obj1 + '.scaleZ')

def hijack(obj1, obj2, translate=True, rotate=True, scale=True, visibility=True):
    '''\n
    obj1 = slave
    obj2 = master
    '''
    if translate == True:
        cmds.connectAttr(obj2 + '.translateX', obj1 + '.translateX')
        cmds.connectAttr(obj2 + '.translateY', obj1 + '.translateY')
        cmds.connectAttr(obj2 + '.translateZ', obj1 + '.translateZ')
    if rotate == True:
        cmds.connectAttr(obj2 + '.rotateX', obj1 + '.rotateX')
        cmds.connectAttr(obj2 + '.rotateY', obj1 + '.rotateY')
        cmds.connectAttr(obj2 + '.rotateZ', obj1 + '.rotateZ')
    if scale == True:
        cmds.connectAttr(obj2 + '.scaleX', obj1 + '.scaleX')
        cmds.connectAttr(obj2 + '.scaleY', obj1 + '.scaleY')
        cmds.connectAttr(obj2 + '.scaleZ', obj1 + '.scaleZ')
    if visibility == True:
        cmds.connectAttr(obj2 + '.visibility', obj1 + '.visibility')
