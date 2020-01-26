import bpy
from .. preferences import getPreferences
from .. utils.blender_ui import redrawAll
from .. utils.nodes import getAnimationNodeTrees

def iterAutoExecutionNodeTrees(events):
    for nodeTree in getAnimationNodeTrees():
        if nodeTree.canAutoExecute(events):
            yield nodeTree

def executeNodeTrees(nodeTrees):
    for nodeTree in nodeTrees:
        nodeTree.autoExecute()

def afterExecution():
    from .. events import isRendering
    if not isRendering():
        redrawAll()
