import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BMeshInvertNormalsNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_BMeshInvertNormalsNode"
    bl_label = "BMesh Invert Normals"

    def create(self):
        self.newInput("BMesh", "BMesh", "bm").dataIsModified = True
        i = self.newInput("Boolean", "Flip Multires", "flipMultires")
        i.value = False
        i.hide = True
        self.newOutput("BMesh", "BMesh", "bm")

    def getExecutionCode(self, required):
        return "bmesh.ops.reverse_faces(bm, faces = bm.faces, flip_multires = flipMultires)"

    def getUsedModules(self):
        return ["bmesh"]
