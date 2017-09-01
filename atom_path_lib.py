import maya.cmds as cmds
# import atom_miscellaneous_lib as misc
import webrImport as web
# web
place = web.mod('atom_place_lib')
cn = web.mod('constraint_lib')

def message(what='', maya=True, warning=False):
    what = '-- ' + what + ' --'
    if '\\' in what:
        what = what.replace('\\', '/')
    if warning:
        cmds.warning(what)
    else:
        if maya:
            mel.eval('print \"' + what + '\";')
        else:
            print what


def attach(up='', reverse=False):
    # select control and path namespace
    sel = cmds.ls(sl=True)
    path = sel[len(sel) - 1]
    path = path.split(':')[0] + ':path'
    up = path.split(':')[0] + ':up'
    print path
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


def path(segments=5, size=0.05, length=10, *args):
    # creates groups and master controller from arguments specified as 'True'

    place.rigPrebuild(Top=1, Ctrl=True, SknJnts=False, Geo=False, World=True, Master=True, OlSkool=False, Size=150*size)
    #place.cleanUp(newSpine[0], Ctrl=False, SknJnts=True, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)

    # up 
    upCnt = place.Controller(place.getUniqueName('up'), 'master', orient=True, shape='loc_ctrl', size=60*size, color=17, setChannels = True, groups = True)
    upCntCt = upCnt.createController()
    place.cleanUp(upCntCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
    cmds.setAttr(upCntCt[0] + '.ty', length/2)
    cmds.parentConstraint('master_Grp', upCntCt[0], mo=True)
    path = place.getUniqueName('path')
    lengthSeg = length/5
    print lengthSeg
    if segments == 1:
        points = segments
    else:
        points = ((segments -1)*4)+1
    cmds.curve(n=path, d=3, p=[(0, 0, -1.128), (0, 0, lengthSeg*2), (0, 0, lengthSeg*3), (0, 0, lengthSeg*4), (0, 0, lengthSeg*5), ])
    # cmds.curve(n=path,d=3,p=[(0,0,-607.033),(0,0,-50),(0,0,-100),(0,0,-150),(0,0,-1832.967),])
    cmds.rebuildCurve(path, d=3, rt=0, s=points)
    cmds.setAttr(path + '.template', 1)
    place.cleanUp(path, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)

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
        cnt = place.Controller('Point' + str(('%0' + str(2) + 'd') % (i)), handle, orient=False, shape='splineEnd_ctrl', size=60*size, color=color, sections=8, degree=1, normal=(0, 0, 1), setChannels = True, groups = True)
        cntCt = cnt.createController()
        segmentChld.append(cntCt[0])
        cmds.setAttr(handle + '.visibility', 0)
        cmds.parentConstraint(cntCt[4], handle, mo=True)
        Ctrls.append(cntCt[2])
        place.cleanUp(cntCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
        # segment parents
        if len(segmentChld) == 4:
            sgmt = place.Controller('Segment' + str(('%0' + str(2) + 'd') % (k)), segmentChld[1], orient=False, shape='splineEnd_ctrl', size=100*size, color=colorP, sections=8, degree=1, normal=(0, 0, 1), setChannels = True, groups = True)
            sgmtCt = sgmt.createController()
            place.scaleUnlock(sgmtCt[2])
            place.scaleUnlock(sgmtCt[3])
            l = 0
            for child in segmentChld:
                if l == 3:
                    cmds.parentConstraint('master_Grp', child, mo=True)
                else:
                    cmds.parentConstraint(sgmtCt[4], child, mo=True)
                l = l + 1
            cmds.parentConstraint('master_Grp', sgmtCt[0], mo=True)
            place.cleanUp(sgmtCt[0], Ctrl=True, SknJnts=False, Body=False, Accessory=False, Utility=False, World=False, olSkool=False)
            segmentChld = []
            k = k + 1
        i = i + 1
    i = 0

    # cleanup clusters and controllers
    cmds.group(cl, n='Ctrl_Points', w=True)
    pGrp = 'Ctrl_Points'
    place.cleanUp(pGrp, Ctrl=False, SknJnts=False, Body=False, Accessory=False, Utility=False, World=True, olSkool=False)

