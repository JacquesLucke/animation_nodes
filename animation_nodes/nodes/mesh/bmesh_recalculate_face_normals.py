import bpy
from ... base_types import AnimationNode

class BMeshRecalculateFaceNormalsNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_BMeshRecalculateFaceNormalsNode"
    bl_label = "BMesh Recalculate Normals"

    def create(self):
        self.newInput("BMesh", "BMesh", "bm").dataIsModified = True
        self.newOutput("BMesh", "BMesh", "bm")

    def getExecutionCode(self, required):
        return "bmesh.ops.recalc_face_normals(bm, faces = bm.faces)"

    def getUsedModules(self):
        return ["bmesh"]
