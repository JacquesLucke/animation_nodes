import bpy
from ... base_types.node import AnimationNode

class BooleanInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_BooleanInputNode"
    bl_label = "Boolean Input"
    isDetermined = True
    
    def create(self):
        self.inputs.new("mn_BooleanSocket", "Boolean")
        self.outputs.new("mn_BooleanSocket", "Boolean")
        
    def getInputSocketNames(self):
        return {"Boolean" : "boolean"}
    def getOutputSocketNames(self):
        return {"Boolean" : "boolean"}
        
    def execute(self, boolean):
        return boolean
