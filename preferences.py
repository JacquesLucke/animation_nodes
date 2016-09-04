import os
import bpy
import sys
from bpy.props import *

addonName = os.path.basename(os.path.dirname(__file__))

class NodeColorProperties(bpy.types.PropertyGroup):

    def changeNodeColors(self, context):
        from . ui.node_colors import colorAllNodes
        colorAllNodes()

    mainNetwork = FloatVectorProperty(name = "Main Network",
        description = "Color for all networks that are not in a subprogram",
        default = [0.7, 0.7, 0.7], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = changeNodeColors)

    invalidNetwork = FloatVectorProperty(name = "Invalid Network",
        description = "Color for networks that stop the execution because they have an error",
        default = [0.8, 0.28, 0.25], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = changeNodeColors)

    subprogramValue = FloatProperty(name = "Subprogram Value",
        description = "Lightness of random subnetwork colors",
        default = 0.7, soft_min = 0.0, soft_max = 1.0,
        update = changeNodeColors)

    subprogramSaturation = FloatProperty(name = "Subprogram Saturation",
        description = "Color intensity of random subnetwork colors",
        default = 0.2, soft_min = 0.0, soft_max = 1.0,
        update = changeNodeColors)

    nodeColorModeItems = [
        ("NETWORKS", "Networks", "", "NONE", 0),
        ("NEEDED_COPIES", "Needed Copies", "", "NONE", 1)]

    nodeColorMode = EnumProperty(name = "Node Color Mode", default = "NETWORKS",
        items = nodeColorModeItems, update = changeNodeColors)


class ProfilingProperties(bpy.types.PropertyGroup):

    profilingFunctionItems = [
        ("EXECUTION", "Execution", "", "NONE", 0),
        ("TREE_ANALYSIS", "Tree Analysis", "", "NONE", 1),
        ("UPDATE_EVERYTHING", "Update Everything", "", "NONE", 2),
        ("SCRIPT_GENERATION", "Script Generation", "", "NONE", 3)]

    profilingOutputTypeItems = [
        ("CONSOLE", "Console", "", "CONSOLE", 0),
        ("TEXT_BLOCK", "Text Block", "", "TEXT", 1)]

    profileSortModeItems = [
        ("calls", "Amount of Calls", "Number of calls", "NONE", 0),
        ("tottime", "Total Time", " Total time spent in the given function (and excluding time made in calls to sub-functions)", "NONE", 1),
        ("cumtime", "Cumulative Time", "Cumulative time spent in this and all subfunctions (from invocation till exit)", "NONE", 2) ]

    function = EnumProperty(name = "Profiling Function",
        default = "EXECUTION", items = profilingFunctionItems)

    output = EnumProperty(name = "Profiling Output",
        default = "CONSOLE", items = profilingOutputTypeItems)

    sort = EnumProperty(name = "Profiling Sort Mode",
        default = "cumtime", items = profileSortModeItems)

class DeveloperProperties(bpy.types.PropertyGroup):

    profiling = PointerProperty(type = ProfilingProperties)

    socketEditModeItems = [
        ("NORMAL", "Normal", "", "NONE", 0),
        ("PERFORMANCE", "Performance", "", "NONE", 1)]

    socketEditMode = EnumProperty(name = "Socket Edit Mode", default = "NORMAL",
        description = "Change to display different sets of socket properties",
        items = socketEditModeItems)

    debug = BoolProperty(name = "Debug", default = False,
        description = "Enable some print statements")

    runTests = BoolProperty(name = "Run Tests", default = False,
        description = "Run the test suite when Blender starts")

class ExecutionCodeProperties(bpy.types.PropertyGroup):

    def settingChanged(self, context):
        from . events import executionCodeChanged
        from . base_types.node import updateNodeLabelMode
        executionCodeChanged()
        updateNodeLabelMode()

    executionCodeTypeItems = [
        ("DEFAULT", "Default", "", "NONE", 0),
        ("MONITOR", "Monitor Execution", "", "NONE", 1),
        ("MEASURE", "Measure Execution Times", "", "NONE", 2),
        ("BAKE", "Bake", "", "NONE", 3)]

    type = EnumProperty(name = "Execution Code Type", default = "DEFAULT",
        description = "Different execution codes can be useful in different contexts",
        update = settingChanged, items = executionCodeTypeItems)

    def get_MeasureExecution(self):
        return self.type == "MEASURE"

    def set_MeasureExecution(self, value):
        if value: self.type = "MEASURE"
        elif self.type == "MEASURE":
            self.type = "DEFAULT"

    measureExecution = BoolProperty(name = "Measure Execution",
        get = get_MeasureExecution, set = set_MeasureExecution,
        description = "Measure execution times of the individual nodes")

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addonName

    redrawAllAfterAutoExecution = BoolProperty(
        name = "Redraw All After Auto Execution", default = True)

    sceneUpdateAfterAutoExecution = BoolProperty(
        name = "Scene Update After Auto Execution", default = True)

    nodeColors = PointerProperty(type = NodeColorProperties)
    developer = PointerProperty(type = DeveloperProperties)
    executionCode = PointerProperty(type = ExecutionCodeProperties)

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        col = row.column()

        subcol = col.column(align = True)
        subcol.label("After Auto Execution:")
        subcol.prop(self, "redrawAllAfterAutoExecution", text = "Redraw All")
        subcol.prop(self, "sceneUpdateAfterAutoExecution", text = "Scene Update")

        col = row.column()

        subcol = col.column(align = True)
        subcol.label("Node Colors:")
        subcol.row().prop(self.nodeColors, "mainNetwork")
        subcol.row().prop(self.nodeColors, "invalidNetwork")
        subcol.prop(self.nodeColors, "subprogramValue", slider = True)
        subcol.prop(self.nodeColors, "subprogramSaturation", slider = True)

        col = layout.column(align = True)
        col.prop(self.developer, "debug")
        col.prop(self.developer, "runTests")

def getPreferences():
    return bpy.context.user_preferences.addons[addonName].preferences

def getDeveloperSettings():
    return getPreferences().developer

def getExecutionCodeSettings():
    return getPreferences().executionCode

def getExecutionCodeType():
    return getExecutionCodeSettings().type

def getColorSettings():
    return getPreferences().nodeColors

def debuggingIsEnabled():
    return getPreferences().developer.debug

def testsAreEnabled():
    return getPreferences().developer.runTests

def getBlenderVersion():
    return bpy.app.version

def getAnimationNodesVersion():
    return sys.modules[addonName].bl_info["version"]
