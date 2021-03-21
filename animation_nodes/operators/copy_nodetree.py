import bpy

class CopyNodeTree(bpy.types.Operator):
    bl_idname = "an.copy_node_tree"
    bl_label = "Copy Animation Node Tree"
    bl_description = "Copy the active animation node tree"

    @classmethod
    def poll(cls, context):
        return context.getActiveAnimationNodeTree() is not None

    def execute(self, context):
        tree = context.space_data.node_tree
        new = tree.copy()
        context.space_data.node_tree = new
        return {"FINISHED"}
