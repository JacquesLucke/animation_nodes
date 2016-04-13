import bpy
from bpy.props import *
from .. utils.blender_ui import getDpiFactor

triggerTypeItems = [
    ("MONITOR_PROPERTY", "Monitor Property", "", "", 0)]

idTypeItems = [
    ("OBJECT", "Object", "", "OBJECT_DATA", 0),
    ("SCENE", "Scene", "", "SCENE_DATA", 1)]

class AddAutoExecutionTrigger(bpy.types.Operator):
    bl_idname = "an.add_auto_execution_trigger"
    bl_label = "Add Auto Execution Trigger"

    triggerType = EnumProperty(name = "Trigger Type", default = "MONITOR_PROPERTY",
        items = triggerTypeItems)

    idType = EnumProperty(name = "ID Type", default = "OBJECT",
        items = idTypeItems)

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR": return False
        tree = context.space_data.node_tree
        if tree is None: return False
        return tree.bl_idname == "an_AnimationNodeTree"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250 * getDpiFactor())

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "triggerType")
        if self.triggerType == "MONITOR_PROPERTY":
            layout.prop(self, "idType")

    def check(self, context):
        return True

    def execute(self, context):
        tree = context.space_data.node_tree
        trigger = tree.autoExecution.customTriggers.new(self.triggerType)
        if self.triggerType == "MONITOR_PROPERTY":
            trigger.idType = self.idType
        context.area.tag_redraw()
        return {"FINISHED"}

class AutoExecutionTrigger_MonitorProperty(bpy.types.PropertyGroup):

    idType = EnumProperty(name = "ID Type", default = "OBJECT",
        items = idTypeItems)

    idObjectName = StringProperty(name = "ID Object Name", default = "")
    dataPath = StringProperty(name = "Data Path", default = "")

    lastState = StringProperty()

    def update(self):
        newState = self.getPropertyState()
        if newState == self.lastState:
            return False
        else:
            self.lastState = newState
            return True

    def getPropertyState(self):
        prop = self.getProperty()
        if prop is None: return ""
        if hasattr(prop, "__iter__"):
            return " ".join(str(part) for part in prop)
        return str(prop)

    def getProperty(self):
        object = self.getObject()
        if object is None:
            return None

        try: return object.path_resolve(self.dataPath)
        except: return None

    def getObject(self):
        if self.idType == "OBJECT":
            return bpy.data.objects.get(self.idObjectName)
        elif self.idType == "SCENE":
            return bpy.data.scenes.get(self.idObjectName)

    def draw(self, layout):
        row = layout.row(align = True)
        if self.idType == "OBJECT":
            row.prop_search(self, "idObjectName", bpy.context.scene, "objects", text = "")
        elif self.idType == "SCENE":
            row.prop_search(self, "idObjectName", bpy.data, "scenes", text = "")
        row.prop(self, "dataPath", icon = "RNA", text = "")


class CustomAutoExecutionTriggers(bpy.types.PropertyGroup):

    monitorPropertyTriggers = CollectionProperty(type = AutoExecutionTrigger_MonitorProperty)

    def new(self, type):
        if type == "MONITOR_PROPERTY":
            return self.monitorPropertyTriggers.add()

    def update(self):
        triggers = [trigger.update() for trigger in self.monitorPropertyTriggers]
        return any(triggers)


class AutoExecutionProperties(bpy.types.PropertyGroup):

    customTriggers = PointerProperty(type = CustomAutoExecutionTriggers)

    enabled = BoolProperty(default = True, name = "Enabled",
        description = "Enable auto execution for this node tree")

    sceneUpdate = BoolProperty(default = True, name = "Scene Update",
        description = "Execute many times per second to react on all changes in real time (deactivated during preview rendering)")

    frameChanged = BoolProperty(default = False, name = "Frame Changed",
        description = "Execute after the frame changed")

    propertyChanged = BoolProperty(default = False, name = "Property Changed",
        description = "Execute when a attribute in a animation node tree changed")

    treeChanged = BoolProperty(default = False, name = "Tree Changed",
        description = "Execute when the node tree changes (create/remove links and nodes)")

    minTimeDifference = FloatProperty(name = "Min Time Difference",
        description = "Auto execute not that often; E.g. only every 0.5 seconds",
        default = 0.0, min = 0.0, soft_max = 1.0)

    lastExecutionTimestamp = FloatProperty(default = 0.0)
