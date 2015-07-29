import bpy
from ... base_types.node import AnimationNode

class InvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_InvertNode"
    bl_label = "Invert Boolean"
    
    def create(self):
        self.inputs.new("mn_BooleanSocket", "Input")
        self.outputs.new("mn_BooleanSocket", "Output")
        
    def getInputSocketNames(self):
        return {"Input" : "input"}
        
    def getOutputSocketNames(self):
        return {"Output" : "output"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$output$ = not %input%"
