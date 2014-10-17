import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class mn_ObjectSocket(NodeSocket):
	bl_idname = "mn_ObjectSocket"
	bl_label = "Object Socket"
	dataType = "Object"
	allowedInputTypes = ["Object", "String"]
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	showName = bpy.props.BoolProperty(default = False)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			col = layout.column()
			row = col.row(align = True)
			if self.showName:
				row.label(text)
			row.prop(self, "objectName", text = "")
			selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
			selector.nodeTreeName = node.id_data.name
			selector.nodeName = node.name
			selector.isOutput = self.is_output
			selector.socketName = self.name
			selector.target = "objectName"
			col.separator()
		else:
			layout.label(text)
		
	def draw_color(self, context, node):
		return (0, 0, 0, 1)
		
	def getValue(self):
		return bpy.data.objects.get(self.objectName)
		
	def setStoreableValue(self, data):
		self.objectName = data
	def getStoreableValue(self):
		return self.objectName
	
	
class AssignActiveObjectToNode(bpy.types.Operator):
	bl_idname = "mn.assign_active_object_to_socket"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	isOutput = bpy.props.BoolProperty()
	socketName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		socket = getSocketFromNode(node, self.isOutput, self.socketName)
		setattr(socket, self.target, obj.name)
		return {'FINISHED'}
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)