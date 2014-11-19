import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_VertexSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_VertexSocket"
	bl_label = "Vertex Socket"
	dataType = "Vertex"
	allowedInputTypes = ["Vertex"]
	drawColor = (0.6, 0.8, 0.36, 1)
	
	position = bpy.props.FloatVectorProperty(default = [0, 0, 0], update = nodePropertyChanged)
	normal = bpy.props.FloatVectorProperty(default = [0, 0, 1], update = nodePropertyChanged)
	
	setType = bpy.props.EnumProperty(default = "position", items = [("position", "Position", ""), ("normal", "Normal", "")], name = "Type")
	
	def drawInput(self, layout, node, text):
		col = layout.column(align = True)
		col.prop(self, "setType", text = "")
		col.prop(self, self.setType, index = 0, text = "X")
		col.prop(self, self.setType, index = 1, text = "Y")
		col.prop(self, self.setType, index = 2, text = "Z")
		col.separator()
		
	def getValue(self):
		# Position, Normal, From Object
		return [self.position, self.normal, 0, None]
		
	def setStoreableValue(self, data):
		self.position, self.normal = data
	def getStoreableValue(self):
		return [self.position, self.normal]

