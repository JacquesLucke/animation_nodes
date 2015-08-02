import bpy
from ... base_types.node import AnimationNode

class AppendToMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_AppendToMeshData"
    bl_label = "Append Mesh Data"

    inputNames = { "Mesh Data" : "meshDataA",
                   "Other" : "meshDataB" }

    outputNames = { "Joined Mesh Data" : "joinedMeshData" }            

    def create(self):
        self.inputs.new("mn_MeshDataSocket", "Mesh Data")
        self.inputs.new("mn_MeshDataSocket", "Other")
        self.outputs.new("mn_MeshDataSocket", "Joined Mesh Data")

    def execute(self, meshDataA, meshDataB):
        offset = len(meshDataA.vertices)

        meshData = meshDataA
        meshData.vertices += meshDataB.vertices

        for edge in meshDataB.edges:
            meshData.edges.append((edge[0] + offset, edge[1] + offset))

        for poly in meshDataB.polygons:
            meshData.polygons.append(tuple([index + offset for index in poly]))

        return meshData
