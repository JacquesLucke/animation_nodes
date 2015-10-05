import bpy
from ... base_types.node import AnimationNode

class BooleanToIntegerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BooleanToIntegerNode"
    bl_label = "Boolean to Integer"

    def create(self):
        self.inputs.new("an_BooleanSocket", "Boolean", "boolean")
        self.outputs.new("an_IntegerSocket", "Number", "number")

    def getExecutionCode(self):
        return "number = int(boolean)"
