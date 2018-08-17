import bpy
from math import isclose
from ... base_types import AnimationNode

class ViewportColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ViewportColorNode"
    bl_label = "Viewport Color"

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Color", "Color", "color")

    def execute(self, material, color):
        if material is None: return

        newColor = color[:3]
        oldColor = list(material.diffuse_color)
        if not all(isclose(a, b) for a, b in zip(oldColor, newColor)):
            material.diffuse_color = newColor
