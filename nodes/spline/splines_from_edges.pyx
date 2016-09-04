from ... math cimport Vector3
from ... data_structures cimport PolySpline, Vector3DList, EdgeIndicesList

import bpy
from ... base_types import AnimationNode


class SplinesFromEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromEdgesNode"
    bl_label = "Splines from Edges"

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Spline List", "Splines", "splines")

    def execute(self, Vector3DList vertices, EdgeIndicesList edgeIndices):
        if vertices.length == 0 or edgeIndices.length == 0: return []

        cdef long highestIndex = edgeIndices.getMaxIndex()
        if highestIndex >= vertices.length: return []

        cdef:
            long i
            list splines = []
            Vector3DList edgeVertices
            Vector3* _edgeVertices

        for i in range(edgeIndices.length):
            edgeVertices = Vector3DList.__new__(Vector3DList, length = 2)
            edgeVertices.data[0] = vertices.data[edgeIndices.data[i].v1]
            edgeVertices.data[1] = vertices.data[edgeIndices.data[i].v2]
            splines.append(PolySpline.__new__(PolySpline, edgeVertices))

        return splines
