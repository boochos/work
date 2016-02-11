import maya.cmds as cmds
import maya.mel as mel


class Get():

    def __init__(self, fromSelection=True):
        self.min = cmds.playbackOptions(q=True, minTime=True)
        self.max = cmds.playbackOptions(q=True, maxTime=True)
        self.selStart = cmds.playbackOptions(q=True, minTime=True)
        self.selEnd = cmds.playbackOptions(q=True, maxTime=True)
        self.start = 0
        self.end = 0
        self.current = cmds.currentTime(q=True)
        self.setStartEnd()
        self.keyStart = 0
        self.keyEnd = 0
        self.selection = False
        if fromSelection:
            self.keyedFrames()
        # Has to be last
        self.selRange()

    def selRange(self):
        # overide range if selected range is detected
        sel = cmds.timeControl('timeControl1', q=True, ra=True)
        range = sel[1] - sel[0]
        if range > 1:
            self.selStart = sel[0]
            self.selEnd = sel[1]
            self.keyStart = sel[0]
            self.keyEnd = sel[1]
            self.selection = True

    def selRangeRecover(self):
        # after baking sel range gets lost, investigate
        pass
        # sel = cmds.timeControl('timeControl1', ra=[self.keyStart, self.keyEnd])

    def setStartEnd(self):
        if self.selStart != 0:
            self.start = self.selStart
            self.end = self.selEnd
        else:
            self.start = self.min
            self.end = self.max

    def keyedFrames(self):
        selAll = cmds.ls(sl=True)
        # print 'X     ', selAll
        frames = []
        if selAll:
            for sel in selAll:
                animCurves = cmds.findKeyframe(sel, c=True)
                # print 'XX    ',
                if animCurves is not None:
                    for crv in animCurves:
                        framesTmp = cmds.keyframe(crv, q=True)
                        # print 'XXX    ', framesTmp
                        for frame in framesTmp:
                            frames.append(frame)
                    frames = list(set(frames))
                    # print 'XXXX    ', frames, selAll
                    self.keyStart = min(frames)
                    self.keyEnd = max(frames)
                else:
                    # print 'no anim curves', sel
                    pass
        else:
            print '-- Select an object. --'
