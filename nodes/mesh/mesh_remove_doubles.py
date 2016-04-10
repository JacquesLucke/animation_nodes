import bpy
import bmesh
from ... base_types.node import AnimationNode

class BMeshRemoveDoublesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshRemoveDoublesNode"
    bl_label = "BMesh Remove Doubles"

    def create(self):
        self.newInput("an_BMeshSocket", "BMesh", "bm").dataIsModified = True
        socket = self.newInput("an_FloatSocket", "Distance", "distance")
        socket.value = 0.0001
        socket.minValue = 0.0
        self.newOutput("an_BMeshSocket", "BMesh", "bm")

    def getExecutionCode(self):
        return "bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = distance)"

    def getUsedModules(self):
        return ["bmesh"]
