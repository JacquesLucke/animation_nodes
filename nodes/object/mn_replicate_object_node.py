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
		cleanupNode = layout.operator("mn.cleanup_replicator_node")
		cleanupNode.nodeTreeName = self.id_data.name
		cleanupNode.nodeName = self.name
		
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
		objectAmount = len(allObjects)
		for i in range(instances):
			item = self.visibleObjectNames[i]
			name = item.objectName
			if item.objectIndex < objectAmount:
				object = allObjects[item.objectIndex]
				if object.name != name:
					object = self.getObjectAndCorrectIndex(name, item, allObjects)
			else:
				object = self.getObjectAndCorrectIndex(name, item, allObjects)
			objects.append(object)
			
		if self.setObjectData:
			for object in objects:
				if object.data != sourceObject.data:
					object.data = sourceObject.data
			self.setObjectData = False
		
		return objects
		
	def getObjectAndCorrectIndex(self, objectName, item, allObjects):
		index = allObjects.find(objectName)
		item.objectIndex = index
		object = allObjects[index]
		return object
		
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
			try:
				bpy.context.scene.objects.link(object)
			except: pass
			item = self.visibleObjectNames.add()
			item.objectName = object.name
			
	def unlinkObjectFromScene(self):
		if len(self.visibleObjectNames) > 0:
			object = bpy.data.objects.get(self.visibleObjectNames[-1].objectName)
			if object is not None:
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
		
	def cleanup(self):
		removeIndices = []
		for i, item in enumerate(self.objectNames):
			object = bpy.data.objects.get(item.objectName)
			if object is None or item.objectIndex == -1:
				removeIndices.append(i)
		for index in removeIndices:
			self.objectNames.remove(index)
			
		removeIndices = []
		for i, item in enumerate(self.visibleObjectNames):
			object = bpy.data.objects.get(item.objectName)
			if object is None or item.objectIndex == -1:
				removeIndices.append(i)
		for alreadyRemoved, index in enumerate(removeIndices):
			self.visibleObjectNames.remove(index - alreadyRemoved)
			
			
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
		
class CleanupReplicatorNode(bpy.types.Operator):
	bl_idname = "mn.cleanup_replicator_node"
	bl_label = "Cleanup"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.cleanup()
		return {'FINISHED'}