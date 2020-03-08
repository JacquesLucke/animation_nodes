import bpy, bmesh
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class BMeshRecalculateFaceNormalsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshRecalculateFaceNormalsNode"
    bl_label = "BMesh Recalculate Normals"

    def create(self):
        self.newInput("BMesh", "BMesh", "bm").dataIsModified = True
        self.newOutput("BMesh", "BMesh", "bm")

    def getExecutionCode(self, required):
        recalcString = "bmesh.ops.recalc_face_normals(bm, faces = bm.faces)"
        return recalcString

    def getUsedModules(self):
        return ["bmesh"]
