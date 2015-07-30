import bpy
from ... base_types.node import AnimationNode
from ... events import propertyChanged

class ColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ColorInputNode"
    bl_label = "Color Input"
    isDetermined = True
    
    inputNames = {}
    outputNames = { "Color" : "color" }
    
    colorProperty = bpy.props.FloatVectorProperty(default = [0.5, 0.5, 0.5], subtype = "COLOR", soft_min = 0.0, soft_max = 1.0, update = propertyChanged)
    
    def create(self):
        self.outputs.new("mn_ColorSocket", "Color")
        
    def draw_buttons(self, context, layout):
        layout.template_color_picker(self, "colorProperty", value_slider = True)
        
    def execute(self):
        color = self.colorProperty
        return [color[0], color[1], color[2], 1.0]