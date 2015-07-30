import bpy
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class GetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GetListElementNode"
    bl_label = "Get List Element"
    
    inputNames = { "List" : "list",
                   "Index" : "index",
                   "Fallback" : "fallback" }

    outputNames = { "Element" : "element" }                   
    
    def create(self):
        self.generateSockets()
        
    def execute(self, list, index, fallback):
        if 0 <= index < len(list):
            return list[index]
        return fallback
        
    def edit(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Element"))
        
        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(getListSocketIdName(targetSockets[0].bl_idname))
            nodeTree.links.new(targetSockets[0], self.outputs.get("Element"))
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        baseIdName = getListBaseSocketIdName(listIdName)
        if baseIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        self.id_data.startEdit()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new("mn_IntegerSocket", "Index")
        self.inputs.new(baseIdName, "Fallback")
        self.outputs.new(baseIdName, "Element")
        self.id_data.stopEdit()
