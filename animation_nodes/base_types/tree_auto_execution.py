import bpy
from bpy.props import *
from .. utils.blender_ui import getDpiFactor

idTypeItems = [
    ("OBJECT", "Object", "", "OBJECT_DATA", 0),
    ("COLLECTION", "Collection", "", "GROUP", 1),
    ("SCENE", "Scene", "", "SCENE_DATA", 2)]

class AutoExecutionTrigger_MonitorProperty(bpy.types.PropertyGroup):
    bl_idname = "an_AutoExecutionTrigger_MonitorProperty"

    def resetIDs(self, context):
        self.object = self.collection = self.scene = None

    idType: EnumProperty(name = "ID Type", default = "OBJECT",
        items = idTypeItems, update = resetIDs)

    object: PointerProperty(type = bpy.types.Object, name = "Object")
    collection: PointerProperty(type = bpy.types.Collection, name = "Collection")
    scene: PointerProperty(type = bpy.types.Scene, name = "Scene")
    dataPaths: StringProperty(name = "Data Paths", default = "",
        description = "Comma separated paths of properties to monitor")

    lastState: StringProperty(default = "")
    expanded: BoolProperty(default = True)
    enabled: BoolProperty(default = True)
    hasError: BoolProperty(default = False)

    def update(self):
        lastState = self.lastState
        newState = self.getPropertiesState()
        if newState == lastState:
            return False
        else:
            self.lastState = newState
            return self.enabled and lastState != ""

    def getPropertiesState(self):
        props = self.getProperties()
        if len(props) == 0: return ""

        propsString = ""
        for prop in props:
            if hasattr(prop, "__iter__"):
                propsString += "".join(str(part) for part in prop)
            else: propsString += str(prop)

        return propsString

    def getProperties(self):
        self.hasError = False
        idBlocks = self.getIDBlocks()
        if len(idBlocks) == 0 or not self.dataPaths.strip(): return []

        try:
            properties = []
            paths = self.getDataPaths()
            for idBlock in idBlocks:
                properties.extend(idBlock.path_resolve(p) for p in paths)
            return properties
        except:
            self.hasError = True
            return []

    def getDataPaths(self):
        return [p.strip() for p in self.dataPaths.split(",")]

    def getIDBlocks(self):
        if self.idType == "OBJECT":
            if self.object is None: return []
            return [self.object]
        elif self.idType == "COLLECTION":
            if self.collection is None: return []
            return self.collection.all_objects
        elif self.idType == "SCENE":
            if self.scene is None: return []
            return [self.scene]

    def draw(self, layout, index):
        box = layout.box()

        header = box.row()
        icon = 'TRIA_DOWN' if self.expanded else 'TRIA_RIGHT'
        header.prop(self, "expanded", icon = icon, text = "", emboss = False)
        if self.hasError: header.label(text = "", icon = "ERROR")
        header.prop(self, "enabled", text = "Enable " + self.dataPaths, toggle = True)
        header.operator("an.remove_auto_execution_trigger", icon = "X",
            text = "", emboss = False).index = index

        if self.expanded:
            col = box.column(align = True)
            col.active = self.enabled
            col.prop(self, "idType", text = "")
            row = col.row(align = True)
            row.operator("an.assign_active_object_to_auto_execution_trigger",
                icon = "EYEDROPPER", text = "").index = index

            if self.idType == "OBJECT":
                row.prop(self, "object", text = "")
            elif self.idType == "COLLECTION":
                row.prop(self, "collection", text = "")
            elif self.idType == "SCENE":
                row.prop(self, "scene", text = "")

            col.prop(self, "dataPaths", text = "")


class CustomAutoExecutionTriggers(bpy.types.PropertyGroup):
    bl_idname = "an_CustomAutoExecutionTriggers"

    monitorPropertyTriggers: CollectionProperty(type = AutoExecutionTrigger_MonitorProperty)

    def new(self, type, **kwargs):
        if type == "MONITOR_PROPERTY":
            item = self.monitorPropertyTriggers.add()
        for key, value in kwargs.items():
            setattr(item, key, value)
        return item

    def update(self):
        triggers = [trigger.update() for trigger in self.monitorPropertyTriggers]
        return any(triggers)


class AutoExecutionProperties(bpy.types.PropertyGroup):

    customTriggers: PointerProperty(type = CustomAutoExecutionTriggers)

    enabled: BoolProperty(default = True, name = "Enabled",
        description = "Enable auto execution for this node tree")

    always: BoolProperty(default = False, name = "Always",
        description = "Execute many times per second to react on all changes in real time (deactivated during preview rendering)")

    sceneChanged: BoolProperty(default = True, name = "Scene Changed",
        description = "Execute after anything in the scene changed")

    frameChanged: BoolProperty(default = True, name = "Frame Changed",
        description = "Execute after the frame changed")

    propertyChanged: BoolProperty(default = True, name = "Property Changed",
        description = "Execute when a attribute in a animation node tree changed")

    treeChanged: BoolProperty(default = True, name = "Tree Changed",
        description = "Execute when the node tree changes (create/remove links and nodes)")

    minTimeDifference: FloatProperty(name = "Min Time Difference",
        description = "Auto execute not that often; E.g. only every 0.5 seconds",
        default = 0.0, min = 0.0, soft_max = 1.0)

    lastExecutionTimestamp: FloatProperty(default = 0.0)

    # Deprecated. Only kept for versioning.
    sceneUpdate: BoolProperty(default = True, name = "Scene Update", description = "Deprecated. Only kept for versioning")


class AddAutoExecutionTrigger(bpy.types.Operator):
    bl_idname = "an.add_auto_execution_trigger"
    bl_label = "Add Auto Execution Trigger"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.getActiveAnimationNodeTree() is not None

    def execute(self, context):
        tree = context.space_data.node_tree
        trigger = tree.autoExecution.customTriggers.new("MONITOR_PROPERTY")
        trigger.idType = "OBJECT"
        context.area.tag_redraw()
        return {"FINISHED"}


class RemoveAutoExecutionTrigger(bpy.types.Operator):
    bl_idname = "an.remove_auto_execution_trigger"
    bl_label = "Remove Auto Execution Trigger"
    bl_options = {"UNDO"}

    index: IntProperty()

    @classmethod
    def poll(cls, context):
        return context.getActiveAnimationNodeTree() is not None

    def execute(self, context):
        tree = context.space_data.node_tree
        customTriggers = tree.autoExecution.customTriggers
        customTriggers.monitorPropertyTriggers.remove(self.index)
        return {"FINISHED"}


class AssignActiveObjectToAutoExecutionTrigger(bpy.types.Operator):
    bl_idname = "an.assign_active_object_to_auto_execution_trigger"
    bl_label = "Assign Active Object to Auto Execution Trigger"
    bl_options = {"UNDO"}

    index: IntProperty()

    @classmethod
    def poll(cls, context):
        return context.getActiveAnimationNodeTree() is not None

    def execute(self, context):
        tree = context.space_data.node_tree
        trigger = tree.autoExecution.customTriggers.monitorPropertyTriggers[self.index]
        if trigger.idType == "OBJECT":
            trigger.object = context.active_object
        if trigger.idType == "COLLECTION":
            trigger.collection = context.collection
        if trigger.idType == "SCENE":
            trigger.scene = context.scene
        return {"FINISHED"}
