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
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text")
        self.inputs.new("mn_IntegerSocket", "Start").number = 0
        self.inputs.new("mn_IntegerSocket", "End").number = 5
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        
    def getInputSocketNames(self):
        return {"Text" : "text",
                "Start" : "start",
                "End" : "end"}
                
    def getOutputSocketNames(self):
        return {"Text" : "text"}
        
    def execute(self, text, start, end):
        if self.autoEnd: end = len(text)
        
        start = min(max(0, start), len(text))
        end = min(max(0, end), len(text))
        
        return text[start:end]