from .. algorithms.random import getRandomColor
from .. utils.timing import measureTime
from .. import preferences

def colorNetworks():
    from .. import tree_info
    for network in tree_info.getNetworks():
        colorNetwork(network)

def colorNetwork(network):
    networkColor = getNetworkColor(network)
    for node in network.getNodes():
        if node.useNetworkColor:
            node.use_custom_color = True
            color = networkColor
            if node.bl_idname == "an_InvokeSubprogramNode":
                if node.subprogramNetwork: color = getNetworkColor(node.subprogramNetwork)
            node.color = color

def getNetworkColor(network):
    colors = getColors()
    if network.type == "Invalid": return colors.invalidNetwork
    if network.type == "Main": return colors.mainNetwork
    if network.type in ("Group", "Loop"): return getRandomNetworkColor(network)

def getRandomNetworkColor(network):
    colors = getColors()
    seed = hash(network.identifier) % 1e5
    return getRandomColor(seed, value = colors.subprogramValue, saturation = colors.subprogramSaturation)

def getColors():
    return preferences.nodeColors()
