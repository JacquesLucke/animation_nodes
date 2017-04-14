from ... math cimport Vector3
from ... data_structures cimport PolySpline, Vector3DList, EdgeIndicesList, DoubleList, FloatList

import bpy
from ... base_types import VectorizedNode


class SplinesFromEdgesNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_SplinesFromEdgesNode"
    bl_label = "Splines from Edges"

    useRadiusList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newInput("Vector List", "Vertices", "vertices", dataIsModified = True)
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")

        self.newVectorizedInput("Float", "useRadiusList",
            ("Radius", "radius", dict(value = 0.1, minValue = 0)),
            ("Radii", "radii"))

        self.newOutput("Spline List", "Splines", "splines")

    def execute(self, Vector3DList vertices, EdgeIndicesList edgeIndices, radius):
        if vertices.length == 0 or edgeIndices.length == 0: return []

        cdef long highestIndex = edgeIndices.getMaxIndex()
        if highestIndex >= vertices.length: return []

        cdef:
            long i
            list splines = []
            DoubleList radii = self.prepareRadiusList(radius, len(edgeIndices))
            Vector3DList edgeVertices
            FloatList edgeRadii

        for i in range(edgeIndices.length):
            edgeVertices = Vector3DList.__new__(Vector3DList, length = 2)
            edgeVertices.data[0] = vertices.data[edgeIndices.data[i].v1]
            edgeVertices.data[1] = vertices.data[edgeIndices.data[i].v2]

            edgeRadii = FloatList.__new__(FloatList, length = 2)
            edgeRadii.data[0] = radii.data[i]
            edgeRadii.data[1] = radii.data[i]

            splines.append(PolySpline.__new__(PolySpline, edgeVertices, edgeRadii))

        return splines

    def prepareRadiusList(self, radii, edgeAmount):
        if not isinstance(radii, DoubleList):
            radii = DoubleList.fromValues([radii]) * edgeAmount

        if len(radii) < edgeAmount:
            radii = radii + DoubleList.fromValues([0]) * (edgeAmount - len(radii))
        elif len(radii) > edgeAmount:
            radii = radii[:edgeAmount]
        return radii
