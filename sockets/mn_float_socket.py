import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class FloatSocket(NodeSocket):
	bl_idname = "FloatSocket"
	bl_label = "Float Socket"
	dataType = "Float"
	allowedInputTypes = ["Float", "Integer"]
	
	number = bpy.props.FloatProperty(default = 0.0, update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			layout.prop(self, "number", text = text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.4, 0.4, 0.7, 1)
		
	def getValue(self):
		return self.number
		
	def setStoreableValue(self, data):
		self.number = data
	def getStoreableValue(self):
		return self.number
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)