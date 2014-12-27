import bpy, bmesh
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_BMeshSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_BMeshSocket"
	bl_label = "BMesh Socket"
	dataType = "BMesh"
	allowedInputTypes = ["BMesh"]
	drawColor = (1.0, 0.9, 0.6, 1)
	
	def drawInput(self, layout, node, text):
		layout.prop(self, "color", text = text)
		
	def getValue(self):
		return bmesh.new()
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

