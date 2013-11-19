import os
import maya.cmds as cmds
import maya.mel as mm
import sys_lib as ksl

def message(what='', maya=False):
    what = '-- ' + what + ' --'
    if maya == True:
    	mm.eval('print \"' + what + '\";')
    else:
        print what

#-------------
#Name        :scanForSrvSelScriptJob
#Arguments   :<None> 
#Description :check to see if the srv_selChanged script job is running
#-------------
def scanForSrvSelScriptJob(*args):
    import maya.mel as mm
    returnVar = False
    getJobs = mm.eval('scriptJob -listJobs')
    for job in getJobs:
        if job.find("srv_selChanged($srv_selLarray, $srv_selRarray)") != -1:
            message('Mirror Selection ON.')
            returnVar = True

    message('Mirror Selection  OFF.')
    return returnVar
#-------------
#Name        :toggleSrvMirSelIcon
#Arguments   :<None>
#Description :toggles the state of all instances of srv_mirSel_off_icon.xpm and srv_mirSel_off_icon.xpm from
#             one to the other
#-------------    
def toggleSrvMirSelIcon(*args):
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

#---End def toggleSrvMirSelIcon