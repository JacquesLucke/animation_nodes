import bpy
from ... base_types import AnimationNode, VectorizedSocket

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"

    useFloatList: VectorizedSocket.newProperty()
    
    def create(self):
        self.newInput("Object", "Object", "object")
        self.newInput("Integer", "Vertex Group Index", "vertexWeightIndex")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))
        self.newInput("Text", "Mode", "modes")

    def getExecutionFunctionName(self):
        if self.useFloatList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, vertexWeightIndex, weight, modes):
        if object is None or object.type != "MESH" or object.mode == "EDIT": return
        if len(bpy.data.objects[object.name].vertex_groups) == 0:
            bpy.data.objects[object.name].vertex_groups.new()
        vertexWeightGroup = self.getVertexWeightGroup(object, vertexWeightIndex)
        if vertexWeightGroup is None: return
        for i in range(len(object.data.vertices)):
            object.vertex_groups[vertexWeightIndex].add([i], weight, modes)
        object.data.update()    

    def executeList(self, object, vertexWeightIndex, weights, modes):
        if object is None or object.type != "MESH" or object.mode == "EDIT": return
        if len(bpy.data.objects[object.name].vertex_groups) == 0:
            bpy.data.objects[object.name].vertex_groups.new()
        vertexWeightGroup = self.getVertexWeightGroup(object, vertexWeightIndex)
        if vertexWeightGroup is None: return
        for i in range(len(weights)):
            if i >= len(object.data.vertices): return  
            object.vertex_groups[vertexWeightIndex].add([i], weights[i], modes)
        object.data.update()
     
    def getVertexWeightGroup(self, object, identifier):
        try:return bpy.data.objects[object.name].vertex_groups[identifier]
        except: return None
