from __future__ import with_statement
from pymel.core import *
from key_core import key_ui
from key_core import key_ui_core
import maya.OpenMaya as OpenMaya
import pickle, time
import maya.mel as mm
from xml.dom import minidom

def removeDeformedFromName(*args):
    sceneNodes = ls(type='mesh')
    
    for node in sceneNodes:
	if node.name().rfind('ShapeDeformed') > -1:
	    name = node.name().replace('Deformed','')
	    node.rename(name)

class MayaXmlChannelInfo(object):
    def __init__(self):
        self.channelName           = None
        self.channelType           = None
        self.channelInterpretation = None
        self.samplingType          = None
        self.samplingRate          = None
        self.startTime             = None
        self.endTime               = None
        
class MayaXmlCacheInfo(object):
    def __init__(self,path,visibility_list=[]):
        self.xml = minidom.parse(path)
        self.path            = path
        self.visibility_list = visibility_list
        self.cacheType       = None
        self.cacheFormat     = None 
        self.timeRange       = None
        self.timePerFrame    = None
        self.cacheVersion    = None
        self.cachePath       = None
        self.version         = None
        self.author          = None
        self.selection_list  = []
        self.channel         = {}
	self.setVis          = []
        self.parse()
        self.populateSelectionList()
        
    def removeTextNodes(self, nodeList):
        for i in range(len(nodeList),0,-1):
            if nodeList[i-1].nodeType == nodeList[i-1].ELEMENT_NODE:
                self.removeTextNodes(nodeList[i-1].childNodes)
                
            elif nodeList[i-1].nodeType == nodeList[i-1].TEXT_NODE:
                parent = nodeList[i-1].parentNode
                if parent.tagName != 'extra':
                    parent.removeChild(nodeList[i-1])

    def populateSelectionList(self):
        for i in range(0,len(self.channel.keys()),1):
            self.selection_list.append(self.channel['channel'+ str(i)].channelName)

    def parse(self):
        extraCnt = 0
        for node in self.xml.documentElement.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.tagName == 'cacheType':
                    self.cacheType   = node.getAttribute('Type')
                    self.cacheFormat = node.getAttribute('Format')
                    
                elif node.tagName == 'time':
                    self.timeRange = node.getAttribute('Range')

                elif node.tagName == 'cacheTimePerFrame':
                    self.timePerFrame = node.getAttribute('TimePerFrame')
                
                elif node.tagName == 'cacheVersion':
                    self.version = node.getAttribute('Version')
                
                elif node.tagName == 'extra':
                    if extraCnt == 0: 
                        self.cachePath = node.childNodes[0].data
                    elif extraCnt == 1:
                        self.version   = node.childNodes[0].data
                    else:
                        self.author    = node.childNodes[0].data
                    extraCnt += 1
                
                elif node.tagName == 'Channels':
                    for child in node.childNodes:
                        if child.nodeType == child.ELEMENT_NODE:
                            channelObj = MayaXmlChannelInfo()
                            channelObj.channelName           = child.getAttribute('ChannelName').strip('\n\t')
                            channelObj.channelType           = child.getAttribute('ChannelType').strip('\n\t')
                            channelObj.channelInterpretation = child.getAttribute('ChannelInterpretation').strip('\n\t')
                            channelObj.samplingType          = child.getAttribute('SamplingType').strip('\n\t')
                            channelObj.samplingRate          = child.getAttribute('SamplingRate').strip('\n\t')
                            channelObj.startTime             = child.getAttribute('StartTime').strip('\n\t')
                            channelObj.endTime               = child.getAttribute('EndTime').strip('\n\t')
                            self.channel[child.tagName]      = channelObj
		
		elif node.tagName == 'Visibility':
		    for child in node.childNodes:
			if child.nodeType == child.ELEMENT_NODE:
			    self.setVis.append([child.getAttribute('Name'),child.getAttribute('visibility')])
			    
    def printChannels(self):
        channels = self.channel.keys()
        channels.sort()
        for obj in channels:
            print '=== Start %s ===' %(obj)
            for sub in self.channel[obj].__dict__:
                print '\t%s = %s' %(sub, self.channel[obj].__dict__[sub])
            print '===  End %s ===' %(obj)
            
    def printAttr(self):
        print '========== START =========='
        for i in self.__dict__:
            if i != 'xml':
                print i, '=', self.__dict__[i]
        print '==========  END  =========='
    
    def addSelectedToXml(self):
        visNode = self.xml.getElementsByTagName('Visibility')
        node    = None
        if len(visNode) != 0 and len(self.visibility_list) > 0 :
            node = visNode[0]
        else:
            node   = self.xml.createElement('Visibility')
        for i in self.visibility_list:
            cNode = self.xml.createElement('Object')
            cNode.setAttribute('Name', i.name()[i.name().rfind(':')+1:])
            cNode.setAttribute('visibility', str(i.visibility.get()))
            node.appendChild(cNode)
        self.xml.documentElement.appendChild(node)
	
	fp = open(self.path,'w')
	self.xml.writexml(fp, '', "\t", "\n", "UTF-8")
	fp.close()
	
class Atom_Tag_Core(object):
    '''
    Class: <Atom_Tag_Core>: Class that reads the predefined directory structure provided in the path and connections objects
                                    based on what has been parsed.

    Methods:
    __init__(path, base_catagory, base_type, base_name, connect) -- Class initialization.
    -Note: the base path is expected to follow the proper file structure for the initilization.
                    
    -base_catagory(provided name, in all cases should be atom)
       + base_type (folder name) - anim,cache, etc..
          + base_name (folder name) - the name off the specfic rig 
             + master_name (folder name) - the name of an object that exists in the maya scene
                + head(.txt file) - file name is the attrtibute to create on the out and in objects, out object is the master
                + lArm(.txt file)   in objects are contained in the .txt files and must exist in the scene being tagged
    
    validate_dirPath -- Validate the existance of the specified folder in the specified path.
    createTagDict    -- Read the selection_lists file structure for its contents and build a dictionary based upon the predefined convention.
                        {base_catagory:{base_type:{base_name:{master:[attr_list]}}}}
    deleteAllTags    -- List all the transforms in the scene and delete the atom attribute tag if they have one
    printTagDict     -- Print out the current tagDict and how it's being nested. 
    getMasters       -- Get all the masters in the scene.
    '''
    def __init__(self, path = os.path.join(os.getenv('KEY_PROJECT_PATH'),'tags'),mShapeType='mesh'): 
        self.tlp        = path
	self.mShapeType = mShapeType
        #Nested dictionary that reflects the folder convention
        self.tagDict    = {}
        #dictionary that's populated with reference node: reference master's
        self.masterDict    = {'None_Referenced':[]} 
        self.createTagDict()
 
    def validate_dirPath(self,path, dirObj):
        if os.path.isdir(path) and dirObj[0] != '.':
            return True
        else:
            return False
        
    def createTagDict(self):
        #{base_catagory:{base_type:{base_name:{master:[attr_list]}}}}
        for i in os.listdir(self.tlp): 
            if self.validate_dirPath(self.tlp,i):
                self.tagDict[i] = {}
                #base type path
                btp = os.path.join(self.tlp,i)
                #follow the path of the specified type
                for j in os.listdir(btp):
                    if self.validate_dirPath(btp,j):
                        #base name path
                        self.tagDict[i][j]={}
                        bnp=os.path.join(btp,j)
                        for k in os.listdir(bnp):
                            if self.validate_dirPath(bnp, k):
                                #base master path
                                self.tagDict[i][j][k]={}
                                bap = os.path.join(bnp,k)
                                for l in os.listdir(bap):
                                    if self.validate_dirPath(bap, l):
                                        filePath = os.path.join(bap,l)
                                        if os.path.isfile(filePath) and l[0] != '.':
                                            fObj = open(filePath,'r')
                                            fLines = fObj.readlines()
                                            fObj.close()
                                            inObjList=[]
                                            for m in fLines:
                                                inObjList.append(m.strip('\n'))
                                            self.tagDict[i][j][k][l]=inObjList
    def deleteAllTags(self,*args):
        #get all the scene transform nodes
        transform = ls(type='transform')
        #set up the print string
        printStr  = ''
        conDiag   = confirmDialog(title='Confirm Tag Delete', message='Are you sure you want to delete ALL tags in scene?',button=['Yes', 'No'],cb='No')
        if conDiag == 'Yes':
            for tran in transform:
                #check for an atom attribute(tag)
                
                if tran.hasAttr('atom'):
                    #Delete it and provide feedback
		    deleteAttr(tran.atom)
		    for i in tran.listAttr():
			if i.find('atomSpecial') != -1:
			    deleteAttr( i)

    def printTagDict(self, base_search='anim', name_search='dog', search_depth = 3):
        base_keys = self.tagDict.keys()
        printStr  = ''
        
        depth = 0
        if base_search in base_keys and depth <= search_depth:
            printStr += '--%s \t| (base_type)' %(base_search)
            name_keys = self.tagDict[base_search].keys()
            
            depth = 1
            if name_search in name_keys and depth <= search_depth:
                printStr += '\n\t--%s \t| (base_name)' %(name_search)
                
                depth = 2
                if depth <= search_depth:
                    master_keys = self.tagDict[base_search][name_search].keys()
                    for master in master_keys:
                        printStr += '\n\t\t--%s \t| (master)' %(master)
                        tag_values = self.tagDict[base_search][name_search][master].keys()
                        
                        depth = 3
                        if depth <= search_depth:
                            for tag in tag_values:
                                printStr += '\n\t\t\t--%s \t| (tag)' %(tag)
                                for obj in self.tagDict[base_search][name_search][master][tag]:
                                    printStr += '\n\t\t\t\t++%s \t| (tag_obj)' %(obj)
                                printStr += '\n'
            print printStr 
	    
    def getMasters(self):
	shapeTypeList = ['mesh', 'nurbsSurface']
	#sort them in the list
	tmpShp = []
        #get all the transform nodes in the scene
	for shape in shapeTypeList:
	    shapes = ls(type=shape)
	    for i in shapes:
		tmpShp.append(str(i))
	tmpShp.sort(key=str.lower)
        shapes = tmpShp
        #check each object for the .atom attribute
        for  shape in shapes:
	    shape = ls(shape)[0]
	    pObj = shape.getParent()
            if pObj.hasAttr('atom'):
                #get the master of the object
                getCon = pObj.atom.children()[0].children()[0].children()[0].children()[0].connections(s=True,d=False)
                master = None
                #if an empty list is returned, there is no master, which makes the node the master
                if len(getCon) == 0:
                    master=pObj
		elif len(getCon) == 1:
		    #condition if the master has a connection going into itself
		    if getCon[0] == pObj.name():
			master = pObj

                #this object has a master
                if master != None:
                    #test if the node is referenced
                    if not master.isReferenced():
			if not master in self.masterDict['None_Referenced']:
			    self.masterDict['None_Referenced'].append(master)
                    else:
                        #the reference node is the dictionary value, the nodes in the reference are appended in a list
                        #within the dictionary
                        ref = referenceQuery(master, rfn = True,topReference=True)
			
                        #check if the node is all ready in the dictionary
                        if not self.masterDict.has_key(ref):
                            self.masterDict[ref]=[master]
                        else:
                            if not master in self.masterDict[ref]:
				self.masterDict[ref].append(master)

class Atom_Tag(Atom_Tag_Core):
    '''
    Class: <Atom_Tag_Core> : Class for setting up the tagging of objects.
    
    Methods: 
      __init__ : initialization.
      tag      : tag object with attributes based on the tag dictionary and how the function has been fed.
       
    '''
    def __init__(self,base_catagory = 'atom', base_type = 'anim', base_name='dog', master='master'):
        super(Atom_Tag,self).__init__()
        self.base_catagory  = base_catagory
        self.base_type      = base_type
        self.base_name      = base_name
        self.master         = master 
        #tag the objects
        self.tag()

    def tag(self):
        if self.tagDict.has_key(self.base_type):
            if self.tagDict[self.base_type].has_key(self.base_name):
                if len(self.tagDict[self.base_type][self.base_name].keys()) > 0:
                    if objExists(self.master):
                        master = ls(self.master)[0]
                        attrLength = len(self.tagDict[self.base_type][self.base_name][master.name()])
                        atName = self.base_catagory
                        execList=[]

                        #create the attributes on the master
                        master.addAttr(self.base_catagory, nc = 1,          at='compound')        
                        master.addAttr(self.base_type,     nc = 1,          at='compound', parent= self.base_catagory)
                        master.addAttr(self.base_name,     nc = 1,          at='compound', parent= self.base_type)
                        master.addAttr(master.name(),      nc = attrLength, at='compound', parent= self.base_name)
                        
                        #add all the attributes
                        for attr in self.tagDict[self.base_type][self.base_name][self.master].keys():
                            master.addAttr(attr, at= 'message', parent=self.master)
                        
                        for attr in self.tagDict[self.base_type][self.base_name][self.master].keys():                            
                            for inObjStr in self.tagDict[self.base_type][self.base_name][self.master][attr]:
                                if objExists(inObjStr):
                                    inObj = ls(inObjStr)[0]
                                    if self.master != inObj.name():                                     
				
                                        inObj.addAttr(self.base_catagory, nc = 1,          at='compound')        
                                        inObj.addAttr(self.base_type,     nc = 1,          at='compound', parent= self.base_catagory)                        
                                        inObj.addAttr(self.base_name,     nc = 1,          at='compound', parent= self.base_type)
                                        inObj.addAttr(self.master,        nc = 1         , at='compound', parent= self.base_name)
					if not inObj.hasAttr(attr):
					    inObj.addAttr(attr,at='message',  parent = self.master)
					    execList.append('ls("' + master.name() + '")[0].' + attr + '.connect(ls("'+inObj.name() +'")[0].'+ attr + ')')
                                        
					else:
					    errorStr = ('In Object: "%s" , has the attr: ', skipping) %(inObjStr, attr)
					    OpenMaya.MGlobal.displayWarning(errorStr)
				    else:
					specAttr = 'atomSpecial_' + attr
					inObj.addAttr(specAttr, at='message')
					exeStr = 'ls("' + inObj.name() + '")[0].' + specAttr + '.connect(ls("'+inObj.name() +'")[0].'+ attr + ')'
					exec(exeStr)
                                else:
                                    errorStr = ('In Object: "%s" , not found in scene, tagging on object failed' ) %(inObjStr)
                                    OpenMaya.MGlobal.displayError(errorStr)
                                
                        #Connect the attributes
                        for i in execList:
                            try:
				exec(i)
                            except:
                                print '%s failed to execute' %(i)
                       
                        print '// Out Connections made from "%s"' %(master.name())
                        
                    else:
                        errorStr = ('Master Object: "%s" , not found in scene, tagging failed' ) %(self.master)
                        OpenMaya.MGlobal.displayError(errorStr)
                else:
                    errorStr = ('Master Name Folder: "%s", does not exist in path, tagging failed...') %(self.base_name)
                    OpenMaya.MGlobal.displayError(errorStr)
            else:
                errorStr = ('Base Name Folder: "%s", does not exist in path, tagging failed...') %(self.base_name)
                OpenMaya.MGlobal.displayError(errorStr)
        else:
            errorStr = ('Base Type Folder: "%s", does not exist in path, tagging failed...') %(self.base_type)
            OpenMaya.MGlobal.displayError(errorStr)
	    
class Atom_Tag_Win(Atom_Tag_Core):
    '''
    class <Atom_Tag_Win> : Class with a UI and functions to set up tagging.
    
    Methonds:
      __init__              : Class initialization
      getTagDictValues<int> : Get dictionary keys based on depth
      validateSelection<int>: Validate selection in the user interface.
      tagCmd:               : Command to tag the specified UI objects
      tslCmd:               : Command when something is selected in the Text Scroll List
      buildTagPanelLayout   : Panel Layout creation 
      win                   : Tagging window         
    '''
    def __init__(self):
        super(Atom_Tag_Win,self).__init__()
        self.controlList = ['atom_tag_type_tsl','atom_tag_name_tsl', 'atom_tag_mstr_tsl','atom_tag_tsl', 'atom_obj_tsl']
    
    def getTagDictValue(self, depth=0):
        base_keys = self.tagDict.keys()
        if depth == 0:
            return base_keys
        
    def validateSelection(self, depth):
        selIdx = textScrollList(self.controlList[depth], query=True,sii=True)
        listCnt = textScrollList(self.controlList[depth], query=True,ni=True)
        if len(selIdx) > 0:
            if selIdx[0] <= listCnt:
                return True
            else:
                return False
        else:
            return False
    
    def tagCmd(self,*args):
        base_type = textScrollList(self.controlList[0],query=True, si=True)
        if len(base_type) != 0:
            base_name = textScrollList(self.controlList[1],query=True, si=True)
            if len(base_name) != 0:
                master = textScrollList(self.controlList[2],query=True, si=True) 
                if len(master) != 0:
                    Atom_Tag(base_type = base_type[0], base_name=base_name[0], master = master[0]) 
                    
    def tslCMD(self,depth):
        if depth == 0:
            if self.validateSelection(depth):
                key = textScrollList(self.controlList[depth], query=True,si=True)[0]
                appendList = self.tagDict[key].keys()
                appendList.sort(key=str.lower)
                textScrollList(self.controlList[depth+1], edit=True, ra=True, append=appendList)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
                textScrollList(self.controlList[depth+3], edit=True, ra=True)
                textScrollList(self.controlList[depth+4], edit=True, ra=True)
            else:
                textScrollList(self.controlList[depth+1], edit=True, ra=True)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
                textScrollList(self.controlList[depth+3], edit=True, ra=True)
                textScrollList(self.controlList[depth+4], edit=True, ra=True)
               
        elif depth == 1:
            if self.validateSelection(depth):
                base_key   = textScrollList(self.controlList[depth-1], query=True,si=True)[0]
                name_key   = textScrollList(self.controlList[depth], query=True,si=True)[0]
                appendList = self.tagDict[base_key][name_key].keys()
                appendList.sort(key=str.lower)
                textScrollList(self.controlList[depth+1], edit=True, ra=True, append=appendList)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
                textScrollList(self.controlList[depth+3], edit=True, ra=True)
                
            else:
                textScrollList(self.controlList[depth+1], edit=True, ra=True)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
                textScrollList(self.controlList[depth+3], edit=True, ra=True)
        
        elif depth == 2:
            if self.validateSelection(depth):
                base_key  = textScrollList(self.controlList[depth-2], query=True,si=True)[0]
                name_key  = textScrollList(self.controlList[depth-1], query=True,si=True)[0]
                mstr_key  = textScrollList(self.controlList[depth], query=True,si=True)[0]
                appendList = self.tagDict[base_key][name_key][mstr_key].keys()
                appendList.sort(key=str.lower)
                textScrollList(self.controlList[depth+1], edit=True, ra=True, append=appendList)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
            else:
                textScrollList(self.controlList[depth+1], edit=True, ra=True)
                textScrollList(self.controlList[depth+2], edit=True, ra=True)
            
        elif depth == 3:
            if self.validateSelection(depth):
                base_key  = textScrollList(self.controlList[depth-3], query=True,si=True)[0]
                name_key  = textScrollList(self.controlList[depth-2], query=True,si=True)[0]
                mstr_key  = textScrollList(self.controlList[depth-1], query=True,si=True)[0]
                tag_key   = textScrollList(self.controlList[depth], query=True,si=True)[0]
                appendList = self.tagDict[base_key][name_key][mstr_key][tag_key]
                appendList.sort(key=str.lower)
                textScrollList(self.controlList[depth+1], edit=True, ra=True, append=appendList)
      
    def buildTagPanelLayout(self,title, depth):
        mainForm = formLayout(numberOfDivisions=100)
        with mainForm:
            titleFrame = frameLayout(l=title,fn='fixedWidthFont', h=21)
            with titleFrame:
                text(l='')
            
            tsl = textScrollList(self.controlList[depth],ams=False)
            
            if depth ==0:
                tslList = self.getTagDictValue(depth)
                tslList.sort(key=str.lower)
                textScrollList(self.controlList[depth], edit=True, append=tslList,sc=Callback(self.tslCMD, depth))
            elif depth == 4:
                textScrollList(self.controlList[depth], edit=True, en=True)
            else:
                textScrollList(self.controlList[depth], edit=True, ams=False, sc=Callback(self.tslCMD, depth))
                
        formLayout(mainForm, edit=True,
                   attachForm    = [(titleFrame, 'top', 5),(titleFrame, 'left', 5),(titleFrame, 'right', 5),
                                    (tsl,'left',3),(tsl,'right',3),(tsl,'bottom',2)],
                   attachControl = [(tsl,'top',2,titleFrame)] 
                   )
        
    def win(self):
        winName = 'atomAttributeTagWin'
        if window(winName, ex=True): deleteUI(winName)
        
        with window(winName, t='Atom Tag Window'):
            mainForm = formLayout(numberOfDivisions=100) 
            with mainForm:
                mainPane = paneLayout(cn='vertical2', aft=0)
                with mainPane:
                    leftPane = paneLayout(cn='vertical3',aft=0)
                    with leftPane:
                        self.buildTagPanelLayout('Base Type',0)
                        self.buildTagPanelLayout('Base Name',1)
                        self.buildTagPanelLayout('Master',2)
                        
                    rghtPane = paneLayout(cn='vertical2',aft=0)
                    with rghtPane:
                        self.buildTagPanelLayout('Tag',3)
                        self.buildTagPanelLayout('Object',4)
                        
                hLayout = horizontalLayout()
                with hLayout:
                    delBtn = button(l='D E L E T E', c=self.deleteAllTags)
                    tagBtn = button(l='T A G', c=self.tagCmd)
                    
            formLayout(mainForm, edit=True,
                       attachForm=[(mainPane, 'left',5),(mainPane,'top',5),(mainPane,'right',5),(mainPane, 'bottom',50),
                                   (hLayout,'left',5),(hLayout,'right',5),(hLayout,'bottom',5)],
                       attachControl=[(hLayout,'top',5,mainPane)]
                       )
            
class Atom_Tag_SingleMaster_Select(object):
    '''
    Class: <Atom_Tag_SingleMaster_Select>: Used when there is only one master, mostly with animation rigs
    
    Methods:
       __init__: initialization
       select  : select tagged objects
    '''
    def __init__(self):
        self.select()
        
    def select(self):
	#try:
	    sel     = ls(sl=True)
	    master  = None
	    selList = []
	    
	    for obj in sel:
		if obj.hasAttr('atom'):
		    base_type  = obj.atom.children()[0]
		    base_name  = base_type.children()[0]
		    attrMaster = base_name.children()[0]
		    attr       = attrMaster.children()[0].split('.')[1]
		    
		    #This will return different depending on if the object is muted or not
		    connections = obj.connections(s=True, d=False, c=True)
	     
		    if len(connections) > 0 :
			#Test the connection for it's node types
			if connections[0][1].type() == 'mute':
			    mute = 'muteObj= ls("%s")[0].%s.connections()[0]'%(obj, attr)
			    exec(mute)
			    #extract the master
			    master =  ls(muteObj)[0].connections()[0]
			    
			else:
			    for con in connections:
				if con[0].split('.')[1] == attr:
				    master = con[1]
			#print master
				
		    if master != None:
			#This will return an array off all the connections
			attrPath  = 'con = ls("%s")[0].atom.%s.%s.%s.%s.connections()' %(master,base_type.split('.')[1], 
			                                                                 base_name.split('.')[1],attrMaster.split('.')[1], attr)
			exec(attrPath)
			if len(con) > 0:
			    for i in con:
				if i.type() == 'mute':
				    selList.append(str(i.connections()[1].name()))
				else:
				    selList.append(str(i.name()))
			
			for i in master.listAttr():
			    if i.find('atomSpecial') > 0:
				idx = i.find('_')
				if i.name()[idx + 1:] == attr:
				    selList.append(str(master.name()))
			
			if master.getShape().type() == 'mesh':
			    selList.append(str(master))
		    else:
			selList.append(str(obj.name()))
			for child in  attrMaster.children():
			    con = child.connections()
			    for i in con:
				if i.type() == 'mute':
				    selList.append(str(i.connections()[1].name()))
				else:
				    selList.append(str(i.name()))                      
	    selList.sort(key=str.lower)
	    select(selList)
	#except:
	#    eStr =  'Invalid object for tag selection.'
	#    OpenMaya.MGlobal.displayError(eStr)

class Atom_Geo_Cache_FrameLayout(object):
    '''
    Class: <Atom_Geo_Cache_FrameLeyout>:
    
    Methods:
       refreshWindowCMD : Refresh the window when the frameLayout is open or closed
       frameLayout      : Build a frameLayout with selection checkbox's for each master
       checkBoxForm     : A form that builds a checkbox for each atom master
       checkBoxCMD      : Selection base command
       checkBoxOnCMD    : Command for on selection
       checkBoxOffCMD   : Command for off selection
    '''
    def __init__(self,parent, name, uiFilter = 'mesh', uiType='export'):
	#parent is a class object
	self.parent           = parent
	self.name             = name
	self.uiType           = uiType 
	self.reference        = None
	self.cachePath        = None
	if nodeType(name) == 'reference':
	    self.reference = FileReference(name)
	
	self.loadState        = self.reference.isLoaded()
	self.uiFilter         = uiFilter
	self.selectionList    = []
	self.checkBoxList     = []
	self.mainFrameLayout  = self.name + '_frameLayout'
	self.mainColumnLayout = self.name + '_columnLayout'

    
    def refreshWindowCMD(self):
	#Get the current width
	curW = window(self.parent.internalName, query=True, width=True)
	#Nudge the window out by one pixel
	window(self.parent.internalName, edit=True, width = curW + 1)
	#Return the window to the original size
	window(self.parent.internalName, edit=True, width = curW)
    
    def frameLayout(self):   
	
	frame = frameLayout(self.mainFrameLayout)
	
	if self.reference != None:
	    frame = frameLayout(frame, edit=True, l=self.reference.namespace, 
	                        fn='boldLabelFont', bv=False, bs='etchedOut', cll=True, ebg=True, bgc=(0.37, 0.42, 0.5),
	                        cc = self.refreshWindowCMD, ec=self.refreshWindowCMD)
	else:
	    frame = frameLayout(self.mainFrameLayout, edit=True, l='None Referenced',fn='boldLabelFont', cll=True, cc = self.refreshWindowCMD, ec=self.refreshWindowCMD)
	with frame:
	    with columnLayout(self.mainColumnLayout, adj=True, rs=5):
		separator()
		if self.uiType == 'export':
		    #for each master build a checkbox for selection
		    for i in self.parent.masterDict[self.name]:
			#use a filter 
			if ls(i)[0].getShape().type() == self.uiFilter:
			    self.checkBoxExportForm(i)
		elif self.uiType == 'import':
			    self.checkBoxImportForm()
		separator()
	 	
    def impCheckCMD(self, *args):
	state = checkBox(self.impCheck, query=True, v=True)
	if state:
	    selList = []
	    refNodes = self.reference.nodes()
	    for node in refNodes:
		if node.type() == 'mesh':
		    selList.append(node.getParent())
	    select(selList)
	else:
	    select(cl=True)
	    
    def checkBoxImportForm(self):
	#print self.name
	impForm = formLayout(self.name + '_cacheImport_formLayout', numberOfDivisions=100, ebg=True, bgc=(0.22, 0.22, 0.22))
	with impForm:
	    impText       = text(self.name  + '_importCache_Text',l='Select Mesh in Reference', al='left')
	    self.impCheck = checkBox(self.name + '_importCache_checkBox',l='',w=17, cc=self.impCheckCMD)
	    
	    ovrVisText       = text(self.name  + '_overRideVis_Text',l='Use Cache Visibility Settings', al='left')
	    self.ovrVisCheck = checkBox(self.name + '_overRideVise_checkBox',l='',v=0,w=17)
	    #Used for loading and unloading the reference
	    if self.loadState:
		self.loadControlCheck = checkBox(self.name + '_refLoadControlCheck', l='Load/Unload Reference', v=True)
	    else:
		self.loadControlCheck = checkBox(self.name + '_refLoadControlCheck', l='Load/Unload Reference', v=False)
	    
	    checkBox(self.loadControlCheck, edit=True, cc=functools.partial(self.loadUnloadRef, self.reference))

	    formLayout(impForm, edit=True,
	               attachForm=[(self.impCheck,'left',5),(self.impCheck, 'top',5),(impText,'top',8),
	                           (self.ovrVisCheck, 'left', 5),(self.loadControlCheck,'top',5)],
	               
	               attachControl = [(impText,'left', 5, self.impCheck),
	                                (self.loadControlCheck,'left',25, impText),(self.ovrVisCheck, 'top',5,impText),
	                                (ovrVisText, 'left',5, self.ovrVisCheck),(ovrVisText,'top',8,impText)]
	               )
	    
    def loadUnloadRef(self, ref, *args):
	
	state = checkBox(self.loadControlCheck, query=True, v=True)
	if state == True: #load a reference
	    FileReference.load(ref)
	else:
	    FileReference.unload(ref)
	self.parent.win() 
	
    def checkBoxExportForm(self,name):
	#cull out the util type as they dont get cached
	typeCheck =  name.atom.getChildren()[0].split('.')[1]
	if typeCheck != 'util':
	    #this is nested within a frameLayout
	    form=formLayout(name + '_formLayout',numberOfDivisions=100)
	    with form:
		#create the checkbox
		check = checkBox(name + '_checkBox',l='',w=17, 
		                 onc = Callback(self.checkBoxCMD),
		                 ofc = Callback(self.checkBoxCMD) )
		self.checkBoxList.append([check,name])
		#text
		txt   = text(name + '_checTxt', l=name)
		#edit the form
		formLayout(form,edit=True,
		           attachForm =[(check,'left',5),(check,'top',5),(txt,'top',5)],
		           attachControl = (txt,'left',0,check)
		           )
    def checkBoxCMD(self):
	select(cl=True)
	self.selectionList = []
	for i in self.checkBoxList:
	    state = checkBox(i[0], query=True, v=True)
	    if state:
		self.getConnectionsTags(i[1])
	
	tmpSel = self.selectionList
	
	tmpLst = []
	for i in tmpSel:
	    tmpLst.append(str(i))
	
	tmpLst.sort(key=str.lower)
	self.selectionList = tmpLst
	select(self.selectionList)
	
    def getConnectionsTags(self,master):
	obj       = ls(master)[0]
	base_type = obj.atom.children()[0]
	base_name = base_type.children()[0]
	master    = base_name.children()[0]
	attr      = master.children()[0]

	con =  master.children()
	self.selectionList.append(master.split('.')[0])
	for child in con:
	    for cCon in child.connections():
		self.selectionList.append(cCon)

class Atom_Geo_Cache_cameraLayout(object):
    '''
    Class: <Atom_Geo_Cache_cameraLayout>:
    
    Methods:
       scanForScale<node> : Scans up a hierarchy checking that scale is 1 starting at the provided node.
       getOptMenuValue    : Return the current value in the camera option menu.
       addCameraMenuItem  : 
       camOptMenu         : Create the text and optionMenu for the camera. This is its own definition so it can be overloaded
                            for export and import.
       cameraFormLayout   : Form that lays out the camera text and optionMenu
    '''
    def __init__(self, internalName):
	self.internalName = internalName
	self.optionMenu   = self.internalName + '_cameraOptionMenu'
	self.formLayout   = self.internalName + '_cameraForm'
	
    def scanForScale(self, obj):
	#when a None object is encountered exit
	while obj != None:
	    if obj.type()=='transform':
		for val in obj.scale.get():
		    if val != 1:
			wStr = '%s has scaling on it, or in its hierarchy.' %(obj)
			OpenMaya.MGlobal.displayWarning(wStr)
			return False
            
	    obj = obj.getParent()
	return True
    
    def getOptMenuValue(self):
	return optionMenu(self.optionMenu, query=True, v=True)
    
    def addCameraMenuItem(self):
	pass
    
    def camOptCMD(self):
	pass
    
class Atom_Geo_Cache_Info(object):
    '''
    class: <Atom_Geo_Cache_Info> : Gets several things in the scene and saves them in a class. This gets pickled later on.
    Methods:
       __init__(ref_nodem<node>, exportPath<string>)
       printStorage: Print what has been stored
       store       : Save scene information into the class
    '''
    def __init__(self, ref_node, exportPath):
        self.ref_node   = str(ref_node)
	self.exportPath = exportPath
	self.namespace  = None
        self.storage    = []
        self.selection  = []
        self.cacheScene = sceneName()
	self.cacheOS    = os.uname()[0]
	self.cacheUser  = os.getenv('USER')
        self.cachePath  = None
        self.store()
	
    def printStorage(self):
        for i in self.storage:
            #node, visibility
            print '==%s:\n\tvisibilty:%s' %(i[0],i[1])
        print ''
        print self.selection
	
    def store(self):
        fileRef = FileReference(self.ref_node)
	self.namespace = fileRef.namespace
	for node in fileRef.nodes():
	    if node.hasAttr('atom'):
		#Use a try incase an invalide node is queried.
		try:
		    if node.getShape().type() == 'mesh':
			rIdx = node.name().rfind(':')
			name = node.name()[rIdx+1:]
			info = [name, node.visibility.get()]
			self.storage.append(info)
		except:
		    pass
		
	selList = ls(sl=True)
	tmplst = []
	#make sure something is selected
	if len(selList) > 0:
	    for node in selList:
		#check that the object has an atom attribute
		if node.hasAttr('atom'):
		    #check if it has a shape node
		    if node.getShape().type() == 'mesh':
			#add the item to the tmplst, which will be sorted next
			tmplst.append(str(node.name()))
			
	    #This is done to insure a proper alphbetical sort
	    tmplst.sort(key=str.lower)
	    for i in tmplst:
		self.selection.append(i)

	    
class Atom_Geo_Cache_Core(Atom_Tag_Core):
    '''
    Class: <Atom_Tag_MultMaster_Select>:Base class for using with geometery cache's. Instanced from Atom_Tag_Core.

    Methods:
    __init__(<string>, <string>,<string>) -- Class initialization.
    newSceneOpenedScriptJob               --
    scrollLayout                          --
    buildLayouts(<sting>)                 --
    win                                   --
    '''
    def __init__(self, internalName, externalName, uiFilter='mesh'):
        super(Atom_Geo_Cache_Core,self).__init__()
	self.internalName = internalName
	self.externalName = externalName
	#reference list
	self.control_list = []
	self.getMasters()
	scriptJob(runOnce = True, e=['SceneOpened' , self.newSceneOpenedScriptJob])
	
    
    def checkSceneToWorkspace(self):
	    
	work    = workspace(q=True, act=True)
	scene   = sceneName() 
	
	if len(scene) > 0:
	    base    = os.path.basename(scene)
	    split   = base.split('_')
	
	    if len(split) >= 5:
		rebuild = '%s_%s_%s' %(split[0], split[1], split[2])
		if not work.rfind(rebuild) > -1:
		    messageStr = 'Scene name not found in workspace, set your project'
		    confirmDialog(title='Information Alert', message = messageStr)
		else:
		    OpenMaya.MGlobal.displayInfo('Project appears to be set, all systems go!')
	    else:
		messageStr = 'Scene name is not following the correct naming convention got: %s\nI hope you know what you`re doing.' % base
		confirmDialog(title='Information Alert', message = messageStr)
	else:
	    messageStr = 'Scene has not been saved, Cache tools may not work as intended.'
	    confirmDialog(title='Information Alert', message = messageStr)

    def newSceneOpenedScriptJob(self):
	if window(self.internalName, ex=True):
	    deleteUI(self.internalName)
    
    def addCameraLayout(self):
	pass
    
    def scrollLayout(self):
	mainScroll = scrollLayout(self.internalName + '_mainScrollLayout',cr=True)
	with mainScroll:
	    mainColumn = columnLayout(self.internalName + '_mainColumnLayout', adj=True, cal='center', cat=('both',5), rs=2)
	    with mainColumn:	
		self.addCameraLayout()
		#sort the keys before building
		tmpKeys = self.masterDict.keys()
		keys    = []
		for k in tmpKeys:
		    keys.append(str(k))
		keys.sort(key= str.lower)
		for k in keys:
		    #Interate through all the references in the scene, create a layout for each instance
		    if len(self.masterDict[k]) > 0:
			#In instances of this class buildLayouts usually gets overloaded
			self.buildLayouts(k)
    
    def buildLayouts(self,name):
	control = Atom_Geo_Cache_FrameLayout(self,name)
	control.frameLayout()
	self.control_list.append(control)      
    
    def win(self, *args):
	if window(self.internalName, ex=True):deleteUI(self.internalName)
        with window(self.internalName,t=self.externalName):
	    self.scrollLayout()
	    width = window(self.internalName, query=True, w=True)
	    window(self.internalName, edit=True, w=width+1)
	    window(self.internalName, edit=True, w=width)
	self.checkSceneToWorkspace()
	
class Atom_Export_Geo_Cache(Atom_Geo_Cache_Core):
    def __init__(self, internalName, externalName):
	super(Atom_Export_Geo_Cache,self).__init__(internalName, externalName)
	self.frameObjectList= [] 
	self.cameraLayOut  = None

    def addCameraLayout(self):
	class Atom_Geo_Cache_exportCameraLayout(Atom_Geo_Cache_cameraLayout):
	    def validateCameras(self):
		self.validCamList= []
		defaultCamList   = ['frontShape', 'perspShape','sideShape','topShape']
		for cam in ls(type='camera'):
		    if not cam in defaultCamList:
			#Detect scaling on cameras here
			if not self.scanForScale(cam):
			    # + '-HAS SCALE'
			    self.validCamList.append([cam.getParent(), '-HAS SCALE'])
						    
			else:
			    self.validCamList.append([cam.getParent(),''])
		
	    def addCameraMenuItem(self):
		menuItem(self.internalName + '_noneCameraMenuItem', l='None', parent =self.internalName + '_cameraOptionMenu')
		for cam in self.validCamList:
		    menuItem(self.internalName + '_cameraMenuItem_'+ cam[0], l=cam[0].name() + cam[1] , parent =self.internalName + '_cameraOptionMenu' )
	    
	    def cameraFormLayout(self):
		cameraForm = formLayout(self.formLayout, numberOfDivisions=100)
		with cameraForm:	   	
		    camText   = text(self.internalName + '_cameraTxt',al='left',w=len('Export Camera: ')*7 +10, l='Export Camera: ', fn='fixedWidthFont' )	
		    camOptMnu = optionMenu(self.optionMenu)  
		    
		    camCheckTxt      = text(self.internalName + '_exportNoneTaggedMeshTxt', al='left',w=164,l='Export Tagged Mesh')
		    self.camCheckBox = checkBox(self.internalName + '_exportNoneTaggedMeshCB', w=20,l='', v=True)
		    
		    self.addCameraMenuItem()
		    formLayout(cameraForm, edit=True,
		               attachForm=[(camText,'left',5),(camText,'top',6),
		                           (camOptMnu, 'top', 5),(camOptMnu,'right',5),
		                           (self.camCheckBox,'left',0)],
		               
		               attachControl=[(camOptMnu, 'left',5,camText),
		                              (self.camCheckBox,'top',5, camText),
		                              (camCheckTxt, 'left',5, self.camCheckBox),(camCheckTxt, 'top',7,camText)])
	    
	camObj = Atom_Geo_Cache_exportCameraLayout(self.internalName)
	camObj.validateCameras()
	if len(camObj.validCamList):
	    camObj.cameraFormLayout()
	    self.cameraLayOut = camObj
	    
	    
    def buildLayouts(self, name):
	self.frameObject = Atom_Geo_Cache_FrameLayout(self,name)
	self.frameObject.frameLayout()
	self.frameObjectList.append(self.frameObject)
	self.exportLayout(name)
	setParent('..')
	setParent('..')
    
    def autoPopulateCMD(self, ctrlList):
	textField( ctrlList[0], edit=True, tx = frameLayout(ctrlList[1], query=True, l=True))
	#self.control_list.append(control)
	
    def exportLayout(self,name):
	exportLayout = formLayout(self.internalName + '_exportFormLayout', parent=self.frameObject.mainColumnLayout)
	with exportLayout:
	    txt    = text(l='Export Cache Name: ', width=117)
	    txtFld = textField(name + '_txt_field', tx='None')
	    self.frameObject.txtFld = txtFld
	    apBut  = button(self.internalName + '_autoPopButton',l='Auto', height=24, c=Callback(self.autoPopulateCMD,[txtFld, self.frameObject.mainFrameLayout]))   
	
	formLayout(exportLayout, edit=True,
	           attachForm    = [(txt, 'left',5),(txt,'top',8), 
	                            (txtFld,'top',5),(txtFld,'right',65),
	                            (apBut, 'top',5),(apBut, 'right',5)],
	           attachControl = [(txtFld, 'left',5,txt),(apBut,'left',5,txtFld)]
	           )

class Atom_Geo_Cache(key_ui.Key_GeoCache):
    '''
    Class: <Atom_Geo_Cache>: Instance of the key_GeoCache win put within a vertical split panel. The extra controls are added to manage the 
			    geo caching.

    Methods:
       parseNameTxt        -- Reads the name textfield and parses it for folder naming.
       getCameraTaggedMesh -- Scan the scene for cameras that have the "camera_export_geo" attribute on them.
       exportCamCMD        -- Export the selected camera and any required tagged geometry.
       makeBaseDirectories -- Create the base file hierarchy for export.
       geoCacheCMD         -- Reselect the proper mesh and do some error checking.
       pickleCache         -- Save a pickled class with various information regarding the geo cache.
       createCache         -- Export the mesh to Geo Cache.
       win                 -- window for the Geo Cache
    '''
    def __init__ (self, intWinName, visWinName, buttonLabel):
	super(Atom_Geo_Cache, self).__init__(intWinName, visWinName, buttonLabel)
	self.atom_reference_object = Atom_Export_Geo_Cache('atomExportGeoCache','Atom Export Geo Cache')
	
	#used in the folder creation
	self.rootName    = ''
	self.vrName      = ''
	self.exportList  = []
	self.rvPath      = None
	
    def parseNameTxt(self):
	name          = text(self.nameTxt, query=True, l=True)
	nameList      = name.split('_')
	self.rootName = ''
	self.vrName   = ''
	versionName   = None
	revisionName  = None
	
	for n in nameList:
	    if n[0] == 'v':
		try:
		    int(n[1])
		    versionName = n
		except:
		    pass
	    
	    elif n[0] == 'r':
		try:
		    int(n[1])
		    revisionName = n
		except:
		    pass
	    else:
		if len(self.rootName) == 0:
		    self.rootName += n
		else:
		    self.rootName += '_' + n
	if versionName != None and revisionName != None:
	    self.vrName = versionName + '_' + revisionName
    
    def getCameraTaggedMesh(self):
	objects = ls(type='transform')
	for obj in objects:
	    if obj.hasAttr('camera_export_geo'):
		self.exportList.append(obj)
    
    def getFileVersion(self, line):
	line_list = line.split(' ')
	if len(line_list) == 3:
	    #Strip off the qoutes and the newline
	    return line_list[2][1:-3]
	else:
	    return None
	
    def exportCamCMD(self):
	self.exportList = []
	#check if the layout has been created
	if self.atom_reference_object.cameraLayOut != None:
	    #Get the selected camera in the optionMenu
	    cam = self.atom_reference_object.cameraLayOut.getOptMenuValue().split('-')[0]
	    if cam != 'None':
		cam_obj = ls(cam)
		if objExists(cam_obj):
		    scenePath = sceneName()
		    exportPath = os.path.join(scenePath[:scenePath.rfind('scenes')+6],'camera')
		    if not os.path.isdir(exportPath):
			os.mkdir(exportPath,0777)
		    
		    #If the checkBox is checked find the geometery to export with the camera
		    if checkBox(self.atom_reference_object.cameraLayOut.camCheckBox, query=True, value=True):
			self.getCameraTaggedMesh()
		    select(cam)
		    
		    if len(self.exportList) >0:
			for i in self.exportList:
			    select(i, tgl=True)
		    
		    #swap the semi-colon with an underscore
		    cam = cam.replace(':', '_')
		    self.rvPath = os.path.join(self.makeBaseDirectories(exportPath), cam + '.ma')

		    #Force the user to delete the current file if it already exists
		    if not os.path.exists(self.rvPath):
			exportSelected(self.rvPath, type='mayaAscii', es=True)
			select(cl=True)
		    else:
			wStr = '%s, already exists, path ignored.' %(self.rvPath)
			OpenMaya.MGlobal.displayWarning(wStr)
			select(cl=True)
		    #make the cam file just output compatable with 2009
		    
		    current_version = str(int(mm.eval("getApplicationVersionAsFloat")))
		    if int(current_version) >= 2011:
			self.makeFile2009()
    
    def makeFile2009(self):
	#if this is 2011, reopen the file and change it to 2009
	_file = open(self.rvPath, 'r')		    
	_file_lines = _file.readlines()
	_file.close()
	final = []
	fileVersion = self.getFileVersion(_file_lines[4])
	for i, l in enumerate(_file_lines):
        #ignore comments
	    if i in [4,8,9]:
		l = l.replace(fileVersion, "2009")
		final.append(l)
	    #ignore a attrs that exist in 2011 but not in 2009
	    elif l.rfind('unw') == -1:
		final.append(l)

	if len(final) != 0:
	    _file = open(self.rvPath,'w')
	    for i in final:
		_file.write(i)
	    _file.close()
	
    def makeBaseDirectories(self,rootPath):
	namepath = None
	rvPath   = None
	if os.path.isdir(rootPath):
	    namePath = os.path.join(rootPath, self.rootName)
	    if not os.path.isdir(namePath):
		os.mkdir(namePath,0777)
		rvPath = os.path.join(namePath,self.vrName)
		if not os.path.isdir(rvPath):
		    os.mkdir(rvPath,0777)
	    else:
		rvPath = os.path.join(namePath,self.vrName)
		if not os.path.isdir(rvPath):
		    os.mkdir(rvPath,0777)
	
	return rvPath
    
    def geoCacheCMD(self, *args):
	self.parseNameTxt()
	self.exportCamCMD()
	
	cPath = self.getPath()
	if os.path.exists(cPath):
	    rvPath = self.makeBaseDirectories(cPath)
	    #interate through each frameLayout
	    checkList = []
	    #Iterate through the frames to make sure there is no duplicate naming.
    
	    for frame in self.atom_reference_object.frameObjectList:
		name = textField(frame.txtFld, query=True, tx=True)
		if name not in checkList:
		    checkList.append(name)
		else:
		    errStr = 'Duplicate Cache names found in "Export Geo Name:"( %s )' %(name)
		    OpenMaya.MGlobal.displayWarning(errStr)
		
	    for frame in self.atom_reference_object.frameObjectList:
		frame.checkBoxCMD()
		if len(ls(sl=True)) > 0:
		    cacheName = textField(frame.txtFld, query=True, tx=True)
		    cachePath = os.path.join(rvPath,cacheName)
		    if not os.path.isdir(cachePath):
			if not cacheName == 'None':
			    os.mkdir(cachePath, 0777)
			    self.createCache(cachePath, frame.reference)
			else:
			    eStr = 'Cache folder can not be named "None"'
			    OpenMaya.MGlobal.displayError(eStr)
		    else:
			eStr = 'Folder %s, exists in export path, cache aborted' %(cacheName)
			OpenMaya.MGlobal.displayError(eStr)
			
		else:
		    OpenMaya.MGlobal.displayWarning('There are NO mesh selected to geo cache.')
		
	else:
	    eStr= '%s\nDoes not exists path is wrong, cache aborted.' %(cPath)
	    OpenMaya.MGlobal.displayError(eStr)
	    
    def pickleCache(self, cachePath):
	cache           = Atom_Geo_Cache_Info(self.atom_reference_object.frameObject.reference, cachePath)
	cache.cachePath = cachePath
	#acp is atom cache pickle
	f = open(os.path.join(cachePath,'cache_info.acp'), 'wb')
	pickle.dump(cache, f)
	f.close()
    
    def createCache(self, path, ref):
	#get the global slider
	gPlayBackSlider = mel.eval('$tmpVar = $gPlayBackSlider')
	minRange  = playbackOptions(query = True, minTime = True) - 1
	maxRange  = playbackOptions(query = True, maxTime = True) + 1 
	useAudio =  checkBox(self.checkBox,query=True, v=True)
	if useAudio:
	    soundNode = cmds.timeControl(gPlayBackSlider, query = True, sound = True)
	    if len(soundNode) > 0:
		minRange = str(int(cmds.sound(soundNode, query=True, o=True))-1)
		maxRange = str(cmds.sound(soundNode, query=True, length=True) + 1).split('.')[0]
	    else:
		OpenMaya.MGlobal.displayWarning('Use Audio Length is selected, but there is no audio in the timeline. Using Animation slider range.')
	mel.eval('doCreateGeometryCache 4 { "0", "'+ str(minRange) +'", "' + str(maxRange) + '", "OneFilePerFrame", "0", "' + path + '","0","'+ ref.namespace +'","0", "export", "1", "1", "1","0","1"}')
	 
	xmlPath = os.path.join(path, os.path.basename(path) +'.xml')
	if os.path.exists(xmlPath):
	    nodeList = []
	    #for node in self.atom_reference_object.frameObject.reference.nodes():
	    for node in ref.nodes():
		if node.hasAttr('atom'):
		    try:
			node.atom.util.children()
		    except:
			try:
			    if node.getShape().type() == 'mesh':
				nodeList.append(node)
			except:
			    pass
			
	    cacheXml = MayaXmlCacheInfo(xmlPath,nodeList)
	    cacheXml.removeTextNodes(cacheXml.xml.documentElement.childNodes)
	    cacheXml.addSelectedToXml()
	    
    def win(self, *args):
	if  window(self.intWinName,   exists = True):
            deleteUI(self.intWinName, window = True)
	#Check that project setting and scene setting are the same if they are not
        window( self.intWinName, menuBar = True, title = self.visWinName, width = 600, height =700)
	self.buildMenuBar()
	
	paneLayout(self.intWinName + 'main_Panel_Layout', configuration='vertical2')
	paneLayout(self.intWinName + 'name_Panel_Layout', configuration="horizontal2", h=100, ps=[1,100,25])
	self.buildNameContents()	
	self.addControls()
	self.parseSceneNameAndPopulate()
	self.buildName()
	setParent('..')
	setParent('..')
	self.atom_reference_object.scrollLayout()
	
        showWindow(self.intWinName)

class Atom_Geo_Cache_Browser(key_ui_core.DirDialog_v01):
    '''
    Class: <Atom_Geo_Cache_Browser>: Directory browser to change the geo cache export path
    Methods:
       bCMD        -- Button command
       buildButton -- Create the button
    '''
    def __init__(self,intWinName, visWinName, buttonLabel, path,parent):
	super(Atom_Geo_Cache_Browser,self).__init__(intWinName, visWinName, buttonLabel, path)
	self.parent = parent
	
    def bCMD(self, *args):
	textField(self.parent.dataFld, edit=True, tx=self.path)
	self.parent.delOptMenuItms(self.parent.baseName)
	self.parent.delOptMenuItms(self.parent.vrOptMnu)
	self.parent.delOptMenuItms(self.parent.cacheOptMnu)
	self.parent.basepath = self.path
	
	if self.parent.cachePath != None:
	    self.parent.autoPopulateOptionMenus()
	else:
	    self.parent.populateOptionMenus()
	
	deleteUI(self.intWinName)
	
    def buildButton(self):
	cmds.button(self.button ,label = self.buttonLabel, c = self.bCMD)

class Atom_Import_Geo_Cache_FormLayout(object):
    '''
    Class: <Atom_Geo_Cache>: Instance of the key_GeoCache win put within a vertical split panel. The extra controls are added to manage the 
			    geo caching.

    Methods:
       populateDict        -- Find all the directories in the provided path and put them into a dictionary.
       printCacheTree      -- Print the contents of the current cacheDict.
       browseCMD           -- Set base path do cache to.
       populateOptionMenus -- Populate a dictionary with keys from the top hierarchy.
       clearOptMenu        -- Clear the provided optionMenu of its menuItems except for items that have 'None' as a label.
       baseOptMenuCMD      -- Change Command used by the Base Option Menu.
       vrOptMenuCMD        -- Change Command used by the the Version Revision Option Menu.
       getACP              -- Get the Atom Cache Pickle file thats in the target folder.
       cacheOptMnuCMD      -- Change Command used by the Cache Option Menu.
       optMenuClearCache   -- Delete all the cache nodes.
       deleteCache         -- Delete any cacheFiles found on the provided object.
       importCache         -- Import cache from the provided path.
       setInfoText         -- Read the acp for information then display for user feedback.
       resetInfoTxt        -- Set the info text back to its original value.
       refreshWindowCMD    -- Change the window width + 1 then back to original value. This forces a UI redraw.
       buildInfoFrame      -- Create the frameLayout that has the acp feedback.
       formLayout          -- Main layout for the controls.
    '''
    def __init__(self, internalName, control):
	self.internalName = internalName
	self.control      = control
	self.cacheDict    = {}
	self.cachePath    = None
	self.basepath     = None
	path              = os.path.join(workspace(q=True,rd=True),'data/geo_cache')
	self.remapLibPath = None
	self.remapList    = []
	self.pathExists   = False
	self.xmlObj       = None
	#print 'control ___ ', self.control.reference
	if self.control.reference != None:
	    #print '___ ', self.control.reference.refNode
	    for node in self.control.reference.nodes():
		#print node
		for con in node.history():
		    if con.type() == 'cacheFile':
			if con.cachePath.get().rfind('3D') > -1:
			    self.cachePath = con.cachePath.get()
			    break	
		if self.cachePath != None:
		    break
		
	if os.path.isdir(path):
	    self.basepath = path
	    self.pathExists = True
	    
	else:
	    eStr = 'Cache path does not exist: %s' %(path)
	    OpenMaya.MGlobal.displayError(eStr)
	    
	self.dataFld      = self.internalName + '_vr_cachePath' 
	self.baseName     = self.internalName + '_baseNameOptionMenu'
	self.vrOptMnu     = self.internalName + '_versionOptionMenu'
	self.cacheOptMnu  = self.internalName + '_revisionOptionMenu'
	
	self.cacheFromTxt = self.internalName + '_cacheFromTxt'
	self.cacheUserTxt = self.internalName + '_cacheUserTxt'
	self.cacheDateTxt = self.internalName + '_cacheDateTxt'
	
	self.cacheOsTxtcacheMayaVrsTxt   = self.internalName + '_cacheOsTxt'
	self.remapOptMnu  = self.internalName + '_cacheRemapOptionMenu'
	self.cacheRngChk  = self.internalName + '_useCacheRangeCheckbox'
	self.acp          = None
    
    def enterCMD(self, *args):
	path = textField(self.dataFld, query=True, tx=True)
	if os.path.isdir(path):
	    self.basepath = path
	    #print 'new path ___ ', self.basepath
	else:
	    #print 'old path ___ ', self.basepath
	    OpenMaya.MGlobal.displayWarning('No such directory.')
	#self.basepath =	textField(self.dataFld, query=True, tx=True)
	self.delOptMenuItms(self.baseName)
	self.delOptMenuItms(self.vrOptMnu)
	self.delOptMenuItms(self.cacheOptMnu)

	if self.cachePath != None:
	    self.autoPopulateOptionMenus()
	else:
	    self.populateOptionMenus()
	     
    def populateDict(self):
	self.cacheDict = {}
	for root, dirs, files in os.walk(self.basepath):
	    r= root.split('geo_cache')[1][1:]
	    if len(r) > 0:
		keys  = r.split('/')
		kStr  = 'self.cacheDict'
		for k in keys:
		    kStr += '["' + k + '"]'
		kStr+='={}'
		exec(kStr)
    
    def printCacheDict(self):
	base = self.cacheDict.keys()
	base.sort(key=str.lower)
	for k in base:
	    print k
	    subDir = self.cacheDict[k].keys()
	    subDir.sort(key=str.lower)
	    for j in subDir:
		print '\t++', j
		lastDir =self.cacheDict[k][j].keys()
		lastDir.sort(key=str.lower)
		for l in lastDir:
		    print '\t\t--', l
	    print '================\n'
	    
    def browseCMD(self):
	
	path = workspace(q=True,rd=True)
	bWin = Atom_Geo_Cache_Browser(self.internalName + '_vr_BrowseWindow', 'BROWSE DATA FOLDER', 'S E T',os.path.join(path, 'data', 'geo_cache'), self )
	bWin.win()
    
    def autoPopulateOptionMenus(self):
	try:
	    self.populateDict()
	    base = self.cacheDict.keys()
	    base.sort(key=str.lower)

	    menuItem(self.internalName + '_menuItem_bnNone', l= 'None', parent = self.baseName)
	    menuItem(self.internalName + '_menuItem_vrNone', l= 'None', parent = self.vrOptMnu)
	    menuItem(self.internalName + '_menuItem_chNone', l= 'None', parent = self.cacheOptMnu)

	    cacheSplit = self.cachePath.split('/')
	    idx = self.cachePath.rfind('geo_cache')

	    #BUG fix, if object has geo cache but the cache path is changed this will error out and break
	    baseSplt       = cacheSplit[len(cacheSplit)-4]
	    vrSplt         = cacheSplit[len(cacheSplit)-3]
	    cacheSplt      = cacheSplit[len(cacheSplit)-2]

	    #base optionMenu
	    for i in base:
		menuItem(self.internalName + '_menuItem_' + i, l= i, parent = self.baseName)
		subDir = self.cacheDict[i].keys()
	    
	    #this can raise exception so auto basepath declare happens in the next line
	    optionMenu(self.baseName, edit=True, v=baseSplt)

	    #auto basepath
	    self.basepath = self.cachePath[:idx+9]

	    #version revision optionMenu
	    vrkeys = self.cacheDict[baseSplt].keys()
	    vrkeys.sort(key=str.lower)
	    for i in vrkeys:
		menuItem(self.internalName + '_menuItem_' + baseSplt + '_'+ i, l = i, parent=self.vrOptMnu)
	    optionMenu(self.vrOptMnu, edit=True, v=vrSplt) 

	    #cache optionMenu
	    cacheKeys = self.cacheDict[baseSplt][vrSplt].keys()
	    cacheKeys.sort(key=str.lower)
	    for i in cacheKeys:
		menuItem(self.internalName + '_menuItem_' + baseSplt + '_'+ vrSplt + '_' + i, l = i, parent=self.cacheOptMnu)
	    optionMenu(self.cacheOptMnu, edit=True, v=cacheSplt)   

	    cPath     = os.path.join(self.basepath, baseSplt,vrSplt,cacheSplt)

	    #reading the xml
	    self.getACP(cPath)
	    xmlPath     = self.getCacheXml(cPath)
	    self.xmlObj = MayaXmlCacheInfo(xmlPath)
	    self.setInfoText()
	except:
	    #print 'exception'
	    pass
	
    def populateOptionMenus(self):
	self.populateDict()
	#print self.populateDict
	base = self.cacheDict.keys()
	#print 'base keys ___', base
	base.sort(key=str.lower)
	

	menuItem(self.internalName + '_menuItem_bnNone', l= 'None', parent = self.baseName)
	menuItem(self.internalName + '_menuItem_vrNone', l= 'None', parent = self.vrOptMnu)
	menuItem(self.internalName + '_menuItem_chNone', l= 'None', parent = self.cacheOptMnu)

	for i in base:
	    menuItem(self.internalName + '_menuItem_' + i, l= i, parent = self.baseName)
	    subDir = self.cacheDict[i].keys()
    
    def delOptMenuItms(self, optMenu):
	mLst = optionMenu(optMenu, query=True,ils=True)
	for i in range(0,len(mLst),1):
	    deleteUI(mLst[i])
	    
    def clearOptMenu(self, optMenu):
	mLst = optionMenu(optMenu, query=True,ils=True)
	for i in range(0,len(mLst),1):
	    if not menuItem(mLst[i], query=True,l=True) == 'None':
		deleteUI(mLst[i])
		
    def baseOptMenuCMD(self, *args):
	value = optionMenu(self.baseName, query=True, v=True)
	if value != 'None':
	    #delete the cache
	    self.optMenuClearCache()
	    #get the version revision keys
	    vrkeys = self.cacheDict[value].keys()
	    vrkeys.sort(key=str.lower)
	    #clear the other option menus
	    self.clearOptMenu(self.vrOptMnu)
	    self.clearOptMenu(self.cacheOptMnu)
	    #re-populate
	    for i in vrkeys:
		menuItem(self.internalName + '_menuItem_' + value + '_'+ i, l = i, parent=self.vrOptMnu)

	else:
	    #Clear the menus and delete the cache
	    self.clearOptMenu(self.vrOptMnu)
	    self.clearOptMenu(self.cacheOptMnu)
	    self.optMenuClearCache()
	    
	#Reset the selection to the first index in the optionMenus
	optionMenu(self.vrOptMnu,    edit=True, sl=1)
	optionMenu(self.cacheOptMnu, edit=True, sl=1)	    

    def vrOptMenuCMD(self, *args):
	baseKey = optionMenu(self.baseName, query=True, v=True)
	#print baseKey
	vrKey   = optionMenu(self.vrOptMnu, query=True, v=True)
	if baseKey != 'None' and vrKey != 'None':
	    cacheKeys = self.cacheDict[baseKey][vrKey].keys()
	    cacheKeys.sort(key=str.lower)
	    self.clearOptMenu(self.cacheOptMnu)
	    for i in cacheKeys:
		menuItem(self.internalName + '_menuItem_' + baseKey + '_'+ vrKey + '_' + i, l = i, parent=self.cacheOptMnu)
	else:
	    self.optMenuClearCache()
	    self.clearOptMenu(self.cacheOptMnu)
	    
	optionMenu(self.cacheOptMnu, edit=True, sl=1)
    
    def getACP(self, path):
	pPath = os.path.join(path, 'cache_info.acp')
	if os.path.exists(pPath):
	    f        = open(pPath, 'rb')
	    self.acp = pickle.load(f)
	    f.close()
    
    def getCacheXml(self,path):
	#print 'get ___ ', path
	xml = None
	for i in os.listdir(path):
	    if i[0] != '.':
		idx = i.rfind('.')
		if i[idx + 1:] == 'xml':
		    return os.path.join(path, i)	
   
    def cacheOptMnuCMD(self, *args):
	base      = optionMenu(self.baseName,    query=True, v=True)
	vr        = optionMenu(self.vrOptMnu,    query=True, v=True)
	cache     = optionMenu(self.cacheOptMnu, query=True, v=True)
	#build that path to the cache files
	#print self.basepath
	cPath     = os.path.join(self.basepath, base,vr,cache)
	#print 'build ___ ', cPath
	if cache != 'None':
	    if os.path.isdir(cPath):
		xmlPath     = self.getCacheXml(cPath)
		self.xmlObj = MayaXmlCacheInfo(xmlPath)
		setVis = None
		
		if len(self.xmlObj.setVis) > 0:
		    setVis = self.xmlObj.setVis
		
		if setVis != None:
		    select(cl=True)
		    #Set the visibility base on the acp
		    if checkBox(self.control.ovrVisCheck, query=True, v=True):			
			for i in setVis:
			    objStr = self.control.reference.namespace + ':' + i[0]
			    if objExists(objStr):
				obj = ls(objStr)[0]
				if i[1] == 'True':
				    obj.visibility.set(1)
				elif i[1] == 'False':
				    obj.visibility.set(0)
			
		selList = [] 
		cnt = 0

		for i in self.xmlObj.selection_list:
		    objStr = self.control.reference.namespace + ':' + i[i.rfind(':')+1:]

		    if objExists(objStr):
			selList.append(objStr)
			self.deleteCache(ls(objStr)[0])
		    #check the index for a remap
		    else:
			remapLen = len(self.remapList) 
			if  remapLen > 0:
			    if remapLen == len(self.remapList):
				objStr = self.control.reference.namespace + ':'+self.remapList[cnt].strip('\n')
				if objExists(objStr):
				    selList.append(objStr)
				    self.deleteCache(ls(objStr)[0])
				else:
				    eStr = '%s, was targeted for remap, and not found in scene' %(objStr)
				    OpenMaya.MGlobal.displayError(eStr)
			    else:
				eStr = 'Remap list length is not the same length as geoCache listed...'
				OpenMaya.MGlobal.displayError(eStr)
			else:
			    wStr = '%s, not found, skipping' %(objStr)
			    OpenMaya.MGlobal.displayWarning(wStr)
		    cnt += 1

		if len(selList) > 0:
		    select(cl=True)
		    for i in selList:
			#Note:
			#When a geoCache is created the maya creates a new shape node with "Deformed" appended to it.
			#When the cache is deleted, maya does not restore the network to it's original state, so the shapeNode is still named deformed
			#Trying to re-cache once this has happened breaks the import as the expected names have changed from the
			#export.To avoid this, the transform node is always selected instead of the shape. The shape node is whats exported in the
			#original geoCache export file.
			node = ls(i)[0] 
			if node.type() == 'mesh':
			    select(node.getParent(),tgl=True)
			else:
			    select(i,tgl=True)
		    self.importCache(xmlPath)
		else:
		    eStr = 'No name matches found, cache aborted'
		    OpenMaya.MGlobal.displayError(eStr)
	    else:
		print 'No such path: ', cPath
	else:
	    self.optMenuClearCache()
	self.refreshWindowCMD()
    
    def importCache(self,path):
	#print path
	if os.path.exists(path):
	    if checkBox(self.cacheRngChk, query=True, v=True):
		idx   = self.xmlObj.timeRange.rfind('-')
		start = float(int(self.xmlObj.timeRange[:idx]) + int(self.xmlObj.timePerFrame)) / float(self.xmlObj.timePerFrame)
		end   = float(int(self.xmlObj.timeRange[idx+1:]) -  int(self.xmlObj.timePerFrame)) / float(self.xmlObj.timePerFrame)
		
		setAttr('defaultRenderGlobals.startFrame', int(start))
		setAttr('defaultRenderGlobals.endFrame',   int(end))
		playbackOptions(min=start, max=end, ast=start, aet=end)			
	    mel.eval("source doImportCacheArgList.mel;")
	    mel.eval('importCacheFile "' + path + '" "Best Guess";')
	    self.setInfoText()
	else:
	    eStr = 'File not found: %s' %(path)
	    OpenMaya.MGlobal.displayError(eStr)
	    	 
    def optMenuClearCache(self):
	self.resetInfoTxt()
	for node in self.control.reference.nodes():
	    if node.type() == 'transform':
		if node.getShape() != None:
		    self.deleteCache(node)
		    #Try to restore hierarchy to it's original state 
		    #check if the transform has multiple nodes under it
		    children = node.getChildren()
		    if len(children) > 1:
			isRefNode    = []
			isNonRefNode = [] 
			#Sort the nodes into referenced and non-referenced nodes
			for child in children:
			    if child.type() == 'mesh':
				if child.isReferenced() == True:
				    isRefNode.append(child)
				else:
				    isNonRefNode.append(child)
			#If there is only one ref node and one scene node, cleanup is viable
			if len(isRefNode) == 1 and len(isNonRefNode) ==1:
			    #make sure both nodes are of type 'mesh'
			    delete(isNonRefNode)
			    isRefNode[0].intermediateObject.set(0)
				
			elif len(isRefNode)>1:
			    wStr = '"%s", has more than one shape node in the reference...This could lead to issues.Cache Restore aborted...' %(node)
			    OpenMaya.MGlobal.displayWarning(wStr)
		    
    def deleteCache(self, obj):
	hasCache=False
	for i in obj.listHistory(lv=2):
	    if i.type() == 'cacheFile':
		hasCache=True
		break
	    
	if hasCache:
	    select(obj)
	    mel.eval('deleteCacheFile 3 { "keep", "", "geometry" };')
	    select(cl=True)

  
    def setInfoText(self):
	'''
	self.cacheType       = None
        self.cacheFormat     = None 
        self.timeRange       = None
        self.timePerFrame    = None
        self.cacheVersion    = None
        self.cachePath       = None
        self.version         = None
        self.author          = None
	'''
	text(self.cacheFromTxt, edit=True, l = 'Exported From : ' + self.xmlObj.cachePath.strip('\n\t'))
	text(self.cacheUserTxt, edit=True, l = 'Exported By   : ' + self.xmlObj.author.strip('\n\t'))
	text(self.cacheDateTxt, edit=True, l = 'Last Modified : ' + time.ctime(os.path.getmtime(self.xmlObj.path)))
	text(self.cacheOsTxtcacheMayaVrsTxt,   edit=True, l = 'Maya Version  : ' + self.xmlObj.version.strip('\n\t') )
    
    def resetInfoTxt(self):
	text(self.cacheFromTxt, edit=True, l = 'Exported From : N/A')
	text(self.cacheUserTxt, edit=True, l = 'Exported By   : N/A')
	text(self.cacheDateTxt, edit=True, l = 'Last Modified : N/A')
	text(self.cacheOsTxtcacheMayaVrsTxt,   edit=True, l = 'Exported OS   : N/A')
    
    def refreshWindowCMD(self):
	#Get the current width
	curW = window(self.control.parent.internalName, query=True, width=True)
	#Nudge the window out by one pixel
	window(self.control.parent.internalName, edit=True, width = curW + 1)
	#Return the window to the original size
	window(self.control.parent.internalName, edit=True, width = curW)
    
    def buildInfoFrame(self):
	infoFrameLayout = frameLayout(self.internalName + '_infoFrameLayout',l='Cache Information', cll=True, cl=True,ebg=True, bgc=(0.45, 0.47, 0.5),
	                              cc = self.refreshWindowCMD, ec=self.refreshWindowCMD)
	infoForm        = None
	with infoFrameLayout:
	    infoForm = formLayout(self.internalName + '_infoFormLayout', ebg=True, bgc=(0.22, 0.22, 0.22))
	    with infoForm:
		sep        = separator()
		expFrmTxt  = text(self.cacheFromTxt, fn = 'fixedWidthFont', l = 'Exported From : N/A', al = 'left')
		expByTxt   = text(self.cacheUserTxt, fn = 'fixedWidthFont', l = 'Exported By   : N/A', al = 'left')
		expDateTxt = text(self.cacheDateTxt, fn = 'fixedWidthFont', l = 'Last Modified : N/A', al = 'left') 
		expOsTxt   = text(self.cacheOsTxtcacheMayaVrsTxt,   fn = 'fixedWidthFont', l = 'Maya Version  : N/A', al = 'left')
	
		formLayout(infoForm,edit=True,
		           attachForm = [(sep,'left',0),(sep,'top',5),(sep, 'right',0),
		                         (expFrmTxt,'left',5),(expFrmTxt,'right',5),
		                         (expByTxt,'left',5),(expByTxt,'right',5),
		                         (expDateTxt,'left',5),(expDateTxt,'right',5),
		                         (expOsTxt,'left',5),(expOsTxt,'right',5)],
		           attachControl = [(expFrmTxt,'top',5,sep),
		                            (expByTxt,'top',5,expFrmTxt),
		                            (expDateTxt,'top',5, expByTxt),
		                            (expOsTxt,'top',5, expDateTxt)]
		           )
	return infoFrameLayout
    
    def populateRemapOptionMenu(self):
	menuItem(self.internalName + '_none_remap_menuItem', l='None', parent=self.remapOptMnu)
	pPath = os.getenv('KEY_PROJECT_PATH') 
	if pPath != None:
	    project = os.path.basename(pPath)
	    libPath = os.path.join('/Volumes/VFX/Projects', project, 
	                           'Assets/Published_Production_Assets/Department_Libraries/Lighting_Library/Cache_Remap')
	    if os.path.exists(libPath):
		self.remapLibPath = libPath
		files = os.listdir(libPath)
		for f in files:
		    if f[0] != '.':
			fName = f.split('.')[0]
			menuItem(self.internalName + '_' +fName + '_remap_menuItem', l=fName, parent=self.remapOptMnu)
	    else:
		wStr = 'Remap folder not found, population aborted...'
		OpenMaya.MGlobal.displayWarning(wStr)

    def remapCMD(self, *args):
	self.remapList = []
	optItem = optionMenu(self.remapOptMnu, query=True, v=True)
	if optItem != 'None':
	    remapTxt = os.path.join(self.remapLibPath, optItem + '.txt')
	    if os.path.exists(remapTxt):
		remapFile = open(remapTxt,'r')
		lines = remapFile.readlines()
		remapFile.close()
		#special case when readlines fails as it doesn't split '\r'
		if len(lines) == 1:
		    tmpLines = lines[0].split('\r')
		    if len(tmpLines)>1:
			lines = tmpLines
			
		for i in lines:
		    self.remapList.append(i.strip('\n'))

	    else:
		wStr = ('%s, not found, point to a different file') %(optItem)
		OpenMaya.MGlobal.displayWarning(wStr)

    def formLayout(self):
	if self.pathExists:
	    form = formLayout(self.internalName + '_vr_FormLayout', parent=self.control.mainColumnLayout)
	    with form:
		bTxt      = text(l='Data Path: ', width=63, align='left')
		bDataFld  = None
		
		if self.cachePath == None:
		    bDataFld  = textField(self.dataFld, tx= self.basepath, cc=self.enterCMD)
		else:
		    idx = self.cachePath.rfind('geo_cache')
		    self.basepath = self.cachePath[:idx+9]
		    bDataFld  = textField(self.dataFld, tx= self.basepath, cc=self.enterCMD)

		bBtn      = iconTextButton(style = 'iconOnly', image = 'fileOpen.xpm', width = 23, height = 23, c=self.browseCMD)
		
		cRngTxt     = text(l='Set timeslider range to cache range', align = 'left')
		cRngChk     = checkBox(self.cacheRngChk,w=17, l='',v=1 )
		
		reMapTxt    = text(l='Remap:', w=53, align = 'left')
		remapOptMnu = optionMenu(self.remapOptMnu, cc=self.remapCMD)
		self.populateRemapOptionMenu()
		
		cacheTxt    = text(l='Cache: ', width = 44)	    
		cacheOptMnu = optionMenu(self.cacheOptMnu, cc= self.cacheOptMnuCMD)
		
		vrTxt     = text(l='Version Revision : ', width=101)
		vrOptMnu  = optionMenu(self.vrOptMnu, cc= self.vrOptMenuCMD)
    
		baseName  = text(l='Base Name : ', width=74, align='left') 
		bnOptMnu  = optionMenu(self.baseName, cc =self.baseOptMenuCMD)
		
		infoFrame  = self.buildInfoFrame()	    
		
		if self.cachePath != None:
		    self.autoPopulateOptionMenus()
		else:
		    self.populateOptionMenus()
		setFocus(bDataFld)
    
	    formLayout(form, edit=True,
		       attachForm    = [(bTxt, 'left',5), (bTxt, 'top',8),
		                        (bDataFld, 'right',33),(bDataFld, 'top',5),
		                        (bBtn, 'top',5),
	                                (cRngChk, 'left', 5),
		                        (reMapTxt, 'left',5),
		                        (baseName, 'left',5),
		                        (infoFrame,'left',5),(infoFrame,'right',5)],
		       
		       attachControl = [(bDataFld, 'left',16, bTxt), (bBtn, 'left',5,bDataFld),
	                                (cRngChk,'top',5,bDataFld),
	                                (cRngTxt, 'left',5,cRngChk),(cRngTxt, 'top', 8, bDataFld),
		                        (reMapTxt, 'top',10, cRngChk),
	                                (remapOptMnu,'left',26,reMapTxt),(remapOptMnu,'top',10,cRngChk),
		                        (baseName, 'top',10, reMapTxt),
		                        (bnOptMnu, 'top',5,reMapTxt),(bnOptMnu,'left',5,baseName),
		                        (vrTxt,'left',5,bnOptMnu),(vrTxt, 'top',6, reMapTxt),
		                        (vrOptMnu, 'left',5,vrTxt),(vrOptMnu, 'top',5,reMapTxt),
		                        (cacheTxt,'left', 5, vrOptMnu),(cacheTxt,'top',6,reMapTxt),
		                        (cacheOptMnu,'left',5,cacheTxt),(cacheOptMnu, 'top',5,reMapTxt),
		                        (infoFrame, 'top', 5,cacheOptMnu)
		                        ]
		       )
		
class Atom_Import_Geo_Cache(Atom_Geo_Cache_Core):
    '''
    Class: <Atom_Import_Geo_Cache>: Instance of the key_GeoCache win put within a vertical split panel. The extra controls are added to manage the 
			    geo caching.

    Methods:
      addCameraLayout -- Add the camera import layout
      buildLayouts    -- Build the layouts
      
    '''
    def __init__(self, internalName, externalName, uiType):
	super(Atom_Import_Geo_Cache,self).__init__(internalName, externalName, uiType)
	self.uiType = uiType
	self.exportField = self.internalName + '_textField'
	self.control = None

    def addCameraLayout(self):
	
	class Atom_Geo_Cache_ImportCameraLayout(Atom_Geo_Cache_cameraLayout):
	    def __init__(self, internalName, parent):
		super(Atom_Geo_Cache_ImportCameraLayout,self).__init__(internalName)
		self.internalName      = internalName
		self.refNode           = None
		self.baseNameCamOptMnu = self.internalName + '_baseNameCamOptMnu'
		self.verRevCamOptMnu   = self.internalName + '_vrCamOptMnu'
		self.refCamOptMnu      = self.internalName + '_refCamOptMnu'
	    
	    def clearOptMenu(self, optMenu):
		mLst = optionMenu(optMenu, query=True,ils=True)
		for i in range(0,len(mLst),1):
		    if not menuItem(mLst[i], query=True,l=True) == 'None':
			deleteUI(mLst[i])
		
		optionMenu(optMenu, edit=True, sl=1)
		if self.refNode != None:
		    self.refNode.remove()
		    self.refNode = None
		    
	    def addBaseMenuItem(self):
		menuItem(self.internalName + '_none_campImp_baseNameMnuItm', l='None',parent=self.baseNameCamOptMnu)
		menuItem(self.internalName + '_none_camImp_vrMnuItm',        l='None',parent=self.verRevCamOptMnu)
		menuItem(self.internalName + '_none_camImp_refCamMnuItm',    l='None',parent=self.refCamOptMnu)
		
		#base folder
		path = text(self.pathTxt, query=True, l=True).split('Camera Path: ')[1]
		if os.path.isdir(path):
		    for i in os.listdir(path):
			tmpPath = os.path.join(path, i)
			if os.path.isdir(tmpPath):
			    menuItem(self.internalName + '_camImportMenuItem_' +i, l=i,parent=self.baseNameCamOptMnu )
			    
	    def baseOptCMD(self, *args):
		camPath = text(self.pathTxt, query=True, l=True).split('Camera Path: ')[1]
		selVal  = optionMenu(self.baseNameCamOptMnu, query=True, v=True)
		dirPath = os.path.join(camPath, selVal)
		if os.path.exists(dirPath):
		    self.clearOptMenu(self.verRevCamOptMnu)
		    self.clearOptMenu(self.refCamOptMnu)
		    for i in os.listdir(dirPath):
			vrPath = os.path.join(dirPath,i)
			if os.path.isdir(vrPath):
			    menuItem(self.internalName + '_menuItem_' +i, l=i, parent=self.verRevCamOptMnu)
		else:
		    self.clearOptMenu(self.verRevCamOptMnu)
		    self.clearOptMenu(self.refCamOptMnu)
	    
	    def verRevOptCMD(self, *args):
		camPath = text(self.pathTxt, query=True, l=True).split('Camera Path: ')[1]
		base    = optionMenu(self.baseNameCamOptMnu, query=True, v=True)
		vr      = optionMenu(self.verRevCamOptMnu,   query=True, v=True)
		path = os.path.join(camPath,base,vr)
		if os.path.exists(path):
		    for i in os.listdir(path):
			if i[0] != '.':
			    menuItem(self.internalName + '_menuItem_' +i.replace('.','_'), l=i, parent=self.refCamOptMnu)
			#Old as of dec 14th/2010, need to support ma and mb
			#iSplit = i.split('.')
			#if  iSplit[1] == 'ma' or iSplit[1] == 'mb':
			    #menuItem(self.internalName + '_menuItem_' +iSplit[0], l=iSplit[0], parent=self.refCamOptMnu)
		else:
		    self.clearOptMenu(self.refCamOptMnu)
		    
	    def camOptCMD(self,*args):
		camPath = text(self.pathTxt, query=True, l=True).split('Camera Path: ')[1]
		base    = optionMenu(self.baseNameCamOptMnu, query=True, v=True)
		vr      = optionMenu(self.verRevCamOptMnu,   query=True, v=True)
		cam     = optionMenu(self.refCamOptMnu,   query=True, v=True)
		path    = os.path.join(camPath,base,vr,cam) #+ .ma #removed to support both ma and mb, the name is in the control
		if os.path.exists(path):
		    if self.refNode != None:
			self.refNode.remove()
			
		    createReference(path, defaultNamespace=True)
		    self.refNode = FileReference(path)
		    msgStr = 'Reference Created: %s' %(path)
		    OpenMaya.MGlobal.displayInfo(msgStr)
		else:
		    if self.refNode != None:
			self.refNode.remove()
			self.refNode = None
	    
	    def cameraFormLayout(self):
		form = formLayout(self.formLayout, numberOfDivisions=100, ebg=True, bgc=(0.72, 0.4, 0.4))
		with form:
		    cameraPath  = os.path.join(Workspace().getName(), 'scenes/camera')
		    if not os.path.exists(cameraPath):
			cameraPath = 'Not Found'

		    self.pathTxt = text(self.internalName + 'camPathTxt', al='left', l= 'Camera Path: ' + cameraPath,fn='fixedWidthFont')
		   
		    baseTxt      = text(self.internalName + '_baseCamTxt',    al='left',w=70, l='Base Name: ')
		    baseOptMnu   = optionMenu(self.baseNameCamOptMnu, width=100, cc=self.baseOptCMD) 

		    vrTxt        = text(self.internalName + '_vrCamTxt',w=100, al='left', l='Version Revision: ')
		    vrOptMnu     = optionMenu(self.verRevCamOptMnu, width=100, cc=self.verRevOptCMD)
		    
		    camTxt       = text(self.internalName + '_camTxt', w=51, al='left', l='Camera: ')
		    camOptMnu    = optionMenu(self.refCamOptMnu,width=100, cc=self.camOptCMD)
		    
		    self.addBaseMenuItem()
		    
		    formLayout(form, edit=True,
		               attachForm=[(self.pathTxt,'left',5),(self.pathTxt,'top',5),(self.pathTxt,'right',5),
		                           (baseTxt,'left',5)],
		               
		               attachControl=[(baseTxt,'top',7,self.pathTxt),
		                            (baseOptMnu, 'left',5,baseTxt),(baseOptMnu, 'top',5,self.pathTxt),
		                            (vrTxt,'left',10,baseOptMnu),(vrTxt,'top',7,self.pathTxt),
		                            (vrOptMnu,'left',5,vrTxt),(vrOptMnu,'top',5,self.pathTxt),
		                            (camTxt,'left',10,vrOptMnu),(camTxt,'top',7,self.pathTxt),
		                            (camOptMnu, 'left',5,camTxt),(camOptMnu,'top',5, self.pathTxt)
		                            ]
	           )
		    
	camObj = Atom_Geo_Cache_ImportCameraLayout(self.internalName +'_refCam', self)
	camObj.cameraFormLayout()
    
    def scrollLayout(self):
	mainScroll = scrollLayout(self.internalName + '_mainScrollLayout',cr=True)
	with mainScroll:
	    mainColumn = columnLayout(self.internalName + '_mainColumnLayout', adj=True, cal='center', cat=('both',5), rs=2)
	    with mainColumn:
		cmds.button(l='R E F R E S H', c=self.win)
		self.addCameraLayout()
		references = listReferences()
		for ref in references:
		    #print ref
		    #print ref.refNode
		    setParent(mainColumn)
		    self.buildLayouts(ref.refNode)
	
    def buildLayouts(self,name):
	self.control = Atom_Geo_Cache_FrameLayout(self,name, uiType=self.uiType)
	self.control.frameLayout()
	if self.control.loadState:
	    Atom_Import_Geo_Cache_FormLayout(name, self.control).formLayout()
	
def atom_export_geo_cache_win(*args):
    AtomGeoCache = Atom_Geo_Cache('atomExportGeoCache','Atom Export Geo Cache','Atom Cache Geo')
    AtomGeoCache.win()
    scriptJob( uiDeleted=[AtomGeoCache.intWinName, AtomGeoCache.deleteChildren])

def addCameraExportGeoTag(*args):
    sel= ls(sl=True)    
    for obj in sel:
	attr = 'camera_export_geo'
	if not obj.hasAttr(attr):
	    obj.addAttr(attr,at='message')
	    msgStr = '%s attribute "%s" added successfully!' %(obj, attr)
	    OpenMaya.MGlobal.displayInfo(msgStr)
                
def deleteCameraExportGeoTag(*args):
    sel= ls(sl=True)    
    for obj in sel:
	attr = 'camera_export_geo'
	if obj.hasAttr(attr):
	    obj.deleteAttr(attr)
	    msgStr = '%s attribute "%s" deleted successfully!' %(obj, attr)
	    OpenMaya.MGlobal.displayInfo(msgStr)
objects = Atom_Tag_Core()
masters = objects.getMasters()
#Atom_Geo_Cache_Core('test','test','test').win()
#atom_export_geo_cache_win()
#Atom_Tag_Win().win()
#Atom_Tag_SingleMaster_Select()
#Atom_Import_Geo_Cache('atomImportGeoCache','Atom Import   Geo Cache', uiType='import').win()