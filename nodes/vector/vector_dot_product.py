import bpy
from ... base_types.node import AnimationNode

class VectorDotProductNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDotProductNode"
    bl_label = "Vector Dot Product"
    
    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        self.outputs.new("an_FloatSocket", "Dot Product", "dotProduct")
    
    def getExecutionCode(self):
        return "dotProduct = a.dot(b)"
