import os

import createWrap as cw
import maya.cmds as cmds
import webrImport as web

#
# web
place = web.mod( 'atom_place_lib' )
# misc = web.mod('atom_miscellaneous_lib')
appendage = web.mod( 'atom_appendage_lib' )
misc = web.mod( 'atom_miscellaneous_lib' )
stage = web.mod( 'atom_splineStage_lib' )
sfk = web.mod( 'atom_splineFk_lib' )
aul = web.mod( 'atom_ui_lib' )
anm = web.mod( "anim_lib" )
krl = web.mod( "key_rig_lib" )


def dragonfly( wingSplines = False ):
    # creates groups and master controller from arguments specified as 'True'
    place.rigPrebuild( Top = 0, Ctrl = True, SknJnts = True, Geo = True, World = True, Master = True, OlSkool = True, Size = 22 )

    # lists for joints and controllers
    endJntL = [
    'legA_08_jnt_L',
    'legB_06_jnt_L',
    'legC_06_jnt_L'
    ]
    endJntR = [
    'legA_08_jnt_R',
    'legB_06_jnt_R',
    'legC_06_jnt_R'
    ]
    kneeJntL = [
    'legA_07_jnt_L',
    'legB_05_jnt_L',
    'legC_05_jnt_L'
    ]
    kneeJntR = [
    'legA_07_jnt_R',
    'legB_05_jnt_R',
    'legC_05_jnt_R'
    ]
    legJntL = [
    'legA_06_jnt_L',
    'legB_04_jnt_L',
    'legC_04_jnt_L'
    ]
    legJntR = [
    'legA_06_jnt_R',
    'legB_04_jnt_R',
    'legC_04_jnt_R'
    ]

    legIkTopL = [
    'legA_06_jnt_L',
    'legB_03_jnt_L',
    'legC_02_jnt_L'
    ]
    legIkTopR = [
    'legA_06_jnt_R',
    'legB_03_jnt_R',
    'legC_02_jnt_R'
    ]

    btmCtrl_L = [
    'legA_08_ct_L',
    'legB_06_ct_L',
    'legC_06_ct_L'
    ]
    btmCtrl_R = [
    'legA_08_ct_R',
    'legB_06_ct_R',
    'legC_06_ct_R'
    ]

    topCtrl_L = [
    'legA_06_ct_L',
    'legB_04_ct_L',
    'legC_04_ct_L'
    ]
    topCtrl_R = [
    'legA_06_ct_R',
    'legB_04_ct_R',
    'legC_04_ct_R'
    ]

    pvNamesL = [
    'legA_pv_07_ct_L',
    'legB_pv_05_ct_L',
    'legC_pv_05_ct_L'
    ]
    pvNamesR = [
    'legA_pv_07_ct_R',
    'legB_pv_05_ct_R',
    'legC_pv_05_ct_R'
    ]
    ikNamesL = [
    'legA_08_ik_L',
    'legB_06_ik_L',
    'legC_06_ik_L'
    ]
    ikNamesR = [
    'legA_08_ik_R',
    'legB_06_ik_R',
    'legC_06_ik_R'
    ]
    legParents = [
    'root_thorax_jnt',
    'root_thorax_jnt',
    'root_thorax_jnt'
    ]
    geo_grp = 'dragonfly_grp'
    geo = 'dragonfly_grp|Dragonfly_body'
    cmds.deltaMush( geo, smoothingIterations = 26, smoothingStep = 0.5, pinBorderVertices = 1, envelope = 1 )
    # creates rig controllers, places in appropriate groups and constrains to the master_grp

    # Create COG Controller and clean up
    cog = 'Cog'
    cnt = place.Controller( cog, 'root_thorax_jnt', orient = False, shape = 'facetZup_ctrl', size = 3.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
    cmds.parentConstraint( cntCt[4], 'root_thorax_jnt', mo = True )

    winga = 'WingA'
    wnga = place.Controller( winga, 'wingA_jnt', orient = False, shape = 'arrow_ctrl', size = 1.25, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    wngaCt = wnga.createController()
    place.cleanUp( wngaCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], wngaCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngaCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngaCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    winga_l = 'WingA_L'
    wnga_l = place.Controller( winga_l, 'wingA_00_jnt_L', orient = True, shape = 'arrow_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
    wnga_lCt = wnga_l.createController()
    place.cleanUp( wnga_lCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngaCt[4], wnga_lCt[0], mo = True )
    cmds.parentConstraint( wnga_lCt[4], 'wingA_00_jnt_L', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wnga_lCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wnga_lCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    '''
    # wingA_L bend
    place.optEnum( wnga_lCt[2], attr = 'bend', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings1' )
    wbend = cmds.nonLinear( type = 'bend', name = 'wingA_Bend_L', curvature = 0.0, lowBound = 0.0, highBound = 2.0 )
    cmds.select( wbend[1], 'wingA_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wbend[1], 'wingA_01_jnt_L' )
    cmds.setAttr( wbend[1] + '.rotateX', 90 )  # [1] handle # [0] deformer
    cmds.setAttr( wbend[1] + '.rotateZ', 90 )
    place.hijackAttrs( wbend[1], wnga_lCt[2], 'translateZ', 'bendSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wbend[0] + 'HandleShape', wnga_lCt[2], 'curvature', 'bendCurvature', set = False, default = 0, force = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wbend[1], [False, False], [False, False], [True, False], [False, False, False] )
    # wingA_L twist
    place.optEnum( wnga_lCt[2], attr = 'twist', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings1' )
    wtwist = cmds.nonLinear( type = 'twist', name = 'wingA_Twist_L', lowBound = 0.0, highBound = 2.0 )
    cmds.select( wtwist[1], 'wingA_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wtwist[1], 'wingA_01_jnt_L' )
    cmds.setAttr( wtwist[1] + '.rotateX', 90 )
    cmds.setAttr( wtwist[1] + '.rotateZ', -90 )
    place.hijackAttrs( wtwist[1], wnga_lCt[2], 'translateZ', 'twistSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_lCt[2], 'highBound', 'twistBound', set = False, default = 2, force = True )
    cmds.setAttr( wnga_lCt[2] + '.twistBound', k = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_lCt[2], 'endAngle', 'twistAngle', set = False, default = 0, force = True )
    cmds.setAttr( wnga_lCt[2] + '.twistAngle', k = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wtwist[1], [False, False], [False, False], [True, False], [False, False, False] )
    '''

    winga_r = 'WingA_R'
    wnga_r = place.Controller( winga_r, 'wingA_00_jnt_R', orient = True, shape = 'arrow_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'red' )
    wnga_rCt = wnga_r.createController()
    place.cleanUp( wnga_rCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngaCt[4], wnga_rCt[0], mo = True )
    cmds.parentConstraint( wnga_rCt[4], 'wingA_00_jnt_R', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wnga_rCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wnga_rCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    '''
    # wingA_R bend
    cmds.select( 'wingA_01_jnt_R' )
    null = place.null( 'wingA_scaleGrp_R' )[0]
    cmds.parent( null, 'wingA_01_jnt_R' )
    cmds.setAttr( null + '.scaleZ', -1 )
    #
    place.optEnum( wnga_rCt[2], attr = 'bend', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings' )
    wbend = cmds.nonLinear( type = 'bend', name = 'wingA_Bend_R', curvature = 0.0, lowBound = 0.0, highBound = 2.0 )
    cmds.select( wbend[1], 'wingA_01_jnt_R' )
    anm.matchObj()
    cmds.parent( wbend[1], null )
    cmds.setAttr( wbend[1] + '.rotateX', 90 )  # [1] handle # [0] deformer
    cmds.setAttr( wbend[1] + '.rotateZ', -90 )
    place.hijackAttrs( wbend[1], wnga_rCt[2], 'translateZ', 'bendSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wbend[0] + 'HandleShape', wnga_rCt[2], 'curvature', 'bendCurvature', set = False, default = 0, force = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wbend[1], [False, False], [False, False], [True, False], [False, False, False] )

    # wingA_R twist
    place.optEnum( wnga_rCt[2], attr = 'twist', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_forewings' )
    wtwist = cmds.nonLinear( type = 'twist', name = 'wingA_Twist_R', lowBound = 0.0, highBound = 2.0 )
    cmds.select( wtwist[1], 'wingA_01_jnt_R' )
    anm.matchObj()
    cmds.parent( wtwist[1], null )
    cmds.setAttr( wtwist[1] + '.rotateX', 90 )
    # cmds.setAttr( wtwist[1] + '.rotateZ', -90 )
    cmds.setAttr( wtwist[1] + '.scaleZ', cmds.getAttr( wtwist[1] + '.scaleZ' ) * -1 )
    place.hijackAttrs( wtwist[1], wnga_rCt[2], 'translateZ', 'twistSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_rCt[2], 'highBound', 'twistBound', set = False, default = 2, force = True )
    cmds.setAttr( wnga_rCt[2] + '.twistBound', k = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wnga_rCt[2], 'endAngle', 'twistAngle', set = False, default = 0, force = True )
    cmds.setAttr( wnga_rCt[2] + '.twistAngle', k = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wtwist[1], [False, False], [False, False], [True, False], [False, False, False] )
    '''

    # return None
    wingb = 'WingB'
    wngb = place.Controller( wingb, 'wingB_jnt', orient = False, shape = 'arrow_ctrl', size = 1.25, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    wngbCt = wngb.createController()
    place.cleanUp( wngbCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], wngbCt[0], mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngbCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngbCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    wingb_l = 'WingB_L'
    wngb_l = place.Controller( wingb_l, 'wingB_00_jnt_L', orient = True, shape = 'arrow_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
    wngb_lCt = wngb_l.createController()
    place.cleanUp( wngb_lCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngbCt[4], wngb_lCt[0], mo = True )
    cmds.parentConstraint( wngb_lCt[4], 'wingB_00_jnt_L', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngb_lCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngb_lCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    '''
    # wingB_L bend
    place.optEnum( wngb_lCt[2], attr = 'bend', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_hindwings1' )
    wbend = cmds.nonLinear( type = 'bend', name = 'wingB_Bend_L', curvature = 0.0, lowBound = 0.0, highBound = 2.0 )
    cmds.select( wbend[1], 'wingB_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wbend[1], 'wingB_01_jnt_L' )
    cmds.setAttr( wbend[1] + '.rotateX', 90 )  # [1] handle # [0] deformer
    cmds.setAttr( wbend[1] + '.rotateZ', 90 )
    place.hijackAttrs( wbend[1], wngb_lCt[2], 'translateZ', 'bendSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wbend[0] + 'HandleShape', wngb_lCt[2], 'curvature', 'bendCurvature', set = False, default = 0, force = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wbend[1], [False, False], [False, False], [True, False], [False, False, False] )

    # wingB_L twist
    place.optEnum( wngb_lCt[2], attr = 'twist', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_hindwings1' )
    wtwist = cmds.nonLinear( type = 'twist', name = 'wingB_Twist_L', lowBound = 0.0, highBound = 2.0 )
    cmds.select( wtwist[1], 'wingB_01_jnt_L' )
    anm.matchObj()
    cmds.parent( wtwist[1], 'wingB_01_jnt_L' )
    cmds.setAttr( wtwist[1] + '.rotateX', 90 )
    cmds.setAttr( wtwist[1] + '.rotateZ', -90 )
    place.hijackAttrs( wtwist[1], wngb_lCt[2], 'translateZ', 'twistSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wngb_lCt[2], 'highBound', 'twistBound', set = False, default = 2, force = True )
    cmds.setAttr( wngb_lCt[2] + '.twistBound', k = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wngb_lCt[2], 'endAngle', 'twistAngle', set = False, default = 0, force = True )
    cmds.setAttr( wngb_lCt[2] + '.twistAngle', k = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wtwist[1], [False, False], [False, False], [True, False], [False, False, False] )
    '''

    wingb_r = 'WingB_R'
    wngb_r = place.Controller( wingb_r, 'wingB_00_jnt_R', orient = True, shape = 'arrow_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True , colorName = 'red' )
    wngb_rCt = wngb_r.createController()
    place.cleanUp( wngb_rCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( wngbCt[4], wngb_rCt[0], mo = True )
    cmds.parentConstraint( wngb_rCt[4], 'wingB_00_jnt_R', mo = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wngb_rCt[2], [False, False], [False, True], [True, False], [True, False, False] )
    place.setChannels( wngb_rCt[3], [False, False], [False, True], [True, False], [True, False, False] )

    '''
    # wingB_R bend
    cmds.select( 'wingB_01_jnt_R' )
    null = place.null( 'wingB_scaleGrp_R' )[0]
    cmds.parent( null, 'wingB_01_jnt_R' )
    cmds.setAttr( null + '.scaleZ', -1 )
    #
    place.optEnum( wngb_rCt[2], attr = 'bend', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_hindwings' )
    wbend = cmds.nonLinear( type = 'bend', name = 'wingB_Bend_R', curvature = 0.0, lowBound = 0.0, highBound = 2.0 )
    cmds.select( wbend[1], 'wingB_01_jnt_R' )
    anm.matchObj()
    cmds.parent( wbend[1], null )
    cmds.setAttr( wbend[1] + '.rotateX', 90 )  # [1] handle # [0] deformer
    cmds.setAttr( wbend[1] + '.rotateZ', -90 )
    place.hijackAttrs( wbend[1], wngb_rCt[2], 'translateZ', 'bendSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wbend[0] + 'HandleShape', wngb_rCt[2], 'curvature', 'bendCurvature', set = False, default = 0, force = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wbend[1], [False, False], [False, False], [True, False], [False, False, False] )

    # wingB_R twist
    place.optEnum( wngb_rCt[2], attr = 'twist', enum = 'DFRMR' )
    cmds.select( 'Dragonfly_hindwings' )
    wtwist = cmds.nonLinear( type = 'twist', name = 'wingB_Twist_R', lowBound = 0.0, highBound = 2.0 )
    cmds.select( wtwist[1], 'wingB_01_jnt_R' )
    anm.matchObj()
    cmds.parent( wtwist[1], null )
    cmds.setAttr( wtwist[1] + '.rotateX', 90 )
    # cmds.setAttr( wtwist[1] + '.rotateZ', -90 )
    cmds.setAttr( wtwist[1] + '.scaleZ', cmds.getAttr( wtwist[1] + '.scaleZ' ) * -1 )
    place.hijackAttrs( wtwist[1], wngb_rCt[2], 'translateZ', 'twistSlide', set = False, default = 0, force = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wngb_rCt[2], 'highBound', 'twistBound', set = False, default = 2, force = True )
    cmds.setAttr( wngb_rCt[2] + '.twistBound', k = True )
    place.hijackAttrs( wtwist[0] + 'HandleShape', wngb_rCt[2], 'endAngle', 'twistAngle', set = False, default = 0, force = True )
    cmds.setAttr( wngb_rCt[2] + '.twistAngle', k = True )
    # lock geo - [lock, keyable], [visible, lock, keyable]
    place.setChannels( wtwist[1], [False, False], [False, False], [True, False], [False, False, False] )
    '''

    abdomen = 'Abdomen'
    abdmn = place.Controller( abdomen, 'abdomen_01_jnt', orient = False, shape = 'facetZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    abdmnCt = abdmn.createController()
    place.cleanUp( abdmnCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], abdmnCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    # return None
    abdomenEnd = 'AbdomenEnd'
    abdmnEnd = place.Controller( abdomenEnd, 'abdomenEnd_01_jnt', orient = False, shape = 'facetZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    abdmnEndCt = abdmnEnd.createController()
    place.cleanUp( abdmnEndCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( cntCt[4], abdmnEndCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    abdomenTip = 'AbdomenTip'
    abdmnTp = place.Controller( abdomenTip, 'abdomenEnd_09_jnt', orient = False, shape = 'facetZup_ctrl', size = 1.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    abdmnTpCt = abdmnTp.createController()
    place.cleanUp( abdmnTpCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( abdmnEndCt[4], abdmnTpCt[0], mo = True )
    # cmds.parentConstraint( cog, 'root_jnt', mo = True )

    cerci = 'Cerci'
    crc = place.Controller( cerci, 'abdomenEnd_09_jnt', orient = False, shape = 'facetZup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    crcCt = crc.createController()
    place.cleanUp( crcCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'abdomenEnd_09_jnt', crcCt[0], mo = True )
    cmds.pointConstraint( 'abdomenEnd_10_jnt', crcCt[4], mo = True )
    cmds.orientConstraint( crcCt[4], 'abdomenEnd_10_jnt', mo = True )

    neck = 'Neck'
    nck = place.Controller( neck, 'neck_01_jnt', orient = False, shape = 'facetZup_ctrl', size = 1.0, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    nckCt = nck.createController()
    place.cleanUp( nckCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'root_thorax_jnt', nckCt[0], mo = True )

    head = 'Head'
    hd = place.Controller( head, 'head_jnt', orient = False, shape = 'facetZup_ctrl', size = 2.6, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    hdCt = hd.createController()
    place.cleanUp( hdCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( nckCt[4], hdCt[0], mo = True )
    # cmds.pointConstraint( 'head_jnt', hdCt[4], mo = True )
    cmds.orientConstraint( hdCt[4], 'head_jnt', mo = True )
    place.setChannels( hdCt[3], [False, False], [False, True], [True, False], [True, False, False] )
    cmds.setAttr( hdCt[2] + '.Offset_Vis', 1 )

    # fk chain
    name = 'Antenna_L'
    # name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    aRig = sfk.SplineFK( name, 'antenna_01_jnt_L', 'antenna_07_jnt_L', None,
                              controllerSize = 0.2, rootParent = 'head_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'blue' )

    # fk chain
    name = 'Antenna_R'
    # name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    aRig = sfk.SplineFK( name, 'antenna_01_jnt_R', 'antenna_07_jnt_R', None,
                              controllerSize = 0.2, rootParent = 'head_jnt', parent1 = 'master_Grp', parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'red' )

    # return None
    # LeftSide of Rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsL = []
    for jnt in endJntL:
        cnt = place.Controller( btmCtrl_L[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsL.append( cntCt[4] )
        i = i + 1
    # print 'catch baseGrpsL:'
    # print baseGrpsL

    i = 0
    scktGrpsL = []
    backTop_ct = []
    for jnt in legIkTopL:
        cnt = place.Controller( topCtrl_L[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.4, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'blue' )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( legParents[i], cntCt[0], mo = True )
        # cmds.parentConstraint( cntCt[4], jnt, mo = True )
        scktGrpsL.append( cntCt[4] )
        if i == 2:
            backTop_ct.append( cntCt[2] )
        i = i + 1
    # print 'catch scktGrpsL:'
    # print scktGrpsL

    # Rightside of rig

    i = 0
    assist = 'Assist'
    attrCstm = 'KneeTwist'
    baseGrpsR = []
    for jnt in endJntR:
        cnt = place.Controller( btmCtrl_R[i], jnt, orient = False, shape = 'facetYup_ctrl', size = 0.5, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'red' )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( 'master_Grp', cntCt[0], mo = True )
        # add pv attributes
        place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
        cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
        cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
        baseGrpsR.append( cntCt[4] )
        i = i + 1
    # print 'catch baseGrpsR:'
    # print baseGrpsR

    i = 0
    scktGrpsR = []
    # backTop_ct = []
    for jnt in legIkTopR:
        cnt = place.Controller( topCtrl_R[i], jnt, orient = False, shape = 'diamond_ctrl', size = 0.4, color = 17, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True, colorName = 'red' )
        cntCt = cnt.createController()
        # parents 'obj' to arguments specified as 'True'
        place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        cmds.parentConstraint( legParents[i], cntCt[0], mo = True )
        # cmds.parentConstraint( cntCt[4], jnt, mo = True )
        scktGrpsR.append( cntCt[4] )
        if i == 2:
            backTop_ct.append( cntCt[2] )
        i = i + 1
    # print 'catch scktGrpsR:'
    # print scktGrpsR

    # create PoleVectors, place and clean up into groups

    # LeftSide of Rig
    # return None

    curveShapePath = 'C:\\Users\\sebas\\Documents\\maya\\controlShapes'

    i = 0
    pvLocListL = []
    # leg pv direction (forward, back, back)
    flipVar = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]]
    dis = [1, -1, -1]
    for jnt in legJntL:
        if i > 0:
            # select 3 for back facing pv
            cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 3 )  # 1 based
        else:
            # select 1 for back facing pv
            cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 1 )  # 1 based
        aul.setPreset()
        # stJnt, endJnt, prefix, suffix, limbName, rotControl, aimControl, upControl, disFactor, locScale, curveShapePath, useFlip = True, flipVar = [0, 0, 0], color = 17, X = 1, midJnt
        pvLoc = appendage.create_3_joint_pv( jnt, endJntL[i], 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', dis[i] * 1.2, 0.2, curveShapePath, True, flipVar = flipVar[i], X = 0.05, midJnt = kneeJntL[i] )
        pvLocListL.append( pvLoc )
        place.cleanUp( pvLocListL[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
        # break
    # print 'catch pvLocListL:'
    # print pvLocListL

    # RightSide of Rig

    i = 0
    pvLocListR = []
    # leg pv direction (forward, back, back)
    flipVar = [
    [0, 1, 1],
    [0, 1, 1],
    [0, 1, 1]]
    dis = [-1, 1, 1]
    for jnt in legJntR:
        if i > 0:
            # select 3 for back facing pv
            cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 4 )  # 1 based
        else:
            # select 1 for back facing pv
            cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 2 )  # 1 based
        aul.setPreset()
        pvLoc = appendage.create_3_joint_pv( jnt, endJntR[i], 'pv', 'R', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                            'atom_bls_limbUp_radioButtonGrp', dis[i] * 1.2, 0.2, curveShapePath, True, flipVar = flipVar[i], X = 0.05, midJnt = kneeJntR[i] )
        pvLocListR.append( pvLoc )
        place.cleanUp( pvLocListR[i], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
        i = i + 1
    # print 'catch pvLocListR:'
    # print pvLocListR
    # return None
    # Creates poleVector Rig for appendages
    """
    creates pole vector rig
    \n*
    name      = name
    Master    = lowest master controller of char          --(not manipulated, 3 objs are constrained to it, for twist value calc)\n
    Top       = controller at top of ik                   --(not manipulated, pvRig group is parented under this object)\n
    Btm       = bottom of ik, controlling group or null   --(not manipulated, aim object for 'Top')\n
    Twist     = object from which twist is derived        --(not manipulated, axis is derived from 'aim' variable)\n
    pv        = pre-positioned pole vector object         --(object gets parented, turned off)\n
    midJnt    = connection joint for guideline            --(not manipulated)\n
    X         = size
    up        = [int, int, int]                           --(ie. [1,0,0], use controller space not joint space)\n
    aim       = [int, int, int]                           --(ie. [0,-1,0], use controller space not joint space)\n
    color     = int 1-31                                  --(ie. 17 is yellow)\n
    *\n
    Note      = Master, Top, Twist should all have the same rotation order.
    ie.       = Twist axis should be main axis. If 'y'is main axis, rotate order = 'zxy' or 'xzy'
    """
    i = 0
    for cnt in btmCtrl_L:
        appendage.pvRig( pvNamesL[i], 'master_Grp', scktGrpsL[i], baseGrpsL[i], baseGrpsL[i], pvLocListL[i], kneeJntL[i], 0.1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 6 )
        i = i + 1

    i = 0
    for cnt in btmCtrl_R:
        appendage.pvRig( pvNamesR[i], 'master_Grp', scktGrpsR[i], baseGrpsR[i], baseGrpsR[i], pvLocListR[i], kneeJntR[i], 0.1, cnt, setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 13 )
        i = i + 1

    place.cleanUp( 'GuideGp', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )

    # Create an ik handle from TopJoint to end effector
    i = 0
    for jnt in legIkTopL:
        cmds.ikHandle( n = ikNamesL[i], sj = jnt, ee = endJntL[i], sol = 'ikRPsolver', p = 2, w = 0.5, srp = True )
        cmds.poleVectorConstraint( pvLocListL[i], ikNamesL[i] )
        cmds.setAttr( ikNamesL[i] + '.visibility', 0 )
        cmds.parent( ikNamesL[i], baseGrpsL[i] )
        i = i + 1
    i = 0
    for jnt in legIkTopR:
        cmds.ikHandle( n = ikNamesR[i], sj = jnt, ee = endJntR[i], sol = 'ikRPsolver', p = 2, w = 0.5, srp = True )
        cmds.poleVectorConstraint( pvLocListR[i], ikNamesR[i] )
        cmds.setAttr( ikNamesR[i] + '.visibility', 0 )
        cmds.parent( ikNamesR[i], baseGrpsR[i] )
        i = i + 1

    # UPPER LEG CONTROLS

    # middle legs
    # L
    # socket
    cnt = place.Controller( 'legB_01_ct_L', 'legB_01_jnt_L', orient = False, shape = 'diamond_ctrl', size = 0.25, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    # parents 'obj' to arguments specified as 'True'
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'root_thorax_jnt', cntCt[0], mo = True )
    place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
    cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
    cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
    cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
    # pv
    dis = [-1, 1]  # distance
    # leg pv direction (forward)
    cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 2 )  # 1 based, pv forward facing
    aul.setPreset()
    pvLoc = appendage.create_3_joint_pv( 'legB_01_jnt_L', 'legB_03_jnt_L', 'pv', 'L', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                        'atom_bls_limbUp_radioButtonGrp', dis[0] * 0.25, 0.2, curveShapePath, True, flipVar = [0, 0, 0], X = 0.05, midJnt = 'legB_02_jnt_L' )
    # print pvLoc
    place.cleanUp( pvLoc, Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    # return None
    # pv rig
    pvName = 'legB_pv_02_ct_L'
    appendage.pvRig( pvName, 'master_Grp', cntCt[4], 'legB_04_ct_L', 'legB_04_ct_L', 'pv_legB_02_jnt_pv_loc_L', 'legB_02_jnt_L', 0.05, cntCt[2], setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 6 )
    # ik
    # return None
    cmds.ikHandle( n = 'legB_03_ik_L', sj = 'legB_01_jnt_L', ee = 'legB_03_jnt_L', sol = 'ikRPsolver', p = 2, w = 0.5, srp = True )
    cmds.poleVectorConstraint( pvLoc, 'legB_03_ik_L' )
    cmds.setAttr( 'legB_03_ik_L' + '.visibility', 0 )
    cmds.parent( 'legB_03_ik_L', 'legB_04_ct_L_Grp' )

    # R
    # socket
    cnt = place.Controller( 'legB_01_ct_R', 'legB_01_jnt_R', orient = False, shape = 'diamond_ctrl', size = 0.25, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    cntCt = cnt.createController()
    # parents 'obj' to arguments specified as 'True'
    place.cleanUp( cntCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.parentConstraint( 'root_thorax_jnt', cntCt[0], mo = True )
    place.optEnum( cntCt[2], attr = assist, enum = 'OPTNS' )
    cmds.addAttr( cntCt[2], ln = attrCstm, at = 'float', h = False )
    cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), cb = True )
    cmds.setAttr( ( cntCt[2] + '.' + attrCstm ), k = True )
    # pv
    dis = [-1, 1]  # distance
    # leg pv direction (forward)
    cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', edit = True, sl = 2 )  # 1 based, pv forward facing
    aul.setPreset()
    pvLoc = appendage.create_3_joint_pv( 'legB_01_jnt_R', 'legB_03_jnt_R', 'pv', 'R', 'leg', 'atom_bls_limbRot_radioButtonGrp', 'atom_bls_limbAim_radioButtonGrp',
                                        'atom_bls_limbUp_radioButtonGrp', dis[1] * 0.25, 0.2, curveShapePath, True, flipVar = [0, 1, 1], X = 0.05, midJnt = 'legB_02_jnt_R' )
    # print pvLoc
    place.cleanUp( pvLoc, Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    # return None
    # pv rig
    pvName = 'legB_pv_02_ct_R'
    appendage.pvRig( pvName, 'master_Grp', cntCt[4], 'legB_04_ct_R', 'legB_04_ct_R', 'pv_legB_02_jnt_pv_loc_R', 'legB_02_jnt_R', 0.05, cntCt[2], setChannels = True, up = [1, 0, 0], aim = [0, -1, 0], color = 13 )
    # ik
    # return None
    cmds.ikHandle( n = 'legB_03_ik_R', sj = 'legB_01_jnt_R', ee = 'legB_03_jnt_R', sol = 'ikRPsolver', p = 2, w = 0.5, srp = True )
    cmds.poleVectorConstraint( pvLoc, 'legB_03_ik_R' )
    cmds.setAttr( 'legB_03_ik_R' + '.visibility', 0 )
    cmds.parent( 'legB_03_ik_R', 'legB_04_ct_R_Grp' )

    # leg L back root up object
    leg_root = 'legC_01_up_L'
    up = place.Controller( leg_root, scktGrpsL[-1], orient = False, shape = 'diamond_ctrl', size = 0.15, color = 6, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    upCt = up.createController()
    place.cleanUp( upCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCt[0] + '.translateX', 0.5 )
    cmds.parentConstraint( scktGrpsL[-1], upCt[0], mo = True )
    # guide line
    gd = place.guideLine( scktGrpsL[-1], upCt[4], leg_root + '_pvGuide' )
    guideGp = cmds.group( em = True, name = leg_root + '_pvGuideGp' )
    place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
    cmds.parent( gd[0], guideGp )
    cmds.parent( gd[1], guideGp )
    place.cleanUp( guideGp, World = True )
    # aim
    cmds.aimConstraint( scktGrpsL[-1], 'legC_01_jnt_L', wuo = upCt[4], wut = 'object', aim = [0, 0, 1], u = [1, 0, 0] )
    # hide pv backTop_ct
    place.hijackAttrs( upCt[2], backTop_ct[0], 'visibility', 'upVisibility', set = False, default = 0, force = True )

    # leg R back root up object
    leg_root = 'legC_01_up_R'
    up = place.Controller( leg_root, scktGrpsR[-1], orient = False, shape = 'diamond_ctrl', size = 0.15, color = 13, sections = 8, degree = 1, normal = ( 0, 0, 1 ), setChannels = True, groups = True )
    upCt = up.createController()
    place.cleanUp( upCt[0], Ctrl = True, SknJnts = False, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    cmds.setAttr( upCt[0] + '.translateX', -0.5 )
    cmds.parentConstraint( scktGrpsR[-1], upCt[0], mo = True )
    # guide line
    gd = place.guideLine( scktGrpsR[-1], upCt[4], leg_root + '_pvGuide' )
    guideGp = cmds.group( em = True, name = leg_root + '_pvGuideGp' )
    place.setChannels( guideGp, [True, False], [True, False], [True, False], [True, False, False] )
    cmds.parent( gd[0], guideGp )
    cmds.parent( gd[1], guideGp )
    place.cleanUp( guideGp, World = True )
    # aim
    cmds.aimConstraint( scktGrpsR[-1], 'legC_01_jnt_R', wuo = upCt[4], wut = 'object', aim = [0, 0, -1], u = [-1, 0, 0] )
    # hide pv backTop_ct
    place.hijackAttrs( upCt[2], backTop_ct[1], 'visibility', 'upVisibility', set = False, default = 0, force = True )

    # cleanup of root_jnt and body_Geo
    place.cleanUp( 'root_thorax_jnt', Ctrl = False, SknJnts = True, Body = False, Accessory = False, Utility = False, World = False, olSkool = False )
    place.cleanUp( geo_grp, Ctrl = False, SknJnts = False, Body = True, Accessory = False, Utility = False, World = False, olSkool = False )
    vray = [
    'VRayLightDome1',
    'vrDispl_base',
    'vrDispl_Wings'
    ]
    # place.cleanUp( vray, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = True, World = False, olSkool = False )
    #

    # fk chain
    # name, startJoint, endJoint, suffix, direction = 0, controllerSize = 1, rootParent = None, parent1 = None, parent2 = None, parentDefault = [1, 1], segIteration = 4, stretch = 0, ik = None, colorScheme = 'yellow'
    name = 'LegA_Tip_L'
    aRig = sfk.SplineFK( name, 'legA_08_jnt_L', 'legA_13_jnt_L', None,
                              controllerSize = 0.2, rootParent = 'legA_07_jnt_L', parent1 = btmCtrl_L[0], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'blue' )
    name = 'LegB_Tip_L'
    aRig = sfk.SplineFK( name, 'legB_06_jnt_L', 'legB_11_jnt_L', None,
                              controllerSize = 0.2, rootParent = 'legB_05_jnt_L', parent1 = btmCtrl_L[1], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'blue' )
    name = 'LegC_Tip_L'
    aRig = sfk.SplineFK( name, 'legC_06_jnt_L', 'legC_10_jnt_L', None,
                              controllerSize = 0.2, rootParent = 'legC_05_jnt_L', parent1 = btmCtrl_L[2], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'blue' )
    #
    name = 'LegA_Tip_R'
    aRig = sfk.SplineFK( name, 'legA_08_jnt_R', 'legA_13_jnt_R', None,
                              controllerSize = 0.2, rootParent = 'legA_07_jnt_R', parent1 = btmCtrl_R[0], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'red' )
    name = 'LegB_Tip_R'
    aRig = sfk.SplineFK( name, 'legB_06_jnt_R', 'legB_11_jnt_R', None,
                              controllerSize = 0.2, rootParent = 'legB_05_jnt_R', parent1 = btmCtrl_R[1], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'red' )
    name = 'LegC_Tip_R'
    aRig = sfk.SplineFK( name, 'legC_06_jnt_R', 'legC_10_jnt_R', None,
                              controllerSize = 0.2, rootParent = 'legC_05_jnt_R', parent1 = btmCtrl_R[2], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = 'red' )

    # wing fk chain

    # wing util
    wngUtl = [
    'wingA_util_L',
    'wingA_util_R',
    'wingB_util_L',
    'wingB_util_R'
    ]
    wngMesh = [
    'Dragonfly_forewings1',
    'Dragonfly_forewings',
    'Dragonfly_hindwings1',
    'Dragonfly_hindwings'
    ]
    names = [
    'wingA_fk_L',
    'wingA_fk_R',
    'wingB_fk_L',
    'wingB_fk_R'
    ]
    fk_jnts = [
        ['wingA_00_jnt_L', 'wingA_05_jnt_L'],
        ['wingA_00_jnt_R', 'wingA_05_jnt_R'],
        ['wingB_00_jnt_L', 'wingB_05_jnt_L'],
        ['wingB_00_jnt_R', 'wingB_05_jnt_R']
        ]
    fk_prnts = [
        ['WingA_L_Grp', 'WingA_Grp'],
        ['WingA_R_Grp', 'WingA_Grp'],
        ['WingB_L_Grp', 'WingB_Grp'],
        ['WingB_R_Grp', 'WingB_Grp']
        ]
    i = 0
    for util in wngUtl:
        #
        cw.createWrap( util, wngMesh[i] )
        place.cleanUp( util, Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = True, World = False, olSkool = False )
        place.cleanUp( util + 'Base', Ctrl = False, SknJnts = False, Body = False, Accessory = False, Utility = False, World = True, olSkool = False )
        #
        if not wingSplines:
            color = 'blue'
            if '_R' in util:
                color = 'red'
            aRig = sfk.SplineFK( names[i], fk_jnts[i][0], fk_jnts[i][1], None,
                                      controllerSize = 0.5, rootParent = fk_prnts[i][0], parent1 = fk_prnts[i][1], parentDefault = [1, 0], segIteration = None, stretch = 0, ik = 'splineIK', colorScheme = color )
        i = i + 1

    if wingSplines:
        buildSplines( wingSplines = True )
    else:
        buildSplines( wingSplines = False )


def buildSplines( wingSplines = False ):
    '''\n
    Build splines for quadraped character\n
    '''
    # X = cmds.floatField('atom_qrig_conScale', query=True, value=True)
    X = 0.15

    def SplineOpts( name, size, distance, falloff ):
        '''\n
        Changes options in Atom rig window\n
        '''
        cmds.textField( 'atom_prefix_textField', e = True, tx = name )
        cmds.floatField( 'atom_spln_scaleFactor_floatField', e = True, v = size )
        cmds.floatField( 'atom_spln_vectorDistance_floatField', e = True, v = distance )
        cmds.floatField( 'atom_spln_falloff_floatField', e = True, v = falloff )

    def OptAttr( obj, attr ):
        '''\n
        Creates separation attr to signify beginning of options for spline\n
        '''
        cmds.addAttr( obj, ln = attr, attributeType = 'enum', en = 'OPTNS' )
        cmds.setAttr( obj + '.' + attr, cb = True )

    # SPINE
    spineName = 'Abdomen'
    spineSize = X * 1
    spineDistance = X * 60
    spineFalloff = 0
    spinePrnt = 'Abdomen_Grp'
    spineStrt = 'Abdomen_Grp'
    spineEnd = 'AbdomenEnd_Grp'
    spineAttr = 'Abdomen'
    spineRoot = 'spine_jnt_01'
    'spine_S_IK_Jnt'
    spine = ['abdomen_01_jnt', 'abdomen_05_jnt']
    # build spline
    SplineOpts( spineName, spineSize, spineDistance, spineFalloff )
    cmds.select( spine )

    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( spineAttr, 'AbdomenSpline' )
    cmds.parentConstraint( spinePrnt, spineName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( spineStrt, spineName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( spineEnd, spineName + '_E_IK_PrntGrp', mo = True )
    # cmds.parentConstraint( spineName + '_S_IK_Jnt', spineRoot, mo = True )
    place.hijackCustomAttrs( spineName + '_IK_CtrlGrp', spineAttr )
    # return None
    # set options
    cmds.setAttr( spineAttr + '.' + spineName + 'Vis', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Root', 0 )
    cmds.setAttr( spineAttr + '.' + spineName + 'Stretch', 0 )
    cmds.setAttr( spineAttr + '.ClstrVis', 0 )
    cmds.setAttr( spineAttr + '.ClstrMidIkBlend', 0.25 )
    cmds.setAttr( spineAttr + '.ClstrMidIkSE_W', 0.25 )
    cmds.setAttr( spineAttr + '.VctrVis', 0 )
    cmds.setAttr( spineAttr + '.VctrMidIkBlend', .25 )
    cmds.setAttr( spineAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( spineAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( spineName + '_S_IK_Cntrl.LockOrientOffOn', 1 )
    cmds.setAttr( spineName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', spineName + '_E_IK_curve_scale.input2Z' )

    # NECK
    neckName = 'Neck'
    neckSize = X * 1
    neckDistance = X * 40
    neckFalloff = 0
    neckPrnt = 'Neck_Grp'
    neckStrt = 'Neck_Grp'
    neckEnd = 'Head'
    neckAttr = 'Neck'
    neck = ['neck_01_jnt', 'neck_03_jnt']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # assemble
    OptAttr( neckAttr, 'NeckSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 0.1 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.1 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.1 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )
    # return False

    # TAIL
    neckName = 'AbdomenEnd'  # spline prefix name
    neckSize = X * 1
    neckDistance = X * 10
    neckFalloff = 0
    neckPrnt = 'AbdomenEnd_Grp'
    neckStrt = 'abdomen_05_jnt'
    neckEnd = 'AbdomenTip'
    neckAttr = 'AbdomenEnd'  # pre-existing control name
    neck = ['abdomenEnd_01_jnt', 'abdomenEnd_09_jnt']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( neckAttr, 'AbdomenEndSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    # return None
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 0 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # LEFT FRONT LEG
    neckName = 'legA_L'  # spline prefix name
    neckSize = X  # * 0.1010
    neckDistance = X * 10
    neckFalloff = 0
    neckPrnt = 'Neck_Grp'
    neckStrt = 'neck_02_jnt'
    neckEnd = 'legA_06_ct_L_Grp'
    neckAttr = 'legA_06_ct_L'  # pre-existing control name
    neck = ['legA_01_jnt_L', 'legA_05_jnt_L']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( neckAttr, 'legA_LSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    # return None
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # LEFT FRONT LEG
    neckName = 'legA_R'  # spline prefix name
    neckSize = X * 1
    neckDistance = X * 10
    neckFalloff = 0
    neckPrnt = 'Neck_Grp'
    neckStrt = 'neck_02_jnt'
    neckEnd = 'legA_06_ct_R_Grp'
    neckAttr = 'legA_06_ct_R'  # pre-existing control name
    neck = ['legA_01_jnt_R', 'legA_05_jnt_R']
    # build spline
    SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
    cmds.select( neck )
    # print 'here'
    stage.splineStage( 4 )
    # return None
    # assemble
    OptAttr( neckAttr, 'legA_RSpline' )
    cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
    cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
    # return None
    cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
    place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
    # set options
    cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
    cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
    cmds.setAttr( neckAttr + '.ClstrVis', 0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
    cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrVis', 0 )
    cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
    cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
    cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
    cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
    cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
    # scale
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
    cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    if wingSplines:
        # WING A L
        neckName = 'WingA_L'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingA_L_Grp'
        neckStrt = 'WingA_L_Grp'
        neckEnd = 'WingA_L_Grp'
        neckAttr = 'WingA_L'  # pre-existing control name
        neck = ['wingA_01_jnt_L', 'wingA_05_jnt_L']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingA_LSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING A R
        neckName = 'WingA_R'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingA_R_Grp'
        neckStrt = 'WingA_R_Grp'
        neckEnd = 'WingA_R_Grp'
        neckAttr = 'WingA_R'  # pre-existing control name
        neck = ['wingA_01_jnt_R', 'wingA_05_jnt_R']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingA_RSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING B L
        neckName = 'WingB_L'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingB_L_Grp'
        neckStrt = 'WingB_L_Grp'
        neckEnd = 'WingB_L_Grp'
        neckAttr = 'WingB_L'  # pre-existing control name
        neck = ['wingB_01_jnt_L', 'wingB_05_jnt_L']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingB_LSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

        # WING B R
        neckName = 'WingB_R'  # spline prefix name
        neckSize = X * 1
        neckDistance = X * 6
        neckFalloff = 0
        neckPrnt = 'WingB_R_Grp'
        neckStrt = 'WingB_R_Grp'
        neckEnd = 'WingB_R_Grp'
        neckAttr = 'WingB_R'  # pre-existing control name
        neck = ['wingB_01_jnt_R', 'wingB_05_jnt_R']
        # build spline
        SplineOpts( neckName, neckSize, neckDistance, neckFalloff )
        cmds.select( neck )
        # print 'here'
        stage.splineStage( 4 )
        # return None
        # assemble
        OptAttr( neckAttr, 'WingB_RSpline' )
        cmds.parentConstraint( neckPrnt, neckName + '_IK_CtrlGrp', mo = True )
        # cmds.parentConstraint( neckStrt, neckName + '_S_IK_PrntGrp', mo = True )
        # return None
        # cmds.parentConstraint( neckEnd, neckName + '_E_IK_PrntGrp', mo = True )
        place.hijackCustomAttrs( neckName + '_IK_CtrlGrp', neckAttr )
        # set options
        cmds.setAttr( neckAttr + '.' + neckName + 'Vis', 1 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Root', 0 )
        cmds.setAttr( neckAttr + '.' + neckName + 'Stretch', 0 )
        cmds.setAttr( neckAttr + '.ClstrVis', 0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkBlend', 1.0 )
        cmds.setAttr( neckAttr + '.ClstrMidIkSE_W', 0.0 )
        cmds.setAttr( neckAttr + '.VctrVis', 0 )
        cmds.setAttr( neckAttr + '.VctrMidIkBlend', 1 )
        cmds.setAttr( neckAttr + '.VctrMidIkSE_W', 0.5 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrnt', 0 )
        cmds.setAttr( neckAttr + '.VctrMidTwstCstrntSE_W', 0.5 )
        cmds.setAttr( neckName + '_S_IK_Cntrl.LockOrientOffOn', 0 )
        cmds.setAttr( neckName + '_E_IK_Cntrl.LockOrientOffOn', 1 )
        # scale
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_S_IK_curve_scale.input2Z' )
        cmds.connectAttr( '___CONTROLS.scaleZ', neckName + '_E_IK_curve_scale.input2Z' )

    # scale
    # scale
    # geo = 'caterpillar_c_geo_lod_0'
    mstr = 'master'
    uni = 'uniformScale'
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    #
    misc.addAttribute( [mstr], [uni], 0.1, 100.0, True, 'float' )
    cmds.setAttr( mstr + '.' + uni, 1.0 )
    # misc.addAttribute( [mstr], [uni], 0.1, 10.0, True, 'float' )
    scl = ['.scaleX', '.scaleY', '.scaleZ']
    misc.scaleUnlock( '___CONTROLS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___CONTROLS' + s )
    misc.scaleUnlock( '___SKIN_JOINTS', sx = True, sy = True, sz = True )
    for s in scl:
        cmds.connectAttr( mstr + '.' + uni, '___SKIN_JOINTS' + s )
        cmds.connectAttr( mstr + '.' + uni, 'deltaMush1' + s )  # set scale, apply deltaMush, add scale connection for deltaMush


def dragonfly_geo():
    '''
    geo names
    '''
    return [
    'dragonfly_grp|Dragonfly_leg_spikes5',
    'dragonfly_grp|Dragonfly_leg_spikes4',
    'dragonfly_grp|Dragonfly_leg_spikes3',
    'dragonfly_grp|Dragonfly_leg_spikes2',
    'dragonfly_grp|Dragonfly_leg_spikes1',
    'dragonfly_grp|Dragonfly_eyes',
    'dragonfly_grp|Dragonfly_ocelli',
    'dragonfly_grp|Dragonfly_leg_spikes',
    'dragonfly_grp|Dragonfly_body',
    'dragonfly_grp|Dragonfly_L_mandible',
    'dragonfly_grp|Dragonfly_R_anteclypeus',
    'dragonfly_grp|Dragonfly_R_maxilla',
    'dragonfly_grp|Dragonfly_R_maxillary_palp',
    'dragonfly_grp|Dragonfly_R_mandible',
    'dragonfly_grp|Dragonfly_labrum',
    'dragonfly_grp|Dragonfly_L_anteclypeus',
    'dragonfly_grp|Dragonfly_L_maxillary_palp',
    'dragonfly_grp|Dragonfly_maxillary_palp_Dragonfly',
    'dragonfly_grp|Dragonfly_L_antenna1',
    'dragonfly_grp|Dragonfly_R_antenna1',
    'Dragonfly_eyeIntGeo'
    ]
    '''
    return [
    'dragonfly_grp|Dragonfly_leg_spikes5',
    'dragonfly_grp|Dragonfly_leg_spikes4',
    'Dragonfly_hindwings',
    'dragonfly_grp|Dragonfly_leg_spikes3',
    'dragonfly_grp|Dragonfly_leg_spikes2',
    'dragonfly_grp|Dragonfly_leg_spikes1',
    'dragonfly_grp|Dragonfly_eyes',
    'dragonfly_grp|Dragonfly_ocelli',
    'dragonfly_grp|Dragonfly_leg_spikes',
    'Dragonfly_forewings',
    'dragonfly_grp|Dragonfly_body',
    'dragonfly_grp|Dragonfly_L_mandible',
    'dragonfly_grp|Dragonfly_R_anteclypeus',
    'dragonfly_grp|Dragonfly_R_maxilla',
    'dragonfly_grp|Dragonfly_R_maxillary_palp',
    'dragonfly_grp|Dragonfly_R_mandible',
    'dragonfly_grp|Dragonfly_labrum',
    'dragonfly_grp|Dragonfly_L_anteclypeus',
    'dragonfly_grp|Dragonfly_L_maxillary_palp',
    'dragonfly_grp|Dragonfly_maxillary_palp_Dragonfly',
    'dragonfly_grp|Dragonfly_L_antenna1',
    'dragonfly_grp|Dragonfly_R_antenna1',
    'Dragonfly_eyeIntGeo',
    'Dragonfly_forewings1',
    'Dragonfly_hindwings1'
    ]'''


def dragonfly_nurbs():
    return [
    'wingA_util_L',
    'wingA_util_R',
    'wingB_util_R',
    'wingB_util_L'
    ]


def weights_path():
    '''
    make path if not present from current file
    '''
    # path
    path = cmds.file( query = True, sceneName = True )
    filename = cmds.file( query = True, sceneName = True , shortName = True )
    path = path.split( filename )[0]
    path = os.path.join( path, 'weights' )
    if not os.path.isdir( path ):
        os.mkdir( path )
    return path


def weights_meshExport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = dragonfly_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        krl.exportMeshWeights( ex_path, geo, updatebar = True )


def weights_nurbsExport():
    '''
    exportNurbsCurveWeights( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = dragonfly_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        ex_path = os.path.join( path, g )
        krl.exportNurbsSurfaceWeights( ex_path, geo )


def weights_meshImport():
    '''
    dargonfly object weights
    '''
    # path
    path = weights_path()
    # geo
    all_geo = dragonfly_geo()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importMeshWeights( im_path, geo, updatebar = True )


def weights_nurbsImport():
    '''
    importNurbSurfaceWeights2( path, obj )
    '''
    # path
    path = weights_path()
    # geo
    all_geo = dragonfly_nurbs()
    for geo in all_geo:
        g = ''
        if '|' in geo:
            g = geo.split( '|' )[-1]
        else:
            g = geo
        im_path = os.path.join( path, g )
        krl.importNurbSurfaceWeights2( im_path, geo )


def renameJointSelection( name = '', pad = 2, suffix = '' ):
    sel = cmds.ls( sl = 1 )
    d = 1
    for i in sel:
        j = cmds.rename( i, name + '_' + str( ( '%0' + str( pad ) + 'd' ) % ( d ) ) + '_jnt' )
        if suffix:
            cmds.rename( j, j + '_' + suffix )
        d = d + 1
