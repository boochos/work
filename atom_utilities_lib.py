from pymel.core import *
import os
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mm
import webrImport as web
# web
ui = web.mod('atom_ui_lib')


class modelPanelUtils(object):

    def __init__(self):
        self.mPanelList = []
        self.panels = cmds.getPanel(type='modelPanel')

    def turnOffAll(self):
        for mPanel in self.panels:
            mEditor = cmds.modelPanel(mPanel, query=True, modelEditor=True)
            cmds.modelEditor(mEditor, edit=True, allObjects=False)

    def setCaptureSettings(self):
        for i in self.mPanelList:
            mEditor = cmds.modelPanel(i['model_panel'], query=True, modelEditor=True)
            for setting in i:
                if setting != 'model_panel':
                    execStr = 'cmds.modelEditor("' + str(mEditor) + '", edit=True, ' + setting + '=' + str(i[setting]) + ')'
                    exec(execStr)

    def captureModelPaneSettings(self):
        for mPanel in self.panels:
            mEditDict = {'model_panel': mPanel, 'nurbsCurves': None, 'nurbsSurfaces': None, 'polymeshes': None, 'subdivSurfaces': None, 'planes': None,
                         'lights': None, 'cameras': None, 'joints': None, 'ikHandles': None, 'deformers': None, 'dynamics': None,
                         'fluids': None, 'hairSystems': None, 'follicles': None, 'nCloths': None, 'nParticles': None, 'dynamicConstraints': None,
                         'locators': None, 'dimensions': None, 'pivots': None, 'handles': None, 'textures': None, 'strokes': None,
                         'manipulators': None, 'controlVertices': None, 'hulls': None, 'grid': None, 'headsUpDisplay': None, 'selectionHiliteDisplay': None}

            mEditor = cmds.modelPanel(mPanel, query=True, modelEditor=True)
            cmds.modelEditor(mEditor, query=True, xr=True)

            for i in mEditDict:
                if i != 'model_panel':
                    exeStr = 'val = cmds.modelEditor("' + str(mEditor) + '", query=True, ' + str(i) + ' = True)'
                    exec(exeStr)
                    mEditDict[i] = val
            self.mPanelList.append(mEditDict)

    def printCaptureSettings(self):
        # make sure the panel exists
        for i in self.mPanelList:
            print '---- %s ----' % (i['model_panel'])
            for setting in i:
                if setting != 'model_panel':
                    print '\t%s = %s' % (setting, i[setting])
            print


def validateSelection():
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        if cmds.nodeType(sel) == 'transform':
            return sel[0]
    else:
        return None


def exportSculpt(path, sel=None):
    '''
    Provide the full path:eg. home/user/exportfile.txt .txt in the name is critical.
    sel = <Transform> Provide the transform that the sculpts are connected to, recommened through script
    sel = <None>(Default), recommended through User Interface calls
    '''
    # gui call, otherwise on object is expected
    if sel == None:
        sel = validateSelection()

    if sel != None:
        path = os.path.join(path, 'sculpt_set')
        # create the sculpt_set folder if one doesn't exist
        if not os.path.exists(path):
            os.mkdir(path)

        # get the shape
        shape = pm.ls(sel)[0].getShape().name()
        # get the sets
        sculptSets = cmds.listSets(type=2, object=shape)

        # iterate through each set
        for _set in sculptSets:
            if _set.rfind('tweak') == -1 and _set.rfind('skinCluster') == -1:
                # find the geo that the set is connected to
                deformer = cmds.listConnections(_set + '.usedBy', d=False, s=True)[0]
                # get the components in the set
                components = cmds.sets(_set, query=True)

                # Build the string to write to file, this is then later eval'd
                exportStr = '['
                for i, comp in enumerate(components):
                    if i + 1 != len(components):
                        exportStr += '"%s",' % comp
                    else:
                        exportStr += '"%s"' % comp
                exportStr += ']'
                # write out the file
                _file = open(os.path.join(path, _set + '.txt'), 'w')
                _file.write(deformer + '\n')
                _file.write(exportStr)
                _file.close()


def importSculpt(path, sel=None):
    '''
    Provide the full path:eg. home/user/exportfile.txt .txt in the name is critical.
    sel = <Transform> Provide the transform that the sculpts are connected to, recommened through script
    sel = <None>(Default), recommended through User Interface calls
    '''
    if sel == None:
        sel = validateSelection()

    if sel != None:
        # get a list of all the files
        path = os.path.join(path, 'sculpt_set')
        if os.path.exists(path):
            files = os.listdir(path)
            for f in files:
                # It's expected that only the sculpt files will be in here
                if os.path.splitext(f)[1] == '.txt':
                    # get the shape
                    shape = pm.ls(sel)[0].getShape().name()
                    _file = file(os.path.join(path, f), 'r')
                    info = _file.readlines()
                    _file.close()
                    deformer = info[0].strip('\n')
                    vertex = eval(info[1])
                    sculptset = cmds.listConnections(deformer + '.message', s=False, d=True)[0]
                    # clear the set
                    cmds.sets(cl=sculptset)
                    # add vertex to the set
                    cmds.sets(vertex, fe=sculptset)


def printSelectionAsSorted(*args):
    '''
    Convert the current selection to lower case the sort. Once sorted print the selection list
    '''
    sel = ls(sl=True)
    if len(sel) > 0:
        strLst = []
        for i in sel:
            strLst.append(str(i.name()))

        strLst.sort(key=str.lower)

        for i in strLst:
            print i
    else:
        wStr = 'Nothing select, select some objects...'
        OpenMaya.MGlobal.displayWarning(wStr)


def dragCallback(dragControl, x, y, modifiers):
    '''dragCallback is called when the user clicks the middle mouse button.The control is set to call this function
    when the control is created. Maya returns the name of the control that the middle click started from, the x, and y, and\n
    any modifiers eg. shift, ctrl being pressed at the same time.
    '''
    # check if the "shift" key is pressed
    if modifiers == 1:
        # Only the From and To textScrollLists will be affected
        if dragControl.rfind('atom_tw_infTsl') == -1:
            # get the selected index item, if the control is empty the query returns None
            index = cmds.textScrollList(dragControl, query=True, sii=True)
            if index != None:
                # remove the item from the list
                cmds.textScrollList(dragControl, edit=True, rii=index)
        # return 'None' so the drop call back ingnores the results
        return ['None']
    # no modifiers are selected that are relevant
    else:
        # this only affects the main influence list
        if dragControl.rfind('atom_tw_infTsl') > -1:
            # get the selected item
            item = cmds.textScrollList(dragControl, query=True, si=True)
            # make sure the list isn't empty
            if item != None and item != 'Select vertex on a skinned mesh.':
                return [item[0]]
            else:
                return['None']
        else:
            return ['None']


def dropCallback(dragControl, dropControl, messages, x, y, dragType):
    '''dropCallback called when the user drops after a drag
    Adds the draged item from the influence list and adds it to the list
    that's dropped on
    '''
    if messages[0] != 'None':
        # add the item to the text scroll list
        cmds.textScrollList(dropControl, edit=True, append=messages[0])


def disableTransferControls(masterList):
    # remove all the items in the textScrollList
    for control in masterList:
        cmds.textScrollList(control, en=False, edit=True, ra=True)
    # Reset the main influence list and the button
    cmds.textScrollList(masterList[0], edit=True, append='Select vertex on a skinned mesh.')
    cmds.button('atom_tw_btn', edit=True, en=False)


def atom_updateInfUI(*args):
    '''Function that updates the atom transfer weights user interface.
    This is run as a script job when the atom_tw_win it open
    '''
    # get the current selection
    sel = cmds.ls(sl=True, fl=True)
    masterList = ['atom_tw_infTsl', 'atom_tw_fromTsl', 'atom_tw_toTsl']
    if len(sel) > 0:
        # check if a vertex is selected
        modeCheck = sel[0].rfind('vtx[')
        # create a list with the textScrollList control names of the win
        if modeCheck > 0:
            # make sure a mesh nodeType is selected
            if cmds.nodeType(sel[0]) == 'mesh':
                # get the skinCluster influence list
                skin = mm.eval('findRelatedSkinCluster("' + cmds.ls(sl=True, fl=True)[0].split('.')[0] + '")')
                if skin != None and len(skin) > 0:
                    infList = cmds.skinCluster(skin, query=True, inf=True)
                    # clear all the lists
                    for control in masterList:
                        cmds.textScrollList(control, en=True, edit=True, ra=True)
                    for inf in sorted(infList):
                        cmds.textScrollList(masterList[0], edit=True, append=inf)
                    cmds.button('atom_tw_btn', edit=True, en=True)
                else:
                    disableTransferControls(masterList)
            else:
                disableTransferControls(masterList)
        # A vertex isn't selected so disable the UI
        else:
            disableTransferControls(masterList)
    else:
        disableTransferControls(masterList)


def findListIndex(findList, value):
    '''Finds the index of the value in the findlist
    findList<list>
    value<string>
    '''
    for i in range(0, len(findList), 1):
        if findList[i] == value:
            return i


def transferWeights(*args):
    sel = cmds.ls(sl=True, fl=True)
    skin = mm.eval('findRelatedSkinCluster("' + sel[0].split('.')[0] + '")')
    infList = cmds.textScrollList('atom_tw_infTsl', query=True, ai=True)
    # list the influences in the From and Two lists
    fromList = cmds.textScrollList('atom_tw_fromTsl', query=True, ai=True)
    toList = cmds.textScrollList('atom_tw_toTsl', query=True, ai=True)
    # make sure the lists are the same length/count
    if len(fromList) == len(toList):
        for i in range(0, len(fromList), 1):
            # put a hold on all the influences, then unhold the from influence and the to influence
            for j in infList:
                cmds.skinCluster(skin, edit=True, inf=j, lw=True)
            # unhold the influences that are to have the weighting transfered
            cmds.skinCluster(skin, edit=True, inf=fromList[i], lw=False)
            cmds.skinCluster(skin, edit=True, inf=toList[i], lw=False)
            # add a weight of 1 to the "to" influence. With normalization on only the
            # weights from the from influence will be transfered
            cmds.skinPercent(skin, sel, tv=[toList[i], 1])
            # Turn off the hold on all the influences
            for j in infList:
                cmds.skinCluster(skin, edit=True, inf=j, lw=False)
    else:
        print '=== From and To list must have the same amount of objects, process aborted! ==='


def helpWin(*args):
    '''help file on how to use the transfer weights tool
    '''
    win_name = "atom_tw_help win"
    if cmds.window(win_name, exists=True):
        cmds.deleteUI(win_name)
    win = cmds.window(win_name, t='Atom Trasfer Weights Help', rtf=True)
    cmds.paneLayout()
    cmds.textScrollList('aton_helpTsl',
                        append=['This tool was designed to trasfer influence weights. When Mayas mirror weights',
                                'puts weighting on both sides of the mesh using with one influence.', 'Usage:',
                                'Select the vertex you want to transfer weighting to', 'Middle mouse drag the influences in the Copy and Paste',
                                'Click the Transfer Weighting button'])
    cmds.showWindow(win)

# used with atom lock win


def lockCmd(control, state):
    selected = cmds.ls(sl=True)
    attribute = cmds.optionMenu('alw_optionMenu', query=True, v=True).lower()
    checked = ui.getCheckBoxSelectionAsList(control)
    for sel in selected:
        for i in range(0, 3, 1):
            if checked[i] == 1:
                if attribute != 'visibility':
                    axis = ui.convertAxisNum(i + 1)
                    cmds.setAttr('%s.%s%s' % (sel, attribute, axis), lock=state)
                else:
                    cmds.setAttr('%s.%s' % (sel, attribute), lock=state)
            else:
                if attribute == 'visibility':
                    cmds.setAttr('%s.%s' % (sel, attribute), lock=state)

# used with atom lock win


def keyableCmd(control, state):
    selected = cmds.ls(sl=True)
    attribute = cmds.optionMenu('alw_optionMenu', query=True, v=True).lower()
    checked = ui.getCheckBoxSelectionAsList(control)
    for sel in selected:
        for i in range(0, 3, 1):
            if checked[i] == 1:
                if attribute != 'visibility':
                    axis = ui.convertAxisNum(i + 1)
                    cmds.setAttr('%s.%s%s' % (sel, attribute, axis), keyable=state)
                else:
                    cmds.setAttr('%s.%s' % (sel, attribute), keyable=state)
            else:
                if attribute == 'visibility':
                    cmds.setAttr('%s.%s' % (sel, attribute), keyable=state)


def atomLockWin(*args):
    if cmds.window('atom_lock_win', ex=True):
        cmds.deleteUI('atom_lock_win')
    # atom lock win = alw
    width = 100
    cmds.window('atom_lock_win', title='Atom Lock Window')
    alw_mainForm = cmds.formLayout('alw_form', numberOfDivisions=100)
    alw_optionMenu = cmds.optionMenu('alw_optionMenu', width=width)
    cmds.menuItem(label='Translate')
    cmds.menuItem(label='Scale')
    cmds.menuItem(label='Rotate')
    cmds.menuItem(label='Visibility')
    alw_checkBoxGrp = cmds.checkBoxGrp('alw_checkBoxGrp', numberOfCheckBoxes=3, labelArray3=['X', 'Y', 'Z'],
                                       cw3=[39, 39, 39], cl4=['left', 'center', 'center', 'center'], h=19)

    alw_lockButton = cmds.button('alw_lockButton', c='import atom_utilities_lib\natom_utilities_lib.lockCmd("alw_checkBoxGrp",True)', label='Lock', width=width)
    alw_unlockButton = cmds.button('alw_unlockButton', c='import atom_utilities_lib\natom_utilities_lib.lockCmd("alw_checkBoxGrp",False)', label='Unlock', width=width)
    alw_keyableButton = cmds.button('alw_keyableButton', c='import atom_utilities_lib\natom_utilities_lib.keyableCmd("alw_checkBoxGrp",True)', label='Keyable', width=width)
    alw_nonkeyableButton = cmds.button('alw_nonkeyableButton', c='import atom_utilities_lib\natom_utilities_lib.keyableCmd("alw_checkBoxGrp",False)', label='Non-Keyable', width=width)

    cmds.formLayout(alw_mainForm, edit=True,

                    attachForm=[(alw_optionMenu, 'top', 5), (alw_optionMenu, 'left', 5),
                                (alw_checkBoxGrp, 'top', 5),
                                (alw_lockButton, 'left', 5), (alw_nonkeyableButton, 'left', 5)],
                    attachControl=[(alw_checkBoxGrp, 'left', 5, alw_optionMenu),
                                   (alw_lockButton, 'top', 5, alw_optionMenu),
                                   (alw_unlockButton, 'left', 5, alw_lockButton), (alw_unlockButton, 'top', 5, alw_optionMenu),
                                   (alw_keyableButton, 'top', 5, alw_lockButton),
                                   (alw_keyableButton, 'left', 5, alw_nonkeyableButton), (alw_nonkeyableButton, 'top', 5, alw_unlockButton)]
                    )

    cmds.showWindow('atom_lock_win')


def transferWin(*args):
    '''
    Transfer weights user interface
    '''
    window_name = "atom_tw_win"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    jobNum = cmds.scriptJob(e=["SelectionChanged", atom_updateInfUI])

    # transfer weighting = tw
    cmds.window(window_name, t='Atom Trasfer Weights', rtf=True, menuBar=True)
    cmds.scriptJob(uiDeleted=[window_name, 'cmds.scriptJob(kill=' + str(jobNum) + ',force=True)'])
    cmds.menu('atom_tw_menuBar', label='Help')
    cmds.menuItem(label='Help', c=helpWin)

    cmds.formLayout('atom_tw_main_formLayout')

    cmds.paneLayout('atom_tw_paneLayout', cn='vertical3', height=300)

    infListForm = cmds.formLayout('atom_infList_form')
    infListTxt = cmds.text('atom_infList_txt', l='Influence List:', align='left')
    mir_infTsl = cmds.textScrollList('atom_tw_infTsl', en=False, numberOfRows=10, width=100, allowMultiSelection=False, append='Select vertex on a skinned mesh.', dgc=dragCallback)

    cmds.formLayout(infListForm, edit=True,
                    attachForm=[(infListTxt, 'top', 5), (infListTxt, 'left', 5),
                                (mir_infTsl, 'left', 5), (mir_infTsl, 'right', 5), (mir_infTsl, 'bottom', 5)],
                    attachControl=[(mir_infTsl, 'top', 5, infListTxt)]
                    )
    cmds.setParent('..')

    fromListForm = cmds.formLayout('atom_fromList_form')
    fromListTxt = cmds.text('atom_fromList_txt', l='Copy Weights From:', align='left')
    mir_fromTsl = cmds.textScrollList('atom_tw_fromTsl', en=False, numberOfRows=10, width=100, allowMultiSelection=False, dgc=dragCallback, dpc=dropCallback)

    cmds.formLayout(fromListForm, edit=True,
                    attachForm=[(fromListTxt, 'top', 5), (fromListTxt, 'left', 5),
                                (mir_fromTsl, 'left', 5), (mir_fromTsl, 'right', 5), (mir_fromTsl, 'bottom', 5)],
                    attachControl=[(mir_fromTsl, 'top', 5, fromListTxt)]
                    )
    cmds.setParent('..')

    toListForm = cmds.formLayout('atom_toList_form')
    toListTxt = cmds.text(l='Paste Weights To:', align='left')
    mir_toTsl = cmds.textScrollList('atom_tw_toTsl', en=False, numberOfRows=10, width=100, allowMultiSelection=False, dgc=dragCallback, dpc=dropCallback)

    cmds.formLayout(toListForm, edit=True,
                    attachForm=[(toListTxt, 'top', 5), (toListTxt, 'left', 5),
                                (mir_toTsl, 'left', 5), (mir_toTsl, 'right', 5), (mir_toTsl, 'bottom', 5)],
                    attachControl=[(mir_toTsl, 'top', 5, toListTxt)]
                    )
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.button('atom_tw_btn', l='Transfer Weighting', c=transferWeights, en=False)

    cmds.formLayout('atom_tw_main_formLayout', edit=True,
                    attachForm=[('atom_tw_paneLayout', 'top', 5), ('atom_tw_paneLayout', 'left', 5), ('atom_tw_paneLayout', 'right', 5), ('atom_tw_paneLayout', 'bottom', 40),
                                ('atom_tw_btn', 'left', 5), ('atom_tw_btn', 'right', 5), ('atom_tw_btn', 'bottom', 5)],
                    attachControl=[('atom_tw_btn', 'top', 5, 'atom_tw_paneLayout')]
                    )
    atom_updateInfUI()
    cmds.showWindow(window_name)
