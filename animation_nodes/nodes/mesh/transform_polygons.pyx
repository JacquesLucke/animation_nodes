import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList, Matrix4x4List
from ... math cimport transformVec3AsPoint_InPlace, Matrix4

class TransformPolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformPolygonsNode"
    bl_label = "Transform Polygons"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newInput("Matrix List", "Matrices", "matrices")

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Vector3DList vertices, PolygonIndicesList polygons, Matrix4x4List matrices):
        self.errorMessage = ""
        if len(polygons) != 0 and polygons.getMaxIndex() >= len(vertices):
            self.errorMessage = "Invalid polygon indices"
            return vertices, polygons
        if len(polygons) != len(matrices):
            self.errorMessage = "Different amount of polygons and matrices"
            return vertices, polygons

        transformPolygons(vertices, polygons, matrices)
        return vertices, polygons

def transformPolygons(Vector3DList vertices, PolygonIndicesList polygons, Matrix4x4List matrices):
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
