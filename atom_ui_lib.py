import os
import platform
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
# import urllib.request
import webrImport as web

ver = platform.python_version()
# print( ver)
if '2.' in ver:
    import urllib2
else:
    import urllib.request

# import urllib2
#
# web
ac = web.mod( 'atom_controlShapes_lib' )
# misc = web.mod('atom_miscellaneous_lib')


def setPreset( *args ):
    idx = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', query = True, sl = True )
    flipCheck = 'atom_qls_flip_checkBoxGrp'
    pvFlip = 'atom_qls_pvFlip_checkBoxGrp'
    ldf = 'atom_qls_ldf_floatField'
    pldf = 'atom_paw_qls_ldf_floatField'
    suffix = 'atom_suffix_optionMenu'
    # back left leg
    if idx == 1:
        cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v1 = 0, v2 = 5, v3 = 5 )
        cmds.optionMenu( suffix, edit = True, sl = 1 )
        cmds.checkBoxGrp( flipCheck, edit = True, va3 = [False, False, False] )
        cmds.checkBoxGrp( pvFlip, edit = True, va3 = [False, False, False] )
        cmds.floatField( ldf, edit = True, v = 10.0 )
        cmds.floatField( pldf, edit = True, v = 3.25 )

    # back right leg
    elif idx == 2:
        cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v1 = 0, v2 = -5, v3 = -5 )
        cmds.optionMenu( suffix, edit = True, sl = 2 )
        cmds.checkBoxGrp( flipCheck, edit = True, va3 = [False, True, True] )
        cmds.checkBoxGrp( pvFlip, edit = True, va3 = [False, False, False] )
        cmds.floatField( ldf, edit = True, v = -10.0 )
        cmds.floatField( pldf, edit = True, v = -3.25 )

    # front left leg
    elif idx == 3:
        cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v1 = 0, v2 = 5, v3 = 5 )

        cmds.optionMenu( suffix, edit = True, sl = 1 )
        cmds.checkBoxGrp( flipCheck, edit = True, va3 = [False, False, False] )
        cmds.checkBoxGrp( pvFlip, edit = True, va3 = [True, False, False] )
        cmds.floatField( ldf, edit = True, v = -10.0 )
        cmds.floatField( pldf, edit = True, v = 3.25 )

    # front right leg
    elif idx == 4:
        cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', edit = True, v1 = 0, v2 = -5, v3 = -5 )
        cmds.optionMenu( suffix, edit = True, sl = 2 )
        cmds.checkBoxGrp( flipCheck, edit = True, va3 = [False, True, True] )
        cmds.checkBoxGrp( pvFlip, edit = True, va3 = [True, False, False] )
        cmds.floatField( ldf, edit = True, v = 10.0 )
        cmds.floatField( pldf, edit = True, v = -3.25 )


def validateFieldTextInput( control ):
    '''
    Name        :validateFieldTextInput
    Arguements  :<control> : textFieldGrp
    Description :builds a name based on the selected items in the Daily Maker windows optionMenuGrp's
    '''
    returnStr = cmds.textField( control, query = True, tx = True )
    exp = ' !@#$%^&*()+-={}|[]\\:\"\';<>?,./'
    if len( returnStr ) > 0:
        for element in returnStr:
            for itm in exp:
                if element == itm:
                    cmds.textField( control, edit = True, tx = 'None' )
                    returnStr = 'None'
                    break
    else:
        cmds.textField( control, edit = True, tx = 'None' )


def refreshWindow( control ):
    '''
    # Name        :refreshWindow
    # Arguements  :<control> : window
    # Description :Change the size of the window by one pixel, then back to its original size.
    #             This forces a refresh on the windows internal controls
    '''
    currentSize = cmds.window( control, query = True, width = True )
    cmds.window( control, edit = True, width = currentSize + 1 )
    cmds.window( control, edit = True, width = currentSize )


def addControlCurveButton( path ):
    '''
    Name        :addControlCurveButton
    Arguements  :<path>: str
    Description :Builds a button that called atom_ui_lib.imortCurveShape to shape pre-defined curves
    Notes       :Used in the Control Curve Shape Toolbox section of the Atom win
    '''
    # print path
    if os.path.isdir( path ):
        files = os.listdir( path )
        if files:
            # print files
            files.sort()
            for file in files:
                # print 'here'
                if os.path.isfile( os.path.join( path, file ) ):
                    txtSplit = file.split( '.' )
                    if txtSplit[1] == 'txt':
                        # cmds.button(label=txtSplit[0], c='import atom_ui_lib\natom_ui_lib.importCurveShape("' + txtSplit[0] + '","' + path + '")')
                        cmds.button( label = txtSplit[0], c = 'import webrImport as web\naui = web.mod("atom_ui_lib")\naui.importCurveShape("' + txtSplit[0] + '","' + path + '")', p = 'atom_ccst_main_columnLayout' )
        else:
            print( 'no shapes found in path:  ' + path )


def exportCurveShape( *args ):
    '''
    Name        :exportCurveShape
    Arguements  :N/A
    Description :Exports the local transforms of the cvs on the selected curve.
    Notes       :This is designed to only work with the Atom win
    '''
    # get sel
    sel = cmds.ls( selection = True )
    if len( sel ) == 1:
        # assemble the variables to build the path name later on
        uiPath = ''
        uiName = cmds.textField( 'atom_csst_exportName_textField', query = True, tx = True )
        if uiName != 'None':
            path = os.path.join( ac.shapeDir(), uiName ) + '.txt'
            # if the file exists, stop here
            # if os.path.isfile(path) == False:
            # extract the curves shape node
            shapeNode = cmds.listRelatives( sel[0], shapes = True )[0]
            if cmds.nodeType( shapeNode ) == 'nurbsCurve':
                cvInfo = cmds.getAttr( shapeNode + '.cv[*]' )
                outFile = open( path, 'w' )
                for i in range( 0, len( cvInfo ), 1 ):
                    info = cmds.xform( shapeNode + '.cv[' + str( i ) + ']', query = True, os = True, t = True )
                    outFile.write( '%s %s %s\n' % ( info[0], info[1], info[2] ) )
                outFile.close()
                # add the butto
                # cmds.button(label=uiName, c='import atom_ui_lib\natom_ui_lib.importCurveShape("' + uiName + '","' + uiPath + '")', p='atom_ccst_main_columnLayout')
                cmds.button( label = uiName, c = 'import webrImport as web\naui = web.mod("atom_ui_lib")\naui.importCurveShape("' + uiName + '","' + uiPath + '")', p = 'atom_ccst_main_columnLayout' )
                refreshWindow( 'atom_win' )
    else:
        print( 'Select one curve to export' )


def importCurveShape( name = '', path = '', codeScale = False, overRide = False ):
    '''
    Name        :importCurveShape
    Arguements  :<name>: str
    path        :<path>: str
    Description :Imports a curve shape based on the path and name info
    Notes       :Function expects a .txt file
    '''
    colors = {'darkRed': 4, 'blue': 6, 'brown': 10, 'red': 13,
              'yellow': 17, 'lightBlue': 18, 'pink': 20, 'lightYellow': 22,
              'green': 23, 'lightBrown': 24, 'purple': 30, 'burgundy': 31}
    selection = cmds.ls( selection = True, tr = True )
    # print path, name
    # path = os.path.join(path, name + '.txt')
    # change the shape of multiple selected curves
    if selection:
        for sel in selection:
            # get the shape node
            shapeNode = cmds.listRelatives( sel, shapes = True )[0]
            # cvInfo is populated then interated through later
            cvInfo = []
            curveScale = None
            if not codeScale:
                curveScale = cmds.floatField( 'atom_csst_curveScale_floatField', query = True, value = True )
            else:
                curveScale = codeScale

            if cmds.nodeType( shapeNode ) == 'nurbsCurve':
                # print path, 'shape__________'
                inFile = importCurveShapeSource( name )
                if inFile:
                    cvInfo = shapeScale( shape = inFile, scale = curveScale )
                    # Shape the curve
                    if overRide:
                        cmds.setAttr( sel + '.overrideEnabled', 1 )
                        cmds.setAttr( sel + '.overrideColor', overRide )
                    if len( cvInfo ) == len( cmds.getAttr( shapeNode + '.cv[*]' ) ):
                        for i in range( 0, len( cvInfo ), 1 ):
                            cmds.xform( shapeNode + '.cv[' + str( i ) + ']', os = True, t = cvInfo[i] )
                    else:
                        # Curves with different CV counts are not compatible
                        OpenMaya.MGlobal.displayError( 'CV count[' + str( len( cmds.getAttr( shapeNode + '.cv[*]' ) ) ) + '] from selected does not match import CV count[' + str( len( cvInfo ) ) + ']' )
                else:
                    print( 'no shape found, tried: local, web' )
    else:
        OpenMaya.MGlobal.displayError( 'Select a NURBS curve if you truly want to proceed...' )


def importCurveShapeSource( shape = '' ):

    # try default location
    inFile = shapeLocal( shape = shape )
    if inFile:
        return inFile
    else:
        return shapeWeb( shape = shape )


def shapeLocal( shape = '' ):
    ac = web.mod( 'atom_controlShapes_lib' )
    path = ac.shapeDir()
    # print path
    if os.path.isdir( path ):
        shapePath = os.path.join( path, shape + '.txt' )
        if os.path.isfile( shapePath ):
            inFile = open( shapePath, 'r' )
            cvInfo = []
            for line in inFile.readlines():
                cvLine = line.strip( '\n' )
                cvLine = cvLine.split( ' ' )
                tmp = float( cvLine[0] ), float( cvLine[1] ), float( cvLine[2] )
                cvInfo.append( tmp )
            inFile.close()
            return cvInfo
        else:
            print( 'shape:  ' + shape + '  is missing, default shape will be used' )
    else:
        pass
        # print 'not a directory'


def shapeWeb( shape = '' ):
    webPath = 'https://raw.githubusercontent.com/boochos/controlShapes/master/'
    urlPath = webPath + shape + '.txt'
    try:
        req = urllib.request( urlPath )
        if req:
            response = urllib.request.urlopen( req )
            inFile = response.read()
            cvInfo = []
            lines = inFile.split( '\n' )
            for line in lines:
                cvLine = line.split( ' ' )
                if cvLine != ['']:
                    tmp = float( cvLine[0] ), float( cvLine[1] ), float( cvLine[2] )
                    cvInfo.append( tmp )
            return cvInfo
        else:
            return None
    except:
        print( 'shape:  ' + shape + '  is missing or internet problem' )


def shapeScale( shape = [], scale = 1.0 ):
    shapeScaled = []
    for point in shape:
        shapeScaled.append( [point[0] * scale, point[1] * scale, point[2] * scale] )
    return shapeScaled


def getRadioSelectionAsList( control ):
    '''
    Name        :getRadioSelectionAsList
    Arguements  :<control>: radioButtonGrp
    Description :Queries the radioButtonGrp for which buttons are on returns a 3 element array
    #            :0 is not selected, 1 is selected
    '''
    returnList = []
    sel = cmds.radioButtonGrp( control, query = True, sl = True )
    nrb = cmds.radioButtonGrp( control, query = True, nrb = True )
    for i in range( 0, nrb, 1 ):
        if i + 1 == sel:
            returnList.append( 1 )
        else:
            returnList.append( 0 )

    return returnList


def createListForTransform( control, value ):

    valList = [value, value, value]
    axisList = getRadioSelectionAsList( control )

    for i in range( 0, len( valList ), 1 ):
        valList[i] = valList[i] * axisList[i]
    return valList


def getCheckBoxSelectionAsList( control ):
    '''
    Name        :getCheckBoxSelectionAsList
    Arguements  :<control>: checkBoxGro
    Description :Queries the checkBoxGrp for which buttons are on returns a 3 element array
    #            :0 is not selected, 1 is selected
    Notes       :For some reason maya doesn't want to return this, all though it seems to be
    #             available in the docs
    '''
    checked = []
    checked.append( cmds.checkBoxGrp( control, query = True, v1 = True ) )
    checked.append( cmds.checkBoxGrp( control, query = True, v2 = True ) )
    checked.append( cmds.checkBoxGrp( control, query = True, v3 = True ) )

    return checked


def convertAxisNum( num ):
    '''
    Name        :convertAxisNum
    Arguements  :<num>: int
    Description :Convert, 1,2,3 to X Y or Z
    '''
    if num == 1:
        return 'X'
    elif num == 2:
        return 'Y'
    elif num == 3:
        return 'Z'
    else:
        return None
