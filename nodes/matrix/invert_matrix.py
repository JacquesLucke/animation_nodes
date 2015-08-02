import bpy
from ... base_types.node import AnimationNode

class InvertMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_InvertMatrix"
    bl_label = "Invert Matrix"
    isDetermined = True

    inputNames = { "Matrix" : "matrix" }
    outputNames = { "Inverted Matrix" : "matrix" }

    def create(self):
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_MatrixSocket", "Inverted Matrix")

    def draw_buttons(self, context, layout):
        layout.separator()

    def getExecutionCode(self, outputUse):
        return "$matrix$ = %matrix%.inverted(mathutils.Matrix.Identity(4))"

    def getModuleList(self):
        return ["mathutils"]
