import bpy
import os
from bpy.props import *

addonName = os.path.basename(os.path.dirname(__file__))

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

    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)
        col.label("After Auto Execution:")
        col.prop(self, "redrawAllAfterAutoExecution", text = "Redraw All")
        col.prop(self, "sceneUpdateAfterAutoExecution", text = "Scene Update")

        col = layout.column(align = True)
        col.label("Execution Code:")
        col.prop(self, "generateCompactCode")

def getPreferences():
    return bpy.context.user_preferences.addons.get(addonName).preferences

def generateCompactCode():
    return getPreferences().generateCompactCode

def forbidSubprogramRecursion():
    return getPreferences().forbidSubprogramRecursion
