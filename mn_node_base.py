import bpy
from mn_execution import nodeTreeChanged
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *

class AnimationNodeTree(bpy.types.NodeTree):
	bl_idname = "AnimationNodeTreeType"
	bl_label = "Animation";
	bl_icon = "ACTION"
	
	isAnimationNodeTree = bpy.props.BoolProperty(default = True)
	
	def update(self):
		nodeTreeChanged()
		
		
class AnimationNode:
	@classmethod
	def poll(cls, nodeTree):
		return nodeTree == "AnimationNodeTreeType"
		
		
def customNameChanged(self, context):
	if not self.customNameIsUpdating:
		self.customNameIsUpdating = True
		if self.customNameIsVariable:
			newCustomName = ""
			for char in self.customName:
				if char.isalpha(): newCustomName += char
			self.customName = newCustomName
		self.customNameIsUpdating = False
		nodeTreeChanged()
		
class mn_SocketProperties:
	editableCustomName = bpy.props.BoolProperty(default = False)
	customName = bpy.props.StringProperty(default = "custom name", update = customNameChanged)
	customNameIsVariable = bpy.props.BoolProperty(default = True)
	customNameIsUpdating = bpy.props.BoolProperty(default = False)
		
class mn_BaseSocket(NodeSocket):
	bl_idname = "mn_BaseSocket"
	bl_label = "Base Socket"
	
	def draw(self, context, layout, node, text):
		if self.editableCustomName:
			layout.prop(self, "customName", text = "")
		else:
			if not self.is_output and not isSocketLinked(self):
				self.drawInput(layout, node, text)
			else:
				layout.label(text)
			
	def draw_color(self, context, node):
		return self.drawColor