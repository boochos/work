import maya.cmds as cmds
import maya.mel as mm
import os
import sys
import key_sys_lib


class intSliderGrp(object):

    '''Description: Class that builds a label, textFieldGrp and an intScrollBar. The textField can have int values
    entered into it and have the scroll bar updated. When the scroll bar has been changed the field will update with
    the scroll bars value.\n
    internalName<string>: The internal name of the maya control\n
    label<string>       : The visible label on the control\n
    decimal<int>        : How many decimal places the field should have\n
    leftspace<int>      : Left spacing of the slider and field\n
    minVal<int>         : Minimum value of the slider\n
    maxVal<int>         : Maximum value of the slider\n
    cmd<object>         : Command object to pass to the controls\n
    '''

    def __init__(self, internalName, label, decimal, step, leftSpace, minVal, maxVal, cmd=False):

        self.name = internalName
        self.label = label
        self.decimal = decimal
        self.leftSpace = leftSpace
        self.minVal = minVal
        self.maxVal = maxVal
        self.step = step
        self.txtFld = self.name + '_txtFld'
        self.intSldr = self.name + '_scrb'
        self.txt = self.name + '_txt'
        self.cmd = cmd

    def validateFieldInput(self, *args):
        '''Description: Validate the input of the text field. Allowing only int\n
        '''
        # get the current text in the field
        txt = cmds.textField(self.txtFld, query=True, tx=True)
        intCheck = True
        # test that all the characters are a number
        for i in txt:
            try:
                # convert the string to an int, if it fails, the string isn't an int
                int(i)
            except:
                print '%s, value is not an interger' % (txt)
                # Reset the field to what the slider currently is
                self.sliderCC()
                # fail the check
                intCheck = False
                break

        if intCheck:
            n = int(txt)

            # make sure the value is within the min and max
            if n >= int(self.minVal) and n <= int(self.maxVal):
                parseStr = '%0' + str(self.decimal) + 'd'
                num = parseStr % (int(txt))
                # update the control
                cmds.textField(self.txtFld, edit=True, tx=num)
                cmds.intScrollBar(self.intSldr, edit=True, v=int(num))
                # execute the extra command
                if self.cmd != False:
                    self.cmd()
            else:
                # provide feedback to the user
                key_sys_lib.printMayaWarning('Min and Max values are forced.')
                self.sliderCC()

    def sliderCC(self, *args):
        '''Description: Command that's executed when the slider is changed
        '''
        parseStr = '%0' + str(self.decimal) + 'd'
        num = parseStr % (cmds.intScrollBar(self.intSldr, query=True, v=True))
        # update the textField
        cmds.textField(self.txtFld, edit=True, tx=num)
        # execute the extra command
        if self.cmd != False:
            self.cmd()

    def intSliderGrp(self):
        '''Description: Build the controls
        '''
        frm = cmds.formLayout(self.name + '_formLayout', numberOfDivisions=100)
        cmds.text(self.txt, l=self.label)

        cmds.textField(self.txtFld, tx=(('%0' + str(self.decimal) + 'd') % (int(self.minVal))),
                       cc= self.validateFieldInput)

        # create the intScrollBar
        cmds.intScrollBar(self.intSldr, min=int(self.minVal), h=18, max=int(self.maxVal), value=int(self.minVal), step=1,
                          largeStep=self.step, cc=self.sliderCC)
        # place the controls
        cmds.formLayout(frm, edit=True,
                        attachForm=[(self.txt, 'left', 0), (self.txt, 'top', 5),
                                    (self.txtFld, 'top', 5), (self.txtFld, 'right', 5),
                                    (self.txtFld, 'left', self.leftSpace),
                                    (self.intSldr, 'left', self.leftSpace), (self.intSldr, 'right', 5)],
                        attachControl=[(self.intSldr, 'top', 5, self.txtFld)]
                        )
        cmds.setParent('..')


class DirDialog_v01(object):

    '''Allows the useer to navigate their directory structure and set a specific directory
    '''
    class CMD(object):

        '''Command that's used by then menuItems
        '''

        def __init__(self, parent, path):
            self.parent = parent
            self.path = path

        def gotoBookmarkCmd(self, *args):
            self.parent.gotoBookmark(self.path)

    def __init__(self, intWinName, visWinName, buttonLabel, path):
        # set the class properties with the given arguments
        self.intWinName = intWinName
        self.visWinName = visWinName
        self.buttonLabel = buttonLabel
        self.path = path
        self.mainMenu = None
        self.pathTxt = None
        self.paneLayout = None
        self.textScrollList = None
        self.cMenu = None
        self.button = self.intWinName + '_button'

    def popWin(self):
        '''Populate the textScrollList with the directories in self.path
        '''
        # clear the list
        cmds.textScrollList(self.textScrollList, edit=True, ra=True)
        # append with '..', which means go up one level
        cmds.textScrollList(self.textScrollList, edit=True, append='..')
        directories = os.listdir(self.path)
        # start an empty list to populate with the final directory strings
        clean = []
        for d in directories:
            # make sure the current item doesnt have a '.' in front and just to be
            # safe make sure it exists
            if d[0] != '.' and os.path.isdir(self.path + '/' + d):
                clean.append(str(d))

        # convert all the strings to lower case and sort
        clean.sort(key=str.lower)
        # add the lo
        cmds.textScrollList(self.textScrollList, edit=True, append=clean)

    def dcc(self, *args):
        '''Command that's executed when a textScollList item is double clicked
        '''
        currentPath = self.path
        # get the item just clicked on
        selItem = cmds.textScrollList(self.textScrollList, query=True, si=True)
        # A click is recorded even if an element isn't selected in the menu
        if selItem != None:
            # if the selection is '..' then go up a directory
            if selItem[0] == '..':
                walkUp = os.path.split(self.path)
                cmds.text(self.pathTxt, edit=True, l=walkUp[0])
                self.path = walkUp[0]
                self.popWin()
            # else go down a directory
            else:
                fullPath = os.path.join(currentPath, selItem[0])
                cmds.text(self.pathTxt, edit=True, l=fullPath)
                self.path = fullPath
                self.popWin()

    def gotoBookmark(self, path):
        '''Command that's used by the bookmarks to set the bookmark directory in the browser
        '''
        self.path = path
        self.popWin()
        cmds.text(self.pathTxt, edit=True, l=path)

    def buildBookmarks(self):
        '''Called when the UI is opened to build the menu and it's bookmarks
        '''
        # Get the name of the current maya file
        name = cmds.file(query=True, sceneName=True)
        threedIdx = name.rfind('3D')
        seq = name.rfind('SEQ')

        home = os.getenv('HOME')
        cmds.menuItem(self.intWinName + '_homeMenuItem', l='H o m e', c=lambda *args: self.gotoBookmark(home))
        cmds.menuItem(self.intWinName + '_desktopMenuItem', l='D e s k t o p', c=lambda *args: self.gotoBookmark(os.path.join(home, 'Desktop')))
        cmds.menuItem(divider=True)

        if len(name) != 0:
            if seq != -1:
                seqPath = name[:seq + 3]
                cmds.menuItem(self.intWinName + '_seqMenuItem', l=seqPath, c=lambda *args: self.gotoBookmark(seqPath))
                fDict = {}
                i = 0

                # split the path appart to find specific folders
                # then put the contents into a dictionary to extrant the index by key
                pathSplit = name.split('/')
                for d in pathSplit:
                    fDict[d] = i
                    i += 1
                # looking for the folder just down from SEQ in the name
                if os.path.exists(os.path.join(name[:seq + 3], pathSplit[fDict['SEQ'] + 1])):
                    cmds.menuItem(self.intWinName + '_seqSubMenuItem', l=os.path.join(name[:seq + 3], pathSplit[fDict['SEQ'] + 1]),
                                  c=lambda *args: self.gotoBookmark(os.path.join(name[:seq + 3], pathSplit[fDict['SEQ'] + 1])))
            if threedIdx != -1:
                root = name[:threedIdx + 2]

                cmds.menuItem(self.intWinName + '_threeDmenuItem', l=os.path.split(root)[0], c=lambda *args: self.gotoBookmark(os.path.split(root)[0]))
                delPath = os.path.join(os.path.split(root)[0], '2D/3D_Delivery')
                if os.path.exists(delPath):
                    cmds.menuItem(self.intWinName + '_twoDDelivery', l=delPath, c=lambda *args: self.gotoBookmark(delPath))

                cmds.menuItem(self.intWinName + '_rootMenuItem', l=root, c=lambda *args: self.gotoBookmark(root))
                cmds.menuItem(self.intWinName + '_scenesMenuItem', l=os.path.join(root, 'scenes'), c=lambda *args: self.gotoBookmark(os.path.join(root, 'scenes')))
                cmds.menuItem(self.intWinName + '_dataMenuItem', l=os.path.join(root, 'data'), c=lambda *args: self.gotoBookmark(os.path.join(root, 'data')))
        else:
            print 'No file name found, save file...'

    def buildCustomBookmarks(self):
        '''Reads any custom paths that the user may have saved
        '''
        # check that a the bookmark file has been saved
        bFile = os.path.join(os.getenv('HOME'), 'key_custom_bookmark.txt')
        if os.path.isfile(bFile):
            #open, read and process
            bFile = open(bFile, 'r')
            fLines = bFile.readlines()
            cnt = 1
            for l in fLines:
                mStr = l.strip('\n')
                cObj = self.CMD(self, mStr)
                # interate the control names to insure a clean ui builds
                cmds.menuItem(self.intWinName + '_customMenuItem_' + str(cnt), l=mStr, parent=self.cMenu, c=cObj.gotoBookmarkCmd)
                cnt += 1

    def deleteCurrentBookmark(self, *args):
        '''Delete the current path in the self.path from the bookmark file and any identical paths in the UI
        '''
        # get a list of menuItems from the custom bookmark menu
        menuItems = cmds.menu(self.cMenu, query=True, ia=True)
        # open the bookmark file
        bFile = open(os.path.join(os.getenv('HOME'), 'key_custom_bookmark.txt'), 'r')
        bLines = bFile.readlines()
        bFile.close()
        # The first three elements can be skipped as they're permanent
        for i in range(3, len(menuItems), 1):
            if self.path == cmds.menuItem(menuItems[i], query=True, l=True):
                keepList = []
                bFile = open(os.path.join(os.getenv('HOME'), 'key_custom_bookmark.txt'), 'w')
                cnt = 0
                for l in bLines:
                    line = l.strip('\n')
                    if line != self.path:
                        if cnt == 0:
                            bFile.write(line)
                            cnt += 1
                        else:
                            bFile.write('\n' + line)

                bFile.close()
        # delete everything in the menu, then rebuild it
        cmds.menu(self.cMenu, edit=True, dai=True)
        self.buildCmenuItems()
        self.buildCustomBookmarks()

    def saveCurrentToBookmark(self, *args):
        '''Save the curret path in self.path to file and add it to the custom bookmark menu
        '''
        filePath = os.path.join(os.getenv('HOME'), 'key_custom_bookmark.txt')
        if not os.path.isfile(filePath):
            # there is no bookmark file so save one
            bFile = open(filePath, 'w')
            bFile.close()

        bFile = open(filePath, 'r+')
        if len(bFile.readlines()) == 0:
            bFile.write(self.path)
        else:
            bFile.write('\n' + self.path)
        bFile.close()

        # create the command class
        cmd = self.CMD(self, self.path)
        # get the menuItem count as this will be appended, this is for the control name
        cbmSize = cmds.menu(self.cMenu, query=True, ia=True)

        # Add the menuItem
        cmds.menuItem(self.intWinName + '_customMenuItem_' + str(len(cbmSize) - 2), l=self.path, parent=self.cMenu, c=cmd.gotoBookmarkCmd)

    def buildCmenuItems(self, *args):
        '''Build the default menuItems
        '''
        cmds.menuItem(self.intWinName + '_saveCurrentMenuItem', l='Save Current', c=self.saveCurrentToBookmark)
        cmds.menuItem(self.intWinName + '_delCurrentMenuItem', l='Delete Current', c=self.deleteCurrentBookmark)
        cmds.menuItem(self.intWinName + '_dividerMenuItem', divider=True)

    def makeBaseControls(self):
        '''Make the base controls for the UI
        '''
        # add the bookmarks
        cmds.menu(self.intWinName + 'bmMenu', l='Bookmarks')
        self.buildBookmarks()
        self.cMenu = cmds.menu(self.intWinName + '_customBmMenu', l='Custom Bookmarks')
        self.buildCmenuItems()
        self.buildCustomBookmarks()

        # Add the other controls
        self.mainForm = cmds.formLayout(self.intWinName + '_mainForm', numberOfDivisions=100)
        self.textScrollList = cmds.textScrollList(self.intWinName + '_tsl', dcc=self.dcc)
        self.pathTxt = cmds.text(self.intWinName + '_text', h=30, l=self.path, font='boldLabelFont')

    def buildButton(self):
        '''Builds the button, this is solo so it can be easily overloaded when the class is instanced if needed
        '''
        cmds.button(self.button, l=self.buttonLabel)

    def editLayout(self):
        '''Edit the main layout
        '''
        cmds.formLayout(self.mainForm, edit=True,
                        attachForm=[(self.textScrollList, 'top', 5), (self.textScrollList, 'left', 5),
                                    (self.textScrollList, 'right', 5), (self.textScrollList, 'bottom', 75),
                                    (self.pathTxt, 'left', 5), (self.pathTxt, 'right', 5),
                                    (self.button, 'left', 5), (self.button, 'right', 5), (self.button, 'bottom', 5)],
                        attachControl=[(self.pathTxt, 'top', 5, self.textScrollList),
                                       (self.button, 'top', 10, self.pathTxt)]
                        )

    def win(self):
        '''Create the main window 
        '''
        if cmds.window(self.intWinName, exists=True):
            cmds.deleteUI(self.intWinName, window=True)

        cmds.window(self.intWinName, menuBar=True, title=self.visWinName, width=350, height=260)
        self.makeBaseControls()
        self.buildButton()
        self.editLayout()
        self.popWin()
        cmds.showWindow(self.intWinName)


class NameDialog_v01(object):

    '''Description: Builds a class that has a ui to manipulate naming within the confines
    of the approved naming convnetion.
    '''
    class SaveMenuCMD(object):

        def __init__(self, parent, menuItem):
            '''Description:Command used in the menuItem, a command object is created to pass information\n
            from the control\n
            parent<object>  : Used to keep class variables in scope\n
            menuItem<string>: the menuItem 
            '''
            self.parent = parent
            self.menuItem = menuItem

        def setNameFromMenuItemCMD(self, *args):
            self.parent.setNameFromMenuItem(self.menuItem)

    # Instance the intSliderGrp and manipulate them within the scope of
    # NameDialog_v01 class
    class NameIntSliderGrp(intSliderGrp):
        pass

    def __init__(self, intWinName, visWinName, buttonLabel):
        '''
        intWinName<string> : Internal name of the window\n
        visWinName<string> : Visibile name of the window\n
        buttonLabel<string>: Visible label of on the button\n
        '''
        self.intWinName = intWinName
        self.visWinName = visWinName
        self.cmdButtonLabel = buttonLabel
        self.baseName = os.path.basename(cmds.file(query=True, sceneName=True)).split('.')[0]
        self.saveFilePath = os.path.join(os.getenv('HOME'), 'key_saved_name.txt')
        self.nameTxt = 'key_nameTxt'

        # Get the current maya project path
        #self.basePath          = os.getenv('MAYA_PROJECT_SEQ_PATH')
        name = cmds.file(query=True, sceneName=True)
        splt = name.rfind('SEQ')
        if os.path.exists(name[:splt + 3]):
            self.basePath = name[:splt + 3]

        elif os.path.exists(os.getenv('MAYA_PROJECT_SEQ_PATH')):
            self.basePath = os.getenv('MAYA_PROJECT_SEQ_PATH')
            print '//Warning: Scene name invalid, defaulting to MAYA_PROJECT_SEQ_PATH'
        else:
            self.basePath = os.getenv('HOME')
            print '//Warning: MAYA_PROJECT_SEQ_PATH invalid, defaulting to HOME'

        self.seqDirs = self.getSequenceDirectories()

        # These list are used to create the items in the sequence textScrollList
        # departmentList and departmentKey must be the same length
        self.departmentList = ['Anim - Animation', 'Cam - Camera', 'Comp - Shot Compositing',
                               'Dev - Development', 'FX - Effects', 'Light - Lighting', 'MM - Match Move',
                               'MM_Anim - Matchmove Animation', 'Pre_Comp - Comp shot prep',
                               'Pre_Light - Matchmove Lighting', 'PreVis - Shot Previs Anim']
        self.departmentKey = ['Anim', 'Cam', 'Comp', 'Dev', 'FX', 'Light', 'MM', 'MM_Anim', 'Pre_Comp',
                              'Pre_Light', 'PreVis']

        # Create a dict of the two lists, the dict is used in the name builder
        self.departmentDict = dict(zip(self.departmentKey, self.departmentList))

        # Create the names for the other controls
        self.txtScrlMainFrm = self.intWinName + '_mainForm'
        self.txtScrlTxt = self.intWinName + '_seqtxt'
        self.txtScrlLst = self.intWinName + '_txtSclLst'
        self.button = self.intWinName + '_button'
        self.department = self.intWinName + '_department_optGrp'
        self.asset = self.intWinName + '_asset_txtFldGrp'
        self.nameModeCB = self.intWinName + '_nameMode_CB'

        # Populated later with UI classes
        self.sequence = None
        self.shot = None
        self.scene = None
        self.version = None
        self.revision = None

    def getNameFromScene(self, *args):
        path = cmds.file(query=True, sceneName=True)
        if path != '':
            name = os.path.basename(path)
            rFind = name.rfind('.')
            finalName = name[:rFind]
            cmds.textFieldGrp(self.asset, edit=True, tx=finalName)
            cmds.text(self.nameTxt, edit=True, l=finalName)
        else:
            key_sys_lib.printMayaWarning('File has not been save, no scene name to populate.')

    def buildName(self, *args):
        '''
        Description:Function that queries the controls and builds a final name based on their
        contents.
        '''
        if cmds.checkBox(self.nameModeCB, query=True, value=True):
            asset = cmds.textFieldGrp(self.asset, query=True, tx=True)
            cmds.text(self.nameTxt, edit=True, l=asset)

        else:

            # Check what's selected in the text scroll List
            finalName = cmds.textScrollList(self.txtScrlLst, query=True, si=True)

            # nothing is selected, so force the selection of the first item
            if finalName == None:
                seqLength = len(self.seqDirs)
                cmds.textScrollList(self.txtScrlLst, edit=True, sii=(seqLength - seqLength) + 1)
                finalName = cmds.textScrollList(self.txtScrlLst, query=True, si=True)[0]
            #something is selected
            else:
                finalName = cmds.textScrollList(self.txtScrlLst, query=True, si=True)[0]

            finalName += '_' + str(cmds.textField(self.scene.txtFld, query=True, tx=True))
            finalName += '_' + str(cmds.textField(self.shot.txtFld, query=True, tx=True))

            # check the department
            department = cmds.optionMenuGrp(self.department, query=True, v=True)
            if department != 'None':
                # Department strings have a space from the object to description, this is how
                # they're being separated
                finalName += '_' + department.split(' ')[0]

            # Check the asset
            asset = cmds.textFieldGrp(self.asset, query=True, tx=True)
            if asset != 'None':
                finalName += '_' + asset

            finalName += '_v' + str(cmds.textField(self.version.txtFld, query=True, tx=True))
            finalName += '_r' + str(cmds.textField(self.revision.txtFld, query=True, tx=True))

            # Add the final name to the self.nameTxt
            cmds.text(self.nameTxt, edit=True, l=finalName)

    def getSequenceDirectories(self):
        '''Get the directories in the provided path.
        '''
        dirs = os.listdir(self.basePath)
        dirs.sort()
        rList = []
        for d in dirs:
            if d[0] != '.' and os.path.isdir(os.path.join(self.basePath, d)):
                rList.append(d)

        return rList

    def validateFieldInputAsStr(self, *args):
        if not cmds.checkBox(self.nameModeCB, query=True, v=True):
            '''Check the input to make sure it's a valid entry
            '''
            returnStr = cmds.textFieldGrp(self.asset, query=True, tx=True)
            exp = ' !@#$%^&*()+-={}|[]\\:\"\';<>?,./_'
            if len(returnStr) > 0:
                for element in returnStr:
                    for itm in exp:
                        if element == itm:
                            cmds.textFieldGrp(self.asset, edit=True, tx='None')
                            break
            else:
                cmds.textFieldGrp(self.asset, edit=True, tx='None')

        self.buildName()

    def populateOptionMenuGrp(self, popList):
        '''After an optionMenuGrp is created, populate it with a list
        '''
        for txt in popList:
            cmds.menuItem(label=txt)

    def setNameFromMenuItem(self, menuItem):
        '''Command run by menuItems to set the name to reflect the selection
        '''
        name = menuItem[:menuItem.rfind('_')]
        self.baseName = name
        cmds.text(self.nameTxt, edit=True, l=name)
        self.parseSceneNameAndPopulate()

    def saveCurrentName(self, *args):
        '''Save the current name to file
        '''
        if not os.path.isfile(self.saveFilePath):
            nFile = open(filePath, 'w')
            nFile.close()

        name = cmds.text(self.nameTxt, query=True, l=True)
        nFile = open(self.saveFilePath, 'a')

        if os.path.getsize(self.saveFilePath) == 0:
            nFile.write(name)
        else:
            nFile.write('\n' + name)
        nFile.close()

        menuItemName = name + '_mi'
        if not cmds.menuItem(menuItemName, query=True, ex=True):
            cmd = self.SaveMenuCMD(self, menuItemName)
            cmds.menuItem(menuItemName, label=name, parent=self.nameMenu, c=cmd.setNameFromMenuItemCMD)

    def buildMenuBar(self):
        '''Build the contents of the menuBar
        '''
        self.nameMenu = cmds.menu(self.intWinName + '_nameMenu', label='Name')
        cmds.menuItem(self.intWinName + '_saveCurrentName_mi', l='Save', c=self.saveCurrentName)
        cmds.menuItem(divider=True)
        if os.path.isfile(self.saveFilePath):
            nFile = open(self.saveFilePath, 'r')
            names = nFile.readlines()
            for name in names:
                name = name.strip('\n')
                name = name.strip(' ')
                if len(name) > 0:
                    menuItemName = name.strip('\n') + '_mi'
                    if not cmds.menuItem(menuItemName, query=True, ex=True):
                        cmd = self.SaveMenuCMD(self, menuItemName)
                        cmds.menuItem(menuItemName, label=name, parent=self.nameMenu, c=cmd.setNameFromMenuItemCMD)

    def textScrollListGrp(self, label):
        '''Build the Sequence text and textScrollList
        '''
        form = cmds.formLayout(self.txtScrlMainFrm)
        txt = cmds.text(self.txtScrlTxt, l=label)
        txtScrlLst = cmds.textScrollList(self.txtScrlLst, nr=len(self.seqDirs), append=self.seqDirs, sc=self.buildName, sii=1)

        cmds.formLayout(form, edit=True,
                        attachForm=[(txt, 'top', 0), (txt, 'left', 5),
                                    (txtScrlLst, 'right', 0), (txtScrlLst, 'top', 0), (txtScrlLst, 'bottom', 0)],
                        attachControl=[txtScrlLst, 'left', 7, txt])
        cmds.setParent('..')

    def buildNameContents(self):
        '''
        Build the lower section of the GUI
        '''
        cw = 78
        self.textScrollListGrp('Sequence:')

        cmds.columnLayout(self.intWinName + '_nameConColumnLayout', adj=True, cat=['both', 5], rs=2)

        cmds.checkBox(self.nameModeCB, l='Manual Mode', onc=self.getNameFromScene)

        # Scene
        self.scene = self.NameIntSliderGrp(self.intWinName + '_scene', 'Scene:', 3, 1, cw, 1, 200, self.buildName)
        self.scene.intSliderGrp()
        # Shot
        self.shot = self.NameIntSliderGrp(self.intWinName + '_shot', 'Shot:', 3, 1, cw, 1, 100, self.buildName)
        self.shot.intSliderGrp()
        # Department
        cmds.optionMenuGrp(self.department, l='Department: ', ni=10, cw=(1, cw),
                           adj = 2, ct2 = ('left', 'right'), cat=[2, 'right', 5], cc=self.buildName)
        self.populateOptionMenuGrp(self.departmentList)
        # Asset
        cmds.textFieldGrp(self.asset, l='Asset:', tx='None', adj=2, cw=(1, cw), cal=(1, 'left'), cat=[2, 'right', 5],
                          cc=self.validateFieldInputAsStr)
        # Version
        self.version = self.NameIntSliderGrp(self.intWinName + '_version', 'Version:', 4, 1, cw, 1, 20, self.buildName)
        self.version.intSliderGrp()
        # Revision
        self.revision = self.NameIntSliderGrp(self.intWinName + '_revision', 'Revision:', 4, 1, cw, 1, 250, self.buildName)
        self.revision.intSliderGrp()

        cmds.separator(height=20, style='double')
        cmds.text(self.nameTxt, l='My_mommy_didnt_love_me_enough', font='boldLabelFont')
        cmds.separator(height=20, style='double')

    def parseSceneNameAndPopulate(self):
        '''Look at the scene name and try populate the menus
        '''
        splitName = self.baseName.split('_')
        splitLen = len(splitName)
        seq = None
        scene = None
        shot = None
        dep = None
        asset = None
        version = None
        revision = None

        if splitLen >= 6:
            seq = splitName[0]
            scene = splitName[1]
            shot = splitName[2]
            dep = splitName[3]
            # Pre_Light, Pre_Comp and MM_Anim have to be handled a bit different
            if dep == 'Pre' or dep == 'MM':
                dep = splitName[3] + '_' + splitName[4]
                del splitName[4]
                splitLen = len(splitName)
            version = splitName[len(splitName) - 2]
            revision = splitName[len(splitName) - 1]
            if splitLen == 7:
                asset = splitName[4]

            if len(self.seqDirs) != 0:
                for i in range(0, len(self.seqDirs), 1):
                    if seq == self.seqDirs[i]:
                        cmds.textScrollList(self.txtScrlLst, edit=True, sii=i + 1)
                        break
            else:
                key_sys_lib.printMayaWarning('Sequence not found, Sequence population failed.')

            if scene != None:
                try:
                    int(scene)
                except:
                    key_sys_lib.printMayaWarning('Scene is not an integer value, scene population failed.')
                else:
                    cmds.textField(self.scene.txtFld, edit=True, tx=scene)
                    cmds.intScrollBar(self.scene.intSldr, edit=True, v=int(scene))

            if shot != None:
                try:
                    int(shot)
                except:
                    key_sys_lib.printMayaWarning('Scene is not an integer value, shot population failed.')
                else:
                    cmds.textField(self.shot.txtFld, edit=True, tx=shot)
                    cmds.intScrollBar(self.shot.intSldr, edit=True, v=int(shot))

            if self.departmentDict.has_key(dep):
                cmds.optionMenuGrp(self.department, edit=True, v=self.departmentDict[dep])
            else:
                key_sys_lib.printMayaWarning('Department not found, Departmet population failed.')

            if asset != None:
                # Setting the width wih some value so the text is visible when edited through script
                cmds.textFieldGrp(self.asset, edit=True, cw=[2, 300])
                cmds.textFieldGrp(self.asset, edit=True, tx=asset)
            else:
                cmds.textFieldGrp(self.asset, edit=True, cw=[2, 300])
                cmds.textFieldGrp(self.asset, edit=True, tx='None')

            if version.rfind('v') > -1:
                try:
                    int(version[1:])
                except:
                    key_sys_lib.printMayaWarning('Version is not an integer value, version population failed.')
                else:
                    cmds.textField(self.version.txtFld, edit=True, tx=version[1:])
                    cmds.intScrollBar(self.version.intSldr, edit=True, v=int(version[1:]))
            else:
                key_sys_lib.printMayaWarning('Version expected string + int, version population failed.')

            if revision.rfind('r') > -1:
                try:
                    int(revision[1:])
                except:
                    key_sys_lib.printMayaWarning('Revision is not an integer value, version population failed.')
                else:
                    cmds.textField(self.revision.txtFld, edit=True, tx=revision[1:])
                    cmds.intScrollBar(self.revision.intSldr, edit=True, v=int(revision[1:]))
            else:
                key_sys_lib.printMayaWarning('Revision expected string + int, revision population failed.')

        else:
            key_sys_lib.printMayaWarning('Name mismatch, convention incorrect, auto populate failed...')

    def buildButton(self):
        '''Build the bottom button, this will usually be overloaded
        '''
        cmds.button(self.button, label=self.cmdButtonLabel)

    def win(self):
        if cmds.window(self.intWinName, exists=True):
            cmds.deleteUI(self.intWinName, window=True)

        cmds.window(self.intWinName, menuBar=True, title=self.visWinName, width=400, height=600)
        self.buildMenuBar()
        cmds.paneLayout(configuration="horizontal2", h=100, ps=[1, 100, 25])
        self.buildNameContents()
        self.buildButton()
        self.parseSceneNameAndPopulate()
        self.buildName()
        cmds.showWindow(self.intWinName)

#TestWin = NameDialog_v01('forTesting','TEST WINDOW','T E S T')
# TestWin.win()

#SaveTestWin = DirDialog_v01('forTesting','TEST WINDOW','T E S T',cmds.workspace(query=True, active=True))
# SaveTestWin.win()
