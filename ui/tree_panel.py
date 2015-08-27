import bpy

class TreePanel(bpy.types.Panel):
    bl_idname = "an_tree_panel"
    bl_label = "Animation Node Tree"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"

    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False
        return tree.bl_idname == "an_AnimationNodeTree"

    def draw(self, context):
        tree = self.getTree()
        layout = self.layout

        col = layout.column()
        col.scale_y = 1.5
        props = col.operator("an.execute_tree", icon = "PLAY")
        props.name = tree.name

        layout.separator()

        time = tree.executionTime
        if time > 1.5: timeText = "{:.2f} s".format(tree.executionTime)
        else: timeText = "{:.5f} ms".format(tree.executionTime * 1000)
        layout.label(timeText, icon = "TIME")

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
