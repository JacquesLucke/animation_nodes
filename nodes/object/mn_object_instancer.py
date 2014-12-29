import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.nodes.mn_node_helper import *
from animation_nodes.utils.mn_name_utils import *
from animation_nodes.mn_cache import *

objectTypes = ["Mesh", "Text"]
objectTypeItems = [(type, type, "") for type in objectTypes]

class mn_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Object Name", default = "", update = nodePropertyChanged)
	objectIndex = bpy.props.IntProperty(name = "Object Index", default = 0, update = nodePropertyChanged)

class mn_ObjectInstancer(Node, AnimationNode):
	bl_idname = "mn_ObjectInstancer"
	bl_label = "Object Instancer"
	
	def copyTypeChanged(self, context):
		self.free()
		nodePropertyChanged(self, context)
		
	def copyFromSourceChanged(self, context):
		self.inputs["Source"].hide = not self.copyFromSource
		nodePropertyChanged(self, context)
		
	def objectTypeChanged(self, context):
		self.resetObjectData = True
		nodePropertyChanged(self, context)
	
	linkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	unlinkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	resetObjectData = bpy.props.BoolProperty(default = False, update = nodePropertyChanged)
	
	copyFromSource = bpy.props.BoolProperty(default = True, name = "Copy from Source", update = copyFromSourceChanged)
	deepCopy = bpy.props.BoolProperty(default = False, update = copyTypeChanged, name = "Deep Copy", description = "Use this to copy all data to the new object (to unlink it from the source mesh for example)")
	objectType = bpy.props.EnumProperty(default = "Mesh", name = "Object Type", items = objectTypeItems, update = objectTypeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Instances").setMinMax(0, 100000)
		self.inputs.new("mn_ObjectSocket", "Source").showName = False
		self.outputs.new("mn_ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "copyFromSource")
		if self.copyFromSource:
			layout.prop(self, "deepCopy")
		else:
			layout.prop(self, "objectType", text = "")
		
	def draw_buttons_ext(self, context, layout):
		setData = layout.operator("mn.reset_object_data_on_all_objects")
		setData.nodeTreeName = self.id_data.name
		setData.nodeName = self.name
	
		unlink = layout.operator("mn.unlink_instances_from_node")
		unlink.nodeTreeName = self.id_data.name
		unlink.nodeName = self.name
		
	def getInputSocketNames(self):
		return {"Instances" : "instances",
				"Source" : "sourceObject"}
	def getOutputSocketNames(self):
		return {"Objects" : "objects",}
		
	def execute(self, instances, sourceObject):
		instances = max(instances, 0)
			
		if self.copyFromSource and sourceObject is None:
			self.free()
			return []
			
		if self.resetObjectData:
			self.free()
			self.resetObjectData = False
			
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
		
		return objects
		
	def unlinkAllObjects(self):
		objectNames = []
		for item in self.linkedObjects:
			objectNames.append(item.objectName)
			
		for name in objectNames:
			object = bpy.data.objects.get(name)
			if object is not None:
				self.unlinkInstance(object)
		
	def unlinkOneObject(self):
		self.unlinkObjectItemIndex(len(self.linkedObjects)-1)
		
	def unlinkObjectItemIndex(self, itemIndex):
		item = self.linkedObjects[itemIndex]
		objectName = item.objectName
		objectIndex = item.objectIndex
		self.linkedObjects.remove(itemIndex)
		object = bpy.data.objects.get(objectName)
		if object is not None:
			try:
				self.unlinkInstance(object)
				newItem = self.unlinkedObjects.add()
				newItem.objectName = objectName
				newItem.objectIndex = objectIndex
			except: pass
			
	def linkNextObjectToScene(self, sourceObject):
		isNewObjectLinked = False
		while not isNewObjectLinked:
			if len(self.unlinkedObjects) == 0:
				self.newInstance(sourceObject)
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
			
	def newInstance(self, sourceObject):
		data = self.getSourceObjectData(sourceObject)
		newObject = bpy.data.objects.new(getPossibleObjectName("instance"), data)
		newObject.parent = getMainObjectContainer()
		item = self.unlinkedObjects.add()
		item.objectName = newObject.name
		item.objectIndex = 0
		
	def getSourceObjectData(self, sourceObject):
		if self.copyFromSource:
			if self.deepCopy:
				return sourceObject.data.copy()
			else:
				return sourceObject.data
		else:
			if self.objectType == "Mesh":
				return bpy.data.meshes.new(getPossibleMeshName("instance mesh"))
			elif self.objectType == "Text":
				return bpy.data.curves.new(getPossibleCurveName("text curve"), type = "FONT")
		return None
		
	def unlinkInstance(self, object):
		if bpy.context.mode != "OBJECT" and getActive() == object: bpy.ops.object.mode_set(mode = "OBJECT")
		bpy.context.scene.objects.unlink(object)
		
	def resetObjectDataOnAllInstances(self):
		self.resetObjectData = True
		
	def unlinkInstancesFromNode(self):
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
		self.inputs.get("Instances").number = 0
			
	def free(self):
		self.unlinkAllObjects()
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
			
	def copy(self, node):
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
		
class ResetObjectDataOnAllInstances(bpy.types.Operator):
	bl_idname = "mn.reset_object_data_on_all_objects"
	bl_label = "Reset Source Data"
	bl_description = "Reset the source data on all instances"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.resetObjectDataOnAllInstances()
		return {'FINISHED'}
		
class UnlinkInstancesFromNode(bpy.types.Operator):
	bl_idname = "mn.unlink_instances_from_node"
	bl_label = "Unlink Instances from Node"
	bl_description = "This will make sure that the objects won't be removed if you remove the Replicate Node."
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.unlinkInstancesFromNode()
		return {'FINISHED'}

