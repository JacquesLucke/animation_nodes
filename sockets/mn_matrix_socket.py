import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *
from mathutils import Matrix

class mn_MatrixSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_MatrixSocket"
	bl_label = "Matrix Socket"
	dataType = "Matrix"
	allowedInputTypes = ["Matrix"]
	drawColor = (1, 0.56, 0.3, 1)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return Matrix.Identity(4)
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		pass

classes = [
	mn_MatrixSocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
