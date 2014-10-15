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
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Lower Case" : "lower",
				"Upper Case" : "upper", 
				"Digits" : "digits", 
				"Special" : "special", 
				"All" : "all"}
		
	def execute(self):
		lower = "abcdefghijklmnopqrstuvwxyz"
		upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digits = "0123456789"
		special = "!$%&/()=?*+#'-_.:,;" + '"'
		all = lower + upper + digits + special
		return lower, upper, digits, special, all
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)