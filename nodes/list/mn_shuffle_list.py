import bpy, random
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ShuffleListNode(Node, AnimationNode):
	bl_idname = "mn_ShuffleListNode"
	bl_label = "Shuffle List"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", ""),
		("OBJECT", "Object", "") ]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "OBJECT", update = setSocketTypes)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Seed")
		self.setSocketType(self.listTypesProperty)
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		output["Shuffled List"] = list
		random.seed(input["Seed"])
		random.shuffle(output["Shuffled List"])
		return output
		
	def setSocketType(self, type):
		forbidCompiling()
		try:
			self.inputs.remove(self.inputs["List"])
			self.outputs.remove(self.outputs["Shuffled List"])
		except:
			pass
		if type == "FLOAT":
			self.inputs.new("mn_FloatListSocket", "List")
			self.outputs.new("mn_FloatListSocket", "Shuffled List")
		elif type == "STRING":
			self.inputs.new("mn_StringListSocket", "List")
			self.outputs.new("mn_StringListSocket", "Shuffled List")
		elif type == "OBJECT":
			self.inputs.new("mn_ObjectListSocket", "List")
			self.outputs.new("mn_ObjectListSocket", "Shuffled List")
		self.inputs.move(0, 1)
		allowCompiling()
