import bpy
from bpy.props import *
from .. events import treeChanged
from .. execution.units import getMainUnitsByNodeTree

class AutoExecutionProperties(bpy.types.PropertyGroup):
    bl_idname = "an_AutoExecutionProperties"

    enabled = BoolProperty(default = True, name = "Enabled",
        description = "Enable auto execution for this node tree")

    sceneUpdate = BoolProperty(default = True, name = "Scene Update",
        description = "Execute many times per second to react on all changes in real time")

    frameChanged = BoolProperty(default = False, name = "Frame Changed",
        description = "Execute after the frame changed")

    propertyChanged = BoolProperty(default = False, name = "Property Changed",
        description = "Execute when a attribute in a animation node tree changed")

    treeChanged = BoolProperty(default = False, name = "Tree Changed",
        description = "Execute when the node tree changes (create/remove links and nodes)")


class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation"
    bl_icon = "ACTION"

    autoExecution = PointerProperty(type = AutoExecutionProperties)

    def update(self):
        treeChanged()

    def canAutoExecute(self, events):
        a = self.autoExecution
        if not a.enabled: return False
        if a.sceneUpdate and "Scene" in events: return True
        if a.frameChanged and "Frame" in events: return True
        if a.propertyChanged and "Property" in events: return True
        if a.treeChanged and "Tree" in events: return True
        if events.intersection({"File", "Addon"}) and (a.sceneUpdate or a.frameChanged or a.propertyChanged or a.treeChanged): return True
        return False

    def execute(self):
        for unit in self.mainUnits:
            unit.execute()

    @property
    def mainUnits(self):
        return getMainUnitsByNodeTree(self)
