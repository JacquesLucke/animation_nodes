import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_ObjectListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_ObjectListSocket"
	bl_label = "Object List Socket"
	dataType = "Object List"
	allowedInputTypes = ["Object List"]
	drawColor = (0, 0, 0, 0.4)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []

	def getCopyValueFunctionString(self):
		return "return value[:]"

