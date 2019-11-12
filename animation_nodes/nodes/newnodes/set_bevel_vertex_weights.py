import bpy
import numpy as np
from ... base_types import AnimationNode, VectorizedSocket

class BevelVertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelVertexWeights"
    bl_label = "Set Bevel Vertex Weights"
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
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True

        weights = np.zeros((len(object.data.vertices)), dtype=float)     
        weights[:] = weight
        object.data.vertices.foreach_set('bevel_weight', weights) 
        object.data.update()
        return object

    def executeList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True
        try:
            object.data.vertices.foreach_set('bevel_weight', weights)
        except:
            self.raiseErrorMessage("Input Weights has wrong length")
            return object
        object.data.update()
        return object