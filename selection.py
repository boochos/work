import maya.cmds as cmds


class Sel():

    def __init__(self):
        self.sel = []
        self.store()

    def store(self):
        self.sel = cmds.ls(sl=True)

    def select(self):
        cmds.select(self.sel, add=True)

    def clear(self):
        self.sel = []

    def prnt(self):
        if len(self.sel) == 0:
            self.sel = cmds.ls(sl=True)
        i = 1
        print '['
        for item in self.sel:
            if i != len(self.sel):
                print "'" + item + "',"
            else:
                print "'" + item + "'"
            i = i + 1
        print ']'
