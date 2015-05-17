import maya.cmds as cmds
import atom_miscellaneous_lib as misc
import atom_placement_lib as place
import constraint_lib as cn


def attach(up='', reverse=False):
    # select control and path namespace
    sel = cmds.ls(sl=True)
    path = sel[len(sel) - 1]
    path = path.split(':')[0] + ':path'
    # remove path from list
    sel.remove(sel[len(sel) - 1])
    i = 0
    mlt = 1.0 / len(sel)
    s = 0.0
    e = 0.3
    locs = []
    for ct in sel:
        cmds.select(ct)
        loc = cn.locatorOnSelection(constrain=False)
        locs.append(loc[0])
        min = cmds.playbackOptions(q=True, minTime=True)
        max = cmds.playbackOptions(q=True, maxTime=True)
        cmds.parentConstraint(loc, ct, mo=True)
        # add world up object to path
        if not reverse:
            cmds.pathAnimation(loc, c=path, startTimeU=min, endTimeU=max, startU=s, endU=e, follow=True, wut='object', wuo=up)
        else:
            cmds.pathAnimation(loc, c=path, startTimeU=min, endTimeU=max, startU=e, endU=s, follow=True, wut='object', wuo=up)
        i = i + 1
        s = s + mlt
        e = e + mlt
    cmds.select(clear=True)
    grp = cmds.group(name='__PATH_GRP__#', em=True)
    cmds.parent(locs, grp)
    cmds.select(locs)


def path(*args):

    # select existing Joint Chain and create List----------------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    cmds.select ('upperD_jnt_05', hi=True)
    names=cmds.ls(sl=True)

    #rename Joint Chain--------------------------------------------------------------------------------------------------------------------------------------------------------------------

    i=0
    for jnt in names:
        jntName = cmds.rename(jnt, 'pathJnt_' + str(('%0'+ str(3) + 'd')%(i)))
        i=i+1

    cmds.rename('pathJnt_000','root_jnt')
    newSpine=cmds.ls(sl=True)
    '''
    # Build Pre-Rig-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # creates groups and master controller from arguments specified as 'True'

    misc.rigPrebuild(Top=1, Ctrl=True, SknJnts=False, Geo=False, World=True, Master=True, OlSkool=False, Size=150)
    #misc.cleanUp(newSpine[0], Ctrl=False, SknJnts=True, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)

    '''
    #Create Controllers, Constrain to master_Grp and assign to appropriate Grouping structure for snake----------------------------------------------------------------------------------------------

    #Create Path Position Controller
    CtVis= 'SpineCt_Vis'
    Vect='VectorVis'
    cnt     = place.Controller('Position',newSpine[0], orient = False, shape = 'vctrArrow_ctrl', size =20, color = 12, sections = 8, degree = 1, normal =( 0 , 0 , 1), setChannels = True, groups = True)
    EndCt = cnt.createController()
    misc.addAttribute(EndCt[2], CtVis, 0, 1, True, 'float')
    cmds.setAttr(EndCt[2] + '.' + CtVis, k=False, cb=True)
    misc.addAttribute(EndCt[2],Vect,0,1,True,'float')
    cmds.setAttr(EndCt[2]+'.'+ Vect, k=False, cb=True)
    cmds.xform(EndCt[0],r=True, t=(0,60,0))
    cmds.parentConstraint(newSpine[0],EndCt[0], mo=True)
    misc.setChannels(EndCt[2],[False,False],[False,False],[False,False],[True,True, False])
    misc.cleanUp(EndCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)

    #Create Controllers for snake body
    i=0
    for jnt in newSpine:
        cnt     = place.Controller('Spine_'+ str(('%0' + str(3) + 'd')%(i)), jnt, orient = False, shape = 'diamond_ctrl', size =10, color = 15, sections = 8, degree = 1, normal =( 0 , 0 , 1), setChannels = True, groups = True)
        spine = cnt.createController()
        cmds.connectAttr(EndCt[2] + '.' + CtVis, spine[2] + '.visibility')
        misc.setChannels(spine[2],[False,True],[False,True],[True,False],[True,True,False],[True,False])
        cmds.parentConstraint( jnt,spine[0],mo=True)
        misc.cleanUp(spine[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
        i=i+1

    '''
    # create path for IkSpline--------------------------------------------------------------------------------------------------------------------------------------------------------------

    path = 'path'
    cmds.curve(n=path, d=3, p=[(0, 0, -1.128), (0, 0, -50), (0, 0, -100), (0, 0, -150), (0, 0, -600), ])
    # cmds.curve(n=path,d=3,p=[(0,0,-607.033),(0,0,-50),(0,0,-100),(0,0,-150),(0,0,-1832.967),])
    cmds.rebuildCurve(path, d=3, rt=0, s=45)
    #cmds.setAttr(path + '.template', 1)
    misc.cleanUp(path, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)

    # Place Clusters on CVs, group, and add Controllers---------------------------------------------------------------------------------------------------------------------------------------------

    # place Clusters on CVs
    cl = place.clstrOnCV(path, 'Clstr')

    # place Controls on Clusters and Constrain
    segmentPar = None
    segmentChld = []
    colors = [12, 15, 11]
    color = 0
    colorP = 0
    i = 0
    j = 1
    k = 0
    v = 0
    Ctrls = []
    for handle in cl:
        # segment colors
        if j < 4:
            if v == 0:
                color = colors[0]
            else:
                color = colors[2]
            colorP = color
            j = j + 1
        elif j == 4:
            color = colors[1]
            j = j + 1
        elif j > 4 and j < 8:
            if v == 0:
                color = colors[0]
            else:
                color = colors[2]
            colorP = color
            j = j + 1
        elif j == 8:
            color = colors[1]
            j = 1
            # switch colors
            if v == 0:
                v = 1
            else:
                v = 0
        # Controls on Clusters
        cnt = place.Controller('Point' + str(('%0' + str(2) + 'd') % (i)), handle, orient=False, shape='splineEnd_ctrl', size=60, color=color, sections=8, degree=1, normal=(0, 0, 1), setChannels = True, groups = True)
        cntCt = cnt.createController()
        segmentChld.append(cntCt[0])
        cmds.setAttr(handle + '.visibility', 0)
        cmds.parentConstraint(cntCt[4], handle, mo=True)
        Ctrls.append(cntCt[2])
        misc.cleanUp(cntCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
        # segment parents
        if len(segmentChld) == 4:
            sgmt = place.Controller('Segment' + str(('%0' + str(2) + 'd') % (k)), segmentChld[1], orient=False, shape='splineEnd_ctrl', size=100, color=colorP, sections=8, degree=1, normal=(0, 0, 1), setChannels = True, groups = True)
            sgmtCt = sgmt.createController()
            misc.scaleUnlock(sgmtCt[2])
            misc.scaleUnlock(sgmtCt[3])
            l = 0
            for child in segmentChld:
                if l == 3:
                    cmds.parentConstraint('master_Grp', child, mo=True)
                else:
                    cmds.parentConstraint(sgmtCt[4], child, mo=True)
                l = l + 1
            cmds.parentConstraint('master_Grp', sgmtCt[0], mo=True)
            misc.cleanUp(sgmtCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
            segmentChld = []
            k = k + 1
        i = i + 1
    i = 0

    # cleanup clusters and controllers
    cmds.group(cl, n='Ctrl_Points', w=True)
    pGrp = 'Ctrl_Points'
    misc.cleanUp(pGrp, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)

    # Make ikSpline for joint chain and assign 'path' as spline-------------------------------------------------------------------------------------------------------------------------------------

    '''
	ikhandle= cmds.ikHandle( sj= newSpine[0], ee=newSpine[88],sol='ikSplineSolver', ccv=False, c=path, pcv=False)[0]
	cmds.setAttr(ikhandle[0] + '.dTwistControlEnable',1)
	cmds.setAttr(ikhandle[0] + 'dWorldUpType',4)


	#Hide and Parent ikhandle
	cmds.setAttr(ikhandle + '.visibility',0)
	misc.cleanUp(ikhandle, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)
	'''
    # create twist controls

    '''
    cmds.select(Ctrls[0])
    startTwParent = place.null('startTwist_Grp')
    startTw=place.loc('startTwist')
    cmds.parent(startTw[0], startTwParent)
    cmds.setAttr(startTw[0] + '.localScaleX', 30)
    cmds.setAttr(startTw[0] + '.localScaleY', 30)
    cmds.setAttr(startTw[0] + '.localScaleZ', 30)
    cmds.parentConstraint('master_Grp',startTwParent,mo=True)
    cmds.connectAttr(EndCt[2] + '.' + Vect, startTw[0] + '.visibility')
    misc.setChannels(startTw[0],[True,False],[False,True],[False,False],[True,True,False])
    misc.cleanUp(startTwParent, Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)

    cmds.select(Ctrls[42])
    endTwParent = place.null('endTwist_Grp')
    endTw=place.loc('endTwist')
    cmds.parent(endTw, endTwParent)
    cmds.setAttr(endTw[0] + '.localScaleX', 30)
    cmds.setAttr(endTw[0] + '.localScaleY', 30)
    cmds.setAttr(endTw[0] + '.localScaleZ', 30)
    cmds.parentConstraint('master_Grp',endTwParent,mo=True)
    cmds.connectAttr(EndCt[2] + '.' + Vect, endTw[0] + '.visibility')
    misc.setChannels(endTw[0],[True,False],[False,True],[False,False],[True,True,False])
    misc.cleanUp(endTwParent, Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)

    #Create Ik Handle
    ikhandle= cmds.ikHandle( sj= newSpine[0], ee=newSpine[88],sol='ikSplineSolver', ccv=False, c=path, pcv=False)[0]
    cmds.setAttr(ikhandle + '.dTwistControlEnable',1)
    cmds.setAttr(ikhandle + '.dWorldUpType',4)
    cmds.connectAttr(startTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrix')
    cmds.connectAttr(endTw[0] + '.worldMatrix', ikhandle + '.dWorldUpMatrixEnd')

    #Hide and Parent ikhandle
    cmds.setAttr(ikhandle + '.visibility',0)
    misc.cleanUp(ikhandle, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)


    #create and connect attribute for IK Slide on 'end' control------------------------------------------------------------------------------------------------------------------------------------------------------------------

    attr='ikPos'
    misc.addAttribute(EndCt[2], attr, 0.0, 200.0, True, 'float')


    MD=cmds.createNode('multiplyDivide',n='Speed_MD')
    cmds.connectAttr(EndCt[2] + '.' + attr, MD + '.input1X')
    cmds.setAttr(MD + '.input2X',0.01)
    cmds.connectAttr(MD + '.outputX', ikhandle + '.offset')
    '''
