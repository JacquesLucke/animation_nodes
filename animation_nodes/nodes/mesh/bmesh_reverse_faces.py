import bpy, bmesh
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class BMeshReverseFacesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshReverseFacesNode"
    bl_label = "BMesh Reverse Faces"

    flip_multires: BoolProperty(name = "Flip Multi Resolution", update = executionCodeChanged)

    def create(self):
        self.newInput("BMesh", "BMesh", "bm").dataIsModified = True
        self.newOutput("BMesh", "BMesh", "bm")

    def draw(self, layout):
        layout.prop(self, "flip_multires")

    def getExecutionCode(self, required):
        recalcString = f"bmesh.ops.reverse_faces(bm, faces = bm.faces, flip_multires = {self.flip_multires})"
        return recalcString

    def getUsedModules(self):
        return ["bmesh"]
