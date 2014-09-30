import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
from mn_execution import nodePropertyChanged

class ObjectInputNode(Node, AnimationNode):
	bl_idname = "ObjectInputNode"
	bl_label = "Object"
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("ObjectSocket", "Object")
		
	def draw_buttons(self, context, layout):
		col = layout.column()
		row = col.row(align = True)
		row.prop(self, "objectName", text = "")
		selector = row.operator("mn.assign_active_object_to_node", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = self.id_data.name
		selector.nodeName = self.name
		selector.target = "objectName"
		col.separator()
		
	def execute(self, input):
		output = {}
		output["Object"] = self.objectName
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)