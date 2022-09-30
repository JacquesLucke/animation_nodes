import bpy
from bpy.props import *
from ... data_structures import Color
from ... events import propertyChanged
from ... base_types import AnimationNode

class ChooseColorNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ChooseColorNode"
    bl_label = "Choose Color"

    colorProperty: FloatVectorProperty(
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0, update = propertyChanged)

    def create(self):
        self.newInput("Float", "Alpha", "alpha", value = 1.0)
        self.newOutput("Color", "Color", "color")

    def draw(self, layout):
        layout.template_color_picker(self, "colorProperty", value_slider = True)

    def execute(self, alpha):
        return Color((*self.colorProperty, alpha))
