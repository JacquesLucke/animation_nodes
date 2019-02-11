import bpy
from ... base_types import AnimationNode, VectorizedSocket

class BevelVertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelVertexWeights"
    bl_label = "Set Bevel Vertex Weights"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))

    def getExecutionFunctionName(self):
        if self.useFloatList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, weight):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True
        for i in range(len(object.data.vertices)):
            object.data.vertices[i].bevel_weight = weight 
        object.data.update()

    def executeList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True
        for i in range(len(weights)):
            if i >= len(object.data.vertices): return
            object.data.vertices[i].bevel_weight = weights[i] 
        object.data.update()
