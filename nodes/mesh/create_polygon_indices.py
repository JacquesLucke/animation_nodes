import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class CreatePolygonIndicesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreatePolygonIndicesNode"
    bl_label = "Create Polygon Indices"

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Integer List", "Indices", "indices")
        self.newOutput("Polygon Indices", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, indices):
        if len(indices) < 3:
            self.errorMessage = "3 or more indices needed"
            return (0, 1, 2)
        elif any(index < 0 for index in indices):
            self.errorMessage = "indices have to be >= 0"
            return (0, 1, 2)
        else:
            self.errorMessage = ""
            return tuple(indices)
