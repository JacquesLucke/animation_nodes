import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_IntegerList2DSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_IntegerList2DSocket"
	bl_label = "Integer List 2D Socket"
	dataType = "Integer List 2D"
	allowedInputTypes = ["Integer List 2D"]
	drawColor = (0.5, 0.7, 0.7, 1.0)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []

