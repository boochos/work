from __future__ import with_statement
import os
import sys
import key_sys_lib
import fnmatch
import maya.cmds as cmds
import maya.mel as mm
import pymel.core as pm


class KeyBrowserCore(object):

    '''
    Add a type var(import/export), starting path var, control name
    '''

    def __init__(self, actionButtonLabel, path, prefix, windowTitle, _filter=['*.txt'], parent=None, dirStr='|-D-|'):
        self.actionButtonLabel = actionButtonLabel
        self.path = path
        self.prefix = prefix
        self.windowTitle = windowTitle
        self._filter = _filter
        self.parent = parent
        self.currentFilter = None
        self.dirStr = dirStr
        self.customPath = '/var/tmp/custom_info.txt'
        self.customInfo = []
        self.defineControlNames()
        self.loadCustomData()

    def setLastPathEnv(self):
        if os.environ.has_key('key_last_saved_path'):
            os.environ['key_last_saved_path'] = os.path.split((cmds.textField(self.pathTxtField, query=True, tx=True)))[0]

    def actionButtonCmd(self):
        '''
        It's expected that this function will be overloaded when the
        class is instanced. The command is used by the actionButton.
        '''
        pass

    def loadCustomData(self):
        '''
        Read any custom path information, if non-exists used the default
        '''
        if not os.path.exists(self.customPath):
            self.customInfo.append(['Home', os.environ['HOME']])
            #self.customInfo.append(['Desktop', os.path.join(os.environ['HOME'], 'Desktop')])
            #self.customInfo.append(['Projects', '/Volumes/VFX/Projects'])
            #self.customInfo.append(['Reindeer', '/Volumes/VFX/Projects/Santa_Pups/Assets/Development/Artist/sweber/CharactersWork/Reindeer/RIG'])
            self.customInfo.append(['--------------------------', '-'])
        else:
            _file = open(self.customPath, 'r')
            lines = _file.readlines()
            for l in lines:
                line = eval(l.strip('\n'))
                self.customInfo.append([line[0], line[1]])

    def defineControlNames(self):
        '''
        Prebuild control names to be used in the class
        '''
        # Option Menu Group = omg, Text Scroll List = tsl
        self.winName = self.prefix + '_fileBrowser'
        self.browseText = self.prefix + '_browseText'
        self.browseTsl = self.prefix + '_browse_textScrollList'
        self.actionButton = self.prefix + '_actionButton'
        self.cancelButton = self.prefix + '_cancelButton'
        self.trashButton = self.prefix + '_trashButton'
        self.customText = self.prefix + '_customText'
        self.customTsl = self.prefix + '_custom_textScrollList'
        self.filterOmg = self.prefix + '_filter_Omg'
        self.pathTxtField = self.prefix + '_textField'
        self.mainLayout = self.prefix + '_mainFormLayout'

    def buildFilterItems(self):
        for i, itm in enumerate(self._filter):
            if i == 0:
                self.currentFilter = itm
            cmds.menuItem(self.prefix + '_%02d_menuItem' % i, l=itm)

    def filterOmgCMD(self, *args):
        self._filter = cmds.optionMenuGrp(self.filterOmg, query=True, v=True)
        self.buildBrowseItems()

    def browseTslCMD(self, *args):
        tmp = cmds.textScrollList(self.browseTsl, query=True, si=True)
        if tmp != None:
            item = tmp[0]
            # print 'list contents'
            # find if the current item is a directory
            if item[:len(self.dirStr)] == self.dirStr:
                item = item[len(self.dirStr):]
                path = os.path.join(self.path, item)
                if os.path.exists(path):
                    if os.access(path, os.R_OK):
                        self.path = str(path)
                        cmds.textField(self.pathTxtField, edit=True, tx=self.path)
                        self.buildBrowseItems()

            elif item == '..':
                path = os.path.split(self.path)[0]
                # go up a directory
                if os.path.exists(path):
                    if os.access(path, os.R_OK):
                        self.path = path
                        cmds.textField(self.pathTxtField, edit=True, tx=path)
                        self.buildBrowseItems()

            else:
                # this is a file
                path = os.path.join(self.path, item)
                if os.path.isfile(path):
                    cmds.textField(self.pathTxtField, edit=True, tx=path)

    def writeCustomData(self):
        count = cmds.textScrollList(self.customTsl, query=True, ni=True)
        _file = open(self.customPath, 'w')
        for i in range(count):
            if i + 1 != count:
                _file.write('["%s","%s"]\n' % (self.customInfo[i][0], self.customInfo[i][1]))
            else:
                _file.write('["%s","%s"]' % (self.customInfo[i][0], self.customInfo[i][1]))

        _file.close()

    def customTslCMD(self):
        tsl = cmds.textScrollList
        tmp = tsl(self.customTsl, query=True, sii=True)
        if tmp != None:
            idx = tmp[0]
            item = self.customInfo[idx - 1][0]
            path = self.customInfo[idx - 1][1]
            if path != '-':
                self.path = path
                cmds.textField(self.pathTxtField, edit=True, tx=path)
                self.buildBrowseItems()

    def buildCustomItems(self):
        for i in self.customInfo:
            cmds.textScrollList(self.customTsl, edit=True, append=i[0])

    def buildBrowseItems(self):
        # Make sure the path exists and access is permitted
        if os.path.isdir(self.path) and os.access(self.path, os.R_OK):
            # Clear the textScrollList
            cmds.textScrollList(self.browseTsl, edit=True, ra=True)
            # Append the '..'(move up a director) as the first item
            cmds.textScrollList(self.browseTsl, edit=True, append='..')
            # Populate the directories and non-directories for organization
            dirs = []
            nonDir = []
            # list the files in the path
            files = os.listdir(str(self.path))
            if len(files) > 1:
                # Sort the directory list based on the names in lowercase
                # This will error if 'u' objects are fed into a list
                files.sort(key=str.lower)
                # pick out the directories
                for i in files:
                    if i[0] != '.':
                        if os.path.isdir(os.path.join(self.path, i)):
                            dirs.append(i)
                        else:
                            nonDir.append(i)

                # Add the directories first
                for i in dirs:
                    cmds.textScrollList(self.browseTsl, edit=True, append=self.dirStr + i)

                # Add the files next
                # print nonDir, '____________________'
                for i in nonDir:
                    # show the files based on the current filter
                    if self._filter in i or '.' not in i:
                        cmds.textScrollList(self.browseTsl, edit=True, append=i)
                    else:
                        print 'filtered   ', i

    def trashDragCallBack(self, control, x, y, modifiers):
        pass

    def trashDropCallback(self, drag, drop, messages, x, y, dragType):
        if drag[drag.rfind('|') + 1:] == self.customTsl:
            tmp = cmds.textScrollList(self.customTsl, query=True, sii=True)
            if tmp != None:
                idx = tmp[0]
                if idx > 4:
                    cmds.textScrollList(self.customTsl, edit=True, rii=idx)
                    del self.customInfo[idx - 1]
                    self.writeCustomData()

    def browswDragCallBack(self, control, x, y, modifiers):
        pass

    def browseDropCallBack(self, drag, drop, messages, x, y, dragType):
        tmp = cmds.textScrollList(drag, query=True, si=True)
        if tmp != None:
            item = tmp[0]
            if item[:len(self.dirStr)] == self.dirStr:
                strip = item[len(self.dirStr):]
                path = str(os.path.join(self.path, strip))
                if os.path.isdir(path):
                    self.customInfo.append([strip, path])
                    cmds.textScrollList(self.customTsl, edit=True, append=strip)
                    self.writeCustomData()

    def deleteWin(self, *args):
        if pm.window(self.winName, exists=True):
            pm.deleteUI(self.winName)

    def createControls(self):
        pm.textField(self.pathTxtField, tx=self.path)
        pm.optionMenuGrp(self.filterOmg, label='Filter:', cw2=[40, 75], height=20, cc=self.filterOmgCMD)
        self.buildFilterItems()

        pm.button(self.actionButton, l=self.actionButtonLabel, w=100, c=self.actionButtonCmd)
        pm.button(self.cancelButton, l='Cancel', w=100, c=self.deleteWin)

        pm.text(self.customText, l='Custom Paths', fn='boldLabelFont', h=15)
        pm.textScrollList(self.customTsl, sc=self.customTslCMD, fn='boldLabelFont', w=240,
                          dgc=self.trashDragCallBack, dpc=self.browseDropCallBack)
        pm.text(self.browseText, l='Browse Directory/Select File', fn='boldLabelFont', h=15, w=200)
        pm.textScrollList(self.browseTsl, dcc=self.browseTslCMD, dgc=self.browswDragCallBack)

        pm.symbolButton(self.trashButton, image='smallTrash.xpm', dpc=self.trashDropCallback,
                        annotation='Drag from custom paths to trash to remove path for UI.')
        # when text is added into a textField the text display is cut short
        # setting the focus fixes this.
        pm.setFocus(self.pathTxtField)
        pm.setFocus(self.browseTsl)

    def layoutForm(self):
        pm.formLayout(self.mainLayout, edit=True,
                      attachForm=[(self.pathTxtField, 'left', 5), (self.pathTxtField, 'top', 5), (self.pathTxtField, 'right', 5),
                                  (self.browseTsl, 'left', 250), (self.browseTsl, 'right', 5), (self.browseTsl, 'bottom', 65),
                                  (self.customText, 'left', 5),
                                  (self.customTsl, 'left', 5), (self.customTsl, 'bottom', 65),
                                  (self.filterOmg, 'left', 5),
                                  (self.cancelButton, 'right', 5)],

                      attachControl=[(self.browseText, 'top', 5, self.pathTxtField), (self.browseText, 'left', 5, self.customTsl),
                                     (self.browseTsl, 'top', 5, self.browseText),
                                     (self.customText, 'top', 5, self.pathTxtField),
                                     (self.trashButton, 'top', 5, self.pathTxtField),
                                     (self.customTsl, 'top', 5, self.customText),
                                     (self.filterOmg, 'top', 5, self.browseTsl),
                                     (self.actionButton, 'top', 5, self.filterOmg), (self.actionButton, 'right', 5, self.cancelButton),
                                     (self.cancelButton, 'top', 5, self.filterOmg)],

                      attachOppositeControl=[(self.trashButton, 'right', 2, self.customTsl), ]
                      )

    def win(self):
        self.deleteWin()
        win = pm.window(self.winName, t=self.windowTitle, menuBar=True)
        with win:
            with pm.formLayout(self.mainLayout, numberOfDivisions=100):
                # Create the controls of the layout
                self.createControls()
                self._filter = self._filter[0]
                # Layout the controls
                self.layoutForm()
                self.buildBrowseItems()
                self.buildCustomItems()

# example call:
#skinImport = KeyBrowserCore('import', '/home/spatapoff/Desktop', 'wtt', 'Import Weights', _filter=['.txt','.mb','.ma','*.*'])
# skinImport.win()


#-------------
# Name        :DirDialog
# Arguments  :<intWinName>   : internal window name
#            <visWinName>   : name displayed to the user
#            <startPath>    : the starting path to start browsing
#            <buttonLabel>  : name if the window that's calling the class
#            <buttonCommand>: the path so set in the parents txtField
# Description :Class that builds a Directory Browser for selecting file paths
#-------------
class DirDialog:

    def __init__(self, intWinName, visWinName, startPath, buttonLabel, buttonCommand):
        # set the class properties with the given arguments
        self.internalWindowName = intWinName
        self.visibleWindowName = visWinName
        self.startingPath = startPath
        self.buttonCommand = buttonCommand
        self.buttonLabel = buttonLabel

    #-------------
    # Name        :popWin
    # Arguments   :<currentDir>: Path of the directory to populate the text scroll list
    # Description :The File Browser Window will be poplulated with the contents
    #             of the given path.
    #-------------
    def popWin(self, currentDir):
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, ra=True)  # clear the list
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append='..')  # append with '..'
        files = os.listdir(currentDir)
        files.sort()
        for file in files:
            fullPath = os.path.join(currentDir, file)  # make the full path
            if os.path.isdir(fullPath) == True:  # filter that will only show the directories
                if not file.startswith('.'):  # filter that will skip the folders that start with '.' at the start of the name
                    cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append=file)

    #-------------
    # Name        :DCCos.pathos.pathos.path
    # Arguments   :none
    # Description :The command to be executed when the user double clicks in the Text Scroll List
    #             that displays the current directory
    # Notes       :DCC short for Double Click Command
    #-------------
    def dcc(self, *args):
        currentPath = cmds.textField(self.internalWindowName + '_txtFld', query=True, tx=True)
        # get the item just clicked on
        selItem = cmds.textScrollList(self.internalWindowName + '_txtScrlLst', query=True, si=True)
        # if the selection is '..' then go up a directory
        if selItem[0] == '..':
            walkUp = os.path.split(currentPath)
            cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=walkUp[0])
            self.popWin(walkUp[0])
        # else go down a directory
        else:
            fullPath = os.path.join(currentPath, selItem[0])
            cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=fullPath)
            self.popWin(fullPath)

    #-------------
    # Name        :dirWin
    # Arguments   :None
    # Description :Build the Directory Browser interface
    #-------------
    def dirWin(self):
        if cmds.window(self.internalWindowName, exists=True):
            cmds.deleteUI(self.internalWindowName, window=True)

        cmds.window(self.internalWindowName, title=self.visibleWindowName, width=350, height=260)
        cmds.columnLayout('masterCol', adjustableColumn=True, cat=('both', 5))
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', numberOfRows=12, allowMultiSelection=False,
                            showIndexedItem=4, dcc=self.dcc)
        cmds.textField(self.internalWindowName + '_txtFld', tx=self.startingPath, editable=False)
        cmds.button(self.internalWindowName + '_but', label=self.buttonLabel, c=self.buttonCommand)
        cmds.showWindow(self.internalWindowName)
        self.popWin(self.startingPath)

#-------------
# Name        :FileDialog
# Arguments  :<intWinName>    : internal window name
#            <visWinName>    : name displayed to the user
#            <fileFilter>    : file type to filter out
#            <startPath>     : starting path of the browser
#            <fieldState>    : Bool, state of the control
#            <operation>     : type of operation 0-3
#            <buttonCommand> : button press command
# Description :Class that builds a File Browser
#-------------


class FileDialog:

    def __init__(self, intWinName, visWinName, fileFilter, startPath, fieldState, operation, buttonCommand):

        # create a dictionary, this is similar to case or switch
        label = {
            0: 'S A V E',
            1: 'L O A D',
            2: 'I M P O R T',
            3: 'E X P O R T'
        }
        self.buttonLabel = label[operation]

        # set the class properties with the given arguments
        self.internalWindowName = intWinName
        self.visibleWindowName = visWinName
        self.startingPath = startPath
        self.buttonCommand = buttonCommand
        self.fileFilter = fileFilter
        self.fieldState = fieldState
        print 'fileD'

    #-------------
    # Name        :popWin
    # Arguments   :<currentDir>: Path of the directory to populate the text scroll list
    # Description :The File Browser Window will be poplulated with the contents
    #             of the given path.
    #-------------
    def popWin(self, currentDir, fFilter):
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, ra=True)  # clear the list
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append='..')  # append with '..'
        files = os.listdir(currentDir)
        files.sort()
        print files
        for file in files:
            print '____here'
            fullPath = os.path.join(currentDir, file)  # make the full path
            if os.path.isfile(fullPath) == True:
                if fFilter == '*.*':
                    cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append=file)
                elif file.find(fFilter) != -1:
                    cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append=file)
            elif os.path.isdir(fullPath) == True:  # filter that will only show the directories
                if not file.startswith('.'):  # filter that will skip the folders that start with '.' at the start of the name
                    cmds.textScrollList(self.internalWindowName + '_txtScrlLst', edit=True, append=file)

    #-------------
    # Name        :dcc
    # Arguments   :none
    # Description :The command to be executed when the user double clicks in the Text Scroll List
    #             that displays the current directory and file. This is more complicated than the
    #             dcc that's used in Dir Browser as there as to be more checkes for selection types.
    # Notes       :dcc is short for Double Click Command
    #-------------
    def dcc(self, *args):
        currentPath = cmds.textField(self.internalWindowName + '_txtFld', query=True, tx=True)
        # get the item just clicked on
        selItem = cmds.textScrollList(self.internalWindowName + '_txtScrlLst', query=True, si=True)
        # if the selection is '..' then go up a directory
        if selItem[0] == '..':
            walkUp = os.path.split(currentPath)
            # check if the tail of the current path is a directory
            if os.path.isdir(walkUp[1]):
                cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=walkUp[0])
                self.popWin(walkUp[0], self.fileFilter)
            # if it's a file another path.split is done to get the directory
            else:
                walkUp = os.path.split(walkUp[0])
                cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=walkUp[0])
                self.popWin(walkUp[0], self.fileFilter)
        else:
            # else go down a directory
            fullPath = os.path.join(currentPath, selItem[0])
            if os.path.isdir(fullPath) == True:
                cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=fullPath)
                self.popWin(fullPath, self.fileFilter)
            else:
                if os.path.isdir(currentPath):
                    cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=fullPath)
                else:
                    # strip tail from the path and add the current selected item
                    fullPath = os.path.join(os.path.split(currentPath)[0], selItem[0])
                    cmds.textField(self.internalWindowName + '_txtFld', edit=True, tx=fullPath)

    #-------------
    # Name        :fileWin
    # Arguments   :None
    # Description :Build the Directory Browser interface
    #-------------
    def fileWin(self):
        if cmds.window(self.internalWindowName, exists=True):
            cmds.deleteUI(self.internalWindowName, window=True)

        cmds.window(self.internalWindowName, title=self.visibleWindowName, width=350, height=260)
        cmds.columnLayout('masterCol', adjustableColumn=True, cat=('both', 5))
        cmds.textScrollList(self.internalWindowName + '_txtScrlLst', numberOfRows=12, allowMultiSelection=False,
                            showIndexedItem=4, dcc=self.dcc)
        cmds.textField(self.internalWindowName + '_txtFld', en=self.fieldState, tx=self.startingPath)
        cmds.button(self.internalWindowName + '_but', label=self.buttonLabel, c=self.buttonCommand)
        cmds.showWindow(self.internalWindowName)
        self.popWin(self.startingPath, self.fileFilter)


#-------------
# Name        :NameDialog
# Arguments  :<intWinName>   : internal window name
#            <visWinName>   : name displayed to the user
#            <fileNamePath> : the starting path to start browsing
#            <changeCmd>    : command to execute when a name is changed
#            <buttonLabel>  : label on the button
#            <buttonCmd>    : buttons command
#            <nameFieldText>: the path so set in the parents txtField
#            <ext>          : extension filter
# Description :Class that builds the rename interface for key tools renaming
#-------------
class NameDialog:

    def __init__(self, intWinName, visWinName, fileNamePath, changeCmd, buttonLabel, buttonCmd, nameFieldText, ext, varName):
        self.internalWindowName = intWinName
        self.visibleWindowName = visWinName
        self.fileNamePath = fileNamePath
        self.changeCmd = changeCmd
        self.cmdButtonLabel = buttonLabel
        self.buttonCommand = buttonCmd
        self.nameFieldText = nameFieldText
        self.extension = ext
        self.varName = varName

    #-------------
    # Name        :nameBuilder
    # Arguements  :none
    # Description :builds a name based on the selected items in the Daily Maker windows optionMenuGrp's
    #-------------
    def nameBuilder(self):
        getOptGrps = cmds.columnLayout(self.internalWindowName + '|masterCol', query=True, ca=True)  # list all children in the layout
        finalName = ''
        cnt = 0
        for optGrp in getOptGrps:
            # look for '_optGrp' find returns an int of where '_optGrp' starting in the string
            if optGrp.find('Artist_', 0) == 0:  # the artist field isn't part of the real name
                pass  # so it needs to be ignored
            elif optGrp.find('_optGrp', 1) > -1:  # find returns -1 if '_optGrp' isn't found
                getValue = cmds.optionMenuGrp(optGrp, query=True, value=True)
                value = getValue.partition(' ')  # break apart the string using ' ' as a value
                if value[0] != 'NULL':  # Null gets ignored
                    if cnt == 0:  # the desired name is in the first index
                        finalName = value[0]
                        cnt += 1
                    else:
                        finalName += '_' + value[0]
            # text field section
            elif optGrp.find('Asset') > -1:
                getValue = cmds.textFieldGrp(optGrp, query=True, tx=True)
                valStr = self.validateFieldTextInput(optGrp)
                if valStr != 'NULL':
                    if len(finalName) > 0:
                        finalName += '_' + valStr
                    else:
                        finalName += valStr
                        cnt += 1

        cmds.text(self.nameFieldText, edit=True, label=finalName)
        # self.saveName()
    #--END nameBuilder

    def autoPopOptMenuGrp(self):

        name = cmds.file(query=True, sceneName=True)
        if len(name) != 0:
            sceneNameList = os.path.basename(name).split('.')[0].split('_')

            if len(sceneNameList) > 6:
                sceneNameList[3] = sceneNameList[3] + '_' + sceneNameList[4]
                del sceneNameList[4]

            if len(sceneNameList) == 6:
                getOptGrps = cmds.columnLayout(self.internalWindowName + '|masterCol', query=True, ca=True)  # list all children in the layout
                finalName = ''
                cnt = 0
                for optGrp in getOptGrps:
                    # look for '_optGrp' find returns an int of where '_optGrp' starting in the string
                    if optGrp.find('Artist_', 0) == 0:  # the artist field isn't part of the real name
                        pass  # so it needs to be ignored
                    elif optGrp.find('_optGrp', 1) > -1:  # find returns -1 if '_optGrp' isn't found
                        menuItems = cmds.optionMenuGrp(optGrp, query=True, ils=True)
                        menuDict = {}
                        for i in range(0, len(menuItems), 1):
                            menuDict[cmds.menuItem(menuItems[i], query=True, label=True).split(' ')[0]] = i

                        if menuDict.has_key(sceneNameList[cnt]):
                            cmds.optionMenuGrp(optGrp, edit=True, sl=menuDict[sceneNameList[cnt]] + 1)
                        elif optGrp == 'Department_optGrp':
                            key_sys_lib.printMayaWarning('\\"' + optGrp.split('_')[0] + '\\" not auto populated, naming mismatch.')

                        cnt += 1
            else:
                key_sys_lib.printMayaWarning('Auto population failed, naming convention mismatch.')

    #-------------
    # Name        :validateFieldTextInput
    # Arguements  :<control> : textFieldGrp
    # Description :builds a name based on the selected items in the Daily Maker windows optionMenuGrp's
    #-------------
    def validateFieldTextInput(self, control):
        returnStr = cmds.textFieldGrp(control, query=True, tx=True)
        exp = ' !@#$%^&*()+-={}|[]\\:\"\';<>?,./'
        if len(returnStr) > 0:
            for element in returnStr:
                for itm in exp:
                    if element == itm:
                        cmds.textFieldGrp(control, edit=True, tx='NULL')
                        returnStr = 'NULL'
                        break
        else:
            cmds.textFieldGrp(control, edit=True, tx='NULL')
        return returnStr
    #--END validateFieldTextInput

    #-------------
    # Name        :optionMenuGrp_builder(source_path, ext)
    # Arguments   :<source path>:  path of where the files exist
    #             <ext>        :  extention the files are using (eg.".mel, .txt")
    # Description :Function that finds all the files in the provided path with the
    #             given extension and build a optionMenuGrp using the files name.
    # Notes       :Calls menuItem_builder to create the contents for the optionMenuGrp
    #-------------
    def optionMenuGrp_builder(self):
        dirFiles = os.listdir(self.fileNamePath)
        dirFiles.sort()
        for file in dirFiles:  # list all the files in the directory
            if file.endswith(self.extension):  # strip off the extension
                tmpName = file.partition(self.extension)  # break the name appart using the extension
                finalName = tmpName[0].partition('_')
                if finalName[2] == 'Asset':
                    cmds.textFieldGrp(finalName[2] + '_textField', label=finalName[2] + ' : ', cw2=(85, 245),
                                      adj = 2, ct2 = ('left', 'right'), tx = 'NULL',
                                      cc = self.changeCmd)  # build the optionMenuGrp
                else:
                    cmds.optionMenuGrp(finalName[2] + '_optGrp', label=finalName[2] + ' : ', ni=10, cw2=(85, 245),
                                       adj = 2, ct2 = ('left', 'right'),
                                       cc = self.changeCmd)  # build the optionMenuGrp
                    self.menuItem_builder(file)  # add the menuItems
    #--END optionMenuGrp_builder

    #-------------
    # Name        :menuItem_builder(source_path, fileName)
    # Arguments  :<source path>:  path of where the files exist
    #             <fileName>  :  name of the file to open, passed from optionMenuGrp_builder
    # Description :Function that populates the created optionMenuGrp with the contents from
    #             the passed fileName.
    #-------------
    def menuItem_builder(self, fileName):
        if fileName.find('Sequence') > -1:
            seqPath = os.getenv('MAYA_PROJECT_SEQ_PATH')
            if seqPath == '/Volumes/VFX/Projects/Key_Base/SEQ':
                seqPath = '/Volumes/VFX/Projects/Santa_Buddies/SEQ'
            seqFolder = sorted(os.listdir(seqPath))
            cmds.menuItem(label='NULL')
            for itm in seqFolder:
                if os.path.isdir(os.path.join(seqPath, itm)):
                    cmds.menuItem(itm)
        else:
            sourceFile = os.path.join(self.fileNamePath, fileName)  # join the filename and source_path together
            for line in open(sourceFile).readlines():  # open the file then read the lines
                if line != 'null':
                    cmds.menuItem(label=line.strip('\n'))  # strip off the '\n' character and create the menuItem
    #--END menuItem_builder

    def saveName(self):
        savePath = '/var/tmp/nameBuilder.txt'
        getOptGrps = cmds.columnLayout(self.internalWindowName + '|masterCol', query=True, ca=True)  # list all children in the layout
        exportList = [cmds.text(self.nameFieldText, query=True, label=True)]
        cnt = 0
        for optGrp in getOptGrps:
            if optGrp.find('separator') > -1:
                break
            elif optGrp.find('menuBarLayout') > -1:
                cnt -= 1
            else:
                if cnt != 5:
                    getValue = cmds.optionMenuGrp(optGrp, query=True, v=True)
                    exportList.append(getValue)
                else:
                    getValue = cmds.textFieldGrp(optGrp, query=True, tx=True)
                    exportList.append(getValue)
            cnt += 1
        readLines = []
        if os.path.exists(savePath):
            saveFile = open(savePath, 'r')
            readLines = saveFile.readlines()
            saveFile.close()

        saveFile = open(savePath, 'w')
        saveFile.write('%s\n' % (exportList))
        lineCnt = 1
        for line in readLines:
            if lineCnt < 15:
                saveFile.write(line)
                lineCnt += 1
        saveFile.close()
        self.win()
        self.popPulldowns('0')

    def popPulldowns(self, lineNum):
        openPath = '/var/tmp/nameBuilder.txt'
        openFile = open(openPath, 'r')
        readLines = openFile.readlines()
        cnt = 0
        for line in readLines:
            if cnt == int(lineNum):
                nameList = eval(line)
                del nameList[0]
                # conver the nameList to a dictionary
                nameDict = {}
                lineIdx = 0
                for i in range(0, len(nameList), 1):
                    nameDict[i] = nameList[i]

                getOptGrps = cmds.columnLayout(self.internalWindowName + '|masterCol', query=True, ca=True)

                for optGrp in getOptGrps:
                    if optGrp.find('_optGrp') > -1:
                        menuItems = cmds.optionMenuGrp(optGrp, query=True, ils=True)
                        menuDict = {}
                        for i in range(0, len(menuItems), 1):
                            menuDict[cmds.menuItem(menuItems[i], query=True, label=True)] = i

                        if menuDict.has_key(nameDict[lineIdx]):
                            cmds.optionMenuGrp(optGrp, edit=True, sl=menuDict[nameDict[lineIdx]] + 1)

                        lineIdx += 1
                    elif optGrp == 'Asset_textField':
                        cmds.textFieldGrp(optGrp, edit=True, tx=nameDict[lineIdx])
                        lineIdx += 1

            cnt += 1
        self.nameBuilder()

    def popMenu(self):
        openPath = '/var/tmp/nameBuilder.txt'
        if os.path.exists(openPath):
            openFile = open(openPath, 'r')
            names = openFile.readlines()
            cnt = 0
            for name in names:
                infoList = eval(name)
                cmds.menuItem(infoList[0] + '_' + str(cnt), label=infoList[0], c=self.varName + '.popPulldowns(' + str(cnt) + ')')
                cnt += 1

    #-------------
    # Name        :win
    # Arguments   :none
    # Description :creates the Daily Maker window
    #-------------
    def win(self):
        if cmds.window(self.internalWindowName, exists=True):
            cmds.deleteUI(self.internalWindowName, window=True)
        cmds.window(self.internalWindowName, title=self.visibleWindowName, width=340, height=300)
        cmds.columnLayout('masterCol', adjustableColumn=True, cat=('both', 5))
        cmds.menuBarLayout()
        cmds.menu(label='Auto Populate')
        self.popMenu()
        cmds.menu(label='Save')
        cmds.menuItem('Save Name', c=self.varName + '.saveName()')
        cmds.menuItem('Clear', c=self.varName + '.win()')
        cmds.columnLayout()
        cmds.setParent('..')
        cmds.setParent('..')
        self.optionMenuGrp_builder()

        cmds.separator(height=20, style='double')
        cmds.text(self.nameFieldText)
        cmds.separator(height=20, style='double')
        cmds.button('executeBtn', label=self.cmdButtonLabel, c=self.buttonCommand)
        self.autoPopOptMenuGrp()
        self.nameBuilder()
        cmds.showWindow(self.internalWindowName)
