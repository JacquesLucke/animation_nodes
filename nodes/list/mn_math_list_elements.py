import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_MathListElementsNode(Node, AnimationNode):
    bl_idname = "mn_MathListElementsNode" 
    bl_label = "Math List Elements"  
    #separated from Sum elements
    #adding option for negative/autoEnd like in trim - 
    #we can keep original Sum elements (hidden) for backwards compatibility
    
    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        nodePropertyChanged(self, context)
        
    autoEnd = bpy.props.BoolProperty(default = False, description = "Use the length of the list as trim-end", update = settingChanged)
    allowNegativeIndex =  bpy.props.BoolProperty(default = False, description = "Negative indices start from the end")
    
    listOperations = [
        ("SUM", "Sum", ""),
        ("AVERAGE", "Average", ""),
        ("MINIMUM", "Minimum", ""),
        ("MAXIMUM", "Maximum", "")]#more?

    listOperationsProperty = bpy.props.EnumProperty(name = "Operation", items = listOperations, default = "SUM")#, update = setSocketTypes, update = nodePropertyChanged
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List")
        self.inputs.new("mn_IntegerSocket", "Start").number = 0
        self.inputs.new("mn_IntegerSocket", "End").number = 5
        self.outputs.new("mn_FloatSocket", "Number").number = 0
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "listOperationsProperty")
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Index")
        
    def getNextNodeSuggestions(self):
        return [("mn_FloatMathNode", (0, 0)),
                ("mn_CombineVector", (0, 0)),
                ("mn_AnimateFloatNode", (0, 2))]

    def getInputSocketNames(self):
        return {"List" : "list",
                "Start" : "start",
                "End" : "end"}
                
    def getOutputSocketNames(self):
        return {"Number" : "number"}

    def execute(self, list, start, end):
        listLength = len(list)
        
        if self.autoEnd: end = listLength
        
        minIndex = -listLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), listLength)
        end = min(max(minIndex, end), listLength)
        
        trimList = list[start:end]
        
        op = self.listOperationsProperty
        
        #number = 0.0
        if op == "SUM": number = sum(trimList)
        elif op == "AVERAGE": number = sum(trimList)/len(trimList)
        elif op == "MINIMUM": number = min(trimList)
        elif op == "MAXIMUM": number = max(trimList)
        
        return number
