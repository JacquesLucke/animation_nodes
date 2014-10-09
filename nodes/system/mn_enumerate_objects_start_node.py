import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_dynamic_sockets_helper import *
from mn_execution import nodePropertyChanged
from mn_utils import *

class EnumerateObjectsStartNode(Node, AnimationNode):
	bl_idname = "EnumerateObjectsStartNode"
	bl_label = "Object Loop Start"
	
	sockets = bpy.props.CollectionProperty(type = SocketPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	subProgramName = bpy.props.StringProperty(default = "Object Loop")
	
	def init(self, context):
		self.outputs.new("ObjectSocket", "Object")
		self.outputs.new("IntegerSocket", "Index")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "subProgramName", text = "Name")
		layout.prop(self, "showEditOptions", text = "Show Options")
		
		layout.separator()
		if self.showEditOptions:
			row = layout.row(align = True)
			
			rebuild = row.operator("mn.rebuild_sub_program_sockets", "Rebuild Sockets")
			rebuild.nodeTreeName = self.id_data.name
			rebuild.nodeName = self.name
			
			newNode = row.operator("node.add_node", text = "", icon = "PLUS")
			newNode.use_transform = True
			newNode.type = "EnumerateObjectsNode"
		
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
		item.socketName = self.getPossibleName(socketType)
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
		self.updateCallerNodeSockets()
	def removeDynamicSockets(self):
		for i, socket in enumerate(self.outputs):
			if i > 1: self.inputs.remove(socket)
			
	def updateCallerNodeSockets(self):
		for node in self.id_data.nodes:
			if node.bl_idname == "EnumerateObjectsNode":
				if node.subProgramsEnum == self.subProgramName:
					rebuildSockets(node)
			
		

# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)