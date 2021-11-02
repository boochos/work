import os

from pymel.core import *

import maya.cmds as cmds
import webrImport as web

# web
uil = web.mod( 'atom_ui_lib' )
atl = web.mod( 'atom_tag_lib' )


class RefreshCallBack( object ):

    def __init__( self, win ):
        self.win = win

    def RefreshCall( self, *args ):
        import atom_ui_lib
        atom_ui_lib.refreshWindow( self.win )


class BuildSnakeFacerigCallback( object ):

    def CMD( self, *args ):
        pass

        import webrImport as web
        af = web.mod( 'atom_face_lib' )
        af.buildSnakeFace()


def convertPymelToSortedStrList( pList ):
    rList = []
    for pNode in pList:
        if isinstance( pNode, PyNode ):
            rList.append( str( pNode.name() ) )
        else:
            rList.append( pNode )

    rList.sort( key = str.lower )
    return rList


def createTagGroups( self ):
    '''
    # Name        :createTagGroups
    # Arguements  :N/A
    # Description :set up groups and group names depending on tags
    '''
    objects = atl.Atom_Tag_Core()
    masters = objects.getMasters()

    for obj in objects.masterDict['None_Referenced']:

        master = obj.atom.children()[0].children()[0].children()[0].split( '.' )[1]
        tmp_name = obj.atom.children()[0].children()[0].children()[0].children()[0].split( '.' )[1].split( '_' )
        # account for different geometry types
        # geo, body and head
        # acc accessories, necklace, etc...
        if len( tmp_name ) == 3:
            # Note, to get the final group names the atom attribute is split
            # appart and the name is built
            if tmp_name[1] == 'geo':
                tag_grp_name = '___' + tmp_name[0] + '_' + tmp_name[2] + 'Gp'

                if not objExists( tag_grp_name ):
                    createNode( 'transform', name = tag_grp_name, ss = True )

                if objExists( '___BODY' ):
                    ls( tag_grp_name )[0].setParent( '___BODY' )

                sortList = convertPymelToSortedStrList( obj.atom.children()[0].children()[0].children()[0].children()[0].connections( s = False, d = True ) )
                sortList.append( obj )
                cObjList = convertPymelToSortedStrList( sortList )
                for cObj in cObjList:
                    obj = ls( cObj )[0]
                    obj.setParent( tag_grp_name )

            elif tmp_name[1] == 'acc':
                tag_grp_name = '___' + tmp_name[0] + '_' + tmp_name[2] + 'Gp'
                if not objExists( tag_grp_name ):
                    createNode( 'transform', name = tag_grp_name, ss = True )

                if objExists( '___ACCESSORY' ):
                    ls( tag_grp_name )[0].setParent( '___ACCESSORY' )

                cObjList = convertPymelToSortedStrList( obj.atom.children()[0].children()[0].children()[0].children()[0].connections( s = False, d = True ) )
                for cObj in cObjList:
                    obj = ls( cObj )[0]
                    obj.setParent( tag_grp_name )

                ls( master )[0].setParent( tag_grp_name )

            elif tmp_name[1] == 'util':
                tag_grp_name = '___' + tmp_name[0] + '_' + tmp_name[2] + 'Gp'

                if not objExists( tag_grp_name ):
                    createNode( 'transform', name = tag_grp_name, ss = True )
                    cmds.setAttr( tag_grp_name + '.visibility', False )

                if objExists( '___UTILITY' ):
                    ls( tag_grp_name )[0].setParent( '___UTILITY' )

                sortList = obj.atom.children()[0].children()[0].children()[0].children()[0].connections( s = False, d = True )
                sortList.append( obj )

                cObjList = convertPymelToSortedStrList( sortList )
                for cObj in cObjList:
                    obj = ls( cObj )[0]
                    obj.setParent( tag_grp_name )


def ratFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_rat_frameLayout', label = 'Rat Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = True )

    atom_rrig_columnLayout = cmds.columnLayout( 'atom_rat_main_columnLayout', adj = True, rs = 5 )
    atom_rrig_faceBuild_checkBox = cmds.checkBox( 'atom_rat_faceCheck', l = 'Build Face Dependencies Only', al = 'left' )
    cmds.separator()
    atom_rrig_earBuild_checkBox = cmds.checkBox( 'atom_rat_earCheck', l = 'Build Ear Rig', al = 'left', v = True )
    cmds.separator()
    # 'import webrImport as web\natm = web.mod("asset_raptor_lib")\natm.preBuild()'
    atom_rrig_prerigBut = cmds.button( l = 'Build Rat Pre-Rig', c = 'import webrImport as web\natm = web.mod("atom_rat_lib")\natm.preBuild()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Appendages', c = 'import webrImport as web\natm = web.mod("atom_rat_lib")\natm.buildAppendages()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Splines', c = 'import webrImport as web\natm = web.mod("atom_rat_lib")\natm.buildSplines()' )
    atom_rrig_buildDeformBut = cmds.button( l = 'Build Rig Deformation', c = 'import webrImport as web\natm = web.mod("atom_rat_lib")\natm.deform()' )
    atom_rrig_faceRig = cmds.button( l = 'Build Face Rig', c = 'import atom_face_lib as face\nface.buildFace()' )
    atom_rrig_faceRig = cmds.button( l = 'Finalize Rig', c = createTagGroups )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main


def bipedFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_biped_frameLayout', label = 'Biped Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = False )

    atom_rrig_columnLayout = cmds.columnLayout( 'atom_rat_main_columnLayout', adj = True, rs = 5 )
    atom_rrig_faceBuild_checkBox = cmds.checkBox( 'atom_rat_faceCheck', l = 'Build Face Dependencies Only', al = 'left' )
    cmds.separator()
    atom_rrig_earBuild_checkBox = cmds.checkBox( 'atom_rat_earCheck', l = 'Build Ear Rig', al = 'left', v = True )
    cmds.separator()

    atom_rrig_prerigBut = cmds.button( l = 'Build Biped Pre-Rig', c = 'import atom_biped_lib as atm\nimport imp\nimp.reload(atm)\natm.preBuild()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Appendages', c = 'import atom_biped_lib as atm\nimport imp\nimp.reload(atm)\natm.buildAppendages()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Splines', c = 'import atom_biped_lib as atm\natm.buildSplines()' )
    # atom_rrig_buildDeformBut = cmds.button(l='Build Rig Deformation', c='import atom_biped_lib as atm\natm.deform()')
    atom_rrig_faceRig = cmds.button( l = 'Build Geo Inputs', c = 'import atom_face_lib as face\nimport imp\nimp.reload(face)\nface.getGeoInputs()' )
    atom_rrig_faceRig = cmds.button( l = 'Finalize Rig', c = createTagGroups )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main


def reindeerFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_reindeer_frameLayout', label = 'Reindeer Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = True )

    atom_rnrig_columnLayout = cmds.columnLayout( 'atom_reindeer_main_columnLayout', adj = True, rs = 5 )
    atom_rnrig_faceBuild_checkBox = cmds.checkBox( 'atom_reindeer_faceCheck', l = 'Build Face Dependencies Only', al = 'left' )
    cmds.separator()
    atom_rnrig_earBuild_checkBox = cmds.checkBox( 'atom_reindeer_earCheck', l = 'Build Ear Rig', al = 'left', v = True )
    cmds.separator()

    atom_rnrig_prerigBut = cmds.button( l = 'Build Reindeer Pre-Rig', c = 'import atom\natom.atom_reindeer_lib.preBuild()' )
    atom_rnrig_buildQuadLegsBut = cmds.button( l = 'Build Rig Appendages', c = 'import atom\natom.atom_reindeer_lib.buildAppendages()' )
    atom_rnrig_buildSpineBut = cmds.button( l = 'Build Rig Splines', c = 'import atom\natom.atom_reindeer_lib.buildSplines()' )
    atom_rnrig_buildHarnessBut = cmds.button( l = 'Build Rig Harness', c = 'import atom\natom.atom_reindeer_lib.harness()' )
    atom_rnrig_buildDeformBut = cmds.button( l = 'Build Rig Deformation', c = 'import atom\natom.atom_reindeer_lib.deform()' )
    atom_rnrig_faceRig = cmds.button( l = 'Build Face Rig', c = 'import atom\natom.atom_face_lib.buildFace()' )
    atom_rnrig_faceRig = cmds.button( l = 'Finalize Rig', c = createTagGroups )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main


def raptorFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_raptor_frameLayout', label = 'Raptor Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = False )

    atom_rrig_columnLayout = cmds.columnLayout( 'atom_Raptor_main_columnLayout', adj = True, rs = 5 )
    cmds.separator()

    atom_rrig_prerigBut = cmds.button( l = 'Build Raptor Pre-Rig', c = 'import webrImport as web\natm = web.mod("asset_raptor_lib")\natm.preBuild()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Splines', c = 'import webrImport as web\natm = web.mod("asset_raptor_lib")\natm.buildSplines()' )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main


def mosFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_mos_frameLayout', label = 'Mosasaurus Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = True )

    atom_rrig_columnLayout = cmds.columnLayout( 'atom_mos_main_columnLayout', adj = True, rs = 5 )
    cmds.separator()

    atom_rrig_prerigBut = cmds.button( l = 'Build Mosasaurus Pre-Rig', c = 'import webrImport as web\natm = web.mod("asset_mosasaurus_lib")\natm.preBuild()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Mosasaurus Splines', c = 'import webrImport as web\natm = web.mod("asset_mosasaurus_lib")\natm.buildSplines()' )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main


def pteranodonFrameLayout( *args ):
    refresh = RefreshCallBack( 'atom_win' )
    main = cmds.frameLayout( 'atom_pteranodon_frameLayout', label = 'Pteranodon Setup',
                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                            mh = 5, mw = 5, cll = True, cl = True )

    atom_rrig_columnLayout = cmds.columnLayout( 'atom_Pteranodon_main_columnLayout', adj = True, rs = 5 )
    cmds.separator()

    atom_rrig_prerigBut = cmds.button( l = 'Build Pteranodon Pre-Rig', c = 'import webrImport as web\natm = web.mod("asset_pteranodon_lib")\natm.preBuild()' )
    atom_rrig_buildSpineBut = cmds.button( l = 'Build Rig Splines', c = 'import webrImport as web\natm = web.mod("asset_pteranodon_lib")\natm.buildSplines()' )

    cmds.setParent( '..' )
    cmds.setParent( '..' )
    return main

#-------------
# Name        :win
# Arguements  :N/A
# Description :Build the main ATOM window
# Notes       :This is mosly layout, atom_ui_lib has most of the internal functions
#-------------


def win( *args ):
    # WINDOW
    if cmds.window( 'atom_win', ex = True ):
        cmds.deleteUI( 'atom_win' )

    refresh = RefreshCallBack( 'atom_win' )
    # Main Window
    atom_win = cmds.window( 'atom_win', title = 'A T O M', width = 250, height = 500 )

    # Main Scroll Layout
    atom_master_scrollLayout = cmds.scrollLayout( 'atom_master_scrollLayout', vst = 8, cr = True, mcw = 235, saw = 16 )

    # Main Form Layout, some controls are here, most are in their own Frame Layout
    atom_main_formLayout = cmds.formLayout( 'atom_main_formLayout', numberOfDivisions = 100 )

    # Some global information multiple functions will have access to
    atom_prefix_text = cmds.text( 'atom_prefix_text', align = 'left', label = 'Prefix:', width = 35 )
    atom_prefix_textField = cmds.textField( 'atom_prefix_textField', w = 175 )

    atom_gScale_text = cmds.text( 'atom_gScale_text', align = 'left', label = 'Global Scale:', width = 75 )
    atom_gScale_floatField = cmds.floatField( 'atom_qrig_conScale', w = 45, v = 1.0, pre = 3 )
    atom_gEar_checkBox = cmds.checkBox( 'atom_gEar_check', l = 'Build Ear Rig', al = 'left', v = True )
    atom_gBfd_checkBox = cmds.checkBox( 'atom_gBfd_check', l = 'Build Face Dependencies', al = 'left' )

    atom_suffix_text = cmds.text( 'atom_suffix_text', align = 'left', label = 'Suffix:', width = 35 )
    atom_suffix_optionMenu = cmds.optionMenu( 'atom_suffix_optionMenu', w = 65 )
    cmds.menuItem( label = 'L' )
    cmds.menuItem( label = 'R' )
    cmds.menuItem( label = 'none' )
    atom_setChannel_label = cmds.text( 'atom_setChannel', l = 'Set Channels:' )
    atom_setChannel_checkBox = cmds.checkBox( 'atom_setChannel_checkBox', l = '', v = True )
    #--------------------
    # Spline Build Section
    #--------------------

    atom_spln_frameLayout = cmds.frameLayout( 'atom_spln_frameLayout', label = 'Atom Spline Setup',
                                             cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                                             mh = 5, mw = 5, cll = True, cl = True )

    atom_spln_formLayout = cmds.formLayout( 'atom_ffqls_formLayout', numberOfDivisions = 100 )

    atom_spln_rotOrderText = cmds.text( 'atom_spln_rotOrder_text', align = 'left', label = 'Rotate Order:', width = 118 )
    atom_spln_rotOrder_optionMenu = cmds.optionMenu( 'atom_spln_rotOrder_optionMenu' )
    cmds.menuItem( label = 'xyz' )
    cmds.menuItem( label = 'yzx' )
    cmds.menuItem( label = 'zxy' )
    cmds.menuItem( label = 'xzy' )
    cmds.menuItem( label = 'yxz' )
    cmds.menuItem( label = 'zyx' )
    cmds.optionMenu( atom_spln_rotOrder_optionMenu, edit = True, sl = 3 )

    cw1 = 95
    cw2 = 40
    cw3 = 40
    cw4 = 40

    atom_spln_rot_radioButtonGrp = cmds.radioButtonGrp( 'atom_spln_rot_radioButtonGrp', label = 'Rotate Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                       cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 1 )
    atom_spln_aim_radioButtonGrp = cmds.radioButtonGrp( 'atom_spln_aim_radioButtonGrp', label = 'Aim Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                       cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 3 )
    atom_spln_up_radioButtonGrp = cmds.radioButtonGrp( 'atom_spln_up_radioButtonGrp', label = 'Up Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                      cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 2 )

    atom_spln_scaleFactor_text = cmds.text( 'atom_spln_scaleFactor_text', align = 'left', label = 'Control Scale:', width = 72 )
    atom_spln_scaleFactor_floatField = cmds.floatField( 'atom_spln_scaleFactor_floatField', v = 1.0, pre = 1, width = 34 )

    atom_spln_vectorDistance_text = cmds.text( 'atom_spln_vectorDistance_text', align = 'left', label = 'Vector Distance:', width = 92 )
    atom_spln_vectorDistance_floatField = cmds.floatField( 'atom_spln_vectorDistance_floatField', v = 3.0, pre = 1, width = 34 )

    atom_spln_falloff_text = cmds.text( 'atom_spln_falloff_text', align = 'left', label = 'Falloff:', width = 92 )
    atom_spln_falloff_floatField = cmds.floatField( 'atom_spln_falloff_floatField', v = 1.0, pre = 1, width = 34 )

    atom_spln_spline_button = cmds.button( 'atom_spln_spline_button', c = 'import atom_splineStage_lib\natom_splineStage_lib.splineStage(4)', label = 'Create Spline', h = 25 )
    atom_spln_spacerText = cmds.text( 'atom_spln_spacerText', label = ' ', h = 5 )

    cmds.formLayout( atom_spln_formLayout, edit = True,
                    attachForm = [( atom_spln_rotOrderText, 'top', 5 ), ( atom_spln_rotOrderText, 'left', 5 ),
                                ( atom_spln_rotOrder_optionMenu, 'top', 5 ),
                                ( atom_spln_rot_radioButtonGrp, 'left', 5 ), ( atom_spln_rot_radioButtonGrp, 'right', 5 ),
                                ( atom_spln_aim_radioButtonGrp, 'left', 5 ), ( atom_spln_aim_radioButtonGrp, 'left', 5 ),
                                ( atom_spln_up_radioButtonGrp, 'left', 5 ), ( atom_spln_up_radioButtonGrp, 'left', 5 ),
                                ( atom_spln_scaleFactor_text, 'left', 5 ),
                                ( atom_spln_vectorDistance_text, 'left', 5 ),
                                ( atom_spln_falloff_text, 'left', 5 ),
                                ( atom_spln_spline_button, 'left', 5 )],

                    attachOppositeForm = [( atom_spln_rotOrder_optionMenu, 'right', -207 ), ( atom_spln_spline_button, 'right', -207 )],

                    attachControl = [( atom_spln_rotOrder_optionMenu, 'left', 5, atom_spln_rotOrderText ),
                                   ( atom_spln_rot_radioButtonGrp, 'top', 5, atom_spln_rotOrder_optionMenu ),
                                   ( atom_spln_aim_radioButtonGrp, 'top', 5, atom_spln_rot_radioButtonGrp ),
                                   ( atom_spln_up_radioButtonGrp, 'top', 5, atom_spln_aim_radioButtonGrp ),
                                   ( atom_spln_scaleFactor_text, 'top', 8, atom_spln_up_radioButtonGrp ),
                                   ( atom_spln_scaleFactor_floatField, 'top', 5, atom_spln_up_radioButtonGrp ), ( atom_spln_scaleFactor_floatField, 'left', 26, atom_spln_scaleFactor_text ),
                                   ( atom_spln_vectorDistance_text, 'top', 12, atom_spln_scaleFactor_text ),
                                   ( atom_spln_vectorDistance_floatField, 'top', 8, atom_spln_scaleFactor_text ),
                                   ( atom_spln_vectorDistance_floatField, 'left', 5, atom_spln_vectorDistance_text ),
                                   ( atom_spln_falloff_text, 'top', 12, atom_spln_vectorDistance_text ),
                                   ( atom_spln_falloff_floatField, 'top', 5, atom_spln_vectorDistance_text ),
                                   ( atom_spln_falloff_floatField, 'left', 5, atom_spln_falloff_text ),
                                   ( atom_spln_spline_button, 'top', 5, atom_spln_falloff_text ),
                                   ( atom_spln_spacerText, 'top', 5, atom_spln_spline_button )]
                    )
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    #-------------------------
    # Bipedal Limb Setup (bls)
    #-------------------------

    atom_bls_frameLayout = cmds.frameLayout( 'atom_bls_frameLayout', label = 'Atom Bipedal Limb Setup',
                                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                                            mh = 5, mw = 5, cll = True, cl = True )
    atom_bls_formLayout = cmds.formLayout( 'atom_bls_formLayout', numberOfDivisions = 100 )

    atom_bls_limb_text = cmds.text( 'atom_bls_limb_text', align = 'left', label = 'Limb Name:', width = 118 )
    atom_bls_limb_optionMenu = cmds.optionMenu( 'atom_bls_limb_optionMenu' )
    cmds.menuItem( label = 'arm' )
    cmds.menuItem( label = 'finger' )
    cmds.menuItem( label = 'digit' )
    cmds.menuItem( label = 'none' )

    atom_bls_flip_checkBoxGrp = cmds.checkBoxGrp( 'atom_bls_flip_checkBoxGrp', label = 'Flip:', ncb = 3, labelArray3 = ['X', 'Y', 'Z'], cw4 = [cw1, cw2, cw3, cw4],
                                                 cl4 = ['left', 'center', 'center', 'center'], h = 19 )
    atom_bls_limbRot_radioButtonGrp = cmds.radioButtonGrp( 'atom_bls_limbRot_radioButtonGrp', label = 'Rotate Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                          cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 1 )
    atom_bls_limbAim_radioButtonGrp = cmds.radioButtonGrp( 'atom_bls_limbAim_radioButtonGrp', label = 'Aim Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                          cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 3 )
    atom_bls_limbUp_radioButtonGrp = cmds.radioButtonGrp( 'atom_bls_limbUp_radioButtonGrp', label = 'Up Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                         cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 2 )

    atom_bls_ldf_text = cmds.text( 'atom_bls_ldf_text', align = 'left', label = 'Locator Distance Factor:', width = 127 )  # ldf = locator distance factor
    atom_bls_ldf_floatField = cmds.floatField( 'atom_bls_ldf_floatField', v = 1.0, pre = 1, width = 34 )

    atom_bls_scale_text = cmds.text( 'atom_bls_scale_text', align = 'left', label = 'Locator Scale:', width = 72 )
    atom_bls_scale_floatField = cmds.floatField( 'atom_bls_scale_floatField', v = 1.0, pre = 1, width = 34 )

    atom_bls_setChannel_text = cmds.text( 'atom_bls_setChannel_text', align = 'left', label = 'Set Channels:', width = 72 )
    atom_bls_setChannel_checkBox = cmds.checkBox( 'atom_bls_setChannel_checkBox', label = '', v = 1 )

    atom_bls_createLimb_button = cmds.button( 'atom_bls_createLimb_button', c = 'import atom_appendage_lib\natom_appendage_lib.create3jointIK("' + atom_bls_setChannel_checkBox + '")', label = 'Create Limb', h = 25 )
    atom_bls_createDigit_button = cmds.button( 'atom_bls_createDigit_button', c = 'import atom_appendage_lib as aal\nimport imp\nimp.reload(aal)\naal.createDigitCMD("' + atom_bls_setChannel_checkBox + '")', label = 'Create Digit', h = 25 )
    atom_bls_spacerText = cmds.text( 'atom_bls_spacerText', label = ' ', h = 5 )

    cmds.formLayout( atom_bls_formLayout, edit = True,
                    attachForm = [( atom_bls_flip_checkBoxGrp, 'left', 5 ), ( atom_bls_limb_text, 'top', 7 ), ( atom_bls_limb_text, 'left', 5 ),
                                ( atom_bls_limb_optionMenu, 'top', 5 ),
                                ( atom_bls_limbRot_radioButtonGrp, 'left', 5 ),
                                ( atom_bls_limbAim_radioButtonGrp, 'left', 5 ), ( atom_bls_limbUp_radioButtonGrp, 'left', 5 ), ( atom_bls_ldf_text, 'left', 5 ),
                                ( atom_bls_scale_text, 'left', 5 ), ( atom_bls_setChannel_text, 'left', 5 ),
                                ( atom_bls_createLimb_button, 'left', 5 ),
                                ( atom_bls_createDigit_button, 'left', 5 )],

                    attachOppositeForm = [( atom_bls_limb_optionMenu, 'right', -207, ), ( atom_bls_createLimb_button, 'right', -207 ),
                                        ( atom_bls_createDigit_button, 'right', -207 )],

                    attachControl = [( atom_bls_limb_optionMenu, 'left', 5, atom_bls_limb_text ),
                                   ( atom_bls_flip_checkBoxGrp, 'top', 0, atom_bls_limb_text ),
                                   ( atom_bls_limbRot_radioButtonGrp, 'top', 5, atom_bls_flip_checkBoxGrp ),
                                   ( atom_bls_limbAim_radioButtonGrp, 'top', 5, atom_bls_limbRot_radioButtonGrp ),
                                   ( atom_bls_limbUp_radioButtonGrp, 'top', 5, atom_bls_limbAim_radioButtonGrp ),
                                   ( atom_bls_ldf_text, 'top', 9, atom_bls_limbUp_radioButtonGrp ), ( atom_bls_ldf_floatField, 'left', 41, atom_bls_ldf_text ),
                                   ( atom_bls_ldf_floatField, 'top', 5, atom_bls_limbUp_radioButtonGrp ), ( atom_bls_scale_text, 'top', 9, atom_bls_ldf_floatField ),
                                   ( atom_bls_scale_floatField, 'top', 5, atom_bls_ldf_floatField ), ( atom_bls_scale_floatField, 'left', 96, atom_bls_scale_text ),
                                   ( atom_bls_setChannel_text, 'top', 7, atom_bls_scale_text ),
                                   ( atom_bls_setChannel_checkBox, 'top', 5, atom_bls_scale_text ), ( atom_bls_setChannel_checkBox, 'left', 10, atom_bls_setChannel_text ),
                                   ( atom_bls_createLimb_button, 'top', 5, atom_bls_setChannel_text ), ( atom_bls_createDigit_button, 'top', 5, atom_bls_createLimb_button ),
                                   ( atom_bls_spacerText, 'top', 0, atom_bls_createDigit_button )]
                    )

    cmds.setParent( '..' )
    cmds.setParent( '..' )

    #-------------------------
    # Quadruped Leg Setup (qls)
    #-------------------------

    atom_qls_frameLayout = cmds.frameLayout( 'atom_qls_frameLayout', label = 'Atom Quadruped Leg Setup',
                                            cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                                            mh = 5, mw = 5, cll = True, cl = True )
    atom_qls_formLayout = cmds.formLayout( 'atom_qls_formLayout', numberOfDivisions = 100 )

    atom_qls_limb_preset_text = cmds.text( 'atom_qls_limb_preset_text', align = 'left', label = 'Limb Preset:', width = 77 )
    atom_qls_limb_preset_optionMenu = cmds.optionMenu( 'atom_qls_limb_preset_optionMenu', width = 120, cc = 'import atom_ui_lib\natom_ui_lib.setPreset()' )
    cmds.menuItem( label = 'Back Left Leg' )
    cmds.menuItem( label = 'Back Right Leg' )
    cmds.menuItem( label = 'Front Left Leg' )
    cmds.menuItem( label = 'Front Right Leg' )

    atom_qls_limb_text = cmds.text( 'atom_qls_limb_text', align = 'left', label = 'Limb Name:', width = 118 )
    atom_qls_limb_optionMenu = cmds.optionMenu( 'atom_qls_limb_optionMenu' )
    cmds.menuItem( label = 'leg' )
    cmds.menuItem( label = 'none' )

    atom_qls_flip_checkBoxGrp = cmds.checkBoxGrp( 'atom_qls_flip_checkBoxGrp', label = 'Flip:', ncb = 3, labelArray3 = ['X', 'Y', 'Z'], cw4 = [cw1, cw2, cw3, cw4],
                                                 cl4 = ['left', 'center', 'center', 'center'], h = 19 )

    atom_qls_limbRot_radioButtonGrp = cmds.radioButtonGrp( 'atom_qls_limbRot_radioButtonGrp', label = 'Rotate Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                          cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 1 )
    atom_qls_limbAim_radioButtonGrp = cmds.radioButtonGrp( 'atom_qls_limbAim_radioButtonGrp', label = 'Aim Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                          cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 3 )
    atom_qls_limbUp_radioButtonGrp = cmds.radioButtonGrp( 'atom_qls_limbUp_radioButtonGrp', label = 'Up Axis:', labelArray3 = ['X', 'Y', 'Z'], nrb = 3, cw4 = [cw1, cw2, cw3, cw4],
                                                         cl4 = ['left', 'center', 'center', 'center'], h = 19, sl = 2 )
    atom_qls_pvFlip_checkBoxGrp = cmds.checkBoxGrp( 'atom_qls_pvFlip_checkBoxGrp', label = 'PV Flip:', ncb = 3, labelArray3 = ['X', 'Y', 'Z'], cw4 = [cw1, cw2, cw3, cw4],
                                                   cl4 = ['left', 'center', 'center', 'center'], h = 19 )
    atom_qls_anklePvFlip_floatFieldGrp = cmds.floatFieldGrp( 'atom_qls_anklePvFlip_floatFieldGrp', label = 'Ankle Loc Pos:', numberOfFields = 3, value1 = 0, value2 = -5, value3 = 5,
                                                            cw4 = [cw1, cw2 - 4, cw3 - 4, cw4 - 5], cl4 = ['left', 'center', 'center', 'center'], h = 19 )

    atom_qls_ldf_text = cmds.text( 'atom_qls_ldf_text', align = 'left', label = 'Locator Distance Factor:', width = 127 )  # ldf = locator distance factor
    atom_qls_ldf_floatField = cmds.floatField( 'atom_qls_ldf_floatField', v = 10.0, pre = 1, width = 34 )

    atom_qls_scale_text = cmds.text( 'atom_qls_scale_text', align = 'left', label = 'Locator Scale:', width = 72 )
    atom_qls_scale_floatField = cmds.floatField( 'atom_qls_scale_floatField', v = 1.0, pre = 1, width = 34 )

    atom_qls_paw_ldf_text = cmds.text( 'atom_paw_qls_ldf_text', align = 'left', label = 'Paw Loc Distance Factor:', width = 130 )  # ldf = locator distance factor
    atom_qls_paw_ldf_floatField = cmds.floatField( 'atom_paw_qls_ldf_floatField', v = 3.25, pre = 1, width = 34 )

    atom_qls_paw_scale_text = cmds.text( 'atom_qls_paw_scale_text', align = 'left', label = 'Paw Digit Loc Scale:', width = 104 )
    atom_qls_paw_scale_floatField = cmds.floatField( 'atom_qls_paw_scale_floatField', v = .5, pre = 1, width = 34 )

    atom_qls_createLimb_button = cmds.button( 'atom_qls_createLimb_button', c = 'import atom_appendage_lib\natom_appendage_lib.createReverseLeg()', label = 'Create Quadruped Limb', h = 25 )
    atom_qls_spacerText = cmds.text( 'atom_qls_spacerText', label = ' ', h = 5 )

    cmds.formLayout( atom_qls_formLayout, edit = True,
                    attachForm = [( atom_qls_limb_preset_text, 'left', 5 ), ( atom_qls_limb_preset_text, 'top', 7 ),
                                ( atom_qls_limb_preset_optionMenu, 'top', 5 ),
                                ( atom_qls_flip_checkBoxGrp, 'left', 5 ), ( atom_qls_limb_text, 'left', 5 ),
                                ( atom_qls_limb_optionMenu, 'top', 5 ),
                                ( atom_qls_limbRot_radioButtonGrp, 'left', 5 ),
                                ( atom_qls_limbAim_radioButtonGrp, 'left', 5 ), ( atom_qls_limbUp_radioButtonGrp, 'left', 5 ),
                                ( atom_qls_pvFlip_checkBoxGrp, 'left', 5 ), ( atom_qls_ldf_text, 'left', 5 ),
                                ( atom_qls_anklePvFlip_floatFieldGrp, 'left', 5 ),
                                ( atom_qls_scale_text, 'left', 5 ), ( atom_qls_createLimb_button, 'left', 5 ),
                                ( atom_qls_paw_ldf_text, 'left', 5 ), ( atom_qls_paw_scale_text, 'left', 5 )],

                    attachOppositeForm = [( atom_qls_limb_optionMenu, 'right', -207, ), ( atom_qls_createLimb_button, 'right', -207 )],

                    attachControl = [( atom_qls_limb_text, 'top', 7, atom_qls_limb_preset_text ),
                                   ( atom_qls_limb_preset_optionMenu, 'left', 5, atom_qls_limb_preset_text ),
                                   ( atom_qls_limb_optionMenu, 'top', 5, atom_qls_limb_preset_optionMenu ),
                                   ( atom_qls_limb_optionMenu, 'left', 5, atom_qls_limb_text ),
                                   ( atom_qls_flip_checkBoxGrp, 'top', 0, atom_qls_limb_text ),
                                   ( atom_qls_limbRot_radioButtonGrp, 'top', 5, atom_qls_flip_checkBoxGrp ),
                                   ( atom_qls_limbAim_radioButtonGrp, 'top', 5, atom_qls_limbRot_radioButtonGrp ),
                                   ( atom_qls_limbUp_radioButtonGrp, 'top', 5, atom_qls_limbAim_radioButtonGrp ),
                                   ( atom_qls_pvFlip_checkBoxGrp, 'top', 5, atom_qls_limbUp_radioButtonGrp ),
                                   ( atom_qls_anklePvFlip_floatFieldGrp, 'top', 5, atom_qls_pvFlip_checkBoxGrp ),
                                   ( atom_qls_ldf_text, 'top', 9, atom_qls_anklePvFlip_floatFieldGrp ), ( atom_qls_ldf_floatField, 'left', 41, atom_qls_ldf_text ),
                                   ( atom_qls_ldf_floatField, 'top', 5, atom_qls_anklePvFlip_floatFieldGrp ), ( atom_qls_scale_text, 'top', 9, atom_qls_ldf_floatField ),
                                   ( atom_qls_scale_floatField, 'top', 5, atom_qls_ldf_floatField ), ( atom_qls_scale_floatField, 'left', 96, atom_qls_scale_text ),
                                   ( atom_qls_paw_ldf_text, 'top', 9, atom_qls_scale_text ),
                                   ( atom_qls_paw_ldf_floatField, 'top', 5, atom_qls_scale_text ), ( atom_qls_paw_ldf_floatField, 'left', 38, atom_qls_paw_ldf_text ),
                                   ( atom_qls_paw_scale_text, 'top', 9, atom_qls_paw_ldf_text ),
                                   ( atom_qls_paw_scale_floatField, 'top', 5, atom_qls_paw_ldf_floatField ), ( atom_qls_paw_scale_floatField, 'left', 96, atom_qls_scale_text ),
                                   ( atom_qls_createLimb_button, 'top', 5, atom_qls_paw_scale_text ), ( atom_qls_spacerText, 'top', 0, atom_qls_createLimb_button )]
                    )

    cmds.setParent( '..' )
    cmds.setParent( '..' )

    #---------------------------
    # Quadriped Rigging
    #---------------------------

    atom_qrig_frameLayout = cmds.frameLayout( 'atom_qrig_frameLayout', label = 'Quad Rig',
                                             cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                                             mh = 5, mw = 5, cll = True, cl = True )

    atom_qrig_columnLayout = cmds.columnLayout( 'atom_qrig_main_columnLayout', adj = True, rs = 5 )
    atom_qrig_faceBuild_checkBox = cmds.checkBox( 'atom_qrig_faceCheck', l = 'Build Face Dependencies Only', al = 'left' )
    cmds.separator()
    # cmds.text('Controller Scale:',width=30, al='left')
    # atom_qrig_faceBuild_conScale = cmds.floatField('atom_qrig_conScale', minValue=0, maxValue=100, value=1, precision=2)
    atom_qrig_prerigBut = cmds.button( l = 'Create Quadriped Pre-Rig', c = 'import atom\natom.atom_quadPreBuild_lib.quadPreBuild()' )
    atom_qrig_buildQuadLegsBut = cmds.button( l = 'Build Quadriped Legs', c = 'import atom\natom.atom_quadLeg_lib.buildQuadripedLegs()' )
    atom_qrig_buildSpineBut = cmds.button( l = 'Build Quadriped Splines', c = 'import atom\natom.atom_quadSplines_lib.quadSplines()' )
    atom_qrig_buildDeformBut = cmds.button( l = 'Build Quadriped Deformation', c = 'import atom\natom.atom_quadDeformation_lib.quadDeform()' )
    atom_qrig_faceRig = cmds.button( l = 'Build Face Rig', c = 'import atom\natom.atom_face_lib.buildFace()' )
    atom_qrig_accessRig = cmds.button( l = 'Build Accessories', c = 'import atom\natom.atom_accessory_lib.buildAccessories()' )
    atom_qrig_finalRig = cmds.button( l = 'Finalize Rig', c = createTagGroups )
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    '''
    # Snake Rig
    atom_srig_frameLayout = cmds.frameLayout('atom_srig_frameLayout', label='Snake Setup',
                                             cc=refresh.RefreshCall, ec=refresh.RefreshCall,
                                             mh=5, mw=5, cll=True, cl=True)

    atom_srig_columnLayout = cmds.columnLayout('atom_srig_main_columnLayout', adj=True, rs=5)
    cmds.text('Controller Scale:', width=30, al='left')
    atom_srig_faceBuild_conScale = cmds.floatField('atom_srig_conScale', minValue=0, maxValue=100, value=1, precision=2)
    cmds.separator()
    atom_qrig_prerigBut = cmds.button(l='Build Snake Pre-Rig', c='import atom\natom.atom_snakeSimplePreBuild_lib.snakePreBuild()')
    atom_qrig_buildSpineBut = cmds.button(l='Build Snake Splines', c='import atom\natom.atom_snakeSimpleSplines_lib.snakeSplines()')
    atom_qrig_buildDeformBut = cmds.button(l='Build Snake Deformation', c='import atom\natom.atom_snakeDeformation_lib.snakeDeform()')
    bldSnkFace = BuildSnakeFacerigCallback()
    atom_qrig_faceRig = cmds.button(l='Build Face Rig', c=bldSnkFace.CMD)
    atom_qrig_faceRig = cmds.button(l='Finalize Rig', c=createTagGroups)
    cmds.setParent('..')
    cmds.setParent('..')
    '''

    atom_rat_frameLayout = ratFrameLayout()

    # atom_reindeer_frameLayout = reindeerFrameLayout()

    atom_biped_frameLayout = bipedFrameLayout()

    # atom_raptor_frameLayout = raptorFrameLayout()

    atom_mos_frameLayout = mosFrameLayout()

    atom_pteranodon_frameLayout = pteranodonFrameLayout()

    #---------------------------
    # Control Curve Shape Toolbox
    #---------------------------
    atom_ccst_frameLayout = cmds.frameLayout( 'atom_ccst_frameLayout', label = 'Control Curve Shape Toolbox',
                                             cc = refresh.RefreshCall, ec = refresh.RefreshCall,
                                             mh = 5, mw = 5, cll = False, cl = True )

    atom_ccst_columnLayout = cmds.columnLayout( 'atom_ccst_main_columnLayout', adj = True, rs = 5 )
    import webrImport as web
    # web
    ac = web.mod( 'atom_controlShapes_lib' )
    atom_ccst_path = ac.shapeDir()
    atom_ccst_formLayout = cmds.formLayout( 'atom_csst_formLayout', numberOfDivisions = 100 )
    # atom_csst_exportPath_text = cmds.text('atom_csst_exportPath_text', label='Export Path:', align='left', width=70, height=14)
    # atom_csst_exportPath_textField = cmds.textField('atom_csst_exportPath_textField', text=atom_ccst_path)
    atom_csst_exportName_text = cmds.text( 'atom_csst_exportName_text', label = 'Export Name:', align = 'left', width = 71, height = 14 )
    atom_csst_exportName_textField = cmds.textField( 'atom_csst_exportName_textField', text = 'None', cc = 'import atom_ui_lib\natom_ui_lib.validateFieldTextInput("atom_csst_exportName_textField")' )
    atom_csst_exportName_button = cmds.button( 'atom_csst_exportName_button', label = 'Export Curve Shape', c = 'import webrImport as web\naul = web.mod("atom_ui_lib")\naul.exportCurveShape()' )
    atom_csst_separatorTop = cmds.separator( 'atom_csst_separatorTop', h = 5 )
    atom_csst_importName_text = cmds.text( 'atom_csst_importName_text', label = 'Import Curve Shape' )
    atom_csst_separatorBottom = cmds.separator( 'atom_csst_separatorBottom' )
    atom_csst_curveScale_text = cmds.text( 'atom_csst_curveScale_text', label = 'Import Curve Scale:', align = 'left', width = 105, height = 14 )
    atom_csst_curveScale_floatField = cmds.floatField( 'atom_csst_curveScale_floatField', v = 1.0, pre = 1, width = 34 )
    cmds.setParent( '..' )
    # Dynamically create button based on saved .txt file with cv positional data in them
    uil.addControlCurveButton( atom_ccst_path )

    cmds.formLayout( atom_ccst_formLayout, edit = True,
                    attachForm = [( atom_csst_exportName_text, 'left', 0 ), ( atom_csst_exportName_button, 'left', 0 ),
                                ( atom_csst_separatorTop, 'left', 0 ),
                                ( atom_csst_importName_text, 'left', 0 ),
                                ( atom_csst_separatorBottom, 'left', 0 ),
                                ( atom_csst_exportName_button, 'right', 0 ),
                                ( atom_csst_separatorTop, 'right', 0 ),
                                ( atom_csst_importName_text, 'right', 0 ),
                                ( atom_csst_separatorBottom, 'right', 0 ),
                                ( atom_csst_exportName_textField, 'right', 0 ),
                                ( atom_csst_curveScale_floatField, 'right', 0 )],
                    attachControl = [( atom_csst_exportName_textField, 'left', 5, atom_csst_exportName_text ),
                                   ( atom_csst_exportName_button, 'top', 5, atom_csst_exportName_textField ),
                                   ( atom_csst_separatorTop, 'top', 5, atom_csst_exportName_button ),
                                   ( atom_csst_importName_text, 'top', 5, atom_csst_separatorTop ),
                                   ( atom_csst_separatorBottom, 'top', 0, atom_csst_importName_text ),
                                   ( atom_csst_curveScale_floatField, 'top', 5, atom_csst_separatorBottom ),
                                   ( atom_csst_curveScale_floatField, 'left', 5, atom_csst_curveScale_text ),
                                   ( atom_csst_curveScale_text, 'top', 10, atom_csst_separatorBottom )]
                    )
    cmds.setParent( '..' )
    cmds.setParent( '..' )

    #---------------------
    # Main Form Layout Edit
    #---------------------
    cmds.formLayout( atom_main_formLayout, edit = True,
                    attachForm = [( atom_prefix_text, 'top', 9 ), ( atom_prefix_text, 'left', 5 ),
                                ( atom_gScale_text, 'left', 5 ), ( atom_suffix_text, 'left', 5 ),
                                ( atom_setChannel_label, 'left', 5 ),
                                ( atom_gBfd_checkBox, 'left', 5 ),
                                ( atom_gEar_checkBox, 'left', 5 ),
                                ( atom_spln_frameLayout, 'left', 5 ), ( atom_spln_frameLayout, 'right', 5 ),
                                ( atom_bls_frameLayout, 'left', 5 ), ( atom_bls_frameLayout, 'right', 5 ),
                                ( atom_qls_frameLayout, 'left', 5 ), ( atom_qls_frameLayout, 'right', 5 ),
                                ( atom_qrig_frameLayout, 'left', 5 ), ( atom_qrig_frameLayout, 'right', 5 ),
                                ( atom_biped_frameLayout, 'left', 5 ), ( atom_biped_frameLayout, 'right', 5 ),
                                ( atom_rat_frameLayout, 'left', 5 ), ( atom_rat_frameLayout, 'right', 5 ),
                                ( atom_mos_frameLayout, 'left', 5 ), ( atom_mos_frameLayout, 'right', 5 ),
                                ( atom_pteranodon_frameLayout, 'left', 5 ), ( atom_pteranodon_frameLayout, 'right', 5 ),
                                ( atom_ccst_frameLayout, 'left', 5 ), ( atom_ccst_frameLayout, 'right', 5 )],

                    attachControl = [( atom_prefix_textField, 'left', 5, atom_prefix_text ),
                                   ( atom_gScale_text, 'top', 9, atom_prefix_text ),
                                   ( atom_gScale_floatField, 'left', 5, atom_gScale_text ),
                                   ( atom_gScale_floatField, 'top', 5, atom_prefix_text ),
                                   ( atom_suffix_text, 'top', 9, atom_gScale_text ),
                                   ( atom_suffix_optionMenu, 'top', 5, atom_gScale_text ),
                                   ( atom_suffix_optionMenu, 'left', 74, atom_gScale_text ),
                                   ( atom_setChannel_label, 'top', 8, atom_suffix_text ),
                                   ( atom_setChannel_checkBox, 'top', 5, atom_suffix_text ),
                                   ( atom_setChannel_checkBox, 'left', 128, atom_setChannel_label ),
                                   ( atom_gBfd_checkBox, 'top', 8, atom_setChannel_label ),
                                   ( atom_gEar_checkBox, 'top', 8, atom_gBfd_checkBox ),
                                   ( atom_spln_frameLayout, 'top', 5, atom_gEar_checkBox ),
                                   ( atom_bls_frameLayout, 'top', 5, atom_spln_frameLayout ),
                                   ( atom_qls_frameLayout, 'top', 5, atom_bls_frameLayout ),
                                   ( atom_qrig_frameLayout, 'top', 5, atom_qls_frameLayout ),
                                   ( atom_biped_frameLayout, 'top', 5, atom_qrig_frameLayout ),
                                   ( atom_rat_frameLayout, 'top', 5, atom_biped_frameLayout ),
                                   ( atom_mos_frameLayout, 'top', 5, atom_rat_frameLayout ),
                                   ( atom_pteranodon_frameLayout, 'top', 5, atom_mos_frameLayout ),
                                   ( atom_ccst_frameLayout, 'top', 5, atom_pteranodon_frameLayout )]
                    )
    cmds.showWindow( atom_win )
    cmds.window( 'atom_win', edit = True, width = 254 )
    cmds.window( 'atom_win', edit = True, width = 255 )
# win()
