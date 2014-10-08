import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_helper import *

class ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)

class ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	objectNames = bpy.props.CollectionProperty(type = ObjectNamePropertyGroup)
	visibleObjectNames = bpy.props.CollectionProperty(type = ObjectNamePropertyGroup)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("IntegerSocket", "Instances")
		self.outputs.new("ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def execute(self, input):
		output = {}
		object = input["Object"]
		amount = max(input["Instances"], 0)
		
		if object is None:
			while 0 < len(self.visibleObjectNames):
				self.unlinkObjectFromScene()
			return { "Objects" : [] }
		
		while amount < len(self.visibleObjectNames):
			self.unlinkObjectFromScene()
		
		while amount > len(self.visibleObjectNames):
			self.linkObjectToScene(object)
			
		objects = []
		for i in range(amount):
			outputObject = bpy.data.objects.get(self.visibleObjectNames[i].objectName)
			if outputObject is not None:
				if outputObject.data != object.data:
					outputObject.data = object.data
				objects.append(outputObject)
			
		output["Objects"] = objects
		return output
		
	def free(self):
		while len(self.visibleObjectNames) > 0:
			self.unlinkObjectFromScene()
			
	def copy(self, node):
		self.objectNames.clear()
		self.visibleObjectNames.clear()
		
	def newInstance(self, object):
		newObject = bpy.data.objects.new(self.getPossibleInstanceName(), object.data)
		newObject.parent = getMainObjectContainer()
		item = self.objectNames.add()
		item.objectName = newObject.name
		return object
	def getPossibleInstanceName(self, name = "instance"):
		randomString = getRandomString(3)
		counter = 1
		while bpy.data.objects.get(name + randomString + str(counter)) is not None:
			counter += 1
		return name + randomString + str(counter)
		
	def linkObjectToScene(self, object):
		if len(self.objectNames) == len(self.visibleObjectNames):
			self.newInstance(object)
		object = bpy.data.objects.get(self.objectNames[len(self.visibleObjectNames)].objectName)
		if object is None:
			self.objectNames.remove(len(self.visibleObjectNames))
		else:
			bpy.context.scene.objects.link(object)
			item = self.visibleObjectNames.add()
			item.objectName = object.name
	def unlinkObjectFromScene(self):
		if len(self.visibleObjectNames) > 0:
			object = bpy.data.objects.get(self.visibleObjectNames[-1].objectName)
			bpy.context.scene.objects.unlink(object)
			self.visibleObjectNames.remove(len(self.visibleObjectNames) - 1)
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)