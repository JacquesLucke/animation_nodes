import bpy
from ... base_types import AnimationNode

class ComposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrixNode"
    bl_label = "Compose Matrix"

    def create(self):
        self.newInput("Vector", "Translation", "translation")
        self.newInput("Euler", "Rotation", "rotation")
        self.newInput("Vector", "Scale", "scale", value = [1, 1, 1])
        self.newOutput("Matrix", "Matrix", "matrix")

    def getExecutionCode(self):
        return "matrix = animation_nodes.utils.math.composeMatrix(translation, rotation, scale)"
