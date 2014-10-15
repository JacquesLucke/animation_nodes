import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class ObjectPropertyGroup(bpy.types.PropertyGroup):
	object = bpy.props.StringProperty(name = "Object", default = "", update = nodePropertyChanged)

class ObjectListInputNode(Node, AnimationNode):
	bl_idname = "ObjectListInputNode"
	bl_label = "Object List"
	
	objects = bpy.props.CollectionProperty(type = ObjectPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		self.outputs.new("ObjectListSocket", "Objects")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "showEditOptions", text = "Show Options")
		layout.separator()
		if self.showEditOptions:
			index = 0
			col = layout.column(align = True)
			for item in self.objects:
				row = col.row(align = True)
				row.scale_y = 1.3
				select = row.operator("mn.assign_active_object_to_list_node", text = "", icon = "EYEDROPPER")
				select.nodeTreeName = self.id_data.name
				select.nodeName = self.name
				select.index = index
				row.prop(item, "object", text = "")
				remove = row.operator("mn.remove_property_from_list_node", text = "", icon = "X")
				remove.nodeTreeName = self.id_data.name
				remove.nodeName = self.name
				remove.index = index
				index += 1
				
			add = layout.operator("mn.new_property_to_list_node", text = "New Item", icon = "PLUS")
			add.nodeTreeName = self.id_data.name
			add.nodeName = self.name
			
			add = layout.operator("mn.selected_objects_to_object_list_node", text = "From Selection", icon = "PLUS")
			add.nodeTreeName = self.id_data.name
			add.nodeName = self.name
			
			layout.separator()
				
	def execute(self, input):
		output = {}
		output["Objects"] = self.getCurrentList()
		return output
		
	def getCurrentList(self):
		objectList = []
		for item in self.objects:
			objectList.append(bpy.data.objects.get(item.object))
		return objectList
		
	def addItemToList(self):
		item = self.objects.add()
		
	def removeItemFromList(self, index):
		self.objects.remove(index)
		
	def setObject(self, object, index):
		self.objects[index].object = object.name
		
	def newItemsFromSelection(self, objects):
		for object in objects:
			item = self.objects.add()
			item.object = object.name
	
	
class AssignActiveObjectToListNode(bpy.types.Operator):
	bl_idname = "mn.assign_active_object_to_list_node"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	index = bpy.props.IntProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		node.setObject(obj, self.index)
		return {'FINISHED'}	
		
class SelectedObjectsToObjectListNode(bpy.types.Operator):
	bl_idname = "mn.selected_objects_to_object_list_node"
	bl_label = "New Items From Selection"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
		
	def execute(self, context):
		selectedObjects = bpy.context.selected_objects
		node = getNode(self.nodeTreeName, self.nodeName)
		node.newItemsFromSelection(selectedObjects)
		return {'FINISHED'}	
