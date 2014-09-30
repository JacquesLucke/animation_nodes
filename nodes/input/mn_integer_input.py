import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class IntegerInputNode(Node, AnimationNode):
	bl_idname = "IntegerInputNode"
	bl_label = "Integer"
	
	intProperty = bpy.props.IntProperty(default = 0, update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("IntegerSocket", "Number")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "intProperty", text = "")
		
	def execute(self, input):
		output = {}
		output["Number"] = self.intProperty
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)