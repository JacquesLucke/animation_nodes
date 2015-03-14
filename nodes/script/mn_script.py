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
	
	textBlockName = bpy.props.StringProperty(name = "Script", default = "", description = "Choose the script you want to execute in this node")
	errorMessage = bpy.props.StringProperty(name = "Error Message", default = "")
	
	def init(self, context):
		forbidCompiling()
		self.createEmptySockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		row.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")  
		operator = row.operator("mn.open_new_script", text = "", icon = "PLUS")
		operator.nodeTreeName = self.id_data.name
		operator.nodeName = self.name
		
		if self.errorMessage != "":
			layout.label(self.errorMessage, icon = "ERROR")
		
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
		self.errorMessage = ""
		textBlock = bpy.data.texts.get(self.textBlockName)
		if textBlock:
			scriptLocals = {}
			for socket in self.inputs:
				if socket.name == emptySocketName: continue
				scriptLocals[socket.customName] = inputs[socket.identifier]
			
			script = textBlock.as_string()
			
			try:
				exec(script, {}, scriptLocals)
				for socket in self.outputs:
					if socket.name == emptySocketName: continue
					outputs[socket.identifier] = scriptLocals[socket.customName]
			except BaseException as e:
				self.errorMessage = str(e)
				for socket in self.outputs:
					if socket.identifier not in outputs:
						outputs[socket.identifier] = socket.getValue()
		return outputs
		
		
class OpenNewScript(bpy.types.Operator):
	bl_idname = "mn.open_new_script"
	bl_label = "New Keyframe"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()

	def invoke(self, context, event):
		node = getNode(self.nodeTreeName, self.nodeName)
		textBlock = bpy.data.texts.new("script")
		node.textBlockName = textBlock.name
		
		if event.ctrl or event.shift or event.alt:
			area = bpy.context.area
			area.type = "TEXT_EDITOR"
			area.spaces.active.text = textBlock
			bpy.ops.screen.area_split(direction = "HORIZONTAL", factor = 0.7)
			area.type = "NODE_EDITOR"
			
		return {'FINISHED'}		
		
	def getAreaByType(self, type):
		for area in bpy.context.screen.areas:
			if area.type == type: return area
		return None