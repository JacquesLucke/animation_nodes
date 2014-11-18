import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ColorInputNode(Node, AnimationNode):
	bl_idname = "mn_ColorInputNode"
	bl_label = "Color Input"
	isDetermined = True
	
	colorProperty = bpy.props.FloatVectorProperty(default = [0.5, 0.5, 0.5], subtype = "COLOR", soft_min = 0.0, soft_max = 1.0, update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_ColorSocket", "Color")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.template_color_picker(self, "colorProperty", value_slider = True)
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Color" : "color"}
		
	def execute(self):
		color = self.colorProperty
		return [color[0], color[1], color[2], 1.0]

classes = [
	mn_ColorInputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
