import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class SetBevelVertexWeightNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetBevelVertexWeightNode"
    bl_label = "Set Bevel Vertex Weight"
    errorHandlingType = "EXCEPTION"

    useWeightList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useWeightList",
            ("Weight", "weight"), ("Weights", "weights")))

        self.newOutput("Object", "Object", "object")

    def execute(self, object, weights):
        if object is None: return None

        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        if object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode.")

        attribute = object.data.attributes.get("bevel_weight_vert")
        if not attribute: attribute = object.data.attributes.new("bevel_weight_vert", "FLOAT", "POINT")
        weights = VirtualDoubleList.create(weights, 0).materialize(len(object.data.vertices))
        attribute.data.foreach_set('value', weights)
        object.data.update()
        return object
