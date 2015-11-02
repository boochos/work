import maya.cmds as cmds
import maya.mel as mel


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya:
        mel.eval('print \"' + what + '\";')
    else:
        print what


def zero():
    # does not account for custom attributes
    # could add another loop for custom attrs
    sel = cmds.ls(sl=True)
    # predefined attrs
    transform = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    scale = ["scaleX", "scaleY", "scaleZ"]
    custom = {'footTilt': 1, 'blender': 1, 'kneeTwist': 0}

    # make sure object selected
    if len(sel) != 0:
        # loop through objects in selection array
        for i in sel:
            # find keyable and unlocked attrs for selected object
            keyable = cmds.listAttr(i, k=True, u=True)
            # loop through predefined attrs in transform[]
            for attr in keyable:
                if attr in transform:
                    cmds.setAttr(i + "." + attr, 0)
            # loop through predefined attrs in $scale array
            for attr in keyable:
                if attr in scale:
                    cmds.setAttr(i + "." + attr, 1)
            # loop through predefined attrs in $custom array
            for attr in keyable:
                for k, v in custom.iteritems():
                    if attr == k:
                        cmds.setAttr(i + "." + attr, v)
    else:
        message('Select at least one object')
