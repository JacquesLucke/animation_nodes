import bpy
from ... base_types.node import AnimationNode

class InvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_InvertNode"
    bl_label = "Invert Boolean"
    
    inputNames = { "Input" : "input" }
    outputNames = { "Output" : "output" }
    
    def create(self):
        self.inputs.new("mn_BooleanSocket", "Input")
        self.outputs.new("mn_BooleanSocket", "Output")
        
    def getExecutionCode(self):
        return "$output$ = not %input%"