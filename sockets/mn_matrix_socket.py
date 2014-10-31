import bpy
from mn_execution import nodePropertyChanged
from mn_node_base import * 

class mn_MatrixSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_MatrixSocket"
	bl_label = "Matrix Socket"
	dataType = "Matrix"
	allowedInputTypes = ["Matrix"]
	drawColor = (1, 0.56, 0.3, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return self.string
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass