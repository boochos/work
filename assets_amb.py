import maya.cmds as cmds
import webrImport as web

#
# web
cn = web.mod( 'constraint_lib' )
ac = web.mod( 'animCurve_lib' )


def match_paths_r():
    '''
    
    '''
    print( 'here' )
    i = 0
    while i < 20:
        src_amb = 'lay:Amb_01:UACR1:UACR_path_straight.cv[' + str( i ) + ']'
        des_amb = 'amb_r:UACR1:UACR_path_straight.cv[' + str( i ) + ']'
        x = cmds.xform( src_amb, q = True, t = True, ws = True )
        print( x )
        cmds.xform( des_amb, t = x, ws = True )
        i = i + 1
        if i >= 20:
            return None


def match_paths_l():
    '''
    
    '''
    print( 'here' )
    i = 0
    while i < 20:
        src_amb = 'lay:Amb_02:UACR1:UACR_path_straight.cv[' + str( i ) + ']'
        des_amb = 'amb_l:UACR1:UACR_path_straight.cv[' + str( i ) + ']'
        x = cmds.xform( src_amb, q = True, t = True, ws = True )
        print( x )
        cmds.xform( des_amb, t = x, ws = True )
        i = i + 1
        if i >= 20:
            return None
