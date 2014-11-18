import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_GenericSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_GenericSocket"
	bl_label = "Generic Socket"
	dataType = "Generic"
	allowedInputTypes = ["all"]
	drawColor = (0.6, 0.3, 0.3, 0.7)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return None
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return None

classes = [
	mn_GenericSocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
