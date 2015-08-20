import bpy

class AutoExecutionPanel(bpy.types.Panel):
    bl_idname = "an_auto_execution_panel"
    bl_label = "Auto Execution"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"

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

        col = layout.column()
        col.active = autoExecution.enabled
        col.prop(autoExecution, "sceneUpdate", text = "Always")
        col.separator()

        col = col.column()
        col.active = not autoExecution.sceneUpdate
        col.prop(autoExecution, "treeChanged", text = "Tree Changed")
        col.prop(autoExecution, "frameChanged", text = "Frame Changed")
        col.prop(autoExecution, "propertyChanged", text = "Property Changed")

        layout.prop(autoExecution, "minTimeDifference", text = "Min Time Difference", slider = True)
        layout.label("Execution Time: {:.5f} ms".format(tree.executionTime * 1000))

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
