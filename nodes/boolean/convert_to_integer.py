import bpy
from ... base_types.node import AnimationNode

class BooleanToIntegerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BooleanToIntegerNode"
    bl_label = "Boolean to Integer"

    def create(self):
        self.newInput("Boolean", "Boolean", "boolean")
        self.newOutput("Integer", "Number", "number")

    def getExecutionCode(self):
        return "number = int(boolean)"
