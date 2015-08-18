import bpy
from ... base_types.node import AnimationNode

class AppendToMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendToMeshData"
    bl_label = "Append Mesh Data"         

    def create(self):
        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshDataA")
        self.inputs.new("an_MeshDataSocket", "Other", "meshDataB")
        self.outputs.new("an_MeshDataSocket", "Joined Mesh Data", "joinedMeshData")

    def execute(self, meshDataA, meshDataB):
        offset = len(meshDataA.vertices)

        meshData = meshDataA
        meshData.vertices += meshDataB.vertices

        for edge in meshDataB.edges:
            meshData.edges.append((edge[0] + offset, edge[1] + offset))

        for poly in meshDataB.polygons:
            meshData.polygons.append(tuple([index + offset for index in poly]))

        return meshData
