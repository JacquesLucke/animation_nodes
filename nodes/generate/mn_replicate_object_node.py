import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)

class ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	objectNames = bpy.props.CollectionProperty(type = ObjectNamePropertyGroup)
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("IntegerSocket", "Instances")
		self.outputs.new("ObjectListSocket", "Objects")
		
	def draw_buttons(self, context, layout):
		pass
		
	def execute(self, input):
		output = {}
		object = input["Object"]
		amount = max(input["Instances"], 0)
		while amount > len(self.objectNames):
			self.newInstance(object)
		while amount < len(self.objectNames):
			self.removeInstance()
			
		objects = []
		for item in self.objectNames:
			objects.append(bpy.data.objects.get(item.objectName))
			
		output["Objects"] = objects
		return output
		
	def free(self):
		while len(self.objectNames) > 0:
			self.removeInstance()
		
	def newInstance(self, object):
		newObject = object.copy()
		newObject.name = self.getPossibleInstanceName()
		bpy.context.scene.objects.link(newObject)
		item = self.objectNames.add()
		item.objectName = newObject.name
		return object
	def getPossibleInstanceName(self, name = "instance"):
		counter = 1
		while bpy.data.objects.get(name + str(counter)) is not None:
			counter += 1
		return name + str(counter)
	def removeInstance(self):
		if len(self.objectNames) > 0:
			object = bpy.data.objects.get(self.objectNames[0].objectName)
			if object is not None:
				object.name += "DELETED"
				bpy.context.scene.objects.unlink(object)
			self.objectNames.remove(0)
		
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