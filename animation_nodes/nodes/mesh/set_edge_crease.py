import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class EdgeCrease(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetEdgeCrease"
    bl_label = "Set Edge Crease"
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

        creases = VirtualDoubleList.create(crease, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('crease', creases.asNumpyArray())
        object.data.update()
        return object

    def executeList(self, object, creases):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return

        creases = VirtualDoubleList.create(creases, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('crease', creases.asNumpyArray())
        object.data.update()
        return object
