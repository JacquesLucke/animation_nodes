import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport createFalloffEvaluator, FalloffEvaluator, Vector3DList
from ... math cimport Vector3

class TestEvaluatorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TestEvaluatorNode"
    bl_label = "Test Evaluator"

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newOutput("Vector List", "Vector List", "vectors")

    def execute(self, Vector3DList vectors, falloff):
        cdef:
            FalloffEvaluator evaluator = createFalloffEvaluator(falloff, "Location")
            Vector3* _vectors = <Vector3*>vectors.base.data
            long i
            double influence

        if evaluator is not None:
            for i in range(vectors.getLength()):
                influence = evaluator.evaluate(_vectors + i, i)
                _vectors[i].z += influence * 5

        return vectors
