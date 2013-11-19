#########################
# Python Module Imports #
#########################
import maya.cmds as cmds
import maya.mel
import os
import shutil

######################
# Main DIR Variables #
######################
s_mainDIR = 'C:/VFX/projects/Scarecrow/Work/'
s_prjFolder = '/maya/'
s_libFolder = 'C:/VFX/projects/Scarecrow/IO/_Library/Scarecrow_asset'

#import workspace file
#s_wsFile = '//ml63/D/_image/_projects/SI/StepDogs/_library/_pipeline/workspace.mel'

#######################################
# Add _library to the top fo the list #
#######################################
s_list = os.walk(s_mainDIR).next()[1]
s_list.reverse()


##########################
# Project Set Definition #
##########################
def setProject():
	s_projDirSel = cmds.textScrollList('PROJECT_DIR', query=True, si=True)
	if (s_projDirSel[0] == '_library'):
		s_projDir = s_mainDIR + s_libFolder
		
	else:
		s_projDir = str(s_mainDIR + s_projDirSel[0] + s_prjFolder)
		
		
	#cmds.evalDeferred(cmds.workspace(s_projDir, o=True))
	s_melCommand = ('setProject "' + s_projDir + '";')	
	maya.mel.eval(s_melCommand)
	
	#shutil.copy (s_wsFile, s_projDir)	
	#s_melCommand = ('source "' + s_projDir + '/workspace.mel"')
	#maya.mel.eval(s_melCommand)
	
	cmds.confirmDialog(title='Setting Project', message=s_projDir)
	#cmds.deleteUI('ProjSel')
		

	
#######
# GUI #
#######
if (cmds.window('ProjSel', ex=True) ==1 ):
	cmds.deleteUI('ProjSel')
cmds.window('ProjSel', title='Project Dir Selection', )
cmds.paneLayout()
cmds.textScrollList('PROJECT_DIR', numberOfRows=80, allowMultiSelection=False, append=s_list, showIndexedItem=1, dcc=setProject)
cmds.showWindow()


