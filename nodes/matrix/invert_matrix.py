import bpy
from ... base_types.node import AnimationNode

class InvertMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertMatrixNode"
    bl_label = "Invert Matrix"

    def create(self):
        self.newInput("an_MatrixSocket", "Matrix", "matrix")
        self.newOutput("an_MatrixSocket", "Inverted Matrix", "invertedMatrix")

    def draw(self, layout):
        layout.separator()

    def getExecutionCode(self):
        return "invertedMatrix = matrix.inverted(mathutils.Matrix.Identity(4))"

    def getUsedModules(self):
        return ["mathutils"]
