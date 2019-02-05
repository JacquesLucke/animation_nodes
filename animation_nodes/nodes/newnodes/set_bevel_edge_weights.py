import bpy
from bpy.props import *
from ... base_types import AnimationNode

noMeshMessage = "Mesh object required"

class BevelEdgeWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelEdgeWeights"
    bl_label = "Set Bevel Edge Weights"
    
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
                source.data.edges[i].bevel_weight = weightFloatIn[i] 

