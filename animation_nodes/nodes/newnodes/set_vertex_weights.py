import bpy
from ... base_types import AnimationNode

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"
    
    def create(self):
        self.newInput("Object", "Object", "source")
        self.newInput("Integer", "Vertex Group Index", "vertexWeightIndex")
        self.newInput("Float List", "Weights", "weightFloatIn")
        self.newInput("Text", "Mode", "modes")
                          
    def execute(self, source, vertexWeightIndex, weightFloatIn, modes):
            if source is None or source.type != "MESH" or source.mode == "EDIT":
                return

            if len(bpy.data.objects[source.name].vertex_groups) == 0:
                bpy.data.objects[source.name].vertex_groups.new()
            
            vertexWeightGroup = self.getVertexWeightGroup(source, vertexWeightIndex)

            if vertexWeightGroup is None:
                return
            
            for i in range(len(weightFloatIn)):
                source.vertex_groups[vertexWeightIndex].add([i], weightFloatIn[i], modes)

            source.data.update()    

    def getVertexWeightGroup(self, object, identifier):
        try:return bpy.data.objects[object.name].vertex_groups[identifier]
        except: return None
