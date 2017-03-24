import bpy
from bpy.props import *
from ... base_types import AnimationNode

class GetVectorsForPolygonNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetVectorsForPolygonNode"
    bl_label = "Get Vectors for Polygon"
    bl_width_default = 170

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Polygon Indices", "Polygon Indices", "polygonIndices")
        self.newInput("Vector List", "All Vectors", "allVectors")
        self.newOutput("Vector List", "Polygon Vectors", "polygonVectors")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionCode(self):
        yield "try:"
        yield "    self.errorMessage = ''"
        yield "    polygonVectors = allVectors[polygonIndices]"
        yield "except IndexError:"
        yield "    self.errorMessage = 'Invalid Indices'"
        yield "    polygonVectors = Vector3DList()"
