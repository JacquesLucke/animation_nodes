import bpy
import time
from bpy.props import *
from .. events import treeChanged
from .. execution.units import getMainUnitsByNodeTree
from .. nodes.generic.debug_loop import clearDebugLoopTextBlocks

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

    minTimeDifference = FloatProperty(default = 0.0, min = 0.0, soft_max = 1.0)

    lastExecutionTimestamp = FloatProperty(default = 0.0)


class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation"
    bl_icon = "ACTION"

    autoExecution = PointerProperty(type = AutoExecutionProperties)
    executionTime = FloatProperty(name = "Execution Time")

    def update(self):
        treeChanged()

    def canAutoExecute(self, events):
        a = self.autoExecution
        if not a.enabled: return False
        if "Render" not in events and abs(time.clock() - a.lastExecutionTimestamp) < a.minTimeDifference: return False
        if a.sceneUpdate and "Scene" in events: return True
        if a.frameChanged and "Frame" in events: return True
        if a.propertyChanged and "Property" in events: return True
        if a.treeChanged and "Tree" in events: return True
        if events.intersection({"File", "Addon"}) and (a.sceneUpdate or a.frameChanged or a.propertyChanged or a.treeChanged): return True
        return False

    def autoExecute(self):
        start = time.clock()

        self.execute()

        end = time.clock()
        self.executionTime = end - start
        self.autoExecution.lastExecutionTimestamp = end

    def execute(self):
        clearDebugLoopTextBlocks(self)
        for unit in self.mainUnits:
            unit.execute()

    @property
    def mainUnits(self):
        return getMainUnitsByNodeTree(self)
