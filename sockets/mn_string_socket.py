import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class StringSocket(NodeSocket):
	bl_idname = "StringSocket"
	bl_label = "String Socket"
	dataType = "String"
	allowedInputTypes = ["String", "Object"]
	
	string = bpy.props.StringProperty(default = "Text", update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			layout.prop(self, "string", text = text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (1, 1, 1, 1)
		
	def getValue(self):
		return self.string
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)