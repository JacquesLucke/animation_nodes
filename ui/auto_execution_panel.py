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
        tree = context.space_data.edit_tree

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
