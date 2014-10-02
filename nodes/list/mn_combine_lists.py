import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class CombineListsNode(Node, AnimationNode):
	bl_idname = "CombineListsNode"
	bl_label = "Combine Lists"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", "")]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "FLOAT", update = setSocketTypes)
	
	def init(self, context):
		self.setSocketType(self.listTypesProperty)
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		
	def execute(self, input):
		output = {}
		combination = input["List 1"][:]
		combination.extend(input["List 2"])
		output["Both Lists"] = combination
		return output
		
	def setSocketType(self, type):
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("FloatListSocket", "List 1")
			self.inputs.new("FloatListSocket", "List 2")
			self.outputs.new("FloatListSocket", "Both Lists")
		elif type == "STRING":
			self.inputs.new("StringListSocket", "List 1")
			self.inputs.new("StringListSocket", "List 2")
			self.outputs.new("StringListSocket", "Both Lists")
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)