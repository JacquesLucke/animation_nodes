import bpy
from ... base_types.node import AnimationNode

class SeparateQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateQuaternionNode"
    bl_label = "Separate Quaternion"

    def create(self):
        self.newInput("an_QuaternionSocket", "Quaternion", "quaternion")
        self.newOutput("an_FloatSocket", "W", "w")
        self.newOutput("an_FloatSocket", "X", "x")
        self.newOutput("an_FloatSocket", "Y", "y")
        self.newOutput("an_FloatSocket", "Z", "z")
        
    def getExecutionCode(self):
        return "w, x, y, z = quaternion"
