import bpy
from ... base_types.node import AnimationNode

class CombineVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVectorNode"
    bl_label = "Combine Vector"

    def create(self):
        self.inputs.new("an_FloatSocket", "X", "x")
        self.inputs.new("an_FloatSocket", "Y", "y")
        self.inputs.new("an_FloatSocket", "Z", "z")
        self.outputs.new("an_VectorSocket", "Vector", "vector")

    def drawLabel(self):
        label = "<X, Y, Z>"
        for axis in "XYZ":
            if self.inputs[axis].isUnlinked:
                label = label.replace(axis, str(round(self.inputs[axis].value, 4)))
        return label

    def getExecutionCode(self):
        return "vector = mathutils.Vector((x, y, z))"

    def getUsedModules(self):
        return ["mathutils"]
