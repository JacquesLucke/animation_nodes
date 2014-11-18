import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_VertexListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_VertexListSocket"
	bl_label = "Vertex List Socket"
	dataType = "Vertex List"
	allowedInputTypes = ["Vertex List"]
	drawColor = (0.3, 1.0, 0.4, 1.0)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []

