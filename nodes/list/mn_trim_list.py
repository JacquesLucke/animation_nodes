import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TrimList(Node, AnimationNode):
    bl_idname = "mn_TrimList"
    bl_label = "Trim List"
    
    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        nodePropertyChanged(self, context)
    

    #adding options and all, keep it like text trim, but list sockets

    autoEnd = bpy.props.BoolProperty(default = False, description = "Use the length of the list as trim-end", update = settingChanged)
    allowNegativeIndex =  bpy.props.BoolProperty(default = False, description = "Allow nwgative index values for start / end")
    
    def init(self, context):
        forbidCompiling()
        self.generateSockets()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Index")
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Start" : "start",
                "End" : "end"}
                
    def getOutputSocketNames(self):
        return {"List" : "list"}
        
    def execute(self, list, start, end):
        listLength = len(list)
        
        if self.autoEnd: end = listLength
        
        minIndex = -listLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), listLength)
        end = min(max(minIndex, end), listLength)
        
        return list[start:end]
    
    def update(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        
        listInput = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        listOutputs = treeInfo.getDataTargetSockets(self.outputs.get("List"))
        
        forbidCompiling()
        
        if listInput is not None and len(listOutputs) == 0:
            self.generateSockets(listInput.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), listInput)
            
        if listInput is None and len(listOutputs) == 1:
            self.generateSockets(listOutputs[0].bl_idname)
            nodeTree.links.new(listOutputs[0], self.outputs.get("List"))
            
        allowCompiling()
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new("mn_IntegerSocket", "Start").number = 0
        self.inputs.new("mn_IntegerSocket", "End").number = 5
        self.outputs.new(listIdName, "List")
        allowCompiling()
