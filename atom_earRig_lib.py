from pymel.core import *
import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')
splnFk = web.mod('atom_splineFk_lib')


class EarRig(object):

    def __init__(self, mid_name, mid_start_jnt, mid_end_jnt, mid_parent1, mid_parent2,
                 front_name, front_start_jnt, front_end_jnt, front_parent1, front_parent2,
                 back_name, back_start_jnt, back_end_jnt, back_parent1, back_parent2,
                 suffix, controllerSize=2, stretch=1, make='all', visibility=0, clean=True, ik=None):

        self.mid_name = mid_name
        self.mid_start_jnt = mid_start_jnt
        self.mid_end_jnt = mid_end_jnt
        self.mid_parent1 = mid_parent1
        self.mid_parent2 = mid_parent2

        self.front_name = front_name
        self.front_start_jnt = front_start_jnt
        self.front_end_jnt = front_end_jnt
        self.front_parent1 = front_parent1
        self.front_parent2 = front_parent2

        self.back_name = back_name
        self.back_start_jnt = back_start_jnt
        self.back_end_jnt = back_end_jnt
        self.back_parent1 = back_parent1
        self.back_parent2 = back_parent2
        self.controllerSize = controllerSize
        self.visibility = visibility

        self.suffix = suffix
        self.controllerSize = controllerSize
        self.visibility = visibility
        self.stretch = stretch
        self.cleanit = clean
        self.ik = ik

        self.parentList = []

        self.mid_spline_FK = None
        self.front_spline_FK = None
        self.back_spline_FK = None

        if make == 'all':
            self.make_mid_rig()
            self.make_front_rig()
            self.make_back_rig()

        # Set the visibility of the root joint
        if cmds.objExists(self.mid_start_jnt):
            # convert the string to a pymel obj
            pyObj_mid_start_jnt = ls(self.mid_start_jnt)[0]
            # Set the visibility of the parent
            pyObj_parent = pyObj_mid_start_jnt.getParent()
            pyObj_parent.visibility.set(self.visibility)
            if self.cleanit:
                if not pyObj_parent.getParent():
                    place.cleanUp(pyObj_parent.name(), SknJnts=True)

    def build_parent_list(self):
        for i in range(len(self.mid.ctrlList), 0, -1):
            obj = self.mid.ctrlList[i - 1][4]
            if i == len(self.mid.ctrlList):
                self.parentList.append(obj)
                self.parentList.append(obj)
            else:
                if len(self.parentList) < len(self.mid.ctrlList):
                    self.parentList.append(obj)

    def clean(self, cleanList):
        for i in cleanList:
            place.cleanUp(i, World=True)

    def make_mid_rig(self):

        self.mid = splnFk.SplineFK(self.mid_name, self.mid_start_jnt, self.mid_end_jnt, self.suffix,
                                   parent1=self.mid_parent1, parent2=self.mid_parent2,
                                   controllerSize=self.controllerSize, stretch=self.stretch, ik=self.ik)
        if self.cleanit:
            self.clean(self.mid.topGrp1)
            self.clean(self.mid.topGrp2)

        if self.front_parent2 == 'make_parent_list':
            self.build_parent_list()
            self.front_parent2 = self.parentList

        if self.back_parent2 == 'make_parent_list':
            self.build_parent_list()
            self.back_parent2 = self.parentList

    def make_front_rig(self):
        rig = splnFk.SplineFK(self.front_name, self.front_start_jnt, self.front_end_jnt, self.suffix,
                              parent1=self.front_parent1, parent2=self.front_parent2,
                              controllerSize=self.controllerSize, stretch=self.stretch, ik=self.ik)
        if self.cleanit:
            self.clean(rig.topGrp1)
            self.clean(rig.topGrp2)

    def make_back_rig(self):
        rig = splnFk.SplineFK(self.back_name, self.back_start_jnt, self.back_end_jnt, self.suffix,
                              parent1=self.back_parent1, parent2=self.back_parent2,
                              controllerSize=self.controllerSize, stretch=self.stretch, ik=self.ik)
        if self.cleanit:
            self.clean(rig.topGrp1)
            self.clean(rig.topGrp2)
