import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *

class mn_PolygonInfo(Node, AnimationNode):
    bl_idname = "mn_PolygonInfo"
    bl_label = "Polygon Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_PolygonSocket", "Polygon")
        self.outputs.new("mn_VectorSocket", "Center")
        self.outputs.new("mn_VectorSocket", "Normal")
        self.outputs.new("mn_VectorSocket", "Material Index")
        self.outputs.new("mn_FloatSocket", "Area")
        self.outputs.new("mn_VertexListSocket", "Vertices")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Polygon" : "polygon"}
    def getOutputSocketNames(self):
        return {"Center" : "center",
                "Normal" : "normal",
                "Material Index" : "materialIndex",
                "Area" : "area",
                "Vertices" : "vertices"}
        
    def execute(self, polygon):
        return polygon.center, polygon.normal, polygon.materialIndex, polygon.area, polygon.vertices