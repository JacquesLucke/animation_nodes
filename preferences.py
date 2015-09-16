import bpy
import os
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


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = addonName

    redrawAllAfterAutoExecution = BoolProperty(
        name = "Redraw All After Auto Execution", default = True)

    sceneUpdateAfterAutoExecution = BoolProperty(
        name = "Scene Update After Auto Execution", default = True)

    generateCompactCode = BoolProperty(
        name = "Generate Compact Code", default = False,
        description = "Avoid comments and blank lines (this has no impact on performance)")

    forbidSubprogramRecursion = BoolProperty(
        name = "Forbid Subprogram Recursion", default = True,
        description = "A subprogram invoker node must not be in the same network that it calls")

    nodeColors = PointerProperty(type = NodeColorProperties)

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        col = row.column()

        subcol = col.column(align = True)
        subcol.label("After Auto Execution:")
        subcol.prop(self, "redrawAllAfterAutoExecution", text = "Redraw All")
        subcol.prop(self, "sceneUpdateAfterAutoExecution", text = "Scene Update")

        subcol = col.column(align = True)
        subcol.label("Execution Code:")
        subcol.prop(self, "generateCompactCode")

        col = row.column()

        subcol = col.column(align = True)
        subcol.label("Node Colors:")
        subcol.row().prop(self.nodeColors, "mainNetwork")
        subcol.row().prop(self.nodeColors, "invalidNetwork")
        subcol.prop(self.nodeColors, "subprogramValue", slider = True)
        subcol.prop(self.nodeColors, "subprogramSaturation", slider = True)

addon = None

def getPreferences():
    if addon is None:
        # This should happen very rarely
        # Problem is that this can access the context while rendering
        #   which can lead to problems 
        _updateAddon()
    return addon.preferences

def generateCompactCode():
    return getPreferences().generateCompactCode

def forbidSubprogramRecursion():
    return getPreferences().forbidSubprogramRecursion

def nodeColors():
    return getPreferences().nodeColors


def _updateAddon():
    global addon
    addon = bpy.context.user_preferences.addons.get(addonName)

def register():
    global addon
    _updateAddon()

def unregister():
    global addon
    addon = None
