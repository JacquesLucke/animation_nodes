import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_EnumerateObjectsStartNode(Node, AnimationNode):
	bl_idname = "mn_EnumerateObjectsStartNode"
	bl_label = "Object Loop Start"
	
	showEditOptions = bpy.props.BoolProperty(default = True)
	loopName = bpy.props.StringProperty(default = "Object Loop")
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_ObjectSocket", "Object")
		self.outputs.new("mn_IntegerSocket", "Index")
		self.outputs.new("mn_IntegerSocket", "List Length")
		self.outputs.new("mn_EmptySocket", "...")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
	
		row.prop(self, "loopName", text = "")
		
		newNode = row.operator("node.add_node", text = "", icon = "PLUS")
		newNode.use_transform = True
		newNode.type = "mn_EnumerateObjectsNode"
		
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
					newSocket = self.outputs.new(idName, self.getNotUsedSocketName())
					newSocket.editableCustomName = True
					newSocket.customName = self.getNotUsedCustomName(prefix = toSocket.name)
					newSocket.removeable = True
					newSocket.callNodeToRemove = True
					newSocket.callNodeWhenCustomNameChanged = True
					self.outputs.new("mn_EmptySocket", "...")
					self.id_data.links.new(toSocket, newSocket)
					oldValue = toSocket.getStoreableValue()
					self.updateCallerNodes(socketStartValue = (newSocket.identifier, oldValue))
		allowCompiling()
		
	def getNotUsedCustomName(self, prefix = "custom name"):
		customName = prefix
		while self.isCustomNameUsed(customName):
			customName = prefix + getRandomString(3)
		return customName
	def isCustomNameUsed(self, customName):
		for socket in self.outputs:
			if socket.customName == customName: return True
		return False
	
	def getNotUsedSocketName(self):
		socketName = getRandomString(5)
		while self.isSocketNameUsed(socketName):
			socketName = getRandomString(5)
		return socketName
	def isSocketNameUsed(self, name):
		for socket in self.outputs:
			if socket.name == name or socket.identifier == name: return True
		return False
		
	def customSocketNameChanged(self, socket):
		self.updateCallerNodes()
		
	def removeSocket(self, socket):
		self.outputs.remove(socket)
		self.updateCallerNodes()
		
	def updateCallerNodes(self, socketStartValue = (None, None)):
		for node in self.id_data.nodes:
			if node.bl_idname == "mn_EnumerateObjectsNode":
				if node.selectedLoop == self.loopName:
					node.updateSockets(self, socketStartValue)
					
		nodeTreeChanged()
					
	def getSocketDescriptions(self):
		socketDescriptions = []
		for socket in self.outputs:
			if socket.name not in ["Object", "Index", "List Length", "..."]:
				socketDescriptions.append((socket.customName, socket.bl_idname, socket.identifier))
		return socketDescriptions
