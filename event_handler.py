from . import problems
from . update import updateEverything
from . utils.recursion import noRecursion
from . utils.nodes import iterAnimationNodes, getAnimationNodeTrees
from . execution.units import setupExecutionUnits, finishExecutionUnits
from . execution.auto_execution import autoExecuteMainUnits, afterExecution

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}) or didNameChange():
        updateEverything()

    if problems.canAutoExecute():
        setupExecutionUnits()
        executed = autoExecuteMainUnits(events)
        if executed: afterExecution()
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
    treeNames = "".join((tree.name for tree in getAnimationNodeTrees()))
    nodeNames = "".join((node.name for node in iterAnimationNodes()))
    return len(treeNames) + len(nodeNames)
