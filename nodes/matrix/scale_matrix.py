import bpy
from ... base_types.node import AnimationNode

class ScaleMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ScaleMatrixNode"
    bl_label = "Scale Matrix"

    def create(self):
        self.inputs.new("an_VectorSocket", "Scale", "scale").value = [1, 1, 1]
        self.outputs.new("an_MatrixSocket", "Matrix", "matrix")

    def getExecutionCode(self):
        return ("matrix ="
                " mathutils.Matrix.Scale(scale[0], 4, (1, 0, 0)) * "
                " mathutils.Matrix.Scale(scale[1], 4, (0, 1, 0)) * "
                " mathutils.Matrix.Scale(scale[2], 4, (0, 0, 1))")

    def getModuleList(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.inputs[0].value = [1, 1, 1]
