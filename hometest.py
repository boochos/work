#establish
loc sizes
aim vectors
distance mid to tip
4 objects selected

#base
place loc on base
constrain to hand, maintain offset

#base up
place loc on base
parent to base loc
add offset, ty
constrain to base
bake
match keys to base

#mid base
place loc on mid base
parent to base loc
constrain to mid base
bake
match keys to mid base

#mid up
place loc on mid base
parent to mid base
add offset, ty
constrain to mid base
bake
match keys to mid base

#tip base, tip target, tip up
#1 loc (tip base)
place loc on tip base
constrain to tip base

#2 loc (tip target)
place loc on tip base
parent to tip base loc
add offset, tx
unparent loc
constrain to tip base
bake
match keys to tip base

#3 loc (tip up)
place loc on tip base
parent to tip base loc
add offset, ty
constrain to tip base
bake
match keys to tip base

#loc 1 (tip target)
parent tip base loc to tip target
bake
match keys to tip target
