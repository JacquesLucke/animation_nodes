import bpy
from ... base_types import AnimationNode, VectorizedSocket

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"

    useFloatList: VectorizedSocket.newProperty()
 
    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Integer", "Vertex Group Index", "vertexWeightIndex")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))
        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useFloatList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, vertexWeightIndex, weight):
        if object is None or object.type != "MESH" or object.mode == "EDIT": return
        if len(bpy.data.objects[object.name].vertex_groups) == 0:
            bpy.data.objects[object.name].vertex_groups.new()
        vertexWeightGroup = self.getVertexWeightGroup(object, vertexWeightIndex)
        if vertexWeightGroup is None: return
        indices = list(range(0, len(object.data.vertices)))
        object.vertex_groups[vertexWeightIndex].add(indices, weight, "REPLACE")
        object.data.update()    
        return object

    def executeList(self, object, vertexWeightIndex, weights):
        if object is None or object.type != "MESH" or object.mode == "EDIT": return
        if len(bpy.data.objects[object.name].vertex_groups) == 0:
            bpy.data.objects[object.name].vertex_groups.new()
        vertexWeightGroup = self.getVertexWeightGroup(object, vertexWeightIndex)
        if vertexWeightGroup is None: return
        totalVertices = len(object.data.vertices)    
        for i, weight in enumerate(weights):
            if i >= totalVertices: return  
            object.vertex_groups[vertexWeightIndex].add([i], weight, "REPLACE")
        object.data.update()
        return object            
     
    def getVertexWeightGroup(self, object, identifier):
        try:return bpy.data.objects[object.name].vertex_groups[identifier]
        except: return None