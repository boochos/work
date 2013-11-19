import os
import maya.cmds as cmds
import atom_face_lib as afl

def buildCorrectiveBody(*args):
    #Assume that the current open file has been opened from the correct directory and get the base path from that
    path          = os.path.dirname(cmds.file(query=True, exn=True))          

    #Files to import
    importList    = ['bodyCorrective']
   
    #Geo to connect inMesh
    to_geoList    = ['body_Geo']
    
    #import the face assets
    afl.importFaceAssets(path, importList)
    
    if cmds.objExists('corrective_body_Geo'):
        #extract the shape and orig nodes from their transforms
        body      = afl.extractShapeNode('body_Geo',   False)
        bodyOrig  = afl.extractShapeNode('body_Geo',   True)
        corBody   = afl.extractShapeNode('corrective_body_Geo', False)
        
        #Duplicate the head_Geo, this is used and an intermediate from the head_Geo and the blendshapes
        bodyInter  = cmds.duplicate(body, name= body + '_intermediateGeo')[0]
        
        #create the blendShape
        blendNode = cmds.blendShape(corBody, bodyInter, n='body_blendshape')
        #set the blendNode target weights
        trgCnt = len(cmds.blendShape(blendNode, query=True, t=True))
        for i in range(0,trgCnt,1):
            cmds.blendShape(blendNode, edit=True, w=(i,0))
       
        #Visibility list
        setVisList = [bodyInter]
        
        #Connect the blendShape to the Orig node    
        cmds.connectAttr(blendNode[0] + '.outputGeometry[0]', bodyOrig + '.inMesh', force=True, )
        
        afl.setFaceItemsVis(setVisList)
        cmds.delete('corrective_body_Geo')