import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getSubprogramNetworks, getNodeFromIdentifier
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

    subprogramIdentifier = StringProperty(name = "Subprogram Identifier", default = "")
    selectedSubprogram = EnumProperty(name = "Subprogram", items = getSubprogramItems)

    def draw(self, layout):
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
