import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_MeshSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_MeshSocket"
	bl_label = "Mesh Socket"
	dataType = "Mesh"
	allowedInputTypes = ["Mesh"]
	drawColor = (0.27, 0.34, 0.14, 1)
	
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
		object = bpy.data.objects.get(self.objectName)
		if object is not None:
			data = object.data
			if isinstance(data, bpy.types.Mesh):
				return data
		return None
		
	def setStoreableValue(self, data):
		self.objectName = data
	def getStoreableValue(self):
		return self.objectName

