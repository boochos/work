import maya.cmds as cmds
import maya.mel as mel


def message( what = '', maya = True ):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval( 'print \"' + what + '\";' )
    else:
        print( what )


def zero( obj = '' ):
    # does not account for custom attributes
    # could add another loop for custom attrs
    sel = []
    if not obj:
        sel = cmds.ls( sl = True )
    else:
        sel = [obj]
    # predefined attrs
    transform = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    scale = ["scaleX", "scaleY", "scaleZ"]
    custom = {'footTilt': 0, 'blender': 0, 'KneeTwist': 0, 'index': 0, 'middle': 0, 'ring': 0,
              'openclose': 0, 'Spread_toes': 0, 'rotateToes': 0}

    # make sure object selected
    if len( sel ) != 0:
        # loop through objects in selection array
        for i in sel:
            # find keyable and unlocked attrs for selected object
            keyable = cmds.listAttr( i, k = True, u = True )
            # loop through predefined attrs in transform[]
            for attr in keyable:
                if attr in transform:
                    cmds.setAttr( i + "." + attr, 0 )
                else:
                    print( 'no trans' )
            # loop through predefined attrs in $scale array
            for attr in keyable:
                if attr in scale:
                    cmds.setAttr( i + "." + attr, 1 )
            # loop through predefined attrs in $custom array
            for attr in keyable:
                for key in custom.keys():
                    if attr == key:
                        cmds.setAttr( i + "." + attr, custom[key] )
    else:
        message( 'Select at least one object' )


def zeroRotations( obj ):
    '''
    
    '''
    cmds.setAttr( obj + '.rotateX', 0 )
    cmds.setAttr( obj + '.rotateY', 0 )
    cmds.setAttr( obj + '.rotateZ', 0 )
