import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class GenericSocket(NodeSocket):
	bl_idname = "GenericSocket"
	bl_label = "Generic Socket"
	dataType = "Generic"
	allowedInputTypes = ["Generic", "Integer", "Float", "Vector", "String", "Object"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.6, 0.3, 0.3, 0.7)
		
	def getValue(self):
		return 0
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)