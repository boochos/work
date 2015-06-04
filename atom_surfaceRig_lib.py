from __future__ import with_statement
from pymel.core import *
from pymel.core.system import *
import atom_placement_lib as place

# ARS = Atom Surface Rig
# class that preforms various function on a shape object that has vertexConstraints on it


class ASR_CoreShape(object):

    '''
    Class: <AtomSurfaceRigCore>: Base Core Object with Utility Functions.

    Methods:

    __init__(<MeshVertex>)  -- Class initialization.
    checkForPlug()          -- Check for the vertexConstraint.py plug-in.
    getBaseVertexNodes()    -- Returns a list of connected vertexConstraint nodes.
    getBaseVertexGroups()   -- Returns a list off connected vertexConstraint groups.
    deleteBaseGroups()      -- Delete vertexConstraint groups.
    createConnectAttr(source object, source attribute,
                      target object, target attribute) -- create and connects the given attributes.
    '''

    def __init__(self, vtx):
        '''
        __init__(<MeshVertex>)  -- Class initialization.
        '''
        self.shape = vtx.node()
        self.plug = self.checkForPlug()

    def checkForPlug(self):
        '''
        Def: checkForPlug: Check for the vertexConstraint.py plug-in
        '''
        # check the the vertexConstraint plugin is registerd
        if pluginInfo('vertexConstraint.py', query=True, r=True):
            # check if it's loaded, if not load it and turn on autoload
            if not pluginInfo('vertexConstraint.py', query=True, l=True):
                loadPlugin('vertexConstraint.py')
                pluginInfo('vertexConstraint.py', edit=True, autoload=True)
                return True
            else:
                return True
        else:
            return False

    def getVertexNodes(self):
        '''
        Def: getVertexNodes: Returns a list of connected vertexConstraint nodes.
        '''
        if self.shape.hasAttr('vcn'):
            return self.shape.vcn.connections()
        else:
            return None

    def getVertexGroups(self):
        '''
        Def: getVertexGroups: Returns a list off connected vertexConstraint groups.
        '''
        if self.shape.hasAttr('vcg'):
            return self.shape.vcg.connections()
        else:
            return None

    def createConnectAttr(self, sObj, sAttr, tObj, tAttr):
        '''
        Def: createConnectAttr(source object, source attribute,
                      target object, target attribute) -- create and connects the given attributes.
        '''
        if not sObj.hasAttr(sAttr):
            sObj.addAttr(sAttr, at='message')

        if not tObj.hasAttr(tAttr):
            tObj.addAttr(tAttr, at='message')

        eval('ls("' + str(sObj) + '")[0].' + sAttr + '.connect(ls("' + str(tObj) + '")[0].' + tAttr + ',force=True)')

# END class ASR_CoreShape


class ASR_CoreElement(ASR_CoreShape):

    '''
    Class: <AtomSurfaceRigBaseComponent>: Instanced from AtomSurfaceCore. Used in creation of the base components for the surface rig.

    Methods:

    __init__(vtx<MeshVertex Object>, 
             name<string>, create<Bool>) : Class initialization, name and create or optional.   

    constrainToVertex()           : Create a vertexConstraint and connect its .outPut to the classes group.transform
    createConstraints()           : Base method that calls the other methods in creation of the vertex constraint.
    '''
    # options are:
    # base ctrl size, aim ctrl size, tip ctrl size

    def __init__(self, vtx, name=None, create=True, overRideConflict=True):
        # Run the AtomSurfaceRigCore init first, passing the vtx.node(), which is the shape.
        # This will also run the check for plug ins properly.
        ASR_CoreShape.__init__(self, vtx)
        '''
	__init__(vtx<MeshVertex Object>, 
                 name<string>, create<Bool>) : Class initialization, name and create or optional.   
	'''
        self.shape = vtx.node()
        self.vtxInt = int(vtx.indices()[0])
        self.create = create
        self.name = str(name) + '_' + self.shape + '_vtx_' + str(self.vtxInt)
        self.tranGroup = None
        self.vtxConNode = None
        self.overRideConflict = True
        # check that the node exists
        if self.create == True:
            self.createNameAttr()
            self.createConstraints()

    def createNameAttr(self):
        '''
        createNameAttr()       -- Create a name attribute on the shape node, this will be
                                  referenced later when rebuilding an ASR Object.
        '''
        if not self.shape.hasAttr('asr_rigName'):
            self.shape.addAttr('asr_rigName', dt='string')
            self.shape.asr_rigName.set(self.name)

    def detectVCConnections(self):
        '''
        detectConnections()     -- Detect if a shape node has a vertexConstraint on a specific vertex.
        '''
        # vcn = vertex constraint node
        if self.shape.hasAttr('vcn'):
            connections = self.shape.vcn.connections()
            if len(connections) != 0:
                for con in connections:
                    if con.vertex.get() == self.vtxInt:
                        if self.tranGroup == None:
                            self.tranGroup = con.output.connections()[0]
                        return True
            else:
                return False
        else:
            return False

    def constrainToVertex(self):
        '''
        constrainToVertex()           : Create a vertexConstraint and connect its .outPut to the classes group.transform
        '''
        # create the mesh info node
        name = '%s_%s_vCon' % (self.name, self.shape)
        self.vtxConNode = createNode('vertexConstraint', name=name, ss=True)

        # set the attributes specific to the meshInfoNode
        self.vtxConNode.vertex.set(self.vtxInt)

        # make the mesh connections
        self.shape.outMesh.connect(self.vtxConNode.inputShape)

        # connect the positional information
        self.vtxConNode.output.connect(self.tranGroup.translate)

        # Set the connections up
        self.createConnectAttr(self.shape, 'vcn', self.vtxConNode, 'vcn')

    def createConstraints(self):
        '''
        createConstraints()           : Base method that calls the other methods in creation of the vertex constraint.
        '''
        if self.plug:
            # if the shapeNode doesn't all ready have a node connected to the vertex
            if not self.detectVCConnections():
                name = '%s_element_ASR_tran' % (self.name)
                self.tranGroup = ls(createNode('transform', name=name, ss=True))[0]
                self.constrainToVertex()
                self.createConnectAttr(self.shape, 'vcg', self.tranGroup, 'vcg')
        else:
            print 'PLUG IN NOT FOUND!'
# END class ASR_CoreElement


class ASR_ControlElement(object):

    def __init__(self, coreElement, jntRad, ctrlSize, name=None, buildJoint=True, overRide=True):
        self.coreElement = coreElement
        self.name = self.coreElement.name
        self.jntRad = jntRad
        self.ctrlSize = ctrlSize
        self.buildJoint = buildJoint
        self.ctrl = None
        self.joint = None
        self.parentCon = None
        self.topGrp = None
        self.ctGrp = None
        self.offset = None
        self.overRide = overRide

    def getControlJoints(self):
        if self.ctrl != None:
            if self.ctrl.hasAttr('cjt'):
                return self.ctrl.cjt.connections()

    def detectCtrlConnections(self):
        if self.overRide:
            return False
        else:
            vNds = self.coreElement.getVertexNodes()
            rVar = False
            if len(vNds) > 0:
                for con in vNds:
                    if con.vertex.get() == self.coreElement.vtxInt:
                        tran = con.output.connections()[0]
                        if tran.hasAttr('src'):
                            ctrl = tran.src.connections()[0]
                            if ctrl != None:
                                rVar = True

            return rVar

    def createControl(self):
        if self.overRide:
            if not self.detectCtrlConnections():
                ctrl = place.Controller(self.name, str(self.coreElement.tranGroup), size=self.ctrlSize, groups=True)

                self.topGrp = ls(ctrl.createController()[0])[0]
                self.ctGrp = self.topGrp.getChildren(type='transform')[0]
                self.ctrl = self.ctGrp.getChildren(type='transform')[0]
                self.offsetCtrl = self.ctrl.getChildren(type='transform')[0]

                if self.buildJoint:
                    self.ctrl.addAttr('jointVis', at='long', min=0, max=1, dv=0)
                    self.ctrl.jointVis.set(cb=True)

                    self.joint = createNode('joint', name=self.name + '_jnt', ss=True)
                    self.joint.radius.set(self.jntRad)

                    self.ctrl.jointVis.connect(self.joint.visibility)
                    self.parentCon = parentConstraint(self.offsetCtrl, self.joint, name=self.name + '_parentConstraint')
                    self.coreElement.createConnectAttr(self.topGrp, 'cjt', self.joint, 'cjt')

                self.coreElement.createConnectAttr(self.coreElement.tranGroup, 'src', self.topGrp, 'src')

                return True
            else:
                return False

# END class ASR_ControlElement


class ASR(object):

    def __init__(self, vtx, jntRad=.1, ctrlSize=1, name=None, buildJoint=True):
        self.vtx = vtx
        self.name = name
        self.jntRad = jntRad
        self.buildJoint = buildJoint
        self.ctrlSize = ctrlSize
        self.ctrlElement = None
        self.coreElement = None

        self.jntGrp = str(self.name) + '_ASR_JNTGRP'
        self.rigWGrp = str(self.name) + '_ASR_WORLD'
        self.rigCtrlGrp = str(self.name) + '_ASR_CTRL'
        self.elementGrp = str(self.name) + '_ELEMENTGRP'
        self.ctrlGrp = str(self.name) + '_vtx_' + str(self.vtx.indices()[0]) + '_CTRLGRP'

    def cleanup(self):
        try:
            PyNode(self.rigWGrp)
        except MayaObjectError:
            createNode('transform', name=self.rigWGrp, ss=True)

        try:
            PyNode(self.elementGrp)
            self.coreElement.tranGroup.setParent(self.elementGrp)
        except:
            if self.coreElement.tranGroup.getParent() == None:
                nullGrp = ls(createNode('transform', name=self.elementGrp, ss=True))[0]
                nullGrp.setParent(self.rigWGrp)
                self.coreElement.tranGroup.setParent(self.elementGrp)

        if self.buildJoint == True:
            try:
                PyNode(self.jntGrp)
            except:
                jntGrp = ls(createNode('transform', name=self.jntGrp, ss=True))[0]
                jntGrp.setParent(self.rigWGrp)

        try:
            PyNode(self.rigCtrlGrp)
        except:
            createNode('transform', name=self.rigCtrlGrp, ss=True)

        try:
            rigCtrlGrp = ls(self.rigCtrlGrp)[0]
            if rigCtrlGrp.getParent() == None:
                rigCtrlGrp.setParent('CONTROLS')
        except:
            pass

        try:
            rigWGrp = ls(self.rigWGrp)[0]
            if rigWGrp.getParent() == None:
                rigWGrp.setParent('WORLD_SPACE')
        except:
            pass

        ctrlGrp = ls(createNode('transform', name=self.ctrlGrp))[0]
        ctrlGrp.setParent(self.rigCtrlGrp)

        if self.buildJoint:
            # parent the joints
            self.ctrlElement.joint.setParent(self.jntGrp)

        self.ctrlElement.topGrp.setParent(ctrlGrp)

    def createRig(self):
        self.coreElement = ASR_CoreElement(self.vtx, self.name)
        self.ctrlElement = ASR_ControlElement(self.coreElement, self.jntRad, self.ctrlSize, self.name, buildJoint=self.buildJoint)
        catch = self.ctrlElement.createControl()

        # if catch:
        #    pointConstraint(self.coreElement.tranGroup, self.ctrlElement.topGrp)
        # self.cleanup()
# END class ASR


class ASR_Rebuild(ASR_CoreShape):

    class ASR_ctrlElementNull(object):

        def __init__(self):
            self.ctrlElement = None
            self.offsetCtrl = None
            self.joint = None
            self.TopGrp = None
            self.ctGrp = None

    class ASR_coreElementNull(object):

        def __init__(self):
            self.tranGroup = None

    def __init__(self, vtx, shape):
        ASR_CoreShape.__init__(self, shape)

        self.vtx = self.shape.vtx[vtx]
        self.vtxInt = vtx
        self.name = None
        self.tranGroup = None
        self.vtxConNode = None
        self.joint = None
        self.coreElement = self.ASR_coreElementNull()
        self.ctrlElement = self.ASR_ctrlElementNull()
        self.ctrlElement.ctrl = None
        self.ctrlElement.offsetCtrl = None
        self.initObject()

    def initObject(self):
        nodes = self.getVertexNodes()
        if nodes != None:
            for node in nodes:
                if node.vertex.get() == self.vtxInt:
                    self.vtxConNode = node
                    self.tranGroup = node.output.connections()[0]

                    if self.tranGroup.hasAttr('src'):
                        self.ctrlElement.TopGrp = self.tranGroup.src.connections()[0]
                        try:
                            self.ctrlElement.offsetCtrl = self.ctrlElement.TopGrp.getChildren(type='transform')[0].getChildren(type='transform')[0].getChildren(type='transform')[0]
                        except:
                            print '//Error: No offset controller found, rig may not be fully built.'

                    if self.ctrlElement.TopGrp != None:
                        if self.ctrlElement.TopGrp.hasAttr('cjt'):
                            self.ctrlElement.joint = self.ctrlElement.TopGrp.cjt.connections()[0]

                        if self.ctrlElement.TopGrp != None:
                            if self.ctrlElement.TopGrp.getChildren() != None:
                                self.ctrlElement.ctGrp = self.ctrlElement.TopGrp.getChildren()[0]

                        if self.ctrlElement.ctGrp != None:
                            if self.ctrlElement.ctGrp.getChildren() != None:
                                self.ctrlElement.ctrl = self.ctrlElement.ctGrp.getChildren()[0]

                    if self.shape != None:
                        if self.shape.hasAttr('vcn'):
                            self.vtxConNode = self.shape.vcn.connections()[0]

                        if self.shape.hasAttr('asr_rigName'):
                            self.name = self.shape.asr_rigName.get()


class ASR_AimRig(object):

    def __init__(self, name, aimVtx, baseVtx, upVtx, jntRad, ctrlSize, highlight=False, aim=[0, 0, 1], up=[1, 0, 0]):
        self.name = name

        self.aimVtx = aimVtx
        self.baseVtx = baseVtx
        self.upVtx = upVtx

        self.aim = aim
        self.up = up

        self.jntRad = jntRad
        self.ctrlSize = ctrlSize
        self.highlight = highlight
        self.aim_rig = None
        self.base_rig = None
        self.up_tran = None
        self.masterCtrl = None

        self.masterCtrl = None
        self.masterCtGrp = None
        self.masterOffset = None

    def cleanup(self):
        self.masterTopGrp.setParent(self.base_rig.ctrlGrp)
        self.up_tran.tranGroup.setParent(self.base_rig.elementGrp)
        # Put the displate mode back into object selection
        if self.highlight:
            hilite(self.baseVtx.node().getParent(), r=True)

    def createRig(self):
        self.aim_rig = ASR(self.aimVtx, self.jntRad, self.ctrlSize, self.name)
        self.aim_rig.createRig()
        self.aim_rig.cleanup()

        self.base_rig = ASR(self.baseVtx, self.jntRad, self.ctrlSize, self.name)
        self.base_rig.createRig()
        self.base_rig.cleanup()

        masterCtrl = place.Controller(self.name + '_master_ctrl_vtx_' + str(self.baseVtx.indices()[0]), str(self.base_rig.coreElement.tranGroup),
                                      size=self.ctrlSize + (self.ctrlSize * .5), groups=True)
        self.masterTopGrp = ls(masterCtrl.createController()[0])[0]
        self.masterCtGrp = self.masterTopGrp.getChildren(type='transform')[0]
        self.masterCtrl = self.masterCtGrp.getChildren(type='transform')[0]
        self.masterOffset = self.masterCtrl.getChildren(type='transform')[0]
        self.up_tran = ASR_CoreElement(self.upVtx, self.name)

        self.up_tran = ASR_CoreElement(self.upVtx, self.name)

        pointConstraint(self.aim_rig.coreElement.tranGroup, self.aim_rig.ctrlElement.topGrp)
        pointConstraint(self.base_rig.coreElement.tranGroup, self.masterTopGrp)
        aimConstraint(self.aim_rig.coreElement.tranGroup, self.masterTopGrp, wut='object', wuo=self.up_tran.tranGroup, aim=self.aim, u=self.up)

        self.masterTopGrp.rotate.connect(self.aim_rig.ctrlElement.topGrp.rotate)

        self.masterCtrl.rotate.connect(self.aim_rig.ctrlElement.ctGrp.rotate)
        self.masterCtrl.translate.connect(self.aim_rig.ctrlElement.ctGrp.translate)

        self.aim_rig.ctrlElement.ctGrp.setPivots(self.masterTopGrp.getTranslation(space='world'), ws=True)
        self.masterTopGrp.rotate.connect(self.base_rig.ctrlElement.topGrp.rotate)

        self.masterCtrl.rotate.connect(self.base_rig.ctrlElement.ctGrp.rotate)
        self.masterTopGrp.translate.connect(self.base_rig.ctrlElement.topGrp.translate)
        self.masterCtrl.translate.connect(self.base_rig.ctrlElement.ctGrp.translate)
        self.cleanup()

# END ASR_AimRig


class AtomSurfaceRigUI(object):

    def __init__(self):
        self.aimNameInfo = ['atom_vCon_aim_vtx_Layout',
                            'atom_vCon_aim_vtx_txt', 'atom_vCon_aim_vtx_intFld', 'Aim Vtx']

        self.baseNameInfo = ['atom_vCon_base_vtx_Layout',
                             'atom_vCon_base_vtx_txt', 'atom_vCon_base_vtx_intFld', 'Base Vtx']

        self.upNameInfo = ['atom_vCon_up_vtx_Layout',
                           'atom_vCon_up_vtx_txt', 'atom_vCon_up_vtx_intFld', 'Up Vtx']
        #Aim, Base, Up
        self.vtxInfoList = [None, None, None]
        self.nameFld = 'atom_vCon_name_tf'
        self.suffixFld = 'atom_vCon_suffix_tf'
        self.cSizeFltFld = 'atom_vCon_ctrlSize_ff'
        self.aimIntFldGrp = 'atom_vCon_aimOpt_ifg'
        self.upIntFldGrp = 'atom_vCon_upOpt_ifg'

    def populateVtxLayout(self, vtxIdx, intFld):
        sel = ls(sl=True)
        if sel != None and len(sel) == 1:
            vtxObj = sel[0]

            if vtxObj.nodeType() == 'mesh':
                self.vtxInfoList[vtxIdx] = vtxObj
                intField(intFld, edit=True, v=vtxObj.indices()[0])

    def createVertexlayout(self, parentControl, uiInfo, rigType, val):
        width = 60
        layout = horizontalLayout(uiInfo[0], parent=parentControl, ratios=[0, 0, 1], spacing=5)
        with layout:
            vtxTxt = text(uiInfo[1], l=uiInfo[3] + ':', width=width, parent=layout, fn='boldLabelFont')
            intFld = intField(uiInfo[2], v=val)
            setBtn = button(l='Set', c=Callback(self.populateVtxLayout, rigType, intFld))

        return layout

    def createSurfaceRigCMD(self, *args):
        name = textField(self.nameFld, q=True, tx=True)
        suffix = textField(self.suffixFld, q=True, tx=True)
        cSize = floatField(self.cSizeFltFld, q=True, v=True)
        aimOpt = intFieldGrp(self.aimIntFldGrp, q=True, v=True)
        upOpt = intFieldGrp(self.upIntFldGrp, q=True, v=True)

        sRig = ASR_AimRig(name, self.vtxInfoList[0], self.vtxInfoList[1], self.vtxInfoList[2],
                          cSize - (cSize * .8), cSize, aim=aimOpt, up=upOpt)
        sRig.createRig()

    def win(self):

        winName = 'atom_constrainVertexWin'
        if window(winName, ex=True):
            deleteUI(winName)

        with window(winName, t='Atom Surface Rig Window') as win:
            main_form = formLayout('atom_vCon_main_formLayout', numberOfDivisions=100)
            with main_form:
                name_txt = text(l='Name:', w=34)
                name_tf = textField(self.nameFld, tx='None')
                suffix_txt = text(l='Suffix:', w=34)
                suffix_tf = textField(self.suffixFld, tx='None')
                ctrlSize_txt = text(l='Controller Size:', w=81)
                ctrlSize_ff = floatField(self.cSizeFltFld, min=.01, pre=2, v=.1)

                fwidth = 30

                aimCon_txt = text(l='Aim Constraint Options:', w=128)
                aimOpt_ifg = intFieldGrp(self.aimIntFldGrp, cw4=[35, fwidth, fwidth, fwidth], numberOfFields=3, label='Aim:', v1=0, v2=0, v3=1)
                upOpt_ifg = intFieldGrp(self.upIntFldGrp, cw4=[35, fwidth, fwidth, fwidth], numberOfFields=3, label='Up:', v1=1, v2=0, v3=0)

                sep_1 = separator('atom_vCon_separator_1')

                aim_layout = self.createVertexlayout(main_form, self.aimNameInfo, 0, 0)
                base_layout = self.createVertexlayout(main_form, self.baseNameInfo, 1, 0)
                up_layout = self.createVertexlayout(main_form, self.upNameInfo, 2, 0)

                sep_2 = separator('atom_vCon_separator_2')

                rigBtn = button('atom_vCon_createRigBut', l='Create Surface Rig', c=self.createSurfaceRigCMD)

                formLayout(main_form, edit=True,
                           attachForm=[(name_txt, 'left', 5), (name_txt, 'top', 8), (name_tf, 'top', 5),
                                       (suffix_txt, 'top', 8), (suffix_tf, 'top', 5), (ctrlSize_txt, 'left', 5),
                                       (aimCon_txt, 'left', 5), (aimOpt_ifg, 'left', 56), (upOpt_ifg, 'left', 56),
                                       (sep_1, 'left', 5), (sep_1, 'right', 5),
                                       (aim_layout, 'left', 5), (aim_layout, 'right', 5),
                                       (base_layout, 'left', 5), (base_layout, 'right', 5),
                                       (up_layout, 'left', 5), (up_layout, 'right', 5),
                                       (sep_2, 'left', 5), (sep_2, 'right', 5),
                                       (rigBtn, 'left', 5), (rigBtn, 'right', 5), (rigBtn, 'bottom', 5)],

                           attachControl=[(name_tf, 'left', 52, name_txt), (suffix_txt, 'left', 5, name_tf),
                                          (suffix_tf, 'left', 5, suffix_txt), (ctrlSize_txt, 'top', 8, name_txt),
                                          (ctrlSize_ff, 'left', 5, ctrlSize_txt), (ctrlSize_ff, 'top', 5, name_txt),
                                          (aimCon_txt, 'top', 5, ctrlSize_txt), (aimOpt_ifg, 'top', 5, aimCon_txt), (upOpt_ifg, 'top', 5, aimOpt_ifg),
                                          (sep_1, 'top', 5, upOpt_ifg),
                                          (aim_layout, 'top', 5, sep_1), (base_layout, 'top', 5, aim_layout), (up_layout, 'top', 5, base_layout),
                                          (sep_2, 'top', 5, up_layout), (rigBtn, 'top', 5, sep_2)]

                           )


def win(*args):
    sRig = AtomSurfaceRigUI()
    sRig.win()
