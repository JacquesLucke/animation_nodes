import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TrimText(Node, AnimationNode):
    bl_idname = "mn_TrimText"
    bl_label = "Trim Text"
    
    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        nodePropertyChanged(self, context)
    
    autoEnd = bpy.props.BoolProperty(default = False, description = "Use the length of the text as trim-end", update = settingChanged)
    allowNegativeIndex = bpy.props.BoolProperty(default = False, description = "Negative indices start from the end")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text")
        self.inputs.new("mn_IntegerSocket", "Start").number = 0
        self.inputs.new("mn_IntegerSocket", "End").number = 5
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Indices")
        
    def getInputSocketNames(self):
        return {"Text" : "text",
                "Start" : "start",
                "End" : "end"}
                
    def getOutputSocketNames(self):
        return {"Text" : "text"}
        
    def execute(self, text, start, end):
        textLength = len(text)
    
        if self.autoEnd: end = textLength
        
        minIndex = -textLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), textLength)
        end = min(max(minIndex, end), textLength)
        
        return text[start:end]