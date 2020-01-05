import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class BevelEdgeWeight(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelEdgeWeight"
    bl_label = "Set Bevel Edge Weight"
    errorHandlingType = "EXCEPTION"

    useWeightList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useWeightList",
            ("Weight", "weight"), ("Weights", "weights")))

        self.newOutput("Object", "Object", "object")

    def execute(self, object, weights):
        if object is None: return None

        if object.type != "MESH" or object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode or is no mesh object.")

        if object.data.use_customdata_edge_bevel is False:
            object.data.use_customdata_edge_bevel = True

        weights = VirtualDoubleList.create(weights, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('bevel_weight', weights)
        object.data.update()
        return object
