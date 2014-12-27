import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *
from mathutils import Matrix

class mn_PolygonListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PolygonListSocket"
	bl_label = "Polygon List Socket"
	dataType = "Polygon List"
	allowedInputTypes = ["Polygon List"]
	drawColor = (0.25, 0.55, 0.23, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

