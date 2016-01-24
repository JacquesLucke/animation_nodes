import itertools
from . import problems
from . update import updateEverything
from . utils.recursion import noRecursion
from . execution.units import setupExecutionUnits, finishExecutionUnits
from . utils.nodes import iterAnimationNodes, getAnimationNodeTrees, iterAnimationNodesSockets
from . execution.auto_execution import iterAutoExecutionNodeTrees, executeNodeTrees, afterExecution

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}) or didNameChange():
        updateEverything()

    updateSocketProperties()

    if problems.canAutoExecute():
        nodeTrees = list(iterAutoExecutionNodeTrees(events))
        if len(nodeTrees) > 0:
            setupExecutionUnits()
            executeNodeTrees(nodeTrees)
            afterExecution()
            finishExecutionUnits()


oldNamesHash = 0

def didNameChange():
    global oldNamesHash
    newHash = getNamesHash()
    if newHash != oldNamesHash:
        oldNamesHash = newHash
        return True
    return False

def getNamesHash():
    names = set(itertools.chain(
        (tree.name for tree in getAnimationNodeTrees()),
        (node.name for node in iterAnimationNodes())))
    return names

def updateSocketProperties():
    for socket in iterAnimationNodesSockets():
        socket.updateProperty()
