from pymel.core import *
import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')
jnt = web.mod('atom_joint_lib')
spln = web.mod('atom_spline_lib')
ui = web.mod('atom_ui_lib')


class SplineFK(object):

    '''\n
    This is different form snake splineFk, which is not a class.
    The extra cvs(second,second last position) that get created with auto curve creation are not used, thereby simplifing the spline creation.
    ik:options= None, 'ik', 'splineIK'
    '''

    def __init__(self, name, startJoint, endJoint, suffix, direction=0, controllerSize=1, rootParent=None, parent1=None, parent2=None, parentDefault=[1, 1], segIteration=4, stretch=0, ik=None, colorScheme='yellow'):
        '''\n
        ik:options= None, 'ik', 'splineIK'
        colorScheme = red, blue, yellow
        '''
        self.name = name
        self.startJoint = startJoint
        self.endJoint = endJoint
        self.suffix = suffix
        self.segmentIteration = segIteration
        self.segmentAttr = 'Segments'
        self.stretch = stretch
        self.colorScheme = colorScheme
        # Direction refers to which icon to use at the start of the controller creation
        self.direction = direction
        self.iconList = ['splineStart_ctrl', 'diamond_ctrl', 'facetZup_ctrl']
        self.ctrlList = []
        self.controlerSize = controllerSize
        self.rootParent = rootParent
        self.parent1 = parent1
        self.parent2 = parent2
        self.skinJoints = jnt.getJointChainHier(self.startJoint, self.endJoint)
        self.ikJoints = None
        self.ikCurve = None
        self.firstCntCt = None
        self.ctParent = None
        self.clusterList = None
        self.clusterGrp = None
        self.baseCtrl = None
        self.vcParent = []
        self.FK = parentDefault[0]
        self.driven = parentDefault[1]
        self.ik = ik
        self.seg = None
        self.segB = [6, 18]
        self.segR = [13, 20]
        self.segY = [17, 22]
        self.topGrp1 = []
        self.topGrp2 = []
        self.ps1_Jnt = None
        self.rootCt = []

        # colorScheme
        if self.colorScheme == 'red':
            self.seg = self.segR
        elif self.colorScheme == 'blue':
            self.seg = self.segB
        else:
            self.seg = self.segY

        # Build

        # master groups
        self.masterGp = cmds.group(em=True, n='splineFk_' + name)
        self.ctGp = cmds.group(em=True, n='splineFK_Ct__' + name)  # scale plug group
        self.utilGp = cmds.group(em=True, n='splineFK_Util__' + name)
        self.hideGp = cmds.group(em=True, n='splineFK_Hide__' + name)
        self.hideJntGp = cmds.group(em=True, n='splineFK_JntHide__' + name)
        cmds.parent(self.ctGp, self.masterGp)
        cmds.parent(self.utilGp, self.masterGp)
        cmds.parent(self.hideGp, self.masterGp)
        cmds.parent(self.hideJntGp, self.hideGp)
        cmds.setAttr(self.hideGp + '.visibility', 0)
        # scale joint group constraint
        cmds.scaleConstraint(self.ctGp, self.hideJntGp)
        place.cleanUp(self.masterGp, Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
        place.cleanUp(self.utilGp, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)

        # places ik joints if ik does not equal None
        self.placeIkJnts()
        # constrains objects in self.clusterList, created in self.placeIkJnts() and checks if 'ik' was flagged.
        # if 'ik' was flagged upvectors need to be built, the vector function is run automatically as it needs to be in a specific order.
        self.parentClusters()

    def nameBuilder(self, name):
        if self.suffix != None:
            return name + '_' + self.suffix
        else:
            return name

    def createController(self, name, orientObj, handle, color, orient=True, ctrlType=['special', 'first']):
        cnt = None
        if ctrlType[0] == 'special':
            if ctrlType[1] == 'first':
                cnt = place.Controller(self.nameBuilder(name), orientObj, orient=orient,
                                       shape=self.iconList[0], size=self.controlerSize * 1.35, color=color, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
                cntCt = cnt.createController()
                self.rootCt = cntCt
                place.setRotOrderWithXform(cntCt[0], 'zxy', True)
                self.baseCtrl = cntCt[2]
            else:
                cnt = place.Controller(self.nameBuilder(name), orientObj, orient=orient,
                                       shape=self.iconList[1], size=self.controlerSize * .25, color=color, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
                cntCt = cnt.createController()
                place.setRotOrder(cntCt[4], 2, False)
                place.setRotOrder(cntCt[2], 3, False)
        else:
            cnt = place.Controller(self.nameBuilder(name), orientObj, orient=orient,
                                   shape=self.iconList[2], size=self.controlerSize, color=color, sections=8, degree=1, normal=(0, 0, 1), setChannels=True, groups=True)
            cntCt = cnt.createController()
            place.setRotOrder(cntCt[4], 2, False)
            place.setRotOrder(cntCt[2], 3, False)
        # place.cleanUp(cntCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
        cmds.parent(cntCt[0], self.masterGp)
        return cntCt

    def setParents(self):
        pass

    def placeIkJnts(self):
        '''\n

        '''
        #
        #
        # IK or no IK
        if self.ik == None:
            # add argument to class for no spline, straight parent constraints on joints
            self.clusterList = self.skinJoints
        else:
            # select the skinJoints
            select(self.skinJoints)

            # create the spln chain, creating a new joint for each selected join
            self.ikJoints = place.joint(0, self.nameBuilder(self.name + '_Spln_jnt'))
            # try to clean up groups
            # place.cleanUp(self.ikJoints[0], Ctrl=False, SknJnts=True, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
            cmds.parent(self.ikJoints[0], self.hideJntGp)

            # hardcoding 'oj' value. Shouldn't be any different. Otherwise spline up vector breaks.
            joint(self.ikJoints[0], e=True, oj='xyz', sao='yup', ch=True)
            for item in self.ikJoints:
                jnt.ZeroJointOrient(item)

            # ls(self.ikJoints[len(self.ikJoints)-1])[0].jointOrientX.set(0)
            # ls(self.ikJoints[len(self.ikJoints)-1])[0].jointOrientY.set(0)
            # ls(self.ikJoints[len(self.ikJoints)-1])[0].jointOrientZ.set(0)
        #
        #
        # Type of IK
        if self.ik == 'ik':
            ikh = []
            # first joint has no ik, append it to cluster list
            ikh.append(self.ikJoints[0])
            # add ik handles through chain
            for i in range(1, len(self.ikJoints), 1):
                ikh.append(cmds.ikHandle(sj=self.ikJoints[i - 1], ee=self.ikJoints[i], sol='ikRPsolver')[0])  # get ikHandle only
            self.clusterList = ikh
            # skin joints are not yet constrained to the new ik joints as they will move/pop once the pole vector constraint is added to the ik joints.
            # the constraint is created in vectors def
        elif self.ik == 'splineIK':
            # point constrain skin joints to ik joints
            for i in range(0, len(self.skinJoints), 1):
                if i != 0:
                    if i != 1:
                        pointConstraint(self.ikJoints[i], self.skinJoints[i], mo=True)

            # spline ik
            # build spline
            ikhandle = spln.splineIK(self.nameBuilder(self.name), ls(self.ikJoints[0])[0].name(), ls(self.ikJoints[len(self.ikJoints) - 1])[0].name(), 2, curve=True)
            ls(ikhandle[0])[0].visibility.set(0)
            # try and clean up
            cmds.parent(ikhandle[0], self.hideGp)
            cmds.parent(ikhandle[2], self.hideGp)
            self.ikCurve = ikhandle[2]

            # CLUSTERS
            # ret
            self.clusterList = place.clstrOnCV(self.ikCurve, self.nameBuilder('Clstr'))
            self.clusterGrp = place.null2(self.nameBuilder(self.name + 'Spline_ClstrGrp'), self.clusterList[0], orient=True)[0]
            for item in self.clusterList:
                parent(item, self.clusterGrp)

            place.cleanUp(self.ikCurve, World=True)

            # try to cleanup cluster group, turn visibility off
            # place.cleanUp(self.clusterGrp, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)
            cmds.parent(self.clusterGrp, self.hideGp)
            ls(self.clusterGrp)[0].visibility.set(0)

    def Stretch(self, attr='OffOn'):
        '''\n
        -should add squash stretch option in addition to length compensate.
        -if 'ik' type is selected this currently breaks, will needs its own arguement
        -need to add squash option to the rig. base squash def will have to be upgraded to include:
        length compensate attr
        squash attr
        min squash attr
        max squash attr
        '''
        # create the driving attribute
        place.optEnum(self.baseCtrl, attr='Stretch')
        place.addAttribute(self.baseCtrl, attr, minimum=0, maximum=1, keyable=True, attrType='double')
        cmds.setAttr(self.baseCtrl + '.' + attr, self.stretch)

        #
        #
        # build length compensate nodes
        if self.ik == 'ik':
            # currently no solution, needs node network to stretch, may be too heavy as a practicle solution
            pass
            '''
            for i in range(1, len(self.ikJoints), 1):
		controller = self.vcParent[i]
		#print self.vcParent[i] , '\n', self.ikJoints[i], '\n'
		constraint = cmds.parentConstraint(controller, self.ikJoints[i], mo=True)[0]
		print constraint
		UsrAttr = cmds.listAttr(constraint, ud=True)
		for weight in UsrAttr:
		    if controller in weight:
			cmds.connectAttr(constraint + '.' + weight, self.baseCtrl + '.' + attr)
		        '''
            # get attr in constraint with controller name
            # hijack to attr var
        elif self.ik == 'splineIK':
            # node structure for spline type length compensate, this not squash/stretch
            BlendNodes = spln.StretchNodes(self.nameBuilder(self.name), self.ikCurve, self.ikJoints)
            for node in BlendNodes:
                # connect blender attr of returned blend nodes
                connectAttr(self.baseCtrl + '.' + attr, node + '.blender')
        else:
            print '________________ ' + str(self.ik) + ' is not an ik variable option ________________'

    def vectors(self):
        '''\n

        '''
        # vars
        i = 1
        j = 0
        upVctr = []
        color = self.seg[0]
        visAttr = 'Vectors'
        # guide group
        # guide group is a null which houses templated lines between controllers and the corolating up vectors
        # all guides are parented under the guide group
        guideGp = cmds.group(em=True, name=self.nameBuilder(self.name + '_UpVctrGdGrp'))
        # the vis attr of guide group is connectged to an attr on the base controller
        place.addAttribute(self.baseCtrl, visAttr, 0, 1, False, 'long')
        place.hijackVis(guideGp, self.baseCtrl, name=visAttr, suffix=False, default=0)
        # try to cleanup
        cmds.parent(guideGp, self.utilGp)
        # place.cleanUp(guideGp, World=True)

        #
        #
        # place vectors
        for item in self.skinJoints[2:]:
            # controller gets placed on skin joint positions
            orntObj = str(ls(item)[0].getParent())
            cntCt = self.createController(self.name + '_upVctr_' + str(('%0' + str(2) + 'd') % (i)), orntObj, item, color, ctrlType=['special', ''])
            # try and cleanup
            # place.cleanUp(cntCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
            cmds.parent(cntCt[0], self.ctGp)
            # vis of controller is connected to base vis controller, teh attr was created above, outside the for loop.
            place.hijackVis(cntCt[2], self.baseCtrl, name=visAttr, suffix=False, default=0)
            # rotations and scales are locked for the controller and controller offset nodes
            place.setChannels(cntCt[2], translate=[False, True], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
            place.setChannels(cntCt[3], translate=[False, True], rotate=[True, False], scale=[True, False], visibility=[True, False, False])
            # create guide
            guide = place.guideLine(cntCt[4], self.ikJoints[i], 'connect')
            # parent guide
            cmds.parent(guide[0], guideGp)
            cmds.parent(guide[1][0], guideGp)
            cmds.parent(guide[1][1], guideGp)
            # get a starting value for height of vectors
            # value is derived from the local translate Z value of the second skin Joint
            Y = ls(self.skinJoints[2])[0].tz.get()
            # set height value of Ct group in controller list
            cmds.setAttr(cntCt[1] + '.ty', Y * 1.75)

            #
            #
            # create constraints for spline type ik, create list for RP type ik that will be fed to the loop below for the PV constraints
            if i == 1:
                upVctr.append(cntCt[4])
                if self.ik == 'splineIK':
                    cmds.aimConstraint(self.ikJoints[i + 1], self.skinJoints[i], mo=True, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType='object', worldUpObject=cntCt[4])
            elif i == len(self.ikJoints):
                upVctr.append(cntCt[4])
            else:
                upVctr.append(cntCt[4])
                if self.ik == 'splineIK':
                    cmds.aimConstraint(self.ikJoints[i + 1], self.skinJoints[i], mo=True, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType='object', worldUpObject=cntCt[4])
                j = j + 1

            # parent constraint for upVector/poleVector
            # self.vcParent is created in self.parentClusters() funtion
            cmds.parentConstraint(self.vcParent[i], cntCt[0], w=1, mo=True)

            # step increment
            i = i + 1

            #
            #
            # check state of segment iteration for a color change
            # segment length is set as top level arguement
            # if segmentIteration has reached limit value, reset j=0, change color
            if j == self.segmentIteration:
                # figure out what the current color is and switch to the opposite
                if color == self.seg[0]:
                    color = self.seg[1]
                else:
                    color = self.seg[0]
                j = 0
        #
        #
        # This condition is easier to run outside the main loop as the iteration is backwards
        # running it backwards prevents the ik joints from moving as the constraints are added.
        # if the proper order were to be used the chain would continually offset down the chain, as the orientation on a 2 joint ik chain is unpredictable.
        if self.ik == 'ik':
            # print 'vectors___\n', upVctr
            # print 'clusters___\n', self.clusterList
            # add pole vector constraint and try to cleanup
            for i in range(len(upVctr) - 1, -1, -1):
                # print i, '  ______________________________________________i'
                # print '___vectors___\n', upVctr[i]
                # print '___clusters___\n', self.clusterList[i + 2]
                cmds.poleVectorConstraint(upVctr[i], self.clusterList[i + 2])
            # place.cleanUp(self.clusterList, World=True)
            cmds.parent(self.clusterList, self.hideGp)
            # root ik joint is in cluster list for this ik type, reparent to hideJnt group
            cmds.parent(self.ikJoints[0], self.hideJntGp)
            # constrain skin joints to ik joints.
            for i in range(1, len(self.ikJoints) - 1, 1):
                cmds.parentConstraint(self.ikJoints[i], self.skinJoints[i], mo=True)

    def parentClusters(self):
        '''\n

        '''
        # CONTROLS
        # ?, may be part of obsolete code
        child = None
        # for loop count
        i = 1
        # segment iterator
        j = 0
        # start color
        color = self.seg[0]
        # first controller of segment
        chainZero = None

        #
        #
        # for each cluster
        for handle in self.clusterList:
            cntCt = None
            # First iteration controller
            if i == 1:
                cntCt = self.createController(self.name + '_' + str(('%0' + str(2) + 'd') % (i)), self.skinJoints[i - 1], handle, color, ctrlType=['special', 'first'])
                if self.parent2 == None:
                    self.firstCntCt = cntCt[4]

            # All other iteration for controller
            else:
                cntCt = self.createController(self.name + '_' + str(('%0' + str(2) + 'd') % (i)), self.skinJoints[i - 1], handle, color, ctrlType=['', ''])
            # append controller to list
            self.ctrlList.append(cntCt)
            # constrain handle or joint. If joint is ocnstrained, means spline was opted to not be built, joints were forwarded as handles
            if handle == self.clusterList[0]:
                cmds.parentConstraint(self.skinJoints[0], handle, mo=True)
            else:
                cmds.parentConstraint(cntCt[4], handle, mo=True)

            #
            #
            # ps1 = parentSwitch -Arguements for lists
            # prepares ps1 variable for the controller constraint section
            # parent1 can sometimes be a list.
            # so that a different parent is used per joint (ie. dynamic chain switch)
            ps1 = None  # _____________________________
            if type(self.parent1).__name__ == 'list':
                # if parent1 is list type
                # i starts at 1, list must be accomodated
                ps1 = self.parent1[i - 1]
            else:
                # if parent1 is not list type
                ps1 = self.parent1
            ps2 = None  # _____________________________
            if type(self.parent2).__name__ == 'list':
                # if parent2 is list type
                # i starts at 1, list must be accomodated
                ps2 = self.parent2[i - 1]
            else:
                # if parent2 is not list type
                ps2 = self.parent2

            #
            #
            # controller constraints, parent switches, rig structure
            # during first iteration (i=1), self.ctParent arguements equals None.
            # every following iteration self.ctParent is populated with current iteration (i), (self.ctParent == cntCt[4]).
            # first controller has no Fk parent. It is the base controller, and has different requirements,
            # which are explained in the else statement of this arguement
            if i != 1:
                #
                #
                # self.parent1 check, make sure parent1 was fed, should awlays be fed... probably... dont really need this if statement.
                # top group of controller always gets constrained so there are no floating groups.
                # not required.
                if ps1 != None:
                    # parent options
                    topRot = cmds.xform(cntCt[0], query=True, ws=True, ro=True)

                    # top 1 is placed above cntCt[0], therefore this parent(ps1) overides the next parent(ps2)
                    # top group is the world in which the ct group gets constrained/driven
                    # ct group gets incoming constraints from its targets, object off/on via parenSwitch function, the rest of the controller hierarchy is under this group

                    TopGrp1 = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_TopGrp1'), cntCt[0])[0]
                    self.topGrp1.append(TopGrp1)
                    cmds.xform(TopGrp1, ws=True, ro=topRot)

                    CtGrp1 = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_CtGrp1'), cntCt[0])[0]
                    cmds.xform(CtGrp1, ws=True, ro=topRot)

                    cmds.parent(CtGrp1, TopGrp1)
                    cmds.parent(cntCt[0], CtGrp1)

                    place.setRotOrderWithXform(TopGrp1, 'zxy', False)
                    place.setRotOrderWithXform(CtGrp1, 'zxy', False)

                    # account for ps1 being a joint type
                    self.ps1_Jnt = ps1
                    if cmds.objectType(ps1) == 'joint':
                        JntIntmdt = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_Prnt1OnAssistGp'), TopGrp1)[0]
                        cmds.parent(JntIntmdt, TopGrp1)
                        place.setRotOrderWithXform(JntIntmdt, 'zxy', False)
                        cmds.parentConstraint(ps1, JntIntmdt, mo=True)
                        self.ps1_Jnt = JntIntmdt

                    # if groups dont match rotate orders the parent switches will fail.
                    # default rotate order of the controller class is 2 or 'zxy'
                    # top group of controller always gets constrained so there are no floating groups.
                    # not required.
                    if ps2 == None:
                        #cmds.parentConstraint(self.firstCntCt, cntCt[0], mo=True)
                        # Dont need as of Nov 30th 2010
                        place.parentSwitch(self.nameBuilder(self.name + '__' + str(('%0' + str(2) + 'd') % (i))), cntCt[2], CtGrp1, TopGrp1, self.ps1_Jnt, self.ctParent,
                                           False, False, True, True, 'FK_', w=self.FK)
                        # place.cleanUp(TopGrp1, Ctrl=True)
                        cmds.parent(TopGrp1, self.ctGp)
                #
                #
                # self.parent2 check
                if ps2 != None:
                    # print ps2
                    # cmds.select(TopGrp1)
                    topRot = cmds.xform(cntCt[0], query=True, ws=True, ro=True)
                    # top 2 is placed above top 1, therefore this parent is only used of ps1 is turned off
                    # top group is the world in which the ct group gets constrained/driven
                    TopGrp2 = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_TopGrp2'), TopGrp1)[0]
                    self.topGrp2.append(TopGrp2)
                    cmds.xform(TopGrp2, ws=True, ro=topRot)

                    # ct group gets incoming constraints from its targets, object off/on via parenSwitch function
                    CtGrp2 = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_CtGrp2'), TopGrp1)[0]
                    cmds.xform(CtGrp2, ws=True, ro=topRot)

                    # if groups dont match rotate orders the parent switches will fail.
                    # default rotate order of the controller class is 2 or 'zxy'
                    # top groups should be accounted for before switches, possibly where ps variables are created.
                    # this shoulde also be accounted for in ps1, add to final setsarent function.
                    cmds.parent(TopGrp1, CtGrp2)
                    cmds.parent(CtGrp2, TopGrp2)

                    place.setRotOrderWithXform(CtGrp2, 'zxy', False)
                    place.setRotOrderWithXform(TopGrp2, 'zxy', False)

                    place.parentSwitch(self.nameBuilder(self.name + '__' + str(('%0' + str(2) + 'd') % (i))), cntCt[2], CtGrp1, TopGrp1, CtGrp2, self.ctParent, False, False, True, True, 'FK_', w=self.FK)

                    if cmds.objectType(ps2) == 'joint':
                        JntIntmdt = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_Prnt2OnAssistGp'), TopGrp1)[0]
                        cmds.parent(JntIntmdt, TopGrp2)
                        place.setRotOrderWithXform(JntIntmdt, 'zxy', False)
                        cmds.parentConstraint(ps2, JntIntmdt, mo=True)
                        place.parentSwitch(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i))), cntCt[2], CtGrp2, TopGrp2, TopGrp2, JntIntmdt, False, False, True, False, 'Driver_', w=self.driven)
                    else:
                        place.parentSwitch(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i))), cntCt[2], CtGrp2, TopGrp2, TopGrp2, ps2, False, False, True, False, 'Driver_', w=self.driven)
                    cmds.parent(TopGrp2, self.ctGp)

                # forward group to be used as parent for next controller iteration
                self.ctParent = cntCt[4]
                # append same controller to list for vector parent
                self.vcParent.append(cntCt[4])

                #
                #
                # segment controls and additive
                # special case for first controller in segment
                # first controller in segment is a type of master
                # its transforms are additive to the ones succeeding
                if j == 0:
                    chainZero = cntCt[3]
                    # make offset shape visible and bigger
                    cmds.setAttr(cntCt[2] + '.Offset_Vis', 1)
                    place.shapeSize(cntCt[3], 1.5)
                    # path = os.path.join(os.getenv('KEY_TOOLS_PYTHONPATH'), 'atom/control_shape_templates')
                    path = os.path.expanduser('~') + '/GitHub/controlShapes/'
                    cmds.select(cntCt[3])
                    ui.importCurveShape(self.iconList[2], path, self.controlerSize * .5, color)
                    # all iterations of segment get scale additive to the joints
                    place.attrBlend(cntCt[3], self.skinJoints[i - 1], cntCt[2], scale=True, skip=2)
                    place.scaleUnlock(cntCt[3], sz=False)
                # all other iterations of segment
                else:
                    # build additive
                    # null is placed above this controller
                    # cmds.select(cntCt[2])
                    rot = cmds.xform(cntCt[1], query=True, ws=True, ro=True)
                    blendNull = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_RotBlendGrp'), cntCt[2])[0]
                    cmds.xform(blendNull, ws=True, ro=rot)
                    cmds.parent(blendNull, cntCt[1])
                    cmds.parent(cntCt[2], blendNull)
                    place.setRotOrderWithXform(blendNull, 'zxy', False)
                    # add additive to rot and pos
                    place.attrBlend(chainZero, blendNull, cntCt[2], rot=True, pos=True, skip=3, default=1)
                    # all iterations of segment get scale additive to the joints
                    place.attrBlend(chainZero, self.skinJoints[i - 1], cntCt[2], scale=True, skip=2)

                # root Parent, useless, object takes parent1 position
                # cmds.parentConstraint(self.rootParent, TopGrp1, mo=True)
                #
                #
                # segment iteration
                # begins during second iteration of (i==2)
                j = j + 1

            # this is first iteration of handle loop. 'else' arguement is (i==1)
            else:
                # forward group to be used as parent for next controller iteration
                self.ctParent = cntCt[4]
                # append same controller to list for vector parent
                self.vcParent.append(cntCt[4])
                # sort out root parent, account for joint type
                rp = self.rootParent
                if cmds.objectType(self.rootParent) == 'joint':
                    JntIntmdt = place.null2((cntCt[2] + '_PrntOnAssistGp'), cntCt[2])[0]
                    cmds.parent(JntIntmdt, cntCt[0])
                    place.setRotOrderWithXform(JntIntmdt, 'zxy', False)
                    cmds.parentConstraint(self.rootParent, JntIntmdt, mo=True)
                    rp = JntIntmdt
                # print self.ps1_Jnt, 'here\n'
                # account for ps1 being a joint type
                self.ps1_Jnt = ps1
                if ps1:
                    if cmds.objectType(ps1) == 'joint':
                        JntIntmdt = place.null2(self.nameBuilder(self.name + '_' + str(('%0' + str(2) + 'd') % (i)) + '_Prnt1OnAssistGp'), cntCt[0])[0]
                        cmds.parent(JntIntmdt, cntCt[0])
                        place.setRotOrderWithXform(JntIntmdt, 'zxy', False)
                        cmds.parentConstraint(ps1, JntIntmdt, mo=True)
                        self.ps1_Jnt = JntIntmdt
                    place.parentSwitch(self.nameBuilder(self.name + '__' + str(('%0' + str(2) + 'd') % (i))), cntCt[2],
                                       cntCt[1], cntCt[0], self.ps1_Jnt, rp, False, True, False, True, 'FK_', w=self.FK)
                cmds.parentConstraint(self.rootParent, cntCt[0], mo=True)
                cmds.parent(cntCt[0], self.ctGp)
            #
            #
            # check state of segment iteration for a color change
            # segment length is set as top level arguement
            # if segmentIteration has reached limit value, reset j=0, change color
            if j == self.segmentIteration:
                # figure out what the current color is and switch to the opposite
                if color == self.seg[0]:
                    color = self.seg[1]
                else:
                    color = self.seg[0]
                # reset j=0
                j = 0
            #
            #
            # step iterator
            i = i + 1

        #
        #
        # if self.spline == True,  a spline has been created and needs stretch options and upvectors
        # otherwise, the joints are constrained directly to the controllers, nothing further needs to be built
        if self.ik == 'splineIK':
            self.Stretch()
            place.optEnum(self.baseCtrl, 'ControllerVis')
            self.vectors()
        elif self.ik == 'ik':
            self.Stretch()
            place.optEnum(self.baseCtrl, 'ControllerVis')
            self.vectors()

        #
        #
        # Add visibility attribute for segements to (root/self.baseCtrl) control
        # segment iterator
        s = 1
        place.optEnum(self.baseCtrl, 'ControllerVis')
        for i in range(0, len(self.ctrlList), 1):
            # do nothing on first/root control group
            if i == 0:
                pass
            # position of first base segment controller group, self.ctrlList[i][1]
            else:
                # if first iteration of (s), step iterator
                # base segment attribute connection is made
                if s == 1:
                    place.hijackVis(self.ctrlList[i][1], self.baseCtrl, name='Base' + self.segmentAttr, suffix=False, default=0)
                    s = s + 1
                # if segment iterator limit is reached, reset segment (s=1)
                # sub segment attribute connection is made
                elif s == self.segmentIteration:
                    place.hijackVis(self.ctrlList[i][1], self.baseCtrl, name='Sub' + self.segmentAttr, suffix=False, default=0)
                    # reset segment
                    s = 1
                # step iterator
                # sub segment attribute connection is made
                else:
                    place.hijackVis(self.ctrlList[i][1], self.baseCtrl, name='Sub' + self.segmentAttr, suffix=False, default=0)
                    s = s + 1
        return self.rootCt
