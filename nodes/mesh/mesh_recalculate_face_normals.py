import bpy, bmesh
from ... base_types.node import AnimationNode

class MeshRecalculateFaceNormals(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MeshRecalculateFaceNormals"
    bl_label = "Recalculate Normals"

    inputNames = { "Mesh" : "bm" }
    outputNames = { "Mesh" : "mesh" }

    invert = bpy.props.BoolProperty(name = "Invert Normals", update = nodePropertyChanged)

    def create(self):
        self.inputs.new("mn_MeshSocket", "Mesh")
        self.outputs.new("mn_MeshSocket", "Mesh")

    def draw_buttons(self, context, layout):
        layout.prop(self, "invert")

    def execute(self, bm):
        self.calculate_face_normals(bm)
        if self.invert:
            self.calculate_face_normals(bm)
        return bm

    def calculate_face_normals(self, bm):
        bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
