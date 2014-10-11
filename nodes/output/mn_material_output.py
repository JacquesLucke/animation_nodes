import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

allowedSocketTypes = [ 
	"NodeSocketVector",
	"NodeSocketFloatFactor",
	"NodeSocketColor",
	"NodeSocketFloat" ]
					

class MaterialOutputNode(Node, AnimationNode):
	bl_idname = "MaterialOutputNode"
	bl_label = "Material Output"
	
	def getPossibleSockets(self, context):
		node = self.getSelectedNode()
		sockets = []
		for socket in node.inputs:
			if socket.bl_idname in allowedSocketTypes:
				sockets.append((socket.identifier, socket.identifier, ""))
		return sockets
	
	materialName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	socketIdentifier = bpy.props.EnumProperty(items = getPossibleSockets, name = "Socket")
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Data")
	
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
		socket = self.getSelectedSocket()
		if socket is not None:
			socket.default_value = input["Data"]
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
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)