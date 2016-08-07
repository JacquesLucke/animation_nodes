import bpy
from ... data_structures import MeshData
from ... base_types.node import AnimationNode

class JoinMeshDataList(bpy.types.Node, AnimationNode):
    bl_idname = "an_JoinMeshDataList"
    bl_label = "Join Mesh Data List"

    def create(self):
        self.newInput("Mesh Data List", "Mesh Data List", "meshDataList", dataIsModified = True)
        self.newOutput("Mesh Data", "Mesh Data", "meshData")

    def execute(self, meshDataList):
        meshData = MeshData([], [], [])
        offset = 0
        for mesh in meshDataList:
            meshData.vertices.extend(mesh.vertices)
            meshData.edges.extend([(index1 + offset, index2 + offset) for index1, index2 in mesh.edges])
            meshData.polygons.extend([tuple(index + offset for index in poly) for poly in mesh.polygons])
            offset += len(mesh.vertices)
        return meshData
