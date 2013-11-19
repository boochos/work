import maya.cmds as cmds
import maya.mel as mel
import os
#from shotgun import shot_tools

def refMostRecent(*args):
    gotLength = '(Timeline is set to Shotgun length)'
    noLength = '(Timeline was not set)'
    timeline = gotLength
    ws = cmds.workspace(query=True,rd=True)
    print ws
    objPath=os.path.join(ws,'Sound')
    print objPath
    #get current scene name
    currentF = cmds.file(q=True, sn=True)
    #get shot length from Shotgun
    shotLen =  None #int(shot_tools.get_sg_shot_length_from_path(currentF))
    if shotLen != None:
        mel.eval('warning \"' + '////... ---Getting shot length from Shotgun ...////' + '\";')
        cmds.playbackOptions( min=1.0, ast=1.0, max=(float(shotLen)), aet=(float(shotLen)) )
        mel.eval('warning \"' + '////... ' + timeline + ' ---Importing Audio file...////' + '\";')
    else:
        mel.eval('warning \"' + '////... Shot length not found in Shotgun. Getting Audio ...////' + '\";')
        timeline = noLength
    ##print objPath
    if os.path.exists(objPath):
        folderFiles = os.listdir(objPath)
        if len(folderFiles) > 0:
            folderFiles.sort()
            date_file_list=[]
            import time
            #sort the files based on date
            #need to add a filter for specified file types
            for obj in folderFiles:
                #some files may be in the directory that have a . in front of them
                #these files will be passed
                srch = obj.find('.')
                if srch != 0:
                    path  = os.path.join(objPath,obj)
                    #make sure only the most recent files are being referenced
                    if not os.path.isdir(path):
                        stats = os.stat(path)
                        lastmod_date = time.localtime(stats[8])
                        date_file_tuple = lastmod_date, path
                        date_file_list.append(date_file_tuple)
            #sort the list then reverse it
            date_file_list.sort()
            #the newest file is first in the list
            date_file_list.reverse()
            #get the file name
            path     = date_file_list[0][1]
            fileName = os.path.split(date_file_list[0][1])[1].split('.')[0]
            #make sure audio is compatible with scene
            if fileName in currentF:
                path = os.path.join(objPath,fileName) + '.aif'
                if 'Audio_' not in fileName:
                    audioNodeName = fileName + '_Audio' 
                    ##print audioNodeName
                else:
                    audioNodeName = fileName
                audioNode = cmds.sound(name=audioNodeName, f=path, o=1)
                aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
                cmds.timeControl( aPlayBackSliderPython, e=True, sound=audioNode, displaySound=True )
                #mel.eval('setPlaybackRangeToSound;')
                soundLen = int(cmds.sound(audioNode, query=True, length=True))
                if soundLen != shotLen:
                    mel.eval('warning \"' + '////... ' + timeline + ' ---Mismatch:  --audio Length ' + str(soundLen) + ' - Shotgun Length ' + str(shotLen) + ' --  ////' + '\";')
                else:
                    mel.eval('warning \"' + '////... (Success!) ---Match:  --audio Length ' + str(soundLen) + ' - Shotgun Length ' + str(shotLen) + ' ...////' + '\";')
            else:
                mel.eval('warning \"' + '////...' + timeline + '  ---Mismatch:  --audio Name - scene Name--  Set project or get audio manually ...////' + '\";')
                cmds.Import()
        else:
            mel.eval('warning \"' + '////... ' + timeline + '  ---No audio files found. ---Ensure project was set ---or pick file from Browser window ...////' + '\";')
            cmds.Import()
    else:
        mel.eval('warning \"' + '////... Directory Not Found ...////' + '\";')