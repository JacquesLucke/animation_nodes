import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures cimport PolygonIndicesList, LongLongList

class PolygonIndicesListFromLengthsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonIndicesListFromLengthsNode"
    bl_label = "Polygon Indices List from Lengths"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Integer List", "Polygon Lengths", "polygonLengths", dataIsModified = True)
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, LongLongList polygonLengths):
        self.errorMessage = ""
        cdef:
            cdef long i, polyLength, currentStart
            long totalLength = polygonLengths.getSumOfElements()
            long polygonAmount = len(polygonLengths)
            PolygonIndicesList polygonIndices

        polygonIndices = PolygonIndicesList(
            indicesAmount = totalLength,
            polygonAmount = polygonAmount)

        for i in range(totalLength):
            polygonIndices.indices.data[i] = i

        currentStart = 0
        for i in range(polygonAmount):
            polyLength = polygonLengths.data[i]
            if polyLength >= 3:
                polygonIndices.polyStarts.data[i] = currentStart
                polygonIndices.polyLengths.data[i] = polyLength
                currentStart += polyLength
            else:
                self.errorMessage = "Lengths must be >= 3"
                return PolygonIndicesList()

        return polygonIndices
