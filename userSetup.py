# start animBot

from maya import cmds
if not cmds.about(batch=True):
    cmds.evalDeferred(lambda: cmds.evalDeferred("import animBot; animBot.launch()", lowestPriority=True))

# end animBot