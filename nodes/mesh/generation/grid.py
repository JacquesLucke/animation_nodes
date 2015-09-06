import bpy
from bpy.props import *
from mathutils import Vector
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation.indices_utils import gridQuadPolygonIndices, gridQuadEdgeIndices
from .... algorithms.mesh_generation.basic_shapes import gridVertices
from .... events import executionCodeChanged

class GridMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GridMeshNode"
    bl_label = "Grid Mesh"

    centerGrid = BoolProperty(name = "Center", default = True, update = executionCodeChanged)

    def create(self):
        self.width = 160
        divisionSockets = [
            self.inputs.new("an_IntegerSocket", "X Divisions", "xDivisions"),
            self.inputs.new("an_IntegerSocket", "Y Divisions", "yDivisions") ]
        for socket in divisionSockets:
            socket.value = 5
            socket.setMinMax(2, 10000000)
        self.inputs.new("an_FloatSocket", "X Distance", "xDistance").value = 1
        self.inputs.new("an_FloatSocket", "Y Distance", "yDistance").value = 1
        self.inputs.new("an_VectorSocket", "Offset", "offset").isDataModified = True
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        layout.prop(self, "centerGrid")

    def execute(self, xDivisions, yDivisions, xDistance, yDistance, offset):
        xDivisions = max(xDivisions, 2)
        yDivisions = max(yDivisions, 2)
        offset = offset.copy()
        offset.x -= (xDivisions - 1) * xDistance / 2 if self.centerGrid else 0
        offset.y -= (yDivisions - 1) * yDistance / 2 if self.centerGrid else 0

        vertices = gridVertices(xDivisions, yDivisions, xDistance, yDistance, offset) if self.outputs[0].isLinked else []
        edgeIndices = gridQuadEdgeIndices(xDivisions, yDivisions) if self.outputs[1].isLinked else []
        polygonIndices = gridQuadPolygonIndices(xDivisions, yDivisions) if self.outputs[2].isLinked else []

        return vertices, edgeIndices, polygonIndices
