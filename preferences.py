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

    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)
        col.label("After Auto Execution:")
        col.prop(self, "redrawAllAfterAutoExecution", text = "Redraw All")
        col.prop(self, "sceneUpdateAfterAutoExecution", text = "Scene Update")

def getPreferences():
    return bpy.context.user_preferences.addons.get(addonName).preferences
