import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_StringLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_StringLengthNode"
    bl_label = "Text Length"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text")
        self.outputs.new("mn_IntegerSocket", "Length")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Text" : "text"}
    def getOutputSocketNames(self):
        return {"Length" : "length"}        
        
    def execute(self, text):
        return len(text)
