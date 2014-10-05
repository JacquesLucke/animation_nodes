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
		
	def update(self):
		if hasLinks(self.inputs["Sub-Program"]):
			startNode = self.inputs["Sub-Program"].links[0].from_node
			for i, output in enumerate(startNode.outputs):
				if i >= 2:
					if len(self.inputs) > i:
						if self.inputs[i].name != output.name:
							self.inputs.remove(self.inputs[i])
							self.inputs.new(output.bl_idname, output.name)
							self.outputs.remove(self.inputs[i])
							self.outputs.new(output.bl_idname, output.name)
					else:
						self.inputs.new(output.bl_idname, output.name)
						self.outputs.new(output.bl_idname, output.name)
					

		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)