import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class CharactersNode(Node, AnimationNode):
	bl_idname = "CharactersNode"
	bl_label = "Characters"
	
	def init(self, context):
		self.outputs.new("StringSocket", "Lower Case")
		self.outputs.new("StringSocket", "Upper Case")
		self.outputs.new("StringSocket", "Digits")
		self.outputs.new("StringSocket", "Special")
		self.outputs.new("StringSocket", "All")
		
	def execute(self, input):
		output = {}
		output["Lower Case"] = "abcdefghijklmnopqrstuvwxyz"
		output["Upper Case"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		output["Digits"] = "0123456789"
		output["Special"] = "!$%&/()=?*+#'-_.:,;" + '"'
		output["All"] = output["Lower Case"] + output["Upper Case"] + output["Digits"] + output["Special"]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)