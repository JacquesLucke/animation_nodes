import bpy

class TemplatesMenu(bpy.types.Menu):
    bl_idname = "an_templates_menu"
    bl_label = "Templates Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("an.empty_group_template")

class TemplatesMenuInHeader(bpy.types.Header):
    bl_idname = "an_templates_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.menu("an_templates_menu", text = "Templates")
