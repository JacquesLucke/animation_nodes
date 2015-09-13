import bpy
from ... base_types.node import AnimationNode

class PolygonInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonInfoNode"
    bl_label = "Polygon Info"

    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon")
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_VectorSocket", "Normal", "normal")
        self.outputs.new("an_VectorSocket", "Center", "center")
        self.outputs.new("an_FloatSocket", "Area", "area")
        self.outputs.new("an_IntegerSocket", "Material Index", "materialIndex")

    def execute(self):
        return
