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

    debug = BoolProperty(name = "Debug", default = False,
        description = "Enable some print statements")

    runTests = BoolProperty(name = "Run Tests", default = False,
        description = "Run the test suite when Blender starts")

class ExecutionCodeProperties(bpy.types.PropertyGroup):

    def settingChanged(self, context):
        from . events import executionCodeChanged
        from . base_types.nodes.base_node import updateNodeLabelMode
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

class DrawMeshIndicesProperties(bpy.types.PropertyGroup):
    activated = BoolProperty(name = "Activated", default = False)

    fontSize = IntProperty(name = "Font Size", default = 12,
        soft_min = 5, soft_max = 40, min = 0)

    textColor = mainNetwork = FloatVectorProperty(name = "Text Color",
        default = [1, 1, 1], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0)

class DrawHandlerProperties(bpy.types.PropertyGroup):
    meshIndices = PointerProperty(type = DrawMeshIndicesProperties)

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addonName

    nodeColors = PointerProperty(type = NodeColorProperties)
    developer = PointerProperty(type = DeveloperProperties)
    executionCode = PointerProperty(type = ExecutionCodeProperties)
    drawHandlers = PointerProperty(type = DrawHandlerProperties)

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        col = row.column(align = True)
        col.label("Node Colors:")
        col.row().prop(self.nodeColors, "mainNetwork")
        col.row().prop(self.nodeColors, "invalidNetwork")
        subrow = col.row(align = True)
        subrow.prop(self.nodeColors, "subprogramValue", slider = True)
        subrow.prop(self.nodeColors, "subprogramSaturation", slider = True)

        col = row.column(align = True)
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

def getMeshIndicesSettings():
    return getPreferences().drawHandlers.meshIndices

def debuggingIsEnabled():
    return getPreferences().developer.debug

def testsAreEnabled():
    return getPreferences().developer.runTests

def getBlenderVersion():
    return bpy.app.version

def getAnimationNodesVersion():
    return sys.modules[addonName].bl_info["version"]
