from . import tree_info
from . utils.nodes import iterAnimationNodes
from . utils.recursion import noRecursion
from . node_link_conversion import correctForbiddenNodeLinks
from . utils.timing import measureTime
from . execution.units import createExecutionUnits, setupExecutionUnits, finishExecutionUnits
from . execution.auto_execution import autoExecuteMainUnits, afterExecution

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}):
        correctNodeTree()
        markNodesInInvalidNetworks()
        createExecutionUnits()

    setupExecutionUnits()
    executed = autoExecuteMainUnits(events)
    if executed: afterExecution()
    finishExecutionUnits()

@measureTime
def correctNodeTree():
    updateDataIfNecessary()
    updateAllNodes()
    correctForbiddenNodeLinks()
    updateDataIfNecessary()

def updateAllNodes():
    for node in iterAnimationNodes():
        node.edit()
        updateDataIfNecessary()

treeUpdatedWhileWorking = False
def treeNeedsUpdate():
    global treeUpdatedWhileWorking
    treeUpdatedWhileWorking = True

def updateDataIfNecessary():
    global treeUpdatedWhileWorking
    if treeUpdatedWhileWorking:
        tree_info.update()
        treeUpdatedWhileWorking = False

def markNodesInInvalidNetworks():
    for network in tree_info.getNetworks():
        isInvalid = network.type == "Invalid"
        for node in network.getAnimationNodes():
            node.inInvalidNetwork = isInvalid
