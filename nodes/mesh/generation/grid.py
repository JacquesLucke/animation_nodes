import bpy
from bpy.props import *
from mathutils import Vector
from .... events import executionCodeChanged
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation import grid

class GridMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GridMeshNode"
    bl_label = "Grid Mesh"
    bl_width_default = 160

    centerGrid = BoolProperty(name = "Center", default = True, update = executionCodeChanged)

    def create(self):
        self.newInput("Float", "Length", "length", value = 2)
        self.newInput("Float", "Width", "width", value = 2)
        self.newInput("Integer", "X Divisions", "xDivisions", value = 5, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 5, minValue = 2)
        self.newInput("Vector", "Offset", "offset", isDataModified = True)

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        layout.prop(self, "centerGrid")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        yield "_xDivisions =  max(xDivisions, 2)"
        yield "_yDivisions =  max(yDivisions, 2)"
        if isLinked["vertices"]:
            yield "vertices = self.calcVertices(length, width, _xDivisions, _yDivisions, offset)"
        if isLinked["edgeIndices"]:
            yield "edgeIndices = self.calcEdgeIndices(_xDivisions, _yDivisions)"
        if isLinked["polygonIndices"]:
            yield "polygonIndices = self.calcPolygonIndices(_xDivisions, _yDivisions)"

    def calcVertices(self, length, width, xDivisions, yDivisions, offset):
        if self.centerGrid:
            offset = offset.copy()
            offset.x -= length / 2 if self.centerGrid else 0
            offset.y -= width / 2 if self.centerGrid else 0
        return grid.vertices(length, width, xDivisions, yDivisions, offset)

    def calcEdgeIndices(self, xDivisions, yDivisions):
        return grid.innerQuadEdges(xDivisions, yDivisions)

    def calcPolygonIndices(self, xDivisions, yDivisions):
        return grid.innerQuadPolygons(xDivisions, yDivisions)
