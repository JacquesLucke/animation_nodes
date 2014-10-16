def getNormalNodeTemplate():
	return '''
import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

	
class mn_YourNodeName(Node, AnimationNode):
	bl_idname = "mn_YourNodeName"
	bl_label = "Template Node"
	node_category = "my category"

	def init(self, context):
		forbidCompiling()
		self.inputs.new("StringSocket", "Text")
		self.outputs.new("StringSocket", "Uppercase")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def execute(self, input):
		output = {}
		output["Uppercase"] = input["Text"].upper()
		return output
'''

def getAutoRegisterCode():
	return '''
if __name__ == "__main__":
	try: bpy.utils.register_module(__name__)
	except: pass
	
'''