import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_PolygonIndicesListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PolygonIndicesListSocket"
	bl_label = "Polygon Indices List Socket"
	dataType = "Polygon Indices List"
	allowedInputTypes = ["Polygon Indices List"]
	drawColor = (0.4, 0.2, 1.0, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

	def getCopyValueFunctionString(self):
		return "return [polygonIndices[:] for polygonIndices in value]"
