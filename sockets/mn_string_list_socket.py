import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_StringListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_StringListSocket"
	bl_label = "String List Socket"
	dataType = "String List"
	allowedInputTypes = ["String List"]
	drawColor = (1, 1, 1, 0.4)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []

