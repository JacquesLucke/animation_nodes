import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class FloatPropertyGroup(bpy.types.PropertyGroup):
	value = bpy.props.FloatProperty(name = "Value", default = 0)

class FloatListInputNode(Node, AnimationNode):
	bl_idname = "FloatListInputNode"
	bl_label = "Float List"
	
	numbers = bpy.props.CollectionProperty(type = FloatPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		self.outputs.new("FloatListSocket", "Numbers")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "showEditOptions", text = "Show Options")
		layout.separator()
		if self.showEditOptions:
			index = 0
			col = layout.column(align = True)
			for item in self.numbers:
				row = col.row(align = True)
				row.scale_y = 1.3
				row.prop(item, "value", text = str(index))
				remove = row.operator("mn.remove_float_property_from_float_list_node", text = "", icon = "X")
				remove.nodeTreeName = self.id_data.name
				remove.nodeName = self.name
				remove.index = index
				index += 1
			add = layout.operator("mn.new_float_property_to_float_list_node", text = "New", icon = "PLUS")
			add.nodeTreeName = self.id_data.name
			add.nodeName = self.name
				
	def execute(self, input):
		output = {}
		output["Numbers"] = self.getCurrentList()
		return output
		
	def getCurrentList(self):
		floatList = []
		for item in self.numbers:
			floatList.append(item.value)
		return floatList
		
	def addItemToList(self):
		item = self.numbers.add()
		item.value = 0.0
		
	def removeItemFromList(self, index):
		self.numbers.remove(index)
		
		
class NewFloatPropertyToFloatListNode(bpy.types.Operator):
	bl_idname = "mn.new_float_property_to_float_list_node"
	bl_label = "New Float Property to Float List Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.addItemToList()
		return {'FINISHED'}
		
class RemoveFloatPropertyFromFloatListNode(bpy.types.Operator):
	bl_idname = "mn.remove_float_property_from_float_list_node"
	bl_label = "Remove Float Property from Float List Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	index = bpy.props.IntProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.removeItemFromList(self.index)
		return {'FINISHED'}
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)