import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged


class mn_FloatListSocket(NodeSocket):
	bl_idname = "mn_FloatListSocket"
	bl_label = "Float List Socket"
	dataType = "Float List"
	allowedInputTypes = ["Float List"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.4, 0.4, 0.7, 0.4)
		
	def getValue(self):
		return []
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return []
		
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)