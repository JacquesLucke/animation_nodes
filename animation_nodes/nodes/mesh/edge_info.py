import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from . c_utils import calculateEdgeLengths, calculateEdgeCenters

class EdgeInfoNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_EdgeInfoNode"
    bl_label = "Edge Info"

    useEdgeList = VectorizedNode.newVectorizeProperty()
    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "Points", "points")

        self.newVectorizedInput("Edge Indices", "useEdgeList",
            ("Edge Indices", "edgeIndices"),
            ("Edge Indices List", "edgeIndicesList"))

        self.newVectorizedOutput("Float", "useEdgeList",
            ("Length", "length"),
            ("Lengths", "lengths"))

        self.newVectorizedOutput("Vector", "useEdgeList",
            ("Center", "center"),
            ("Centers", "centers"))

    def draw(self, layout):
        if self.errorMessage != "" and self.inputs[1].isLinked:
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        yield "self.errorMessage = ''"
        if self.useEdgeList:
            yield from self.iterExecutionCode_List(isLinked)
        else:
            yield from self.iterExecutionCode_Single(isLinked)

    def iterExecutionCode_Single(self, isLinked):
        yield "try:"
        yield "    i1, i2 = edgeIndices"
        if isLinked["length"]: yield "    length = (points[i1] - points[i2]).length"
        if isLinked["center"]: yield "    center = (points[i1] + points[i2]) / 2"
        yield "except IndexError:"
        yield "    self.errorMessage = 'invalid edge'"
        yield "    length, center = Vector((0, 0, 0)), Vector((0, 0, 0))"

    def iterExecutionCode_List(self, isLinked):
        yield "try:"
        if isLinked["lengths"]: yield "    lengths = self.calculateEdgeLengths(points, edgeIndicesList)"
        if isLinked["centers"]: yield "    centers = self.calculateEdgeCenters(points, edgeIndicesList)"
        yield "    pass"
        yield "except IndexError:"
        yield "    self.errorMessage = 'invalid edges'"
        yield "    lengths, centers = DoubleList(), Vector3DList()"

    def calculateEdgeLengths(self, points, edges):
        return calculateEdgeLengths(points, edges)

    def calculateEdgeCenters(self, points, edges):
        return calculateEdgeCenters(points, edges)
