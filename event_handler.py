from . import tree_info
from . utils.nodes import iterAnimationNodes
from . utils.recursion import noRecursion
from . node_link_conversion import correctForbiddenNodeLinks

@noRecursion
def update(events):
    if "Tree" in events:
        updateNodes()
        tree_info.update()
        correctForbiddenNodeLinks()

def updateNodes():
    updateAllNodes()

def updateAllNodes():
    for node in iterAnimationNodes():
        updateDataIfNecessary()
        node.edit()

treeUpdatedWhileWorking = False
def treeUpdated():
    global treeUpdatedWhileWorking
    treeUpdatedWhileWorking = True

def updateDataIfNecessary():
    global treeUpdatedWhileWorking
    if treeUpdatedWhileWorking:
        tree_info.update()
        treeUpdatedWhileWorking = False
