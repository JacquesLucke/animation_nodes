import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class SetEdgeCreaseNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetEdgeCreaseNode"
    bl_label = "Set Edge Crease"
    errorHandlingType = "EXCEPTION"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Crease", "crease"), ("Creases", "creases")))
        self.newOutput("Object", "Object", "object")

    def execute(self, object, creases):
        if object is None: return None

        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        if object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode.")

        attribute = object.data.attributes.get("crease_edge")
        if not attribute: attribute = object.data.attributes.new("crease_edge", "FLOAT", "EDGE")
        creases = VirtualDoubleList.create(creases, 0).materialize(len(object.data.edges))
        attribute.data.foreach_set('value', creases)
        object.data.update()
        return object
