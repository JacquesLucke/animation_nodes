import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class EulerFromVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EulerFromVectorNode"
    bl_label = "Euler from Vector"

    useDegree = BoolProperty(name = "Use Degree", default = False,
        update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector", "vector")
        self.outputs.new("an_EulerSocket", "Euler", "euler")

    def draw(self, layout):
        layout.prop(self, "useDegree")

    def getExecutionCode(self):
        if self.useDegree:
            return "euler = mathutils.Euler(vector / 180 * math.pi, 'XYZ')"
        else:
            return "euler = mathutils.Euler(vector, 'XYZ')"

    def getUsedModules(self):
        return ["mathutils", "math"]
