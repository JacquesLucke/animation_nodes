import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class SubProgramStartNode(Node, AnimationNode):
	bl_idname = "SubProgramStartNode"
	bl_label = "Sub-Program Start"
	
	def init(self, context):
		self.outputs.new("SubProgramSocket", "Sub-Program")
		self.outputs.new("IntegerSocket", "Index")
		
	def draw_buttons(self, context, layout):
		layout.label("Add New Socket")
		
		objectList = layout.operator("mn.new_sub_program_socket", text = "Object List")
		objectList.nodeTreeName = self.id_data.name
		objectList.nodeName = self.name
		objectList.socketType = "ObjectListSocket"
		
		objectList = layout.operator("mn.new_sub_program_socket", text = "Float")
		objectList.nodeTreeName = self.id_data.name
		objectList.nodeName = self.name
		objectList.socketType = "FloatSocket"
		
	def execute(self, input):
		return input
		
	def newSocket(self, socketType):
		self.outputs.new(socketType, self.getPossibleName("Socket"))
	def getPossibleName(self, name):
		counter = 1
		while self.outputs.get(name + " " + str(counter)) is not None:
			counter += 1
		
		return name + " " + str(counter)
		
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
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)