import bpy, bmesh
from ... base_types.node import AnimationNode

class SetMeshOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetMeshOnObjectNode"
    bl_label = "Set Mesh on Object"

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.showName = False
        socket.objectCreationType = "MESH"
        self.inputs.new("an_MeshSocket", "Mesh", "bm")
        self.outputs.new("an_ObjectSocket", "Object", "outObject")

    def execute(self, object, bm):
        if object is None: return object
        if object.type == "MESH":
            if object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode = "OBJECT")
            if object.mode == "OBJECT":
                bm.to_mesh(object.data)
        return object
