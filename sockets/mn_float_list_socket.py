import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class FloatPropertyGroup(bpy.types.PropertyGroup):
	value = bpy.props.FloatProperty(name = "Value", default = 0)

class FloatListSocket(NodeSocket):
	bl_idname = "FloatListSocket"
	bl_label = "Float List Socket"
	dataType = "Float List"
	allowedInputTypes = ["Float List"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.4, 0.4, 0.7, 0.4)
		
	def getValue(self):
		return [0]
		
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)