from .. import preferences
from .. tree_info import getNetworks
from .. algorithms.random import getRandomColor

def colorNetworks():
    for network in getNetworks():
        colorNetwork(network, network.getAnimationNodes())

def colorNetwork(network, nodes):
    networkColor = getNetworkColor(network)
    for node in nodes:
        if node.useAutoColor:
            node.use_custom_color = True
            color = networkColor
            if node.bl_idname == "an_InvokeSubprogramNode":
                if node.subprogramNetwork: color = getNetworkColor(node.subprogramNetwork)
            node.color = color

def getNetworkColor(network):
    colors = getColors()
    if network.type == "Invalid": return colors.invalidNetwork
    if network.type == "Main": return colors.mainNetwork
    if network.type in ("Group", "Loop", "Script"):
        node = network.ownerNode
        if node.useAutoColor: return getRandomNetworkColor(network)
        return node.color

def getRandomNetworkColor(network):
    colors = getColors()
    seed = hash(network.identifier) % 1e5
    return getRandomColor(seed, value = colors.subprogramValue, saturation = colors.subprogramSaturation)

def getColors():
    return preferences.nodeColors()
