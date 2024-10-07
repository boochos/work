sel = cmds.ls( sl = 1 )
for s in sel:
    pos = cmds.xform( s, q = 1, ws = True, rp = True )
    print( pos )
    txt = s.split( ':' )[0]
    ann = cmds.annotate( s, tx = txt, p = ( 0, 0, 0 ) )
    cmds.setAttr( ann + '.displayArrow', 0 )
    p = cmds.listRelatives( ann, p = 1 )
    cmds.xform( p, ws = 1, t = [pos[0], pos[1] + 2, pos[2]] )
    print( p )
    cmds.parentConstraint( s, p, mo = True )
