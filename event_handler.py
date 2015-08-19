from . import tree_info
from . utils.nodes import iterAnimationNodes
from . utils.recursion import noRecursion
from . node_link_conversion import correctForbiddenNodeLinks
from . utils.timing import measureTime

@noRecursion
def update(events):
    if events.intersection({"File", "Addon", "Tree"}):
        correctNodeTree()

    from . code_generator import generateCode
    network = tree_info._networks.networks[0]
    preparation, execution = generateCode(network)

    if "Tree" in events or "Addon" in events:
        print("#"*1000)
        print(execution)

    data = {}
    exec(preparation, data, data)
    #print(data["_factor_d9"])
    exec(execution, data, data)


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
