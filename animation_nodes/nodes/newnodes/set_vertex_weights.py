import bpy
from bpy.props import *
from mathutils import Color
from ... base_types import AnimationNode

groupNotFoundMessage = "Group is not found"
noMeshMessage = "Mesh object required"

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"
    
    errorMessage = StringProperty();
    myLabel = StringProperty(); 
    
    def create(self):
        self.newInput("Object", "Object", "source")
        self.newInput("Integer", "Vertex Group Index", "vertexWeightIndex")
        self.newInput("Float List", "Weights", "weightFloatIn")
        self.newInput("Text", "Mode", "modes")
    
    
    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")
                          
    def execute(self, source, vertexWeightIndex, weightFloatIn, modes):
            self.errorMessage = ""
            
            if source is None:
                self.errorMessage = noMeshMessage
                return

            if source.type is not "MESH":
                self.errorMessage = noMeshMessage
                return

            if len(bpy.data.objects[source.name].vertex_groups) == 0:
                bpy.data.objects[source.name].vertex_groups.new()
            
            vertexWeightGroup = self.getVertexWeightGroup(source, vertexWeightIndex)

            if vertexWeightGroup is None:
                self.errorMessage = groupNotFoundMessage
                return
            
            for i in range(len(weightFloatIn)):
                source.vertex_groups[vertexWeightIndex].add([i], weightFloatIn[i], modes)
                        
                
    def getVertexWeightGroup(self, object, identifier):
        try:return bpy.data.objects[object.name].vertex_groups[identifier]
        except: return None
