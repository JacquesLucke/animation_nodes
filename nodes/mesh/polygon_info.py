import bpy
from ... base_types.node import AnimationNode

class PolygonInfo(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonInfo"
    bl_label = "Polygon Info"

    inputNames = { "Polygon" : "polygon" }

    outputNames = { "Center" : "center",
                    "Normal" : "normal",
                    "Material Index" : "materialIndex",
                    "Area" : "area",
                    "Vertices" : "vertices" }

    def create(self):
        self.inputs.new("an_PolygonSocket", "Polygon")
        self.outputs.new("an_VectorSocket", "Center")
        self.outputs.new("an_VectorSocket", "Normal")
        self.outputs.new("an_VectorSocket", "Material Index")
        self.outputs.new("an_FloatSocket", "Area")
        self.outputs.new("an_VertexListSocket", "Vertices")

    def execute(self, polygon):
        return polygon.center, polygon.normal, polygon.materialIndex, polygon.area, polygon.vertices
