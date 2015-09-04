import bpy, bmesh
from ... base_types.node import AnimationNode

class SetBMeshOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBMeshOnObjectNode"
    bl_label = "Set BMesh on Object"

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"
        self.inputs.new("an_BMeshSocket", "BMesh", "bm")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def execute(self, object, bm):
        if object is None: return object
        if object.type == "MESH":
            if object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode = "OBJECT")
            if object.mode == "OBJECT":
                bm.to_mesh(object.data)
        return object
