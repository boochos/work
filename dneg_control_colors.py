from maya import cmds


def change_color( name = '', color = 17 ):
    '''
    only works for primary control, no other considerations
    overrideColor
    '''
    found = False
    try:
        cons = cmds.listConnections( name + '.priority', type = 'choice' )
        # print(cons)
        for c in cons:
            if 'Colour' in c:
                cmds.setAttr( c + '.primaryControlColourIndex', color )
                found = True
    except:
        pass
    if not found:
        cmds.setAttr( name + 'Shape.overrideColor', color )


def change_color_red():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 4 )


def change_color_blue():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 6 )


def change_color_magenta():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 9 )


def change_color_brown():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 10 )


def change_color_brightGreen():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 14 )


def change_color_yellow():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 17 )


def change_color_lightBlue():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 18 )


def change_color_pink():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 20 )


def change_color_green():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 7 )


def change_color_purple():
    '''
    multi select, specific color
    '''
    sel = cmds.ls( sl = 1 )
    for s in sel:
        change_color( s, 30 )

# soft mod colors
# character01carnivorousTree01body01:softMod_root07OffsetCtrlColour_choice
# character01carnivorousTree01body01:softMod_root07CtrlColour_choice
# primaryControlColourIndex


'''
for i in range( 1, 9 ):
    print( i )'''


'''
import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_purple()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_red()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_blue()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_magenta()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_brightGreen()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_pink()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_lightBlue()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_brown()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_green()

import imp
import dneg_control_colors as dcc
imp.reload(dcc)
dcc.change_color_yellow()
'''
