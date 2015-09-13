import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... nodes.container_provider import getMainObjectContainer
from ... utils.names import (getPossibleObjectName,
                                     getPossibleMeshName,
                                     getPossibleCurveName,
                                     getPossibleCameraName,
                                     getPossibleLampName,
                                     getPossibleCurveName)

objectTypes = ["Mesh", "Text", "Camera", "Point Lamp", "Curve"]
objectTypeItems = [(type, type, "") for type in objectTypes]

class an_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
    objectName = StringProperty(name = "Object Name", default = "", update = propertyChanged)
    objectIndex = IntProperty(name = "Object Index", default = 0, update = propertyChanged)

class ObjectInstancerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectInstancerNode"
    bl_label = "Object Instancer"
    options = {"No Subprogram"}
    searchTags = ["Object Replicator (old)"]

    def copyFromSourceChanged(self, context):
        self.inputs["Source"].hide = not self.copyFromSource
        self.resetInstancesEvent(context)

    def resetInstancesEvent(self, context):
        self.resetInstances = True

    linkedObjects = CollectionProperty(type = an_ObjectNamePropertyGroup)
    resetInstances = BoolProperty(default = False, update = propertyChanged)
    sourceObjectHash = StringProperty()

    copyFromSource = BoolProperty(default = True, name = "Copy from Source", update = copyFromSourceChanged)
    deepCopy = BoolProperty(default = False, update = resetInstancesEvent, name = "Deep Copy", description = "Make the instances independent of the source object (e.g. copy mesh)")
    objectType = EnumProperty(default = "Mesh", name = "Object Type", items = objectTypeItems, update = resetInstancesEvent)
    copyObjectProperties = BoolProperty(default = False, update = resetInstancesEvent, description = "Enable this to copy modifiers/constrains/... from the source objec.)")

    parentInstances = BoolProperty(default = True, name = "Parent to Main Container", update = resetInstancesEvent)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Instances", "instancesAmount").minValue = 0
        self.inputs.new("an_ObjectSocket", "Source", "sourceObject").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_SceneSocket", "Scene", "scene").hide = True
        self.outputs.new("an_ObjectListSocket", "Objects", "objects")

    def draw(self, layout):
        layout.prop(self, "copyFromSource")
        if self.copyFromSource:
            layout.prop(self, "copyObjectProperties", text = "Copy Full Object")
            layout.prop(self, "deepCopy")
        else:
            layout.prop(self, "objectType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "parentInstances")

        self.invokeFunction(layout, "resetObjectDataOnAllInstances",
            text = "Reset Source Data",
            description = "Reset the source data on all instances")
        self.invokeFunction(layout, "unlinkInstancesFromNode",
            text = "Unlink Instances from Node",
            description = "This will make sure that the objects won't be removed if you remove the Replicate Node.")

    def execute(self, instancesAmount, sourceObject, scene):
        instancesAmount = max(instancesAmount, 0)

        if self.copyFromSource and sourceObject is not None:
            if self.sourceObjectHash != str(hash(sourceObject)):
                self.removeAllObjects()
                self.sourceObjectHash = str(hash(sourceObject))

        if self.copyFromSource and sourceObject is None or scene is None:
            self.removeAllObjects()
            return []

        if self.resetInstances:
            self.removeAllObjects()
            self.resetInstances = False

        while instancesAmount < len(self.linkedObjects):
            self.removeLastObject()

        return self.getOutputObjects(instancesAmount, sourceObject, scene)

    def getOutputObjects(self, instancesAmount, sourceObject, scene):
        objects = []
        objectAmount = len(bpy.data.objects)
        counter = 0

        self.updateFastListAccess()

        while(counter < instancesAmount):
            if counter < len(self.linkedObjectsList):
                object = self.getObjectFromItemIndex(counter, objectAmount)
                if object is None:
                    self.removeObjectFromItemIndex(counter)
                    self.updateFastListAccess()
            else:
                object = self.appendNewObject(sourceObject, scene)

            if object is not None:
                objects.append(object)
                counter += 1

        return objects

    def updateFastListAccess(self):
        self.linkedObjectsList = list(self.linkedObjects)
        self.objectList = list(bpy.data.objects)

    # at first try to get the object by index, because it's faster and then search by name
    def getObjectFromItemIndex(self, itemIndex, objectAmount):
        item = self.linkedObjectsList[itemIndex]
        if item.objectIndex < objectAmount:
            object = self.objectList[item.objectIndex]
            if object.name == item.objectName:
                return object

        index = bpy.data.objects.find(item.objectName)
        if index == -1: return None

        item.objectIndex = index
        return bpy.data.objects[index]

    def removeAllObjects(self):
        objectNames = []
        for item in self.linkedObjects:
            objectNames.append(item.objectName)

        for name in objectNames:
            object = bpy.data.objects.get(name)
            if object is not None:
                self.removeObject(object)

        self.linkedObjects.clear()

    def removeLastObject(self):
        self.removeObjectFromItemIndex(len(self.linkedObjects)-1)

    def removeObjectFromItemIndex(self, itemIndex):
        item = self.linkedObjects[itemIndex]
        objectName = item.objectName
        self.linkedObjects.remove(itemIndex)
        object = bpy.data.objects.get(objectName)
        if object is not None:
            self.removeObject(object)

    def removeObject(self, object):
        self.unlinkInstance(object)
        if object.users == 0:
            data = object.data
            type = object.type
            bpy.data.objects.remove(object)
            self.removeObjectData(data, type)

    def removeObjectData(self, data, type):
        if data.users == 0:
            if type == "MESH":
                bpy.data.meshes.remove(data)
            elif type == "CAMERA":
                bpy.data.cameras.remove(data)
            elif type in ["FONT", "CURVE", "SURFACE"]:
                bpy.data.curves.remove(data)
            elif type == "META":
                bpy.data.metaballs.remove(data)
            elif type == "ARMATURE":
                bpy.data.armatures.remove(data)
            elif type == "LATTICE":
                bpy.data.lattices.remove(data)
            elif type == "LAMP":
                bpy.data.lamps.remove(data)
            elif type == "SPEAKER":
                bpy.data.speakers.remove(data)

    def appendNewObject(self, sourceObject, scene):
        object = self.newInstance(sourceObject, scene)
        scene.objects.link(object)
        linkedItem = self.linkedObjects.add()
        linkedItem.objectName = object.name
        linkedItem.objectIndex = bpy.data.objects.find(object.name)
        return object

    def newInstance(self, sourceObject, scene):
        instanceData = self.getSourceObjectData(sourceObject)
        if self.copyObjectProperties and self.copyFromSource:
            newObject = sourceObject.copy()
            newObject.data = instanceData
        else:
            newObject = bpy.data.objects.new(getPossibleObjectName("instance"), instanceData)

        if self.parentInstances:
            newObject.parent = getMainObjectContainer(scene)
        return newObject

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
                return bpy.data.curves.new(getPossibleCurveName("instance text"), type = "FONT")
            elif self.objectType == "Camera":
                return bpy.data.cameras.new(getPossibleCameraName("instance camera"))
            elif self.objectType == "Point Lamp":
                return bpy.data.lamps.new(getPossibleLampName("instance lamp"), type = "POINT")
            elif self.objectType == "Curve":
                return bpy.data.curves.new(getPossibleCurveName("instance curve"), type = "CURVE")
        return None

    def unlinkInstance(self, object):
        if bpy.context.mode != "OBJECT" and bpy.context.active_object == object:
            bpy.ops.object.mode_set(mode = "OBJECT")
        for scene in bpy.data.scenes:
            if object.name in scene.objects:
                scene.objects.unlink(object)

    def resetObjectDataOnAllInstances(self):
        self.resetInstances = True

    def unlinkInstancesFromNode(self):
        self.linkedObjects.clear()
        self.inputs.get("Instances").number = 0

    def delete(self):
        self.removeAllObjects()

    def duplicate(self, sourceNode):
        self.linkedObjects.clear()
