import bpy
import numpy as np
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
        weights = np.zeros((len(object.data.edges)), dtype=float)     
        weights[:] = weight
        object.data.edges.foreach_set('bevel_weight', weights)
        object.data.update()
        return object

    def executeList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True
        try:
            object.data.edges.foreach_set('bevel_weight', weights)
        except:
            self.raiseErrorMessage("Input Weights has wrong length")
            return object
        object.data.update()
        return object