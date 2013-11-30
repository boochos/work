import maya.cmds as cmds
import maya.mel as mel
import constraint_lib as cn


def message(what=''):
    mel.eval('print \"' + '-- ' + what + ' --' + '\";')

def geInv():
    ge = 'graphEditor1'
    b = 'getTraxButton'
    cmds.control(b, q=1, fpn=1)
    # Result: MayaWindow|formLayout1|viewPanes|graphEditor1|formLayout37|frameLayout6|formLayout38|getTraxButton # 
    f = 'formLayout37'
    cmds.formLayout(f, q=1, ca=1)
    # Result: [u'frameLayout6', u'paneLayout1'] # 
    p = 'paneLayout1'
    cmds.paneLayout(p, q=1, ca=1)
    # Result: [u'graphEditor1OutlineEdForm', u'graphEditor1GraphEd'] # 
    g = 'graphEditor1OutlineEdForm'
    cmds.control(g, q=1, fpn=1)
    # Result: MayaWindow|formLayout1|viewPanes|graphEditor1|formLayout37|paneLayout1|graphEditor1OutlineEdForm # 
    g = 'MayaWindow|formLayout1|viewPanes|graphEditor1|formLayout37|paneLayout1|graphEditor1OutlineEdForm'
    cmds.outlinerPanel(g, q=1, iu=1)
    cmds.control(g, e=1, m=1)
    cmds.control(g, e=1, w=0)
    #graphEditor1OutlineEd MayaWindow|formLayout1|viewPanes|graphEditor1|formLayout37|paneLayout1|graphEditor1OutlineEdForm|formLayout39|textField5;
    t = 'textField5'
    cmds.control(t, e=1, m=0)
    cmds.control(t, e=1, m=1)
    f = 'formLayout39'
    cmds.control(f, e=1, m=0)
    cmds.control(f, e=1, m=1)
    cmds.formLayout(f, q=1, ca=1)
    # Result: [u'textField5', u'iconTextButton29'] # button and text in graph editor to replace
    b = 'iconTextButton29'
    cmds.control(b, e=1, m=0)
    cmds.control(b, e=1, m=1)
    
    cmds.deleteUI(field, control=True) 
    AC   = 'Amplify_Curves'
    w = 26
    h = 24
    bg = [0.2, 0.2, 0.2]
    c1='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(-1)'
    flip = 'Flip_Cruvess'
    cmds.setParent(f)
    field = cmds.textField(flip, h=20)
    attachForm = [(field, 'left', 24), (field, 'right', 0)]
    #attachControl = [(field, 'top', 0, heading)]
    cmds.formLayout(f, edit=True, attachForm=attachForm)
    #cmds.formLayout( f, e=True, aoc=(field, 'left', w*3+1, b))

def buttonsGENames():
    return ['Amplify_Curves', 'Flip_Cruves', 'Hold_Curves', 'Amp_Curves']

def buttonsGE():
    #should make this a class
    #should make button creation a subclass
    #should add tangent button
    #should add delete/recreation of buttons
    trxB = 'getTraxButton'
    AC   = 'Amplify_Curves'
    p = cmds.iconTextButton(trxB, q=True, p=True)
    w = 26
    h = 24
    bg = [0.2, 0.2, 0.2]

    flip = 'Flip_Cruves'
    if not cmds.control(flip, ex=1):
        c1='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(-1)'
        btn1 = cmds.iconTextButton(flip, p=p, style='textOnly', stp='python', c=c1, al='center', bgc=bg, mw=1, w=w, label='FLP')
        cmds.formLayout( p, e=True, aoc=(btn1, 'right', w*3+1, trxB))
    else:
        #print flip
        cmds.deleteUI(flip, control=True)

    holdPre = 'Hold_Pre'
    if not cmds.control(holdPre, ex=1):
        c2='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv(preCurrent=False)'
        btn2 = cmds.iconTextButton(holdPre, p=p, style='textOnly', stp='python', c=c2, al='center', bgc=bg, mw=1,  w=w, label='-->')
        cmds.formLayout( p, e=True, aoc=(btn2, 'right', w+1,btn1))
    else:
        #print holdPre
        cmds.deleteUI(holdPre, control=True)

    hold = 'Hold'
    if not cmds.control(hold, ex=1):
        c3='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv()'
        btn3 = cmds.iconTextButton(hold, p=p, style='textOnly', stp='python', c=c3, al='center', bgc=bg, mw=1,  w=w, label='HLD')
        cmds.formLayout( p, e=True, aoc=(btn3, 'right', w+1,btn2))
    else:
        #print hold
        cmds.deleteUI(hold, control=True)

    holdPost = 'Hold_Post'
    if not cmds.control(holdPost, ex=1):
        c4='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv(postCurrent=False)'
        btn4 = cmds.iconTextButton(holdPost, p=p, style='textOnly', stp='python', c=c4, al='center', bgc=bg, mw=1,  w=w, label='<--')
        cmds.formLayout( p, e=True, aoc=(btn4, 'right', w+1,btn3))
    else:
        #print holdPost
        cmds.deleteUI(holdPost, control=True)

    scaleUp = 'Scale_Up'
    if not cmds.control(scaleUp, ex=1):
        c5='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(1.025)'
        btn5 = cmds.iconTextButton(scaleUp, p=p, style='textOnly', stp='python', c=c5, al='center', bgc=bg, mw=1,  w=w, label='+')
        cmds.formLayout( p, e=True, aoc=(btn5, 'right', w+1, btn4))
    else:
        #print scaleUp
        cmds.deleteUI(scaleUp, control=True)

    scaleDown = 'Scale_Down'
    if not cmds.control(scaleDown, ex=1):
        c6='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(0.975)'
        btn6 = cmds.iconTextButton(scaleDown, p=p, style='textOnly', stp='python', c=c6, al='center', bgc=bg, mw=1,  w=w, label='-')
        cmds.formLayout( p, e=True, aoc=(btn6, 'right', w+1, btn5))
    else:
        #print scaleDown
        cmds.deleteUI(scaleDown, control=True)

    fil = 'graphFilter'
    t   = 'textField5'
    if not cmds.control(fil, ex=1):
        cmds.control(t, e=1, m=0)
        f = 'formLayout39'
        c7='import graphFilter\nreload(graphFilter)\ngraphFilter.graphEditorCMD()'
        cmds.setParent(f)
        field = cmds.textField(fil, h=20, cc=c7, ec=c7)
        attachForm = [(field, 'left', 24), (field, 'right', 0)]
        cmds.formLayout(f, edit=True, attachForm=attachForm)
    else:
        cmds.deleteUI(fil, control=True)
        cmds.control(t, e=1, m=1)

    '''
    fld = cmds.textField(AC, p=p, w=w*2, h=h, tx='1.1')
    ec = "import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(float(cmds.textField(\'" + AC + "\', q=True, tx=True)))\n"
    cmds.textField(AC, e=True, p=p, ec=ec, w=w*2, h=h, tx='1.1')
    cmds.formLayout( p, e=True, aoc=(AC, 'right', w+2, btn2))
    '''

def toggleObjectDisplay(purpose):

    #get active and find type of panel
    currentPanel = cmds.getPanel( withFocus=True )
    panelType = cmds.getPanel(to = currentPanel)
    
    if panelType ==  'modelPanel':
        #all off
        cmds.modelEditor(currentPanel, e=True, alo=0)
        
        #arguments
        if purpose == 'anim':
            #specific on
            cmds.modelEditor(currentPanel, e=True, nurbsCurves=1)
            cmds.modelEditor(currentPanel, e=True, polymeshes=1)
            cmds.modelEditor(currentPanel, e=True, locators=1)
            cmds.modelEditor(currentPanel, e=True, cameras=1)
            cmds.modelEditor(currentPanel, e=True, handles=1)
            message( 'Panel display set for animation')
            
        
        elif purpose == 'cam':
            #specific on
            cmds.modelEditor(currentPanel, e=True, cameras=1)
            cmds.modelEditor(currentPanel, e=True, polymeshes=1)
            message('Panel display set for camera')
            
    else:
        message('Current panel is of the wrong type')

def toggleGeo():
    pnl = cmds.getPanel(withFocus=True)
    if cmds.getPanel(to=pnl) == 'modelPanel':
        state = cmds.modelEditor(pnl, q=True, polymeshes=True)
        if state:
            cmds.modelEditor(pnl, e=True, polymeshes=0)
        else:
            cmds.modelEditor(pnl, e=True, polymeshes=1)

def toggleRes():
    sel = cmds.ls(sl=True)
    c = ':c_master_CTRL.'
    attrHi = 'hiResGeoVis'
    attrLo = 'loResGeoVis'
    name = sel[0].split(':')[0]
    if cmds.getAttr(name + c + attrHi) == 1:
        cmds.setAttr(name + c + attrHi, 0)
        cmds.setAttr(name + c + attrLo, 1)
        message('LO res')
    else:
        cmds.setAttr(name + c + attrHi, 1)
        cmds.setAttr(name + c + attrLo, 0)
        message('HI res')

def shapeSize(obj=None, mltp=1):
    '''\n
    mltp = size multiplier of shape nodes
    '''
    if obj == None:
        #make a list from selection
        obj = cmds.ls(sl=True, l=True)
        shapeSize(obj, mltp)
    elif type(obj) == list:
        #no need to accomodate
        for i in obj:
            shapeSize(i, mltp)
    else:
        #obj must be a single item, make a list
        obj = [obj]
        #run the loop on list
        for item in obj:
            shape = cmds.listRelatives(item, s=True, f=True)
            if shape != None:
                for node in shape:
                    if 'SharedAttr' not in node:
                        cmds.scale( mltp, mltp, mltp, node + '.cv[*]')

def locSize(lc, mltp=1):
    axis = ['X','Y','Z']
    for axs in axis:
        sz = cmds.getAttr(lc + 'Shape.localScale' + axs)
        cmds.setAttr(lc + 'Shape.localScale' + axs, sz*X)

def changeColor(color=17, shapes=False):
    sel = cmds.ls(sl=True)
    if sel != None:
        if shapes == True:
            sel = shapeNodes()
        for item in sel:
            cmds.setAttr(item + '.overrideEnabled', 1)
            cmds.setAttr(item + '.overrideColor', color)
    else:
        message('Select an object')

def worldSpdExp(sel, attr):
    exp = "float $currentPos[] = `getAttr -t (frame) "+sel+".worldMatrix`;\nfloat $lastPos[] = `getAttr -t (frame-1) "+sel+".worldMatrix`;\nfloat $speed = abs(mag (<<0*"+sel+".tx+$currentPos[12]-$lastPos[12], 0*"+sel+".ty+$currentPos[13]-$lastPos[13], 0*"+sel+".tz+$currentPos[14]-$lastPos[14]>>) );\nfloat $inKPH = $speed*24*60*60/10000;\n"+sel+"."+attr+" = $inKPH;"
    return exp

def localSpdExp(sel, attr):
    exp = "float $lastPosX = `getAttr -t (frame-1) "+sel+".tx`;\nfloat $lastPosY = `getAttr -t (frame-1) "+sel+".ty`;\nfloat $lastPosZ = `getAttr -t (frame-1) "+sel+".tz`;\nfloat $speed = abs(mag (<<"+sel+".translateX-$lastPosX,"+sel+".translateY-$lastPosY,"+sel+".translateZ-$lastPosZ>>) );\nfloat $inKPH = $speed*24*60*60/10000;\n"+sel+"."+attr+" = $inKPH;" 
    return exp

def createSpeedAttr(sel, attr, exp):
    cmds.addAttr(sel,longName=attr ,attributeType = 'float', k=0)
    cmds.setAttr(sel + "." + attr, cb=1)
    e = cmds.expression(o=sel, s=exp)

def speed(world=True, local=True):
    selected = cmds.ls( sl=True )
    if len(selected) != 0:
        for sel in selected:
            if world == True:
                attr = 'worldSpeed'
                exp = worldSpdExp(sel, attr)
                if cmds.attributeQuery(attr, node=sel, ex=True) == False:
                    createSpeedAttr(sel, attr, exp)
                else:
                    cmds.warning('-- Speed attr (' + attr + ') already exists. Skipping' + sel + ' ! --')
                    return None
            if local == True:
                attr = 'localSpeed'
                exp = localSpdExp(sel, attr)
                if cmds.attributeQuery(attr, node=sel, ex=True) == False:
                    createSpeedAttr(sel, attr, exp)
                else:
                    cmds.warning('-- Speed attr (' + attr + ') already exists. Skipping -' + sel + ' ! --')
                    return None
    else:
        message('Select an object.')

def createDisAttr(sel, attr, exp):
    '''
    creates attr and applies expression
    '''
    cmds.addAttr(sel,longName=attr ,attributeType = 'float', k=True)
    cmds.setAttr(sel + "." + attr, cb=1)
    e = cmds.expression(o=sel, s=exp)

def measureDis(obj1, obj2):
    '''
    math for distance between 2 objects
    '''
    p1 = cmds.xform(obj1, q=True, ws=True, t=True )
    p2 = cmds.xform(obj2, q=True, ws=True, t=True )
    v = [0,0,0]
    v[0] = p1[0] - p2[0]
    v[1] = p1[1] - p2[1]
    v[2] = p1[2] - p2[2]
    distance = v[0]*v[0] + v[1]*v[1] + v[2]*v[2]
    from math import sqrt
    distance = sqrt(distance)
    return distance

def distanceExp(sel, sel2, attr):
    '''
    builds expression string
    '''
    exp0 = "python \"import display_lib as dis\";\npython \"reload(dis)\";\n"
    exp1 = sel+ "." +attr+ " = `python \"dis.measureDis('" + sel + "','" + sel2 + "')\"`;"
    exp = exp0 + exp1
    return exp

def distance():
    '''
    assembles distance relationship
    '''
    selected = cmds.ls( sl=True )
    if len(selected) == 2:
        i = 1
        for sel in selected:
            attr = 'distance'
            exp = distanceExp(sel, selected[i], attr)
            if cmds.attributeQuery(attr, node=sel, ex=True) == False:
                createDisAttr(sel, attr, exp)
            else:
                cmds.warning('-- Speed attr (' + attr + ') already exists. Skipping' + sel + ' ! --')
                return None
            if i == 1:
                i = 0
    else:
        message('Select an object.')


def deleteUserAttr(sel=None, exp=True):
    if sel == None:
        sel = cmds.ls(sl=True)
        if len(sel) != 1:
             message('Select one object')
             return None
        else:
            sel = sel[0]
    selectedAttr = cmds.channelBox('mainChannelBox', q=True, sma=True)
    userAttr = cmds.listAttr(sel, ud=True)
    if selectedAttr != None:
        for attr in selectedAttr:
            if attr in userAttr:
                con = cmds.listConnections(sel + '.' + attr, d=False, s=True)
                if con != None:
                    if exp == True:
                        if cmds.nodeType(con[0]) =='expression':
                            cmds.delete(con[0])
                        else:
                            message( 'No expression node was found.')
                cmds.deleteAttr(sel + '.' + attr)
            else:
                message('Attribute ' + attr + ' is not a user defined attribute. It cannot be deleted.')
    else:
        message('Select an attribute(s) in the channelBox.')

def rotateManip():
    mode = cmds.manipRotateContext('Rotate', q=True, mode=True)
    if mode == 0:
        cmds.manipRotateContext('Rotate', e=True, mode=2)
        message('Gimbal')
    elif mode ==2:
        cmds.manipRotateContext('Rotate', e=True, mode=0)
        message('Local')
    elif mode == 1:
        cmds.manipRotateContext('Rotate', q=True, mode=2)
        message('Gimbal')

def translateManip():
    mode = cmds.manipMoveContext('Move', q=True, mode=True)
    print mode
    if mode == 0:
        cmds.manipMoveContext('Move', e=True, mode=1)
        message('Local')
    elif mode == 1:
        cmds.manipMoveContext('Move', e=True, mode=2)
        message('World')
    elif mode ==2:
        cmds.manipMoveContext('Move', e=True, mode=0)
        message('Object')

def clearKey():
    mel.eval('timeSliderClearKey;')


def altFrame():
    pnl = cmds.getPanel(withFocus=True)
    typ = cmds.getPanel(typeOf=pnl)
    if typ == 'modelPanel':
        sel    = cmds.ls(sl=True)
        locs = []
        if sel:
            for item in sel:
                loc = cn.locator(obj=item, ro='zxy', X=0.01, constrain=False)[0]
                locs.append(loc)
            cmds.select(locs)
            mel.eval("fitPanel -selected;")
            cmds.delete(locs)
            cmds.select(sel)
        else:
            message('select an object')
    else:
        mel.eval("fitPanel -selected;")
