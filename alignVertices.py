from pymel.core import *
import pymel.core.datatypes as dt

def convertRangeStr(string):
    '''\n
    ie.
    -string       = 'head_Geo.vtx[2533:2534]'
    -return list  = ['head_Geo.vtx[2533]', 'head_Geo.vtx[2534]']
    '''
    rangeList = []
    start  = string.rfind('[')
    end    = string.rfind(']')
    split  = string.rfind(':')
    v1     = string[start+1:split]
    v2     = string[split+1:end]
    strngA = string[:start+1]
    strngB = string[end:]
    for i in range(int(v1), int(v2)+1, 1):
        rangeList.append(strngA + str(i) + strngB)
    return rangeList

def getPairList(*args):
    '''\n
    -Create vertex pair list from edge selection\n
    '''
    edges = cmds.ls(sl=True, fl=True)
    pairList=[]
    for edge in  edges:
        result = cmds.polyListComponentConversion(edge, fe=True, tv=True)
        if ':' in str(result):
            result = convertRangeStr(result[0])
        pairList.append(result)
    return pairList

def findFirst(pairList=None):
    '''\n
    -find first vertex then loop thorugh for all others
    '''
    order = []
    orderStop = ((len(pairList)-1) * 2) +1
    stop = len(pairList)-1
    next = None
    nextPair = None
    i=0
    while i <= stop:
        for vert in pairList[i]:
            end = findNext(vert, pairList[i], pairList)
            if end[0] == False:
                order.append(vert)
                order.append(findPartner(vert, pairList[i]))
                next     = order[1]
                nextPair = pairList[i]
                j = 0
                while len(order) < orderStop:
                    result = findNext(next, nextPair, pairList)
                    if result[0] != False:
                        next     = result[0]
                        nextPair = result[1]
                        order.append(next)
                    else :
                        return order
                    j=j+1
                    if j ==  orderStop * 2:
                        #sanity
                        break
                return order
        i=i+1

def findNext(vert, vertPair, pairList):
    '''\n
    -ie. pairList[pair1[v1______v2], pair2[v2______v3]] (starting with v2,  in first pair, get v3 in second pair)
    -vert     = (ie.v2 in first pair)
    -vertPair = pair to which the vertex belongs, (ie.pair1)
    -pairList = full pair list from selection (ie.top example, outside list)
    -False    = a return of False means the vert is at the end/start of order and has no next vertex
    '''
    v = 0
    j = 0
    next = [[None],[None]]
    nextPair = None
    for iteratedPair in pairList:
        if vert in iteratedPair:
            v=v+1
            if pairCompare(vertPair, iteratedPair) == False:
                next[0] = findPartner(vert, iteratedPair)
                next[1] = iteratedPair
        j=j+1
    if v==2:
        return next
    elif v==1:
        next[0] = False
        return next

def pairCompare(pair1, pair2):
    '''\n
    -compares two pairs of vertices for same members
    '''
    if pair1[0] in pair2:
        if pair1[1] in pair2:
            return True
        else:
            return False
    else:
        return False

def findPartner(vert, VertPair):
    '''\n
    ie. pair1[v1______v2]\n
    if v1 given, v2 is returned\n
    '''
    if vert == VertPair[0]:
        return VertPair[1]
    else:
        return VertPair[0]

def alignVertices(*args):
    '''\n
    -derived from edge selection
    -divides vector length by number of verts, and spaces them evenly
    '''
    #get selection
    pairList = getPairList()
    #reorder selection
    order = findFirst(pairList)
    #get start pos
    vector1  = dt.Vector(cmds.xform(order[0], q=True, os=True, t=True))
    #get ewnd position
    vector2  = dt.Vector(cmds.xform(order[(len(order)-1)], q=True, os=True, t=True))
    #divide length between start/end evenly
    posDiff  = ((vector1) - (vector2)) / (len(order)-1)
    #repostion verts
    i=0
    for v in order:
        cntDiff = (posDiff*i)
        newPos = ((vector1) - (cntDiff))
        cmds.xform(v, os=True, t=[newPos.x, newPos.y, newPos.z])
        i=i+1


alignVertices()
