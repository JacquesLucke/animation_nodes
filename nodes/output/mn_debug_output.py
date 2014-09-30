import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class DebugOutputNode(Node, AnimationNode):
	bl_idname = "DebugOutputNode"
	bl_label = "Debug"
	
	debugOutputString = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Data")
		
	def draw_buttons(self, context, layout):
		layout.label(self.debugOutputString)
		
	def execute(self, input):
		self.debugOutputString = str(input["Data"])
		return {}
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)