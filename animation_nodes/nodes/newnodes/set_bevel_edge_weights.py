import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class BevelEdgeWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelEdgeWeights"
    bl_label = "Set Bevel Edge Weights"
    errorHandlingType = "EXCEPTION"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Weight", "weight"), ("Weights", "weights")))
        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useFloatList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, weight):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True

        weights = VirtualDoubleList.create(weight, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('bevel_weight', weights.asNumpyArray())
        object.data.update()
        return object

    def executeList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True
        
        weights = VirtualDoubleList.create(weights, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('bevel_weight', weights.asNumpyArray())
        object.data.update()
        return object

