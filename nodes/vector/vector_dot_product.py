import bpy
from ... base_types.node import AnimationNode

class VectorDotProductNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDotProductNode"
    bl_label = "Vector Dot Product"
    
    def create(self):
        self.newInput("an_VectorSocket", "A", "a")
        self.newInput("an_VectorSocket", "B", "b")
        self.newOutput("an_FloatSocket", "Dot Product", "dotProduct")
    
    def getExecutionCode(self):
        return "dotProduct = a.dot(b)"
