from . import problems
from . import tree_info
from . ui import node_colors
from . utils.nodes import iterAnimationNodes, getAnimationNodeTrees
from . execution.units import createExecutionUnits
from . node_link_conversion import correctForbiddenNodeLinks

def updateEverything():
    '''
    Call when the node tree changed in a way that the execution code does
    not work anymore.
    '''
    problems.reset()
    enableUseFakeUser()
    callNodeEditFunctions()
    correctForbiddenNodeLinks()
    checkNetworks()
    createExecutionUnits()


def enableUseFakeUser():
    '''
    Make sure the node trees will not be removed when closing the file.
    '''
    for tree in getAnimationNodeTrees():
        tree.use_fake_user = True

def callNodeEditFunctions():
    tree_info.updateIfNecessary()
    for node in iterAnimationNodes():
        node.edit()
        tree_info.updateIfNecessary()

def checkNetworks():
    invalidNetworkExists = False

    for network in tree_info.getNetworks():
        if network.type == "Invalid":
            invalidNetworkExists = True
        nodes = network.getAnimationNodes()
        markInvalidNodes(network, nodes)
        node_colors.colorNetwork(network, nodes)
        checkNodeOptions(network, nodes)

    if invalidNetworkExists:
        problems.InvalidNetworksExist().report()

def markInvalidNodes(network, nodes):
    isInvalid = network.type == "Invalid"
    for node in nodes:
        node.inInvalidNetwork = isInvalid

def checkNodeOptions(network, nodes):
    for node in nodes:
        if "No Execution" in node.options:
            problems.NodeDoesNotSupportExecution(node.identifier).report()
        if "No Subprogram" in node.options and network.type in ("Group", "Loop"):
            problems.NodeMustNotBeInSubprogram(node.identifier).report()
        if "No Auto Execution" in node.options:
            problems.NodeShouldNotBeUsedInAutoExecution(node.identifier).report()
