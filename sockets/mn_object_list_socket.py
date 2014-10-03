import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged


class ObjectListSocket(NodeSocket):
	bl_idname = "ObjectListSocket"
	bl_label = "Object List Socket"
	dataType = "Object List"
	allowedInputTypes = ["Object List"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0, 0, 0, 0.4)
		
	def getValue(self):
		return [""]
		
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
