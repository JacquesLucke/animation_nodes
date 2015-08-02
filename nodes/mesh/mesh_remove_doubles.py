import bpy, bmesh
from ... base_types.node import AnimationNode

class MeshRemoveDoubles(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MeshRemoveDoubles"
    bl_label = "Mesh Remove Doubles"

    inputNames = { "Mesh" : "bm",
                   "Distance" : "distance" }

    outputNames = { "Mesh" : "mesh" }

    def create(self):
        self.inputs.new("mn_MeshSocket", "Mesh")
        socket = self.inputs.new("mn_FloatSocket", "Distance")
        socket.value = 0.0001
        socket.setMinMax(0.0, 10000.0)
        self.outputs.new("mn_MeshSocket", "Mesh")

    def execute(self, bm, distance):
        bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = distance)
        return bm
