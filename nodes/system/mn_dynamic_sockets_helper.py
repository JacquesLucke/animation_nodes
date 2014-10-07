import bpy
from mn_execution import nodePropertyChanged
from mn_utils import *

addSocketList = [
	("Object List", "ObjectListSocket"),
	("String List", "StringListSocket"),
	("Float", "FloatSocket"),
	("Text", "StringSocket"),
	("Object", "ObjectSocket") ]

def getAddSocketList():
	return addSocketList

class SocketPropertyGroup(bpy.types.PropertyGroup):
	socketName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)
	socketType = bpy.props.StringProperty(name = "Socket Type", default = "", update = nodePropertyChanged)

class NewSubProgramSocketNode(bpy.types.Operator):
	bl_idname = "mn.new_sub_program_socket"
	bl_label = "New Sub-Program Socket"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	socketType = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.newSocket(self.socketType)
		return {'FINISHED'}
		
class RebuildSubProgramSockets(bpy.types.Operator):
	bl_idname = "mn.rebuild_sub_program_sockets"
	bl_label = "Rebuild Sub-Program Sockets"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.rebuildSubProgramSockets()
		return {'FINISHED'}	
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)