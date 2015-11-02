import maya.cmds as cmds
import maya.mel as mel
import atom_placement_lib as place
import atom_miscellaneous_lib as misc
import atom_ui_lib as ui
import os

# place Clusters on CV derived from 'curve' variable
# curve
# curve from which to make clusters
# clstrSuffix
# suffix for cluster


def clstrOnCV(curve, clstrSuffix):
    clstr = []
    i = 0
    num = cmds.getAttr((curve + '.cv[*]'))
    for item in num:
        c = cmds.cluster((curve + '.cv[' + str(i) + ']'), n=(clstrSuffix + str(i)), envelope=True)[1]
        i = i + 1
        clstr.append(c)
    return clstr

# places curve on points derived from selection


def curve(name, points):
    '''\n
    name = name...
    points = list of objects from which xfrom can be derived
    '''
    pos = []
    if len(points) > 2:
        for item in points:
            x = cmds.xform(item, q=True, t=True, ws=True)
            pos.append(x)
        curve = cmds.curve(p=pos, name=(name), d=2)
        return curve
    else:
        mel.eval('warning \"' + '////... select 3 objects ...////' + '\";')
        return None

# place joints on positions derived from selection
# order(boolean) = placement order
# 0 = first to last selected object
# 1 = last to first selected object
# jntSuffix
# suffix for joints


def joint(order, jntSuffix, pad=2, rpQuery=True):
    sel = cmds.ls(sl=True, fl=True, l=True)
    if len(sel) > 0:
        if order == 0:
            jnt = []
            cmds.select(cl=True)
            i = 1
            for item in sel:
                if rpQuery == True:
                    pos = cmds.xform(item, q=True, rp=True, ws=True)
                else:
                    pos = cmds.xform(item, q=True, t=True, ws=True)
                plc = cmds.joint(name=(jntSuffix + '_' + str(('%0' + str(pad) + 'd') % (i))), p=pos)
                jnt.append(plc)
                i = i + 1
            cmds.select(sel)
            return jnt
        elif order == 1:
            rvrsSel = []
            for i in range(len(sel), 0, -1):  # (reverse order loop - range(size of(array),stop@,increment by)
                rvrsSel.append(sel[i - 1])
            sel = list(rvrsSel)
            jnt = []
            cmds.select(cl=True)
            for item in sel:
                if rpQuery == True:
                    pos = cmds.xform(item, q=True, rp=True, ws=True)
                else:
                    pos = cmds.xform(item, q=True, t=True, ws=True)
                plc = cmds.joint(name=(jntSuffix + '#'), p=pos)
                jnt.append(plc)
            cmds.select(sel)
            return jnt
    else:
        mel.eval('warning \"' + '////... select at least one object ...////' + '\";')
        return None

# place locators on positions derived from selection
# locSuffix
# suffix for spaceLocators


def loc(locSuffix, obj=None):
    sel = []
    if obj == None:
        sel = cmds.ls(sl=True, fl=True, l=True)
    else:
        sel.append(obj)
    if len(sel) > 0:
        loc = []
        cmds.select(cl=True)
        for item in sel:
            pos = cmds.xform(item, q=True, t=True, ws=True)
            rot = cmds.xform(item, q=True, ro=True, ws=True)
            n = cmds.spaceLocator(name=locSuffix)[0]
            cmds.xform(n, t=(pos), ro=(rot))
            loc.append(n)
        cmds.select(sel)
        # returns list
        return loc
    else:
        mel.eval('warning \"' + '////... select at least one object ...////' + '\";')
        return None

# place nulls on positions derived from selection
# nllSuffix
# suffix for null


def null(nllSuffix, order=None):
    sel = cmds.ls(sl=True, fl=True, l=True)
    if len(sel) > 0:
        null = []
        cmds.select(cl=True)
        for item in sel:
            pos = cmds.xform(item, q=True, rp=True, ws=True)
            rot = cmds.xform(item, q=True, ro=True, ws=True)
            n = cmds.group(name=nllSuffix, em=True)
            if order != None:
                cmds.xform(n, roo=order)
            cmds.xform(n, t=pos, ro=rot)
            null.append(n)
        cmds.select(sel)
        return null

    else:
        mel.eval('warning \"' + '////... select at least one object ...////' + '\";')
        return None

# place circle
# name     = name of circle
# obj      = object whose position to match
# shape    = shape of circle to import(name of text file)
# sections = number of CVs
# degree   = Linear(1) or Cubic(3) ,has to be int
# normal   = plane on which to build circle


def circle(name, obj, shape, size, color, sections=8, degree=1, normal=(0, 0, 1), orient=True):
    path = os.path.expanduser('~') + '/GitHub/controlShapes/'
    Circle = []
    if type(obj) != list:
        pos = cmds.xform(obj, q=True, rp=True, ws=True)
        rot = cmds.xform(obj, q=True, ro=True, ws=True)
        n = cmds.circle(name=name, center=(0, 0, 0), normal=normal, sweep=360, radius=1, degree=degree, sections=sections, constructionHistory=1)[0]
        cmds.xform(n, t=pos)
        if orient == True:
            cmds.xform(n, ro=rot)
        else:
            print 'no orient'
        Circle.append(n)
        ##import shape
        cmds.select(n)
        ui.importCurveShape(shape, path, size, color)
        return Circle
    elif len(obj) > 0:
        for item in obj:
            pos = cmds.xform(item, q=True, rp=True, ws=True)
            rot = cmds.xform(item, q=True, ro=True, ws=True)
            n = cmds.circle(name=name, center=(0, 0, 0), normal=normal, sweep=360, radius=1, degree=degree, sections=sections, constructionHistory=1)[0]
            cmds.xform(n, t=pos, ro=rot)
            Circle.append(n)
            cmds.select(n)
            ui.importCurveShape(shape, path, size, color)
        return Circle

    else:
        mel.eval('warning \"' + '////... No object specified under \'obj\' variable ...////' + '\";')
        return None

# Version 2 (no selection required, state object(s) to match as variable "obj")
# place nulls on positions derived from selection
# nllSuffix
# suffix for null


def null2(nllSuffix, obj, orient=True):
    null = []
    if type(obj) != list:
        pos = cmds.xform(obj, q=True, rp=True, ws=True)
        rot = cmds.xform(obj, q=True, ro=True, ws=True)
        n = cmds.group(name=nllSuffix, em=True)
        cmds.xform(n, t=pos, ro=rot, ws=True)
        if orient == False:
            cmds.xform(n, ro=(0, 0, 0))
        null.append(n)
        return null
    elif len(obj) > 0:
        for item in obj:
            pos = cmds.xform(item, q=True, rp=True, ws=True)
            rot = cmds.xform(item, q=True, ro=True, ws=True)
            n = cmds.group(name=nllSuffix, em=True)
            cmds.xform(n, t=pos, ro=rot, ws=True)
            if orient == False:
                cmds.xform(n, ro=(0, 0, 0))
            null.append(n)
        return null
    else:
        mel.eval('warning \"' + '////... \"obj\" variable must be a single object or list type ...////' + '\";')
        return None

# places controller object(controller, controllerOffset, group)


class Controller():
    # initialize

    def __init__(self, name, obj, orient=True, shape='diamond_ctrl', size=1, color=8, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=False):
        self.name = name
        self.obj = obj
        self.orient = orient
        self.shape = shape
        self.size = size
        self.color = color
        self.sections = sections
        self.degree = degree
        self.normal = normal
        self.setChannels = setChannels
        self.groups = groups

    # conditions
    def condition(self):
        if type(self.obj) == list:
            if len(self.obj) == 1:
                self.createController()
            else:
                mel.eval('warning \"' + '////... \'obj\' variable has to be only item in list ...////' + '\";')
        elif len(self.obj) > 0:
            self.createController()
        else:
            mel.eval('warning \"' + '////... \'obj\' variable can only be one object...////' + '\";')

    # create
    def createController(self):
        ct = place.circle(self.name, self.obj, self.shape, self.size * (0.3), self.color, self.sections, self.degree, self.normal)[0]
        ctO = place.circle(self.name + '_Offset', self.obj, self.shape, self.size * (0.25), self.color, self.sections, self.degree, self.normal)[0]
        gp = place.null2(self.name + '_Grp', self.obj)[0]
        if self.groups == True:
            ctgp = place.null2(self.name + '_CtGrp', self.obj)[0]
            topgp = place.null2(self.name + '_TopGrp', self.obj)[0]
            cmds.parent(ct, ctgp)
            cmds.parent(ctgp, topgp)
            if self.setChannels == True:
                misc.setChannels(ctgp, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False], other=[False, True])
                misc.setChannels(topgp, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False], other=[False, True])

        # parent
        cmds.parent(gp, ctO)
        cmds.parent(ctO, ct)
        # align orient query
        if self.orient == False:
            if self.groups == True:
                cmds.setAttr(topgp + '.rotate', 0, 0, 0)
            else:
                cmds.setAttr(ct + '.rotate', 0, 0, 0)
        elif self.orient != False and self.orient != True:
            rot = cmds.xform(self.orient, query=True, ws=True, ro=True)
            if self.groups == True:
                cmds.setAttr(topgp + '.rotate', rot[0], rot[1], rot[2])
            else:
                cmds.setAttr(ct + '.rotate', rot[0], rot[1], rot[2])
        # attrs
        # ct
        attr = 'Offset_Vis'
        misc.addAttribute(ct, 'Offset_Vis', 0, 1, False, 'long')
        # ctO
        cmds.connectAttr(ct + '.' + attr, ctO + '.visibility')
        # gp
        # Done
        cmds.select(cl=True)
        if self.setChannels == True:
            misc.setChannels(ct, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False], other=[False, True])
            misc.setChannels(ctO, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[False, False, False], other=[False, True])
            misc.setChannels(gp, translate=[False, True], rotate=[False, True], scale=[True, False], visibility=[True, False, False], other=[False, True])
            cmds.setAttr(ctO + '.visibility', cb=False)
            i = cmds.getAttr(ctO + '.visibility', cb=True)

        if self.groups == True:
            return topgp, ctgp, ct, ctO, gp
        else:
            return ct, ctO, gp


def twoJointPV(name, ik, distance=1, constrain=True, size=1):
    sj = cmds.ikHandle(ik, q=True, sj=True)
    Gp = place.null2(name + '_PvGrp', sj, False)[0]
    Pv = place.circle(name + '_PV', sj, 'diamond_ctrl', size * 1, 17, 8, 1, (0, 0, 1))[0]
    cmds.parent(Pv, Gp)
    X = cmds.getAttr(ik + '.poleVectorX')
    Y = cmds.getAttr(ik + '.poleVectorY')
    Z = cmds.getAttr(ik + '.poleVectorZ')
    cmds.setAttr(Pv + '.translateX', distance * X)
    cmds.setAttr(Pv + '.translateY', distance * Y)
    cmds.setAttr(Pv + '.translateZ', distance * Z)
    if constrain == True:
        cmds.poleVectorConstraint(Pv, ik)
    return Gp, Pv


def controllerDownChain(root, name, pad=2, base=None, parent=None, shape='loc_ctrl',
                        color=17, size=10, groups=True, orient=False, suffix=None,
                        scale=True, setChannel=True, clone=False, fk=False):
    '''\n

    '''
    result = []
    control_chain = []
    clone_chain = []
    cmds.select(root, hi=True)
    sel = cmds.ls(sl=True, typ='transform')
    i = 1
    for obj in sel:
        if pad > 0:
            num = '_' + str(('%0' + str(pad) + 'd') % (i))
        else:
            num = ''
        # SUFFIX
        if suffix != None:
            ctrl = place.Controller(name + num + '_' + suffix, obj, shape=shape, color=color, size=size, groups=groups, orient=orient)
        else:
            ctrl = place.Controller(name + num, obj, shape=shape, color=color, size=size, groups=groups, orient=orient)
        Control = ctrl.createController()
        control_chain.append(Control)
        # CLONE
        if clone == False:
            cmds.parentConstraint(Control[4], obj, mo=True)
        else:
            clone_parent = place.null2(Control[2] + '_CloneTopGrp', obj, orient)[0]
            clone_child = place.null2(Control[2] + '_CloneCtGrp', obj, orient)[0]
            clone_offset = place.null2(Control[2] + '_CloneOffstGrp', obj, orient)[0]
            cmds.parentConstraint(clone_offset, obj, mo=True)
            clone_set = [clone_parent, clone_child, clone_offset]
            clone_chain.append(clone_set)
            cmds.parent(clone_offset, clone_child)
            cmds.parent(clone_child, clone_parent)
            misc.hijack(clone_offset, Control[3], scale=False, visibility=False)
            misc.hijack(clone_child, Control[2], scale=False, visibility=False)
        # BASE
        if base != None:
            cmds.parentConstraint(base, Control[0], mo=True)
        # PARENT
        if parent != None:
            cmds.parent(Control[0], parent)
        # SETCHANNEL
        if setChannel != True:
            for item in Control:
                misc.setChannels(item, translate=[False, True], rotate=[False, True], scale=[False, True], visibility=[True, False, False])
        # SCALE
        if scale == True:
            if clone == False:
                misc.hijackScale(obj, Control[2])
            else:
                misc.hijackScale(obj, clone_child)
                misc.hijackScale(clone_child, Control[2])
                misc.scaleUnlock(Control[2])
        i = i + 1
    # FK
    if fk == True:
        num = len(control_chain)
        j = 1
        for item in control_chain:
            if num > j:
                cmds.parent(control_chain[j][0], item[2])
                cmds.parentConstraint(item[3], control_chain[j][0], mo=True)
                if clone == True:
                    cmds.parent(clone_chain[j][0], clone_chain[j - 1][2])
            j = j + 1
    return control_chain, clone_chain


def match(obj1, obj2, p=True, r=True):
    if p == True:
        pos1 = cmds.xform(obj1, q=True, t=True, ws=True)
        print 'from', pos1
        pos2 = cmds.xform(obj2, q=True, t=True, ws=True)
        print 'to', pos2
        cmds.xform(obj2, t=(pos1))
        pos2 = cmds.xform(obj2, q=True, t=True, ws=True)
        print 'to', pos2
    if r == True:
        rot = cmds.xform(obj1, q=True, ro=True, ws=True)
        cmds.xform(obj2, ro=(rot))
