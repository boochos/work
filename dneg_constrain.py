import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds
import maya.mel as mel
import webrImport as web

#
# web
cs = web.mod( 'characterSet_lib' )
hj = web.mod( 'hijack_lib' )
fr = web.mod( 'frameRange_lib' )
plc = web.mod( 'atom_place_lib' )


def constrain_loop():
    '''
    first item in selection is driver, the rest are driven
    '''
    #
    driven = cmds.ls( sl = 1 )
    driver = driven[0]
    driven.remove( driver )
    for i in driven:
        con = cmds.parentConstraint( driver, i, skipRotate = 'none', mo = True )[0]
