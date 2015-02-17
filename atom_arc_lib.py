import maya.cmds as cmds
import atom_miscellaneous_lib as misc
import atom_utilities_lib as aul


class AtomArc():

    def __init__(self, obj):
        self.obj = obj
        # check that the obj doesn't have the atomArcObj attribute
        if not cmds.attributeQuery('atomArcObj', node=self.obj, ex=True):

            attrLst = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']
            self.addDbleLnr = cmds.createNode('plusMinusAverage', name=self.obj + '_atomArc_addDoubleLinear')
            cmds.addAttr(self.obj, ln='atomScriptJobAttr', at='double')
            cmds.setAttr(self.obj + '.atomScriptJobAttr', edit=True, keyable=True)

            for i in range(0, len(attrLst), 1):
                cmds.connectAttr(self.obj + attrLst[i], self.addDbleLnr + '.input1D[' + str(i) + ']')

            # start the script jobs
            cmds.connectAttr(self.addDbleLnr + '.output1D', self.obj + '.atomScriptJobAttr')
            cmds.addAttr(self.addDbleLnr, ln='atomScriptJobAttr', at='message')

            # cmds.scriptJob( attributeChange=[self.obj + '.atomScriptJobAttr', 'from atom import atom_arc_lib\natom_arc_lib.refreshScriptJob()'],
            #	                kws=True, parent='atom_arcWin', runOnce=True)

            cmds.addAttr(self.obj, ln='atomArcObj', at='message')
            # get the current time slider range
            self.startFrame = int(cmds.playbackOptions(query=True, minTime=True))
            self.endFrame = int(cmds.playbackOptions(query=True, maxTime=True))

            # Set the the xKeyInfo vars
            self.keyframes = []
            self.keyPosList = []

            # only the first created sphere are created, all the objects after will be instances
            self.origKeyObj = None
            self.origInbObj = None

            # create the groups
            self.group = cmds.group(em=True, name=str(self.obj + '___ARC___'), w=True)

            cmds.addAttr(self.group, ln='atomArcGrp', at='message')
            cmds.addAttr(self.group, ln='atomArcMasterGrp', at='message')
            cmds.addAttr(self.group, ln='atomArcItem', at='message')
            cmds.addAttr(self.group, ln='atomArcKeyItem', at='message')
            cmds.addAttr(self.group, ln='atomArcInbItem', at='message')
            cmds.addAttr(self.group, ln='atomArcObj', at='message')
            misc.setChannels(self.group, [True, False], [True, False], [True, False], [True, True, False])

            cmds.connectAttr(self.group + '.atomArcObj', self.obj + '.atomArcObj')

            self.keyGroup = cmds.group(em=True, name=self.obj + '___ARCKEY___', parent=self.group)
            cmds.addAttr(self.keyGroup, ln='atomArcGrp', at='message')
            cmds.addAttr(self.keyGroup, ln='atomArcItem', at='message')
            misc.setChannels(self.keyGroup, [True, False], [True, False], [True, False], [True, True, False])
            misc.setChannels(self.keyGroup, [True, False], [True, False], [True, False], [True, True, False])

            self.inbGroup = cmds.group(em=True, name=self.obj + '___ARCINB___', parent=self.group)
            cmds.addAttr(self.inbGroup, ln='atomArcGrp', at='message')
            cmds.addAttr(self.inbGroup, ln='atomArcItem', at='message')
            misc.setChannels(self.inbGroup, [True, False], [True, False], [True, False], [True, True, False])

            self.arcLineGrp = cmds.group(em=True, name=self.obj + '___ARCPATH___', parent=self.group)
            cmds.addAttr(self.arcLineGrp, ln='atomArcGrp', at='message')
            cmds.addAttr(self.arcLineGrp, ln='atomArcItem', at='message')
            misc.setChannels(self.arcLineGrp, [True, False], [True, False], [True, False], [True, True, False])

            cmds.connectAttr(self.group + '.atomArcGrp', self.keyGroup + '.atomArcGrp')
            cmds.connectAttr(self.group + '.atomArcGrp', self.inbGroup + '.atomArcGrp')
            cmds.connectAttr(self.group + '.atomArcGrp', self.arcLineGrp + '.atomArcGrp')

            # test if animation curves are connected
            animCurve = cmds.listConnections(self.obj, type='animCurveTL')
            # check for a character node, as a character set may be involved
            if animCurve == None:
                animCurve = []
                con = cmds.listConnections(self.obj, p=True, scn=True, et=True, s=False, d=True, type='character')
                if con != None:
                    charObj = None
                    for c in con:
                        charObj = c.split('.')[0]
                        if cmds.objExists(charObj):
                            break

                    kCon = cmds.listConnections(charObj, s=True, d=False, type='animCurveTL')

                    for i in kCon:
                        if obj in i:
                            animCurve.append(i)

            if animCurve != None:
                keyList = []
                # Get the keyframes for each traslation axis
                keyList.append(self.extractKeyframesFromAnimCurve(cmds.keyframe(self.obj, attribute='tx',
                                                                                query=True, timeChange=True, valueChange=True)))
                keyList.append(self.extractKeyframesFromAnimCurve(cmds.keyframe(self.obj, attribute='ty',
                                                                                query=True, timeChange=True, valueChange=True)))
                keyList.append(self.extractKeyframesFromAnimCurve(cmds.keyframe(self.obj, attribute='tz',
                                                                                query=True, timeChange=True, valueChange=True)))

                # iterate through each axis and add the keyframe if it exists
                for keys in keyList:
                    # test that a connection has been returned
                    if keys != None:
                        for i in keys:
                            # test that there is a keyframe
                            if i != None:
                                # If the keyframe isn't in the list already add it
                                if i not in self.keyframes:
                                    self.keyframes.append(i)
                # sort the keyframes so they are in order
                self.keyframes.sort()

    def extractTransformFromMatrixAtTime(self, key):
        cmds.currentTime(key)
        matrix = cmds.xform(self.obj, q=True, ws=True, t=True)
        pos = matrix
        return pos

    def setDisplayAttributes(self, obj, color):
        cmds.setAttr(obj + '.overrideEnabled', 1)
        cmds.setAttr(obj + '.overrideShading', 0)
        cmds.setAttr(obj + '.overrideColor', color)

    def extractKeyframesFromAnimCurve(self, keyInfo):
        infoList = None
        if keyInfo != None:
            infoList = []
            for i in range(0, len(keyInfo), 2):
                infoList.append(keyInfo[i])
        return infoList

    def createArcObjects(self):
        setting = aul.modelPanelUtils()
        setting.captureModelPaneSettings()
        setting.turnOffAll()
        for i in range(self.startFrame, self.endFrame + 1, 1):
            if i in self.keyframes:
                scale = cmds.floatSliderGrp('atom_arckScaleFsg', query=True, v=True)
                self.createKeyObj(i, scale, 'key')
            else:
                scale = cmds.floatSliderGrp('atom_arckInScaleFsg', query=True, v=True)
                self.createKeyObj(i, scale, 'inbetween')

        # create the 'path' or line that the animation follows
        lineObj = cmds.curve(name=self.obj + '___atomArc_path___', p=self.keyPosList, degree=1)
        cmds.addAttr(lineObj, ln='atomArcItem', at='message')
        cmds.connectAttr(self.arcLineGrp + '.atomArcItem', lineObj + '.atomArcItem')
        cmds.parent(lineObj, self.arcLineGrp)
        self.setDisplayAttributes(lineObj, 16)

        cmds.button('atom_refreshArcButton', edit=True, en=True)
        cmds.button('atom_deleteArcButton', edit=True, en=True)
        setting.setCaptureSettings()

    def createKeyObj(self, frame, scale, kType):
        # create the name
        name = self.obj + '___atomArc_kSphere_' + kType + '___' + str(frame).split('.')[0]

        # create the frame object
        fObj = cmds.sphere(name=name, ax=[0, 1, 0], ch=False, po=0, r=scale, d=1)[0]

        # place the object

        pos = self.extractTransformFromMatrixAtTime(frame)
        cmds.xform(fObj, ws=True, t=pos)

        # Append the posList, this is used when creating the path/arc curve
        self.keyPosList.append(pos)
        misc.setChannels(fObj, [True, False], [True, False], [False, False])
        # Set grouping and display attributes
        if kType == 'key':
            cmds.parent(fObj, self.keyGroup)

            cmds.addAttr(fObj, ln='atomArcItem', at='message')
            cmds.connectAttr(self.group + '.atomArcItem', fObj + '.atomArcItem')

            cmds.addAttr(fObj, ln='atomArcKeyItem', at='message')
            cmds.connectAttr(self.group + '.atomArcKeyItem', fObj + '.atomArcKeyItem')

            self.setDisplayAttributes(fObj, 4)

        elif kType == 'inbetween':
            cmds.parent(fObj, self.inbGroup)

            cmds.addAttr(fObj, ln='atomArcItem', at='message')
            cmds.connectAttr(self.group + '.atomArcItem', fObj + '.atomArcItem')

            cmds.addAttr(fObj, ln='atomArcInbItem', at='message')
            cmds.connectAttr(self.group + '.atomArcInbItem', fObj + '.atomArcInbItem')

            self.setDisplayAttributes(fObj, 2)


def findScriptJob(oStr):
    jobNumList = []
    jobs = cmds.scriptJob(listJobs=True)
    for job in jobs:
        if job.find('atomScriptJob') != -1:
            jobList = job.split(',')
            jobCall = jobList[2]
            stripObj = jobCall[jobCall.find("'") + 1:-1]
            if stripObj == oStr:
                jobNum = int(jobList[0].split(':')[0])
                jobNumList.append(int(jobNum))
                print jobNum
    return jobNumList


def populateTslOnShow(*args):
    transforms = cmds.ls(type='transform')
    transforms.sort()
    hasArc = False
    for transform in transforms:
        if cmds.attributeQuery('atomArcMasterGrp', node=transform, ex=True):
            cmds.textScrollList('atom_arcTsl', edit=True, append=[transform])
            hasArc = True
    if hasArc == True:
        cmds.button('atom_refreshArcButton', edit=True, en=True)
        cmds.button('atom_deleteArcButton', edit=True, en=True)


def deleteArc(*args):
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        arcGrps = cmds.listConnections(selItem[0] + '.atomArcGrp')
        arcItems = cmds.listConnections(selItem[0] + '.atomArcItem')
        cmds.delete(arcItems)
        cmds.delete(arcGrps)

        obj = cmds.listConnections(selItem[0] + '.atomArcObj')
        # cleanup the connections to the obj
        node = cmds.listConnections(obj[0] + '.atomScriptJobAttr')
        cmds.delete(node)
        if node != None:
            cmds.deleteAttr(obj[0] + '.atomScriptJobAttr')

        if obj != None:
            cmds.deleteAttr(obj[0] + '.atomArcObj')

        # delete the master group
        cmds.delete(selItem[0])

        # update the ui
        cmds.textScrollList('atom_arcTsl', edit=True, ri=selItem[0])

        # check if the list is empty if so, disable the refresh and delete buttons
        listItems = cmds.textScrollList('atom_arcTsl', query=True, ni=True)
        if listItems == 0:
            cmds.button('atom_refreshArcButton', edit=True, en=False)
            cmds.button('atom_deleteArcButton', edit=True, en=False)


def createArcCMD(*args):
    selList = cmds.ls(sl=True)
    for sel in selList:
        if not cmds.attributeQuery('atomArcObj', node=sel, ex=True):
            cmds.undoInfo(openChunk=True)
            arc = AtomArc(sel)
            arc.createArcObjects()
            cmds.textScrollList('atom_arcTsl', edit=True, append=[arc.group])
            cmds.textScrollList('atom_arcTsl', edit=True, si=[arc.group])
            cmds.undoInfo(closeChunk=True)
            del(arc)
        cmds.select(sel)


def tslSelCMD(*args):
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        keyObj = cmds.listConnections(selItem[0] + '.atomArcObj')
        cmds.select(keyObj)


def tslDoubleClickCMD(*args):
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        cmds.select(selItem[0])


def refreshArcCMD(*args):
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        keyObj = cmds.listConnections(selItem[0] + '.atomArcObj')
        deleteArc()
        cmds.select(keyObj)
        createArcCMD()


def scaleKeyObjCMD(*args):
    # get the selected item in the textScrollList
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        if cmds.objExists(selItem[0]):
            scale = cmds.floatSliderGrp('atom_arckScaleFsg', query=True, v=True)
            # get the keyObjects
            keyObjs = cmds.listConnections(selItem[0] + '.atomArcKeyItem')
            if len(keyObjs) > 0:
                for obj in keyObjs:
                    cmds.setAttr(obj + '.sx', scale)
                    cmds.setAttr(obj + '.sy', scale)
                    cmds.setAttr(obj + '.sz', scale)


def scaleInbObjCMD(*args):
    # get the selected item in the textScrollList
    selItem = cmds.textScrollList('atom_arcTsl', query=True, si=True)
    if selItem != None:
        if cmds.objExists(selItem[0]):
            scale = cmds.floatSliderGrp('atom_arckInScaleFsg', query=True, v=True)
            # get the keyObjects
            keyObjs = cmds.listConnections(selItem[0] + '.atomArcInbItem')
            if len(keyObjs) > 0:
                for obj in keyObjs:
                    cmds.setAttr(obj + '.sx', scale)
                    cmds.setAttr(obj + '.sy', scale)
                    cmds.setAttr(obj + '.sz', scale)


def refreshScriptJob(*args):
    if cmds.window('atom_arcWin', ex=True):
        if cmds.checkBoxGrp('atom_arcRefreshCgb', query=True, v1=True):
            refreshArcCMD()


def findAtomArcNodes(*args):
    sceneNodes = cmds.ls()

    for node in sceneNodes:
        arcAttrList = ['atomScriptJobAttr', 'atomArcObj', 'atomArcGrp',
                       'atomArcMasterGrp', 'atomArcItem', 'atomArcKeyItem', 'atomArcInbItem']
        for attr in arcAttrList:
            if cmds.attributeQuery(attr, node=node, ex=True):
                print '%s has %s' % (node, attr)


def win(*args):
    if cmds.window('atom_arcWin', ex=True):
        cmds.deleteUI('atom_arcWin')

    cmds.window('atom_arcWin', t='Atom Arc Control')
    atom_mainForm = cmds.formLayout(numberOfDivisions=100)
    #atom_autoRefresh_cbg = cmds.checkBoxGrp('atom_arcRefreshCgb', numberOfCheckBoxes = 1, label='Auto Refresh:', cw=[1,98], onc=refreshArcCMD)
    atom_arc_kFsg = cmds.floatSliderGrp('atom_arckScaleFsg', label='Key Scale:', pre=2, ss=.01, fs=.01, field=True, minValue=.01, maxValue=20.0,
                                        cw=[1, 100], fieldMinValue=.01, fieldMaxValue=20, value=1, cc=scaleKeyObjCMD, dc=scaleKeyObjCMD)

    atom_arc_inbFsg = cmds.floatSliderGrp('atom_arckInScaleFsg', label='Inbetween Scale:', pre=2, ss=.01, fs=.01, field=True, minValue=.01, maxValue=20.0,
                                          cw=[1, 100], fieldMinValue=.01, fieldMaxValue=20, value=.25, cc=scaleInbObjCMD, dc=scaleInbObjCMD)

    atom_arc_createBut = cmds.button('Create Arc', c=createArcCMD)
    atom_arc_refBut = cmds.button('atom_refreshArcButton', l='Refresh Arc', c=refreshArcCMD, en=False)
    atom_arc_tsl = cmds.textScrollList('atom_arcTsl', sc=tslSelCMD, dcc=tslDoubleClickCMD)

    atom_arc_delBut = cmds.button('atom_deleteArcButton', l='Delect Selected Arc', c=deleteArc, en=True)

    cmds.formLayout(atom_mainForm, edit=True,
                    attachForm=[
                        (atom_arc_kFsg, 'top', 5), (atom_arc_kFsg, 'left', 5), (atom_arc_kFsg, 'right', 5),
                        (atom_arc_inbFsg, 'left', 5), (atom_arc_inbFsg, 'right', 5),
                        (atom_arc_createBut, 'left', 5), (atom_arc_createBut, 'right', 5),
                        (atom_arc_refBut, 'left', 5), (atom_arc_refBut, 'right', 5),
                        (atom_arc_tsl, 'left', 5), (atom_arc_tsl, 'right', 5),
                        (atom_arc_delBut, 'left', 5), (atom_arc_delBut, 'right', 5),
                        (atom_arc_tsl, 'bottom', 30)],

                    attachControl=[
                        (atom_arc_inbFsg, 'top', 5, atom_arc_kFsg),
                        (atom_arc_createBut, 'top', 5, atom_arc_inbFsg),
                        (atom_arc_refBut, 'top', 5, atom_arc_createBut),
                        (atom_arc_tsl, 'top', 5, atom_arc_refBut),
                        (atom_arc_delBut, 'top', 5, atom_arc_tsl), ]
                    )
    cmds.showWindow('atom_arcWin')
    populateTslOnShow()
