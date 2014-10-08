import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class VectorSocket(NodeSocket):
	bl_idname = "VectorSocket"
	bl_label = "Vector Socket"
	dataType = "Vector"
	allowedInputTypes = ["Vector"]
	
	vector = bpy.props.FloatVectorProperty(default = (0, 0, 0), update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			col = layout.column(align = True)
			col.label(text)
			col.prop(self, "vector", index = 0, text = "X")
			col.prop(self, "vector", index = 1, text = "Y")
			col.prop(self, "vector", index = 2, text = "Z")
			col.separator()
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.05, 0.05, 0.8, 0.7)
		
	def getValue(self):
		return self.vector
		
	def setStoreableValue(self, data):
		self.vector = data
	def getStoreableValue(self):
		return self.vector
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)