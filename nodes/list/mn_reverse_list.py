import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ReverseListNode(Node, AnimationNode):
    bl_idname = "mn_ReverseListNode"
    bl_label = "Reverse List"
    
    def init(self, context):
        forbidCompiling()
        self.generateSockets()
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"List" : "list"}
    def getOutputSocketNames(self):
        return {"Reversed List" : "list"}
        
    def execute(self, list):
        list.reverse()
        return list
        
    def update(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Reversed List"))
        
        forbidCompiling()
        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(targetSockets[0].bl_idname)
            nodeTree.links.new(targetSockets[0], self.outputs.get("Reversed List"))
        allowCompiling()
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.outputs.new(listIdName, "Reversed List")
        allowCompiling()
