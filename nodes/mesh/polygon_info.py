import bpy
from ... base_types.node import AnimationNode

class PolygonInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_PolygonInfo"
    bl_label = "Polygon Info"

    inputNames = { "Polygon" : "polygon" }

    outputNames = { "Center" : "center",
                    "Normal" : "normal",
                    "Material Index" : "materialIndex",
                    "Area" : "area",
                    "Vertices" : "vertices" }

    def create(self):
        self.inputs.new("mn_PolygonSocket", "Polygon")
        self.outputs.new("mn_VectorSocket", "Center")
        self.outputs.new("mn_VectorSocket", "Normal")
        self.outputs.new("mn_VectorSocket", "Material Index")
        self.outputs.new("mn_FloatSocket", "Area")
        self.outputs.new("mn_VertexListSocket", "Vertices")

    def execute(self, polygon):
        return polygon.center, polygon.normal, polygon.materialIndex, polygon.area, polygon.vertices
