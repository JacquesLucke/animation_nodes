import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

def getValue(self):
	return min(max(self.min, self.get("number", 0)), self.max)
def setValue(self, value):
	self["number"] = min(max(self.min, value), self.max)

class mn_IntegerSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_IntegerSocket"
	bl_label = "Integer Socket"
	dataType = "Integer"
	allowedInputTypes = ["Integer"]
	drawColor = (0.2, 0.2, 1.0, 1.0)
	
	number = bpy.props.IntProperty(default = 0, update = nodePropertyChanged, set = setValue, get = getValue)
	showName = bpy.props.BoolProperty(default = True)
	
	min = bpy.props.IntProperty(default = -10000000)
	max = bpy.props.IntProperty(default = 10000000)
	
	def drawInput(self, layout, node, text):
		if not self.showName: text = ""
		layout.prop(self, "number", text = text)
	
	def getValue(self):
		return self.number
		
	def setStoreableValue(self, data):
		self.number = data
	def getStoreableValue(self):
		return self.number
		
	def setMinMax(self, min, max):
		self.min = min
		self.max = max
		


