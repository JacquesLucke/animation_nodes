import bpy
from .. problems import canExecute
from .. utils.layout import writeText
from .. utils.blender_ui import isViewportRendering

class AutoExecutionPanel(bpy.types.Panel):
    bl_idname = "AN_PT_auto_execution_panel"
    bl_label = "Auto Execution"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node Tree"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False
        return tree.bl_idname == "an_AnimationNodeTree"

    def draw_header(self, context):
        tree = self.getTree()
        self.layout.prop(tree.autoExecution, "enabled", text = "")

    def draw(self, context):
        layout = self.layout

        tree = context.space_data.edit_tree
        autoExecution = tree.autoExecution

        isRendering = isViewportRendering()

        if not canExecute():
            layout.label(text = "Look in the 'Problems' panel", icon = "INFO")

        layout.active = autoExecution.enabled

        col = layout.column()
        col.active = not isRendering
        text = "Always" if not isRendering else "Always (deactivated)"
        col.prop(autoExecution, "always", text = text)

        col = layout.column()
        col.active = not autoExecution.always or isRendering
        col.prop(autoExecution, "sceneChanged", text = "Scene Changed")
        col = col.column()
        col.active = not autoExecution.sceneChanged
        col.prop(autoExecution, "treeChanged", text = "Tree Changed")
        col.prop(autoExecution, "frameChanged", text = "Frame Changed")
        col.prop(autoExecution, "propertyChanged", text = "Property Changed")

        layout.prop(autoExecution, "minTimeDifference", slider = True)

        customTriggers = autoExecution.customTriggers
        for i, monitorPropertyTrigger in enumerate(customTriggers.monitorPropertyTriggers):
            monitorPropertyTrigger.draw(layout, i)

        layout.operator("an.add_auto_execution_trigger", text = "New Trigger", icon = "ADD")

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
