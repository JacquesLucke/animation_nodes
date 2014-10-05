import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class SocketPropertyGroup(bpy.types.PropertyGroup):
	socketName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)
	socketType = bpy.props.StringProperty(name = "Socket Type", default = "", update = nodePropertyChanged)

class SubProgramStartNode(Node, AnimationNode):
	bl_idname = "SubProgramStartNode"
	bl_label = "Sub-Program Start"
	
	sockets = bpy.props.CollectionProperty(type = SocketPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		self.outputs.new("SubProgramSocket", "Sub-Program")
		self.outputs.new("IntegerSocket", "Index")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "showEditOptions", text = "Show Options")
		layout.separator()
		if self.showEditOptions:
		
			rebuild = layout.operator("mn.rebuild_sub_program_sockets", "Rebuild Sockets")
			rebuild.nodeTreeName = self.id_data.name
			rebuild.nodeName = self.name
		
			col = layout.column(align = True)
			for index, item in enumerate(self.sockets):
				row = col.row(align = True)
				row.scale_y = 1.3
				row.prop(item, "socketName", text = "")
				remove = row.operator("mn.remove_property_from_list_node", text = "", icon = "X")
				remove.nodeTreeName = self.id_data.name
				remove.nodeName = self.name
				remove.index = index
				
			addSocketList = [
				("Object List", "ObjectListSocket"),
				("String List", "StringListSocket"),
				("Float", "FloatSocket"),
				("Text", "StringSocket") ]
			layout.label("Add Sockets")
			col = layout.column(align = True)
			for displayTame, socketType in addSocketList:
				add = col.operator("mn.new_sub_program_socket", text = displayTame)
				add.nodeTreeName = self.id_data.name
				add.nodeName = self.name
				add.socketType = socketType
		
	def execute(self, input):
		return input
		
	def newSocket(self, socketType):
		item = self.sockets.add()
		item.socketType = socketType
		item.socketName = self.getPossibleName("Socket")
	def getPossibleName(self, name):
		counter = 1
		while self.socketNameExists(name + " " + str(counter)):
			counter += 1
		return name + " " + str(counter)
	def socketNameExists(self, name):
		for item in self.sockets:
			if item.socketName == name: return True
		return False
		
	def removeItemFromList(self, index):
		self.sockets.remove(index)
		
	def rebuildSubProgramSockets(self):
		self.removeDynamicSockets()
		for item in self.sockets:
			self.outputs.new(item.socketType, item.socketName)
	def removeDynamicSockets(self):
		for i, socket in enumerate(self.outputs):
			if i >= 2: self.inputs.remove(socket)
			
		
class NewSubProgramSocketNode(bpy.types.Operator):
	bl_idname = "mn.new_sub_program_socket"
	bl_label = "New Sub-Program Socket"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	socketType = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.newSocket(self.socketType)
		return {'FINISHED'}
		
class RebuildSubProgramSockets(bpy.types.Operator):
	bl_idname = "mn.rebuild_sub_program_sockets"
	bl_label = "Rebuild Sub-Program Sockets"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.rebuildSubProgramSockets()
		return {'FINISHED'}	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)