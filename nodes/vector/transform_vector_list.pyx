import bpy
from ... base_types.node import AnimationNode
from ... utils.cmath cimport *
from ... data_structures.lists.complex_lists cimport Vector3DList

class TransformVectorListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorListNode"
    bl_label = "Transform Vector List"

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector List", "Vectors List", "vectors")

    def execute(self, Vector3DList vectors, matrix):
        cdef Matrix4_t m
        applyMatrix(&m, matrix)

        cdef long i
        cdef Vector3_t* v = <Vector3_t*>vectors.base.data
        for i in range(len(vectors)):
            transformVec3(v+i, v+i, &m)
        return vectors
