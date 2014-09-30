import bpy

class AnimationNode:
	@classmethod
	def poll(cls, nodeTree):
		return nodeTree == "AnimationNodeTreeType"
				

class AssignActiveObjectToNode(bpy.types.Operator):
	bl_idname = "mn.assign_active_object_to_node"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		setattr(node, self.target, obj.name)
		return {'FINISHED'}		

	
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)