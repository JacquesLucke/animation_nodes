import bpy
from ... base_types.node import AnimationNode

class CombineVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVectorNode"
    bl_label = "Combine Vector"
    dynamicLabelType = "HIDDEN_ONLY"

    def create(self):
        self.newInput("an_FloatSocket", "X", "x")
        self.newInput("an_FloatSocket", "Y", "y")
        self.newInput("an_FloatSocket", "Z", "z")
        self.newOutput("an_VectorSocket", "Vector", "vector")

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
