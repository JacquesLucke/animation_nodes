import bpy
from .. problems import canExecute
from .. utils.layout import writeText
from .. utils.timing import prettyTime

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

        if not canExecute():
            message = ("Your node tree cannot be executed. "
                       "Look in the 'Problems' panel for more information.")
            writeText(layout, message, width = 35, icon = "INFO")

        layout.label(prettyTime(tree.lastExecutionInfo.executionTime), icon = "TIME")

        layout.separator()
        layout.prop_search(tree, "sceneName", bpy.data, "scenes", icon = "SCENE_DATA", text = "Scene")
        layout.prop(tree, "editNodeLabels")


    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
