import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

vertexModeTypeItems = [
    ("ADD_MODE", "ADD", "", "NONE", 0),
    ("SUBTRACT_MODE", "SUBTRACT", "", "NONE", 1),
    ("REPLACE_MODE", "REPLACE", "", "NONE", 2)    
]

class VertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexWeights"
    bl_label = "Set Vertex Weights"

    useFloatList: VectorizedSocket.newProperty()
 
    vertexModeType: EnumProperty(name = "Vertex Weight Mode Type", default = "REPLACE_MODE",
        items = vertexModeTypeItems, update = AnimationNode.refresh)
    
    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Integer", "Vertex Group Index", "vertexWeightIndex")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))
        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "vertexModeType", text = "")

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
        if self.vertexModeType == "REPLACE_MODE":
            modes = "REPLACE"
        elif self.vertexModeType == "ADD_MODE":
            modes = "ADD"
        elif self.vertexModeType == "SUBTRACT_MODE":
            modes = "SUBTRACT"
        indices = list(range(0, len(object.data.vertices)))
        object.vertex_groups[vertexWeightIndex].add(indices, weight, modes)
        object.data.update()    
        return object

    def executeList(self, object, vertexWeightIndex, weights):
        if object is None or object.type != "MESH" or object.mode == "EDIT": return
        if len(bpy.data.objects[object.name].vertex_groups) == 0:
            bpy.data.objects[object.name].vertex_groups.new()
        vertexWeightGroup = self.getVertexWeightGroup(object, vertexWeightIndex)
        if vertexWeightGroup is None: return
        if self.vertexModeType == "REPLACE_MODE":
            modes = "REPLACE"
        elif self.vertexModeType == "ADD_MODE":
            modes = "ADD"
        elif self.vertexModeType == "SUBTRACT_MODE":
            modes = "SUBTRACT"
        totalVertices = len(object.data.vertices)    
        for i, weight in enumerate(weights):
            if i >= totalVertices: return  
            object.vertex_groups[vertexWeightIndex].add([i], weight, modes)
        object.data.update()
        return object            
     
    def getVertexWeightGroup(self, object, identifier):
        try:return bpy.data.objects[object.name].vertex_groups[identifier]
        except: return None