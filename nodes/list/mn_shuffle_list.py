import bpy, random
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ShuffleListNode(Node, AnimationNode):
	bl_idname = "ShuffleListNode"
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
		self.inputs.new("IntegerSocket", "Seed")
		self.setSocketType(self.listTypesProperty)
		
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
		try:
			self.inputs.remove(self.inputs["List"])
			self.outputs.remove(self.outputs["Shuffled List"])
		except:
			pass
		if type == "FLOAT":
			self.inputs.new("FloatListSocket", "List")
			self.outputs.new("FloatListSocket", "Shuffled List")
		elif type == "STRING":
			self.inputs.new("StringListSocket", "List")
			self.outputs.new("StringListSocket", "Shuffled List")
		elif type == "OBJECT":
			self.inputs.new("ObjectListSocket", "List")
			self.outputs.new("ObjectListSocket", "Shuffled List")
		self.inputs.move(0, 1)
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
