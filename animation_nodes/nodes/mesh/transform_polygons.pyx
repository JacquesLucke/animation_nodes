import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... math cimport transformVec3AsPoint_InPlace, Matrix4, Vector3
from ... data_structures cimport Vector3DList, PolygonIndicesList, Matrix4x4List

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
        Matrix4* _matrices = matrices.data
        Matrix4* matrix
        long i, j
        long start, length
        Vector3* _vertices = vertices.data
        unsigned int* _polyStarts = polygons.polyStarts.data
        unsigned int* _polyLengths = polygons.polyLengths.data
        unsigned int* _indices = polygons.indices.data

    for i in range(matrices.length):
        matrix = _matrices + i
        start = _polyStarts[i]
        length = _polyLengths[i]
        for j in range(length):
            transformVec3AsPoint_InPlace(_vertices + _indices[start + j], matrix)
