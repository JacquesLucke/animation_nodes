import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class GetListElementNode(Node, AnimationNode):
	bl_idname = "GetListElementNode"
	bl_label = "Get Element"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", ""),
		("OBJECT", "Object", "") ]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "FLOAT", update = setSocketTypes)
	
	def init(self, context):
		self.setSocketType(self.listTypesProperty)
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		index = input["Index"]
		output["Number"] = None
		if len(list) > 0:
			output["Number"] = list[max(min(index, len(list) - 1), 0)]
		return output
		
	def setSocketType(self, type):
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("FloatListSocket", "List")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("FloatSocket", "Number")
		elif type == "STRING":
			self.inputs.new("StringListSocket", "List")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("StringSocket", "Number")
		elif type == "OBJECT":
			self.inputs.new("ObjectListSocket", "List")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("ObjectSocket", "Number")
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
