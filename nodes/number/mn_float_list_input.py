import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_FloatPropertyGroup(bpy.types.PropertyGroup):
	value = bpy.props.FloatProperty(name = "Value", default = 0, update = nodePropertyChanged)

class mn_FloatListInputNode(Node, AnimationNode):
	bl_idname = "mn_FloatListInputNode"
	bl_label = "Number List"
	isDetermined = True
	
	numbers = bpy.props.CollectionProperty(type = mn_FloatPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_FloatListSocket", "Numbers")
		allowCompiling()
		
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
				remove = row.operator("mn.remove_property_from_list_node", text = "", icon = "X")
				remove.nodeTreeName = self.id_data.name
				remove.nodeName = self.name
				remove.index = index
				index += 1
			add = layout.operator("mn.new_property_to_list_node", text = "New", icon = "PLUS")
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

