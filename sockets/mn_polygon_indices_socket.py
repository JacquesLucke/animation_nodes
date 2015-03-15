import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_PolygonIndicesSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PolygonIndicesSocket"
	bl_label = "Polygon Indices Socket"
	dataType = "Polygon Indices"
	allowedInputTypes = ["Polygon Indices"]
	drawColor = (0.5, 0.8, 0.4, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return (0, 1, 2)
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

	def getCopyValueFunctionString(self):
		return "return value[:]"
