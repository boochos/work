sel = cmds.ls( sl = 1 )[0]
path = 'O:\\projects\\cbw\\cbw100\\cbw100_142\\cbw100_142_030\\renders\\RetimeCurve_v001.txt'
path = 'P:\\FATE2\\207\\FATE2_207_018_0130\\comp\\207_018_0130_retime_curve_v001.txt'
print( path )
f = open( path )
lines = f.readlines()
for line in lines:
    v_f = line.split( ' ' )
    value = float( v_f[0] )
    frame = float( v_f[1] )
    cmds.setKeyframe( sel, attribute = 'timeWarpedFrame', t = [frame, frame], v = value )

