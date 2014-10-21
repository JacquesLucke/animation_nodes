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
	
	linkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	unlinkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
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
			self.unlinkAllObjects()
			return []
			
		while instances < len(self.linkedObjects):
			self.unlinkOneObject()
			
			
		objects = []
		allObjects = bpy.data.objects
		objectAmount = len(allObjects)
		
		outputObjectCounter = 0
		currentIndex = 0
		while(outputObjectCounter < instances):
			useObject = False
			incrementIndex = True
			if currentIndex < len(self.linkedObjects):
				item = self.linkedObjects[currentIndex]
				searchName = item.objectName
				if item.objectIndex < objectAmount:
					object = allObjects[item.objectIndex]
					if object.name == searchName: useObject = True
					else:
						index = allObjects.find(searchName)
						if index != -1:
							item.objectIndex = index
							object = allObjects[index]
							useObject = True
						else:
							self.unlinkObjectItemIndex(currentIndex)
							incrementIndex = False
				else: # duplicated code. have to find a cleaner solution
					index = allObjects.find(searchName)
					if index != -1:
						item.objectIndex = index
						object = allObjects[index]
						useObject = True
					else:
						self.unlinkObjectItemIndex(currentIndex)
						incrementIndex = False
			else:
				object = self.linkNextObjectToScene(sourceObject)
				useObject = True
				incrementIndex = False
			
			if useObject: 
				objects.append(object)
				outputObjectCounter += 1
			if incrementIndex: currentIndex += 1
		
		if self.setObjectData:
			for object in objects:
				if object.data != sourceObject.data:
					object.data = sourceObject.data
			self.setObjectData = False
		
		return objects
		
	def unlinkAllObjects(self):
		while len(self.linkedObjects) > 0:
			self.unlinkObjectItemIndex(0)
		self.linkedObjects.clear()
		
	def unlinkOneObject(self):
		self.unlinkObjectItemIndex(0)
		
	def unlinkObjectItemIndex(self, itemIndex):
		item = self.linkedObjects[itemIndex]
		object = bpy.data.objects.get(item.objectName)
		if object is not None:
			try:
				bpy.context.scene.objects.unlink(object)
				newItem = self.unlinkedObjects.add()
				newItem.objectName = item.objectName
				newItem.objectIndex = item.objectIndex
			except: pass
		self.linkedObjects.remove(itemIndex)
			
	def linkNextObjectToScene(self, sourceObject):
		isNewObjectLinked = False
		while not isNewObjectLinked:
			if len(self.unlinkedObjects) == 0:
				self.newReplication(sourceObject)
			item = self.unlinkedObjects[0]
			object = bpy.data.objects.get(item.objectName)
			if object is not None:
				bpy.context.scene.objects.link(object)
				linkedItem = self.linkedObjects.add()
				linkedItem.objectName = item.objectName
				linkedItem.objectIndex = item.objectIndex
				isNewObjectLinked = True
			self.unlinkedObjects.remove(0)
		return object
			
	def newReplication(self, sourceObject):
		newObject = bpy.data.objects.new(getPossibleObjectName("instance"), sourceObject.data)
		newObject.parent = getMainObjectContainer()
		item = self.unlinkedObjects.add()
		item.objectName = newObject.name
		item.objectIndex = 0
		
	def setObjectDataOnAllObjects(self):
		self.setObjectData = True
			
	def free(self):
		self.unlinkAllObjects()
			
	def copy(self, node):
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
		
class SetObjectDataOnAllObjects(bpy.types.Operator):
	bl_idname = "mn.set_object_data_on_all_objects"
	bl_label = "Set Correct Mesh"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.setObjectDataOnAllObjects()
		return {'FINISHED'}