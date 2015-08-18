import bpy
from bpy.props import *
from .. events import treeChanged

class AutoExecutionProperties(bpy.types.PropertyGroup):
    bl_idname = "an_AutoExecutionProperties"

    enabled = BoolProperty(default = True, name = "Enabled")
    sceneUpdate = BoolProperty(default = True, name = "Scene Update")
    frameChange = BoolProperty(default = False, name = "Frame Change")
    propertyChange = BoolProperty(default = False, name = "Property Change")
    treeChange = BoolProperty(default = False, name = "Tree Change")


class AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "an_AnimationNodeTree"
    bl_label = "Animation"
    bl_icon = "ACTION"

    autoExecution = PointerProperty(type = AutoExecutionProperties)

    def update(self):
        treeChanged()
