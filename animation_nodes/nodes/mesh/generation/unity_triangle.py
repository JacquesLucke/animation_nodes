import bpy
from .... base_types import AnimationNode
from .... data_structures import (
    Mesh,
    LongList,
    Vector3DList,
    EdgeIndicesList,
    PolygonIndicesList,
)

class UnityTriangleMeshNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_UnityTriangleMeshNode"
    bl_label = "Unity Triangle Mesh"

    def create(self):
        self.newOutput("Mesh", "Mesh", "meshData")

    def execute(self):
        return mesh.copy()

vertexLocations = Vector3DList.fromValues([
    (-3**-0.25, -3**-0.75, 0),
    (3**-0.25, -3**-0.75, 0),
    (0, 2/3**0.75, 0)
])
edgeIndices = EdgeIndicesList.fromValues(
    [(0, 1), (1, 2), (2, 0)]
)
polygonIndices = PolygonIndicesList.fromValues(
    [(0, 1, 2)]
)
materialIndices = LongList.fromValues(
    [0]
)
mesh = Mesh(vertexLocations, edgeIndices, polygonIndices, skipValidation = True)
