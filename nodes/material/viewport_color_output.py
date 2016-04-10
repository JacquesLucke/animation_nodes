import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class ViewportColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ViewportColorNode"
    bl_label = "Viewport Color"

    materialName = StringProperty(update = propertyChanged)

    def create(self):
        self.newInput("Color", "Color", "color")

    def draw(self, layout):
        layout.prop_search(self, 'materialName', bpy.data, 'materials', text='', icon='MATERIAL_DATA')

    def execute(self, color):
        material = bpy.data.materials.get(self.materialName)
        if material is None: return

        try: material.diffuse_color = color[:3]
        except: pass
