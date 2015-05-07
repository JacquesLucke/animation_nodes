import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... utils.mn_mesh_utils import *
from mathutils import Matrix

class mn_TransformVertex(Node, AnimationNode):
    bl_idname = "mn_TransformVertex"
    bl_label = "Transform Vertex"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VertexSocket", "Vertex")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VertexSocket", "Vertex")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vertex" : "vertex",
                "Matrix" : "matrix"}
    def getOutputSocketNames(self):
        return {"Vertex" : "vertex"}
        
    def execute(self, vertex, matrix):
        vertex.location = matrix * vertex.location
        return vertex
        
        
