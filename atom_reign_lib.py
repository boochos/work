import maya.cmds as cmds
from atom import atom_placement_lib as place
from atom import atom_miscellaneous_lib as misc
from atom import atom_appendage_lib as apg
from atom import atom_joint_lib as jnt
from pymel.core import *

def insrtTrnsfrm(crvs):
    for crv in crvs:
        crvShp = cmds.listRelatives(crv, typ='shape')
        tmp = cmds.listConnections(crvShp, d=False, s=True, type='transform', connections=True)
        pnt = []
        cnnct = []
        for item in tmp:
            if 'controlPoints' in item:
                pnt.append(item)
            else:
                cnnct.append(item)
        if len(pnt) == len(cnnct):
            #print pnt
            #print cnnct
            parent = cmds.listRelatives(crv, parent=True, typ='transform')
            spc = cmds.group(name=crv+'_' +'spaceCnvrsn', em=True)
            cmds.parent(spc, parent)
            i=0
            for item in cnnct:
                grp = cmds.group(name=crv+'_point'+str(i)+'_grp', em=True)
                cmds.select(grp)
                loc = place.loc(crv+'_point'+str(i)+ '_loc')[0]
                cmds.parent(loc, grp)
                cmds.parent(grp, spc)
                cns = cmds.pointConstraint(
                    cmds.listRelatives(item, parent=True, typ='transform'), 
                    grp, mo=False)
                #cmds.delete(cns)
                cns = cmds.parentConstraint(item, loc, mo=False)
                cmds.connectAttr(loc + '.translate', pnt[i], f=True)
                i=i+1
        else:
            print "you're here for some reason"


def sagIK(name, suffix, X, jPos, ikCns, master='CTRL_Gp', cleanup=True, percent=100):
    '''
	-Rig for reigns. 
    -3 joint ik system automates sagging of reigns in a rudamentary fashion. 
    -Limits stretching.
	
	'''
    members = []
    #select objects and create joints on positions
    cmds.select(jPos)
    jnts = place.joint(0, (name + '_jnt' + '_'))
    members.append(jnts[0])
    cmds.joint(jnts[0], e=True, oj='zyx', sao='yup', ch=True)
    #make 3 joints planar
    cmds.parent(jnts[1], w=True)
    cmds.parent(jnts[2], w=True)
    ##aim root at mid, tip is up vector
    cns = cmds.aimConstraint(jnts[1], jnts[0], aimVector=(0,0,1), upVector=(0,1,0), mo=False,
                             worldUpType="object", worldUpObject=jnts[2])
    cmds.delete(cns)
    cmds.parent(jnts[1], jnts[0])
    cmds.setAttr(jnts[1] + '.jointOrientY', 0)
    cmds.setAttr(jnts[1] + '.jointOrientZ', 0)
    cmds.parent(jnts[2], jnts[1])
    cmds.setAttr(jnts[2] + '.jointOrientX', 0)
    cmds.setAttr(jnts[2] + '.jointOrientY', 0)
    cmds.setAttr(jnts[2] + '.jointOrientZ', 0)
    #adjust controller size
    cmds.floatField('atom_qrig_conScale', edit=True, v=X)
    #create pv control
    pv = apg.create_3_joint_pv(jnts[0],
                               jnts[2],
                               '', '', '', 
                               'atom_qls_limbRot_radioButtonGrp',
                               'atom_qls_limbAim_radioButtonGrp',
                               'atom_qls_limbUp_radioButtonGrp',
                               X* -15,
                               0, 
                               cmds.textField('atom_csst_exportPath_textField', query=True, text=True),
                               useFlip=True,
                               flipVar=[1,0,0])
    pvShape = cmds.listRelatives(pv, shapes =True)[0]
    cmds.setAttr(pvShape + '.overrideEnabled', 1)
    cmds.setAttr(pvShape + '.overrideColor', 9)
    pv = cmds.rename(pv, name)
    pvGrp = place.null2(pv + '_CtGrp', pv, True)
    cmds.parent(pv, pvGrp)
    misc.setChannels(pv, [False, True], [True, False], [True, False], [True, False, False])
    members.append(pvGrp)
    #ik handle
    ik = cmds.ikHandle(name = name + '_ik', 
                             sj=jnts[0], ee= jnts[2], 
                             sol='ikRPsolver', weight=1, pw=1, fs=1, shf=1,s='sticky')
    members.append(ik[0])
    cmds.poleVectorConstraint(pv, ik[0])
    cmds.parentConstraint(ikCns[0], jnts[0], mo=True)
    cmds.parentConstraint(ikCns[2], ik[0], mo=True)
    cmds.parentConstraint(jnts[1],ikCns[1], mo=True)
    #add strecth and joint limits
    apg.ikStretch(pv, jnts[0], jPos[00], jPos[2], percent)
    #guide line
    guides = misc.guideLine(pv, jPos[1], name + '_')
    grpGds = cmds.group(name=name + '_Guide', em=True)
    for item in guides:
        cmds.parent(item, grpGds)
    #clean up
    grpIK = cmds.group(name=name + '_Utl', em=True)
    for item in members:
        cmds.parent(item, grpIK)
    grp = cmds.group(name=name + '_TopGrp', em=True)
    cmds.parent(grpIK, grp)
    cmds.parent(grpGds, grp)
    cmds.setAttr(ik[0] + '.visibility', 0)
    cmds.setAttr(jnts[0] + '.visibility', 0)
    cmds.parentConstraint(master, grp, mo=True)
    if cleanup == True:
        misc.cleanUp(guides[0], World=True)
        misc.cleanUp(grp, Ctrl=True)

def attachReign(sets):
    parent = None
    for pair in sets:
        parent = pair[0]
        for member in pair:
            if member != pair[0]:
                cmds.parentConstraint(parent, member, mo=True)


def runPrebuild(*args):
    X=1
    PreBuild    = misc.rigPrebuild(Top=3, Ctrl=True, SknJnts=False, Geo=False, World=True, Master=False, OlSkool=True, Size=X*180)
    CHARACTER   = PreBuild[0]
    CONTROLS    = PreBuild[1]
    #SKIN_JOINTS = PreBuild[1]
    #GEO         = PreBuild[1]
    WORLD_SPACE = PreBuild[2]
    #MasterCt    = PreBuild[5]
    OlSkool     = PreBuild[3]
    cmds.parent('TopNode', OlSkool)

def runInsrtTrnsfrm(*args):
    crvs = [
        'LfDn_rein_Crv',
        'RtDn_rein_Crv',
        'LfMd_rein_Crv',
        'RtMd_rein_Crv',
        'LfLf_rein_Crv',
        'LfRt_rein_Crv',
        'RtLf_rein_Crv',
        'RtRt_rein_Crv'
    ]
    insrtTrnsfrm(crvs)

def runSagIk(*args):
    #Bells L
    sagIK(name = 'LfDn', suffix = 'L', X = 6, 
          jPos = ['LfDn_rein_1x','LfDn_rein_3x','LfDn_rein_5x'], 
          ikCns = ['LfDn_rein_1x','LfDn_rein_3x_CtGp','LfDn_rein_5x'],
          percent=60)
    #ReignFront_L L
    sagIK(name = 'LfLf_front', suffix = 'L', X = 3, 
          jPos = ['LfLf_rein_1x','LfLf_rein_3x','LfLf_rein_5x'], 
          ikCns = ['LfLf_rein_1x','LfLf_rein_3x_CtGp','LfLf_rein_5x'],
          percent=50)
    #ReignBack_L L
    sagIK(name = 'LfLf_back', suffix = 'L', X = 5, 
          jPos = ['LfLf_rein_5x','LfLf_rein_8x','LfLf_rein_10x'], 
          ikCns = ['LfLf_rein_5x','LfLf_rein_8x_CtGp','LfLf_rein_10x'],
          percent=60)
    #ReignFront_R L
    sagIK(name = 'LfRt_front', suffix = 'L', X = 3, 
          jPos = ['LfRt_rein_1x','LfRt_rein_3x','LfRt_rein_5x'], 
          ikCns = ['LfRt_rein_1x','LfRt_rein_3x_CtGp','LfRt_rein_5x'],
          percent=50)
    #ReignBack_R L
    sagIK(name = 'LfRt_back', suffix = 'L', X = 5, 
          jPos = ['LfRt_rein_5x','LfRt_rein_8x','LfRt_rein_10x'], 
          ikCns = ['LfRt_rein_5x','LfRt_rein_8x_CtGp','LfRt_rein_10x'],
          percent=60)
    #Bells R
    sagIK(name = 'RtDn', suffix = 'R', X = 6, 
          jPos = ['RtDn_rein_1x','RtDn_rein_3x','RtDn_rein_5x'], 
          ikCns = ['RtDn_rein_1x','RtDn_rein_3x_CtGp','RtDn_rein_5x'],
          percent=60)
    #ReignFront_L R
    sagIK(name = 'RtLf_front', suffix = 'R', X = 3, 
          jPos = ['RtLf_rein_1x','RtLf_rein_3x','RtLf_rein_5x'], 
          ikCns = ['RtLf_rein_1x','RtLf_rein_3x_CtGp','RtLf_rein_5x'],
          percent=50)
    #ReignBack_L R
    sagIK(name = 'RtLf_back', suffix = 'R', X = 5, 
          jPos = ['RtLf_rein_5x','RtLf_rein_8x','RtLf_rein_10x'], 
          ikCns = ['RtLf_rein_5x','RtLf_rein_8x_CtGp','RtLf_rein_10x'],
          percent=60)
    #ReignFront_R R
    sagIK(name = 'RtRt_front', suffix = 'R', X = 3, 
          jPos = ['RtRt_rein_1x','RtRt_rein_3x','RtRt_rein_5x'], 
          ikCns = ['RtRt_rein_1x','RtRt_rein_3x_CtGp','RtRt_rein_5x'],
          percent=50)
    #ReignBack_R R
    sagIK(name = 'RtRt_back', suffix = 'R', X = 5, 
          jPos = ['RtRt_rein_5x','RtRt_rein_8x','RtRt_rein_10x'], 
          ikCns = ['RtRt_rein_5x','RtRt_rein_8x_CtGp','RtRt_rein_10x'],
          percent=60)

def runAttachReigns(*args):
    sleigh   = 'Sleigh:sledMinor_1x'
    reignNS  = ['Reigns3', 'Reigns2', 'Reigns1', 'Reigns']
    lftFrnt  = ['Reindeer7', 'Reindeer5', 'Reindeer3', 'Reindeer1']
    lftBck   = ['Reindeer5', 'Reindeer3', 'Reindeer1', sleigh]
    rghtFrnt = ['Reindeer6', 'Reindeer4', 'Reindeer2', 'Reindeer']
    rghtBck  = ['Reindeer4', 'Reindeer2', 'Reindeer', sleigh]    
    i=0
    for reign in reignNS:
        # ___ reign ___  attach objects
        #Reindeer L side
        ##from jaw L side
        LfLf1 = [lftFrnt[i] + ':accsHdHrnss_00_Grp', reign + ':LfLf_rein_1x_CtGp', reign + ':LfLf_rein_2x_CtGp']
        LfLf2 = [lftFrnt[i]  + ':accsBdyHrnss_00_Grp', reign + ':LfLf_rein_4x_CtGp', reign + ':LfLf_rein_6x_CtGp', reign + ':LfLf_rein_7x_CtGp']
        LfLf3 = [lftBck[i]  + ':accsBdyHrnss_00_Grp', reign + ':LfLf_rein_10x_CtGp']
        ##from neck L side
        LfDn1 = [lftFrnt[i]  + ':accsNckHrnss_00_Grp', reign + ':LfDn_rein_1x_CtGp', reign + ':LfDn_rein_2x_CtGp']
        LfDn2 = [lftBck[i]  + ':accsNckHrnss_00_Grp', reign + ':LfLf_rein_9x_CtGp', reign + ':LfDn_rein_4x_CtGp', reign + ':LfDn_rein_5x_CtGp']
        ##from jaw R side
        LfRt1 = [lftFrnt[i]  + ':accsHdHrnss_01_Grp', reign + ':LfRt_rein_1x_CtGp', reign + ':LfRt_rein_2x_CtGp']
        LfRt2 = [lftFrnt[i]  + ':accsBdyHrnss_05_Grp', reign + ':LfRt_rein_4x_CtGp', reign + ':LfRt_rein_6x_CtGp', reign + ':LfRt_rein_7x_CtGp']
        LfRt3 = [lftBck[i]  + ':accsBdyHrnss_05_Grp', reign + ':LfRt_rein_9x_CtGp', reign + ':LfRt_rein_10x_CtGp']
        ##from body R side
        LfMd1 = [lftFrnt[i]  + ':accsBdyHrnss_04_Grp', reign + ':LfMd_rein_1x_CtGp', reign + ':LfMd_rein_2x_CtGp', reign + ':LfMd_rein_3x_CtGp', reign + ':Ft_nunChuck_CtGp']
        FtBk1 = [lftBck[i]  + ':accsBdyHrnss_04_Grp', reign + ':FtBk_CtGp']
        ##chest
        chestL = [lftFrnt[i]  + ':chest_Grp',reign + ':LfRt_front_CtGrp',reign + ':LfLf_front_CtGrp']
        ##cog
        cogL = [lftFrnt[i]  + ':cog_Grp',reign + ':LfDn_CtGrp',reign + ':LfRt_back_CtGrp',reign + ':LfLf_back_CtGrp']
        #Reindeer R side
        ##from jaw L side
        RtLf1 = [rghtFrnt[i]  + ':accsHdHrnss_00_Grp', reign + ':RtLf_rein_1x_CtGp', reign + ':RtLf_rein_2x_CtGp']
        RtLf2 = [rghtFrnt[i]  + ':accsBdyHrnss_00_Grp', reign + ':RtLf_rein_4x_CtGp', reign + ':RtLf_rein_6x_CtGp', reign + ':RtLf_rein_7x_CtGp']
        RtLf3 = [rghtBck[i]  + ':accsNckHrnss_00_Grp', reign + ':RtLf_rein_9x_CtGp', reign + ':RtLf_rein_10x_CtGp']
        ##from body L side
        RtMd1 = [rghtFrnt[i]  + ':accsBdyHrnss_01_Grp', reign + ':RtMd_rein_1x_CtGp', reign + ':RtMd_rein_2x_CtGp', reign + ':RtMd_rein_3x_CtGp', reign + ':Ft_nunChuck_CtGp']
        FtBk2 = [rghtBck[i]  + ':accsBdyHrnss_01_Grp', reign + ':FtBk_CtGp']
        ##from jaw R side
        RtRt1 = [rghtFrnt[i]  + ':accsHdHrnss_01_Grp', reign + ':RtRt_rein_1x_CtGp', reign + ':RtRt_rein_2x_CtGp']
        RtRt2 = [rghtFrnt[i]  + ':accsBdyHrnss_05_Grp', reign + ':RtRt_rein_4x_CtGp', reign + ':RtRt_rein_6x_CtGp', reign + ':RtRt_rein_7x_CtGp']
        RtRt3 = [rghtBck[i]  + ':accsBdyHrnss_05_Grp', reign + ':RtRt_rein_10x_CtGp']
        ##from neck R side
        RtDn1 = [rghtFrnt[i]  + ':accsNckHrnss_01_Grp', reign + ':RtDn_rein_1x_CtGp', reign + ':RtDn_rein_2x_CtGp']
        RtDn2 = [rghtBck[i]  + ':accsNckHrnss_01_Grp', reign + ':RtRt_rein_9x_CtGp', reign + ':RtDn_rein_4x_CtGp', reign + ':RtDn_rein_5x_CtGp']
        ##chest
        chestR = [rghtFrnt[i]  + ':chest_Grp',reign + ':RtRt_front_CtGrp',reign + ':RtLf_front_CtGrp']
        ##cog
        cogR = [rghtFrnt[i]  + ':cog_Grp',reign + ':RtDn_CtGrp',reign + ':RtRt_back_CtGrp',reign + ':RtLf_back_CtGrp']
        if i == 3:
            LfLf3[0] = sleigh
            LfDn2[0] = sleigh
            LfRt3[0] = sleigh
            FtBk1[0] = sleigh
            RtLf3[0] = sleigh
            FtBk2[0] = sleigh
            RtRt3[0] = sleigh
            RtDn2[0] = sleigh

        i=i+1
        
        sets = [LfLf1, LfLf2, LfLf3,
                LfDn1, LfDn2,
                LfRt1, LfRt2, LfRt3,
                LfMd1, FtBk1,
                RtLf1, RtLf2, RtLf3,
                RtMd1, FtBk2,
                RtRt1, RtRt2, RtRt3,
                RtDn1, RtDn2,
                chestL, cogL,
                chestR, cogR,]
        
        attachReign(sets)