import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport createFalloffEvaluator, FalloffEvaluator, Vector3DList
from ... math cimport Vector3, toVector3

class OffsetVectorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetVectorsNode"
    bl_label = "Offset Vectors"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Vector", "Offset", "offset", value = (0, 0, 1))
        self.newInput("Falloff", "Falloff", "falloff")
        self.newOutput("Vector List", "Vector List", "vectors")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Vector3DList vectors, offset, falloff):
        cdef:
            FalloffEvaluator evaluator = createFalloffEvaluator(falloff, "Location")
            Vector3* _vectors = <Vector3*>vectors.base.data
            Vector3 _offset
            double influence
            long i

        toVector3(&_offset, offset)

        if evaluator is None:
            self.errorMessage = "Falloff cannot be evaluated for vectors"
            return vectors

        for i in range(vectors.getLength()):
            influence = evaluator.evaluate(_vectors + i, i)
            _vectors[i].x += _offset.x * influence
            _vectors[i].y += _offset.y * influence
            _vectors[i].z += _offset.z * influence

        return vectors
