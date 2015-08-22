import bpy
from .. import problems

class ProblemsPanel(bpy.types.Panel):
    bl_idname = "an_problems_panel"
    bl_label = "Problems"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"

    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False
        return tree.bl_idname == "an_AnimationNodeTree" and len(problems.getProblems()) > 0

    def draw_header(self, context):
        self.layout.label("", icon = "ERROR")

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.console_toggle", text = "Toogle Console")
        for problem in problems.getProblems():
            layout.label(problem.message)

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
