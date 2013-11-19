import os
import maya.cmds as cmds
import maya.mel as mm


def job():
    rootPath = "C:/Users/Slabster & Vicster/Documents/maya/scripts"
    path = rootPath + "/faceRig_selection_pair.txt"
    pairList = []
    pair = []
    lf = True
    for line in open(path).readlines():
        line = line.strip('\n')
        if lf:
            pair.append(line)
            lf = False
        else:
            pair.append(line)
            pairList.append(pair)
            pair= []
            lf = True
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        sel = sel[len(sel)-1]
        if ':' in sel:
            gg = sel.split(':')[1]
            ref = sel.split(':')[0]
        for p in pairList:
            if gg in p:
                p.remove(gg)
                cmds.select(ref + ':' + p[0], tgl=True)
                break
    else:
        pass
        #print 'failed'

def toggleIcon(*args):
    #List all the layouts in Maya
    controlLayouts = cmds.lsUI(controls = True)
    #interate through the layouts and find the shelves
    for control in controlLayouts:
        if control == 'Custom' or control == 'Rendering':
            children = cmds.shelfLayout(control, query = True, ca = True)
            if children:
                for child in children:
                    checkJob = scanForSrvSelScriptJob()
                    #find that shelfButton that's using the appropriate image, then change it
                    getImage = cmds.shelfButton(child, query = True, image = True)
                    icon_path = 'C:/Users/Slabster & Vicster/Documents/maya/2013-x64/prefs/icons'
                    #icon_path = os.getenv("KEY_MAYA_ICON")
                    if getImage == icon_path + '/srv_mirSel_off_icon.xpm' or getImage == icon_path + '/srv_mirSel_on_icon.xpm':
                        if checkJob == True:
                            cmds.shelfButton(child, edit = True, image = icon_path + '/srv_mirSel_on_icon.xpm')
                        else:
                            cmds.shelfButton(child, edit = True, image = icon_path + '/srv_mirSel_off_icon.xpm')
                    elif getImage == 'srv_mirSel_off_icon.xpm' or getImage == 'srv_mirSel_off_icon.xpm':
                        if checkJob == True:
                            cmds.shelfButton(child, edit = True, image = 'srv_mirSel_on_icon.xpm')
                        else:
                            cmds.shelfButton(child, edit = True, image = 'srv_mirSel_off_icon.xpm')
        
'''
class MirrorSelect():
    def __init__ (self):
    
    def icon(self):
    
    def script(self):
    
    def pair(self):
    
    def selection(self):
'''










'''

print '---- in srv_pair module... wy? -----'

srvPairList = [[],[]]
#changeme
pairPath = os.getenv('KEY_TOOLS_PYTHONPATH') + '/surveyor/code/faceRig_selection_pair.txt'

def test(srvPairList):
	cnt = 0
	for line in open(pairPath).readlines():
		check = cnt%2
		if check == 0:
			srvPairList[[0][0]].append((line).strip('\n'))
		else:
			srvPairList[[1][0]].append((line).strip('\n'))
		cnt += 1
			
def srv_selChanged(*args):
	undoInfo = cmds.undoInfo(query = True, undoName = True)
	selList = []
	if undoInfo.find('select') > -1:	
		sel = cmds.ls(selection = True)
		if len(sel) == 1:
			for i in range(0, len(srvPairList[0]), 1):
				if (sel[0] == srvPairList[0][i]):
					cmds.undo()
					cmds.select(cl =True)
					selList.append(srvPairList[1][i])
					selList.append(srvPairList[0][i])
	
		
				elif sel[0] == srvPairList[1][i]:
					cmds.undo()
					cmds.select( cl = True)
					selList.append(srvPairList[0][i])
					selList.append(srvPairList[1][i])

			cmds.select(selList)
'''