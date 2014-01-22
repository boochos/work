def smoothImproved():
    crvs   = '' #cmds.keyframe(q=True, name=True, sl=True)
    frames = [0.0,5.0,10.0] #cmds.keyframe(crvs, q=True, sl=True)
    size   = len(frames)
    value  = None
    if size > 2:
        #first key val
        x = 0.0#cmds.keyframe(crvs, q=True, vc=True, time=(frames[0], frames[0]))[0]
        i=0
        for frame in frames:
            if frame == frames[0] or frame == frames[size-1]:
                pass
            else:
                #this itter
                y = 2.5 #cmds.keyframe(crvs, q=True, vc=True, time=(frame, frame))[0]
                #next itter
                z = 5.0 #cmds.keyframe(crvs, q=True, vc=True, time=(frame, frame))[0]
                frameRange = int((frames[i-1] - frames[i+1])*-1)
                valueRange = x-z
                if valueRange < 0:
                    valueRange = valueRange*-1
                inc = valueRange/frameRange
                mlt = int((frames[i-1] - frame)*-1)
                keyPos = inc*mlt
                print keyPos
                #cmds.keyframe(crvs, vc=keyPos, time=(frame, frame))
            i=i+1


smoothImproved()
