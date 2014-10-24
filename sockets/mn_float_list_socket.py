import bpy
from mn_execution import nodePropertyChanged
from mn_node_base import * 

class mn_FloatListSocket(mn_BaseSocket):
	bl_idname = "mn_FloatListSocket"
	bl_label = "Float List Socket"
	dataType = "Float List"
	allowedInputTypes = ["Float List"]
	drawColor = (0.4, 0.4, 0.7, 0.4)
	
	def drawInput(self, layout, node, text):
		layout.label(text)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []