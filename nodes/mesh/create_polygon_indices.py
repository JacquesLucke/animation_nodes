import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class CreatePolygonIndices(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CreatePolygonIndices"
    bl_label = "Create Polygon Indices"
    isDetermined = True

    inputNames = { "Indices" : "indices" }
    outputNames = { "Polygon Indices" : "polygonIndices" }

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("mn_IntegerListSocket", "Indices")
        self.outputs.new("mn_PolygonIndicesSocket", "Polygon Indices")

    def draw_buttons(self, context, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, indices):
        if len(indices) >= 3:
            self.errorMessage = ""
            return tuple(indices)
        else:
            self.errorMessage = "3 or more indices needed"
            return (0, 1, 2)
