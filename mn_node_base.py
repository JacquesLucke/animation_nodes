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
		
		
class mn_BaseSocket(NodeSocket):
	bl_idname = "mn_BaseSocket"
	bl_label = "Base Socket"
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			self.drawInput(layout, node, text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return self.drawColor