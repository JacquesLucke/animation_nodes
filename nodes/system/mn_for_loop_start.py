import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_utils import *

fromListSocketName = "From List"
fromSingleSocketName = "From Single"

class mn_ForLoopStartNode(Node, AnimationNode):
	bl_idname = "mn_ForLoopStartNode"
	bl_label = "For Loop Start"
	
	loopName = bpy.props.StringProperty(default = "Object Loop")
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_IntegerSocket", "Index")
		self.outputs.new("mn_IntegerSocket", "List Length")
		self.outputs.new("mn_EmptySocket", fromListSocketName)
		self.outputs.new("mn_EmptySocket", fromSingleSocketName)
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
		
		# from list socket
		socket = self.outputs.get(fromListSocketName)
		targetSocket = self.getValidTargetSocket(socket)
		if targetSocket is not None:
			newSocket = self.newOutputSocket(targetSocket)
			newSocket.loopAsList = True
			self.id_data.links.new(targetSocket, newSocket)
			newIndex = self.outputs.find(socket.name)
			self.outputs.move(len(self.outputs) - 1, newIndex)
			self.updateCallerNodes()
			
			
		# from single socket
		socket = self.outputs.get(fromSingleSocketName)
		targetSocket = self.getValidTargetSocket(socket)
		if targetSocket is not None:
			newSocket = self.newOutputSocket(targetSocket)
			self.id_data.links.new(targetSocket, newSocket)
			newIndex = self.outputs.find(socket.name)
			self.outputs.move(len(self.outputs) - 1, newIndex)
			self.updateCallerNodes()
			
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
		
	def newOutputSocket(self, targetSocket):
		idName = self.correctIdName(targetSocket.bl_idname)
		
		socket = self.outputs.new(idName, getNotUsedSocketName(self, prefix = "socket"))
		socket.customName = getNotUsedCustomSocketName(self, prefix = targetSocket.name)
		targetSocket = None
		socket.editableCustomName = True
		socket.callNodeWhenCustomNameChanged = True
		socket.removeable = True
		socket.callNodeToRemove = True
		return socket
		
	def correctIdName(self, idName):
		if idName == "mn_EmptySocket":
			idName = "mn_GenericSocket"
		return idName
		
	def customSocketNameChanged(self, socket):
		self.updateCallerNodes()
		
	def removeSocket(self, socket):
		self.outputs.remove(socket)
		self.updateCallerNodes()
		
	def updateCallerNodes(self):
		nodes = getNodesFromTypeWithAttribute("mn_ForLoopNode", "selectedLoop", self.loopName)
		for node in nodes:
			node.updateSockets(self)
			
	def getSocketDescriptions(self):
		fromListSockets = []
		fromSingleSockets = []
		
		for i, socket in enumerate(self.outputs):
			if i > 1 and socket.bl_idname != "mn_EmptySocket":
				if socket.loopAsList: fromListSockets.append(socket)
				else: fromSingleSockets.append(socket)
			
		return (fromListSockets, fromSingleSockets)
