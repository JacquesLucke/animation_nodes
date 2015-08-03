import bpy
from ... base_types.node import AnimationNode
from ... utils.nodes import NodeTreeInfo

class ReverseListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReverseListNode"
    bl_label = "Reverse List"

    inputNames = { "List" : "list" }
    outputNames = { "Reversed List" : "list" }

    def create(self):
        self.generateSockets()

    def execute(self, list):
        list.reverse()
        return list

    def edit(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Reversed List"))

        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(targetSockets[0].bl_idname)
            nodeTree.links.new(targetSockets[0], self.outputs.get("Reversed List"))

    def generateSockets(self, listIdName = "an_ObjectListSocket"):
        if listIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return

        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.outputs.new(listIdName, "Reversed List")
