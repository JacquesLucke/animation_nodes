import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class BMeshInvertNormalsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshInvertNormalsNode"
    bl_label = "BMesh Invert Normals"

    flipMultires: BoolProperty(name = "Flip Multires", update = executionCodeChanged)

    def create(self):
        self.newInput("BMesh", "BMesh", "bm").dataIsModified = True
        self.newOutput("BMesh", "BMesh", "bm")

    def draw(self, layout):
        layout.prop(self, "flipMultires")

    def getExecutionCode(self, required):
        return "bmesh.ops.reverse_faces(bm, faces = bm.faces, flip_multires = self.flipMultires)"

    def getUsedModules(self):
        return ["bmesh"]
