import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ToStringConversion(Node, AnimationNode):
	bl_idname = "ToStringConversion"
	bl_label = "To String"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("StringSocket", "Text")
		
	def getSocketVariableConnections(self):
		return ({"Value" : "value"}, {"Text" : "text"})
		
	def execute(self, value):
		return str(value)
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)