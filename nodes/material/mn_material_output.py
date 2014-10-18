import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *

allowedSocketTypes = { 
	"NodeSocketVector" : "mn_VectorSocket",
	"NodeSocketColor" : "mn_ColorSocket",
	"NodeSocketFloatFactor" : "mn_FloatSocket",
	"NodeSocketFloat" : "mn_FloatSocket" }
					

class mn_CyclesMaterialOutputNode(Node, AnimationNode):
	bl_idname = "mn_CyclesMaterialOutputNode"
	bl_label = "Cycles Material Output"
	
	def getPossibleSocketItems(self, context):
		sockets = self.getPossibleSockets()
		items = []
		for socket in sockets:
			if socket.bl_idname in allowedSocketTypes.keys():
				items.append((socket.identifier, socket.identifier, ""))
		return items
	def getPossibleSockets(self):
		node = self.getSelectedNode()
		identifiers = []
		for socket in node.inputs:
			if socket.bl_idname in allowedSocketTypes.keys():
				identifiers.append(socket)
		return identifiers
		
	def selectedSocketChanged(self, context):
		self.socketIsChanging = True
		self.setInputSocket()
		self.socketIsChanging = False
		nodeTreeChanged()
	
	materialName = bpy.props.StringProperty(update = selectedSocketChanged)
	nodeName = bpy.props.StringProperty(update = selectedSocketChanged)
	socketIdentifier = bpy.props.EnumProperty(items = getPossibleSocketItems, name = "Socket", update = selectedSocketChanged)
	socketIsChanging = bpy.props.BoolProperty()
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Data")
		allowCompiling()
	
	def draw_buttons(self, context, layout): 
		layout.prop_search(self, 'materialName', bpy.data, 'materials', text='', icon='MATERIAL_DATA')
		material = bpy.data.materials.get(self.materialName)
		if material is not None:
			nodeTree = material.node_tree
			layout.prop_search(self, 'nodeName', nodeTree, 'nodes', text='', icon='NODE')
			node = material.node_tree.nodes.get(self.nodeName)
			if node is not None:
				layout.prop(self, "socketIdentifier", text = "")
		
	def execute(self, input):
		output = {}
		data = input["Data"]
		socket = self.getSelectedSocket()
		if socket is not None:
			try:
				socket.default_value = data
			except:
				pass
		return output
		
	def update(self):
		socket = self.inputs.get("Data")
		if socket is not None and not self.socketIsChanging:
			if hasLinks(socket):
				fromType = self.inputs[0].links[0].from_socket.bl_idname
				possibleIdentifiers = self.getInputIdentifiersFromSocketType(fromType)
				if self.inputs["Data"].bl_idname != fromType and len(possibleIdentifiers) > 0:
					self.socketIdentifier = possibleIdentifiers[0]
					self.setInputSocket()
		
	def getInputIdentifiersFromSocketType(self, searchType):
		identifiers = []
		sockets = self.getPossibleSockets()
		for socket in sockets:
			if allowedSocketTypes[socket.bl_idname] == searchType:
				identifiers.append(socket.identifier)
		return identifiers
		
	def getSelectedNode(self):
		material = bpy.data.materials.get(self.materialName)
		if material is not None:
			node = material.node_tree.nodes.get(self.nodeName)
			return node
		return None
		
	def getSelectedSocket(self):
		node = self.getSelectedNode()
		if node is not None:
			socket = self.getInputSocketWithIdentifier(node, self.socketIdentifier)
			return socket
		return None
			
	def getInputSocketWithIdentifier(self, node, identifier):
		for socket in node.inputs:
			if socket.identifier == identifier: return socket
		return None
		
	def setInputSocket(self):
		forbidCompiling()
		socket = self.getSelectedSocket()
		connections = getConnectionDictionaries(self)
		self.inputs.clear()
		if socket is None:
			self.inputs.new("mn_GenericSocket", "Data")
		else:
			data = socket.default_value
			self.inputs.new(allowedSocketTypes[socket.bl_idname], "Data")
			self.inputs["Data"].setStoreableValue(data)
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
			