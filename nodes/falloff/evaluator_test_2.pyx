import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport getFalloffEvaluator, FalloffEvaluator, Matrix4x4List
from ... math cimport Matrix4

class TestEvaluator2Node(bpy.types.Node, AnimationNode):
    bl_idname = "an_TestEvaluator2Node"
    bl_label = "Test Evaluator 2"

    def create(self):
        self.newInput("Matrix List", "Matrix List", "matrices", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newOutput("Matrix List", "Matrix List", "matrices")

    def execute(self, Matrix4x4List matrices, falloff):
        cdef:
            FalloffEvaluator evaluator = getFalloffEvaluator(falloff, "Transformation Matrix")
            Matrix4* _matrices = <Matrix4*>matrices.base.data
            long i
            double influence

        if evaluator is not None:
            for i in range(matrices.getLength()):
                influence = evaluator.evaluate(_matrices + i, i)
                _matrices[i].a34 += influence

        return matrices
