#==============================================================
# Jeremy Mesana
#==============================================================

import maya.cmds as mc
import maya.OpenMaya as om 

# function that swaps space on frame
def swapSpaceOnFrame ( objName, newSpaceSetting, newSpaceIndex ):

	keyAtts = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','space']
	
	#create null
	if not mc.objExists ( 'xNull' ):
		xNull = mc.spaceLocator ( n = 'xNull' )

	#constrain point and orient null to object
	mc.pointConstraint ( objName, xNull )
	mc.orientConstraint ( objName, xNull )

	#remove constaints
	mc.delete ( xNull, cn = True )

	#set objName space attr to new space
	mc.setAttr ( '%s.space' %objName, newSpaceIndex )

	#constrain obj to null to get back original position and rotations
	try:
		pConstraint = mc.pointConstraint ( xNull, objName )
	except:
		#ignore if can't make constraint
		pass

	try:
		rConstraint = mc.orientConstraint ( xNull, objName )
	except:
		#ignore if can't make constraint
		pass

	#key object atts that have keys on them
	mc.setKeyframe ( objName, at = keyAtts )

	if pConstraint:
		mc.delete ( pConstraint )

	if rConstraint:
		mc.delete ( rConstraint )


	#delete xNull
	if mc.objExists ( 'xNull' ):
		mc.delete ( 'xNull' )


def swapSpaceAnim ( objName, newSpaceSetting, newSpaceIndex ):

	keyAtts = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ', 'space']

	currentFrame = mc.currentTime ( q = True )
	firstFrame = mc.playbackOptions ( min = True, query = True )
	lastFrame = mc.playbackOptions ( max = True, query = True )

	########################################################################
	#	IsolateSelected in all model windows
	########################################################################
	allPanels = mc.getPanel ( type = 'modelPanel' )
	currentPanel = mc.getPanel ( withFocus = True )

	# turn on isolateSelect for all modelPanels
	for p in allPanels:
		mc.isolateSelect ( p, state = 1 )

	########################################################################


	#create null
	if not mc.objExists ( 'xNull' ):
		xNull = mc.spaceLocator ( n = 'xNull' )

	# find keyframes
	keys = []
	allKeys = mc.keyframe( objName, time = (firstFrame,lastFrame),query=True, attribute = keyAtts )


	# sort keys and remove duplicates
	if allKeys:
		for k in allKeys:
			if k not in keys:
				keys.append (k)
		keys = sorted(keys)

	if keys:

		# loop once and set keyframes for position and rotation on all keys for trans and rots and space
		for k in keys:
			mc.currentTime (k)
			mc.setKeyframe (objName, attribute = keyAtts, time = (k,k) )

		# loop through again and do swap
		for k in keys:

			mc.currentTime (k)

			##### Swapping stuffs

			#constrain point and orient null to object
			mc.pointConstraint ( objName, xNull )
			mc.orientConstraint ( objName, xNull )

			#remove constaints
			mc.delete ( xNull, cn = True )

			#set attr to new space
			mc.setAttr ( '%s.space' %objName, newSpaceIndex )

			#constrain obj to null to get back original position and rotations
			try:
				pConstraint = mc.pointConstraint ( xNull, objName )
			except:
				pass

			try:
				rConstraint = mc.orientConstraint ( xNull, objName )
			except:
				pass

			#key object
			mc.setKeyframe ( objName, attribute = keyAtts )

			#delete constraints
			if pConstraint:
				mc.delete ( pConstraint )
			if rConstraint:
				mc.delete ( rConstraint )

		#return to original frame
		mc.currentTime ( currentFrame )


	# POST swap stuff

	# delete xNull
	if mc.objExists ( 'xNull' ):
		mc.delete ( 'xNull' )

	# euler filter curve
	mc.select ( objName )
	mc.filterCurve ( )

	#turn off isolateSelect for all model panels
	if allPanels:
		for p in allPanels:
			mc.isolateSelect ( p, state = 0 )


# onFrame and overTime button press function
def doSwitch ( switchType ):

	# check whats in the space settings UI
	spaceObjects = mc.columnLayout( 'settingsColumn', q = True, childArray = True)

	# check objects current space setting vs ui space setting
	# if different run appropriate space swap function
	if spaceObjects:
		for spaceObject in spaceObjects:
			objName = mc.optionMenu ( spaceObject, q = True, label = True )
			spaceUISetting = mc.optionMenu ( spaceObject, q = True, v = True )
			spaceUIIndex = mc.optionMenu ( spaceObject, q = True, sl = True ) - 1

			if objName:
				# query objects current space attr
				currentSpace = mc.getAttr ( '%s.space' %objName, asString = True )


				if currentSpace != spaceUISetting:
				
					# switch on frame
					if switchType == 'frame':

						swapSpaceOnFrame ( objName, spaceUISetting, spaceUIIndex )

					# switch all anim keys
					elif switchType == 'anim':
					
						swapSpaceAnim ( objName, spaceUISetting, spaceUIIndex )
	

		

# function that loads selected cons with space attr
def loadSelected ( *args ):

	# clear loaded char cons
	uiChildren = mc.columnLayout( 'settingsColumn', q = True, childArray = True )
		
	if uiChildren:
		for child in uiChildren:
			mc.deleteUI ( child, control = True )	

	
	sels = mc.ls ( selection = True )
	chars = []
	loadCons = []
	
	if sels:
	
		for sel in sels:
			selAttrs = mc.listAttr ( v = True, u = True )
			
			if selAttrs:
				for selAttr in selAttrs:

					if selAttr == 'space':
					
						if sel not in loadCons:
							loadCons.append ( sel )
								
	if loadCons:
	
		mc.setParent ( 'settingsColumn' )
		
		for loadCon in loadCons:
		
			currentSetting = mc.getAttr ( '%s.space' %loadCon, asString = True )
			spaceList = mc.attributeQuery ( 'space', node = loadCon, le = True )

			if spaceList:
				
				spaces = spaceList[0].split ( ':' )
		
			uiConName = mc.optionMenu ( label = loadCon )
			if spaces:
				for space in spaces:
					mc.menuItem ( label = space )
			
			mc.optionMenu ( uiConName, edit = True, v = currentSetting )
		
#### UI stuff
def spaceSwap_UI ():


	if mc.window ('spaceSwapWindow', exists = True):
		mc.deleteUI ('spaceSwapWindow', window = True)

	if mc.windowPref('spaceSwapWindow', exists=True):
	       mc.windowPref('spaceSwapWindow', remove=True)	
	
	spaceSwapWindow = mc.window( 'spaceSwapWindow', t = 'Space Switcher v1.3', w = 300, h = 400)
	
	mainForm = mc.formLayout()
	
	loadSelectedButton = mc.button ( label='Load Selected', h = 40, command = loadSelected )

	buttonFrame = mc.frameLayout ( 'buttonFrame', label='Space Switch Type', borderStyle='etchedIn', h = 100 )
	buttonForm = mc.formLayout()	
	
	frameButton = mc.button( label='On\nFrame', w = 125, h = 50, command = lambda x, y = 'frame': doSwitch ( y ) )
	animButton = mc.button( label='Over\nTime', w = 125, h = 50, command = lambda x, y = 'anim': doSwitch ( y ) )
	
	mc.formLayout (buttonForm, edit = True, attachForm = [	(frameButton, 'top', 10), (frameButton, 'left', 5 ),\
								(animButton, 'top', 10), (animButton, 'left', 157 ), \
								])

	mc.setParent ( mainForm )


	settingsFrame = mc.frameLayout ( 'settingsFrame', label='Space Settings', borderStyle='etchedIn', h = 270 )
	settingsScroll = mc.scrollLayout ( 'settingsScroll', h = 225, w = 265)
	settingsColumn = mc.columnLayout( 'settingsColumn', rowSpacing=5)


	mc.formLayout (mainForm, edit = True, attachForm = [	(buttonFrame, 'top', 10), (buttonFrame, 'left', 5) , (buttonFrame, 'right', 5),\
								(loadSelectedButton, 'top', 120), (loadSelectedButton, 'left', 10) , (loadSelectedButton, 'right', 10),\
								(settingsFrame, 'top', 170), (settingsFrame, 'left', 5), (settingsFrame, 'right', 5), (settingsFrame, 'bottom', 5),\
								])
	
	mc.showWindow( spaceSwapWindow )
	loadSelected ()
