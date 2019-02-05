import bpy
from bpy.props import *
from ... base_types import AnimationNode

noMeshMessage = "Mesh object required"

class BevelVertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelVertexWeights"
    bl_label = "Set Bevel Vertex Weights"
    
    errorMessage = StringProperty();
    myLabel = StringProperty(); 
    
    def create(self):
        self.newInput("Object", "Object", "source")
        self.newInput("Float List", "Weights", "weightFloatIn")
    
    
    def draw(self, layout):
        #layout.prop(self,,text)
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")
                          
    def execute(self, source, weightFloatIn):
            self.errorMessage = ""
            
            if source is None:
                self.errorMessage = noMeshMessage
                return

            if source.type != "MESH":
                self.errorMessage = noMeshMessage
                return

            for i in range(len(weightFloatIn)):
                source.data.vertices[i].bevel_weight = weightFloatIn[i] 

