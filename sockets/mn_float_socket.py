import bpy
from mn_execution import nodePropertyChanged
from mn_node_base import * 

class mn_FloatSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_FloatSocket"
	bl_label = "Float Socket"
	dataType = "Float"
	allowedInputTypes = ["Float", "Integer"]
	drawColor = (0.4, 0.4, 0.7, 1)
	
	number = bpy.props.FloatProperty(default = 0.0, update = nodePropertyChanged)
	showName = bpy.props.BoolProperty(default = True)
	
	def drawInput(self, layout, node, text):
		if not self.showName: text = ""
		layout.prop(self, "number", text = text)
	
	def getValue(self):
		return self.number
		
	def setStoreableValue(self, data):
		self.number = data
	def getStoreableValue(self):
		return self.number