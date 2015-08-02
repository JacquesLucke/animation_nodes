import bpy
import operator
import functools
from mathutils import Matrix
from ... base_types.node import AnimationNode

class MatrixCombine(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MatrixCombine"
    bl_label = "Combine Matrices"
    isDetermined = True

    inputNames = { "Matrices" : "matrices" }
    outputNames = { "Result" : "result" }

    def create(self):
        self.inputs.new("mn_MatrixListSocket", "Matrices")
        self.outputs.new("mn_MatrixSocket", "Result")

    def execute(self, matrices):
        return functools.reduce(operator.mul, reversed(matrices), Matrix.Identity(4))
