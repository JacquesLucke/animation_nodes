import bpy
from mn_execution import nodeTreeChanged

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
	
	
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)