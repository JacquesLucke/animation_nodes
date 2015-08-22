import bpy
from .. import problems
from .. utils.nodes import getAnimationNodeTrees
from .. preferences import getPreferences

def autoExecuteMainUnits(events):
    if not problems.canExecute(): return False
    
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
    if bpy.context.screen is None: return
    for area in bpy.context.screen.areas:
        area.tag_redraw()
