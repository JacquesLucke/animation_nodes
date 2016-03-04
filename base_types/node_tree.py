import bpy
import time
from bpy.props import *
from .. utils.handlers import eventHandler
from .. utils.nodes import getAnimationNodeTrees
from .. events import treeChanged, isRendering, propertyChanged
from .. nodes.generic.debug_loop import clearDebugLoopTextBlocks
from .. utils.blender_ui import iterActiveScreens, isViewportRendering
from .. execution.units import getMainUnitsByNodeTree, setupExecutionUnits, finishExecutionUnits

class AutoExecutionProperties(bpy.types.PropertyGroup):
    bl_idname = "an_AutoExecutionProperties"

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


class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation"
    bl_icon = "ACTION"

    autoExecution = PointerProperty(type = AutoExecutionProperties)
    executionTime = FloatProperty(name = "Execution Time")

    sceneName = StringProperty()

    editNodeLabels = BoolProperty(name = "Edit Node Labels", default = False)
    dynamicNodeLabels = BoolProperty(name = "Dynamic Node Labels", default = True)

    def update(self):
        treeChanged()

    def canAutoExecute(self, events):
        def isAnimationPlaying():
            return any([screen.is_animation_playing for screen in iterActiveScreens()])

        a = self.autoExecution
        if not a.enabled: return False
        if not self.hasMainExecutionUnits: return False

        if isRendering():
            if "Scene" in events and a.sceneUpdate: return True
            if "Frame" in events and (a.frameChanged or a.sceneUpdate): return True
        else:
            if self.timeSinceLastAutoExecution < a.minTimeDifference: return False

            if isAnimationPlaying():
                if (a.sceneUpdate or a.frameChanged) and "Frame" in events: return True
            elif not isViewportRendering():
                if "Scene" in events and a.sceneUpdate: return True
            if "Frame" in events and a.frameChanged: return True
            if "Property" in events and a.propertyChanged: return True
            if "Tree" in events and a.treeChanged: return True
            if events.intersection({"File", "Addon"}) and \
                (a.sceneUpdate or a.frameChanged or a.propertyChanged or a.treeChanged): return True

        return False

    def autoExecute(self):
        self._execute()
        self.autoExecution.lastExecutionTimestamp = time.clock()

    def execute(self):
        setupExecutionUnits()
        self._execute()
        finishExecutionUnits()

    def _execute(self):
        units = self.mainUnits
        if len(units) == 0:
            self.executionTime = 0
            return

        clearDebugLoopTextBlocks(self)
        start = time.clock()
        for unit in units:
            unit.execute()
        end = time.clock()
        self.executionTime = end - start

    @property
    def hasMainExecutionUnits(self):
        return len(self.mainUnits) > 0

    @property
    def mainUnits(self):
        return getMainUnitsByNodeTree(self)

    @property
    def scene(self):
        scene = bpy.data.scenes.get(self.sceneName)
        if scene is None:
            scene = bpy.data.scenes[0]
        return scene

    @property
    def timeSinceLastAutoExecution(self):
        return abs(time.clock() - self.autoExecution.lastExecutionTimestamp)

@eventHandler("SCENE_UPDATE_POST")
def updateSelectedScenes(scene):
    for tree in getAnimationNodeTrees():
        scene = tree.scene
        if scene.name != tree.sceneName:
            tree.sceneName = scene.name
