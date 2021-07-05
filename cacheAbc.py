import os
import subprocess

import maya.cmds as cmds
import maya.mel as mel

# // CVD DM specific playblaster
# //AbcExport -j "-frameRange 1 5 -step 0.5 -root |group|foo -file /tmp/test.abc"

# string $filePath = `file -q -sn`;
path = cmds.file( query = True, sceneName = True )
'''
//string $fileList = 
string $pathTokens[];
string $splitTokens[];
string $numTokens[];
string $numTokens1[];
string $numTokens2[];
string $numTokens3[];
#

# //find out version
int $tokenCount = `tokenize ($filePath) "//" $pathTokens`;
int $scnCount = `tokenize ($filePath) "//" $pathTokens`;
string $sceneName = $pathTokens[$scnCount-1];
string $outPath = $pathTokens[$tokenCount-5];
string $epNum = $pathTokens[$tokenCount-6];
string $shotName = $pathTokens[$tokenCount-5];
string $showName = $pathTokens[$tokenCount-7];

int $tokenCount1 = `tokenize ($sceneName) "_" $numTokens`;
string $fileName = $numTokens[$tokenCount1-1];

int $tokenCount2 = `tokenize ($fileName) "." $numTokens`;
string $verName1 = $numTokens[$tokenCount2-2];
string $verName2 = $numTokens[$tokenCount2-1];

string $verName3 = $verName1 + "_" + $verName2;


string $fname = $shotName + "_" + $verName1;
string $fpath = $fname + "/" + $fname;
'''

# int $frmS1 = `playbackOptions -q -ast`;
# int $frmE1 = `playbackOptions -q -aet`;
frmS1 = cmds.playbackOptions(q=True, animationStartTime = True )
frmE1 = cmds.playbackOptions(q=True,  animationEndTime = True )


# string $dataEx[] = `ls -sl -type "transform"`;
dataEx = cmds.ls( sl = True, type= 'transform' )

# //string $outTopGrp[] = `pickWalk -d up`;

# string $outDataExp = $dataEx[0]; 
outDataExp = dataEx[0]


string $nameTokens[];
int $tokenCount10 = `tokenize ($dataEx[0]) ":" $nameTokens`;
string $objName = $nameTokens[$tokenCount10-1];

string $outputAbc = "P:/" + $showName + "/" + $epNum + "/" + $shotName+ "/assets/geo/" + $shotName + "_" + $objName + "_" + $verName1 + ".abc";

string $outExec = "-frameRange " + $frmS1 +" "+ $frmE1 + " -u vrayUserScalar_shaderId -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root " + $outDataExp +" -sn -uv -ws -file " + $outputAbc;

print $outExec;

# string $disIM[]= `ls -type imagePlane`;
disIM = cmds.ls( type= 'imagePlane' )

'''
int $num = size ($disIM);
for ( $i=0; $i<$num; ++$i )
{
    catchQuiet (`setAttr ($disIM[$i] + ".displayMode") 0`);
}'''

for i in disIM:
    cmds.setAttr(i + '.displayMode', 0)

AbcExport -j $outExec;

'''
string $disIM[]= `ls -type imagePlane`;
int $num = size ($disIM);
for ( $i=0; $i<$num; ++$i )
{
    catchQuiet (`setAttr ($disIM[$i] + ".displayMode") 2`);
}'''
 
for i in disIM:
    cmds.setAttr(i + '.displayMode', 2)