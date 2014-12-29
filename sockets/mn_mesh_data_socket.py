import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *
from animation_nodes.utils.mn_mesh_utils import MeshData

class mn_MeshDataSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_MeshDataSocket"
	bl_label = "Mesh Data Socket"
	dataType = "Mesh Data"
	allowedInputTypes = ["Mesh Data"]
	drawColor = (0.3, 0.4, 0.18, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return MeshData()
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

