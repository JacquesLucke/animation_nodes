import bpy, random
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ShuffleListNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ShuffleListNode"
    bl_label = "Shuffle List"
    
    def init(self, context):
        forbidCompiling()
        self.generateSockets()
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Seed" : "seed"}
    def getOutputSocketNames(self):
        return {"Shuffled List" : "shuffledList"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return """
random.seed(%seed%)
$shuffledList$ = %list%[:]
random.shuffle($shuffledList$) """

    def getModuleList(self):
        return ["random"]
        
    def update(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Shuffled List"))
        
        forbidCompiling()
        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(targetSockets[0].bl_idname)
            nodeTree.links.new(targetSockets[0], self.outputs.get("Shuffled List"))
        allowCompiling()
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        if not isListSocketIdName(listIdName): return
        
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.outputs.new(listIdName, "Shuffled List")
        allowCompiling()
