import bpy
from ... base_types.node import AnimationNode

class InvertMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertMatrix"
    bl_label = "Invert Matrix"

    def create(self):
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_MatrixSocket", "Inverted Matrix", "invertedMatrix")

    def draw(self, layout):
        layout.separator()

    def getExecutionCode(self):
        return "invertedMatrix = matrix.inverted(mathutils.Matrix.Identity(4))"

    def getModuleList(self):
        return ["mathutils"]
