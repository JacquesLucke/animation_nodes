import bpy, random
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_MultiMathNode(Node, AnimationNode):
	bl_idname = "mn_MultiMathNode"
	bl_label = "Multi Math"
	node_category = "Math"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "1.")
		self.inputs.new("mn_FloatSocket", "2.")
		self.inputs.new("mn_EmptySocket", "...")
		self.outputs.new("mn_FloatSocket", "Result")
		allowCompiling()
		
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
					if originSocket.dataType in ["Float", "Integer"]:
						self.inputs.remove(socket)
						newSocketName = str(len(self.inputs) + 1) + "."
						newSocket = self.inputs.new("mn_FloatSocket", newSocketName)
						self.inputs.new("mn_EmptySocket", "...")
						self.id_data.links.new(newSocket, fromSocket)
				
		allowCompiling()
		
	def execute(self, inputs):
		output = {}
		return output
		