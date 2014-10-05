import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class SubProgramSocket(NodeSocket):
	bl_idname = "SubProgramSocket"
	bl_label = "Sub Program Socket"
	dataType = "SubProgram"
	allowedInputTypes = ["all"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.9, 0.3, 0.3, 1)
		
	def getValue(self):
		return ""
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)