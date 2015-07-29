import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *

class mn_VertexInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VertexInfo"
    bl_label = "Vertex Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VertexSocket", "Vertex")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Normal")
        self.outputs.new("mn_FloatListSocket", "Group Weights")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vertex" : "vertex"}
    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Normal" : "normal",
                "Group Weights" : "groupWeights"}
        
    def execute(self, vertex):
        return vertex.location, vertex.normal, vertex.groupWeights