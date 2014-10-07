import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_dynamic_sockets_helper import *
from mn_utils import *


class SubProgramStartNode(Node, AnimationNode):
	bl_idname = "SubProgramStartNode"
	bl_label = "Sub-Program Start"
	
	sockets = bpy.props.CollectionProperty(type = SocketPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	subProgramName = bpy.props.StringProperty(default = "Name")
	
	def init(self, context):
		self.outputs.new("IntegerSocket", "Index")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "subProgramName", text = "Name")
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
				
			layout.label("Add Sockets")
			col = layout.column(align = True)
			for displayTame, socketType in getAddSocketList():
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
			if i > 0: self.inputs.remove(socket)
			
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)