import bpy
from ... base_types import AnimationNode

class CombineVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVectorNode"
    bl_label = "Combine Vector"
    dynamicLabelType = "HIDDEN_ONLY"

    def create(self):
        self.newInput("Float", "X", "x")
        self.newInput("Float", "Y", "y")
        self.newInput("Float", "Z", "z")
        self.newOutput("Vector", "Vector", "vector")

    def drawLabel(self):
        label = "<X, Y, Z>"
        for axis in "XYZ":
            if self.inputs[axis].isUnlinked:
                label = label.replace(axis, str(round(self.inputs[axis].value, 4)))
        return label

    def getExecutionCode(self):
        return "vector = Vector((x, y, z))"
