import bpy
from .. import preferences
from .. tree_info import getNetworks
from .. utils.layout import writeText
from .. algorithms.random import getRandomColor

def colorNetworks():
    for network in getNetworks():
        colorNetwork(network, network.getAnimationNodes())

def colorNetwork(network, nodes):
    networkColor = getNetworkColor(network)
    for node in nodes:
        if not node.useNetworkColor: continue
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
        return network.ownerNode.networkColor

def getColors():
    return preferences.nodeColors()


def draw(self, context):
    node = bpy.context.active_node
    if not hasattr(context.active_node, "isAnimationNode"): return

    col = self.layout.column(align = True)
    col.prop(node, "useNetworkColor")

    if node.bl_idname == "an_InvokeSubprogramNode": network = node.subprogramNetwork
    else: network = node.network

    if network.isSubnetwork: col.prop(network.ownerNode, "networkColor", text = "")
    else: writeText(col, "Only subprograms have a custom network color", width = 25)

# Register
##################################

def register():
    bpy.types.NODE_PT_active_node_color.append(draw)

def unregister():
    bpy.types.NODE_PT_active_node_color.remove(draw)
