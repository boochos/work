from __future__ import with_statement

# import cPickle
import json
import os

from maya.OpenMaya import *
from maya.OpenMayaAnim import MFnSkinCluster
from maya.OpenMayaMPx import *
import maya.cmds as cmds
import maya.mel as mm
import pymel.core as pm
import webrImport as web

#
# web
kwo = web.mod( 'key_weighting_objects' )
key_ui_lib = web.mod( 'key_ui_lib' )


def getMFnSkinCluster( skinClusterName ):
    '''
    Get an API skinCluster object 
    '''
    # get the skinCluster object
    selectionList = MSelectionList()
    selectionList.add( skinClusterName )
    mObj = MObject()
    selectionList.getDependNode( 0, mObj )
    return MFnSkinCluster( mObj )


class CopySeam:
    #------use------#
    # --Create the class
    # CopySeam =CopySeam()
    # --select the copy vertex
    # CopySeam.setVtx(1)
    # select the paste vertex
    # CopySeam.setVtx(2)
    # --find the vertex pairs on the seam
    # CopySeam.pairVtx()
    # --Copy the weights
    # CopySeam.copyPasteVtx()

    def __init__( self ):
        self.copyVtx = None
        self.pasteVtx = None
        self.pairList = []
    # Set the selected vertex mode(1) = copy, mode(2) = paste

    def setVtx( self, mode ):
        if len( cmds.ls( sl = True, fl = True ) ) > 0:
            if mode == 1:
                self.copyVtx = cmds.ls( sl = True, fl = True )

            elif mode == 2:
                self.pasteVtx = cmds.ls( sl = True, fl = True )

    # Print the current set vertex
    def printVtx( self, mode ):
        if mode == 1:
            print( self.copyVtx )

        elif mode == 2:
            print( self.pasteVtx )
    # Return the current set vertex

    def getVtx( self, mode ):
        if mode == 1:
            return self.copyVtx

        elif mode == 2:
            return self.pasteVtx

    def pairVtx( self ):
        import key_util_lib as kul
        # make sure copy and paste have been populated
        if self.copyVtx != None and self.pairVtx != None:
            # interate through pasteVtx and find the cloest vertex in copyVertex
            for i in range( 0, len( self.pasteVtx ), 1 ):
                pVtx = self.pasteVtx[i]
                dis = 100000000
                pair = None
                for j in range( 0, len( self.copyVtx ), 1 ):
                    cVtx = self.copyVtx[j]
                    getDis = kul.distance2Pts( cmds.xform( pVtx, query = True, ws = True, t = True ), cmds.xform( cVtx, query = True, ws = True, t = True ) )
                    if getDis < dis:
                        dis = getDis
                        closestCopyVtx = cVtx
                self.pairList.append( [closestCopyVtx, pVtx] )

    def copyPasteVtx( self ):
        for pair in self.pairList:
            cmds.select( pair[0] )
            copyWeightFromSelVtx()
            cmds.select( pair[1] )
            pasteWeightsFromSelectedVtx( False )
        print( '===== copyPasteVtx process complete =====' )


class WeightBroswer( key_ui_lib.FileDialog ):

    '''Class that builds a file browser and exports the weights from the selected mesh
    '''

    def __init__( self, intWinName, visWinName, fileFilter, startPath, fieldState, buttonLabel, mode ):
        # set the class properties with the given arguments
        # mode
        # 1 = import
        # 2 = export
        self.buttonLabel = buttonLabel
        self.internalWindowName = intWinName
        self.visibleWindowName = visWinName
        self.startingPath = startPath
        self.fileFilter = fileFilter
        self.fieldState = fieldState
        self.mode = mode
        self.command = ''

        if self.mode == 1:
            self.command = self.exportWeights
        elif self.mode == 2:
            self.command = self.importWeights
        else:
            self.command = self.batchNurbsWeightsCMD

    def batchNurbsWeightsCMD( self, *args ):
        path = cmds.textField( self.internalWindowName + '_txtFld', query = True, tx = True )
        cmds.deleteUI( self.internalWindowName, window = True )

        sel = cmds.ls( sl = True )
        if len( sel ) == 1:
            if self.mode == 3:
                batchExportNurbsWeights( path, sel[0] )
            else:
                batchImportNurbsWeights( path )

        else:
            OpenMaya.MGlobal.displayWarning( 'Select ONE object for preform operation on.' )

    def exportWeights( self, *args ):
        '''Command to export weights from the selected mesh\n
        '''
        path = cmds.textField( self.internalWindowName + '_txtFld', query = True, tx = True )
        cmds.deleteUI( self.internalWindowName, window = True )
        # 1 = polygons, 2 = NURBS
        surfaceType = cmds.radioButtonGrp( 'key_surfaceType_rbg', query = True, sl = True )
        sel = cmds.ls( sl = True )[0]
        if len( sel ) > 0:
            if surfaceType == 1:
                exportMeshWeights( path, sel, True )
            else:
                exportNurbsSurfaceWeights( path, sel )
        else:
            print( 'Selection size is wrong, select one mesh.' )

    def importWeights( self, *args ):
        '''Command to import weights from the selected mesh\n
        '''
        path = cmds.textField( self.internalWindowName + '_txtFld', query = True, tx = True )
        cmds.deleteUI( self.internalWindowName, window = True )
        # 1 = polygons, 2 = NURBS
        surfaceType = cmds.radioButtonGrp( 'key_surfaceType_rbg', query = True, sl = True )
        sel = cmds.ls( sl = True )[0]
        if len( sel ) > 0:
            if surfaceType == 1:
                importMeshWeights( path, sel, True )
            else:
                importNurbSurfaceWeights2( path, sel )
        else:
            print( 'Selection size is wrong, select one mesh.' )

    def fileWin( self ):
        '''File browser window\n
        '''
        if cmds.window( self.internalWindowName, exists = True ):
            cmds.deleteUI( self.internalWindowName, window = True )

        cmds.window( self.internalWindowName, title = self.visibleWindowName, width = 350, height = 260 )
        form = cmds.formLayout( 'masterWgt_Form', numberOfDivisions = 100 )
        tsl = cmds.textScrollList( self.internalWindowName + '_txtScrlLst', numberOfRows = 12, allowMultiSelection = False,
                                  showIndexedItem = 4, dcc = self.dcc )

        tfld = cmds.textField( self.internalWindowName + '_txtFld', en = self.fieldState, tx = self.startingPath )
        btn = cmds.button( self.internalWindowName + '_but', label = self.buttonLabel, c = self.command )

        cmds.formLayout( form, edit = True,
                        attachForm = [( tsl, 'top', 5 ), ( tsl, 'left', 5 ), ( tsl, 'right', 5 ), ( tsl, 'bottom', 100 ),
                                    ( tfld, 'left', 5 ), ( tfld, 'right', 5 ),
                                    ( btn, 'left', 5 ), ( btn, 'right', 5 ), ( btn, 'bottom', 5 )],

                        attachControl = [( tfld, 'top', 5, tsl ), ( btn, 'top', 5, tfld )]
                        )
        cmds.showWindow( self.internalWindowName )
        self.popWin( self.startingPath, self.fileFilter )


def getSkinCluster( obj = '' ):
    '''
    Get a skinCluster node
    '''
    #
    skinNode = None
    #
    if obj:
        pm_node = obj
    else:
        pm_node = cmds.ls( sl = 1 )
        if len( pm_node ) == 1:
            pm_node = pm_node[0]
        else:
            print( 'expected one object in selection', pm_node )
            return skinNode
    #
    if cmds.nodeType( pm_node ) == 'transform':
        print( pm_node )
        pm_shape = cmds.listRelatives( pm_node, shapes = True )
        print( pm_shape )
        for s in pm_shape:
            cons = cmds.listHistory( s, pdo = True )
            if cons:
                for con in cons:
                    if cmds.nodeType( con ) == 'skinCluster':
                        print( con )
                        skinNode = con
    return skinNode


def storeSkinInfo( skinClusterName, skinInfo, update = False, increment = .2 ):
    '''
    Function that scans a mesh and extracts weighting information
    Returns a list of SkinPoints, one SkinPoint for each vertex
    '''
    skinClusterNode = getMFnSkinCluster( skinClusterName )

    # get the influences
    infs = MDagPathArray()
    # get the number of influences
    numInfs = skinClusterNode.influenceObjects( infs )

    # get dagpath for the skinCluster
    skinPath = MDagPath()
    index = 0
    skinClusterNode.indexForOutputConnection( index )
    skinClusterNode.getPathAtIndex( index, skinPath )

    # store the vertex information for return
    info = []
    # skinInfo is the first item in the list that gets saved
    info.append( skinInfo )
    # list all the joint names and influence objects
    infInfo = []

    for i in range( 0, numInfs, 1 ):
        infInfo.append( str( infs[i].partialPathName() ) )

    gIter = MItGeometry( skinPath )
    _util = MScriptUtil()
    infCount = _util.asUintPtr()
    timer = cmds.timerX()

    print( '==== Creating %s SkinPoints ====' % gIter.count() )
    if update == True:
        gMainProgressBar = mm.eval( '$tmp = $gMainProgressBar' )
        cmds.progressBar( gMainProgressBar, edit = True, w = 200,
                         beginProgress = True, status = '0',
                         maxValue = gIter.count() )

        # increase the progressBar frequence depends on increment factor
        incrementSize = int( gIter.count() * increment )
        incrementTotal = incrementSize

    # iterate through all the vertecies and extract info
    while not gIter.isDone():
        # Putting any prints in here will slow things down a lot
        # prints gtfo
        index = gIter.index()
        if update == True and gIter.index() == incrementTotal:
            cmds.progressBar( gMainProgressBar, edit = True, status = index, step = incrementSize )
            incrementTotal += incrementSize

        # Get the worldspace position of the point, may be useful in the future
        world_tran = gIter.position( MSpace.kWorld )

        comp = MObject( gIter.component() )
        wts = MDoubleArray()

        # getWeights requires an unsigned int, which doesn't exists in python asUintPtr takes care of that
        skinClusterNode.getWeights( skinPath, comp, wts, infCount )

        # data needs to be converted into pickle friendly formats
        inf = []
        wgt = []

        # Get the infuences and weighting for the point
        # infInfo  = influence list
        # i        = individual influence name
        # #wts[idx] = weight
        for idx, i in enumerate( infInfo ):
            inf.append( str( i ) ), wgt.append( float( wts[idx] ) )

        # next loop reorders weight list to match reordered influences
        # reordering is necessary when the index[0] influence is not a joint.
        # this occurs when the binding joint has been removed from the list and the next influence in list is a geometry.
        # the loop matches the method in which the reorder() function reorders its list, in this module.
        reorder = []
        tmp = []
        for idx, i in enumerate( infInfo ):
            if cmds.nodeType( i ) == 'joint':
                reorder.append( wgt[idx] )
            else:
                tmp.append( wgt[idx] )
        if tmp:
            for item in tmp:
                reorder.append( item )
        wgt = reorder

        # Make the skinPoint
        skinPoint = kwo.SkinPoint( index, inf, wgt, [world_tran.x, world_tran.y, world_tran.z] )
        # print index, inf, wgt
        # Append it to the info
        info.append( skinPoint )
        # Interate to the next point
        gIter.next()

    if update:
        cmds.progressBar( gMainProgressBar, edit = True, endProgress = True )
    print( '==== SkinPoints created in: %s seconds ====' % cmds.timerX( st = timer ) )
    return info


def reorderInf( inf ):
    '''
    reorders influences so that joint type is first index
    '''
    reorder = []
    tmp = []
    for item in inf:
        if cmds.nodeType( item ) == 'joint':
            reorder.append( item )
        else:
            tmp.append( item )
    if tmp:
        for item in tmp:
            reorder.append( item )
    # print reorder
    inf = reorder
    return inf


def getSkinNodeInformation( skinNode ):
    '''
    Create the skinInformation object
    '''
    if cmds.objExists( skinNode ):
        sknF = cmds.skinCluster
        gAtr = cmds.getAttr

        dropoffRate = []
        polygonSmoothness = []
        nurbsSamples = []
        infList = []
        objTypes = []

        useComponents = cmds.getAttr( '%s.useComponents' % skinNode )
        influences = sknF( skinNode, query = True, influence = True )
        influences = reorderInf( influences )

        # These calls need an influence
        for idx, inf in enumerate( influences ):
            infList.append( str( inf ) )
            dropoffRate.append( int( sknF( skinNode, query = True, dropoffRate = True, inf = inf ) ) )
            polygonSmoothness.append( int( sknF( skinNode, query = True, polySmoothness = True, inf = inf ) ) )
            nurbsSamples.append( int( sknF( skinNode, query = True, nurbsSamples = True, inf = inf ) ) )
            objTypes.append( cmds.nodeType( inf ) )
        skinNodeInf = kwo.SkinNodeInformation( infList, objTypes, dropoffRate, polygonSmoothness, nurbsSamples, useComponents )
        return skinNodeInf


def importWeights02( obj, path ):
    '''
    Load the pickled skinfile and setSkinInfo
    '''
    start = cmds.timerX()
    # _import = open(path, 'rb')
    _import = open( path, 'r' )
    importInfo = []
    print( '---- Loading file ----\n---- Path: %s ----' % path )
    # data = cPickle.load(_import)
    data = json.load( _import, object_hook = from_json )
    print( '---- File loaded in: %s seconds ----' % cmds.timerX( st = start ) )
    start = cmds.timerX()
    print( '==== Setting weighting data on %s points ====' % str( len( data ) - 1 ) )
    setSkinInfo( obj, data, update = True )
    print( '==== Skin point data loaded in: %s seconds ====' % cmds.timerX( st = start ) )
    _import.close()

    #
    '''
    fileObjectJSON = open(path, 'r')
    clpJSON = json.load(fileObjectJSON, object_hook=from_json)
    fileObjectJSON.close()
    return clpJSON
    '''


def exportWeights02( path ):
    '''
    Export the weighting and skinCluster information 
    '''
    sel = cmds.ls( sl = True )
    if len( sel ) == 1:
        skinNode = getSkinCluster( sel[0] )
        if skinNode != None:
            # store skinning information
            storedSkinInfo = storeSkinInfo( skinNode, getSkinNodeInformation( skinNode ), True )

            if len( storedSkinInfo ) > 0:
                # export = open(path, 'wb')
                timer = cmds.timerX()
                print( '++++ Dumping weighting information ++++\n++++ path: %s ++++' % path )
                '''
                cPickle.dump(storedSkinInfo, export)
                export.close()
                '''
                #
                export = open( path, 'wt' )  # wt = write text # wb = write bytes
                json.dump( storedSkinInfo, export, default = to_json, indent = 1 )
                export.close()
                print( '++++ Dump Complete in: %s seconds ++++' % cmds.timerX( st = timer ) )
            else:
                OpenMaya.MGlobal.displayWarning( '' )


def to_json( python_object ):
    if isinstance( python_object, kwo.SkinNodeInformation ):
        return {'__class__': 'SkinNodeInformation',
                '__value__': python_object.__dict__}
    if isinstance( python_object, kwo.SkinPoint ):
        return {'__class__': 'SkinPoint',
                '__value__': python_object.__dict__}
    raise TypeError( repr( python_object ) + ' is not JSON serializable' )


def from_json( json_object ):
    if '__class__' in json_object:
        if json_object['__class__'] == 'SkinNodeInformation':
            # !!! decoding breaks here !!!
            # print 'Clip'
            sni = kwo.SkinNodeInformation()
            sni = populate_from_json( sni, json_object['__value__'] )
            return sni
            # return Clip(**json_object['__value__'])
        if json_object['__class__'] == 'SkinPoint':
            # print 'Layer'
            sp = kwo.SkinPoint()
            sp = populate_from_json( sp, json_object['__value__'] )
            return sp
            # return Layer(**json_object['__value__'])
    return json_object


def populate_from_json( cls, dct = {} ):
    for key in dct:
        try:
            getattr( cls, key )
        except AttributeError:
            pass
            # print "Doesn't exist"
        else:
            setattr( cls, key, dct[key] )
    return cls


def batchNurbsWeightControl( func, *args ):
    '''
        def batchNurbsWeightsCMD(self,*args):
        path = cmds.textField(self.internalWindowName + '_txtFld', query=True, tx=True)
        cmds.deleteUI(self.internalWindowName, window = True)

        sel = cmds.ls(sl=True)
        if len(sel) == 1:
            if self.mode == 3:
                batchExportNurbsWeights(path, sel[0])
            else:
                batchImportNurbsWeights(path)

        else:
            OpenMaya.MGlobal.displayWarning('Select ONE object for preform operation on.')
            '''
    funcDict = {'import': [batchImportNurbsWeights, 'Batch Import NURBS Weights'], 'export': [batchExportNurbsWeights, 'Batch Export NURBS Weights']}
    sel = cmds.ls( sl = True )

    if len( sel ) == 1:
        skinNode = getSkinCluster( sel[0] )
        # change the behavior based on the existnce of a skinCluster on the
        # selected item
        skinCheck = None
        if skinNode != None or func == 'import':
            skinCheck = True

        if skinCheck != None:

            # Inherite the KeyBrowserCore and override actionButtonCommand
            class SkinBrowser( key_ui_lib.KeyBrowserCore ):

                def actionButtonCmd( self, *args ):
                    filePath = pm.textField( self.pathTxtField, query = True, tx = True )
                    # make sure the filePath is a file and not a directory
                    if os.path.isdir( filePath ):
                        self.setLastPathEnv()
                        if pm.window( self.winName, exists = True ):
                            pm.deleteUI( self.winName )
                        if func == 'export':
                            funcDict[func][0]( filePath, sel[0] )
                        else:
                            funcDict[func][0]( filePath )
                    else:
                        cmds.error( 'File found, directory required.' )

            # Set the default path to the HOME
            path = os.environ['HOME']
            # if not os.environ.has_key( 'key_last_saved_path' ):
            if 'key_last_saved_path' not in os.environ:
                os.environ['key_last_saved_path'] = 'none'
            else:
                pass
                # print 'no!'
            # Set the last saved path for the next time the window is opened
            lastpath = os.environ['key_last_saved_path']

            if lastpath != 'none':
                path = lastpath
            skinExport = SkinBrowser( func[0].upper() + func[+1:], path, 'wtt', funcDict[func][1],
                                     _filter = ['.txt', '.mb', '.ma', '*.*'] )
            skinExport.win()
        else:
            cmds.error( 'No skinCluster found, we\'re done here.' )
    else:
        cmds.error( 'Selection size incorrect, select ONE object.' )


def weightTransferControl( func, path = None, *args ):
    '''
    Control the import or export depending one what func it
    func<string>, string should be either import or export
    '''
    funcDict = {'import': [importWeights02, 'Import Weights'], 'export': [exportWeights02, 'Export Weights']}
    sel = cmds.ls( sl = True )
    print( '???', sel )

    if len( sel ) == 1:
        skinNode = getSkinCluster( sel[0] )
        print( '___', skinNode )
        # change the behavior based on the existnce of a skinCluster on the
        # selected item
        skinCheck = None
        if skinNode != None or func == 'import':
            skinCheck = True

        if skinCheck != None:

            # Inherite the KeyBrowserCore and override actionButtonCommand
            class SkinBrowser( key_ui_lib.KeyBrowserCore ):

                def actionButtonCmd( self, *args ):
                    filePath = pm.textField( self.pathTxtField, query = True, tx = True )
                    # make sure the filePath is a file and not a directory
                    if not os.path.isdir( filePath ):
                        self.setLastPathEnv()
                        if pm.window( self.winName, exists = True ):
                            pm.deleteUI( self.winName )
                        if func == 'export':
                            funcDict[func][0]( filePath )
                        else:
                            funcDict[func][0]( sel[0], filePath )
                    else:
                        cmds.error( 'Directory given, file required.' )

            # Set the default path to the desktop
            path = os.environ['HOME']
            # if not os.environ.has_key( 'key_last_saved_path' ):
            if 'key_last_saved_path'not in os.environ:
                os.environ['key_last_saved_path'] = 'none'
            # Set the last saved path for the next time the window is opened
            lastpath = os.environ['key_last_saved_path']

            if lastpath != 'none':
                path = lastpath
            skinExport = SkinBrowser( func[0].upper() + func[+1:], path, 'wtt', funcDict[func][1],
                                     _filter = ['.txt', '.mb', '.ma', '*.*'] )
            skinExport.win()
        else:
            cmds.error( 'No skinCluster found, we\'re done here.' )
    else:
        cmds.error( 'Selection size incorrect, select ONE object.' )


def createSkinCluster( obj, skinInfo ):
    '''
    Make a skinCluster node, based off of the information in the skinInfo object.
    '''
    skinCluster = None
    mesh = []
    for idx, inf in enumerate( skinInfo[0].influences ):
        print( inf )
        if cmds.objExists( inf ):
            # When creating a skinCluster it's critical the first infleuence is a joint
            # otherwise Maya won't create the cluster
            if cmds.nodeType( inf ) == 'joint':
                # If no skinCluster create the skinCluster with index
                if skinCluster == None:
                    skinCluster = cmds.skinCluster( obj, inf, tsb = True )[0]
                    cmds.setAttr( skinCluster + '.useComponents', int( skinInfo[0].useComponents ) )
                    '''
                    if mesh > 0:
                        for item in mesh:
                            shapeNode = cmds.listRelatives(item[0], shapes=True)[0]
                            if cmds.nodeType(shapeNode)=='mesh':
                                cmds.skinCluster(skinCluster, edit=True, weight=0, dr=skinInfo[0].dropoffRate[item[1]],
                                                 ps=skinInfo[0].polygonSmoothness[item[1]],ug=True, ai=item[0])
                            else:
                                cmds.skinCluster(skinCluster, edit=True, weight=0, dr=skinInfo[0].dropoffRate[item[1]],
                                                 ns=skinInfo[0].nurbsSamples[item[1]], ug=True, ai=item[0])
                                                 '''
                else:
                    cmds.skinCluster( skinCluster, edit = True, weight = 0, ai = inf )

            # Mesh and Nurbs surfaces... And first index not a 'joint'.
            else:
                # print 'here'
                if skinCluster != None:
                    shapeNode = cmds.listRelatives( inf, shapes = True )[0]

                    if cmds.nodeType( shapeNode ) == 'mesh':
                        cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = skinInfo[0].dropoffRate[idx],
                                         ps = skinInfo[0].polygonSmoothness[idx], ug = True, ai = inf )
                    else:
                        cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = skinInfo[0].dropoffRate[idx],
                                         ns = skinInfo[0].nurbsSamples[idx], ug = True, ai = inf )
                # If the loops get to here the first item in the exported list is probably not a joint.
                else:
                    # try adding list object to account for mesh instead of joint as first influence
                    cmds.error( 'No skinCluster created, first object in exported skin not a joint\nOpperation aborted' )
                    # mesh.append([inf,idx])
                    print( mesh )
        else:
            cmds.error( '%s, not found in scene skipping adding as influence' )

    return skinCluster


def setSkinInfo( obj, storedSkinInfo, update = False, updatePercent = .2 ):
    '''
    Set(import) the skinning information to the storedSkinInfo
    '''
    if update:
        incrementSize = int( ( len( storedSkinInfo ) - 1 ) * updatePercent )
        incrementTotal = incrementSize
        gMainProgressBar = mm.eval( '$tmp = $gMainProgressBar' )
        cmds.progressBar( gMainProgressBar, edit = True, w = 200,
                         beginProgress = True,
                         status = '0',
                         maxValue = len( storedSkinInfo ) - 1 )

    skinNode = getSkinCluster( obj )
    # Out with the old, delete the current skinNode
    if skinNode != None:
        cmds.delete( skinNode )

    # In with the new
    skinNode = createSkinCluster( obj, storedSkinInfo )
    if skinNode != None:
        cmds.setAttr( skinNode + '.normalizeWeights', 0 )
        baseFmtStr = skinNode + '.weightList[%d]'

        # interate through each skinPoint
        for idx, info in enumerate( storedSkinInfo ):
            # skip the first index as it's the SkinNodeInformation
            if idx > 0:
                if update and info.index == incrementTotal:
                    cmds.progressBar( gMainProgressBar, edit = True, status = incrementTotal, step = incrementSize )
                    incrementTotal += incrementSize

                weightFmtStr = baseFmtStr % info.index + '.weights[%d]'

                for inf in range( len( storedSkinInfo[0].influences ) ):
                    if info.weightList[inf] > 0:
                        # For a speed inprovment the skinCluster is deleted then re-created with the same options
                        cmds.setAttr( weightFmtStr % inf, info.weightList[inf] )
                        # The first influence is added with a weighting of 1 on all vertex. Not ideal but unavoidable.
                        # Remove the weighting from the first influence on each vertex, this will avoid double transformation.
                        cmds.setAttr( weightFmtStr % 0, info.weightList[0] )
        if update:
            cmds.progressBar( gMainProgressBar, edit = True, endProgress = True )
        cmds.setAttr( skinNode + '.normalizeWeights', 1 )


def rotateLocalJointAxis( *args ):
    '''
    #-------------
    # Name        :rotateLocalJointAxis
    # Arguements  :None
    # Description :Rotate the local rotational axis of the selected joint
    '''
    tmpSel = cmds.ls( sl = True )
    if len( tmpSel ) == 1:
        # declare the rotation variables and set them to 0
        x = y = z = 0

        # get the selected rotation axis
        sel = cmds.radioCollection( 'rotRbCol', query = True, sl = True )
        # get the value to rotate by
        val = cmds.intFieldGrp( 'localRotVal', query = True, value1 = True )

        # set the x y or z value depending on which button is selected
        if sel == 'radioButton1':
            x = val
        elif sel == 'radioButton2':
            y = val
        else:
            z = val
        # convert the selection list into a single string
        sel = tmpSel[0]
        # check sel for nodeType
        if cmds.nodeType( sel ) == 'joint':
            # rotate the local rotational axis
            cmds.rotate( x, y, z, ( sel ), r = True, os = True )
        else:
            print( 'Select a joint.' )
    else:
        print( 'Selection count wrong, please have only one joint selected.' )


def toggleLocalAxisVis( *args ):
    '''
    #-------------
    # Name        :rotateLocalJointAxis
    # Arguements  :None
    # Description :Toggle the local rotational axis visibility
    #-------------
    '''
    # get the current selection
    sel = cmds.ls( sl = True )
    if len( sel ) > 0:
        # iterate through the selection and toggle the visibility of the
        # local rotational axis if the selection is a joint
        for itm in sel:
            if cmds.nodeType( itm ) == 'joint':
                # get the current state of the display
                getSel = cmds.getAttr( itm + '.displayLocalAxis' )
                if getSel == 1:
                    cmds.setAttr( itm + '.displayLocalAxis', 0 )
                else:
                    cmds.setAttr( itm + '.displayLocalAxis', 1 )
            else:
                print( '%s, is not a joint, passing' ) % ( itm )
    else:
        print( 'Nothing is selected...' )


def rotLocalAxisWin( *args ):
    '''
    #-------------
    # Name        :rotLocalAxisWin
    # Arguements  :None
    # Description :GUI for editing location rotational axis
    # Dependancies: toggleLocalAxisVis(),rotateLocalJointAxis()
    #-------------
    '''
    # delete the window if it exists
    if cmds.window( 'rotateLocalAxisWin', exists = True ):
        cmds.deleteUI( 'rotateLocalAxisWin', window = True )

    cmds.window( 'rotateLocalAxisWin', width = 180, height = 115, s = False )
    mainForm = cmds.formLayout( numberOfDivisions = 100 )
    # create the axis radio buttons
    rbCollection = cmds.radioCollection( 'rotRbCol' )
    rbX = cmds.radioButton( label = 'x', sl = True )
    rbY = cmds.radioButton( label = 'y' )
    rbZ = cmds.radioButton( label = 'z' )
    cmds.setParent( '..' )

    # create the int field and buttons
    val = cmds.intFieldGrp( 'localRotVal', numberOfFields = 1, label = 'Rotate Value:', value1 = 90, cw2 = [90, 40] )
    visBtn = cmds.button( 'toggleLocalRotDisBtn', label = 'Toggle Local Axis Display', c = 'key_rig_lib.toggleLocalAxisVis()' )
    rotBtn = cmds.button( 'rotateBtn', label = 'Rotate', c = 'key_rig_lib.rotateLocalJointAxis()' )

    # lay out the controls in the window
    cmds.formLayout( 
        mainForm, edit = True,
        attachForm = [( rbX, 'top', 5 ), ( rbX, 'left', 5 ), ( rbY, 'top', 5 ), ( rbZ, 'top', 5 ),
                    ( val, 'left', 5 ), ( rotBtn, 'left', 5 ), ( rotBtn, 'right', 5 ),
                    ( visBtn, 'left', 5 ), ( visBtn, 'right', 5 )],
        attachControl = [( rbY, 'left', 25, rbX ), ( rbZ, 'left', 25, rbY ), ( val, 'top', 5, rbX ), ( rotBtn, 'top', 5, val ),
                       ( visBtn, 'top', 5, rotBtn )]
    )
    # show the window
    cmds.showWindow( 'rotateLocalAxisWin' )


def exportWeights( path, obj ):
    '''
    #-------------
    # Name        :exportWeights
    # Arguments   :<path> : string
    #             <obj>  : string
    # Description :Export weighting information based on the nodeType of the obj.
    # Object types are, mesh, nurbsSurface and nurbsCurve
    #-------------
    '''
    # get the type of node
    nodeType = cmds.nodeType( cmds.listRelatives( obj, shapes = True )[0] )
    if nodeType == 'mesh':
        exportMeshWeights( path, obj )
    elif nodeType == 'nurbsSurface':
        exportNurbsSurfaceWeights( path, obj )
    elif nodeType == 'nurbsCurve':
        exportNurbsCurveWeights( path, obj )


def exportNurbsCurveWeights( path, obj ):
    '''
    #-------------
    # Name        :exportNurbsCurveWeights
    # Arguments   :<path> : string
    #             <obj>  : string
    # Description :Export weighting of the nurbsCurv
    #-------------
    '''
    # get the degree and span count
    cvs = cmds.getAttr( obj + '.degree' ) + cmds.getAttr( obj + '.spans' )
    # extract the skinCluster
    import maya.mel as mm
    skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
    if len( skin ) != 0:
        # force normilization of the weighting
        cmds.setAttr( skin + '.normalizeWeights', 1 )
        cmds.skinPercent( skin, obj, nrm = True )

        # get a list of all the influences on in the skin
        infList = cmds.listConnections( skin + '.matrix' )

        # create/open then output file
        fileOut = open( path, 'w' )

        # on the first list write out the influence list
        fileOut.writelines( str( infList ) + '\n' )

        for cv in range( 0, cvs ):
            infCnt = 0
            exportStr = '(' + str( cv ) + ','
            for inf in range( len( infList ) ):
                infInfo = cmds.skinPercent( skin, obj + '.cv [' + str( cv ) + ']', transform = infList[inf], query = True )
                if infInfo != 0:
                    if infCnt == 0:
                        if infInfo == 1.0:
                            exportStr += ( '%s,%s' ) % ( inf, infInfo )
                            infCnt += 1
                        else:
                            exportStr += ( '%s,%s,' ) % ( inf, infInfo )
                            infCnt += 1
                    else:
                        if infCnt == 1:
                            exportStr += ( '%s,%s' ) % ( inf, infInfo )
                            infCnt += 1
                        else:
                            exportStr += ( ',%s,%s' ) % ( inf, infInfo )
                            infCnt += 1

            if cv + 1 == cvs:
                exportStr += ')'
            else:
                exportStr += ')\n'

            fileOut.writelines( exportStr )
        fileOut.close()


def exportMeshWeights( path, obj, updatebar = False ):
    '''
    #-------------
    # Name        :exportMeshWeights
    # Arguments   :<path>: string
    #             <obj> : string
    # Description :Export the weight information from a polygon object
    #-------------
    '''
    # get the vertex count
    vtxCnt = cmds.polyEvaluate( obj, v = True )
    # extract the skinCluster
    import maya.mel as mm
    if updatebar == True:
        gMainProgressBar = mm.eval( '$tmp=$gMainProgressBar' )
        cmds.progressBar( gMainProgressBar, edit = True, beginProgress = True, isInterruptable = False, status = 'Exporting Weights from ' + obj, maxValue = vtxCnt )
    skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
    if len( skin ) != 0:
        # force normilization of the weighting
        cmds.setAttr( skin + '.normalizeWeights', 1 )
        cmds.skinPercent( skin, obj, prw = .0001 )
        cmds.skinPercent( skin, obj, nrm = True )
        # get a list of all the influences on in the skin
        infList = cmds.listConnections( skin + '.matrix' )

        # create/open then output file
        fileOut = open( path, 'w' )
        # on the first list write out the influence list
        fileOut.writelines( str( infList ) + '\n' )
        for vtx in range( 0, vtxCnt ):
            if updatebar == True:
                cmds.progressBar( gMainProgressBar, edit = True, step = 1 )
            infCnt = 0
            exportStr = '(' + str( vtx ) + ','
            for inf in range( len( infList ) ):
                infInfo = cmds.skinPercent( skin, obj + '.vtx[' + str( vtx ) + ']', transform = infList[inf], query = True )

                # forcing normalization as maya can't seem to handle it
                if infInfo > 1:
                    infInfo = 1

                if infInfo > 0:
                    if infCnt == 0:
                        if infInfo == 1.0:
                            exportStr += ( '%s,%s' ) % ( inf, infInfo )
                            infCnt += 1
                        else:
                            exportStr += ( '%s,%s,' ) % ( inf, infInfo )
                            infCnt += 1
                    else:
                        if infCnt == 1:
                            exportStr += ( '%s,%s' ) % ( inf, infInfo )
                            infCnt += 1

                        else:
                            exportStr += ( ',%s,%s' ) % ( inf, infInfo )
                            infCnt += 1

            if vtx + 1 == vtxCnt:
                exportStr += ')'
            else:
                exportStr += ')\n'

            fileOut.writelines( exportStr )
        fileOut.close()
        if updatebar == True:
            cmds.progressBar( gMainProgressBar, edit = True, endProgress = True )
    else:
        print( 'skinCluster not found, no weights exported.' )


def exportNurbsSurfaceWeights( path, obj ):
    '''
    #-------------
    # Name        :exportNurbsSurfaceWeights
    # Arguments   :<node>          : string
    #             <attribute name>: string
    # Description :Export the weighting from a nurbs surface
    #-------------
    '''
    # check for a skinCluster
    import maya.mel as mm
    skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
    if len( skin ) != 0:
        # force normilization of the weighting
        cmds.setAttr( skin + '.normalizeWeights', 1 )
        cmds.skinPercent( skin, obj, nrm = True )

        # get the influence list
        infList = cmds.listConnections( skin + '.matrix' )

        minMaxRangeU = cmds.getAttr( cmds.listRelatives( obj, shapes = True )[0] + '.minMaxRangeU' )[0][1]
        # get the range of U CVs
        numSpansU = cmds.getAttr( obj + '.spansU' )
        degreeU = cmds.getAttr( obj + '.degreeU' )

        # get the range of V CVs
        numSpansV = cmds.getAttr( obj + '.spansV' )
        degreeV = cmds.getAttr( obj + '.degreeV' )

        formU = cmds.getAttr( obj + '.formU' )
        formV = cmds.getAttr( obj + '.formV' )

        uCv = numSpansU + degreeU
        if formU == 2:
            uCv -= degreeU

        vCv = numSpansV + degreeV
        if formV == 2:
            vCv -= degreeV

        # open the fileOut path
        fileOut = open( path, 'w' )

        # write the file out
        fileOut.writelines( str( infList ) + '\n' )

        for i in range( uCv ):  # spans
            for j in range( vCv ):  # degree
                infCnt = 0
                exportStr = '(\'[%s][%s]\',' % ( i, j )
                for inf in range( len( infList ) ):
                    # get the weighting  information
                    infInfo = cmds.skinPercent( skin, obj + '.cv[' + str( i ) + '][' + str( j ) + ']', t = infList[inf], query = True )
                    if infInfo != 0:
                        if infCnt == 0:
                            if infInfo == 1.0:
                                exportStr += ( '\'%s\',%s' ) % ( infList[inf], infInfo )
                                infCnt += 1
                            else:
                                exportStr += ( '\'%s\',%s,' ) % ( infList[inf], infInfo )
                                infCnt += 1
                        else:
                            if infCnt == 1:
                                exportStr += ( '\'%s\',%s' ) % ( infList[inf], infInfo )
                                infCnt += 1
                            else:
                                exportStr += ( ',\'%s\',%s' ) % ( infList[inf], infInfo )
                                infCnt += 1
                exportStr += ')\n'
                fileOut.write( exportStr )
        fileOut.close()


def importWeights( path, obj ):
    '''
    #-------------
    # Name        :importWeights
    # Arguments   :<node>          : string
    #             <attribute name>: string
    # Description :Import weighting information
    #-------------
    '''
    if cmds.objExists( obj ) == 1:
        # get the type of node
        try:
            nodeType = cmds.nodeType( cmds.listRelatives( obj, shapes = True )[0] )
            if nodeType == 'mesh':
                importMeshWeights( path, obj )
            elif nodeType == 'nurbsSurface':
                importNurbSurfaceWeights2( path, obj )
            elif nodeType == 'nurbsCurve':
                importMeshWeights( path, obj )
        except:
            print( 'something isn\'t working!' )
    else:
        print( ( '%s does not exist in scene, skipping...' ) % ( obj ) )


def importNurbSurfaceWeights( path, obj ):
    '''
    #-------------
    # Name        :importNurbSurfaceWights
    # Arguments   :<node>          : string
    #             <attribute name>: string
    # Description :Import weighting information for Nurbs Surfaces
    #-------------
    '''
    # get the range of U CVs
    numSpansU = cmds.getAttr( obj + '.spansU' )
    degreeU = cmds.getAttr( obj + '.degreeU' )

    # get the range of V CVs
    numSpansV = cmds.getAttr( obj + '.spansV' )
    degreeV = cmds.getAttr( obj + '.degreeV' )

    formU = cmds.getAttr( obj + '.formU' )
    formV = cmds.getAttr( obj + '.formV' )

    uCv = numSpansU + degreeU
    if formU == 2:
        uCv -= degreeU

    vCv = numSpansV + degreeV
    if formV == 2:
        vCv -= degreeV

    # open the file path
    fileIn = open( path, 'r' )
    fileString = fileIn.readlines()
    cnt = 0
    infList = []

    import maya.mel as mm
    skinCluster = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )

    if len( skinCluster ) != 0:
        cmds.delete( skinCluster )

    fileIn = open( path, 'r' )
    fileInList = fileIn.readlines()

    while cnt != len( fileInList ):
        if cnt == 0:
            infList = eval( fileInList[cnt] )
            for idx in range( 0, len( infList ) ):
                getNode = cmds.nodeType( infList[idx] )
                if getNode == 'joint':
                    if idx == 0:
                        skinCluster = cmds.skinCluster( obj, infList[idx], tsb = True )[0]
                    else:
                        cmds.skinCluster( skinCluster, edit = True, weight = 0, ai = infList[idx] )
                else:
                    cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = 4, ps = 5, ns = 15, ug = True, ai = cmds.listRelatives( infList[idx], shapes = True )[0] )
            cmds.setAttr( skinCluster + ".useComponents", 1 )
            cnt += 1
        else:
            for i in range( vCv ):
                for j in range( uCv ):
                    evalLine = eval( fileInList[cnt] )
                    wgtStr = 'cmds.skinPercent(\'' + skinCluster + '\', \'' + obj + '.cv' + evalLine[0] + '\', tv =['
                    for itm in range( 1, len( evalLine ), 2 ):
                        if itm != 1:
                            wgtStr += ( ',(\'%s\', %s)' ) % ( evalLine[itm], evalLine[itm + 1] )
                        else:
                            wgtStr += ( '(\'%s\', %s)' ) % ( evalLine[itm], evalLine[itm + 1] )

                    wgtStr += '])'
                    eval( wgtStr )
        cnt += 1


def importNurbSurfaceWeights2( path, obj ):
    # open the file path
    fileIn = open( path, 'r' )
    fileString = fileIn.readlines()
    cnt = 0
    infList = []

    skinCluster = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )

    if len( skinCluster ) != 0:
        cmds.delete( skinCluster )

    fileIn = open( path, 'r' )
    fileInList = fileIn.readlines()
    fileIn.close()
    for i, v in enumerate( fileInList ):
        info = v.strip( '\n' )
        if i == 0:
            infList = eval( info )
            for idx, inf in enumerate( infList ):
                getNode = cmds.nodeType( inf )
                # Create the skinCluster then add the influences
                if getNode == 'joint':
                    if idx == 0:
                        skinCluster = cmds.skinCluster( obj, inf, tsb = True )[0]
                    else:
                        cmds.skinCluster( skinCluster, edit = True, weight = 0, ai = inf )
                else:
                    # if a piece of geomitry is being added
                    infShape = cmds.listRelatives( inf, shapes = True )[0]

                    cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = 0, ps = 0, ns = 0, ug = True, ai = infShape )
            cmds.setAttr( skinCluster + ".useComponents", 0 )
        else:
            evalLine = eval( info )

            wgtStr = 'cmds.skinPercent(\'' + skinCluster + '\', \'' + obj + '.cv' + evalLine[0] + '\', tv =['

            for itm in range( 1, len( evalLine ), 2 ):
                if itm != 1:
                    wgtStr += ( ',(\'%s\', %s)' ) % ( evalLine[itm], evalLine[itm + 1] )
                else:
                    wgtStr += ( '(\'%s\', %s)' ) % ( evalLine[itm], evalLine[itm + 1] )

            wgtStr += '])'
            eval( wgtStr )
    cmds.setAttr( skinCluster + ".useComponents", 1 )


def exportWeightsToFile( *args ):
    #  def __init__(self, intWinName, visWinName, fileFilter, startPath, fieldState):
    fileDialog = WeightBroswer( 'key_exportWeightsWin', 'Export Weights Window', '.txt', os.environ['HOME'], 1, 'Export Weights', 1 )
    fileDialog.fileWin()


def importWeightsFromFile( *args ):
    #  def __init__(self, intWinName, visWinName, fileFilter, startPath, fieldState):
    fileDialog = WeightBroswer( 'key_importWeightsWin', 'Import Weights Window', '.txt', os.environ['HOME'], 1, 'Import Weights', 2 )
    fileDialog.fileWin()


def importMeshWeights( path, obj, updatebar = False ):
    '''
    #-------------
    # Name        :importWeights
    # Arguments   :<node>          : string
    #             <attribute name>: string
    # Description :Import weighting information
    #-------------
    '''
    # open the file path
    fileIn = open( path, 'r' )
    fileString = fileIn.readlines()
    lineCnt = 0
    infList = []
    skinCluster = ''
    try:
        skinCluster = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
    except:
        pass
    if len( skinCluster ) != 0:
        cmds.delete( skinCluster )
    if updatebar == True:
        gMainProgressBar = mm.eval( '$tmp = $gMainProgressBar' )
        cmds.progressBar( gMainProgressBar, edit = True, beginProgress = True, isInterruptable = False, status = 'Importing Weights to ' + obj, maxValue = len( fileString ) )

    for line in fileString:
        if updatebar == True:
            cmds.progressBar( gMainProgressBar, edit = True, step = 1 )
        if lineCnt == 0:
            infList = eval( line )
            lineCnt += 1
            # make the skinCluster
            for idx in range( 0, len( infList ) ):
                nodeExists = cmds.objExists( infList[idx] )
                if nodeExists:
                    getNode = cmds.nodeType( infList[idx] )
                    if getNode == 'joint':
                        if idx == 0:
                            skinCluster = cmds.skinCluster( obj, infList[idx], tsb = True )[0]
                        else:
                            cmds.skinCluster( skinCluster, edit = True, weight = 0, ai = infList[idx] )
                    else:
                        shapeNode = cmds.listRelatives( infList[idx], shapes = True )[0]
                        shapeType = cmds.nodeType( shapeNode )
                        if shapeType == 'mesh':
                            cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = 4, ps = 0, ns = 0, ug = True, ai = shapeNode )
                        else:
                            cmds.skinCluster( skinCluster, edit = True, weight = 0, dr = 4, ps = 0, ns = 11, ug = True, ai = shapeNode )

                    cmds.setAttr( skinCluster + ".useComponents", 0 )
                else:
                    import key_sys_lib as ksl
                    ksl.printMayaWarning( 'skipping...' + infList[idx] + ' not found in scene.' )
        else:
            infInfo = eval( line )
            # remove the original weights since there is no normalization, this will prevent double transforms
            # removing all the weights from the first influence in the skinCluster on each vertex
            cmds.setAttr( skinCluster + '.weightList[' + str( infInfo[0] ) + '].weights[0]', 0 )
            if lineCnt - 1 == 0:
                for i in range( 1, len( infInfo ), 2 ):
                    cmds.setAttr( skinCluster + '.weightList[' + str( infInfo[0] ) + '].weights[' + str( infInfo[i] ) + ']', infInfo[i + 1] )
                lineCnt += 1
            else:
                cmds.setAttr( skinCluster + '.weightList[' + str( infInfo[0] ) + '].weights[' + str( 0 ) + ']', 0 )
                for i in range( 1, len( infInfo ), 2 ):
                    try:
                        cmds.setAttr( skinCluster + '.weightList[' + str( infInfo[0] ) + '].weights[' + str( infInfo[i] ) + ']', infInfo[i + 1] )
                    except:
                        print( 'Something went wrong with vertx %s' % infInfo[0] )
                lineCnt += 1
    fileIn.close()
    cmds.setAttr( skinCluster + ".useComponents", 1 )
    if updatebar == True:
        cmds.progressBar( gMainProgressBar, edit = True, endProgress = True )


def copyWeightFromSelVtx( verbose = False ):
    '''Copy the influences and their weights from the selected vertex.'''
    # get a list of the selections
    sel = cmds.ls( sl = True, fl = True, long = True )
    # make sure one vertex is selected
    if len( sel ) == 1:
        # recast sel to the first selection as a list was returned
        sel = sel[0]
        # extract the name of the object
        obj = sel.split( '.' )[0]
        # get the skinCluster
        skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
        # if the obj has a skinCluster
        if len( skin ) != 0:
            # get a list of the influences on the skinCluster
            infList = cmds.listConnections( skin + '.matrix' )
            wgtList = [], []
            # interate through the list to get the weighting
            for i in range( 0, len( infList ) ):
                # get the weight
                infInfo = cmds.skinPercent( skin, sel, transform = infList[i], query = True )
                # if the inf has a weight, then capture the value as well as the influence object
                if infInfo > 0:
                    wgtList[0].append( infInfo )
                    wgtList[1].append( infList[i] )
            # Pass the values to maya in a string, these values will be queried when doing the paste
            mm.eval( 'string $atom_copy_wgt_array[];' )
            # make sure the array is clear
            mm.eval( 'clear $atom_copy_wgt_array' )

            mm.eval( 'string $atom_copy_inf_array[];' )
            mm.eval( 'clear $atom_copy_inf_array' )
            # Pass the data to Maya
            for i in range( 0, len( wgtList[0] ) ):
                if verbose == True:
                    print( ( 'INF IDX:%s, INFLUENCE:%s, WEIGHT: %s' ) % ( i, wgtList[1][i], wgtList[0][i] ) )

                mm.eval( '$atom_copy_wgt_array[' + str( i ) + ']=' + str( wgtList[0][i] ) + ';' )
                mm.eval( '$atom_copy_inf_array[' + str( i ) + ']="' + str( wgtList[1][i] ) + '";' )
        else:
            print( 'Selected object has no skinCluster.' )
    else:
        print( 'Selection is wrong, select ONE vertex.' )


def findInfIndex( skin, inf ):
    '''Find the index of the current influence in it's influence list.\n
    skin:<skinCluster>
    inf:<string>
    '''
    # get a list of all the influence objects, this returns a list of strings
    infList = cmds.listConnections( skin + '.matrix' )
    index = None
    for i in range( 0, len( infList ) ):
        if infList[i] == inf:
            index = i
    return index


def clearWeightsFromVtx( obj, skin, vtx ):
    '''Set all the influence weights on the vtx to 0.\n
    skin:<skinCluster>
    vtx:int or string(gets converted to a string regardless)
    Notes:For this to work effectively turn off normalization.
    '''

    infList = cmds.listConnections( skin + '.matrix' )
    for i in range( 0, len( infList ), 1 ):
        cmds.setAttr( skin + '.weightList[' + str( vtx ) + '].weights[' + str( i ) + ']', 0 )
        # skinStr = 'skinPercent -tv ' + infList[i] + ' 0 ' + skin + ' ' + obj +'.vtx[' + vtx +']'
        # mm.eval(skinStr)


def pasteWeightsFromSelectedVtx( *args ):
    '''Paste the stored copy information to the selected vertex.'''
    sel = cmds.ls( sl = True, fl = True, long = True )
    if len( sel ) == 1:
        # recast sel to the first selection as a list was returned
        sel = sel[0]
        # extract the name of the object
        obj = sel.split( '.' )[0]
        # extract the vertex
        vtx = sel.split( '.' )[1][4:-1]
        # get the skinCluster
        skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
        # if the obj has a skinCluster
        if len( skin ) != 0:
            # turn off weight normalization
            cmds.setAttr( skin + '.normalizeWeights', 0 )
            # pass the varaible information from Maya to python, $temp is needed or maya will error, this also causes the call to return
            # the list.
            infList = mm.eval( '$temp = $atom_copy_inf_array' )
            wgtList = mm.eval( '$temp = $atom_copy_wgt_array' )

            # clear the weights before anything get changed
            clearWeightsFromVtx( obj, skin, vtx )
            for i in range( 0, len( infList ) ):
                # get the current influences index in it's skinCluster
                infIdx = findInfIndex( skin, infList[i] )

                if infIdx != None:
                    # vertex number, influence index, value
                    cmds.setAttr( skin + '.weightList[' + str( vtx ) + '].weights[' + str( infIdx ) + ']', float( wgtList[i] ) )
                    # skinStr = 'skinPercent -tv ' + infList[i] +' ' + wgtList[i] + ' ' + skin + ' ' + obj +'.vtx[' + vtx +']'
                    # mm.eval(skinStr)
            cmds.setAttr( skin + '.normalizeWeights', 1 )


def importWeightsFromFileToVtx( updatebar = 'False' ):
    '''Import Weighting to the selected vertex. It's assumed that the user is using the identical\n
    skinCluster for the import that was used to generate the exported file.
    '''
    path = cmds.fileDialog( directoryMask = os.environ['HOME'], dm = '*.txt' )
    if len( path ) > 0:
        # read in the file, going to assume the user knows what they're doing
        wgtFile = file( path, 'r' )
        # read all the lines
        impList = wgtFile.readlines()
        # break the lines into lists
        impInfList = eval( impList[0] )
        # get the current vtx selection, this may be a mistake, but going to assume
        # the user knows what they're doing
        sel = cmds.ls( sl = True, fl = True )
        if len( sel ) > 0:
            # get the skinCluster of the selection
            skin = mm.eval( 'findRelatedSkinCluster("' + sel[0].split( '.' )[0] + '")' )
            # get the skins influence list
            skinInfList = cmds.listConnections( skin + '.matrix' )
            # turn off weight normalization
            cmds.setAttr( skin + '.normalizeWeights', 0 )
            gMainProgressBar = ''
            if updatebar == "True":
                gMainProgressBar = mm.eval( '$tmp = $gMainProgressBar' )
                cmds.progressBar( gMainProgressBar, edit = True, beginProgress = True, isInterruptable = False, status = 'Importing Weights To Selected Vtx ...', maxValue = len( sel ) )

            for i in sel:
                if updatebar == "True":
                    cmds.progressBar( gMainProgressBar, edit = True, step = 1 )

                vtx = i.split( '.' )[1][4:-1]
                # clear all the weights before adding any
                from key_libs import key_rig_lib as krl
                obj = i.split( '.' )[0]
                krl.clearWeightsFromVtx( obj, skin, vtx )
                # the list will be off by one vertex as the influence list is in the
                # first line of the exported file
                info = eval( impList[int( vtx ) + 1] )
                vtx = info[0]
                # wgt  =[]
                # inf  =[]
                wgt = None
                inf = None
                for i in range( 1, len( info ), 2 ):
                    inf = info[i]
                    wgt = info[i + 1]

                    # make sure the influences have the same index, if not find
                    # the right info from the imported list
                    if impInfList[int( inf )] != skinInfList[int( inf )]:
                        for j in range( 0, len( impInfList ), 1 ):
                            if impInfList[j] == skinInfList[int( inf )]:
                                # now that it's found in the list, get the index in the skinCluster
                                inf = krl.findInfIndex( skin, impInfList[j] )
                                break
                    # now set the weighting
                    cmds.setAttr( skin + '.weightList[' + str( info[0] ) + '].weights[' + str( inf ) + ']', float( wgt ) )
            # turn nomalization back on
            cmds.setAttr( skin + '.normalizeWeights', 1 )
            wgtFile.close()
            if updatebar == "True":
                cmds.progressBar( gMainProgressBar, edit = True, endProgress = True )


def populateInfTsl( control ):
    '''
    Description:Populate the control(textScrollList) with the selected objects influence list\n
    Arguments:
    control<textScrollList>: maya UI type
    return:N\A\n
    '''
    # get the first selected item
    obj = cmds.ls( sl = True )[0]
    skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
    # make sure something is selected
    if len( obj ) != 0:
        infList = None
        # make sure the obj has a skinCluster
        if len( skin ) != 0:
            infList = sorted( cmds.skinCluster( skin, query = True, inf = True ) )

        # make sure the skinCluster has some influences
        if infList != None:
            # clear the list before re-populating
            cmds.textScrollList( control, edit = True, ra = True )
            # turn on the "To" buttons
            cmds.button( 'ktiw_getInfToBut', edit = True, en = True )
            if control == 'ktiw_getInfToTsl':
                # the ktiw_getInfoFromTsl list should be populated, so get that info
                fromList = cmds.textScrollList( 'ktiw_getInfFromTsl', query = True, ai = True )
                for i in fromList:
                    # only want to add the influences that the target skinCluster does not have to the infList
                    if not i in infList:
                        cmds.textScrollList( control, edit = True, append = i )
                # in this case, both skinClusters have the same influences, so there is nothing to add
                if cmds.textScrollList( 'ktiw_getInfToTsl', query = True, ai = True ) == None:
                    cmds.textScrollList( control, edit = True, append = 'No influeces found to add' )
                    cmds.textScrollList( control, edit = True, append = 'from Master skinCluster' )
            # This is the master or "From" list
            else:
                for i in infList:
                    cmds.textScrollList( control, edit = True, append = i )
        # No skinCluster is found
        else:
            cmds.button( 'ktiw_getInfToBut', edit = True, en = False )
            cmds.textScrollList( control, edit = True, ra = True )
            cmds.textScrollList( control, edit = True, append = 'No skinCluster found' )


def removeInfTsl( control ):
    '''
    Description:Remove the selected influences from the control \n
    Arguments:
    control<textScrollList>: maya UI type
    return:N\A\n
    '''
    # get the selected items in the textScrollList
    listSel = cmds.textScrollList( control, query = True, si = True )
    if listSel != None:
        for i in listSel:
            listSel = cmds.textScrollList( control, edit = True, ri = i )


def addInf( control ):
    '''
    Description:Add the influences that exist in the textScrollList\n
    Arguments:
    control<textScrollList>: maya UI type
    return:N\A\n
    '''
    # get a list of influences
    infList = cmds.textScrollList( control, query = True, ai = True )
    if infList != None:
        # get the first selected object
        obj = cmds.ls( sl = True )[0]
        # get the skinCluster
        skin = mm.eval( 'findRelatedSkinCluster("' + obj + '")' )
        for inf in infList:
            # add the influences with no weighting
            cmds.skinCluster( skin, edit = True, ai = inf, wt = 0.0 )


def transferInfWin( *args ):
    '''
    Description:User interface for transfering influences\n
    Arguments:N\A\n
    return:N\A\n
    '''
    if cmds.window( 'key_addSkinInf_win', exists = True ):
        cmds.deleteUI( 'key_addSkinInf_win', window = True )

    ktiw_win = cmds.window( 'key_addSkinInf_win', title = 'Add Skin Influence', width = 415 )
    ktiw_mainFormLayout = cmds.formLayout( 'ktiw_mainFormLayout', numberOfDivisions = 100 )

    ktiw_getInfFromBut = cmds.button( 'ktiw_getInfFromBut', label = 'Get Influences "From"', width = 200, c = 'import key_rig_lib\nkey_rig_lib.populateInfTsl("ktiw_getInfFromTsl")' )
    ktiw_getInfFromTxt = cmds.text( 'ktiw_getInfoFromText', l = 'From:', width = 29, height = 14 )
    ktiw_getInfFromTsl = cmds.textScrollList( 'ktiw_getInfFromTsl', width = 202 )
    ktiw_delInfFromBut = 'placeholder'

    ktiw_getInfToBut = cmds.button( 'ktiw_getInfToBut', label = 'Get Influences "To"', width = 200, en = False, c = 'import key_rig_lib\nkey_rig_lib.populateInfTsl("ktiw_getInfToTsl")' )
    ktiw_getInfToTxt = cmds.text( 'ktiw_getInfToText', l = 'To:', width = 20, height = 14 )
    ktiw_getInfToTsl = cmds.textScrollList( 'ktiw_getInfToTsl', width = 202 )
    ktiw_remInfToBut = cmds.button( 'ktiw_remInfToBut', label = 'Remove Selected From list', width = 198, c = 'import key_rig_lib\nkey_rig_lib.removeInfTsl("ktiw_getInfToTsl")' )
    ktiw_addInfBut = cmds.button( 'ktiw_addInfBut', label = 'Add Influence', width = 198, c = 'import key_rig_lib\nkey_rig_lib.addInf("ktiw_getInfToTsl")' )

    cmds.formLayout( ktiw_mainFormLayout, edit = True,
                    attachForm = [( ktiw_getInfFromBut, 'top', 5 ), ( ktiw_getInfFromBut, 'left', 5 ),
                                ( ktiw_getInfToBut, 'top', 5 ),
                                ( ktiw_getInfFromTxt, 'left', 5 ),
                                ( ktiw_getInfFromTsl, 'left', 3 ), ( ktiw_getInfFromTsl, 'bottom', 55 ),
                                ( ktiw_getInfToTsl, 'bottom', 55 ),
                                ( ktiw_addInfBut, 'bottom', 5 ),
                                ],

                    attachControl = [( ktiw_getInfToBut, 'left', 5, ktiw_getInfFromBut ),
                                   ( ktiw_getInfFromTxt, 'top', 5, ktiw_getInfFromBut ),
                                   ( ktiw_getInfToTxt, 'top', 5, ktiw_getInfToBut ), ( ktiw_getInfToTxt, 'left', 5, ktiw_getInfFromBut ),
                                   ( ktiw_getInfFromTsl, 'top', 5, ktiw_getInfFromTxt ),
                                   ( ktiw_getInfToTsl, 'top', 5, ktiw_getInfToTxt ), ( ktiw_getInfToTsl, 'left', 3, ktiw_getInfFromBut ),
                                   ( ktiw_remInfToBut, 'left', 5, ktiw_getInfFromBut ),
                                   ( ktiw_addInfBut, 'left', 5, ktiw_getInfFromBut ),
                                   ( ktiw_remInfToBut, 'bottom', 5, ktiw_addInfBut ),
                                   ],
                    )
    cmds.window( ktiw_win, edit = True, width = 415, height = 430 )
    cmds.showWindow( 'key_addSkinInf_win' )


def batchImportNurbsWeightsBrowser( *args ):
    path = None
    root = os.path.dirname( pm.sceneName() )

    if root == '':
        # This is probably a new scene or unsaved scene file
        # give a warning and use home as the path
        path = os.environ['HOME']
        OpenMaya.MGlobal.displayWarning( 'Scene file not saved, defaulting to HOME.' )
    else:
        path = root

    fileDialog = WeightBroswer( 'key_batchImportWeightsWin', 'Batch Import Weights Window', '.txt', path, 1, 'Batch Import Weights', 4 )
    fileDialog.fileWin()


def batchExportNurbsWeightsBrowser( *args ):
    path = None
    root = os.path.dirname( pm.sceneName() )
    print( root, "WTF" )

    if root == '':
        # This is probably a new scene or unsaved scene file
        # give a warning and use home as the path
        path = os.environ['HOME']
        OpenMaya.MGlobal.displayWarning( 'Scene file not saved, defaulting to HOME.' )
    else:
        exportPath = os.path.join( root, 'WeightsNurbsBatch' )
        if not os.path.exists( exportPath ):
            path = root
        else:
            path = exportPath

    fileDialog = WeightBroswer( 'key_batchExportWeightsWin', 'Batch Export Weights Window', '.txt', path, 1, 'Batch Export Weights', 3 )
    fileDialog.fileWin()


def batchImportNurbsWeights( path ):
    print( path, '_   path' )
    if os.path.isdir( path ):
        obj = os.listdir( path )
        print( obj )
        path = os.path.join( path, obj[0] )
        print( path )
        files = os.listdir( path )
        print( files )
        for f in files:
            # account for a .ds or anyother such nonsense
            if f[0] != '.':
                # make sure this is a txt file
                print( f, '______file' )
                split = f.split( '.' )

                if split[1] == 'txt':
                    if cmds.objExists( split[0] ):
                        importNurbSurfaceWeights2( os.path.join( path, f ), split[0] )


def batchExportNurbsWeights( root, surface ):
    obj = pm.ls( surface )[0]
    print( obj, '++++++' )
    basepath = os.path.join( root, 'WeightsNurbsBatch' )
    finalpath = os.path.join( basepath, surface )

    if not os.path.exists( basepath ):
        os.mkdir( basepath )

    if not os.path.exists( finalpath ):
        os.mkdir( finalpath )

    shape = obj.getShape()

    tmp = getSkinCluster( surface )
    inf = 0
    # print tmp, 'lllllll'
    if tmp:
        skin = pm.ls( tmp )[0]
        inf = skin.getInfluence()
    else:
        print( 'noooooooooooooo skin', tmp )
    if len( inf ) > 0:
        print( inf )
        for i in inf:
            # iterate through the nodes to find the transform, cmds is faster in this case
            # pymel can be slow, so only convert them to pyNodes when it needs to be done
            print( i.__dict__ )
            if cmds.nodeType( i._name ) == 'transform':
                print( i.__dict__ )
                # Convert the nodes to pymel to get the shape and type
                pyNode = pm.ls( i )[0]
                if pyNode.getShape().type() == 'nurbsSurface':
                    obj = pyNode.name()
                    exportPath = os.path.join( finalpath, '%s.txt' % obj )
                    exportNurbsSurfaceWeights( exportPath, obj )
                else:
                    print( 'not nurbs' )
            else:
                print( 'not transform', i )
                print( cmds.nodeType( i ) )
    else:
        print( 'no inf   ', inf )


def weightingUtilWin( *args ):
    if cmds.window( 'key_weightUtil_win', exists = True ):
        cmds.deleteUI( 'key_weightUtil_win', window = True )
    cmds.window( 'key_weightUtil_win', title = 'Weighting Utility', width = 250, height = 227, sizeable = True )
    cmds.columnLayout( adjustableColumn = True, co = ['both', 10], rs = 10 )
    cmds.text( l = 'Copy/Paste Weights', height = 15 )
    cmds.button( l = 'Copy', c = 'from key_libs import key_rig_lib\nkey_rig_lib.copyWeightFromSelVtx()' )
    cmds.button( l = 'Paste', c = 'from key_libs import key_rig_lib\nkey_rig_lib.pasteWeightsFromSelectedVtx()' )
    cmds.separator()
    cmds.button( l = 'Set Copy Seam', c = 'Seamer.setVtx(1)' )
    cmds.button( l = 'Set Paste Seam', c = 'Seamer.setVtx(2),Seamer.pairVtx()' )
    cmds.button( l = 'Copy/Paste Seam', c = 'Seamer.copyPasteVtx()' )
    cmds.separator()
    cmds.radioButtonGrp( 'key_surfaceType_rbg', l = 'Surface Type:', labelArray2 = ['Polygon', 'NURBS'], numberOfRadioButtons = 2, sl = 1 )
    cmds.button( l = 'Export Weights From Selected Object', c = 'import key_rig_lib\nkey_rig_lib.exportWeightsToFile()' )
    cmds.button( l = 'Import Weights To Selected Object', c = 'import key_rig_lib\nkey_rig_lib.importWeightsFromFile()' )
    cmds.separator()
    cmds.button( l = 'Batch Export Nurbs Weights From Selected Object', c = batchExportNurbsWeightsBrowser )
    cmds.button( l = 'Batch Import Nurbs Weights', c = batchImportNurbsWeightsBrowser )
    cmds.separator()
    cmds.button( l = 'Import Weights To Selected Vertex', c = 'import key_rig_lib\nkey_rig_lib.importWeightsFromFileToVtx("True")' )
    cmds.showWindow( 'key_weightUtil_win' )
    Seamer = CopySeam()
    return Seamer


def weightingUtilWinv02():
    if pm.window( 'wtt', ex = True ):
        pm.deleteUI( 'wtt' )
    win = pm.window( 'wtt', t = 'Weight Tools v2' )  # wtt
    with win:
        mainLayout = pm.columnLayout( adj = True, rs = 5, cat = ( 'both', 5 ) )
        with mainLayout:
            # Export from selected object
            # efso_button = pm.button('Export Weights From Selected Mesh', c=pm.Callback(weightTransferControl, 'export'))
            pm.button( 'Export Weights From Selected Mesh', c = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.weightTransferControl("export")' )
            # Import to selected object
            # itso_button = pm.button('Import Weights To Selected Mesh', c=pm.Callback(weightTransferControl, 'import'))
            pm.button( 'Import Weights To Selected Mesh', c = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.weightTransferControl("import")' )
            cmds.separator()
            # cmds.button(l='Batch Export Nurbs Weights From Selected Mesh', c=pm.Callback(batchNurbsWeightControl, 'export'))
            cmds.button( l = 'Batch Export Nurbs Weights From Selected Mesh', c = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.batchNurbsWeightControl("export")' )
            # cmds.button(l='Batch Import Nurbs Weights To Selected Mesh', c=pm.Callback(batchNurbsWeightControl, 'import'))
            cmds.button( l = 'Batch Import Nurbs Weights To Selected Mesh', c = 'import webrImport as web\nkrl = web.mod("key_rig_lib")\nkrl.batchNurbsWeightControl("import")' )


def matchSkinInfs( source = 'skinCluster15', dest = 'skinCluster16', bind = False ):
    skinS = source
    skinD = dest
    joints = []
    nurbs = []
    inf = cmds.skinCluster( skinS, q = True, inf = True )
    infD = cmds.skinCluster( skinD, q = True, inf = True )
    for item in inf:
        if item not in infD:
            if cmds.nodeType( item ) == 'joint':
                joints.append( item )
            else:
                nurbs.append( item )
    # for item in joints:
    if joints:
        cmds.skinCluster( skinD, edit = True, ai = joints, tsb = True, lw = True, wt = 0.0 )
    # for item in nurbs:
    if nurbs:
        cmds.skinCluster( skinD, edit = True, ai = nurbs, ns = 10, dropoffRate = 4.0, ug = True, lw = True, wt = 0.0 )
