import bpy
from ... base_types.node import AnimationNode

from ... math.conversion cimport toMatrix4
from ... math.ctypes cimport Matrix4, Vector3
from ... math.base_operations cimport transformVec3
from ... data_structures.lists.complex_lists cimport Vector3DList

class TransformVectorListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorListNode"
    bl_label = "Transform Vector List"

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector List", "Vectors List", "vectors")

    def execute(self, Vector3DList vectors, matrix):
        cdef Matrix4 mat
        toMatrix4(&mat, matrix)

        cdef long i
        cdef Vector3* v = <Vector3*>vectors.base.data
        for i in range(len(vectors)):
            transformVec3(v+i, v+i, &mat)
        return vectors
