import bpy
import bmesh
from ... base_types.node import AnimationNode

class SetMeshDataOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetMeshDataOnObjectNode"
    bl_label = "Set Mesh Data on Object"

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"
        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def execute(self, object, meshData):
        if object is None: return object
        if object.type == "MESH":
            if object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode = "OBJECT")
            if object.mode == "OBJECT":
                bmesh.new().to_mesh(object.data)
                object.data.from_pydata(meshData.vertices, meshData.edges, meshData.polygons)
        return object
