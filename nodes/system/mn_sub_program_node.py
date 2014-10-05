import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class SubProgramNode(Node, AnimationNode):
	bl_idname = "SubProgramNode"
	bl_label = "Sub-Program"
	
	def init(self, context):
		self.inputs.new("SubProgramSocket", "Sub-Program")
		self.inputs.new("IntegerSocket", "Amount")
		
	def draw_buttons(self, context, layout):
		rebuild = layout.operator("mn.rebuild_sub_program_sockets", "Rebuild Sockets")
		rebuild.nodeTreeName = self.id_data.name
		rebuild.nodeName = self.name
						
	def rebuildSubProgramSockets(self):
		self.removeDynamicSockets()
		if hasLinks(self.inputs["Sub-Program"]):
			startNode = self.inputs["Sub-Program"].links[0].from_node
			for i, output in enumerate(startNode.outputs):
				if i >= 2:
					self.inputs.new(output.bl_idname, output.name)
					self.outputs.new(output.bl_idname, output.name)
	def removeDynamicSockets(self):
		self.outputs.clear()
		for i, socket in enumerate(self.inputs):
			if i >= 2: self.inputs.remove(socket)
					

		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)