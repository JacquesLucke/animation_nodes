import bpy
from .. utils.nodes import getAnimationNodeTrees
from .. preferences import getPreferences

def autoExecuteMainUnits(events):
    executed = False
    for nodeTree in getAnimationNodeTrees():
        if nodeTree.canAutoExecute(events):
            nodeTree.autoExecute()
            executed = True
    return executed

def afterExecution():
    prefs = getPreferences()
    if prefs.sceneUpdateAfterAutoExecution:
        bpy.context.scene.update()
    if prefs.redrawAllAfterAutoExecution:
        redrawAll()

def redrawAll():
    for area in bpy.context.screen.areas:
        area.tag_redraw()
