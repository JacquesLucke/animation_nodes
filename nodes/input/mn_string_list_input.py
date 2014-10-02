import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class StringPropertyGroup(bpy.types.PropertyGroup):
	string = bpy.props.StringProperty(name = "String", default = "", update = nodePropertyChanged)

class StringListInputNode(Node, AnimationNode):
	bl_idname = "StringListInputNode"
	bl_label = "String List"
	
	strings = bpy.props.CollectionProperty(type = StringPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		self.outputs.new("StringListSocket", "Strings")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "showEditOptions", text = "Show Options")
		layout.separator()
		if self.showEditOptions:
			index = 0
			col = layout.column(align = True)
			for item in self.strings:
				row = col.row(align = True)
				row.scale_y = 1.3
				row.prop(item, "string", text = "")
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
		output["Strings"] = self.getCurrentList()
		return output
		
	def getCurrentList(self):
		floatList = []
		for item in self.strings:
			floatList.append(item.string)
		return floatList
		
	def addItemToList(self):
		item = self.strings.add()
		item.value = 0.0
		
	def removeItemFromList(self, index):
		self.strings.remove(index)
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)