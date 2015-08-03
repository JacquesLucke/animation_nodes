import bpy
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import NodeTreeInfo
from ... sockets.info import isList

class ShuffleListNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ShuffleListNode"
    bl_label = "Shuffle List"

    inputNames = { "List" : "list",
                   "Seed" : "seed" }

    outputNames = { "Shuffled List" : "shuffledList" }

    def create(self):
        self.generateSockets()

    def getExecutionCode(self, outputUse):
        return ("random.seed(%seed%) \n"
                "$shuffledList$ = %list%[:] \n"
                "random.shuffle($shuffledList$)")

    def getModuleList(self):
        return ["random"]

    def edit(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Shuffled List"))

        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(targetSockets[0].bl_idname)
            nodeTree.links.new(targetSockets[0], self.outputs.get("Shuffled List"))

    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        if not isList(listIdName): return

        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.outputs.new(listIdName, "Shuffled List")
