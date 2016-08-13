from ... math cimport Vector3
from ... data_structures cimport PolySpline, Vector3DList, EdgeIndicesList

import bpy
from ... base_types.node import AnimationNode


class SplinesFromEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromEdgesNode"
    bl_label = "Splines from Edges"

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Spline List", "Splines", "splines")

    def execute(self, Vector3DList vertices, EdgeIndicesList edgeIndices):
        if vertices.getLength() == 0 or edgeIndices.getLength() == 0: return []

        cdef long highestIndex = edgeIndices.base.getMaxValue()
        if highestIndex >= vertices.getLength(): return []

        cdef:
            long i
            list splines = []
            Vector3DList edgeVertices
            Vector3* _vertices = <Vector3*>vertices.base.data
            Vector3* _edgeVertices

        for i in range(edgeIndices.getLength()):
            edgeVertices = Vector3DList.__new__(Vector3DList, length = 2)
            _edgeVertices = <Vector3*>edgeVertices.base.data
            _edgeVertices[0] = _vertices[edgeIndices.base.data[2 * i + 0]]
            _edgeVertices[1] = _vertices[edgeIndices.base.data[2 * i + 1]]
            splines.append(PolySpline.__new__(PolySpline, edgeVertices))

        return splines
