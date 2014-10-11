import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ColorInputNode(Node, AnimationNode):
	bl_idname = "ColorInputNode"
	bl_label = "Color"
	
	colorProperty = bpy.props.FloatVectorProperty(default = [0.5, 0.5, 0.5], subtype = "COLOR", soft_min = 0.0, soft_max = 1.0, update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("ColorSocket", "Color")
		pass
		
	def draw_buttons(self, context, layout):
		layout.template_color_picker(self, "colorProperty", value_slider = True)
		
	def execute(self, input):
		output = {}
		output["Color"] = self.colorProperty
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)