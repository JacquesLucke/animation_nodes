import bpy
from bpy.types import Node
from mathutils import *
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_MatrixCombine(Node, AnimationNode):
	bl_idname = "mn_MatrixCombine"
	bl_label = "Combine Matrices"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		socket = self.inputs.new("mn_MatrixSocket", "Matrix")
		socket.removeable = True
		socket.callNodeToRemove = True
		self.inputs.new("mn_MatrixSocket", "Matrix").removeable = True
		socket.removeable = True
		socket.callNodeToRemove = True
		self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_MatrixSocket"
		self.outputs.new("mn_MatrixSocket", "Result")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def update(self):
		forbidCompiling()
		
		socket = self.inputs.get("...")
		updateDependencyNode(socket)
		
		if socket is not None:
			links = socket.links
			if len(links) == 1:
				link = links[0]
				fromSocket = link.from_socket
				originSocket = getOriginSocket(socket)
				self.id_data.links.remove(link)
				if originSocket is not None:
					if originSocket.dataType == "Matrix":
						self.inputs.remove(socket)
						newSocket = self.inputs.new("mn_MatrixSocket", "Matrix")
						newSocket.removeable = True
						newSocket.callNodeToRemove = True
						self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_MatrixSocket"
						self.id_data.links.new(newSocket, fromSocket)
		allowCompiling()
		
	def removeSocket(self, socket):
		forbidCompiling()
		self.inputs.remove(socket)
		allowCompiling()
		
	def execute(self, input):
		result = Matrix.Identity(4)
		
		sockets = self.inputs
		for socket in reversed(sockets):
			if socket.bl_idname == "mn_MatrixSocket":
				result *= input[socket.identifier]
		
		return { "Result" : result }

classes = [
	mn_MatrixCombine
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
