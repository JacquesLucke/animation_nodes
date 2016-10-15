import bpy
from bpy.props import *
from ... math cimport Vector3
from libc.string cimport memcpy
from ... base_types.node import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList

class SeparatePolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparatePolygonsNode"
    bl_label = "Separate Polygons"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "inVertices")
        self.newInput("Polygon Indices List", "Polygon Indices", "inPolygonIndices")

        self.newOutput("Vector List", "Vertices", "outVertices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "outPolygonIndices")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, Vector3DList vertices, PolygonIndicesList polygons):
        self.errorMessage = ""
        if len(polygons) == 0 or polygons.getMaxIndex() < len(vertices):
            return separatePolygons(vertices, polygons)
        else:
            self.errorMessage = "Invalid polygon indices"
            return Vector3DList(), PolygonIndicesList()

def separatePolygons(Vector3DList oldVertices, PolygonIndicesList oldPolygons):
    cdef Vector3DList newVertices
    cdef PolygonIndicesList newPolygons

    newVertices = Vector3DList(length = oldPolygons.indices.length)
    newPolygons = PolygonIndicesList(indicesAmount = oldPolygons.indices.length,
                                     polygonAmount = oldPolygons.getLength())

    memcpy(newPolygons.polyStarts.data,
           oldPolygons.polyStarts.data,
           oldPolygons.polyStarts.length * oldPolygons.polyStarts.getElementSize())

    memcpy(newPolygons.polyLengths.data,
           oldPolygons.polyLengths.data,
           oldPolygons.polyLengths.length * oldPolygons.polyLengths.getElementSize())

    cdef:
        long i
        Vector3* _oldVertices = oldVertices.data
        Vector3* _newVertices = newVertices.data
        unsigned int* _oldIndices = oldPolygons.indices.data
        unsigned int* _newIndices = newPolygons.indices.data

    for i in range(oldPolygons.indices.length):
        _newIndices[i] = i
        _newVertices[i] = _oldVertices[_oldIndices[i]]

    return newVertices, newPolygons
