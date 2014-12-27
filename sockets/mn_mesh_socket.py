import bpy, bmesh
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_MeshSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_MeshSocket"
	bl_label = "Mesh Socket"
	dataType = "Mesh"
	allowedInputTypes = ["Mesh"]
	drawColor = (1.0, 0.9, 0.6, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return bmesh.new()
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

