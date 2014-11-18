import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_BooleanSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_BooleanSocket"
	bl_label = "Boolean Socket"
	dataType = "Boolean"
	allowedInputTypes = ["Boolean"]
	drawColor = (0.5, 0.5, 0.2, 1)
	
	value = bpy.props.BoolProperty(default = True, update = nodePropertyChanged)
	
	def drawInput(self, layout, node, text):
		layout.prop(self, "value", text = text)
		
	def getValue(self):
		return self.value
		
	def setStoreableValue(self, data):
		self.value = data
		
	def getStoreableValue(self):
		return self.value


