import bpy
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import NodeTreeInfo
from ... sockets.mn_socket_info import getListBaseSocketIdName, getListSocketIdName

class AppendListNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_AppendListNode"
    bl_label = "Append to List"
    
    inputNames = { "List" : "list",
                   "Element" : "element" }
    outputNames = { "List" : "list" }
    
    def create(self):
        self.generateSockets()
        
    def getExecutionCode(self):
        return "$list$ = %list%\n" + \
                "$list$.append(%element%)"
                
    def edit(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        
        listInput = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        elementInput = treeInfo.getDataOriginSocket(self.inputs.get("Element"))
        listOutputs = treeInfo.getDataTargetSockets(self.outputs.get("List"))
        
        if listInput is not None and elementInput is None and len(listOutputs) == 0:
            self.generateSockets(listInput.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), listInput)
            
        if listInput is None and elementInput is not None and len(listOutputs) == 0:
            self.generateSockets(getListSocketIdName(elementInput.bl_idname))
            nodeTree.links.new(self.inputs.get("Element"), elementInput)
            
        if listInput is None and elementInput is None and len(listOutputs) == 1:
            self.generateSockets(listOutputs[0].bl_idname)
            nodeTree.links.new(listOutputs[0], self.outputs.get("List"))
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        baseIdName = getListBaseSocketIdName(listIdName)
        if baseIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        self.id_data.startEdit()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new(baseIdName, "Element")
        self.outputs.new(listIdName, "List")
        self.id_data.stopEdit()
