import maya.cmds as cmds
import maya.mel as mel


def removeRogueModelPanelChangeEvents():
    EVIL_METHOD_NAMES = ['DCF_updateViewportList', 'CgAbBlastPanelOptChangeCallback', 'onModelChange3dc']
    capitalEvilMethodNames = [name.upper() for name in EVIL_METHOD_NAMES]
    modelPanelLabel = mel.eval( 'localizedPanelLabel("ModelPanel")' )
    processedPanelNames = []
    panelName = cmds.sceneUIReplacement( getNextPanel = ( 'modelPanel', modelPanelLabel ) )
    while panelName and panelName not in processedPanelNames:
        editorChangedValue = cmds.modelEditor( panelName, query = True, editorChanged = True )
        parts = editorChangedValue.split( ';' )
        newParts = []
        changed = False
        for part in parts:
            for evilMethodName in capitalEvilMethodNames:
                if evilMethodName in part.upper():
                    changed = True
                    break
            else:
                newParts.append( part )
        if changed:
            cmds.modelEditor( panelName, edit = True, editorChanged = ';'.join( newParts ) )
            print( "Model panel error fixed!" ),
        processedPanelNames.append( panelName )
        panelName = cmds.sceneUIReplacement( getNextPanel = ( 'modelPanel', modelPanelLabel ) )


removeRogueModelPanelChangeEvents()
