import bpy
from mn_execution import nodePropertyChanged
from mn_node_base import * 

class mn_ObjectSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_ObjectSocket"
	bl_label = "Object Socket"
	dataType = "Object"
	allowedInputTypes = ["Object", "String"]
	drawColor = (0, 0, 0, 1)
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	showName = bpy.props.BoolProperty(default = True)
	
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if self.showName:
			row.label(text)
		row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")  
		selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = node.id_data.name
		selector.nodeName = node.name
		selector.isOutput = self.is_output
		selector.socketName = self.name
		selector.target = "objectName"
		col.separator()
		
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