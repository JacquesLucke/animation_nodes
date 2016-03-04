import bpy
from .. import problems
from .. preferences import getPreferences
from .. utils.blender_ui import iterAreas
from .. utils.nodes import getAnimationNodeTrees

def iterAutoExecutionNodeTrees(events):
    if not problems.canExecute(): return
    for nodeTree in getAnimationNodeTrees():
        if nodeTree.canAutoExecute(events):
            yield nodeTree

def executeNodeTrees(nodeTrees):
    for nodeTree in nodeTrees:
        nodeTree.autoExecute()

def afterExecution():
    prefs = getPreferences()
    if prefs.sceneUpdateAfterAutoExecution:
        for scene in bpy.data.scenes:
            scene.update()

    from .. events import isRendering
    if prefs.redrawAllAfterAutoExecution and not isRendering():
        redrawAll()

def redrawAll():
    for area in iterAreas():
        area.tag_redraw()
