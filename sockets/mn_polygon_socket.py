import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_PolygonSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PolygonSocket"
	bl_label = "Polygon Socket"
	dataType = "Polygon"
	allowedInputTypes = ["Polygon"]
	drawColor = (0.14, 0.34, 0.19, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		# [center, normal, area, material_index]
		return [[0, 0, 0], [0, 0, 1], 0.0, 0]
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return None

classes = [
	mn_PolygonSocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
