import bpy
from mn_execution import nodePropertyChanged
from mn_node_base import * 

class mn_StringSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_StringSocket"
	bl_label = "String Socket"
	dataType = "String"
	allowedInputTypes = ["String", "Object"]
	drawColor = (1, 1, 1, 1)
	
	string = bpy.props.StringProperty(default = "", update = nodePropertyChanged)
	
	def drawInput(self, layout, node, text):
		layout.prop(self, "string", text = text)
		
	def getValue(self):
		return self.string
		
	def setStoreableValue(self, data):
		self.string = data
	def getStoreableValue(self):
		return self.string