import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_dynamic_sockets_helper import *

class EnumerateObjectsNode(Node, AnimationNode):
	bl_idname = "EnumerateObjectsNode"
	bl_label = "Loop Objects"
	
	def getEnumerateObjectStartNodeNames(self, context):
		nodeTree = self.id_data
		subProgramNames = []
		for node in nodeTree.nodes:
			if node.bl_idname == "EnumerateObjectsStartNode": subProgramNames.append((node.subProgramName, node.subProgramName, ""))
		return subProgramNames
	def selectedProgramChanged(self, context):
		rebuildSockets(self)
	
	subProgramsEnum = bpy.props.EnumProperty(items = getEnumerateObjectStartNodeNames, name = "Sub-Programs", update=selectedProgramChanged)
	
	def init(self, context):
		self.inputs.new("ObjectListSocket", "Objects")
		self.outputs.new("ObjectListSocket", "Objects")
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		
		row.prop(self, "subProgramsEnum", text = "")
		newNode = row.operator("node.add_node", text = "", icon = "PLUS")
		newNode.use_transform = True
		newNode.type = "EnumerateObjectsStartNode"
		
		rebuild = layout.operator("mn.rebuild_sub_program_caller_sockets", "Rebuild Sockets")
		rebuild.nodeTreeName = self.id_data.name
		rebuild.nodeName = self.name
		
	def removeDynamicSockets(self):
		for i, socket in enumerate(self.inputs):
			if i > 0: self.inputs.remove(socket)	
		for i, socket in enumerate(self.outputs):
			if i > 0: self.outputs.remove(socket)

	def getStartNode(self):
		subProgramsName = self.subProgramsEnum
		for node in self.id_data.nodes:
			if node.bl_idname == "EnumerateObjectsStartNode":
				if node.subProgramName == subProgramsName:
					return node
		return None
					

		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)