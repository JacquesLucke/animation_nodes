import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_ObjectListSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_ObjectListSocket"
	bl_label = "Object List Socket"
	dataType = "Object List"
	allowedInputTypes = ["Object List"]
	drawColor = (0, 0, 0, 0.4)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []


classes = [
	mn_ObjectListSocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
