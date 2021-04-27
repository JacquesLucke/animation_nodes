import bpy
from .... base_types import AnimationNode
from .. c_utils import generateHexagonGrid, replicateMesh
from .... data_structures import (
    Mesh,
    Vector3DList,
    EdgeIndicesList,
    PolygonIndicesList,
)

class HexagonGridNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_HexagonGridNode"
    bl_label = "Hexagon Grid"

    def create(self):
        self.newInput("Integer", "X Divisions", "xDivisions", value = 6, minValue = 1)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 6, minValue = 1)
        self.newInput("Float", "Radius", "radius", value = 1)

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, xDivisions, yDivisions, radius):
        mesh = hexagonMesh(radius)
        grid = generateHexagonGrid(xDivisions, yDivisions, radius)
        return replicateMesh(mesh, grid)

def hexagonMesh(radius):
    val1 = radius * 0.5
    val2 = radius * 0.866
    vertexLocations = Vector3DList.fromValues([
            (radius, 0, 0), (val1, val2, 0), (-val1, val2, 0),
            (-radius, 0, 0), (-val1, -val2, 0), (val1, -val2, 0)
    ])
    edgeIndices = EdgeIndicesList.fromValues([
        (0, 5), (4, 5), (3, 4),
        (0, 1), (2, 3), (1, 2)
    ])
    polygonIndices = PolygonIndicesList.fromValues([(0, 1, 2, 3, 4, 5)])

    return Mesh(vertexLocations, edgeIndices, polygonIndices, skipValidation = True)
