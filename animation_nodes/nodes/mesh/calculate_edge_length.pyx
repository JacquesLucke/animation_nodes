import bpy
from bpy.props import *
from ... math cimport Vector3, distanceVec3
from ... base_types import VectorizedNode
from ... data_structures cimport Vector3DList, EdgeIndicesList, DoubleList

class CalculateEdgeLengthNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_CalculateEdgeLengthNode"
    bl_label = "Calculate Edge Length"
    bl_width_default = 160

    errorMessage = StringProperty()
    useEdgeList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newInput("Vector List", "Points", "points")

        self.newVectorizedInput("Edge Indices", "useEdgeList",
            ("Edge", "edge"), ("Edges", "edges"))

        self.newVectorizedOutput("Float", "useEdgeList",
            ("Distance", "distance"), ("Distances", "distances"))

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionFunctionName(self):
        if self.useEdgeList:
            return "execute_List"

    def getExecutionCode(self):
        yield "self.errorMessage = ''"
        yield "try: distance = (points[edge[0]] - points[edge[1]]).length"
        yield "except IndexError:"
        yield "    distance = 0"
        yield "    self.errorMessage = 'Edge is invalid'"

    def execute_List(self, Vector3DList points, EdgeIndicesList edges):
        self.errorMessage = ""
        if len(edges) == 0:
            return DoubleList()

        if edges.getMaxIndex() >= len(points):
            self.errorMessage = "too high index"
            return DoubleList()

        cdef DoubleList distances = DoubleList(length = len(edges))
        cdef Py_ssize_t i
        cdef Vector3 *v1
        cdef Vector3 *v2
        for i in range(len(edges)):
            v1 = points.data + edges.data[i].v1
            v2 = points.data + edges.data[i].v2
            distances.data[i] = distanceVec3(v1, v2)
        return distances
