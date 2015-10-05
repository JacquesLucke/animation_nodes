import bpy

class RemoveNodeTree(bpy.types.Operator):
    bl_idname = "an.remove_node_tree"
    bl_label = "Remove Animation Node Tree"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        if not space: return False
        if space.type != "NODE_EDITOR": return False
        if space.tree_type != "an_AnimationNodeTree": return False
        return space.node_tree is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        tree = context.space_data.node_tree
        tree.use_fake_user = False
        context.space_data.node_tree = None
        # the doc says this can maybe crash Blender
        # I didn't experienced this yet
        tree.user_clear()
        bpy.data.node_groups.remove(tree)
        return {"FINISHED"}
