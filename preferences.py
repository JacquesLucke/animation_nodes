import os
import bpy
import sys
from bpy.props import *

addonName = os.path.basename(os.path.dirname(__file__))

class NodeColorProperties(bpy.types.PropertyGroup):
    bl_idname = "an_NodeColorProperties"

    def changeNodeColors(self, context):
        from . ui.node_colors import colorNetworks
        colorNetworks()

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


class ProfilingProperties(bpy.types.PropertyGroup):
    bl_idname = "an_ProfilingProperties"

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
    bl_idname = "an_DeveloperProperties"

    def settingChanged(self, context):
        from . events import executionCodeChanged
        from . execution.measurements import resetMeasurements
        executionCodeChanged()
        resetMeasurements()

    profiling = PointerProperty(type = ProfilingProperties)

    measureNodeExecutionTimes = BoolProperty(name = "Measure Node Execution Times", default = False,
        description = "Measure the time a node takes to execute each time it is called",
        update = settingChanged)

    monitorExecution = BoolProperty(name = "Monitor Execution", default = False,
        description = "Enable to find out which node raises exceptions",
        update = settingChanged)

    debug = BoolProperty(name = "Debug", default = False)


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addonName

    redrawAllAfterAutoExecution = BoolProperty(
        name = "Redraw All After Auto Execution", default = True)

    sceneUpdateAfterAutoExecution = BoolProperty(
        name = "Scene Update After Auto Execution", default = True)

    nodeColors = PointerProperty(type = NodeColorProperties)
    developer = PointerProperty(type = DeveloperProperties)

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

        layout.prop(self.developer, "debug")

def getPreferences():
    # TODO: access user_preferences without the context
    return bpy.context.user_preferences.addons[addonName].preferences

def getDeveloperSettings():
    return getPreferences().developer

def nodeColors():
    return getPreferences().nodeColors

def debuggingIsEnabled():
    return getPreferences().developer.debug

def measureNodeExecutionTimesIsEnabled():
    return getDeveloperSettings().measureNodeExecutionTimes

def monitorExecutionIsEnabled():
    return getDeveloperSettings().monitorExecution

def getBlenderVersion():
    return bpy.app.version

def getAnimationNodesVersion():
    return sys.modules[addonName].bl_info["version"]
