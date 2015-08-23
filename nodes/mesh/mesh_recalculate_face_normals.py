import bpy, bmesh
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import propertyChanged

class MeshRecalculateFaceNormals(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshRecalculateFaceNormals"
    bl_label = "Recalculate Normals"

    invert = BoolProperty(name = "Invert Normals", update = propertyChanged)

    def create(self):
        self.inputs.new("an_MeshSocket", "Mesh", "bm").dataIsModified = True
        self.outputs.new("an_MeshSocket", "Mesh", "mesh")

    def draw(self, layout):
        layout.prop(self, "invert")

    def execute(self, bm):
        self.calculate_face_normals(bm)
        if self.invert:
            self.calculate_face_normals(bm)
        return bm

    def calculate_face_normals(self, bm):
        bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
