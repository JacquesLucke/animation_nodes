import bpy
import numpy as np
from ... base_types import AnimationNode, VectorizedSocket

class EdgeCreases(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetEdgeCreases"
    bl_label = "Set Edge Creases"
    errorHandlingType = "EXCEPTION"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Crease", "crease"), ("Creases", "creases")))
        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useFloatList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, crease):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        creases = np.zeros((len(object.data.edges)), dtype=float)     
        creases[:] = crease
        object.data.edges.foreach_set('crease', creases)
        object.data.update()
        return object

    def executeList(self, object, creases):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        try:
            object.data.edges.foreach_set('crease', creases)
        except:
            self.raiseErrorMessage("Input Creases has wrong length")
            return object
        object.data.update()
        return object