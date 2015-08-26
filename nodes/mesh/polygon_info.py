import bpy
from ... base_types.node import AnimationNode

class PolygonInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonInfoNode"
    bl_label = "Polygon Info"

    def create(self):
        # can be modified when another node modifies the center or normal vector
        self.inputs.new("an_PolygonSocket", "Polygon", "polygon").dataIsModified = True
        self.outputs.new("an_VectorSocket", "Center", "center")
        self.outputs.new("an_VectorSocket", "Normal", "normal")
        self.outputs.new("an_VectorSocket", "Material Index", "materialIndex")
        self.outputs.new("an_FloatSocket", "Area", "area")
        self.outputs.new("an_VertexListSocket", "Vertices", "vertices")

    def execute(self, polygon):
        return polygon.center, polygon.normal, polygon.materialIndex, polygon.area, polygon.vertices
