import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from . c_utils import calculateEdgeLengths

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
            ("Length", "length"), ("Lengths", "lengths"))

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionFunctionName(self):
        if self.useEdgeList:
            return "execute_List"

    def getExecutionCode(self):
        yield "self.errorMessage = ''"
        yield "try: length = (points[edge[0]] - points[edge[1]]).length"
        yield "except IndexError:"
        yield "    length = 0"
        yield "    self.errorMessage = 'Edge is invalid'"

    def execute_List(self, points, edges):
        self.errorMessage = ""
        try: return calculateEdgeLengths(points, edges)
        except Exception as e: self.errorMessage = str(e)
