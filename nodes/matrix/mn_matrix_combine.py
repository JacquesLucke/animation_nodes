import bpy
from bpy.types import Node
from mathutils import *
from mn_utils import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_MatrixCombine(Node, AnimationNode):
	bl_idname = "mn_MatrixCombine"
	bl_label = "Combine Matrices"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_MatrixSocket", "1.")
		self.inputs.new("mn_MatrixSocket", "2.")
		self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_MatrixSocket"
		self.outputs.new("mn_MatrixSocket", "Result")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def update(self):
		forbidCompiling()
		socket = self.inputs.get("...")
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
						newSocketName = str(len(self.inputs) + 1) + "."
						newSocket = self.inputs.new("mn_MatrixSocket", newSocketName)
						self.inputs.new("mn_EmptySocket", "...")
						self.id_data.links.new(newSocket, fromSocket)
				
		allowCompiling()
		
	def execute(self, input):
		result = Matrix.Identity(4)
		
		sockets = self.inputs
		for socket in reversed(sockets):
			if socket.bl_idname == "mn_MatrixSocket":
				result *= input[socket.name]
		
		return { "Result" : result }