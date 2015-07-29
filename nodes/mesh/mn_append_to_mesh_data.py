import bpy, bmesh
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *
import bmesh

class mn_AppendToMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_AppendToMeshData"
    bl_label = "Append Mesh Data"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MeshDataSocket", "Mesh Data")
        self.inputs.new("mn_MeshDataSocket", "Other")
        self.outputs.new("mn_MeshDataSocket", "Joined Mesh Data")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Mesh Data" : "meshDataA",
                "Other" : "meshDataB"}
    def getOutputSocketNames(self):
        return {"Joined Mesh Data" : "meshData"}
        
    def execute(self, meshDataA, meshDataB):
        offset = len(meshDataA.vertices)
        
        meshData = meshDataA
        meshData.vertices += meshDataB.vertices
        
        for edge in meshDataB.edges:
            meshData.edges.append((edge[0] + offset, edge[1] + offset))
            
        for poly in meshDataB.polygons:
            meshData.polygons.append(tuple([index + offset for index in poly]))
            
        return meshData