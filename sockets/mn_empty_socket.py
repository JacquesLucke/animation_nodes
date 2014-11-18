import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_EmptySocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_EmptySocket"
	bl_label = "Empty Socket"
	dataType = "Empty"
	allowedInputTypes = ["all"]
	drawColor = (0.0, 0.0, 0.0, 0.0)
	
	passiveSocketType = bpy.props.StringProperty(default = "")
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return None
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return None

classes = [
	mn_EmptySocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
