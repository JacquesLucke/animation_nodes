import bpy, re
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import NodeTreeInfo
from animation_nodes.utils.mn_name_utils import getPossibleSocketName
from animation_nodes.sockets.mn_socket_info import getSocketNameItems, getSocketNameByDataType

emptySocketName = "New Socket"

class mn_ScriptNode(Node, AnimationNode):
	bl_idname = "mn_ScriptNode"
	bl_label = "Script"
	
	def makeFromClipboardChanged(self, context):
		if self.makeFromClipboard:
			self.buildFromText(context.window_manager.clipboard)
			
	def hideEditableElementsChanged(self, context):
		hide = self.hideEditableElements
		for socket in list(self.inputs) + list(self.outputs):
			if socket.name == emptySocketName:
				socket.hide = hide
			else:
				socket.editableCustomName = not hide
				socket.removeable = not hide
	
	textBlockName = bpy.props.StringProperty(name = "Script", default = "", description = "Choose the script you want to execute in this node")
	errorMessage = bpy.props.StringProperty(name = "Error Message", default = "")
	selectedSocketType = bpy.props.EnumProperty(name = "Selected Socket Type", items = getSocketNameItems)
	makeFromClipboard = bpy.props.BoolProperty(default = False, update = makeFromClipboardChanged)
	hideEditableElements = bpy.props.BoolProperty(name = "Hide Editable Elements", default = False, update = hideEditableElementsChanged)
	
	def init(self, context):
		forbidCompiling()
		self.createEmptySockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if not self.hideEditableElements:
			row = layout.row(align = True)
			row.prop_search(self, "textBlockName",  bpy.data, "texts", text = "")  
			operator = row.operator("mn.open_new_script", text = "", icon = "PLUS")
			operator.nodeTreeName = self.id_data.name
			operator.nodeName = self.name
			
		if self.errorMessage != "":
			layout.label(self.errorMessage, icon = "ERROR")
			
		if not self.hideEditableElements:
			layout.separator()
			
	def draw_buttons_ext(self, context, layout):
		col = layout.column(align = True)
		col.label("New Socket")
		col.prop(self, "selectedSocketType", text = "")
		
		row = col.row(align = True)
		
		operator = row.operator("mn.append_socket_to_script_node", text = "Input")
		operator.nodeTreeName = self.id_data.name
		operator.nodeName = self.name
		operator.makeOutputSocket = False
		
		operator = row.operator("mn.append_socket_to_script_node", text = "Output")
		operator.nodeTreeName = self.id_data.name
		operator.nodeName = self.name
		operator.makeOutputSocket = True
		
		operator = layout.operator("mn.export_script_node")
		operator.nodeTreeName = self.id_data.name
		operator.nodeName = self.name
		
		layout.prop(self, "hideEditableElements")
		
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
		socket.callNodeWhenCustomNameChanged = True
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
		
		scriptLocals = {}
		for socket in self.inputs:
			if socket.name == emptySocketName: continue
			scriptLocals[socket.customName] = inputs[socket.identifier]
		
		try:
			exec(self.getScript(), {}, scriptLocals)
			for socket in self.outputs:
				if socket.name == emptySocketName: continue
				outputs[socket.identifier] = scriptLocals[socket.customName]
		except BaseException as e:
			self.errorMessage = str(e)
			for socket in self.outputs:
				if socket.identifier not in outputs:
					outputs[socket.identifier] = socket.getValue()
		return outputs
		
	def getScript(self):
		textBlock = bpy.data.texts.get(self.textBlockName)
		if textBlock:
			return textBlock.as_string()
		return ""
		
	def buildFromText(self, text):
		lines = text.split("\n")
		state = "none"
		
		scriptLines = []
		
		for line in lines:
			if state == "none":
				if re.match("[Ii]nputs:", line): 
					state = "inputs"
					continue
			elif state == "inputs":
				if re.match("[Oo]utputs:", line): 
					state = "outputs"
					continue
				match = re.search("\s*(\w+)\s*-\s*(.+)", line)
				if match:
					self.appendSocket(self.inputs, getSocketNameByDataType(match.group(2).strip()), match.group(1))
			elif state == "outputs":
				if re.match("[Ss]cript:", line): 
					state = "script"
					continue
				match = re.search("\s*(\w+)\s*-\s*(.+)", line)
				if match:
					self.appendSocket(self.outputs, getSocketNameByDataType(match.group(2).strip()), match.group(1))
			elif state == "script":
				scriptLines.append(line)
				
		scriptText = "\n".join(scriptLines)
		textBlock = self.getTextBlockWithText(scriptText)
		self.textBlockName = textBlock.name
		self.hideEditableElements = True
		
	def customSocketNameChanged(self, socket):
		forbidCompiling()
		socket.name = socket.customName
		allowCompiling()
		
	def getTextBlockWithText(self, text):
		for textBlock in bpy.data.texts:
			if len(textBlock.as_string()) == len(text):
				return textBlock
		textBlock = bpy.data.texts.new("script")
		textBlock.from_string(text)
		return textBlock
		
		
class OpenNewScript(bpy.types.Operator):
	bl_idname = "mn.open_new_script"
	bl_label = "New Keyframe"
	bl_description = "Create a new text block (hold ctrl to open a new text editor)"
	
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
		
		
class AppendSocket(bpy.types.Operator):
	bl_idname = "mn.append_socket_to_script_node"
	bl_label = "Append Socket to Script Node"
	bl_description = "Append a new socket to this node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	makeOutputSocket = bpy.props.BoolProperty()

	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		type = getSocketNameByDataType(node.selectedSocketType)
		if self.makeOutputSocket:
			node.appendSocket(node.outputs, type, getPossibleSocketName(node, "socket"))
		else:
			node.appendSocket(node.inputs, type, getPossibleSocketName(node, "socket"))
			
		return {'FINISHED'}	
		
		
class ExportScriptNode(bpy.types.Operator):
	bl_idname = "mn.export_script_node"
	bl_label = "Export Script Node"
	bl_description = "Copy a text that describes the full script node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()

	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		socketLines = []
		socketLines.append("Inputs:")
		for socket in node.inputs[:-1]:
			socketLines.append(socket.customName + " - " + socket.dataType)
		socketLines.append("\nOutputs:")
		for socket in node.outputs[:-1]:
			socketLines.append(socket.customName + " - " + socket.dataType)
			
		scriptText = "Script:\n"
		scriptText += node.getScript()
			
		exportText = "\n".join(socketLines)	+ "\n\n" + scriptText	
		context.window_manager.clipboard = exportText
		return {'FINISHED'}			