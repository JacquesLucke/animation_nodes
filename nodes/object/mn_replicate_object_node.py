import bpy, time
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_helper import *
from mn_object_utils import *
from mn_cache import *

class mn_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Object Name", default = "", update = nodePropertyChanged)
	objectIndex = bpy.props.IntProperty(name = "Object Index", default = 0, update = nodePropertyChanged)

class mn_ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "mn_ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	objectNames = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	visibleObjectNames = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	setObjectData = bpy.props.BoolProperty(default = False)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_IntegerSocket", "Instances")
		self.outputs.new("mn_ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		setData = layout.operator("mn.set_object_data_on_all_objects")
		setData.nodeTreeName = self.id_data.name
		setData.nodeName = self.name
		
	def getInputSocketNames(self):
		return {"Object" : "sourceObject",
				"Instances" : "instances"}
	def getOutputSocketNames(self):
		return {"Objects" : "objects",}
		
	def execute(self, sourceObject, instances):
		instances = max(instances, 0)
		
		if sourceObject is None:
			while 0 < len(self.visibleObjectNames):
				self.unlinkObjectFromScene()
			return []
		
		self.linkCorrectAmountOfObjects(instances, sourceObject)
		objects = []
		allObjects = bpy.data.objects
		for i in range(instances):
			item = self.visibleObjectNames[i]
			name = item.objectName
			object = allObjects[item.objectIndex]
			if object.name != name:
				index = allObjects.find(name)
				item.objectIndex = index
				object = allObjects[index]
				print("hey")
			objects.append(object)
			
		if self.setObjectData:
			for object in objects:
				if object.data != sourceObject.data:
					object.data = sourceObject.data
			self.setObjectData = False
		
		return objects
		
	def linkCorrectAmountOfObjects(self, instances, object):
		while instances < len(self.visibleObjectNames):
			self.unlinkObjectFromScene()
		while instances > len(self.visibleObjectNames):
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
		
	def setObjectDataOnAllObjects(self):
		self.setObjectData = True
			
			
	def free(self):
		while len(self.visibleObjectNames) > 0:
			self.unlinkObjectFromScene()
			
	def copy(self, node):
		self.objectNames.clear()
		self.visibleObjectNames.clear()
		
class SetObjectDataOnAllObjects(bpy.types.Operator):
	bl_idname = "mn.set_object_data_on_all_objects"
	bl_label = "Set Correct Mesh"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.setObjectDataOnAllObjects()
		return {'FINISHED'}