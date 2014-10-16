import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

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
	
	materialName = bpy.props.StringProperty(update = nodePropertyChanged)
	nodeName = bpy.props.StringProperty(update = nodePropertyChanged)
	socketIdentifier = bpy.props.EnumProperty(items = getPossibleSockets, name = "Socket", update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("GenericSocket", "Data")
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
				# correct color by adding alpha channel
				if socket.bl_idname == "NodeSocketColor" and len(data) == 3:
					data = [data[0], data[1], data[2], 1.0]
					
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