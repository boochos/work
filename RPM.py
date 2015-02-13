import maya.cmds as cmds


class RPM():
    def __init__(self):
        self.attr = None
        self.obj = None
        self.label = None
        self.hud = 'RPM'
        self.frames = []
        self.val = []
        self.rpm = []
        self.getObj()
        if self.attr is not None:
            self.display()

    def getObj(self):
        try:
            self.attr = cmds.channelBox('mainChannelBox', q=True, sma=True)[0]
            self.obj = cmds.channelBox('mainChannelBox', q=True, mol=True)[0]
            self.label = self.hud + '__' + self.obj + '.' + self.attr
        except:
            cmds.warning('Select an attr in the ChannelBox')

    def avg(self):
        # 360/(fps * 60) = degrees
        # 360/(24  * 60) = 0.25
        self.frames = [cmds.currentTime(q=True) - 1, cmds.currentTime(q=True), cmds.currentTime(q=True) + 1]
        self.val = []
        self.rpm = []
        for frame in self.frames:
            self.val.append(cmds.getAttr(self.obj + '.' + self.attr, t=frame))
        list(set(self.val))
        if len(self.val) != 1:
            self.rpm.append((self.val[0] - self.val[1]) / 0.25)
            self.rpm.append((self.val[1] - self.val[2]) / 0.25)
            # average of 2 values
            return sum(self.rpm, 0.0) / len(self.rpm)
        else:
            return 0.0

    def remove(self):
        if cmds.headsUpDisplay(self.hud, ex=True):
            cmds.headsUpDisplay(self.hud, remove=True)

    def display(self):
        self.remove()
        cmds.headsUpDisplay(self.hud, section=1, block=0, blockSize='small', label=self.label, labelFontSize='small', command=self.avg, event='idle')  # nodeChanges='attributeChange'
