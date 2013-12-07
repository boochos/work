import maya.cmds as cmds
import display_lib as ds

def graphFilterCore(attr='', panel=''):
    '''\n
    adds/clears filters for the default graphEditor
    '''
    #graph editor (default graphEditor supported only)
    #panel = cmds.getPanel(wf=True) #old way,
    #check for any filters currently being used
    c = cmds.outlinerEditor(panel + 'OutlineEd', q=True, af=True)
    #if attrs arg is not empty execute, else delete filters reset filter to None
    if attr != '':
        #make new filter
        f = cmds.itemFilterAttr(bn=attr)
        #f = cmds.rename(f, panel + '_attrFilter___' + attr.replace('*', '_') + '___')
        #if a filter is already being used merge new/current #else use new filter
        if c != '0':
            #unify new/current filter
            cf = cmds.itemFilterAttr( un=[c, f])
            #delete current filter
            cmds.delete(c)
            #set unified filter
            ##for graph in panel:
            cmds.outlinerEditor(panel + 'OutlineEd', e=True, af=cf)
        else:
            #set new filter
            ##for graph in panel:
            cmds.outlinerEditor(panel + 'OutlineEd', e=True, af=f)
    else:
        if c != '0':
            #clear all user filters
            #d = cmds.itemFilterAttr( luf=True)
            #cmds.delete(d)
            cmds.delete(c)
        #reset filters to None
        ##for graph in panel:
        cmds.outlinerEditor(panel + 'OutlineEd', e=True, af=0)
        #print '---filters for ' + panel + ' cleared---'
    
def graphFilters(attrs, panel=''):
    '''\n
    attrs should be seperated by commas
    use * as for wildcards/shortcuts ie.(ro*X) will filter rotateX
    '''
    shortName = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    longName = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
    print panel, '___panel'
    if attrs == '':
        graphFilterCore(attr='',panel=panel)
    else:
        #clear any filters
        graphFilterCore(attr='',panel=panel)
        #run new filters
        givenList = attrs.split(',')
        for givenName in givenList:
            i=0
            givenName = givenName.strip(' ')
            for short in shortName:
                if givenName == short:
                    givenList.append(longName[i])
                i=i+1
        #print givenList
        for attr in givenList:
            graphFilterCore(attr=attr,panel=panel)

def graphEditorCMD():
    ui = ds.GeBtn()
    panel = ds.findControlParent(control=ui.fil, split=5)
    panel = panel.split('|')
    attrs = cmds.textField(ui.fil, query=True, tx=True)
    graphFilters(attrs, panel[len(panel)-1])
