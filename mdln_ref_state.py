import maya.cmds as cmds
import maya.mel as mel


def load_offloaded( find = '' ):
    '''
    
    '''
    #
    rfs = cmds.ls( typ = 'reference' )
    for ref in rfs:
        stt = True
        try:
            stt = cmds.referenceQuery( ref, isLoaded = True )
        except:
            pass
        if not stt:
            if find:
                if find in ref:
                    cmds.file( lr = ref, lrd = 'all' )
            else:
                cmds.file( lr = ref, lrd = 'all' )


def offload_loaded( find = '' ):
    '''
    
    '''
    #
    rfs = cmds.ls( typ = 'reference' )
    for ref in rfs:
        stt = False
        try:
            stt = cmds.referenceQuery( ref, isLoaded = True )
        except:
            pass
        if stt:
            if find:
                if find in ref:
                    cmds.file( ur = ref )
            else:
                cmds.file( ur = ref )

