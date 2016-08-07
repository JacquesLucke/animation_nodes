import bpy
from bpy.props import *
from mathutils import Vector
from .... events import executionCodeChanged
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation.basic_shapes import gridVertices
from .... algorithms.mesh_generation.indices_utils import GridMeshIndices

class GridMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GridMeshNode"
    bl_label = "Grid Mesh"
    bl_width_default = 160

    centerGrid = BoolProperty(name = "Center", default = True, update = executionCodeChanged)

    def create(self):
        self.newInput("Integer", "X Divisions", "xDivisions", value = 5, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 5, minValue = 2)
        self.newInput("Float", "X Distance", "xDistance", value = 1)
        self.newInput("Float", "Y Distance", "yDistance", value = 1)
        self.newInput("Vector", "Offset", "offset", isDataModified = True)

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        layout.prop(self, "centerGrid")

    def execute(self, xDivisions, yDivisions, xDistance, yDistance, offset):
        xDivisions = max(xDivisions, 2)
        yDivisions = max(yDivisions, 2)
        offset = offset.copy()
        offset.x -= (xDivisions - 1) * xDistance / 2 if self.centerGrid else 0
        offset.y -= (yDivisions - 1) * yDistance / 2 if self.centerGrid else 0

        vertices = gridVertices(xDivisions, yDivisions, xDistance, yDistance, offset) if self.outputs[0].isLinked else []
        edgeIndices = GridMeshIndices.innerQuadEdges(xDivisions, yDivisions) if self.outputs[1].isLinked else []
        polygonIndices = GridMeshIndices.innerQuadPolygons(xDivisions, yDivisions) if self.outputs[2].isLinked else []

        return vertices, edgeIndices, polygonIndices
