import maya.cmds as cmds
import maya.mel as mel
import constraint_lib as cn


def message(what='', maya=True):
    what = '-- ' + what + ' --'
    if maya == True:
        mel.eval('print \"' + what + '\";')
    else:
        print what

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
    #graphEditor2OutlineEd graphEditor2Window|TearOffPane|graphEditor2|formLayout40|paneLayout4|graphEditor2OutlineEdForm|formLayout42|textField6;
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

def buttonsGENames():
    return ['Amplify_Curves', 'Flip_Cruves', 'Hold_Curves', 'Amp_Curves']

def geButton(name='', parent='', attach=None, label='', cmd='', gap=2, w=26, h=19, bg=[0.21, 0.21, 0.21], ann='' ):
    #"boldLabelFont", "smallBoldLabelFont", "tinyBoldLabelFont", "plainLabelFont", "smallPlainLabelFont",
    #"obliqueLabelFont", "smallObliqueLabelFont", "fixedWidthFont" and "smallFixedWidthFont"
    if not cmds.control(name, ex=1):
        cmd=cmd
        #btn = cmds.iconTextButton(name, p=parent, style='textOnly', stp='python', c=cmd, al='center', h=h, bgc=bg, mw=1, w=w, label=label, ann=ann)
        btn = cmds.button(name, p=parent, c=cmd, al='center', h=h, bgc=bg,w=w, label=label, ann=ann)
        ac = [(btn, 'left', gap, attach)]
        attachForm = [(btn, 'bottom', 3)]
        if attach:
            cmds.formLayout( parent, e=True, ac=ac, attachForm=attachForm)
        else:
            attachForm = [(btn, 'left', 2), (btn, 'bottom', 3)]
            cmds.formLayout( parent, e=True, attachForm=attachForm)
        return btn
    else:
        print ''
        cmds.deleteUI(name, control=True)

def geHeading(name='', parent='', attach=None, label='', cmd='', gap=10, ann='', bgc=[0.275,0.275,0.275], w=45, h=17):
    if not cmds.control(name, ex=1):
        lab = cmds.text(name, l=label, fn='obliqueLabelFont', al='center', bgc=bgc, ebg=True, ann=ann, w=w, h=h)
        ac = [(lab, 'left', gap, attach)]
        attachForm = [(lab, 'bottom', 4)]
        if attach:
            cmds.formLayout( parent, e=True, ac=ac, attachForm=attachForm)
        else:
            cmds.formLayout( parent, e=True, attachForm=attachForm)
        return lab
    else:
        print ''
        cmds.deleteUI(name, control=True)

def geField(name='', parent='', attach=None, label='', cmd='', w=100, gap=10, tx='', ann=''):
    if not cmds.control(name, ex=1):
        field = cmds.textField(name, tx=tx, h=21, w=w, cc=cmd, ec=cmd, ann=ann)
        ac = [(field, 'left', gap, attach)]
        attachForm = [(field, 'left', 2), (field, 'bottom', 2)]
        if attach:
            cmds.formLayout(parent, edit=True, ac=ac, attachForm=attachForm)
        else:
            cmds.formLayout(parent, edit=True, attachForm=attachForm)
        return field
    else:
        print ''
        cmds.deleteUI(name, control=True)

def geFieldTx(name='', v=''):
    try:
        tx = cmds.textField(name, q=1, tx=1)
        if not tx:
            cmds.textField(name, e=1, tx=v)
            import graphFilter
            reload(graphFilter)
            graphFilter.graphEditorCMD()
        else:
            cmds.textField(name, e=1, tx='')
            import graphFilter
            graphFilter.graphEditorCMD()
    except:
        pass

def buttonsGE():

    #filter
    filD    = 'FilterDefault'
    fil     = 'graphFilter'
    #hold
    hldPre  = 'holdPre'
    hldAll  = 'holdAll'
    hldPost = 'holdPost'
    #scale
    sclDwn = 'scaleDown'
    sclTx   = 'scaleTxt'
    sclUp   = 'scaleUp'
    flp     = 'FlipCurves'
    #value move
    movDwn  = 'moveDown'
    movTx  = 'moveValue'
    movUp   = 'moveUp'
    #time move
    movTmLf   = 'moveLeft'
    movTmTx   = 'moveTime'
    movTmRt   = 'moveRight'
    #scale time
    sclTmTx = 'scale'
    sclTmBy = 'scaleTimeBy'
    #subframe out
    sbfrm   = 'subframeOut'
    #unify keys
    unfy    = 'unifyKeys'
    #bake infinity
    bkInfty = 'bakeInfinity'

    #default GE items to switch, only works with default GE not a tearOff
    t   = 'textField5'
    x   = 'formLayout39'
    p   = 'formLayout38'

    if not cmds.control(filD, ex=1):
        cmds.formLayout(p, e=1, h=52)
        cmds.control(t, e=1, m=0)
        cmds.control(x, e=1, m=0)
        cmds.setParent(p)
        #build
        item = geButton(name=filD, parent=p, label='::', cmd="import display_lib\nreload(display_lib)\ndisplay_lib.geFieldTx('graphFilter','tr*,ro*')", gap=2, w=15,bg=[0.2, 0.3, 0.5],ann="add default channel filter: tr*,ro*")
        item = geField(name=fil, parent=p, attach=item, cmd="import graphFilter\nreload(graphFilter)\ngraphFilter.graphEditorCMD()",w=185, gap=2, ann="add channel filters by name and/or wildcards: 't*X'")
        item = geButton(name=hldPre, parent=p, attach=item, label='<--', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv(postCurrent=False)', gap=5, bg=[0.4, 0.2, 0.2],ann='hold value of selected curve to the left')
        item = geButton(name=hldAll, parent=p, attach=item, label='HOLD', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv()', w=45, gap=0, bg=[0.5, 0.2, 0.2], ann='hold value of selected curve')
        item = geButton(name=hldPost, parent=p, attach=item, label='-->', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.holdCrv(preCurrent=False)', gap=0, bg=[0.4, 0.2, 0.2], ann='hold value of selected curve to the right')
        item = geButton(name=sclDwn, parent=p, attach=item, label='-', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(0.975)', gap=5, bg=[0.1, 0.4, 0.4], ann='scale curve:\npivot @ key = keys with same values selected\npivot @ 0     = keys with dif values selected\n')
        item = geHeading(name=sclTx, parent=p, attach=item, label='SCALE', gap=0, w=45, bgc=[0.25, 0.4, 0.4])
        item = geButton(name=sclUp, parent=p, attach=item, label='+', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(1.025)', gap=0,  bg=[0.1, 0.4, 0.4], ann='scale curve:\npivot @ key = keys with same values selected\npivot @ 0     = keys with dif values selected\n')
        item = geButton(name=flp, parent=p, attach=item, label='FLIP', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.scaleCrv(-1)', w=50, gap=0, bg=[0.1, 0.4, 0.4])
        item = geButton(name=movDwn, parent=p, attach=item, label='-', cmd="import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.moveValue(False)",  gap=5, bg=[0.3, 0.3, 0.5], ann='nudge keys/curves down in value')
        item = geHeading(name=movTx, parent=p, attach=item, label='VALUE', gap=0, bgc=[0.35, 0.35, 0.5])
        item = geButton(name=movUp, parent=p, attach=item, label='+', cmd="import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.moveValue(True)", gap=0,  bg=[0.3, 0.3, 0.5], ann='nudge keys/curves up in value')
        item = geButton(name=movTmLf, parent=p, attach=item, label='<', cmd="import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.moveTime(True)", gap=5, bg=[0.2, 0.3, 0.5],ann='move keys/curves to the left')
        item = geHeading(name=movTmTx, parent=p, attach=item, label='TIME', gap=0, bgc=[0.3, 0.35, 0.5])
        item = geButton(name=movTmRt, parent=p, attach=item, label='>', cmd="import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.moveTime(False)",  gap=0, bg=[0.2, 0.3, 0.5],ann='move keys/curves to the right')
        item = geHeading(name=sclTmTx, parent=p, attach=item, label='SCALE TIME', w=65)
        item = geField(name=sclTmBy, parent=p, attach=item, cmd="import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.animScale(cmds.textField('scaleTimeBy',query=True,tx=True))",w=40, gap=2, tx=1.0, ann='Scale selected curves from the first frame of playback' )
        item = geButton(name=sbfrm, parent=p, attach=item, label='SUBfrm_X', cmd='import constraint_lib\nreload(constraint_lib)\nconstraint_lib.subframe()', w=70, gap=20, bg=[0.5,0.5,0],ann='subframes to whole frames ')
        item = geButton(name=unfy, parent=p, attach=item, label='UNIFY', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.unifyKeys()', w=70, gap=0, bg=[0.3, 0.5, 0.3])
        item = geButton(name=bkInfty, parent=p, attach=item, label='BAKE_Infnty', cmd='import animCurve_lib\nreload(animCurve_lib)\nanimCurve_lib.bakeInfinity()', w=70, gap=0, bg=[0.5, 0.3, 0.4])
    else:
        #clean UI
        xx = GeBtn()
        d  = xx.__dict__
        try:
            for s in d:
                if cmds.control(str(d[s]), ex=1):
                    cmds.deleteUI(d[s], control=True)
        except:
            print 'cant delete all', xx.__dict__
        cmds.formLayout(p, e=1, h=28)
        cmds.control(t, e=1, m=1)
        cmds.control(x, e=1, m=1)

class GeBtn():
    def __init__(self):
        #filter
        self.filD    = 'FilterDefault'
        self.fil     = 'graphFilter'
        #hold
        self.hldPre  = 'holdPre'
        self.hldAll  = 'holdAll'
        self.hldPost = 'holdPost'
        #scale
        self.sclDwn = 'scaleDown'
        self.sclTx   = 'scaleTxt'
        self.sclUp   = 'scaleUp'
        self.flp     = 'FlipCurves'
        #value move
        self.movDwn  = 'moveDown'
        self.movTx  = 'moveValue'
        self.movUp   = 'moveUp'
        #time move
        self.movTmLf   = 'moveLeft'
        self.movTmTx   = 'moveTime'
        self.movTmRt   = 'moveRight'
        #scale time
        self.sclTmTx = 'scale'
        self.sclTmBy = 'scaleTimeBy'
        #subframe out
        self.sbfrm   = 'subframeOut'
        #unify keys
        self.unfy    = 'unifyKeys'
        #bake infinity
        self.bkInfty = 'bakeInfinity'


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
