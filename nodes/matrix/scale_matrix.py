import bpy
from ... base_types.node import AnimationNode

class ScaleMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ScaleMatrix"
    bl_label = "Scale Matrix"
    isDetermined = True

    inputNames = { "Scale" : "scale" }
    outputNames = { "Matrix" : "matrix" }

    def create(self):
        self.inputs.new("mn_VectorSocket", "Scale").value = [1, 1, 1]
        self.outputs.new("mn_MatrixSocket", "Matrix")

    def getExecutionCode(self, outputUse):
        return ("$matrix$ ="
                " mathutils.Matrix.Scale(%scale%[0], 4, (1, 0, 0)) * "
                " mathutils.Matrix.Scale(%scale%[1], 4, (0, 1, 0)) * "
                " mathutils.Matrix.Scale(%scale%[2], 4, (0, 0, 1))")

    def getModuleList(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.inputs[0].value = [1, 1, 1]
