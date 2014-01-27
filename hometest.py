#establish
X   = loc sizes
aim = aim vectors
up  = up vectors
dis = distance mid to tip
mlt = offset multiplier
#4 objects selected
obj[0] = tip control
obj[1] = mid control
obj[2] = base control
obj[3] = hand

#base
base = place loc on obj[2]
cmds.parentConstraint(obj[3], base, mo=1)

#base up
baseUp = place loc on obj[2]
cmds.parent(baseUp, base)
cmds.setAttr(baseUp + '.ty', offset*5)
cmds.parentConstraint(obj[2], baseUp, mo=1)
bake
match keys to base

#mid base
mid = place loc on obj[1]
cmds.parent(mid, base)
cmds.parentConstraint(obj[1], mid, mo=1)
bake
match keys to mid base

#mid up
midUp = place loc on obj[1]
cmds.parent(midUp, mid)
cmds.setAttr(midUp + '.ty', offset*5)
cmds.parentConstraint(obj[1], midUp, mo=1)
bake
match keys to mid base

#tip base, tip target, tip up
#1 loc (tip base)
tip = place loc on obj[0]
cmds.parentConstraint(obj[0], tip, mo=1)

#2 loc (tip target)
tipTarget = place loc on obj[0]
cmds.parent(tipTarget, tip)
cmds.setAttr(midUp + '.tx', offset)
cmds.parent(tipTarget, w=1)
cmds.parentConstraint(tipTarget, tip, mo=1)
bake
match keys to tip base

#3 loc (tip up)
tipUp = place loc on obj[0]
cmds.parent(tipUp, tip)
cmds.setAttr(tipUp + '.ty', offset*5)
cmds.parentConstraint(tip, tipUp, mo=1)
bake
match keys to tip base

#loc 1 (tip target)
cmds.parent(tip, tipTarget)
bake
match keys to tip target
