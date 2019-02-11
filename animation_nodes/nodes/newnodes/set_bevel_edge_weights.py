import bpy
from ... base_types import AnimationNode, VectorizedSocket

class BevelEdgeWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelEdgeWeights"
    bl_label = "Set Bevel Edge Weights"

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
        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True
        for i in range(len(object.data.edges)):
            object.data.edges[i].bevel_weight = weight 
        object.data.update()

    def executeList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True
        for i in range(len(weights)):
            if i >= len(object.data.edges): return 
            object.data.edges[i].bevel_weight = weights[i] 
        object.data.update()
