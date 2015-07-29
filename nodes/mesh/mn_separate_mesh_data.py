import bpy, time
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *
from ... mn_cache import *

class mn_SeparateMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SeparateMeshData"
    bl_label = "Separate Mesh Data"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MeshDataSocket", "Mesh Data")
        self.outputs.new("mn_VectorListSocket", "Vertex Locations")
        self.outputs.new("mn_EdgeIndicesListSocket", "Edges Indices")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons Indices")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Mesh Data" : "meshData"}
    def getOutputSocketNames(self):
        return {"Vertex Locations" : "vertexLocations",
                "Edges Indices" : "edgesIndices",
                "Polygons Indices" : "polygonsIndices"}
        
    def execute(self, meshData):
        return meshData.vertices, meshData.edges, meshData.polygons