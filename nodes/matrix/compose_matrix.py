import bpy
from ... base_types.node import AnimationNode

class ComposeMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "an_ComposeMatrix"
    bl_label = "Compose Matrix"
    isDetermined = True

    inputNames = { "Translation" : "translation",
                   "Rotation" : "rotation",
                   "Scale" : "scale" }

    outputNames = { "Matrix" : "matrix" }

    def create(self):
        self.inputs.new("an_VectorSocket", "Translation")
        self.inputs.new("an_VectorSocket", "Rotation")
        self.inputs.new("an_VectorSocket", "Scale").value = [1, 1, 1]
        self.outputs.new("an_MatrixSocket", "Matrix")

    def getExecutionCode(self):
        return "$matrix$ = animation_nodes.utils.math.composeMatrix(%translation%, %rotation%, %scale%)"
