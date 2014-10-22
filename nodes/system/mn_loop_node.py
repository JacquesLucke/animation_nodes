import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_dynamic_sockets_helper import *

class mn_LoopNode(Node, AnimationNode):
	bl_idname = "mn_LoopNode"
	bl_label = "Loop"
	
	def getSubProgramNames(self, context):
		nodeTree = self.id_data
		subProgramNames = []
		for node in nodeTree.nodes:
			if node.bl_idname == "mn_LoopStartNode": subProgramNames.append((node.loopName, node.loopName, ""))
		return subProgramNames
	def selectedProgramChanged(self, context):
		rebuildSockets(self)
	
	loopsEnum = bpy.props.EnumProperty(items = getSubProgramNames, name = "Loop", update=selectedProgramChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Amount")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		row.prop(self, "loopsEnum")
		newNode = row.operator("node.add_node", text = "", icon = "PLUS")
		newNode.use_transform = True
		newNode.type = "mn_LoopStartNode"
		rebuild = layout.operator("mn.rebuild_sub_program_caller_sockets", "Rebuild Sockets")
		rebuild.nodeTreeName = self.id_data.name
		rebuild.nodeName = self.name
		
	def removeDynamicSockets(self):
		self.outputs.clear()
		for i, socket in enumerate(self.inputs):
			if i > 0: self.inputs.remove(socket)	

	def getStartNode(self):
		loopName = self.loopsEnum
		for node in self.id_data.nodes:
			if node.bl_idname == "mn_LoopStartNode":
				if node.loopName == loopName:
					return node
		return None
