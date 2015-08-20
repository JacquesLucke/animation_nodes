import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getSubprogramNetworks, getNodeFromIdentifier, getNetworkByIdentifier
from ... utils.enum_items import enumItemsFromDicts

@enumItemsFromDicts
def getSubprogramItems(self, context):
    itemDict = []
    for network in getSubprogramNetworks():
        itemDict.append({
            "id" : network.identifier,
            "name" : network.name,
            "description" : network.description})
    return itemDict

class SubprogramCaller(bpy.types.Node, AnimationNode):
    bl_idname = "an_SubprogramCaller"
    bl_label = "Subprogram Caller"

    def subprogramIdentifierChanged(self, context):
        self.updateSockets()

    def selectedSubprogramChanged(self, context):
        self.subprogramIdentifier = self.selectedSubprogram

    subprogramIdentifier = StringProperty(name = "Subprogram Identifier", default = "", update = subprogramIdentifierChanged)
    selectedSubprogram = EnumProperty(name = "Subprogram", items = getSubprogramItems, update = selectedSubprogramChanged)

    def draw(self, layout):
        networks = getSubprogramNetworks()
        network = self.subprogramNetwork

        layout.separator()
        if len(networks) == 0:
            col = layout.column()
            col.scale_y = 1.6
            self.functionOperator(col, "createNewGroup", text = "Group", icon = "PLUS")
        elif network is None:
            layout.prop(self, "selectedSubprogram", text = "", icon = "GROUP_VERTEX")
        else:
            layout.label(network.name, icon = "GROUP_VERTEX")
        layout.separator()

    def drawAdvanced(self, layout):
        networks = getSubprogramNetworks()
        if len(networks) == 0:
            self.functionOperator(layout, "createNewGroup", text = "Group", icon = "PLUS")
        else:
            layout.prop(self, "selectedSubprogram", text = "", icon = "GROUP_VERTEX")

    def updateSockets(self):
        subprogram = self.subprogramNode
        if subprogram is None: self.clearSockets()
        else: subprogram.getSocketData().apply(self)

    @property
    def subprogramNode(self):
        try: return getNodeFromIdentifier(self.subprogramIdentifier)
        except: return None

    @property
    def subprogramNetwork(self):
        return getNetworkByIdentifier(self.subprogramIdentifier)

    def createNewGroup(self):
        bpy.ops.node.add_and_link_node(type = "an_GroupInput")
        inputNode = self.nodeTree.nodes[-1]
        inputNode.location.x -= 200
        inputNode.location.y += 40
        self.subprogramIdentifier = inputNode.identifier
        bpy.ops.node.add_and_link_node(type = "an_GroupOutput")
        outputNode = self.nodeTree.nodes[-1]
        outputNode.location.x += 60
        outputNode.location.y += 40
        outputNode.groupInputIdentifier = inputNode.identifier
        inputNode.select = True
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")
