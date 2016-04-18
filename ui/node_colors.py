import bpy
from .. tree_info import getNetworks
from .. utils.layout import writeText
from .. preferences import getColorSettings


class NetworkColorsMode():
    @classmethod
    def colorNetwork(cls, network, nodesInNetwork, nodeByID = None):
        networkColor = cls.getNetworkColor(network, nodeByID)
        for node in nodesInNetwork:
            if not node.useNetworkColor: continue
            node.use_custom_color = True
            color = networkColor
            if node.bl_idname == "an_InvokeSubprogramNode":
                if node.subprogramNetwork: color = cls.getNetworkColor(node.subprogramNetwork, nodeByID)
            node.color = color

    @classmethod
    def getNetworkColor(cls, network, nodeByID):
        colors = getColorSettings()
        if network.type == "Invalid": return colors.invalidNetwork
        if network.type == "Main": return colors.mainNetwork
        if network.type in ("Group", "Loop", "Script"):
            return network.getOwnerNode(nodeByID).networkColor


coloringMode = "NETWORK"

def colorNetworks():
    for network in getNetworks():
        colorNetwork(network, network.getAnimationNodes())

def colorNetwork(network, nodesInNetwork, nodeByID = None):
    if coloringMode == "NETWORK":
        NetworkColorsMode.colorNetwork(network, nodesInNetwork)


def drawNodeColorPanel(self, context):
    node = bpy.context.active_node
    if not getattr(node, "isAnimationNode", False): return

    col = self.layout.column(align = True)
    col.prop(node, "useNetworkColor")

    if node.bl_idname == "an_InvokeSubprogramNode": network = node.subprogramNetwork
    else: network = node.network

    if getattr(network, "isSubnetwork", False): col.prop(network.getOwnerNode(), "networkColor", text = "")
    else: writeText(col, "Only subprograms have a custom network color", width = 25)

# Register
##################################

def register():
    bpy.types.NODE_PT_active_node_color.append(drawNodeColorPanel)

def unregister():
    bpy.types.NODE_PT_active_node_color.remove(drawNodeColorPanel)
