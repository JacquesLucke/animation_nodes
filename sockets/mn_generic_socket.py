import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class mn_GenericSocket(NodeSocket):
	bl_idname = "mn_GenericSocket"
	bl_label = "Generic Socket"
	dataType = "Generic"
	allowedInputTypes = ["all"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.6, 0.3, 0.3, 0.7)
		
	def getValue(self):
		return None
		
	def setStoreableValue(self, data):
		pass
	def getStoreableValue(self):
		return None
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)