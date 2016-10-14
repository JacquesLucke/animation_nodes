import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport Vector3DList, PolygonIndicesList
from libc.string cimport memcpy

class SeparatePolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparatePolygonsNode"
    bl_label = "Separate Polygons"

    def create(self):
        self.newInput("Vector List", "Vertices", "inVertices")
        self.newInput("Polygon Indices List", "Polygon Indices", "inPolygonIndices")

        self.newOutput("Vector List", "Vertices", "outVertices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "outPolygonIndices")

    def execute(self, Vector3DList oldVertices, PolygonIndicesList oldPolygons):
        cdef:
            Vector3DList newVertices
            PolygonIndicesList newPolygons

        newVertices = Vector3DList(length = oldPolygons.indices.length)
        newPolygons = PolygonIndicesList(indicesAmount = oldPolygons.indices.length,
                                         polygonAmount = oldPolygons.getLength())

        memcpy(newPolygons.polyStarts.data,
               oldPolygons.polyStarts.data,
               oldPolygons.polyStarts.length * oldPolygons.polyStarts.getElementSize())

        memcpy(newPolygons.polyLengths.data,
               oldPolygons.polyLengths.data,
               oldPolygons.polyLengths.length * oldPolygons.polyLengths.getElementSize())

        cdef long i
        for i in range(oldPolygons.indices.length):
            newPolygons.indices.data[i] = i
            newVertices.data[i] = oldVertices.data[oldPolygons.indices.data[i]]

        return newVertices, newPolygons
