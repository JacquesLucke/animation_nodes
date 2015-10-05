import bpy
from .. import problems
from .. preferences import getPreferences
from .. utils.blender_ui import iterAreas
from .. utils.nodes import getAnimationNodeTrees

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
        for scene in set(tree.scene for tree in getAnimationNodeTrees()):
            scene.update()

    from .. events import isRendering
    if prefs.redrawAllAfterAutoExecution and not isRendering():
        redrawAll()

def redrawAll():
    for area in iterAreas():
        area.tag_redraw()
