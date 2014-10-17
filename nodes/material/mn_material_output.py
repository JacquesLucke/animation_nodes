import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *

allowedSocketTypes = [ 
	"NodeSocketVector",
	"NodeSocketFloatFactor",
	"NodeSocketColor",
	"NodeSocketFloat" ]
					

class mn_MaterialOutputNode(Node, AnimationNode):
	bl_idname = "mn_MaterialOutputNode"
	bl_label = "Material Output"
	
	def getPossibleSockets(self, context):
		node = self.getSelectedNode()
		sockets = []
		for socket in node.inputs:
			if socket.bl_idname in allowedSocketTypes:
				sockets.append((socket.identifier, socket.identifier, ""))
		return sockets
		
	def selectedSocketChanged(self, context):
		self.setInputSocket()
		nodeTreeChanged()
	
	materialName = bpy.props.StringProperty(update = selectedSocketChanged)
	nodeName = bpy.props.StringProperty(update = selectedSocketChanged)
	socketIdentifier = bpy.props.EnumProperty(items = getPossibleSockets, name = "Socket", update = selectedSocketChanged)
	
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
			name = socket.bl_idname
			if name == "NodeSocketColor": self.inputs.new("mn_ColorSocket", "Data")
			elif name == "NodeSocketFloat": self.inputs.new("mn_FloatSocket", "Data")
			elif name == "NodeSocketFloatFactor": self.inputs.new("mn_FloatSocket", "Data")
			elif name == "NodeSocketVector": self.inputs.new("mn_VectorSocket", "Data")
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
			