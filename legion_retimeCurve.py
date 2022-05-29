sel = cmds.ls( sl = 1 )[0]
path = 'O:\\projects\\cbw\\cbw100\\cbw100_142\\cbw100_142_030\\renders\\RetimeCurve_v001.txt'
print( path )
f = open( path )
lines = f.readlines()
for line in lines:
    v_f = line.split( ' ' )
    value = float( v_f[0] )
    frame = float( v_f[1] )
    cmds.setKeyframe( sel, attribute = 'timeWarpedFrame', t = [frame, frame], v = value )

