from maya import cmds
import maya.internal.nodes.proximitywrap.node_interface as node_interface
import rig.utils.attach
import rig.utils.attribute
import rig.utils.deformer
import rig.utils.name


def assign_old_texture( nameSpace = 'body01' ):
    # cmds.file('/jobs/OGN/kong_dev/maya/renderData/shaders/animShaders.ma', i=True, mergeNamespacesOnClash=False, rpr='animShaders')
    body = ['%s:teethUpper_11__organic_skin_geo' % nameSpace, '%s:teethUpper_10__organic_skin_geo' % nameSpace, '%s:teethUpper_09__organic_skin_geo' % nameSpace,
            '%s:teethUpper_08__organic_skin_geo' % nameSpace, '%s:teethUpper_07__organic_skin_geo' % nameSpace, '%s:teethUpper_06__organic_skin_geo' % nameSpace,
            '%s:teethUpper_05__organic_skin_geo' % nameSpace, '%s:teethUpper_04__organic_skin_geo' % nameSpace, '%s:teethUpper_16__organic_skin_geo' % nameSpace,
            '%s:teethUpper_15__organic_skin_geo' % nameSpace, '%s:teethUpper_14__organic_skin_geo' % nameSpace, '%s:teethUpper_13__organic_skin_geo' % nameSpace,
            '%s:teethUpper_12__organic_skin_geo' % nameSpace, '%s:teethLower_11__organic_skin_geo' % nameSpace, '%s:teethLower_10__organic_skin_geo' % nameSpace,
            '%s:teethLower_09__organic_skin_geo' % nameSpace, '%s:teethLower_08__organic_skin_geo' % nameSpace, '%s:teethLower_07__organic_skin_geo' % nameSpace,
            '%s:teethLower_06__organic_skin_geo' % nameSpace, '%s:teethLower_05__organic_skin_geo' % nameSpace, '%s:teethLower_04__organic_skin_geo' % nameSpace,
            '%s:teethUpper_03__organic_skin_geo' % nameSpace, '%s:teethUpper_02__organic_skin_geo' % nameSpace, '%s:teethUpper_01__organic_skin_geo' % nameSpace,
            '%s:teethLower_16__organic_skin_geo' % nameSpace, '%s:teethLower_15__organic_skin_geo' % nameSpace, '%s:teethLower_14__organic_skin_geo' % nameSpace,
            '%s:teethLower_13__organic_skin_geo' % nameSpace, '%s:teethLower_12__organic_skin_geo' % nameSpace, '%s:fingerNailsR_05__organic_skin_geo' % nameSpace,
            '%s:fingerNailsR_04__organic_skin_geo' % nameSpace, '%s:fingerNailsR_03__organic_skin_geo' % nameSpace, '%s:fingerNailsR_02__organic_skin_geo' % nameSpace,
            '%s:fingerNailsR_01__organic_skin_geo' % nameSpace, '%s:toeNailsL_05__organic_skin_geo' % nameSpace, '%s:toeNailsL_04__organic_skin_geo' % nameSpace,
            '%s:toeNailsL_03__organic_skin_geo' % nameSpace, '%s:teethLower_03__organic_skin_geo' % nameSpace, '%s:teethLower_02__organic_skin_geo' % nameSpace,
            '%s:teethLower_01__organic_skin_geo' % nameSpace, '%s:toeNailsR_05__organic_skin_geo' % nameSpace, '%s:toeNailsR_04__organic_skin_geo' % nameSpace,
            '%s:toeNailsR_03__organic_skin_geo' % nameSpace, '%s:toeNailsR_02__organic_skin_geo' % nameSpace, '%s:toeNailsR_01__organic_skin_geo' % nameSpace,
            '%s:toeNailsL_02__organic_skin_geo' % nameSpace, '%s:toeNailsL_01__organic_skin_geo' % nameSpace, '%s:fingerNailsL_05__organic_skin_geo' % nameSpace,
            '%s:fingerNailsL_04__organic_skin_geo' % nameSpace, '%s:fingerNailsL_03__organic_skin_geo' % nameSpace, '%s:fingerNailsL_02__organic_skin_geo' % nameSpace,
            '%s:fingerNailsL_01__organic_skin_geo' % nameSpace, '%s:body__organic_skin_geo' % nameSpace, '%s:L_tearLine__organic_skin_geo' % nameSpace,
            '%s:R_tearLine__organic_skin_geo' % nameSpace]
    cmds.select( body )
    cmds.hyperShade( assign = '%s:body' % nameSpace )
    cmds.select( cl = True )

    iris = ['%s:L_irisBack__organic_skin_geo' % nameSpace, '%s:L_irisFront__organic_skin_geo' % nameSpace, '%s:L_irisIpes__organic_skin_geo' % nameSpace,
    '%s:R_irisBack__organic_skin_geo' % nameSpace, '%s:R_irisFront__organic_skin_geo' % nameSpace, '%s:R_irisIpes__organic_skin_geo' % nameSpace]
    cmds.select( iris )
    cmds.hyperShade( assign = '%s:iris' % nameSpace )
    cmds.select( cl = True )

    outerEye = ['%s:L_outerEye__organic_skin_geo' % nameSpace, '%s:R_outerEye__organic_skin_geo' % nameSpace]
    cmds.select( outerEye )
    cmds.hyperShade( assign = '%s:sclera' % nameSpace )
    cmds.select( cl = True )

    meniscus = ['%s:L_meniscus__organic_skin_geo' % nameSpace, '%s:R_meniscus__organic_skin_geo' % nameSpace]
    cmds.select( meniscus )
    cmds.hyperShade( assign = '%s:meniscus3' % nameSpace )
    cmds.select( cl = True )

    furCard = ['%s:furEnvelope_5_geo' % nameSpace, '%s:cards_geo' % nameSpace, '%s:cardsScalp_geo' % nameSpace,
               '%s:cardsCheeks_geo' % nameSpace, '%s:furEnvelope_1_geo' % nameSpace]
    cmds.select( furCard )
    cmds.hyperShade( assign = '%s:fur' % nameSpace )
    cmds.select( cl = True )


def qualify():
    ns = ''
    sel = cmds.ls( sl = True )
    if sel:
        if ':' in sel[0]:
            ns = sel[0].split( ':' )[0]
            print( ns )
            assign_old_texture( nameSpace = ns )
            cmds.setAttr( ns + ':preferences.furCard', 0 )
        else:
            cmds.warning( 'Select a control on the body rig, with a namespace' )
    else:
        cmds.warning( 'Select a control on the body rig, with a namespace' )
    cmds.select( sel )


qualify()
