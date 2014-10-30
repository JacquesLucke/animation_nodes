import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_utils import *
from mn_socket_info import *

newListSocketName = "New List"
newOptionSocketName = "New Option"

class mn_LoopStartNode(Node, AnimationNode):
	bl_idname = "mn_LoopStartNode"
	bl_label = "Loop"
	
	def loopNameChanged(self, context):
		if not self.nameIsChanging:
			self.nameIsChanging = True
			self.loopName = self.getNotUsedLoopName(prefix = self.loopName)
			self.nameIsChanging = False
	def allowNewListChanged(self, context):
		self.outputs.get(newListSocketName).hide = not self.allowNewList
	def presetChanged(self, context):
		self.buildPreset()
	
	loopName = bpy.props.StringProperty(default = "Object Loop", update = loopNameChanged)
	nameIsChanging = bpy.props.BoolProperty(default = False)
	
	allowNewList = bpy.props.BoolProperty(default = True, update = allowNewListChanged)
	preset = bpy.props.StringProperty(default = "", update = presetChanged)
	
	boolPresetBuild = bpy.props.BoolProperty(default = False)
	
	def init(self, context):
		forbidCompiling()
		self.loopName = self.getNotUsedLoopName()
		self.outputs.new("mn_IntegerSocket", "Index")
		self.outputs.new("mn_IntegerSocket", "List Length")
		self.outputs.new("mn_EmptySocket", newListSocketName)
		self.outputs.new("mn_EmptySocket", newOptionSocketName)
		self.outputs.get(newListSocketName).hide = not self.allowNewList
		self.updateCallerNodes()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
	
		row.prop(self, "loopName", text = "")
		
		newNode = row.operator("node.add_node", text = "", icon = "PLUS")
		newNode.use_transform = True
		newNode.type = "mn_LoopCallerNode"
		setting = newNode.settings.add()
		setting.name = "selectedLoop"
		setting.value = repr(self.loopName)
		
	def draw_buttons_ext(self, context, layout):
		layout.prop(self, "allowNewList", text = "Allow New List")
		
	def execute(self, input):
		return input
		
	def update(self):
		forbidCompiling()
		
		# from list socket
		socket = self.outputs.get(newListSocketName)
		targetSocket = self.getValidTargetSocket(socket)
		if targetSocket is not None:
			socketType = self.getTargetSocketType(targetSocket)
			if hasListSocketType(socketType):
				newSocket = self.newOutputSocket(socketType, namePrefix = targetSocket.name)
				newSocket.loopAsList = True
				self.id_data.links.new(targetSocket, newSocket)
				newIndex = self.outputs.find(socket.name)
				self.outputs.move(len(self.outputs) - 1, newIndex)
				self.updateCallerNodes()
			else:
				self.id_data.links.remove(socket.links[0])
			
		# from single socket	
		socket = self.outputs.get(newOptionSocketName)
		targetSocket = self.getValidTargetSocket(socket)
		if targetSocket is not None:
			socketType = self.getTargetSocketType(targetSocket)
			newSocket = self.newOutputSocket(socketType, namePrefix = targetSocket.name)
			self.id_data.links.new(targetSocket, newSocket)
			newIndex = self.outputs.find(socket.name)
			self.outputs.move(len(self.outputs) - 1, newIndex)
			
			socketStartValue = (None, None)
			if targetSocket.bl_idname != "mn_EmptySocket":
				socketStartValue = (newSocket, targetSocket.getStoreableValue())
			self.updateCallerNodes(socketStartValue)
			
		allowCompiling()
		
	def getTargetSocketType(self, targetSocket):
		idName = targetSocket.bl_idname
		if idName == "mn_EmptySocket":
			if targetSocket.passiveSocketType != "":
				idName = targetSocket.passiveSocketType
		return idName
		
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
		
	def newOutputSocket(self, idName, namePrefix):		
		socket = self.outputs.new(idName, getNotUsedSocketName(self, prefix = "socket"))
		socket.customName = getNotUsedCustomSocketName(self, prefix = namePrefix)
		targetSocket = None
		socket.editableCustomName = True
		socket.callNodeWhenCustomNameChanged = True
		socket.removeable = True
		socket.callNodeToRemove = True
		return socket
		
	def customSocketNameChanged(self, socket):
		self.updateCallerNodes()
		
	def removeSocket(self, socket):
		self.outputs.remove(socket)
		self.updateCallerNodes()
		
	def updateCallerNodes(self, socketStartValue = (None, None)):
		nodes = getNodesFromTypeWithAttribute("mn_LoopCallerNode", "selectedLoop", self.loopName)
		for node in nodes:
			node.updateSockets(self, socketStartValue)
		nodeTreeChanged()
		
	def clearCallerNodes(self):
		nodes = getNodesFromTypeWithAttribute("mn_LoopCallerNode", "selectedLoop", self.loopName)
		for node in nodes:
			node.loopRemoved()
			
	def getSocketDescriptions(self):
		fromListSockets = []
		fromSingleSockets = []
		
		for i, socket in enumerate(self.outputs):
			if i > 1 and socket.bl_idname != "mn_EmptySocket":
				if socket.loopAsList: fromListSockets.append(socket)
				else: fromSingleSockets.append(socket)
			
		return (fromListSockets, fromSingleSockets)
		
	def buildPreset(self):
		self.removeDynamicSockets()
		if self.preset == "OBJECT":
			objectSocket = self.newOutputSocket("mn_ObjectSocket", namePrefix = "Object")
			objectSocket.loopAsList = True
			self.outputs.move(4, 2)
			self.allowNewList = False
		self.updateCallerNodes()
			
	def removeDynamicSockets(self):
		for socket in self.outputs:
			if socket.identifier not in ["Index", "List Length", newListSocketName, newOptionSocketName]:
				self.outputs.remove(socket)
	
	def copy(self, node):
		self.loopName = self.getNotUsedLoopName()
		
	def free(self):
		self.clearCallerNodes()
		
	def getNotUsedLoopName(self, prefix = "Loop"):
		loopName = prefix
		while getNodeFromTypeWithAttribute("mn_LoopStartNode", "loopName", loopName) not in [self, None]:
			loopName = prefix + getRandomString(3)
		return loopName