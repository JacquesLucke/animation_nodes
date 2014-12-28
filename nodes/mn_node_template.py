def getNormalNodeTemplate():
	return '''import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TransformText(Node, AnimationNode):
	bl_idname = "mn_TransformText"
	bl_label = "Transform Text"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_StringSocket", "Text")
		self.inputs.new("mn_BooleanSocket", "To Uppercase")
		self.outputs.new("mn_StringSocket", "New Text")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Text" : "text",
				"To Uppercase" : "toUpper"}
	def getOutputSocketNames(self):
		return {"New Text" : "newText"}
		
	def execute(self, text, toUpper):
		if toUpper:
			newText = text.upper()
		else:
			newText = text.lower()
		return newText


'''

def getAutoRegisterCode():
	return '''
	
if __name__ == "__main__":
	try: bpy.utils.register_module(__name__)
	except: pass
	
'''