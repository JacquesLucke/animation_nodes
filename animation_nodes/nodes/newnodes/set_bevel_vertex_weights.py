import bpy
from ... base_types import AnimationNode

class BevelVertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelVertexWeights"
    bl_label = "Set Bevel Vertex Weights"
    
    def create(self):
        self.newInput("Object", "Object", "source")
        self.newInput("Float List", "Weights", "weightFloatIn")
                          
    def execute(self, source, weightFloatIn):
            if source is None or source.type != "MESH" or source.mode != "OBJECT":
                return

            for i in range(len(weightFloatIn)):
                source.data.vertices[i].bevel_weight = weightFloatIn[i] 

            source.data.update()
