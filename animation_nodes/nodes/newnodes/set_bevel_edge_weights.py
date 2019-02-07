import bpy
from ... base_types import AnimationNode

class BevelEdgeWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelEdgeWeights"
    bl_label = "Set Bevel Edge Weights"

    def create(self):
        self.newInput("Object", "Object", "source")
        self.newInput("Float List", "Weights", "weightFloatIn")

    def execute(self, source, weightFloatIn):
            if source is None or source.type != "MESH" or source.mode != "OBJECT":
                return

            for i in range(len(weightFloatIn)):
                source.data.edges[i].bevel_weight = weightFloatIn[i] 

            source.data.update()
