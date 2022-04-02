import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... utils.names import getRandomString
from ... utils.blender_ui import iterActiveSpacesByType
from ... utils.data_blocks import removeNotUsedDataBlock
from ... nodes.container_provider import getMainObjectContainer
from ... utils.names import (getPossibleMeshName,
                             getPossibleCameraName,
                             getPossibleLightName,
                             getPossibleCurveName,
                             getPossibleGreasePencilName)

lastSourceHashes = {}
lastContainerHashes = {}

objectTypeItems = [
    ("MESH", "Mesh", "", "MESH_DATA", 0),
    ("TEXT", "Text", "", "FONT_DATA", 1),
    ("CAMERA", "Camera", "", "CAMERA_DATA", 2),
    ("POINT_LAMP", "Point Lamp", "", "LIGHT_POINT", 3),
    ("CURVE_2D", "Curve 2D", "", "FORCE_CURVE", 4),
    ("CURVE_3D", "Curve 3D", "", "CURVE_DATA", 5),
    ("EMPTY", "Empty", "", "EMPTY_DATA", 6),
    ("GREASE_PENCIL", "Grease Pencil", "", "OUTLINER_DATA_GREASEPENCIL", 7),
]

containerTypeItems = (
    ("COLLECTIONS", "Collections", "Link the objects to all input collections", 0),
    ("SCENES", "Scenes", "Link the objects to the scene collection of all input scenes", 1),
    ("MAIN_CONTAINER", "Main Container", "Link the objects to a collection created by "
        "Animation Nodes in all input scenes", 2),
)

emptyDisplayTypeItems = []
for item in bpy.types.Object.bl_rna.properties["empty_display_type"].enum_items:
    emptyDisplayTypeItems.append((item.identifier, item.name, ""))

class ObjectPropertyGroup(bpy.types.PropertyGroup):
    bl_idname = "an_ObjectPropertyGroup"
    object: PointerProperty(type = bpy.types.Object, name = "Object")

class ObjectInstancerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectInstancerNode"
    bl_label = "Object Instancer"
    bl_width_default = 160
    options = {"NOT_IN_SUBPROGRAM"}

    def copyFromSourceChanged(self, context):
        self.refresh()
        self.resetInstancesEvent(context)

    def resetInstancesEvent(self, context):
        self.resetInstances = True
        propertyChanged()

    def resetInstancesEventAndRefresh(self, context):
        self.resetInstancesEvent(context)
        self.refresh()

    linkedObjects: CollectionProperty(type = ObjectPropertyGroup)
    resetInstances: BoolProperty(default = False, update = propertyChanged)

    copyFromSource: BoolProperty(name = "Copy from Source",
        default = True, update = copyFromSourceChanged)

    deepCopy: BoolProperty(name = "Deep Copy", default = False, update = resetInstancesEvent,
        description = "Make the instances independent of the source object (e.g. copy mesh)")

    objectType: EnumProperty(name = "Object Type", default = "MESH",
        items = objectTypeItems, update = resetInstancesEvent)

    copyObjectProperties: BoolProperty(name = "Copy Full Object", default = False,
        description = "Enable this to copy modifiers/constraints/... from the source object",
        update = resetInstancesEvent)

    removeAnimationData: BoolProperty(name = "Remove Animation Data", default = True,
        description = "Remove the active action on the instance; This is useful when you want to animate the object yourself",
        update = resetInstancesEvent)

    containerType: EnumProperty(name = "Container Type", description = "The type of container the objects will be linked to",
        items = containerTypeItems, default = "MAIN_CONTAINER", update = resetInstancesEventAndRefresh)

    emptyDisplayType: EnumProperty(name = "Empty Draw Type", default = "PLAIN_AXES",
        items = emptyDisplayTypeItems, update = resetInstancesEvent)

    def create(self):
        self.newInput("Integer", "Instances", "instancesAmount", minValue = 0)
        if self.copyFromSource:
            self.newInput("Object", "Source", "sourceObject",
                defaultDrawType = "PROPERTY_ONLY", showHideToggle = True)
        if self.containerType in ("SCENES", "MAIN_CONTAINER"):
            self.newInput("Scene List", "Scenes", "scenes", hide = True)
        elif self.containerType == "COLLECTIONS":
            self.newInput("Collection List", "Collections", "collections", hide = True)

        self.newOutput("an_ObjectListSocket", "Objects", "objects")

    def draw(self, layout):
        layout.prop(self, "copyFromSource")
        if self.copyFromSource:
            layout.prop(self, "copyObjectProperties", text = "Copy Full Object")
            layout.prop(self, "deepCopy")
        else:
            layout.prop(self, "objectType", text = "")
            if self.objectType == "Empty":
                layout.prop(self, "emptyDisplayType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "containerType")
        layout.prop(self, "removeAnimationData")

        self.invokeFunction(layout, "resetObjectDataOnAllInstances",
            text = "Reset Source Data",
            description = "Reset the source data on all instances")
        self.invokeFunction(layout, "unlinkInstancesFromNode",
            confirm = True,
            text = "Unlink Instances from Node",
            description = "This will make sure that the objects won't be removed if you remove the Instancer Node")

    def getExecutionCode(self, required):
        if self.containerType in ("SCENES", "MAIN_CONTAINER"): yield "containers = set(scenes)"
        elif self.containerType == "COLLECTIONS": yield "containers = set(collections)"

        if self.copyFromSource:
            yield "objects = self.getInstances_WithSource(instancesAmount, sourceObject, containers)"
        else:
            yield "objects = self.getInstances_WithoutSource(instancesAmount, containers)"

    def getInstances_WithSource(self, instancesAmount, sourceObject, containers):
        if sourceObject is None:
            self.removeAllObjects()
            return []
        else:
            sourceHash = hash(sourceObject)
            if self.identifier in lastSourceHashes:
                if lastSourceHashes[self.identifier] != sourceHash:
                    self.removeAllObjects()
            lastSourceHashes[self.identifier] = sourceHash

        return self.getInstances_Base(instancesAmount, sourceObject, containers)

    def getInstances_WithoutSource(self, instancesAmount, containers):
        return self.getInstances_Base(instancesAmount, None, containers)

    def getInstances_Base(self, instancesAmount, sourceObject, containers):
        instancesAmount = max(instancesAmount, 0)

        if not any(containers):
            self.removeAllObjects()
            return []
        else:
            containerHashes = set(hash(container) for container in containers)
            if self.identifier in lastContainerHashes:
                if lastContainerHashes[self.identifier] != containerHashes:
                    self.removeAllObjects()
            lastContainerHashes[self.identifier] = containerHashes

        if self.resetInstances:
            self.removeAllObjects()
            self.resetInstances = False

        self.removeObjectsInRange(instancesAmount, len(self.linkedObjects))

        return self.getOutputObjects(instancesAmount, sourceObject, containers)


    def getOutputObjects(self, instancesAmount, sourceObject, containers):
        objects = []

        for i, objectGroup in enumerate(self.linkedObjects):
            object = objectGroup.object
            if object is None:
                self.linkedObjects.remove(i)
            else:
                objects.append(object)

        missingAmount = instancesAmount - len(objects)
        if missingAmount == 0:
            return objects

        newObjects = self.createNewObjects(missingAmount, sourceObject, containers)
        objects.extend(newObjects)

        return objects

    def removeAllObjects(self):
        for objectGroup in self.linkedObjects:
            object = objectGroup.object
            if object is not None:
                self.removeObject(object)

        self.linkedObjects.clear()

    def removeObjectsInRange(self, start, end):
        for i in reversed(range(start, end)):
            self.removeObjectAtIndex(i)

    def removeObjectAtIndex(self, index):
        object = self.linkedObjects[index].object
        if object is not None:
            self.removeObject(object)
        self.linkedObjects.remove(index)

    def removeObject(self, object):
        data = object.data
        type = object.type
        self.removeShapeKeys(object)
        bpy.data.objects.remove(object)
        self.removeObjectData(data, type)

    def removeObjectData(self, data, type):
        if data is None: return # the object was an empty
        if data.an_data.removeOnZeroUsers and data.users == 0:
            removeNotUsedDataBlock(data, type)

    def removeShapeKeys(self, object):
        # don't remove the shape key if it is used somewhere else
        if object.type not in ("MESH", "CURVE", "LATTICE"): return
        if object.data.shape_keys is None: return
        if object.data.shape_keys.user.users > 1: return

        object.active_shape_key_index = 0
        while object.active_shape_key is not None:
            object.shape_key_remove(object.active_shape_key)

    def createNewObjects(self, amount, sourceObject, containers):
        objects = []
        nameSuffix = "instance_{}_".format(getRandomString(5))
        for i in range(amount):
            name = nameSuffix + str(i)
            newObject = self.appendNewObject(name, sourceObject, containers)
            objects.append(newObject)
        return objects

    def appendNewObject(self, name, sourceObject, containers):
        object = self.newInstance(name, sourceObject)
        self.linkObject(object, containers)
        self.linkedObjects.add().object = object
        return object

    def linkObject(self, object, containers):
        if self.containerType == "MAIN_CONTAINER":
            self.linkObjectToMainContainer(object, containers)
        elif self.containerType == "SCENES":
            self.linkObjectToScenes(object, containers)
        else:
            self.linkObjectToCollections(object, containers)

    def linkObjectToMainContainer(self, object, scenes):
        for scene in scenes:
            if scene is None: continue
            getMainObjectContainer(scene).objects.link(object)

    def linkObjectToScenes(self, object, scenes):
        for scene in scenes:
            if scene is None: continue
            scene.collection.objects.link(object)

    def linkObjectToCollections(self, object, collections):
        for collection in collections:
            if collection is None: continue
            collection.objects.link(object)

    def newInstance(self, name, sourceObject):
        instanceData = self.getSourceObjectData(sourceObject)
        if self.copyObjectProperties and self.copyFromSource:
            newObject = sourceObject.copy()
            newObject.data = instanceData
        else:
            newObject = bpy.data.objects.new(name, instanceData)

        if self.removeAnimationData and newObject.animation_data is not None:
            newObject.animation_data.action = None

        if not self.copyFromSource and self.objectType == "Empty":
            newObject.empty_display_type = self.emptyDisplayType
        return newObject

    def getSourceObjectData(self, sourceObject):
        data = None
        if self.copyFromSource:
            if self.deepCopy and sourceObject.data is not None:
                data = sourceObject.data.copy()
            else:
                return sourceObject.data
        else:
            if self.objectType == "MESH":
                data = bpy.data.meshes.new(getPossibleMeshName("instance mesh"))
            elif self.objectType == "TEXT":
                data = bpy.data.curves.new(getPossibleCurveName("instance text"), type = "FONT")
            elif self.objectType == "CAMERA":
                data = bpy.data.cameras.new(getPossibleCameraName("instance camera"))
            elif self.objectType == "POINT_LAMP":
                data = bpy.data.lights.new(getPossibleLightName("instance lamp"), type = "POINT")
            elif self.objectType.startswith("CURVE"):
                data = bpy.data.curves.new(getPossibleCurveName("instance curve"), type = "CURVE")
                data.dimensions = self.objectType[-2:]
            elif self.objectType == "GREASE_PENCIL":
                data = bpy.data.grease_pencils.new(getPossibleGreasePencilName("instance grease pencil"))

        if data is None:
            return None
        else:
            data.an_data.removeOnZeroUsers = True
            return data

    def resetObjectDataOnAllInstances(self):
        self.resetInstances = True

    def unlinkInstancesFromNode(self):
        self.linkedObjects.clear()
        self.inputs.get("Instances").number = 0

    def delete(self):
        self.removeAllObjects()

    def duplicate(self, sourceNode):
        self.linkedObjects.clear()
