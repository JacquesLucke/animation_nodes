import bpy
from ... base_types.node import AnimationNode

class ComposeMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrixNode"
    bl_label = "Compose Matrix"

    def create(self):
        self.newInput("an_VectorSocket", "Translation", "translation")
        self.newInput("an_EulerSocket", "Rotation", "rotation")
        self.newInput("an_VectorSocket", "Scale", "scale").value = [1, 1, 1]
        self.newOutput("an_MatrixSocket", "Matrix", "matrix")

    def getExecutionCode(self):
        return "matrix = animation_nodes.utils.math.composeMatrix(translation, rotation, scale)"
