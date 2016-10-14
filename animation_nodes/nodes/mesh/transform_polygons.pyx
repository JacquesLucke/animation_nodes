import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList, Matrix4x4List
from ... math cimport transformVec3AsPoint_InPlace, Matrix4

class TransformPolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newInput("Matrix List", "Matrices", "matrices")

        self.newOutput("Vector List", "Vertices", "vertices")

    def execute(self, Vector3DList vertices, PolygonIndicesList polygons, Matrix4x4List matrices):
        cdef:
            Matrix4* matrix
            long i, j
            long start, length
            long index

        for i in range(matrices.length):
            matrix = matrices.data + i
            start = polygons.polyStarts.data[i]
            length = polygons.polyLengths.data[i]
            for j in range(length):
                index = polygons.indices.data[start + j]
                transformVec3AsPoint_InPlace(vertices.data + polygons.indices.data[index], matrix)

        return vertices
