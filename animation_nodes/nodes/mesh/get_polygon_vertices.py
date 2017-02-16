import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class GetPolygonVerticesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetPolygonVerticesNode"
    bl_label = "Get Polygon Vertices"
    bl_width_default = 160

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Vector List", "All Vertices", "allVertices")
        self.newInput("Polygon Indices", "Polygon Indices", "polygonIndices")
        self.newOutput("Vector List", "Polygon Vertices", "polygonVertices")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionCode(self):
        yield "try:"
        yield "    self.errorMessage = ''"
        yield "    polygonVertices = allVertices[polygonIndices]"
        yield "except IndexError:"
        yield "    self.errorMessage = 'Invalid Indices'"
        yield "    polygonVertices = Vector3DList()"
