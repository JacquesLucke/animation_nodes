import bpy
from .. preferences import getDeveloperSettings

class DeveloperPanel(bpy.types.Panel):
    bl_idname = "an_developer_panel"
    bl_label = "Developer"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree

        col = layout.column()
        col.label("Execution Code:")
        row = col.row(align = True)
        row.operator("an.print_current_execution_code", text = "Print", icon = "CONSOLE")
        row.operator("an.write_current_execution_code", text = "Write", icon = "TEXT")

        layout.separator()

        col = layout.column()
        col.label("Profile Execution:")
        row = col.row(align = True)
        row.operator("an.print_profile_execution_result", text = "Print", icon = "CONSOLE")
        row.operator("an.write_profile_execution_result", text = "Write", icon = "TEXT")
        layout.prop(getDeveloperSettings(), "profilingSortMode", text = "Sort")
