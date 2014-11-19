import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.sockets.mn_socket_info import *

newInputSocketName = "New Input"

class mn_GroupInput(Node, AnimationNode):
	bl_idname = "mn_GroupInput"
	bl_label = "Group Input"
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_EmptySocket", newInputSocketName)
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		
	def execute(self, input):
		return input
		
	def update(self):
		forbidCompiling()
		socket = self.outputs.get(newInputSocketName)
		targetSocket = self.getValidTargetSocket(socket)
		if targetSocket is not None:
			socketType = self.getTargetSocketType(targetSocket)
			newSocket = self.newOutputSocket(socketType, namePrefix = "socket")
			self.id_data.links.new(targetSocket, newSocket)
			newIndex = self.outputs.find(socket.name)
			self.outputs.move(len(self.outputs) - 1, newIndex)
		else:
			removeLinksFromSocket(socket)
		allowCompiling()
	
	def getValidTargetSocket(self, socket):
		if socket is None:
			return None
		links = socket.links
		if len(links) == 0:
			return None
		toSocket = links[0].to_socket
		if toSocket.node.type == "REROUTE":
			return None
		return toSocket
		
	def getTargetSocketType(self, targetSocket):
		idName = targetSocket.bl_idname
		if idName == "mn_EmptySocket":
			if targetSocket.passiveSocketType != "":
				idName = targetSocket.passiveSocketType
		return idName
		
	def newOutputSocket(self, idName, namePrefix):		
		socket = self.outputs.new(idName, getNotUsedSocketName(self, prefix = "socket"))
		socket.customName = getNotUsedCustomSocketName(self, prefix = namePrefix)
		targetSocket = None
		socket.editableCustomName = True
		socket.callNodeWhenCustomNameChanged = True
		socket.removeable = True
		socket.callNodeToRemove = True
		return socket
		
	def removeSocket(self, socket):
		self.outputs.remove(socket)