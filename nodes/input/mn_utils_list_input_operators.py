import bpy
from mn_utils import *

class mn_NewPropertyListNode(bpy.types.Operator):
	bl_idname = "mn.new_property_to_list_node"
	bl_label = "New String Property to String List Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.addItemToList()
		return {'FINISHED'}
		
class mn_RemovePropertyFromListNode(bpy.types.Operator):
	bl_idname = "mn.remove_property_from_list_node"
	bl_label = "Remove String Property from String List Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	index = bpy.props.IntProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.removeItemFromList(self.index)
		return {'FINISHED'}