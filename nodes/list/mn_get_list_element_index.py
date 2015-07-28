import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListElementIndexNode(Node, AnimationNode):
    bl_idname = "mn_GetListElementIndexNode"
    bl_label = "Get Element Index"    #Search List Element ?
    
    def init(self, context):
        forbidCompiling()
        self.generateSockets()  #could use generic, just analize #if we use generic we skip all socket update
        self.outputs.new("mn_IntegerListSocket", "Indices")
        self.outputs.new("mn_IntegerSocket", "Occurrences")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Search" : "search"}
    def getOutputSocketNames(self):
        return {"Indices" : "indices",
                "Occurrences" : "occurrences"}
        
    def execute(self, list, search):  
        indices = [i for i, x in enumerate(list) if x == search]    #some say count may be faster
        return indices, len(indices)
        
    def update(self):   
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        
        forbidCompiling()
        if originSocket is not None:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        allowCompiling()
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        baseIdName = getListBaseSocketIdName(listIdName)
        if baseIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        forbidCompiling()
        self.inputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new(baseIdName, "Search")
        allowCompiling()
