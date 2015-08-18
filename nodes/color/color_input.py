import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class ColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ColorInputNode"
    bl_label = "Color Input"
    isDetermined = True

    colorProperty = FloatVectorProperty(
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0, update = propertyChanged)

    def create(self):
        self.outputs.new("an_ColorSocket", "Color", "color")

    def draw(self, layout):
        layout.template_color_picker(self, "colorProperty", value_slider = True)

    def execute(self):
        color = self.colorProperty
        return [color[0], color[1], color[2], 1.0]
