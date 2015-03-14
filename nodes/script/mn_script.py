import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import NodeTreeInfo

emptySocketName = "New Socket"

class mn_ScriptNode(Node, AnimationNode):
	bl_idname = "mn_ScriptNode"
	bl_label = "Script"
	
	textBlockName = bpy.props.StringProperty(name = "Script", default = "", description = "Choose")
	
	def init(self, context):
		forbidCompiling()
		self.createEmptySockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		operator = layout.operator("mn.open_new_script", text = "New Script")
		operator.nodeTreeName = self.id_data.name
		operator.nodeName = self.name
			
	# def getInputSocketNames(self):
		# return {socket.identifier: socket.customName for socket in self.inputs}
	# def getOutputSocketNames(self):
		# return {socket.identifier: socket.customName for socket in self.outputs}
		
	def update(self):
		forbidCompiling()
		nodeTreeInfo = NodeTreeInfo(self.id_data)
		for sockets in (self.inputs, self.outputs):
			emptySocket = sockets.get(emptySocketName)
			if emptySocket:
				linkedDataSocket = nodeTreeInfo.getFirstLinkedSocket(emptySocket)
				if linkedDataSocket:
					link = emptySocket.links[0]
					type = linkedDataSocket.bl_idname
					if type != "mn_EmptySocket":
						newSocket = self.appendSocket(sockets, linkedDataSocket.bl_idname, linkedDataSocket.name)
						linkedSocket = self.getSocketFromOtherNode(link)
						self.id_data.links.remove(link)
						self.makeLink(newSocket, linkedSocket)
		allowCompiling()
		
	def createEmptySockets(self):
		for sockets in (self.inputs, self.outputs):
			socket = sockets.new("mn_EmptySocket", emptySocketName)
			socket.passiveSocketType = "mn_GenericSocket"
			socket.customName = "EMPTYSOCKET"
			
	def appendSocket(self, sockets, type, name):
		socket = sockets.new(type, name)
		self.setupNewSocket(socket, name)
		sockets.move(len(sockets)-1, len(sockets)-2)
		return socket
		
	def setupNewSocket(self, socket, name):
		socket.editableCustomName = True
		socket.customName = name
		socket.customNameIsVariable = True
		socket.removeable = True
		
	def getSocketFromOtherNode(self, link):
		if link.from_node == self:
			return link.to_socket
		return link.from_socket
		
	def makeLink(self, socketA, socketB):
		if socketA.is_output:
			self.id_data.links.new(socketB, socketA)
		else:
			self.id_data.links.new(socketA, socketB)
		
	def execute(self, inputs):
		outputs = {}
		return outputs
		
		
class OpenNewScript(bpy.types.Operator):
	bl_idname = "mn.open_new_script"
	bl_label = "New Keyframe"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()

	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		textBlock = bpy.data.texts.new("script")
		
		return {'FINISHED'}		