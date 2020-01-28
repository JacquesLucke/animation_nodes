import bpy
import time
from .. import bl_info
from bpy.props import * 
from .. utils.handlers import eventHandler
from .. utils.nodes import getAnimationNodeTrees
from .. utils.animation import isAnimationPlaying
from .. utils.blender_ui import isViewportRendering
from . tree_auto_execution import AutoExecutionProperties
from .. events import treeChanged, isRendering, propertyChanged
from .. preferences import getBlenderVersion, getAnimationNodesVersion
from .. tree_info import getNetworksByNodeTree, getSubprogramNetworksByNodeTree
from .. execution.units import getMainUnitsByNodeTree, setupExecutionUnits, finishExecutionUnits


class LastTreeExecutionInfo(bpy.types.PropertyGroup):
    bl_idname = "an_LastTreeExecutionInfo"

    isDefault: BoolProperty(default = True)
    executionTime: FloatProperty(name = "Execution Time")
    blenderVersion: IntVectorProperty(name = "Blender Version", default = bl_info["blender"])
    animationNodesVersion: IntVectorProperty(name = "Animation Nodes Version", default = bl_info["version"])

    def updateVersions(self):
        self.blenderVersion = getBlenderVersion()
        self.animationNodesVersion = getAnimationNodesVersion()
        self.isDefault = False

    @property
    def blenderVersionString(self):
        return self.toVersionString(self.blenderVersion)

    @property
    def animationNodesVersionString(self):
        return self.toVersionString(self.animationNodesVersion)

    def toVersionString(self, intVector):
        numbers = tuple(intVector)
        return "{}.{}.{}".format(*numbers)

class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation Nodes"
    bl_icon = "ONIONSKIN_ON"

    autoExecution: PointerProperty(type = AutoExecutionProperties)
    lastExecutionInfo: PointerProperty(type = LastTreeExecutionInfo)

    globalScene: PointerProperty(type = bpy.types.Scene, name = "Scene",
        description = "The global scene used by this node tree (never none)")

    editNodeLabels: BoolProperty(name = "Edit Node Labels", default = False)

    def update(self):
        treeChanged()

    def canAutoExecute(self, events):
        a = self.autoExecution

        # Always update the triggers for better visual feedback.
        customTriggerHasBeenActivated = a.customTriggers.update()

        if not a.enabled: return False
        if not self.hasMainExecutionUnits: return False

        if "Frame" in events and (a.sceneUpdate or a.frameChanged): return True
        # TODO: We should also check if we are not exporting.
        if not isRendering():
            if self.timeSinceLastAutoExecution < a.minTimeDifference: return False

            if "Property" in events and a.propertyChanged: return True
            if "Tree" in events and a.treeChanged: return True
            if events.intersection({"File", "Addon"}) and any(
                (a.sceneUpdate, a.frameChanged, a.propertyChanged, a.treeChanged)): return True

            if not isViewportRendering() or isAnimationPlaying():
                if a.sceneUpdate: return True

        return customTriggerHasBeenActivated

    def autoExecute(self):
        self._execute()
        self.autoExecution.lastExecutionTimestamp = time.process_time()

    def execute(self):
        setupExecutionUnits()
        self._execute()
        finishExecutionUnits()

    def _execute(self):
        units = self.mainUnits
        if len(units) == 0:
            self.lastExecutionInfo.executionTime = 0
            return

        allExecutionsSuccessfull = True

        start = time.perf_counter()
        for unit in units:
            success = unit.execute()
            if not success:
                allExecutionsSuccessfull = False
        end = time.perf_counter()

        if allExecutionsSuccessfull:
            self.lastExecutionInfo.executionTime = end - start
            self.lastExecutionInfo.updateVersions()

    @property
    def hasMainExecutionUnits(self):
        return len(self.mainUnits) > 0

    @property
    def mainUnits(self):
        return getMainUnitsByNodeTree(self)

    @property
    def scene(self):
        return bpy.data.scenes[0] if self.globalScene is None else self.globalScene

    @property
    def timeSinceLastAutoExecution(self):
        return abs(time.process_time() - self.autoExecution.lastExecutionTimestamp)

    @property
    def networks(self):
        return getNetworksByNodeTree(self)

    @property
    def subprogramNetworks(self):
        return getSubprogramNetworksByNodeTree(self)

@eventHandler("ALWAYS")
def updateSelectedScenes():
    for tree in getAnimationNodeTrees():
            tree.globalScene = tree.scene
