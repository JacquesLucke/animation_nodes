import bpy
from ... base_types.node import AnimationNode


class TranslationMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TranslationMatrix"
    bl_label = "Translation Matrix"
    isDetermined = True

    inputNames = { "Translation" : "translation" }
    outputNames = { "Matrix" : "matrix" }

    def create(self):
        self.inputs.new("mn_VectorSocket", "Translation")
        self.outputs.new("mn_MatrixSocket", "Matrix")

    def getExecutionCode(self):
        return "$matrix$ = mathutils.Matrix.Translation(%translation%)"

    def getModuleList(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.inputs[0].value = [0, 0, 0]
