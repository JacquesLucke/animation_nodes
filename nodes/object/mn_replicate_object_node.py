import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_helper import *
from mn_object_utils import *
from mn_cache import *

class mn_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)

class mn_ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "mn_ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	objectNames = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	visibleObjectNames = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_IntegerSocket", "Instances")
		self.outputs.new("mn_ObjectListSocket", "Objects")
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
		
		self.linkCorrectAmountOfObjects(amount, object)
			
		objects = []
		for i in range(amount):
			outputObject = bpy.data.objects.get(self.visibleObjectNames[i].objectName)
			if outputObject is not None:
				if outputObject.data != object.data:
					outputObject.data = object.data
				objects.append(outputObject)
			
		output["Objects"] = objects
		return output
		
	def linkCorrectAmountOfObjects(self, amount, object):
		while amount < len(self.visibleObjectNames):
			self.unlinkObjectFromScene()
		while amount > len(self.visibleObjectNames):
			self.linkObjectToScene(object)
			
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
		
	def newInstance(self, object):
		newObject = bpy.data.objects.new(getPossibleObjectName("instance"), object.data)
		newObject.parent = getMainObjectContainer()
		item = self.objectNames.add()
		item.objectName = newObject.name
		return object
			
	def free(self):
		while len(self.visibleObjectNames) > 0:
			self.unlinkObjectFromScene()
			
	def copy(self, node):
		self.objectNames.clear()
		self.visibleObjectNames.clear()