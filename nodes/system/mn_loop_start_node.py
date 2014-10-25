import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_dynamic_sockets_helper import *
from mn_utils import *


class mn_LoopStartNode(Node, AnimationNode):
	bl_idname = "mn_LoopStartNode"
	bl_label = "Loop Start"
	
	sockets = bpy.props.CollectionProperty(type = SocketPropertyGroup)
	showEditOptions = bpy.props.BoolProperty(default = True)
	loopName = bpy.props.StringProperty(default = "Name")
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_IntegerSocket", "Index")		
		self.outputs.new("mn_EmptySocket", "...")
		self.updateCallerNodes()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
	
		row.prop(self, "loopName", text = "")
		
		newNode = row.operator("node.add_node", text = "", icon = "PLUS")
		newNode.use_transform = True
		newNode.type = "mn_LoopNode"
		
	def execute(self, input):
		return input
		
	def update(self):
		forbidCompiling()
		socket = self.outputs.get("...")
		if socket is not None:
			links = socket.links
			if len(links) > 0:
				toSocket = links[0].to_socket
				self.id_data.links.remove(links[0])
				if toSocket.node.type != "REROUTE":
					self.outputs.remove(socket)
					idName = toSocket.bl_idname
					if idName == "mn_EmptySocket": 
						idName = "mn_GenericSocket"
					newSocket = self.outputs.new(idName, toSocket.name)
					newSocket.editableCustomName = True
					newSocket.customName = toSocket.name
					newSocket.removeable = True
					newSocket.callNodeToRemove = True
					newSocket.callNodeWhenCustomNameChanged = True
					self.outputs.new("mn_EmptySocket", "...")
					self.id_data.links.new(toSocket, newSocket)
				self.updateCallerNodes()
		allowCompiling()
		
	def customSocketNameChanged(self, socket):
		self.updateCallerNodes()
		print("hey")
		
	def removeSocket(self, socket):
		self.outputs.remove(socket)
		self.updateCallerNodes()
		
	def updateCallerNodes(self):
		socketDescriptions = self.getSocketDescriptions()
		
		for node in self.id_data.nodes:
			if node.bl_idname == "mn_LoopNode":
				if node.selectedLoop == self.loopName:
					node.updateSockets(socketDescriptions)
					
		nodeTreeChanged()
					
	def getSocketDescriptions(self):
		socketDescriptions = []
		for socket in self.outputs:
			if socket.name not in ["Index", "..."]:
				socketDescriptions.append((socket.customName, socket.bl_idname))
		return socketDescriptions
