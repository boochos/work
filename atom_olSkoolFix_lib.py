from __future__ import with_statement

import pickle

from pymel.core import *

import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

# web
place = web.mod( 'atom_place_lib' )
# import atom_miscellaneous_lib as aml


def lockCT( *args ):
    '''\n
    Locks unused attrs on face rig controls
    '''
    lockAll = ['cheeks_10x', 'cheeks_11x', 'cheeks_12x', 'cheeks_13x', 'cheeks_14x', 'cheeks_15x', 'cheeks_16x', 'cheeks_17x', 'cheeks_18x',
               'cheeks_19x', 'cheeks_1x', 'cheeks_2x', 'cheeks_3x', 'cheeks_4x', 'cheeks_5x', 'cheeks_6x', 'cheeks_7x', 'cheeks_8x', 'cheeks_9x',
               'Dn_lip', 'Dn_lip_10x', 'Dn_lip_11x', 'Dn_lip_12x', 'Dn_lip_13x', 'Dn_lip_14x', 'Dn_lip_15x', 'Dn_lip_3x', 'Dn_lip_4x', 'Dn_lip_5x',
               'Dn_lip_6x', 'Dn_lip_7x', 'Dn_lip_8x', 'Dn_lip_9x', 'DnMd_lip', 'eyes', 'jaw', 'jawSwivel', 'jawTrans', 'Lf_brow', 'Lf_cheek', 'Lf_eye_1x',
               'Lf_eye_2x', 'Lf_eye_3x', 'Lf_eye_4x', 'Lf_eye_5x', 'Lf_eye_6x', 'Lf_eye_7x', 'Lf_eye_8x', 'Lf_eyeBall', 'Lf_eyeFK', 'Lf_eyeFKAim', 'Lf_lids',
               'Lf_lip', 'Lf_snarl', 'LfDn_brow', 'LfDn_cheek', 'LfDn_lid', 'LfDn_lid_3x', 'LfDn_lid_4x', 'LfDn_lid_5x', 'LfDn_lip', 'LfDnFt_cheek', 'LfDnFt_lip',
               'LfMd_cheek', 'LfUp_brow', 'LfUp_cheek', 'LfUp_lid', 'LfUp_lid_2x', 'LfUp_lid_3x', 'LfUp_lid_4x', 'LfUp_lid_5x', 'LfUp_lid_6x', 'LfUp_lip',
               'LfUpBk_cheek', 'LfUpBk_lip', 'LfUpFt_cheek', 'LfUpFt_lip', 'muzzle', 'nose', 'Rt_brow', 'Rt_cheek', 'Rt_eye_1x', 'Rt_eye_2x',
               'Rt_eye_3x', 'Rt_eye_4x', 'Rt_eye_5x', 'Rt_eye_6x', 'Rt_eye_7x', 'Rt_eye_8x', 'Rt_eyeBall', 'Rt_eyeFK', 'Rt_eyeFKAim',
               'Rt_lids', 'Rt_lip', 'Rt_snarl', 'RtDn_brow', 'RtDn_cheek', 'RtDn_lid', 'RtDn_lid_3x', 'RtDn_lid_4x', 'RtDn_lid_5x', 'RtDn_lip',
               'RtDnFt_cheek', 'RtDnFt_lip', 'RtMd_cheek', 'RtUp_brow', 'RtUp_cheek', 'RtUp_lid', 'RtUp_lid_2x', 'RtUp_lid_3x', 'RtUp_lid_4x',
               'RtUp_lid_5x', 'RtUp_lid_6x', 'RtUp_lip', 'RtUpBk_cheek', 'RtUpBk_lip', 'RtUpFt_cheek', 'RtUpFt_lip', 'skull', 'tongue_1x',
               'tongue_2x', 'tongue_3x', 'tongue_4x', 'tongue_5x', 'tongue_6x', 'tongue_7x', 'tongue_8x', 'Up_lip', 'Up_lip_10x', 'Up_lip_11x',
               'Up_lip_12x', 'Up_lip_13x', 'Up_lip_14x', 'Up_lip_15x', 'Up_lip_16x', 'Up_lip_2x', 'Up_lip_3x', 'Up_lip_4x', 'Up_lip_5x', 'Up_lip_6x',
               'Up_lip_7x', 'Up_lip_8x', 'Up_lip_9x', 'UpMd_lip']

    for ct in lockAll:
        cmds.setAttr( ct + '.translateX', l = True, k = False )
        cmds.setAttr( ct + '.translateY', l = True, k = False )
        cmds.setAttr( ct + '.translateZ', l = True, k = False )
        cmds.setAttr( ct + '.rotateX', l = True, k = False )
        cmds.setAttr( ct + '.rotateY', l = True, k = False )
        cmds.setAttr( ct + '.rotateZ', l = True, k = False )
        cmds.setAttr( ct + '.scaleX', l = True, k = False )
        cmds.setAttr( ct + '.scaleY', l = True, k = False )
        cmds.setAttr( ct + '.scaleZ', l = True, k = False )
        cmds.setAttr( ct + '.visibility', l = True, k = False )

    # TX
    txList = [u'Lf_brow', u'Rt_brow', u'muzzle']
    for ct in txList:
        cmds.setAttr( ct + '.translateX', l = False, k = True )

    # TY
    tyList = [u'Lf_brow', u'Rt_brow', u'LfUpBk_lip', u'Lf_cheek', u'RtUpBk_lip', u'Rt_cheek', u'Lf_snarl', u'Rt_snarl', u'muzzle', u'jawTrans']
    for ct in tyList:
        cmds.setAttr( ct + '.translateY', l = False, k = True )

    # TZ
    tzList = [u'LfUpBk_lip', u'Lf_cheek', u'RtUpBk_lip', u'Rt_cheek']
    for ct in tzList:
        cmds.setAttr( ct + '.translateZ', l = False, k = True )

    # RX
    rxList = [u'Up_lip', u'Dn_lip']
    for ct in rxList:
        cmds.setAttr( ct + '.rotateX', l = False, k = True )

    # RZ
    rzList = [u'Lf_brow', u'Rt_brow']
    for ct in rzList:
        cmds.setAttr( ct + '.rotateZ', l = False, k = True )

    # ROT
    rotList = [u'Lf_eyeBall', u'Rt_eyeBall', u'Lf_eyeFK', u'Rt_eyeFK', u'LfDn_lid', u'LfUp_lid', u'Lf_lids', u'RtDn_lid', u'Rt_lids',
               u'RtUp_lid', u'eyes', u'jaw', u'skull']
    for ct in rotList:
        cmds.setAttr( ct + '.rotateX', l = False, k = True )
        cmds.setAttr( ct + '.rotateY', l = False, k = True )
        cmds.setAttr( ct + '.rotateZ', l = False, k = True )

    # SCALE
    scaleList = [u'Lf_eyeBall', u'Rt_eyeBall', u'LfDn_lid', u'LfUp_lid', u'Lf_lids', u'RtDn_lid', u'Rt_lids', u'RtUp_lid', u'eyes', u'skull', 'jaw']
    for ct in scaleList:
        cmds.setAttr( ct + '.scaleX', l = False, k = True )
        cmds.setAttr( ct + '.scaleY', l = False, k = True )
        cmds.setAttr( ct + '.scaleZ', l = False, k = True )

    # TRANS
    transList = [u'Lf_eyeBall', u'Rt_eyeBall', u'LfDn_lid', u'LfUp_lid', u'Lf_lids', u'RtDn_lid', u'Rt_lids', u'RtUp_lid', u'Lf_eyeFKAim',
                 u'Rt_eyeFKAim', u'eyes', u'Up_lip', u'Dn_lip', u'jaw', u'skull']
    for ct in transList:
        cmds.setAttr( ct + '.translateX', l = False, k = True )
        cmds.setAttr( ct + '.translateY', l = False, k = True )
        cmds.setAttr( ct + '.translateZ', l = False, k = True )

    macros = ['DnMd_lip', 'Lf_lip', 'LfDn_brow', 'LfDn_cheek', 'LfDn_lip', 'LfDnFt_cheek', 'LfDnFt_lip', 'LfMd_cheek', 'LfUp_brow', 'LfUp_cheek',
              'LfUp_lip', 'LfUpBk_cheek', 'LfUpFt_cheek', 'LfUpFt_lip', 'nose', 'Rt_lip', 'RtDn_brow', 'RtDn_cheek', 'RtDn_lip', 'RtDnFt_cheek',
              'RtDnFt_lip', 'RtMd_cheek', 'RtUp_brow', 'RtUp_cheek', 'RtUp_lip', 'RtUpBk_cheek', 'RtUpFt_cheek', 'RtUpFt_lip', 'UpMd_lip']
    for ct in macros:
        cmds.setAttr( ct + '.translateX', l = False, k = True )
        cmds.setAttr( ct + '.translateY', l = False, k = True )
        cmds.setAttr( ct + '.translateZ', l = False, k = True )
        cmds.setAttr( ct + '.rotateX', l = False, k = True )
        cmds.setAttr( ct + '.rotateY', l = False, k = True )
        cmds.setAttr( ct + '.rotateZ', l = False, k = True )
        cmds.setAttr( ct + '.scaleX', l = False, k = True )
        cmds.setAttr( ct + '.scaleY', l = False, k = True )
        cmds.setAttr( ct + '.scaleZ', l = False, k = True )

    micros = ['cheeks_10x', 'cheeks_11x', 'cheeks_12x', 'cheeks_13x', 'cheeks_14x', 'cheeks_15x', 'cheeks_16x', 'cheeks_17x', 'cheeks_18x',
              'cheeks_19x', 'cheeks_1x', 'cheeks_2x', 'cheeks_3x', 'cheeks_4x', 'cheeks_5x', 'cheeks_6x', 'cheeks_7x', 'cheeks_8x', 'cheeks_9x',
              'Dn_lip_10x', 'Dn_lip_11x', 'Dn_lip_12x', 'Dn_lip_13x', 'Dn_lip_14x', 'Dn_lip_15x', 'Dn_lip_3x', 'Dn_lip_4x', 'Dn_lip_5x',
              'Dn_lip_6x', 'Dn_lip_7x', 'Dn_lip_8x', 'Dn_lip_9x', 'Up_lip_10x', 'Up_lip_11x', 'Up_lip_12x', 'Up_lip_13x', 'Up_lip_14x',
              'Up_lip_15x', 'Up_lip_16x', 'Up_lip_2x', 'Up_lip_3x', 'Up_lip_4x', 'Up_lip_5x', 'Up_lip_6x', 'Up_lip_7x', 'Up_lip_8x', 'Up_lip_9x',
              'Lf_eye_1x', 'Lf_eye_2x', 'Lf_eye_3x', 'Lf_eye_4x', 'Lf_eye_5x', 'Lf_eye_6x', 'Lf_eye_7x', 'Lf_eye_8x', 'LfDn_lid_3x', 'LfDn_lid_4x',
              'LfDn_lid_5x', 'LfUp_lid_2x', 'LfUp_lid_3x', 'LfUp_lid_4x', 'LfUp_lid_5x', 'LfUp_lid_6x', 'Rt_eye_1x', 'Rt_eye_2x', 'Rt_eye_3x', 'Rt_eye_4x',
              'Rt_eye_5x', 'Rt_eye_6x', 'Rt_eye_7x', 'Rt_eye_8x', 'RtDn_lid_3x', 'RtDn_lid_4x', 'RtDn_lid_5x', 'RtUp_lid_2x', 'RtUp_lid_3x', 'RtUp_lid_4x',
              'RtUp_lid_5x', 'RtUp_lid_6x']
    for ct in micros:
        cmds.setAttr( ct + '.translateX', l = False, k = True )
        cmds.setAttr( ct + '.translateY', l = False, k = True )
        cmds.setAttr( ct + '.translateZ', l = False, k = True )


class OldSkooInfoLayout( object ):

    def __init__( self, prefix, button_label, command ):
        self.prefix = prefix
        self.buttonLabel = button_label
        self.command = command
        self.mainLayout = None
        self.weightPath = None
        self.buildFilePath()
        self.buildLayout()

    def buildFilePath( self ):
        scnName = sceneName()
        if len( scnName ) != 0:
            # look for RIG in the path
            # find RIG in the path
            rigIdx = scnName.rfind( 'RIG' )
            if rigIdx > 0:
                basePath = scnName[:rigIdx + 4]
                baseName = os.path.basename( scnName )
                idx = baseName.rfind( '.' )
                name = baseName[:idx] + '.osfw'
                dirPath = os.path.join( basePath, 'oldSkooFaceWeights' )
                if not os.path.exists( dirPath ):
                    os.mkdir( dirPath )
                self.weightPath = os.path.join( dirPath, name )

    def buildLayout( self ):
        self.mainLayout = formLayout( self.prefix + 'FormLayout' )
        with self.mainLayout:
            exTxtFld = textField( self.prefix + 'textField', tx = self.weightPath )
            exBtn = button( self.prefix + 'exportButton', l = self.buttonLabel, c = Callback( self.command, self.weightPath ) )

            formLayout( self.mainLayout, edit = True,
                       attachForm = [( exTxtFld, 'left', 5 ), ( exTxtFld, 'top', 5 ), ( exTxtFld, 'right', 5 ),
                                   ( exBtn, 'left', 5 ), ( exBtn, 'right', 5 )],
                       attachControl = [( exBtn, 'top', 5, exTxtFld )] )

            setFocus( exTxtFld )


class OldSkooPointInfo( object ):

    def __init__( self, point ):
        self.name = point
        self.pos = cmds.xform( self.name, q = True, ws = True, t = True )
        self.tx = self.pos[0]
        self.ty = self.pos[1]
        self.tz = self.pos[2]


class OldSkooFaceInfo( object ):

    def __init__( self, faceDriver_Crv = 'faceDriver_Crv' ):

        self.microList = ['Up_lip_2x', 'Up_lip_3x', 'Up_lip_4x', 'Up_lip_5x', 'Up_lip_6x', 'Up_lip_7x', 'Up_lip_8x', 'Up_lip_9x',
                          'Up_lip_10x', 'Up_lip_11x', 'Up_lip_12x', 'Up_lip_13x', 'Up_lip_14x', 'Up_lip_15x', 'Up_lip_16x', 'Dn_lip_3x',
                          'Dn_lip_4x', 'Dn_lip_5x', 'Dn_lip_6x', 'Dn_lip_7x', 'Dn_lip_8x', 'Dn_lip_9x', 'Dn_lip_10x', 'Dn_lip_11x', 'Dn_lip_12x',
                          'Dn_lip_13x', 'Dn_lip_14x', 'Dn_lip_15x', 'cheeks_1x', 'cheeks_2x', 'cheeks_3x', 'cheeks_4x', 'cheeks_5x', 'cheeks_6x',
                          'cheeks_7x', 'cheeks_8x', 'cheeks_9x', 'cheeks_10x', 'cheeks_11x', 'cheeks_12x', 'cheeks_13x', 'cheeks_14x', 'cheeks_15x',
                          'cheeks_16x', 'cheeks_17x', 'cheeks_18x', 'cheeks_19x', 'Lf_eye_1x', 'Lf_eye_2x', 'Lf_eye_3x', 'Lf_eye_4x', 'Lf_eye_5x',
                          'Lf_eye_6x', 'Lf_eye_7x', 'Lf_eye_8x', 'Rt_eye_1x', 'Rt_eye_2x', 'Rt_eye_3x', 'Rt_eye_4x', 'Rt_eye_5x', 'Rt_eye_6x',
                          'Rt_eye_7x', 'Rt_eye_8x', 'Up_lipLft_2x', 'Up_lipLft_3x', 'Up_lipLft_4x', 'Up_lipLft_5x', 'Up_lipLft_6x', 'Up_lipLft_7x', 'Up_lipLft_8x',
                          'Up_lipLft_9x', 'Up_lipLft_10x', 'Up_lipLft_11x', 'Up_lipLft_12x', 'Up_lipLft_13x', 'Up_lipLft_14x', 'Up_lipLft_15x', 'Up_lipLft_16x',
                          'Dn_lipLft_3x', 'Dn_lipLft_4x', 'Dn_lipLft_5x', 'Dn_lipLft_6x', 'Dn_lipLft_7x', 'Dn_lipLft_8x', 'Dn_lipLft_9x', 'Dn_lipLft_10x', 'Dn_lipLft_11x',
                          'Dn_lipLft_12x', 'Dn_lipLft_13x', 'Dn_lipLft_14x', 'Dn_lipLft_15x', 'cheeksLft_1x', 'cheeksLft_2x', 'cheeksLft_3x', 'cheeksLft_4x',
                          'cheeksLft_5x', 'cheeksLft_6x', 'cheeksLft_7x', 'cheeksLft_8x', 'cheeksLft_9x', 'cheeksLft_10x', 'cheeksLft_11x', 'cheeksLft_12x',
                          'cheeksLft_13x', 'cheeksLft_14x', 'cheeksLft_15x', 'cheeksLft_16x', 'cheeksLft_17x', 'cheeksLft_18x', 'cheeksLft_19x']
        '''
        self.meshList             = ['Up_lipLoft_msh','cheekLoft_msh','Dn_lipLoft_msh','Lf_eyeLoft_msh','Rt_eyeLoft_msh',
                                     'LfUp_eyeLidLoft_msh','LfDn_eyeLidLoft_msh','RtUp_eyeLidLoft_msh','RtDn_eyeLidLoft_msh']
        
        self.curveList            = ['Up_lip_Crv','Dn_lip_Crv','cheeks_Crv','Up_lipLft_Crv','Dn_lipLft_Crv','cheeksLft_Crv',
                                     'Rt_eye','Lf_eye']
        '''
        self.faceDriver_Crv = faceDriver_Crv
        self.skinCluster = cmds.ls( cmds.listHistory( faceDriver_Crv ), type = 'skinCluster' )[0]
        self.cvList = []
        self.cvCnt = cmds.getAttr( self.faceDriver_Crv + '.spans' )
        self.influenceDict = None
        self.influenceInfoDict = {}
        self.createCvList()

    def createCvList( self ):
        cvStr = self.faceDriver_Crv + '.cv'
        for i in range( 0, self.cvCnt, 1 ):
            fullCvStr = cvStr + '[%d]' % i
            self.cvList.append( OldSkooPointInfo( fullCvStr ) )


def getMapPnt( anchorList, cv, printInfo = False ):
    closestPoint = None
    closestObj = None
    distance = 1e10

    for mic in anchorList:
        getDistance = place.distance2Pts( cv.pos, cmds.xform( mic, q = True, ws = True, t = True ) )
        if getDistance < distance:
            distance = getDistance
            closestPoint = mic
    '''
    for geo in OldSkooObj.meshList:
        #Iterate through each vtx on the geo
        verts = cmds.ls(cmds.polyListComponentConversion(geo, toVertex=True), fl=True)
        for i, vert in enumerate(verts):
            getDistance = place.distance2Pts(cv.pos, cmds.xform(vert,q=True, ws=True, t=True))
            if getDistance < distance:
                distance     = getDistance
                closestPoint = vert
                closestObj   = geo
                
    if distance > .005:
        for crv in OldSkooObj.curveList:
            points = cmds.getAttr(crv + '.spans')
            for i in range(0,points,1):
                cvStr       = crv + '.cv[%d]' % i
                getDistance = place.distance2Pts(cv.pos, cmds.xform(cvStr, q=True, ws=True, t=True))
                if getDistance < distance:
                    distance     = getDistance
                    closestPoint = cvStr
                    closestObj   = i  
                    '''
    if printInfo:
        print( '%s, %s' % ( closestPoint, distance ) )

    return closestPoint, distance


def OldSkooFaceRigWeightExportCMD( OldSkooObj ):
    # Interate through each CV on the faceDriver_Crv
    for cv in OldSkooObj.cvList:
        infLst = cmds.skinPercent( OldSkooObj.skinCluster, cv.name, ib = 1e-4, query = True, transform = None )
        wgtLst = cmds.skinPercent( OldSkooObj.skinCluster, cv.name, ib = 1e-4, query = True, v = True )
        closestPoint = getMapPnt( OldSkooObj.microList, cv )
        # Some debugging info
        # if OldSkooObj.influenceInfoDict.has_key(closestPoint[0]):
        #    print 'Key Exists %s, for %s, %s' %( closestPoint[0], cv.name,closestPoint[1])
        #    print infLst, wgtLst
        OldSkooObj.influenceInfoDict[closestPoint[0]] = [infLst, wgtLst]


def oldSkooFaceRigWeightExport( path ):
    # By default the face driver curve is used and the skinCluster is extracted
    Export_Info = OldSkooFaceInfo()
    exportInfList = cmds.skinCluster( Export_Info.skinCluster, query = True, inf = True )

    infDict = {}
    for i, inf in enumerate( exportInfList ):
        infDict[inf] = i

    OldSkooFaceRigWeightExportCMD( Export_Info )
    Export_Info.influenceDict = infDict
    exportFile = open( path, 'w' )
    export_pickle = pickle.dump( Export_Info, exportFile )
    exportFile.close()


def oldSkooFaceRigWeightImport( path ):

    pickleFile = open( path, 'r' )
    Import_Info = pickle.load( pickleFile )
    pickleFile.close()
    sknClstr = Import_Info.skinCluster
    cmds.setAttr( sknClstr + '.normalizeWeights', 0 )
    points = cmds.getAttr( 'faceDriver_Crv.spans' )
    # Iterate through each point on the faceDriver_Crv
    for i in range( 0, points, 1 ):
        cv = OldSkooPointInfo( 'faceDriver_Crv.cv[' + str( i ) + ']' )
        closestPoint = getMapPnt( Import_Info.influenceInfoDict.keys(), cv )
        if Import_Info.influenceInfoDict.has_key( closestPoint[0] ):
            setInfList = Import_Info.influenceInfoDict[closestPoint[0]][0]
            setWgtList = Import_Info.influenceInfoDict[closestPoint[0]][1]

            infLst = cmds.skinPercent( sknClstr, cv.name, ib = 1e-4, query = True, transform = None )
            # Set the weights to 0
            for i in infLst:
                cmds.skinPercent( sknClstr, cv.name, tv = [i, 0] )

            for i, inf in enumerate( setInfList ):
                cmds.skinPercent( sknClstr, cv.name, tv = [inf, setWgtList[i]] )
        else:
            print( '-- point missed: %s, closest point: %s' % ( cv.name, closestPoint[0] ) )
    cmds.setAttr( sknClstr + '.normalizeWeights', 1 )

# trasferOldSkoo wieghtInfo = toswi


def oldSkooFaceWeightWin( *args ):
    winName = 'toswi_main_window'
    ctlPrfx = 'toswi_'
    if window( winName, ex = True ):
        deleteUI( winName )

    mainWin = window( 'toswi_main_window', t = 'Old Skoo Weight Transfer' )
    with mainWin:
        mainForm = formLayout( ctlPrfx + 'mainformLayout', numberOfDivisions = 100 )
        with mainForm:
            exportForm = OldSkooInfoLayout( ctlPrfx + 'export_', 'E X P O R T', oldSkooFaceRigWeightExport ).mainLayout
            importForm = OldSkooInfoLayout( ctlPrfx + 'import_', 'I M P O R T', oldSkooFaceRigWeightImport ).mainLayout

            sep = separator()
            formLayout( mainForm, edit = True,
                       attachForm = [( exportForm, 'left', 5 ), ( exportForm, 'top', 5 ), ( exportForm, 'right', 5 ),
                                   ( sep, 'left', 10 ), ( sep, 'right', 10 ),
                                   ( importForm, 'left', 5 ), ( importForm, 'right', 5 )],

                       attachControl = [( sep, 'top', 15, exportForm ), ( importForm, 'top', 10, sep )]
                       )
            setFocus( mainForm )
